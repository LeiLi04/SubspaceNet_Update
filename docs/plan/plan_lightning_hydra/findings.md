# Findings & Decisions

## Requirements

- 采用 `docs/constructure.md` 作为目标架构参考。
- 规划聚焦 Lightning + Hydra 统一，不扩散到无关重构。
- 所有变更默认“兼容优先”，避免破坏现有可用流程。

## Initial Findings

- 入口层存在双轨：click (`main.py`) + 自定义配置处理 (`config_handler.py`)。
- Lightning 适配层存在，但尚未成为主运行路径：
  - `src/models/lit_module.py`
  - `src/data/lit_datamodule.py`
- `configs/` 存在历史分叉（`Legacy/`, `Used_for_paper/`），主入口辨识成本高。

## Technical Direction

- 主方向：新增 Hydra 训练入口并逐步收敛配置。
- 迁移策略：旧 CLI 先保留为兼容层，分阶段降权。
- 验证标准：功能一致性 + 可复现命令 + 最小集成测试。

## Resources

- `docs/constructure.md`
- `main.py`
- `config_handler.py`
- `src/train/core.py`
- `src/models/lit_module.py`
- `src/data/lit_datamodule.py`
- `configs/`

## Open Risks

- 环境依赖不齐时，Hydra/Lightning smoke 可能受阻。
- 旧配置文件中的隐式假设可能在收敛时暴露问题。
- 训练循环若仍由 legacy 代码主导，短期内会形成“壳对齐、核未对齐”。

## Findings Update (2026-02-12, Run 2)

- Added new file `src/train.py`:
  - Uses `@hydra.main(config_path="../configs", config_name="config")`.
  - Loads baseline legacy config via `config.loader.load_config`.
  - Converts composed Hydra config into legacy dotted overrides via `apply_overrides`.
  - Reuses `create_components_from_config` + `Simulation` for execution (`training/evaluation/online_learning/full`).
- Safety/compatibility decisions:
  - Did not replace old CLI; Hydra path is additive.
  - Added direct-script path bootstrap so `python src/train.py ...` can import top-level `config`.
- Environment findings:
  - Default python in current shell lacks `hydra`.
  - `doa` env has `hydra`/`omegaconf` and can run `src/train.py --help`.
  - `conda run -n doa ...` hit a temp-file activation issue on this host; direct env python path worked.
- Skill integration note:
  - `planning-with-files` session-catchup script path from `~/.claude/skills` is absent on this machine; proceeded with manual catchup using existing planning files + git diff.

## Findings Update (2026-02-12, Run 3)

- Canonical-entry consolidation:
  - `configs/config.yaml` now composes canonical groups first:
    - `system_model: default`
    - `dataset: default`
    - `training: default`
    - `simulation: default`
  - Transitional groups (`data`, `trainer`) remain for compatibility while migration is in progress.
- Single-source improvement for high-frequency params:
  - Removed duplicated root values from `configs/default.yaml`.
  - High-frequency knobs (`N/M/T/snr`, `samples_size`, `epochs/batch_size`, simulation toggles) now reside in canonical group files.
- Archive indexing:
  - Added `configs/ARCHIVE_INDEX.md` as central archival policy and migration guide.
  - Added `configs/Legacy/README.md` and `configs/Used_for_paper/README.md` to mark archive status in-place.
- Validation:
  - Hydra help in `doa` env confirms new groups are discoverable (`dataset/system_model/training/simulation`).

## Findings Update (2026-02-12, Run 4)

- `src/data/lit_datamodule.py` had extensive mojibake text in top-level and method docstrings.
  - Resolution: rewrote docs/comments to clean UTF-8 ASCII-safe text while preserving runtime logic.
- Lightning dependency strategy was previously implicit/silent:
  - DataModule inherited from `object` when import failed, with no explicit error at construction.
  - Resolution: added explicit runtime error on instantiation when `pytorch_lightning` is unavailable.
- `src/models/lit_module.py` previously used `LegacyLightningModule = None` when import failed.
  - Resolution: replaced with fail-fast placeholder class that raises a clear dependency error.
- Path-fit conclusion:
  - `lit_module` now has deterministic behavior in both dependency-present and dependency-missing environments, which aligns with Hydra migration diagnostics and reduces silent fallback ambiguity.

## Findings Update (2026-02-12, Run 5)

- Smoke validation:
  - Hydra path (`src/train.py`) succeeded with safe overrides (`train/load/eval` disabled, small dataset).
  - Legacy CLI path (`main.py run`) succeeded with equivalent overrides.
- Output-field parity:
  - Compared `Simulation.run_training()` return payload between:
    - legacy setup path (`setup_configuration`)
    - hydra setup path (`load_config + _build_legacy_overrides + apply_overrides`)
  - Result: `status_equal=True`, `key_sets_equal=True`
  - Key set in both paths: `['status', 'trained_model']`
- Integration test addition:
  - Added `tests/integration/test_hydra_bridge.py` covering:
    - transitional mapping (`data/trainer` -> `dataset/training`)
    - canonical group declarations in `configs/config.yaml`
- Environment note:
  - `pytest` is not installed in `doa`; tests were validated by direct module-function execution as fallback.
- New technical risk identified:
  - Naming collision persists between file `src/train.py` and package directory `src/train/`, requiring path-based import in tooling/tests.

## Findings Update (2026-02-12, Run 6)

- README previously pointed to outdated entry usage (`python -m src.train run ...`) that no longer represented the Hydra-first path.
- Updated documentation now reflects production-safe current state:
  - Primary entry: `src/train.py` (Hydra)
  - Compatibility entry: `main.py` (Click)
- Added explicit migration map and known constraints to reduce onboarding and troubleshooting friction.
- Confirmed doc commands are executable in `doa` environment (`src/train.py --help`).

## Final Conclusion

- Lightning + Hydra unification plan phases 1-6 are now complete at implementation+validation+documentation level.
- System state after closure:
  - Hydra entry exists and is validated by smoke tests.
  - Canonical config path is established with archive indexing for historical configs.
  - Data/Model Lightning adapters are hardened with explicit dependency behavior.
  - Integration parity for core training return fields is validated against legacy path.
  - README and migration guide are aligned with current architecture.

## Findings Update (2026-02-12, Run 7)

- Started Phase 7 and completed item 7.1 (runtime takeover):
  - Added `configs/runtime/default.yaml` with `_target_: src.train.runtime_runner.SimulationRuntimeRunner`
  - Updated `configs/config.yaml` defaults to include `runtime: default`
  - Refactored `src/train.py` dispatch logic to instantiate runtime runner from Hydra config
- This establishes `_target_` ownership at the entrypoint control layer while preserving current simulation backend.
- Added/updated integration checks to enforce runtime target presence and config wiring.

## Findings Update (2026-02-12, Run 8)

- Native `_target_` instantiation now covers:
  - `cfg.data` -> `DataComponentFactory`
  - `cfg.model` -> `ModelComponentFactory`
  - `cfg.trainer` -> `TrainerComponentFactory`
- Legacy dependency reduction:
  - New default flow no longer starts from `legacy_config` by default path; it constructs `Config` directly from Hydra-composed values.
  - Legacy loader path remains as guarded fallback for backward compatibility.
- New integration risk uncovered:
  - Since `trajectory` is not part of current Hydra defaults tree, native path uses schema default (`trajectory.enabled=false`) unless user provides `+trajectory...` overrides.
  - In this mode, current standard dataset branch can hit existing backend signature mismatch (`create_dataset(... samples_model=...)`).
  - Practical workaround validated: `+trajectory.enabled=true` for smoke path.

## Findings Update (2026-02-12, Run 9)

- Native-first path exposed two backend compatibility issues; both were addressed:
  1) DCD_MUSIC `create_dataset` signature mismatch (`samples_model` vs `system_model_params`).
     - Resolution: compatibility call pattern with preferred modern signature and TypeError fallback.
  2) Non-trajectory dataset object lacks `get_dataloaders`.
     - Resolution: fallback splitting in `Simulation._run_data_pipeline` using `random_split + DataLoader`.
- Namespace collision mitigation:
  - Previous pain point: `src/train.py` file name collided with `src/train/` package for imports.
  - Resolution: moved importable Hydra logic to `src/train_entry.py` and kept `src/train.py` as execution wrapper.
  - Outcome: tooling/tests can import `src.train_entry` directly without path-based hacks.

## Findings Update (2026-02-12, Run 10)

- Phase 7.4 migration strategy adopted: incremental by data mode.
  - First target: non-trajectory path (lower coupling, easier contract).
  - Trajectory path remains on legacy trainer for now.
- Lightning path result:
  - `training.use_lightning=true` + `training.epochs=1` smoke run in `doa` completed successfully.
  - Model checkpoint save + pipeline result save remained intact.
- Compatibility hardening done during migration:
  - Avoid legacy trainer factory invocation when Lightning path is enabled.
  - Fixed source-count handling in Lightning fallback objective (batched tensor -> scalar source count for model forward).
  - Fixed canonical-vs-transitional precedence so `training.epochs` is not overwritten by `trainer.max_epochs` mapping.
- Residual issue observed:
  - Console emits GBK unicode logging errors from external Lightning tip message (emoji). Training still succeeds; this is a logging-encoding noise issue.

## Findings Update (2026-02-12, Run 11)

- Trajectory Lightning migration is now functional for current far-field trajectory flow:
  - Command validated in `doa` env:
    - `+trajectory.enabled=true`
    - `training.use_lightning=true`
    - `training.epochs=1`
  - Run completed with `Hydra run finished: success` and model save.
- Implementation approach:
  - Extended `LegacyLightningModule` to detect trajectory batches and unroll step-wise loss/validation over trajectory length.
  - Reused model-native hooks when available; fallback objective remains MSE-based for compatibility.
- Residual technical debt:
  - External Lightning tip logging emits Unicode errors under GBK console encoding; non-blocking but noisy.
  - Near-field trajectory branch remains conservative fallback in `Simulation` and should be addressed in subsequent refinement.

## Findings Update (2026-02-12, Run 12)

- Milestone 2 (trajectory -> Lightning) is reproducible in `doa` on CPU with current config stack.
- Observed behavior:
  - Training and validation loops run through full epoch on trajectory data.
  - Checkpoint save and pipeline completion are intact.
- Residual non-blocking issue:
  - Console logging still shows GBK UnicodeEncodeError from external Lightning tip message containing emoji ("💡").
  - This does not break training result or exit status.

## Findings Update (2026-02-12, Run 13)

- Root cause for previous near-field failure was not Lightning itself; it was model contract mismatch:
  - near-field + `esprit` is invalid at model initialization.
  - near-field `music_1D` may require `known_angles` in forward path.
- Fix strategy:
  - Keep Lightning as orchestration layer and adapt fallback objective in `LegacyLightningModule` to near-field label reality (trajectory labels currently angle-only).
  - When range targets are unavailable, use angle-only fallback and known-angles-compatible forward path.
- Logging issue status:
  - GBK `UnicodeEncodeError` from Lightning tip emoji ("💡") is resolved by rank-zero logger suppression in trainer setup.
- Validation outcome:
  - far-field trajectory + Lightning: PASS
  - near-field trajectory + Lightning (`model.params.diff_method=music_1D`): PASS

## Findings Update (2026-02-12, Run 14)

- Directory-level documentation sync completed for `docs/plan/plan_lightning_hydra`.
- Status alignment:
  - `task_plan.md` top-level phase marker updated to `Completed (Phase 1-7)`.
  - Added explicit closure snapshot section to reduce ambiguity for future sessions.
- Migration guide alignment:
  - Added near-field trajectory Lightning command example with compatible overrides.
