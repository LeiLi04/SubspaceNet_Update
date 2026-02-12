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

Recommended entrypoint (Hydra):

```bash
python src/train.py +scenario=training
```

Legacy CLI entrypoint (compatibility path):

```bash
python main.py run -c configs/default_config.yaml
```

Hydra is now the primary config composition path. Legacy CLI remains available for compatibility and rollback.

## Environment

- Python dependencies are listed in `requirements.txt`.
- Minimum critical packages for the new main path:
  - `torch`
  - `hydra-core`
  - `pytorch-lightning`
- Recommended runtime validation:

```bash
python -m py_compile src/train.py src/data/lit_datamodule.py src/models/lit_module.py
python src/train.py --help
```

If using conda:

```bash
conda activate doa
python src/train.py --help
```

## Typical Commands

Hydra training smoke (safe mode, no model load/train/eval):

```bash
python src/train.py +scenario=training simulation.load_model=false simulation.train_model=false simulation.evaluate_model=false training.enabled=false dataset.samples_size=8
```

Legacy CLI equivalent smoke:

```bash
python main.py run -c configs/default_config.yaml -O simulation.load_model=false -O simulation.train_model=false -O simulation.evaluate_model=false -O training.enabled=false -O dataset.samples_size=8
```

## CLI-to-Hydra Migration Map

| Legacy CLI | Hydra |
| --- | --- |
| `main.py run -c configs/default_config.yaml` | `src/train.py +scenario=training` |
| `-O simulation.train_model=false` | `simulation.train_model=false` |
| `-O simulation.load_model=false` | `simulation.load_model=false` |
| `-O dataset.samples_size=8` | `dataset.samples_size=8` |

Detailed migration notes: `docs/plan/plan_lightning_hydra/migration_guide.md`

## Migration strategy

1. Keep runtime behavior stable by preserving legacy modules.
2. Add compatibility wrappers under `src/`.
3. Move business logic incrementally from legacy paths into `src/`.
4. After full migration, retire compatibility wrappers.
