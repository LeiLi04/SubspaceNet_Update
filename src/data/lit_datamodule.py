"""Lightning-compatible DataModule for DOA experiments.

Algorithm summary:
- Build either trajectory or classic datasets from project config.
- Split deterministically into train/val/test.
- Expose DataLoaders used by Lightning training/evaluation entrypoints.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Callable, Optional, Tuple

import torch
from torch.utils.data import DataLoader, Dataset, random_split

from src.data.trajectory import TrajectoryDataHandler, TrajectoryDataset

logger = logging.getLogger("SubspaceNet.data")

try:
    import pytorch_lightning as pl

    _LightningDataModuleBase = pl.LightningDataModule
    _LIGHTNING_AVAILABLE = True
    _LIGHTNING_IMPORT_ERROR = None
except Exception as exc:  # pragma: no cover
    _LightningDataModuleBase = object
    _LIGHTNING_AVAILABLE = False
    _LIGHTNING_IMPORT_ERROR = exc


class DOADataModule(_LightningDataModuleBase):
    """Lightning DataModule for DOA experiments."""

    def __init__(self, config, system_model, trajectory_handler: Optional[TrajectoryDataHandler] = None):
        """Initialize DataModule with config, system model, and optional trajectory handler."""
        if not _LIGHTNING_AVAILABLE:
            raise RuntimeError(
                "pytorch_lightning is required to use DOADataModule. "
                "Install it in the active environment and retry."
            ) from _LIGHTNING_IMPORT_ERROR

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
        """Build full dataset and split to train/val/test deterministically."""
        # ==========================================================================
        # STEP 01: Stage Canonicalization & Gating
        # ==========================================================================
        stage = stage or "fit"

        if stage in ("fit", "validate", "test", "predict"):
            # --------------------------------------------------------------------------
            # step 1.1: Build Full Dataset
            # --------------------------------------------------------------------------
            full_dataset, collate_fn = self._build_dataset(samples_size=self.config.dataset.samples_size)
            self._train_collate_fn = collate_fn
            self._eval_collate_fn = collate_fn

            # --------------------------------------------------------------------------
            # step 1.2: Ratio Normalization & Integer Length Mapping
            # --------------------------------------------------------------------------
            test_ratio, val_ratio, train_ratio = self._normalized_splits()
            train_len, val_len, test_len = self._split_lengths(
                len(full_dataset), test_ratio, val_ratio, train_ratio
            )

            # --------------------------------------------------------------------------
            # step 1.3: Deterministic Random Split
            # --------------------------------------------------------------------------
            # Why: fixed seed=42 keeps split reproducible across runs.
            # Shape Flow: dataset size [S] -> subsets [S_train, S_val, S_test]
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
        """Build training DataLoader."""
        return DataLoader(
            self.train_dataset,
            batch_size=self.config.training.batch_size,
            shuffle=True,
            collate_fn=self._train_collate_fn,
        )

    def val_dataloader(self) -> DataLoader:
        """Build validation DataLoader."""
        return DataLoader(
            self.val_dataset,
            batch_size=self.config.training.batch_size,
            shuffle=False,
            collate_fn=self._eval_collate_fn,
        )

    def test_dataloader(self) -> DataLoader:
        """Build test DataLoader."""
        return DataLoader(
            self.test_dataset,
            batch_size=self.config.training.batch_size,
            shuffle=False,
            collate_fn=self._eval_collate_fn,
        )

    def _build_dataset(self, samples_size: int) -> Tuple[Dataset, Optional[Callable]]:
        """Build either trajectory dataset or classic DCD_MUSIC dataset."""
        # ==========================================================================
        # STEP 01: Trajectory Branch
        # ==========================================================================
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
            # Shape Flow: trajectory item usually [L, N, T] plus variable-cardinality labels.
            return dataset, dataset._collate_trajectories if isinstance(dataset, TrajectoryDataset) else None

        # ==========================================================================
        # STEP 02: Classic DCD_MUSIC Branch
        # ==========================================================================
        from DCD_MUSIC.src.data_handler import create_dataset

        dataset_kwargs = dict(
            samples_size=samples_size,
            save_datasets=self.config.dataset.save_dataset,
            datasets_path=self.dataset_root,
            true_doa=self.config.dataset.true_doa_train,
            true_range=self.config.dataset.true_range_train,
            phase="train",
        )

        try:
            dataset, _ = create_dataset(
                system_model_params=self.system_model.params,
                **dataset_kwargs,
            )
        except TypeError:
            from DCD_MUSIC.src.signal_creation import Samples

            samples_model = Samples(self.system_model.params)
            dataset, _ = create_dataset(
                samples_model=samples_model,
                **dataset_kwargs,
            )
        return dataset, None

    def _normalized_splits(self) -> Tuple[float, float, float]:
        """Normalize split ratios as (test, val, train)."""
        splits = getattr(self.config.dataset, "test_validation_train_split", [0.2, 0.2, 0.6])
        total = sum(splits)
        if total <= 0:
            return 0.2, 0.2, 0.6
        test_ratio, val_ratio, train_ratio = [s / total for s in splits]
        return test_ratio, val_ratio, train_ratio

    @staticmethod
    def _split_lengths(total: int, test_ratio: float, val_ratio: float, train_ratio: float) -> Tuple[int, int, int]:
        """Map ratios to integer split lengths with boundary correction."""
        # ==========================================================================
        # STEP 01: Initial Integer Projection
        # ==========================================================================
        train_len = max(1, int(total * train_ratio)) if total >= 3 else max(1, total - 2)
        val_len = max(1, int(total * val_ratio)) if total >= 3 else 1
        test_len = total - train_len - val_len

        # ==========================================================================
        # STEP 02: Boundary Correction
        # ==========================================================================
        # Why: ensure non-empty test split to avoid evaluation-time empty dataset failures.
        if test_len <= 0:
            test_len = 1
            if train_len > val_len:
                train_len -= 1
            else:
                val_len -= 1
        return train_len, val_len, test_len
