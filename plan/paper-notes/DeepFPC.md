# DeepFPC: A Deep Unfolded Network for Sparse Signal Recovery from 1-Bit Measurements

**Authors:** Xiao, Peng; Liao, Bin; Deligiannis, Nikos
**Venue:** Signal Processing, Vol 176, pp 107699, 2020
**Zotero Key:** SK2QQHHD
**Category:** Methods

---

## Research Question
How can algorithm unrolling be applied to sparse signal recovery from 1-bit measurements for DOA estimation?

## Core Method
- Unfolds the fixed-point continuation (FPC) algorithm into a deep network
- Each layer corresponds to one iteration of FPC with learnable parameters
- Applied to DOA estimation from 1-bit quantized measurements
- Network architecture resembles deep residual learning
- Bridges iterative sparse recovery and deep networks

## Key Findings
- Deep unfolding improves convergence speed over iterative FPC
- Learnable parameters adapt to signal statistics
- Effective DOA estimation from severely quantized (1-bit) measurements
- Demonstrates the algorithm unrolling paradigm for DOA applications

## Limitations
- Sparse recovery formulation requires grid discretization
- 1-bit scenario is extreme; less clear advantage for higher resolution
- Fixed network depth limits adaptability

## Relevance to Our Research
Deep unfolding approach for DOA under quantization — parallel methodology to SubspaceNet. While SubspaceNet learns surrogate covariance, DeepFPC unrolls iterative sparse recovery. Both represent model-based deep learning but from different perspectives.
