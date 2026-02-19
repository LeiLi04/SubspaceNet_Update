# Search Run Log (2026-02-19)

**Date executed (UTC)**: 2026-02-19  
**Executed by**: agent (web search aggregation)  
**Goal**: 为 `docs/literature/` 的综述建立“真实检索”的初始候选集合（seed set），覆盖 DOA / array mismatch / tracking innovation / online adaptation。

## Important Note (Limitations)
- 本次使用公开 Web 检索聚合（arXiv / Semantic Scholar / IEEE 入口等域名过滤）获取候选条目。
- 该方式通常不能可靠提供“数据库内部总命中数”（total hits）。因此这里记录的是“抓取到的候选条目数 K”和可追溯链接，用于后续手工或 API 精确计数时的起点。

## Queries Used

### Q1 (arXiv)
("direction of arrival" OR DOA) AND (array imperfection OR array mismatch OR calibration) AND (online OR adaptation OR unsupervised OR "test time")

### Q2 (Semantic Scholar)
direction of arrival (innovation OR residual) (Kalman OR EKF) (online OR unsupervised) adaptation

### Q3 (IEEE Xplore entry)
"direction of arrival" Kalman innovation unsupervised adaptation

## Retrieved Candidates (Expanded Seed Set, K = 20+)

1. SDOA-Net: An Efficient Deep Learning-Based DOA Estimation Network for Imperfect Array (arXiv, 2022)
   - URL: https://arxiv.org/abs/2203.10231
   - Why relevant: imperfect array 条件下深度 DOA；与“阵列失配鲁棒性/泛化”主题相关。

2. A Deep Learning-Based Supervised Transfer Learning Framework for DOA Estimation with Array Imperfections (arXiv, 2025)
   - URL: https://arxiv.org/abs/2504.13394
   - Why relevant: imperfections 下的 supervised transfer，适合作为“无标签在线适配”的对照路线。

3. Learning-based robust direction-of-arrival estimation with array imperfections (Signal Processing, 2025)
   - URL: https://www.sciencedirect.com/science/article/pii/S0165168425001148
   - Why relevant: array imperfection 鲁棒 DOA（期刊来源，适合作为主题 A/B 的近期代表）。

4. A novel calibration algorithm for MUSIC DOA estimation under sensor position error (Scientific Reports, 2025)
   - URL: https://www.nature.com/articles/s41598-025-06393-0
   - Why relevant: 经典 MUSIC 在位置误差下的校正（主题 A：经典方法与失配鲁棒）。
   - Note: 当前自动抓取无法打开该页面获取摘要/作者信息，已作为“待核验”候选保留。

5. SubspaceNet: Deep Learning-Aided Subspace Methods for DoA Estimation (arXiv, 2023)
   - URL: https://arxiv.org/abs/2306.02271

6. Deep Learning-Aided Subspace-Based DOA Recovery for Sparse Arrays (Sparse-SubspaceNet) (arXiv, 2023)
   - URL: https://arxiv.org/abs/2309.05109

7. DA-MUSIC: Data-Driven DoA Estimation via Deep Augmented MUSIC Algorithm (arXiv, 2021)
   - URL: https://arxiv.org/abs/2109.10581

8. Deep Networks for Direction-of-Arrival Estimation in Low SNR (arXiv, 2020)
   - URL: https://arxiv.org/abs/2011.08848

9. TransMUSIC (arXiv, 2023; ICASSP 2024)
   - URL: https://arxiv.org/abs/2309.08174

10. DeepMUSIC (IEEE Sensors Letters, 2020)
   - DOI: 10.1109/LSENS.2020.2980384

11. Robust and sparse M-estimation of DOA (Signal Processing, 2024)
   - DOI: 10.1016/j.sigpro.2024.109461

12. Array self-calibration with large sensor position errors (Signal Processing, 2001)
   - DOI: 10.1016/S0165-1684(01)00121-9

13. Covariance sparsity-aware DOA estimation for nonuniform noise (Digital Signal Processing, 2014)
   - DOI: 10.1016/j.dsp.2014.02.013

14. Grid-less DOA estimation of coherent sources based on the covariance matrix recovery (Physical Communication, 2021)
   - DOI: 10.1016/j.phycom.2021.101345

15. A Sparse Bayesian Learning-Based DOA Estimation Method With the Kalman Filter in MIMO Radar (Electronics, 2020)
   - DOI: 10.3390/electronics9020347

16. Interpretable and Efficient Beamforming-Based Deep Learning for Single Snapshot DOA Estimation (arXiv, 2023)
   - URL: https://arxiv.org/abs/2309.07411

17. Gridless Parameter Estimation in Partly Calibrated Rectangular Arrays (arXiv, 2024)
   - URL: https://arxiv.org/abs/2406.16041

18. Joint Frequency-Space Sparse Reconstruction for DOA Estimation under Coherent Sources and Amplitude-Phase Errors (arXiv, 2025)
   - URL: https://arxiv.org/abs/2509.03983

19. HYPERDOA: Robust and Efficient DoA Estimation using Hyperdimensional Computing (arXiv, 2025)
   - URL: https://arxiv.org/abs/2510.10718

20. A Novel DOA Estimation Algorithm Using Array Rotation Technique (Future Internet, 2014)
   - DOI: 10.3390/fi6010155

## Next Actions
- 将本次 seed set 与本地 `docs/reference_original/` 的论文合并，填入 `docs/literature/data_extraction_template.md`。
- 对每个 candidate 做快速筛选（标题/摘要），并补齐 “venue / shift type / trigger / loss / downstream tracking” 等字段。
