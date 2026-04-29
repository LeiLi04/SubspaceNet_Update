from __future__ import annotations

from typing import Dict, Optional, List, Tuple
import numpy as np
import torch

from src.trainer_module.online_learning import (
    logger,
    device,
    WindowEvaluationResult,
)
from src.utils.utils import log_window_summary
from simulation.kalman_filter.extended import ExtendedKalmanFilter1D


def _normalize_prediction_tensor(angles_pred: torch.Tensor, num_sources_this_step: int) -> torch.Tensor:
    """
    Normalize model prediction tensor to shape [1, num_sources].
    """
    if angles_pred.dim() == 3:  # [batch, channels, sources] -> [batch, sources]
        return angles_pred.squeeze(1)[:, :num_sources_this_step]
    if angles_pred.dim() == 2:  # [batch, sources] or [batch, features]
        return angles_pred.view(1, -1)[:, :num_sources_this_step]
    # [sources] -> [1, sources]
    return angles_pred.view(1, -1)[:, :num_sources_this_step]


def _build_step_result(
    *,
    step_predictions: List[torch.Tensor],
    step_covariances: List[torch.Tensor],
    step_innovations: List[torch.Tensor],
    step_kalman_gains: List[torch.Tensor],
    step_kalman_gain_times_innovation: List[torch.Tensor],
    step_y_s_inv_y: List[torch.Tensor],
    pre_ekf_angles_pred: torch.Tensor,
    ekf_angles_pred: torch.Tensor,
    true_angles_tensor: torch.Tensor,
    num_sources_this_step: int,
    step_innovation_covariance: List[torch.Tensor],
) -> Dict:
    """
    Build unified step-result payload with canonical and legacy-compatible keys.
    """
    return {
        'success': True,
        'step_predictions': step_predictions,
        'step_covariances': step_covariances,
        'step_innovations': step_innovations,
        'step_kalman_gains': step_kalman_gains,
        'step_kalman_gain_times_innovation': step_kalman_gain_times_innovation,
        'step_y_s_inv_y': step_y_s_inv_y,
        'pre_ekf_angles_pred_tensor': pre_ekf_angles_pred,
        'ekf_angles_pred_tensor': ekf_angles_pred,
        'true_angles_tensor': true_angles_tensor,
        'num_sources': num_sources_this_step,
        'step_innovation_covariance': step_innovation_covariance,
        'step_Innovation_Covariance': step_innovation_covariance,
    }


def _check_gradients_impl(self, model, step: int, gd_step: int) -> bool:
    """
    Check if gradients were properly computed after backward pass.

    Args:
        model: The model to check gradients for
        step: Current training step
        gd_step: Current gradient descent step

    Returns:
        bool: True if gradients exist and are finite, False otherwise
    """
    has_gradients = False
    total_norm = 0
    num_params_with_grad = 0

    for name, param in model.named_parameters():
        if param.grad is not None:
            has_gradients = True
            num_params_with_grad += 1

            # Check for NaN or inf gradients
            if torch.isnan(param.grad).any() or torch.isinf(param.grad).any():
                logger.error(f"NaN/Inf gradients detected in {name} at step {step}, GD {gd_step}")
                return False

            param_norm = param.grad.data.norm(2)
            total_norm += param_norm.item() ** 2

    if has_gradients:
        total_norm = total_norm ** (1. / 2)
        logger.debug(f"Step {step}, GD {gd_step}: {num_params_with_grad} params have gradients, norm: {total_norm:.6f}")
        return True
    else:
        logger.warning(f"No gradients computed in step {step}, GD {gd_step}")
        return False



def _validate_inputs_impl(self, window_time_series: torch.Tensor, window_sources_num: List[int], 
                    window_labels: List[np.ndarray]) -> Tuple[int, str]:
    """
    Validate input data for window evaluation.

    Args:
        window_time_series: Time series data for window [window_size, N, T]
        window_sources_num: Source counts for window [window_size]
        window_labels: Labels for window [window_size]

    Returns:
        Tuple of (valid_window_size, error_message). If valid, error_message is empty string.
    """
    current_window_len = window_time_series.shape[0]

    # Sanity check the input lengths
    if len(window_sources_num) < current_window_len:
        logger.warning(f"Window source count list length ({len(window_sources_num)}) is less than time series length ({current_window_len}). Truncating window.")
        current_window_len = len(window_sources_num)

    if len(window_labels) < current_window_len:
        logger.warning(f"Window labels list length ({len(window_labels)}) is less than time series length ({current_window_len}). Truncating window.")
        current_window_len = len(window_labels)

    if current_window_len == 0:
        return 0, "Window has zero valid steps. Cannot evaluate."

    return current_window_len, ""



def _initialize_ekf_filters_impl(self, max_sources: int, window_idx: int = 0, step_idx: int = 0) -> List[ExtendedKalmanFilter1D]:
    """
    Initialize Extended Kalman Filters for window evaluation.

    Args:
        max_sources: Maximum number of sources to track
        window_idx: Index of the current window (used to calculate initial time)
        step_idx: Index of the current step within the window (used to calculate initial time)

    Returns:
        List of initialized EKF filter instances, each with source-specific parameters
    """
    # Calculate the initial time based on window and step indices
    # This ensures the EKF filters start with the correct time for oscillatory models
    window_size = self.config.online_learning.window_size
    initial_time = window_idx * window_size + step_idx

    ekf_filters = []

    # Create EKF filters for each source with source-specific parameters
    for i in range(max_sources):
        # Create EKF filter with source index i - the filter will use source-specific parameters
        ekf_filter = ExtendedKalmanFilter1D.create_from_config(
            self.config, 
            trajectory_type=self.config.trajectory.trajectory_type,
            device=device,
            source_idx=i,  # Pass source index to the filter
            initial_time=initial_time  # Pass initial time for correct oscillatory behavior
        )
        ekf_filters.append(ekf_filter)

    current_eta = self.system_model.params.eta
    logger.info(f"Initialized {max_sources} EKF instances for window {window_idx}, step {step_idx} (initial_time={initial_time}, eta={current_eta:.4f})")

    return ekf_filters



def _initialize_ekf_state_impl(self, step: int, num_sources_this_step: int, true_angles_this_step: np.ndarray,
                        ekf_filters: List[ExtendedKalmanFilter1D], is_first_window: bool,
                        last_ekf_predictions: Optional[List], last_ekf_covariances: Optional[List]) -> None:
    """
    Initialize EKF state for the current step.

    Args:
        step: Current step index
        num_sources_this_step: Number of sources in current step
        true_angles_this_step: Ground truth angles for current step
        ekf_filters: List of EKF filter instances
        is_first_window: Whether this is the first window
        last_ekf_predictions: Last EKF predictions from previous window
        last_ekf_covariances: Last EKF covariances from previous window
    """
    if step != 0:
        return

    if num_sources_this_step > len(ekf_filters):
        raise RuntimeError(
            f"EKF filter count ({len(ekf_filters)}) is smaller than sources in step 0 ({num_sources_this_step})."
        )

    if is_first_window:
        # Initialize with true angles for first window
        for i in range(num_sources_this_step):
            ekf_filters[i].initialize_state(true_angles_this_step[i])
        return

    # Initialize with last predictions from previous window when available.
    has_last_state = (
        isinstance(last_ekf_predictions, torch.Tensor)
        and isinstance(last_ekf_covariances, torch.Tensor)
        and last_ekf_predictions.dim() >= 2
        and last_ekf_covariances.dim() >= 2
        and last_ekf_predictions.shape[0] > 0
        and last_ekf_covariances.shape[0] > 0
        and last_ekf_predictions.shape[1] >= num_sources_this_step
        and last_ekf_covariances.shape[1] >= num_sources_this_step
    )
    if has_last_state:
        last_predictions_pre_perm = last_ekf_predictions[-1, :num_sources_this_step]
        true_angles_tensor = torch.tensor(true_angles_this_step, device=last_predictions_pre_perm.device)
        last_perm = self._get_optimal_permutation_tensor(last_predictions_pre_perm, true_angles_tensor)
        last_predictions = last_predictions_pre_perm[last_perm]

        last_covariances_pre_perm = last_ekf_covariances[-1, :num_sources_this_step]
        last_covariances = last_covariances_pre_perm[last_perm]

        for i in range(num_sources_this_step):
            ekf_filters[i].initialize_state(last_predictions.flatten()[i].item())
            ekf_filters[i].P = last_covariances.flatten()[i].item()
        return

    # Fallback to true angles if no valid last predictions/covariances.
    logger.warning("No valid last EKF state found at step 0, falling back to true-angle initialization.")
    for i in range(num_sources_this_step):
        ekf_filters[i].initialize_state(true_angles_this_step.flatten()[i].flatten())



def _process_single_step_impl(self, step: int, time_series_steps: torch.Tensor, sources_num_per_step: List[int],
                       labels_per_step_list: List[np.ndarray], ekf_filters: List[ExtendedKalmanFilter1D],
                       model, is_near_field: bool, Pretrained_model: bool) -> Tuple[bool, Dict]:
    """
    Process a single step in the window evaluation - data collection only.

    Args:
        step: Current step index
        time_series_steps: Time series data for all steps
        sources_num_per_step: Source counts for all steps
        labels_per_step_list: Labels for all steps
        ekf_filters: List of EKF filter instances
        model: Model to use for predictions
        is_near_field: Whether processing near-field or far-field
        Pretrained_model: Whether the model is the Pretrained_model or online trained model

    Returns:
        Tuple of (success, step_results_dict) containing only raw data
    """
    try:
        # Extract data for this step
        step_data_tensor = time_series_steps[step:step+1].to(device)  # Shape: [1, N, T]
        num_sources_this_step = sources_num_per_step[step]
        true_angles_this_step = labels_per_step_list[step][:num_sources_this_step]
        if num_sources_this_step < 0:
            raise RuntimeError(f"Step {step}: negative source count {num_sources_this_step}.")
        if (not is_near_field) and num_sources_this_step > len(ekf_filters):
            raise RuntimeError(
                f"Step {step}: EKF filter count ({len(ekf_filters)}) < source count ({num_sources_this_step})."
            )

        # Forward pass through model
        was_training = bool(getattr(model, "training", False))
        model.eval()
        with torch.no_grad():
            if not is_near_field:
                # Model expects num_sources as int or 0-dim tensor
                angles_pred, _, _ = model(step_data_tensor, num_sources_this_step)

                # Compare model weights properly
                model_state = model.state_dict()
                trained_state = self.trained_model.state_dict()
                weights_equal = all(torch.equal(model_state[key], trained_state[key]) for key in model_state.keys())
                true_angles_tensor = torch.tensor(true_angles_this_step, device=device).unsqueeze(0)

                if weights_equal and not Pretrained_model:
                    logger.error("Model and trained model have the same weights - online model was not properly copied!")
                    raise RuntimeError("Online model and trained model have identical weights. This indicates the online model was not properly initialized as an independent copy. Cannot proceed with online learning.")
                elif Pretrained_model:
                    logger.info("The evaluated model is not the online model,online model is not initialized yet or this is evaluation comparison")
                else:
                    logger.info("Model and trained model dont have the same weights - online model is properly initialized")
                    # Debug: Compare online model with pretrained model (no loss calculation)
                    pretrained_model_angle_pred, _, _ = self.trained_model(step_data_tensor,num_sources_this_step)
                    pretrained_model_angle_pred= pretrained_model_angle_pred.view(1, -1)[:, :num_sources_this_step]
                    model_perm = self._get_optimal_permutation(pretrained_model_angle_pred.cpu().numpy().flatten(), true_angles_this_step)
                    pretrained_model_angle_pred = pretrained_model_angle_pred[:, torch.tensor(model_perm, device=device)]
                    model_perm = self._get_optimal_permutation(angles_pred.cpu().numpy().flatten(), true_angles_this_step)
                    angles_pred = angles_pred[:, torch.tensor(model_perm, device=device)]
                # Prepare pre-EKF predictions tensor: force shape [1, num_sources].
                pre_ekf_angles_pred = _normalize_prediction_tensor(angles_pred, num_sources_this_step)

                # Get optimal permutation for model predictions (need numpy for permutation)
                angles_pred_np = angles_pred.cpu().numpy().flatten()[:num_sources_this_step]
                model_perm = self._get_optimal_permutation(angles_pred_np, true_angles_this_step)

                # Apply permutation to both numpy and tensor versions
                angles_pred_np = angles_pred_np[model_perm]
                pre_ekf_angles_pred = pre_ekf_angles_pred[:, model_perm]

                # EKF update for each source - use tensor directly
                step_predictions = []
                step_covariances = []
                step_innovations = []
                step_kalman_gains = []
                step_kalman_gain_times_innovation = []
                step_y_s_inv_y = []
                step_Innovation_Covariance = []

                for i in range(num_sources_this_step):
                    # Predict and update in one step - pass tensor directly

                    predicted_angle, updated_angle, innovation, kalman_gain, kalman_gain_times_innovation, y_s_inv_y,Innovation_Covariance = ekf_filters[i].predict_and_update(
                        measurement= pre_ekf_angles_pred.flatten()[i],  # Flatten to get proper indexing
                        true_state= true_angles_this_step[i]
                    )      
                    # Store prediction, covariance and innovation
                    step_predictions.append(updated_angle)
                    step_covariances.append(ekf_filters[i].P)
                    step_innovations.append(innovation)
                    step_kalman_gains.append(kalman_gain)
                    step_kalman_gain_times_innovation.append(kalman_gain_times_innovation)
                    step_y_s_inv_y.append(y_s_inv_y)
                    step_Innovation_Covariance.append(Innovation_Covariance)
                # Create tensor from EKF predictions
                # Ensure ekf_angles_pred has shape [1, num_sources] for loss functions
                ekf_angles_pred = torch.tensor(step_predictions, device=device).unsqueeze(0)  # Shape: [1, num_sources]
                if len(step_predictions) != num_sources_this_step:
                    raise RuntimeError(
                        f"Step {step}: prediction count mismatch. expected={num_sources_this_step}, got={len(step_predictions)}"
                    )
                if len(step_covariances) != num_sources_this_step:
                    raise RuntimeError(
                        f"Step {step}: covariance count mismatch. expected={num_sources_this_step}, got={len(step_covariances)}"
                    )
                if len(step_Innovation_Covariance) != num_sources_this_step:
                    raise RuntimeError(
                        f"Step {step}: innovation covariance count mismatch. "
                        f"expected={num_sources_this_step}, got={len(step_Innovation_Covariance)}"
                    )
                if pre_ekf_angles_pred.device != true_angles_tensor.device:
                    raise RuntimeError(
                        f"Step {step}: device mismatch between pre-EKF pred and labels: "
                        f"{pre_ekf_angles_pred.device} vs {true_angles_tensor.device}"
                    )
                if ekf_angles_pred.device != pre_ekf_angles_pred.device:
                    raise RuntimeError(
                        f"Step {step}: device mismatch between EKF and pre-EKF predictions: "
                        f"{ekf_angles_pred.device} vs {pre_ekf_angles_pred.device}"
                    )

                step_results = _build_step_result(
                    step_predictions=step_predictions,
                    step_covariances=step_covariances,
                    step_innovations=step_innovations,
                    step_kalman_gains=step_kalman_gains,
                    step_kalman_gain_times_innovation=step_kalman_gain_times_innovation,
                    step_y_s_inv_y=step_y_s_inv_y,
                    pre_ekf_angles_pred=pre_ekf_angles_pred,
                    ekf_angles_pred=ekf_angles_pred,
                    true_angles_tensor=true_angles_tensor,
                    num_sources_this_step=num_sources_this_step,
                    step_innovation_covariance=step_Innovation_Covariance,
                )

                return True, step_results
            else:
                # Near-field fallback: evaluate with direct model prediction (no EKF update path).
                logger.warning(
                    "Near-field EKF path is unavailable. Falling back to direct model-prediction evaluation for this step."
                )
                angles_pred, _, _ = model(step_data_tensor, num_sources_this_step)

                pre_ekf_angles_pred = _normalize_prediction_tensor(angles_pred, num_sources_this_step)

                angles_pred_np = pre_ekf_angles_pred.detach().cpu().numpy().flatten()[:num_sources_this_step]
                model_perm = self._get_optimal_permutation(angles_pred_np, true_angles_this_step)
                pre_ekf_angles_pred = pre_ekf_angles_pred[:, model_perm]
                true_angles_tensor = torch.tensor(true_angles_this_step, device=device).unsqueeze(0)

                step_predictions = [pre_ekf_angles_pred.flatten()[i] for i in range(num_sources_this_step)]
                step_covariances = [torch.tensor(1.0, device=device) for _ in range(num_sources_this_step)]
                step_innovations = [torch.tensor(0.0, device=device) for _ in range(num_sources_this_step)]
                step_kalman_gains = [torch.tensor(1.0, device=device) for _ in range(num_sources_this_step)]
                step_kalman_gain_times_innovation = [torch.tensor(0.0, device=device) for _ in range(num_sources_this_step)]
                step_y_s_inv_y = [torch.tensor(0.0, device=device) for _ in range(num_sources_this_step)]
                step_Innovation_Covariance = [torch.tensor(1.0, device=device) for _ in range(num_sources_this_step)]
                if pre_ekf_angles_pred.device != true_angles_tensor.device:
                    raise RuntimeError(
                        f"Near-field step {step}: device mismatch between prediction and labels: "
                        f"{pre_ekf_angles_pred.device} vs {true_angles_tensor.device}"
                    )

                step_results = _build_step_result(
                    step_predictions=step_predictions,
                    step_covariances=step_covariances,
                    step_innovations=step_innovations,
                    step_kalman_gains=step_kalman_gains,
                    step_kalman_gain_times_innovation=step_kalman_gain_times_innovation,
                    step_y_s_inv_y=step_y_s_inv_y,
                    pre_ekf_angles_pred=pre_ekf_angles_pred,
                    ekf_angles_pred=pre_ekf_angles_pred.clone(),
                    true_angles_tensor=true_angles_tensor,
                    num_sources_this_step=num_sources_this_step,
                    step_innovation_covariance=step_Innovation_Covariance,
                )
                return True, step_results

    except Exception as e:
        logger.warning(f"Error processing step {step}: {e}")
        return False, {'success': False, 'error': str(e)}
    finally:
        # Avoid leaking eval mode when caller expects model training state to remain unchanged.
        if 'was_training' in locals() and was_training:
            model.train()



def _evaluate_window_impl(self, window_time_series, window_sources_num, window_labels, trajectory_idx: int = 0, window_idx: int = 0,
                     is_first_window: bool = True, last_ekf_predictions: List = None, last_ekf_covariances: List = None, model=None) -> WindowEvaluationResult:
    """
    Calculate loss on a window of trajectory data using Extended Kalman Filter.

    Args:
        window_time_series: Time series data for window [batch, window_size, N, T]
        window_sources_num: Source counts for window [batch, window_size]
        window_labels: Labels for window (list of tensors)
        trajectory_idx: Index of the current trajectory
        window_idx: Index of the current window within the trajectory
        is_first_window: Flag indicating if this is the first window evaluation
        last_ekf_predictions: List of last EKF predictions from previous window
        last_ekf_covariances: List of last EKF covariances from previous window
        model: Model to use for predictions (defaults to trained_model)

    Returns:
        WindowEvaluationResult containing all metrics and data
    """
    # Debug: Log input shapes
    logger.debug(f"_evaluate_window input shapes: "
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

    # Use provided model or default to trained model
    if model is None:
        model = self.trained_model
        Pretrained_model = True
    else:
        Pretrained_model = False

    # Check if we're dealing with far-field or near-field
    is_near_field = hasattr(model, 'field_type') and model.field_type.lower() == "near"

    # Initialize Extended Kalman Filters
    max_sources = self.config.system_model.M
    ekf_filters = self._initialize_ekf_filters(max_sources, window_idx, 0)

    # Get current eta value from system model
    current_eta = self.system_model.params.eta

    # Get loss configuration for online learning
    loss_config = getattr(self.config.online_learning, 'loss_config', None)

    # Process each step in window
    step_results_list = []
    for step in range(current_window_len):
        # Initialize EKF state if this is the first step
        num_sources_this_step = sources_num_per_step[step]
        true_angles_this_step = labels_per_step_list[step][:num_sources_this_step]
        self._initialize_ekf_state(step, num_sources_this_step, true_angles_this_step, 
                                 ekf_filters, is_first_window, last_ekf_predictions, last_ekf_covariances)
        # Process single step
        success, step_result = self._process_single_step(
            step, time_series_steps, sources_num_per_step, labels_per_step_list,
            ekf_filters, model, is_near_field, Pretrained_model
        )

        step_results_list.append(step_result)

    # Calculate aggregated metrics using unified method
    result = self._calculate_metrics(step_results_list, current_window_len, max_sources, current_eta, is_near_field, loss_config)

    # Log window summary
    if result.is_valid:
        log_window_summary(result.loss_metrics, result.window_metrics.avg_covariance, 
                         current_eta, is_near_field, trajectory_idx, window_idx)

    return result
