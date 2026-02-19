# Findings & Decisions (Fulltext v2)

## Metadata
- Created At: `2026-02-19 11:38:57 UTC`
- Last Updated At: `2026-02-19 12:11:45 UTC`

## Requirements
- 从三源导出（IEEE+Scopus+WoS）去重得到 export scope：identified=632, dedup=598。
- 标题/摘要筛选采用 v2（严格 DOA+Kalman 查询）：included=157（auto v2）。
- 从 157 中挑选 15–30 篇做全文获取与数据抽取，驱动综述定稿。

## Research Findings
- Export dedup：`docs/literature/exports_dedup_report.md`
- Auto screening v2：`docs/literature/title_abstract_screening_v2.csv` / `docs/literature/title_abstract_screening_v2_summary.md`
- 当前 references：`docs/literature/references.bib`（seed set R01–R23）
- v2 INCLUDE 集合的 top-30 短名单已生成：`docs/literature/plan_fulltext_v2/shortlist_30.md`
- 已优先抓取“明显 OA”PDF（可自动落盘的部分），清单见：`docs/literature/plan_fulltext_v2/oa_fulltext_manifest.md`
  - OK: `10.1038/s41598-025-03276-1` (Scientific Reports) -> `docs/literature/fulltext/oa/10.1038_s41598-025-03276-1.pdf`
  - OK: `10.3390/rs15020420` (MDPI Remote Sensing; via `mdpi-res.com`) -> `docs/literature/fulltext/oa/10.3390_rs15020420.pdf`
  - OK: `10.3390/fi6010155` (MDPI Future Internet; via `mdpi-res.com`) -> `docs/literature/fulltext/oa/10.3390_fi6010155.pdf`
  - Missing (needs manual): `10.14429/dsj.57.1772` (Defence Science Journal) -> OpenAlex 未提供直链 PDF
- 已对 4 份可用全文（3 OA + 1 本地 Konstantino PDF）做全文文本抽取并沉淀关键证据：
  - 文本缓存：`docs/literature/plan_fulltext_v2/fulltext_txt/`
  - 抽取表：`docs/literature/data_extraction_template.md`（R02/R06/R07 补齐，新增 R24）
  - 主题段落：`docs/literature/thematic_draft.md`（主题 A/D/E 增强并补充 `[@R06]`/`[@R07]`/`[@R24]`/`[@R02]`）
- 已从自动 top-30 短名单剔除明显跑题条目（定位/SLAM/非 DOA tracking），并从 v2 INCLUDE 池补齐至 25 篇：
  - `docs/literature/plan_fulltext_v2/shortlist_final_25.md`
- 已对 final-25 的 DOI 列表批量尝试 OA 全文抓取（OpenAlex `pdf_url` + 发布商兜底），并落盘新增 2 篇 OA：
  - Manifest: `docs/literature/plan_fulltext_v2/oa_fulltext_manifest_shortlist_final_25.md`（ok=5/22; blocked=1; missing=16）
  - 新增 OA PDF：
    - `docs/literature/fulltext/oa/10.1186_s13634-018-0541-0.pdf` (SpringerOpen/EURASIP)
    - `docs/literature/fulltext/oa/10.1109_twc.2021.3085753.pdf` (IEEE TWC; OpenAlex 指向 ielx PDF)

## Technical Decisions
| Decision | Rationale |
|----------|-----------|
| Shortlist 单独文件落盘 | 便于人工确认与后续全文抓取追踪 |
| Fulltext 目录分离 | 避免污染 `docs/reference_original/`，并保持综述材料集中 |

## Issues Encountered
| Issue | Resolution |
|-------|------------|
| WoS refine facets xlsx 不可用于去重 | 已自动忽略；使用 savedrecs.xls 记录表 |
| mdpi.com PDF 直链普遍 403 | 增加 `mdpi-res.com` 兜底路径（脚本自动） |

## Resources
- `docs/literature/plan_fulltext_v2/task_plan.md`
- `docs/literature/title_abstract_screening_v2.csv`
- `docs/literature/exports_dedup.json`
