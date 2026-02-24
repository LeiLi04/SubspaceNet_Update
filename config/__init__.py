"""
SubspaceNet Configuration Framework

This package provides a simplified configuration system for SubspaceNet.
"""

from .schema import (
    Config, 
    SystemModelConfig, 
    DatasetConfig, 
    ModelConfig,
    ModelParamsConfig,
    TrainingConfig,
    SimulationConfig,
    EvaluationConfig,
    TrajectoryConfig,
    KalmanFilterConfig,
    OnlineLearningConfig
)

from .loader import (
    load_config,
    save_config,
    apply_overrides
)
from .utils import (
    create_system_model,
    create_system_model_params,
    import_from_dcd_music,
)

__all__ = [
    'Config',
    'SystemModelConfig',
    'DatasetConfig',
    'ModelConfig',
    'ModelParamsConfig',
    'TrainingConfig',
    'SimulationConfig',
    'EvaluationConfig',
    'TrajectoryConfig',
    'KalmanFilterConfig',
    'OnlineLearningConfig',
    'load_config',
    'save_config',
    'apply_overrides',
    'create_system_model',
    'create_system_model_params',
    'import_from_dcd_music',
]
