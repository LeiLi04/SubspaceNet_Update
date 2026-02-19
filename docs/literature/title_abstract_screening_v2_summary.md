# Title/Abstract Screening Summary (Auto v2: Query-Scoped)

- Input exports: `docs/literature/exports_dedup.json`
- Input screening v1: `docs/literature/title_abstract_screening.csv`
- Output screening v2: `docs/literature/title_abstract_screening_v2.csv`

## PRISMA (Auto v2, export scope)
- Records identified (exports): n = 632
- Duplicates removed (exports): n = 34
- Records after duplicates removed (exports): n = 598
- Records screened (title/abstract): n = 598
- Excluded after title/abstract (auto v2): n = 441
- Included after title/abstract (auto v2): n = 157
- Needs manual review (auto v2): n = 0

## Reason Codes (Auto v2)
| Code | Count |
|---|---:|
| E_NOT_DOA | 238 |
| I_DOA_TRACK | 157 |
| E_KALMAN_NO_DOA | 120 |
| E_DOA_NO_KALMAN | 49 |
| E_ARRAY_NO_DOA_TRACK | 34 |

## Notes
- v2 resolves all prior REVIEW rows by enforcing the DOA+Kalman query scope.
- Final PRISMA still benefits from spot-checking borderline cases.
