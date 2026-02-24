# Task Plan: Refactor SubspaceNet_Update to architecture-design Template

## Metadata
- Created At: 2026-02-24T20:00:00
- Last Updated At: 2026-02-24T21:00:00

## Goal

Refactor the SubspaceNet_Update project to fully comply with the `architecture-design` skill (v2.0.0):
- **Lightning**: LightningModule + LightningDataModule + pl.Trainer
- **Hydra**: direct `_target_` instantiation (no factory wrappers)
- **Structure**: modular, 200-400 line files

## Phases

| # | Phase | Status | Notes |
|---|-------|--------|------|
| 1 | LightningModule wrappers for models | completed | Dedicated wrappers with explicit ctor params + `save_hyperparameters()` |
| 2 | Direct `_target_` in YAML configs | completed | Per-model YAMLs and direct datamodule/trainer targets |
| 3 | Replace legacy trainer with `pl.Trainer.fit` | completed | Standard training path uses Lightning trainer + datamodule |
| 4 | Decompose monolithic files | pending | core.py (~1430 lines) + training.py (~998 lines) |
| 5 | Unify config system (Pydantic vs Hydra) | pending | Remove redundant factory/loader layers |
| 6 | Directory reorganization | completed | Already renamed: `data_module`, `model_module`, `trainer_module`, `eval_module` |
| 7 | Generic entry point | pending | Simplify `train_entry.py` to template pattern |

## Phase 1: LightningModule Wrappers — completed

- Added:
  - `src/model_module/subspacenet_lightning.py`
  - `src/model_module/dcd_music_lightning.py`
- Both wrappers:
  - use explicit Hydra-injectable parameters
  - call `self.save_hyperparameters()`
  - create internal DCD_MUSIC model instances
  - expose optimizer/scheduler config via `configure_optimizers()`

## Phase 2: Direct `_target_` in YAML Configs — completed

- Added model config files:
  - `configs/model/subspacenet.yaml`
  - `configs/model/dcd_music.yaml`
- Updated default model selection:
  - `configs/config.yaml` uses `model: subspacenet`
- Updated direct targets:
  - `configs/data/default.yaml` -> `src.data_module.lit_datamodule.DOADataModule`
  - `configs/trainer/default.yaml` -> `pytorch_lightning.Trainer`
- Kept `src/trainer_module/component_factories.py` and marked it deprecated.

## Phase 3: Replace Legacy Trainer — completed

- `src/train_entry.py` now builds components via direct `hydra.utils.instantiate(...)`.
- `src/trainer_module/simulation/runner.py` and `training_pipeline.py` now use instantiated Lightning stack.
- Standard training execution goes through `trainer.fit(lightning_model, datamodule=datamodule)`.
- Online-learning path remains separate in simulation pipeline.

### Validation (Phase 1-3)

- `PYTHONPATH=. pytest -q tests/integration/test_hydra_bridge.py` (passed)
- no-train runtime scenario (passed)
- 1-epoch SubspaceNet Lightning training run (passed)
- DCD-MUSIC instantiate/no-train scenario (passed)

## Phase 4: Decompose Monolithic Files — pending

**Goal**: Split large files into 200-400 line modules.

**Targets**:
- `src/trainer_module/simulation/runner.py` (if still monolithic after Phase 3 changes) → composition-based split:
  - `data_pipeline.py` — data preparation
  - `training_pipeline.py` — training orchestration (may already exist)
  - `eval_pipeline.py` — evaluation logic
  - `online_learning.py` — online adaptation
- `src/trainer_module/training.py` (~998 lines) → likely deprecated by Phase 3, verify and clean up

## Phase 5: Unify Config System — pending

**Goal**: Remove redundant config layers.

**Plan**:
1. `config/factory.py` (433 lines) → delete (replaced by Hydra `_target_` in Phase 2)
2. `config/loader.py` → simplify or remove redundant conversion logic
3. `config/schema.py` → keep Pydantic validation for complex signal processing params
4. Remove deprecated `src/trainer_module/component_factories.py`

## Phase 6: Directory Reorganization — completed

Already done. Active layout:
- `src/data_module/`
- `src/model_module/`
- `src/trainer_module/`
- `src/eval_module/`

## Phase 7: Generic Entry Point — pending

**Goal**: Simplify `src/train_entry.py` (217 lines) to template pattern.

**Target** (~30-50 lines):
```python
@hydra.main(config_path="../configs", config_name="config", version_base=None)
def main(cfg: DictConfig) -> None:
    dm = hydra.utils.instantiate(cfg.data)
    model = hydra.utils.instantiate(cfg.model)
    trainer = hydra.utils.instantiate(cfg.trainer)
    trainer.fit(model, dm)
```

**Depends on**: Phase 5 complete (remove legacy bridge code).

## Execution Order

```
Phase 1-3 (Lightning migration) ✅ completed
    ↓
Phase 4 (decompose files) → Phase 5 (unify config) → Phase 7 (entry point)
Phase 6 (directory rename) ✅ already done
```

## Post-Execution Requirements

After each phase execution, update these planning files:
- `task_plan.md` — mark phase status, record delivered changes
- `findings.md` — record new discoveries and constraints
- `progress.md` — append session log entry

## Errors Encountered

- `TensorBoardLogger` failed due to missing `tensorboard`; switched to `CSVLogger`.
- DCD-MUSIC initialization required near-field system setting; wrapper sets `system_model.params.field_type = "Near"`.
