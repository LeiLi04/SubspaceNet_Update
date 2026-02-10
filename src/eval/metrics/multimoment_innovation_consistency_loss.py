"""Multi-moment innovation consistency loss (lightweight implementation)."""

from __future__ import annotations

from dataclasses import dataclass

import torch
from torch import nn


@dataclass
class MultiMomentComponents:
    rmape: torch.Tensor
    rmspe: torch.Tensor
    total: torch.Tensor


class MultiMomentInnovationConsistencyLoss(nn.Module):
    """Blend RMSPE and RMAPE losses with scalar weights."""

    def __init__(self, alpha: float = 1.0, beta: float = 1.0, eps: float = 1e-8):
        super().__init__()
        self.alpha = alpha
        self.beta = beta
        self.eps = eps

    def forward(self, angles_pred: torch.Tensor, angles: torch.Tensor, return_components: bool = False):
        diff = angles_pred - angles
        rmspe = torch.sqrt(torch.mean(diff**2) + self.eps)
        rmape = torch.mean(torch.abs(diff) / torch.clamp(torch.abs(angles), min=self.eps))
        total = self.alpha * rmape + self.beta * rmspe

        if return_components:
            return MultiMomentComponents(rmape=rmape, rmspe=rmspe, total=total)
        return total
