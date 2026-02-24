# Findings

## Metadata
- Created At: `2026-02-24 17:43:26 +0100`
- Last Updated At: `2026-02-24 18:04:27 +0100`

## Notes
- Runtime package layout in this branch is already renamed: `src/*_module` (not legacy `src/train`, `src/models`, etc.).
- `train_entry.py` required restoration of helper mapping functions (`_build_native_config`, `_build_legacy_overrides`) while keeping direct Hydra instantiation.
- `DCDMusicLightning` requires near-field `system_model` semantics; setting `system_model.params.field_type = "Near"` before `DCDMUSIC` construction prevents initialization failure.
- `TensorBoardLogger` failed in this environment due missing `tensorboard`; `CSVLogger` in trainer config removed that dependency.
