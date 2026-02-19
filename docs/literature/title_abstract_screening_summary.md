# Title/Abstract Screening Summary (Auto)

- Input: `docs/literature/exports_dedup.json`
- Output checklist: `docs/literature/title_abstract_screening.csv`

## PRISMA (Auto, export scope)
- Records identified (exports): n = 632
- Duplicates removed (exports): n = 34
- Records after duplicates removed (exports): n = 598
- Records screened (title/abstract): n = 598
- Excluded after title/abstract (auto): n = 272
- Included after title/abstract (auto): n = 157
- Needs manual review (auto): n = 169

## Exclusion/Review Reasons (Auto)
| Code | Count |
|---|---:|
| E_NOT_DOA | 238 |
| I_DOA_TRACK | 157 |
| R_TRACK_ARRAY | 120 |
| R_DOA_ONLY | 49 |
| E_ARRAY_NO_DOA_TRACK | 34 |

## Notes
- This is heuristic and will over/under-include; use it to prioritize manual screening.
- Final PRISMA should be based on human-confirmed decisions (especially REVIEW rows).
