"""Simulation compatibility package."""

__all__ = ["Simulation", "ScenarioType"]


def __getattr__(name):
    if name == "Simulation":
        from .core import Simulation

        return Simulation
    if name == "ScenarioType":
        from .scenarios import ScenarioType

        return ScenarioType
    raise AttributeError(name)
