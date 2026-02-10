#!/usr/bin/env python3
"""Generate a structured IEEE-style review template in Markdown."""

from __future__ import annotations

import argparse
from pathlib import Path


def build_template(title: str, venue: str, paper_id: str | None) -> str:
    header_id = paper_id if paper_id else "N/A"
    return f"""# IEEE Review Draft

- Paper Title: {title}
- Venue: {venue}
- Paper ID: {header_id}

## 1. Summary
- 

## 2. Strengths
- 

## 3. Major Concerns
- 

## 4. Minor Concerns
- 

## 5. Reproducibility And Ethics
- Reproducibility: 
- Ethics: 

## 6. Scores (1-5)
- Novelty: 
- Technical Soundness: 
- Experimental Rigor: 
- Clarity: 
- Reproducibility: 

## 7. Recommendation
- Decision: 
- Confidence: 
- Rationale: 
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build an IEEE review markdown template.")
    parser.add_argument("--title", required=True, help="Paper title")
    parser.add_argument("--venue", default="IEEE Venue", help="Target venue or track")
    parser.add_argument("--paper-id", default=None, help="Paper identifier")
    parser.add_argument("--output", required=True, help="Output markdown path")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    content = build_template(args.title, args.venue, args.paper_id)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(content, encoding="utf-8")
    print(f"Wrote review template to {output}")


if __name__ == "__main__":
    main()
