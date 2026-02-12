# Task Plan: Lightning + Hydra Unification

## Goal

将当前项目的训练/评估入口与配置体系收敛到“Hydra + Lightning”主路径，减少 click/手写配置分叉，提升可复现性、可维护性与自动化测试可行性。

## Current Phase

Completed (Phase 1-7)

## Phases

### Phase 1: Baseline Freeze & Scope Definition

- [x] 盘点现有入口：`main.py`、`config_handler.py`、`src/train/core.py`
- [x] 确认保留策略：现有 click CLI 先保留为兼容层
- [x] 确认新主入口：`src/train.py`（Hydra）
- **Status:** complete

### Phase 2: Hydra Entry Skeleton

- [x] 新增 `src/train.py`，实现 `@hydra.main` 最小可运行入口
- [x] 使用 `hydra.utils.instantiate` 创建 data/model/trainer（或兼容当前工厂）
- [x] 支持最小命令：训练单次 run（不破坏原路径）
- **Status:** complete

### Phase 3: Config Canonicalization

- [x] 定义唯一主配置入口（`configs/config.yaml`）
- [x] 整理 `Legacy/`、`Used_for_paper/` 为归档目录并加索引说明
- [x] 统一关键超参数来源，移除硬编码高频项
- **Status:** complete

### Phase 4: Data/Model Adapter Hardening

- [x] 清理 `src/data/lit_datamodule.py` 文档乱码与注释噪声
- [x] 明确 Lightning 依赖策略（避免 silent fallback 影响排障）
- [x] 确认 `src/models/lit_module.py` 与训练路径契合
- **Status:** complete

### Phase 5: Integration Validation

- [x] 在 `doa` 环境跑 Hydra 入口 smoke
- [x] 对比旧入口与新入口的核心输出字段一致性
- [x] 增补最小集成测试（入口/配置/委托链）
- **Status:** complete

### Phase 6: Documentation & Migration Guide

- [x] 更新 README：推荐入口、环境要求、典型命令
- [x] 增加迁移说明：旧 CLI 到 Hydra 命令映射
- [x] 在 `docs/plan/plan_lightning_hydra/` 记录最终结论
- **Status:** complete

## Key Questions

1. 是否要求短期内完全替换 click CLI，还是长期并存一段时间？
2. 配置归档是否允许保留论文复现实验原文件名不变？
3. Lightning 依赖缺失时是否允许降级，还是直接 fail fast？

## Decisions Made

| Decision | Rationale |
| --- | --- |
| 新增 Hydra 主入口而非直接替换旧 CLI | 降低迁移风险，保留回滚路径 |
| 先收敛配置入口，再做深层训练逻辑改造 | 先建立稳定边界，减少返工 |
| 计划文件落在 `docs/plan/plan_lightning_hydra` | 与本轮任务范围一一对应 |

## Errors Encountered

| Error | Attempt | Resolution |
| --- | --- | --- |
| None yet | - | - |

## Notes

- 每完成一阶段，更新 `Status` 并追加到 `progress.md`。
- 若同类失败连续 3 次，切换方案并记录到 `findings.md`。

## Closure Snapshot (2026-02-12)

- Plan status: closed.
- Completed scope:
  - Phase 1-6 baseline unification work.
  - Phase 7 hardening (`_target_` runtime takeover, native instantiate path, namespace cleanup, Lightning migration).
  - Trajectory path on Lightning validated for far-field and near-field-compatible settings.
- Residual notes:
  - Near-field run requires compatible diff method (for example `model.params.diff_method=music_1D`).
  - Remaining warnings are non-blocking runtime hints (for example DataLoader workers), not plan blockers.

## Execution Update (2026-02-12, Run 2)

- Completed this run:
  - Phase 1 baseline freeze checklist verified against current codebase.
  - Phase 2 implemented: added `src/train.py` as Hydra entry skeleton (compatibility-first, legacy pipeline delegation).
- Phase status transition:
  - Phase 1: complete
  - Phase 2: complete
  - Next: Phase 3 (Config Canonicalization)
- Notes:
  - Kept legacy Click path untouched (`main.py`, `src/train/entry.py`).
  - Added compatibility mapping for transitional Hydra groups (`data` -> `dataset`, `trainer` -> `training`).

## Execution Update (2026-02-12, Run 3)

- Completed this run:
  - Phase 3 Config Canonicalization implemented.
- Phase status transition:
  - Phase 3: complete
  - Next: Phase 4 (Data/Model Adapter Hardening)
- What changed:
  - Canonical config groups introduced for `system_model`, `dataset`, `training`, `simulation`.
  - `configs/default.yaml` simplified to single-source bridge (`legacy_config` only).
  - Added archive index + folder-level archive notes for historical configs.

## Execution Update (2026-02-12, Run 4)

- Completed this run:
  - Phase 4 Data/Model Adapter Hardening completed.
- Phase status transition:
  - Phase 4: complete
  - Next: Phase 5 (Integration Validation)
- What changed:
  - Cleaned `src/data/lit_datamodule.py` encoding/docstrings/comments (removed mojibake).
  - Made Lightning dependency policy explicit and fail-fast in DataModule and LightningModule adapter.
  - Kept current training path compatibility: legacy trainer remains primary; Lightning adapter is explicit migration path.

## Execution Update (2026-02-12, Run 5)

- Completed this run:
  - Phase 5 Integration Validation completed.
- Phase status transition:
  - Phase 5: complete
  - Next: Phase 6 (Documentation & Migration Guide)
- Validation scope executed:
  1) Hydra entry smoke in `doa` env.
  2) Legacy CLI smoke in `doa` env.
  3) Core output field parity check between legacy config path and Hydra config path.
  4) Minimal integration test for Hydra bridge mapping + canonical group presence.

## Execution Update (2026-02-12, Run 6)

- Completed this run:
  - Phase 6 Documentation & Migration Guide completed.
- Phase status transition:
  - Phase 6: complete
  - Plan status: all phases complete
- Delivery outputs:
  1) README updated with recommended Hydra entrypoint, environment requirements, and typical commands.
  2) Added migration guide with legacy CLI -> Hydra command/override/scenario mapping.
  3) Added final closure notes in planning records.

## Phase 7: Post-Unification Hardening (New)

### Scope

在已完成 1-6 阶段基础上，继续将架构从“Hydra兼容桥接”推进到“Hydra/Lightning 原生主路径”。

### Phase 7.1: Hydra `_target_` Runtime Takeover

- [x] 引入 runtime `_target_` 配置组并接管入口调度
- [x] 在 `src/train.py` 使用 `hydra.utils.instantiate(cfg.runtime, simulation=...)`
- [x] 为 runtime `_target_` 增补最小集成验证
- **Status:** complete

### Phase 7.2: `_target_` Data/Model/Trainer Native Instantiation

- [ ] 为 data/model/trainer 提供可直接 `instantiate` 的原生配置与适配器
- [ ] 逐步减少 `legacy_config + apply_overrides` 依赖
- **Status:** pending

### Phase 7.3: Train Namespace Collision Cleanup

- [ ] 解决 `src/train.py` 与 `src/train/` 包同名冲突
- [ ] 更新导入路径与测试工具链适配
- **Status:** pending

### Phase 7.4: Lightning-Native Training Loop Migration

- [ ] 将 `src/train/training.py` 关键训练循环逐步迁移到 `LightningModule.training_step`
- [ ] 保留旧循环为兼容路径并补充迁移开关
- **Status:** pending

## Execution Update (2026-02-12, Run 8)

- Completed this run:
  - Phase 7.2 (`_target_` Data/Model/Trainer Native Instantiation) implemented with native-first runtime path.
- Phase status transition:
  - Phase 7.2: complete (with compatibility fallback retained)
  - Next: Phase 7.3 (Train Namespace Collision Cleanup)
- What changed:
  - Added Hydra-instantiable data/model/trainer component factories.
  - Updated corresponding config groups with `_target_` entries.
  - `src/train.py` now builds `Config` directly from composed Hydra config (native-first), and only falls back to legacy bridge on native failure.

## Execution Update (2026-02-12, Run 9)

- Follow-up hardening after Phase 7.2 rollout:
  1) Fixed DCD_MUSIC dataset signature compatibility in standard data branches.
  2) Added non-trajectory DataLoader fallback when dataset lacks `get_dataloaders`.
- Additional progress:
  - Phase 7.3 (Train Namespace Collision Cleanup) completed via import-safe split:
    - `src/train_entry.py` now contains importable Hydra logic.
    - `src/train.py` reduced to wrapper script entrypoint.
- Phase status transition:
  - Phase 7.3: complete
  - Next: Phase 7.4 (Lightning-Native Training Loop Migration)

## Execution Update (2026-02-12, Run 10)

- Entered Phase 7.4 and completed first migration slice:
  - Non-trajectory training now supports Lightning-native training loop (`Trainer.fit`) via `training.use_lightning=true`.
- Phase status transition:
  - Phase 7.4: in_progress
- Implemented scope (this run):
  - Added Lightning training switch in schema/config.
  - Added Lightning training pipeline in `Simulation` with compatibility guards.
  - Implemented functional `LegacyLightningModule.training_step/validation_step` fallback objective.
  - Preserved legacy training loop as default path.

## Execution Update (2026-02-12, Run 11)

- Completed Phase 7.4 Milestone 2:
  - Trajectory training path now supports Lightning-native loop (`Trainer.fit`) when `training.use_lightning=true`.
- Current Phase 7.4 status:
  - in_progress (Milestone 1 + Milestone 2 completed)
- Remaining scope for Phase 7.4:
  - near-field trajectory Lightning parity and cleanup of residual logging noise.

## Execution Update (2026-02-12, Run 12)

- Completed this run:
  - Revalidated Phase 7.4 Milestone 2 (trajectory path on Lightning-native training loop) in `doa`.
- Phase status transition:
  - Phase 7.4: in_progress (Milestone 1 + Milestone 2 stable)
- Validation command:
  - `python src/train.py +scenario=training +trajectory.enabled=true training.use_lightning=true training.epochs=1 training.batch_size=2 simulation.train_model=true simulation.load_model=false simulation.evaluate_model=false dataset.samples_size=8`
- Result:
  - Hydra run finished with success; one-epoch `Trainer.fit` completed and model saved.

## Execution Update (2026-02-12, Run 13)

- Completed this run:
  - Closed two pending Phase 7.4 tail items:
    1) near-field trajectory alignment on Lightning path
    2) GBK console Lightning emoji logging noise suppression
- Phase status transition:
  - Phase 7.4: complete
  - Phase 7: complete
- Implementation highlights:
  - `src/train/core.py`
    - removed near-field forced fallback so trajectory near/far can use Lightning-native path under `training.use_lightning=true`
    - raised rank-zero logger levels to suppress non-essential info messages that trigger GBK emoji encode failures
  - `src/models/lit_module.py`
    - added robust near-field trajectory handling for label contracts without range targets
    - added angle-only fallback path for near-field (`music_1D`/known-angles-required cases)
    - converted one-time warning helper to structured logging
