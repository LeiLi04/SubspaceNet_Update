#!/usr/bin/env python3
"""Make a refined shortlist (final 25) from the auto top-30 and v2 INCLUDE pool.

Output:
  docs/literature/plan_fulltext_v2/shortlist_final_25.md

Policy (heuristic):
- Drop obvious off-topic: SLAM/localization/UWB/TDOA/handbook/etc.
- Keep DOA/AoA + tracking/KF/EKF/UKF/filters; allow underwater/radar/acoustic/speaker tracking.
- Fill up to 25 by selecting additional candidates from title_abstract_screening_v2.csv (INCLUDE).
"""

from __future__ import annotations

import csv
import os
import re
from dataclasses import dataclass
from typing import Optional

ROOT = "/Users/lilei/PycharmProjects/SubspaceNet_Update"
SHORTLIST30 = os.path.join(ROOT, "docs/literature/plan_fulltext_v2/shortlist_30.md")
INCLUDE_CSV = os.path.join(ROOT, "docs/literature/title_abstract_screening_v2.csv")
OUT_MD = os.path.join(ROOT, "docs/literature/plan_fulltext_v2/shortlist_final_25.md")

FULLTEXT_OA_DIR = os.path.join(ROOT, "docs/literature/fulltext/oa")
FULLTEXT_LOCAL_DIR = os.path.join(ROOT, "docs/literature/fulltext/local")
FULLTEXT_SUB_DIR = os.path.join(ROOT, "docs/literature/fulltext/subscription")


def norm_doi(doi: str) -> str:
    doi = (doi or "").strip()
    doi = re.sub(r"^https?://(dx\.)?doi\.org/", "", doi, flags=re.I)
    return doi.lower()


def doi_to_fname(doi: str) -> str:
    return norm_doi(doi).replace("/", "_") + ".pdf"


def classify_offtopic(title: str) -> Optional[str]:
    t = (title or "").lower()

    # Explicit off-topic buckets requested by user.
    if "slam" in t:
        return "SLAM"
    if "uwb" in t or "ultra-wide" in t or "ultra wide" in t:
        return "UWB/positioning"
    if "tdoa" in t:
        return "TDOA/positioning"
    if "handbook" in t or "measures and analysis" in t:
        return "Handbook/survey-like"
    if "channel estimation" in t:
        return "Channel estimation"

    # Localization/navigation often drifts away from DOA tracking itself.
    if "localization" in t or "geolocation" in t or "positioning" in t:
        return "Localization"
    # For this stage, treat navigation/position-centric papers as localization (user requested to drop them).
    if "navigation" in t:
        return "Localization"
    if "vehicle position" in t:
        return "Localization"
    # Heuristic: if title is position-centric but doesn't explicitly say DOA/direction, drop it.
    if re.search(r"\bposition\b", t) and ("doa" not in t) and ("direction" not in t):
        return "Localization"

    # Generic tracking items without DOA focus.
    if "people tracking" in t:
        return "Tracking (non-DOA)"

    return None


def is_core_doa_tracking(title: str) -> bool:
    t = (title or "").lower()
    doa_terms = ["doa", "direction-of-arrival", "direction of arrival", "aoa", "angle of arrival"]
    track_terms = ["tracking", "kalman", "ekf", "ukf", "filter", "particle", "phd", "bayesian"]
    has_doa = any(x in t for x in doa_terms)
    # Some titles use \"plane wave direction\" instead of DOA keywords.
    if not has_doa and "plane wave" not in t and "bearing" not in t:
        return False
    return any(x in t for x in track_terms) or ("radar" in t and has_doa)


def oa_guess(doi: str, venue: str, url: str) -> str:
    doi = norm_doi(doi)
    v = (venue or "").lower()
    u = (url or "").lower()

    if "arxiv" in u or "arxiv" in v:
        return "Yes"
    if doi.startswith("10.3390/"):
        return "Yes (MDPI)"
    if doi.startswith("10.1038/s41598"):
        return "Yes (SciRep)"
    # IEEE Access is often OA-ish but not guaranteed; keep conservative.
    if "ieee access" in v:
        return "Maybe"
    return "Unknown"


def fulltext_path_status(doi: str, title: str) -> tuple[str, str]:
    """Return (status, path_or_target)."""
    doi_n = norm_doi(doi)
    if doi_n:
        fname = doi_to_fname(doi_n)
        for base in [FULLTEXT_OA_DIR, FULLTEXT_SUB_DIR]:
            p = os.path.join(base, fname)
            if os.path.exists(p):
                return "HAVE", os.path.relpath(p, ROOT)
        # For OA-ish, target OA dir; else subscription.
        target_base = FULLTEXT_OA_DIR if oa_guess(doi_n, "", "").startswith("Yes") else FULLTEXT_SUB_DIR
        return "NEED", os.path.relpath(os.path.join(target_base, fname), ROOT)

    # No DOI: try local konstantino
    if "unsupervised adaptation of ai doa estimators" in (title or "").lower():
        p = os.path.join(FULLTEXT_LOCAL_DIR, "konstantino_unsupervised_adaptation_doa_estimators_downstream_tracking.pdf")
        if os.path.exists(p):
            return "HAVE", os.path.relpath(p, ROOT)

    # Otherwise, use a slug
    slug = re.sub(r"[^a-z0-9]+", "_", (title or "paper").lower()).strip("_")[:80]
    return "NEED", os.path.relpath(os.path.join(FULLTEXT_SUB_DIR, f"{slug}.pdf"), ROOT)


@dataclass
class Item:
    title: str
    year: str
    venue: str
    doi: str
    url: str
    source_file: str
    note: str = ""


def parse_shortlist30(path: str) -> list[Item]:
    text = open(path, "r", encoding="utf-8").read().splitlines()
    items: list[Item] = []
    cur = None

    for line in text:
        m = re.match(r"^\d+\. \*\*(.+)\*\* \((\d{4})\)", line)
        if m:
            if cur:
                items.append(cur)
            cur = Item(title=m.group(1).strip(), year=m.group(2), venue="", doi="", url="", source_file="")
            continue
        if not cur:
            continue
        m = re.match(r"\s*- venue:\s*(.+)$", line)
        if m:
            cur.venue = m.group(1).strip()
        m = re.match(r"\s*- doi:\s*(.+)$", line)
        if m:
            cur.doi = norm_doi(m.group(1).strip())
        m = re.match(r"\s*- url:\s*(.+)$", line)
        if m:
            cur.url = m.group(1).strip()
        m = re.match(r"\s*- source:\s*(.+)$", line)
        if m:
            cur.source_file = m.group(1).strip()

    if cur:
        items.append(cur)
    return items


def load_include_pool(path: str) -> list[Item]:
    items: list[Item] = []
    with open(path, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r.get("decision") != "INCLUDE":
                continue
            items.append(
                Item(
                    title=(r.get("title") or "").strip(),
                    year=(r.get("year") or "").strip(),
                    venue=(r.get("venue") or "").strip(),
                    doi=norm_doi(r.get("doi") or ""),
                    url=(r.get("url") or "").strip(),
                    source_file=(r.get("source_file") or "").strip(),
                )
            )
    return items


def score_item(it: Item) -> int:
    t = (it.title or "").lower()
    s = 0
    if "doa tracking" in t or "direction-of-arrival tracking" in t or "direction of arrival tracking" in t:
        s += 6
    if "kalman" in t or "ekf" in t or "ukf" in t:
        s += 4
    if "bayesian" in t or "particle" in t or "phd" in t:
        s += 2
    if "underwater" in t or "hydrophone" in t or "acoustic" in t or "speaker" in t:
        s += 1
    if "mimo" in t or "radar" in t:
        s += 2
    if "robust" in t or "non-gaussian" in t or "nonstationary" in t:
        s += 1
    # downweight localization-ish even if not excluded
    if "localization" in t or "position" in t or "navigation" in t:
        s -= 3
    if "slam" in t:
        s -= 10
    return s


def main() -> int:
    os.makedirs(FULLTEXT_SUB_DIR, exist_ok=True)

    top30 = parse_shortlist30(SHORTLIST30)

    kept_from_30: list[Item] = []
    dropped_from_30: list[tuple[Item, str]] = []

    for it in top30:
        reason = classify_offtopic(it.title)
        if reason:
            dropped_from_30.append((it, reason))
            continue
        # Require core DOA tracking; drop weak items.
        if not is_core_doa_tracking(it.title):
            dropped_from_30.append((it, "Non-DOA-tracking focus"))
            continue
        kept_from_30.append(it)

    # Always include the 4 already-available fulltexts as anchors (may duplicate existing).
    anchors = [
        Item(
            title="Unsupervised Adaptation of AI DoA Estimators via Downstream Tracking",
            year="2026",
            venue="Manuscript (local PDF)",
            doi="",
            url="",
            source_file="local",
            note="Already available (local PDF).",
        ),
        Item(
            title="MIMO radar DOA element position error correction method based on overlapping reference element matrix reconstruction",
            year="2025",
            venue="Scientific Reports",
            doi="10.1038/s41598-025-03276-1",
            url="https://doi.org/10.1038/s41598-025-03276-1",
            source_file="oa_seed",
            note="Already downloaded (OA).",
        ),
        Item(
            title="A Novel DOA Estimation Algorithm Using Array Rotation Technique",
            year="2014",
            venue="Future Internet",
            doi="10.3390/fi6010155",
            url="https://doi.org/10.3390/fi6010155",
            source_file="oa_seed",
            note="Already downloaded (OA).",
        ),
        Item(
            title="Robust Underwater Direction-of-Arrival Tracking Based on AI-Aided Variational Bayesian Extended Kalman Filter",
            year="2023",
            venue="Remote Sensing",
            doi="10.3390/rs15020420",
            url="https://doi.org/10.3390/rs15020420",
            source_file="wos_savedrecs_2026-02-19.xls",
            note="Already downloaded (OA).",
        ),
    ]

    # Start final list: anchors + best kept from 30 (dedup by DOI/title)
    final: list[Item] = []
    seen_doi = set()
    seen_title = set()

    def add(it: Item):
        d = norm_doi(it.doi)
        t = (it.title or "").strip().lower()
        if d and d in seen_doi:
            return
        if t and t in seen_title:
            return
        final.append(it)
        if d:
            seen_doi.add(d)
        if t:
            seen_title.add(t)

    for a in anchors:
        add(a)

    for it in sorted(kept_from_30, key=score_item, reverse=True):
        add(it)

    pool = load_include_pool(INCLUDE_CSV)

    # Filter pool to DOA tracking-ish, exclude off-topic, then add by score.
    cand: list[Item] = []
    for it in pool:
        if classify_offtopic(it.title):
            continue
        if not is_core_doa_tracking(it.title):
            continue
        cand.append(it)

    for it in sorted(cand, key=score_item, reverse=True):
        if len(final) >= 25:
            break
        add(it)

    # If still short, relax and include remaining high-score items (even if borderline localization) but not SLAM.
    if len(final) < 25:
        for it in sorted(pool, key=score_item, reverse=True):
            if len(final) >= 25:
                break
            if "slam" in (it.title or "").lower():
                continue
            add(it)

    # Write markdown
    lines: list[str] = []
    lines.append("# Shortlist (Final 25, Refined)\n")
    lines.append("来源：`shortlist_30.md` 精炼 + `title_abstract_screening_v2.csv` 的 INCLUDE 池补齐。\n")
    lines.append("表头字段：DOI/来源库/OA(粗略判断)/全文获取路径(已有或建议存放路径)。\n")

    lines.append("## Selected (25)\n")
    lines.append("| ID | Title | Year | Venue | DOI | Source | OA? | Fulltext | Notes |")
    lines.append("|---|---|---:|---|---|---|---|---|---|")

    for idx, it in enumerate(final[:25], start=1):
        oa = oa_guess(it.doi, it.venue, it.url)
        status, p = fulltext_path_status(it.doi, it.title)
        fulltext = f"{status}: `{p}`"
        doi_disp = it.doi or ""
        source = it.source_file or ""
        notes = it.note or ""
        lines.append(
            "| {id} | {title} | {year} | {venue} | {doi} | {source} | {oa} | {fulltext} | {notes} |".format(
                id=f"S{idx:02d}",
                title=it.title.replace("|", "\\|"),
                year=it.year or "",
                venue=(it.venue or "").replace("|", "\\|"),
                doi=doi_disp,
                source=source,
                oa=oa,
                fulltext=fulltext,
                notes=notes.replace("|", "\\|"),
            )
        )

    lines.append("\n## Dropped From Auto Top-30 (Obvious Off-Topic)\n")
    lines.append("| # | Title | Year | DOI | Reason |")
    lines.append("|---:|---|---:|---|---|")
    for i, (it, reason) in enumerate(dropped_from_30, start=1):
        lines.append(
            f"| {i} | {it.title.replace('|','\\|')} | {it.year} | {it.doi} | {reason} |"
        )

    with open(OUT_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(lines).rstrip() + "\n")

    print(OUT_MD)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
