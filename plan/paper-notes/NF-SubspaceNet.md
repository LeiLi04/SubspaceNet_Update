# Near Field Localization via AI-Aided Subspace Methods (NF-SubspaceNet)

**Authors:** Shmuel, Dor H.; Shlezinger, Nir
**Venue:** arXiv preprint, 2025
**Zotero Key:** W3BJUB7D
**Category:** Core Papers

---

## Research Question
How can SubspaceNet be extended to near-field localization where both angle and range must be estimated?

## Core Method
- Extends the SubspaceNet paradigm to near-field scenarios
- Deep learning-augmented 2D MUSIC algorithm (DCD-MUSIC)
- Learns surrogate covariance matrix for near-field conditions
- Cascaded angle-range estimation with reduced complexity
- Near-field model accounts for spherical wavefronts rather than planar

## Key Findings
- Successfully extends surrogate covariance learning to near-field localization
- DCD-MUSIC achieves cascaded angle-range estimation efficiently
- Demonstrates the versatility of the SubspaceNet paradigm beyond far-field DOA
- Handles near-field-specific challenges (range-angle coupling, Fresnel approximation)

## Limitations
- Preprint — not yet peer-reviewed
- Near-field scenarios require denser arrays or higher frequencies
- Computational cost of 2D search (angle + range)
- Limited to scenarios within the Fresnel region

## Relevance to Our Research
Direct extension of SubspaceNet by the same authors. Demonstrates that the surrogate covariance learning paradigm generalizes beyond far-field DOA to near-field localization. Validates the research direction of building upon SubspaceNet.
