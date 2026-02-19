#!/usr/bin/env python3
"""
Second-pass auto screening.

Goal: resolve REVIEW rows by enforcing the *query scope*:
  - must mention DOA/AoA AND Kalman/EKF/UKF/particle/innovation/residual/tracking

This is appropriate when your actual database query is "Direction of arrival" AND "Kalman Filter".
"""

from __future__ import annotations

import csv
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Tuple


DOA_PAT = re.compile(r"\b(doa|aoa)\b|direction[- ]of[- ]arrival|angle[- ]of[- ]arrival", re.IGNORECASE)
TRACK_PAT = re.compile(r"\bkalman\b|\bekf\b|\bukf\b|\bparticle filter\b|tracking|innovation|residual", re.IGNORECASE)
RADAR_ARRAY_PAT = re.compile(r"\bradar\b|\bsonar\b|\bantenna\b|\barray\b|\bbeamforming\b|\bsubspace\b", re.IGNORECASE)


def _norm_title(title: str) -> str:
    title = (title or "").strip().lower()
    title = re.sub(r"\s+", " ", title)
    title = re.sub(r"[^a-z0-9 ]+", "", title)
    return title.strip()


def key_from_row(row: Dict[str, str]) -> Tuple[str, str]:
    doi = (row.get("doi") or "").strip().lower()
    if doi:
        return ("doi", doi)
    arx = (row.get("arxiv") or "").strip().lower()
    if arx:
        return ("arxiv", arx)
    return ("title", _norm_title(row.get("title") or ""))


def text_from_unique(u: Dict[str, Any]) -> str:
    title = (u.get("title") or "").strip()
    extra = u.get("extra") or {}
    ab = ""
    if isinstance(extra, dict):
        ab = (extra.get("AB") or "").strip()
    combined = re.sub(r"\s+", " ", " ".join([title, ab])).strip()
    return combined


def load_unique_map(exports_dedup_json: Path) -> Dict[Tuple[str, str], Dict[str, Any]]:
    obj = json.loads(exports_dedup_json.read_text(encoding="utf-8"))
    m: Dict[Tuple[str, str], Dict[str, Any]] = {}
    for u in obj.get("unique", []):
        k = (u.get("dedup_key_kind", ""), u.get("dedup_key", ""))
        if k[0] and k[1]:
            m[(k[0], str(k[1]).strip().lower())] = u
    return m


def main() -> int:
    base = Path("docs/literature")
    in_csv = base / "title_abstract_screening.csv"
    in_json = base / "exports_dedup.json"
    out_csv = base / "title_abstract_screening_v2.csv"
    out_md = base / "title_abstract_screening_v2_summary.md"

    unique_map = load_unique_map(in_json)

    rows: List[Dict[str, str]] = []
    with in_csv.open(newline="", encoding="utf-8") as f:
        rd = csv.DictReader(f)
        for row in rd:
            rows.append(dict(row))

    counts = Counter()
    reason_counts = Counter()

    for row in rows:
        prev_dec = row.get("decision", "")
        row["prev_decision"] = prev_dec
        row["prev_reason_code"] = row.get("reason_code", "")

        if prev_dec != "REVIEW":
            counts[prev_dec] += 1
            reason_counts[row.get("reason_code", "")] += 1
            continue

        k_kind, k_val = key_from_row(row)
        u = unique_map.get((k_kind, k_val))
        text = ""
        if u:
            text = text_from_unique(u)
        else:
            # fall back to snippet
            text = (row.get("title", "") + " " + row.get("abstract_snippet", "")).strip()

        has_doa = bool(DOA_PAT.search(text))
        has_track = bool(TRACK_PAT.search(text))
        has_array = bool(RADAR_ARRAY_PAT.search(text))

        if has_doa and has_track:
            row["decision"] = "INCLUDE"
            row["reason_code"] = "I_QUERY_DOA_KALMAN"
            row["reason"] = "Matches query scope: DOA/AoA + Kalman/tracking terms."
        else:
            row["decision"] = "EXCLUDE"
            if has_doa and not has_track:
                row["reason_code"] = "E_DOA_NO_KALMAN"
                row["reason"] = "DOA present but no Kalman/tracking terms; excluded for DOA+Kalman query scope."
            elif has_track and not has_doa:
                row["reason_code"] = "E_KALMAN_NO_DOA"
                row["reason"] = "Kalman/tracking present but no DOA/AoA terms; excluded for DOA+Kalman query scope."
            elif has_array:
                row["reason_code"] = "E_ARRAY_NO_QUERY_MATCH"
                row["reason"] = "Array/radar context but does not match DOA+Kalman query scope."
            else:
                row["reason_code"] = "E_NOT_QUERY_MATCH"
                row["reason"] = "Does not match DOA+Kalman query scope."

        counts[row["decision"]] += 1
        reason_counts[row["reason_code"]] += 1

    # write v2 csv
    fieldnames = list(rows[0].keys()) if rows else []
    with out_csv.open("w", newline="", encoding="utf-8") as f:
        wr = csv.DictWriter(f, fieldnames=fieldnames)
        wr.writeheader()
        wr.writerows(rows)

    # summary
    obj = json.loads(in_json.read_text(encoding="utf-8"))
    identified = int(obj.get("records_total", 0))
    dedup = int(obj.get("unique_total", 0))
    dups = int(obj.get("duplicates_total", 0))

    include_n = counts.get("INCLUDE", 0)
    exclude_n = counts.get("EXCLUDE", 0)
    review_n = counts.get("REVIEW", 0)

    lines: List[str] = []
    lines.append("# Title/Abstract Screening Summary (Auto v2: Query-Scoped)\n\n")
    lines.append(f"- Input exports: `docs/literature/exports_dedup.json`\n")
    lines.append(f"- Input screening v1: `docs/literature/title_abstract_screening.csv`\n")
    lines.append(f"- Output screening v2: `docs/literature/title_abstract_screening_v2.csv`\n")
    lines.append("\n## PRISMA (Auto v2, export scope)\n")
    lines.append(f"- Records identified (exports): n = {identified}\n")
    lines.append(f"- Duplicates removed (exports): n = {dups}\n")
    lines.append(f"- Records after duplicates removed (exports): n = {dedup}\n")
    lines.append(f"- Records screened (title/abstract): n = {dedup}\n")
    lines.append(f"- Excluded after title/abstract (auto v2): n = {exclude_n}\n")
    lines.append(f"- Included after title/abstract (auto v2): n = {include_n}\n")
    lines.append(f"- Needs manual review (auto v2): n = {review_n}\n")
    lines.append("\n## Reason Codes (Auto v2)\n")
    lines.append("| Code | Count |\n|---|---:|\n")
    for code, cnt in reason_counts.most_common():
        if not code:
            continue
        lines.append(f"| {code} | {cnt} |\n")
    lines.append("\n## Notes\n")
    lines.append("- v2 resolves all prior REVIEW rows by enforcing the DOA+Kalman query scope.\n")
    lines.append("- Final PRISMA still benefits from spot-checking borderline cases.\n")
    out_md.write_text("".join(lines), encoding="utf-8")

    print(f"Wrote {out_csv} and {out_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

