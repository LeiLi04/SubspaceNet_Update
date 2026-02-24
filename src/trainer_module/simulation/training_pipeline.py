"""Training pipeline extracted from the monolithic Simulation class."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional, Tuple
import logging

import torch

from src.trainer_module.training import TrainingConfig, TrajectoryTrainer

logger = logging.getLogger(__name__)


class TrainingPipeline:
    """Run training and weight-loading flows."""

    def __init__(self, config, components: Dict[str, Any], simulation, output_dir: Path):
        self.config = config
        self.components = components
        self.sim = simulation
        self.output_dir = output_dir

    def _run_training_pipeline(self) -> None:
        """Execute training pipeline with trajectory and Lightning branch support."""
        logger.info("Starting training pipeline")

        use_trajectory_training = self.config.trajectory.enabled
        use_lightning_training = (
            self.sim.lightning_model is not None
            and self.sim.datamodule is not None
            and self.sim.lightning_trainer is not None
        ) or bool(getattr(self.config.training, "use_lightning", False))

        if use_lightning_training:
            mode = "trajectory" if use_trajectory_training else "non-trajectory"
            logger.info("Using Lightning-native trainer path for %s training", mode)
            self._run_lightning_training_pipeline()
            return

        training_config = TrainingConfig(
            learning_rate=self.config.training.learning_rate,
            weight_decay=self.config.training.weight_decay,
            epochs=self.config.training.epochs,
            batch_size=self.config.training.batch_size,
            optimizer=self.config.training.optimizer,
            scheduler=self.config.training.scheduler,
            step_size=self.config.training.step_size,
            gamma=self.config.training.gamma,
            training_objective=self.config.training.training_objective,
            save_checkpoint=getattr(self.config.training, "save_checkpoint", True),
            checkpoint_path=self.output_dir / "checkpoints",
        )

        trainer = self._initialize_trainer(
            use_trajectory_training=use_trajectory_training,
            training_config=training_config,
        )
        self.components["trainer"] = trainer

        logger.info("Starting model training with %d epochs", training_config.epochs)
        self.sim.trained_model = trainer.train(
            self.sim.train_dataloader,
            self.sim.valid_dataloader,
            seed=42,
        )
        self.components["model"] = self.sim.trained_model
        logger.info("Training completed")

    def _initialize_trainer(self, use_trajectory_training: bool, training_config: TrainingConfig):
        """Create trainer object from current config and mode."""
        if use_trajectory_training:
            logger.info("Using trajectory-based trainer")
            return TrajectoryTrainer(
                model=self.sim.model,
                config=training_config,
                output_dir=self.output_dir,
            )

        logger.info("Using standard trainer")
        if "trainer" in self.components:
            logger.info("Using pre-created trainer from components")
            return self.components["trainer"]

        from DCD_MUSIC.src.training import Trainer as DCDTrainer, TrainingParamsNew

        training_params = TrainingParamsNew(
            learning_rate=training_config.learning_rate,
            weight_decay=training_config.weight_decay,
            epochs=training_config.epochs,
            optimizer=training_config.optimizer,
            scheduler=training_config.scheduler,
            step_size=training_config.step_size,
            gamma=training_config.gamma,
            training_objective=training_config.training_objective,
            batch_size=training_config.batch_size,
        )

        return DCDTrainer(
            model=self.sim.model,
            training_params=training_params,
            show_plots=False,
        )

    def _run_lightning_training_pipeline(self) -> None:
        """Execute Lightning Trainer.fit path."""
        try:
            import pytorch_lightning as pl
        except Exception as exc:
            raise RuntimeError(
                "pytorch_lightning is required for training.use_lightning=true, but import failed."
            ) from exc

        from src.model_module.lit_module import LegacyLightningModule

        logging.getLogger("lightning_utilities.core.rank_zero").setLevel(logging.ERROR)
        logging.getLogger("pytorch_lightning.utilities.rank_zero").setLevel(logging.ERROR)
        logging.getLogger("pytorch_lightning").setLevel(logging.WARNING)

        lightning_model = self.sim.lightning_model
        if lightning_model is None:
            lightning_model = LegacyLightningModule(
                model=self.sim.model,
                learning_rate=float(self.config.training.learning_rate),
            )
            self.sim.lightning_model = lightning_model
            self.components["lightning_model"] = lightning_model

        datamodule = self.sim.datamodule
        if datamodule is None:
            from src.data_module.lit_datamodule import DOADataModule

            datamodule = DOADataModule(
                config=self.config,
                system_model=self.sim.system_model,
                trajectory_handler=self.sim.trajectory_handler,
            )
            self.sim.datamodule = datamodule
            self.components["datamodule"] = datamodule

        trainer = self.sim.lightning_trainer
        if trainer is None or not isinstance(trainer, pl.Trainer):
            trainer = pl.Trainer(
                max_epochs=int(getattr(self.config.training, "epochs", 1)),
                accelerator="auto",
                devices="auto",
            )
            self.sim.lightning_trainer = trainer
            self.components["trainer"] = trainer

        trainer.fit(lightning_model, datamodule=datamodule)

        self.sim.trained_model = getattr(lightning_model, "model", lightning_model)
        self.sim.model = self.sim.trained_model
        self.components["model"] = self.sim.trained_model
        logger.info("Lightning-native training completed")

    def _load_and_apply_weights(self, model_path: Path, device: torch.device) -> Tuple[bool, Optional[str]]:
        """Load weights from checkpoint path and apply to current model."""
        logger.info("Attempting to load model weights from: %s", model_path)
        target_model = self.sim.model
        if target_model is None and self.sim.lightning_model is not None:
            target_model = getattr(self.sim.lightning_model, "model", self.sim.lightning_model)
            self.sim.model = target_model

        if "*" in str(model_path):
            import glob

            expanded_paths = glob.glob(str(model_path))
            if not expanded_paths:
                return False, f"No files found matching pattern: {model_path}"
            if len(expanded_paths) > 1:
                logger.warning(
                    "Multiple files found for pattern %s: %s. Using the first one.",
                    model_path,
                    expanded_paths,
                )
            model_path = Path(expanded_paths[0])
            logger.info("Expanded wildcard to: %s", model_path)

        try:
            try:
                try:
                    import torch.serialization

                    torch.serialization.add_safe_globals(["numpy._core.multiarray.scalar"])
                    logger.info("Added numpy.scalar to PyTorch safe globals list")
                except Exception as exc:
                    logger.warning("Could not add numpy.scalar to safe globals: %s", exc)

                state_dict = torch.load(model_path, map_location=device)
            except Exception as exc:
                logger.warning(
                    "Standard loading failed, attempting with backward compatibility mode: %s",
                    exc,
                )
                try:
                    state_dict = torch.load(model_path, map_location=device, weights_only=False)
                except Exception as exc2:
                    try:
                        logger.warning("Compatibility mode failed, trying with safe_globals context manager")
                        from torch.serialization import safe_globals

                        with safe_globals(["numpy._core.multiarray.scalar"]):
                            state_dict = torch.load(model_path, map_location=device)
                    except Exception as exc3:
                        raise RuntimeError(
                            "Failed to load checkpoint file with all methods: "
                            f"{exc}, then: {exc2}, then: {exc3}"
                        )

            if isinstance(state_dict, dict):
                possible_keys = [
                    "model_state_dict",
                    "state_dict",
                    "model",
                    "network",
                    "net_state_dict",
                    "net",
                    "weights",
                    "params",
                    "parameters",
                ]

                model_keys = target_model.state_dict().keys()
                is_direct_weights = any(k in state_dict for k in model_keys)

                if not is_direct_weights:
                    found_key = None
                    for key in possible_keys:
                        if key in state_dict and isinstance(state_dict[key], dict):
                            nested_dict = state_dict[key]
                            if any(k in nested_dict for k in model_keys):
                                found_key = key
                                logger.info("Found model weights in checkpoint under '%s' key", key)
                                state_dict = nested_dict
                                break
                    if not found_key:
                        logger.warning(
                            "Could not find model weights in checkpoint. Available keys: %s",
                            list(state_dict.keys()),
                        )
                        logger.warning("Will attempt to use checkpoint as-is - this may fail")
            else:
                logger.warning(
                    "Loaded checkpoint is not a dictionary (type: %s). Attempting to use as-is.",
                    type(state_dict),
                )

            try:
                if isinstance(state_dict, dict) and all(k.startswith("module.") for k in state_dict.keys()):
                    logger.info("Detected DataParallel wrapped model weights - removing 'module.' prefix")
                    state_dict = {k.replace("module.", ""): v for k, v in state_dict.items()}

                target_model.load_state_dict(state_dict, strict=True)
                logger.info("Model weights loaded successfully (strict=True)")
                target_model = target_model.to(device)
                self.sim.model = target_model
                self.sim.trained_model = target_model
                return True, "Model loaded successfully"
            except RuntimeError as exc:
                logger.warning("Strict loading failed: %s. Attempting partial loading (strict=False).", exc)

                if isinstance(state_dict, dict):
                    model_keys_set = set(target_model.state_dict().keys())
                    state_dict_keys_set = set(state_dict.keys())
                    missing_keys = model_keys_set - state_dict_keys_set
                    unexpected_keys = state_dict_keys_set - model_keys_set
                    if missing_keys:
                        logger.warning("Missing keys in checkpoint: %s", missing_keys)
                    if unexpected_keys:
                        logger.warning("Unexpected keys in checkpoint: %s", unexpected_keys)
                else:
                    logger.warning("Cannot perform key comparison: loaded state_dict is not a dictionary.")

                try:
                    if isinstance(state_dict, dict) and all(k.startswith("module.") for k in state_dict.keys()):
                        state_dict = {k.replace("module.", ""): v for k, v in state_dict.items()}

                    if not isinstance(state_dict, dict):
                        raise TypeError(
                            f"Cannot load state_dict: Expected a dictionary, but got {type(state_dict)}"
                        )

                    incompatible_keys = target_model.load_state_dict(state_dict, strict=False)
                    if incompatible_keys.missing_keys:
                        logger.warning("Partial loading: Missing keys: %s", incompatible_keys.missing_keys)
                    if incompatible_keys.unexpected_keys:
                        logger.warning(
                            "Partial loading: Unexpected keys: %s", incompatible_keys.unexpected_keys
                        )

                    if incompatible_keys.missing_keys and len(incompatible_keys.missing_keys) >= len(target_model.state_dict()):
                        raise RuntimeError("Partial loading failed: No matching keys found.")

                    target_model = target_model.to(device)
                    self.sim.model = target_model
                    self.sim.trained_model = target_model
                    msg = (
                        "Model partially loaded. "
                        f"Missing: {incompatible_keys.missing_keys}, "
                        f"Unexpected: {incompatible_keys.unexpected_keys}"
                    )
                    logger.info(msg)
                    return True, msg
                except Exception as exc2:
                    logger.error("Strict and partial loading both failed: %s", exc2)
                    return False, f"Failed to apply state_dict to model. Strict error: {exc}. Partial error: {exc2}"

        except Exception as load_err:
            logger.error("Failed to load or apply model weights from %s: %s", model_path, load_err)
            return False, f"Error during model loading: {load_err}"
