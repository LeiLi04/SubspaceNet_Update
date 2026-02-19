# Findings: Strong Evidence Gap Fix

## Metadata
- Created At: `2026-02-19 16:48:00 UTC`
- Last Updated At: `2026-02-19 16:55:00 UTC`

## S13 Fulltext Status
- DOI landing resolves to IEEE Xplore doc `4217602`, but automated retrieval is blocked (HTTP 418 / bot protection).
- Action needed: user downloads PDF via subscription in browser/Zotero and saves to:
  - `docs/literature/fulltext/subscription/10.1109_icassp.2007.366429.pdf`
- After PDF arrives: re-run full-text screening and update PRISMA (Final-25 assessed/included) if S13 is included.

## R32 Strong Evidence (Digitized From Fig.3)
Paper: R32 (ICICSP 2025), DOI `10.1109/ICICSP66564.2025.11338321`.

Digitized artifact note:
- `docs/literature/plan_strong_evidence_gapfix_2026-02-19/R32_fig3_digitized_key_numbers.md`

Key numbers (digitized approximate; Fig.3 RMSE vs time, noise window 3600–4000 s):
- EKF: median ~3.309 deg, p95 ~4.443 deg
- SH-EKF: median ~1.965 deg, p95 ~3.078 deg
- VB-EKF: median ~1.809 deg, p95 ~2.974 deg
- FD-EKF: median ~1.026 deg, p95 ~1.365 deg

Debug evidence paths:
- Plot crop: `docs/literature/plan_strong_evidence_gapfix_2026-02-19/R32_fig3_graph_only.png`
- Mask overlay: `docs/literature/plan_strong_evidence_gapfix_2026-02-19/R32_fig3_curve_masks_v2.png`

## Data Extraction Hygiene
- R39 cell contained `ŝ[-1|-1]` which breaks markdown table columns; fixed by escaping `|` as `\\|` in `docs/literature/data_extraction_template.md`.

