# Refactor Plan (Based on Structure.md)

## Completed in this pass

1. Added `src/` architecture with train/data/model/eval/utils layers.
2. Added `python -m src.train` entrypoint.
3. Added compatibility wrappers so legacy modules still run.
4. Added standard directories for docs, outputs, scripts, notebooks, figures.
5. Added grouped config folders and root config files aligned with the target layout.

## Next migration steps

1. Move training loop from `simulation/` into `src/train/`.
2. Replace compatibility wrappers with real `LightningModule` + `DataModule`.
3. Shift metric/loss logic into `src/eval/metrics/`.
4. Move reusable utilities from `utils/` into `src/utils/` and update imports.
5. Retire legacy entrypoint once CI/test coverage is green on `src/` only.
