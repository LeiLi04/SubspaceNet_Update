---
name: annotation
description: Deeply annotate existing Python code for ML/AI research readability with bilingual (Chinese-English) Google-style docstrings, tensor shape-flow tracking, and step-by-step inline comments. Use when users ask for NeurIPS/CVPR-style appendix annotations, PyTorch/HuggingFace-like code explanations, Unicode math notation, or strict annotation-only edits without changing code logic.
---
# Annotation

## Overview

Annotate existing Python code to publication-grade quality while preserving executable behavior exactly. Focus on shape flow, mathematical intent, engineering rationale, and bilingual readability.

## Execution Workflow

1. Read the full target file before editing.
2. Keep all logic unchanged; only add or refine comments/docstrings.
3. Add or update file-level top docstring:
   - Algorithm Summary (one sentence)
   - Symbol Legend (dimensions and symbols)
   - Core Tensor Flow (input -> bottleneck -> output)
4. Add bilingual Google-style docstrings to key functions/methods:
   - Chinese for explanatory logic
   - English for standard technical terms
5. Add 3-level inline comment hierarchy:
   - Macro: `STEP 0X`
   - Meso: `step X.X`
   - Micro: `step X.Xa` with `Why`, `Maths`, `Shape Flow`
6. Enforce output contract requested by user (often full Python code only).

## Hard Constraints

1. Never modify code behavior, control flow, variable names, imports, or structure unless explicitly requested.
2. Annotation-only edits: comments/docstrings/explanatory text.
3. Never use LaTeX notation in comments/docstrings:
   - forbidden: `$...$`, `\frac`, `\sum`, `\alpha`
4. Use Unicode math symbols when writing formulas:
   - `Σ`, `∈`, `ℝ`, `∂`, `∇`, `⊙`, `×`, `√`, `ᵀ`
5. Explain all magic numbers/constants (e.g., `0.1`, `1e-5`, `dim=-1`).
6. Explicitly mark broadcasting in shape flow.

## Annotation Standard

### File-level Context

At file top, include:

- `算法摘要 (Algorithm Summary)`: one-sentence purpose.
- `符号图例 (Symbol Legend)`: dimensions and symbols.
- `核心张量流 (Core Tensor Flow)`: input -> bottleneck -> output.

Recommended dimensions:

- `B`: Batch size
- `T`: Sequence length
- `D`: Embedding dimension
- `H`: Number of heads
- `d`: Per-head dimension (`d = D / H`)

### Google-style Docstring (Bilingual)

Each key function/method should include:

- `Args:` type + Chinese explanation + initial shape
- `Returns:` meaning + final shape
- `Math & Logic:` Unicode equation(s), e.g. `Attention(Q, K, V) = softmax((QKᵀ) / √d)V`
- `References (Optional):` e.g. `Eq. 1 in Vaswani et al. (2017)`

### Inline Shape-Flow Pyramid

Use this density and format:

- Macro block for each major stage (`STEP 0X`)
- Meso block for each submodule (`step X.X`)
- Micro block per atomic operation (`step X.Xa`) with:
  - Maths
  - Shape Flow

Shape-flow examples:

- `[B, T, D] -> view -> [B, T, H, d] -> permute -> [B, H, T, d]`
- `[B, T, D] + [1, 1, D] (Broadcast) -> [B, T, D]`

## Quality Gate

Before returning:

1. Confirm no code logic changes.
2. Confirm no LaTeX syntax remains.
3. Confirm Unicode symbols are used for formulas.
4. Confirm all key tensor ops include shape flow.
5. Confirm all constants are explained.
6. Confirm output format matches user request.

## Resource

Use `references/annotation-template.md` as the canonical annotation skeleton.
