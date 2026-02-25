"""Hydra training entrypoint using direct `_target_` instantiation."""
from __future__ import annotations

from pathlib import Path
import logging

import hydra
from omegaconf import DictConfig, OmegaConf

from config.utils import create_system_model

LOGGER = logging.getLogger("SubspaceNet.hydra")


def _ensure_runtime_sections(cfg: DictConfig) -> DictConfig:
    """Inject minimal runtime sections when config groups are not composed."""
    defaults = OmegaConf.create(
        {
            "evaluation": {},
            "trajectory": {
                "enabled": False,
                "trajectory_type": "random_walk",
                "trajectory_length": 30,
                "save_trajectory": False,
            },
            "kalman_filter": {
                "filter_type": "standard",
                "process_noise_std_dev": None,
                "measurement_noise_std_dev": 1.0e-3,
                "initial_covariance": 1.0,
            },
            "online_learning": {"enabled": False},
            "logging": {"level": "INFO"},
        }
    )
    return OmegaConf.merge(defaults, cfg)


@hydra.main(version_base=None, config_path="../../conf", config_name="config")
def main(cfg: DictConfig) -> None:
    cfg = _ensure_runtime_sections(cfg)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    LOGGER.info("Hydra config composed")
    LOGGER.debug("Hydra config:\n%s", OmegaConf.to_yaml(cfg))

    system_model = create_system_model(cfg)
    datamodule = hydra.utils.instantiate(cfg.data, cfg, system_model=system_model)
    lightning_model = hydra.utils.instantiate(cfg.model, system_model=system_model)
    trainer = hydra.utils.instantiate(cfg.trainer)

    from src.trainer_module.core import Simulation

    simulation = Simulation(
        cfg,
        {
            "system_model": system_model,
            "model": getattr(lightning_model, "model", lightning_model),
            "lightning_model": lightning_model,
            "datamodule": datamodule,
            "trainer": trainer,
        },
        output_dir=Path.cwd(),
    )

    runtime_cfg = cfg.get("runtime")
    if runtime_cfg is not None:
        result = hydra.utils.instantiate(runtime_cfg, simulation=simulation).run()
    else:
        scenario = str(cfg.get("scenario", "training")).lower()
        scenario_map = {
            "training": simulation.run_training,
            "evaluation": simulation.run_evaluation,
            "online_learning": simulation.execute_online_learning,
            "full": simulation.run,
        }
        if scenario not in scenario_map:
            raise ValueError(
                f"Unsupported scenario '{scenario}'. Supported: training, evaluation, online_learning, full."
            )
        result = scenario_map[scenario]()

    LOGGER.info("Hydra run finished: %s", result.get("status", "unknown"))


if __name__ == "__main__":
    main()
