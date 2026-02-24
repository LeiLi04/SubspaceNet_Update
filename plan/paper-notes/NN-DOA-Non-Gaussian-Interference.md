# Neural-Network-Based DOA Estimation in the Presence of Non-Gaussian Interference

**Authors:** Feintuch, Stefan; Tabrikian, Joseph; Bilik, Igal; Permuter, Haim
**Venue:** IEEE Trans. Aerospace and Electronic Systems, Vol 60(1), pp 119-132, 2024
**Zotero Key:** BNLGHIIB
**Category:** Methods

---

## Research Question
How can neural networks perform DOA estimation in multisource scenarios with unknown source count under non-Gaussian spatially-colored interference?

## Core Method
- NN-based spatial spectrum estimation
- Handles non-Gaussian, spatially-colored interference (violates classical subspace assumptions)
- Unknown number of sources — no prior knowledge required
- Learns to suppress non-Gaussian interference that second-order methods cannot model

## Key Findings
- Significantly outperforms conventional and NN-based approaches under non-Gaussian interference
- Classical subspace methods (MUSIC, ESPRIT) degrade substantially under non-Gaussian conditions
- Most pronounced advantages at low SNR and strong interference
- Published in prestigious IEEE TAES venue

## Limitations
- Requires training data representative of the interference environment
- Generalization to unseen interference distributions may be limited
- May need retraining for different interference environments

## Relevance to Our Research
Addresses non-Gaussian interference where classical subspace methods fundamentally fail. Provides insights for extending SubspaceNet to non-Gaussian environments. The need for environment-specific training connects to our adaptation research direction.
