"""Deprecated legacy training module.

Split for Phase 4:
- `src.trainer_module.training_config.TrainingConfig`
- `src.trainer_module.trajectory_trainer.TrajectoryTrainer`

This module is kept as a compatibility shim for existing imports.
"""

from src.trainer_module.training_config import TrainingConfig
from src.trainer_module.trajectory_trainer import OnlineTrainer, Trainer, TrajectoryTrainer

__all__ = ["Trainer", "TrainingConfig", "TrajectoryTrainer", "OnlineTrainer"]
