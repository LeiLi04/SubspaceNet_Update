# Task Plan: Theme B/C/D Evidence Upgrade (Numeric + Strong Citations)

## Metadata
- Created At: `2026-02-19 16:23:00 UTC`
- Last Updated At: `2026-02-19 16:36:00 UTC`

## Goal
把 `docs/literature/review_skeleton.md` 中主题 B/C/D 的段落从“可用”升级到“可投稿”，补齐可追溯的**关键数值证据**并在段落中以 `[@Rxx]` 强引用。

## Scope
- Target themes: B/C/D
- Target papers (priority): R42/R43/R44/R45（跟踪与系统级证据），以及补强 B/C 的代表性深度方法（R03/R08）。
- Outputs:
  - Update extraction rows: `docs/literature/data_extraction_template.md`
  - Update text: `docs/literature/thematic_draft.md` and `docs/literature/review_skeleton.md`
  - Rebuild: `docs/literature/review_skeleton.pdf`
  - Evidence artifacts: `docs/literature/plan_theme_evidence_BCD_2026-02-19/`

## Phases

### Phase 1: Collect Numeric Evidence (tables/figures)
- [x] R42 Table I runtime numbers (WGMM vs Hist-WGMM).
- [x] R43 Table 2 time cost numbers (VSBL vs VSBLKF/OGVSBLKF).
- [x] R45 Fig.7 RMSE vs SNR (digitized, approximate).
- [x] R44 Fig.8 RMSE vs SNR (digitized, approximate; 3 cases).
- [x] R03 (SDOA-Net) key RMSE improvement statement (SNR=10 dB).
- [x] R08 (SubspaceNet) Table I coherent-source RMSPE numbers.
- **Status:** complete

### Phase 2: Update Extraction Table Rows
- [x] Patched R42–R45 notes/results with extracted numbers + evidence paths.
- **Status:** complete

### Phase 3: Update Theme Paragraphs B/C/D
- [x] Injected numeric evidence into Theme B/C (R03/R08).
- [x] Injected numeric evidence into Theme D (R42–R45).
- [x] Synced into `review_skeleton.md` and refreshed `thematic_draft.md`.
- **Status:** complete

### Phase 4: Build PDF + Sanity Check
- [x] Rebuilt `review_skeleton.pdf` and verified citations/figures resolve.
- **Status:** complete

## Decisions Made
| Decision | Rationale |
|---|---|
| Prefer tables when available; use figure-digitization only as approximate evidence | Reduce risk of overclaim; keep traceability via saved crops/overlays |
| Keep digitized values labeled as “approx/digitized” in text | Reviewer-facing honesty; prevents false precision |

## Errors Encountered
| Error | Attempt | Resolution |
|---|---:|---|
| Misused `pdf_to_text.py` (output path treated as input PDF) | 1 | Re-ran with `--out-dir` |
