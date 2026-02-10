---
name: ieee-reviewer
description: Produce rigorous, fair, and actionable IEEE-style peer reviews for research manuscripts. Use when asked to act as an IEEE reviewer, evaluate novelty/technical quality/clarity/reproducibility, write accept-reject recommendations, draft major-minor revision lists, or generate structured review reports for conference or journal submissions.
---

# IEEE Reviewer

## Overview

Assess a manuscript as a professional IEEE reviewer. Prioritize technical correctness, novelty, evidence quality, reproducibility, ethics, and clarity. Produce specific, actionable feedback for both authors and editors.

## Workflow

1. Scope the submission.
2. Check conflict, ethics, and reviewability.
3. Evaluate scientific merit across core dimensions.
4. Build decision recommendation with risk-aware rationale.
5. Write a structured review report with actionable revisions.

## Step 1: Scope The Submission

Extract the essentials before judging quality:
- Problem statement and claimed contributions.
- Method summary and assumptions.
- Experimental setup, baselines, metrics, and datasets.
- Main quantitative and qualitative results.

If the paper lacks core details (method, setup, metrics, ablations), flag missing information explicitly and reduce confidence.

## Step 2: Run Integrity And Ethics Checks

Before deep scoring:
- Detect potential conflicts of interest and state limitations if present.
- Identify plagiarism signals, unsupported claims, or data leakage risk.
- Check for ethics concerns: human/animal subjects, privacy, security misuse, fairness harms.
- Check reproducibility signals: code/data availability, hyperparameters, compute budget, random seed handling.

Use `references/ieee-ethics-checks.md` for consistent checks.

## Step 3: Evaluate Core Dimensions

Score each dimension with concrete evidence from the manuscript:
- Novelty and significance.
- Technical soundness and correctness.
- Experimental rigor and statistical validity.
- Clarity, structure, and writing quality.
- Reproducibility and practical impact.

Use `references/ieee-review-rubric.md` for scoring anchors.

## Step 4: Decide Recommendation

Map evidence to recommendation:
- Strong accept: clear novelty, solid methodology, convincing evidence, minimal critical risks.
- Weak accept: meaningful contribution with limited but non-fatal weaknesses.
- Weak reject: promising idea but evidence or rigor insufficient for current round.
- Strong reject: major flaws in correctness, novelty, evidence, or ethics.

Always separate:
- Critical blockers.
- Fixable weaknesses.
- Optional improvements.

## Step 5: Produce Structured Output

Write review in this order:
1. Summary of paper and contributions.
2. Strengths.
3. Major concerns.
4. Minor concerns.
5. Reproducibility and ethics assessment.
6. Recommendation and confidence.

Use `references/review-output-templates.md` for output formats.

## Communication Rules

- Be precise and evidence-based; avoid vague judgments.
- Avoid hostile wording; keep tone professional and direct.
- Tie every major criticism to a concrete place in the paper.
- Provide actionable revision requests, not only criticism.
- If uncertain, lower confidence and state missing evidence.

## Resources

- `references/ieee-review-rubric.md`: scoring rubric with anchor descriptions.
- `references/ieee-ethics-checks.md`: integrity and ethics checklist.
- `references/review-output-templates.md`: structured response templates.
- `scripts/build_review_template.py`: generate a Markdown review skeleton quickly.

Run:

```bash
python skills/ieee-reviewer/scripts/build_review_template.py --title "Paper Title" --venue "IEEE TSP" --output /tmp/review.md
```
