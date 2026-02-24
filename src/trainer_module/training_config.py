"""Legacy training configuration container."""

from __future__ import annotations

from pathlib import Path


class TrainingConfig:
    """Container for legacy trainer hyperparameters."""

    def __init__(self, **kwargs):
        self.learning_rate = 0.001
        self.weight_decay = 1e-9
        self.epochs = 50
        self.optimizer = "Adam"
        self.scheduler = "StepLR"
        self.step_size = 50
        self.gamma = 0.5
        self.batch_size = 32
        self.save_checkpoint = True
        self.checkpoint_path = Path("experiments/checkpoints")
        self.training_objective = "angle"
        self.__dict__.update(kwargs)

    def __getitem__(self, key):
        return self.__dict__[key]

    def __setitem__(self, key, value):
        self.__dict__[key] = value

    def get(self, key, default=None):
        return self.__dict__.get(key, default)

    def update(self, new_params):
        self.__dict__.update(new_params)
