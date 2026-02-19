#!/usr/bin/env python3
"""
Create a 15-30 paper shortlist from the v2 INCLUDE set.

Inputs:
  - docs/literature/title_abstract_screening_v2.csv
  - docs/literature/exports_dedup.json

Output:
  - docs/literature/plan_fulltext_v2/shortlist_30.md
"""

from __future__ import annotations

import csv
import json
import re
from pathlib import Path
from typing import Any, Dict, List, Tuple


DEEP_PAT = re.compile(r"\b(deep|neural|cnn|transformer|learning)\b", re.IGNORECASE)
SUBSPACE_PAT = re.compile(r"\b(subspace|music|esprit|root-music)\b", re.IGNORECASE)
SPARSE_PAT = re.compile(r"\b(sparse|bayesian|sbl|gridless)\b", re.IGNORECASE)
ADAPT_PAT = re.compile(r"\b(adapt|calibr|mismatch|imperfection|drift|error)\b", re.IGNORECASE)
TRACK_PAT = re.compile(r"\bkalman\b|\bekf\b|\bukf\b|\bparticle\b|tracking|innovation|residual", re.IGNORECASE)


def _norm_title(t: str) -> str:
    t = (t or "").strip().lower()
    t = re.sub(r"\s+", " ", t)
    t = re.sub(r"[^a-z0-9 ]+", "", t)
    return t


def key_from_row(row: Dict[str, str]) -> Tuple[str, str]:
    doi = (row.get("doi") or "").strip().lower()
    if doi:
        return ("doi", doi)
    arx = (row.get("arxiv") or "").strip().lower()
    if arx:
        return ("arxiv", arx)
    return ("title", _norm_title(row.get("title") or ""))


def build_unique_map(exports_dedup_json: Path) -> Dict[Tuple[str, str], Dict[str, Any]]:
    obj = json.loads(exports_dedup_json.read_text(encoding="utf-8"))
    m: Dict[Tuple[str, str], Dict[str, Any]] = {}
    for u in obj.get("unique", []):
        k = (u.get("dedup_key_kind", ""), str(u.get("dedup_key", "")).strip().lower())
        if k[0] and k[1]:
            m[k] = u
    return m


def score(text: str) -> int:
    s = 0
    if DEEP_PAT.search(text):
        s += 3
    if SUBSPACE_PAT.search(text):
        s += 3
    if SPARSE_PAT.search(text):
        s += 2
    if ADAPT_PAT.search(text):
        s += 3
    if TRACK_PAT.search(text):
        s += 2
    return s


def main() -> int:
    base = Path("docs/literature")
    in_csv = base / "title_abstract_screening_v2.csv"
    in_json = base / "exports_dedup.json"
    out_md = base / "plan_fulltext_v2" / "shortlist_30.md"

    unique_map = build_unique_map(in_json)

    include_rows: List[Dict[str, str]] = []
    with in_csv.open(newline="", encoding="utf-8") as f:
        rd = csv.DictReader(f)
        for row in rd:
            if row.get("decision") == "INCLUDE":
                include_rows.append(dict(row))

    scored: List[Tuple[int, Dict[str, str], Dict[str, Any]]] = []
    for row in include_rows:
        k = key_from_row(row)
        u = unique_map.get((k[0], k[1]))
        title = row.get("title") or ""
        ab = ""
        if u and isinstance(u.get("extra"), dict):
            ab = u["extra"].get("AB") or ""
        text = f"{title} {ab}"
        scored.append((score(text), row, u or {}))

    scored.sort(key=lambda x: (x[0], x[1].get("year", "")), reverse=True)

    # Ensure some diversity by selecting in rounds over buckets.
    buckets = {"deep": [], "subspace": [], "sparse": [], "adapt": [], "other": []}
    for sc, row, u in scored:
        text = (row.get("title", "") + " " + (u.get("extra", {}) or {}).get("AB", "")).strip()
        if DEEP_PAT.search(text):
            buckets["deep"].append((sc, row, u))
        elif SUBSPACE_PAT.search(text):
            buckets["subspace"].append((sc, row, u))
        elif SPARSE_PAT.search(text):
            buckets["sparse"].append((sc, row, u))
        elif ADAPT_PAT.search(text):
            buckets["adapt"].append((sc, row, u))
        else:
            buckets["other"].append((sc, row, u))

    pick: List[Tuple[int, Dict[str, str], Dict[str, Any]]] = []
    order = ["adapt", "deep", "subspace", "sparse", "other"]
    seen_keys = set()
    while len(pick) < 30:
        progressed = False
        for k in order:
            if not buckets[k]:
                continue
            sc, row, u = buckets[k].pop(0)
            key = (row.get("doi") or row.get("arxiv") or row.get("title") or "").strip()
            if key in seen_keys:
                continue
            seen_keys.add(key)
            pick.append((sc, row, u))
            progressed = True
            if len(pick) >= 30:
                break
        if not progressed:
            break

    lines: List[str] = []
    lines.append("# Shortlist (Top 30, Auto)\n\n")
    lines.append("来源：`title_abstract_screening_v2.csv` 的 INCLUDE 集合（严格 DOA+Kalman 查询口径）。\n\n")
    for i, (sc, row, u) in enumerate(pick, start=1):
        title = row.get("title", "").strip()
        year = row.get("year", "").strip()
        venue = row.get("venue", "").strip()
        doi = row.get("doi", "").strip()
        url = row.get("url", "").strip()
        src = row.get("source_file", "").strip()
        lines.append(f"{i}. **{title}** ({year})\n")
        lines.append(f"   - venue: {venue}\n")
        if doi:
            lines.append(f"   - doi: {doi}\n")
        if url:
            lines.append(f"   - url: {url}\n")
        lines.append(f"   - source: {src}\n")
        lines.append(f"   - score: {sc}\n")
    out_md.write_text("".join(lines), encoding="utf-8")
    print(f"Wrote {out_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

