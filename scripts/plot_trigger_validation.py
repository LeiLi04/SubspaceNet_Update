"""Plot trigger-validation detection, false-alarm, and delay metrics."""

from __future__ import annotations

import argparse
import csv
import logging
import os
from collections import defaultdict
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib")

import matplotlib.pyplot as plt


LOGGER = logging.getLogger(__name__)


def load_rows(csv_path: Path) -> list[dict[str, str]]:
    with csv_path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _optional_float(value: str) -> float | None:
    if value in {"", "None", "none", "null", "-"}:
        return None
    return float(value)


def plot_detect_rate(rows: list[dict[str, str]], out_path: Path) -> None:
    by_trigger: dict[str, list[tuple[float, float]]] = defaultdict(list)
    for row in rows:
        eta = float(row["eta"])
        rate = _optional_float(row["detect_rate"])
        if eta == 0.0 or rate is None:
            continue
        by_trigger[row["trigger"]].append((eta, rate))

    fig, ax = plt.subplots(figsize=(6.0, 3.8))
    for trigger, points in sorted(by_trigger.items()):
        points.sort()
        xs, ys = zip(*points)
        ax.plot(xs, ys, marker="o", linewidth=2, label=trigger)
    ax.set_xlabel(r"drift magnitude $\eta$")
    ax.set_ylabel("detection rate")
    ax.set_ylim(0, 1.05)
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=220)
    plt.close(fig)
    LOGGER.info("Wrote %s", out_path)


def plot_false_alarm(rows: list[dict[str, str]], out_path: Path) -> None:
    triggers = sorted({row["trigger"] for row in rows})
    rates: list[float] = []
    for trigger in triggers:
        match = [row for row in rows if row["trigger"] == trigger and float(row["eta"]) == 0.0]
        rates.append(float(match[0]["false_alarm_rate"]) if match else 0.0)

    fig, ax = plt.subplots(figsize=(5.8, 3.4))
    ax.bar(triggers, rates, color=["#4c78a8", "#f58518", "#54a24b"][: len(triggers)])
    ax.axhline(0.05, color="#c44e52", linestyle="--", linewidth=1.5, label="5% target")
    ax.set_ylabel("no-drift false alarm rate")
    ax.set_ylim(0, max(rates + [0.05]) * 1.35 + 0.01)
    ax.tick_params(axis="x", rotation=15)
    ax.legend()
    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=220)
    plt.close(fig)
    LOGGER.info("Wrote %s", out_path)


def plot_delay(rows: list[dict[str, str]], out_path: Path) -> None:
    by_trigger: dict[str, list[tuple[float, float]]] = defaultdict(list)
    for row in rows:
        eta = float(row["eta"])
        delay = _optional_float(row["mean_detection_delay"])
        if eta == 0.0 or delay is None:
            continue
        by_trigger[row["trigger"]].append((eta, delay))

    fig, ax = plt.subplots(figsize=(6.0, 3.8))
    for trigger, points in sorted(by_trigger.items()):
        points.sort()
        xs, ys = zip(*points)
        ax.plot(xs, ys, marker="s", linewidth=2, label=trigger)
    ax.set_xlabel(r"drift magnitude $\eta$")
    ax.set_ylabel("mean detection delay (windows)")
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=220)
    plt.close(fig)
    LOGGER.info("Wrote %s", out_path)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(message)s")
    rows = load_rows(args.csv)
    plot_detect_rate(rows, args.out_dir / "detect_rate_vs_eta.png")
    plot_false_alarm(rows, args.out_dir / "false_alarm_no_drift.png")
    plot_delay(rows, args.out_dir / "delay_vs_eta.png")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
