# Progress Log (Fulltext v2)

## Metadata
- Created At: `2026-02-19 11:38:57 UTC`
- Last Updated At: `2026-02-19 13:52:12 UTC`

## Session: 2026-02-19

### Phase 1: Requirements & Discovery
- **Status:** complete
- **Started:** 2026-02-19 11:38:57 UTC
- Actions taken:
  - Initialized planning files under `docs/literature/plan_fulltext_v2/`
- Files created/modified:
  - `docs/literature/plan_fulltext_v2/task_plan.md` (created)
  - `docs/literature/plan_fulltext_v2/findings.md` (created)
  - `docs/literature/plan_fulltext_v2/progress.md` (created)

### Phase 2: Shortlist (15–30)
- **Status:** in_progress
- **Started:** 2026-02-19 11:40:20 UTC
- Actions taken:
  - Generated top-30 auto shortlist from v2 INCLUDE set
  - Started OA-first fulltext acquisition (MDPI/Nature OA endpoints)
  - Extracted fulltext text for 4 available PDFs and updated extraction + thematic drafts with evidence/citations
  - Refined auto top-30 by removing off-topic (localization/SLAM/etc) and filled to 25 with v2 INCLUDE pool
  - OA fulltext acquisition for final-25 DOI list via OpenAlex/pdf endpoints (batch manifest)
  - Ingested user-downloaded PDFs by theme, copied into `docs/literature/fulltext/subscription/`, extracted text, and generated full-text screening checklist
- Files created/modified:
  - `docs/literature/plan_fulltext_v2/shortlist_30.md` (created)
  - `docs/literature/scripts/fetch_oa_fulltext.py` (created/updated)
  - `docs/literature/plan_fulltext_v2/oa_targets_seed.txt` (created)
  - `docs/literature/plan_fulltext_v2/oa_fulltext_manifest.md` (created/updated)
  - `docs/literature/plan_fulltext_v2/oa_fulltext_manifest.json` (created/updated)
  - `docs/literature/fulltext/oa/10.1038_s41598-025-03276-1.pdf` (downloaded)
  - `docs/literature/fulltext/oa/10.3390_rs15020420.pdf` (downloaded)
  - `docs/literature/fulltext/oa/10.3390_fi6010155.pdf` (downloaded)
  - `docs/literature/fulltext/local/konstantino_unsupervised_adaptation_doa_estimators_downstream_tracking.pdf` (copied from reference_original)
  - `docs/literature/scripts/pdf_to_text.py` (created)
  - `docs/literature/plan_fulltext_v2/fulltext_txt/10.1038_s41598-025-03276-1.txt` (created)
  - `docs/literature/plan_fulltext_v2/fulltext_txt/10.3390_rs15020420.txt` (created)
  - `docs/literature/plan_fulltext_v2/fulltext_txt/10.3390_fi6010155.txt` (created)
  - `docs/literature/plan_fulltext_v2/fulltext_txt/konstantino_unsupervised_adaptation_doa_estimators_downstream_tracking.txt` (created)
  - `docs/literature/data_extraction_template.md` (updated: R02/R06/R07 enriched; R24 added)
  - `docs/literature/thematic_draft.md` (updated: A/D/E evidence + [@Rxx] citations)
  - `docs/literature/references.bib` (updated: R24 added)
  - `docs/literature/scripts/make_shortlist_final_25.py` (created)
  - `docs/literature/plan_fulltext_v2/shortlist_final_25.md` (created)
  - `docs/literature/plan_fulltext_v2/oa_targets_shortlist_final_25.txt` (created)
  - `docs/literature/plan_fulltext_v2/oa_fulltext_manifest_shortlist_final_25.md` (created)
  - `docs/literature/plan_fulltext_v2/oa_fulltext_manifest_shortlist_final_25.json` (created)
  - `docs/literature/fulltext/oa/10.1186_s13634-018-0541-0.pdf` (downloaded, OA)
  - `docs/literature/fulltext/oa/10.1109_twc.2021.3085753.pdf` (downloaded, OA via OpenAlex)
  - `docs/literature/plan_fulltext_v2/subscription_download_list_by_theme.md` (created)
  - `docs/literature/plan_fulltext_v2/fulltext_by_theme_inventory.md` (created)
  - `docs/literature/plan_fulltext_v2/fulltext_by_theme_inventory.json` (created)
  - `docs/literature/plan_fulltext_v2/fulltext_screening_checklist.md` (created/updated)
  - `docs/literature/plan_fulltext_v2/fulltext_screening_checklist_summary.md` (created/updated)
  - `docs/literature/scripts/make_fulltext_screening_checklist.py` (created)
  - `docs/literature/scripts/ocr_pdf_first_pages.py` (created)
  - `docs/literature/plan_fulltext_v2/fulltext_txt/IRSI2001_ocr_p1-2.txt` (created)
  - `docs/literature/screening_criteria.md` (updated: shortlist final-25 fulltext retrieval status)

## Test Results
| Test | Input | Expected | Actual | Status |
|------|-------|----------|--------|--------|
| plan files exist | ls docs/literature/plan_fulltext_v2 | 3 files | 3 files | ✓ |

| review pdf build | pandoc review_skeleton.md | pdf generated | review_skeleton.pdf updated | ✓ |

## Updates
- 2026-02-19: Finalized `docs/literature/plan_fulltext_v2/fulltext_screening_checklist.md` decisions for Final-25 (INCLUDE=24, EXCLUDE=1 due to E2 no full text).
- 2026-02-19: Identified missing S13 metadata: DOI `10.1109/ICASSP.2007.366429`, IEEE Xplore arnumber `4217602`; updated suggested filename to `docs/literature/fulltext/subscription/10.1109_icassp.2007.366429.pdf`.
