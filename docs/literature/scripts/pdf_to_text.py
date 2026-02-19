#!/usr/bin/env python3
"""
Extract plain text from PDFs using PyMuPDF.

Usage:
  python3 pdf_to_text.py /path/in.pdf -o /path/out.txt
  python3 pdf_to_text.py /path/a.pdf /path/b.pdf --out-dir /dir
"""

from __future__ import annotations

import argparse
import os
import re
import sys

import fitz  # PyMuPDF


def default_out_path(pdf_path: str, out_dir: str) -> str:
    base = os.path.basename(pdf_path)
    base = re.sub(r"\.pdf$", "", base, flags=re.I)
    safe = re.sub(r"[^A-Za-z0-9._-]+", "_", base).strip("._-") or "paper"
    return os.path.join(out_dir, f"{safe}.txt")


def extract_text(pdf_path: str) -> str:
    doc = fitz.open(pdf_path)
    parts: list[str] = []
    for i, page in enumerate(doc, start=1):
        text = page.get_text("text") or ""
        parts.append(f"\n\n===== PAGE {i} =====\n")
        parts.append(text)
    return "".join(parts)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("pdfs", nargs="+", help="PDF file(s)")
    ap.add_argument("-o", "--out", help="Output text file (only valid for single input)")
    ap.add_argument("--out-dir", default=".", help="Output directory for multiple inputs")
    args = ap.parse_args()

    if args.out and len(args.pdfs) != 1:
        print("--out requires exactly one input PDF", file=sys.stderr)
        return 2

    os.makedirs(args.out_dir, exist_ok=True)

    for pdf in args.pdfs:
        out_path = args.out or default_out_path(pdf, args.out_dir)
        text = extract_text(pdf)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(text)
        print(out_path)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

