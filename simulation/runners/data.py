"""Compatibility shim for migrated data pipeline modules."""

from src.data_module.trajectory import (
    OnlineLearningDataset,
    OnlineLearningTrajectoryGenerator,
    TrajectoryDataHandler,
    TrajectoryDataset,
    create_online_learning_dataset,
)

__all__ = [
    "TrajectoryDataHandler",
    "TrajectoryDataset",
    "OnlineLearningTrajectoryGenerator",
    "OnlineLearningDataset",
    "create_online_learning_dataset",
]
