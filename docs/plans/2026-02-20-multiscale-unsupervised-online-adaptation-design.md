# Multi-Scale Unsupervised Online Adaptation Design

Date: 2026-02-20  
Project: SubspaceNet_Update  
Scope: Strategy draft only (no code changes)

## 1. Goal and Loss Definition

Primary objective: achieve both
1. Fast adaptation under sudden distribution shifts.
2. Stable long-horizon behavior with reduced oscillation and catastrophic drift.

Total loss:

\[
L_t = \lambda_s(t)\cdot L_{\text{short}}(t) + \lambda_l(t)\cdot L_{\text{long}}(t)
\]

- `L_short` (short window, fast response):
  - Window-level innovation/MSIE-style unsupervised term.
  - Emphasizes immediate correction to newly emerged drift.

- `L_long` (long window, stability constraint):
  - Parameter-drift penalty: \(\|\theta_t - \theta_{t-\Delta}\|^2\).
  - Low-frequency innovation consistency penalty (long-window statistics).
  - Emphasizes smoothness and robustness over time.

- Weighting policy (stability-prioritized):
  - Default regime: \(\lambda_l \ge \lambda_s\).
  - Drift regime: temporarily increase \(\lambda_s\), then decay back.

## 2. Integration with Current Pipeline (Design-Level Mapping)

No structural rewrite required; integrate at the current window-training loss path.

- Keep online loop and triggers unchanged.
- Add a new training loss mode (example name): `multiscale_unsupervised`.
- Compute:
  - `L_short` from current short window.
  - `L_long` from long-window stats and parameter-anchor regularization.
  - `L_total` as weighted sum for backprop.

Design-level state to maintain:
- Long-window innovation statistics buffer (queue or EMA).
- Parameter anchor snapshot every `K` windows.

Design-level config extensions:
- `ws`, `wl`
- `lambda_s`, `lambda_l`
- optional dynamic controls: `lambda_boost_on_drift`, `lambda_decay`.

## 3. Weight Scheduling and Anti-Conflict Mechanism

Use event-driven scheduling with smooth rollback:

1. Stable regime:
   - Example: `lambda_s = 0.3`, `lambda_l = 0.7`.
2. Drift-response regime (for `H` windows after trigger):
   - Raise `lambda_s` to `0.6~0.8`, reduce `lambda_l` accordingly.
3. Recovery regime:
   - Decay `lambda_s` back to baseline (linear or exponential).
   - Restore `lambda_l` to baseline.

Protection rules:
- Gradient-conflict gating:
  - If angle between short/long gradients is too large, clip short-loss contribution.
- Update-cap per window:
  - Hard cap on parameter delta magnitude.
- Optional layer strategy:
  - Update head/late layers first when drift is weak.

## 4. Paper Narrative (Dual-Track: Research + Engineering)

Problem:
- Single-timescale unsupervised adaptation often cannot balance fast shift response and long-term stability.

Core idea:
- Multi-scale unsupervised objective with dynamic reweighting between short-term correction and long-term stabilization.

Method:
- \(L_t = \lambda_s(t)L_{\text{short}} + \lambda_l(t)L_{\text{long}}\)
- Event-driven schedule for \(\lambda_s,\lambda_l\).

Why it should work (intuition):
- `L_short` reduces adaptation lag under shift.
- `L_long` controls update variance and drift accumulation.
- Scheduler performs online bias-variance rebalancing.

Claims:
1. Lower window-level volatility than single-scale baselines.
2. Comparable shift-recovery speed to short-window-only methods.
3. Better long-horizon cumulative error behavior.

## 5. Experimental Matrix and Baselines

Baselines:
- `B1`: short-only unsupervised (`L_short`).
- `B2`: long-only stable objective (`L_long`).
- `B3`: dual-window fixed weights (no schedule).
- `B4`: current online-learning default loss.

Proposed variants:
- `M1`: dual-window + event-driven schedule (main method).
- `M2`: remove anti-conflict protection (ablation).
- `M3`: remove smooth recovery schedule (ablation).

Scenarios:
- Abrupt drift (step eta).
- Gradual drift (continuous eta).
- Mixed drift (abrupt + gradual).
- Low-snapshot / low-SNR subsets.

Metrics:
- Stability-first:
  - window-level loss variance
  - P95 fluctuation amplitude
  - max drawdown
- Adaptation:
  - recovery windows after shift
  - avg RMSPE/RMAPE
- Cost:
  - trigger count
  - per-window training time

Expected outcome template:
- `M1` keeps recovery speed near `B1` while significantly reducing volatility and drawdown versus `B1/B4`.

## 6. Open Risks and Mitigations

Risk 1: Short/long objective conflict.
- Mitigation: gradient conflict gating + capped update norm.

Risk 2: Over-tuned schedule.
- Mitigation: small parameterized scheduler family, fixed tuning budget, report robustness grid.

Risk 3: Tracker-induced pseudo-label bias.
- Mitigation: incorporate confidence-aware weighting in next iteration if needed.

## 7. Immediate Next Design Step (No Code Yet)

Produce an implementation plan artifact that maps this strategy to:
1. config schema additions,
2. loss-branch insertion point,
3. state-buffer lifecycle,
4. logging and evaluation outputs,
5. staged ablation execution order.
