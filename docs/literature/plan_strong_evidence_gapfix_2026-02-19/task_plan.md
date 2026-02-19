# Task Plan: Strong Evidence Gap Fix (S13 + R32 digitization + table hygiene)

## Metadata
- Created At: `2026-02-19 16:48:00 UTC`
- Last Updated At: `2026-02-19 16:55:00 UTC`

## Goal
补齐“强证据缺口”并清零正文/抽取表中的“待核验”占位：
- S13：若能获取全文则补回 full-text assessed 并重新判定是否纳入（当前仍 missing）。
- R32：对 Fig.3 的关键指标进行图表数字化，替换 “数值需图中核验”。
- 修复抽取表中因 `|` 等字符导致的表格污染/断列（如 R39 的 `ŝ[-1|-1]`）。

## Phases
### Phase 1: S13 Fulltext Retrieval Attempt
- [x] Attempted direct DOI -> IEEE landing page; blocked by IEEE (HTTP 418 / bot protection).
- [ ] Waiting for user subscription download via browser/Zotero; expected path: `docs/literature/fulltext/subscription/10.1109_icassp.2007.366429.pdf`.
- **Status:** in_progress

### Phase 2: R32 Figure Digitization
- [x] Cropped Fig.3 plot and digitized key stats for the strong-noise window (3600–4000 s).
- [x] Saved debug artifacts and a key-number markdown note.
- **Status:** complete

### Phase 3: Extraction Table Hygiene Fix
- [x] Escaped `|` in R39 notes (`ŝ[-1\\|-1]`, `M[-1\\|-1]`) to prevent markdown table column breakage.
- **Status:** complete

### Phase 4: Global “Pending” Cleanup
- [x] Removed `pending digitization/需核验` placeholders for R32 in extraction and quality tables.
- **Status:** complete

## Outputs
- Digitization artifacts: `docs/literature/plan_strong_evidence_gapfix_2026-02-19/`
- Updated extraction: `docs/literature/data_extraction_template.md`

