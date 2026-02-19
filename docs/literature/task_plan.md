# Task Plan: Literature Review (Search + Extraction + Thematic Draft)

## Metadata
- Created At: `2026-02-19 09:42:44 UTC`
- Last Updated At: `2026-02-19 09:50:10 UTC`

## Goal
在 `docs/literature/` 形成可提交的综述工作流落地：完成一次真实多库检索并记录；将 `docs/reference_original/` 现有论文按模板抽取；产出主题 A-E 的初稿段落，便于直接并入综述正文。

## Current Phase
Phase 1

## Phases

### Phase 1: Record Previous Step + Requirements
- [x] 记录“已生成 docs/literature 综述骨架”到 planning 文件
- [x] 明确本轮交付物（真实检索记录、抽取表、主题初稿）
- **Status:** complete

### Phase 2: Real Search Run (Multi-Database)
- [ ] 按 `docs/literature/search_strategy.md` 执行真实检索（优先公开可访问库）
- [ ] 记录每个库的执行日期、检索式、过滤条件与结果数
- [ ] 输出 `docs/literature/search_run_2026-02-19.md`
- **Status:** complete

### Phase 3: Screening Seed Set (Local PDFs)
- [ ] 枚举 `docs/reference_original/` 中可用论文（PDF/MD）
- [ ] 为每篇生成 1-2 句方法与实验摘要（用于主题段落）
- **Status:** complete

### Phase 4: Data Extraction Table
- [ ] 将已存在论文填入 `docs/literature/data_extraction_template.md`
- [ ] 增补必要字段（venue/shift/trigger/loss 等）
- **Status:** complete

### Phase 5: Thematic Draft A–E
- [ ] 产出主题 A-E 初稿段落（可直接粘贴进综述）
- [ ] 存到 `docs/literature/thematic_draft.md` 并在 `review_skeleton.md` 标注插入点
- **Status:** complete

### Phase 6: Verification + Handoff
- [ ] 检查文档链接、占位符、可读性
- [ ] 更新 planning 文件状态与进度日志
- **Status:** complete

## Key Questions
1. 本轮“真实检索”优先数据库：公开可访问库为主（arXiv、Semantic Scholar、IEEE Xplore 入口），Scopus/WoS 若无权限则以公开入口替代并注明限制。
2. 主题 A-E 初稿以“可复现协议与信号设计”视角组织，优先对齐本仓库（SubspaceNet + EKF + innovation-consistency + 在线适配）。

## Decisions Made
| Decision | Rationale |
|----------|-----------|
| 优先检索 arXiv + Semantic Scholar + IEEE 入口 | 公开可访问、可复现；Scopus/WoS 可能需要机构权限 |
| 主题初稿单独文件输出 | 便于后续合并进 `review_skeleton.md` 并迭代 |

## Errors Encountered
| Error | Attempt | Resolution |
|-------|---------|------------|
|       | 1       |            |

## Notes
- 遵循 planning-with-files 的 2-Action Rule：每完成 2 次检索/浏览操作就写入 `findings.md`。
