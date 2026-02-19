# Task Plan: Upgrade Quality/Evidence Traceability (Reviewer-Ready)

## Metadata
- Created At: `2026-02-19 17:00:00 UTC`
- Last Updated At: `2026-02-19 17:00:00 UTC`

## Goal
把 “质量/证据追踪” 从 NS 占比高的粗表升级为 **可审稿** 版本：
- 对 Related Work 强推的关键纳入文献（约 8–12 篇）逐篇核验：开源/消融/真实数据/漂移注入/关键超参，并给出证据锚点（page + Table/Fig/Exp）。
- 正文中涉及这些强结论的位置补齐 “Table/Fig/Exp” 锚点（优先写明 Table/Fig 编号；否则标注 Exp 并指向抽取表证据列）。

## Phases
### Phase 1: Evidence Audit (Key Papers)
- [x] Generate key-paper evidence audit with page-level snippets for open-source / real-data / ablation hints.
- **Status:** complete

### Phase 2: Upgrade Quality Table Rows (Key Papers)
- [ ] Replace `NS` in the “质量/可复现性小表（Included=24）” for key papers with reviewer-ready values: `Yes/No/Partial` + anchors.
- **Status:** in_progress

### Phase 3: Wire Evidence Anchors Into Main Text
- [ ] Ensure each strong claim in `review_skeleton.md` carries a `Table/Fig/Exp` anchor (e.g., add Fig.11 for R03; add code availability note for R02).
- **Status:** pending

### Phase 4: Rebuild PDF
- [ ] Rebuild `docs/literature/review_skeleton.pdf`.
- **Status:** pending

