# Findings & Decisions

## Metadata
- Created At: `2026-02-19 09:42:44 UTC`
- Last Updated At: `2026-02-19 09:50:10 UTC`

## Requirements
- 在仓库内建立“可提交版综述骨架”（已完成，位于 `docs/literature/`）。
- 执行一次真实检索：按 `docs/literature/search_strategy.md`，记录数据库/检索式/日期/结果数，输出检索运行记录。
- 将 `docs/reference_original/` 中现有论文（至少包含 Konstantino 那篇）按模板填入 `docs/literature/data_extraction_template.md`。
- 产出主题 A–E 的初稿段落（可直接并入综述正文）。

## Research Findings
- `docs/literature/` 已创建并包含：`review_skeleton.md`、`search_strategy.md`、`screening_criteria.md`、`data_extraction_template.md`、`figures.md`、`README.md`。
- `docs/reference_original/` 已包含至少 2 篇相关 PDF：Konstantino（innovation 驱动无监督适配）与 Weißer 2023（无监督参数估计相关）。
- 真实检索（2026-02-19）初步候选（来自公开 Web 检索聚合，未等价于数据库内“总命中数”）：
  - arXiv: SDOA-Net (2022) 关注 imperfect array 下的深度 DOA 估计（含代码）。
  - arXiv: supervised transfer learning 框架用于 array imperfections (2025)。
  - Signal Processing (ScienceDirect): learning-based robust DOA with array imperfections (2025)。
  - Scientific Reports: MUSIC 在阵元位置误差下的校正方法 (2025)。
- 本地全文种子集（`docs/reference_original/`）已抽取并填表：
  - R01: Weißer et al. (2023) 无监督 AE + model-based decoder（同时估计 DOA 与信号协方差）。
  - R02: Konstantino et al. (manuscript) 使用下游 Kalman innovation 触发并指导无监督在线适配（MSIE）。

## Technical Decisions
| Decision | Rationale |
|----------|-----------|
| 检索优先选公开可访问库（arXiv、Semantic Scholar、IEEE 入口） | 不依赖机构登录，便于复现 |
| 将检索结果单独落盘 `search_run_2026-02-19.md` | 保留可复现日志与后续 PRISMA 数字来源 |

## Issues Encountered
| Issue | Resolution |
|-------|------------|
| Scopus/WoS 可能需要机构权限 | 若不可用，使用公开入口替代并在方法学中声明限制 |
| Web 搜索工具不直接返回“总命中数” | 在 `search_run_2026-02-19.md` 明确记录“抓取条目数 K”并声明该限制；若需要精确命中数，需用各库 API/手工记录 |

## Resources
- `docs/literature/search_strategy.md`
- `docs/literature/search_run_2026-02-19.md`
- `docs/literature/data_extraction_template.md`
- `docs/literature/thematic_draft.md`
- `docs/reference_original/`

## Visual/Browser Findings
- （待补）真实检索页面/结果数与筛选信息将写入本节（2-Action Rule）。
