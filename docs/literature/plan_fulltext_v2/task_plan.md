# Task Plan: Full-Text Acquisition + Data Extraction (Post-PRISMA v2)

## Metadata
- Created At: `2026-02-19 11:38:57 UTC`
- Last Updated At: `2026-02-19 12:02:01 UTC`

## Goal
把 PRISMA v2（DOA+Kalman 查询）筛出的候选集合推进到“可写综述”的状态：完成 15–30 篇的全文获取、数据抽取与主题化综合材料沉淀，并更新综述正文与引用库。

## Current Phase
Phase 2

## Phases

### Phase 1: Requirements & Discovery
- [ ] 明确写作目标：综述需纳入的核心论文数量（目标 15–30）
- [ ] 明确筛选口径：PRISMA v2 作为主口径；v1 作为背景池
- [ ] 记录约束：全文可获取性（OA/机构订阅/作者版本）
- **Status:** complete

### Phase 2: Shortlist (15–30)
- [ ] 从 `title_abstract_screening_v2.csv` 的 INCLUDE 集合中挑选 15–30 篇（覆盖 classical/deep/model-based/online）
- [ ] 生成短名单文件（含 DOI/URL/来源库/摘要片段）
- [x] 优先抓取“明显 OA”全文（MDPI `mdpi-res.com`、Nature PDF 直链、arXiv 等），并落盘到 `docs/literature/fulltext/oa/`
- [x] 生成并维护 OA 获取清单：`docs/literature/plan_fulltext_v2/oa_fulltext_manifest.md`
- **Status:** in_progress

### Phase 3: Full-Text Acquisition
- [ ] 优先获取 arXiv/MDPI/开放获取版本 PDF
- [ ] 对需要订阅的条目，记录“获取方式”（IEEE/Scopus/WoS 下载、或替代版本）
- [ ] 将 PDF 放入 `docs/literature/fulltext/`（按 Paper ID 命名）
- **Status:** pending

### Phase 4: Data Extraction
- [ ] 为短名单每篇填充抽取字段（模型、漂移类型、触发器、损失、指标、结果）
- [x] 先对“已到手全文”做抽取：R02/R06/R07 + 新增 R24（Remote Sensing）
- [x] 更新 `docs/literature/data_extraction_template.md`（新增条目 ID 与字段）
- **Status:** in_progress

### Phase 5: Synthesis Draft Update
- [ ] 将主题 A–E 段落用短名单证据强化（具体对比点 + 引用）
- [x] 用 4 篇全文的证据增强主题 A/D/E（并补充 `[@Rxx]` 引用标注）
- [x] 更新 `docs/literature/review_skeleton.md` 与 PDF
- **Status:** in_progress

### Phase 6: Verification + Handoff
- [ ] 更新 PRISMA（full-text/included）为人工复核口径
- [ ] 更新 references.bib（为短名单补齐 BibTeX）
- **Status:** pending

## Key Questions
1. 15–30 篇短名单的选择标准：优先“DOA + tracking innovation/滤波耦合 + array mismatch/漂移”最直接相关工作，其余作为背景池。
2. 全文获取策略：优先 OA；订阅论文若无法拉取全文，用摘要+方法部分补齐并明确限制。

## Decisions Made
| Decision | Rationale |
|----------|-----------|
| PRISMA v2 做主口径 | 与实际检索关键词一致，口径可复现 |
| v1 保留为背景池 | 避免丢失 DOA-only 或 tracking-only 的有价值背景文献 |

## Errors Encountered
| Error | Attempt | Resolution |
|-------|---------|------------|
|       | 1       |            |
