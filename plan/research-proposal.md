# Research Proposal: Multiscale Unsupervised Online Adaptation for Subspace-based Deep Learning DOA Estimation

**Date:** 2026-02-23
**Related Collection:** Research-SubspaceDOA-2026-02

---

## 1. Problem Statement

AI-aided direction-of-arrival (DOA) estimators, particularly those built on subspace methods augmented with deep neural networks (e.g., SubspaceNet), achieve state-of-the-art performance under training conditions. However, they suffer from significant performance degradation when deployed in environments that differ from training—due to calibration drifts, hardware aging, changing propagation conditions, or varying source statistics. Current adaptation strategies either require labeled data (impractical in deployment) or address only single-type distribution shifts.

**Research Question:** How can we enable subspace-based deep learning DOA estimators to continuously and autonomously adapt to multiscale distribution shifts during deployment, without requiring ground-truth labels?

---

## 2. Background and Motivation

### 2.1 State of the Art

SubspaceNet \cite{shmuel_subspacenet_2025} learns a surrogate covariance matrix via a convolutional autoencoder trained end-to-end through Root-MUSIC, enabling robust DOA estimation under coherent sources, low SNR, and limited snapshots. DA-MUSIC \cite{merkofer_da-music_2024} augments MUSIC with learned temporal correlations. TransMUSIC \cite{ji_transmusic_2024} handles quantized observations via Transformer-based subspace learning.

The recent work by Konstantino et al. \cite{konstantino_unsupervised_2025} introduces unsupervised adaptation via downstream tracking innovations—using Kalman filter statistics to detect distribution shifts and adapt the DOA estimator online. This provides the foundational framework for our proposed research.

### 2.2 Identified Gaps

1. **Single-scale adaptation**: Existing methods handle one type of drift at a time (e.g., array miscalibration). Real deployments face simultaneous drifts at multiple scales (array, environment, sources).
2. **Static adaptation triggers**: Current methods use fixed thresholds for drift detection. Adaptive, data-driven triggering mechanisms are needed.
3. **No theoretical guarantees**: Convergence and performance bounds for online adaptation of learned subspace methods are absent.
4. **Limited real-world validation**: Most results are simulation-only.

---

## 3. Proposed Approach

### 3.1 Multiscale Adaptation Framework

We propose a hierarchical adaptation framework operating at three timescales:

```
Fast adaptation (per-block):    Source dynamics → Kalman tracking
Medium adaptation (windowed):   Environment changes → Innovation-based DNN update
Slow adaptation (periodic):     Hardware drifts → Full surrogate covariance relearning
```

**Key innovation:** Different types of distribution shifts manifest at different frequencies in the innovation statistics. By decomposing the innovation signal into frequency bands, we can detect and respond to each type of drift independently.

### 3.2 Architecture: Adaptive SubspaceNet

```
Input: X_i (array snapshots)
    ↓
[Surrogate Covariance Autoencoder] ← (slow adaptation: array calibration)
    ↓
[Learned Subspace Decomposition]   ← (medium adaptation: environment)
    ↓
[Root-MUSIC / MUSIC / ESPRIT]
    ↓
θ̂_i (DOA estimates)
    ↓
[Downstream Tracker (EKF/UKF)]     ← (fast adaptation: source dynamics)
    ↓
θ̃_i (filtered estimates)
    ↓
[Multiscale Innovation Monitor]
    ↓
[Adaptation Controller] → triggers appropriate adaptation level
```

### 3.3 Unsupervised Loss Functions

Building on the innovation-based loss from \cite{konstantino_unsupervised_2025}:

1. **Mean-Squared Innovation Error (MSIE)**: Existing baseline for medium-timescale adaptation.
2. **Innovation Spectrum Analysis**: FFT of innovation sequence to detect drift frequency characteristics.
3. **Normalized Innovation Squared (NIS) Test**: Chi-squared consistency test for Kalman filter health monitoring.
4. **Multi-resolution Wavelet Analysis**: Decompose innovations across temporal scales for multiscale drift detection.

### 3.4 Theoretical Contributions

- **Convergence analysis** of online SGD applied to the MSIE loss under Markovian state evolution.
- **Regret bounds** comparing adaptive vs. oracle (supervised) online learning.
- **Conditions for identifiability** of different drift types from innovation statistics alone.

---

## 4. Experimental Plan

### 4.1 Simulation Studies

| Scenario | Array | Sources | Drift Type | Metric |
|----------|-------|---------|------------|--------|
| Baseline | ULA-9 | M=3, narrowband | None | RMSPE |
| Single drift | ULA-9 | M=3 | Calibration only | RMSPE, adaptation delay |
| Multi-drift | ULA-9 | M=3 | Calibration + environment | RMSPE, drift detection accuracy |
| Scaling | ULA-32/64 | M=5-10 | Multi-drift | RMSPE, computation time |
| Quantized | ULA-9, 1-bit ADC | M=3 | Multi-drift | RMSPE |
| Near-field | ULA-16 | M=3, near-field | Multi-drift | RMSPE, range error |

### 4.2 Real-World Validation

- **USRP-based testbed**: Over-the-air DOA estimation with real calibration errors.
- **Acoustic DOA**: Microphone array for speaker localization in changing room conditions.

### 4.3 Baselines

1. Static SubspaceNet (pre-trained, no adaptation)
2. Online supervised SubspaceNet (oracle upper bound)
3. Single-scale unsupervised adaptation \cite{konstantino_unsupervised_2025}
4. Domain-adaptive methods \cite{shen_domain_2025}
5. Classical MUSIC/ESPRIT (no DNN)

---

## 5. Timeline

| Phase | Duration | Activities |
|-------|----------|-----------|
| Phase 1 | Months 1-3 | Framework design, multiscale innovation analysis |
| Phase 2 | Months 3-6 | Implementation of adaptive SubspaceNet, simulation studies |
| Phase 3 | Months 6-8 | Theoretical analysis (convergence, regret bounds) |
| Phase 4 | Months 8-10 | Real-world validation, USRP experiments |
| Phase 5 | Months 10-12 | Paper writing, submission to IEEE TSP or NeurIPS |

---

## 6. Expected Contributions

1. **Multiscale unsupervised adaptation framework** for subspace-based deep learning DOA estimators
2. **Innovation spectrum analysis** method for drift type identification
3. **Convergence guarantees** for online adaptation of learned subspace methods
4. **Open-source implementation** extending the SubspaceNet codebase

---

## 7. Target Venues

- **Primary:** IEEE Transactions on Signal Processing (TSP)
- **Conference:** ICASSP 2027, IEEE SAM 2026
- **Stretch:** NeurIPS 2026 (if theoretical contributions are strong)

---

## 8. Related Work Positioning

This research directly builds on:
- SubspaceNet \cite{shmuel_subspacenet_2025} — the base architecture
- Unsupervised adaptation via tracking \cite{konstantino_unsupervised_2025} — the adaptation paradigm
- Algorithm unrolling \cite{monga_algorithm_2021} — theoretical framework for model-based DL

And addresses gaps identified in:
- Domain adaptation for DOA \cite{shen_domain_2025}
- TransMUSIC quantized DOA \cite{ji_transmusic_2024}
- Near-field localization \cite{shmuel_near_2025}
