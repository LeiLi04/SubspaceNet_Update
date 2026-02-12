# Task Plan: 高收益收敛

## Goal

在不破坏当前可运行主路径的前提下，以最小风险完成 near-field 标签契约统一、Hydra 配置收敛、legacy bridge 缩减与测试补齐，降低后续维护成本。

## Current Phase

Phase 1

## Phases

### Phase 1: Scope Lock & Baseline Audit

- [ ] 锁定本轮高收益收敛边界（仅做训练路径与配置层，不扩散到全仓重写）
- [ ] 盘点 near-field 当前真实数据/标签契约（trajectory + training + lightning adapter）
- [ ] 建立最小回归基线命令（far-field / near-field / legacy）
- **Status:** in_progress

### Phase 2: Near-field Label Contract Unification

- [ ] 统一 trajectory 数据标签定义（明确 angle-only 或 angle+range）
- [ ] 训练路径（legacy + lightning）按同一契约处理标签
- [ ] 清理临时 fallback 分支，保留必要兼容并加显式日志
- **Status:** pending

### Phase 3: Hydra Canonicalization Hardening

- [ ] 在 canonical config 中显式声明 near-field 关键参数与默认值
- [ ] 增加 diff_method 与 field_type 的合法组合校验（如 Near 不允许 esprit）
- [ ] 减少 `+override` 才能运行的场景，提升默认可用性
- **Status:** pending

### Phase 4: Legacy Bridge 收敛

- [ ] 梳理 `src/train_entry.py` 的 native-first 与 legacy fallback 边界
- [ ] 下沉或删除低价值兼容桥接逻辑
- [ ] 保留可回滚路径并写明触发条件
- **Status:** pending

### Phase 5: Integration Matrix & Tests

- [ ] 补齐 3 条最小集成 smoke（far-field Lightning、near-field Lightning、legacy）
- [ ] 核对关键输出字段一致性（status / trained_model / model save）
- [ ] 记录已知非阻塞 warning，并区分 blocker vs noise
- **Status:** pending

### Phase 6: Delivery & Docs Closure

- [ ] 更新迁移文档与运行示例（near/far 各一组）
- [ ] 更新计划目录三文件状态并给出 closure snapshot
- [ ] 输出下一阶段可执行 backlog（最多 5 条）
- **Status:** pending

## Key Questions

1. near-field 在本项目的最终标签契约是否定为 angle+range（推荐）？
2. 是否接受短期保留 legacy bridge 作为回滚路径？
3. 集成验证是否统一在 `doa` 环境作为发布门禁？

## Decisions Made

| Decision | Rationale |
| --- | --- |
| 先做“高收益收敛”而非全仓重构 | 控制风险，快速提升稳定性 |
| 以训练主路径和配置主路径为优先 | 对日常迭代收益最大 |
| 规划产物固定落盘到 `docs/plan/plan_高收益收敛` | 便于后续连续执行和追踪 |

## Errors Encountered

| Error | Attempt | Resolution |
| --- | --- | --- |
| None | 1 | N/A |

## Notes

- 每完成一阶段，同步更新 `task_plan.md` / `findings.md` / `progress.md`。
- 若同类问题连续 3 次失败，切换方案并记录决策理由。
