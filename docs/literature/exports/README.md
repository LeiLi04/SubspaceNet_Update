# Export Drops (IEEE/Scopus/WoS)

把你从各数据库导出的检索结果文件放在这里，便于后续去重、统计 PRISMA、以及自动生成引用库。

## 推荐导出格式
- IEEE Xplore: `RIS` 或 `BibTeX`
- Scopus: `RIS` 或 `BibTeX`（包含 DOI/abstract 更好）
- Web of Science: `RIS` 或 `Tab-delimited/CSV`（Full Record）

## Web of Science 注意事项
- `refine.xlsx`/`analyze results` 这类文件通常是“分面统计”（例如 `Publication Years_Count`），不是论文记录列表，无法用于去重与 PRISMA 的去重链路。
- 需要导出“论文记录列表”：
  - 在 WoS 结果页点 `Export` / `Save to ...`
  - 选择 `Full Record and Cited References`（或至少 `Full Record`）
  - 文件格式选 `Tab-delimited (Win)` 或 `Excel`/`CSV`
  - 确保包含 `Title`、`DOI`、`Year`、`Source`、`Authors` 等字段

## 同步记录（很重要）
每个库导出时，请在同名 `.txt` 里记录下面 4 项（用于正式 PRISMA）：
- total hits（数据库页面显示的命中总数）
- applied filters（年份范围、文献类型、语言等）
- export count（本次导出的条目数；如果分批导出，写每批）
- query（你实际输入的检索式）

示例：`ieee_xplore_2026-02-19.txt`
