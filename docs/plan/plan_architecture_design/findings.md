# Findings: Refactor SubspaceNet_Update to architecture-design Template

## Metadata
- Created At: 2026-02-24T20:00:00
- Last Updated At: 2026-02-24T21:00:00

## Key Findings

### 1. Directory Layout Already Renamed

The active repository layout already uses renamed packages:
- `src/model_module`
- `src/data_module`
- `src/trainer_module`
- `src/eval_module`

Phase 6 (directory reorganization) was already done before this refactoring started. All work uses the `*_module` paths.

### 2. Model Wrappers Are Now Explicit and Direct (Phase 1)

New wrappers added for direct Hydra model instantiation:
- `src/model_module/subspacenet_lightning.py`
- `src/model_module/dcd_music_lightning.py`

Both wrappers:
- expose explicit constructor params (Hydra-injectable)
- call `save_hyperparameters()`
- build internal DCD_MUSIC model objects
- provide optimizer/scheduler via `configure_optimizers()`

### 3. Config Groups Moved to Direct _target_ Path (Phase 2)

Direct targets now used for model/data/trainer:
- model: `configs/model/subspacenet.yaml`, `configs/model/dcd_music.yaml`
- data: `configs/data/default.yaml` -> `src.data_module.lit_datamodule.DOADataModule`
- trainer: `configs/trainer/default.yaml` -> `pytorch_lightning.Trainer`

### 4. Entry and Training Orchestration Updated (Phase 3)

`src/train_entry.py` now:
- builds `Config` from composed Hydra config
- creates `system_model`
- instantiates datamodule/model/trainer directly with `hydra.utils.instantiate`
- passes components into `Simulation`

`src/trainer_module/simulation/training_pipeline.py` now uses:
- `trainer.fit(lightning_model, datamodule=datamodule)` when Lightning components present.

### 5. DCD-MUSIC Initialization Constraint

DCD-MUSIC wrapper needed near-field semantics at construction time. Setting:
- `system_model.params.field_type = "Near"`
inside `DCDMusicLightning.__init__` avoided initialization failure in MUSIC range-grid setup.

### 6. Logger Adjustment

`TensorBoardLogger` failed due to missing `tensorboard` package.
Trainer logger switched to `CSVLogger` for dependency-light runtime.

### 7. Legacy Layers Still Present (Phase 4-5 scope)

Deprecated but not yet removed:
- `src/trainer_module/component_factories.py` — marked deprecated, no longer in active path
- `config/factory.py` (433 lines) — manual if/elif factory, replaced by `_target_`
- `config/loader.py` — redundant conversion logic between Pydantic and Hydra
- `src/train_entry.py` still has legacy bridge code (~170 lines of overhead)

### 8. File Size Status

| File | Lines | Status |
|------|-------|--------|
| `src/trainer_module/training.py` | ~998 | Likely deprecated by Phase 3, needs verification |
| `config/factory.py` | 433 | To be deleted (Phase 5) |
| `config/schema.py` | 306 | Keep — valuable Pydantic validation |
| `src/train_entry.py` | 217 | To be simplified (Phase 7) |

### 9. Architecture Decision (from prior session)

- **Hydra `_target_` only** — no Registry, no Factory
- `hydra.utils.instantiate` is the sole instantiation mechanism
- Model `__init__` uses explicit params (injected by Hydra), not `cfg` object
- `self.save_hyperparameters()` + `self.hparams.*` for accessing params
- Documented in `~/.claude/skills/architecture-design/SKILL.md` v2.0.0
