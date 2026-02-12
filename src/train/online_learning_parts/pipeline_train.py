from __future__ import annotations

from typing import Optional
import torch
import torch.optim as optim

from src.train.online_learning import (
    logger,
    device,
    WindowEvaluationResult,
)
from src.eval.metrics.rmspe_loss import RMSPELoss
from src.eval.metrics.rmape_loss import RMAPELoss
from simulation.kalman_filter.extended import ExtendedKalmanFilter1D

def _online_training_window_impl(self, window_time_series, window_sources_num, window_labels, trajectory_idx: int = 0, window_idx: int = 0, 
                           is_first_window: bool = True, last_ekf_predictions: Optional[torch.Tensor] = None, 
                           last_ekf_covariances: Optional[torch.Tensor] = None, model=None, loss_config_override=None) -> WindowEvaluationResult:
    """
    Train the provided model on a single window, then evaluate it like _evaluate_window.

    This function performs the same evaluation as _evaluate_window but adds a training step
    after the model forward pass and before the Kalman filter processing.

    Args:
        model: Model to train (defaults to self.online_model if None)
        loss_config_override: Optional loss configuration override (defaults to online loss config if None)

    Args:
        window_time_series: Time series data for window
        window_sources_num: Source counts for window  
        window_labels: Labels for window
        trajectory_idx: Index of the current trajectory
        window_idx: Index of the current window within the trajectory
        is_first_window: Whether this is the first window
        last_ekf_predictions: Last EKF predictions from previous window (tensor format)
        last_ekf_covariances: Last EKF covariances from previous window (tensor format)

    Returns:
        WindowEvaluationResult containing all metrics and data
    """
    # Increment training counter
    self.online_training_count += 1
    logger.info(f"Online training step {self.online_training_count} called for trajectory {trajectory_idx}, window {window_idx}")

    # Set learning done after 7 training calls
    if self.online_training_count >= 10:
        self.learning_done = True
        logger.info(f"Online model training completed after {self.online_training_count} training windows")

    # Debug: Log input shapes
    logger.debug(f"_online_training_window input shapes: "
                 f"window_time_series={window_time_series.shape if hasattr(window_time_series, 'shape') else 'not tensor'}, "
                 f"window_sources_num={len(window_sources_num)}, "
                 f"window_labels={len(window_labels)}")

    # Unpack arguments directly, assuming they are for a single window
    time_series_steps = window_time_series  # Already [window_size, N, T]
    sources_num_per_step = window_sources_num  # List[int]
    labels_per_step_list = window_labels  # List[np.ndarray]

    # Validate inputs
    current_window_len, error_message = self._validate_inputs(time_series_steps, sources_num_per_step, labels_per_step_list)
    if error_message:
        logger.error(error_message)
        return WindowEvaluationResult.create_error_result(error_message)

    # Use provided model or default to online_model
    training_model = model if model is not None else self.online_model

    # Check if we're dealing with far-field or near-field
    is_near_field = hasattr(training_model, 'field_type') and training_model.field_type.lower() == "near"

    # Use RMSPE loss for evaluation
    rmspe_criterion = RMSPELoss().to(device)

    # Use RMAPE loss for online training
    rmape_criterion = RMAPELoss().to(device)

    # Set up optimizer for training
    if training_model is self.online_model:
        # Use online optimizer for online model
        if not hasattr(self, 'online_optimizer'):
            self.online_optimizer = optim.Adam(self.online_model.parameters(), lr=1e-3)
        optimizer = self.online_optimizer
    elif training_model is self.supervised_trained_model:
        # Use supervised optimizer for supervised model
        if not hasattr(self, 'supervised_optimizer'):
            self.supervised_optimizer = optim.Adam(self.supervised_trained_model.parameters(), lr=1e-3)
        optimizer = self.supervised_optimizer
    else:
        # Fallback: create a temporary optimizer
        optimizer = optim.Adam(training_model.parameters(), lr=1e-3)

    # Initialize Extended Kalman Filters
    max_sources = self.config.system_model.M
    ekf_filters = self._initialize_ekf_filters(max_sources, window_idx, 0)

    # Get current eta value from system model
    current_eta = self.system_model.params.eta
    logger.info(f"Online training: Initialized {max_sources} EKF instances for window (eta={current_eta:.4f})")

    # Training phase: Run gradient descent steps per window
    training_model.train()  # Set to training mode
    total_training_loss = 0.0
    num_training_steps = 0

    # Number of gradient descent steps per window
    num_gd_steps = 5

    # Get loss configuration for training (use override if provided)
    base_loss_config = getattr(self.config.online_learning, 'loss_config', None)
    if loss_config_override is not None:
        loss_config = loss_config_override
    else:
        loss_config = base_loss_config
    windows_last_ekf_covariances = last_ekf_covariances
    windows_last_ekf_predictions = last_ekf_predictions
    for gd_step in range(num_gd_steps):
        # Zero gradients at the start of each GD step
        optimizer.zero_grad()

        # Collect step results for window-level loss calculation
        # Each GD iteration processes the entire window and calculates window-level loss
        window_step_results = []  # Store step results for window-level loss calculation
        step_count = 0
        last_ekf_covariances = windows_last_ekf_covariances
        last_ekf_predictions = windows_last_ekf_predictions
        # Process each step for training in this gradient descent iteration
        for step in range(current_window_len):
            try:
                # Extract data for this step
                step_data_tensor = time_series_steps[step:step+1].to(device)  # Shape: [1, N, T]
                num_sources_this_step = sources_num_per_step[step]

                # Skip if no sources
                if num_sources_this_step <= 0:
                    continue
                if step ==0:
                    last_ekf_predictions = windows_last_ekf_predictions
                    last_ekf_covariances = windows_last_ekf_covariances

                # Get ground truth labels for this step
                true_angles_this_step = labels_per_step_list[step][:num_sources_this_step]

                if not is_near_field:
                    # Forward pass through training model (with gradients for training)
                    angles_pred, _, _ = training_model(step_data_tensor, num_sources_this_step)

                    # Convert predictions and true angles to proper format
                    # Ensure angles_pred_tensor has shape [1, num_sources] for loss functions
                    if angles_pred.dim() == 3:  # [batch, channels, sources] -> [batch, sources]
                        angles_pred_tensor = angles_pred.squeeze(1)[:, :num_sources_this_step]
                    elif angles_pred.dim() == 2:  # [batch, sources] or [batch, features]
                        angles_pred_tensor = angles_pred.view(1, -1)[:, :num_sources_this_step]
                    else:  # [sources] -> [1, sources]
                        angles_pred_tensor = angles_pred.view(1, -1)[:, :num_sources_this_step]

                    # Ensure true_angles_tensor has shape [1, num_sources]
                    true_angles_tensor = torch.tensor(true_angles_this_step, device=device).unsqueeze(0)  # Shape: [1, num_sources]

                    # Get optimal permutation for training
                    angles_pred_np = angles_pred.detach().cpu().numpy().flatten()[:num_sources_this_step]
                    model_perm = self._get_optimal_permutation(angles_pred_np, true_angles_this_step)
                    angles_pred_tensor = angles_pred_tensor[:, model_perm]
                    angles_pred_np = angles_pred_np[model_perm].flatten()

                    # ============ EKF Processing for Training ============
                    # Initialize EKF for this training step (create fresh filters for each step)
                    # Calculate initial time for training EKF filters
                    window_size = self.config.online_learning.window_size
                    training_initial_time = window_idx * window_size + step

                    # Initialize training EKF filters (separate from evaluation EKF)
                    self.training_ekf_filters = []
                    for i in range(num_sources_this_step):
                        training_ekf = ExtendedKalmanFilter1D.create_from_config(
                            self.config, 
                            trajectory_type=self.config.trajectory.trajectory_type,
                            device=device,
                            source_idx=i,  # Pass source index to use source-specific parameters
                            initial_time=training_initial_time  # Pass initial time for correct oscillatory behavior
                        )
                        self.training_ekf_filters.append(training_ekf)

                    # Use the _initialize_ekf_state method to properly initialize state and covariance
                    # This ensures we use the last predictions and covariances from the previous window
                    self._initialize_ekf_state(
                        step=0, 
                        num_sources_this_step=num_sources_this_step, 
                        true_angles_this_step=true_angles_this_step,
                        ekf_filters=self.training_ekf_filters, 
                        is_first_window=False,  # Not first window since we're in online training
                        last_ekf_predictions=last_ekf_predictions, 
                        last_ekf_covariances=last_ekf_covariances
                    )

                    # Apply EKF to each source prediction using tensor inputs to preserve gradients
                    ekf_angles_pred = []
                    ekf_covariances_pred = []
                    kalman_gain_times_innovation_list = []  # Collect K*y for training
                    y_s_inv_y_list = []  # Collect y*S^-1*y for training
                    step_Innovation_Covariance_list = []  # Collect Innovation Covariance for training
                    for i in range(num_sources_this_step):
                        if i < len(self.training_ekf_filters) and i < angles_pred_tensor.size(2):
                            ekf_filter = self.training_ekf_filters[i]

                            # Use tensor measurement to preserve gradients (shape: [batch, seq, sources])
                            tensor_measurement = angles_pred_tensor[0, 0, i]

                            # EKF predict and update with tensor measurement
                            _, updated_state, _, kalman_gain, kalman_gain_times_innovation, y_s_inv_y,Innovation_Covariance = ekf_filter.predict_and_update(
                                measurement=tensor_measurement, 
                                true_state=true_angles_this_step[i]
                            )

                            # Verify tensors maintain gradients - fail hard if not
                            if not isinstance(updated_state, torch.Tensor):
                                raise RuntimeError(f"EKF updated_state is not a tensor: {type(updated_state)}. EKF must return tensors for gradient computation.")
                            if not updated_state.requires_grad:
                                raise RuntimeError(f"EKF updated_state tensor does not require gradients. This breaks the computation graph.")

                            # Verify kalman_gain_times_innovation maintains gradients
                            if not isinstance(kalman_gain_times_innovation, torch.Tensor):
                                raise RuntimeError(f"EKF kalman_gain_times_innovation is not a tensor: {type(kalman_gain_times_innovation)}. EKF must return tensors for gradient computation.")
                            if not kalman_gain_times_innovation.requires_grad:
                                raise RuntimeError(f"EKF kalman_gain_times_innovation tensor does not require gradients. This breaks the computation graph.")

                            # Verify y_s_inv_y maintains gradients
                            if not isinstance(y_s_inv_y, torch.Tensor):
                                raise RuntimeError(f"EKF y_s_inv_y is not a tensor: {type(y_s_inv_y)}. EKF must return tensors for gradient computation.")
                            if not y_s_inv_y.requires_grad:
                                raise RuntimeError(f"EKF y_s_inv_y tensor does not require gradients. This breaks the computation graph.")

                            # Ensure updated_state is a scalar tensor for consistent stacking
                            if updated_state.dim() > 0:
                                updated_state_scalar = updated_state.flatten()[0]  # Take first element if multi-dimensional
                            else:
                                updated_state_scalar = updated_state
                            ekf_angles_pred.append(updated_state_scalar)
                            ekf_covariances_pred.append(ekf_filter.P)
                            kalman_gain_times_innovation_list.append(kalman_gain_times_innovation)
                            y_s_inv_y_list.append(y_s_inv_y)
                            step_Innovation_Covariance_list.append(Innovation_Covariance)
                        else:
                            # No fallback - fail hard if EKF not available or index out of bounds
                            if i >= len(self.training_ekf_filters):
                                raise RuntimeError(f"EKF filter index {i} out of bounds. Expected {len(self.training_ekf_filters)} training EKF filters but got {num_sources_this_step} sources.")
                            if i >= angles_pred_tensor.size(2):
                                raise RuntimeError(f"Source index {i} out of bounds for tensor shape {angles_pred_tensor.shape}. Cannot access source {i} from {angles_pred_tensor.size(2)} sources.")
                            raise RuntimeError(f"EKF filter {i} not available but should be. This indicates a serious configuration error.")

                    # Create EKF predictions tensor
                    # Ensure ekf_angles_pred_tensor has shape [1, num_sources] for loss functions
                    ekf_angles_pred_tensor = torch.stack(ekf_angles_pred).unsqueeze(0)  # Shape: [1, num_sources]
                    logger.debug(f"EKF predictions tensor shape: {ekf_angles_pred_tensor.shape} (expected [1, {num_sources_this_step}])")
                    ekf_covariances_tensor = torch.stack(ekf_covariances_pred).view(1, -1)  # Shape: [1, num_sources]
                    step_Innovation_Covariance_tensor = torch.stack(step_Innovation_Covariance_list).view(1, -1)  # Shape: [1, num_sources]
                    last_ekf_predictions = ekf_angles_pred_tensor
                    last_ekf_covariances = ekf_covariances_tensor
                    # Minimal contract checks for downstream window-loss aggregation.
                    if angles_pred_tensor.device != true_angles_tensor.device:
                        raise RuntimeError(
                            f"Device mismatch in training step {step}: "
                            f"pred={angles_pred_tensor.device}, true={true_angles_tensor.device}"
                        )
                    if step_Innovation_Covariance_tensor.dim() != 2 or step_Innovation_Covariance_tensor.shape[0] != 1:
                        raise RuntimeError(
                            f"Invalid innovation covariance tensor shape in training step {step}: "
                            f"{tuple(step_Innovation_Covariance_tensor.shape)}"
                        )
                    if step_Innovation_Covariance_tensor.shape[1] != num_sources_this_step:
                        raise RuntimeError(
                            f"Innovation covariance source-count mismatch in training step {step}: "
                            f"expected {num_sources_this_step}, got {step_Innovation_Covariance_tensor.shape[1]}"
                        )

                    # Store step results for window-level loss calculation
                    step_result = {
                        'success': True,
                        'pre_ekf_angles_pred_tensor': angles_pred_tensor,  # Tensor for window-level loss calculation
                        'ekf_angles_pred_tensor': ekf_angles_pred_tensor,  # Tensor for window-level loss calculation
                        'true_angles_tensor': true_angles_tensor,  # Tensor for window-level loss calculation
                        'num_sources': num_sources_this_step,
                        # Canonical key for innovation covariance tensor in training path.
                        'step_innovation_covariance_tensor': step_Innovation_Covariance_tensor,
                        # Backward-compatibility alias (legacy key).
                        'Innovation_Covariance_tensor': step_Innovation_Covariance_tensor
                    }

                    # Store step result for window-level loss calculation
                    window_step_results.append(step_result)
                    step_count += 1

                    logger.debug(f"Training step {step}, GD {gd_step}: Collected step result for window-level loss calculation")

                else:
                    # Near-field fallback: bypass EKF and use model prediction directly.
                    # This keeps online training operational when near-field EKF path is unavailable.
                    logger.warning(
                        "Near-field EKF path is unavailable. Falling back to direct model-prediction training for this step."
                    )
                    angles_pred, _, _ = training_model(step_data_tensor, num_sources_this_step)

                    if angles_pred.dim() == 3:
                        angles_pred_tensor = angles_pred.squeeze(1)[:, :num_sources_this_step]
                    elif angles_pred.dim() == 2:
                        angles_pred_tensor = angles_pred.view(1, -1)[:, :num_sources_this_step]
                    else:
                        angles_pred_tensor = angles_pred.view(1, -1)[:, :num_sources_this_step]

                    true_angles_tensor = torch.tensor(true_angles_this_step, device=device).unsqueeze(0)
                    angles_pred_np = angles_pred_tensor.detach().cpu().numpy().flatten()[:num_sources_this_step]
                    model_perm = self._get_optimal_permutation(angles_pred_np, true_angles_this_step)
                    angles_pred_tensor = angles_pred_tensor[:, model_perm]

                    # Keep API-compatible tensors for downstream unified loss calculation.
                    ekf_angles_pred_tensor = angles_pred_tensor.clone()
                    step_Innovation_Covariance_tensor = torch.ones_like(ekf_angles_pred_tensor)
                    last_ekf_predictions = ekf_angles_pred_tensor
                    last_ekf_covariances = torch.ones_like(ekf_angles_pred_tensor)

                    if angles_pred_tensor.device != true_angles_tensor.device:
                        raise RuntimeError(
                            f"Device mismatch in near-field training step {step}: "
                            f"pred={angles_pred_tensor.device}, true={true_angles_tensor.device}"
                        )
                    if step_Innovation_Covariance_tensor.dim() != 2 or step_Innovation_Covariance_tensor.shape[0] != 1:
                        raise RuntimeError(
                            f"Invalid near-field innovation covariance tensor shape in training step {step}: "
                            f"{tuple(step_Innovation_Covariance_tensor.shape)}"
                        )
                    if step_Innovation_Covariance_tensor.shape[1] != num_sources_this_step:
                        raise RuntimeError(
                            f"Near-field innovation covariance source-count mismatch in training step {step}: "
                            f"expected {num_sources_this_step}, got {step_Innovation_Covariance_tensor.shape[1]}"
                        )

                    step_result = {
                        'success': True,
                        'pre_ekf_angles_pred_tensor': angles_pred_tensor,
                        'ekf_angles_pred_tensor': ekf_angles_pred_tensor,
                        'true_angles_tensor': true_angles_tensor,
                        'num_sources': num_sources_this_step,
                        # Canonical key for innovation covariance tensor in training path.
                        'step_innovation_covariance_tensor': step_Innovation_Covariance_tensor,
                        # Backward-compatibility alias (legacy key).
                        'Innovation_Covariance_tensor': step_Innovation_Covariance_tensor
                    }
                    window_step_results.append(step_result)
                    step_count += 1

            except Exception as e:
                logger.warning(f"Error during online training step {step} in GD iteration {gd_step}: {e}")
                continue

        # Calculate window-level loss and perform backpropagation
        if step_count > 0 and len(window_step_results) > 0:
            # Unified window-level loss calculation
            window_loss = self._calculate_window_training_loss(window_step_results, loss_config, rmspe_criterion, rmape_criterion)
            logger.info(f"GD step {gd_step + 1}: Window loss = {window_loss.item():.6f} over {step_count} steps")

            # Backward pass on the window loss
            window_loss.backward()

            # Check if gradients were computed properly
            gradients_ok = self._check_gradients(training_model, step_count, gd_step)

            # Update model parameters
            optimizer.step()
            # Zero gradients after optimizer step to prepare for next GD iteration
            optimizer.zero_grad()

            total_training_loss += window_loss.item()
            num_training_steps += 1  # Count each GD step, not each individual step
            logger.info(f"Online training GD step {gd_step + 1}/{num_gd_steps}: Updated model with window loss = {window_loss.item():.6f} over {step_count} steps")
        else:
            logger.warning(f"No valid training steps in GD iteration {gd_step} for window {window_idx}")

    # Calculate overall average training loss across all GD iterations
    # Note: num_training_steps now counts GD iterations, not individual steps
    if num_training_steps > 0:
        avg_training_loss = total_training_loss / num_training_steps
        logger.info(f"Online training step {self.online_training_count}: Completed {num_gd_steps} GD iterations with overall avg loss = {avg_training_loss:.6f} over {num_training_steps} GD steps")
    else:
        avg_training_loss = float('inf')  # Set default value if no training steps
        logger.warning(f"No valid training steps in window {window_idx}")

    # Set model back to eval mode for EKF evaluation
    training_model.eval()

    # Clean up training EKF filters to free memory
    if hasattr(self, 'training_ekf_filters'):
        delattr(self, 'training_ekf_filters')
        logger.debug(f"Cleaned up training EKF filters after window {window_idx}")

    # Now evaluate the trained model with EKF using the same pattern as _evaluate_window
    # Process each step in window
    step_results_list = []
    last_ekf_predictions = windows_last_ekf_predictions
    last_ekf_covariances = windows_last_ekf_covariances
    for step in range(current_window_len):
        # Initialize EKF state if this is the first step
        num_sources_this_step = sources_num_per_step[step]
        true_angles_this_step = labels_per_step_list[step][:num_sources_this_step]

        self._initialize_ekf_state(step, num_sources_this_step, true_angles_this_step, 
                                 ekf_filters, is_first_window, last_ekf_predictions, last_ekf_covariances)

        # Process single step
        success, step_result = self._process_single_step(
            step, time_series_steps, sources_num_per_step, labels_per_step_list,
            ekf_filters, training_model, is_near_field, False
        )

        step_results_list.append(step_result)

    # Use loss config override if provided, otherwise use default
    effective_loss_config = loss_config_override if loss_config_override is not None else loss_config

    # Calculate aggregated metrics using the same helper method
    result = self._calculate_metrics(step_results_list, current_window_len, max_sources, current_eta, is_near_field, effective_loss_config)

    # Log window summary
    if result.is_valid:
        logger.info(f"Online training window {window_idx}: "
                   f"Pre-EKF Loss = {result.loss_metrics.pre_ekf_loss:.6f}, "
                   f"Main Loss = {result.loss_metrics.main_loss:.6f} ({result.loss_metrics.main_loss_config}), "
                   f"Avg Cov = {result.window_metrics.avg_covariance:.6f}, "
                   f"Training Loss = {avg_training_loss:.6f}")

    return result
