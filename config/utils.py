"""Shared configuration utilities used by Hydra/native runtime paths."""

from __future__ import annotations

import importlib
import logging
from typing import Any, Mapping

try:
    from omegaconf import DictConfig, OmegaConf
except Exception:  # pragma: no cover
    DictConfig = None
    OmegaConf = None

logger = logging.getLogger("SubspaceNet.config.utils")


def import_from_dcd_music(module_path: str, class_name: str) -> Any:
    """Import a class/function from the vendored DCD_MUSIC package."""
    try:
        module = importlib.import_module(f"DCD_MUSIC.{module_path}")
        return getattr(module, class_name)
    except (ImportError, AttributeError) as exc:
        logger.error("Failed to import %s from DCD_MUSIC.%s: %s", class_name, module_path, exc)
        raise ImportError(f"Failed to import {class_name} from DCD_MUSIC.{module_path}") from exc


def _as_plain_dict(value: Any) -> dict[str, Any]:
    """Convert section payloads from pydantic/DictConfig/mapping into a plain dict."""
    if value is None:
        return {}
    if hasattr(value, "dict"):
        return value.dict()
    if DictConfig is not None and isinstance(value, DictConfig):
        container = OmegaConf.to_container(value, resolve=True)
        if not isinstance(container, dict):
            raise TypeError(f"Expected mapping section, got {type(container)}")
        return container
    if isinstance(value, Mapping):
        return dict(value)
    if hasattr(value, "items"):
        return {k: v for k, v in value.items()}
    raise TypeError(f"Unsupported section type: {type(value)}")


def _get_section(config: Any, section: str) -> Any:
    """Read a config section from object-like or mapping-like config containers."""
    if DictConfig is not None and isinstance(config, DictConfig):
        return config.get(section)
    if isinstance(config, Mapping):
        return config.get(section)
    return getattr(config, section, None)


def _get_field(section: Any, key: str, default: Any = None) -> Any:
    """Read a field from object-like or mapping-like section payloads."""
    if section is None:
        return default
    if DictConfig is not None and isinstance(section, DictConfig):
        return section.get(key, default)
    if isinstance(section, Mapping):
        return section.get(key, default)
    return getattr(section, key, default)


def create_system_model_params(config: Any) -> Any:
    """Build SystemModelParams from pydantic Config or Hydra DictConfig."""
    SystemModelParams = import_from_dcd_music("src.system_model", "SystemModelParams")
    system_model_params = SystemModelParams()

    system_model_cfg = _get_section(config, "system_model")
    if system_model_cfg is None:
        raise ValueError("Missing `system_model` section in configuration")

    config_dict = _as_plain_dict(system_model_cfg)
    if "wavelength" not in config_dict:
        config_dict["wavelength"] = 1.0

    for key, value in config_dict.items():
        if key == "field_type" and isinstance(value, str):
            lower = value.lower()
            if lower == "far":
                value = "Far"
            elif lower == "near":
                value = "Near"

        if key == "signal_type" and isinstance(value, str):
            lower = value.lower()
            if lower == "narrowband":
                value = "NarrowBand"
            elif lower == "broadband":
                value = "Broadband"

        system_model_params.set_parameter(key, value)

    return system_model_params


def create_system_model(config: Any) -> Any:
    """Instantiate DCD_MUSIC SystemModel from pydantic Config or Hydra DictConfig."""
    system_model_params = create_system_model_params(config)
    SystemModel = import_from_dcd_music("src.system_model", "SystemModel")

    nominal = bool(_get_field(_get_section(config, "system_model"), "nominal", False))
    try:
        return SystemModel(system_model_params, nominal=nominal)
    except TypeError:
        return SystemModel(system_model_params)
