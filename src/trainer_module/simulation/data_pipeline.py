"""Data preparation pipeline extracted from the monolithic Simulation class."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Tuple
import logging

import torch

from src.data_module.trajectory import TrajectoryDataHandler, create_online_learning_dataset

logger = logging.getLogger(__name__)


class DataPipeline:
    """Create/load datasets and expose train/val/test/online dataloaders."""

    def __init__(self, config, components: Dict[str, Any], simulation):
        self.config = config
        self.components = components
        self.sim = simulation

    def create_trajectory_handler(self) -> None:
        """Create a trajectory data handler if not already present."""
        if self.sim.trajectory_handler is None and self.config.trajectory.enabled:
            logger.info("Creating trajectory data handler")
            self.sim.trajectory_handler = TrajectoryDataHandler(
                system_model_params=self.sim.system_model.params,
                config=self.config,
            )
            self.components["trajectory_handler"] = self.sim.trajectory_handler
            logger.info("Trajectory data handler created successfully")

    def _run_data_pipeline(self, scenario: str = "training") -> None:
        """Run scenario-specific data preparation."""
        logger.info("Starting data pipeline for scenario: %s", scenario)

        if scenario == "evaluation":
            self._prepare_test_dataset()
            return

        if scenario == "online_learning":
            self._prepare_online_learning_dataset()
            return

        if scenario != "training":
            logger.error("Invalid scenario: %s", scenario)
            raise ValueError(f"Invalid scenario: {scenario}")

        if self.config.trajectory.enabled:
            if self.sim.trajectory_handler is None:
                logger.error("Trajectory mode enabled but no trajectory_handler found")
                return
            logger.info("Using trajectory-based data pipeline")
            dataset, samples_model = self._create_trajectory_dataset()
            self.components["samples_model"] = samples_model
        else:
            # TODO(phase-1-3): once Lightning DataModule is the canonical path,
            # route dataset/dataloader setup through instantiated `cfg.data`.
            if self.config.dataset.create_data:
                logger.info("Creating new dataset")
                dataset = self._create_standard_dataset()
            else:
                logger.info("Loading existing dataset")
                dataset = self._load_standard_dataset()

        if dataset is None:
            logger.error("Failed to create or load dataset")
            return

        self.sim.dataset = dataset
        self.components["dataset"] = dataset

        if "trainer" in self.components and self.components["trainer"] is not None:
            logger.info("Updating trainer with created dataset")
            self.components["trainer"].dataset = dataset

        logger.info("Creating dataloaders with batch size: %d", self.config.training.batch_size)
        splits = getattr(self.config.dataset, "test_validation_train_split", [0.1, 0.1, 0.8])
        total = sum(splits)
        if abs(total - 1.0) > 1e-6:
            splits = [p / total for p in splits]

        test_prop, val_prop, train_prop = splits
        logger.info("Using split: test=%.2f, val=%.2f, train=%.2f", test_prop, val_prop, train_prop)

        val_split = val_prop / (train_prop + val_prop) if (train_prop + val_prop) > 0 else 0

        if hasattr(dataset, "get_dataloaders"):
            self.sim.train_dataloader, self.sim.valid_dataloader = dataset.get_dataloaders(
                batch_size=self.config.training.batch_size,
                validation_split=val_split,
            )
        else:
            from torch.utils.data import DataLoader, random_split

            total_len = len(dataset)
            train_len = int(total_len * (1.0 - val_split))
            val_len = total_len - train_len
            if train_len <= 0 and total_len > 0:
                train_len = 1
                val_len = max(0, total_len - 1)
            if val_len <= 0 and total_len > 1:
                val_len = 1
                train_len = total_len - 1

            train_ds, val_ds = random_split(
                dataset,
                [train_len, val_len],
                generator=torch.Generator().manual_seed(42),
            )
            self.sim.train_dataloader = DataLoader(
                train_ds,
                batch_size=self.config.training.batch_size,
                shuffle=True,
            )
            self.sim.valid_dataloader = DataLoader(
                val_ds,
                batch_size=self.config.training.batch_size,
                shuffle=False,
            )

        logger.info(
            "Created dataloaders: train=%d, val=%d",
            len(self.sim.train_dataloader),
            len(self.sim.valid_dataloader),
        )

        self.components["train_dataloader"] = self.sim.train_dataloader
        self.components["valid_dataloader"] = self.sim.valid_dataloader

        self._prepare_test_dataset()

    def _prepare_test_dataset(self) -> None:
        """Create test dataset and dataloader."""
        splits = getattr(self.config.dataset, "test_validation_train_split", [0.1, 0.1, 0.8])
        total = sum(splits)
        if abs(total - 1.0) > 1e-6:
            splits = [p / total for p in splits]

        test_prop = splits[0]
        test_samples_size = max(1, int(self.config.dataset.samples_size * test_prop))
        logger.info("Creating test dataset: %d samples (%.0f%%)", test_samples_size, test_prop * 100)

        if self.config.trajectory.enabled:
            if self.sim.trajectory_handler is None:
                logger.error("Trajectory mode enabled but no trajectory_handler found for testing")
                return
            test_dataset, _ = self._create_trajectory_dataset_for_testing(test_samples_size)
        else:
            test_dataset = self._create_standard_test_dataset(test_samples_size)

        if test_dataset is None:
            logger.error("Failed to create test dataset")
            return

        from torch.utils.data import DataLoader

        self.sim.test_dataloader = DataLoader(
            test_dataset,
            batch_size=self.config.training.batch_size,
            shuffle=False,
            collate_fn=test_dataset._collate_trajectories if hasattr(test_dataset, "_collate_trajectories") else None,
        )
        logger.info("Created test dataloader with %d batches", len(self.sim.test_dataloader))
        self.components["test_dataloader"] = self.sim.test_dataloader

    def _prepare_online_learning_dataset(self) -> None:
        """Create online-learning dataloader if online learning is enabled."""
        if hasattr(self.config, "online_learning") and getattr(self.config.online_learning, "enabled", False):
            logger.info("Online learning is enabled, creating on-demand dataset and dataloader.")
            if not self.config.trajectory.enabled:
                logger.warning(
                    "Online learning typically relies on trajectory mode. "
                    "Ensure config is appropriate when trajectory.enabled is False."
                )

            if self.sim.system_model is None or not hasattr(self.sim.system_model, "params") or self.sim.system_model.params is None:
                logger.error(
                    "SystemModel or its params unavailable for online learning dataset creation. "
                    "Online learning will be skipped."
                )
                self.sim.online_learning_dataloader = None
                return

            online_config = self.config.online_learning
            window_size = getattr(online_config, "window_size", 10)
            stride = getattr(online_config, "stride", 5)

            try:
                online_dataset = create_online_learning_dataset(
                    system_model_params=self.sim.system_model.params,
                    config=self.config,
                    window_size=window_size,
                    stride=stride,
                )
                self.sim.online_learning_dataloader = online_dataset.get_dataloader(batch_size=1, shuffle=False)
                logger.info(
                    "Created on-demand online learning dataloader for %d windows.",
                    len(self.sim.online_learning_dataloader),
                )
                self.components["online_learning_dataloader"] = self.sim.online_learning_dataloader
            except ValueError as exc:
                logger.error("Error creating online learning dataset: %s. Online learning may not function.", exc)
                self.sim.online_learning_dataloader = None
            except Exception as exc:
                logger.exception("Unexpected error during online learning dataset creation: %s", exc)
                self.sim.online_learning_dataloader = None
            return

        self.sim.online_learning_dataloader = None
        logger.info("Online learning is not enabled. Skipping online learning dataset creation.")

    def _create_trajectory_dataset(self) -> Tuple[Any, Any]:
        """Create trajectory dataset used for training/validation."""
        return self.sim.trajectory_handler.create_dataset(
            samples_size=self.config.dataset.samples_size,
            trajectory_length=self.config.trajectory.trajectory_length,
            trajectory_type=self.config.trajectory.trajectory_type,
            save_dataset=self.config.trajectory.save_trajectory,
            dataset_path=Path("data/datasets").absolute(),
        )

    def _create_standard_dataset(self) -> Any:
        """Create standard (non-trajectory) dataset."""
        from DCD_MUSIC.src.data_handler import create_dataset

        try:
            dataset_kwargs = dict(
                samples_size=self.config.dataset.samples_size,
                save_datasets=self.config.dataset.save_dataset,
                datasets_path=Path("data/datasets").absolute(),
                true_doa=self.config.dataset.true_doa_train,
                true_range=self.config.dataset.true_range_train,
                phase="train",
            )

            try:
                dataset, samples_model = create_dataset(
                    system_model_params=self.sim.system_model.params,
                    **dataset_kwargs,
                )
            except TypeError:
                from DCD_MUSIC.src.signal_creation import Samples

                samples_model = Samples(self.sim.system_model.params)
                dataset, _ = create_dataset(samples_model=samples_model, **dataset_kwargs)

            self.components["samples_model"] = samples_model
            return dataset
        except Exception as exc:
            logger.error("Failed to create standard dataset: %s", exc)
            return None

    def _load_standard_dataset(self) -> Any:
        """Load standard (non-trajectory) dataset."""
        from DCD_MUSIC.src.data_handler import load_datasets

        try:
            dataset = load_datasets(
                system_model_params=self.sim.system_model.params,
                samples_size=self.config.dataset.samples_size,
                datasets_path=Path("data/datasets").absolute(),
                is_training=True,
            )
            return dataset
        except Exception as exc:
            logger.error("Failed to load dataset: %s", exc)
            return None

    def _create_trajectory_dataset_for_testing(self, samples_size: int) -> Tuple[Any, Any]:
        """Create trajectory dataset specifically for testing."""
        return self.sim.trajectory_handler.create_dataset(
            samples_size=samples_size,
            trajectory_length=self.config.trajectory.trajectory_length,
            trajectory_type=self.config.trajectory.trajectory_type,
            save_dataset=False,
            dataset_path=Path("data/datasets").absolute(),
        )

    def _create_standard_test_dataset(self, samples_size: int) -> Any:
        """Create standard (non-trajectory) dataset for testing."""
        from DCD_MUSIC.src.data_handler import create_dataset

        dataset_kwargs = dict(
            samples_size=samples_size,
            save_datasets=False,
            datasets_path=Path("data/datasets").absolute(),
            true_doa=self.config.dataset.true_doa_test
            if hasattr(self.config.dataset, "true_doa_test")
            else self.config.dataset.true_doa_train,
            true_range=self.config.dataset.true_range_test
            if hasattr(self.config.dataset, "true_range_test")
            else self.config.dataset.true_range_train,
            phase="test",
        )

        try:
            dataset, _ = create_dataset(system_model_params=self.sim.system_model.params, **dataset_kwargs)
        except TypeError:
            from DCD_MUSIC.src.signal_creation import Samples

            samples_model = Samples(self.sim.system_model.params)
            dataset, _ = create_dataset(samples_model=samples_model, **dataset_kwargs)
        return dataset
