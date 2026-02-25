# Findings: Full architecture-design Template Alignment

## Metadata
- Created At: 2026-02-24
- Last Updated At: 2026-02-24T23:31:58+01:00

## Key Findings

### 1. DCD_MUSIC still depends on `src/*` proxy modules

A direct scan of `DCD_MUSIC/src` shows many absolute imports like:
- `from src.system_model import ...`
- `from src.signal_creation import ...`
- `from src.models import ...`
- `from src.methods import ...`
- `from src.criterions import ...`
- `from src.models_pack.*` and `from src.methods_pack.*`

Conclusion:
- root-level `src/*` compatibility proxy files cannot be fully removed yet.
- removing them breaks test collection/runtime imports.

### 2. Safe cleanup scope is narrower than initial plan draft

Safe removals completed:
- `src/train.py`
- `src/train_entry.py`
- empty legacy directories (`src/data`, `src/eval`, `src/train`, `src/models`)

Restored/retained for compatibility:
- DCD_MUSIC proxy shim modules under `src/` and `src/models_pack/`.

### 3. Config migration to `run/conf` is complete

- `configs/` was moved to `run/conf/`.
- all alignment-sensitive references were updated in:
  - tests
  - structure script
  - README
  - loader fallback path

### 4. Entrypoint migration is complete

- New canonical entrypoint: `run/pipeline/training/train.py`.
- old `src/train_entry.py` was removed.
- startup path now uses `config_path="../../conf"`.

### 5. Runtime compatibility gap in composed config

`Simulation` expects additional sections (`trajectory`, `kalman_filter`, `online_learning`, etc.)
that are not always present in current Hydra composition defaults.

Mitigation implemented:
- `run/pipeline/training/train.py` injects minimal defaults for missing runtime sections via `OmegaConf.merge`.
- This enabled no-train startup success for the required smoke command.

### 6. Project packaging modernization

- Added `pyproject.toml` with dependencies migrated from `requirements.txt`.
- Added hatch wheel package selection (`packages = ["src"]`) to make editable build resolvable.
- `uv sync` succeeds.

### 7. Test status after alignment changes

- Integration bridge test: passes (`5 passed`).
- Full suite under `uv`: still has 13 failing kalman-filter tests due existing API/test expectation mismatch.
- These failures are outside this structure-alignment scope and were not introduced by config/entrypoint migration.
