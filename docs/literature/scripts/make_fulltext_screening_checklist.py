#!/usr/bin/env python3
"""Create a full-text screening checklist from shortlist_final_25.md.

Outputs:
  - docs/literature/plan_fulltext_v2/fulltext_screening_checklist.md
  - docs/literature/plan_fulltext_v2/fulltext_screening_checklist_summary.md
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from pathlib import Path

ROOT = Path('/Users/lilei/PycharmProjects/SubspaceNet_Update')
IN_MD = ROOT / 'docs/literature/plan_fulltext_v2/shortlist_final_25.md'
OUT_MD = ROOT / 'docs/literature/plan_fulltext_v2/fulltext_screening_checklist.md'
OUT_SUMMARY = ROOT / 'docs/literature/plan_fulltext_v2/fulltext_screening_checklist_summary.md'


@dataclass
class Row:
    sid: str
    title: str
    year: str
    venue: str
    doi: str
    source: str
    oa: str
    fulltext_field: str
    notes: str


def parse_shortlist(path: Path) -> list[Row]:
    rows: list[Row] = []
    for line in path.read_text(encoding='utf-8').splitlines():
        if not line.startswith('| S'):
            continue
        parts = [x.strip() for x in line.strip().strip('|').split('|')]
        if len(parts) < 9:
            continue
        rows.append(Row(
            sid=parts[0],
            title=parts[1],
            year=parts[2],
            venue=parts[3],
            doi=parts[4],
            source=parts[5],
            oa=parts[6],
            fulltext_field=parts[7],
            notes=parts[8],
        ))
    return rows


def extract_path(fulltext_field: str) -> str:
    m = re.search(r"`([^`]+)`", fulltext_field)
    return m.group(1) if m else ''


def main() -> int:
    rows = parse_shortlist(IN_MD)
    if not rows:
        raise SystemExit('No rows parsed from shortlist_final_25.md')

    have = 0
    need = 0

    out_lines: list[str] = []
    out_lines.append('# Full-Text Screening Checklist (Final-25)\n')
    out_lines.append('来源：`shortlist_final_25.md`。\n')
    out_lines.append('说明：`Fulltext status` 为自动检测；`Decision/Reason` 需要人工最终确认（我会在你确认口径后写入 PRISMA）。\n')
    out_lines.append('| ID | DOI | Year | Title | Venue | Fulltext status | File | Decision | Exclusion reason | Notes |')
    out_lines.append('|---|---|---:|---|---|---|---|---|---|---|')

    for r in rows:
        p = extract_path(r.fulltext_field)
        abs_p = (ROOT / p).resolve() if p else None
        exists = abs_p.exists() if abs_p else False
        status = 'HAVE' if exists else 'NEED'
        if exists:
            have += 1
        else:
            need += 1
        out_lines.append(
            f"| {r.sid} | {r.doi} | {r.year} | {r.title.replace('|','\\|')} | {r.venue.replace('|','\\|')} | {status} | `{p}` | TBD |  | {r.notes.replace('|','\\|')} |"
        )

    OUT_MD.write_text('\n'.join(out_lines).rstrip() + '\n', encoding='utf-8')

    OUT_SUMMARY.write_text(
        '\n'.join([
            '# Full-Text Screening Checklist Summary\n',
            f'- total shortlist items: {len(rows)}',
            f'- fulltext available (HAVE): {have}',
            f'- fulltext missing (NEED): {need}',
            '',
            'Next: fill `Decision` and (if excluded) `Exclusion reason`, then update PRISMA numbers in screening_criteria.md.',
            ''
        ]),
        encoding='utf-8'
    )

    print(OUT_MD)
    print(OUT_SUMMARY)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
