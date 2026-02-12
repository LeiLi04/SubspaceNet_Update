# Findings & Decisions

## Requirements

- 按“高收益收敛”优先级推进，不做低收益大改。
- 重点聚焦：near-field 标签契约、Hydra canonical 配置、legacy bridge 收敛、最小回归矩阵。
- 所有修改需可在当前 `doa` 环境复现验证。

## Research Findings

- 当前 far-field trajectory + Lightning 路径已可稳定跑通。
- near-field trajectory + Lightning 已打通，但仍存在标签契约与模型差异化处理的兼容分支。
- 入口层仍存在 native-first + legacy fallback 双轨，维护成本偏高。

## Technical Decisions

| Decision | Rationale |
| --- | --- |
| 先统一 near-field 标签契约 | 这是训练分支复杂度和回归风险的根源 |
| 再做 Hydra 参数合法组合校验 | 提前拦截错误配置，减少运行时失败 |
| 最后收敛 legacy bridge | 在功能稳定后再降兼容，风险更低 |

## Issues Encountered

| Issue | Resolution |
| --- | --- |
| None | N/A |

## Resources

- `docs/plan/plan_lightning_hydra/task_plan.md`
- `docs/plan/plan_lightning_hydra/findings.md`
- `docs/plan/plan_lightning_hydra/progress.md`
- `src/train/core.py`
- `src/models/lit_module.py`
- `src/data/trajectory.py`
- `src/train_entry.py`
- `config/schema.py`
- `configs/`

## Visual/Browser Findings

- 本轮未使用外部浏览器检索。
