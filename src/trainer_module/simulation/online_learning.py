"""Online-learning pipeline extracted from the monolithic Simulation class."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from src.trainer_module.online_learning import OnlineLearning


class OnlineLearningPipeline:
    """Delegate online-learning execution to dedicated OnlineLearning handler."""

    def __init__(self, config, components: Dict[str, Any], simulation, output_dir: Path):
        self.config = config
        self.components = components
        self.sim = simulation
        self.output_dir = output_dir

    def execute_online_learning(self) -> Dict[str, Any]:
        """Run online-learning handler and return its result dictionary."""
        # TODO(phase-1-3): if online-learning logic is moved into a Lightning callback
        # or dedicated runtime object, switch this handoff to that implementation.
        online_learning_handler = OnlineLearning(
            config=self.config,
            system_model=self.sim.system_model,
            trained_model=self.sim.trained_model,
            output_dir=self.output_dir,
            results=self.sim.results,
        )
        return online_learning_handler.run_online_learning()
