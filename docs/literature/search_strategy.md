# 检索策略（Search Strategy）：Non-Stationary DOA + Tracking + Online Adaptation

**检索截止日期**: 2026-02-19  
**建议时间范围**: 2016-01-01 至 2026-02-19（若需更“近期”，可改为 2019-01-01 起）  
**最小数据库集合**: IEEE Xplore + (Scopus 或 Web of Science) + (arXiv 或 Semantic Scholar)  

---

## 1. 概念拆解（2-4 个主概念 + 同义词）

**C1：任务与对象（DOA）**
- "direction of arrival" OR DOA OR AoA OR "angle of arrival"

**C2：方法（深度/AI/结构化学习）**
- "deep learning" OR neural OR CNN OR transformer OR "model-based deep learning" OR "deep unfolding"
- SubspaceNet

**C3：非平稳/漂移/失配**
- "distribution shift" OR drift OR "array mismatch" OR calibration OR "sensor drift" OR "geometry error"

**C4：时序与系统耦合（tracking）**
- tracking OR "Kalman filter" OR EKF OR UKF OR "state-space" OR innovation OR residual

**C5：在线/无监督适配**
- online OR "continual learning" OR adaptation OR "test-time" OR unsupervised OR self-supervised

---

## 2. 可复制检索式模板（按库微调）

### 2.1 IEEE Xplore（示例）
建议先用宽检索，再加限制（Year、Content type）。
```
("direction of arrival" OR DOA OR AoA OR "angle of arrival")
AND (("deep learning" OR neural OR SubspaceNet OR "model-based deep learning" OR unfolding))
AND (tracking OR "Kalman" OR EKF OR innovation OR residual)
AND (online OR adaptation OR unsupervised OR "test-time" OR continual)
```

### 2.2 Scopus / Web of Science（示例）
```
TITLE-ABS-KEY(("direction of arrival" OR DOA OR AoA OR "angle of arrival")
AND ("deep learning" OR neural OR SubspaceNet OR "model-based deep learning" OR unfolding)
AND (tracking OR "Kalman" OR EKF OR innovation OR residual)
AND (online OR adaptation OR unsupervised OR "test-time" OR continual))
```

### 2.3 arXiv（示例：eess.SP / cs.LG）
```
("direction of arrival" OR DOA OR AoA) AND (deep OR neural OR SubspaceNet)
AND (tracking OR Kalman OR EKF OR innovation)
AND (online OR adaptation OR unsupervised OR "test time")
```

### 2.4 Semantic Scholar（示例）
```
("direction of arrival" OR DOA OR AoA) (SubspaceNet OR "model-based deep learning" OR "deep unfolding")
(tracking OR Kalman OR EKF OR innovation) (online OR adaptation OR unsupervised OR "test-time")
```

---

## 3. 检索日志记录表（复制后逐条填写）

| Database | Date Executed | Date Range | Query | Filters | Results | Export Format | Notes |
|---|---|---|---|---|---:|---|---|
| IEEE Xplore (entry) | 2026-02-19 | 2016-01-01..2026-02-19 | Q3 (see search_run_2026-02-19.md) | domain-filtered web search | K>=1 (seed) | URL list | 无法稳定获取 total hits；记录 seed set |
| Scopus/WoS | [填] | 2016-01-01..2026-02-19 | [填] | [填] | [填] | [BibTeX/CSV] | 若无权限则跳过并注明 |
| arXiv | 2026-02-19 | 2016-01-01..2026-02-19 | Q1 (see search_run_2026-02-19.md) | domain-filtered web search | K>=8 (seed) | URL list | 后续可用 arXiv API 精确计数 |
| Semantic Scholar | 2026-02-19 | 2016-01-01..2026-02-19 | Q2 (see search_run_2026-02-19.md) | domain-filtered web search | K>=5 (seed) | URL list | 后续可用 API/手工补齐 |

---

## 4. 引用链扩展（Citation Chaining）
- Backward chaining：对 5-10 篇“种子论文”逐条阅读参考文献，补齐基础工作（MUSIC/ESPRIT、深度 DOA、SubspaceNet 相关）。
- Forward chaining：在 Scholar/Semantic Scholar/IEEE Xplore 找“被引用”论文，补齐 2023-2026 年的更新工作。

---

## 5. 可复现性提示
- 强烈建议导出 BibTeX 并统一管理（例如 `docs/ml_paper_writing/references.bib` 或本目录新增 bib 文件）。
- 记录每次检索的“执行日期”和“结果数量”，后续写方法学时可直接引用。
