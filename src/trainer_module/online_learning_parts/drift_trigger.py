"""Drift trigger strategies for unsupervised online adaptation."""
from __future__ import annotations

import logging
import math
from abc import ABC, abstractmethod
from collections import deque
from dataclasses import dataclass, field
from typing import Any, Deque, Mapping, Sequence

import numpy as np
from scipy.optimize import brentq
from scipy.stats import chi2

logger = logging.getLogger(__name__)


def compute_chi2_threshold(p_fa: float, dof: int) -> float:
    """Return tau where P(chi2(dof) > tau) = p_fa."""
    if not (0.0 < p_fa < 1.0):
        raise ValueError(f"p_fa must be in (0, 1), got {p_fa}")
    if dof <= 0:
        raise ValueError(f"dof must be positive, got {dof}")
    return float(chi2.ppf(1.0 - p_fa, df=dof))


def compute_cusum_threshold(p_fa: float, dof: int, b_offset: float) -> float:
    """Return Page-CUSUM threshold solving h * exp(-h) = p_fa."""
    if not (0.0 < p_fa < 0.5):
        raise ValueError(f"p_fa must be in (0, 0.5), got {p_fa}")
    if dof <= 0:
        raise ValueError(f"dof must be positive, got {dof}")
    if b_offset <= 0:
        raise ValueError(f"b_offset must be positive, got {b_offset}")
    if p_fa >= math.exp(-1.0):
        raise ValueError(f"p_fa={p_fa} is too large for the large-root ARL approximation")

    def residual(h: float) -> float:
        return h * math.exp(-h) - p_fa

    return float(brentq(residual, 1.0 + 1e-9, 50.0, xtol=1e-9))


@dataclass
class PageCusum:
    """Page-CUSUM accumulator: G_i = max(0, G_{i-1} + c_i - b)."""

    reference_value: float
    threshold: float
    statistic: float = field(default=0.0, init=False)
    n_updates: int = field(default=0, init=False)

    def __post_init__(self) -> None:
        if self.reference_value <= 0:
            raise ValueError(f"reference_value must be positive, got {self.reference_value}")
        if self.threshold <= 0:
            raise ValueError(f"threshold must be positive, got {self.threshold}")

    def update(self, c: float) -> bool:
        """Update the accumulator and return True when the threshold is crossed."""
        self.statistic = max(0.0, self.statistic + float(c) - self.reference_value)
        self.n_updates += 1
        return self.statistic > self.threshold

    def reset(self) -> None:
        """Reset the accumulated CUSUM statistic."""
        self.statistic = 0.0


class DriftTrigger(ABC):
    """Strategy interface for one-window drift decisions."""

    @abstractmethod
    def observe_window(self, window_idx: int, c_per_step: Sequence[float]) -> bool:
        """Return True iff drift is declared for this window."""

    @property
    @abstractmethod
    def state(self) -> Mapping[str, Any]:
        """Diagnostic state for logging and plots."""


class TimeToLearnTrigger(DriftTrigger):
    """Legacy one-shot trigger at a configured window index."""

    def __init__(self, target_window: int) -> None:
        if target_window < 0:
            raise ValueError(f"target_window must be >= 0, got {target_window}")
        self.target_window = target_window
        self._fired = False

    def observe_window(self, window_idx: int, c_per_step: Sequence[float]) -> bool:
        if window_idx == self.target_window and not self._fired:
            self._fired = True
            return True
        return False

    @property
    def state(self) -> Mapping[str, Any]:
        return {"type": "time_to_learn", "target": self.target_window, "fired": self._fired}


class SigmaYSqTrigger(DriftTrigger):
    """Sliding-window sigma_y^2 trigger used as an original-paper comparator."""

    def __init__(self, tau_sigma: float, window_size: int) -> None:
        if tau_sigma <= 0:
            raise ValueError(f"tau_sigma must be positive, got {tau_sigma}")
        if window_size <= 0:
            raise ValueError(f"window_size must be positive, got {window_size}")
        self.tau_sigma = tau_sigma
        self.window_size = window_size
        self._buf: Deque[float] = deque(maxlen=window_size)
        self._last_sigma2 = 0.0

    def observe_window(self, window_idx: int, c_per_step: Sequence[float]) -> bool:
        for c in c_per_step:
            self._buf.append(float(c))
        if len(self._buf) < self.window_size:
            return False
        self._last_sigma2 = float(np.mean(self._buf))
        return self._last_sigma2 > self.tau_sigma

    @property
    def state(self) -> Mapping[str, Any]:
        return {"type": "sigma_y_sq", "tau_sigma": self.tau_sigma, "sigma2": self._last_sigma2}


class WhitenedCusumTrigger(DriftTrigger):
    """Whitened-innovation Page-CUSUM trigger with analytical threshold."""

    def __init__(
        self,
        p_fa: float,
        dof: int,
        b_offset: float = 1.0,
        reset_after_trigger: bool = True,
    ) -> None:
        self.p_fa = p_fa
        self.dof = dof
        self.b_offset = b_offset
        self.reset_after_trigger = reset_after_trigger
        threshold = compute_cusum_threshold(p_fa=p_fa, dof=dof, b_offset=b_offset)
        reference_value = float(dof) + b_offset
        self._cusum = PageCusum(reference_value=reference_value, threshold=threshold)
        logger.info(
            "WhitenedCusumTrigger initialized: dof=%s, p_fa=%s, b=%.3f, h=%.3f",
            dof,
            p_fa,
            reference_value,
            threshold,
        )

    def observe_window(self, window_idx: int, c_per_step: Sequence[float]) -> bool:
        triggered = False
        for c in c_per_step:
            if self._cusum.update(float(c)):
                triggered = True
                break
        if triggered and self.reset_after_trigger:
            self._cusum.reset()
        return triggered

    @property
    def state(self) -> Mapping[str, Any]:
        return {
            "type": "whitened_cusum",
            "p_fa": self.p_fa,
            "dof": self.dof,
            "threshold": self._cusum.threshold,
            "reference": self._cusum.reference_value,
            "statistic": self._cusum.statistic,
            "n_updates": self._cusum.n_updates,
        }


def build_drift_trigger(cfg: Mapping[str, Any]) -> DriftTrigger:
    """Build a drift trigger from a config mapping."""
    trigger_type = cfg.get("type", "time_to_learn")
    if trigger_type == "time_to_learn":
        return TimeToLearnTrigger(target_window=int(cfg["target_window"]))
    if trigger_type == "sigma_y_sq":
        return SigmaYSqTrigger(
            tau_sigma=float(cfg["tau_sigma"]),
            window_size=int(cfg["window_size"]),
        )
    if trigger_type == "whitened_cusum":
        return WhitenedCusumTrigger(
            p_fa=float(cfg["p_fa"]),
            dof=int(cfg["dof"]),
            b_offset=float(cfg.get("b_offset", 1.0)),
            reset_after_trigger=bool(cfg.get("reset_after_trigger", True)),
        )
    raise ValueError(f"Unknown drift trigger type: {trigger_type}")
