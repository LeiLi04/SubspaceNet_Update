# Progress Log: Fix 13 Kalman Filter Test Failures

## Metadata
- Created At: 2026-02-24
- Last Updated At: 2026-02-24

## Session Log

### [2026-02-24 10:00] Baseline and Scope
- 读取 `docs/plan/plan_kalman_fix/task_plan.md`、`findings.md`、`progress.md`。
- 运行 `uv run python -m pytest tests/kalman_filter/ -q --tb=short`，确认 13 个失败。
- 确认执行原则：production 为 ground truth，仅修测试。

### [2026-02-24 10:10] Phase 1: API Signature Confirmation
- 读取 `simulation/kalman_filter/extended.py`、`simulation/kalman_filter/models/sine_accel.py`、`simulation/kalman_filter/models/mult_noise.py`。
- 确认关键差异：
  - `predict()` 内部调用 `f/F_jacobian/noise_variance(x, source_idx)`。
  - `update()` 返回 6 元组。
  - `from_config()` 返回 `(state_model, R, P0)` tuple。
  - helper 已走 `create_from_config()`。

### [2026-02-24 10:20] Phase 2: test_models.py
- 更新 tensor 断言为 `.item()`。
- 对齐当前实现期望值（弧度输入、Sine 模型当前行为、MultNoise 方差公式）。
- 处理 1 个浮点精度边界：将对应断言 `places=6` 调整为 `places=5`。

### [2026-02-24 10:30] Phase 3: test_extended.py
- `test_predict`：按 `(tensor_x, source_idx)` 检查调用参数。
- `test_update`：按 6 元组解包并逐项断言。
- `test_from_config_*`：
  - 统一设置 `process_noise_std_dev=None`。
  - `sine_accel` 分支设置 `config.system_model.M = 1`。
  - 更新 constructor 参数断言（`device/initial_time`）。
  - 校验 `from_config` tuple 返回结构。

### [2026-02-24 10:40] Phase 4: test_helpers.py
- patch 目标从 `from_config` 改为 `create_from_config`。
- 调整 4 个 helper 测试的调用断言和返回值 mock。

### [2026-02-24 10:50] Phase 5: Validation
- 分文件验证：
  - `uv run python -m pytest tests/kalman_filter/test_models.py -q --tb=short`
  - `uv run python -m pytest tests/kalman_filter/test_extended.py -q --tb=short`
  - `uv run python -m pytest tests/kalman_filter/test_helpers.py -q --tb=short`
- 全量验证：
  - `uv run python -m pytest tests/kalman_filter/ -q --tb=short`
  - 结果：`18 passed, 2 warnings`

## Current Phase Status

- Phase 1: completed
- Phase 2: completed
- Phase 3: completed
- Phase 4: completed
- Phase 5: completed

## Files Modified in This Session

- `tests/kalman_filter/test_models.py`
- `tests/kalman_filter/test_extended.py`
- `tests/kalman_filter/test_helpers.py`
- `docs/plan/plan_kalman_fix/task_plan.md`
- `docs/plan/plan_kalman_fix/findings.md`
- `docs/plan/plan_kalman_fix/progress.md`
