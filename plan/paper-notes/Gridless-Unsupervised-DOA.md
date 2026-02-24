# A Gridless DOA Estimation Algorithm Based on Unsupervised Deep Learning

**Authors:** Chen, Tao; Shen, Mengyu; Guo, Limin; Hu, Xuejing
**Venue:** Digital Signal Processing, Vol 133, pp 103823, 2023
**Zotero Key:** SW58H7E5
**Category:** Methods

---

## Research Question
How can unsupervised deep learning achieve gridless DOA estimation without requiring labeled training data?

## Core Method
- Unsupervised deep learning for DOA estimation
- Eliminates the need for labeled training data (ground-truth DOAs)
- Gridless formulation avoids discretization artifacts
- Self-supervised loss function derived from signal model properties

## Key Findings
- Unsupervised training achieves competitive performance with supervised methods
- Gridless output avoids quantization errors inherent in classification-based approaches
- Reduces dependence on expensive labeled training data

## Limitations
- Unsupervised performance gap vs. supervised methods in some scenarios
- Self-supervised loss may not capture all signal characteristics
- Limited validation scope

## Relevance to Our Research
Directly related to our research direction of reducing label dependence. Our proposed unsupervised adaptation (via tracking innovations) shares the goal of label-free learning. Different mechanism: this uses self-supervised loss from signal model, we use downstream tracking innovations.
