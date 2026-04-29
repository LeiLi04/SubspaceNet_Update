# Whitened CUSUM Trigger Implementation Notes

## Completed

- [x] `compute_chi2_threshold` and `compute_cusum_threshold` analytical thresholds
- [x] `PageCusum` accumulator with reset support
- [x] `DriftTrigger` strategies: `time_to_learn`, `sigma_y_sq`, `whitened_cusum`
- [x] `pipeline_run.py` strategy wiring for window-level drift detection
- [x] `c_per_step` diagnostic export on window results
- [x] YAML config block and comparator presets
- [x] Unit tests, lightweight integration smoke, and null-distribution validation script
- [x] `dump_c_per_step_path` pipeline hook for real null-distribution npz export
- [x] `validate_null_distribution.py` now requires real `--input` unless explicitly run as synthetic smoke
- [x] pipeline helper smoke verifies `c_per_step` is fed to the trigger
- [x] Non-blocking review nits: expose `dof` in trigger state and move dump imports to module top-level
- [x] Real-null review fixes: dump `c_per_step_per_source`, add `--per-source`, add `--decimate`
- [x] Step 0 per-source real-null diagnostic run
- [x] Short fixed-seed `measurement_noise_std_dev` sweep after oracle EKF check
- [x] Long multi-trajectory validation for `measurement_noise_std_dev ∈ {0.12, 0.11, 0.105}`
- [x] Lightweight CUSUM trigger replay grid for `p_fa / b_offset`
- [x] Calibrated YAML preset and one-trajectory end-to-end smoke

## Remaining Research Items

- [ ] Decide between scalar `R_obs=0.105^2` and source-specific / calibration-data `R_obs`
- [ ] Multi-trajectory end-to-end comparison against `time_to_learn` and `sigma_y_sq`
- [ ] `R_obs` online/calibration-data estimation
- [ ] `b_offset` sensitivity sweep
- [ ] EKF vs UKF null-distribution comparison
- [ ] Non-Gaussian impulse-noise robustness
- [ ] Huberized whitened innovation fallback

## Real Null Validation

Task 2 was run on 2026-04-29 with a no-drift short trajectory:

```text
system_model.eta=0
system_model.sv_noise_var=0
online_learning.dataset_size=1
online_learning.trajectory_length=30
online_learning.eta_increment=0
online_learning.max_eta=0
online_learning.dump_c_per_step_path=outputs/null_validation_real.npz
```

Validation command:

```bash
.venv-wsl/bin/python scripts/validate_null_distribution.py --input outputs/null_validation_real.npz
```

Result: validation did not pass. The dump contained `N=130` samples with `mean(c)=12.444` versus theoretical `E[chi2(3)]=3`; KS test returned `stat=0.4740`, `p=2.425e-27`.

Conclusion: current EKF observation-noise calibration is not consistent with the real no-drift pipeline output. Before any blind `R_obs` sweep, regenerate the no-drift dump with per-source diagnostics and run `--per-source`; if only one source is inflated, diagnose source association / EKF initialization first. If all sources inflate together, sweep `kalman_filter.measurement_noise_std_dev` over `{0.05, 0.1, 0.2, 0.5, 1.0}` with `stride >= window_size`.

## Step 0 Per-Source Diagnostic

Step 0 was run on 2026-04-29 with `stride=5`, `window_size=5`, and dump path `outputs/null_validation_per_source.npz`.

Dump summary:

```text
keys: ['c', 'c_per_step_per_source', 'dof', 'trajectory_idx']
c_shape = (30,)
c_per_step_per_source_shape = (30, 3)
mean(c) = 6.077
mean(c_source) = [1.176, 1.732, 3.168]
max(c) = 27.784
max(c_source) = 19.308
```

Validation:

```text
source[0]: mean=1.176, KS p=0.1679 PASS
source[1]: mean=1.732, KS p=0.4564 PASS
source[2]: mean=3.168, KS p=0.0121 FAIL
total: mean=6.077, KS p=0.002349 FAIL
```

Conclusion: the first per-source run showed source 2 dominating the null inflation, but a repeat with diagnostic fields showed the dominant source can vary with the random trajectory. The stable pattern is SubspaceNet measurement error larger than the current innovation covariance, not an EKF dynamics failure.

## EKF / R_obs Diagnostic Follow-up

The dump hook now also stores:

```text
true_angles
pre_ekf_predictions
ekf_predictions
innovations
innovation_covariances
```

An oracle check using true angles as the EKF measurement produced:

```text
oracle_true_measurement_mean_c_source = [0.005608, 0.000110, 0.047073]
oracle_true_measurement_mean_total = 0.052792
```

This indicates the EKF sine-acceleration dynamics are not the source of the null inflation. The practical issue is that the pretrained SubspaceNet measurement error is larger than the current `S=P+R`.

Fixed-seed short sweep:

```text
measurement_noise_std_dev=0.05 -> mean_total=11.0704, mean_src=[3.4987, 2.0420, 5.5297]
measurement_noise_std_dev=0.10 -> mean_total=4.2091,  mean_src=[1.3000, 0.9508, 1.9582]
measurement_noise_std_dev=0.12 -> mean_total=3.1839,  mean_src=[0.9912, 0.7520, 1.4408]
measurement_noise_std_dev=0.13 -> mean_total=2.8122,  mean_src=[0.8809, 0.6759, 1.2553]
measurement_noise_std_dev=0.14 -> mean_total=2.5053,  mean_src=[0.7906, 0.6113, 1.1034]
measurement_noise_std_dev=0.20 -> mean_total=1.4333,  mean_src=[0.4806, 0.3683, 0.5844]
```

Best short-run candidate: `measurement_noise_std_dev=0.12`.

Validation for `outputs/null_validation_noise_0p12.npz`:

```text
total: mean=3.184, KS p=0.1366 PASS
source[0]: mean=0.991, KS p=0.5847 PASS
source[1]: mean=0.752, KS p=0.3321 PASS
source[2]: mean=1.441, KS p=0.2660 PASS
```

Long validation showed `0.12` is too conservative on shorter runs, `0.11` is acceptable by total mean, and `0.105` is the best scalar candidate so far.

Long validation summary:

```text
noise=0.12
ds=3,len=50:  mean_total=2.3825, p_total=1.994e-05, mean_src=[0.9369, 0.6430, 0.8025]
ds=3,len=100: mean_total=2.7235, p_total=0.0003338, mean_src=[0.9601, 0.6944, 1.0690]
ds=5,len=50:  mean_total=2.3997, p_total=1.066e-06, mean_src=[0.9222, 0.6385, 0.8390]
ds=5,len=100: mean_total=2.7121, p_total=4.595e-05, mean_src=[0.9366, 0.7415, 1.0340]

noise=0.11
ds=3,len=50:  mean_total=2.7066, p_total=0.007013, mean_src=[1.0690, 0.7228, 0.9148]
ds=3,len=100: mean_total=3.1048, p_total=0.09671,  mean_src=[1.0948, 0.7830, 1.2269]
ds=5,len=50:  mean_total=2.7221, p_total=0.003201, mean_src=[1.0487, 0.7145, 0.9589]
ds=5,len=100: mean_total=3.0879, p_total=0.06506,  mean_src=[1.0639, 0.8370, 1.1870]

noise=0.105
ds=3,len=50:  mean_total=2.8960, p_total=0.05036, mean_src=[1.1466, 0.7690, 0.9805]
ds=3,len=100: mean_total=3.3280, p_total=0.48300, mean_src=[1.1737, 0.8345, 1.3198]
ds=5,len=50:  mean_total=2.9104, p_total=0.03063, mean_src=[1.1230, 0.7582, 1.0293]
ds=5,len=100: mean_total=3.3076, p_total=0.25540, mean_src=[1.1382, 0.8925, 1.2770]
```

Conclusion: use `measurement_noise_std_dev=0.105` as the best scalar `R_obs` candidate for the next CUSUM experiments, not as a final theoretical default. It satisfies the robust total-mean criterion in all long-validation combos, but source[1] remains slightly under-dispersed and some KS tests still fail with larger N. The next research step is source-specific or calibration-data `R_obs`.

## CUSUM Trigger Replay

Lightweight trigger replay was run on 2026-04-29 using calibrated `measurement_noise_std_dev=0.105`.

Important execution note: fixed-eta `execute_online_learning()` runs are not valid drift streams because `run_online_learning_impl()` resets eta to 0 at each trajectory start. Drift replay therefore used dynamic eta updates:

```text
trajectory_length=100
window_size=5
stride=5
eta_update_interval_windows=5
eta_increment ∈ {0.6, 1.0}
max_eta ∈ {0.6, 1.0}
```

Initial grid (`p_fa ∈ {0.01, 0.05, 0.10}`, `b_offset ∈ {0.5, 1.0, 1.5}`) detected drift quickly but was unusable for no-drift because every null trajectory had at least one false alarm.

Conservative grid result:

```text
p_fa=1e-6, b_offset=20
No-drift validation across all 0.105 long-null files:
  ds=3,len=50:  0/3 trajectories false-alarmed
  ds=3,len=100: 0/3 trajectories false-alarmed
  ds=5,len=50:  0/5 trajectories false-alarmed
  ds=5,len=100: 0/5 trajectories false-alarmed
  total: 0/16 trajectories false-alarmed

Dynamic eta=0.6: detect_rate=1.0, avg_delay=1.667 windows
Dynamic eta=1.0: detect_rate=1.0, avg_delay=1.000 windows
```

Conclusion: use `p_fa=1e-6`, `b_offset=20`, `reset_after_trigger=true` as the conservative replay candidate for the next end-to-end online-training run. This is empirical and should not be described as the analytical false-alarm target being achieved; the real residual tails require a much larger reference value than the original theory suggested.

## End-to-End Smoke

Added calibrated preset:

```text
run/conf/Used_for_paper/SineAccel_whitened_cusum_calibrated.yaml
```

Preset values:

```text
kalman_filter.measurement_noise_std_dev=0.105
online_learning.drift_trigger.type=whitened_cusum
online_learning.drift_trigger.p_fa=1e-6
online_learning.drift_trigger.b_offset=20.0
online_learning.drift_trigger.reset_after_trigger=true
```

One-trajectory dynamic-drift smoke:

```text
trajectory_length=100
window_size=5
stride=5
eta_update_interval_windows=5
eta_increment=0.6
max_eta=0.6
max_iterations=1
dump=outputs/e2e_whitened_cusum_calibrated_eta0p6.npz
```

Result: run completed successfully. Offline replay on the emitted dump with the calibrated trigger fired first at window 6:

```text
replay_fired_windows = [6, 12, 13, 16, 18, 19]
window_mean_first12 = [3.592, 2.285, 1.624, 2.097, 2.808, 1.866, 23.871, 17.641, 5.079, 13.512, 8.295, 13.374]
```

The online-training logs show training began at window 6 and post-learning evaluation began at window 11. This confirms the conservative whitened CUSUM candidate can drive the full online-training path on one dynamic-drift trajectory.

## Trigger Pause And Comparator Smoke

During the three-trigger short closed-loop comparison, the original pipeline exposed two bookkeeping problems:

1. `window_update_flags` only appended `False` on non-trigger windows, so trigger windows were not represented as `True`.
2. The trigger continued to be observed after the trajectory had already entered the online-learning path, inflating `drift_detected_count` with repeated detections.

Fix in:

```text
src/trainer_module/online_learning_parts/pipeline_run.py
```

Current behavior:

- `window_update_flags` gets one boolean per window.
- trigger windows append `True`.
- after `self.drift_detected` becomes true, the pipeline still collects `c_per_step` diagnostics but skips further trigger observation for that trajectory.
- `drift_detected_count` is now at most one per trajectory in the current single-drift experiment design.

Short comparator smoke output:

```text
outputs/e2e_whitened_cusum_trigger_comparison_20260429/summary.json
```

Shared settings:

```text
dataset_size=3
trajectory_length=100
window_size=5
stride=5
eta_update_interval_windows=5
eta_increment ∈ {0.6, 1.0}
max_iterations=1
measurement_noise_std_dev=0.105
```

Because the configured pretrained checkpoint is absent in this workspace, the run used `simulation.load_model=false`; treat this as a pipeline/comparator smoke, not a paper-quality performance result.

Post-fix summary:

```text
eta=0.6
  time_to_learn: first_online=[6,6,6], pre-false=0/3, drift_count=3, tail5_improve=+0.1415
  sigma_y_sq:    first_online=[0,0,0], pre-false=3/3, drift_count=3, tail5_improve=+0.0637
  whitened:      first_online=[2,6,8], pre-false=1/3, drift_count=3, tail5_improve=+0.1010

eta=1.0
  time_to_learn: first_online=[6,6,6], pre-false=0/3, drift_count=3, tail5_improve=+0.1452
  sigma_y_sq:    first_online=[0,0,0], pre-false=3/3, drift_count=3, tail5_improve=+0.0709
  whitened:      first_online=[3,1,0], pre-false=3/3, drift_count=3, tail5_improve=+0.0739
```

Interpretation: repeat-trigger pollution is fixed, but closed-loop early firing remains. Next validation should use the real pretrained checkpoint and add a closed-loop no-drift smoke before treating the calibrated CUSUM as accepted.

Closed-loop no-drift follow-up:

```text
outputs/e2e_whitened_cusum_closed_loop_null_20260429/summary.json
```

With `eta_increment=0`, `max_eta=0`, `b_offset=20`, calibrated CUSUM still entered the online path on all 3 trajectories:

```text
first_online_windows=[2, 2, 0]
false_trigger_trajectory_count=3/3
```

Conservative `b_offset` sweep:

```text
outputs/e2e_whitened_cusum_closed_loop_null_boffset_sweep_20260429/summary.json
```

Result: even `b_offset=200` still false-triggered 1/3 trajectories (`first_online_windows=[5, null, null]`).

Single-trajectory diagnostic dump:

```text
outputs/e2e_whitened_cusum_closed_loop_null_boffset200_traj0_dump_20260429/summary.json
```

The false trigger is caused by a source-level spike:

```text
c_max=225.722 at window 5
argmax_source_values=[0.983, 0.157, 224.582]
```

Do not keep increasing `b_offset` as the primary fix. The next useful work is source-level association / covariance diagnostics, preferably with the real pretrained checkpoint restored.

## Verification

Recommended checks:

1. `pytest tests/online_learning/test_drift_trigger.py -v`
2. `pytest tests/online_learning/ -v`
3. `pytest tests/integration/test_whitened_trigger_smoke.py -v -m integration`
4. Generate a real no-drift npz with `online_learning.dump_c_per_step_path=...`, then run `python scripts/validate_null_distribution.py --input <path>` and `python scripts/validate_null_distribution.py --input <path> --per-source`

In this workspace shell, `.venv-wsl` is the working Linux virtual environment for Codex/WSL tests. Do not use the Windows `.venv/Scripts/python.exe` from WSL.
