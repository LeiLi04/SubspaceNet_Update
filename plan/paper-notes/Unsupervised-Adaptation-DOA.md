# Unsupervised Adaptation of AI DOA Estimators via Downstream Tracking

**Authors:** Konstantino, Shaul; Li, Lei; Shlezinger, Nir; Dardari, Davide
**Venue:** Journal article (2025)
**Zotero Key:** K888AXCC
**Category:** Baselines (User's Own Paper)

---

## Research Question
How can AI-based DOA estimators be adapted online without labeled data when distribution shifts occur during deployment?

## Core Method
- Holistic system-level perspective: DOA estimators are followed by downstream tracking (Kalman filtering)
- Exploits innovation statistics from tracking algorithms as unsupervised performance measures
- Innovation variance serves as drift detector
- Mean-squared innovation error serves as unsupervised loss for adaptation
- Dedicated learning algorithm for continual unsupervised adaptation
- No ground-truth DOA labels needed during deployment

## Key Findings
- Kalman filter innovations provide effective unsupervised signal for DOA estimator adaptation
- Enables reliable AI-aided DOA estimation in time-varying environments
- Framework is estimator-agnostic — works with any differentiable DOA estimator
- Addresses the critical deployment gap: AI models degrade under distribution shift

## Limitations
- Requires a downstream tracking module (Kalman filter) to be present
- Addresses single-type distribution shifts; multiscale adaptation not explored
- Assumes the tracking model is well-specified
- Adaptation speed limited by innovation statistics convergence

## Relevance to Our Research
**USER'S OWN PAPER** — the adaptation framework this research builds upon. Our research proposal extends this to multiscale adaptation (simultaneously handling drifts in array calibration, propagation environment, and source statistics at fast/medium/slow timescales). The innovation-based unsupervised loss is the foundation of our proposed hierarchical adaptation architecture.

## Key Equations/Concepts
- Innovation: ν_k = z_k - H_k x̂_{k|k-1} (measurement minus prediction)
- Unsupervised loss: L = E[||ν_k||²] (mean-squared innovation error)
- Drift detection: monitoring innovation variance against theoretical baseline
