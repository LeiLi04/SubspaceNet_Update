"""RMSPE loss compatibility implementation."""

from __future__ import annotations

from itertools import permutations
from typing import Optional

import numpy as np
import torch
from torch import nn


class RMSPELoss(nn.Module):
    """RMSPE with optional best-permutation output for compatibility."""

    def __init__(self, balance_factor: Optional[float] = None):
        super().__init__()
        self.balance_factor = 0.5 if balance_factor is None else balance_factor

    def forward(
        self,
        doa_predictions: torch.Tensor,
        doa: torch.Tensor,
        distance_predictions: torch.Tensor = None,
        distance: torch.Tensor = None,
        return_best_perm: bool = False,
    ):
        device = doa_predictions.device
        num_sources = doa_predictions.shape[1]
        perm = list(permutations(range(num_sources), num_sources))
        perm_tensor = torch.tensor(perm, dtype=torch.long, device=device)

        err_angle = doa_predictions[:, perm_tensor] - doa[:, None, :].to(torch.float32)
        err_angle = (err_angle + torch.pi / 2) % torch.pi - torch.pi / 2
        rmspe_angle = np.sqrt(1 / num_sources) * torch.linalg.norm(err_angle, dim=-1)

        if distance is None:
            rmspe, min_idx = torch.min(rmspe_angle, dim=-1)
            loss = torch.sum(rmspe)
            if return_best_perm:
                best_perm = perm_tensor[min_idx]
                return loss, best_perm
            return loss

        err_distance = distance_predictions[:, perm_tensor].to(device) - distance[:, None, :].to(device)
        rmspe_distance = np.sqrt(1 / num_sources) * torch.linalg.norm(err_distance, dim=-1)
        rmspe_angle_min, min_idx = torch.min(rmspe_angle, dim=-1)
        rmspe_distance_min = torch.gather(rmspe_distance, 1, min_idx.unsqueeze(1)).squeeze(1)

        rmspe = self.balance_factor * rmspe_angle_min + (1 - self.balance_factor) * rmspe_distance_min
        result = torch.sum(rmspe)
        if return_best_perm:
            best_perm = perm_tensor[min_idx]
            return result, best_perm

        result_angle = torch.sum(rmspe_angle_min)
        result_distance = torch.sum(rmspe_distance_min)
        return result, result_angle, result_distance
