#!/usr/bin/env python3
"""Fetch obvious OA PDFs.

Inputs:
  - DOI list (one per line) OR --from-seed to pull known OA-ish DOIs.

Outputs:
  - PDFs saved under docs/literature/fulltext/oa/
  - Manifest markdown + JSON

Notes:
  - Uses OpenAlex best_oa_location/pdf_url when available.
  - Adds publisher-specific fallbacks (MDPI, Nature/SciRep).
"""

from __future__ import annotations

import argparse
import dataclasses
import datetime as dt
import hashlib
import json
import os
import re
import sys
import time
import urllib.parse

import requests

ROOT = "/Users/lilei/PycharmProjects/SubspaceNet_Update"
OUT_DIR = os.path.join(ROOT, "docs/literature/fulltext/oa")

UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/121.0.0.0 Safari/537.36"
)

MDPI_ISSN_BY_PREFIX = {
    # Extend as needed.
    "rs": "2072-4292",  # Remote Sensing
    "fi": "1999-5903",  # Future Internet
}

MDPI_JOURNAL_BY_PREFIX = {
    # For mdpi-res.com fallback (bypasses mdpi.com 403 in many environments).
    "rs": "remotesensing",
    "fi": "futureinternet",
}


def now_utc() -> str:
    return dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def norm_doi(doi: str) -> str:
    doi = doi.strip()
    doi = re.sub(r"^https?://(dx\.)?doi\.org/", "", doi, flags=re.I)
    doi = doi.strip()
    return doi.lower()


def safe_slug(s: str, max_len: int = 120) -> str:
    s = s.strip().lower()
    s = re.sub(r"\s+", "_", s)
    s = re.sub(r"[^a-z0-9._-]+", "", s)
    return s[:max_len].strip("._-") or "paper"


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


@dataclasses.dataclass
class FetchResult:
    doi: str
    title: str | None = None
    oa_pdf_url: str | None = None
    landing_url: str | None = None
    attempted_urls: list[str] = dataclasses.field(default_factory=list)
    status: str = "pending"  # ok | blocked | missing | error
    http_status: int | None = None
    out_path: str | None = None
    sha256: str | None = None
    bytes: int | None = None
    note: str | None = None


def openalex_lookup(doi: str) -> dict:
    url = f"https://api.openalex.org/works/https://doi.org/{urllib.parse.quote(doi, safe='') }"
    r = requests.get(url, headers={"User-Agent": UA}, timeout=30)
    if r.status_code != 200:
        raise RuntimeError(f"OpenAlex lookup failed: {r.status_code}")
    return r.json()


def mdpi_res_url(prefix: str, volume: str, first_page: str) -> str | None:
    journal = MDPI_JOURNAL_BY_PREFIX.get(prefix)
    if not journal:
        return None
    try:
        vol = f"{int(volume):02d}"
        art = f"{int(first_page):05d}"
    except Exception:
        return None
    stem = f"{journal}-{vol}-{art}"
    return f"https://mdpi-res.com/d_attachment/{journal}/{stem}/article_deploy/{stem}.pdf"


def mdpi_fallback_urls(doi: str, biblio: dict | None = None) -> list[str]:
    # Prefer OpenAlex biblio fields because MDPI DOI internal encoding is ambiguous for small volumes.
    urls: list[str] = []

    prefix_m = re.fullmatch(r"10\.3390/([a-z]{2}).+", doi)
    prefix = prefix_m.group(1) if prefix_m else None

    if prefix and isinstance(biblio, dict):
        vol = biblio.get("volume")
        fp = biblio.get("first_page")
        if vol and fp:
            u = mdpi_res_url(prefix, str(vol), str(fp))
            if u:
                urls.append(u)

    # As a secondary candidate, try the canonical mdpi.com URL when we can parse
    # volume/issue/first_page. This is often blocked by anti-bot, but sometimes works.
    if prefix and isinstance(biblio, dict):
        issn = MDPI_ISSN_BY_PREFIX.get(prefix)
        vol = biblio.get("volume")
        issue = biblio.get("issue")
        fp = biblio.get("first_page")
        if issn and vol and issue and fp:
            try:
                urls.append(f"https://www.mdpi.com/{issn}/{int(vol)}/{int(issue)}/{int(fp)}/pdf")
            except Exception:
                pass

    return urls


def scirep_fallback_urls(doi: str) -> list[str]:
    # 10.1038/s41598-025-03276-1 -> nature direct pdf
    m = re.fullmatch(r"10\.1038/(s\d+-\d+-\d+-\d+)", doi)
    if not m:
        return []
    suffix = m.group(1)
    return [f"https://www.nature.com/articles/{suffix}.pdf"]


def download_pdf(url: str, out_path: str) -> tuple[int, int]:
    # returns (http_status, bytes)
    with requests.get(
        url,
        headers={
            "User-Agent": UA,
            "Accept": "application/pdf,application/octet-stream;q=0.9,*/*;q=0.8",
        },
        timeout=60,
        stream=True,
        allow_redirects=True,
    ) as r:
        status = r.status_code
        if status != 200:
            return status, 0
        # Write and validate header
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        n = 0
        with open(out_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=1024 * 64):
                if not chunk:
                    continue
                f.write(chunk)
                n += len(chunk)
        # Basic PDF magic check
        with open(out_path, "rb") as f:
            head = f.read(5)
        if head != b"%PDF-":
            # Not a PDF; keep file for debugging but mark as error
            return 200, -n
        return 200, n


def build_candidates_from_openalex(oa: dict) -> tuple[str | None, str | None, str | None]:
    title = oa.get("title")
    landing = None
    if isinstance(oa.get("primary_location"), dict):
        landing = oa["primary_location"].get("landing_page_url")
    pdf_url = None
    loc = oa.get("best_oa_location")
    if isinstance(loc, dict):
        pdf_url = loc.get("pdf_url") or loc.get("url")
        landing = landing or loc.get("landing_page_url") or loc.get("url")
    return title, pdf_url, landing


def fetch_one(doi: str) -> FetchResult:
    doi = norm_doi(doi)
    res = FetchResult(doi=doi)

    # 1) OpenAlex
    oa_biblio = None
    try:
        oa = openalex_lookup(doi)
        res.title, res.oa_pdf_url, res.landing_url = build_candidates_from_openalex(oa)
        oa_biblio = oa.get("biblio") if isinstance(oa, dict) else None
    except Exception as e:
        res.note = f"OpenAlex lookup failed: {e}"

    candidates: list[str] = []
    if res.oa_pdf_url:
        candidates.append(res.oa_pdf_url)

    # 2) Publisher fallbacks
    if doi.startswith("10.3390/"):
        candidates += mdpi_fallback_urls(doi, biblio=oa_biblio if isinstance(oa_biblio, dict) else None)
    if doi.startswith("10.1038/"):
        candidates += scirep_fallback_urls(doi)

    # 3) De-dupe candidate urls, keep order
    seen = set()
    uniq = []
    for u in candidates:
        if not u:
            continue
        u = u.strip()
        if u in seen:
            continue
        seen.add(u)
        uniq.append(u)

    if not uniq:
        res.status = "missing"
        res.note = (res.note + "; " if res.note else "") + "No PDF URL candidates"
        return res

    base = safe_slug(doi.replace("/", "_"))
    out_path = os.path.join(OUT_DIR, f"{base}.pdf")

    # 4) Try downloads
    last_http = None
    for u in uniq:
        res.attempted_urls.append(u)
        try:
            http_status, n = download_pdf(u, out_path)
            last_http = http_status
            if http_status == 200 and n > 0:
                res.status = "ok"
                res.http_status = 200
                res.out_path = out_path
                res.bytes = n
                res.sha256 = sha256_file(out_path)
                return res
            if http_status == 200 and n < 0:
                res.status = "error"
                res.http_status = 200
                res.note = f"Downloaded but not a PDF (bytes={-n})"
                # Keep trying next candidate
                continue
        except Exception as e:
            res.note = f"Download error: {e}"
            continue
        finally:
            time.sleep(0.2)

    res.http_status = last_http
    if last_http in (401, 403):
        res.status = "blocked"
        res.note = res.note or f"HTTP {last_http}"
    else:
        res.status = "error"
        res.note = res.note or f"HTTP {last_http}"
    return res


def write_manifest(results: list[FetchResult], out_md: str, out_json: str) -> None:
    md_lines = []
    md_lines.append(f"# OA Fulltext Manifest\n")
    md_lines.append(f"Generated at (UTC): `{now_utc()}`\n")

    # Summary counts
    from collections import Counter

    c = Counter(r.status for r in results)
    md_lines.append("## Summary\n")
    md_lines.append(f"- total: {len(results)}\n")
    for k in ["ok", "blocked", "missing", "error", "pending"]:
        if k in c:
            md_lines.append(f"- {k}: {c[k]}\n")
    md_lines.append("\n## Items\n")

    for r in results:
        md_lines.append(f"- **{r.doi}** | status: `{r.status}`")
        if r.title:
            md_lines[-1] += f" | title: {r.title}"
        md_lines.append("  ")
        if r.out_path:
            md_lines.append(f"  - file: `{r.out_path}`")
        if r.bytes is not None:
            md_lines.append(f"  - bytes: {r.bytes}")
        if r.sha256:
            md_lines.append(f"  - sha256: `{r.sha256}`")
        if r.oa_pdf_url:
            md_lines.append(f"  - openalex_pdf_url: `{r.oa_pdf_url}`")
        if r.landing_url:
            md_lines.append(f"  - landing_url: `{r.landing_url}`")
        if r.attempted_urls:
            md_lines.append("  - attempted_urls:")
            for u in r.attempted_urls[:6]:
                md_lines.append(f"    - `{u}`")
            if len(r.attempted_urls) > 6:
                md_lines.append(f"    - ... ({len(r.attempted_urls)-6} more)")
        if r.http_status is not None:
            md_lines.append(f"  - last_http_status: {r.http_status}")
        if r.note:
            md_lines.append(f"  - note: {r.note}")

    with open(out_md, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines).rstrip() + "\n")

    # JSON
    def as_dict(x: FetchResult) -> dict:
        return dataclasses.asdict(x)

    with open(out_json, "w", encoding="utf-8") as f:
        json.dump([as_dict(r) for r in results], f, ensure_ascii=False, indent=2)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--doi-file", help="Path to text file with DOIs")
    ap.add_argument("--dois", nargs="*", help="DOIs as args")
    ap.add_argument("--out-md", default=os.path.join(ROOT, "docs/literature/plan_fulltext_v2/oa_fulltext_manifest.md"))
    ap.add_argument("--out-json", default=os.path.join(ROOT, "docs/literature/plan_fulltext_v2/oa_fulltext_manifest.json"))
    args = ap.parse_args()

    dois: list[str] = []
    if args.doi_file:
        with open(args.doi_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                dois.append(line)
    if args.dois:
        dois += args.dois

    dois = [norm_doi(d) for d in dois if d.strip()]
    # de-dupe
    seen = set()
    uniq = []
    for d in dois:
        if d in seen:
            continue
        seen.add(d)
        uniq.append(d)

    if not uniq:
        print("No DOIs provided", file=sys.stderr)
        return 2

    results: list[FetchResult] = []
    for d in uniq:
        print(f"Fetching {d}...", file=sys.stderr)
        try:
            r = fetch_one(d)
        except Exception as e:
            r = FetchResult(doi=d, status="error", note=f"Unhandled: {e}")
        results.append(r)

    write_manifest(results, args.out_md, args.out_json)

    ok = sum(1 for r in results if r.status == "ok")
    print(f"Done. ok={ok}/{len(results)}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
