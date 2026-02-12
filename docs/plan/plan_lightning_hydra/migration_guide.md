# Migration Guide: Legacy CLI to Hydra

This guide defines the supported migration path from legacy Click CLI commands to the Hydra-based entrypoint.

## Status

- Primary path: `src/train.py` (Hydra)
- Compatibility path: `main.py` (Click CLI)

## Entrypoints

- Hydra:

```bash
python src/train.py +scenario=training
```

- Legacy CLI:

```bash
python main.py run -c configs/default_config.yaml
```

## Override Mapping

| Legacy CLI (Click) | Hydra |
| --- | --- |
| `-O simulation.train_model=false` | `simulation.train_model=false` |
| `-O simulation.load_model=false` | `simulation.load_model=false` |
| `-O simulation.evaluate_model=false` | `simulation.evaluate_model=false` |
| `-O training.enabled=false` | `training.enabled=false` |
| `-O dataset.samples_size=8` | `dataset.samples_size=8` |

## Scenario Mapping

| Legacy intent | Hydra form |
| --- | --- |
| Training flow | `+scenario=training` |
| Evaluation flow | `+scenario=evaluation` |
| Online learning flow | `+scenario=online_learning` |
| Full pipeline | `+scenario=full` |

Notes:
- `scenario` is not in the base structured config, so use `+scenario=...`.
- Keep `configs/default_config.yaml` as legacy baseline through `legacy_config` bridge.

## Trajectory Lightning Examples

- Far-field trajectory, Lightning-native loop:

```bash
python src/train.py +scenario=training +trajectory.enabled=true training.use_lightning=true training.epochs=1 training.batch_size=2 simulation.train_model=true simulation.load_model=false simulation.evaluate_model=false dataset.samples_size=8
```

- Near-field trajectory, Lightning-native loop (near-field compatible override set):

```bash
python src/train.py +scenario=training +trajectory.enabled=true training.use_lightning=true training.epochs=1 training.batch_size=2 simulation.train_model=true simulation.load_model=false simulation.evaluate_model=false dataset.samples_size=8 +system_model.field_type=near +model.params.field_type=Near model.params.diff_method=music_1D
```

## Validation Checklist

1. `python src/train.py --help` succeeds in active environment.
2. Hydra smoke command completes with status `success`.
3. Legacy CLI smoke command still completes with status `success`.
4. Core result payload keys remain consistent (`status`, `trained_model`) for training smoke.

## Known Constraints

1. `src/train.py` file and `src/train/` package share the same base name, which can affect direct imports (`import src.train` resolves to package).
2. In such cases, tooling/tests may need path-based loading for `src/train.py`.
3. `pytest` may not be installed in some runtime environments; direct script assertions are an acceptable fallback for smoke validation.
