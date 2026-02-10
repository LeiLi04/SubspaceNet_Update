"""LightningModule-compatible wrapper for legacy SubspaceNet models."""

from __future__ import annotations

import torch
from torch import nn


class LegacyModelModule(nn.Module):
    """Thin wrapper around the existing model object."""

    def __init__(self, model: nn.Module):
        super().__init__()
        self.model = model

    def forward(self, x, sources_num=None):
        if sources_num is None:
            return self.model(x)
        return self.model(x, sources_num)


try:
    import pytorch_lightning as pl

    class LegacyLightningModule(pl.LightningModule):
        """Minimal Lightning adapter for incremental migration."""

        def __init__(self, model: nn.Module, learning_rate: float = 1e-3):
            super().__init__()
            self.model = model
            self.learning_rate = learning_rate

        def forward(self, x, sources_num=None):
            if sources_num is None:
                return self.model(x)
            return self.model(x, sources_num)

        def configure_optimizers(self):
            return torch.optim.Adam(self.parameters(), lr=self.learning_rate)

        def training_step(self, batch, batch_idx):
            raise NotImplementedError("Legacy training loop is still handled by src.train.training")

except ImportError:
    LegacyLightningModule = None
