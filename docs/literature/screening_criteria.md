# 纳排标准与筛选记录（Screening Criteria）

**检索截止日期**: 2026-02-19  

---

## 1. 纳入标准（Inclusion）
- I1：研究对象包含 DOA/AoA 估计（电磁或声学阵列均可），并给出明确的估计目标与评价指标。
- I2：方法属于以下至少一类：
  - 子空间/模型驱动 DOA（MUSIC/ESPRIT 等）及其鲁棒扩展；
  - 深度学习 DOA（端到端、谱图/特征学习、分类/回归）；
  - Model-based deep learning / unfolding / DNN-augmented subspace（如 SubspaceNet 路线）；
  - 在线/持续学习/测试时适配（TTA）、无监督/自监督适配；
  - DOA + KF/EKF/跟踪耦合，尤其使用 innovation/residual 做检测或学习信号。
- I3：提供可评估的实验（仿真或真实数据），并至少报告一个核心指标（如 RMSPE/RMAPE、角度误差、跟踪误差、innovation 统计等）。
- I4：全文可获取（含技术报告/预印本）。

## 2. 排除标准（Exclusion）
- E1：仅做波束形成/波束管理，不涉及 DOA/AoA 估计或未给出 DOA 评价。
- E2：仅为短摘要、海报、无全文的会议摘要。
- E3：与阵列观测模型无关（例如纯视觉/IMU 的角度估计且不与阵列 DOA 对齐）。
- E4：重复发表（保留信息更完整、版本更新的一个）。
- E5：明显不在研究范围（例如纯硬件天线设计且无算法/学习内容）。

---

## 3. 筛选流程（建议）
1. 去重：DOI 优先；缺 DOI 时用 `title + first_author + year`。
2. 标题筛选：剔除 E1/E2/E3/E5。
3. 摘要筛选：重点核对是否满足 I1/I2/I3。
4. 全文筛选：记录排除原因（E1-E5 或新增原因）。

---

## 4. PRISMA 记录（已锁定口径，投稿请只引用 4E.0）

说明：
- 本文件历史上保留过 “seed set (R01–R23)” 的占位 PRISMA 数字，但当前综述已锁定为 **4E.0** 的“正式 PRISMA（exports）+ prioritized full-text subset（Final-25）”口径。
- 为避免自相矛盾，投稿文本应仅引用 **4E.0** 与 **4A2/4A3**（Final-25 的获取与评估）对应的数字。

---

## 4A2. 全文获取进度（shortlist final-25，人工获取口径）

基于 `docs/literature/plan_fulltext_v2/shortlist_final_25.md` 与全文落盘检查清单：
- 清单：`docs/literature/plan_fulltext_v2/fulltext_screening_checklist.md`
- 汇总：`docs/literature/plan_fulltext_v2/fulltext_screening_checklist_summary.md`

当前进度（final-25）：
```
Full-text sought (shortlist final-25): n = 25
Full-text retrieved (local/OA/subscription): n = 24
Full-text not retrieved: n = 1
```

说明：
- `n=1` 当前缺失条目为 S13（`shortlist_final_25.md` 中 `Fulltext status = NEED`）。
- 已额外获得 1 篇“非 final-25 但相关”的扫描全文（`docs/literature/fulltext/subscription/IRSI2001.pdf`），用于背景补充；其 OCR 文本见 `docs/literature/plan_fulltext_v2/fulltext_txt/IRSI2001_ocr_p1-2.txt`。

## 4A3. 全文筛选结果（shortlist final-25，人工 full-text screening 口径）

基于 `docs/literature/plan_fulltext_v2/fulltext_screening_checklist.md` 的当前定稿：
```
Full-text sought (shortlist final-25): n = 25
Full-text retrieved and assessed: n = 24
Full-text not retrieved: n = 1

Studies included in synthesis (full-text assessed): n = 24
Full-text exclusions (assessed -> excluded): n = 0
```

---

## 4B. PRISMA（正式数据库口径，占位：从导出文件统计）

基于 `docs/literature/exports/` 的导出文件去重报告（`docs/literature/exports_dedup_report.md`）：
```
Records identified through database searching (exports): n = 632
Duplicates removed (exports): n = 34
Records after duplicates removed (exports): n = 598
```

说明（export 口径）：
- 当前纳入 IEEE Xplore + Scopus 导出文件：
- IEEE Xplore（CSV，查询：DOA + Kalman Filter）：
  - `docs/literature/exports/ieee_xplore_2026-02-19_05-59-34.csv`
  - `docs/literature/exports/ieee_xplore_2026-02-19_06-02-26.csv`
- Scopus（CSV，查询同主题）：
  - `docs/literature/exports/scopus_2026-02-19.csv`
- Web of Science：
  - `docs/literature/exports/wos_savedrecs_2026-02-19.xls`（记录列表，已纳入去重统计）
  - `docs/literature/exports/wos_refine_facets_2026-02-19.xlsx`（分面统计，非记录列表，自动忽略；说明见 `docs/literature/exports/README.md`）
- 该口径用于后续与 Scopus/WoS 导出合并去重，形成最终“正式 PRISMA”数字；当前不替代 seed-set 口径。

---

## 4C. 标题/摘要筛选（自动口径，占位：用于推进到 screened/full-text/included）

基于 `docs/literature/exports_dedup.json` 的自动筛选输出：
- 清单（逐条）：`docs/literature/title_abstract_screening.csv`
- 汇总（统计 + reason codes）：`docs/literature/title_abstract_screening_summary.md`

PRISMA（auto, export scope）：
```
Records screened (title/abstract): n = 598
Records excluded after title/abstract (auto): n = 272
Full-text articles assessed for eligibility (auto candidates): n = 326
Studies included in synthesis (auto, strong include only): n = 157
```

说明（自动口径）：
- `Full-text assessed (auto candidates)` 这里按“未被自动排除”的条目数计算（INCLUDE + REVIEW），用于把流程推进到 full-text 阶段；最终仍以人工复核为准。
- `Included (auto)` 仅统计强纳入（INCLUDE）；REVIEW（n=169）需要人工判定后再计入 included 或 excluded。

排除原因统计（auto, reason codes）以 `title_abstract_screening_summary.md` 为准。

---

## 4D. 标题/摘要筛选（自动口径 v2：严格匹配 DOA + Kalman 查询）

当你的数据库检索关键词为 `Direction of arrival` AND `Kalman Filter` 时，更贴近检索口径的做法是：标题/摘要阶段仅保留同时出现 DOA/AoA 与 Kalman/跟踪相关术语的条目。

输出：
- 清单（v2）：`docs/literature/title_abstract_screening_v2.csv`
- 汇总（v2）：`docs/literature/title_abstract_screening_v2_summary.md`

PRISMA（auto v2, export scope）：
```
Records screened (title/abstract): n = 598
Records excluded after title/abstract (auto v2): n = 441
Full-text articles assessed for eligibility (auto v2 candidates): n = 157
Studies included in synthesis (auto v2): n = 157
```

说明（自动口径 v2）：
- v2 会把上一版中所有 REVIEW 行（n=169）强制归类为 EXCLUDE（Kalman 但无 DOA）或 EXCLUDE（DOA 但无 Kalman），从而做到 “Needs manual review = 0”。
- 这更适合“严格围绕当前检索式写 PRISMA”，但会丢掉一些对综述写作有价值的背景文献（例如 DOA-only 或 tracking-only 的方法学论文）。

---

## 4E. PRISMA（正式口径：export 去重 -> title/abstract -> full-text -> included）

### 4E.0 本综述锁定口径（当前选择）
你已选择口径：
- **A)** “正式 PRISMA（exports=632）+ prioritized full-text subset（Final-25, included=24）”

因此本文的 PRISMA 流程在 **title/abstract** 阶段覆盖全部 export 去重集（n=598），但 **full-text assessed / included** 目前仅对优先子集（Final-25）给出可复现的人工全文筛选数字（n=24）。

说明：
- **identified / deduplicated / screened** 采用数据库导出（IEEE Xplore + Scopus + WoS）的去重结果：`docs/literature/exports_dedup.json`。
- **title/abstract excluded / included** 采用严格检索式口径（auto v2，DOA + Kalman）：`docs/literature/title_abstract_screening_v2.csv`。
- **full-text sought/assessed/included** 当前按“优先种子集（final-25）”执行真实下载与全文筛选：`docs/literature/plan_fulltext_v2/fulltext_screening_checklist.md`。

PRISMA（export scope + prioritized full-text subset）：
```
Records identified through database searching (exports): n = 632
Records after duplicates removed (exports): n = 598

Records screened (title/abstract, auto v2): n = 598
Records excluded after title/abstract (auto v2): n = 441
Records included after title/abstract (auto v2): n = 157

Reports sought for retrieval (prioritized subset = final-25): n = 25
Reports not retrieved: n = 1 (S13)
Reports assessed for eligibility: n = 24
Studies included in synthesis (full-text assessed): n = 24
```

Full-text 排除原因清单（final-25）：
- `docs/literature/fulltext_exclusion_reasons_final25.md`

---

## 5. 全文排除原因统计（final-25, current）
| Reason | Count |
|---|---:|
| E1 (no DOA evaluation) | 0 |
| E2 (no full text) | 1 |
| E3 (out of scope modality) | 0 |
| E4 (duplicate) | 0 |
| E5 (not relevant) | 0 |
| Other | 0 |
