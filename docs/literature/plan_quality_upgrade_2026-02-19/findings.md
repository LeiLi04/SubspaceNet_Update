# Findings & Decisions

## Metadata
- Created At: `2026-02-19 17:04:58 +0100`
- Last Updated At: `2026-02-19 17:13:36 +0100`

## Requirements
- 升级 `data_extraction_template.md` 的质量/证据追踪到“可审稿”级别（重点：强推 8–12 篇）。
- `review_skeleton.md` 中每个关键结论都要落到 `Table/Fig/Exp` 证据锚点，并用 `[@Rxx]` 标注。

## Research Findings
- R02 (Konstantino) 在正文明确给出代码/超参的 GitHub 链接：`https://github.com/UliKonstantin/SubspaceNet`。
- R45 里的 “open_source” 命中为假阳性（指 DOI/彩色版本链接），不能算代码开源。
- R32 仅图表提供对比，需要 digitize 并明确标注为 approximate。
- 已将 key set 的全文抽取文本落到本次计划目录：`/Users/lilei/PycharmProjects/SubspaceNet_Update/docs/literature/plan_quality_upgrade_2026-02-19/text/`，并清理了含 NUL 字节的提取文本（生成 `_clean.txt`）以支持可重复的关键字核验。

## Technical Decisions
| Decision | Rationale |
|----------|-----------|
| 质量字段用 Yes/No/Partial/NS | 让审稿人一眼看出证据强弱；NS 仅用于全文未报告 |
| 证据锚点写法统一为 `Sec.X / Fig.Y / Table Z / Exp` | 方便复核；跨版本也不容易失效 |

## Issues Encountered
| Issue | Resolution |
|-------|------------|
| S13 全文缺失 | 需用户用订阅下载；否则 PRISMA 保持 not retrieved=1 |
| markdown 表格被 `|` 污染 | 表格单元内 `|` 必须转义成 `\\|` |

## Resources
- `/Users/lilei/PycharmProjects/SubspaceNet_Update/docs/literature/plan_quality_audit_2026-02-19/evidence_audit_key_papers.md`
- `/Users/lilei/PycharmProjects/SubspaceNet_Update/docs/literature/plan_strong_evidence_gapfix_2026-02-19/R32_fig3_digitized_key_numbers.md`

## Visual/Browser Findings
- R32 Fig.3: FD-EKF 曲线在 3600–4000s 强噪段仍显著低于 EKF/SH-EKF/VB-EKF；已 digitize 记录典型时间点 RMSE（deg）。
- key set 的“证据锚点”已能稳定落到 Table/Fig/Exp：例如 R26 的 Fig.3 + Table 1/2（ABEE 与 one-step time），R33 的 Fig.1/2（EM 迭代与网格分辨率）与停止准则（norm-delta<1e-8 或 max 25），R06 的 Data availability（按 request 获取数据）与 Table 6/runtime（i5-12500）。
