# Literature Review (SubspaceNet_Update)

本目录用于撰写“可提交版”的相关工作/文献综述，面向本仓库主题：
非平稳/动态场景下的 DOA 估计与跟踪（SubspaceNet + EKF/KF + 在线/无监督自适应）。

快速入口：
- `review_skeleton.md`：可直接填充的综述主文骨架（含章节结构与写作占位符）。
- `review_skeleton.pdf`：由 `review_skeleton.md` 生成的 PDF（含目录与引用处理）。
- `search_strategy.md`：多数据库检索策略与可复制的检索式模板（含记录表）。
- `search_run_2026-02-19.md`：一次真实检索的运行记录（seed set + 记录限制说明）。
- `screening_criteria.md`：纳排标准与筛选记录规范（PRISMA 占位符）。
- `title_abstract_screening.csv`：基于导出去重结果的标题/摘要自动筛选清单（可人工复核）。
- `title_abstract_screening_summary.md`：标题/摘要筛选统计与排除原因统计（自动口径）。
- `title_abstract_screening_v2.csv`：标题/摘要自动筛选清单（v2，严格匹配 DOA+Kalman 查询）。
- `title_abstract_screening_v2_summary.md`：标题/摘要筛选汇总（v2）。
- `data_extraction_template.md`：数据抽取表单模板（建议每篇文献一行）。
- `figures.md`：图示清单与推荐图内容（含 mermaid 占位图）。
- `thematic_draft.md`：主题 A–E 的初稿段落（可直接并入综述）。
- `exports/`：数据库导出文件投递目录（用于正式 PRISMA/去重/引用库生成）。

建议工作流（最小可复现）：
1. 明确研究问题（review_skeleton.md: “研究问题与范围”）。
2. 按 search_strategy.md 执行至少 3 个库检索并记录日志。
3. 依 screening_criteria.md 做去重与分层筛选（标题/摘要/全文）。
4. 用 data_extraction_template.md 抽取关键字段，按主题综合写结果。
5. 生成图示（figures.md）并在正文引用。
