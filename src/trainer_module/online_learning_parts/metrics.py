from __future__ import annotations

from typing import Dict, List
import torch

from src.trainer_module.online_learning import (
    WindowEvaluationResult,
    LossMetrics,
    WindowMetrics,
    StepMetrics,
    DOAMetrics,
)

def _get_step_innovation_covariance(step_result: Dict) -> List[torch.Tensor]:
    """
    Extract per-source innovation covariance from step result with backward compatibility.
    """
    if 'step_innovation_covariance' in step_result:
        return step_result['step_innovation_covariance']
    if 'step_Innovation_Covariance' in step_result:
        return step_result['step_Innovation_Covariance']
    if 'step_innovation_covariance_tensor' in step_result:
        cov_tensor = step_result['step_innovation_covariance_tensor']
        if isinstance(cov_tensor, torch.Tensor):
            return [cov_tensor.flatten()[i] for i in range(cov_tensor.numel())]
    if 'Innovation_Covariance_tensor' in step_result:
        cov_tensor = step_result['Innovation_Covariance_tensor']
        if isinstance(cov_tensor, torch.Tensor):
            return [cov_tensor.flatten()[i] for i in range(cov_tensor.numel())]
    raise RuntimeError("step_result is missing innovation covariance field")


def _validate_step_result_contract(step_result: Dict, step_idx: int) -> None:
    """
    Validate minimal runtime contract for step results consumed by metrics aggregation.
    """
    required_keys = (
        'success',
        'num_sources',
        'pre_ekf_angles_pred_tensor',
        'ekf_angles_pred_tensor',
        'true_angles_tensor',
    )
    missing = [k for k in required_keys if k not in step_result]
    if missing:
        raise RuntimeError(f"Step {step_idx}: missing required step_result keys: {missing}")

    pre = step_result['pre_ekf_angles_pred_tensor']
    ekf = step_result['ekf_angles_pred_tensor']
    true = step_result['true_angles_tensor']
    for name, value in (('pre_ekf', pre), ('ekf', ekf), ('true', true)):
        if not isinstance(value, torch.Tensor):
            raise RuntimeError(f"Step {step_idx}: {name} tensor is not a torch.Tensor ({type(value)})")
        if value.dim() not in (2, 3):
            raise RuntimeError(f"Step {step_idx}: {name} tensor has invalid rank {value.dim()}")

    if pre.device != ekf.device or pre.device != true.device:
        raise RuntimeError(
            f"Step {step_idx}: device mismatch pre={pre.device}, ekf={ekf.device}, true={true.device}"
        )

    num_sources = int(step_result['num_sources'])
    innovation_cov = _get_step_innovation_covariance(step_result)
    if len(innovation_cov) < num_sources:
        raise RuntimeError(
            f"Step {step_idx}: innovation covariance length {len(innovation_cov)} < num_sources {num_sources}"
        )

def _calculate_metrics_impl(self, step_results_list: List[Dict], current_window_len: int, 
                      max_sources: int, current_eta: float, is_near_field: bool, 
                      loss_config=None) -> WindowEvaluationResult:
    """
    Calculate aggregated metrics from step results.

    Args:
        step_results_list: List of step result dictionaries
        current_window_len: Length of the window
        max_sources: Maximum number of sources
        current_eta: Current eta value
        is_near_field: Whether processing near-field or far-field
        loss_config: Loss configuration object (optional)

    Returns:
        WindowEvaluationResult containing all calculated metrics
    """
    # Initialize tensors for storing results
    ekf_predictions = torch.empty((current_window_len, max_sources), dtype=torch.float64)
    ekf_covariances = torch.empty((current_window_len, max_sources), dtype=torch.float64)
    ekf_innovations = torch.empty((current_window_len, max_sources), dtype=torch.float64)
    ekf_kalman_gains = torch.empty((current_window_len, max_sources), dtype=torch.float64)
    ekf_kalman_gain_times_innovation = torch.empty((current_window_len, max_sources), dtype=torch.float64)
    ekf_y_s_inv_y = torch.empty((current_window_len, max_sources), dtype=torch.float64)
    pre_ekf_angles_pred_list = torch.empty((current_window_len, max_sources), dtype=torch.float64)

    # Collect all tensors for window-level loss calculation
    all_pre_ekf_preds = []
    all_ekf_preds = []
    all_true_angles = []
    all_innovation_covariances = []

    # Initialize accumulation variables
    num_valid_steps = 0
    total_covariance = 0.0
    total_cov_points = 0

    # Process each step result
    for step, step_result in enumerate(step_results_list):
        _validate_step_result_contract(step_result, step)
        if not step_result['success']:
            continue

        num_sources = step_result['num_sources']

        # Store EKF metrics (all are tensors now)
        for i in range(num_sources):
            ekf_predictions[step, i] = step_result['step_predictions'][i].item()
            ekf_covariances[step, i] = step_result['step_covariances'][i].item()
            ekf_innovations[step, i] = step_result['step_innovations'][i].item()
            ekf_kalman_gains[step, i] = step_result['step_kalman_gains'][i].item()
            ekf_kalman_gain_times_innovation[step, i] = step_result['step_kalman_gain_times_innovation'][i].item()
            ekf_y_s_inv_y[step, i] = step_result['step_y_s_inv_y'][i].item()

        # Store pre-EKF predictions (tensor)
        pre_ekf_preds = step_result['pre_ekf_angles_pred_tensor'].flatten()
        for i in range(min(num_sources, len(pre_ekf_preds))):
            pre_ekf_angles_pred_list[step, i] = pre_ekf_preds[i].item()

        # Collect tensors for window-level loss calculation
        all_pre_ekf_preds.append(step_result['pre_ekf_angles_pred_tensor'])
        all_ekf_preds.append(step_result['ekf_angles_pred_tensor'])
        all_true_angles.append(step_result['true_angles_tensor'])
        all_innovation_covariances.append(_get_step_innovation_covariance(step_result))

        # Accumulate covariance (convert tensors to scalars for sum)
        total_covariance += sum(tensor.item() for tensor in step_result['step_covariances'])
        total_cov_points += num_sources

        num_valid_steps += 1

    # Calculate window-level losses using unified method
    if num_valid_steps > 0 and all_pre_ekf_preds:
        # Stack predictions across time steps
        window_pre_ekf_preds = torch.cat(all_pre_ekf_preds, dim=0)  # [window_size, num_sources]
        window_ekf_preds = torch.cat(all_ekf_preds, dim=0)          # [window_size, num_sources]
        window_true_angles = torch.cat(all_true_angles, dim=0)      # [window_size, num_sources]

        # Calculate ALL losses at window level
        loss_metrics = self._calculate_all_losses(
            window_pre_ekf_preds, window_ekf_preds, window_true_angles, all_innovation_covariances, loss_config
        )

        avg_covariance = total_covariance / total_cov_points if total_cov_points > 0 else float('nan')
    else:
        # Create default loss metrics if no valid steps
        loss_metrics = LossMetrics(
            main_loss=float('inf'),
            main_loss_db=float('inf'),
            main_loss_config="no_valid_steps",
            online_training_reference_loss=float('inf'),
            online_training_reference_loss_config="no_valid_steps",
            pre_ekf_loss=float('inf'),
            ekf_gain_rmspe=0.0,
            ekf_gain_rmape=0.0
        )
        avg_covariance = float('nan')

    # Calculate averaged metrics across time steps
    avg_ekf_angle_pred = []
    avg_pre_ekf_angle_pred = []
    avg_ekf_covariances = []
    avg_ekf_innovations = []
    avg_ekf_kalman_gains = []
    avg_ekf_kalman_gain_times_innovation = []
    avg_ekf_y_s_inv_y = []
    avg_step_innovation_covariances = []

    if num_valid_steps > 0:
        # Get the number of sources from the first valid step
        first_valid_step = next((result for result in step_results_list if result['success']), None)
        if first_valid_step:
            num_sources = first_valid_step['num_sources']

            # Average EKF predictions across time steps for each source
            for source_idx in range(num_sources):
                source_predictions = []
                for step_result in step_results_list:
                    if step_result['success'] and len(step_result['step_predictions']) > source_idx:
                        source_predictions.append(step_result['step_predictions'][source_idx].item())

                if source_predictions:
                    avg_ekf_angle_pred.append(float(sum(source_predictions) / len(source_predictions)))

            # Average pre-EKF predictions across time steps for each source
            for source_idx in range(num_sources):
                source_predictions = []
                for step_result in step_results_list:
                    if step_result['success']:
                        pre_ekf_preds = step_result['pre_ekf_angles_pred_tensor'].flatten()
                        if len(pre_ekf_preds) > source_idx:
                            source_predictions.append(pre_ekf_preds[source_idx].item())

                if source_predictions:
                    avg_pre_ekf_angle_pred.append(float(sum(source_predictions) / len(source_predictions)))

            # Average EKF covariances across time steps for each source
            for source_idx in range(num_sources):
                source_covariances = []
                for step_result in step_results_list:
                    if step_result['success'] and len(step_result['step_covariances']) > source_idx:
                        source_covariances.append(step_result['step_covariances'][source_idx].item())

                if source_covariances:
                    avg_ekf_covariances.append(float(sum(source_covariances) / len(source_covariances)))

            # Average EKF innovations across time steps for each source
            for source_idx in range(num_sources):
                source_innovations = []
                for step_result in step_results_list:
                    if step_result['success'] and len(step_result['step_innovations']) > source_idx:
                        source_innovations.append(step_result['step_innovations'][source_idx].item())

                if source_innovations:
                    avg_ekf_innovations.append(float(sum(source_innovations) / len(source_innovations)))

            # Average EKF Kalman gains across time steps for each source
            for source_idx in range(num_sources):
                source_kalman_gains = []
                for step_result in step_results_list:
                    if step_result['success'] and len(step_result['step_kalman_gains']) > source_idx:
                        source_kalman_gains.append(step_result['step_kalman_gains'][source_idx].item())

                if source_kalman_gains:
                    avg_ekf_kalman_gains.append(float(sum(source_kalman_gains) / len(source_kalman_gains)))

            # Average EKF Kalman gain times innovation across time steps for each source
            for source_idx in range(num_sources):
                source_kalman_gain_times_innovation = []
                for step_result in step_results_list:
                    if step_result['success'] and len(step_result['step_kalman_gain_times_innovation']) > source_idx:
                        source_kalman_gain_times_innovation.append(step_result['step_kalman_gain_times_innovation'][source_idx].item())

                if source_kalman_gain_times_innovation:
                    avg_ekf_kalman_gain_times_innovation.append(float(sum(source_kalman_gain_times_innovation) / len(source_kalman_gain_times_innovation)))

            # Average EKF y_s_inv_y across time steps for each source
            for source_idx in range(num_sources):
                source_y_s_inv_y = []
                for step_result in step_results_list:
                    if step_result['success'] and len(step_result['step_y_s_inv_y']) > source_idx:
                        source_y_s_inv_y.append(step_result['step_y_s_inv_y'][source_idx].item())

                if source_y_s_inv_y:
                    avg_ekf_y_s_inv_y.append(float(sum(source_y_s_inv_y) / len(source_y_s_inv_y)))

            # Average step innovation covariances across time steps for each source
            for source_idx in range(num_sources):
                source_innovation_covariances = []
                for step_result in step_results_list:
                    if not step_result['success']:
                        continue
                    step_cov = _get_step_innovation_covariance(step_result)
                    if len(step_cov) > source_idx:
                        source_innovation_covariances.append(step_cov[source_idx].item())

                if source_innovation_covariances:
                    avg_step_innovation_covariances.append(float(sum(source_innovation_covariances) / len(source_innovation_covariances)))

    # Create window metrics with averaged values
    window_metrics = WindowMetrics(
        window_size=current_window_len,
        num_sources=num_sources if num_valid_steps > 0 else 0,
        avg_covariance=avg_covariance,
        eta_value=current_eta,
        is_near_field=is_near_field,
        avg_ekf_angle_pred=avg_ekf_angle_pred,
        avg_pre_ekf_angle_pred=avg_pre_ekf_angle_pred,
        avg_ekf_covariances=avg_ekf_covariances,
        avg_ekf_innovations=avg_ekf_innovations,
        avg_ekf_kalman_gains=avg_ekf_kalman_gains,
        avg_ekf_kalman_gain_times_innovation=avg_ekf_kalman_gain_times_innovation,
        avg_ekf_y_s_inv_y=avg_ekf_y_s_inv_y,
        avg_step_innovation_covariances=avg_step_innovation_covariances
    )

    # Create step metrics (renamed from EKF metrics)
    step_metrics = StepMetrics(
        covariances=ekf_covariances,
        innovations=ekf_innovations,
        kalman_gains=ekf_kalman_gains,
        kalman_gain_times_innovation=ekf_kalman_gain_times_innovation,
        y_s_inv_y=ekf_y_s_inv_y
    )
    c_per_step_list = ekf_y_s_inv_y.sum(dim=1).tolist()
    setattr(step_metrics, "c_per_step", c_per_step_list)

    # Create DOA metrics with predictions and true angles
    doa_metrics = DOAMetrics(
        ekf_predictions=ekf_predictions,
        pre_ekf_predictions=pre_ekf_angles_pred_list,
        true_angles=torch.cat(all_true_angles, dim=0) if all_true_angles else torch.empty((0, 0), dtype=torch.float64),
        avg_ekf_angle_pred=avg_ekf_angle_pred,
        avg_pre_ekf_angle_pred=avg_pre_ekf_angle_pred
    )

    return WindowEvaluationResult(
        loss_metrics=loss_metrics,
        window_metrics=window_metrics,
        step_metrics=step_metrics,
        doa_metrics=doa_metrics,
        is_valid=num_valid_steps > 0
    )




def _average_online_learning_results_across_trajectories_impl(self, results_list):
    from src.trainer_module.online_learning_parts.metrics_aggregate import _average_online_learning_results_across_trajectories_impl as impl
    return impl(self, results_list)
