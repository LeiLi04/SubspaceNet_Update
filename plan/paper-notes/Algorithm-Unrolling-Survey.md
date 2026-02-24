# Algorithm Unrolling: Interpretable, Efficient Deep Learning for Signal and Image Processing

**Authors:** Monga, Vishal; Li, Yuelong; Eldar, Yonina C.
**Venue:** IEEE J. Selected Topics in Signal Processing, Vol 15(1), pp 130-168, 2021
**Zotero Key:** 57Z6GB2F
**Category:** Methods

---

## Research Question
How does algorithm unrolling bridge iterative algorithms and deep networks for signal and image processing?

## Core Method
- Comprehensive review of the algorithm unrolling paradigm
- Maps each iteration of an iterative algorithm to a layer of a deep network
- Learnable parameters replace fixed algorithm parameters
- Covers LISTA, ADMM-Net, and other unrolled architectures
- Provides theoretical analysis of convergence and generalization

## Key Findings
- Algorithm unrolling produces interpretable deep networks with faster convergence than original iterative algorithms
- Fewer parameters than generic deep networks — better data efficiency
- Applicable to sparse recovery, compressed sensing, and signal estimation
- Theoretical connections between unrolled networks and original algorithms

## Limitations
- Survey paper — does not propose new methods
- Fixed depth limits adaptability to problem difficulty
- Some theoretical guarantees only hold under restrictive assumptions

## Relevance to Our Research
Foundational survey providing theoretical grounding for deep unfolding approaches to DOA estimation. SubspaceNet takes a different approach (surrogate covariance) rather than algorithm unrolling, but understanding this paradigm contextualizes the field.
