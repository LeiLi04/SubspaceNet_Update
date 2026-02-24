# Task Plan: Optimize architecture-design Skill

## Metadata
- Created At: 2026-02-24T15:00:00
- Last Updated At: 2026-02-24T19:45:00

## Goal

Merge `docs/constructure_schedule.md` (project-specific, Lightning-oriented) into `~/.claude/skills/architecture-design/SKILL.md` (generic ML template), making the skill the single source of truth for all ML project architecture.

## Architecture Decision

**Hydra `_target_` only — no Registry.**
- Hydra `_target_` + `hydra.utils.instantiate` is the sole DI mechanism
- Registry/Factory pattern removed entirely to avoid confusion
- Components instantiated directly via YAML `_target_` + `hydra.utils.instantiate`

## Comparison Items

| # | Aspect | Status |
|---|--------|--------|
| 1 | Directory structure | ✅ complete |
| 2 | Framework → Lightning | ✅ complete |
| 3 | Config → Hydra `_target_` instantiation | ✅ complete |
| 4 | ~~Factory/Registry + Auto-import~~ → removed | ✅ v2.0.0: Hydra `_target_` only |
| 5 | Model → LightningModule | ✅ complete (with #2) |
| 6 | Data → LightningDataModule | ✅ complete (with #2) |
| 7 | ~~Auto-import~~ → removed | ✅ removed with #4 in v2.0.0 |
| 8 | Code style | ✅ covered by `rules/coding-style.md` |
| 9 | Config management | ✅ merged into #3 |
| 10 | Code generation rules | ✅ merged into #3 |

## Phase Details

### Phase 1: Directory Structure ✅ complete

- Merged both — user's annotation clarity + skill's broader coverage
- Added: Makefile, notebooks/, tests/, scripts/, per-file comments, config examples, outputs detail
- Kept skill's broader `src/` coverage: augmentation/, collate_fn/, compute_metrics/
- Removed project-specific items: brain_decoder/, llm/, data_func/, prepare_data/

### Phase 2: Framework → Lightning ✅ complete

- Decision: PyTorch Lightning as standard framework
- Updated Overview section with Lightning + Hydra tech stack
- Updated Model template to LightningModule with training_step, validation_step, configure_optimizers
- Updated Data template to two-layer: raw Dataset + LightningDataModule

### Phase 3: Config → Hydra `_target_` ✅ complete

- Added Hydra rules: no argparse, no hardcoded params, no raw training loops
- Added YAML `_target_` examples for model, data, trainer, config.yaml
- Added generic entry point pattern with hydra.utils.instantiate
- Merged items #9 (config management) and #10 (code generation rules) here

### Phase 4: Factory/Registry + Auto-import → removed in v2.0.0

- Initially implemented canonical `__init__.py` template (Registry + Factory + Auto-Import)
- User decided to use Hydra `_target_` exclusively — all Registry/Factory/Auto-Import removed
- Final state: no Registry, no Factory, no Auto-Import; Hydra `_target_` is sole DI

### Phase 5-6: Model/Data → Lightning ✅ complete (with Phase 2)

### Phase 7: Auto-import → removed with Phase 4 in v2.0.0

### Phase 8: Code style ✅ covered

- Already handled by `rules/coding-style.md`
- Added "DO NOT write raw training loops" rule to skill (Lightning-implied)

## Post-Merge Fixes ✅ complete

- Fixed frontmatter scope (was too narrow, only Factory/Registry)
- Fixed config example inconsistency (learning_rate placement)
- Annotated placeholder _target_ paths as examples
- Removed all Registry/Factory/Auto-Import content — Hydra `_target_` only (v2.0.0)
- Model `__init__` now uses explicit params (injected by Hydra), not `cfg` object
- Synced `rules/coding-style.md`: Factory & Registry → Hydra `_target_`, nn.Module → pl.LightningModule

## Errors Encountered

(none)
