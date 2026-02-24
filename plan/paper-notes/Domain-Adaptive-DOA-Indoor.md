# Domain-Adaptive DOA Estimation in Complex Indoor Environments

**Authors:** Shen, Lingyu; Li, Jianfeng; Pan, Jingjing; Shi, Junpeng; Xu, Rui; Wang, Hao; Deng, Weiming
**Venue:** Sensors, Vol 25(10), pp 2959, 2025
**Zotero Key:** BUS2HBHC
**Category:** To-Read

---

## Research Question
How can domain adaptation enable DOA estimation across different indoor environments with minimal labeled data?

## Core Method
- Convolutional Autoencoder (CAE) for deep feature extraction
- Domain-Adversarial Neural Network (DANN) for domain adaptation
- Gradient Reversal Layer (GRL) counters domain shifts
- Maximum Mean Discrepancy (MMD) loss refines feature alignment
- Minimal labeled data from target domain + labeled source data
- CAE-DANN enables transfer between domains with similar features

## Key Findings
- Outperforms other methods in complex indoor environments (multipath, noise)
- Effectively reduces distributional differences between source and target domains
- Requires minimal labeled data from target domain
- Robust for high-precision DOA in new environments

## Limitations
- Requires some labeled target-domain data (not fully unsupervised)
- Specific to indoor environments with multipath
- DANN may not handle extreme domain gaps
- Published in mid-tier venue

## Relevance to Our Research
Directly related to our adaptation research — different approach from our proposed method. This uses DANN (domain-adversarial) with some labeled target data; our approach uses tracking innovations for fully unsupervised adaptation. Comparison point for supervised vs. unsupervised domain adaptation for DOA.
