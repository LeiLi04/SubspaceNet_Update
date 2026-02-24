from __future__ import annotations

from typing import Dict, List
import numpy as np
import torch
from itertools import permutations

from src.trainer_module.online_learning import (
    device,
    LossMetrics,
)
from src.eval_module.metrics.multimoment_innovation_consistency_loss import MultiMomentInnovationConsistencyLoss
def _fix_tensor_shape_for_loss_impl(self, tensor: torch.Tensor) -> torch.Tensor:
    """
    Fix tensor shape for loss calculations.
    Expected: [window_size, num_sources]
    Actual: [window_size, 1, num_sources] -> squeeze middle dimension
    """
    if tensor.dim() == 3 and tensor.shape[1] == 1:
        return tensor.squeeze(1)  # Remove middle dimension
    return tensor



def _calculate_all_losses_impl(self, pre_ekf_preds: torch.Tensor, ekf_preds: torch.Tensor, 
                        true_angles: torch.Tensor, innovation_covariances: list = None, loss_config=None) -> 'LossMetrics':
    """
    Calculate all losses at window level.

    Args:
        pre_ekf_preds: Pre-EKF predictions tensor [window_size, num_sources]
        ekf_preds: EKF predictions tensor [window_size, num_sources]
        true_angles: True angles tensor [window_size, num_sources]
        innovation_covariances: List of innovation covariance tensors for each step (optional)
        loss_config: Loss configuration object (optional)

    Returns:
        LossMetrics object with all calculated losses
    """
    # Import loss criteria
    from src.eval_module.metrics.rmspe_loss import RMSPELoss
    from src.eval_module.metrics.rmape_loss import RMAPELoss

    rmspe_criterion = RMSPELoss().to(device)
    rmape_criterion = RMAPELoss().to(device)

    # Fix tensor shapes - remove extra dimension if present
    pre_ekf_preds = self._fix_tensor_shape_for_loss(pre_ekf_preds)
    ekf_preds = self._fix_tensor_shape_for_loss(ekf_preds)
    true_angles = self._fix_tensor_shape_for_loss(true_angles)

    # Get window size for proper averaging
    window_size = pre_ekf_preds.shape[0]

    # Main loss (what the system is optimized for - uses supervision + metric)
    if loss_config is None:
        raise RuntimeError("loss_config is required for _calculate_all_losses but was None")

    # Determine targets based on supervision mode
    if loss_config.supervision == "supervised":
        targets = true_angles
    elif loss_config.supervision == "unsupervised":  # unsupervised
        targets = pre_ekf_preds
    else:
        raise RuntimeError(f"Unknown supervision mode: {loss_config.supervision}. Must be one of: supervised, unsupervised")

    # Calculate main loss using supervision + metric (NOT training_loss_type)
    main_loss_config = f"{loss_config.supervision}_{loss_config.metric}"
    if loss_config.metric == "rmspe":
        main_loss = rmspe_criterion(ekf_preds, targets) / window_size  # RMSPE sums across batch, divide by window size
    elif loss_config.metric == "rmape": # rmape
        main_loss = rmape_criterion(ekf_preds, targets) / window_size  # RMAPE sums across batch, divide by window size
    else:
        raise RuntimeError(f"Unknown metric: {loss_config.metric}. Must be one of: rmspe, rmape")

    # Calculate main loss in dB units (20 * log10(main_loss))
    import math
    main_loss_value = main_loss.item() if hasattr(main_loss, 'item') else main_loss
    main_loss_db = 20 * math.log10(main_loss_value)  # Avoid log(0) with small epsilon

    # Online training reference loss (uses training_loss_type configuration)
    if not hasattr(loss_config, 'training_loss_type'):
        raise RuntimeError("loss_config.training_loss_type is required for online_training_reference_loss but was not found")

    training_loss_type = loss_config.training_loss_type
    online_training_reference_loss_config = training_loss_type

    if training_loss_type == "multimoment":
        # Multi-Moment loss: use pre-EKF as predictions, EKF as targets
        try:
            multimoment_criterion = MultiMomentInnovationConsistencyLoss(
                alpha=getattr(loss_config, 'multimoment_alpha', 1.0),
                beta=getattr(loss_config, 'multimoment_beta', 1.0)
            ).to(device)
            online_training_reference_loss = multimoment_criterion(
                angles_pred=pre_ekf_preds,
                angles=ekf_preds,
                return_components=False
            )
            # Multi-Moment already divides by batch_size, no need for .mean()
        except Exception as e:
            raise RuntimeError(f"Failed to calculate Multi-Moment reference loss: {e}")
    elif training_loss_type == "unsupervised_rmspe":
        # Unsupervised RMSPE: EKF vs pre-EKF
        online_training_reference_loss = rmspe_criterion(ekf_preds, pre_ekf_preds) / window_size  # RMSPE sums across batch, divide by window size
    elif training_loss_type == "unsupervised_rmape":
        # Unsupervised RMAPE: EKF vs pre-EKF
        online_training_reference_loss = rmape_criterion(ekf_preds, pre_ekf_preds) / window_size  # RMAPE sums across batch, divide by window size
    elif training_loss_type == "supervised_rmspe":
        # Supervised RMSPE: EKF vs true angles
        online_training_reference_loss = rmspe_criterion(ekf_preds, true_angles) / window_size  # RMSPE sums across batch, divide by window size
    elif training_loss_type == "supervised_rmape":
        # Supervised RMAPE: EKF vs true angles
        online_training_reference_loss = rmape_criterion(ekf_preds, true_angles) / window_size  # RMAPE sums across batch, divide by window size
    else:
        # Unknown training_loss_type, terminate with error
        raise RuntimeError(f"Unknown training_loss_type: {training_loss_type}. Must be one of: multimoment, unsupervised_rmspe, unsupervised_rmape, supervised_rmspe, supervised_rmape")

    # Pre-EKF loss (raw model performance)
    pre_ekf_loss = rmspe_criterion(pre_ekf_preds, true_angles) / window_size  # RMSPE sums across batch, divide by window size

    # EKF gain losses (EKF improvement over raw predictions)
    ekf_gain_rmspe = rmspe_criterion(ekf_preds, pre_ekf_preds) / window_size  # RMSPE sums across batch, divide by window size
    ekf_gain_rmape = rmape_criterion(ekf_preds, pre_ekf_preds) / window_size  # RMAPE sums across batch, divide by window size

    return LossMetrics(
        main_loss=main_loss.item() if hasattr(main_loss, 'item') else main_loss,
        main_loss_db=main_loss_db,
        main_loss_config=main_loss_config,
        online_training_reference_loss=online_training_reference_loss.item() if hasattr(online_training_reference_loss, 'item') else online_training_reference_loss,
        online_training_reference_loss_config=online_training_reference_loss_config,
        pre_ekf_loss=pre_ekf_loss.item() if hasattr(pre_ekf_loss, 'item') else pre_ekf_loss,
        ekf_gain_rmspe=ekf_gain_rmspe.item() if hasattr(ekf_gain_rmspe, 'item') else ekf_gain_rmspe,
        ekf_gain_rmape=ekf_gain_rmape.item() if hasattr(ekf_gain_rmape, 'item') else ekf_gain_rmape
    )




def _calculate_window_training_loss_impl(self, step_results_list: List[Dict], 
                                  loss_config=None, rmspe_criterion=None, rmape_criterion=None) -> torch.Tensor:
    """
    Calculate window-level training loss based on configuration.

    Args:
        step_results_list: List of step result dictionaries from window
        loss_config: Loss configuration (optional)
        rmspe_criterion: RMSPE loss criterion instance
        rmape_criterion: RMAPE loss criterion instance

    Returns:
        Window-level loss tensor
    """
    if not step_results_list:
        return torch.tensor(0.0, device=device, requires_grad=True)

    # Collect all tensors for window-level loss calculation
    all_pre_ekf_preds = []
    all_ekf_preds = []
    all_true_angles = []

    for step_result in step_results_list:
        if step_result['success']:
            all_pre_ekf_preds.append(step_result['pre_ekf_angles_pred_tensor'])
            all_ekf_preds.append(step_result['ekf_angles_pred_tensor'])
            all_true_angles.append(step_result['true_angles_tensor'])

    if not all_pre_ekf_preds:
        return torch.tensor(0.0, device=device, requires_grad=True)

    # Stack predictions across time steps
    window_pre_ekf_preds = torch.cat(all_pre_ekf_preds, dim=0)  # [window_size, num_sources]
    window_ekf_preds = torch.cat(all_ekf_preds, dim=0)          # [window_size, num_sources]
    window_true_angles = torch.cat(all_true_angles, dim=0)      # [window_size, num_sources]

    # Fix tensor shapes - remove extra dimension if present
    window_pre_ekf_preds = self._fix_tensor_shape_for_loss(window_pre_ekf_preds)
    window_ekf_preds = self._fix_tensor_shape_for_loss(window_ekf_preds)
    window_true_angles = self._fix_tensor_shape_for_loss(window_true_angles)

    # Get window size for proper averaging
    window_size = window_pre_ekf_preds.shape[0]

    # Calculate window-level loss based on training_loss_type configuration
    if loss_config is not None and hasattr(loss_config, 'training_loss_type'):
        training_loss_type = loss_config.training_loss_type

        if training_loss_type == "multimoment":
            # Multi-Moment loss: use pre-EKF as predictions, EKF as targets
            try:
                multimoment_criterion = MultiMomentInnovationConsistencyLoss(
                    alpha=getattr(loss_config, 'multimoment_alpha', 1.0),
                    beta=getattr(loss_config, 'multimoment_beta', 1.0)
                ).to(device)
                return multimoment_criterion(
                    angles_pred=window_pre_ekf_preds,
                    angles=window_ekf_preds,
                    return_components=False
                )
            except Exception as e:
                raise RuntimeError(f"Failed to calculate Multi-Moment training loss: {e}")
        elif training_loss_type == "unsupervised_rmspe":
            # Unsupervised RMSPE: EKF vs pre-EKF
            return rmspe_criterion(window_ekf_preds, window_pre_ekf_preds) / window_size  # RMSPE sums across batch, divide by window size
        elif training_loss_type == "unsupervised_rmape":
            # Unsupervised RMAPE: EKF vs pre-EKF
            return rmape_criterion(window_ekf_preds, window_pre_ekf_preds) / window_size  # RMAPE sums across batch, divide by window size
        elif training_loss_type == "supervised_rmspe":
            # Supervised RMSPE: EKF vs true angles
            return rmspe_criterion(window_ekf_preds, window_true_angles) / window_size  # RMSPE sums across batch, divide by window size
        elif training_loss_type == "supervised_rmape":
            # Supervised RMAPE: EKF vs true angles
            return rmape_criterion(window_ekf_preds, window_true_angles) / window_size  # RMAPE sums across batch, divide by window size
        else:
            # Unknown training_loss_type, terminate with error
            raise RuntimeError(f"Unknown training_loss_type: {training_loss_type}. Must be one of: multimoment, unsupervised_rmspe, unsupervised_rmape, supervised_rmspe, supervised_rmape")
    else:
        # Default to RMSPE loss
        return rmspe_criterion(window_ekf_preds, window_true_angles) / window_size  # RMSPE sums across batch, divide by window size





def _get_optimal_permutation_impl(self, predictions: np.ndarray, true_angles: np.ndarray) -> np.ndarray:
    """
    Calculate optimal permutation between predictions and true angles using RMSPE.

    Args:
        predictions: Array of predicted angles [num_sources]
        true_angles: Array of true angles [num_sources]

    Returns:
        optimal_perm: Array containing the optimal permutation indices
    """
    import torch
    from src.eval_module.metrics.rmspe_loss import RMSPELoss
    from itertools import permutations

    # Convert inputs to tensors and reshape
    pred_tensor = torch.tensor(predictions, device=device).view(1, -1)
    true_tensor = torch.tensor(true_angles, device=device).view(1, -1)

    num_sources = pred_tensor.shape[1]
    perm = list(permutations(range(num_sources), num_sources))
    num_of_perm = len(perm)

    # Calculate errors for all permutations
    err_angle = (pred_tensor[:, perm] - torch.tile(true_tensor[:, None, :], (1, num_of_perm, 1)).to(torch.float32))
    err_angle += torch.pi / 2
    err_angle %= torch.pi
    err_angle -= torch.pi / 2
    rmspe_angle_all_permutations = np.sqrt(1 / num_sources) * torch.linalg.norm(err_angle, dim=-1)
    _, min_idx = torch.min(rmspe_angle_all_permutations, dim=-1)

    # Get optimal permutation
    optimal_perm = torch.tensor(perm, dtype=torch.long, device=device)[min_idx]
    return optimal_perm.cpu().numpy()



def _get_optimal_permutation_tensor_impl(self, predictions: torch.Tensor, true_angles: torch.Tensor) -> torch.Tensor:
    """
    Calculate optimal permutation between predictions and true angles using RMSPE.
    Tensor version that works directly with tensors.

    Args:
        predictions: Tensor of predicted angles [num_sources] or [1, num_sources]
        true_angles: Tensor of true angles [num_sources] or [1, num_sources]

    Returns:
        optimal_perm: Tensor containing the optimal permutation indices
    """
    from itertools import permutations

    # Ensure inputs are 2D tensors
    if predictions.dim() == 1:
        pred_tensor = predictions.unsqueeze(0)
    else:
        pred_tensor = predictions

    if true_angles.dim() == 1:
        true_tensor = true_angles.unsqueeze(0)
    else:
        true_tensor = true_angles

    num_sources = pred_tensor.shape[1]
    perm = list(permutations(range(num_sources), num_sources))
    num_of_perm = len(perm)

    # Calculate errors for all permutations
    err_angle = (pred_tensor[:, perm] - torch.tile(true_tensor[:, None, :], (1, num_of_perm, 1)).to(torch.float32))
    err_angle += torch.pi / 2
    err_angle %= torch.pi
    err_angle -= torch.pi / 2
    rmspe_angle_all_permutations = torch.sqrt(torch.tensor(1.0 / num_sources, device=predictions.device)) * torch.linalg.norm(err_angle, dim=-1)
    _, min_idx = torch.min(rmspe_angle_all_permutations, dim=-1)

    # Get optimal permutation
    optimal_perm = torch.tensor(perm, dtype=torch.long, device=predictions.device)[min_idx]
    return optimal_perm


