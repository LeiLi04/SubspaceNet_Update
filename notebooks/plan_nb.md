# `04_whitened_innov_CUSUM.ipynb` 写作计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:executing-plans` to implement this plan task-by-task. The target output is a completed Jupyter notebook, not another planning document.

**Goal:** 把 2026-04-26 到 2026-04-30 的 whitened innovation CUSUM 工作整理成一个可用于 PPT 展示的 notebook，回答四个问题：打算做什么、怎么做、做完有什么结果、相比原本手动阈值有什么好处。

**Architecture:** `notebooks/04_whitened_innov_CUSUM.ipynb` 应该是“展示型研究 notebook”，不是代码开发日志。它以 Markdown 叙事为主，少量 code cell 用来读取 `summary.csv`、显示表格和插入已有图。每个主要 section 最后都要给出一句 `PPT takeaway`，方便后续直接搬到 slides。

**Tech Stack:** Jupyter Notebook, Markdown, Python 3, pandas, matplotlib/IPython display, existing artifacts under `plan/plan_26Apr`, `plan/plan_29Apr`, `plan/plan_29Apr/figures`.

---

## 0. 重要边界

当前 `notebooks/04_whitened_innov_CUSUM.ipynb` 里已经被写入了一版错误方向的内容：它更像“如何写 notebook 的工程计划”。执行本计划时，第一步要把它改成真正的“研究展示 notebook”。

不要做这些事：

- 不要把 notebook 写成 task checklist。
- 不要重新跑 N=20 online-learning 实验。
- 不要声称 whitened CUSUM 在当前数据下 detection power 优于 `sigma_y_sq`。
- 不要隐藏 no-drift false alarm 没过门槛这件事。
- 不要把 `time_to_learn` 的 no-drift false alarm 当成公平比较；它是固定窗口 oracle/reference baseline。

必须做这些事：

- 明确说明原始 `sigma_y^2 > tau_sigma` 是手动阈值，迁移到新部署场景时缺少统计解释。
- 明确说明 whitened innovation 的核心好处是把 raw innovation energy 标准化成 covariance-aware statistic。
- 明确说明最终 N=20 结果是 `4/6` 门槛通过，当前 calibration 不能直接定稿论文。
- 明确说明 PPT framing：贡献点是“statistically interpretable trigger design + calibration workflow”，不是“全面超过手动阈值 baseline”。

---

## 1. Source Assets

执行 notebook 写作时只读取这些现有结果，不重新生成长实验：

| 文件 | 用途 |
| --- | --- |
| `plan/plan_26Apr/findings.md` | 说明任务起点：仓库有 SubspaceNet+EKF+online learning，但 drift trigger 主要还是 `time_to_learn`。 |
| `plan/plan_26Apr/plan_whiten_innov.md` | 说明方法动机：白化新息、chi-square null、Page-CUSUM。 |
| `plan/plan_26Apr/IMPLEMENTATION_NOTES.md` | 说明实现和 calibration 过程。 |
| `plan/plan_29Apr/results.md` | 说明最终 N=20 结果、局限和验收门槛。 |
| `plan/plan_29Apr/summary.csv` | notebook 里读取成结果表。 |
| `plan/plan_29Apr/figures/detect_rate_vs_eta.png` | PPT 图：检测率 vs drift magnitude。 |
| `plan/plan_29Apr/figures/false_alarm_no_drift.png` | PPT 图：no-drift false alarm。 |
| `plan/plan_29Apr/figures/delay_vs_eta.png` | PPT 图：mean detection delay。 |
| `src/trainer_module/online_learning_parts/drift_trigger.py` | 说明代码落点：三种 trigger strategy。 |
| `run/conf/Used_for_paper/SineAccel_whitened_cusum_pretrained_calibrated.yaml` | 说明最终验证配置。 |

---

## 1.5 Figure / Visualization Requirements

参考 `$results-analysis` 的 `references/visualization-best-practices.md`，这个 notebook 的图要优先满足 notebook/PPT 展示清晰度；本计划只要求 PNG。

核心规则：

- notebook 可以显示已有 `plan/plan_29Apr/figures/*.png` 作为结果复核；最终在 notebook 中使用重新生成的 PNG。
- 配色使用 colorblind-friendly palette，优先 Okabe-Ito：
  - orange `#E69F00`
  - sky blue `#56B4E9`
  - green `#009E73`
  - blue `#0072B2`
  - vermillion `#D55E00`
  - black `#000000`
- 不要只靠颜色区分曲线；线型和 marker 也要不同。
- 坐标轴必须有完整 label 和单位：`drift magnitude eta`、`detection rate`、`false alarm rate`、`mean detection delay (windows)`。
- false-alarm 图必须画出 `5% target` 虚线，不能隐藏失败门槛。
- detection-rate 图的 y-axis 固定在 `[0, 1.05]`，避免夸大差异。
- 图题和 caption 要说观察结论，不只重复变量名。
- PNG 使用 `dpi=220` 或更高即可；保持图中文字、图例和坐标轴在 notebook/PPT 中清楚可读。

Notebook 里建议输出到：

```text
notebooks/figures/whitened_cusum_detect_rate.png
notebooks/figures/whitened_cusum_false_alarm.png
notebooks/figures/whitened_cusum_delay.png
```

PPT 使用优先级：

1. 直接使用 notebook 生成的 PNG。
2. 如果 PPT 里需要裁剪或二次标注，仍以 PNG 为底图。

---

## 2. Notebook 最终结构

`notebooks/04_whitened_innov_CUSUM.ipynb` 最终建议包含 13 个 cells：

| Cell | 类型 | 标题 | PPT 作用 |
| ---: | --- | --- | --- |
| 1 | Markdown | `# Whitened Innovation CUSUM for Drift-Triggered Online Adaptation` | 标题页 + 一句话结论 |
| 2 | Markdown | `## 1. What were we trying to do?` | 说明目标 |
| 3 | Markdown | `## 2. Why manual thresholding is not enough` | 说明手动 `tau_sigma` 的问题 |
| 4 | Markdown | `## 3. Core idea: whiten the innovation` | 说明白化新息 |
| 5 | Markdown | `## 4. From statistic to trigger: Page-CUSUM` | 说明 CUSUM |
| 6 | Markdown | `## 5. How it was implemented in this repo` | 说明代码结构 |
| 7 | Code | imports + paths | 读取 artifacts |
| 8 | Code | load result table | 展示 N=20 summary |
| 9 | Code | generate notebook-ready figures | 生成 PNG |
| 10 | Code | display figures | 展示三张 PPT 图 |
| 11 | Markdown | `## 6. What results did we get?` | 总结结果 |
| 12 | Markdown | `## 7. Compared with manual thresholding` | 对比好处和限制 |
| 13 | Markdown | `## 8. Final slide message` | PPT 最后一页 |

---

## 3. Task 1: 重写 notebook 标题与总览

**Files:**
- Modify: `notebooks/04_whitened_innov_CUSUM.ipynb`

- [ ] **Step 1.1: 清空当前 notebook 的错误计划内容**

把 `notebooks/04_whitened_innov_CUSUM.ipynb` 改成一个新的有效 notebook。不要保留当前“Notebook Plan / Task checklist”式内容。

验证命令：

```bash
python3 -m json.tool notebooks/04_whitened_innov_CUSUM.ipynb >/tmp/04_whitened_innov_CUSUM.json
```

Expected: exit code 0。

- [ ] **Step 1.2: 写标题 cell**

第一个 Markdown cell 内容：

````markdown
# Whitened Innovation CUSUM for Drift-Triggered Online Adaptation

**Purpose.** Summarize what we did over the last two days: replacing hard-coded/manual drift triggers with a covariance-aware whitened innovation CUSUM trigger in the SubspaceNet+EKF online-learning pipeline.

**Main result.** The trigger detects drift effectively in N=20 validation, but the current calibration still has 2/20 no-drift false alarms, so it is not yet a final paper configuration.

**PPT takeaway.** The contribution is a statistically interpretable trigger design and validation workflow, not a claim that the current setting already beats every manual baseline.
````

---

## 4. Task 2: 写“打算做什么”

**Files:**
- Modify: `notebooks/04_whitened_innov_CUSUM.ipynb`
- Read: `plan/plan_26Apr/findings.md`

- [ ] **Step 2.1: 写目标 cell**

第二个 Markdown cell 内容：

````markdown
## 1. What were we trying to do?

The starting point was a SubspaceNet+EKF online adaptation pipeline for DoA estimation under array-response drift.

Before this task, the repository already had:

| Component | Status |
| --- | --- |
| SubspaceNet DoA estimator | Implemented. |
| EKF downstream tracker | Implemented and already outputs innovation-related quantities. |
| Online adaptation with pseudo-labels | Implemented. |
| Automatic drift trigger | Not fully solved; online learning was still mainly controlled by `time_to_learn`. |

The task was to turn innovation statistics into a real drift trigger:

```text
X_i -> SubspaceNet g_psi(X_i) -> EKF tracker -> innovation y_i
                                      |
                                      +-> drift detection
                                      +-> unsupervised adaptation
```

**PPT takeaway.** The pipeline had the estimator, tracker, and online-learning machinery; the missing piece was a statistically grounded automatic trigger.
````

---

## 5. Task 3: 写“为什么不能只用手动阈值”

**Files:**
- Modify: `notebooks/04_whitened_innov_CUSUM.ipynb`
- Read: `plan/plan_26Apr/findings.md`
- Read: `plan/plan_26Apr/plan_whiten_innov.md`

- [ ] **Step 3.1: 写 manual threshold 问题 cell**

第三个 Markdown cell 内容：

````markdown
## 2. Why manual thresholding is not enough

The original trigger idea monitors a sliding-window innovation energy:

$$
\sigma_y^2(i)=\frac{1}{I}\sum_{j=i-I+1}^{i}\|y_j\|^2
$$

and starts online adaptation when:

$$
\sigma_y^2(i) > \tau_\sigma.
$$

This has three practical problems:

1. **Manual tuning.** `tau_sigma` is a hand-set threshold.
2. **Scale sensitivity.** Raw innovation magnitude depends on EKF uncertainty, measurement noise, SNR, snapshot count, and checkpoint quality.
3. **Weak transferability.** A threshold that works for one drift/noise/checkpoint setting may not be meaningful in another deployment.

**PPT takeaway.** Manual `tau_sigma` can work as an engineering baseline, but it does not provide a portable false-alarm interpretation.
````

---

## 6. Task 4: 写“怎么做：白化新息”

**Files:**
- Modify: `notebooks/04_whitened_innov_CUSUM.ipynb`
- Read: `plan/plan_26Apr/plan_whiten_innov.md`

- [ ] **Step 4.1: 写 whitened innovation 方法 cell**

第四个 Markdown cell 内容：

````markdown
## 3. Core idea: whiten the innovation

The EKF already computes an innovation covariance:

$$
S_i = P_{i|i-1} + R_{obs}.
$$

Instead of thresholding raw innovation energy, we normalize the innovation by this covariance:

$$
c_i = y_i^T S_i^{-1}y_i.
$$

If the no-drift model is well calibrated, this statistic should behave like a chi-square statistic with `M=3` degrees of freedom:

$$
c_i \approx \chi^2(3) \quad \text{under no drift}.
$$

This changes the detection problem from:

```text
How large is the raw residual?
```

to:

```text
How surprising is the residual relative to the EKF uncertainty?
```

**PPT takeaway.** Whitening makes the trigger covariance-aware; the same residual is treated differently when the tracker is uncertain versus confident.
````

---

## 7. Task 5: 写“怎么做：Page-CUSUM”

**Files:**
- Modify: `notebooks/04_whitened_innov_CUSUM.ipynb`
- Read: `plan/plan_26Apr/plan_whiten_innov.md`

- [ ] **Step 5.1: 写 CUSUM trigger cell**

第五个 Markdown cell 内容：

````markdown
## 4. From statistic to trigger: Page-CUSUM

A single large residual can be noisy, so the trigger accumulates persistent evidence:

$$
G_i = \max(0, G_{i-1} + c_i - b).
$$

Online adaptation starts when:

$$
G_i > h.
$$

In this implementation:

| Quantity | Meaning |
| --- | --- |
| `c_i` | whitened innovation statistic |
| `b` | reference value; implemented through `b_offset` |
| `h` | CUSUM threshold derived from target `p_fa` |
| `reset_after_trigger` | resets the accumulator after a trigger |

Final validated candidate:

```yaml
kalman_filter:
  measurement_noise_std_dev: 0.125

online_learning:
  drift_trigger:
    type: whitened_cusum
    p_fa: 1e-6
    dof: 3
    b_offset: 24.0
    reset_after_trigger: true
```

**PPT takeaway.** CUSUM converts whitened innovation into a persistent-drift detector rather than a one-step alarm.
````

---

## 8. Task 6: 写“代码里怎么接进去”

**Files:**
- Modify: `notebooks/04_whitened_innov_CUSUM.ipynb`
- Read: `plan/plan_26Apr/IMPLEMENTATION_NOTES.md`
- Read: `src/trainer_module/online_learning_parts/drift_trigger.py`
- Read: `run/conf/Used_for_paper/SineAccel_whitened_cusum_pretrained_calibrated.yaml`

- [ ] **Step 6.1: 写 implementation map cell**

第六个 Markdown cell 内容：

````markdown
## 5. How it was implemented in this repo

The implementation added a common drift-trigger interface and three trigger strategies:

| Strategy | Role |
| --- | --- |
| `time_to_learn` | Legacy fixed-window/oracle-style reference. |
| `sigma_y_sq` | Manual threshold baseline using innovation energy. |
| `whitened_cusum` | New covariance-aware CUSUM trigger. |

Implementation map:

| Area | File | Purpose |
| --- | --- | --- |
| Trigger strategies | `src/trainer_module/online_learning_parts/drift_trigger.py` | Thresholds, Page-CUSUM, strategy factory. |
| Pipeline wiring | `src/trainer_module/online_learning_parts/pipeline_run.py` | Feeds window-level innovation statistics into the selected trigger. |
| Metrics / diagnostics | `metrics.py` and dump hooks | Expose `c_per_step` and per-source diagnostics. |
| Validation scripts | `scripts/run_trigger_validation.py`, `scripts/aggregate_trigger_results.py`, `scripts/plot_trigger_validation.py` | Run, aggregate, and plot N=20 validation results. |
| Config | `SineAccel_whitened_cusum_pretrained_calibrated.yaml` | Final candidate used for N=20 validation. |

**PPT takeaway.** The contribution is not just a formula; it is wired into the actual closed-loop online-learning path.
````

---

## 9. Task 7: 加载结果表和图

**Files:**
- Modify: `notebooks/04_whitened_innov_CUSUM.ipynb`
- Read: `plan/plan_29Apr/summary.csv`
- Read: `plan/plan_29Apr/figures/*.png`
- Create: `notebooks/figures/*.png`

- [ ] **Step 7.1: 添加 imports/path code cell**

第七个 code cell 内容：

```python
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt
from IPython.display import Image, Markdown, display

ROOT = Path.cwd().resolve()
SUMMARY_CSV = ROOT / "plan" / "plan_29Apr" / "summary.csv"
FIG_DIR = ROOT / "plan" / "plan_29Apr" / "figures"
NOTEBOOK_FIG_DIR = ROOT / "notebooks" / "figures"
NOTEBOOK_FIG_DIR.mkdir(parents=True, exist_ok=True)

assert SUMMARY_CSV.exists(), SUMMARY_CSV
assert FIG_DIR.exists(), FIG_DIR
```

- [ ] **Step 7.2: 添加结果表 code cell**

第八个 code cell 内容：

```python
summary = pd.read_csv(SUMMARY_CSV)
summary
```

- [ ] **Step 7.3: 添加 PPT-friendly table code cell**

如果 notebook 需要更紧凑的表，用这个 code cell 替代原始 `summary` 展示：

```python
ppt_table = summary.copy()
ppt_table["false_alarm_rate"] = ppt_table["false_alarm_rate"].map(lambda x: f"{x:.0%}")
ppt_table["detect_rate"] = ppt_table["detect_rate"].map(lambda x: "-" if pd.isna(x) else f"{x:.0%}")
ppt_table["mean_detection_delay"] = ppt_table["mean_detection_delay"].map(
    lambda x: "-" if pd.isna(x) else f"{x:.2f}"
)
ppt_table["tail5_improve"] = ppt_table["tail5_improve"].map(lambda x: f"{x:.4f}")
ppt_table
```

- [ ] **Step 7.4: 添加 PNG figure generation code cell**

第九个 code cell 内容。这个 cell 重新生成 notebook/PPT 可用的 PNG，不只复用已有 PNG：

```python
OKABE_ITO = {
    "sigma_y_sq": "#0072B2",      # blue
    "time_to_learn": "#E69F00",   # orange
    "whitened_cusum": "#009E73",  # green
}

LINE_STYLES = {
    "sigma_y_sq": ("o", "-"),
    "time_to_learn": ("s", "--"),
    "whitened_cusum": ("^", "-."),
}

DISPLAY_NAMES = {
    "sigma_y_sq": "manual sigma_y_sq",
    "time_to_learn": "fixed time reference",
    "whitened_cusum": "whitened CUSUM",
}

plt.rcParams.update({
    "figure.dpi": 140,
    "savefig.dpi": 220,
    "font.size": 11,
    "axes.labelsize": 11,
    "axes.titlesize": 12,
    "legend.fontsize": 9,
    "axes.spines.top": False,
    "axes.spines.right": False,
})


def save_png(fig, stem: str) -> None:
    fig.savefig(NOTEBOOK_FIG_DIR / f"{stem}.png", bbox_inches="tight")


def plot_detection_rate(df: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(5.8, 3.6))
    plot_df = df[(df["eta"] > 0) & df["detect_rate"].notna()]
    for trigger, group in plot_df.groupby("trigger"):
        group = group.sort_values("eta")
        marker, linestyle = LINE_STYLES[trigger]
        ax.plot(
            group["eta"],
            group["detect_rate"],
            marker=marker,
            linestyle=linestyle,
            linewidth=2.0,
            markersize=6,
            color=OKABE_ITO[trigger],
            label=DISPLAY_NAMES[trigger],
        )
    ax.set_xlabel(r"drift magnitude $\eta$")
    ax.set_ylabel("detection rate")
    ax.set_ylim(0.0, 1.05)
    ax.grid(True, alpha=0.3)
    ax.legend(frameon=False, loc="lower right")
    ax.set_title("Detection rate improves under stronger drift")
    fig.tight_layout()
    save_png(fig, "whitened_cusum_detect_rate")
    return fig


def plot_false_alarm(df: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(5.8, 3.4))
    null_df = df[df["eta"] == 0].copy().sort_values("trigger")
    colors = [OKABE_ITO[t] for t in null_df["trigger"]]
    labels = [DISPLAY_NAMES[t] for t in null_df["trigger"]]
    ax.bar(labels, null_df["false_alarm_rate"], color=colors, edgecolor="black", linewidth=0.7)
    ax.axhline(0.05, color="#D55E00", linestyle="--", linewidth=1.8, label="5% target")
    ax.set_ylabel("no-drift false alarm rate")
    ax.set_ylim(0, 1.08)
    ax.tick_params(axis="x", rotation=12)
    ax.legend(frameon=False)
    ax.set_title("Current whitened CUSUM calibration still exceeds the 5% target")
    fig.tight_layout()
    save_png(fig, "whitened_cusum_false_alarm")
    return fig


def plot_detection_delay(df: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(5.8, 3.6))
    plot_df = df[(df["eta"] > 0) & df["mean_detection_delay"].notna()]
    for trigger, group in plot_df.groupby("trigger"):
        group = group.sort_values("eta")
        marker, linestyle = LINE_STYLES[trigger]
        ax.plot(
            group["eta"],
            group["mean_detection_delay"],
            marker=marker,
            linestyle=linestyle,
            linewidth=2.0,
            markersize=6,
            color=OKABE_ITO[trigger],
            label=DISPLAY_NAMES[trigger],
        )
    ax.set_xlabel(r"drift magnitude $\eta$")
    ax.set_ylabel("mean detection delay (windows)")
    ax.grid(True, alpha=0.3)
    ax.legend(frameon=False)
    ax.set_title("Whitened CUSUM detects strong drift within the target delay")
    fig.tight_layout()
    save_png(fig, "whitened_cusum_delay")
    return fig


fig_detect = plot_detection_rate(summary)
fig_fa = plot_false_alarm(summary)
fig_delay = plot_detection_delay(summary)
plt.show()
```

- [ ] **Step 7.5: 添加图像展示 code cell**

第十个 code cell 内容：

```python
for fig_name, caption in [
    ("whitened_cusum_detect_rate.png", "Detection rate across drift magnitude"),
    ("whitened_cusum_false_alarm.png", "No-drift false alarm with 5% target"),
    ("whitened_cusum_delay.png", "Mean detection delay in windows"),
]:
    fig_path = NOTEBOOK_FIG_DIR / fig_name
    assert fig_path.exists(), fig_path
    display(Markdown(f"### {caption}"))
    display(Image(filename=str(fig_path)))
```

- [ ] **Step 7.6: 添加 figure caption Markdown cell**

在图后面添加一个短 Markdown cell：

````markdown
Figure captions for PPT:

1. **Detection rate.** Whitened CUSUM reaches 95% detection at `eta=1.0` and 85% at `eta=0.6`, showing that the trigger is effective under moderate-to-strong drift.
2. **False alarm.** The current calibration gives 2/20 no-drift false alarms, above the 5% target; this is the main remaining calibration issue.
3. **Detection delay.** Strong drift is detected within 3.21 windows on average, passing the <=5 window delay target.
````

验证：

```bash
python3 -m json.tool notebooks/04_whitened_innov_CUSUM.ipynb >/tmp/04_whitened_innov_CUSUM.json
```

Expected: exit code 0。

执行后检查：

```bash
find notebooks/figures -maxdepth 1 -type f | sort
```

Expected: 至少包含 3 个 `.png` 文件。

---

## 10. Task 8: 写“做完有什么结果”

**Files:**
- Modify: `notebooks/04_whitened_innov_CUSUM.ipynb`
- Read: `plan/plan_29Apr/results.md`
- Read: `plan/plan_29Apr/summary.csv`

- [ ] **Step 8.1: 写 final results cell**

第十个 Markdown cell 内容：

````markdown
## 6. What results did we get?

Validation setting:

| Item | Value |
| --- | --- |
| Checkpoint | `saved_SubspaceNet_trained_20260224_180720.pt` |
| N | 20 trajectories per cell |
| Whitened CUSUM calibration | `R_obs=0.125`, `p_fa=1e-6`, `b_offset=24` |

Key N=20 results:

| Case | Result |
| --- | --- |
| no drift | false alarm = 2/20 = 10%; target was <=1/20 = 5% |
| `eta=0.3` | detect rate = 19/20 = 95%; mean delay = 6.05 windows |
| `eta=0.6` | detect rate = 17/20 = 85%; mean delay = 5.24 windows |
| `eta=1.0` | detect rate = 19/20 = 95%; mean delay = 3.21 windows |

Acceptance gates:

| Gate | Target | Result | Status |
| --- | --- | --- | --- |
| strong drift detection | `eta=1.0`, >=18/20 | 19/20 | pass |
| medium drift detection | `eta=0.6`, >=12/20 | 17/20 | pass |
| weak drift | report only | 19/20 | pass |
| strong drift delay | <=5 windows | 3.21 windows | pass |
| no-drift false alarm | <=1/20 | 2/20 | fail |
| detect rate >= `sigma_y_sq` | same eta | lower at all drift levels | fail |

Overall: 4/6 gates passed.

**PPT takeaway.** Detection effectiveness is credible, but current calibration is not tight enough for a final paper-ready setting.
````

---

## 11. Task 9: 写“相比手动阈值有什么好处”

**Files:**
- Modify: `notebooks/04_whitened_innov_CUSUM.ipynb`
- Read: `plan/plan_29Apr/results.md`

- [ ] **Step 9.1: 写 comparison cell**

第十一个 Markdown cell 内容：

````markdown
## 7. Compared with manual thresholding

The manual `sigma_y_sq` trigger and whitened CUSUM are useful in different ways.

| Dimension | Manual `sigma_y_sq > tau_sigma` | Whitened innovation CUSUM |
| --- | --- | --- |
| Statistic | Raw/sliding-window innovation energy | Covariance-normalized innovation statistic |
| Threshold meaning | Empirical/manual | Linked to false-alarm target through null-distribution framing |
| Transferability | Needs retuning across settings | More interpretable, but still needs calibration when model residuals are heavy-tailed |
| Current N=20 detection power | Strong: 100% at tested drift levels after retuning `tau_sigma=12` | Good but lower: 85-95% |
| Current no-drift false alarm | 2/20 after retuning | 2/20 with current calibration |
| Best current claim | Strong comparator baseline | Better statistical framing and calibration workflow |

Important interpretation:

- Do not claim whitened CUSUM currently detects earlier or more reliably than `sigma_y_sq`.
- Do claim that whitened CUSUM gives a cleaner statistical story: residuals are judged relative to EKF uncertainty, and the trigger has an explicit false-alarm-control framing.
- The current limitation is calibration: real SubspaceNet residuals are heavier-tailed than the ideal chi-square null, so `R_obs` and `b_offset` still need closed-loop tuning.

**PPT takeaway.** The benefit is interpretability and deployment-oriented calibration, not yet raw detection superiority.
````

---

## 12. Task 10: 写 PPT final message

**Files:**
- Modify: `notebooks/04_whitened_innov_CUSUM.ipynb`

- [ ] **Step 10.1: 写最后总结 cell**

第十二个 Markdown cell 内容：

````markdown
## 8. Final slide message

### What we planned

Replace manual/fixed online-learning triggers with a whitened innovation CUSUM trigger that uses EKF uncertainty.

### How we did it

1. Extracted innovation statistics already available in the EKF pipeline.
2. Converted raw residuals into the whitened statistic `c_i = y_i^T S_i^{-1}y_i`.
3. Added a Page-CUSUM trigger with configurable `p_fa`, `b_offset`, and reset behavior.
4. Wired the trigger into the closed-loop SubspaceNet+EKF online-learning pipeline.
5. Validated three triggers over N=20 trajectories: `time_to_learn`, `sigma_y_sq`, and `whitened_cusum`.

### What we found

- Whitened CUSUM detects drift effectively: 95% at `eta=1.0`, 85% at `eta=0.6`, 95% at `eta=0.3`.
- Strong-drift delay passes the target: 3.21 windows.
- Current no-drift false alarm is too high: 2/20 = 10%, target <=5%.
- Retuned `sigma_y_sq` remains a strong detection-power baseline.

### Final framing

This is a promising statistically interpretable trigger and calibration workflow. It is not yet a final paper configuration until false alarm is reduced to <=1/20 or validated with larger N.
````

---

## 13. Task 11: 验证 notebook 是否可展示

**Files:**
- Modify: `notebooks/04_whitened_innov_CUSUM.ipynb`

- [ ] **Step 11.1: JSON 验证**

Run:

```bash
python3 -m json.tool notebooks/04_whitened_innov_CUSUM.ipynb >/tmp/04_whitened_innov_CUSUM.json
```

Expected: exit code 0。

- [ ] **Step 11.2: Notebook smoke execution**

如果当前环境安装了 Jupyter，运行：

```bash
python3 -m jupyter nbconvert \
  --to notebook \
  --execute notebooks/04_whitened_innov_CUSUM.ipynb \
  --output /tmp/04_whitened_innov_CUSUM.executed.ipynb
```

Expected: 所有 code cells 执行通过，尤其是 `summary.csv` 和三张 figure 的路径断言通过。

如果没有 Jupyter，至少运行：

```bash
python3 - <<'PY'
import json
from pathlib import Path

nb = json.loads(Path("notebooks/04_whitened_innov_CUSUM.ipynb").read_text(encoding="utf-8"))
text = "\n".join("".join(cell.get("source", [])) for cell in nb["cells"])
required = [
    "What were we trying to do?",
    "Why manual thresholding is not enough",
    "Core idea: whiten the innovation",
    "What results did we get?",
    "Compared with manual thresholding",
    "Final slide message",
    "2/20 = 10%",
    "4/6 gates passed",
]
missing = [item for item in required if item not in text]
if missing:
    raise SystemExit(f"missing required notebook content: {missing}")
print("notebook content smoke: OK")
PY
```

Expected: `notebook content smoke: OK`。

- [ ] **Step 11.3: PPT readiness 人工检查**

逐项确认：

- notebook 第一屏能说明“这两天做了什么”。
- 手动阈值 `tau_sigma` 的问题讲清楚了。
- whitened innovation / CUSUM 公式讲清楚了。
- 实现落点不是空讲，有文件路径。
- 结果数字与 `plan/plan_29Apr/summary.csv` 一致。
- 图使用 colorblind-friendly palette，且曲线同时用 marker/linestyle 区分。
- 图已经导出 PNG，且在 notebook 中清晰可读。
- false-alarm 图明确画出 5% target line，不能只展示方法排名。
- no-drift false alarm 失败没有被隐藏。
- 对比 `sigma_y_sq` 时没有 oversell。
- 最后一节可以直接变成 1 页 summary slide。

---

## 14. Completion Criteria

完成后，`notebooks/04_whitened_innov_CUSUM.ipynb` 应满足：

1. 是一个完整的研究展示 notebook，不是计划文档。
2. 可以回答：
   - 打算做什么？
   - 为什么要做？
   - 怎么做？
   - 做完有什么结果？
   - 相比原本手动设置阈值有什么好处？
3. 包含 `summary.csv` 结果表。
4. 在 `notebooks/figures/` 生成三张 PNG 图。
5. 结论表述克制：`4/6` 通过，检测有效但 calibration 未定稿。
6. 内容可直接拆成 8-10 页 PPT。
