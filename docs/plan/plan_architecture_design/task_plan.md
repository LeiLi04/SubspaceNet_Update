# Task Plan: Refactor SubspaceNet_Update to architecture-design Template

## Metadata
- Created At: 2026-02-24T20:00:00
- Last Updated At: 2026-02-24T22:03:17+01:00

## Goal

Refactor the SubspaceNet_Update project to align with the architecture-design template:
- Lightning stack: LightningModule + LightningDataModule + pl.Trainer
- Hydra direct instantiation via `_target_`
- Modular file layout with files generally in 200-400 lines

## Phases

| # | Phase | Status | Notes |
|---|---|---|---|
| 1 | LightningModule wrappers for models | completed | Wrappers with explicit ctor args and `save_hyperparameters()` |
| 2 | Direct `_target_` in YAML configs | completed | data/model/trainer use direct Hydra targets |
| 3 | Replace legacy trainer with `pl.Trainer.fit` | completed | standard path uses instantiated Lightning stack |
| 4 | Decompose monolithic files | completed | simulation split complete; eval pipeline now split into two files |
| 5 | Unify config system (Pydantic vs Hydra) | completed | removed factory layers; retained loader for active scenario override path |
| 6 | Directory reorganization | completed | `data_module`, `model_module`, `trainer_module`, `eval_module` |
| 7 | Generic entry point | completed | `src/train_entry.py` reduced to 52 lines without bridge helpers |

## Phase 1: LightningModule Wrappers - completed

- Added:
  - `src/model_module/subspacenet_lightning.py`
  - `src/model_module/dcd_music_lightning.py`
- Both wrappers expose explicit Hydra-injectable args and use `save_hyperparameters()`.

## Phase 2: Direct `_target_` in YAML Configs - completed

- Added model configs:
  - `configs/model/subspacenet.yaml`
  - `configs/model/dcd_music.yaml`
- Updated default model selection and direct targets for data/trainer groups.

## Phase 3: Replace Legacy Trainer - completed

- `src/train_entry.py` and runtime pipeline instantiate data/model/trainer via `hydra.utils.instantiate(...)`.
- Standard training uses `trainer.fit(lightning_model, datamodule=datamodule)`.

## Phase 4: Decompose Monolithic Files - completed

Goal: split large simulation modules into smaller focused files.

Delivered:
- `src/trainer_module/simulation/eval_pipeline.py` reduced to 292 lines
- Added `src/trainer_module/simulation/eval_reporting.py` (167 lines)
- Moved evaluation metric aggregation/printing logic into `eval_reporting.py`

## Phase 5: Unify Config System - completed

Delivered:
1. Deleted `config/factory.py`
2. Deleted `src/trainer_module/component_factories.py`
3. Removed remaining `config.factory` runtime dependency in `src/trainer_module/online_learning_parts/pipeline_run.py`
4. Kept `config/loader.py` because `Simulation.run_scenario()` still uses `apply_overrides`; updated loader to support Hydra `DictConfig`

## Phase 6: Directory Reorganization - completed

Already completed before this pass.

## Phase 7: Generic Entry Point - completed

Goal: simplify `src/train_entry.py` to a thin Hydra entrypoint without legacy bridge helpers.

Delivered:
- removed `_build_legacy_overrides` and `_build_native_config`
- switched to `from config.utils import create_system_model`
- `src/train_entry.py` reduced from 224 lines to 52 lines
- updated integration test to validate bridge removal constraints

## Execution Order

Phase order executed:
1. Phase 4 completed
2. Phase 7 completed
3. Phase 5 completed

## Post-Execution Requirements

After each phase:
- update `task_plan.md`
- update `findings.md`
- append `progress.md`
- run `PYTHONPATH=. pytest -q tests/integration/test_hydra_bridge.py`

## Errors Encountered

- TensorBoard logger unavailable in environment; switched to CSV logger earlier.
- DCD-MUSIC initialization required near-field setting in wrapper constructor.

## Append Sync Log

### 2026-02-24T22:07:06+01:00

- Append-only sync requested for planning files.
- Phase status snapshot unchanged: Phase 1/2/3/4/5/6/7 are completed.
- No scope rollback or status regression was introduced in this sync.
