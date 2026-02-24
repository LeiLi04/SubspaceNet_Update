# Learning-Based Robust DOA Estimation with Array Imperfections

**Authors:** Unknown
**Venue:** Signal Processing, 2025
**Zotero Key:** SGXKVFZ9
**Category:** Methods

---

## Research Question
How can learning-based methods achieve robust DOA estimation in the presence of array imperfections?

## Core Method
- CANN (Convolutional-Attention Neural Network) architecture
- Uses covariance vectors as input representation
- Demonstrates advantages over I/Q sequence inputs for handling array imperfections
- Designed for robustness to mutual coupling, gain/phase errors, sensor position errors

## Key Findings
- Covariance vector inputs are more robust than raw I/Q inputs under array imperfections
- CANN architecture effectively compensates for various array imperfection types
- Input representation choice significantly impacts robustness

## Limitations
- Limited metadata available (author unknown in Zotero entry)
- Specific imperfection types and severity ranges not fully characterized

## Relevance to Our Research
Addresses array imperfection robustness — a key challenge also handled by SubspaceNet. The finding that covariance-based inputs outperform raw signals supports SubspaceNet's covariance-centric approach.
