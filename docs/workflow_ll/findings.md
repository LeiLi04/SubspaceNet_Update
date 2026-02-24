# Findings: architecture-design Skill Optimization

## Metadata
- Created At: 2026-02-24T15:00:00
- Last Updated At: 2026-02-24T19:45:00

## Key Findings

### Registry vs Hydra `_target_`

- They are **parallel solutions** (not layered) — both map string → class
- Registry: Python dict + `@register` decorator (no external deps)
- Hydra `_target_`: YAML path + `importlib` (requires Hydra)
- Current project uses Hydra `_target_` + manual if/elif factory, no Registry
- Adding Registry is cosmetic at 2 model types — real payoff at 10+
- **Decision**: Hydra `_target_` only — Registry removed entirely to avoid confusion

### Architecture Priority

- **Hydra `_target_` only** — no Registry/Factory pattern
- `hydra.utils.instantiate` is the sole instantiation mechanism
- YAML `_target_` declares class import path + params → Hydra creates the object
- Entry point (`train.py`) is generic: no specific model/data imports
- Model `__init__` uses explicit params (injected by Hydra), not a `cfg` object

### Merge result

- **Before**: your doc (Lightning + Hydra) vs Skill (raw PyTorch + Factory/Registry) — complementary but inconsistent
- **After (v2.0.0)**: Skill = Lightning + Hydra `_target_` only, single source of truth; `docs/constructure_schedule.md` deprecated

### Framework Choice: Lightning

- PyTorch Lightning chosen as standard framework
- No fatal compatibility issues; more concise than raw PyTorch
- Key abstractions: LightningModule (model), LightningDataModule (data), Trainer (training)
- Eliminates raw `for epoch in range(...)` loops

### Config Namespace Convention

- Model architecture params: `cfg.model.*` (matches model YAML file)
- Training/optimizer params: `cfg.training.*` (lives in `config.yaml`)
- Data params: `cfg.data.*` (matches data YAML file)
- Trainer params: `cfg.trainer.*` (matches trainer YAML file)

### `config/factory.py` current state

- Manual Factory with if/elif for 2 models (SubspaceNet, DCD-MUSIC)
- Models live in `DCD_MUSIC/` — user owns source code, can add decorators
- Uses `_instantiate_with_compatible_kwargs` for flexible init

### SKILL.md Consistency Fixes Applied

- Frontmatter scope expanded: was "ONLY Factory/Registry" → now covers full architecture (Lightning + Hydra + YAML configs)
- Config example aligned: model params in YAML, passed directly to `__init__` by Hydra
- Placeholder `_target_` paths annotated as "(example — adapt to your project)"
- Added `config.yaml` example showing defaults composition pattern
- v2.0.0: Removed all Registry/Factory/Auto-Import — Hydra `_target_` only
- Model `__init__` uses explicit params (injected by Hydra), not a `cfg` object
- Removed references to factory_pattern.md, registry_pattern.md, auto_import.md
- `rules/coding-style.md` also synced: Factory & Registry → Hydra `_target_`, nn.Module → pl.LightningModule
