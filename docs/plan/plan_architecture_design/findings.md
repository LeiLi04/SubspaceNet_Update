# Findings: Lightning + Hydra _target_ Migration (Phase 1-3)

## Metadata
- Created At: 2026-02-24T17:43:26+0100
- Last Updated At: 2026-02-24T18:09:01+0100

## Key Findings

### 1. Runtime Layout Reality

The active repository layout already uses renamed packages:
- `src/model_module`
- `src/data_module`
- `src/trainer_module`

All migration work had to be applied on this layout (not legacy `src/models`, `src/data`, `src/train` paths).

### 2. Model Wrappers Are Now Explicit and Direct

New wrappers were added for direct Hydra model instantiation:
- `src/model_module/subspacenet_lightning.py`
- `src/model_module/dcd_music_lightning.py`

Both wrappers:
- expose explicit constructor params (Hydra-injectable)
- call `save_hyperparameters()`
- build internal DCD_MUSIC model objects
- provide optimizer/scheduler via `configure_optimizers()`

### 3. Config Groups Moved to Direct _target_ Path

Direct targets are now used for model/data/trainer:
- model:
  - `configs/model/subspacenet.yaml`
  - `configs/model/dcd_music.yaml`
- data:
  - `configs/data/default.yaml` -> `src.data_module.lit_datamodule.DOADataModule`
- trainer:
  - `configs/trainer/default.yaml` -> `pytorch_lightning.Trainer`

### 4. Entry and Training Orchestration Updated

`src/train_entry.py` now:
- builds `Config` from composed Hydra config
- creates `system_model`
- instantiates datamodule/model/trainer directly with `hydra.utils.instantiate`
- passes components into `Simulation`

`src/trainer_module/simulation/training_pipeline.py` now uses:
- `trainer.fit(lightning_model, datamodule=datamodule)`
when instantiated Lightning components are present.

### 5. Compatibility Kept, but Deprecated

`src/trainer_module/component_factories.py` is retained but marked deprecated.
The active path no longer depends on component factory wrappers.

### 6. DCD-MUSIC Initialization Constraint

DCD-MUSIC wrapper needed near-field semantics at construction time. Setting:
- `system_model.params.field_type = "Near"`
inside `DCDMusicLightning.__init__` avoided initialization failure in MUSIC range-grid setup.

### 7. Environment-Driven Logger Adjustment

`TensorBoardLogger` failed in this environment due missing `tensorboard` package.
Trainer logger switched to `CSVLogger` to keep runtime path dependency-light and stable.

### 8. Verification Outcome

Verified successfully:
- integration target assertions
- no-train runtime path
- 1-epoch Lightning fit for SubspaceNet
- DCD-MUSIC instantiate/no-train runtime path

Phase 1-3 migration objectives are met for the standard training path.
