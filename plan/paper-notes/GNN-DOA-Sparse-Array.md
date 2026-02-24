# DOA Estimation for Random Sparse Linear Array Based on Graph Neural Network

**Authors:** Yang, Yiye; Zhang, Miao; Peng, Shihua; Ye, Mingkun; Zhang, Yixiong
**Venue:** Sensors, Vol 24(1), pp 91, 2023
**Zotero Key:** 5MPWDFC3
**Category:** Applications

---

## Research Question
How can GNNs adapt to DOA estimation for non-uniform random sparse linear arrays without prior array information?

## Core Method
- GNN with neighbor node aggregation and update operations
- Adapts to non-uniform random sparse arrays without prior information
- End-to-end training reducing network complexity
- Graph structure naturally represents inter-antenna spatial relationships

## Key Findings
- Superior performance on arrays with large sparsity where classical methods fail
- Outperforms CNN and fully-connected DL models
- Excellent performance under limited snapshots, low SNR, and large array sparsity
- Low computational cost suitable for low-latency scenarios

## Limitations
- Specific to sparse linear array configurations
- Graph construction strategy may need tuning for different array types
- Primarily simulation-based validation

## Relevance to Our Research
Graph-based approach for sparse arrays — handles geometries that challenge classical subspace methods. SubspaceNet currently assumes uniform linear arrays; GNN approach could inspire extensions to non-uniform arrays.
