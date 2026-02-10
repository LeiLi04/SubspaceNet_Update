"""RMAPE loss implementation used by online-learning routines."""

from __future__ import annotations

import torch
from torch import nn


class RMAPELoss(nn.Module):
    """Relative MAPE-style loss for angle predictions."""

    def __init__(self, eps: float = 1e-8):
        super().__init__()
        self.eps = eps

    def forward(self, angles_pred: torch.Tensor, angles: torch.Tensor) -> torch.Tensor:
        denom = torch.clamp(torch.abs(angles), min=self.eps)
        rel = torch.abs(angles_pred - angles) / denom
        return torch.sum(rel)
