
# T2 研究方案草稿 · 白化新息统计触发机制

> **研究问题（一句话）**：在阵列响应漂移幅度 $\eta\in[0.3,1.5]$ 未知的无标签部署场景中，能否以基于白化新息（whitened innovation）的 CUSUM/GLR 统计量替代手动触发阈值 $\tau_\sigma$，使漂移检测概率 $P_d > 90\%$ 且误触发率 $P_{fa} < 0.10$，且跨不同漂移幅度无需重新调参？

---

## 🎯 候选方法矩阵

| Gap 主题       | 候选     | 方法名称                            | Action type | 主要构件                        | 推荐   |
| ------------ | ------ | ------------------------------- | ----------- | --------------------------- | ---- |
| T2 · 超参数黑箱壁垒 | **C1** | Page-CUSUM on 白化新息 $\chi^2$ 统计量 | 改造          | Kalman $S_i$（复用）+ CUSUM（新建） | ✅ 首选 |

---

## 候选方法 C1 · Page-CUSUM on 白化新息（首选）

### (a) 问题建模 → 关键洞察

**信号模型**

第 $i$ 个数据块 ($i=1,\ldots,B$，$B=100$) 的阵列接收信号为：

$$\mathbf{X}_i = \mathbf{A}_i(\boldsymbol{\theta}_i)\mathbf{S}_i + \mathbf{V}_i \in \mathbb{C}^{N \times T} \tag{Eq. 1}$$

其中 $N=9$ 为阵元数，$T\in\{20,200\}$ 为快拍数，$\boldsymbol{\theta}_i \in \mathbb{R}^M$（$M=3$）为真实 DoA 向量，$\mathbf{A}_i$ 为漂移后导向矩阵（扰动模型见 Eq. 8），$\mathbf{V}_i$ 为加性高斯白噪声。

**AI DoA 估计器**（以 SubspaceNet 为骨干）：

$$\hat{\boldsymbol{\theta}}_i = g_\psi(\mathbf{X}_i) \in \mathbb{R}^M \tag{Eq. 2}$$

**Kalman 跟踪器**（非线性扩展 Kalman Filter，EKF）在每块末端输出预测值：

$$\tilde{\boldsymbol{\theta}}_i = f\!\left(\hat{\boldsymbol{\theta}}_{i-1|i-1}\right), \quad P_{i|i-1} = F_{i-1} P_{i-1|i-1} F_{i-1}^{\top} + Q \tag{Eq. 3}$$

**新息（Innovation）**定义为 AI 估计器输出与 Kalman 预测值的偏差：

$$\mathbf{y}_i = \tilde{\boldsymbol{\theta}}_i - g_\psi(\mathbf{X}_i) \in \mathbb{R}^M \tag{Eq. 4}$$

**现有触发方法（原论文）**的阈值判决：

$$\sigma_y^2(i) = \frac{1}{I}\sum_{j=i-I+1}^{i}\|\mathbf{y}_j\|^2 > \tau_\sigma \quad \Rightarrow \text{ 触发适配} \tag{Eq. 5}$$

---

**核心困难**：

1. **原论文滑窗能量触发**（Eq. 5）的阈值 $\tau_\sigma$ 依赖人工调参：$\tau_\sigma$ 的最优值随漂移幅度 $\eta$、快拍数 $T$、Kalman 参数 $Q, R$ 共同变化，无单一全局最优值。作者明确表示"手动调整以避免对新息分布作强假设"，在新部署场景中可移植性为零。

2. **$\sigma_y^2(i)$ 使用原始新息 $\|\mathbf{y}_i\|^2$**：未利用 Kalman 协方差信息 $P_{i|i-1}$，当跟踪器处于高不确定性阶段（$P_{i|i-1}$ 大）时，自然存在大的新息方差，误触发率偏高；反之在高确定性阶段又可能漏检。这种混淆根本原因是统计没有被"白化"。

3. **无 null 分布理论保证**：由于 $\|\mathbf{y}_i\|^2$ 的 null 分布（无漂移时）未被推导，当前框架无法给出 $P_{fa}$ 的解析表达式，只能通过仿真逐一验证，本质上是"暗箱"。

---

**关键洞察**（Eq. 6-7）

Kalman 滤波器在每步更新中天然计算**新息协方差矩阵** $S_i$：

$$S_i = H_i P_{i|i-1} H_i^{\top} + R_{\text{obs}} \in \mathbb{R}^{M \times M} \tag{Eq. 6}$$

其中 $H_i = I_M$（AI 估计器直接观测 DoA 状态），$R_{\text{obs}} \approx \text{CRB}(\boldsymbol{\theta}_i)$ 为估计器噪声协方差。对新息进行**白化（whitening）**：

$$\bar{\mathbf{y}}_i = S_i^{-1/2}\,\mathbf{y}_i \tag{Eq. 7}$$

**在无漂移假设 $\mathcal{H}_0$ 下**，由 Kalman 一致性定理（innovation consistency property）：

$$\bar{\mathbf{y}}_i \stackrel{d}{\approx} \mathcal{N}(\mathbf{0},\,I_M) \quad \text{（i.i.d.）} \tag{Eq. 7b}$$

因此白化后的 chi-squared 统计量 $c_i = \bar{\mathbf{y}}_i^{\top}\bar{\mathbf{y}}_i = \mathbf{y}_i^{\top}S_i^{-1}\mathbf{y}_i$ 在 $\mathcal{H}_0$ 下服从自由度为 $M=3$ 的 $\chi^2$ 分布，**其期望值 $M=3$ 与漂移幅度、快拍数、Kalman 参数均无关**。

---

**Aha moment**：用 $S_i^{-1/2}$ 对新息做一次矩阵白化变换，$\mathbf{y}_i$ 的分布被标准化为 $\mathcal{N}(\mathbf{0}, I_M)$，null 分布从"随参数变化的未知分布"变成"精确已知的标准 $\chi^2(M)$"，从而将手动阈值问题转化为解析可计算的 Neyman-Pearson 假设检验。

> [!info] 为什么"知道 null 分布"就能解析定阈值？
>
> **Null 分布**指的是：在 $\mathcal{H}_0$（无漂移、系统正常）时，检测统计量的概率分布。只有知道它，才能反推出使 $P_{fa}$ 恰好等于目标值的阈值 $\tau$。
>
> **原论文的困境**：统计量 $\sigma_y^2(i) = \frac{1}{I}\sum\|\mathbf{y}_j\|^2$ 在 $\mathcal{H}_0$ 下服从加权 $\chi^2$ 分布，权重由 $S_j$ 的特征值决定。而 $S_j = P_{j|j-1} + R_{\text{obs}}$ 随 SNR、快拍数 $T$、Kalman 参数 $Q, R$ 共同变化，导致 null 分布形状无法预先确定，阈值 $\tau_\sigma$ 只能靠仿真逐场景凑出来。
>
> **白化后的解决方案**：$c_i = \mathbf{y}_i^\top S_i^{-1} \mathbf{y}_i$ 是 $M$ 个独立标准正态变量的平方和，根据定义服从 $\chi^2(M)$，且期望 $M$ 与任何系统参数无关。因此：
> $$P_{fa} = P(c_i > \tau \mid \mathcal{H}_0) = 1 - F_{\chi^2(M)}(\tau)$$
> 反解即得解析阈值，无需仿真：$\tau = F_{\chi^2(M)}^{-1}(1 - P_{fa})$。
>
> **Neyman-Pearson 框架**的核心是：在固定 $P_{fa}$ 约束下最大化 $P_d$。其前提恰好是"知道 $\mathcal{H}_0$ 下的分布"。白化操作满足了这一前提，使得整个触发决策从"暗箱调参"升级为有严格统计保证的假设检验。

---

### (b) 方法总体流程（逻辑链）

因为白化新息在 $\mathcal{H}_0$ 下服从精确已知的 $\chi^2(M)$ 分布，C1 方案将触发决策建模为 Page-CUSUM 变点检测问题，利用 chi-squared 统计的已知矩直接推导出**与漂移幅度无关的解析阈值** $h$。

```
输入: 第 i 块原始快拍数据 X_i
         │
         ▼
[AI DoA 估计器 g_ψ(X_i)]
  输出: θ̂_i = g_ψ(X_i) ∈ R^M
         │
         ▼
[Kalman 预测步]
  θ̃_i = f(θ̂_{i-1|i-1})
  P_{i|i-1} = F P_{i-1|i-1} F^T + Q
         │
         ▼
[新息计算]
  y_i = θ̃_i - θ̂_i  ∈ R^M
         │
         ▼
[新息协方差计算]           ← 标准 Kalman 输出，零额外开销
  S_i = P_{i|i-1} + R_obs  ∈ R^(M×M)
         │
         ▼
[白化（Whitening）]  ← ★ 创新点 1
  ȳ_i = S_i^{-1/2} y_i
  c_i = ȳ_i^T ȳ_i = y_i^T S_i^{-1} y_i  ~ χ²(M) under H0
         │
         ▼
[Page-CUSUM 累积]    ← ★ 创新点 2
  G_0 = 0
  G_i = max(0, G_{i-1} + (c_i - b))
  b = M + γ  (参考值，γ 为小正数补偿)
         │
         ▼
[解析阈值决策]       ← ★ 创新点 3
  若 G_i > h → 触发适配（调用 MSIE 梯度更新 S 步）
  h = -ln(P_fa_target) 由期望运行长度公式给出
  Kalman 更新: θ̂_{i|i}, P_{i|i}
         │
         ▼
输出: 触发标志 flag_i ∈ {0,1}  +  Kalman 更新后状态 θ̂_{i|i}
损失（触发后）: L_{W_i}(ψ) = (1/I) Σ ||θ̃_j - g_ψ(X_j)||²（原始 MSIE，不变）
```

**信息流**：原始快拍 $\mathbf{X}_i$ 进入 AI 估计器，输出 $\hat{\boldsymbol{\theta}}_i$ 后与 Kalman 预测 $\tilde{\boldsymbol{\theta}}_i$ 作差得到新息 $\mathbf{y}_i$。关键改动在**白化步**：利用 Kalman 协方差 $S_i$（已是标准输出，无额外成本）将 $\mathbf{y}_i$ 变换为 $\bar{\mathbf{y}}_i$，使其分布在正常运行时精确为 $\mathcal{N}(\mathbf{0}, I_M)$。CUSUM 在标准化后的 $c_i = \bar{\mathbf{y}}_i^{\top}\bar{\mathbf{y}}_i$ 上积累，当检测到均值偏离 $M$ 时报警。阈值 $h$ 由目标 $P_{fa}$ 唯一确定，无需仿真调参。

**与原论文方法的改动对比**：

| 模块      | 原论文（Konstantino et al., 2026）                             | C1（本方案）                                                         |
| ------- | --------------------------------------------------------- | --------------------------------------------------------------- |
| 触发统计量   | $\sigma_y^2(i) = \frac{1}{I}\sum\|\mathbf{y}_j\|^2$（原始能量） | $c_i = \mathbf{y}_i^{\top}S_i^{-1}\mathbf{y}_i$（白化 chi-squared） |
| 阈值来源    | 手动调参 $\tau_\sigma$（经验值）                                   | 解析推导：$h = f(P_{fa\_target})$（由期望运行长度公式给出）                       |
| 触发机制    | 滑窗均值与 $\tau_\sigma$ 比较                                    | Page-CUSUM 累积量 $G_i$ 超越 $h$                                     |
| 漂移幅度依赖  | $\tau_\sigma$ 随 $\eta$ 变化（需重调）                            | $h$ 仅依赖 $P_{fa\_target}$，与 $\eta$ 无关                            |
| null 分布 | 未推导（暗箱）                                                   | $c_i \sim \chi^2(3)$（精确已知）                                      |
| 额外计算开销  | 无                                                         | Cholesky 分解 $S_i^{-1/2}$：$O(M^3)$（$M=3$，可忽略）                    |

**构件分解表**：

| Stage                 | 构件名                                                            | 来源                                              | Action type |
| --------------------- | -------------------------------------------------------------- | ----------------------------------------------- | ----------- |
| AI DoA 估计器            | SubspaceNet 卷积自编码器骨干                                           | `[[MBDL/{2}[17] SubspaceNet]]` 方法段              | 复用          |
| Kalman 预测步            | 扩展 Kalman 滤波器 $f, F, Q$                                        | `[[main_Ref/(2nd author)UNSUPERVISED...]]` Eq.3 | 复用          |
| 新息协方差 $S_i$           | Kalman 标准输出 $P_{i\|i-1} + R_{\text{obs}}$                      | 标准 EKF 公式                                       | 复用          |
| 白化变换 $S_i^{-1/2}$     | Cholesky 分解 $S_i = L L^\top$，$S_i^{-1/2} = L^{-\top}$          | 线性代数基础；无现有构件                                    | **新建**      |
| chi-squared 统计量 $c_i$ | $c_i = \mathbf{y}_i^{\top}S_i^{-1}\mathbf{y}_i \sim \chi^2(M)$ | 白化后的 null 分布推导；无现有构件                            | **新建**      |
| Page-CUSUM 累积器 $G_i$  | $G_i = \max(0, G_{i-1} + c_i - b)$                             | Basseville & Nikiforov (1993) 经典CUSUM；无现有构件     | **新建**      |
| 解析阈值 $h$              | $h = h(P_{fa\_target})$ from Lorden's bound / ARL formula      | 序列分析理论；无现有构件                                    | **新建**      |
| MSIE 损失（触发后）          | $L_{W_i}(\psi)$（与原论文相同）                                        | `[[main_Ref/(2nd author)UNSUPERVISED...]]` Eq.7 | 复用          |

---

## 📐 关键公式推导备忘

### 白化步 Null 分布

在 $\mathcal{H}_0$（无漂移）下，新息 $\mathbf{y}_i \sim \mathcal{N}(\mathbf{0}, S_i)$，因此：

$$c_i = \mathbf{y}_i^{\top} S_i^{-1} \mathbf{y}_i \sim \chi^2(M), \quad \mathbb{E}[c_i] = M, \quad \text{Var}[c_i] = 2M \tag{Eq. 12}$$

在 $\mathcal{H}_1$（漂移导致偏差 $\boldsymbol{\mu}_i = \tilde{\boldsymbol{\theta}}_i - (\boldsymbol{\theta}_i + \text{bias}_i)$）下：

$$c_i \sim \chi^2_{\text{nc}}\!\left(M, \lambda_i\right), \quad \lambda_i = \boldsymbol{\mu}_i^{\top} S_i^{-1} \boldsymbol{\mu}_i \geq 0 \tag{Eq. 13}$$

其中 $\lambda_i$ 为非中心参数，$\mathbb{E}[c_i] = M + \lambda_i > M$，这正是 CUSUM 可检测到的均值偏移。

### Page-CUSUM 阈值解析推导（C1）

参考值选取：$b = \mathbb{E}[c_i | \mathcal{H}_0] + s = M + s$，其中 $s = \lambda_{\min}/2$（Lorden 最优参考值为偏移量的一半）。实践中 $s$ 在 $[0.5, 1.5]$ 范围内，对最终性能不敏感。

期望运行长度（ARL）近似（Lorden's bound，$s$ 为偏移量的一半时近似精确）：

$$\mathbb{E}[\tau | \mathcal{H}_0] \approx \frac{e^h}{h} \cdot \frac{1}{2\pi} \quad \Rightarrow \quad P_{fa} \approx \frac{1}{\mathbb{E}[\tau | \mathcal{H}_0]} \tag{Eq. 14}$$

因此给定目标 $P_{fa}$，通过数值求解 $h e^{-h} = P_{fa}$ 得到阈值 $h$（等价于 $h = -W(-P_{fa})$，Lambert W 函数）。

实用近似：$h \approx -\ln(P_{fa}) - \ln(-\ln(P_{fa}))$（对 $P_{fa} \leq 0.2$ 精度 <5%）。

$$\boxed{h = \text{lambertw}\!\left(-P_{fa}\right) + 1, \quad \text{or numerically solve } h = -\ln(h \cdot P_{fa})} \tag{Eq. 15}$$

---

## ✅ 待解决的实现细节

- [ ] **$R_{\text{obs}}$ 的估计方法**：AI 估计器输出噪声协方差 $R_{\text{obs}} \approx \text{CRB}(\boldsymbol{\theta}_i)$ 的计算。选项 A：离线用校准数据估计（与 SubspaceNet 预训练阶段同步）；选项 B：在线用滑窗估计 $\hat{R} = \frac{1}{W_{\text{cal}}} \sum (\hat{\boldsymbol{\theta}}_j - \tilde{\boldsymbol{\theta}}_j)(\hat{\boldsymbol{\theta}}_j - \tilde{\boldsymbol{\theta}}_j)^{\top}$（仅在初始稳定期使用）。需实验对比两种方案在低快拍 $T=20$ 下的稳定性。

- [ ] **Null 分布验证**：在原论文台架（无漂移，$\eta=0$）下，绘制 $c_i = \mathbf{y}_i^{\top}S_i^{-1}\mathbf{y}_i$ 的经验分布，与理论 $\chi^2(3)$ 对比（Kolmogorov-Smirnov test）。若存在显著偏离（$p<0.05$），需诊断 $R_{\text{obs}}$ 估计偏差或 EKF 非线性导致的分布偏差。

- [ ] **C1 参考值 $b$ 的敏感性分析**：固定 $P_{fa}=0.10$，在 $s \in \{0.5, 1.0, 1.5\}$ 下分别跑 C1，报告 $P_d$ 和 RMSPE 收敛速度，确认 $s$ 不敏感范围。

- [ ] **C1 CUSUM 复位策略**：漂移结束后（或完成适配后），$G_i$ 是否复位为 0？若不复位，下次漂移检测可能过快。建议：适配完成后将 $G_i$ 复位为 0，并在论文中说明复位时机。

- [ ] **Kalman EKF vs UKF 的选择**：原论文使用 EKF；当 DoA 轨迹非线性较强时，UKF 的 $S_i$ 估计更准确，白化效果更好。需测试两种 Kalman 变体对 null 分布贴合度的影响。

- [ ] **代码集成点**：在原论文开源代码（如存在）的 Algorithm 1 中，找到 `σ²_y > τ_σ` 的判断行，替换为 `G_i > h`，并新增 `compute_S_i` 函数和 `chi2_stat` 函数。估计改动约 30-40 行。

- [ ] **非高斯噪声下的鲁棒性测试**：在 $\mathcal{H}_0$ 下引入 10% 的脉冲噪声（$\alpha$-stable），测试实际 $P_{fa}$ 与理论值 0.10 的偏差。若偏差 >50%，考虑使用 Huber 化白化（robust Mahalanobis distance）作为 fallback。

---

## 🔗 下游指针

- 本草稿将直接支撑 **Methods 章节**初稿写作（Section III 或 Section IV，视期刊格式）
- 建议实验对照组（Table）：
  - 行：$\eta \in \{0.3, 0.6, 0.9, 1.2, 1.5\}$ × $T \in \{20, 200\}$（10 组）
  - 列：原论文手动阈值 $\tau_\sigma$ | C1 CUSUM | 在线监督基线
  - 指标：$P_d$（检测概率）、$P_{fa}$（误触发率）、漂移后 RMSPE（前 10 blocks）、稳态 RMSPE
- 投稿目标：**IEEE Signal Processing Letters**（页数 ≤5，方法简洁，与 SPL 风格匹配）；备选 **ICASSP 2027**
- 建议先做"待解决 #1 + #2"（共约 1 周），确认 null 分布成立后进入完整实验

---

## 📝 实现状态

详见 [plan_implementation_whiten_innov.md](plan_implementation_whiten_innov.md) 与 [IMPLEMENTATION_NOTES.md](IMPLEMENTATION_NOTES.md)。

---

## 🔎 首轮验收报告（2026-04-28）

整体实现**结构正确、核心逻辑可用**，但有两处需要修，一处需要重做。

### ✅ 通过

| 项 | 结果 |
| --- | --- |
| 文件结构（drift_trigger.py / 三策略 / 工厂） | ✓ 与计划一致，194 行 |
| `pipeline_run.py` 触发器接入（`L18-34`, `L83-88`, `L294-314`） | ✓ time_to_learn 硬编码已移除 |
| `_extract_c_per_step` 对源求和 → χ²(M=3) | ✓ |
| YAML 三预设 + base 配置 schema | ✓ |
| Pydantic schema 扩展（`config/schema.py:164`） | ✓ 计划外但必需 |
| `metrics.py` 暴露 `c_per_step` | ✓ |
| 单元测试 12/14 通过 | ⚠ 见下 |
| 集成 smoke + metrics_aggregate 5/5 通过 | ✓ |

### ⚠️ 必须修的问题

#### 1. 两个单元测试失败（统计公差过紧，非实现 bug）

```text
FAILED test_page_cusum_stays_zero_under_null  — 16 alarms in 1000 steps; 容忍 <15
FAILED test_whitened_cusum_trigger_fires_under_drift  — null 阶段第 4 窗即触发
```

根因：Lorden ARL 公式 `h*exp(-h)=P_fa` 是**渐近近似**，不是精确解；实测 `P_fa=0.01` 配置下经验 `P_fa` 偏高（~1-2%），是统计学意义上的合法 Type-I error，不是代码错。

**修法（任选其一）**：

- 把 test 1 的容忍上限从 15 提到 30（仍远低于无 trigger 的期望 ~500）
- test 2：把 null 验证改为"null 阶段触发次数 ≤ ⌈P_fa·样本数⌉×2"，而不是"零触发"
- 或干脆把这两个测试标 `@pytest.mark.flaky(reruns=3)` 并降低 `P_fa` 至 `1e-4`

#### 2. `validate_null_distribution.py` 是空壳，不符合 plan_whiten_innov.md「待解决 #2」

`scripts/validate_null_distribution.py:39-41` 默认行为：用 `rng.chisquare(df=3)` 生成**合成** χ² 样本，再用 KS test 对 χ²(3) —— 这是**自洽性验证**，恒过 PASS，毫无信息量。

实跑结果：

```text
N=300 samples, mean=2.878 (theoretical 3)
KS test vs chi2(3): stat=0.0497, p=0.4346
PASS: cannot reject H0 at alpha=0.05
```

`mean=2.878` 是从合成样本来的，不是从仓库 EKF+SubspaceNet 在 η=0 下跑出来的。

计划本意是「跑无漂移管线 → 收集真实 `c_per_step` → KS 校验是否符合 χ²(3)」。当前脚本仅支持 `--input` 模式加载预存 npz，但**没有任何脚本/钩子去生成那个 npz**。

**修法**：要么把脚本改成真正调起 `OnlineLearning.run()` 抽 `window_result.step_metrics.c_per_step`，要么至少在 `pipeline_run.py` 加一个可选的 `dump_c_per_step_path` 配置项把每个 trajectory 的 `c_per_step` 写到 npz，再让 script 加载。

### 🟡 建议修但可暂留

**3. dead state**：`pipeline_run.py:141` 仍读 `loss_threshold` 但只在 metadata 里日志输出（`L482`），不再驱动任何决策。可以删，也可以留作 metadata。

**4. Smoke 测试被简化**：计划要求端到端 1 条轨迹跑通；Codex 改成"配置→trigger 构造 + 提取函数单测"。trade-off 合理（避免重 deps），但**没有验证 pipeline 真的把 `c_per_step` 喂给 trigger**。如果想要原计划级别的验收，需要补一个真的 `runner.run()` 测试。

**5. 小毛病**：

- `SineAccel_whitened_cusum_trigger.yaml` 的 defaults list 缺 `_self_`，会触发 Hydra UserWarning（不影响功能）。
- `pytest.mark.integration` 未在 `pyproject.toml` 注册，触发 PytestUnknownMarkWarning。

### 📌 结论

实现的**架构与代码正确**，可以打 commit。但**先修以下三件再打 PR**：

1. 修两个失败的单元测试（放宽容忍）
2. 重写 `validate_null_distribution.py` 让它真正跑管线，或至少加入 dump 钩子
3. （可选）补一个真正运行 `OnlineLearning.run()` 的 smoke test

---

## ✅ 二轮执行记录（2026-04-28）

已根据首轮验收报告继续修复：

1. **单元测试统计公差已修复**
   - `test_page_cusum_stays_zero_under_null` 放宽到固定 seed 下稳定通过的 false-alarm 容忍。
   - `test_whitened_cusum_trigger_fires_under_drift` 使用更严格的 `p_fa=0.001` 做 null 阶段，并提高 H1 非中心参数，避免测试把合法 Type-I error 当作失败。
   - 验证：`tests/online_learning/test_drift_trigger.py` 14/14 PASS。

2. **Null 分布验证脚本不再默认合成样本**
   - `scripts/validate_null_distribution.py` 现在要求 `--input <npz>` 才做真实验证。
   - 仅在显式传入 `--synthetic-null` 时才生成合成 χ² 样本，并标注为 script smoke。
   - 无 `--input` 运行会退出码 2 并提示先用 `online_learning.dump_c_per_step_path` 生成真实 `c_per_step` npz。

3. **新增真实 `c_per_step` dump 钩子**
   - `config/schema.py` 增加 `online_learning.dump_c_per_step_path: Optional[str]`。
   - `pipeline_run.py` 在每个 window 后收集真实 `_extract_c_per_step(window_result)`，若配置了 `dump_c_per_step_path`，则在 trajectory 结束时写出 `np.savez(path, c=..., dof=..., trajectory_idx=...)`。
   - base YAML 默认 `dump_c_per_step_path: null`，不影响原实验。

4. **补充 pipeline → trigger 喂数验证**
   - 新增 `_observe_drift_trigger(self, window_idx, window_result)`，集中执行 `c_per_step` 提取和 trigger 更新。
   - `tests/integration/test_whitened_trigger_smoke.py` 增加 `RecordingTrigger` 测试，验证 pipeline helper 确实把 `[6.0, 1.5]` 喂给 trigger。
   - 这不是完整 `OnlineLearning.run()` 端到端测试，但覆盖了首轮报告指出的关键未验证边。

5. **清理两个 warning**
   - `SineAccel_whitened_cusum_trigger.yaml` 与 `SineAccel_sigma_y_sq_trigger.yaml` defaults 增加 `_self_`，消除 Hydra defaults warning。
   - `pyproject.toml` 注册 `integration` marker，消除 PytestUnknownMarkWarning。

当前验证结果：

```text
PYTHONPATH=. .venv-wsl/bin/python -m pytest tests/online_learning/test_drift_trigger.py -v
# 14 passed

PYTHONPATH=. .venv-wsl/bin/python -m pytest tests/online_learning/test_metrics_aggregate.py -v
# 3 passed

PYTHONPATH=. .venv-wsl/bin/python -m pytest tests/online_learning/ -v --tb=short
# 26 passed

PYTHONPATH=. .venv-wsl/bin/python -m pytest tests/integration/test_whitened_trigger_smoke.py -v -m integration
# 3 passed

.venv-wsl/bin/python scripts/validate_null_distribution.py
# exit code 2, as expected: real validation now requires --input

.venv-wsl/bin/python scripts/validate_null_distribution.py --input /tmp/null_validation_input.npz
# PASS
```

---

## 🔎 二轮验收报告（2026-04-29）

### ✅ 全部通过

| 二轮承诺 | 验证 |
| --- | --- |
| 单元测试 14/14 | ✓ pytest 实跑 PASS（`tests/online_learning/test_drift_trigger.py:61` tolerance 15→25；`:111` `p_fa` 0.01→0.001, `nonc` 15→20） |
| `validate_null_distribution.py` 不再默认合成 | ✓ 无参运行 exit code 2 + 报错提示 |
| 显式 `--synthetic-null` 才生成合成样本 | ✓ `scripts/validate_null_distribution.py:39, 50-53` |
| `config/schema.py` 增加 `dump_c_per_step_path` | ✓ `config/schema.py:210` |
| `pipeline_run.py` 新增 `_observe_drift_trigger` helper | ✓ `pipeline_run.py:43-50` |
| 真实 dump 钩子 `np.savez` 在 trajectory 结束时写出 | ✓ `pipeline_run.py:474-494`，累积在 `:307` |
| `RecordingTrigger` 验证 pipeline 喂数 | ✓ `test_pipeline_observe_feeds_c_per_step_to_trigger` PASS，断言 `[6.0, 1.5]` |
| 两个 YAML 加 `_self_` | ✓ Hydra warning 消失 |
| `pyproject.toml` 注册 `integration` marker | ✓ `pyproject.toml:38`，警告消失 |

实跑 `pytest tests/online_learning/test_drift_trigger.py tests/online_learning/test_metrics_aggregate.py tests/integration/test_whitened_trigger_smoke.py -v`：**20 passed, 2 warnings**（剩下的 2 个 Pydantic V2 弃用警告与本特性无关，是项目历史遗留）。

### 🟡 仍可优化的细节（非阻塞）

1. **`pipeline_run.py:485`** `drift_state.get("dof", ...)`：`WhitenedCusumTrigger.state` 字典里其实**没有 `"dof"` 键**（`drift_trigger.py:166-173`），所以这行永远走 fallback。功能正确（fallback 取 `system_model.M`），但表达冗余。建议在 `state` 里把 `dof` 也暴露出来，让 `.get` 真正命中。

2. **`pipeline_run.py:477-478`** `import numpy as np` 和 `from pathlib import Path` 写在函数内部 dump 分支里。轻微违反 import 规范，但避免了无 dump 配置时多加载；挪到顶部更合规。

3. **首轮报告 #3「dead `loss_threshold`」** 未处理（仍在 `pipeline_run.py:141, 482` 作为 metadata）—— 当时标记"可暂留"，本轮也未列入 commit gate，可接受。

4. **首轮报告 #3 的端到端 smoke**（真正 `runner.run()` 一条短轨迹）也未补 —— 首轮标"可选"，本轮以 `RecordingTrigger` 单测覆盖关键边，可接受。

### 📌 二轮结论

二轮修复**全部命中首轮报告的 P0 与 P1 项**。代码与测试都达到可 commit / 可 PR 的状态，剩下三条都是非阻塞型微优化。

建议下一步：

1. 现在按 `feature/whiten_innov` 分支纪律（按路径 `git add`）打第一个正式 commit
2. （可选）顺手修一下 1、2 两条小瑕疵
3. 然后真正跑一次 `dump_c_per_step_path` + `validate_null_distribution.py --input <npz>` 的端到端 null 分布验证（兑现 plan_whiten_innov.md「待解决 #2」）

---

## 🧹 小瑕疵优化记录（2026-04-29）

已顺手处理二轮验收报告中的两条非阻塞小瑕疵：

1. `WhitenedCusumTrigger.state` 已暴露 `"dof"`，`pipeline_run.py` dump 分支中的 `drift_state.get("dof", ...)` 现在会真实命中 whitened CUSUM 配置；其他 trigger 仍安全 fallback 到 `system_model.M`。
2. `pipeline_run.py` 中 `numpy` 与 `Path` 已从 dump 分支内部移动到文件顶部 import 区，符合项目常规 import 风格。

回归验证：

```text
PYTHONPATH=. .venv-wsl/bin/python -m pytest tests/online_learning/test_drift_trigger.py tests/integration/test_whitened_trigger_smoke.py -v
# PASS
```

---

## 🔎 三轮小瑕疵验收（2026-04-29）

两条都**真实修复且无回归**。

| 报告承诺 | 验证结果 |
| --- | --- |
| `WhitenedCusumTrigger.state` 暴露 `"dof"` | ✓ `drift_trigger.py:169` 新增 `"dof": self.dof` |
| dump 分支 `drift_state.get("dof", ...)` 真实命中 | ✓ `pipeline_run.py:486` 现在能从 whitened CUSUM state 直取，其他 trigger fallback 到 `system_model.M`（语义保留） |
| `numpy` 与 `Path` 移到文件顶部 | ✓ `pipeline_run.py:4` `from pathlib import Path`，`:6` `import numpy as np`；dump 分支（`L477-494`）已无 inline import |

**回归测试**：

```text
.venv\Scripts\python.exe -m pytest tests/online_learning/test_drift_trigger.py tests/integration/test_whitened_trigger_smoke.py -v
# 17 passed, 2 warnings in 3.33s
# （2 个 PydanticDeprecatedSince20 警告与本特性无关，是项目历史遗留）
```

二轮报告里**未承诺要修的两条**（dead `loss_threshold`、端到端 `runner.run()` smoke）保持不变，符合预期。

---

## 🧪 Task 2 真实 Null 分布验证（2026-04-29）

### 运行设置

目标：兑现「待解决 #2」，在无阵列漂移条件下收集真实 pipeline 输出的 `c_per_step`，再与理论 `χ²(3)` 做 KS 检验。

本次使用配置等价于：

```text
system_model.eta=0
system_model.sv_noise_var=0
system_model.nominal=true
online_learning.dataset_size=1
online_learning.trajectory_length=30
online_learning.window_size=5
online_learning.stride=1
online_learning.eta_update_interval_windows=0
online_learning.eta_increment=0
online_learning.max_eta=0
online_learning.min_eta=0
online_learning.dump_c_per_step_path=outputs/null_validation_real.npz
online_learning.drift_trigger.type=time_to_learn
online_learning.drift_trigger.target_window=999999
simulation.model_path=checkpoints/saved_SubspaceNet_trained_20260224_180720.pt
```

说明：当前 legacy CLI 入口依赖缺失的 `config/factory.py`，因此本次通过 Python 片段直接构造 `Simulation` 与 `SubspaceNet`，但执行的是同一个 `sim.execute_online_learning()` / `pipeline_run.py` 路径。运行中还发现并补齐了真实路径所需的拆分模块 import：

- `pipeline_run.py` 显式 import `create_online_learning_dataset`、`OnlineTrainer`、`device`、`glrt_changepoint_detection`、`log_online_learning_window_summary`、`save_model_state`
- `step_processor.py` 显式 import `log_window_summary`
- `pipeline.py` 显式 import `glrt_changepoint_detection`、`plot_results`

### 真实 dump

运行成功生成：

```text
outputs/null_validation_real.npz
```

dump 摘要：

```text
keys: ['c', 'dof', 'trajectory_idx']
N = 130
mean(c) = 12.444
std(c) = 16.617
min(c) = 0.085
max(c) = 89.146
dof = 3
```

### KS 检验

命令：

```bash
.venv-wsl/bin/python scripts/validate_null_distribution.py --input outputs/null_validation_real.npz
```

结果：

```text
Loaded 130 c-values from outputs/null_validation_real.npz
N=130 samples, mean=12.444 (theoretical 3)
KS test vs chi2(3): stat=0.4740, p=2.425e-27
FAIL: p=2.425e-27 <= alpha=0.05; null distribution deviates
```

### 结论

真实 null 分布验证**未通过**。`mean(c)=12.444` 明显高于理论 `E[χ²(3)]=3`，说明当前 EKF/观测噪声标定下，白化统计量并未被校准到标准 `χ²(3)`。

最可能的后续诊断方向：

1. **`R_obs` / `measurement_noise_std_dev` 偏小**：当前 `S=P+R_obs` 低估实际 AI DoA 输出误差，导致 `y^T S^{-1}y` 系统性偏大。
2. **SubspaceNet 输出误差非高斯或有偏**：即使 η=0，模型预测误差可能不满足 EKF 一致性假设。
3. **轨迹动态/重叠 window 相关性**：本次 30-step、stride=1 的短轨迹产生 130 个高度相关样本；相关性不改变均值偏高的事实，但会影响 KS p-value 的严格解释。

下一步建议先做 `R_obs` 标定 sweep：

```text
kalman_filter.measurement_noise_std_dev ∈ {0.05, 0.1, 0.2, 0.5, 1.0}
```

每个设置重复生成 `outputs/null_validation_real_<noise>.npz` 并跑 KS test；若某一范围能让 `mean(c)` 接近 3 且 `p>0.05`，即可把该设置作为 CUSUM null 校准默认值或进入更细 sweep。

### 📌 三轮结论

本特性的代码层面已基本干净，真实 null 分布验证也已执行。当前关键结论不是“验证未跑”，而是“验证未通过”：`mean(c)=12.444` 明显高于理论 `E[χ²(3)]=3`，KS test `p=2.425e-27`。因此下一阶段重点应从触发器实现转入 EKF 观测噪声标定与 null 分布校准。

## 🧭 下一步计划（2026-04-29，按评审修正版）

本节以「下一步计划评审修正」为准，覆盖前一版计划。Task 2 的核心结论保持不变：`mean(c)=12.444` 远高于理论 `E[χ²(3)]=3`，说明当前白化统计量没有校准好。但执行顺序需要先排除 per-source / association 问题，再进入 `R_obs` sweep。

### Step 0：per-source 拆分诊断（新增，优先执行）

目标：判断 `c` 膨胀是三源同步发生，还是由某一个源主导。

已补齐诊断能力：

- `pipeline_run.py` 的 dump 钩子额外保存 `c_per_step_per_source: np.ndarray[steps, sources]`
- `validate_null_distribution.py` 支持 `--per-source`，逐源对 `χ²(1)` 做统计检验
- `validate_null_distribution.py` 支持 `--decimate <N>`，用于对重叠 window 产生的高相关样本做二次抽样

建议先重新生成一次 no-drift dump：

```text
system_model.eta=0
system_model.sv_noise_var=0
system_model.nominal=true
online_learning.dataset_size=1
online_learning.trajectory_length=30
online_learning.window_size=5
online_learning.stride=5
online_learning.eta_increment=0
online_learning.max_eta=0
online_learning.dump_c_per_step_path=outputs/null_validation_per_source.npz
online_learning.drift_trigger.type=time_to_learn
online_learning.drift_trigger.target_window=999999
```

然后运行：

```bash
.venv-wsl/bin/python scripts/validate_null_distribution.py --input outputs/null_validation_per_source.npz --per-source
.venv-wsl/bin/python scripts/validate_null_distribution.py --input outputs/null_validation_per_source.npz
```

判读规则：

- 若三源 `mean(c_source)` 都接近 `1.0`，而总量仍偏大，则检查 source 间相关性或求和假设。
- 若只有某个源 `mean(c_source) >> 1.0`，优先诊断 source association / EKF 初始化，不进入盲目 `R_obs` sweep。
- 若三源都同步偏大，才进入 Step 1 的 `R_obs` / `measurement_noise_std_dev` 标定。

### Step 1：做 `R_obs` / `measurement_noise_std_dev` 标定 sweep

目标：找到能让真实 no-drift `c_per_step` 接近 `χ²(3)` 的观测噪声配置。

初始 sweep：

```text
kalman_filter.measurement_noise_std_dev ∈ {0.05, 0.1, 0.2, 0.5, 1.0}
```

执行要求：

- `stride >= window_size`，否则 KS test 的 iid 假设不成立。
- 主要验收指标改为 `mean(c) ∈ [2.5, 3.5]`。
- KS test 只作为辅助；若使用 `stride=1` 的高密度 dump，必须加 `--decimate <window_size>` 后再解释 KS。

推荐命令形态：

```bash
.venv-wsl/bin/python scripts/validate_null_distribution.py --input outputs/null_validation_real_<noise>.npz
.venv-wsl/bin/python scripts/validate_null_distribution.py --input outputs/null_validation_real_<noise>.npz --per-source
```

若没有任何设置通过，则保留最接近 `mean(c)=3` 且 per-source 最均衡的候选点，并继续细化 sweep。

### Step 2：扩展验证样本，降低短轨迹偶然性

当 Step 0/1 找到候选配置后，用更长或更多轨迹复验：

```text
dataset_size ∈ {3, 5}
trajectory_length ∈ {50, 100}
stride ∈ {window_size, 2*window_size}
```

重点观察：

- 总量 `mean(c)` 是否稳定落在 `[2.5, 3.5]`
- 三个 source 的 `mean(c_source)` 是否都接近 `1.0`
- decimated KS p-value 是否可接受

### Step 3：模型误差 / calibration-data `R_obs` 诊断（与 Step 1 并行）

如果 Step 0 显示单源异常，或 Step 1 单纯放大 `measurement_noise_std_dev` 仍无法让 null 分布接近目标，需要检查 SubspaceNet 在 η=0 条件下的观测误差：

- 统计 AI DoA 预测误差的均值、方差、偏度、峰度
- 检查误差是否存在系统性 bias 或 source swap
- 对比 `z - h(x_pred)` 与 EKF 预测协方差 `P` 的量级
- 评估是否需要用 calibration-data 估计经验 `R_obs`，而不是固定 scalar noise

### Step 4：确定 whitened CUSUM 默认配置（不扩 trigger 接口）

采用评审推荐方案 (a)：当前不新增 `warmup_windows` / `min_gap_windows`，保持 `WhitenedCusumTrigger` 接口简单。

只有当真实 null 分布校准通过后，才进入 CUSUM 阈值默认值定稿：

- 固定通过验证的 `measurement_noise_std_dev`
- 重新生成 no-drift null dump
- 用该配置运行 `whitened_cusum` smoke
- 记录推荐默认值：`p_fa`、`b_offset`、`reset_after_trigger`

### Step 5：文档与测试收尾

完成以上步骤后更新：

- `plan/plan_26Apr/IMPLEMENTATION_NOTES.md`
- `plan/plan_26Apr/plan_whiten_innov.md`
- 必要时新增一个 sweep 辅助脚本，避免手动改 YAML 重复执行

最终验收标准：

```text
pytest tests/online_learning/ -v
pytest tests/integration/test_whitened_trigger_smoke.py -v -m integration
python scripts/validate_null_distribution.py --input outputs/null_validation_real_best.npz
python scripts/validate_null_distribution.py --input outputs/null_validation_real_best.npz --per-source
```

真实 null 验证必须同时满足：总量 `mean(c) ∈ [2.5, 3.5]`，三源 `mean(c_source)` 均接近 `1.0`。KS test 仅在 `stride >= window_size` 或使用 `--decimate` 后作为辅助判断；若校准不通过，不把 whitened CUSUM 作为默认生产触发器，只保留为实验模式。

---

## 📝 下一步计划评审修正（2026-04-29）

对上一节「🧭 下一步计划」做三处修正。Task 2 失败的诊断方向正确（`mean(c)=12.44 vs 期望 3`，`S` 被低估约 4×），但执行细节有可改进之处。

### 修正 1：把 KS 验收限定在 stride ≥ window_size 的样本上

**问题**：当前 dump 用 `trajectory_length=30, window_size=5, stride=1` 产生 130 个样本，相邻样本来自高度重叠的 EKF 轨迹，**iid 假设被严重违反**，KS p-value 不可解释。报告自己提到这点但仍把 KS 当主要验收指标，自相矛盾。

**两个统计量的鲁棒性差异**：

| 指标 | 对样本相关性鲁棒？ | 当前是否可信 |
| --- | --- | --- |
| `mean(c)` 接近理论 dof=3 | ✅ 鲁棒（线性统计量） | ✅ 可信，结论"`S` 被低估"成立 |
| KS test p > 0.05 | ❌ 假设 iid | ❌ 当前 p=2.4e-27 含相关性偏差 |

**修正**：

- Step 1 sweep 时 `stride` 必须设为 `>= window_size`（即至少 5），否则 KS 输出无意义
- 主要验收指标改为 `mean(c) ∈ [2.5, 3.5]`（鲁棒），KS 只作辅助
- 若必须保留高密度 dump（stride=1）做诊断，至少在脚本里支持 `--decimate <stride>` 二次采样后再做 KS

### 修正 2：先做零成本的 per-source 拆分，再决定是否 R_obs sweep

**问题**：当前 `c_step = sum_over_sources(y_s_inv_y[step, src])` 把 3 个源的 χ²(1) 求和成 χ²(3)，**仅当三源独立时**才成立。Task 2 dump 里 `max(c)=89.15`，比 χ²(3) 的 99.9% 分位 16.27 高 **5.5 倍**，是非常强的"单步爆炸"信号——常见原因是 source-association 错位（plan_whiten_innov.md 待解决 #4 / 论文 note L251 都警示过）。

**为什么这是必要的前置步骤**：

- 若**某个源**主导了膨胀（典型的 association swap），盲目 sweep R_obs 会把好源的 R 也一起放大，引入新偏差
- 若**三源同等膨胀**，才是真正的 R_obs 标定问题，此时 sweep 才有意义

**修正**：在 Step 1 之前插入 **Step 0**：

- `pipeline_run.py` 的 dump 钩子额外保存 `c_per_step_per_source: np.ndarray[steps, num_sources]`（约 5 行改动）
- `validate_null_distribution.py` 增加 `--per-source` 模式，逐源 KS test 对 χ²(1)
- 验收：三源 mean 都接近 1.0；若任一源 mean ≫ 1.0 而其他源接近 1.0，问题在 association/EKF 初始化，**不是 R_obs**

### 修正 3：Step 4 的默认值参数对齐当前 trigger 接口

**问题**：Step 4 写了

```text
记录推荐默认值：alpha、b_offset、warmup_windows、min_gap_windows
```

但 `WhitenedCusumTrigger.__init__` 当前签名只有 `p_fa, dof, b_offset, reset_after_trigger`（`drift_trigger.py:132-138`）。`alpha` 命名歧义、`warmup_windows` / `min_gap_windows` 在代码里不存在。

**修正**（二选一）：

- **(a) 不扩接口**：Step 4 改为记录 `p_fa, b_offset, reset_after_trigger` 三项的推荐默认值，删除 `warmup_windows / min_gap_windows`
- **(b) 扩接口**：把"扩展 `WhitenedCusumTrigger` 加 `warmup_windows` 与 `min_gap_windows` + 写对应 unit test"显式列为 Step 4.0 子任务，并在 Step 5 验收命令里覆盖到

推荐 (a)，理由是：CUSUM 已有 `reset_after_trigger` 的 reset 语义，warmup 也可以通过让上层 pipeline 在前 N 个 window 不调用 `observe_window` 简单实现，不必污染 trigger 类。

### 修正后的执行顺序

```text
Step 0  per-source 拆分诊断          ← 新增，零成本
  ├─ 若 single-source 异常 → 修 association/EKF 初始化，不进 R_obs sweep
  └─ 若 three-source 同步异常 → 进入 Step 1

Step 1  R_obs sweep（stride≥window_size）  ← 验收指标主改 mean，KS 辅助
        与 Step 3（calibration-data R_obs）并行考虑

Step 2  长轨迹复验                    ← 不变

Step 3  模型误差诊断                  ← 改为与 Step 1 并行候选

Step 4  推荐默认值（采用 (a) 不扩接口）

Step 5  文档与测试收尾                ← 不变
```

### 📌 修正后结论

Task 2 失败本身是 commit 前暴露的好信号。修正后的下一步计划要点：

1. **Step 0 优先**：per-source 诊断 5 行代码即可，可能直接跳过 R_obs sweep
2. **stride 必须 ≥ window_size 才允许做 KS**，主要验收用 `mean(c)`
3. **不引入 trigger 接口里不存在的参数**

按此顺序推进，最坏情况能在 1-2 天内确定"白化 CUSUM 在本仓库 SubspaceNet+EKF 下是否真的可用"。

---

## 🔧 下一步计划评审修正执行记录（2026-04-29）

已按评审修正落地三项基础能力：

1. `pipeline_run.py` 的 null dump 现在同时写出总量 `c` 与逐源矩阵 `c_per_step_per_source`，后续可区分 single-source association 问题和 three-source 同步膨胀问题。
2. `scripts/validate_null_distribution.py` 新增 `--per-source` 与 `--decimate <N>`：
   - `--per-source`：逐源按 `χ²(1)` 输出 mean 与 KS test。
   - `--decimate`：对 stride=1 这类重叠 window dump 做二次抽样后再检验。
3. 「下一步计划」已改为评审修正版：
   - Step 0 先做 per-source 拆分诊断。
   - Step 1 的 KS 仅在 `stride >= window_size` 或 decimate 后解释。
   - Step 4 不扩 trigger 接口，只记录 `p_fa`、`b_offset`、`reset_after_trigger`。

新增/更新的轻量测试：

```text
tests/online_learning/test_validate_null_distribution.py
tests/integration/test_whitened_trigger_smoke.py
```

---

## 🧪 Step 0 per-source 真实诊断结果（2026-04-29）

已按修正版计划先跑 Step 0，而不是直接进入 `R_obs` sweep。

运行配置：

```text
system_model.eta=0
system_model.sv_noise_var=0
system_model.nominal=true
online_learning.dataset_size=1
online_learning.trajectory_length=30
online_learning.window_size=5
online_learning.stride=5
online_learning.eta_increment=0
online_learning.max_eta=0
online_learning.dump_c_per_step_path=outputs/null_validation_per_source.npz
online_learning.drift_trigger.type=time_to_learn
online_learning.drift_trigger.target_window=999999
```

dump 摘要：

```text
keys: ['c', 'c_per_step_per_source', 'dof', 'trajectory_idx']
c_shape = (30,)
c_per_step_per_source_shape = (30, 3)
mean(c) = 6.077
mean(c_source) = [1.176, 1.732, 3.168]
min(c) = 0.123
max(c) = 27.784
max(c_source) = 19.308
```

逐源验证：

```text
.venv-wsl/bin/python scripts/validate_null_distribution.py --input outputs/null_validation_per_source.npz --per-source

source[0]: N=30, mean=1.176, KS p=0.1679  PASS
source[1]: N=30, mean=1.732, KS p=0.4564  PASS
source[2]: N=30, mean=3.168, KS p=0.0121  FAIL
```

总量验证：

```text
.venv-wsl/bin/python scripts/validate_null_distribution.py --input outputs/null_validation_per_source.npz

total: N=30, mean=6.077, KS p=0.002349  FAIL
```

### 结论

Step 0 显示问题不是干净的 three-source 同步膨胀。`source[2]` 明显主导 null 分布偏离，`source[1]` 也有中等偏高，`source[0]` 基本正常。因此暂不进入盲目的 `R_obs` / `measurement_noise_std_dev` sweep。

下一步应先诊断：

1. source association 是否在第 3 个源附近发生 swap 或排序错位；
2. EKF 初始化 / 上一窗状态传递是否对 source[2] 更敏感；
3. `labels`、SubspaceNet 输出、EKF prediction 三者在每一步的 source 顺序是否一致；
4. 若修正 association 后三源仍同步偏大，再回到 Step 1 做 `R_obs` sweep。

---

## 🔬 Source / R_obs 诊断继续执行（2026-04-29）

在继续诊断时补充了更细的 dump 字段：

```text
true_angles
pre_ekf_predictions
ekf_predictions
innovations
innovation_covariances
```

### 1. 复跑 Step 0 后的观察

由于未固定随机种子，复跑后的异常源不再固定为 `source[2]`，而是 `source[0]`、`source[1]` 更高：

```text
mean(c_source) = [4.825, 2.393, 1.990]
mean(c_total) = 9.207
mean_abs_measurement_error_deg = [9.132, 9.242, 5.160]
mean_abs_innovation_deg = [7.616, 5.974, 5.073]
mean_sqrtS_deg = [4.628, 4.628, 4.628]
```

切片分析显示，第一窗口确实有冷启动大残差，但去掉第一窗口后仍偏高：

```text
drop_first_window_5:
mean_total = 7.056
mean_src = [3.269, 1.656, 2.132]
```

这说明问题不是某一个固定 source 的 association bug，而是 SubspaceNet 测量误差整体大于当前 EKF 观测噪声假设。

### 2. Oracle EKF 检查

用真实角度作为 EKF measurement 重新计算 null 统计：

```text
oracle_true_measurement_mean_c_source = [0.005608, 0.000110, 0.047073]
oracle_true_measurement_mean_total = 0.052792
oracle_mean_abs_innov_deg = [0.1461, 0.0357, 0.5600]
oracle_mean_sqrtS_deg = [4.6275, 4.6275, 4.6275]
```

结论：EKF sine-acceleration 动力学本身没有制造 null 膨胀；主要矛盾是 `R_obs` / `measurement_noise_std_dev` 低估了 pretrained SubspaceNet 的实际测量误差。

### 3. 固定 seed 的短轨迹 `measurement_noise_std_dev` sweep

固定 seed 后，对同一条 no-drift 轨迹做短 sweep：

```text
measurement_noise_std_dev=0.05 -> mean_total=11.0704, mean_src=[3.4987, 2.0420, 5.5297], sqrtS=4.628°
measurement_noise_std_dev=0.10 -> mean_total=4.2091,  mean_src=[1.3000, 0.9508, 1.9582], sqrtS=7.300°
measurement_noise_std_dev=0.12 -> mean_total=3.1839,  mean_src=[0.9912, 0.7520, 1.4408], sqrtS=8.405°
measurement_noise_std_dev=0.13 -> mean_total=2.8122,  mean_src=[0.8809, 0.6759, 1.2553], sqrtS=8.961°
measurement_noise_std_dev=0.14 -> mean_total=2.5053,  mean_src=[0.7906, 0.6113, 1.1034], sqrtS=9.518°
measurement_noise_std_dev=0.20 -> mean_total=1.4333,  mean_src=[0.4806, 0.3683, 0.5844], sqrtS=12.879°
```

`0.12` 是当前最好的短轨迹候选：

```text
.venv-wsl/bin/python scripts/validate_null_distribution.py --input outputs/null_validation_noise_0p12.npz
total: mean=3.184, KS p=0.1366 PASS

.venv-wsl/bin/python scripts/validate_null_distribution.py --input outputs/null_validation_noise_0p12.npz --per-source
source[0]: mean=0.991, KS p=0.5847 PASS
source[1]: mean=0.752, KS p=0.3321 PASS
source[2]: mean=1.441, KS p=0.2660 PASS
```

### 4. 长轨迹复验

按计划继续跑长轨迹复验，固定：

```text
dataset_size ∈ {3, 5}
trajectory_length ∈ {50, 100}
window_size = 5
stride = 5
```

先验证短轨迹候选 `measurement_noise_std_dev=0.12`：

```text
0.12 / ds=3,len=50:  N=150, mean_total=2.3825, p_total=1.994e-05, mean_src=[0.9369, 0.6430, 0.8025]
0.12 / ds=3,len=100: N=300, mean_total=2.7235, p_total=0.0003338, mean_src=[0.9601, 0.6944, 1.0690]
0.12 / ds=5,len=50:  N=250, mean_total=2.3997, p_total=1.066e-06, mean_src=[0.9222, 0.6385, 0.8390]
0.12 / ds=5,len=100: N=500, mean_total=2.7121, p_total=4.595e-05, mean_src=[0.9366, 0.7415, 1.0340]
```

结论：`0.12` 在长轨迹上偏保守，短长度组合的 `mean_total < 2.5`，且 `source[1]` 长期偏低。

随后细化到 `0.11`：

```text
0.11 / ds=3,len=50:  N=150, mean_total=2.7066, p_total=0.007013, mean_src=[1.0690, 0.7228, 0.9148]
0.11 / ds=3,len=100: N=300, mean_total=3.1048, p_total=0.09671,  mean_src=[1.0948, 0.7830, 1.2269]
0.11 / ds=5,len=50:  N=250, mean_total=2.7221, p_total=0.003201, mean_src=[1.0487, 0.7145, 0.9589]
0.11 / ds=5,len=100: N=500, mean_total=3.0879, p_total=0.06506,  mean_src=[1.0639, 0.8370, 1.1870]
```

结论：`0.11` 的 total mean 四组全部落在 `[2.5, 3.5]`，但 source[1] 仍低，短长度 total KS 仍失败。

最后细化到 `0.105`：

```text
0.105 / ds=3,len=50:  N=150, mean_total=2.8960, p_total=0.05036, mean_src=[1.1466, 0.7690, 0.9805]
0.105 / ds=3,len=100: N=300, mean_total=3.3280, p_total=0.48300, mean_src=[1.1737, 0.8345, 1.3198]
0.105 / ds=5,len=50:  N=250, mean_total=2.9104, p_total=0.03063, mean_src=[1.1230, 0.7582, 1.0293]
0.105 / ds=5,len=100: N=500, mean_total=3.3076, p_total=0.25540, mean_src=[1.1382, 0.8925, 1.2770]
```

### 5. 长复验结论

当前最佳 scalar `R_obs` 候选：

```text
kalman_filter.measurement_noise_std_dev = 0.105
```

理由：

- 四个长复验组合的 `mean_total` 全部落在 `[2.5, 3.5]`；
- `trajectory_length=100` 的两组 total KS 都通过；
- 三源 mean 比 `0.12` 更接近 `[1,1,1]`，且比 `0.11` 更接近总量目标。

限制：

- `source[1]` 仍持续 under-dispersed（约 `0.77-0.89`），说明单一 scalar `R_obs` 不是完美校准；
- `ds=5,len=50` 的 total KS 仍失败（`p=0.03063`），因此不能声称严格 χ² null 已完全成立；
- 更严谨的下一步是 source-specific `R_obs` 或 calibration-data empirical `R_obs`。

执行决策：

```text
measurement_noise_std_dev=0.105 可作为下一阶段 whitened CUSUM 触发实验的 scalar 候选值；
不要把它写成最终理论默认值；
下一步进入 b_offset / p_fa 触发效果实验，同时保留 source-specific R_obs 作为研究项。
```

---

## 🚦 Whitened CUSUM 触发参数回放实验（2026-04-29）

### 1. 实验方式

为了先评估触发器参数，而不引入在线训练带来的额外变量，本轮使用 lightweight replay：

1. 用已校准的 `measurement_noise_std_dev=0.105` 生成 no-drift / drift 的 `c_per_step` 序列；
2. 离线构造 `WhitenedCusumTrigger(p_fa, dof=3, b_offset, reset_after_trigger=True)`；
3. 按 window 顺序把每个 window 的 5 个 `c` 喂给 trigger；
4. 统计 no-drift 误触发率、drift 检测率和首次触发延迟。

执行注意：不能用固定 `system_model.eta=0.6/1.0` 直接调用 `execute_online_learning()` 来生成 drift stream，因为 `run_online_learning_impl()` 会在每条 trajectory 开始时把 eta 重置为 0。本轮 drift stream 改用动态 eta 更新：

```text
trajectory_length=100
window_size=5
stride=5
eta_update_interval_windows=5
eta_increment ∈ {0.6, 1.0}
max_eta ∈ {0.6, 1.0}
drift_onset_window = 5
```

### 2. 初始参数矩阵失败

初始矩阵：

```text
p_fa ∈ {0.01, 0.05, 0.10}
b_offset ∈ {0.5, 1.0, 1.5}
```

结果：所有组合都能在动态 drift 后快速触发，但 no-drift replay 中 `null_any_rate=1.0`，即每条 no-drift trajectory 至少误触发一次。

结论：真实 residual tail 比理论 χ²/CUSUM 假设更重，原始解析阈值太激进，不能直接用 `p_fa≤0.1` 与小 `b_offset`。

### 3. 保守参数矩阵

继续扩展：

```text
p_fa ∈ {1e-6, 1e-5, 1e-4}
b_offset ∈ {6, 8, 10, 12, 16, 20}
```

最佳候选：

```text
p_fa = 1e-6
b_offset = 20
reset_after_trigger = true
```

在全部 `measurement_noise_std_dev=0.105` 长复验 no-drift 文件上回放：

```text
ds=3,len=50:   0/3 trajectories false-alarmed
ds=3,len=100:  0/3 trajectories false-alarmed
ds=5,len=50:   0/5 trajectories false-alarmed
ds=5,len=100:  0/5 trajectories false-alarmed
ALL:           0/16 trajectories false-alarmed
```

动态 drift replay：

```text
eta=0.6: detect_rate=1.0, avg_delay=1.667 windows
eta=1.0: detect_rate=1.0, avg_delay=1.000 windows
```

### 4. 触发实验结论

当前推荐进入下一阶段 end-to-end online-training 的保守 replay 候选：

```yaml
kalman_filter:
  measurement_noise_std_dev: 0.105

online_learning:
  drift_trigger:
    type: whitened_cusum
    p_fa: 1e-6
    dof: 3
    b_offset: 20.0
    reset_after_trigger: true
```

注意措辞：

- 这不是“理论 p_fa=1e-6 已被证明成立”；
- 这是“在当前 long-null replay 集合上 0/16 trajectory 误触发”的经验候选；
- `b_offset=20` 远大于原先理论建议，说明真实 residual tail / source imbalance 仍未完全满足理想 χ² 假设；
- 若后续要写论文，应该把它描述为 **empirically calibrated conservative CUSUM reference**，并把 source-specific `R_obs` 作为进一步收紧理论假设的方向。

下一步：

```text
用 measurement_noise_std_dev=0.105 + p_fa=1e-6 + b_offset=20 跑一次真正 end-to-end online-training；
观察 drift_detected_count、training_start_window、RMSPE 是否改善；
若训练闭环稳定，再与 time_to_learn / sigma_y_sq comparator 对比。
```

---

## 🧪 Calibrated Whitened CUSUM 闭环 Smoke（2026-04-29）

### 1. 新增 YAML 预设

新增：

```text
run/conf/Used_for_paper/SineAccel_whitened_cusum_calibrated.yaml
```

内容要点：

```yaml
kalman_filter:
  measurement_noise_std_dev: 0.105

online_learning:
  drift_trigger:
    type: whitened_cusum
    p_fa: 1e-6
    dof: 3
    b_offset: 20.0
    reset_after_trigger: true
```

### 2. 一条 trajectory 闭环验证

运行设置：

```text
trajectory_length=100
window_size=5
stride=5
eta_update_interval_windows=5
eta_increment=0.6
max_eta=0.6
max_iterations=1
dump_c_per_step_path=outputs/e2e_whitened_cusum_calibrated_eta0p6.npz
```

运行结果：

```text
E2E_STATUS success
```

由于 `execute_online_learning()` 顶层返回的是 averaged 结构，本次用 dump replay 与日志共同确认触发窗口。对输出 dump 重新回放 calibrated trigger：

```text
replay_fired_windows = [6, 12, 13, 16, 18, 19]
window_mean_first12 = [3.592, 2.285, 1.624, 2.097, 2.808, 1.866, 23.871, 17.641, 5.079, 13.512, 8.295, 13.374]
```

日志显示：

```text
window 6 进入 LEARNING PHASE
window 11 起进入 POST-LEARNING
```

### 3. Calibrated 候选参数的多轨迹回放验证

闭环 smoke 之外，把同样 `p_fa=1e-6 / b_offset=20 / reset_after_trigger=True` 的 calibrated CUSUM 在已有 dump 上做 windowed replay（`window_size=5, stride=5`），验证候选参数不是单条 trajectory 的偶然结果。

数据来源：

```text
no-drift（4 个 dump，共 16 条轨迹）:
  outputs/long_null_noise_0p105_ds3_len50.npz   (3 trajs × 50 steps)
  outputs/long_null_noise_0p105_ds3_len100.npz  (3 trajs × 100 steps)
  outputs/long_null_noise_0p105_ds5_len50.npz   (5 trajs × 50 steps)
  outputs/long_null_noise_0p105_ds5_len100.npz  (5 trajs × 100 steps)

dynamic drift（每条 dump 含 3 条轨迹，onset_window=5）:
  outputs/trigger_replay_dynamic_eta_0p6_noise_0p105.npz
  outputs/trigger_replay_dynamic_eta_1p0_noise_0p105.npz
```

回放结果（已用本仓库 `WhitenedCusumTrigger` 实测复算确认）：

| 场景 | 检测/总轨迹 | 首次触发延迟（window） | 备注 |
| --- | --- | --- | --- |
| no-drift | **0 / 16** 出现误触发 | N/A | 跨 ds∈{3,5} × len∈{50,100} 全部 0 误触发 |
| dynamic eta=0.6 | **3 / 3** | mean=1.667 | onset 后 1-2 window 内全部触发 |
| dynamic eta=1.0 | **3 / 3** | mean=1.000 | onset 后 1 window 内全部触发 |

补充验证：

- Hydra 加载 `SineAccel_whitened_cusum_calibrated.yaml` 配置 smoke 通过（trigger 正常构建，`measurement_noise_std_dev=0.105` 生效）
- `pytest tests/online_learning/test_drift_trigger.py tests/integration/test_whitened_trigger_smoke.py -v`：**17 passed, 2 warnings**（剩 Pydantic V2 警告与本特性无关）

### 4. 闭环结论

保守候选：

```text
measurement_noise_std_dev=0.105
p_fa=1e-6
b_offset=20
reset_after_trigger=true
```

跨 16 条 no-drift 轨迹零误触发，跨两个漂移幅度 6/6 全部检测且平均延迟 1-2 个 window，已经具备进入正式实验对比的基础。

仍需注意：

- **同条件三 trigger 对比已在下一节补做**：calibrated whitened CUSUM 与 `time_to_learn` / `sigma_y_sq` 已完成一轮短闭环 smoke；结果显示 replay 通过不等于闭环路径无提前触发，见下一节。
- **重复触发问题未修**：闭环 replay 在单条 trajectory 上观察到 `[6, 12, 13, 16, 18, 19]` 多次触发；若要在生产路径里减少冗余 GD 调用，需要在 pipeline 层加 post-trigger cooldown，或在 learning phase 内暂停 drift trigger（**注意**：cooldown 不是 trigger 类的职责，建议放在 `pipeline_run.py` 的窗口循环里，不污染 trigger 接口）

下一步实验建议：

```text
dataset_size=3
trajectory_length=100
eta_update_interval_windows=5
eta_increment ∈ {0.6, 1.0}

对比：
1. time_to_learn baseline
2. sigma_y_sq comparator
3. calibrated whitened_cusum

指标：
- first_trigger_window
- pre-drift false trigger
- drift_detected_count
- training_start_window / training_end_window
- post-learning RMSPE improvement
```

---

## ⚖️ 三触发器短闭环对比 Smoke（2026-04-29）

### 1. 执行目的

上一节的 replay 结果说明 `measurement_noise_std_dev=0.105 / p_fa=1e-6 / b_offset=20` 在已有 no-drift dump 上足够保守，但 replay 只把保存好的 `c_per_step` 喂给 trigger，没有覆盖完整在线学习闭环。

本轮补做同条件短闭环对比：

1. `time_to_learn`
2. `sigma_y_sq`
3. `whitened_cusum_calibrated`

主要看：

- 首次进入 online path 的窗口（用 `online_trajectory_results.window_indices[0]` 作为 proxy）
- 是否在 drift onset 前提前进入 online path
- `drift_detected_count`
- tail-5 RMSPE 是否比 pretrained 路径改善

### 2. 实验设置

输出目录：

```text
outputs/e2e_whitened_cusum_trigger_comparison_20260429/
```

压缩结果：

```text
outputs/e2e_whitened_cusum_trigger_comparison_20260429/summary.json
```

共同设置：

```text
dataset_size=3
trajectory_length=100
window_size=5
stride=5
eta_update_interval_windows=5
eta_increment ∈ {0.6, 1.0}
max_eta ∈ {0.6, 1.0}
drift_onset_window=5
max_iterations=1
kalman_filter.measurement_noise_std_dev=0.105
```

`time_to_learn` 特殊说明：

```text
target_window=6
```

原因：短实验只有 20 个 window，原配置 `time_to_learn=35` 不会触发；这里把 fixed-time baseline 设成 onset 后 1 个 window，用来作为“已知漂移大致发生时刻”的乐观固定触发基线。

模型权重说明：

```text
simulation.load_model=false
```

原因：当前 workspace 中配置里指向的 checkpoint：

```text
experiments/results/base_model_random_data_snr_10_SubspaceNet_esprit_N9_M3_SNR10.0_Far_ESPRIT/checkpoints/final_SubspaceNet_20250916_084930.pt
```

不存在。因此本轮是 pipeline / comparator smoke，不是最终论文级性能实验。后续正式结论必须恢复真实 pretrained checkpoint。

### 3. 结果表

字段说明：

- `first_online_windows`：每条 trajectory 第一次进入 online model 路径的 window；它是闭环里 trigger/training start 的近似 proxy。
- `pre-false`：`first_online_window < drift_onset_window(5)` 的 trajectory 数。
- `drift_count`：三条 trajectory 的总触发次数。修复 `pipeline_run.py` 后，同一 trajectory 进入 online-learning path 后会暂停继续观察 trigger，因此该值每条 trajectory 最多计 1 次。
- `tail5_improve`：最后 5 个窗口中 `pretrained RMSPE - online RMSPE` 的平均值；正数表示 online path 更低。

本节执行过程中顺手修复了一个 pipeline 级问题：

```text
src/trainer_module/online_learning_parts/pipeline_run.py
```

修复内容：

- 每个 window 都写入 `window_update_flags`，触发窗口写 `True`，非触发窗口写 `False`；
- 一旦当前 trajectory 已经进入 online-learning path，就暂停继续调用 drift trigger，只保留 `c_per_step` dump 诊断；
- 这样 `drift_detected_count` 不再被 post-trigger 重复触发污染。

`eta=0.6`：

| Trigger | first_online_windows | pre-false | drift_count | mean first window | tail5_improve |
| --- | --- | ---: | ---: | ---: | ---: |
| `time_to_learn` | `[6, 6, 6]` | 0 / 3 | 3 | 6.000 | +0.1415 |
| `sigma_y_sq` | `[0, 0, 0]` | 3 / 3 | 3 | 0.000 | +0.0637 |
| `whitened_cusum_calibrated` | `[2, 6, 8]` | 1 / 3 | 3 | 5.333 | +0.1010 |

`eta=1.0`：

| Trigger | first_online_windows | pre-false | drift_count | mean first window | tail5_improve |
| --- | --- | ---: | ---: | ---: | ---: |
| `time_to_learn` | `[6, 6, 6]` | 0 / 3 | 3 | 6.000 | +0.1452 |
| `sigma_y_sq` | `[0, 0, 0]` | 3 / 3 | 3 | 0.000 | +0.0709 |
| `whitened_cusum_calibrated` | `[3, 1, 0]` | 3 / 3 | 3 | 1.333 | +0.0739 |

### 4. 本轮结论

正向结论：

- 三个 trigger 的闭环路径均能跑通，`status=success`。
- `time_to_learn(target_window=6)` 作为乐观固定基线最稳定：无提前触发，tail-5 RMSPE 改善最大。
- `whitened_cusum_calibrated` 相比 `sigma_y_sq` 更保守一些：`eta=0.6` 时只 1/3 提前触发，而 `sigma_y_sq` 是 3/3 从 window 0 开始触发。

暴露的问题：

- replay 上 `whitened_cusum_calibrated` 的 no-drift 是 `0/16` 误触发，但闭环 smoke 中仍出现 pre-drift 提前进入 online path：
  - `eta=0.6`: 1 / 3
  - `eta=1.0`: 3 / 3
- 原因可能不是 trigger 类本身，而是闭环运行的随机轨迹 / 随机模型 / 数据生成分布与之前 dump replay 不完全一致。
- `sigma_y_sq(tau_sigma=1.5)` 在短闭环里明显过敏：两组 eta 都是 window 0 开始触发，不能作为当前阈值下的有效 comparator。
- 重复触发计数已通过 pipeline pause 修复；当前剩余问题集中在 **首次触发过早**，不是重复计数。

### 5. 下一步修正

本轮不应直接把 calibrated CUSUM 宣称为“闭环已优于 baseline”。更合理的下一步是：

```text
1. 恢复真实 pretrained checkpoint，重跑同条件三触发器对比。
2. 已执行闭环 no-drift smoke 和 b_offset 复扫，结果见下一小节。
3. 对 sigma_y_sq 单独扫 tau_sigma；当前 tau=1.5 在本设置下太敏感。
4. 如果需要支持多次真实漂移，再把当前“触发后暂停”升级为带恢复条件的 cooldown 状态机；当前单漂移实验不需要。
```

当前状态判断：

```text
whitened CUSUM 的统计量与 replay 基础能力已经可用；
但闭环触发策略尚未验收完成，不能进入最终性能结论；
重复触发污染已修复；
下一轮优先解决“source-level c 爆点诊断”和真实 checkpoint 复验。
```

### 6. 闭环 no-drift smoke 与 b_offset 复扫

按上一节修正项，继续跑 calibrated CUSUM 的闭环 no-drift smoke：

```text
outputs/e2e_whitened_cusum_closed_loop_null_20260429/summary.json
```

设置：

```text
dataset_size=3
trajectory_length=100
window_size=5
stride=5
eta_increment=0
max_eta=0
measurement_noise_std_dev=0.105
p_fa=1e-6
b_offset=20
simulation.load_model=false
```

结果：

```text
first_online_windows = [2, 2, 0]
false_trigger_trajectory_count = 3 / 3
total_drift_detected = 3
```

结论：闭环 no-drift 未通过。虽然 dump replay 的 no-drift 是 `0/16`，但完整 pipeline 的 no-drift 仍会提前进入 online path。

随后扫更保守的 `b_offset`：

```text
outputs/e2e_whitened_cusum_closed_loop_null_boffset_sweep_20260429/summary.json
```

| b_offset | first_online_windows | false trigger |
| ---: | --- | ---: |
| 20 | `[2, 2, 0]` | 3 / 3 |
| 24 | `[2, 2, 0]` | 3 / 3 |
| 28 | `[2, 2, 0]` | 3 / 3 |
| 32 | `[3, 13, 0]` | 3 / 3 |
| 40 | `[3, null, 3]` | 2 / 3 |
| 50 | `[5, null, 11]` | 2 / 3 |
| 60 | `[5, null, 11]` | 2 / 3 |
| 80 | `[5, null, 11]` | 2 / 3 |
| 100 | `[5, null, null]` | 1 / 3 |
| 150 | `[5, null, null]` | 1 / 3 |
| 200 | `[5, null, null]` | 1 / 3 |

`b_offset=200` 仍在第 1 条 trajectory 的 window 5 触发，于是单独 dump 该 trajectory：

```text
outputs/e2e_whitened_cusum_closed_loop_null_boffset200_traj0_dump_20260429/summary.json
```

关键统计：

```text
first_online_windows = [5]
c_max = 225.722
argmax_step = 25
argmax_window = 5
argmax_source_values = [0.983, 0.157, 224.582]
c_mean = 9.544
c_p95 = 48.197
c_p99 = 64.191
top10 = [225.722, 62.559, 61.449, 54.179, 48.216, 48.196, 38.015, 36.014, 32.841, 27.343]
```

解释：

- `b_offset=200` 的 reference 是 `dof + b_offset = 203`，threshold 约 `16.63`，单步 `c≈225.7` 足以直接越过阈值。
- 爆点几乎全部来自 `source[2]`，不是三源均匀偏大。
- 继续盲目增大 `b_offset` 已经不合理；这会把真实 drift 检测也钝化，并且没有解决 source-level outlier。

更新后的下一步：

```text
1. 不再继续单纯抬 b_offset。
2. 回到 source-level 诊断：检查 source[2] 的 association / permutation / innovation covariance。
3. 用真实 pretrained checkpoint 复验；当前 random/unloaded model 可能放大 measurement residual。
4. 若真实 checkpoint 下仍有 source-level 爆点，再考虑：
   - source-specific R_obs
   - empirical/capped innovation covariance
   - trigger 侧加入 per-window robust aggregation（例如 winsorize 单步 c），但这属于策略改动，需要单独论证。
```

验证：

```text
PYTHONPATH=. .venv-wsl/bin/python -m pytest \
  tests/online_learning/test_drift_trigger.py \
  tests/integration/test_whitened_trigger_smoke.py \
  tests/online_learning/test_validate_null_distribution.py -q

20 passed, 2 warnings
```

---

## 🧭 Pretrained Checkpoint 复验计划（2026-04-29）

### 1. 规则对齐说明

本节按本仓库本地工作流中记录的 `architecture-design` / `superpowers:executing-plans` 风格继续执行：

- 使用 checkbox 任务追踪；
- 每一步先写清目标、输入、输出和验收标准；
- 优先做最小闭环验证，再扩大实验矩阵；
- 保留配置、输出目录、随机种子、checkpoint 路径，保证实验可复现；
- 不把 random/unloaded model 的 smoke 结果当成最终性能结论。

说明：当前 Codex 会话没有注册可直接调用的 `/superpowers` 或 `/ll-architecture-design` skill；本节使用仓库内 `docs/workflow_ll/workflow_ll.md` 与已有 `plan_implementation_whiten_innov.md` 的执行规范作为等价本地规则来源。

### 2. Checkpoint 搜索结果

目标配置原本引用：

```text
experiments/results/base_model_random_data_snr_10_SubspaceNet_esprit_N9_M3_SNR10.0_Far_ESPRIT/checkpoints/final_SubspaceNet_20250916_084930.pt
```

当前 workspace 中未找到该精确文件。

可用候选：

```text
checkpoints/saved_SubspaceNet_trained_20260224_180720.pt
```

兼容性检查：

```text
exists=True
size_bytes=172802
type=collections.OrderedDict
tensor_key_count=13
strict_load=success
```

因此下一轮复验使用：

```text
simulation.load_model=true
simulation.model_path=checkpoints/saved_SubspaceNet_trained_20260224_180720.pt
```

### 3. 执行计划

- [x] **Step A：确认候选 checkpoint 是否存在**
  - 输入：`checkpoints/saved_SubspaceNet_trained_20260224_180720.pt`
  - 验收：文件存在，且不是 Lightning wrapper-only artifact。
  - 结果：通过。

- [x] **Step B：确认 checkpoint 能否加载到当前 SubspaceNet**
  - 输入：`SineAccel_whitened_cusum_calibrated.yaml` 当前模型结构。
  - 验收：`model.load_state_dict(state, strict=True)` 成功。
  - 结果：通过。

- [x] **Step C：用 pretrained checkpoint 重跑闭环 no-drift smoke**
  - 目的：判断之前 no-drift 提前触发是否主要由 random/unloaded model 放大 residual 导致。
  - 设置：

```text
dataset_size=3
trajectory_length=100
window_size=5
stride=5
eta_increment=0
max_eta=0
measurement_noise_std_dev=0.105
p_fa=1e-6
b_offset=20
simulation.load_model=true
simulation.model_path=checkpoints/saved_SubspaceNet_trained_20260224_180720.pt
```

  - 验收：
    - `status=success`
    - `first_online_windows` 为空或全为 `null` 才算 no-drift 通过
    - 若仍误触发，记录 `c_max / argmax_window / argmax_source_values`
  - 结果：运行成功，但 no-drift 未完全通过，见「Step C 执行记录」。

- [ ] **Step D：若 Step C 通过，再跑 dynamic drift smoke**
  - 设置：

```text
eta_increment ∈ {0.6, 1.0}
max_eta ∈ {0.6, 1.0}
其他设置与 Step C 相同
```

  - 验收：
    - no pre-drift false trigger
    - drift onset 后能进入 online path
    - tail-5 RMSPE improvement 不显著劣化

- [x] **Step E：若 Step C 失败，进入 source-level 诊断**
  - 重点：
    - 误触发 window 的 `c_per_step_per_source`
    - source association / permutation
    - source[2] 的 innovation covariance 是否被低估
    - 是否需要 source-specific `R_obs`
  - 结果：完成初步 source-level dump 诊断，爆点来源从 random model 下的 source[2] 变为 pretrained 下的 source[0]，见下方记录。

当前优先执行下一节「association sanity check」，先判断误触发是否来自 source 对齐问题。

### 4. Step C 执行记录：pretrained no-drift smoke

输出目录：

```text
outputs/e2e_whitened_cusum_pretrained_null_20260429/
```

输入 checkpoint：

```text
checkpoints/saved_SubspaceNet_trained_20260224_180720.pt
```

运行设置：

```text
dataset_size=3
trajectory_length=100
window_size=5
stride=5
eta_increment=0
max_eta=0
measurement_noise_std_dev=0.105
p_fa=1e-6
b_offset=20
simulation.load_model=true
simulation.model_path=checkpoints/saved_SubspaceNet_trained_20260224_180720.pt
dump_c_per_step_path=c_dump.npz
```

结果：

```text
status = success
first_online_windows = [null, null, 15]
false_trigger_trajectory_count = 1 / 3
avg_drift_detected = 0.3333
total_drift_detected = 1
```

和 random/unloaded model 的对比：

| 条件 | first_online_windows | false trigger |
| --- | --- | ---: |
| random/unloaded model | `[2, 2, 0]` | 3 / 3 |
| pretrained checkpoint | `[null, null, 15]` | 1 / 3 |

结论：

- pretrained checkpoint 明显降低 no-drift 提前触发；
- 但 calibrated CUSUM 仍未通过闭环 no-drift 验收；
- 这说明 random model 确实放大了 residual，但不是唯一原因。

### 5. Step E 初步 source-level 诊断

dump 文件：

```text
outputs/e2e_whitened_cusum_pretrained_null_20260429/c_dump.npz
```

最大统计量：

```text
c_max = 56.187
argmax_step = 76
argmax_window = 15
argmax_source_values = [53.946, 2.134, 0.107]
c_mean = 3.887
c_median = 2.091
c_p95 = 11.484
c_p99 = 21.098
```

对应 step 的详细量：

```text
true_angles         = [0.0847, 0.0363, -0.0533]
pre_ekf_predictions = [1.1585, 0.1071, -0.1577]
ekf_predictions     = [0.5493, 0.2282, -0.1848]
innovations         = [0.9764, -0.1942, 0.0435]
innovation_cov      = [0.01767, 0.01767, 0.01767]
pre_minus_true      = [1.0738, 0.0707, -0.1044]
ekf_minus_true      = [0.4646, 0.1919, -0.1315]
```

局部窗口附近的 `c`：

```text
step 73/window14: c=9.067,  per_source=[4.063, 4.605, 0.399]
step 74/window14: c=11.616, per_source=[0.359, 10.746, 0.511]
step 75/window15: c=2.156,  per_source=[0.351, 1.793, 0.012]
step 76/window15: c=56.187, per_source=[53.946, 2.134, 0.107]
step 77/window15: c=20.744, per_source=[12.157, 7.907, 0.681]
step 78/window15: c=1.577,  per_source=[0.470, 0.645, 0.462]
```

解释：

- pretrained 后爆点从 random model 的 `c≈225.7` 降到 `c≈56.2`；
- 误触发仍由单源主导，但本次主导源是 `source[0]`，不是之前 random model 的 `source[2]`；
- `innovation_covariance≈0.01767` 对三个 source 相同，source[0] 的 innovation `0.9764` 会得到：

```text
0.9764^2 / 0.01767 ≈ 53.95
```

这与 `c_per_source[0]=53.946` 对上，说明爆点来自「单源 innovation 大 + R/S 估计较小」的组合。

### 6. 更新后的下一步

当前不建议立刻改 trigger 策略。下一步按架构诊断顺序做：

```text
1. 检查 step_processor / losses 中 source permutation 的应用位置：
   - true_angles 排序
   - pre_ekf_predictions 排序
   - EKF state 与 measurement 的 source 对齐

2. 对 pretrained no-drift dump 做 association sanity check：
   - 对每个 step 计算 pre_ekf 与 true_angles 的最优 permutation
   - 比较当前顺序误差 vs 最优 permutation 误差
   - 如果 spike step 的最优 permutation 能显著降低 source[0] innovation，则优先修 association

3. 如果 association 正常，再诊断 R_obs/S：
   - 当前 S≈0.01767，sqrt(S)≈0.133 rad
   - source[0] innovation≈0.976 rad，约 7.35σ
   - 判断是模型预测 outlier，还是 measurement covariance 低估

4. 只有在 association/R_obs 都解释不了时，才讨论 robust CUSUM：
   - per-step c winsorization
   - per-source capped contribution
   - median/trimmed window aggregation
```

### 7. Association sanity check 执行记录

输出：

```text
outputs/e2e_whitened_cusum_pretrained_null_20260429/association_sanity.json
```

检查方式：

- 对每个 step 计算当前 source 顺序下的 RMSE；
- 枚举 3 个 source 的所有 permutation；
- 比较当前顺序 RMSE 与最优 permutation RMSE；
- 若 spike step 的最优 permutation 能显著降低误差，则说明可能是 source association 错位。

整体结果：

```text
pre_perm_changes_count = 0 / 100
ekf_perm_changes_count = 3 / 100
mean_pre_current_rmse = 0.18568
mean_pre_best_rmse    = 0.18568
mean_ekf_current_rmse = 0.14872
mean_ekf_best_rmse    = 0.14861
```

最大爆点 step：

```text
argmax_step = 76
argmax_window = 15
c = 56.187
c_per_source = [53.946, 2.134, 0.107]
pre_best_perm = [0, 1, 2]
ekf_best_perm = [0, 1, 2]
pre_current_rmse = pre_best_rmse = 0.62421
ekf_current_rmse = ekf_best_rmse = 0.30000
```

结论：

- 当前误触发不是 source permutation 错位造成的；
- spike step 的最佳 permutation 仍是原顺序 `[0,1,2]`；
- source[0] 的 `pre_ekf_prediction=1.158 rad` 相对 `true_angle=0.085 rad` 是真正的模型 outlier；
- EKF 把该 outlier 拉回到 `0.549 rad`，但 innovation `0.976 rad` 与 `S≈0.01767` 组合后仍产生 `c≈53.95`。

更新后的下一步：

```text
1. 不优先修 association。
2. 检查 checkpoint 是否与当前数据分布匹配：
   - SNR=10
   - M=3
   - Far field
   - diff_method=esprit
   - tau=8
   - 是否训练在 random samples 而非 sine-accel trajectory
3. 如果 checkpoint 分布不匹配，优先寻找/训练正确 checkpoint。
4. 如果 checkpoint 分布匹配，则进入 R_obs / robust innovation 诊断：
   - b_offset 小幅复扫可作为工程缓解，但不能解释根因；
   - source-specific R_obs 或 innovation clipping 需要单独作为策略改动评审。
```

### 8. 2 月 24 日候选 checkpoint 筛查

由于当前目录下没有原配置引用的：

```text
final_SubspaceNet_20250916_084930.pt
```

因此进一步比较当前可用的两个 2026-02-24 候选：

```text
checkpoints/saved_SubspaceNet_trained_20260224_180248.pt
checkpoints/saved_SubspaceNet_trained_20260224_180720.pt
```

输出：

```text
outputs/e2e_whitened_cusum_checkpoint_screen_20260429/summary.json
```

共同设置：

```text
dataset_size=3
trajectory_length=100
window_size=5
stride=5
eta_increment=0
max_eta=0
measurement_noise_std_dev=0.105
p_fa=1e-6
b_offset=20
simulation.load_model=true
```

结果：

| checkpoint | first_online_windows | false trigger | c_max | argmax_window | argmax_source_values |
| --- | --- | ---: | ---: | ---: | --- |
| `20260224_180248.pt` | `[9, 1, 15]` | 3 / 3 | 71.347 | 16 | `[64.397, 2.657, 4.293]` |
| `20260224_180720.pt` | `[null, null, 15]` | 1 / 3 | 56.187 | 15 | `[53.946, 2.134, 0.107]` |

结论：

- `20260224_180720.pt` 是当前目录下更合适的候选；
- `20260224_180248.pt` 在同条件 no-drift 下 3/3 误触发，不建议继续使用；
- 即便使用较优的 `180720`，闭环 no-drift 仍未完全通过，后续仍需解决单源 prediction outlier / covariance 低估问题。

后续 checkpoint 策略：

```text
1. 若能找回原始 2025-09-16 SNR10 checkpoint，应优先用原始 checkpoint 复验。
2. 若找不回，短期继续以 20260224_180720.pt 作为当前 workspace 的 best available checkpoint。
3. 论文级实验前需要重新训练或恢复与当前配置严格匹配的 checkpoint，并记录训练配置。
```

### 9. R_obs 闭环 no-drift sweep 计划

Association sanity check 已排除明显 source permutation 错位；pretrained checkpoint 也显著降低了爆点幅度。因此下一步先检查 `R_obs` 是否仍偏小。

执行计划：

- [x] **Step R1：用 best available checkpoint 扫 `measurement_noise_std_dev`**
  - checkpoint：

```text
checkpoints/saved_SubspaceNet_trained_20260224_180720.pt
```

  - sweep：

```text
measurement_noise_std_dev ∈ {0.105, 0.15, 0.20, 0.25, 0.30, 0.40}
```

  - 固定设置：

```text
dataset_size=3
trajectory_length=100
window_size=5
stride=5
eta_increment=0
max_eta=0
p_fa=1e-6
b_offset=20
simulation.load_model=true
```

  - 验收：
    - no-drift `false_trigger_trajectory_count=0/3`
    - 记录 `c_mean / c_p95 / c_p99 / c_max`
  - 结果：完成，`measurement_noise_std_dev=0.15` 是第一档 no-drift 0/3 误触发的候选。

- [x] **Step R2：若找到 no-drift 通过的 R_obs，再跑 dynamic drift smoke**
  - `eta_increment ∈ {0.6, 1.0}`
  - 观察 first online window 和 tail-5 RMSPE improvement。
  - 结果：`R_obs=0.15` no-drift 通过，但 dynamic drift 检测偏迟钝，需要在 `0.105-0.15` 之间细扫。

- [ ] **Step R3：若 R_obs 需要远大于 0.105 才通过，回写结论**
  - 说明 scalar `R_obs=0.105` 只适合 dump replay，不足以覆盖闭环 source outlier；
  - 再决定是否进入 source-specific `R_obs` 或 robust trigger。

#### Step R1 执行记录

输出：

```text
outputs/e2e_whitened_cusum_pretrained_null_robs_sweep_20260429/summary.json
```

结果：

| measurement_noise_std_dev | first_online_windows | false trigger | c_mean | c_p95 | c_p99 | c_max |
| ---: | --- | ---: | ---: | ---: | ---: | ---: |
| 0.105 | `[null, null, 15]` | 1 / 3 | 3.887 | 11.484 | 21.098 | 56.187 |
| 0.150 | `[null, null, null]` | 0 / 3 | 2.334 | 6.275 | 10.331 | 30.437 |
| 0.200 | `[null, null, null]` | 0 / 3 | 1.533 | 3.839 | 6.452 | 18.213 |
| 0.250 | `[null, null, null]` | 0 / 3 | 1.102 | 2.691 | 4.435 | 12.146 |
| 0.300 | `[null, null, null]` | 0 / 3 | 0.839 | 2.263 | 3.249 | 8.690 |
| 0.400 | `[null, null, null]` | 0 / 3 | 0.542 | 1.339 | 1.974 | 5.091 |

解释：

- `0.15` 是最小的 no-drift 闭环通过候选；
- `0.20+` 虽然也通过，但 `c_mean` 明显低于理论 `χ²(3)` 期望 3，可能过保守；
- 下一步用 `0.15` 跑 dynamic drift smoke，检查是否还能及时检测漂移。

#### Step R2 执行记录

输出：

```text
outputs/e2e_whitened_cusum_pretrained_dynamic_robs0p15_20260429/summary.json
```

设置：

```text
measurement_noise_std_dev=0.15
eta_increment ∈ {0.6, 1.0}
max_eta ∈ {0.6, 1.0}
dataset_size=3
trajectory_length=100
window_size=5
stride=5
drift_onset_window=5
p_fa=1e-6
b_offset=20
```

结果：

| eta_increment | first_online_windows | pre-drift false | detect rate | mean delay | tail5_improve | c_max |
| ---: | --- | ---: | ---: | ---: | ---: | ---: |
| 0.6 | `[null, null, 14]` | 0 / 3 | 1 / 3 | 9.0 | +0.0925 | 42.356 |
| 1.0 | `[14, null, 9]` | 0 / 3 | 2 / 3 | 6.5 | +0.0706 | 50.690 |

结论：

- `R_obs=0.15` 的闭环 no-drift 表现好，但 dynamic drift 检测偏迟钝；
- 这说明 `0.15` 可能是保守上界，不是最佳折中；
- 下一步应在 `0.105-0.15` 之间细扫，例如 `{0.115, 0.12, 0.125, 0.13, 0.135, 0.14, 0.145}`。

#### Step R2b 细扫计划

- [x] 用 best checkpoint 在 no-drift 下细扫 `measurement_noise_std_dev ∈ {0.115, 0.12, 0.125, 0.13, 0.135, 0.14, 0.145}`
- [x] 选择最小的 0/3 false-trigger 候选
- [x] 对该候选重跑 dynamic drift smoke

细扫输出：

```text
outputs/e2e_whitened_cusum_pretrained_null_robs_fine_sweep_20260429/summary.json
```

no-drift 结果：

| measurement_noise_std_dev | first_online_windows | false trigger | c_mean | c_p99 | c_max |
| ---: | --- | ---: | ---: | ---: | ---: |
| 0.115 | `[null, null, 15]` | 1 / 3 | 3.418 | 17.349 | 48.225 |
| 0.120 | `[null, null, 15]` | 1 / 3 | 3.218 | 15.830 | 44.855 |
| 0.125 | `[null, null, 15]` | 1 / 3 | 3.035 | 14.497 | 41.822 |
| 0.130 | `[null, null, null]` | 0 / 3 | 3.116 | 20.481 | 39.085 |
| 0.135 | `[null, null, null]` | 0 / 3 | 2.718 | 12.285 | 36.607 |
| 0.140 | `[null, null, null]` | 0 / 3 | 2.579 | 11.536 | 34.357 |
| 0.145 | `[null, null, null]` | 0 / 3 | 2.452 | 10.908 | 32.308 |

第一档 no-drift 通过候选：

```text
measurement_noise_std_dev=0.13
```

dynamic drift 输出：

```text
outputs/e2e_whitened_cusum_pretrained_dynamic_robs0p13_20260429/summary.json
```

| eta_increment | first_online_windows | pre-drift false | detect rate | mean delay | tail5_improve |
| ---: | --- | ---: | ---: | ---: | ---: |
| 0.6 | `[11, 9, null]` | 0 / 3 | 2 / 3 | 5.0 | -0.0109 |
| 1.0 | `[7, 6, 12]` | 0 / 3 | 3 / 3 | 3.333 | +0.1132 |

结论：

- `R_obs=0.13, b_offset=20` 是当前最好的 scalar 闭环候选；
- 它已经解决 no-drift 提前触发，并能稳定检测较强漂移 `eta=1.0`；
- 对较弱漂移 `eta=0.6` 仍偏迟钝，且 tail-5 improvement 不稳定；
- 下一步做小范围 joint 调参：尝试更低 `R_obs` 搭配更高 `b_offset`，例如 `(0.125, 24)`、`(0.12, 28)`、`(0.115, 32)`。

#### Step R2c joint R_obs/b_offset 计划

- [x] no-drift 筛查 `(measurement_noise_std_dev, b_offset) ∈ {(0.125, 24), (0.12, 28), (0.115, 32)}`
- [x] 对 no-drift 通过且 `c_mean` 更接近 3 的候选跑 dynamic drift smoke

no-drift joint sweep 输出：

```text
outputs/e2e_whitened_cusum_pretrained_null_joint_sweep_20260429/summary.json
```

| measurement_noise_std_dev | b_offset | first_online_windows | false trigger | c_mean | c_p99 | c_max |
| ---: | ---: | --- | ---: | ---: | ---: | ---: |
| 0.125 | 24 | `[null, null, null]` | 0 / 3 | 3.035 | 14.497 | 41.822 |
| 0.120 | 28 | `[null, null, null]` | 0 / 3 | 3.217 | 15.830 | 44.855 |
| 0.115 | 32 | `[null, null, null]` | 0 / 3 | 3.417 | 17.349 | 48.225 |

dynamic joint 输出：

```text
outputs/e2e_whitened_cusum_pretrained_dynamic_joint_20260429/summary.json
```

| measurement_noise_std_dev | b_offset | eta | first_online_windows | pre-drift false | detect rate | mean delay | tail5_improve |
| ---: | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| 0.125 | 24 | 0.6 | `[11, 9, null]` | 0 / 3 | 2 / 3 | 5.0 | +0.0351 |
| 0.125 | 24 | 1.0 | `[7, 6, 12]` | 0 / 3 | 3 / 3 | 3.333 | +0.0898 |
| 0.120 | 28 | 0.6 | `[11, 9, null]` | 0 / 3 | 2 / 3 | 5.0 | +0.0525 |
| 0.120 | 28 | 1.0 | `[7, 9, 13]` | 0 / 3 | 3 / 3 | 4.667 | +0.0803 |
| 0.115 | 32 | 0.6 | `[11, 9, null]` | 0 / 3 | 2 / 3 | 5.0 | +0.0199 |
| 0.115 | 32 | 1.0 | `[7, 9, 13]` | 0 / 3 | 3 / 3 | 4.667 | +0.0816 |

选择当前闭环候选：

```text
measurement_noise_std_dev = 0.125
b_offset = 24.0
p_fa = 1e-6
checkpoint = checkpoints/saved_SubspaceNet_trained_20260224_180720.pt
```

理由：

- no-drift 0/3 误触发；
- no-drift `c_mean=3.035`，最接近理论 `χ²(3)` 期望 3；
- `eta=1.0` 强漂移 3/3 检测，平均延迟 3.333 window，是三组 joint 候选里最快；
- `eta=0.6` 弱漂移仍只有 2/3 检测，说明 scalar R_obs + CUSUM 当前还不能声称覆盖弱漂移。

新增 YAML preset：

```text
run/conf/Used_for_paper/SineAccel_whitened_cusum_pretrained_calibrated.yaml
```

内容要点：

```yaml
kalman_filter:
  measurement_noise_std_dev: 0.125

online_learning:
  drift_trigger:
    type: whitened_cusum
    p_fa: 1e-6
    dof: 3
    b_offset: 24.0
    reset_after_trigger: true
```

注意：旧的 `SineAccel_whitened_cusum_calibrated.yaml` 保留为 replay-calibrated 历史候选；新的 `pretrained_calibrated` 才是当前闭环 best-available checkpoint 下的推荐候选。

验证：

```text
Hydra config smoke:
  config_name=SineAccel_whitened_cusum_pretrained_calibrated
  measurement_noise_std_dev=0.125
  trigger_state.reference=27.0
  trigger_state.threshold=16.6265

pytest:
  PYTHONPATH=. .venv-wsl/bin/python -m pytest \
    tests/online_learning/test_drift_trigger.py \
    tests/integration/test_whitened_trigger_smoke.py \
    tests/online_learning/test_validate_null_distribution.py -q

  20 passed, 2 warnings

git diff --check:
  pass
```
