#!/usr/bin/env python3
"""
OCR first N pages of a (scanned) PDF using PyMuPDF + pytesseract.

Example:
  python3 ocr_pdf_first_pages.py input.pdf --pages 2 -o out.txt
"""

from __future__ import annotations

import argparse
import os
import sys

import fitz  # PyMuPDF
import pytesseract
from PIL import Image


def ocr_page(page: fitz.Page, zoom: float = 2.0) -> str:
    # Render page to a reasonably high-res image for OCR.
    mat = fitz.Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=mat, alpha=False)
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    txt = pytesseract.image_to_string(img)
    return txt


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf", help="Input PDF")
    ap.add_argument("--pages", type=int, default=2, help="Number of pages to OCR (default: 2)")
    ap.add_argument("-o", "--out", required=True, help="Output text file")
    args = ap.parse_args()

    doc = fitz.open(args.pdf)
    n = min(args.pages, doc.page_count)

    parts: list[str] = []
    parts.append(f"OCR_SOURCE: {args.pdf}\n")
    parts.append(f"OCR_PAGES: 1..{n}\n")
    parts.append("\n")

    for i in range(n):
        parts.append(f"\n\n===== OCR PAGE {i+1} =====\n")
        try:
            parts.append(ocr_page(doc[i]))
        except Exception as e:
            parts.append(f"[OCR ERROR] {e}\n")

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        f.write("".join(parts).rstrip() + "\n")

    print(args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

