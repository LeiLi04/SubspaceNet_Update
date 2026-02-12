# Task Plan: Online Learning Refactor Next Steps

## Goal

将在线学习重构从“可编译”推进到“可维护、可测试、可回归”，完成模块契约稳定、关键测试覆盖、编码清理与集成验证。

## Current Phase

Completed (Phase 1-6 all executed at least once)

## Phase Status

### Phase 1: Scope Freeze & Risk Mapping

- [x] 确认拆分结构可编译：`online_learning.py` + `online_learning_parts/*`
- [x] 明确后续阶段目标与风险
- [x] 输出阶段执行顺序
- **Status:** completed

### Phase 2: Pipeline Contract Stabilization

- [x] 统一 `step_result` 创新协方差字段命名
- [x] 保留兼容别名，避免调用方回归
- [x] 增加最小运行时断言（shape/type/device）
- **Status:** completed (pass 1)

### Phase 3: Step Processor Hardening

- [x] 提取公共函数，减少 far/near 分支重复
- [x] 增加 EKF 状态迁移一致性检查
- [x] 增加模型模式恢复（eval/train）防止隐式状态泄漏
- **Status:** completed (pass 1)

### Phase 4: Losses & Metrics Testability

- [x] 新增 `losses.py` 核心路径测试
- [x] 新增 `metrics_aggregate.py` 聚合测试（含部分空轨迹）
- [x] 新增 near-field fallback 路径测试
- **Status:** completed (pass 1)

### Phase 5: Encoding & Hygiene Cleanup

- [x] 清理 `src/data/trajectory.py` 头部与关键日志乱码
- [x] 清理 `src/train/online_learning_parts/*` 冗余导入
- [x] 保留有意义占位注释，移除噪声内容
- **Status:** completed (pass 1)

### Phase 6: Integration Validation & Delivery

- [x] 尝试 CLI smoke（受环境依赖阻塞：`click`）
- [x] 增加无运行时依赖的集成契约测试
- [x] 在 `doa` 环境复测在线学习测试集（11 tests passed）
- **Status:** completed (pass 2, runtime-verified in `doa`)

## Key Questions (Archived)

1. 是否将 `step_results` 固化为 dataclass（替代松散 dict）
2. near-field 降级是否需要 strict/fallback 开关
3. `pipeline_run.py` 是否继续拆分（模型复制、绘图、GLRT）

## Decisions Made

| Decision | Rationale |
| --- | --- |
| 保持 `OnlineLearning` 对外 API 不变，仅做内部委托拆分 | 最小化外部调用改动，降低回归风险 |
| 先“可运行+可编译”，再“可测试+可维护” | 分阶段收敛，减少定位复杂度 |
| 计划文件固定放在 `docs/plan` | 与团队路径约定一致，便于持续维护 |

## Errors Encountered

| Error | Attempt | Resolution |
| --- | --- | --- |
| `IndentationError` during split generation | 1 | 修复自动拆分脚本产物并重新编译 |
| CLI smoke blocked (`click` missing) | 1 | 改为无依赖集成契约测试 + 在 `doa` 环境补充运行验证 |

## Notes

- 所有阶段已至少完成一次执行与记录。
- 当前计划进入维护态；后续可新建 `task_plan_v2.md` 继续迭代。
