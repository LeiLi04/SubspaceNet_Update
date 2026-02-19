# Task Plan: Quality/Evidence Traceability Upgrade (Reviewer-Ready)

## Metadata
- Created At: `2026-02-19 17:04:58 +0100`
- Last Updated At: `2026-02-19 17:20:26 +0100`

## Goal
把 `data_extraction_template.md` 的“质量/证据追踪”升级到可审稿版本：对 Related Work 要强推的 8–12 篇关键纳入文献逐篇从全文核验（开源/消融/真实数据/漂移注入/关键超参），并把 `review_skeleton.md` 中关键结论落到可追溯的 `Table/Fig/Exp` 证据锚点。

## Current Phase
Phase 1

## Phases

### Phase 1: Requirements & Discovery
- [x] 锁定口径：PRISMA A（exports=632 -> dedup=598 -> title/abstract(v2)=157；Final-25: assessed=24, included=24, not retrieved=1=S13）
- [x] 确认输入集：优先核验 key set（12 篇）：R02, R29, R24, R26, R27, R33, R43, R45, R44, R42, R36, R06
- [x] 定位全文 PDF 路径并建立“证据锚点”抽取清单（页码+章节/图表号）
- **Status:** complete

### Phase 2: Planning & Structure
- [ ] 定义质量表字段口径（Yes/No/Partial/NS 的使用规则）
- [ ] 定义正文证据锚点规则（每个关键结论至少 1 个 Table/Fig/Exp，必要时允许 digitized approximate 并指向产物文件）
- **Status:** pending

### Phase 3: Implementation
- [ ] 逐篇核验 key set：开源、消融、真实数据、漂移/失配注入细节、关键超参（从全文定位）
- [ ] 回填 `data_extraction_template.md`：质量/可复现性小表 + 每篇 notes/evidence 字段
- [ ] 增强 `review_skeleton.md`：补齐所有关键结论的 Table/Fig/Exp 锚点与 [@Rxx]
- **Status:** in_progress

### Phase 4: Testing & Verification
- [ ] 全文一致性检查：`screening_criteria.md` vs `review_skeleton.md` PRISMA 数字不冲突
- [ ] grep 检查：key set 不应再出现 `NS/待核验/需核验`（除非明确标注原因）
- [ ] 重新生成 `review_skeleton.pdf`
- **Status:** pending

### Phase 5: Delivery
- [ ] 输出本次修改清单（文件级）+ 仍需用户补齐项（例如 S13 全文）
- **Status:** pending

## Key Questions
1. “开源/可复现”口径：只认论文明确给出 repo/代码链接（Yes），仅给出第三方工具或数据生成器链接记为 Partial？
2. key set 的最终名单是否需要缩到 8–10（更聚焦），还是保留 12（覆盖更全）？

## Decisions Made
| Decision | Rationale |
|----------|-----------|
| Evidence 允许 digitized approximate | 少数论文只有图，无表格数值；用可追溯图像产物+说明可审稿 |
| 开源 Yes 需论文明确 repo/链接 | 避免误判“open access/open_source”等假阳性 |

## Errors Encountered
| Error | Attempt | Resolution |
|-------|---------|------------|
| IEEE 自动下载被 418/反爬拦截（S13） | 1 | 需要用户用订阅手工下载 PDF 到指定目录 |

## Notes
- 上一步已完成：R32 Fig.3 数值 digitize（approx）并回填；R39 markdown 表格污染修复；S13 仍缺。
