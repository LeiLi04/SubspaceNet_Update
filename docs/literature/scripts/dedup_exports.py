#!/usr/bin/env python3
"""
Deduplicate literature exports (RIS/BibTeX) and compute PRISMA-style counts.

Primary key: DOI
Fallback: arXiv id (from eprint/url)
Fallback: normalized title
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple


_DOI_RE = re.compile(r"\b10\.\d{4,9}/[^\s\"<>]+", re.IGNORECASE)
_ARXIV_RE = re.compile(r"\barxiv:([0-9]{4}\.[0-9]{4,5})\b", re.IGNORECASE)
_ARXIV_URL_RE = re.compile(r"\barxiv\.org/(abs|pdf)/([0-9]{4}\.[0-9]{4,5})\b", re.IGNORECASE)


def _clean_doi(raw: str) -> str:
    raw = raw.strip()
    m = _DOI_RE.search(raw)
    if not m:
        return ""
    doi = m.group(0).rstrip(").,;")
    return doi.lower()


def _extract_arxiv_id(text: str) -> str:
    if not text:
        return ""
    m = _ARXIV_RE.search(text)
    if m:
        return m.group(1).lower()
    m = _ARXIV_URL_RE.search(text)
    if m:
        return m.group(2).lower()
    return ""


def _norm_title(title: str) -> str:
    title = (title or "").strip().lower()
    title = re.sub(r"\s+", " ", title)
    title = re.sub(r"[^a-z0-9 ]+", "", title)
    return title.strip()


@dataclass(frozen=True)
class RecordKey:
    kind: str
    value: str


def _make_key(rec: Dict[str, Any]) -> RecordKey:
    doi = _clean_doi(rec.get("doi", "") or "")
    if doi:
        return RecordKey("doi", doi)
    arx = _extract_arxiv_id(" ".join([str(rec.get("eprint", "") or ""), str(rec.get("url", "") or "")]))
    if arx:
        return RecordKey("arxiv", arx)
    title = _norm_title(rec.get("title", "") or "")
    return RecordKey("title", title or "unknown")


def parse_ris(path: Path) -> List[Dict[str, Any]]:
    text = path.read_text(encoding="utf-8", errors="replace")
    records: List[Dict[str, Any]] = []
    current: Dict[str, Any] = {"source_file": str(path)}
    for line in text.splitlines():
        if line.startswith("ER  -"):
            # end record
            if any(k for k in current.keys() if k not in {"source_file"}):
                records.append(current)
            current = {"source_file": str(path)}
            continue
        if len(line) < 6 or line[2:6] != "  -":
            continue
        tag = line[:2]
        val = line[6:].strip()
        if not val:
            continue
        if tag in {"TI", "T1"}:
            current["title"] = val if "title" not in current else (str(current["title"]) + " " + val)
        elif tag in {"DO"}:
            current["doi"] = val
        elif tag in {"UR"}:
            current["url"] = val
        elif tag in {"PY", "Y1"}:
            current["year"] = val[:4]
        elif tag in {"JO", "JF", "T2"}:
            current["venue"] = val
        elif tag in {"AU", "A1"}:
            current.setdefault("authors", []).append(val)
        else:
            # keep a few potentially useful fields
            if tag in {"AB", "KW"}:
                current.setdefault("extra", {})[tag] = val
    return records


_BIB_ENTRY_RE = re.compile(r"@(?P<type>\w+)\s*\{\s*(?P<key>[^,\s]+)\s*,", re.IGNORECASE)
_BIB_FIELD_RE = re.compile(r"(?P<field>\w+)\s*=\s*(?P<val>\{(?:[^{}]|\{[^{}]*\})*\}|\"(?:[^\"\\\\]|\\\\.)*\")\s*,?", re.IGNORECASE)


def _strip_bib_val(v: str) -> str:
    v = v.strip()
    if v.startswith("{") and v.endswith("}"):
        v = v[1:-1]
    if v.startswith('"') and v.endswith('"'):
        v = v[1:-1]
    return v.strip()


def parse_bibtex(path: Path) -> List[Dict[str, Any]]:
    text = path.read_text(encoding="utf-8", errors="replace")
    # naive split by '@' while keeping it
    chunks = ["@" + c for c in text.split("@") if c.strip()]
    out: List[Dict[str, Any]] = []
    for ch in chunks:
        m = _BIB_ENTRY_RE.search(ch)
        if not m:
            continue
        rec: Dict[str, Any] = {"source_file": str(path), "bib_key": m.group("key"), "bib_type": m.group("type")}
        for fm in _BIB_FIELD_RE.finditer(ch):
            f = fm.group("field").lower()
            v = _strip_bib_val(fm.group("val"))
            rec[f] = v
        # normalize common aliases
        if "doi" not in rec and "DOI" in rec:
            rec["doi"] = rec["DOI"]
        if "title" in rec:
            rec["title"] = rec["title"].replace("\n", " ").strip()
        if "year" in rec:
            rec["year"] = str(rec["year"])[:4]
        if "eprint" in rec:
            rec["eprint"] = str(rec["eprint"]).strip()
        return_url = rec.get("url") or rec.get("howpublished") or ""
        if return_url:
            rec["url"] = str(return_url)
        out.append(rec)
    return out


def load_exports(exports_dir: Path) -> List[Dict[str, Any]]:
    recs: List[Dict[str, Any]] = []
    for p in sorted(exports_dir.glob("*")):
        if p.is_dir():
            continue
        suf = p.suffix.lower()
        if suf == ".ris":
            recs.extend(parse_ris(p))
        elif suf == ".bib":
            recs.extend(parse_bibtex(p))
        elif suf == ".csv":
            recs.extend(parse_csv(p))
        elif suf in {".xls", ".xlsx"}:
            recs.extend(parse_excel(p))
    return recs


def deduplicate(records: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    seen: Dict[RecordKey, Dict[str, Any]] = {}
    dups: List[Dict[str, Any]] = []
    for r in records:
        k = _make_key(r)
        if k in seen:
            dups.append({"duplicate_of": seen[k].get("source_file"), "key_kind": k.kind, "key": k.value, "record": r})
            continue
        rr = dict(r)
        rr["dedup_key_kind"] = k.kind
        rr["dedup_key"] = k.value
        rr["doi"] = _clean_doi(rr.get("doi", "") or "") or rr.get("doi", "")
        rr["arxiv"] = _extract_arxiv_id(" ".join([str(rr.get("eprint", "") or ""), str(rr.get("url", "") or "")]))
        seen[k] = rr
    return list(seen.values()), dups


def parse_csv(path: Path) -> List[Dict[str, Any]]:
    # Supports IEEE Xplore and Scopus CSV exports.
    import csv

    with path.open(newline="", encoding="utf-8", errors="replace") as f:
        rd = csv.DictReader(f)
        # normalize fieldnames: strip BOM/quotes/spaces
        if rd.fieldnames:
            rd.fieldnames = [fn.lstrip("\ufeff").strip().strip('"') for fn in rd.fieldnames]
        out: List[Dict[str, Any]] = []
        for row in rd:
            rec: Dict[str, Any] = {"source_file": str(path)}
            # tolerate slight column name variations
            title = (
                row.get("Document Title")
                or row.get("Title")
                or row.get("title")
                or ""
            )
            doi = row.get("DOI") or row.get("doi") or ""
            url = row.get("PDF Link") or row.get("URL") or row.get("url") or ""
            year = row.get("Publication Year") or row.get("Year") or row.get("year") or ""
            venue = (
                row.get("Publication Title")
                or row.get("Source title")  # Scopus
                or row.get("Journal")
                or row.get("Source")
                or ""
            )
            authors = (
                row.get("Authors")
                or row.get("Author full names")  # Scopus
                or row.get("Author")
                or ""
            )

            rec["title"] = title.strip()
            rec["doi"] = doi.strip()
            rec["url"] = url.strip()
            rec["year"] = str(year).strip()[:4]
            rec["venue"] = venue.strip()
            if authors:
                rec["authors"] = [a.strip() for a in authors.split(";") if a.strip()] if ";" in authors else [authors.strip()]

            # keep abstract if present (useful later, not for dedup key)
            ab = row.get("Abstract") or row.get("abstract") or ""
            if ab:
                rec.setdefault("extra", {})["AB"] = ab.strip()

            out.append(rec)
    return out


def parse_excel(path: Path) -> List[Dict[str, Any]]:
    # WoS exports can arrive as .xls/.xlsx and include columns like:
    # Article Title, Source Title, Publication Year, DOI, Authors, Abstract, etc.
    try:
        import pandas as pd
    except Exception:
        return []

    engine = None
    if path.suffix.lower() == ".xls":
        engine = "xlrd"
    elif path.suffix.lower() == ".xlsx":
        engine = "openpyxl"

    try:
        df = pd.read_excel(path, sheet_name=0, engine=engine)
    except Exception:
        return []

    cols = [str(c) for c in df.columns]
    # If this looks like a "refine/analyze facets" table (lots of *_Count), ignore it.
    if any(c.endswith("_Count") for c in cols) and "Article Title" not in cols and "Title" not in cols:
        return []

    def get_col(row: Dict[str, Any], *names: str) -> str:
        for n in names:
            if n in row and row[n] is not None:
                v = str(row[n]).strip()
                if v and v.lower() != "nan":
                    return v
        return ""

    out: List[Dict[str, Any]] = []
    for _, r in df.iterrows():
        row = {str(k): r[k] for k in df.columns}
        rec: Dict[str, Any] = {"source_file": str(path)}

        title = get_col(row, "Article Title", "Title", "Document Title")
        doi = get_col(row, "DOI", "doi")
        year = get_col(row, "Publication Year", "Year", "year")
        venue = get_col(row, "Source Title", "Publication Title", "Source title", "Journal")
        authors = get_col(row, "Authors", "Author Full Names", "Author full names")
        url = get_col(row, "Link", "URL", "url")
        ab = get_col(row, "Abstract", "abstract")

        if not title and not doi and not venue:
            continue

        rec["title"] = title
        rec["doi"] = doi
        rec["year"] = year[:4] if year else ""
        rec["venue"] = venue
        rec["url"] = url
        if authors:
            # WoS "Authors" often uses ';' separators.
            rec["authors"] = [a.strip() for a in authors.split(";") if a.strip()] if ";" in authors else [authors]
        if ab:
            rec.setdefault("extra", {})["AB"] = ab
        out.append(rec)

    return out


def write_report(
    out_md: Path,
    records_total: int,
    unique_total: int,
    dup_total: int,
    unique_records: List[Dict[str, Any]],
    dups: List[Dict[str, Any]],
) -> None:
    # per-source counts
    by_source: Dict[str, Dict[str, int]] = {}
    for r in unique_records:
        src = r.get("source_file", "unknown")
        by_source.setdefault(src, {"unique": 0, "total": 0})
        by_source[src]["unique"] += 1
    for d in dups:
        src = d["record"].get("source_file", "unknown")
        by_source.setdefault(src, {"unique": 0, "total": 0})
    # count totals per source file
    for r in unique_records:
        by_source[r.get("source_file", "unknown")]["total"] += 1
    for d in dups:
        by_source[d["record"].get("source_file", "unknown")]["total"] += 1

    lines: List[str] = []
    lines.append("# Export Dedup Report\n")
    lines.append("## PRISMA (database export scope)\n")
    lines.append(f"- Records identified (exports): n = {records_total}\n")
    lines.append(f"- Duplicates removed: n = {dup_total}\n")
    lines.append(f"- Records after duplicates removed: n = {unique_total}\n")
    lines.append("\n## By Source File\n")
    lines.append("| Source | Total | Unique | Duplicates |\n")
    lines.append("|---|---:|---:|---:|\n")
    for src in sorted(by_source.keys()):
        total = by_source[src]["total"]
        uniq = by_source[src]["unique"]
        lines.append(f"| {Path(src).name} | {total} | {uniq} | {total - uniq} |\n")

    # diagnostics
    missing_title = [r for r in unique_records if not (r.get("title") or "").strip()]
    missing_doi = [r for r in unique_records if not (r.get("doi") or "").strip() and not (r.get("arxiv") or "").strip()]
    lines.append("\n## Diagnostics\n")
    lines.append(f"- Unique records missing title: {len(missing_title)}\n")
    lines.append(f"- Unique records missing DOI and arXiv id: {len(missing_doi)}\n")
    lines.append("\n## Notes\n")
    lines.append("- Dedup keys: DOI > arXiv id > normalized title.\n")
    lines.append("- Use this report to fill `docs/literature/screening_criteria.md` with official export-based counts.\n")

    out_md.write_text("".join(lines), encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--exports-dir", default="docs/literature/exports", help="Directory containing .ris/.bib exports")
    ap.add_argument("--out-json", default="docs/literature/exports_dedup.json", help="Output JSON (unique + duplicates)")
    ap.add_argument("--out-md", default="docs/literature/exports_dedup_report.md", help="Output markdown report")
    args = ap.parse_args()

    exports_dir = Path(args.exports_dir)
    if not exports_dir.exists():
        raise SystemExit(f"exports dir not found: {exports_dir}")

    records = load_exports(exports_dir)
    unique, dups = deduplicate(records)

    out_json = Path(args.out_json)
    payload = {
        "exports_dir": str(exports_dir),
        "records_total": len(records),
        "unique_total": len(unique),
        "duplicates_total": len(dups),
        "unique": unique,
        "duplicates": dups,
    }
    out_json.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    out_md = Path(args.out_md)
    write_report(out_md, len(records), len(unique), len(dups), unique, dups)
    print(f"Wrote {out_json} and {out_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
