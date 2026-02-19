# Export Dedup Report
## PRISMA (database export scope)
- Records identified (exports): n = 632
- Duplicates removed: n = 34
- Records after duplicates removed: n = 598

## By Source File
| Source | Total | Unique | Duplicates |
|---|---:|---:|---:|
| ieee_xplore_2026-02-19_05-59-34.csv | 17 | 17 | 0 |
| ieee_xplore_2026-02-19_06-02-26.csv | 555 | 538 | 17 |
| scopus_2026-02-19.csv | 10 | 7 | 3 |
| wos_savedrecs_2026-02-19.xls | 50 | 36 | 14 |

## Diagnostics
- Unique records missing title: 0
- Unique records missing DOI and arXiv id: 29

## Notes
- Dedup keys: DOI > arXiv id > normalized title.
- Use this report to fill `docs/literature/screening_criteria.md` with official export-based counts.
