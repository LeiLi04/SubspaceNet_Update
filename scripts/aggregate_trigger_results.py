"""Aggregate trigger-validation summaries into CSV and Markdown tables."""

from __future__ import annotations

import argparse
import csv
import json
import logging
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Optional


LOGGER = logging.getLogger(__name__)


@dataclass
class CellMetrics:
    trigger: str
    eta: float
    n_trajectories: int
    false_alarm_rate: float
    detect_rate: Optional[float]
    mean_detection_delay: Optional[float]
    tail5_improve: Optional[float]


def aggregate_cell(summary_path: Path, eta: float, trigger: str) -> CellMetrics:
    payload = json.loads(summary_path.read_text(encoding="utf-8"))
    first_online = payload["first_online_windows"]
    drift_onset = int(payload.get("drift_onset_window", 5))
    n = int(payload.get("trajectory_count", len(first_online)))

    pre_drift = sum(1 for window in first_online if window is not None and window < drift_onset)
    detected = sum(1 for window in first_online if window is not None and window >= drift_onset)
    false_alarms = sum(1 for window in first_online if window is not None) if eta == 0.0 else pre_drift
    delays = [window - drift_onset for window in first_online if window is not None and window >= drift_onset]

    if n <= 0:
        false_alarm_rate = 0.0
        detect_rate: Optional[float] = None if eta == 0.0 else 0.0
    else:
        false_alarm_rate = false_alarms / n
        detect_rate = None if eta == 0.0 else detected / n

    return CellMetrics(
        trigger=trigger,
        eta=eta,
        n_trajectories=n,
        false_alarm_rate=false_alarm_rate,
        detect_rate=detect_rate,
        mean_detection_delay=(sum(delays) / len(delays)) if delays and eta != 0.0 else None,
        tail5_improve=payload.get("tail5_rmspe_improvement_avg"),
    )


def discover_cells(root: Path) -> list[tuple[Path, float, str]]:
    cells: list[tuple[Path, float, str]] = []
    for trigger_dir in sorted(root.iterdir()):
        if not trigger_dir.is_dir():
            continue
        for eta_dir in sorted(trigger_dir.iterdir()):
            if not eta_dir.is_dir() or not eta_dir.name.startswith("eta_"):
                continue
            summary = eta_dir / "online_learning_results.json"
            if not summary.exists():
                summary = eta_dir / "summary.json"
            if not summary.exists():
                continue
            eta = float(eta_dir.name.removeprefix("eta_").replace("p", "."))
            cells.append((summary, eta, trigger_dir.name))
    return cells


def write_summary_table(cells: list[CellMetrics], csv_path: Path, md_path: Path) -> None:
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "trigger",
        "eta",
        "n_trajectories",
        "false_alarm_rate",
        "detect_rate",
        "mean_detection_delay",
        "tail5_improve",
    ]

    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for cell in cells:
            writer.writerow(asdict(cell))

    def fmt(value: float | None, digits: int = 3) -> str:
        return "-" if value is None else f"{value:.{digits}f}"

    lines = [
        "| Trigger | eta | N | False Alarm | Detect | Mean Delay (w) | Tail5 Improve |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for cell in cells:
        lines.append(
            f"| {cell.trigger} | {cell.eta:.2f} | {cell.n_trajectories} | "
            f"{cell.false_alarm_rate:.3f} | {fmt(cell.detect_rate)} | "
            f"{fmt(cell.mean_detection_delay, 2)} | {fmt(cell.tail5_improve, 4)} |"
        )
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--csv", type=Path, required=True)
    parser.add_argument("--md", type=Path, required=True)
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(message)s")
    cells = [aggregate_cell(path, eta, trigger) for path, eta, trigger in discover_cells(args.root)]
    if not cells:
        LOGGER.error("No trigger-validation summaries found under %s", args.root)
        return 1
    write_summary_table(cells, args.csv, args.md)
    LOGGER.info("Wrote %s and %s with %d cells", args.csv, args.md, len(cells))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
