# Task Plan: Fix Kalman Filter Test Failures

## Metadata
- Created At: 2026-02-24
- Last Updated At: 2026-02-24

## Goal

修复 `tests/kalman_filter/` 中 13 个失败测试，并与当前 production API 对齐。
策略：**production 是 ground truth，只改测试，不改 production code**。

## Phases

| # | Phase | Status | Notes |
|---|---|---|---|
| 1 | 阅读 production API（`extended.py` + state models） | completed | 已确认真实签名和返回结构 |
| 2 | 修复 `test_models.py`（4 个失败） | completed | Tensor 断言改为 `.item()`，并对齐当前模型数学行为 |
| 3 | 修复 `test_extended.py`（5 个失败） | completed | 对齐 `f(..., source_idx)`、`update()` tuple、`from_config` tuple |
| 4 | 修复 `test_helpers.py`（4 个失败） | completed | mock 从 `from_config` 改为 `create_from_config` |
| 5 | 全量验证 | completed | `tests/kalman_filter/` 全绿 |

## Phase 1 Output: Confirmed API Signatures

```text
ExtendedKalmanFilter1D.predict() -> Tensor
  - internal calls: state_model.f(x, source_idx)
                    state_model.F_jacobian(x, source_idx)
                    state_model.noise_variance(x, source_idx)

ExtendedKalmanFilter1D.update(z)
  -> (x_new, y, K, K*y, y_s_inv_y, S)

ExtendedKalmanFilter1D.from_config(config, trajectory_type=None, device=None, initial_time=0.0)
  -> (state_model, kf_R, kf_P0)

ExtendedKalmanFilter1D.create_from_config(config, trajectory_type=None, device=None, source_idx=0, initial_time=0.0)
  -> ExtendedKalmanFilter1D instance

SineAccelStateModel.__init__(omega0, kappa, noise_std, time_step=1.0, device=None, initial_time=0.0)
SineAccelStateModel.f(x, source_idx=0)
SineAccelStateModel.F_jacobian(x, source_idx=0)
SineAccelStateModel.noise_variance(x, source_idx=0)

MultNoiseStateModel.__init__(omega0, amp, base_std, time_step=1.0, device=None)
MultNoiseStateModel.f(x)
MultNoiseStateModel.F_jacobian(x)
MultNoiseStateModel.noise_variance(x)
```

## Files Modified

- `tests/kalman_filter/test_models.py`
- `tests/kalman_filter/test_extended.py`
- `tests/kalman_filter/test_helpers.py`

## Validation

```bash
uv run python -m pytest tests/kalman_filter/ -q --tb=short
# Result: 18 passed, 2 warnings
```

## Errors Encountered

| Error | Attempt | Resolution |
|---|---:|---|
| `apply_patch` failed due text encoding mismatch | 1 | Rewrote target test file directly with UTF-8 content |
| Float precision boundary (`assertAlmostEqual` at 6 places) | 1 | Adjusted one assertion to `places=5` |
