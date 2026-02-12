"""Hydra-instantiated runtime runner for scenario dispatch."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class SimulationRuntimeRunner:
    """Dispatch simulation execution by scenario.

    This class is instantiated by Hydra via `_target_` and acts as the
    runtime controller at the entrypoint layer.
    """

    simulation: Any
    scenario: str = "training"

    def run(self) -> Dict[str, Any]:
        scenario = str(self.scenario).lower()
        if scenario == "training":
            return self.simulation.run_training()
        if scenario == "evaluation":
            return self.simulation.run_evaluation()
        if scenario == "online_learning":
            return self.simulation.execute_online_learning()
        if scenario == "full":
            return self.simulation.run()
        raise ValueError(
            f"Unsupported scenario '{scenario}'. Supported: training, evaluation, online_learning, full."
        )

