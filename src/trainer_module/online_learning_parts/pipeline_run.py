from __future__ import annotations

from typing import Dict, Any
import torch
from tqdm import tqdm

from src.trainer_module.online_learning import (
    logger,
    TrajectoryResults,
)

def _run_single_trajectory_online_learning_impl(self, trajectory_idx: int = 0) -> Dict[str, Any]:
    """
    Run online learning pipeline for a single trajectory.
    """
    try:
        # Access online learning configuration
        online_config = self.config.online_learning

        # Check if model is available for online learning
        if self.trained_model is None:
            logger.error("No model available for online learning")
            return {"status": "error", "message": "No model available for online learning"}

        # Initialize online model as copy of trained model using the same factory function
        from copy import deepcopy

        # Create a new model instance using the same factory function that created the trained model
        try:
            # Method 1: Use the same factory function to ensure identical architecture
            from config.factory import create_model
            self.online_model = create_model(self.config, self.system_model)
            self.online_model.load_state_dict(self.trained_model.state_dict())
            self.online_model.eval()  # Set to eval mode like the trained model
            logger.info("Initialized online model as copy of trained model using factory function")
        except Exception as e:
            logger.warning(f"Factory function copy failed ({e}), trying clone approach")
            try:
                # Method 2: Use torch.clone() for parameters
                self.online_model = deepcopy(self.trained_model.cpu())
                if torch.cuda.is_available() and next(self.trained_model.parameters()).is_cuda:
                    self.online_model = self.online_model.cuda()
                logger.info("Initialized online model using CPU deepcopy then moved to GPU")
            except Exception as e2:
                logger.error(f"All model copying methods failed: {e2}")
                raise RuntimeError(f"Failed to create online model copy. Factory function failed: {e}, Deepcopy failed: {e2}. Cannot proceed with online learning.")

        # Create supervised trained model as copy of trained model (same approach as online model)
        try:
            # Method 1: Use the same factory function to ensure identical architecture
            self.supervised_trained_model = create_model(self.config, self.system_model)
            self.supervised_trained_model.load_state_dict(self.trained_model.state_dict())
            self.supervised_trained_model.train()  # Set to training mode for supervised learning
            logger.info("Initialized supervised trained model as copy of trained model using factory function")
        except Exception as e:
            logger.warning(f"Factory function copy failed for supervised model ({e}), trying clone approach")
            try:
                # Method 2: Use torch.clone() for parameters
                self.supervised_trained_model = deepcopy(self.trained_model.cpu())
                if torch.cuda.is_available() and next(self.trained_model.parameters()).is_cuda:
                    self.supervised_trained_model = self.supervised_trained_model.cuda()
                self.supervised_trained_model.train()  # Set to training mode for supervised learning
                logger.info("Initialized supervised trained model using CPU deepcopy then moved to GPU")
            except Exception as e2:
                logger.error(f"All supervised model copying methods failed: {e2}")
                raise RuntimeError(f"Failed to create supervised trained model copy. Factory function failed: {e}, Deepcopy failed: {e2}. Cannot proceed with supervised learning.")

        # Reset dual model state for new trajectory
        self.drift_detected = False
        self.learning_done = False
        self.online_training_count = 0
        self.first_eta_change = True
        # Reset online optimizer to start fresh for new trajectory
        if hasattr(self, 'online_optimizer'):
            delattr(self, 'online_optimizer')
        # Reset supervised optimizer to start fresh for new trajectory
        if hasattr(self, 'supervised_optimizer'):
            delattr(self, 'supervised_optimizer')
        logger.info("Reset dual model state for new trajectory")

        # Get online learning parameters
        window_size = getattr(online_config, 'window_size', 10)
        stride = getattr(online_config, 'stride', 5)

        # Create an on-demand dataset and dataloader for online learning
        # This will generate data in windows with the current system_model.params.
        # This allows dynamic eta updates within the generator to be reflected.
        system_model_params = self.system_model.params

        # Create on-demand dataset using the factory function
        logger.info("Online learning is enabled, creating on-demand dataset and dataloader.")
            # SET BREAKPOINT HERE - Before creating dataset
        print(f"Creating dataset with SNR: {system_model_params.snr}")
        online_learning_dataset = create_online_learning_dataset(
            system_model_params=system_model_params,
            config=self.config,
            window_size=window_size,
            stride=stride
        )

        # Ensure the dataset generator uses the current (reset) eta value
        current_eta = system_model_params.eta
        online_learning_dataset.update_eta(current_eta)
        logger.info(f"Initialized trajectory with eta = {current_eta:.4f}")

        # Create dataloader from on-demand dataset
        from torch.utils.data import DataLoader
        online_learning_dataloader = DataLoader(
            online_learning_dataset,
            batch_size=1,  # Process one window at a time
            shuffle=False,
            num_workers=0,  # On-demand dataset must use 0 workers
            drop_last=False
        )
        logger.info(f"Created on-demand online learning dataloader for {len(online_learning_dataloader)} windows.")

        # Create online trainer
        online_trainer = OnlineTrainer(
            model=self.trained_model,
            config=self.config,
            device=device
        )

        # Set loss threshold for drift detection
        loss_threshold = getattr(online_config, 'loss_threshold', 0.5)
        max_iterations = getattr(online_config, 'max_iterations', 10)

        # Initialize trajectory results structure
        trajectory_results = TrajectoryResults()
        window_update_flags = []
        drift_detected_count = 0
        model_updated_count = 0
        last_ekf_predictions = None  # Track last window's EKF predictions
        last_ekf_covariances = None  # Track last window's EKF covariances

        # Initialize online model results structure
        online_trajectory_results = TrajectoryResults()

        # Initialize supervised model results structure
        supervised_trajectory_results = TrajectoryResults()

        # EKF state tracking for online learning
        online_last_ekf_predictions = None
        online_last_ekf_covariances = None

        # EKF state tracking for supervised learning
        supervised_last_ekf_predictions = None
        supervised_last_ekf_covariances = None

        # Track training and eta change events
        eta_change_windows = []  # List of window indices where eta changed
        training_start_window = None  # Window where training started
        training_end_window = None  # Window where training ended

        # GLRT drift detection tracking variables
        glrt_ref_loss_changepoint_window = None  # Most likely window where change occurred (reference loss)
        glrt_ref_loss_likelihood = None  # Log-GLR value for reference loss
        glrt_ref_loss_all_log_glr = None  # All log-GLR values for reference loss
        glrt_ref_loss_candidate_points = None  # Candidate changepoint indices for reference loss
        glrt_ref_losses = None  # Loss values used for reference loss GLRT
        glrt_main_loss_changepoint_window = None  # Most likely window where change occurred (main loss)
        glrt_main_loss_likelihood = None  # Log-GLR value for main loss
        glrt_main_loss_all_log_glr = None  # All log-GLR values for main loss
        glrt_main_loss_candidate_points = None  # Candidate changepoint indices for main loss
        glrt_main_losses = None  # Loss values used for main loss GLRT

        # Process each window of online data
        for window_idx, (time_series_batch, sources_num_batch, labels_batch) in enumerate(tqdm(online_learning_dataloader, desc="Online Learning")):
            # --- Dynamic Eta Update Logic ---
            if online_config.eta_update_interval_windows and online_config.eta_update_interval_windows > 0 and \
               window_idx > 0 and window_idx % online_config.eta_update_interval_windows == 0:
                current_eta = self.system_model.params.eta # Get current eta from the shared SystemModelParams
                eta_increment = online_config.eta_increment if online_config.eta_increment is not None else 0.01
                new_eta = current_eta + eta_increment

                # Apply min/max constraints if specified
                if online_config.max_eta is not None:
                    new_eta = min(new_eta, online_config.max_eta)
                if online_config.min_eta is not None:
                    new_eta = max(new_eta, online_config.min_eta)

                # Only update if there's an actual change
                if abs(new_eta - current_eta) > 1e-6:
                    logger.info(f"Online Learning: Dynamically updating eta at window {window_idx}. From {current_eta:.4f} to {new_eta:.4f}")
                    # Track eta change window
                    eta_change_windows.append(window_idx)
                if self.first_eta_change:
                    self.first_eta_change = False
                    logger.info(f"First eta modification at window {window_idx}")
                    # The dataset holds the generator, which updates the shared self.system_model.params.eta
                    online_learning_dataloader.dataset.update_eta(new_eta)
                                        # Set drift detected on first eta change only
            if self.time_to_learn is not None and window_idx == self.time_to_learn:
                self.drift_detected = True
                logger.info(f"Drift detected at window {window_idx} (configured time_to_learn)")
                # Initialize online EKF state with static model's current state
                online_last_ekf_predictions = last_ekf_predictions
                online_last_ekf_covariances = last_ekf_covariances
                logger.info(f"Initialized online EKF state with static model's state at window {window_idx}")

            # --- End Dynamic Eta Update Logic ---

            # Unpack batch data
            # The batch data shapes are:
            # time_series_batch: [1, window_size, N, T] = [1, 10, 8, 200]
            # sources_num_batch: [10, 1] (not [1, 10] as expected)
            # labels_batch: [10, 1, 3] (not [1, 10, 3] as expected)

            # Extract the content properly from the batch
            time_series_single_window = time_series_batch[0]  # Shape: [window_size, N, T]

            # Reshape sources_num to be a list of integers
            sources_num_single_window_list = sources_num_batch[:, 0].tolist() if isinstance(sources_num_batch, torch.Tensor) else [s[0] for s in sources_num_batch]

            # Reshape labels to be a list of arrays
            if isinstance(labels_batch, torch.Tensor):
                # If labels_batch is a tensor [10, 1, 3]
                labels_single_window_list_of_arrays = [arr[0].cpu().numpy() if isinstance(arr, torch.Tensor) else arr[0] for arr in labels_batch]
            else:
                # If labels_batch is a list of tensors or arrays
                labels_single_window_list_of_arrays = [arr[0].cpu().numpy() if isinstance(arr, torch.Tensor) else arr[0] for arr in labels_batch]

            # Calculate loss on the current window (generated with current eta)
            window_result = self._evaluate_window(
                time_series_single_window,
                sources_num_single_window_list,
                labels_single_window_list_of_arrays,
                trajectory_idx,
                window_idx,
                is_first_window=(window_idx == 0),
                last_ekf_predictions=last_ekf_predictions,
                last_ekf_covariances=last_ekf_covariances
            )

            # Add window result to trajectory results
            trajectory_results.add_window_result(window_idx, window_result, self.system_model.params.eta, labels_single_window_list_of_arrays)

            # GLRT drift detection on trajectory results
            # Extract losses for GLRT analysis
            min_segment_size = 5  # Minimum windows needed for GLRT
            # Need at least 2*min_segment_size+1 windows to have at least one candidate changepoint
            if len(trajectory_results.window_results) >= 2 * min_segment_size + 1:
                # Extract online_training_reference_loss values
                ref_losses = [wr.loss_metrics.online_training_reference_loss for wr in trajectory_results.window_results]

                # Extract main_loss values
                main_losses = [wr.loss_metrics.main_loss for wr in trajectory_results.window_results]

                # Run GLRT on reference loss
                try:
                    ref_changepoint, ref_log_glr, ref_all_log_glr, ref_candidate_points = glrt_changepoint_detection(ref_losses, min_segment_size=min_segment_size)
                    glrt_ref_loss_changepoint_window = ref_changepoint
                    glrt_ref_loss_likelihood = ref_log_glr
                    glrt_ref_loss_all_log_glr = ref_all_log_glr
                    glrt_ref_loss_candidate_points = ref_candidate_points
                    glrt_ref_losses = ref_losses
                    logger.info(f"GLRT (ref_loss) - Window {window_idx}: Changepoint at window {ref_changepoint}, Log-GLR: {ref_log_glr:.4f}")
                except Exception as e:
                    logger.warning(f"GLRT (ref_loss) failed at window {window_idx}: {e}")

                # Run GLRT on main loss
                try:
                    main_changepoint, main_log_glr, main_all_log_glr, main_candidate_points = glrt_changepoint_detection(main_losses, min_segment_size=min_segment_size)
                    glrt_main_loss_changepoint_window = main_changepoint
                    glrt_main_loss_likelihood = main_log_glr
                    glrt_main_loss_all_log_glr = main_all_log_glr
                    glrt_main_loss_candidate_points = main_candidate_points
                    glrt_main_losses = main_losses
                    logger.info(f"GLRT (main_loss) - Window {window_idx}: Changepoint at window {main_changepoint}, Log-GLR: {main_log_glr:.4f}")
                except Exception as e:
                    logger.warning(f"GLRT (main_loss) failed at window {window_idx}: {e}")

            # Update last predictions and covariances for next window
            last_ekf_predictions = window_result.doa_metrics.ekf_predictions
            last_ekf_covariances = window_result.step_metrics.covariances

            logger.info(f"Window {window_idx}: Main Loss = {window_result.loss_metrics.main_loss:.6f} ({window_result.loss_metrics.main_loss_config}), Cov = {window_result.window_metrics.avg_covariance:.6f} (current eta={self.system_model.params.eta:.4f})")

            # Log all loss metrics for comparison
            logger.info(f"Window {window_idx}: Pre-EKF Loss = {window_result.loss_metrics.pre_ekf_loss:.6f}, Main Loss = {window_result.loss_metrics.main_loss:.6f} ({window_result.loss_metrics.main_loss_config}), Training Ref Loss = {window_result.loss_metrics.online_training_reference_loss:.6f} ({window_result.loss_metrics.online_training_reference_loss_config}), Cov = {window_result.window_metrics.avg_covariance:.6f} (eta={self.system_model.params.eta:.4f})")

            # Store trained model results for comparison
            trained_subspacenet_loss = window_result.loss_metrics.pre_ekf_loss
            trained_ekf_loss = window_result.loss_metrics.main_loss

            # Check if loss exceeds threshold (drift detected)
            if window_result.loss_metrics.main_loss > loss_threshold:
                logger.info(f"Drift detected in window {window_idx} (loss: {window_result.loss_metrics.main_loss:.6f} > threshold: {loss_threshold:.6f})")
                # window_update_flags.append(False)
                # self.drift_detected = True
                # Track when learning started
                # if self.learning_start_window is None:
                #     self.learning_start_window = window_idx
                #     logger.info(f"Online learning started at window {window_idx}")
            else:
                logger.info(f"No drift detected in window {window_idx} (loss: {window_result.loss_metrics.main_loss:.6f} <= threshold: {loss_threshold:.6f})")
                window_update_flags.append(False)
                # Keep previous drift_detected state if no drift in current window

            # Dual model processing logic
            if self.drift_detected:
                if self.learning_done:
                    # Online model finished training, evaluate it normally
                    logger.info(f"Evaluating online model (post-training) for window {window_idx}")
                    online_window_result = self._evaluate_window(
                        time_series_single_window,
                        sources_num_single_window_list,
                        labels_single_window_list_of_arrays,
                        trajectory_idx,
                        window_idx,
                        is_first_window=(window_idx == 0),
                        last_ekf_predictions=online_last_ekf_predictions,
                        last_ekf_covariances=online_last_ekf_covariances,
                        model=self.online_model
                    )

                    # Add online model result to trajectory results
                    online_trajectory_results.add_window_result(window_idx, online_window_result, self.system_model.params.eta, labels_single_window_list_of_arrays)

                    logger.info(f"Online model - Window {window_idx}: Main Loss = {online_window_result.loss_metrics.main_loss:.6f} ({online_window_result.loss_metrics.main_loss_config}), Cov = {online_window_result.window_metrics.avg_covariance:.6f}")

                    # Log online learning window summary (post-learning evaluation)
                    log_online_learning_window_summary(
                        subspacenet_loss=trained_subspacenet_loss,
                        ekf_loss=trained_ekf_loss,
                        online_ekf_loss=online_window_result.loss_metrics.main_loss,
                        current_eta=self.system_model.params.eta,
                        is_near_field=hasattr(self.trained_model, 'field_type') and self.trained_model.field_type.lower() == "near",
                        trajectory_idx=trajectory_idx,
                        window_idx=window_idx,
                        is_learning=False
                    )

                    # Evaluate supervised trained model (post-training)
                    logger.info(f"Evaluating supervised trained model (post-training) for window {window_idx}")
                    supervised_window_result = self._evaluate_window(
                        time_series_single_window,
                        sources_num_single_window_list,
                        labels_single_window_list_of_arrays,
                        trajectory_idx,
                        window_idx,
                        is_first_window=(window_idx == 0),
                        last_ekf_predictions=supervised_last_ekf_predictions,
                        last_ekf_covariances=supervised_last_ekf_covariances,
                        model=self.supervised_trained_model
                    )

                    # Add supervised model result to trajectory results
                    supervised_trajectory_results.add_window_result(window_idx, supervised_window_result, self.system_model.params.eta, labels_single_window_list_of_arrays)

                    logger.info(f"Supervised trained model - Window {window_idx}: Main Loss = {supervised_window_result.loss_metrics.main_loss:.6f} ({supervised_window_result.loss_metrics.main_loss_config}), Cov = {supervised_window_result.window_metrics.avg_covariance:.6f}")

                    # Update supervised EKF state for next window
                    supervised_last_ekf_predictions = supervised_window_result.doa_metrics.ekf_predictions
                    supervised_last_ekf_covariances = supervised_window_result.step_metrics.covariances

                    # Update online EKF state for next window
                    # online_window_result.doa_metrics.ekf_predictions is already in tensor format
                    online_last_ekf_predictions = online_window_result.doa_metrics.ekf_predictions
                    online_last_ekf_covariances = online_window_result.step_metrics.covariances
                else:
                    # Online model still learning/adapting
                    logger.info(f"Training online model for window {window_idx}")

                    # Track training start on first training call
                    if training_start_window is None:
                        training_start_window = window_idx
                        logger.info(f"Training started at window {window_idx}")

                    # Call the refactored _online_training_window method
                    training_result = self._online_training_window(
                        time_series_single_window,
                        sources_num_single_window_list,
                        labels_single_window_list_of_arrays,
                        trajectory_idx,
                        window_idx,
                        is_first_window=(window_idx == 0),
                        last_ekf_predictions=online_last_ekf_predictions,
                        last_ekf_covariances=online_last_ekf_covariances
                    )

                    # Add training result to online trajectory results
                    online_trajectory_results.add_window_result(window_idx, training_result, self.system_model.params.eta, labels_single_window_list_of_arrays)

                    logger.info(f"Online training - Window {window_idx}: Main Loss = {training_result.loss_metrics.main_loss:.6f} ({training_result.loss_metrics.main_loss_config}), Cov = {training_result.window_metrics.avg_covariance:.6f}, Pre-EKF Loss = {training_result.loss_metrics.pre_ekf_loss:.6f}")

                    # Log online learning window summary (learning phase)
                    log_online_learning_window_summary(
                        subspacenet_loss=trained_subspacenet_loss,
                        ekf_loss=trained_ekf_loss,
                        online_ekf_loss=training_result.loss_metrics.main_loss,
                        current_eta=self.system_model.params.eta,
                        is_near_field=hasattr(self.trained_model, 'field_type') and self.trained_model.field_type.lower() == "near",
                        trajectory_idx=trajectory_idx,
                        window_idx=window_idx,
                        is_learning=True
                    )

                    # Check if training just ended (learning_done became True)
                    if self.learning_done and training_end_window is None:
                        training_end_window = window_idx
                        logger.info(f"Training ended at window {window_idx}")

                    # Update online EKF state for next window
                    # training_result.doa_metrics.ekf_predictions is already in tensor format
                    online_last_ekf_predictions = training_result.doa_metrics.ekf_predictions
                    online_last_ekf_covariances = training_result.step_metrics.covariances

                    # Train supervised model with supervised loss configuration
                    logger.info(f"Training supervised trained model for window {window_idx}")

                    # Create supervised loss config object
                    from copy import deepcopy
                    supervised_loss_config = deepcopy(self.config.online_learning.loss_config)
                    # Override the training_loss_type with supervised_loss_type
                    supervised_loss_config.training_loss_type = self.config.online_learning.loss_config.supervised_loss_type

                    supervised_training_result = self._online_training_window(
                        time_series_single_window,
                        sources_num_single_window_list,
                        labels_single_window_list_of_arrays,
                        trajectory_idx,
                        window_idx,
                        is_first_window=(window_idx == 0),
                        last_ekf_predictions=supervised_last_ekf_predictions,
                        last_ekf_covariances=supervised_last_ekf_covariances,
                        model=self.supervised_trained_model,
                        loss_config_override=supervised_loss_config
                    )

                    # Add supervised training result to supervised trajectory results
                    supervised_trajectory_results.add_window_result(window_idx, supervised_training_result, self.system_model.params.eta, labels_single_window_list_of_arrays)

                    logger.info(f"Supervised training - Window {window_idx}: Main Loss = {supervised_training_result.loss_metrics.main_loss:.6f} ({supervised_training_result.loss_metrics.main_loss_config}), Cov = {supervised_training_result.window_metrics.avg_covariance:.6f}, Pre-EKF Loss = {supervised_training_result.loss_metrics.pre_ekf_loss:.6f}")

                    # Update supervised EKF state for next window
                    supervised_last_ekf_predictions = supervised_training_result.doa_metrics.ekf_predictions
                    supervised_last_ekf_covariances = supervised_training_result.step_metrics.covariances

        # Save final model if it was updated
        if model_updated_count > 0:
            model_save_path = save_model_state(
                self.trained_model,
                self.output_dir,
                model_type=f"{self.config.model.type}_online_updated"
            )
            logger.info(f"Saved final online-updated model to {model_save_path}")

        # Return results
        return {
            "status": "success",
            "online_learning_results": {
                # Model results
                "pretrained_model_trajectory_results": trajectory_results,
                "online_model_trajectory_results": online_trajectory_results,
                "supervised_model_trajectory_results": supervised_trajectory_results,

                # Learning metadata
                "window_updates": window_update_flags,
                "drift_detected_count": drift_detected_count,
                "model_updated_count": model_updated_count,
                "window_count": len(online_learning_dataloader),
                "window_size": online_config.window_size,
                "stride": online_config.stride,
                "loss_threshold": loss_threshold,
                "learning_start_window": self.learning_start_window,

                # Learning state tracking
                "drift_detected_final": self.drift_detected,
                "learning_done_final": self.learning_done,
                "first_eta_change_final": self.first_eta_change,
                "online_training_count_final": self.online_training_count,

                # Training and eta change tracking
                "eta_change_windows": eta_change_windows,
                "training_start_window": training_start_window,
                "training_end_window": training_end_window,

                # GLRT drift detection results
                "glrt_ref_loss_changepoint_window": glrt_ref_loss_changepoint_window,
                "glrt_ref_loss_likelihood": glrt_ref_loss_likelihood,
                "glrt_ref_losses": glrt_ref_losses,
                "glrt_main_loss_changepoint_window": glrt_main_loss_changepoint_window,
                "glrt_main_loss_likelihood": glrt_main_loss_likelihood,
                "glrt_main_losses": glrt_main_losses
            }
        }

    except Exception as e:
        logger.exception(f"Error during online learning: {e}")
        return {"status": "error", "message": str(e), "exception": type(e).__name__}
