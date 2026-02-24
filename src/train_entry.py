"""Hydra-based training entrypoint with direct `_target_` instantiation."""

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

from config.factory import create_system_model
from config.schema import Config
from src.trainer_module.core import Simulation

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
    cfg_dict = OmegaConf.to_container(cfg, resolve=False)
    if not isinstance(cfg_dict, dict):
        return Config()

    payload: Dict[str, Any] = {}
    for section in _CANONICAL_SECTIONS:
        section_data = cfg_dict.get(section)
        if isinstance(section_data, dict):
            if section == "model":
                model_map = _strip_private_keys(section_data)
                target = str(section_data.get("_target_", "")).lower()
                model_type = model_map.get("type")
                if model_type is None:
                    model_type = "DCD-MUSIC" if "dcd_music_lightning" in target else "SubspaceNet"

                model_params = {
                    "diff_method": model_map.get("diff_method"),
                    "train_loss_type": model_map.get("train_loss_type"),
                    "tau": model_map.get("tau"),
                    "field_type": model_map.get("field_type"),
                    "regularization": model_map.get("regularization"),
                    "variant": model_map.get("variant"),
                    "norm_layer": model_map.get("norm_layer"),
                    "batch_norm": model_map.get("batch_norm"),
                }
                if isinstance(model_map.get("params"), dict):
                    model_params.update(model_map["params"])
                if isinstance(model_params.get("diff_method"), list):
                    model_params["diff_method"] = tuple(model_params["diff_method"])
                if isinstance(model_params.get("train_loss_type"), list):
                    model_params["train_loss_type"] = tuple(model_params["train_loss_type"])
                payload[section] = {
                    "type": model_type,
                    "params": {k: v for k, v in model_params.items() if v is not None},
                }
            else:
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
                training_payload.setdefault(target_key, trainer_cfg[source_key])

    return Config(**payload)


@hydra.main(
    version_base=None,
    config_path=str((Path(__file__).resolve().parents[1] / "configs")),
    config_name="config",
)
def main(cfg: DictConfig) -> None:
    """Run SubspaceNet using direct Hydra `_target_` components."""
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    LOGGER.info("Hydra config composed")
    LOGGER.debug("Hydra config:\n%s", OmegaConf.to_yaml(cfg))

    config_obj = _build_native_config(cfg)
    system_model = create_system_model(config_obj)
    if system_model is None:
        raise RuntimeError("System model creation returned None")

    datamodule = hydra.utils.instantiate(cfg.data, config_obj, system_model=system_model)
    lightning_model = hydra.utils.instantiate(cfg.model, system_model=system_model)
    trainer = hydra.utils.instantiate(cfg.trainer)

    model = getattr(lightning_model, "model", lightning_model)
    components = {
        "system_model": system_model,
        "model": model,
        "lightning_model": lightning_model,
        "datamodule": datamodule,
        "trainer": trainer,
    }

    simulation = Simulation(config_obj, components, output_dir=Path.cwd())

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
