"""Run trigger-validation cells with the current direct Simulation path.

Usage:
    python scripts/run_trigger_validation.py --dry-run --n-traj 5
    python scripts/run_trigger_validation.py --n-traj 20
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import random
from pathlib import Path
from typing import Any

os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib")

import numpy as np
import torch
from hydra import compose, initialize_config_dir
from omegaconf import OmegaConf

from config.schema import Config
from config.utils import create_system_model
from DCD_MUSIC.src.models_pack.subspacenet import SubspaceNet
from src.trainer_module.online_learning import OnlineLearning
from src.trainer_module.simulation.runner import DEVICE, Simulation


logging.basicConfig(level=logging.WARNING, format="%(asctime)s [%(levelname)s] %(message)s")
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)

ROOT = Path(__file__).resolve().parents[1]
CONFIG_DIR = ROOT / "run" / "conf" / "Used_for_paper"
OUTPUT_ROOT = ROOT / "outputs" / "trigger_validation_20260429"
CHECKPOINT = "checkpoints/saved_SubspaceNet_trained_20260224_180720.pt"

# Confirmed on 2026-04-29 with:
#     rg -n "@hydra\.main|hydra\.main" . -g "*.py"
# The Used_for_paper configs are legacy-shaped, so this validation script uses
# direct Simulation execution while keeping the true Hydra entry documented.
PIPELINE_ENTRY = "run.pipeline.training.train"
EXECUTION_MODE = "direct_simulation"

TRIGGERS: dict[str, dict[str, Any]] = {
    "time_to_learn": {
        "config_name": "SineAccel_base_model_Online_learning_snr_sweep_config",
        "overrides": [
            "online_learning.drift_trigger.type=time_to_learn",
            "online_learning.drift_trigger.target_window=6",
            "online_learning.time_to_learn=6",
        ],
    },
    "sigma_y_sq": {
        "config_name": "SineAccel_sigma_y_sq_trigger_retuned",
        "overrides": [],
    },
    "whitened_cusum": {
        "config_name": "SineAccel_whitened_cusum_pretrained_calibrated",
        "overrides": [],
    },
}

ETAS = [0.0, 0.3, 0.6, 1.0]
DRIFT_ONSET_WINDOW = 5


def _configure_runtime_noise() -> None:
    """Keep long validation runs readable while preserving our progress logs."""
    logging.getLogger().setLevel(logging.WARNING)
    for name in (
        "src",
        "DCD_MUSIC",
        "simulation",
        "SubspaceNet",
        "matplotlib",
        "torch",
    ):
        logging.getLogger(name).setLevel(logging.ERROR)

    try:
        import src.trainer_module.online_learning_parts.pipeline_run as pipeline_run

        pipeline_run.tqdm = lambda iterable, *args, **kwargs: iterable
    except Exception:
        LOGGER.debug("Could not disable tqdm progress bars", exc_info=True)


def _eta_dirname(eta: float) -> str:
    return f"eta_{eta:.2f}".replace(".", "p")


def _seed_for(trigger: str, eta: float, trajectory_idx: int) -> int:
    trigger_offset = sum(ord(ch) for ch in trigger)
    return 29042026 + trigger_offset + int(round(eta * 1000)) + trajectory_idx


def _set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def _compose_config(trigger: str, eta: float, n_traj: int) -> Config:
    if trigger not in TRIGGERS:
        raise ValueError(f"Unknown trigger '{trigger}'. Valid: {sorted(TRIGGERS)}")

    trigger_cfg = TRIGGERS[trigger]
    common_overrides = [
        f"online_learning.dataset_size={n_traj}",
        "online_learning.trajectory_length=100",
        "online_learning.window_size=5",
        "online_learning.stride=5",
        "online_learning.eta_update_interval_windows=5",
        f"online_learning.eta_increment={eta}",
        f"online_learning.max_eta={eta}",
        "online_learning.min_eta=0.0",
        "online_learning.max_iterations=1",
        "kalman_filter.measurement_noise_std_dev=0.125",
        "simulation.load_model=true",
        "simulation.train_model=false",
        "simulation.evaluate_model=false",
        "simulation.save_model=false",
        "simulation.plot_results=false",
        "simulation.save_plots=false",
        f"simulation.model_path={CHECKPOINT}",
        "logging.level=WARNING",
        "logging.kalman_filter_level=WARNING",
        "logging.torch_level=WARNING",
        "logging.matplotlib_level=WARNING",
    ]

    with initialize_config_dir(config_dir=str(CONFIG_DIR), version_base=None):
        cfg = compose(
            config_name=trigger_cfg["config_name"],
            overrides=common_overrides + trigger_cfg["overrides"],
        )
    return Config(**OmegaConf.to_container(cfg, resolve=True))


def _build_simulation(config: Config, output_dir: Path) -> Simulation:
    system_model = create_system_model(config)
    model = SubspaceNet(
        tau=config.model.params.tau,
        diff_method=config.model.params.diff_method,
        system_model=system_model,
        field_type=config.model.params.field_type,
    )
    simulation = Simulation(
        config,
        {"system_model": system_model, "model": model},
        output_dir=output_dir,
    )
    ok, message = simulation.training_pipeline._load_and_apply_weights(Path(CHECKPOINT), DEVICE)
    if not ok:
        raise RuntimeError(message)
    return simulation


def _first_update_window(window_updates: list[Any]) -> int | None:
    for idx, value in enumerate(window_updates):
        if bool(value):
            return idx
    return None


def _losses_by_window(trajectory: Any) -> dict[int, float]:
    if trajectory is None:
        return {}
    out: dict[int, float] = {}
    for idx, result in zip(trajectory.window_indices, trajectory.window_results):
        if getattr(result, "is_valid", False):
            out[int(idx)] = float(result.loss_metrics.main_loss)
    return out


def _tail5_rmspe_improvement(result: dict[str, Any]) -> float | None:
    ol = result.get("online_learning_results", {})
    pretrained = _losses_by_window(ol.get("pretrained_model_trajectory_results"))
    online = _losses_by_window(ol.get("online_model_trajectory_results"))
    common = sorted(set(pretrained) & set(online))
    if not common:
        return None
    tail = common[-5:]
    return float(np.mean([pretrained[idx] - online[idx] for idx in tail]))


def _read_c_values(dump_paths: list[Path]) -> np.ndarray:
    chunks: list[np.ndarray] = []
    for path in dump_paths:
        if not path.exists():
            continue
        payload = np.load(path)
        if "c" in payload:
            chunks.append(np.asarray(payload["c"], dtype=np.float64).reshape(-1))
    if not chunks:
        return np.asarray([], dtype=np.float64)
    return np.concatenate(chunks)


def _summarize_cell(
    *,
    trigger: str,
    eta: float,
    n_traj: int,
    trajectory_results: list[dict[str, Any]],
    dump_paths: list[Path],
) -> dict[str, Any]:
    first_online_windows = [
        _first_update_window(result["online_learning_results"].get("window_updates", []))
        for result in trajectory_results
    ]
    detected_after_onset = [
        win for win in first_online_windows if win is not None and win >= DRIFT_ONSET_WINDOW
    ]
    pre_drift_false = [
        win for win in first_online_windows if win is not None and win < DRIFT_ONSET_WINDOW
    ]
    false_trigger_count = sum(win is not None for win in first_online_windows) if eta == 0 else len(pre_drift_false)
    delays = [win - DRIFT_ONSET_WINDOW for win in detected_after_onset]
    tail_improvements = [
        value
        for value in (_tail5_rmspe_improvement(result) for result in trajectory_results)
        if value is not None and np.isfinite(value)
    ]

    c_values = _read_c_values(dump_paths)
    c_stats: dict[str, float | None]
    if c_values.size:
        c_stats = {
            "c_mean": float(np.mean(c_values)),
            "c_p95": float(np.percentile(c_values, 95)),
            "c_p99": float(np.percentile(c_values, 99)),
            "c_max": float(np.max(c_values)),
        }
    else:
        c_stats = {"c_mean": None, "c_p95": None, "c_p99": None, "c_max": None}

    return {
        "status": "success",
        "execution_mode": EXECUTION_MODE,
        "pipeline_entry_confirmed": PIPELINE_ENTRY,
        "trigger": trigger,
        "eta": eta,
        "trajectory_count": n_traj,
        "drift_onset_window": DRIFT_ONSET_WINDOW,
        "first_online_windows": first_online_windows,
        "false_trigger_trajectory_count": false_trigger_count,
        "pre_drift_false_trajectory_count": len(pre_drift_false),
        "detected_after_onset_count": len(detected_after_onset),
        "detect_rate_by_first_online": len(detected_after_onset) / n_traj if n_traj else 0.0,
        "mean_detection_delay_windows": float(np.mean(delays)) if delays else None,
        "tail5_rmspe_improvement_avg": float(np.mean(tail_improvements)) if tail_improvements else None,
        **c_stats,
    }


def run_cell(trigger: str, eta: float, n_traj: int, output_root: Path) -> dict[str, Any]:
    out_dir = output_root / trigger / _eta_dirname(eta)
    out_dir.mkdir(parents=True, exist_ok=True)
    config = _compose_config(trigger, eta, n_traj)
    simulation = _build_simulation(config, out_dir)
    handler = OnlineLearning(
        config=config,
        system_model=simulation.system_model,
        trained_model=simulation.trained_model,
        output_dir=out_dir,
        results=simulation.results,
    )

    trajectory_results: list[dict[str, Any]] = []
    dump_paths: list[Path] = []
    for trajectory_idx in range(n_traj):
        seed = _seed_for(trigger, eta, trajectory_idx)
        _set_seed(seed)

        handler.system_model.params.eta = 0.0
        if hasattr(handler.system_model, "_SystemModel__set_eta"):
            handler.system_model.eta = handler.system_model._SystemModel__set_eta()
        elif hasattr(handler.system_model, "eta"):
            handler.system_model.eta = 0.0
        if (
            not getattr(handler.system_model.params, "nominal", True)
            and hasattr(handler.system_model, "get_distance_noise")
        ):
            handler.system_model.location_noise = handler.system_model.get_distance_noise(True)

        dump_path = out_dir / f"c_dump_traj_{trajectory_idx:03d}.npz"
        handler.config.online_learning.dump_c_per_step_path = str(dump_path)
        dump_paths.append(dump_path)

        LOGGER.info("[%s eta=%.2f] trajectory %d/%d", trigger, eta, trajectory_idx + 1, n_traj)
        result = handler._run_single_trajectory_online_learning(trajectory_idx)
        if result.get("status") != "success":
            raise RuntimeError(f"Trajectory {trajectory_idx} failed: {result}")
        trajectory_results.append(result)

    summary = _summarize_cell(
        trigger=trigger,
        eta=eta,
        n_traj=n_traj,
        trajectory_results=trajectory_results,
        dump_paths=dump_paths,
    )
    for filename in ("summary.json", "online_learning_results.json"):
        (out_dir / filename).write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    return summary


def _dry_run_rows(triggers: list[str], etas: list[float], n_traj: int, output_root: Path) -> list[str]:
    rows = []
    for trigger in triggers:
        for eta in etas:
            rows.append(
                f"trigger={trigger} eta={eta:.2f} n_traj={n_traj} "
                f"out={output_root / trigger / _eta_dirname(eta)} "
                f"entry={PIPELINE_ENTRY} mode={EXECUTION_MODE}"
            )
    return rows


def main() -> int:
    _configure_runtime_noise()

    parser = argparse.ArgumentParser()
    parser.add_argument("--n-traj", type=int, default=20)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--triggers", nargs="*", default=list(TRIGGERS))
    parser.add_argument("--etas", nargs="*", type=float, default=ETAS)
    parser.add_argument("--output-root", type=Path, default=OUTPUT_ROOT)
    args = parser.parse_args()

    if args.n_traj <= 0:
        raise ValueError("--n-traj must be positive")
    args.output_root.mkdir(parents=True, exist_ok=True)

    if args.dry_run:
        for row in _dry_run_rows(args.triggers, args.etas, args.n_traj, args.output_root):
            print(row)
        return 0

    summaries = []
    for trigger in args.triggers:
        for eta in args.etas:
            summaries.append(run_cell(trigger, eta, args.n_traj, args.output_root))

    rollup = {
        "status": "success",
        "pipeline_entry_confirmed": PIPELINE_ENTRY,
        "execution_mode": EXECUTION_MODE,
        "trajectory_count_per_cell": args.n_traj,
        "summaries": summaries,
    }
    (args.output_root / "summary.json").write_text(
        json.dumps(rollup, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    LOGGER.info("Completed %d validation cells", len(summaries))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
