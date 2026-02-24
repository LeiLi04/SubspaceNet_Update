"""Shared configuration utilities used by Hydra/native runtime paths."""

from __future__ import annotations

import importlib
import logging
from typing import Any

from config.schema import Config

logger = logging.getLogger("SubspaceNet.config.utils")


def import_from_dcd_music(module_path: str, class_name: str) -> Any:
    """Import a class/function from the vendored DCD_MUSIC package."""
    try:
        module = importlib.import_module(f"DCD_MUSIC.{module_path}")
        return getattr(module, class_name)
    except (ImportError, AttributeError) as exc:
        logger.error("Failed to import %s from DCD_MUSIC.%s: %s", class_name, module_path, exc)
        raise ImportError(f"Failed to import {class_name} from DCD_MUSIC.{module_path}") from exc


def create_system_model_params(config: Config) -> Any:
    """Build SystemModelParams from validated config object."""
    SystemModelParams = import_from_dcd_music("src.system_model", "SystemModelParams")
    system_model_params = SystemModelParams()

    config_dict = config.system_model.dict()
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


def create_system_model(config: Config) -> Any:
    """Instantiate DCD_MUSIC SystemModel from validated config object."""
    system_model_params = create_system_model_params(config)
    SystemModel = import_from_dcd_music("src.system_model", "SystemModel")

    try:
        return SystemModel(system_model_params, nominal=config.system_model.nominal)
    except TypeError:
        return SystemModel(system_model_params)
