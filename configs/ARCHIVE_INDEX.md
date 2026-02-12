# Config Archive Index

This index marks historical config folders that are kept for reproducibility and backward compatibility.

## Canonical Entry (Recommended)

- Hydra main entry: `configs/config.yaml`
- Legacy baseline fallback: `configs/default_config.yaml` (via `legacy_config` bridge)

## Archive Folders

### `configs/Legacy/`

Status: archived (do not use as default for new runs)

Typical use:
- old nonlinear tracking experiments
- old eta scenario experiments

### `configs/Used_for_paper/`

Status: archived (paper reproduction only)

Typical use:
- exact paper-level experiment replay
- SNR sweep / online learning variants used for publication figures

## Migration Notes

1. Prefer Hydra overrides against `configs/config.yaml`.
2. Keep archived file names unchanged for traceability.
3. If an archived config is still needed, run through legacy CLI path and record the reason.

## Ownership Rule

- New experiments: add/update canonical groups under `configs/` (for example `system_model/`, `dataset/`, `training/`, `simulation/`, `model/`).
- Archived experiments: no structural edits unless a reproducibility fix is required.

