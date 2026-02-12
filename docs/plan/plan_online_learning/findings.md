# Findings & Decisions

## Requirements

- 规划文件固定路径：`docs/plan`
- 目标是“将要做的内容 + 已执行结果闭环”，不是单纯历史归档
- 重点围绕 `src/train/online_learning.py` 拆分后稳定性与可测试性

## Architecture Findings

- 在线学习主入口保留在：`src/train/online_learning.py`
- 主要实现已拆分至：`src/train/online_learning_parts/`
  - `pipeline.py`
  - `pipeline_run.py`
  - `pipeline_train.py`
  - `step_processor.py`
  - `losses.py`
  - `metrics.py`
  - `metrics_aggregate.py`
- 关键模块已满足单文件行数控制目标（重点文件 < 500 行）

## Technical Decisions

| Decision | Rationale |
| --- | --- |
| 先稳契约，再补测试 | 测试依赖稳定接口，先锁边界减少返工 |
| near-field 采用 fallback 策略 | 防止在线流程硬中断，提升可运行性 |
| 保留兼容字段别名 | 避免重构阶段对历史调用方造成破坏 |

## Issues Encountered

| Issue | Resolution |
| --- | --- |
| 拆分后字段命名不一致 | 增加规范键并保留旧键兼容 |
| 环境依赖不齐（系统 Python 缺 torch，CLI 缺 click） | 使用 `doa` 环境复测；增加无依赖集成契约测试 |
| 部分计划文件历史乱码 | 统一重写为 UTF-8 并清理内容 |

## Validation Summary

- Contract & hardening:
  - `py_compile` passed
- Unit tests:
  - `tests/online_learning/test_losses.py`
  - `tests/online_learning/test_metrics_aggregate.py`
  - `tests/online_learning/test_step_processor.py`
- Integration contracts:
  - `tests/online_learning/test_integration_contracts.py`
- Runtime verification:
  - `conda run -n doa python -m unittest ...` => Ran 11 tests, OK

## Delivery Note

- Phase 1-6 均已完成至少一轮。
- 当前版本已达到“结构化、可验证、可追踪”的交付标准。
- 若继续优化，建议开启下一版计划文件（例如 `docs/plan/task_plan_v2.md`）。
