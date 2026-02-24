# Deep Tensor 2-D DOA Estimation for URA

**Authors:** Zheng, Hang; Shi, Zhiguo; Zhou, Chengwei; Vorobyov, Sergiy A.; Gu, Yujie
**Venue:** IEEE Trans. Signal Processing, Vol 72, pp 4065-4080, 2024
**Zotero Key:** 3KQKA37F
**Category:** Core Papers

---

## Research Question
How can tensor decomposition be combined with deep learning for 2D DOA estimation using uniform rectangular arrays (URAs)?

## Core Method
- Exploits multi-dimensional tensor structure of URA data
- Combines tensor decomposition with deep learning for joint azimuth-elevation estimation
- Leverages the inherent multi-linear structure that 1D methods cannot exploit
- Published in IEEE TSP — rigorous theoretical and experimental treatment

## Key Findings
- Tensor-based representation preserves multi-dimensional array structure better than vectorized approaches
- DL-enhanced tensor decomposition outperforms both pure tensor and pure DL methods for 2D DOA
- Demonstrates the value of exploiting array geometry in the DL architecture design
- Applicable to practical URA configurations

## Limitations
- Specific to uniform rectangular arrays; doesn't generalize to arbitrary 2D geometries
- Tensor operations add computational complexity
- 2D DOA estimation inherently more complex than 1D

## Relevance to Our Research
Extends DOA estimation to 2D (azimuth + elevation) using tensor structure — complementary to SubspaceNet's 1D ULA focus. Shows how array geometry can be incorporated into DL architecture design.
