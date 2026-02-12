"""Hydra-based training entrypoint (native-first with compatibility fallback)."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Iterable, List
import logging
import sys

# Allow direct script execution in edge cases.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import hydra
from omegaconf import DictConfig, OmegaConf

from config.factory import create_components_from_config, create_system_model
from config.loader import apply_overrides, load_config
from config.schema import Config
from src.train.core import Simulation

LOGGER = logging.getLogger("SubspaceNet.hydra")

_CANONICAL_SECTIONS: tuple[str, ...] = (
    "system_model",
    "dataset",
    "model",
    "training",
    "simulation",
    "evaluation",
    "trajectory",
    "kalman_filter",
    "online_learning",
    "logging",
)


def _encode_override_value(value: Any) -> str:
    """Encode a Python value as a CLI-style override string value."""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, list):
        return ",".join(str(v) for v in value)
    return str(value)


def _flatten_mapping(prefix: str, mapping: Dict[str, Any]) -> Iterable[str]:
    """Flatten nested mapping into dotted `key=value` override strings."""
    for key, value in mapping.items():
        if key.startswith("_"):
            continue
        dotted_key = f"{prefix}.{key}" if prefix else key
        if isinstance(value, dict):
            yield from _flatten_mapping(dotted_key, value)
        else:
            yield f"{dotted_key}={_encode_override_value(value)}"


def _strip_private_keys(value: Any) -> Any:
    """Recursively drop Hydra/private keys like `_target_` from a mapping."""
    if isinstance(value, dict):
        return {k: _strip_private_keys(v) for k, v in value.items() if not str(k).startswith("_")}
    if isinstance(value, list):
        return [_strip_private_keys(v) for v in value]
    return value


def _build_legacy_overrides(cfg: DictConfig) -> List[str]:
    """Build overrides consumed by `config.loader.apply_overrides`."""
    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(cfg_dict, dict):
        return []

    overrides: List[str] = []

    for section in _CANONICAL_SECTIONS:
        section_data = cfg_dict.get(section)
        if isinstance(section_data, dict):
            overrides.extend(_flatten_mapping(section, section_data))

    data_cfg = cfg_dict.get("data")
    if isinstance(data_cfg, dict):
        for key in ("create_data", "save_dataset", "samples_size"):
            if key in data_cfg:
                overrides.append(f"dataset.{key}={_encode_override_value(data_cfg[key])}")

    trainer_cfg = cfg_dict.get("trainer")
    if isinstance(trainer_cfg, dict):
        trainer_map = {
            "max_epochs": "epochs",
            "batch_size": "batch_size",
            "learning_rate": "learning_rate",
            "weight_decay": "weight_decay",
        }
        for source_key, target_key in trainer_map.items():
            if source_key in trainer_cfg:
                overrides.append(
                    f"training.{target_key}={_encode_override_value(trainer_cfg[source_key])}"
                )

    deduped: List[str] = []
    seen: set[str] = set()
    for item in overrides:
        if item in seen:
            continue
        seen.add(item)
        deduped.append(item)
    return deduped


def _build_native_config(cfg: DictConfig) -> Config:
    """Build pydantic Config directly from composed Hydra config."""
    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(cfg_dict, dict):
        return Config()

    payload: Dict[str, Any] = {}
    for section in _CANONICAL_SECTIONS:
        section_data = cfg_dict.get(section)
        if isinstance(section_data, dict):
            payload[section] = _strip_private_keys(section_data)

    data_cfg = cfg_dict.get("data")
    if isinstance(data_cfg, dict):
        dataset_payload = payload.setdefault("dataset", {})
        for key in ("create_data", "save_dataset", "samples_size"):
            if key in data_cfg:
                dataset_payload[key] = data_cfg[key]

    trainer_cfg = cfg_dict.get("trainer")
    if isinstance(trainer_cfg, dict):
        training_payload = payload.setdefault("training", {})
        trainer_map = {
            "max_epochs": "epochs",
            "batch_size": "batch_size",
            "learning_rate": "learning_rate",
            "weight_decay": "weight_decay",
        }
        for source_key, target_key in trainer_map.items():
            if source_key in trainer_cfg:
                # Keep canonical training.* as source of truth when already present.
                training_payload.setdefault(target_key, trainer_cfg[source_key])

    return Config(**payload)


@hydra.main(
    version_base=None,
    config_path=str((Path(__file__).resolve().parents[1] / "configs")),
    config_name="config",
)
def main(cfg: DictConfig) -> None:
    """Run SubspaceNet using Hydra composition with native-first component instantiation."""
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    LOGGER.info("Hydra config composed")
    LOGGER.debug("Hydra config:\n%s", OmegaConf.to_yaml(cfg))

    try:
        config_obj = _build_native_config(cfg)
        system_model = create_system_model(config_obj)
        if system_model is None:
            raise RuntimeError("Native system_model creation returned None")

        data_factory = hydra.utils.instantiate(cfg.data, cfg_obj=config_obj)
        model_factory = hydra.utils.instantiate(cfg.model, cfg_obj=config_obj)
        trainer_factory = hydra.utils.instantiate(cfg.trainer, cfg_obj=config_obj)

        trajectory_handler = data_factory.build(system_model=system_model) if data_factory else None
        model = model_factory.build(system_model=system_model) if model_factory else None
        trainer = trainer_factory.build(model=model) if trainer_factory else None
        if model is None:
            raise RuntimeError("Native model creation returned None")

        components = {"system_model": system_model, "model": model}
        if trajectory_handler is not None:
            components["trajectory_handler"] = trajectory_handler
        if trainer is not None:
            components["trainer"] = trainer
    except Exception as native_exc:
        LOGGER.warning("Native Hydra instantiation failed, falling back to legacy bridge: %s", native_exc)
        legacy_config_path = cfg.get("legacy_config", "configs/default_config.yaml")
        legacy_config_abs = hydra.utils.to_absolute_path(str(legacy_config_path))
        config_obj = load_config(legacy_config_abs)

        overrides = _build_legacy_overrides(cfg)
        if overrides:
            LOGGER.info("Applying %d Hydra-derived overrides to legacy config", len(overrides))
            config_obj = apply_overrides(config_obj, overrides)

        components = create_components_from_config(config_obj)
        if "error" in components:
            raise RuntimeError(f"Failed to create components: {components['error']}")

    output_dir = Path.cwd()
    simulation = Simulation(config_obj, components, output_dir=output_dir)

    runtime_cfg = cfg.get("runtime")
    if runtime_cfg is not None:
        runner = hydra.utils.instantiate(runtime_cfg, simulation=simulation)
        result = runner.run()
    else:
        scenario = str(cfg.get("scenario", "training")).lower()
        if scenario == "training":
            result = simulation.run_training()
        elif scenario == "evaluation":
            result = simulation.run_evaluation()
        elif scenario == "online_learning":
            result = simulation.execute_online_learning()
        elif scenario == "full":
            result = simulation.run()
        else:
            raise ValueError(
                f"Unsupported scenario '{scenario}'. Supported: training, evaluation, online_learning, full."
            )

    LOGGER.info("Hydra run finished: %s", result.get("status", "unknown"))
