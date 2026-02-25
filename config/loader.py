"""Configuration loader for SubspaceNet.

This module provides functions for loading, validating, and managing configurations.
Hydra runtime paths should instantiate directly from composed configs.
This loader remains for legacy CLI/config-file workflows.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Mapping, Union

import yaml

from .schema import Config

try:
    from omegaconf import DictConfig, OmegaConf
except Exception:  # pragma: no cover
    DictConfig = None
    OmegaConf = None


def _to_plain_dict(config: Union[Config, Dict[str, Any], Any]) -> Dict[str, Any]:
    """Convert config payload to a mutable plain dictionary."""
    if hasattr(config, "dict"):
        return config.dict()
    if DictConfig is not None and isinstance(config, DictConfig):
        container = OmegaConf.to_container(config, resolve=True)
        if not isinstance(container, dict):
            raise TypeError(f"Expected DictConfig mapping, got {type(container)}")
        return container
    if isinstance(config, Mapping):
        return dict(config)
    raise TypeError(f"Unsupported config type for overrides: {type(config)}")


def _restore_config_type(original: Any, payload: Dict[str, Any]) -> Any:
    """Restore payload to the same config family as the original input."""
    if hasattr(original, "dict"):
        return Config(**payload)
    if DictConfig is not None and isinstance(original, DictConfig):
        return OmegaConf.create(payload)
    if isinstance(original, Mapping):
        return payload
    return Config(**payload)


def load_config(config_file_path: str) -> Config:
    """Load configuration from YAML and validate with pydantic schema."""
    config_path = Path(config_file_path)
    if not config_path.exists():
        config_path = Path(__file__).parent.parent / "run" / "conf" / "default_config.yaml"

    with open(config_path, "r", encoding="utf-8") as f:
        config_dict = yaml.safe_load(f)

    return Config(**config_dict)


def save_config(config: Union[Config, Dict[str, Any], Any], output_path: str) -> None:
    """Save a configuration object to YAML."""
    config_dict = _to_plain_dict(config)
    with open(output_path, "w", encoding="utf-8") as f:
        yaml.dump(config_dict, f, default_flow_style=False)


def apply_overrides(config: Union[Config, Dict[str, Any], Any], overrides: List[str]) -> Any:
    """Apply command-line style overrides like `section.key=value`."""
    config_dict = _to_plain_dict(config)

    for override in overrides:
        key, value = override.split("=", 1)
        keys = key.split(".")

        current = config_dict
        for section_key in keys[:-1]:
            if section_key not in current:
                raise ValueError(f"Invalid configuration key: {key}")
            current = current[section_key]

        final_key = keys[-1]
        if final_key not in current:
            raise ValueError(f"Invalid configuration key: {key}")

        current_value = current[final_key]

        if key == "model.params.regularization":
            valid_values = [None, "aic", "mdl", "threshold", "null", "none"]
            if value.lower() not in [str(v).lower() for v in valid_values]:
                raise ValueError(
                    f"Invalid value for regularization: {value}. Must be one of {valid_values}"
                )
            current[final_key] = "null" if value.lower() in ["null", "none"] else value.lower()
            continue

        if current_value is None:
            if value.lower() in ["null", "none"]:
                current[final_key] = None
            else:
                current[final_key] = value
        elif isinstance(current_value, bool):
            current[final_key] = value.lower() == "true"
        elif isinstance(current_value, int):
            try:
                current[final_key] = int(value)
            except ValueError:
                try:
                    current[final_key] = int(float(value))
                except ValueError as exc:
                    raise ValueError(f"Cannot convert '{value}' to int for key '{key}'") from exc
        elif isinstance(current_value, float):
            current[final_key] = float(value)
        elif isinstance(current_value, list):
            if value.lower() in ["null", "none"]:
                current[final_key] = None
            else:
                current[final_key] = [item.strip() for item in value.split(",")]
        else:
            current[final_key] = value

    return _restore_config_type(config, config_dict)
