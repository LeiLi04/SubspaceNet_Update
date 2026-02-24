# Literature Review: Subspace-based Deep Learning for DOA Estimation

**Topic:** Subspace-based Deep Learning for Direction-of-Arrival Estimation
**Scope:** Focused (2022–2025)
**Date:** 2026-02-23
**Zotero Collection:** Research-SubspaceDOA-2026-02

---

## 1. Introduction

Direction-of-arrival (DOA) estimation is a foundational problem in array signal processing, with applications spanning radar, wireless communications, sonar, and navigation. Classical subspace methods such as MUSIC \cite{schmidt_multiple_1986} and ESPRIT \cite{pillai_array_2012} exploit the eigenstructure of the received signal covariance matrix to achieve high-resolution DOA recovery. However, these methods rely on restrictive assumptions—including narrowband non-coherent sources, fully calibrated arrays, and sufficient snapshots—that limit their robustness in practical deployments.

The past three years have witnessed a paradigm shift toward integrating deep neural networks (DNNs) with classical subspace methods, yielding hybrid estimators that preserve the interpretability of model-based approaches while leveraging the adaptability of data-driven learning. This review systematically categorizes and analyzes 28 papers covering this intersection.

---

## 2. Taxonomy of Approaches

We organize the literature into five categories based on how deep learning interfaces with subspace-based DOA estimation:

### 2.1 Surrogate Covariance Learning

**Core idea:** A DNN learns to map raw observations or sample covariance matrices into a surrogate covariance matrix that is well-conditioned for subspace decomposition.

- **SubspaceNet** \cite{shmuel_subspacenet_2025}: A convolutional autoencoder learns the empirical autocorrelation of the input and is trained end-to-end through the differentiable Root-MUSIC pipeline. Once trained, the learned surrogate covariance can be plugged into any subspace method (MUSIC, ESPRIT, Root-MUSIC). Handles coherent sources, wideband signals, low SNR, calibration mismatches, and limited snapshots. Published in IEEE Trans. Vehicular Technology.

- **NF-SubspaceNet** \cite{shmuel_near_2025}: Extends SubspaceNet to near-field localization via a deep learning-augmented 2D MUSIC algorithm. Introduces DCD-MUSIC for cascaded angle-range estimation with reduced complexity.

- **Covariance reconstruction under limited snapshots** \cite{zhao_doa_2025}: Combines adaptive diagonal loading with a squeeze-and-excitation multi-scale deep convolutional network (SE-MSDCN) to reconstruct structured covariance matrices from few snapshots.

### 2.2 Deep Augmented Subspace Methods

**Core idea:** Replace specific model-mismatch-sensitive components of classical algorithms with learned neural network modules.

- **DA-MUSIC** \cite{merkofer_da-music_2024}: A hybrid model-based/data-driven estimator that augments MUSIC with a dedicated RNN to learn temporal correlations from data. Replaces the sample covariance estimation and source number detection steps with neural components while preserving the MUSIC spectral analysis flow. Validated on narrowband, broadband, and real seismic data.

- **TransMUSIC** \cite{ji_transmusic_2024}: Uses a Transformer module to learn the noise subspace directly from quantized data. The attention mechanism captures global correlations across snapshots, enabling DOA estimation even with 1-bit ADCs. Unifies DOA recovery and model order estimation.

- **DL-Aided Coherent DOA (FTMR)** \cite{hoang_deep_2022}: Applies deep learning to augment the forward-backward spatial smoothing and MUSIC pipeline for coherent source scenarios.

### 2.3 Deep Unfolding / Algorithm Unrolling

**Core idea:** Unroll iterative optimization algorithms into deep network layers with learnable parameters.

- **Algorithm Unrolling survey** \cite{monga_algorithm_2021}: Comprehensive review of the algorithm unrolling paradigm that bridges iterative algorithms and deep networks. Provides the theoretical foundation for applying this methodology to sparse recovery and DOA estimation.

- **DeepFPC** \cite{xiao_deepfpc_2020}: Unfolds the fixed-point continuation algorithm for sparse signal recovery from 1-bit measurements, with application to DOA estimation. Network architecture resembles deep residual learning.

- **DL-Enabled One-Bit DOA** \cite{author_deep_2024}: Deep unrolling for DOA estimation under coarse quantization, approaching DOA as a sparse recovery problem.

- **Unsupervised DOA with Capon Penalty** \cite{zheng_deep_2024}: Introduces deep unfolded layers to remove iterative solution of sparse recovery, constructing an unsupervised learning network where labels are no longer required. Uses threshold Capon spectrum weighted penalty.

### 2.4 End-to-End DNN Approaches

**Core idea:** Purely data-driven networks that learn DOA estimation without explicit subspace decomposition.

- **Super resolution DOA via DNN** \cite{liu_super_2020}: Trains a DNN to directly estimate DOAs from array observations, achieving super-resolution performance comparable to subspace methods.

- **GNN-based DOA estimation** \cite{yang_doa_2023, liu_gnn_2025}: Transforms DOA estimation into a graph learning problem. GNNs capture spatial structure of sensor arrays and adapt to non-uniform sparse arrays without prior information.

- **Deep Tensor 2-D DOA** \cite{zheng_deep_2024b}: Tensor decomposition combined with deep learning for 2D DOA estimation using uniform rectangular arrays (URAs).

- **Multi-Task Learning DOA** \cite{kim_enhancing_2024}: Multi-task CNN that simultaneously estimates the number of sources and their DOAs.

### 2.5 Adaptation and Robustness

**Core idea:** Addressing the distribution shift and generalization challenges of DNN-based DOA estimators.

- **Unsupervised Adaptation via Downstream Tracking** \cite{konstantino_unsupervised_2025}: Proposes a framework for unsupervised online adaptation of AI-based DOA estimators by exploiting Kalman filter innovation statistics. Key insight: DOA estimators are rarely deployed in isolation but are followed by downstream tracking. Uses innovation variance as a drift detector and mean-squared innovation error as unsupervised loss.

- **Domain-Adaptive DOA** \cite{shen_domain_2025}: Combines convolutional autoencoders with domain-adversarial neural networks (DANN) for DOA estimation in complex indoor environments with multipath and domain discrepancies.

- **Transfer Learning for Array Imperfections** \cite{author_deep_2025}: Supervised transfer learning framework that bridges ideal and practical scenarios with array imperfections.

- **Learning-based robust DOA with array imperfections** \cite{author_learning_2025}: CANN architecture using covariance vectors as input, demonstrating advantages over I/Q sequence inputs.

- **Adaptive Deep-Residual DOA** \cite{yao_adaptive_2025}: RI-ResNN-DAE framework for DOA estimation under mixed impulsive and non-uniform Gaussian noise with adaptation to unknown modulation types.

---

## 3. Key Trends

### 3.1 From Black-Box to Model-Based Deep Learning
The dominant trend is the shift from purely data-driven approaches to model-based deep learning, where neural networks are integrated into the algorithmic flow of classical methods rather than replacing them entirely. This preserves interpretability and reduces data requirements.

### 3.2 Handling Challenging Scenarios
Recent methods systematically address:
- **Coherent sources**: SubspaceNet, DA-MUSIC
- **Low SNR / limited snapshots**: SubspaceNet, covariance reconstruction methods
- **Quantized observations**: TransMUSIC, DeepFPC, One-Bit DOA
- **Array imperfections**: Transfer learning frameworks, CANN
- **Wideband signals**: SubspaceNet, DA-MUSIC

### 3.3 Emerging Architectures
- **Transformers** for capturing global correlations across snapshots (TransMUSIC)
- **Graph Neural Networks** for sparse/non-uniform arrays
- **Autoencoders** for covariance learning and domain adaptation

### 3.4 Unsupervised and Self-Supervised Learning
Growing interest in reducing reliance on labeled training data:
- Gridless unsupervised DOA \cite{chen_gridless_2023}
- Unsupervised adaptation via tracking innovations \cite{konstantino_unsupervised_2025}
- Unsupervised deep unfolding \cite{zheng_deep_2024}

---

## 4. Research Gaps

### Gap 1: Online Adaptation Without Ground-Truth Labels
Most DNN-based DOA estimators assume stationary deployment conditions and require labeled data for retraining. The work by Konstantino et al. \cite{konstantino_unsupervised_2025} addresses this for single-type distribution shifts, but **multiscale adaptation** (simultaneously handling drifts in array calibration, propagation environment, and source statistics) remains unexplored. Additionally, adaptation across fundamentally different array geometries or frequency bands has not been addressed.

### Gap 2: Scalability to Massive Arrays and Near-Field Regimes
While NF-SubspaceNet extends to near-field, the computational scaling of learned surrogate covariance approaches to massive MIMO arrays (hundreds of elements) is unclear. The interaction between spatial non-stationarity in massive arrays and learned subspace decomposition is an open problem.

### Gap 3: Theoretical Performance Guarantees
Existing works demonstrate empirical improvements but lack theoretical analysis of:
- Convergence guarantees for learned covariance surrogates
- Sample complexity bounds for DNN-augmented subspace methods
- Conditions under which model-based DL provably outperforms classical methods
- Cramér-Rao bound analysis for hybrid estimators

### Gap 4: Joint Source Enumeration and DOA Estimation
While TransMUSIC and multi-task learning approaches address this, robust joint estimation under model mismatch (coherent sources, unknown noise distribution) remains challenging. The interplay between source number estimation errors and DOA accuracy in hybrid methods is underexplored.

### Gap 5: Real-World Validation at Scale
Most works validate on synthetic data or small-scale experiments. Large-scale real-world validation with true array imperfections, multipath, and dynamic environments is critically lacking. The gap between simulation performance and real deployment remains significant.

---

## 5. Summary Statistics

| Category | Papers | Key Methods |
|----------|--------|-------------|
| Surrogate Covariance Learning | 3 | SubspaceNet, NF-SubspaceNet, SE-MSDCN |
| Deep Augmented Subspace | 3 | DA-MUSIC, TransMUSIC, FTMR |
| Deep Unfolding | 4 | DeepFPC, One-Bit DOA, Unsupervised Unfolding |
| End-to-End DNN | 4 | GNN-DOA, Deep Tensor, Multi-Task CNN |
| Adaptation & Robustness | 5 | Tracking Adaptation, Domain-Adaptive, Transfer Learning |
| Other (baselines, surveys) | ~9 | Classical methods, surveys, application papers |

---

## 6. Comparison Matrix

### 6.1 Method Comparison

| Paper | Approach | Architecture | Input | Subspace Integration | Coherent | Low SNR | Quantized | Adaptation | Venue |
|-------|----------|-------------|-------|---------------------|----------|---------|-----------|------------|-------|
| SubspaceNet | Surrogate Cov | CNN-AE | Raw obs | Root-MUSIC (diff.) | ✓ | ✓ | ✗ | ✗ | IEEE TVT'25 |
| NF-SubspaceNet | Surrogate Cov | CNN-AE | Raw obs | 2D MUSIC | ✗ | ✓ | ✗ | ✗ | arXiv'25 |
| SE-MSDCN | Cov Recon | CNN+SE | Cov matrix | Peak search | ✗ | ✓ | ✗ | ✗ | EL'25 |
| DA-MUSIC | Augmented | RNN | Raw obs | MUSIC spectrum | ✓ | ✓ | ✗ | ✗ | IEEE TVT'24 |
| TransMUSIC | Augmented | Transformer | Quantized | Noise subspace | ✗ | ✗ | ✓ | ✗ | ICASSP'24 |
| FTMR+DL | Augmented | CNN+MLC | FTMR eig. | MUSIC via FTMR | ✓ | ✓ | ✗ | ✗ | IEEE TSP'22 |
| DeepFPC | Unfolding | Unrolled FPC | 1-bit meas. | Sparse recovery | ✗ | ✗ | ✓ | ✗ | SP'20 |
| One-Bit DOA | Unfolding | Deep unrolling | 1-bit meas. | Sparse recovery | ✗ | ✗ | ✓ | ✗ | arXiv'24 |
| Gridless Unsup. | Unfolding | Unsup. DL | Cov matrix | Capon penalty | ✗ | ✗ | ✗ | ✗ | DSP'23 |
| Off-Grid DOA | DL Framework | DNN | Cov matrix | Grid-free learning | ✗ | ✓ | ✗ | ✗ | SCIS'23 |
| DNN-DOA | End-to-End | DNN | Raw obs | None | ✗ | ✓ | ✗ | ✗ | Sci Rep'20 |
| GNN-DOA | End-to-End | GNN | Raw obs | None (graph) | ✗ | ✓ | ✗ | ✗ | Sensors'24 |
| Deep Tensor | End-to-End | Tensor+DL | Tensor data | Tensor decomp. | ✗ | ✗ | ✗ | ✗ | IEEE TSP'24 |
| Multi-Task | End-to-End | CNN (MTL) | Cov matrix | None | ✗ | ✗ | ✗ | ✗ | Sensors'24 |
| NN Non-Gauss. | End-to-End | NN | Cov matrix | Spatial spectrum | ✗ | ✓ | ✗ | ✗ | IEEE TAES'24 |
| MIMO DNN-DOA | End-to-End | AE+CNN+BiLSTM | Cov matrix | None | ✓ | ✓ | ✗ | ✗ | IEEE SJ'21 |
| Unsup. Adapt. | Adaptation | Any (agnostic) | KF innov. | Any subspace | ✗ | ✗ | ✗ | ✓ (unsup.) | 2025 |
| CAE-DANN | Adaptation | CAE+DANN | Cov matrix | None | ✗ | ✗ | ✗ | ✓ (semi-sup.) | Sensors'25 |
| Transfer DOA | Adaptation | Transfer DL | — | — | ✗ | ✗ | ✗ | ✓ (sup.) | arXiv'25 |
| CANN | Robustness | CNN+Attn | Cov vectors | None | ✗ | ✗ | ✗ | ✗ | SP'25 |
| RI-ResNN-DAE | Robustness | ResNet+DAE | RI features | None | ✗ | ✗ | ✗ | ✗ | EL'25 |
| DFNeT | Robustness | DFT+CNN | Cov matrix | Freq. domain | ✗ | ✓ | ✗ | ✗ | Electronics'25 |

### 6.2 Adaptation Approaches Comparison

| Paper | Adaptation Type | Labeled Data | Mechanism | Scope | Online |
|-------|----------------|-------------|-----------|-------|--------|
| Unsup. Adapt. (K888AXCC) | Unsupervised | None | KF innovation statistics | Single-type drift | ✓ |
| CAE-DANN (BUS2HBHC) | Semi-supervised | Minimal target | Domain-adversarial + MMD | Domain shift | ✗ |
| Transfer DOA (A6SI544T) | Supervised | Source + target | Transfer learning | Array imperfections | ✗ |
| CANN (SGXKVFZ9) | Robustness (no adapt.) | Training only | Robust input repr. | Array imperfections | ✗ |
| RI-ResNN-DAE (GX44S3QN) | Robustness (no adapt.) | Training only | Rotation-invariant features | Modulation changes | ✗ |
| **Proposed (Ours)** | **Unsupervised** | **None** | **Multiscale KF innovations** | **Multi-type drift** | **✓** |

### 6.3 Thematic Grouping

**Theme A: Model-Based Deep Learning for Subspace Methods**
- SubspaceNet → NF-SubspaceNet → (Proposed extension)
- DA-MUSIC → TransMUSIC
- FTMR + DL
- SE-MSDCN covariance reconstruction
- *Trend: Increasing integration of DL into classical algorithmic flow*

**Theme B: Deep Unfolding for DOA**
- Algorithm Unrolling (survey) → DeepFPC → One-Bit DOA
- Gridless unsupervised DOA with Capon penalty
- *Trend: Moving from supervised to unsupervised unfolding*

**Theme C: Architecture Innovation**
- Transformers: TransMUSIC (global attention for snapshot correlations)
- GNNs: GNN-DOA (graph structure for sparse arrays)
- Tensors: Deep Tensor 2D DOA (multi-dimensional structure)
- DFT: DFNeT (frequency-domain features)
- *Trend: Task-specific architectures exploiting signal structure*

**Theme D: Robustness and Adaptation**
- Unsupervised adaptation via tracking innovations (our foundation)
- Domain adaptation: CAE-DANN, Transfer DOA
- Noise robustness: NN Non-Gaussian, RI-ResNN-DAE
- Array robustness: CANN, SubspaceNet
- *Trend: Moving from static robustness to dynamic adaptation*

---

## 7. Paper Notes

Individual structured notes for all 26 papers are available in the `paper-notes/` directory. Each note includes: research question, core method, key findings, limitations, and relevance to our research.

---

## References

See `references.bib` for complete BibTeX entries. All citations correspond to entries in the Zotero collection `Research-SubspaceDOA-2026-02`.
