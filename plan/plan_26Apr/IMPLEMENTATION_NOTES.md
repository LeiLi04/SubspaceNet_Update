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

## Remaining Research Items

- [ ] `R_obs` online/calibration-data estimation
- [ ] `b_offset` sensitivity sweep
- [ ] EKF vs UKF null-distribution comparison
- [ ] Non-Gaussian impulse-noise robustness
- [ ] Huberized whitened innovation fallback

## Verification

Recommended checks:

1. `pytest tests/online_learning/test_drift_trigger.py -v`
2. `pytest tests/online_learning/ -v`
3. `pytest tests/integration/test_whitened_trigger_smoke.py -v -m integration`
4. Generate a real no-drift npz with `online_learning.dump_c_per_step_path=...`, then run `python scripts/validate_null_distribution.py --input <path>`

In this workspace shell, `.venv-wsl` is the working Linux virtual environment for Codex/WSL tests. Do not use the Windows `.venv/Scripts/python.exe` from WSL.
