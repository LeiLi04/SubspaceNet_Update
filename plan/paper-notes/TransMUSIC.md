# TransMUSIC: A Transformer-Aided Subspace Method for DOA Estimation with Low-Resolution ADCs

**Authors:** Ji, Junkai; Mao, Wei; Xi, Feng; Chen, Shengyao
**Venue:** ICASSP 2024, pp 8576-8580
**Zotero Key:** MJ4N4B9V
**Category:** Core Papers

---

## Research Question
How can DOA estimation be performed with low-resolution ADCs (e.g., 1-bit quantization) using a Transformer-aided subspace method?

## Core Method
- Transformer module learns the noise subspace directly from quantized data
- Attention mechanism captures global correlations across snapshots
- Unifies DOA recovery and model order estimation in a single framework
- Addresses the severe information loss caused by low-resolution ADC quantization

## Key Findings
- Enables MUSIC-like DOA estimation even with 1-bit ADC data
- Transformer attention effectively captures global snapshot correlations
- Joint DOA and model order estimation improves robustness
- Outperforms classical methods designed for quantized observations

## Limitations
- ICASSP conference paper — limited experimental validation scope
- Transformer computational complexity scales quadratically with sequence length
- Focus on low-resolution ADC scenario; less clear advantage for high-resolution data
- Single array geometry tested

## Relevance to Our Research
Alternative architecture (Transformer vs. CNN autoencoder) for subspace learning. Addresses quantized data scenario not covered by SubspaceNet. The attention mechanism's global correlation capture is complementary to SubspaceNet's convolutional approach.
