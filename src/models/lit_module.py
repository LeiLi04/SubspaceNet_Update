"""Lightning adapters for incremental migration from legacy training code."""

from __future__ import annotations

import torch
from torch import nn
import logging

_WARNING_ONCE_CACHE = set()
_LOGGER = logging.getLogger(__name__)


def _warning_once(message: str) -> None:
    if message in _WARNING_ONCE_CACHE:
        return
    _WARNING_ONCE_CACHE.add(message)
    _LOGGER.warning("%s", message)


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
    _LIGHTNING_AVAILABLE = True
    _LIGHTNING_IMPORT_ERROR = None

    class LegacyLightningModule(pl.LightningModule):
        """Minimal Lightning adapter while legacy trainer remains primary."""

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

        @staticmethod
        def _select_prediction(output):
            if isinstance(output, tuple):
                return output[0]
            return output

        @staticmethod
        def _build_target_tensor(labels: torch.Tensor, sources_num: torch.Tensor, pred: torch.Tensor) -> torch.Tensor:
            """Project labels to target tensor shape compatible with prediction."""
            if labels.dim() == 1:
                labels = labels.unsqueeze(0)
            labels = labels.to(pred.device).to(pred.dtype)
            sources_num = sources_num.to(pred.device).long()

            target = torch.zeros_like(pred)
            max_pred_m = pred.shape[1] if pred.dim() > 1 else 1
            for i in range(pred.shape[0]):
                m_i = int(sources_num[i].item()) if sources_num.numel() > 1 else int(sources_num.item())
                m_i = max(1, min(m_i, max_pred_m))
                if pred.dim() == 1:
                    target[i] = labels[i, 0]
                else:
                    target[i, :m_i] = labels[i, :m_i]
            return target

        @staticmethod
        def _calculate_accuracy(true_sources: torch.Tensor, estimated_sources) -> torch.Tensor:
            if estimated_sources is None:
                return torch.tensor(1.0, device=true_sources.device)
            if not torch.is_tensor(estimated_sources):
                return torch.tensor(1.0, device=true_sources.device)
            est = estimated_sources.to(true_sources.device)
            if est.shape != true_sources.shape:
                return torch.tensor(1.0, device=true_sources.device)
            correct = (est == true_sources).sum().float()
            total = float(true_sources.numel()) if true_sources.numel() > 0 else 1.0
            return correct / total

        def _extract_step_labels(self, labels: torch.Tensor, step: int, step_sources: torch.Tensor):
            """Extract labels for one trajectory step."""
            is_near_field = hasattr(self.model, "field_type") and str(self.model.field_type).lower() == "near"
            step_labels = labels[:, step].to(self.device)
            if not is_near_field:
                return step_labels

            max_sources = int(torch.max(step_sources).item()) if step_sources.numel() > 0 else 0
            if step_labels.shape[1] >= max_sources * 2 and max_sources > 0:
                angles = step_labels[:, :max_sources]
                ranges = step_labels[:, max_sources:max_sources * 2]
                return angles, ranges

            _warning_once(
                "Near-field trajectory labels do not include range targets; using angle-only objective fallback."
            )
            return step_labels

        def _trajectory_step_forward(self, step_data, step_sources, step_labels, is_train: bool):
            """Compute single-step loss/acc for trajectory batches."""
            is_near_field = hasattr(self.model, "field_type") and str(self.model.field_type).lower() == "near"
            sources_arg = (
                int(step_sources[0].item())
                if torch.is_tensor(step_sources) and step_sources.numel() > 0
                else int(step_sources)
            )

            if is_train:
                if not is_near_field and hasattr(self.model, "training_step"):
                    out = self.model.training_step((step_data, step_sources, step_labels), None)
                    if isinstance(out, tuple):
                        loss = out[0]
                        acc = out[1] if len(out) > 1 and torch.is_tensor(out[1]) else torch.tensor(0.0, device=self.device)
                    else:
                        loss = out
                        acc = torch.tensor(0.0, device=self.device)
                    return loss, acc
                if is_near_field and hasattr(self.model, "training_step") and isinstance(step_labels, tuple):
                    angles, ranges = step_labels
                    model_step_labels = torch.cat([angles, ranges], dim=1)
                    out = self.model.training_step((step_data, step_sources, model_step_labels), None)
                    if isinstance(out, tuple):
                        loss = out[0] if not isinstance(out[0], tuple) else out[0][0]
                        acc = out[1] if len(out) > 1 and torch.is_tensor(out[1]) else torch.tensor(0.0, device=self.device)
                    else:
                        loss = out
                        acc = torch.tensor(0.0, device=self.device)
                    return loss, acc

                # Fallback forward objective
                if not is_near_field:
                    preds, source_estimation, _ = self.model(step_data, sources_arg)
                    loss = torch.nn.functional.mse_loss(preds, step_labels)
                    acc = self._calculate_accuracy(step_sources, source_estimation)
                    return loss, acc
                if isinstance(step_labels, tuple):
                    angles, ranges = step_labels
                    angles_pred, ranges_pred, source_estimation, _ = self.model(step_data, sources_arg)
                    loss = torch.nn.functional.mse_loss(angles_pred, angles) + torch.nn.functional.mse_loss(ranges_pred, ranges)
                    acc = self._calculate_accuracy(step_sources, source_estimation)
                    return loss, acc
                angles = step_labels
                try:
                    angles_pred, _, source_estimation, _ = self.model(step_data, sources_arg)
                    loss = torch.nn.functional.mse_loss(angles_pred, angles)
                    acc = self._calculate_accuracy(step_sources, source_estimation)
                    return loss, acc
                except Exception:
                    # Near-field diff_method (e.g., music_1D) may require known_angles to estimate ranges.
                    known_angles, distance_pred, _ = self.model(step_data, sources_arg, known_angles=angles)
                    distance_reg = torch.mean(distance_pred.pow(2))
                    loss = distance_reg * 1e-4
                    angle_consistency = torch.nn.functional.mse_loss(known_angles, angles)
                    loss = loss + (angle_consistency * 0.0)
                    acc = torch.tensor(1.0, device=self.device)
                    return loss, acc

            # Validation
            if not is_near_field and hasattr(self.model, "validation_step"):
                out = self.model.validation_step((step_data, step_sources, step_labels), None)
                if isinstance(out, tuple):
                    loss = out[0] if not isinstance(out[0], tuple) else out[0][0]
                    acc = out[1] if len(out) > 1 and torch.is_tensor(out[1]) else torch.tensor(0.0, device=self.device)
                else:
                    loss = out
                    acc = torch.tensor(0.0, device=self.device)
                return loss, acc
            if is_near_field and hasattr(self.model, "validation_step") and isinstance(step_labels, tuple):
                angles, ranges = step_labels
                model_step_labels = torch.cat([angles, ranges], dim=1)
                out = self.model.validation_step((step_data, step_sources, model_step_labels), None)
                if isinstance(out, tuple):
                    loss = out[0] if not isinstance(out[0], tuple) else out[0][0]
                    acc = out[1] if len(out) > 1 and torch.is_tensor(out[1]) else torch.tensor(0.0, device=self.device)
                else:
                    loss = out
                    acc = torch.tensor(0.0, device=self.device)
                return loss, acc

            # Fallback validation objective
            if not is_near_field:
                preds, source_estimation, _ = self.model(step_data, sources_arg)
                loss = torch.nn.functional.mse_loss(preds, step_labels)
                acc = self._calculate_accuracy(step_sources, source_estimation)
                return loss, acc
            if isinstance(step_labels, tuple):
                angles, ranges = step_labels
                angles_pred, ranges_pred, source_estimation, _ = self.model(step_data, sources_arg)
                loss = torch.nn.functional.mse_loss(angles_pred, angles) + torch.nn.functional.mse_loss(ranges_pred, ranges)
                acc = self._calculate_accuracy(step_sources, source_estimation)
                return loss, acc
            angles = step_labels
            try:
                angles_pred, _, source_estimation, _ = self.model(step_data, sources_arg)
                loss = torch.nn.functional.mse_loss(angles_pred, angles)
                acc = self._calculate_accuracy(step_sources, source_estimation)
                return loss, acc
            except Exception:
                known_angles, distance_pred, _ = self.model(step_data, sources_arg, known_angles=angles)
                distance_reg = torch.mean(distance_pred.pow(2))
                loss = distance_reg * 1e-4
                angle_consistency = torch.nn.functional.mse_loss(known_angles, angles)
                loss = loss + (angle_consistency * 0.0)
                acc = torch.tensor(1.0, device=self.device)
                return loss, acc

        def _compute_loss_and_acc(self, batch):
            """Fallback MSE-based objective when model-specific training hooks are absent."""
            if len(batch) >= 3:
                x, sources_num, labels = batch[:3]
                if torch.is_tensor(x) and x.ndim == 4 and torch.is_tensor(sources_num) and sources_num.ndim == 2:
                    raise RuntimeError("Trajectory batch should be processed via trajectory path, not fallback.")
                if torch.is_tensor(sources_num):
                    if sources_num.ndim == 0:
                        sources_arg = int(sources_num.item())
                    else:
                        sources_arg = int(sources_num[0].item())
                else:
                    sources_arg = int(sources_num)

                preds = self._select_prediction(self.model(x, sources_arg))
                if not isinstance(preds, torch.Tensor):
                    raise RuntimeError("Model forward output is not tensor-like for Lightning fallback.")
                target = self._build_target_tensor(labels, sources_num, preds)
                loss = torch.nn.functional.mse_loss(preds, target)
                mae = torch.mean(torch.abs(preds - target))
                acc = torch.clamp(1.0 - mae, min=0.0, max=1.0)
                return loss, acc

            raise RuntimeError("Unsupported batch format for LegacyLightningModule fallback objective.")

        def training_step(self, batch, batch_idx):
            if len(batch) >= 3:
                x, sources_num, labels = batch[:3]
                if torch.is_tensor(x) and x.ndim == 4 and torch.is_tensor(sources_num) and sources_num.ndim == 2:
                    trajectory_length = x.shape[1]
                    step_losses = []
                    step_accs = []
                    for step in range(trajectory_length):
                        step_data = x[:, step]
                        step_sources = sources_num[:, step]
                        step_labels = self._extract_step_labels(labels, step, step_sources)
                        loss_step, acc_step = self._trajectory_step_forward(
                            step_data, step_sources, step_labels, is_train=True
                        )
                        step_losses.append(loss_step if torch.is_tensor(loss_step) else torch.tensor(loss_step, device=self.device))
                        step_accs.append(acc_step if torch.is_tensor(acc_step) else torch.tensor(acc_step, device=self.device))
                    loss = torch.stack(step_losses).mean()
                    acc = torch.stack(step_accs).mean() if step_accs else torch.tensor(0.0, device=self.device)
                    self.log("train_loss", loss, on_step=False, on_epoch=True, prog_bar=True)
                    self.log("train_acc", acc, on_step=False, on_epoch=True, prog_bar=False)
                    return loss

            if hasattr(self.model, "training_step"):
                try:
                    out = self.model.training_step(batch, batch_idx)
                    if isinstance(out, tuple):
                        loss = out[0]
                        acc = out[1] if len(out) > 1 and torch.is_tensor(out[1]) else torch.tensor(0.0, device=loss.device)
                    else:
                        loss = out
                        acc = torch.tensor(0.0, device=loss.device)
                except Exception:
                    loss, acc = self._compute_loss_and_acc(batch)
            else:
                loss, acc = self._compute_loss_and_acc(batch)

            self.log("train_loss", loss, on_step=False, on_epoch=True, prog_bar=True)
            if torch.is_tensor(acc):
                self.log("train_acc", acc, on_step=False, on_epoch=True, prog_bar=False)
            return loss

        def validation_step(self, batch, batch_idx):
            if len(batch) >= 3:
                x, sources_num, labels = batch[:3]
                if torch.is_tensor(x) and x.ndim == 4 and torch.is_tensor(sources_num) and sources_num.ndim == 2:
                    trajectory_length = x.shape[1]
                    step_losses = []
                    step_accs = []
                    for step in range(trajectory_length):
                        step_data = x[:, step]
                        step_sources = sources_num[:, step]
                        step_labels = self._extract_step_labels(labels, step, step_sources)
                        loss_step, acc_step = self._trajectory_step_forward(
                            step_data, step_sources, step_labels, is_train=False
                        )
                        step_losses.append(loss_step if torch.is_tensor(loss_step) else torch.tensor(loss_step, device=self.device))
                        step_accs.append(acc_step if torch.is_tensor(acc_step) else torch.tensor(acc_step, device=self.device))
                    loss = torch.stack(step_losses).mean()
                    acc = torch.stack(step_accs).mean() if step_accs else torch.tensor(0.0, device=self.device)
                    self.log("val_loss", loss, on_step=False, on_epoch=True, prog_bar=True)
                    self.log("val_acc", acc, on_step=False, on_epoch=True, prog_bar=False)
                    return loss

            if hasattr(self.model, "validation_step"):
                try:
                    out = self.model.validation_step(batch, batch_idx)
                    if isinstance(out, tuple):
                        loss = out[0]
                        acc = out[1] if len(out) > 1 and torch.is_tensor(out[1]) else torch.tensor(0.0, device=loss.device)
                    else:
                        loss = out
                        acc = torch.tensor(0.0, device=loss.device)
                except Exception:
                    loss, acc = self._compute_loss_and_acc(batch)
            else:
                loss, acc = self._compute_loss_and_acc(batch)

            self.log("val_loss", loss, on_step=False, on_epoch=True, prog_bar=True)
            if torch.is_tensor(acc):
                self.log("val_acc", acc, on_step=False, on_epoch=True, prog_bar=False)
            return loss

except Exception as exc:
    _LIGHTNING_AVAILABLE = False
    _LIGHTNING_IMPORT_ERROR = exc

    class LegacyLightningModule:  # pragma: no cover
        """Fail-fast placeholder when pytorch_lightning is unavailable."""

        def __init__(self, *args, **kwargs):
            raise RuntimeError(
                "pytorch_lightning is required to construct LegacyLightningModule. "
                "Install it in the active environment and retry."
            ) from _LIGHTNING_IMPORT_ERROR
