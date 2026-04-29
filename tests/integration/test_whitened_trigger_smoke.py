from pathlib import Path
from types import SimpleNamespace

import pytest
import torch

pytestmark = pytest.mark.integration


def test_whitened_cusum_config_builds_trigger():
    pytest.importorskip("hydra")
    pytest.importorskip("omegaconf")
    from hydra import compose, initialize_config_dir

    from src.trainer_module.online_learning_parts.pipeline_run import _make_drift_trigger

    config_dir = str((Path.cwd() / "run" / "conf" / "Used_for_paper").resolve())
    with initialize_config_dir(version_base=None, config_dir=config_dir):
        cfg = compose(config_name="SineAccel_whitened_cusum_trigger")

    trigger = _make_drift_trigger(cfg.online_learning)
    state = trigger.state
    assert state["type"] == "whitened_cusum"
    assert state["n_updates"] == 0


def test_pipeline_extracts_c_per_step_from_window_result():
    from src.trainer_module.online_learning_parts.pipeline_run import (
        _extract_c_per_step,
        _extract_c_per_step_per_source,
        _tensor_to_float_rows,
    )

    window_result = SimpleNamespace(
        step_metrics=SimpleNamespace(
            y_s_inv_y=torch.tensor([[1.0, 2.0, 3.0], [0.5, 0.5, 0.5]])
        )
    )

    assert _extract_c_per_step(window_result) == [6.0, 1.5]
    assert _extract_c_per_step_per_source(window_result) == [[1.0, 2.0, 3.0], [0.5, 0.5, 0.5]]
    assert _tensor_to_float_rows(window_result.step_metrics.y_s_inv_y) == [[1.0, 2.0, 3.0], [0.5, 0.5, 0.5]]


def test_pipeline_observe_feeds_c_per_step_to_trigger():
    from src.trainer_module.online_learning_parts.pipeline_run import _observe_drift_trigger

    class RecordingTrigger:
        def __init__(self):
            self.observed = None

        def observe_window(self, window_idx, c_per_step):
            self.observed = (window_idx, list(c_per_step))
            return True

    trigger = RecordingTrigger()
    pipeline = SimpleNamespace(_drift_trigger=trigger)
    window_result = SimpleNamespace(
        step_metrics=SimpleNamespace(
            y_s_inv_y=torch.tensor([[1.0, 2.0, 3.0], [0.5, 0.5, 0.5]])
        )
    )

    triggered, c_per_step = _observe_drift_trigger(pipeline, window_idx=9, window_result=window_result)

    assert triggered is True
    assert c_per_step == [6.0, 1.5]
    assert trigger.observed == (9, [6.0, 1.5])
