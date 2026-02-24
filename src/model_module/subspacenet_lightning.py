"""Native Lightning wrapper for SubspaceNet with explicit Hydra params."""

from __future__ import annotations

from typing import Any, Optional

import torch

from DCD_MUSIC.src.models_pack.subspacenet import SubspaceNet
from src.model_module.lit_module import LegacyLightningModule


class SubspaceNetLightning(LegacyLightningModule):
    """LightningModule for SubspaceNet."""

    def __init__(
        self,
        tau: int = 8,
        diff_method: str = "esprit",
        train_loss_type: str = "rmspe",
        field_type: str = "Far",
        learning_rate: float = 1e-3,
        weight_decay: float = 1e-9,
        optimizer: str = "Adam",
        scheduler: str = "ReduceLROnPlateau",
        step_size: int = 50,
        gamma: float = 0.5,
        momentum: float = 0.9,
        regularization: Optional[str] = None,
        variant: str = "small",
        norm_layer: bool = False,
        batch_norm: bool = False,
        system_model: Any = None,
    ) -> None:
        if system_model is None:
            raise ValueError("SubspaceNetLightning requires `system_model`.")

        model = SubspaceNet(
            tau=tau,
            diff_method=diff_method,
            system_model=system_model,
            field_type=field_type,
        )
        super().__init__(model=model, learning_rate=learning_rate)
        self.save_hyperparameters(ignore=["system_model"])

        self.train_loss_type = train_loss_type
        self.regularization = regularization
        self.variant = variant
        self.norm_layer = norm_layer
        self.batch_norm = batch_norm

    def forward(self, x, sources_num=None):
        return super().forward(x, sources_num=sources_num)

    def training_step(self, batch, batch_idx):
        return super().training_step(batch, batch_idx)

    def validation_step(self, batch, batch_idx):
        return super().validation_step(batch, batch_idx)

    def configure_optimizers(self):
        optimizer_name = str(self.hparams.optimizer).lower()
        if optimizer_name == "sgd":
            optimizer = torch.optim.SGD(
                self.parameters(),
                lr=float(self.hparams.learning_rate),
                weight_decay=float(self.hparams.weight_decay),
                momentum=float(self.hparams.momentum),
            )
        elif optimizer_name == "rmsprop":
            optimizer = torch.optim.RMSprop(
                self.parameters(),
                lr=float(self.hparams.learning_rate),
                weight_decay=float(self.hparams.weight_decay),
            )
        else:
            optimizer = torch.optim.Adam(
                self.parameters(),
                lr=float(self.hparams.learning_rate),
                weight_decay=float(self.hparams.weight_decay),
            )

        scheduler_name = str(self.hparams.scheduler).lower()
        if scheduler_name == "steplr":
            scheduler = torch.optim.lr_scheduler.StepLR(
                optimizer,
                step_size=int(self.hparams.step_size),
                gamma=float(self.hparams.gamma),
            )
            return {"optimizer": optimizer, "lr_scheduler": scheduler}
        if scheduler_name == "reducelronplateau":
            scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
                optimizer,
                mode="min",
                factor=float(self.hparams.gamma),
                patience=10,
            )
            return {
                "optimizer": optimizer,
                "lr_scheduler": {"scheduler": scheduler, "monitor": "val_loss"},
            }
        if scheduler_name == "cosineannealinglr":
            scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(
                optimizer,
                T_max=int(self.trainer.max_epochs) if self.trainer is not None else int(self.hparams.step_size),
            )
            return {"optimizer": optimizer, "lr_scheduler": scheduler}
        return optimizer
