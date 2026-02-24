# Enhancing Direction-of-Arrival Estimation with Multi-Task Learning

**Authors:** Kim, Chang-Jae; Jo, Hong-Ik
**Venue:** Sensors, Vol 24(22), 2024
**Zotero Key:** XGQUX4R8
**Category:** Baselines

---

## Research Question
How can multi-task learning simultaneously estimate both the number of sources and their DOAs?

## Core Method
- Multi-task CNN with shared feature extraction backbone
- Joint optimization of source enumeration (classification) and DOA estimation (regression)
- Shared representation learning benefits both tasks

## Key Findings
- Joint estimation improves both source counting and DOA accuracy
- Multi-task learning provides implicit regularization
- Demonstrates the benefit of treating source number and DOA as related tasks

## Limitations
- CNN architecture may miss global correlations (vs. Transformer)
- Published in Sensors (mid-tier venue)
- Joint estimation complexity may increase with source number

## Relevance to Our Research
Addresses Gap 4 (Joint Source Enumeration and DOA) in our literature review. SubspaceNet currently assumes known source number — multi-task learning could extend it to joint estimation.
