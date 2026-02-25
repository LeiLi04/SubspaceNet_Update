# SubspaceNet Update

This repository uses Hydra for the primary training pipeline and keeps the legacy CLI for compatibility.

## Project Layout

- `run/conf/`:
  - `run/conf/config.yaml`
  - `run/conf/{data,model,trainer,callbacks,runtime,training,...}`
- `run/pipeline/training/train.py`: primary Hydra entrypoint
- `src/` core modules:
  - `src/data_module/`
  - `src/model_module/`
  - `src/trainer_module/`
  - `src/eval_module/`

## Entrypoints

Primary (Hydra):

```bash
python run/pipeline/training/train.py +scenario=training
```

Legacy CLI path:

```bash
python main.py run -c run/conf/default_config.yaml
```

## Environment

Dependencies are listed in `requirements.txt`.

Quick syntax/runtime checks:

```bash
python -m py_compile run/pipeline/training/train.py src/data_module/lit_datamodule.py src/model_module/lit_module.py
python run/pipeline/training/train.py --help
```

## Typical Commands

Hydra no-train smoke:

```bash
python run/pipeline/training/train.py +scenario=training simulation.load_model=false simulation.train_model=false simulation.evaluate_model=false training.enabled=false dataset.samples_size=8
```

Legacy CLI equivalent:

```bash
python main.py run -c run/conf/default_config.yaml -O simulation.load_model=false -O simulation.train_model=false -O simulation.evaluate_model=false -O training.enabled=false -O dataset.samples_size=8
```

## CLI-to-Hydra Migration Map

| Legacy CLI | Hydra |
| --- | --- |
| `main.py run -c run/conf/default_config.yaml` | `run/pipeline/training/train.py +scenario=training` |
| `-O simulation.train_model=false` | `simulation.train_model=false` |
| `-O simulation.load_model=false` | `simulation.load_model=false` |
| `-O dataset.samples_size=8` | `dataset.samples_size=8` |
