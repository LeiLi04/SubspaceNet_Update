#!/usr/bin/env python3
"""
Auto-screen deduplicated export records (title/abstract) for a DOA+Kalman/Tracking literature review.

Inputs:
  - docs/literature/exports_dedup.json (from dedup_exports.py)

Outputs:
  - docs/literature/title_abstract_screening.csv  (row-per-record, editable)
  - docs/literature/title_abstract_screening_summary.md (counts + exclusion reasons)

This is a *suggestion engine*:
  - Always treat outputs as "needs human review" before final PRISMA reporting.
"""

from __future__ import annotations

import csv
import json
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Tuple


DOA_PAT = re.compile(r"\b(doa|aoa)\b|direction[- ]of[- ]arrival|angle[- ]of[- ]arrival", re.IGNORECASE)
TRACK_PAT = re.compile(r"\bkalman\b|\bekf\b|\bukf\b|\bparticle filter\b|tracking|innovation|residual", re.IGNORECASE)

# Helpful "non-target" patterns to avoid over-including generic tracking/localization papers.
RADAR_SONAR_PAT = re.compile(r"\bradar\b|\bsonar\b|\bantenna\b|\barray\b|\bbeamforming\b|\bsubspace\b", re.IGNORECASE)


@dataclass(frozen=True)
class Decision:
    decision: str  # INCLUDE / EXCLUDE / REVIEW
    reason_code: str
    reason: str


def get_text(rec: Dict[str, Any]) -> Tuple[str, str, str]:
    title = (rec.get("title") or "").strip()
    extra = rec.get("extra") or {}
    abstract = ""
    if isinstance(extra, dict):
        abstract = (extra.get("AB") or "").strip()
    combined = " ".join([title, abstract])
    combined = re.sub(r"\s+", " ", combined).strip()
    return title, abstract, combined


def decide(rec: Dict[str, Any]) -> Decision:
    title, abstract, combined = get_text(rec)
    if not title:
        return Decision("REVIEW", "R_MISSING_TITLE", "Missing title; needs manual inspection.")

    has_doa = bool(DOA_PAT.search(combined))
    has_track = bool(TRACK_PAT.search(combined))
    has_array_context = bool(RADAR_SONAR_PAT.search(combined))

    # Strong include: both DOA and tracking/kalman-ish signals appear.
    if has_doa and has_track:
        return Decision("INCLUDE", "I_DOA_TRACK", "Mentions DOA/AoA and tracking (Kalman/EKF/UKF/innovation).")

    # Likely include for review: DOA present but tracking signal absent.
    if has_doa and not has_track:
        return Decision("REVIEW", "R_DOA_ONLY", "Mentions DOA/AoA but no explicit Kalman/tracking terms; review.")

    # Likely include for review: tracking present with array/radar context (could be DOA-related but not explicit).
    if has_track and has_array_context:
        return Decision("REVIEW", "R_TRACK_ARRAY", "Tracking terms with array/radar context; DOA not explicit.")

    # Exclude: neither DOA nor likely array context.
    if not has_doa and not has_array_context:
        return Decision("EXCLUDE", "E_NOT_DOA", "No DOA/AoA/array context in title/abstract.")

    # Exclude: array context but no DOA/tracking - generic signal processing / comms.
    if has_array_context and (not has_doa) and (not has_track):
        return Decision("EXCLUDE", "E_ARRAY_NO_DOA_TRACK", "Array/radar terms but no DOA or tracking terms.")

    return Decision("REVIEW", "R_UNCERTAIN", "Ambiguous; needs manual inspection.")


def main() -> int:
    base = Path("docs/literature")
    in_path = base / "exports_dedup.json"
    out_csv = base / "title_abstract_screening.csv"
    out_md = base / "title_abstract_screening_summary.md"

    obj = json.loads(in_path.read_text(encoding="utf-8"))
    unique: List[Dict[str, Any]] = obj.get("unique", [])

    rows: List[Dict[str, Any]] = []
    counts = Counter()
    reason_counts = Counter()

    for rec in unique:
        title, abstract, _ = get_text(rec)
        dec = decide(rec)
        counts[dec.decision] += 1
        reason_counts[dec.reason_code] += 1

        rows.append(
            {
                "decision": dec.decision,
                "reason_code": dec.reason_code,
                "reason": dec.reason,
                "title": title,
                "year": rec.get("year", ""),
                "venue": rec.get("venue", ""),
                "doi": rec.get("doi", ""),
                "arxiv": rec.get("arxiv", ""),
                "url": rec.get("url", ""),
                "source_file": Path(rec.get("source_file", "")).name,
                "abstract_snippet": (abstract[:280] + "...") if len(abstract) > 280 else abstract,
            }
        )

    # Write CSV (editable checklist)
    fieldnames = [
        "decision",
        "reason_code",
        "reason",
        "title",
        "year",
        "venue",
        "doi",
        "arxiv",
        "url",
        "source_file",
        "abstract_snippet",
    ]
    with out_csv.open("w", newline="", encoding="utf-8") as f:
        wr = csv.DictWriter(f, fieldnames=fieldnames)
        wr.writeheader()
        wr.writerows(rows)

    # Summary markdown
    identified = int(obj.get("records_total", 0))
    dedup = int(obj.get("unique_total", len(unique)))
    dups = int(obj.get("duplicates_total", 0))
    include_n = counts.get("INCLUDE", 0)
    exclude_n = counts.get("EXCLUDE", 0)
    review_n = counts.get("REVIEW", 0)

    lines: List[str] = []
    lines.append("# Title/Abstract Screening Summary (Auto)\n\n")
    lines.append(f"- Input: `{in_path.as_posix()}`\n")
    lines.append(f"- Output checklist: `{out_csv.as_posix()}`\n")
    lines.append("\n## PRISMA (Auto, export scope)\n")
    lines.append(f"- Records identified (exports): n = {identified}\n")
    lines.append(f"- Duplicates removed (exports): n = {dups}\n")
    lines.append(f"- Records after duplicates removed (exports): n = {dedup}\n")
    lines.append(f"- Records screened (title/abstract): n = {dedup}\n")
    lines.append(f"- Excluded after title/abstract (auto): n = {exclude_n}\n")
    lines.append(f"- Included after title/abstract (auto): n = {include_n}\n")
    lines.append(f"- Needs manual review (auto): n = {review_n}\n")
    lines.append("\n## Exclusion/Review Reasons (Auto)\n")
    lines.append("| Code | Count |\n|---|---:|\n")
    for code, cnt in reason_counts.most_common():
        lines.append(f"| {code} | {cnt} |\n")
    lines.append("\n## Notes\n")
    lines.append("- This is heuristic and will over/under-include; use it to prioritize manual screening.\n")
    lines.append("- Final PRISMA should be based on human-confirmed decisions (especially REVIEW rows).\n")

    out_md.write_text("".join(lines), encoding="utf-8")
    print(f"Wrote {out_csv} and {out_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

