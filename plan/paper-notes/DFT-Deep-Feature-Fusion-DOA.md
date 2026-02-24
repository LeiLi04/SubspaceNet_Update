# DOA Estimation with Discrete Fourier Transform and Deep Feature Fusion (DFNeT)

**Authors:** Zheng, He; Zheng, Guimei; Song, Yuwei; Xiao, Liyuan; Qin, Cong
**Venue:** Electronics, Vol 14(12), pp 2449, 2025
**Zotero Key:** 95GJRW6P
**Category:** To-Read

---

## Research Question
How can DFT-based feature fusion improve DOA estimation robustness and interpretability over conventional CNNs?

## Core Method
- DFNeT: DFT-based deep learning framework for DOA estimation
- DFT-based deep feature fusion to denoise covariance matrices
- Integrates spatial and frequency-domain information
- Series of DFT modules extract discriminative frequency-domain features
- Mitigates noise via explicit frequency-domain operations

## Key Findings
- DFT-enhanced networks improve global modeling and noise robustness
- Frequency-domain operations enhance feature extraction interpretability
- Better computational efficiency than attention-based global modeling
- Effectively denoises covariance matrices through spatial-frequency fusion

## Limitations
- Published in Electronics (mid-tier venue)
- DFT-based approach may miss non-stationary features
- Limited to specific covariance input representations

## Relevance to Our Research
Frequency-domain feature extraction for covariance denoising — alternative signal representation that could complement SubspaceNet's spatial-domain autoencoder approach.
