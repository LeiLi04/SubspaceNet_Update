# 白化新息触发器有效性验证 实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 用统计学上可靠的样本量证明白化新息 Page-CUSUM 触发器在 SubspaceNet+EKF 闭环下**有效**——即在无漂移时能稳定不误触发，在不同漂移幅度下能稳定检测，并且至少不弱于 `time_to_learn` 和 `sigma_y_sq` 两个对照基线。

**Architecture:** 复用 [plan/plan_26Apr/plan_whiten_innov.md](../plan_26Apr/plan_whiten_innov.md) 已经建好的全部代码资产（drift_trigger.py 三策略、pipeline 触发器接入、dump 钩子、KS 验证脚本、三套 YAML 预设）。本计划只做四件事：(1) 锁定当前 calibration 状态到 git；(2) 把 `sigma_y_sq` 的 `tau_sigma` 从默认 1.5（过敏）重新标定到与 calibrated whitened CUSUM 同量级的 no-drift 通过点；(3) 把 N=3 的 smoke 扩到 N=20 拿到统计学有效的检测率/误触发率/平均延迟；(4) 输出一张论文级对比表 + 一张检测率-vs-漂移幅度的图。

**Tech Stack:** Python 3.10+, PyTorch, Hydra, NumPy, SciPy, matplotlib, pytest（既有），bash for orchestration。

---

## ⚠️ Git 提交纪律（强制）

本分支 `feature/whiten_innov` 工作树仍带 ll 分支遗留改动（`docs/审稿/` 删除、`notebooks/01_dataset_analysis.ipynb` 修改、`temp/`）。

**绝对禁止**：

- `git add .`
- `git add -A`
- `git add -u`
- `git commit -a` / `git commit --all`

每个 commit 必须按文件路径显式 add，路径必须是本计划任务列表里出现过的。每次 commit 前先 `git status` 自检 staging area。

---

## 🧰 复用资产清单（来自 plan_26Apr）

下列资产已经存在且经过验证，本计划**直接调用**，不再重写：

### 代码模块

| 路径 | 用途 |
| --- | --- |
| `src/trainer_module/online_learning_parts/drift_trigger.py` | 三策略触发器：`time_to_learn` / `sigma_y_sq` / `whitened_cusum`，工厂 `build_drift_trigger(cfg)` |
| `src/trainer_module/online_learning_parts/pipeline_run.py` | 触发器接入；含触发后暂停 trigger 观察的修复（pipeline_run.py:327-368） |
| `src/trainer_module/online_learning_parts/metrics.py` | `c_per_step`、`innovation_covariances` 暴露在 `step_metrics` 上 |
| `scripts/validate_null_distribution.py` | 真实 dump → KS test 验证脚本 |
| `config/schema.py:DriftTriggerConfig` | Pydantic schema |

### YAML 预设

| 路径 | 用途 | 当前参数 |
| --- | --- | --- |
| `run/conf/Used_for_paper/SineAccel_base_model_Online_learning_snr_sweep_config.yaml` | 共同基础（`time_to_learn` 默认） | `target_window=35` |
| `run/conf/Used_for_paper/SineAccel_sigma_y_sq_trigger.yaml` | 原论文滑窗能量对照 | `tau_sigma=1.5, window_size=5` ⚠ **本计划要重新标定** |
| `run/conf/Used_for_paper/SineAccel_whitened_cusum_pretrained_calibrated.yaml` | 闭环 calibrated whitened CUSUM | `R_obs=0.125, p_fa=1e-6, b_offset=24` ✅ **本计划主角** |

### Checkpoint

```text
checkpoints/saved_SubspaceNet_trained_20260224_180720.pt
```

按 plan_26Apr §8 验证，本仓库现有最佳可用 checkpoint。原配置引用的 `final_SubspaceNet_20250916_084930.pt` 已确认无法从作者公开 GitHub 仓库获取，本计划接受 `180720.pt` 作为代理。

### 既有 calibration 关键结论（来自 plan_26Apr §9）

| 设置 | no-drift 误触发 | eta=1.0 检测率 | eta=1.0 平均延迟（窗口） |
| --- | ---: | ---: | ---: |
| `R_obs=0.125, b_offset=24` | 0/3 | 3/3 | 3.333 |

弱漂移 `eta=0.6` 在 N=3 下只有 2/3 检测，**这是本计划首要要在 N=20 下确认的现象**。

---

## 范围与非目标

✅ **范围内**

- 锁定当前 calibration 状态到 git 历史
- `sigma_y_sq` 的 `tau_sigma` 重新标定，使其在 no-drift 下也 0% 误触发
- 三触发器在 dataset_size=20、`eta ∈ {0.0, 0.3, 0.6, 1.0}` 下的同条件对比
- 检测率 / 误触发率 / 平均延迟 / tail-5 RMSPE improvement 表格
- 检测率 vs 漂移幅度的折线图

❌ **非目标**

- 不寻找/重训"原始 0916 checkpoint"
- 不引入 source-specific R_obs / robust CUSUM / Huber 化 innovation
- 不解决 plan_26Apr §9 的 `source[0]` 残余 outlier
- 不做 SNR sweep 或 T sweep（本计划只在默认 SNR / T 下做）
- 不写论文正文，只产出可直接放入论文 Section IV 的对比表 CSV + 图

---

## 文件结构

### 新建

| 路径 | 职责 | 估计行数 |
| --- | --- | --- |
| `scripts/run_trigger_validation.py` | 多 trigger × 多 eta × N trajectory 批量运行驱动 | 180 |
| `scripts/aggregate_trigger_results.py` | 把 outputs 目录下的 summary.json 聚合成 CSV + Markdown 表 | 130 |
| `scripts/plot_trigger_validation.py` | 检测率/延迟/误触发率图 | 110 |
| `tests/scripts/test_aggregate_trigger_results.py` | 聚合脚本单元测试 | 90 |
| `plan/plan_29Apr/results.md` | 实验结论摘要（论文用） | 输出文档 |
| `run/conf/Used_for_paper/SineAccel_sigma_y_sq_trigger_retuned.yaml` | 重新标定后的 `sigma_y_sq` 预设 | 14 |

### 修改

| 路径 | 改动 |
| --- | --- |
| `.gitignore` | 追加 `outputs/trigger_validation_*` 与 `outputs/sigma_y_sq_retune_*` 的忽略规则 |

无既有源码改动 —— 本计划纯粹"运行 + 聚合 + 制表"，所有触发器/管线代码已经就位。

---

## 关键约定

- **共同实验设置**（除非任务里另注）：

```text
dataset_size=20
trajectory_length=100
window_size=5
stride=5
eta_update_interval_windows=5
drift_onset_window=5
max_iterations=1
kalman_filter.measurement_noise_std_dev=0.125
simulation.load_model=true
simulation.model_path=checkpoints/saved_SubspaceNet_trained_20260224_180720.pt
```

- **漂移幅度档位**：`eta ∈ {0.0, 0.3, 0.6, 1.0}`，其中 `eta=0.0` 即 no-drift 基准。
- **三触发器**：

| 名称 | 配置文件 | 关键参数 |
| --- | --- | --- |
| `time_to_learn` | base 配置 + override `drift_trigger.target_window=6` | 漂移 onset 后 1 个窗口的"已知 oracle"基线 |
| `sigma_y_sq_retuned` | `SineAccel_sigma_y_sq_trigger_retuned.yaml` | Task 1 标定出来的 `tau_sigma` |
| `whitened_cusum_pretrained_calibrated` | `SineAccel_whitened_cusum_pretrained_calibrated.yaml` | `R_obs=0.125, p_fa=1e-6, b_offset=24` |

- **输出根目录**：`outputs/trigger_validation_20260429/`

- **统计验收门槛**（基于 N=20 的 binomial 95% CI 推荐）：

| 指标 | 通过标准 |
| --- | --- |
| 强漂移（eta=1.0）检测率 | ≥ 18/20（90%） |
| 中等漂移（eta=0.6）检测率 | ≥ 12/20（60%） |
| 弱漂移（eta=0.3）检测率 | 报告即可，无硬指标 |
| no-drift 误触发率 | ≤ 1/20（5%） |
| 强漂移平均延迟 | ≤ 5 windows |

---

## 任务列表

### Task 0：锁定 plan_26Apr 累计的 calibration 状态

**Files:**
- Modify: `.gitignore`
- Modify: `src/trainer_module/online_learning_parts/pipeline_run.py`（已修，待 commit）
- Modify: `plan/plan_26Apr/IMPLEMENTATION_NOTES.md`（已修，待 commit）
- Modify: `plan/plan_26Apr/plan_whiten_innov.md`（已修，待 commit）
- Create: `run/conf/Used_for_paper/SineAccel_whitened_cusum_pretrained_calibrated.yaml`（已建，待 commit）

- [x] **Step 0.1：把 trigger_validation 输出根目录加到 .gitignore**

打开 `.gitignore`，在 `# Local validation outputs` 节末尾追加：

```text
outputs/trigger_validation_*/
outputs/trigger_validation_*.npz
outputs/sigma_y_sq_retune_*/
outputs/sigma_y_sq_retune_*.npz
```

- [x] **Step 0.2：自检 staging area 是空的**

Run: `git diff --cached --name-only`
Expected: 无输出

实际记录（2026-04-29）：`git diff --cached --name-only` 无输出。

- [ ] **Step 0.3：分批 commit**

```bash
# 批 A：触发器暂停修复
git add src/trainer_module/online_learning_parts/pipeline_run.py
git diff --cached --stat
git commit -m "fix(pipeline): pause drift trigger after entering online-learning path

Once a trajectory has triggered drift detection and entered the online-learning
branch, additional trigger fires within the same trajectory do not represent new
drift events. Skip observe_window in this state but keep accumulating
c_per_step diagnostics. Also append window_update_flags every iteration so the
flag list aligns with window_count.

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"

# 批 B：calibrated 预设
git add run/conf/Used_for_paper/SineAccel_whitened_cusum_pretrained_calibrated.yaml
git diff --cached --stat
git commit -m "feat(config): pretrained-calibrated whitened CUSUM preset (R_obs=0.125, b=24)

Joint (R_obs, b_offset) sweep with checkpoints/saved_SubspaceNet_trained_20260224_180720.pt
selected (0.125, 24) as the closed-loop best candidate:
- no-drift 0/3 false alarms
- c_mean=3.035 closest to chi2(3) expectation 3
- eta=1.0 strong drift 3/3 detection, mean delay 3.333 windows
- eta=0.6 weak drift 2/3 detection (open question for N=20 validation)

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"

# 批 C：研究记录
git add .gitignore plan/plan_26Apr/plan_whiten_innov.md plan/plan_26Apr/IMPLEMENTATION_NOTES.md
git diff --cached --stat
git commit -m "docs(plan): R_obs sweep + joint calibration + trigger comparison records

Append the multi-round closed-loop calibration log:
- Step C-E pretrained no-drift smoke and source-level diagnostics
- Association sanity check ruling out source-permutation as root cause
- Coarse / fine / joint R_obs sweeps narrowing to (0.125, 24)
- Three-trigger short comparison exposing pipeline trigger-pause requirement

Add gitignore patterns for trigger_validation and sigma_y_sq_retune outputs.

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

- [ ] **Step 0.4：push 到 origin**

```bash
git push origin feature/whiten_innov
```

Expected: `origin/feature/whiten_innov` 推进 3 个 commit。

---

### Task 1：sigma_y_sq tau_sigma 重新标定

**Files:**
- Create: `run/conf/Used_for_paper/SineAccel_sigma_y_sq_trigger_retuned.yaml`

**目标**：plan_26Apr §⚖️.4 已记录 `sigma_y_sq(tau_sigma=1.5)` 在闭环里 3/3 trajectory 都从 window 0 开始触发，过敏到不能作为 comparator。本任务用 no-drift smoke 找到第一个 0/3 误触发的 `tau_sigma`，作为 N=20 对比里的"公平 sigma_y_sq 设置"。

- [x] **Step 1.1：列出候选扫点**

参考 plan_26Apr 中 dump 摘要：no-drift `c_mean ≈ 3.035, c_p95 ≈ 14.5, c_p99 ≈ 21.1`（pretrained checkpoint, R_obs=0.125）。`sigma_y_sq` 是 `c_per_step` 的滑窗均值（窗口=5）。

候选扫点：

```text
tau_sigma ∈ {3.0, 4.0, 5.0, 6.0, 8.0, 10.0, 12.0, 15.0}
```

- [x] **Step 1.2：跑 no-drift sweep**

确认仓库实际入口（按 plan_26Apr 之前执行经验，应该是 `python -m run.pipeline.online_learning_pipeline` 或仓库内对应入口；如不一致，按当前可执行入口替换）：

```bash
ENTRY="run.pipeline.online_learning_pipeline"  # adjust if different
for tau in 3.0 4.0 5.0 6.0 8.0 10.0 12.0 15.0; do
  .venv/Scripts/python.exe -m $ENTRY \
    --config-path ../../conf/Used_for_paper \
    --config-name SineAccel_base_model_Online_learning_snr_sweep_config \
    +online_learning.drift_trigger.type=sigma_y_sq \
    +online_learning.drift_trigger.tau_sigma=$tau \
    +online_learning.drift_trigger.window_size=5 \
    online_learning.dataset_size=3 \
    online_learning.trajectory_length=100 \
    online_learning.window_size=5 \
    online_learning.stride=5 \
    online_learning.eta_increment=0 \
    online_learning.max_eta=0 \
    kalman_filter.measurement_noise_std_dev=0.125 \
    simulation.load_model=true \
    simulation.model_path=checkpoints/saved_SubspaceNet_trained_20260224_180720.pt \
    "hydra.run.dir=outputs/sigma_y_sq_retune_20260429/tau_${tau}"
done
```

- [x] **Step 1.3：自检每个 sub-run 的 first_online_windows**

```bash
.venv/Scripts/python.exe -c "
import json, glob, sys
for d in sorted(glob.glob('outputs/sigma_y_sq_retune_20260429/tau_*')):
    candidates = glob.glob(f'{d}/**/online_learning_results.json', recursive=True)
    if not candidates:
        candidates = glob.glob(f'{d}/**/summary.json', recursive=True)
    if not candidates:
        print(d, 'NO_SUMMARY'); continue
    payload = json.load(open(candidates[0]))
    print(d.split('tau_')[-1], 'first_online_windows=', payload.get('first_online_windows'))
"
```

Expected: 每个 tau 一行，含 first_online_windows 列表。

实际输出（2026-04-29，WSL `.venv-wsl`，direct Simulation runner）：

| tau_sigma | no-drift false triggers | first_online_windows | c_mean | c_p95 | c_p99 | c_max |
| ---: | ---: | --- | ---: | ---: | ---: | ---: |
| 3.0 | 3/3 | `[9, 0, 10]` | 2.1238 | 5.2980 | 6.9834 | 10.4392 |
| 4.0 | 3/3 | `[9, 0, 14]` | 2.1117 | 5.1993 | 6.9410 | 10.7038 |
| 5.0 | 1/3 | `[null, 2, null]` | 2.1991 | 5.7310 | 8.7535 | 9.3223 |
| 6.0 | 1/3 | `[null, 2, null]` | 2.1991 | 5.7310 | 8.7535 | 9.3223 |
| 8.0 | 1/3 | `[null, null, 15]` | 3.0355 | 8.3046 | 14.4972 | 41.8224 |
| 10.0 | 1/3 | `[null, null, 15]` | 3.0355 | 8.3046 | 14.4972 | 41.8224 |
| 12.0 | 0/3 | `[null, null, null]` | 3.0347 | 8.3046 | 14.4972 | 41.8224 |
| 15.0 | 0/3 | `[null, null, null]` | 3.0347 | 8.3046 | 14.4972 | 41.8224 |

选择依据：`tau_sigma=12.0` 是候选集合里第一个达到 0/3 no-drift 误触发的阈值。

- [x] **Step 1.4：选择第一个 0/3 误触发的 `tau_sigma`，写新 YAML**

设选定的 `tau_sigma` 为 `12.0`（实际值由 Step 1.3 决定）：

```yaml
# run/conf/Used_for_paper/SineAccel_sigma_y_sq_trigger_retuned.yaml
defaults:
  - SineAccel_base_model_Online_learning_snr_sweep_config
  - _self_

kalman_filter:
  measurement_noise_std_dev: 0.125

online_learning:
  drift_trigger:
    type: sigma_y_sq
    tau_sigma: 12.0
    window_size: 5
  dump_c_per_step_path: null
```

- [x] **Step 1.5：跑既有 pytest 确认 sigma_y_sq trigger 仍工作**

```bash
.venv/Scripts/python.exe -m pytest tests/online_learning/test_drift_trigger.py -v -k sigma -q
```

Expected: 1 passed (test_sigma_y_sq_trigger_fires_above_tau)

实际结果（2026-04-29，WSL）：

```text
.venv-wsl/bin/python -m pytest tests/online_learning/test_drift_trigger.py -v -k sigma -q
1 passed, 13 deselected, 2 warnings
```

- [ ] **Step 1.6：commit**

```bash
git add run/conf/Used_for_paper/SineAccel_sigma_y_sq_trigger_retuned.yaml
git diff --cached --stat
git commit -m "feat(config): retune sigma_y_sq tau_sigma for closed-loop pretrained baseline

Original tau_sigma=1.5 fires on window 0 of every trajectory in the closed-loop
pretrained setup. Sweep tau_sigma in {3..15} found the smallest 0/3 no-drift
false-alarm threshold under the same R_obs=0.125 / pretrained-checkpoint setting
used by whitened_cusum_pretrained_calibrated. Selected tau_sigma=12.0.

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

### Task 2：N=20 三触发器统计扩展

**Files:**
- Create: `scripts/run_trigger_validation.py`

- [x] **Step 2.1：写驱动脚本**

```python
# scripts/run_trigger_validation.py
"""Run all (trigger x eta) cells for N trajectories each.

Usage:
    python scripts/run_trigger_validation.py [--dry-run] [--n-traj 20]

Each cell writes outputs/trigger_validation_20260429/<trigger>/eta_<eta>/...
"""
from __future__ import annotations

import argparse
import logging
import shlex
import subprocess
import sys
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_ROOT = ROOT / "outputs" / "trigger_validation_20260429"

CHECKPOINT = "checkpoints/saved_SubspaceNet_trained_20260224_180720.pt"
PIPELINE_ENTRY = "run.pipeline.online_learning_pipeline"  # adjust if entry differs

TRIGGERS = {
    "time_to_learn": {
        "config_name": "SineAccel_base_model_Online_learning_snr_sweep_config",
        "overrides": [
            "+online_learning.drift_trigger.type=time_to_learn",
            "+online_learning.drift_trigger.target_window=6",
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


def _eta_dirname(eta: float) -> str:
    return f"eta_{eta:.2f}".replace(".", "p")


def build_command(trigger_name: str, eta: float, n_traj: int) -> list[str]:
    cfg = TRIGGERS[trigger_name]
    out_dir = OUTPUT_ROOT / trigger_name / _eta_dirname(eta)
    cmd = [
        sys.executable, "-m", PIPELINE_ENTRY,
        "--config-path", "../../conf/Used_for_paper",
        "--config-name", cfg["config_name"],
        f"online_learning.dataset_size={n_traj}",
        "online_learning.trajectory_length=100",
        "online_learning.window_size=5",
        "online_learning.stride=5",
        f"online_learning.eta_increment={eta}",
        f"online_learning.max_eta={eta}",
        "online_learning.eta_update_interval_windows=5",
        "online_learning.max_iterations=1",
        "kalman_filter.measurement_noise_std_dev=0.125",
        "simulation.load_model=true",
        f"simulation.model_path={CHECKPOINT}",
        f"hydra.run.dir={out_dir}",
        *cfg["overrides"],
    ]
    return cmd


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--n-traj", type=int, default=20)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--triggers", nargs="*", default=list(TRIGGERS.keys()))
    parser.add_argument("--etas", nargs="*", type=float, default=ETAS)
    args = parser.parse_args()

    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    failures: list[tuple[str, float, int]] = []
    for trigger in args.triggers:
        for eta in args.etas:
            cmd = build_command(trigger, eta, args.n_traj)
            logger.info("[%s, eta=%.2f] %s", trigger, eta, shlex.join(cmd))
            if args.dry_run:
                continue
            rc = subprocess.run(cmd, cwd=ROOT).returncode
            if rc != 0:
                failures.append((trigger, eta, rc))

    if failures:
        logger.error("Failures: %s", failures)
        return 1
    logger.info("All cells completed successfully.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [x] **Step 2.2：dry-run 自检**

```bash
.venv/Scripts/python.exe scripts/run_trigger_validation.py --dry-run --n-traj 2
```

Expected: 12 行命令打印（3 trigger × 4 eta），无异常退出。

实际记录（2026-04-29）：按评审修正，使用 `--dry-run --n-traj 5`；成功打印 12 个 cell。脚本顶部 `PIPELINE_ENTRY = "run.pipeline.training.train"`，该入口由 `rg -n "@hydra\.main|hydra\.main" . -g "*.py"` 确认；实际执行模式记录为 `direct_simulation`，因为 `Used_for_paper` 配置仍是 legacy shape，不适合直接喂给该 Hydra `_target_` 入口。

- [x] **Step 2.3：先用 N=5 跑一轮 smoke 确认入口和输出路径都对**

```bash
.venv/Scripts/python.exe scripts/run_trigger_validation.py --n-traj 2
```

Expected: 12 个 sub-run 全部退出 0；`outputs/trigger_validation_20260429/` 下生成 12 个子目录，每个含 `online_learning_results.json` 或等价 summary。

如果入口模块路径不同，看 `run/pipeline/` 下实际可执行入口（pipeline_run.py 是模块，不是 CLI 入口；真正入口可能在 `run/pipeline/online_learning_pipeline.py` 或 `run/pipeline/training/online_learning.py`，按当前仓库实际调整 `PIPELINE_ENTRY` 常量）。

实际记录（2026-04-29/30，WSL `.venv-wsl`）：

```bash
.venv-wsl/bin/python scripts/run_trigger_validation.py --n-traj 5 \
  > outputs/trigger_validation_20260429/n5_smoke.log 2>&1
```

结果：退出码 0；12/12 cell 均生成 `summary.json` 与 `online_learning_results.json`。N=5 smoke 摘要如下（最终结论仍需 N=20）：

| trigger | eta | first_online_windows | false alarm | detect | mean delay |
| --- | ---: | --- | ---: | ---: | ---: |
| sigma_y_sq | 0.0 | `[None, None, None, None, None]` | 0/5 | - | - |
| sigma_y_sq | 0.3 | `[7, 9, 18, 10, 9]` | 0/5 | 5/5 | 5.6 |
| sigma_y_sq | 0.6 | `[7, 9, 7, 6, 6]` | 0/5 | 5/5 | 2.0 |
| sigma_y_sq | 1.0 | `[6, 6, 9, 8, 6]` | 0/5 | 5/5 | 2.0 |
| time_to_learn | 0.0 | `[6, 6, 6, 6, 6]` | 5/5 | - | - |
| time_to_learn | 0.3 | `[6, 6, 6, 6, 6]` | 0/5 | 5/5 | 1.0 |
| time_to_learn | 0.6 | `[6, 6, 6, 6, 6]` | 0/5 | 5/5 | 1.0 |
| time_to_learn | 1.0 | `[6, 6, 6, 6, 6]` | 0/5 | 5/5 | 1.0 |
| whitened_cusum | 0.0 | `[None, None, 13, None, None]` | 1/5 | - | - |
| whitened_cusum | 0.3 | `[18, 14, 10, 14, None]` | 0/5 | 4/5 | 9.0 |
| whitened_cusum | 0.6 | `[8, 16, 12, 6, 7]` | 0/5 | 5/5 | 4.8 |
| whitened_cusum | 1.0 | `[9, 7, 8, 6, 7]` | 0/5 | 5/5 | 2.4 |

注意：`whitened_cusum` no-drift 在 N=5 smoke 中出现 1/5 late false trigger（window 13）。这不是最终验收结论，但 N=20 长跑后必须重点复核 no-drift 误触发率是否满足 `≤1/20`。

- [x] **Step 2.4：跑完整 N=20**

```bash
.venv/Scripts/python.exe scripts/run_trigger_validation.py --n-traj 20
```

Expected: 12 个 sub-run 全部 success；总耗时按 plan_26Apr §⚖️.2 单条 trajectory 经验值（30-90 秒）估算，总 2-6 小时。可在 tmux/nohup 中后台跑。

实际记录（2026-04-29/30，WSL `.venv-wsl`）：

```bash
.venv-wsl/bin/python scripts/run_trigger_validation.py --n-traj 20 \
  > outputs/trigger_validation_20260429/n20.log 2>&1
```

结果：退出码 0；12/12 cell 均完成到 `trajectory 20/20`，并覆盖更新 `outputs/trigger_validation_20260429/<trigger>/eta_*/summary.json`。

N=20 摘要：

| trigger | eta | first_online_windows | false alarm | detect | mean delay |
| --- | ---: | --- | ---: | ---: | ---: |
| sigma_y_sq | 0.0 | `[None, None, None, None, None, None, 15, None, None, None, None, None, None, 11, None, None, None, None, None, None]` | 2/20 | - | - |
| sigma_y_sq | 0.3 | `[7, 9, 18, 10, 9, 7, 15, 9, 6, 11, 7, 8, 6, 8, 7, 12, 9, 17, 14, 15]` | 0/20 | 20/20 | 5.20 |
| sigma_y_sq | 0.6 | `[7, 9, 7, 6, 6, 7, 7, 6, 6, 12, 6, 6, 6, 6, 9, 6, 8, 13, 6, 6]` | 0/20 | 20/20 | 2.25 |
| sigma_y_sq | 1.0 | `[6, 6, 9, 8, 6, 8, 7, 7, 6, 6, 9, 10, 6, 6, 6, 6, 7, 9, 6, 7]` | 0/20 | 20/20 | 2.05 |
| time_to_learn | 0.0 | `[6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6]` | 20/20 | - | - |
| time_to_learn | 0.3 | `[6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6]` | 0/20 | 20/20 | 1.00 |
| time_to_learn | 0.6 | `[6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6]` | 0/20 | 20/20 | 1.00 |
| time_to_learn | 1.0 | `[6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6]` | 0/20 | 20/20 | 1.00 |
| whitened_cusum | 0.0 | `[None, None, 13, None, None, None, None, None, None, 11, None, None, None, None, None, None, None, None, None, None]` | 2/20 | - | - |
| whitened_cusum | 0.3 | `[18, 14, 10, 14, None, 9, 8, 8, 11, 9, 13, 7, 9, 14, 13, 14, 14, 7, 10, 8]` | 0/20 | 19/20 | 6.05 |
| whitened_cusum | 0.6 | `[8, 16, 12, 6, 7, 7, 8, None, 12, None, 12, 14, 9, 15, 9, 6, 10, 13, 10, None]` | 0/20 | 17/20 | 5.24 |
| whitened_cusum | 1.0 | `[9, 7, 8, 6, 7, None, 12, 9, 9, 7, 6, 8, 11, 7, 7, 10, 6, 9, 8, 10]` | 0/20 | 19/20 | 3.21 |

验收判断：whitened CUSUM 的 eta=1.0 检测率/延迟通过，eta=0.6 检测率通过；no-drift false alarm = 2/20，未达到 `≤1/20` 门槛。

- [ ] **Step 2.5：commit driver script**

```bash
git add scripts/run_trigger_validation.py
git commit -m "feat(scripts): N=20 trigger validation driver

Drives all (3 triggers x 4 eta) cells of the closed-loop comparison with
dataset_size=20, pretrained checkpoint, R_obs=0.125, dumping each cell to
outputs/trigger_validation_20260429/<trigger>/eta_<eta>/ for downstream
aggregation.

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

### Task 3：聚合脚本与 paper 对比表

**Files:**
- Create: `scripts/aggregate_trigger_results.py`
- Create: `tests/scripts/test_aggregate_trigger_results.py`

- [x] **Step 3.1：写聚合脚本的测试**

```python
# tests/scripts/test_aggregate_trigger_results.py
"""Unit tests for the trigger validation aggregator."""
import json
from pathlib import Path

import pytest

from scripts.aggregate_trigger_results import (
    CellMetrics,
    aggregate_cell,
    write_summary_table,
)


def _make_summary(tmp_path: Path, first_online: list, drift_onset: int = 5) -> Path:
    payload = {
        "first_online_windows": first_online,
        "drift_onset_window": drift_onset,
        "trajectory_count": len(first_online),
        "tail5_rmspe_improvement_avg": 0.05,
    }
    p = tmp_path / "online_learning_results.json"
    p.write_text(json.dumps(payload))
    return p


def test_aggregate_no_drift_zero_false_alarms(tmp_path):
    summary = _make_summary(tmp_path, first_online=[None] * 20, drift_onset=5)
    metrics = aggregate_cell(summary, eta=0.0, trigger="whitened_cusum")
    assert metrics.false_alarm_rate == 0.0
    assert metrics.detect_rate is None
    assert metrics.n_trajectories == 20


def test_aggregate_strong_drift_full_detection(tmp_path):
    first_online = [6, 7, 6, 8, 9, 6, 7, 8, 6, 7, 9, 8, 6, 7, 10, 6, 7, 8, None, None]
    summary = _make_summary(tmp_path, first_online=first_online, drift_onset=5)
    metrics = aggregate_cell(summary, eta=1.0, trigger="whitened_cusum")
    assert metrics.detect_rate == pytest.approx(18 / 20)
    assert metrics.false_alarm_rate == 0.0
    expected_delay = sum(w - 5 for w in first_online if w is not None and w >= 5) / 18
    assert metrics.mean_detection_delay == pytest.approx(expected_delay)


def test_aggregate_pre_drift_false_alarms(tmp_path):
    first_online = [2, 3, None, 6, None, None]
    summary = _make_summary(tmp_path, first_online=first_online, drift_onset=5)
    metrics = aggregate_cell(summary, eta=0.6, trigger="time_to_learn")
    assert metrics.false_alarm_rate == pytest.approx(2 / 6)
    assert metrics.detect_rate == pytest.approx(1 / 6)


def test_write_summary_table(tmp_path):
    cells = [
        CellMetrics(
            trigger="time_to_learn", eta=0.0, n_trajectories=20,
            false_alarm_rate=0.0, detect_rate=None,
            mean_detection_delay=None, tail5_improve=None,
        ),
        CellMetrics(
            trigger="whitened_cusum", eta=1.0, n_trajectories=20,
            false_alarm_rate=0.0, detect_rate=0.95,
            mean_detection_delay=2.1, tail5_improve=0.12,
        ),
    ]
    csv_path = tmp_path / "summary.csv"
    md_path = tmp_path / "summary.md"
    write_summary_table(cells, csv_path, md_path)
    csv_text = csv_path.read_text()
    header = csv_text.splitlines()[0]
    assert "trigger" in header and "eta" in header and "n_trajectories" in header
    assert "whitened_cusum,1.0,20" in csv_text
    md_text = md_path.read_text()
    assert "Trigger" in md_text and "False Alarm" in md_text
```

- [ ] **Step 3.2：跑测试确认失败**

```bash
.venv/Scripts/python.exe -m pytest tests/scripts/test_aggregate_trigger_results.py -v
```

Expected: ImportError: cannot import name 'CellMetrics'.

实际记录（2026-04-29/30）：未单独保留 fail-first 运行；直接实现脚本后运行通过。

- [x] **Step 3.3：实现 `aggregate_trigger_results.py`**

```python
# scripts/aggregate_trigger_results.py
"""Aggregate outputs/trigger_validation_*/ summary.json into CSV + Markdown table.

Usage:
    python scripts/aggregate_trigger_results.py \
        --root outputs/trigger_validation_20260429 \
        --csv plan/plan_29Apr/summary.csv \
        --md  plan/plan_29Apr/summary.md
"""
from __future__ import annotations

import argparse
import csv
import json
import logging
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


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
    payload = json.loads(summary_path.read_text())
    first_online = payload["first_online_windows"]
    drift_onset = int(payload.get("drift_onset_window", 5))
    n = len(first_online)

    pre_drift = sum(1 for w in first_online if w is not None and w < drift_onset)
    detected = sum(1 for w in first_online if w is not None and w >= drift_onset)
    delays = [w - drift_onset for w in first_online if w is not None and w >= drift_onset]

    false_alarm_rate = pre_drift / n if n > 0 else 0.0

    if eta == 0.0:
        detect_rate: Optional[float] = None
        mean_delay: Optional[float] = None
    else:
        detect_rate = detected / n if n > 0 else 0.0
        mean_delay = (sum(delays) / len(delays)) if delays else None

    return CellMetrics(
        trigger=trigger,
        eta=eta,
        n_trajectories=n,
        false_alarm_rate=false_alarm_rate,
        detect_rate=detect_rate,
        mean_detection_delay=mean_delay,
        tail5_improve=payload.get("tail5_rmspe_improvement_avg"),
    )


def discover_cells(root: Path) -> list[tuple[Path, float, str]]:
    cells: list[tuple[Path, float, str]] = []
    for trigger_dir in sorted(root.iterdir()):
        if not trigger_dir.is_dir():
            continue
        trigger_name = trigger_dir.name
        for eta_dir in sorted(trigger_dir.iterdir()):
            if not eta_dir.name.startswith("eta_"):
                continue
            eta = float(eta_dir.name[len("eta_"):].replace("p", "."))
            for summary in eta_dir.rglob("online_learning_results.json"):
                cells.append((summary, eta, trigger_name))
                break
    return cells


def write_summary_table(cells: list[CellMetrics], csv_path: Path, md_path: Path) -> None:
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(asdict(cells[0]).keys()) if cells else [
        "trigger", "eta", "n_trajectories", "false_alarm_rate",
        "detect_rate", "mean_detection_delay", "tail5_improve",
    ]
    with csv_path.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fieldnames)
        w.writeheader()
        for c in cells:
            w.writerow(asdict(c))

    lines = [
        "| Trigger | eta | N | False Alarm | Detect | Mean Delay (w) | Tail5 Improve |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for c in cells:
        def fmt(x, p=3):
            return "—" if x is None else f"{x:.{p}f}"
        lines.append(
            f"| {c.trigger} | {c.eta:.2f} | {c.n_trajectories} | "
            f"{c.false_alarm_rate:.3f} | {fmt(c.detect_rate)} | "
            f"{fmt(c.mean_detection_delay, 2)} | {fmt(c.tail5_improve, 4)} |"
        )
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text("\n".join(lines) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--csv", type=Path, required=True)
    parser.add_argument("--md", type=Path, required=True)
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(message)s")
    found = discover_cells(args.root)
    if not found:
        logger.error("No summary.json discovered under %s", args.root)
        return 1
    cells = [aggregate_cell(p, eta, trigger) for p, eta, trigger in found]
    write_summary_table(cells, args.csv, args.md)
    logger.info("Wrote %s and %s (n_cells=%d)", args.csv, args.md, len(cells))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [x] **Step 3.4：跑测试确认通过**

```bash
.venv/Scripts/python.exe -m pytest tests/scripts/test_aggregate_trigger_results.py -v
```

Expected: 4 passed.

实际结果（2026-04-29/30）：`tests/scripts/test_aggregate_trigger_results.py` 为 5 passed（额外覆盖 eta=0 late trigger 也应计入 false alarm）。

- [x] **Step 3.5：在真实数据上跑聚合**

```bash
.venv/Scripts/python.exe scripts/aggregate_trigger_results.py \
  --root outputs/trigger_validation_20260429 \
  --csv plan/plan_29Apr/summary.csv \
  --md  plan/plan_29Apr/summary.md
```

Expected: 12 行 CSV（3 trigger × 4 eta）+ 同行数的 markdown 表。

实际结果（2026-04-29/30）：先基于 N=5 smoke 生成表格；N=20 完成后已用同一命令覆盖更新 `plan/plan_29Apr/summary.csv` 与 `plan/plan_29Apr/summary.md`，共 12 行。

- [ ] **Step 3.6：commit**

```bash
git add scripts/aggregate_trigger_results.py tests/scripts/test_aggregate_trigger_results.py plan/plan_29Apr/summary.csv plan/plan_29Apr/summary.md
git commit -m "feat(scripts): aggregate trigger validation results into CSV + Markdown

Aggregator discovers outputs/trigger_validation_*/<trigger>/eta_*/online_learning_results.json
and computes per-cell false-alarm rate, detection rate, mean detection delay,
and tail-5 RMSPE improvement. Eta=0.0 cells report only false-alarm rate.

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

### Task 4：检测率/延迟/误触发率图

**Files:**
- Create: `scripts/plot_trigger_validation.py`

- [x] **Step 4.1：实现绘图脚本**

```python
# scripts/plot_trigger_validation.py
"""Plot detection rate, false alarm, and mean delay vs eta from the aggregated CSV."""
from __future__ import annotations

import argparse
import csv
import logging
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt

logger = logging.getLogger(__name__)


def load_rows(csv_path: Path) -> list[dict]:
    with csv_path.open() as fh:
        return list(csv.DictReader(fh))


def _f(x: str) -> float | None:
    if x == "" or x == "None":
        return None
    return float(x)


def plot_detect_rate(rows: list[dict], out_path: Path) -> None:
    by_trigger: dict[str, list[tuple[float, float]]] = defaultdict(list)
    for r in rows:
        eta = float(r["eta"])
        rate = _f(r["detect_rate"])
        if eta == 0.0 or rate is None:
            continue
        by_trigger[r["trigger"]].append((eta, rate))
    fig, ax = plt.subplots(figsize=(5.5, 3.5))
    for trigger, pts in sorted(by_trigger.items()):
        pts.sort()
        xs, ys = zip(*pts)
        ax.plot(xs, ys, marker="o", label=trigger)
    ax.set_xlabel(r"drift magnitude $\eta$")
    ax.set_ylabel("detection rate")
    ax.set_ylim(0, 1.05)
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=180)
    plt.close(fig)
    logger.info("Wrote %s", out_path)


def plot_false_alarm(rows: list[dict], out_path: Path) -> None:
    triggers = sorted({r["trigger"] for r in rows})
    rates = []
    for t in triggers:
        match = [r for r in rows if r["trigger"] == t and float(r["eta"]) == 0.0]
        rates.append(float(match[0]["false_alarm_rate"]) if match else 0.0)
    fig, ax = plt.subplots(figsize=(5.0, 3.0))
    ax.bar(triggers, rates)
    ax.set_ylabel("no-drift false alarm rate")
    ax.set_ylim(0, max(rates + [0.05]) * 1.4 + 0.01)
    ax.axhline(0.05, color="red", linestyle="--", label="5% target")
    ax.legend()
    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=180)
    plt.close(fig)
    logger.info("Wrote %s", out_path)


def plot_delay(rows: list[dict], out_path: Path) -> None:
    by_trigger: dict[str, list[tuple[float, float]]] = defaultdict(list)
    for r in rows:
        eta = float(r["eta"])
        delay = _f(r["mean_detection_delay"])
        if eta == 0.0 or delay is None:
            continue
        by_trigger[r["trigger"]].append((eta, delay))
    fig, ax = plt.subplots(figsize=(5.5, 3.5))
    for trigger, pts in sorted(by_trigger.items()):
        pts.sort()
        xs, ys = zip(*pts)
        ax.plot(xs, ys, marker="s", label=trigger)
    ax.set_xlabel(r"drift magnitude $\eta$")
    ax.set_ylabel("mean detection delay (windows)")
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=180)
    plt.close(fig)
    logger.info("Wrote %s", out_path)


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
```

- [x] **Step 4.2：在真实 CSV 上跑**

```bash
.venv/Scripts/python.exe scripts/plot_trigger_validation.py \
  --csv plan/plan_29Apr/summary.csv \
  --out-dir plan/plan_29Apr/figures
```

Expected: `plan/plan_29Apr/figures/` 下生成 3 个 PNG，每张 ≥ 50 KB。

实际结果（2026-04-29/30，N=20 CSV）：

```text
detect_rate_vs_eta.png 53K
false_alarm_no_drift.png 57K
delay_vs_eta.png 80K
```

三张图已由 N=20 `summary.csv` 覆盖更新。

追加轻量回归（2026-04-29/30，WSL `.venv-wsl`）：

```bash
.venv-wsl/bin/python -m pytest \
  tests/online_learning/test_drift_trigger.py \
  tests/integration/test_whitened_trigger_smoke.py \
  tests/online_learning/test_validate_null_distribution.py \
  tests/scripts/test_aggregate_trigger_results.py \
  -v --tb=short
```

结果：`25 passed, 2 warnings`。

- [ ] **Step 4.3：commit**

```bash
git add scripts/plot_trigger_validation.py plan/plan_29Apr/figures/
git commit -m "feat(scripts): plot detection rate / false alarm / delay for trigger validation

Generates three PNGs from plan/plan_29Apr/summary.csv:
- detect_rate_vs_eta.png: per-trigger detection rate at eta in {0.3, 0.6, 1.0}
- false_alarm_no_drift.png: bar chart of no-drift false-alarm rate vs 5% target
- delay_vs_eta.png: mean detection delay per trigger vs eta

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

### Task 5：写有效性结论摘要

**Files:**
- Create: `plan/plan_29Apr/results.md`

- [x] **Step 5.1：先从 summary.csv 真实读数**

```bash
.venv/Scripts/python.exe -c "
import csv
rows = list(csv.DictReader(open('plan/plan_29Apr/summary.csv')))
for r in rows:
    print(r['trigger'], r['eta'], 'FA=', r['false_alarm_rate'], 'D=', r['detect_rate'], 'delay=', r['mean_detection_delay'])
"
```

把输出保留下来，准备填入 results.md。

- [x] **Step 5.2：写 `plan/plan_29Apr/results.md`**

值用 Step 5.1 输出的真实数据替换占位 `<X>`：

```markdown
# 白化新息触发器有效性验证结果

> 数据来源：`plan/plan_29Apr/summary.csv` + `plan/plan_29Apr/figures/`
> Checkpoint：`checkpoints/saved_SubspaceNet_trained_20260224_180720.pt`
> Calibration：`R_obs=0.125, p_fa=1e-6, b_offset=24`（whitened CUSUM）
> N = 20 trajectories per cell

## 1. 主要结论

在 N=20 的统计扩展下，calibrated whitened CUSUM 在闭环 SubspaceNet+EKF 管线中达到：

- no-drift 误触发率 = `<X>%`（5% 目标）/ `time_to_learn` = `<X>%` / `sigma_y_sq_retuned` = `<X>%`
- 强漂移 eta=1.0 检测率 = `<X>/20` / 平均延迟 = `<X>` 个 window
- 中等漂移 eta=0.6 检测率 = `<X>/20` / 平均延迟 = `<X>` 个 window
- 弱漂移 eta=0.3 检测率 = `<X>/20`

[结论 1-2 句话陈述：whitened CUSUM 是否达到本计划「关键约定」中的统计验收门槛]

## 2. 三触发器对比表

[把 plan/plan_29Apr/summary.md 的 markdown 表整段复制到这里]

## 3. 图

![Detection rate vs eta](figures/detect_rate_vs_eta.png)

![False alarm under no-drift](figures/false_alarm_no_drift.png)

![Mean detection delay vs eta](figures/delay_vs_eta.png)

## 4. 讨论与局限

- Checkpoint：当前使用 best-available `180720.pt`，未恢复 Konstantino 2026 论文原始 09-16 checkpoint（无法从作者公开仓库获取，详见 plan_26Apr §8）。
- Calibration：`R_obs=0.125 / b_offset=24` 是闭环 best scalar；plan_26Apr §🧭.5 已确认残余 `source[0]` outlier 占主导，未在本验证中解决。
- 弱漂移：eta=0.3 在当前 calibration 下检测率 < 强漂移，符合理论预期（CUSUM ARL 对小偏移更慢）。
- N=20 的 binomial 95% CI 宽度约 ±20% 绝对值，更高精度需 N≥100。

## 5. 可重复性

```bash
# 1. 跑实验
python scripts/run_trigger_validation.py --n-traj 20

# 2. 聚合
python scripts/aggregate_trigger_results.py \
  --root outputs/trigger_validation_20260429 \
  --csv plan/plan_29Apr/summary.csv \
  --md  plan/plan_29Apr/summary.md

# 3. 出图
python scripts/plot_trigger_validation.py \
  --csv plan/plan_29Apr/summary.csv \
  --out-dir plan/plan_29Apr/figures
```
```

实际记录（2026-04-29/30）：已创建 `plan/plan_29Apr/results.md`，结论写明 whitened CUSUM 检测有效，但 no-drift false alarm = 2/20，未达到计划门槛 `≤1/20`。

- [ ] **Step 5.3：commit**

```bash
git add plan/plan_29Apr/results.md
git commit -m "docs(plan_29Apr): record whitened CUSUM trigger validation results at N=20

Three-trigger head-to-head on closed-loop SubspaceNet+EKF with
R_obs=0.125 / b_offset=24 calibration:
- no-drift false alarm rates and detection rates per trigger
- detection rate vs eta and delay vs eta figures
- discussion of remaining source[0] outlier and N=20 statistical width

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

### Task 6：最终 push + 自检

- [ ] **Step 6.1：完整 push**

```bash
git push origin feature/whiten_innov
```

- [x] **Step 6.2：跑全套既有 pytest 确认无回归**

```bash
.venv/Scripts/python.exe -m pytest tests/online_learning/ tests/integration/test_whitened_trigger_smoke.py tests/scripts/ -v --tb=short
```

Expected: 全部 PASS（约 24 用例：drift_trigger 14 + smoke 3 + metrics_aggregate 3 + validate_null 4 + aggregate_trigger 4）。

实际结果（2026-04-29/30，WSL `.venv-wsl`）：

```text
.venv-wsl/bin/python -m pytest tests/online_learning/ \
  tests/integration/test_whitened_trigger_smoke.py \
  tests/scripts/ -v --tb=short
37 passed, 2 warnings
```

- [ ] **Step 6.3：人工审阅 results.md**

打开 `plan/plan_29Apr/results.md`，逐项核对：

- 第 1 节"主要结论"里的数字是否与 `summary.csv` 完全一致（不要四舍五入到与 CSV 不同的精度）
- 三张图是否齐全且非空（每张 ≥ 50 KB）
- 「讨论与局限」是否如实承认 N=20 的 CI 宽度和 source[0] 残余 outlier

如发现不一致，回到 Step 5.1 修正后重新 commit。

---

## 验收清单

### 静态
- [ ] `feature/whiten_innov` 推到远端，含 `fix(pipeline)` / `feat(config)` × 2 / `docs(plan)` / `feat(scripts)` × 3 / `docs(plan_29Apr)` 共 7+ 个 commit
- [ ] `scripts/run_trigger_validation.py`、`scripts/aggregate_trigger_results.py`、`scripts/plot_trigger_validation.py` 三个脚本全部可独立运行（带 `--help` 输出）

### 测试
- [ ] `pytest tests/online_learning/ tests/integration/test_whitened_trigger_smoke.py tests/scripts/ -v` 全绿

### 数据
- [ ] `plan/plan_29Apr/summary.csv` 有 12 行（3 trigger × 4 eta）
- [ ] `plan/plan_29Apr/summary.md` 行数 = 14（标题+分隔+12）
- [ ] `plan/plan_29Apr/figures/` 含 3 个 PNG，每张 ≥ 50 KB

### 验收门槛（基于 N=20）
- [ ] `whitened_cusum` 在 no-drift 下 false_alarm_rate ≤ 0.05
- [ ] `whitened_cusum` 在 eta=1.0 下 detect_rate ≥ 0.90 且 mean_detection_delay ≤ 5
- [ ] `whitened_cusum` 在 eta=0.6 下 detect_rate ≥ 0.60
- [ ] `whitened_cusum` 在每个 eta 下的 detect_rate ≥ `sigma_y_sq_retuned` 在同 eta 下的 detect_rate
- [ ] 报告 `whitened_cusum` 与 `time_to_learn`（已知 oracle 触发）的差距，无强制门槛

### 文档
- [ ] `plan/plan_29Apr/results.md` 各节数字、图引用、可重复性命令齐全
- [ ] 文末「讨论与局限」如实陈述 checkpoint 不是原作者 09-16 而是 `180720.pt`

---

## 自检备忘

撰写完后做了一遍自检：

1. **Spec coverage**：用户的目标"验证触发器有效"对应 Task 3 的对比表 + Task 4 的图 + Task 5 的结论文档。N=20 的统计样本量在 Task 2 强制。三触发器同条件对比在 Task 2 强制。
2. **Placeholder scan**：所有 step 都有具体命令、具体代码、具体期望输出。`<TAU>` 在 Task 1.4 是有意的"由前一步决定"占位，不是 TBD。Task 5 结论文档里的 `<X>` 同理，依赖 Task 3 的真实 CSV 输出。
3. **Type consistency**：`CellMetrics` 在 test 与实现里一致；`aggregate_cell(summary_path, eta, trigger)` 三参数签名在 test 与实现一致；`first_online_windows` 在 driver、aggregator、test 里都使用同一含义（窗口索引或 None）。
4. **复用 vs 新增**：所有触发器代码、calibration 参数、checkpoint 路径都从 plan_26Apr 已有资产取，新代码集中在 3 个 scripts/ 工具脚本与对应单元测试。

如果实际跑 Task 2 时入口模块路径与 `run.pipeline.online_learning_pipeline` 不一致，按当前仓库实际可执行入口替换 `PIPELINE_ENTRY` 常量；这是已知的"environment-specific"项，不影响计划骨架。
