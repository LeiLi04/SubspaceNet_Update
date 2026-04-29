"""Unit tests for the trigger-validation aggregator."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.aggregate_trigger_results import CellMetrics, aggregate_cell, write_summary_table


def _make_summary(tmp_path: Path, first_online: list[int | None], drift_onset: int = 5) -> Path:
    payload = {
        "first_online_windows": first_online,
        "drift_onset_window": drift_onset,
        "trajectory_count": len(first_online),
        "tail5_rmspe_improvement_avg": 0.05,
    }
    path = tmp_path / "online_learning_results.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def test_aggregate_no_drift_zero_false_alarms(tmp_path: Path) -> None:
    summary = _make_summary(tmp_path, first_online=[None] * 20)
    metrics = aggregate_cell(summary, eta=0.0, trigger="whitened_cusum")
    assert metrics.false_alarm_rate == 0.0
    assert metrics.detect_rate is None
    assert metrics.n_trajectories == 20


def test_aggregate_no_drift_counts_late_triggers_as_false_alarms(tmp_path: Path) -> None:
    summary = _make_summary(tmp_path, first_online=[None, 13, None, 6])
    metrics = aggregate_cell(summary, eta=0.0, trigger="whitened_cusum")
    assert metrics.false_alarm_rate == pytest.approx(2 / 4)
    assert metrics.detect_rate is None
    assert metrics.mean_detection_delay is None


def test_aggregate_strong_drift_full_detection(tmp_path: Path) -> None:
    first_online = [6, 7, 6, 8, 9, 6, 7, 8, 6, 7, 9, 8, 6, 7, 10, 6, 7, 8, None, None]
    summary = _make_summary(tmp_path, first_online=first_online)
    metrics = aggregate_cell(summary, eta=1.0, trigger="whitened_cusum")
    assert metrics.detect_rate == pytest.approx(18 / 20)
    assert metrics.false_alarm_rate == 0.0
    expected_delay = sum(window - 5 for window in first_online if window is not None and window >= 5) / 18
    assert metrics.mean_detection_delay == pytest.approx(expected_delay)


def test_aggregate_pre_drift_false_alarms(tmp_path: Path) -> None:
    first_online = [2, 3, None, 6, None, None]
    summary = _make_summary(tmp_path, first_online=first_online)
    metrics = aggregate_cell(summary, eta=0.6, trigger="time_to_learn")
    assert metrics.false_alarm_rate == pytest.approx(2 / 6)
    assert metrics.detect_rate == pytest.approx(1 / 6)


def test_write_summary_table(tmp_path: Path) -> None:
    cells = [
        CellMetrics(
            trigger="time_to_learn",
            eta=0.0,
            n_trajectories=20,
            false_alarm_rate=0.0,
            detect_rate=None,
            mean_detection_delay=None,
            tail5_improve=None,
        ),
        CellMetrics(
            trigger="whitened_cusum",
            eta=1.0,
            n_trajectories=20,
            false_alarm_rate=0.0,
            detect_rate=0.95,
            mean_detection_delay=2.1,
            tail5_improve=0.12,
        ),
    ]
    csv_path = tmp_path / "summary.csv"
    md_path = tmp_path / "summary.md"
    write_summary_table(cells, csv_path, md_path)

    csv_text = csv_path.read_text(encoding="utf-8")
    header = csv_text.splitlines()[0]
    assert "trigger" in header and "eta" in header and "n_trajectories" in header
    assert "whitened_cusum,1.0,20" in csv_text

    md_text = md_path.read_text(encoding="utf-8")
    assert "Trigger" in md_text and "False Alarm" in md_text
