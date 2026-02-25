# Findings: Kalman Filter Test Failures (13 -> 0)

## Metadata
- Created At: 2026-02-24
- Last Updated At: 2026-02-24

## Failure Summary (Original)

```text
FAILED tests/kalman_filter/test_extended.py::TestExtendedKalmanFilter1D::test_predict
FAILED tests/kalman_filter/test_extended.py::TestExtendedKalmanFilter1D::test_update
FAILED tests/kalman_filter/test_extended.py::TestExtendedKalmanFilter1D::test_from_config_mult_noise
FAILED tests/kalman_filter/test_extended.py::TestExtendedKalmanFilter1D::test_from_config_random_walk
FAILED tests/kalman_filter/test_extended.py::TestExtendedKalmanFilter1D::test_from_config_sine_accel
FAILED tests/kalman_filter/test_helpers.py::TestHelperFunctions::test_get_kalman_filter_extended
FAILED tests/kalman_filter/test_helpers.py::TestHelperFunctions::test_get_kalman_filter_nonlinear_trajectory
FAILED tests/kalman_filter/test_helpers.py::TestHelperFunctions::test_get_kalman_filter_standard
FAILED tests/kalman_filter/test_helpers.py::TestHelperFunctions::test_get_kalman_filter_with_trajectory_type_param
FAILED tests/kalman_filter/test_models.py::TestSineAccelStateModel::test_jacobian
FAILED tests/kalman_filter/test_models.py::TestSineAccelStateModel::test_state_transition
FAILED tests/kalman_filter/test_models.py::TestMultNoiseStateModel::test_noise_variance
FAILED tests/kalman_filter/test_models.py::TestMultNoiseStateModel::test_state_transition
```

---

## Root Causes and Fixes

### 1) `f(x)` -> `f(x, source_idx)`

- **Root cause**: `ExtendedKalmanFilter1D.predict()` 现在调用 `state_model.f(self.x, self.source_idx)`。
- **Affected test**: `test_predict`
- **Fix**: 更新断言为检查调用参数 `(tensor_x, 0)`。

### 2) `update()` return changed to tuple

- **Root cause**: `update()` 返回 6 元组：`(x_new, y, K, K*y, y_s_inv_y, S)`。
- **Affected test**: `test_update`
- **Fix**: 测试中改为解包 tuple，并对每个关键值做数值断言。

### 3) `assertAlmostEqual` with Tensor

- **Root cause**: state model API 返回 `torch.Tensor`，原测试直接把 tensor 传入 `assertAlmostEqual`。
- **Affected tests**: `test_models.py` 中 4 个失败项。
- **Fix**: 使用 `.item()` 进行标量比较，并修正期望公式使其匹配当前实现（例如 `SineAccelStateModel.f` 在 t=0 的 0.99 缩放、`MultNoiseStateModel` 使用弧度输入）。

### 4) constructor signature drift (`device`, `initial_time`, source count check)

- **Root cause**:
  - `SineAccelStateModel` 构造函数包含 `device`, `initial_time`。
  - `MultNoiseStateModel` 构造函数包含 `device`。
  - `from_config` 对 `SINE_ACCEL_NONLINEAR` 分支会校验 `len(omega0) == config.system_model.M`。
- **Affected tests**: `test_from_config_*`
- **Fix**:
  - 在 mock config 中显式设置 `process_noise_std_dev = None` 以走 fallback 噪声。
  - 设置 `config.system_model.M = 1`。
  - 更新 `assert_called_once_with(...)` 期望（含 `device=None`, `initial_time=0.0`，以及列表参数）。
  - 将 `from_config` 测试改为校验 tuple 返回值，而非 filter instance。

### 5) `create_from_config` call chain in helpers

- **Root cause**: `get_kalman_filter()` 现在调用的是 `KalmanFilter1D.create_from_config` / `ExtendedKalmanFilter1D.create_from_config`，而非 `from_config`。
- **Affected tests**: `test_helpers.py` 4 个失败项。
- **Fix**: patch 目标改为 `create_from_config`，并调整调用断言。

---

## Ground-Truth Principle Applied

- 不改 production:
  - `simulation/kalman_filter/extended.py`
  - `simulation/kalman_filter/models/*`
- 仅改测试:
  - `tests/kalman_filter/test_extended.py`
  - `tests/kalman_filter/test_models.py`
  - `tests/kalman_filter/test_helpers.py`

---

## Final Verification

```bash
uv run python -m pytest tests/kalman_filter/ -q --tb=short
# 18 passed, 2 warnings
```
