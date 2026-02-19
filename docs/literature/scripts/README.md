# Scripts

## `dedup_exports.py`

用于对 `docs/literature/exports/` 下的数据库导出文件（`.ris`/`.bib`）进行去重并生成 PRISMA 计数报告。

运行：
```bash
python docs/literature/scripts/dedup_exports.py
```

输出：
- `docs/literature/exports_dedup.json`：唯一条目 + 重复条目（含去重 key）
- `docs/literature/exports_dedup_report.md`：PRISMA-style 计数与按文件统计

## `auto_screen_exports.py`

基于 `docs/literature/exports_dedup.json` 做标题/摘要的启发式筛选，输出可人工复核的清单与排除原因统计。

运行：
```bash
python docs/literature/scripts/auto_screen_exports.py
```

输出：
- `docs/literature/title_abstract_screening.csv`
- `docs/literature/title_abstract_screening_summary.md`
