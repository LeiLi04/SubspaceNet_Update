# SubspaceNet Update

This repository has been refactored to follow the project layout defined in `Structure.md`.

## New working layout

- `configs/` now includes `config.yaml`, `default.yaml`, and grouped folders:
  - `configs/data/`
  - `configs/model/`
  - `configs/trainer/`
  - `configs/callbacks/`
- `src/` is now the primary source tree:
  - `src/data/`
  - `src/models/`
  - `src/train/`
  - `src/eval/`
  - `src/utils/`
- Artifact and documentation layers are standardized:
  - `outputs/{checkpoints,logs,figures}`
  - `figures/final/`
  - `docs/{plan,Data,problem_formulation,reference_original,reference_conclu,prompts}`

## Entrypoint

Use the new training entrypoint:

```bash
python -m src.train run -c configs/default_config.yaml
```

`src.train` currently proxies to the existing Click CLI in `main.py`, so old workflows continue to work while code migrates into `src/`.

## Migration strategy

1. Keep runtime behavior stable by preserving legacy modules.
2. Add compatibility wrappers under `src/`.
3. Move business logic incrementally from legacy paths into `src/`.
4. After full migration, retire compatibility wrappers.
