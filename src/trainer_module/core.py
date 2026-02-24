"""Compatibility layer for legacy imports.

The Simulation implementation moved to `src.trainer_module.simulation.runner`.
"""

from src.trainer_module.simulation.runner import Simulation

__all__ = ["Simulation"]
