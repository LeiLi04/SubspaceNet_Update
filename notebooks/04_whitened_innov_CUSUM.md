<!-- Generated from notebooks/04_whitened_innov_CUSUM.ipynb. Code cells are omitted; generated figures are linked from notebooks/figures/. -->

# Whitened Innovation CUSUM for Drift-Triggered Online Adaptation

**Purpose.** Summarize what we did over the last two days: replacing hard-coded/manual drift triggers with a covariance-aware whitened innovation CUSUM trigger in the SubspaceNet+EKF online-learning pipeline.

**Main result.** The trigger detects drift effectively in N=20 validation, but the current calibration still has 2/20 no-drift false alarms, so it is not yet a final paper configuration.

**PPT takeaway.** The contribution is a statistically interpretable trigger design and validation workflow, not a claim that the current setting already beats every manual baseline.

---
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

---
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

---
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

---
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

---
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

---
Figure captions for PPT:

1. **Detection rate.** Whitened CUSUM reaches 95% detection at `eta=1.0` and 85% at `eta=0.6`, showing that the trigger is effective under moderate-to-strong drift.
2. **False alarm.** The current calibration gives 2/20 no-drift false alarms, above the 5% target; this is the main remaining calibration issue.
3. **Detection delay.** Strong drift is detected within 3.21 windows on average, passing the <=5 window delay target.

## Figures

### Detection rate under different drift magnitudes

![Detection rate under different drift magnitudes](figures/whitened_cusum_detect_rate.png)

### No-drift false alarm vs 5% target

![No-drift false alarm vs 5% target](figures/whitened_cusum_false_alarm.png)

### Mean detection delay in windows

![Mean detection delay in windows](figures/whitened_cusum_delay.png)

---
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

---
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

---
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
