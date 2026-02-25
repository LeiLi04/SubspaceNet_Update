# Task Plan: Full architecture-design Template Alignment

## Metadata
- Created At: 2026-02-24
- Last Updated At: 2026-02-24T23:31:58+01:00

## Goal

Complete full structure and workflow alignment with the architecture-design template after Phase 1-7 migration:
- clean legacy layers safely
- move Hydra config tree to `run/conf/`
- move runtime entrypoint to `run/pipeline/training/train.py`
- add modern project files (`pyproject.toml`, `Makefile`)

## Phases

| # | Phase | Status | Notes |
|---|---|---|---|
| A | `src/` legacy safety analysis | completed | verified transitive DCD_MUSIC imports still require several `src/*` compatibility proxies |
| B | `src/` legacy cleanup | completed | removed only safe targets; retained required DCD_MUSIC proxy files |
| C | `configs/ -> run/conf/` migration | completed | moved full Hydra config tree to `run/conf/` |
| D | entrypoint migration to `run/pipeline/` | completed | created `run/pipeline/training/train.py`, removed old `src/train_entry.py` |
| E | add `pyproject.toml` | completed | created pyproject + hatch target; `uv sync` succeeds |
| F | add `Makefile` | completed | added `train/test/lint/clean` targets |

## Phase A Summary

- Scanned `src/`, `tests/`, and `scripts` for direct shim imports.
- Scanned `DCD_MUSIC/src` for transitive absolute imports.
- Key result: DCD_MUSIC still imports:
  - `src.system_model`, `src.signal_creation`, `src.models`, `src.methods`, `src.criterions`, etc.
  - `src.models_pack.*` and `src.methods_pack.*`
- Decision: keep these compatibility proxies for runtime compatibility.

## Phase B Summary

Removed safe legacy items:
- `src/train.py`
- `src/train_entry.py`
- empty legacy directories: `src/data/`, `src/eval/`, `src/train/`, `src/models/`

Retained (required by DCD_MUSIC transitive imports):
- `src/criterions.py`, `src/data_handler.py`, `src/evaluation.py`, `src/methods.py`, `src/models.py`, `src/plotting.py`, `src/signal_creation.py`, `src/system_model.py`, `src/training.py`
- `src/models_pack/` compatibility proxies
- `src/methods_pack/` compatibility proxies

## Phase C + D Summary

- Moved `configs/` to `run/conf/`.
- Added package path files:
  - `run/__init__.py`
  - `run/pipeline/__init__.py`
  - `run/pipeline/training/__init__.py`
- Added new entrypoint:
  - `run/pipeline/training/train.py`
- Updated related paths and docs/tests:
  - `tests/integration/test_hydra_bridge.py`
  - `scripts/check_structure.sh`
  - `README.md`
  - `main.py` comment path
  - `config/loader.py` fallback config path
- Added runtime safeguard in new entrypoint to inject missing optional sections (`trajectory`, `kalman_filter`, etc.) when not composed.

## Phase E Summary

- Added `pyproject.toml` from `requirements.txt` dependencies.
- Added hatch wheel selection:
  - `[tool.hatch.build.targets.wheel]`
  - `packages = ["src"]`
- Validation: `uv sync` succeeded.

## Phase F Summary

- Added `Makefile` with targets:
  - `train`
  - `test`
  - `lint`
  - `clean`

## Validation

Executed:
- `python -m pytest -q tests/` (system Python): failed during collection due missing `torch` in system interpreter.
- `uv run python -m pytest -q tests/`: runs with deps, but 13 existing kalman-filter tests fail (pre-existing behavior mismatch, not introduced by this alignment change).
- `uv run python -m pytest -q tests/integration/test_hydra_bridge.py`: **5 passed**.
- `uv run python run/pipeline/training/train.py +scenario=training simulation.load_model=false simulation.train_model=false simulation.evaluate_model=false training.enabled=false dataset.samples_size=8`: **startup success** (exit code 0).

## Residual Risks

- Full test suite still has failing kalman-filter tests in current codebase.
- `make` command is not installed in this Windows shell, so `make test` command-level validation could not be run directly.
