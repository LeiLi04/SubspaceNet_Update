# Task Plan: Lightning + Hydra `_target_` Migration (Phase 1-3)

## Metadata
- Created At: `2026-02-24 17:43:26 +0100`
- Last Updated At: `2026-02-24 18:04:27 +0100`

## Goal
Complete Phase 1-3 migration to native Lightning modules and direct Hydra `_target_` instantiation for model/data/trainer, with standard training routed through `pl.Trainer.fit(model, datamodule)`.

## Phases
| Phase | Status | Notes |
|---|---|---|
| 1. Implement model-specific LightningModules | completed | Added `SubspaceNetLightning` and `DCDMusicLightning` with explicit params + `save_hyperparameters()` |
| 2. Convert config groups to direct `_target_` | completed | Added `configs/model/subspacenet.yaml` + `dcd_music.yaml`; updated data/trainer defaults |
| 3. Switch runtime wiring to direct Hydra instantiation | completed | `src/train_entry.py` now instantiates system_model/datamodule/model/trainer directly |
| 4. Route training through Lightning Trainer + DataModule | completed | Simulation/training pipeline now uses instantiated Lightning components and `trainer.fit(..., datamodule=...)` |
| 5. Deprecate factory wrappers (no deletion) | completed | Marked component factories as deprecated and stopped using them in entrypoint |
| 6. Validate migration | completed | Integration tests passed; SubspaceNet 1-epoch Lightning smoke run passed; DCD-MUSIC instantiate smoke passed |

## Constraints
- Hydra `_target_` only for DI in active training path.
- No new registry/factory layers.
- Keep online-learning path separate from standard Trainer fit loop.
