#!/usr/bin/env python3
"""Render Mermaid (.mmd) to PNG via Kroki.

Usage:
  python3 render_mermaid_kroki.py in.mmd -o out.png

Notes:
- Uses https://kroki.io/mermaid/png
- Deterministic given the same input text (modulo Kroki renderer updates).
"""

from __future__ import annotations

import argparse
from pathlib import Path

import urllib.request

KROKI_URL = "https://kroki.io/mermaid/png"


def render_mermaid_to_png(src: str) -> bytes:
    data = src.encode("utf-8")
    req = urllib.request.Request(
        KROKI_URL,
        data=data,
        headers={
            "Content-Type": "text/plain; charset=utf-8",
            "Accept": "image/png",
            "User-Agent": "SubspaceNet_Update-literature-review/1.0",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        return resp.read()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("input", help="Input .mmd file")
    ap.add_argument("-o", "--out", required=True, help="Output .png path")
    args = ap.parse_args()

    in_path = Path(args.input)
    out_path = Path(args.out)

    src = in_path.read_text(encoding="utf-8")
    png = render_mermaid_to_png(src)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_bytes(png)
    print(str(out_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
