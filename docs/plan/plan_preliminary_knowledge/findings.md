# Findings

## Metadata
- Created At: `2026-02-18 17:21:00 +0100`
- Last Updated At: `2026-02-18 17:27:20 +0100`

## Context
- Source material: `docs/preliminary_knowledge.md`
- Target artifact: `notebooks/preliminary.ipynb`

## Content decisions
- Notebook mode: tutorial-style self-study.
- Kept code deterministic with fixed random seed.
- Added four technical sections:
  1. Narrowband criterion (`B * Delta_tau`)
  2. ULA steering vector example
  3. MUSIC covariance/EVD/pseudospectrum
  4. Wideband mismatch peak broadening demo
- Implemented wideband mismatch using fixed center-frequency steering with true multi-frequency sources.

## Validation observations
- Notebook JSON parsed successfully.
- All code cells executed successfully in sequence.
- Wideband mismatch demo shows broader peak than narrowband reference.

## Update Log
- `2026-02-18 17:21:00 +0100` Recorded context, design decisions, and validation notes.
- `2026-02-18 17:27:20 +0100` Added metadata timestamps and timestamping convention.
