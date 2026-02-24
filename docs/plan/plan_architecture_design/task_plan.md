# Task Plan: Lightning + Hydra _target_ Migration (Phase 1-3)

## Metadata
- Created At: 2026-02-24T17:43:26+0100
- Last Updated At: 2026-02-24T18:09:01+0100

## Goal

Complete Phase 1-3 migration on the current refactored layout (`src/model_module`, `src/data_module`, `src/trainer_module`):
- model-specific LightningModule wrappers with explicit params
- direct Hydra `_target_` instantiation for model/data/trainer
- standard training path through `pl.Trainer.fit(model, datamodule)`

## Current State Summary

Phase 1-3 core objectives are now implemented in active runtime path:
- `SubspaceNetLightning` and `DCDMusicLightning` exist and are Hydra-instantiable
- model/data/trainer config groups now use direct `_target_` classes
- `src/train_entry.py` instantiates model/datamodule/trainer directly
- simulation training path uses instantiated Lightning components and `trainer.fit(..., datamodule=...)`
- legacy factory classes are kept but marked deprecated

## Phases

| # | Phase | Status | Notes |
|---|-------|--------|------|
| 1 | LightningModule wrappers for models | completed | Added dedicated wrappers with explicit ctor params + `save_hyperparameters()` |
| 2 | Direct `_target_` in YAML configs | completed | Added per-model YAMLs and direct datamodule/trainer targets |
| 3 | Replace legacy trainer loop with `pl.Trainer.fit` for standard path | completed | Active training path now uses instantiated Lightning trainer + datamodule |

## Delivered Changes

### Phase 1

- Added:
  - `src/model_module/subspacenet_lightning.py`
  - `src/model_module/dcd_music_lightning.py`
- Both wrappers:
  - use explicit Hydra-injectable parameters
  - call `self.save_hyperparameters()`
  - create internal DCD_MUSIC model instances
  - expose optimizer/scheduler config via `configure_optimizers()`

### Phase 2

- Added model config files:
  - `configs/model/subspacenet.yaml`
  - `configs/model/dcd_music.yaml`
- Updated default model selection:
  - `configs/config.yaml` uses `model: subspacenet`
- Updated direct targets:
  - `configs/data/default.yaml` -> `src.data_module.lit_datamodule.DOADataModule`
  - `configs/trainer/default.yaml` -> `pytorch_lightning.Trainer`
- Kept `src/trainer_module/component_factories.py` and marked it deprecated.

### Phase 3

- `src/train_entry.py` now builds components via direct `hydra.utils.instantiate(...)`.
- `src/trainer_module/simulation/runner.py` and `training_pipeline.py` now use instantiated Lightning stack when present.
- Standard training execution goes through `trainer.fit(lightning_model, datamodule=datamodule)`.
- Online-learning path remains separate in simulation pipeline.

## Validation Summary

- Compile checks passed for updated Python modules.
- Integration checks passed:
  - `PYTHONPATH=. pytest -q tests/integration/test_hydra_bridge.py`
- Runtime smoke checks passed:
  - no-train training scenario
  - 1-epoch SubspaceNet Lightning training
  - DCD-MUSIC instantiate/no-train scenario

## Remaining Follow-up (outside this phase scope)

1. Remove any remaining compatibility fallbacks after downstream cleanup phases are complete.
2. Decide when to fully retire legacy factory/loader compatibility paths.

## Errors Encountered

- `TensorBoardLogger` failed in this environment due missing `tensorboard`; switched trainer logger to `CSVLogger`.
- DCD-MUSIC initialization required near-field system setting; wrapper now sets `system_model.params.field_type = "Near"` before model construction.
