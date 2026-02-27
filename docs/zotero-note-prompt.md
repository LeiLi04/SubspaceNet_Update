# Zotero Reading Note Prompt

> Append this prompt after your template when using GPT.

---

## Prompt

```
You are a senior PhD researcher acting as a rigorous peer reviewer. Read the attached paper using the three-phase process below, and fill in EACH section of the template above. The CORE GOAL: this note must be a STANDALONE substitute — the reader should fully understand "what, why, how, and how well" WITHOUT reading the original paper.

===================================================================
Phase 1: SCANNING → Fill in「📜 Research Core」
===================================================================

### ⚙️ Content

Extract and quote directly from the paper:
- **Purpose**: What phenomenon or theoretical gap drives this research?
- **Research Question**: What central question threads trough the entire paper?
- **Focus**: What is the core object of study?
- **Contribution**: List each contribution as the author states it.
- Then synthesize into one positioning paragraph: Task → Gap → Proposal → Core Claim.

### 💡 Innovations

For each innovation point:
- [What]: Specific technical novelty
- [Why it matters]: What problem does it solve
- [Difference]: How it differs from the closest prior work
- Be maximally specific — not "uses deep learning" but "replaces the learned decoder with a deterministic model-based function..."

### 🧩 Shortcomings

Two separate parts:
- **Author-acknowledged**: Quote directly from the paper, then assess the impact
- **Your critique**: Act as a harsh reviewer. For each point, state: the issue → severity (minor/moderate/major) → impact on the paper's claims

===================================================================
Phase 2: DEEP READING → Fill in「🔁 Research Content」
===================================================================

Read as a "demanding peer reviewer". For each section below, not only summarize but VERIFY and CRITIQUE.

### 💧 Data

- Full description: data source, distributions, dimensions, parameter ranges, train/val/test split, preprocessing
- If synthetic: the EXACT generative model, parameter distributions, sampling procedure
- If real-world: dataset name, size, source, known biases
- 🔍 Critique: Is the data sufficient? Is the sampling representative? Are there coverage gaps?

### 👩🏻‍💻 Method

⚠️ THIS MUST BE THE LONGEST SECTION (~40-50% of the entire note).

The goal of this section is to TELL THE AUTHOR'S STORY: what problem formulation leads to what insight, which then motivates what architecture/algorithm. The reader should finish this section understanding the LOGIC CHAIN, not just a list of equations.

Write as a NARRATIVE, not a catalog. Inline key equations where they naturally appear in the story. Detailed formula tables go to the Appendix.

(a) **Problem Formulation → Key Insight**
    - What mathematical framework does the paper start from? (e.g., signal model, objective function)
    - What is the core difficulty / bottleneck that existing approaches cannot solve?
    - What is the KEY INSIGHT or "aha moment" that unlocks the proposed solution?
    - Inline the 2-3 most important equations that define the problem and the insight.
      Use Eq.(X) references for the rest — the Appendix has full details.

(b) **Method Overview (Logic Flow)**
    - Describe the overall approach as a coherent narrative:
      "Because of [insight], the authors propose [architecture/algorithm], which works by [mechanism]."
    - Pipeline: Input → Step 1 → Step 2 → ... → Output
      For each step: what it does and WHY (not just layer dimensions — explain the reasoning)
    - How does information flow? What are the key intermediate representations?

(c) **Core Technical Contributions (Deep Dive)**
    - For each main technical contribution, explain:
      - What problem it solves in the pipeline
      - How it works (with inline equations where natural)
      - Why this design over alternatives (what problem the alternatives would cause)
    - Loss function: explain the derivation LOGIC (why this objective makes sense), not just the math

(d) **Design Choices & Constraints**
    - For each non-obvious decision: what problem it solves → alternatives considered → why this one
    - Implementation details that matter for reproduction (activations, constraints, parameterization tricks)

(e) **Variants**: If the method has multiple configurations, describe each with differences and when to use which.

🔍 Critique: Does the logic chain hold? Assumptions valid? Hidden failure modes? Gaps between formulation and implementation?

### 🔬 Experiment

- Setup: full configuration, evaluation protocol, metrics (with metric formulas)
- ALL baselines: name + one-sentence description
- Quantitative results: COPY actual numbers or describe figure trends:
  "Fig.X shows [what]. At [condition], Method achieves [value] vs. Baseline at [value]."
- Ablation: which component contributes how much, with numbers
- Statistical rigor: error bars, confidence intervals, p-values reported?
- 🔍 Critique: Baseline selection fair? Important baselines missing? Cherry-picked scenarios? Edge cases tested?

### 📜 Conclusion

- Main findings (2-3 sentences with quantitative support)
- Future work directions as stated by the authors
- Your assessment: are the conclusions fully supported by the evidence?

===================================================================
Phase 3: CONSOLIDATION → Fill in「🤔 Personal Summary」
===================================================================

### 🙋‍♀️ Key Records

- 3-5 most important technical takeaways, each with a concrete example from the paper
- Which design choices are transferable? Be specific about HOW to reuse them.
- Key terminology or methods encountered — record definitions in context

### 📌 To be resolved

- Assumptions that may not hold in practice — list each with its consequence
- Missing experiments you would want to see
- Contradictory findings in the literature not addressed by this paper
- What must be verified before building on this work?

### 💭 Thought Inspiration

- Connection to my research: I am a PhD student working at the intersection of AI and Communication Engineering (signal processing, array processing, DOA estimation, deep learning-based methods for wireless systems). Evaluate this paper from both the ML methodology and the signal processing theory perspectives.
- Extensions, method combinations, or new experiments this inspires
- If you were to write a follow-up paper, what would the research question be?

===================================================================
Appendix: Formula Catalog → Fill in「📎 Appendix: Formula Catalog」
===================================================================

This section is a REFERENCE TABLE — exhaustive but mechanical. It supplements the narrative Method section.

🚨 HARD RULE: List EVERY equation from the paper — numbered equations, unnumbered inline derivations, metric definitions, loss functions, constraint formulations — ALL of them.

Present in ORDER of appearance. For EACH equation:

- **Eq.(X)** [descriptive name]
  $$
  [formula in LaTeX]
  $$
- Variable Table (EVERY symbol must be defined, no exceptions):
  | Symbol | Meaning | Dimension/Range |
  |--------|---------|-----------------|
  | ...    | ...     | ...             |
- 💡 One-sentence intuition
- ← Derivation context: from Eq.(Y) by [what operation/assumption]

After all equations, add a **Formula Dependency Map**:
```

Eq.(1) [Signal Model]
  → Eq.(4) [Covariance Matrix]  (by taking expectation)
    → Eq.(5) [Joint Likelihood]  (by assuming i.i.d. snapshots)
      → Eq.(6) [SML Objective]   (by taking log + simplifying)

```

===================================================================
RULES
===================================================================

1. Fill in EVERY section header from the template. Do not skip or merge sections.
2. LaTeX: $...$ inline, $$...$$ display. ALL equations must appear (in Appendix).
3. Use bullet points, not long paragraphs. Use tables for comparisons.
4. When quoting the paper, use "> ..." blockquote with section reference.

### Language Rule — MANDATORY

5. Draft in English first, then translate the ENTIRE note into Chinese as the final output.
   - All section headers, descriptions, critiques, and summaries → Chinese
   - Keep the following in English (do NOT translate):
     - LaTeX formulas and variable names (e.g., $C_y$, $\theta$, RMSPE)
     - Proper nouns: method names (MUSIC, SPICE, SubspaceNet), venue names (NeurIPS, SPAWC), author names
     - Technical abbreviations: DOA, SML, AE, CNN, MLP, CRB, UCA, ULA, SNR
     - Code snippets and file paths
   - Variable table headers → Chinese: 符号 / 含义 / 维度/范围
   - Section header examples: "⚙️ 内容", "💡 创新点", "🧩 不足", "💧 数据", "👩🏻‍💻 方法", "🔬 实验", "📜 结论", "🙋‍♀️ 关键记录", "📌 待解决", "💭 思考启发"

===================================================================
SELF-CHECK (verify before output)
===================================================================

- [ ] ⚙️ Content: Purpose, Research Question, Focus, Contribution each explicitly stated?
- [ ] 👩🏻‍💻 Method: Logic chain clear? (Problem → Insight → Architecture → Why it works)
- [ ] 👩🏻‍💻 Method: Pipeline complete enough for reimplementation?
- [ ] 📎 Appendix: Count equations in paper = count in appendix? Every symbol defined?
- [ ] 📎 Appendix: Formula Dependency Map included?
- [ ] 🔬 Experiment: Actual numbers/trends reported (not just "performs well")?
- [ ] 🧩 Shortcomings + each 🔍 Critique: At least one critical observation per section?
- [ ] 🙋‍♀️ Key Records: Takeaways are specific and actionable?
- [ ] Overall: Can someone in the field understand the FULL paper from this note alone?
```
