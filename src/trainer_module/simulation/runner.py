"""Simulation runner orchestrating training/eval/online-learning pipelines."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional
import logging

import torch

from config.schema import Config
from src.utils.io import save_model_state

from .data_pipeline import DataPipeline
from .eval_pipeline import EvalPipeline
from .online_learning import OnlineLearningPipeline
from .training_pipeline import TrainingPipeline

logger = logging.getLogger(__name__)

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")


class Simulation:
    """Main simulation controller composed from dedicated pipeline objects."""

    def __init__(self, config: Config, components: Dict[str, Any], output_dir: Optional[Path] = None):
        self.config = config
        self.components = components
        self.output_dir = output_dir or Path("experiments/results")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.system_model = components.get("system_model")
        self.model = components.get("model")
        self.lightning_model = components.get("lightning_model")
        self.datamodule = components.get("datamodule")
        self.lightning_trainer = components.get("trainer")
        self.trajectory_handler = components.get("trajectory_handler")

        if self.lightning_model is None and self.model is not None:
            try:
                import pytorch_lightning as pl

                if isinstance(self.model, pl.LightningModule):
                    self.lightning_model = self.model
                    self.model = getattr(self.model, "model", self.model)
            except Exception:
                pass

        self.dataset = None
        self.train_dataloader = None
        self.valid_dataloader = None
        self.test_dataloader = None
        self.online_learning_dataloader = None
        self.trained_model = None
        self.results: Dict[str, Any] = {}

        self.data_pipeline = DataPipeline(config=self.config, components=self.components, simulation=self)
        self.training_pipeline = TrainingPipeline(
            config=self.config,
            components=self.components,
            simulation=self,
            output_dir=self.output_dir,
        )
        self.eval_pipeline = EvalPipeline(
            config=self.config,
            components=self.components,
            simulation=self,
            output_dir=self.output_dir,
        )
        self.online_learning_pipeline = OnlineLearningPipeline(
            config=self.config,
            components=self.components,
            simulation=self,
            output_dir=self.output_dir,
        )

        if self.config.trajectory.enabled and self.trajectory_handler is None:
            self.data_pipeline.create_trajectory_handler()

        logger.info("Simulation initialized with output directory: %s", self.output_dir)
        logger.info("Trajectory mode: %s", "Enabled" if self.config.trajectory.enabled else "Disabled")

    def run(self) -> Dict[str, Any]:
        """Run complete pipeline: training -> evaluation -> online learning."""
        logger.info("Starting complete simulation (training, evaluation, and online learning)")
        training_results = self.run_training()
        if training_results.get("status") == "error":
            return training_results

        if self.config.simulation.evaluate_model:
            evaluation_results = self.run_evaluation()
            for key, value in evaluation_results.items():
                if key != "status":
                    training_results[key] = value

        if hasattr(self.config, "online_learning") and getattr(self.config.online_learning, "enabled", False):
            online_results = self.execute_online_learning()
            for key, value in online_results.items():
                if key != "status":
                    training_results[key] = value

        return training_results

    def run_training(self) -> Dict[str, Any]:
        """Run data + training pipeline for training scenario."""
        logger.info("Starting training pipeline")
        try:
            use_lightning_stack = (
                self.lightning_model is not None
                and self.datamodule is not None
                and self.lightning_trainer is not None
            )

            if use_lightning_stack:
                logger.info("Using instantiated Lightning datamodule/trainer; skipping legacy data pipeline")
            else:
                self.data_pipeline._run_data_pipeline(scenario="training")
                if self.train_dataloader is None:
                    logger.error("Data pipeline failed, skipping training")
                    return {"status": "error", "message": "Data pipeline failed"}

            if self.config.simulation.load_model:
                if hasattr(self.config.simulation, "model_path") and self.config.simulation.model_path:
                    model_path = Path(self.config.simulation.model_path)
                    success, message = self.training_pipeline._load_and_apply_weights(model_path, DEVICE)
                    if not success:
                        return {"status": "error", "message": message}
                else:
                    logger.error("Model loading requested but no model_path provided in config")
                    return {"status": "error", "message": "No model_path provided"}

            if self.config.training.enabled and self.config.simulation.train_model:
                logger.info("Running training pipeline (training.enabled=True, simulation.train_model=True)")
                self.training_pipeline._run_training_pipeline()
                if self.trained_model is None:
                    logger.error("Training pipeline failed")
                    return {"status": "error", "message": "Training pipeline failed"}
            elif not self.config.simulation.train_model:
                logger.info("Skipping training (simulation.train_model=False)")
            elif not self.config.training.enabled:
                logger.info("Skipping training (training.enabled=False)")

            if self.config.simulation.save_model and self.trained_model is not None:
                save_model_state(self.trained_model, self.output_dir, f"{self.config.model.type}_trained")

            self.eval_pipeline._save_results()
            return {"status": "success", "trained_model": self.trained_model is not None}
        except Exception as exc:
            logger.exception("Error running training: %s", exc)
            return {"status": "error", "message": str(exc), "exception": type(exc).__name__}

    def run_evaluation(self) -> Dict[str, Any]:
        """Run data + evaluation pipeline for evaluation scenario."""
        logger.info("Starting evaluation pipeline")
        try:
            self.data_pipeline._run_data_pipeline(scenario="evaluation")
            if self.test_dataloader is None:
                logger.error("Data pipeline failed, cannot create test dataset")
                return {"status": "error", "message": "Failed to create test dataset"}

            if self.config.simulation.load_model:
                if hasattr(self.config.simulation, "model_path") and self.config.simulation.model_path:
                    model_path = Path(self.config.simulation.model_path)
                    logger.info("Loading model from path: %s", model_path)
                    success, message = self.training_pipeline._load_and_apply_weights(model_path, DEVICE)
                    if not success:
                        logger.error("Failed to load model: %s", message)
                        return {"status": "error", "message": message}
                else:
                    logger.error("Model loading requested but no model_path provided in config")
                    return {"status": "error", "message": "No model_path provided"}

            if self.trained_model is None:
                if self.model is not None:
                    logger.info("Using non-trained model for evaluation")
                    self.trained_model = self.model
                else:
                    logger.error("No model available for evaluation")
                    return {"status": "error", "message": "No model available for evaluation"}

            self.eval_pipeline._run_evaluation_pipeline()
            self.eval_pipeline._save_results()
            return {"status": "success", "evaluation_results": self.results}
        except Exception as exc:
            logger.exception("Error running evaluation: %s", exc)
            return {"status": "error", "message": str(exc), "exception": type(exc).__name__}

    def execute_online_learning(self) -> Dict[str, Any]:
        """Run online-learning scenario."""
        logger.info("Starting online learning pipeline")
        try:
            if self.config.simulation.load_model:
                if hasattr(self.config.simulation, "model_path") and self.config.simulation.model_path:
                    model_path = Path(self.config.simulation.model_path)
                    logger.info("Loading model from path: %s", model_path)
                    success, message = self.training_pipeline._load_and_apply_weights(model_path, DEVICE)
                    if not success:
                        logger.error("Failed to load model: %s", message)
                        return {"status": "error", "message": message}
                else:
                    logger.error("Model loading requested but no model_path provided in config")
                    return {"status": "error", "message": "No model_path provided"}

            if self.trained_model is None:
                if self.model is not None:
                    logger.info("Using non-trained model for online learning")
                    self.trained_model = self.model
                else:
                    logger.error("No model available for online learning")
                    return {"status": "error", "message": "No model available for online learning"}

            result = self.online_learning_pipeline.execute_online_learning()
            self.eval_pipeline._save_results()
            return result
        except Exception as exc:
            logger.exception("Error running online learning: %s", exc)
            return {"status": "error", "message": str(exc), "exception": type(exc).__name__}

    def run_scenario(self, scenario_type: str, values: List[Any], full_mode: bool = False) -> Dict[str, Dict[str, Any]]:
        """Run parametric scenario sweeps."""
        logger.info("Running %s scenario with values: %s", scenario_type, values)
        scenario_results: Dict[str, Dict[str, Any]] = {}

        model_paths = None
        if (
            hasattr(self.config, "scenario_config")
            and hasattr(self.config.scenario_config, "model_paths")
            and self.config.scenario_config.model_paths
        ):
            model_paths = self.config.scenario_config.model_paths
            logger.info("Found %d model paths in scenario_config for scenario sweep", len(model_paths))

        for idx, value in enumerate(values):
            logger.info("Running scenario with %s=%s", scenario_type, value)
            overrides = [f"system_model.{scenario_type.lower()}={value}"]

            if model_paths and idx < len(model_paths):
                model_path = model_paths[idx]
                overrides.append(f"simulation.model_path={model_path}")
                logger.info("Using model path for %s=%s: %s", scenario_type, value, model_path)
            else:
                overrides.append("simulation.model_path=null")

            from config.loader import apply_overrides
            modified_config = apply_overrides(self.config, overrides)

            from config_handler import update_components_for_sweep
            updated_components = update_components_for_sweep(
                components=self.components,
                config=modified_config,
                sweep_param=scenario_type,
                sweep_value=value,
            )

            simulation = Simulation(
                config=modified_config,
                components=updated_components,
                output_dir=self.output_dir / f"{scenario_type}_{value}",
            )

            if full_mode:
                result = simulation.run()
            elif self.config.simulation.evaluate_model and not self.config.simulation.train_model:
                logger.info("Running evaluation for %s=%s", scenario_type, value)
                result = simulation.run_evaluation()
            elif self.config.simulation.load_model and not self.config.simulation.train_model:
                logger.info("Running online learning for %s=%s", scenario_type, value)
                result = simulation.execute_online_learning()
            else:
                result = simulation.run_training()

            scenario_results[value] = result

        self.results[scenario_type] = scenario_results
        return scenario_results

    # Compatibility wrappers for legacy callers.
    def _run_data_pipeline(self, scenario: str = "training") -> None:
        self.data_pipeline._run_data_pipeline(scenario)

    def _prepare_test_dataset(self) -> None:
        self.data_pipeline._prepare_test_dataset()

    def _prepare_online_learning_dataset(self) -> None:
        self.data_pipeline._prepare_online_learning_dataset()

    def _create_trajectory_dataset(self):
        return self.data_pipeline._create_trajectory_dataset()

    def _create_standard_dataset(self):
        return self.data_pipeline._create_standard_dataset()

    def _load_standard_dataset(self):
        return self.data_pipeline._load_standard_dataset()

    def _run_training_pipeline(self) -> None:
        self.training_pipeline._run_training_pipeline()

    def _run_evaluation_pipeline(self) -> None:
        self.eval_pipeline._run_evaluation_pipeline()

    def _save_results(self) -> None:
        self.eval_pipeline._save_results()

    def _load_and_apply_weights(self, model_path: Path, device: torch.device):
        return self.training_pipeline._load_and_apply_weights(model_path, device)
