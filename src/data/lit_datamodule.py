"""PyTorch Lightning style DataModule for SubspaceNet DOA data."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional, Tuple

import torch
from torch.utils.data import DataLoader, Dataset, random_split

from src.data.trajectory import TrajectoryDataHandler, TrajectoryDataset

logger = logging.getLogger("SubspaceNet.data")

try:
    import pytorch_lightning as pl

    _LightningDataModuleBase = pl.LightningDataModule
except Exception:  # pragma: no cover
    _LightningDataModuleBase = object


class DOADataModule(_LightningDataModuleBase):
    """Lightning-compatible data module for train/val/test splits."""

    def __init__(self, config, system_model, trajectory_handler: Optional[TrajectoryDataHandler] = None):
        super().__init__()
        self.config = config
        self.system_model = system_model
        self.trajectory_handler = trajectory_handler
        self.dataset_root = Path("data/datasets").absolute()

        self.train_dataset: Optional[Dataset] = None
        self.val_dataset: Optional[Dataset] = None
        self.test_dataset: Optional[Dataset] = None

        self._train_collate_fn = None
        self._eval_collate_fn = None

    def setup(self, stage: Optional[str] = None) -> None:
        stage = stage or "fit"

        if stage in ("fit", "validate", "test", "predict"):
            full_dataset, collate_fn = self._build_dataset(samples_size=self.config.dataset.samples_size)
            self._train_collate_fn = collate_fn
            self._eval_collate_fn = collate_fn

            test_ratio, val_ratio, train_ratio = self._normalized_splits()
            lengths = self._split_lengths(len(full_dataset), test_ratio, val_ratio, train_ratio)
            train_len, val_len, test_len = lengths

            self.train_dataset, self.val_dataset, self.test_dataset = random_split(
                full_dataset,
                [train_len, val_len, test_len],
                generator=torch.Generator().manual_seed(42),
            )

            logger.info(
                "DataModule splits created: train=%d val=%d test=%d",
                len(self.train_dataset),
                len(self.val_dataset),
                len(self.test_dataset),
            )

    def train_dataloader(self) -> DataLoader:
        return DataLoader(
            self.train_dataset,
            batch_size=self.config.training.batch_size,
            shuffle=True,
            collate_fn=self._train_collate_fn,
        )

    def val_dataloader(self) -> DataLoader:
        return DataLoader(
            self.val_dataset,
            batch_size=self.config.training.batch_size,
            shuffle=False,
            collate_fn=self._eval_collate_fn,
        )

    def test_dataloader(self) -> DataLoader:
        return DataLoader(
            self.test_dataset,
            batch_size=self.config.training.batch_size,
            shuffle=False,
            collate_fn=self._eval_collate_fn,
        )

    def _build_dataset(self, samples_size: int) -> Tuple[Dataset, Optional[callable]]:
        if self.config.trajectory.enabled:
            handler = self.trajectory_handler or TrajectoryDataHandler(
                system_model_params=self.system_model.params,
                config=self.config,
            )
            dataset, _ = handler.create_dataset(
                samples_size=samples_size,
                trajectory_length=self.config.trajectory.trajectory_length,
                trajectory_type=self.config.trajectory.trajectory_type,
                save_dataset=self.config.trajectory.save_trajectory,
                dataset_path=self.dataset_root,
            )
            return dataset, dataset._collate_trajectories if isinstance(dataset, TrajectoryDataset) else None

        from DCD_MUSIC.src.data_handler import create_dataset
        from DCD_MUSIC.src.signal_creation import Samples

        samples_model = Samples(self.system_model.params)
        dataset, _ = create_dataset(
            samples_model=samples_model,
            samples_size=samples_size,
            save_datasets=self.config.dataset.save_dataset,
            datasets_path=self.dataset_root,
            true_doa=self.config.dataset.true_doa_train,
            true_range=self.config.dataset.true_range_train,
            phase="train",
        )
        return dataset, None

    def _normalized_splits(self) -> Tuple[float, float, float]:
        splits = getattr(self.config.dataset, "test_validation_train_split", [0.2, 0.2, 0.6])
        total = sum(splits)
        if total <= 0:
            return 0.2, 0.2, 0.6
        test_ratio, val_ratio, train_ratio = [s / total for s in splits]
        return test_ratio, val_ratio, train_ratio

    @staticmethod
    def _split_lengths(total: int, test_ratio: float, val_ratio: float, train_ratio: float) -> Tuple[int, int, int]:
        train_len = max(1, int(total * train_ratio)) if total >= 3 else max(1, total - 2)
        val_len = max(1, int(total * val_ratio)) if total >= 3 else 1
        test_len = total - train_len - val_len
        if test_len <= 0:
            test_len = 1
            if train_len > val_len:
                train_len -= 1
            else:
                val_len -= 1
        return train_len, val_len, test_len
