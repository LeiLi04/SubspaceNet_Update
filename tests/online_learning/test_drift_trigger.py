import math
from typing import Optional

import numpy as np
import pytest
from scipy.stats import chi2

from src.trainer_module.online_learning_parts.drift_trigger import (
    DriftTrigger,
    PageCusum,
    SigmaYSqTrigger,
    TimeToLearnTrigger,
    WhitenedCusumTrigger,
    build_drift_trigger,
    compute_chi2_threshold,
    compute_cusum_threshold,
)


def test_chi2_threshold_matches_scipy_inverse_cdf():
    p_fa = 0.05
    dof = 3
    tau = compute_chi2_threshold(p_fa=p_fa, dof=dof)
    expected = chi2.ppf(1 - p_fa, df=dof)
    assert math.isclose(tau, expected, rel_tol=1e-9)


def test_chi2_threshold_rejects_invalid_pfa():
    with pytest.raises(ValueError):
        compute_chi2_threshold(p_fa=0.0, dof=3)
    with pytest.raises(ValueError):
        compute_chi2_threshold(p_fa=1.0, dof=3)


def test_chi2_threshold_rejects_invalid_dof():
    with pytest.raises(ValueError):
        compute_chi2_threshold(p_fa=0.05, dof=0)


def test_cusum_threshold_satisfies_arl_relation():
    p_fa = 0.01
    h = compute_cusum_threshold(p_fa=p_fa, dof=3, b_offset=1.0)
    residual = h * math.exp(-h) - p_fa
    assert abs(residual) < 1e-6


def test_cusum_threshold_decreases_with_higher_pfa():
    h_strict = compute_cusum_threshold(p_fa=0.001, dof=3, b_offset=1.0)
    h_loose = compute_cusum_threshold(p_fa=0.10, dof=3, b_offset=1.0)
    assert h_strict > h_loose


def test_page_cusum_stays_zero_under_null():
    rng = np.random.default_rng(seed=42)
    cusum = PageCusum(reference_value=4.0, threshold=8.0)
    triggered_count = 0
    for _ in range(1000):
        if cusum.update(float(rng.chisquare(df=3))):
            triggered_count += 1
            cusum.reset()
    assert triggered_count < 25


def test_page_cusum_triggers_under_drift():
    rng = np.random.default_rng(seed=7)
    cusum = PageCusum(reference_value=4.0, threshold=8.0)
    triggered_at: Optional[int] = None
    for i in range(200):
        if cusum.update(float(rng.noncentral_chisquare(df=3, nonc=15.0))):
            triggered_at = i
            break
    assert triggered_at is not None
    assert triggered_at < 50


def test_page_cusum_reset_clears_state():
    cusum = PageCusum(reference_value=4.0, threshold=8.0)
    for c in [10.0, 10.0, 10.0]:
        cusum.update(c)
    assert cusum.statistic > 0
    cusum.reset()
    assert cusum.statistic == 0.0


def test_page_cusum_never_negative():
    cusum = PageCusum(reference_value=10.0, threshold=8.0)
    for c in [1.0, 1.0, 1.0]:
        cusum.update(c)
    assert cusum.statistic == 0.0


def test_time_to_learn_trigger_fires_at_target_window():
    trig = TimeToLearnTrigger(target_window=5)
    assert isinstance(trig, DriftTrigger)
    for w in range(10):
        triggered = trig.observe_window(window_idx=w, c_per_step=[3.0, 3.0, 3.0])
        if w == 5:
            assert triggered
        else:
            assert not triggered


def test_sigma_y_sq_trigger_fires_above_tau():
    trig = SigmaYSqTrigger(tau_sigma=2.0, window_size=5)
    for w in range(5):
        assert not trig.observe_window(window_idx=w, c_per_step=[0.5] * 10)
    assert trig.observe_window(window_idx=5, c_per_step=[10.0] * 10)


def test_whitened_cusum_trigger_fires_under_drift():
    trig = WhitenedCusumTrigger(p_fa=0.001, dof=3, b_offset=1.0, reset_after_trigger=True)
    rng = np.random.default_rng(seed=11)
    fired_window: Optional[int] = None

    for w in range(5):
        c_per_step = [float(rng.chisquare(df=3)) for _ in range(10)]
        if trig.observe_window(window_idx=w, c_per_step=c_per_step):
            fired_window = w
            break
    assert fired_window is None

    for w in range(5, 25):
        c_per_step = [float(rng.noncentral_chisquare(df=3, nonc=20.0)) for _ in range(10)]
        if trig.observe_window(window_idx=w, c_per_step=c_per_step):
            fired_window = w
            break
    assert fired_window is not None and fired_window < 15


def test_build_drift_trigger_dispatch():
    cfg_time = {"type": "time_to_learn", "target_window": 7}
    cfg_sigma = {"type": "sigma_y_sq", "tau_sigma": 1.5, "window_size": 5}
    cfg_cusum = {
        "type": "whitened_cusum",
        "p_fa": 0.01,
        "dof": 3,
        "b_offset": 1.0,
        "reset_after_trigger": True,
    }
    assert isinstance(build_drift_trigger(cfg_time), TimeToLearnTrigger)
    assert isinstance(build_drift_trigger(cfg_sigma), SigmaYSqTrigger)
    assert isinstance(build_drift_trigger(cfg_cusum), WhitenedCusumTrigger)


def test_build_drift_trigger_unknown_raises():
    with pytest.raises(ValueError, match="Unknown drift trigger type"):
        build_drift_trigger({"type": "nonexistent"})
