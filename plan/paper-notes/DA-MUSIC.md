# DA-MUSIC: Data-Driven DoA Estimation via Deep Augmented MUSIC Algorithm

**Authors:** Merkofer, Julian P.; Revach, Guy; Shlezinger, Nir; Routtenberg, Tirza; van Sloun, Ruud J. G.
**Venue:** IEEE Trans. Vehicular Technology, Vol 73(2), pp 2771-2785, 2024
**Zotero Key:** TQ3JG472
**Category:** Core Papers

---

## Research Question
How can the MUSIC algorithm be augmented with data-driven components while preserving its model-based spectral analysis flow?

## Core Method
- Hybrid model-based/data-driven DOA estimator
- Dedicated RNN learns temporal correlations from data
- Replaces sample covariance estimation and source number detection with neural components
- Preserves the MUSIC spectral analysis flow (subspace decomposition → spectrum computation → peak finding)
- Validated on narrowband, broadband, and real seismic data

## Key Findings
- Successfully augments MUSIC with learned components for improved performance
- Works across narrowband, broadband, and real-world seismic data
- Demonstrates that selective neural augmentation of classical algorithms outperforms both pure classical and pure DL approaches
- Predecessor to SubspaceNet — pioneered the deep augmented subspace paradigm

## Limitations
- RNN architecture may have scalability issues for large arrays
- Requires labeled training data
- MUSIC spectral peak search has grid resolution limitations
- Sequential RNN processing limits throughput

## Relevance to Our Research
Key predecessor to SubspaceNet from the same research group (Shlezinger, van Sloun). Established the principle of selectively augmenting classical subspace methods with neural components. DA-MUSIC's RNN-based approach inspired SubspaceNet's more general surrogate covariance paradigm.
