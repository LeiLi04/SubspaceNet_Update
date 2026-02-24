"""DEPRECATED: legacy component factories replaced by direct Hydra `_target_` configs."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

from config.factory import create_model, create_trajectory_data_handler, create_trainer


@dataclass
class DataComponentFactory:
    """Build data-related runtime components from unified config."""

    cfg_obj: Any

    def __init__(self, cfg_obj: Any, **_: Any) -> None:
        self.cfg_obj = cfg_obj

    def build(self, system_model: Any) -> Optional[Any]:
        if not getattr(self.cfg_obj.trajectory, "enabled", False):
            return None
        return create_trajectory_data_handler(self.cfg_obj, system_model)


@dataclass
class ModelComponentFactory:
    """Build model component from unified config."""

    cfg_obj: Any

    def __init__(self, cfg_obj: Any, **_: Any) -> None:
        self.cfg_obj = cfg_obj

    def build(self, system_model: Any) -> Any:
        return create_model(self.cfg_obj, system_model)


@dataclass
class TrainerComponentFactory:
    """Build trainer component from unified config."""

    cfg_obj: Any

    def __init__(self, cfg_obj: Any, **_: Any) -> None:
        self.cfg_obj = cfg_obj

    def build(self, model: Any) -> Optional[Any]:
        if not getattr(self.cfg_obj.training, "enabled", False):
            return None
        if bool(getattr(self.cfg_obj.training, "use_lightning", False)):
            # Lightning path creates its own trainer in runtime pipeline.
            return None
        return create_trainer(self.cfg_obj, model, None)
