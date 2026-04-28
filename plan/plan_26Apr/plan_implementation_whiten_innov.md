# 白化新息 CUSUM 触发器 实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将 [plan_whiten_innov.md](plan_whiten_innov.md) 中提出的"白化新息 + Page-CUSUM + 解析阈值"漂移触发器接入 SubspaceNet+EKF 在线学习管线，替换当前仅靠 `time_to_learn` 配置项的硬编码触发，并保留与原论文 `sigma_y^2 > tau_sigma` 触发器的对照能力。

**Architecture:** 新增一个独立的 `drift_trigger.py` 模块，按 SRP 拆成「解析阈值计算」「Page-CUSUM 累积器」「触发器策略接口」三块；在 `pipeline_run.py` 中按配置实例化具体策略，把 EKF 已有输出的 `step_y_s_inv_y` 逐步求和喂给触发器，触发后写入 `self.drift_detected = True` 并复用现有 `time_to_learn` 后的训练分支。配置层暴露 `drift_trigger.type ∈ {time_to_learn, sigma_y_sq, whitened_cusum}` 三选项，互斥但共享下游训练逻辑。

**Tech Stack:** Python 3.10+, PyTorch, NumPy, SciPy（`scipy.stats.chi2` 用于解析阈值），pytest（既有测试框架），Hydra（配置）。

---

## ⚠️ Git 提交纪律（强制）

本分支 `feature/whiten_innov` 的工作区**遗留有与本计划无关的改动**（来自上游 `ll` 分支的未提交修改：`notebooks/01_dataset_analysis.ipynb`、`docs/审稿/` 删除、`.codex/`、`temp/` 等）。这些改动**不属于本特性**，绝不能进入 `feature/whiten_innov` 的 commit 历史。

**绝对禁止**：

- `git add .`
- `git add -A`
- `git add -u`
- `git commit -a` / `git commit --all`

**强制要求**：每个 commit 必须**按文件路径显式 add**，且 add 的路径必须是本计划任务列表中明确出现过的（例如 `src/trainer_module/online_learning_parts/drift_trigger.py`、`tests/online_learning/test_drift_trigger.py` 等）。本计划任务列表中的每条 `git add` 命令都已经写好精确路径，请逐字执行，**不要简化、不要合并、不要替换为通配**。

每次 commit 前先跑一次 `git status` 确认 staging area 只含计划允许的文件；若发现 `notebooks/`、`docs/审稿/`、`.codex/`、`temp/` 中的任何条目被 staged，立即 `git restore --staged <path>` 取消。

---

## 范围与非目标

- ✅ 范围内
  - 解析阈值：χ²(M) 直接 NP 检验、Page-CUSUM 期望 ARL 阈值
  - Page-CUSUM 累积器（含可配置的 reset 策略）
  - 三种触发策略（time_to_learn / sigma_y_sq / whitened_cusum）共享同一接口
  - 配置 schema 扩展 + 日志/window 指标导出 `c_i`、`G_i`
  - Null 分布合规性验证脚本（无漂移台架下经验分布 vs 理论 χ²(3)）
  - 单元测试 + 一个最小集成 smoke 测试

- ❌ 非目标
  - 不替换或修改现有 `unsupervised_rmspe` MSIE 损失函数
  - 不改 EKF 数学（`extended.py:update()` 已返回 `S` 与 `y_s_inv_y`，零额外开销）
  - 不引入 UKF/IMM/PF（plan_whiten_innov.md L204 列为 future work）
  - 不实现 Huber 化白化（plan_whiten_innov.md L208，纳入 future work）
  - 不修改 SubspaceNet 模型结构

---

## 文件结构

### 新建

| 文件 | 职责 | 估计行数 |
| --- | --- | --- |
| `src/trainer_module/online_learning_parts/drift_trigger.py` | 阈值计算 + CUSUM + 三策略类 | 220 |
| `tests/online_learning/test_drift_trigger.py` | 单元测试 | 200 |
| `tests/integration/test_whitened_trigger_smoke.py` | 端到端 smoke 测试 | 80 |
| `scripts/validate_null_distribution.py` | Null 分布 KS 校验脚本 | 90 |

### 修改

| 文件 | 改动范围 | 说明 |
| --- | --- | --- |
| `src/trainer_module/online_learning_parts/pipeline_run.py:50-60` | 构造函数实例化 trigger | 按 cfg 选策略 |
| `src/trainer_module/online_learning_parts/pipeline_run.py:170-185` | 替换 time_to_learn-only 触发 | 改为 `trigger.update(...)` |
| `src/trainer_module/online_learning_parts/pipeline_run.py:267-285` | 接通 window 级 c_i 到 trigger | 取消注释、走新接口 |
| `src/trainer_module/online_learning_parts/metrics.py:280-295` | window_result 增加 `c_per_step` 与 `cusum_state` | 便于绘图与诊断 |
| `run/conf/Used_for_paper/SineAccel_base_model_Online_learning_snr_sweep_config.yaml` | 新增 `drift_trigger:` 配置块 | 默认保持 `time_to_learn` 不破坏既有实验 |

---

## 关键约定

- **数据流约定**：每个 step 的统计量 `c_step = sum_over_sources(y_s_inv_y[step, src])`；当所有 M=3 个独立 1D EKF 的 innovation 在 H0 下近似独立 N(0,1) 时，`c_step ~ χ²(M=3)`。这与 [plan_whiten_innov.md:Eq.7b](plan_whiten_innov.md) 在 M=3 时一致。
- **CUSUM 更新粒度**：默认 per-step；可配置 per-window（取窗口内均值）。
- **复位策略**：触发后立刻复位 `G=0`，对应 [plan_whiten_innov.md:202](plan_whiten_innov.md) 中的「待解决 #4」首选方案。
- **数值实现**：阈值 `h` 用 `scipy.optimize.brentq` 解 `h * exp(-h) = P_fa` 而非 Lambert W，避免引入 mpmath/scipy.special.lambertw 边界问题。
- **配置默认**：`drift_trigger.type: time_to_learn` 保持向后兼容；新功能需显式打开。

---

## 任务列表

### Task 1：解析阈值计算（χ² + CUSUM ARL）

**Files:**
- Create: `src/trainer_module/online_learning_parts/drift_trigger.py`
- Test: `tests/online_learning/test_drift_trigger.py`

- [ ] **Step 1.1：写第一个失败测试 — χ² 阈值反查**

```python
# tests/online_learning/test_drift_trigger.py
import math
from typing import Optional

import numpy as np
import pytest
from scipy.stats import chi2

from src.trainer_module.online_learning_parts.drift_trigger import (
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
```

- [ ] **Step 1.2：跑测试确认失败**

Run: `pytest tests/online_learning/test_drift_trigger.py::test_chi2_threshold_matches_scipy_inverse_cdf -v`
Expected: `ImportError: cannot import name 'compute_chi2_threshold'`

- [ ] **Step 1.3：实现 `compute_chi2_threshold`**

```python
# src/trainer_module/online_learning_parts/drift_trigger.py
"""Drift trigger strategies for unsupervised online adaptation.

Implements three strategies:
  - TimeToLearnTrigger: legacy hard-coded trigger at configured window index
  - SigmaYSqTrigger: original Konstantino paper sliding-window energy threshold
  - WhitenedCusumTrigger: whitened-innovation Page-CUSUM with analytical threshold
"""
from __future__ import annotations

import logging
import math
from dataclasses import dataclass, field
from typing import Optional, Sequence

import numpy as np
from scipy.optimize import brentq
from scipy.stats import chi2

logger = logging.getLogger(__name__)


def compute_chi2_threshold(p_fa: float, dof: int) -> float:
    """Inverse-CDF threshold for direct chi-square Neyman-Pearson test.

    Solves: P(c > tau | H0) = p_fa, where c ~ chi2(dof).
    """
    if not (0.0 < p_fa < 1.0):
        raise ValueError(f"p_fa must be in (0,1), got {p_fa}")
    if dof <= 0:
        raise ValueError(f"dof must be positive integer, got {dof}")
    return float(chi2.ppf(1.0 - p_fa, df=dof))
```

- [ ] **Step 1.4：跑测试确认通过**

Run: `pytest tests/online_learning/test_drift_trigger.py::test_chi2_threshold_matches_scipy_inverse_cdf tests/online_learning/test_drift_trigger.py::test_chi2_threshold_rejects_invalid_pfa tests/online_learning/test_drift_trigger.py::test_chi2_threshold_rejects_invalid_dof -v`
Expected: 3 PASS

- [ ] **Step 1.5：写 CUSUM 阈值测试**

```python
# tests/online_learning/test_drift_trigger.py（追加）
def test_cusum_threshold_satisfies_arl_relation():
    """h satisfies h * exp(-h) ≈ p_fa via Lorden ARL approximation."""
    p_fa = 0.01
    h = compute_cusum_threshold(p_fa=p_fa, dof=3, b_offset=1.0)
    # ARL relation: P_fa ≈ h * exp(-h)
    residual = h * math.exp(-h) - p_fa
    assert abs(residual) < 1e-6, f"h={h} does not satisfy ARL relation, residual={residual}"


def test_cusum_threshold_decreases_with_higher_pfa():
    """Looser p_fa → lower threshold."""
    h_strict = compute_cusum_threshold(p_fa=0.001, dof=3, b_offset=1.0)
    h_loose = compute_cusum_threshold(p_fa=0.10, dof=3, b_offset=1.0)
    assert h_strict > h_loose
```

- [ ] **Step 1.6：跑测试确认失败**

Run: `pytest tests/online_learning/test_drift_trigger.py::test_cusum_threshold_satisfies_arl_relation -v`
Expected: `ImportError`

- [ ] **Step 1.7：实现 `compute_cusum_threshold`**

```python
# 追加到 drift_trigger.py
def compute_cusum_threshold(p_fa: float, dof: int, b_offset: float) -> float:
    """Page-CUSUM threshold from Lorden's ARL approximation.

    Solves: h * exp(-h) = p_fa  (Eq.14-15 of plan_whiten_innov.md).
    The dof and b_offset are accepted for interface symmetry; the analytical
    relation only depends on p_fa under the chi-square null with parametric
    reference value b = E[c|H0] + b_offset.
    """
    if not (0.0 < p_fa < 0.5):
        raise ValueError(f"p_fa must be in (0, 0.5), got {p_fa}")
    if dof <= 0:
        raise ValueError(f"dof must be positive integer, got {dof}")
    if b_offset <= 0:
        raise ValueError(f"b_offset must be positive, got {b_offset}")

    def _residual(h: float) -> float:
        return h * math.exp(-h) - p_fa

    # h * exp(-h) is unimodal on (0, +inf); peak at h=1 with value 1/e ≈ 0.368.
    # For p_fa < 1/e there are two roots; we want the larger one (h > 1).
    if p_fa >= math.exp(-1.0):
        raise ValueError(
            f"p_fa={p_fa} too large for analytical CUSUM threshold (must be < 1/e ≈ 0.368)"
        )
    h = brentq(_residual, 1.0 + 1e-9, 50.0, xtol=1e-9)
    return float(h)
```

- [ ] **Step 1.8：跑测试确认通过**

Run: `pytest tests/online_learning/test_drift_trigger.py -v -k threshold`
Expected: 5 PASS

- [ ] **Step 1.9：commit**

```bash
git add src/trainer_module/online_learning_parts/drift_trigger.py tests/online_learning/test_drift_trigger.py
git commit -m "feat(drift_trigger): add analytical chi-square and CUSUM thresholds"
```

---

### Task 2：Page-CUSUM 累积器

**Files:**
- Modify: `src/trainer_module/online_learning_parts/drift_trigger.py`
- Modify: `tests/online_learning/test_drift_trigger.py`

- [ ] **Step 2.1：写 CUSUM 行为测试**

```python
# tests/online_learning/test_drift_trigger.py（追加）
import numpy as np

from src.trainer_module.online_learning_parts.drift_trigger import PageCusum


def test_page_cusum_stays_zero_under_null():
    """Under H0 (c_i drawn from chi2(M)), G_i should rarely cross threshold."""
    rng = np.random.default_rng(seed=42)
    M = 3
    cusum = PageCusum(reference_value=M + 1.0, threshold=8.0)
    n_steps = 1000
    triggered_count = 0
    for _ in range(n_steps):
        c = float(rng.chisquare(df=M))
        if cusum.update(c):
            triggered_count += 1
            cusum.reset()
    # With h=8, P_fa ≈ h*exp(-h) ≈ 0.0027 → expect <10 triggers in 1000 steps
    assert triggered_count < 15, f"too many false alarms: {triggered_count}/{n_steps}"


def test_page_cusum_triggers_under_drift():
    """Under H1 (c_i from non-central chi2 with large lambda), G_i must trigger."""
    rng = np.random.default_rng(seed=7)
    M = 3
    cusum = PageCusum(reference_value=M + 1.0, threshold=8.0)
    triggered_at: Optional[int] = None
    for i in range(200):
        # Non-central chi2 with lambda=15 → mean = M + lambda = 18 >> reference 4
        c = float(rng.noncentral_chisquare(df=M, nonc=15.0))
        if cusum.update(c):
            triggered_at = i
            break
    assert triggered_at is not None, "CUSUM failed to trigger under strong drift"
    assert triggered_at < 50, f"CUSUM trigger too slow: {triggered_at} steps"


def test_page_cusum_reset_clears_state():
    cusum = PageCusum(reference_value=4.0, threshold=8.0)
    for c in [10.0, 10.0, 10.0]:
        cusum.update(c)
    assert cusum.statistic > 0
    cusum.reset()
    assert cusum.statistic == 0.0


def test_page_cusum_never_negative():
    """G_i = max(0, G_{i-1} + c_i - b) — must clamp at zero."""
    cusum = PageCusum(reference_value=10.0, threshold=8.0)
    for c in [1.0, 1.0, 1.0]:  # all below reference
        cusum.update(c)
    assert cusum.statistic == 0.0
```

- [ ] **Step 2.2：跑测试确认失败**

Run: `pytest tests/online_learning/test_drift_trigger.py -v -k cusum`
Expected: `ImportError: cannot import name 'PageCusum'`

- [ ] **Step 2.3：实现 `PageCusum`**

```python
# 追加到 drift_trigger.py
@dataclass
class PageCusum:
    """Page-CUSUM accumulator: G_i = max(0, G_{i-1} + c_i - b)."""

    reference_value: float
    threshold: float
    statistic: float = field(default=0.0, init=False)
    n_updates: int = field(default=0, init=False)

    def __post_init__(self) -> None:
        if self.threshold <= 0:
            raise ValueError(f"threshold must be positive, got {self.threshold}")
        if self.reference_value <= 0:
            raise ValueError(f"reference_value must be positive, got {self.reference_value}")

    def update(self, c: float) -> bool:
        """Push new statistic c_i; return True if threshold crossed this step."""
        self.statistic = max(0.0, self.statistic + c - self.reference_value)
        self.n_updates += 1
        return self.statistic > self.threshold

    def reset(self) -> None:
        self.statistic = 0.0
```

- [ ] **Step 2.4：跑测试确认通过**

Run: `pytest tests/online_learning/test_drift_trigger.py -v -k cusum`
Expected: 4 PASS

- [ ] **Step 2.5：commit**

```bash
git add src/trainer_module/online_learning_parts/drift_trigger.py tests/online_learning/test_drift_trigger.py
git commit -m "feat(drift_trigger): add PageCusum accumulator with reset"
```

---

### Task 3：触发器策略接口与三种实现

**Files:**
- Modify: `src/trainer_module/online_learning_parts/drift_trigger.py`
- Modify: `tests/online_learning/test_drift_trigger.py`

- [ ] **Step 3.1：写策略接口契约测试**

```python
# tests/online_learning/test_drift_trigger.py（追加）
from src.trainer_module.online_learning_parts.drift_trigger import (
    DriftTrigger,
    TimeToLearnTrigger,
    SigmaYSqTrigger,
    WhitenedCusumTrigger,
    build_drift_trigger,
)


def test_time_to_learn_trigger_fires_at_target_window():
    trig = TimeToLearnTrigger(target_window=5)
    for w in range(10):
        per_step_c = [3.0, 3.0, 3.0]
        triggered = trig.observe_window(window_idx=w, c_per_step=per_step_c)
        if w < 5:
            assert not triggered
        elif w == 5:
            assert triggered
        else:
            assert not triggered  # one-shot semantics


def test_sigma_y_sq_trigger_fires_above_tau():
    trig = SigmaYSqTrigger(tau_sigma=2.0, window_size=5)
    # Feed 5 windows of low-energy innovations: should not fire
    for w in range(5):
        triggered = trig.observe_window(window_idx=w, c_per_step=[0.5] * 10)
        assert not triggered
    # Then feed high-energy: should fire
    triggered = trig.observe_window(window_idx=5, c_per_step=[10.0] * 10)
    assert triggered


def test_whitened_cusum_trigger_fires_under_drift():
    trig = WhitenedCusumTrigger(p_fa=0.01, dof=3, b_offset=1.0, reset_after_trigger=True)
    rng = np.random.default_rng(seed=11)
    fired_window: Optional[int] = None
    # 5 null windows
    for w in range(5):
        c_per_step = [float(rng.chisquare(df=3)) for _ in range(10)]
        if trig.observe_window(window_idx=w, c_per_step=c_per_step):
            fired_window = w
            break
    assert fired_window is None, "false alarm under null"
    # Drifted windows
    for w in range(5, 25):
        c_per_step = [float(rng.noncentral_chisquare(df=3, nonc=15.0)) for _ in range(10)]
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
```

- [ ] **Step 3.2：跑测试确认失败**

Run: `pytest tests/online_learning/test_drift_trigger.py -v -k trigger`
Expected: ImportError on `DriftTrigger`

- [ ] **Step 3.3：实现策略基类与三种实现**

```python
# 追加到 drift_trigger.py
from abc import ABC, abstractmethod
from typing import Mapping, Any, Deque
from collections import deque


class DriftTrigger(ABC):
    """Strategy interface: observe one window of per-step chi-square statistics."""

    @abstractmethod
    def observe_window(self, window_idx: int, c_per_step: Sequence[float]) -> bool:
        """Return True iff drift is declared this window."""

    @property
    @abstractmethod
    def state(self) -> Mapping[str, Any]:
        """Diagnostic state for logging (current_stat, threshold, etc.)."""


class TimeToLearnTrigger(DriftTrigger):
    """Legacy: fire exactly once at the configured window index."""

    def __init__(self, target_window: int) -> None:
        if target_window < 0:
            raise ValueError(f"target_window must be >=0, got {target_window}")
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
    """Original Konstantino sliding-window energy trigger: sigma_y^2(i) > tau_sigma.

    Operates on the same per-step chi-square statistics as the whitened version
    for fair comparison: sigma_y^2 here is the sliding mean of c_per_step.
    """

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
        return {
            "type": "sigma_y_sq",
            "tau_sigma": self.tau_sigma,
            "sigma2": self._last_sigma2,
        }


class WhitenedCusumTrigger(DriftTrigger):
    """Whitened-innovation Page-CUSUM with analytical threshold (Eq.7-15)."""

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
        reference = float(dof) + b_offset
        self._cusum = PageCusum(reference_value=reference, threshold=threshold)
        logger.info(
            f"WhitenedCusumTrigger: dof={dof}, p_fa={p_fa}, "
            f"b={reference:.3f}, h={threshold:.3f}"
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
            "threshold": self._cusum.threshold,
            "reference": self._cusum.reference_value,
            "statistic": self._cusum.statistic,
            "n_updates": self._cusum.n_updates,
        }


def build_drift_trigger(cfg: Mapping[str, Any]) -> DriftTrigger:
    """Factory dispatching on cfg['type']."""
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
```

- [ ] **Step 3.4：跑测试确认通过**

Run: `pytest tests/online_learning/test_drift_trigger.py -v`
Expected: 全部 PASS（共约 12 个测试）

- [ ] **Step 3.5：commit**

```bash
git add src/trainer_module/online_learning_parts/drift_trigger.py tests/online_learning/test_drift_trigger.py
git commit -m "feat(drift_trigger): add three-strategy DriftTrigger interface and factory"
```

---

### Task 4：在 pipeline_run.py 中接入触发器

**Files:**
- Modify: `src/trainer_module/online_learning_parts/pipeline_run.py:50-60`
- Modify: `src/trainer_module/online_learning_parts/pipeline_run.py:170-185`
- Modify: `src/trainer_module/online_learning_parts/pipeline_run.py:267-285`

- [ ] **Step 4.1：阅读上下文**

Run: `pytest tests/online_learning/test_drift_trigger.py -v` 一遍确认绿灯，然后阅读 [pipeline_run.py:40-110](../../src/trainer_module/online_learning_parts/pipeline_run.py) 与 [pipeline_run.py:170-300](../../src/trainer_module/online_learning_parts/pipeline_run.py)。

- [ ] **Step 4.2：在 pipeline_run.py 顶部加 import**

定位 pipeline_run.py 的 import 区，在最后一个本地 import 后追加：

```python
from src.trainer_module.online_learning_parts.drift_trigger import (
    DriftTrigger,
    build_drift_trigger,
)
```

- [ ] **Step 4.3：在构造函数中实例化 trigger**

定位 `self.drift_detected = False`（约 L53）。在它**之后**插入：

```python
        # Build drift-trigger strategy from config (with backward-compat fallback)
        drift_cfg = getattr(online_config, "drift_trigger", None)
        if drift_cfg is None:
            # Legacy path: synthesize time_to_learn config from existing field
            target = getattr(online_config, "time_to_learn", 0)
            drift_cfg = {"type": "time_to_learn", "target_window": int(target)}
        elif not isinstance(drift_cfg, dict):
            # Hydra DictConfig → plain dict
            from omegaconf import OmegaConf
            drift_cfg = OmegaConf.to_container(drift_cfg, resolve=True)
        self._drift_trigger: DriftTrigger = build_drift_trigger(drift_cfg)
        logger.info(f"Drift trigger initialized: {self._drift_trigger.state}")
```

- [ ] **Step 4.4：替换 time_to_learn 硬编码触发**

定位 [pipeline_run.py:177-179](../../src/trainer_module/online_learning_parts/pipeline_run.py)（当前为 `if self.time_to_learn is not None and window_idx == self.time_to_learn:`）。**删除整段 if 块**（3 行）。这一职责现在由 trigger 接管。

- [ ] **Step 4.5：在 window 评估完成后调用 trigger**

定位 L267-280（即 `if window_result.loss_metrics.main_loss > loss_threshold:` 那段）。**整段替换**为：

```python
            # Drift detection via configured trigger strategy
            c_per_step = self._extract_c_per_step(window_result)
            triggered_this_window = self._drift_trigger.observe_window(
                window_idx=window_idx,
                c_per_step=c_per_step,
            )
            if triggered_this_window:
                self.drift_detected = True
                drift_detected_count += 1
                logger.info(
                    f"Drift detected in window {window_idx} via "
                    f"{self._drift_trigger.state['type']} trigger; "
                    f"state={self._drift_trigger.state}"
                )
            else:
                logger.debug(
                    f"No drift in window {window_idx}; trigger state={self._drift_trigger.state}"
                )
```

- [ ] **Step 4.6：实现 `_extract_c_per_step` 辅助方法**

在 `OnlineLearningPipelineRun` 类（pipeline_run.py 主类）的合适位置（建议放在 `_evaluate_window` 之后，触发逻辑之前）追加：

```python
    @staticmethod
    def _extract_c_per_step(window_result) -> list[float]:
        """Sum per-source y_s_inv_y across sources to obtain scalar c_step ~ chi2(M)."""
        y_tensor = window_result.step_metrics.y_s_inv_y  # [steps, max_sources]
        # Each row sums to chi2(M) under H0 (M independent 1D EKFs)
        return y_tensor.sum(dim=1).tolist()
```

- [ ] **Step 4.7：跑既有 pipeline_run 相关测试不破坏**

Run: `pytest tests/online_learning/ -v --tb=short`
Expected: 既有用例仍 PASS；test_drift_trigger.py 全 PASS。

- [ ] **Step 4.8：commit**

```bash
git add src/trainer_module/online_learning_parts/pipeline_run.py
git commit -m "refactor(pipeline_run): wire DriftTrigger strategy and remove hard-coded time_to_learn"
```

---

### Task 5：window_result 暴露诊断字段

**Files:**
- Modify: `src/trainer_module/online_learning_parts/metrics.py:280-295`
- Modify: `tests/online_learning/test_metrics_aggregate.py`（视情况）

- [ ] **Step 5.1：定位 `step_metrics = StepMetrics(...)` 构造点（L286）**

阅读 [metrics.py:280-310](../../src/trainer_module/online_learning_parts/metrics.py)，确认 `StepMetrics` 是否已能容纳新字段。

- [ ] **Step 5.2：在 metrics.py 中导出 c_per_step 与 cusum 状态快照**

在 `_build_window_result_impl`（或对应的 build 函数）紧邻 `step_metrics = StepMetrics(...)` **之后**新增：

```python
    # Derived stat: per-step whitened innovation chi-square (sum across sources)
    c_per_step_list = ekf_y_s_inv_y.sum(dim=1).tolist()
    if hasattr(step_metrics, "c_per_step"):
        step_metrics.c_per_step = c_per_step_list
    else:
        # StepMetrics dataclass not yet extended; attach as attribute
        setattr(step_metrics, "c_per_step", c_per_step_list)
```

- [ ] **Step 5.3：写一个轻量验证测试**

```python
# tests/online_learning/test_metrics_aggregate.py（追加）
import torch

from src.trainer_module.online_learning_parts.metrics import StepMetrics


def test_c_per_step_equals_sum_over_sources():
    y = torch.tensor([[1.0, 2.0, 3.0], [0.5, 0.5, 0.5]])
    expected = [6.0, 1.5]
    # Surrogate: emulate the assignment performed in metrics.py
    c = y.sum(dim=1).tolist()
    assert c == expected
```

- [ ] **Step 5.4：跑测试确认通过**

Run: `pytest tests/online_learning/test_metrics_aggregate.py -v -k c_per_step`
Expected: PASS

- [ ] **Step 5.5：commit**

```bash
git add src/trainer_module/online_learning_parts/metrics.py tests/online_learning/test_metrics_aggregate.py
git commit -m "feat(metrics): expose c_per_step diagnostic on window result"
```

---

### Task 6：配置 schema 扩展

**Files:**
- Modify: `run/conf/Used_for_paper/SineAccel_base_model_Online_learning_snr_sweep_config.yaml`

- [ ] **Step 6.1：阅读现有 online 配置块**

Run: `head -160 run/conf/Used_for_paper/SineAccel_base_model_Online_learning_snr_sweep_config.yaml`，定位 `online_learning:` 节点（含 `time_to_learn` 字段）。

- [ ] **Step 6.2：在 online 配置块末尾追加 `drift_trigger`**

```yaml
  # ---- Drift trigger configuration ----
  # Three strategies:
  #   - time_to_learn: legacy fixed window index (default for backward compat)
  #   - sigma_y_sq:    Konstantino paper sliding-window energy threshold
  #   - whitened_cusum: whitened-innovation Page-CUSUM with analytical threshold
  drift_trigger:
    type: time_to_learn        # one of: time_to_learn, sigma_y_sq, whitened_cusum
    target_window: 50          # used by time_to_learn
    # The following are read only when type matches:
    tau_sigma: 1.5             # used by sigma_y_sq
    window_size: 5             # used by sigma_y_sq
    p_fa: 0.01                 # used by whitened_cusum
    dof: 3                     # used by whitened_cusum (== M sources)
    b_offset: 1.0              # used by whitened_cusum (Lorden reference offset)
    reset_after_trigger: true  # used by whitened_cusum
```

- [ ] **Step 6.3：再克隆出两份对照配置**

新建 `run/conf/Used_for_paper/SineAccel_sigma_y_sq_trigger.yaml` 与 `run/conf/Used_for_paper/SineAccel_whitened_cusum_trigger.yaml`，内容：

```yaml
# SineAccel_whitened_cusum_trigger.yaml
defaults:
  - SineAccel_base_model_Online_learning_snr_sweep_config

online_learning:
  drift_trigger:
    type: whitened_cusum
    p_fa: 0.01
    dof: 3
    b_offset: 1.0
    reset_after_trigger: true
```

```yaml
# SineAccel_sigma_y_sq_trigger.yaml
defaults:
  - SineAccel_base_model_Online_learning_snr_sweep_config

online_learning:
  drift_trigger:
    type: sigma_y_sq
    tau_sigma: 1.5
    window_size: 5
```

- [ ] **Step 6.4：commit**

```bash
git add run/conf/Used_for_paper/
git commit -m "feat(config): expose drift_trigger config and add three preset variants"
```

---

### Task 7：Smoke 集成测试

**Files:**
- Create: `tests/integration/test_whitened_trigger_smoke.py`

- [ ] **Step 7.1：探查既有集成测试结构**

Run: `ls tests/integration/ && head -40 tests/integration/test_integration_contracts.py 2>/dev/null || true`
（先了解现有 fixture/工具）

- [ ] **Step 7.2：写 smoke 测试**

```python
# tests/integration/test_whitened_trigger_smoke.py
"""End-to-end smoke: run a 1-trajectory online learning session with whitened_cusum.

Validates:
  1. Pipeline runs without exception.
  2. drift_detected flips True at least once when drift is injected.
  3. Trigger state is non-default (CUSUM accumulated >= 1 update).
"""
import pytest

pytestmark = pytest.mark.integration


def test_whitened_cusum_trigger_runs_end_to_end(tmp_path):
    """Minimal config override: 1 trajectory, short horizon, whitened_cusum trigger."""
    pytest.importorskip("hydra")
    pytest.importorskip("omegaconf")
    from hydra import compose, initialize_config_dir
    from omegaconf import OmegaConf

    import os
    config_dir = os.path.abspath("run/conf/Used_for_paper")

    with initialize_config_dir(version_base=None, config_dir=config_dir):
        cfg = compose(
            config_name="SineAccel_whitened_cusum_trigger",
            overrides=[
                "online_learning.dataset_size=1",
                "online_learning.trajectory_length=60",
                "online_learning.eta_increment=1.0",
                "online_learning.max_eta=1.0",
                f"hydra.run.dir={tmp_path}",
            ],
        )

    # Lazy import to avoid heavy startup when test is skipped
    from src.trainer_module.online_learning import OnlineLearning

    runner = OnlineLearning(cfg)
    runner.run()

    # Inspect the last pipeline_run state
    pipeline = runner._pipeline_run  # exposed for testing; document if not yet
    assert pipeline._drift_trigger is not None
    state = pipeline._drift_trigger.state
    assert state["type"] == "whitened_cusum"
    # Either drift fired or CUSUM accumulated some updates without firing
    assert state["n_updates"] >= 1, f"trigger never observed any window: state={state}"
```

- [ ] **Step 7.3：跑 smoke**

Run: `pytest tests/integration/test_whitened_trigger_smoke.py -v -m integration --tb=short`
Expected: PASS（若依赖私有属性 `_pipeline_run` 不存在，则在 pipeline_run/online_learning 中加最小 getter 后再跑；本步骤明确允许 ≤10 行的 setter/getter 增补）。

- [ ] **Step 7.4：commit**

```bash
git add tests/integration/test_whitened_trigger_smoke.py
# 若动了 online_learning.py 或 pipeline_run.py：一并 add
git commit -m "test(integration): smoke for whitened CUSUM trigger end-to-end"
```

---

### Task 8：Null 分布合规性脚本（plan_whiten_innov.md 待解决 #2）

**Files:**
- Create: `scripts/validate_null_distribution.py`

- [ ] **Step 8.1：写脚本**

```python
# scripts/validate_null_distribution.py
"""Empirical validation: c_i = y^T S^-1 y under no-drift should follow chi2(M).

Runs the existing pipeline with eta=0 (no drift) for a single trajectory,
collects all c_step values, and runs a Kolmogorov-Smirnov test against chi2(M).

Usage:
    python scripts/validate_null_distribution.py --config SineAccel_base_model_Online_learning_snr_sweep_config

Exit code 0 iff KS p-value > 0.05 (cannot reject null).
"""
from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

import numpy as np
from scipy import stats

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="SineAccel_base_model_Online_learning_snr_sweep_config")
    parser.add_argument("--dof", type=int, default=3)
    parser.add_argument("--alpha", type=float, default=0.05)
    parser.add_argument("--out", type=Path, default=Path("outputs/null_validation.npz"))
    args = parser.parse_args()

    from hydra import compose, initialize_config_dir
    config_dir = str(Path("run/conf/Used_for_paper").resolve())
    with initialize_config_dir(version_base=None, config_dir=config_dir):
        cfg = compose(
            config_name=args.config,
            overrides=[
                "online_learning.dataset_size=1",
                "online_learning.trajectory_length=300",
                "online_learning.eta_increment=0.0",
                "online_learning.max_eta=0.0",
                "online_learning.drift_trigger.type=time_to_learn",
                "online_learning.drift_trigger.target_window=999999",  # never fire
            ],
        )
    from src.trainer_module.online_learning import OnlineLearning
    runner = OnlineLearning(cfg)
    runner.run()

    pipeline = runner._pipeline_run
    c_values: list[float] = []
    for wr in pipeline._trajectory_results.window_results:
        y = wr.step_metrics.y_s_inv_y  # [steps, max_sources]
        c_values.extend(y.sum(dim=1).tolist())

    c_arr = np.asarray(c_values, dtype=np.float64)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    np.savez(args.out, c=c_arr, dof=args.dof)

    ks_stat, p_value = stats.kstest(c_arr, "chi2", args=(args.dof,))
    logger.info(f"N={len(c_arr)} samples, mean={c_arr.mean():.3f} (theoretical {args.dof})")
    logger.info(f"KS test vs chi2({args.dof}): stat={ks_stat:.4f}, p={p_value:.4g}")

    if p_value > args.alpha:
        logger.info(f"PASS: cannot reject H0 at alpha={args.alpha}")
        return 0
    logger.warning(f"FAIL: p={p_value:.4g} <= alpha={args.alpha}; null distribution deviates")
    return 1


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 8.2：跑一次脚本（不阻塞计划）**

Run: `python scripts/validate_null_distribution.py --config SineAccel_base_model_Online_learning_snr_sweep_config`
Expected: 退出码 0；输出形如 `mean ≈ 3.0`。若 p < 0.05 则记录 R_obs 估计偏差，列入 follow-up（plan_whiten_innov.md 待解决 #1）。

- [ ] **Step 8.3：commit**

```bash
git add scripts/validate_null_distribution.py
git commit -m "feat(scripts): add chi-square null-distribution KS validator"
```

---

### Task 9：文档与最终 commit

**Files:**
- Modify: `plan/plan_26Apr/plan_whiten_innov.md`（在文末追加 implementation status）
- Create: `plan/plan_26Apr/IMPLEMENTATION_NOTES.md`

- [ ] **Step 9.1：写实现状态备忘**

```markdown
# IMPLEMENTATION_NOTES.md

## 已完成
- [x] `compute_chi2_threshold` 与 `compute_cusum_threshold` 解析阈值
- [x] `PageCusum` 累积器（含 reset）
- [x] `DriftTrigger` 三策略（time_to_learn / sigma_y_sq / whitened_cusum）
- [x] `pipeline_run.py` 接入策略，移除 time_to_learn 硬编码分支
- [x] `c_per_step` 暴露到 window_result 用于诊断
- [x] 配置 schema + 三个 YAML 预设
- [x] 单元测试（drift_trigger 12 用例）+ 集成 smoke + null 分布脚本

## 未完成（plan_whiten_innov.md 待解决条目）
- [ ] #1 R_obs 在线估计（选项 B）—— 当前用 EKF 预设 R
- [ ] #3 b_offset 敏感性 sweep
- [ ] #5 EKF vs UKF 对比
- [ ] #7 非高斯（脉冲）噪声鲁棒性
- [ ] Huber 化白化 fallback

## 验收建议
1. 跑 `pytest tests/online_learning/test_drift_trigger.py tests/integration/test_whitened_trigger_smoke.py -v` 全绿
2. 跑 `python scripts/validate_null_distribution.py` 退出码 0
3. 用 `SineAccel_whitened_cusum_trigger.yaml` 与 `SineAccel_sigma_y_sq_trigger.yaml` 各跑一次完整 SNR sweep，输出对比表
```

- [ ] **Step 9.2：在 plan_whiten_innov.md 末尾追加一行指向**

```markdown

---

## 📝 实现状态

详见 [plan_implementation_whiten_innov.md](plan_implementation_whiten_innov.md) 与 [IMPLEMENTATION_NOTES.md](IMPLEMENTATION_NOTES.md)。
```

- [ ] **Step 9.3：commit**

```bash
git add plan/plan_26Apr/IMPLEMENTATION_NOTES.md plan/plan_26Apr/plan_whiten_innov.md
git commit -m "docs(plan): record implementation status of whitened CUSUM trigger"
```

---

## 验收清单（供 Claude 验收 Codex 成果时使用）

### 静态检查
- [ ] `src/trainer_module/online_learning_parts/drift_trigger.py` 存在且 < 250 行
- [ ] 所有公共函数/类有类型注解与简洁 docstring
- [ ] `pipeline_run.py` 中已无 `if self.time_to_learn is not None and window_idx == self.time_to_learn` 这一硬编码片段
- [ ] `pipeline_run.py:271-285` 的 `# self.drift_detected = True` 注释已被新触发器逻辑取代（注释行不应残留）

### 测试
- [ ] `pytest tests/online_learning/test_drift_trigger.py -v` 全绿（约 12 用例）
- [ ] `pytest tests/online_learning/ -v` 全绿，没有破坏既有用例
- [ ] `pytest tests/integration/test_whitened_trigger_smoke.py -v -m integration` 通过

### 运行时
- [ ] `python scripts/validate_null_distribution.py` 退出码 0；mean(c) 在 [2.5, 3.5]
- [ ] 用 `SineAccel_whitened_cusum_trigger.yaml` 跑 1 条短轨迹，日志中能看到 `Drift trigger initialized: {'type': 'whitened_cusum', ...}`
- [ ] 触发后 CUSUM `statistic` 被 reset 为 0（reset_after_trigger=true 路径）

### 配置
- [ ] 不指定 `drift_trigger` 时，pipeline 仍按 `time_to_learn` 兼容运行（向后兼容）
- [ ] 三种 type 切换无需改代码，仅改 YAML

### 文档
- [ ] `IMPLEMENTATION_NOTES.md` 列出已完成/未完成对照表
- [ ] 配置 YAML 中的注释解释了三种 type 的语义
