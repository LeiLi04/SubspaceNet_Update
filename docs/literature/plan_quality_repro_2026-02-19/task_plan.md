# Task Plan: Quality Assessment + Evidence Trace Table

## Metadata
- Created At: `2026-02-19 16:41:00 UTC`
- Last Updated At: `2026-02-19 16:46:00 UTC`

## Goal
在 `docs/literature/data_extraction_template.md`（Quality/Evidence 字段）基础上：
1. 补一张“质量/可复现性”小表（开源/真实数据/消融/超参与漂移注入报告）。
2. 在 `docs/literature/review_skeleton.md` 正文中声明：关键结论的证据追踪到具体 `Table/Fig/Exp`，并引用抽取表的位置。

## Phases
### Phase 1: Build Quality/Repro Table (Included=24)
- [x] Derived per-paper flags for open-source / real-data / ablation / protocol / drift injection.
- [x] Added a compact table to `docs/literature/data_extraction_template.md`.
- **Status:** complete

### Phase 2: Wire Into Main Text
- [x] Added a short “evidence traceability” paragraph to `docs/literature/review_skeleton.md` (Methodology + Discussion).
- [x] Ensured key numeric claims mention Table/Fig/Exp where available.
- **Status:** complete

### Phase 3: Rebuild PDF
- [x] Rebuilt `docs/literature/review_skeleton.pdf`.
- **Status:** complete
