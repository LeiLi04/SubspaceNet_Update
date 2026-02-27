# [5] SPICE: A Sparse Covariance-Based Estimation Method for Array Processing

**Authors:** Stoica, Petre; Babu, Prabhu; Li, Jian
**Journal:** IEEE Transactions on Signal Processing, 2011
**Zotero Key:** BS5RJTZZ

---

## 📜 研究核心

### ⚙️ 内容

- **目的**：解决现有稀疏 DOA 估计方法（如 $\ell_1$-SVD [3]）的三个关键问题：(1) 噪声场景下 $\ell_1$ 动机不清晰；(2) 正则化超参数 $\epsilon$ 难以选择；(3) SOCP 求解器在大规模问题上太慢。
- **研究问题**：能否从协方差拟合的统计视角出发，推导出一种无需超参数、自然处理噪声、且具有全局收敛性的稀疏估计方法？
- **研究对象**：SPICE（SParse Iterative Covariance-based Estimation）——基于加权协方差矩阵拟合准则的迭代稀疏估计算法。
- **贡献**：
  1. 从协方差拟合准则（统计上有坚实基础）推导出 SPICE 估计准则，天然处理噪声；
  2. SPICE 完全无需用户选择超参数（无 $\lambda$, 无 $\epsilon$），完全数据自适应；
  3. 推导出简洁的乘性迭代更新公式（Eq.(33)-(34)），计算高效；
  4. 证明 SPICE 的 SOCP 等价形式是经典 $\ell_1$-范数问题的加权扩展，揭示了协方差拟合与 $\ell_1$ 稀疏估计的深层联系；
  5. 证明全局收敛性。

**定位段**：$\ell_1$-范数稀疏估计方法（如 [3]）在阵列处理中表现出色但存在超参数选择困难 → SPICE 从加权协方差矩阵拟合出发，推导出一种统计上有坚实基础、无需超参数、全局收敛的迭代算法，同时揭示了与 $\ell_1$-范数最小化的数学联系。

### 💡 创新点

1. **协方差拟合的统计基础**（Eq.(13)）：SPICE 准则 $f(\mathbf{p}) = \|\hat{R}^{-1/2}(R(\mathbf{p}) - \hat{R})\hat{R}^{-1/2}\|_F^2$ 最小化加权协方差拟合误差，其中权重由样本协方差矩阵自然确定。在适当条件下，该准则的估计量是渐近有效的。与 $\ell_1$-SVD 的启发式正则化根本不同——这里的稀疏性是从统计准则中自然涌现的。
2. **无超参数设计**：通过将优化准则分解为增广形式（Eq.(22)）并交替最小化，SPICE 自动确定信号功率和噪声功率的估计，无需用户指定任何参数。经典方法 [3] 需要选择 $\epsilon$（关键影响性能），SPICE 完全消除了这一困难。
3. **乘性迭代的封闭形式**（Eq.(33)-(34)）：SPICE 的核心更新公式极其简洁：$p_k^{(i+1)} = p_k^{(i)} \cdot |\mathbf{a}^H(\bar{\theta}_k) \hat{R}_i^{-1} \hat{\mathbf{r}}|$，其中 $\hat{R}_i$ 由当前功率估计构建。无需求解大规模优化问题，每步仅需矩阵-向量乘法。
4. **与 $\ell_1$-范数的理论联系**（Section IV, Eq.(48)）：SPICE 的 SOCP 等价形式为加权 $\ell_1$ 问题，其中权重 $w_k \propto 1/p_k$ 随估计自适应——功率越小的网格点权重越大（更强的稀疏惩罚）。这提供了对 $\ell_1$ 方法的全新统计解释。

### 🧩 不足

**作者承认的不足**：
- 信号空间不相关假设（Eq.(9)）不总成立，但实验表明 SPICE 对此假设具有鲁棒性（参考 [7]）。

**评审批评**：
1. **空间不相关假设**（中等/moderate）：协方差模型 $R = \sum p_k \mathbf{a}_k \mathbf{a}_k^H + \text{diag}(\sigma^2)$ 假设源不相关。虽然实验显示鲁棒性，但缺乏对强相干场景的严格理论分析。
2. **收敛速度未量化**（minor）：证明了全局收敛但未给出收敛速率（线性/超线性？）。实际中迭代次数如何依赖问题参数？
3. **与 IAA 的关系**（minor）：SPICE 与 IAA（Iterative Adaptive Approach [12]）在更新公式上类似，但论文未充分讨论两者的本质区别和联系。
4. **仅考虑窄带场景**：未扩展到宽带或近场。

---

## 🔁 研究内容

### 💧 数据

- **仿真设置**：
  - **ULA**：$M = 10$ 个传感器，半波长间距，$T = 100$ 快拍
  - **NULA**：非均匀线阵，$M = 10$（具体间距见 Fig.1），$T = 200$ 快拍
  - DOA 搜索网格：$[-90°, 90°)$，步长 0.1°，$N = 1800$
  - 恒模信号（通信场景），相位均匀随机
- **测试条件**：
  - 3 个固定源：10°, 40°, 55°
  - 不相关源 vs 相干源（10° 和 55° 相干）
  - SNR：-20 dB 到 30 dB
  - 2 个移动源跟踪场景
- 🔍 **批评**：数据设置全面（涵盖 ULA/NULA、不相关/相干、固定/移动），但缺少超大阵列（$M > 100$）或 2D DOA 估计的测试。

### 👩🏻‍💻 方法

#### (a) 问题建模 → 核心洞察

从阵列信号的半参数模型出发（Eq.(1)）：

$$\mathbf{x}(t) = \sum_{k=1}^{N} \mathbf{a}(\bar{\theta}_k) s_k(t) + \mathbf{w}(t), \quad t = 1, \ldots, T$$

假设信号和噪声互不相关（Eq.(9)），协方差矩阵为（Eq.(10)）：

$$R = \sum_{k=1}^{N} p_k \mathbf{a}(\bar{\theta}_k) \mathbf{a}^H(\bar{\theta}_k) + \text{diag}(\sigma_1^2, \ldots, \sigma_M^2)$$

其中 $p_k = E[|s_k(t)|^2]$ 是第 $k$ 个网格点的信号功率。

**核心难点**：需要从 $T$ 个快拍估计 $N + M$ 个参数（$N$ 个功率 $p_k$ + $M$ 个噪声方差 $\sigma_m^2$），其中大部分 $p_k = 0$（稀疏性）。经典 $\ell_1$ 方法需要手动选择正则化参数。

**核心洞察**：采用加权协方差矩阵拟合准则（Eq.(13)）：

$$f(\mathbf{p}, \boldsymbol{\sigma}^2) = \|\hat{R}^{-1/2}(R(\mathbf{p}) - \hat{R})\hat{R}^{-1/2}\|_F^2$$

通过数学化简（Eq.(16)-(18)），该准则等价于最小化：

$$g(\mathbf{p}) = \text{tr}(R^{-1}\hat{R}) + \text{tr}(R\hat{R}^{-1}) \quad \text{Eq.(18)}$$

**关键发现**：对 $g(\mathbf{p})$ 关于 $\mathbf{p}$ 的约束最小化（Eq.(20)：$\min_{\mathbf{p} \geq 0} g(\mathbf{p})$ s.t. $\text{tr}(R(\mathbf{p})\hat{R}^{-1}) = M$）可以通过引入增广变量（Eq.(22)）转化为交替最小化问题，得到封闭形式的更新公式。且该约束是**加权 $\ell_1$-范数型**（Eq.(20)-(21)的线性约束），自然诱导稀疏解。

#### (b) 方法概览（逻辑流）

因为加权协方差拟合准则自然产生加权 $\ell_1$ 约束（核心洞察），SPICE 无需手动设定正则化参数即可获得稀疏解。

**流水线**：

1. **数据采集** → 计算样本协方差 $\hat{R} = \frac{1}{T}\sum_t \mathbf{x}(t)\mathbf{x}^H(t)$
2. **初始化** → 用 periodogram 估计初始功率 $p_k^{(0)} = |\mathbf{a}^H(\bar{\theta}_k)\hat{R}\mathbf{a}(\bar{\theta}_k)|$（Eq.(35)）
3. **SPICE 迭代** → 交替更新：
   - 固定 $\mathbf{p}$，更新辅助变量 $\mathbf{q}$（封闭形式，Eq.(23)）
   - 固定 $\mathbf{q}$，更新 $\mathbf{p}$ 和 $\boldsymbol{\sigma}^2$（封闭形式，Eq.(31)）
   - 合并得到乘性更新（Eq.(33)-(34)）
4. **收敛判断** → 功率估计变化小于阈值
5. **DOA 提取** → $p_k > \text{threshold}$ 的网格点对应源方向

#### (c) 核心技术贡献（深入）

**协方差拟合准则推导**：

起点是加权最小二乘准则（Eq.(13)）：
$$f = \|\hat{R}^{-1/2}(R - \hat{R})\hat{R}^{-1/2}\|_F^2$$

展开并利用 $\text{tr}(\hat{R}^{-1}\hat{R}) = M$（Eq.(16)），化简为（Eq.(18)）：
$$g(\mathbf{p}) = \text{tr}(R^{-1}\hat{R}) + \text{tr}(R\hat{R}^{-1})$$

此函数关于 $\mathbf{p}$ 非凸，但其约束版本（Eq.(20)）可通过 SDP 求解。

**增广函数与交替最小化**（Eq.(22)）：

$$h(\mathbf{p}, \mathbf{q}) = \sum_{k=1}^{N+M} \left(\frac{q_k}{p_k} + p_k r_k\right)$$

其中 $r_k = \mathbf{a}^H_k \hat{R}^{-1} \mathbf{a}_k$（对信号项）或相应的噪声项。

- 固定 $\mathbf{p}$，对 $\mathbf{q}$ 最小化：$q_k^* = p_k |\mathbf{a}^H_k R^{-1}(\mathbf{p}) \hat{\mathbf{r}}_k|$（Eq.(23)）
- 固定 $\mathbf{q}$，对 $\mathbf{p}$ 最小化：$p_k^* = \sqrt{q_k / r_k}$（Eq.(31)）

合并两步得到**SPICE 乘性更新**（Eq.(33)-(34)）：

$$p_k^{(i+1)} = p_k^{(i)} \sqrt{\frac{|\mathbf{a}^H(\bar{\theta}_k) R_i^{-1} \hat{\mathbf{r}}_k|}{r_k^{(i)}}} \quad \text{Eq.(33)}$$

$$\sigma_m^{2,(i+1)} = \sigma_m^{2,(i)} \sqrt{\frac{|\mathbf{e}_m^H R_i^{-1} \hat{\mathbf{r}}_m|}{[\hat{R}^{-1}]_{mm}}} \quad \text{Eq.(34)}$$

**全局收敛性**：由于 SPICE 单调递减凸目标函数，且交替最小化的极限点是全局解（由 [10] 的一般分析保证）。

**SOCP 等价形式**（Eq.(48)）：

SPICE 等价于求解：

$$\min_{\boldsymbol{\gamma}} \sum_k w_k |\gamma_k| \quad \text{s.t. } \tilde{\mathbf{Y}} = \tilde{\mathbf{B}} \boldsymbol{\gamma}$$

其中 $w_k \propto 1/p_k$ 是自适应权重，$\tilde{\mathbf{B}}$ 和 $\tilde{\mathbf{Y}}$ 是考虑噪声的增广矩阵（比 [3] 的 Eq.(6) 多了 $M$ 行噪声项）。

**与经典 $\ell_1$ 的三个关键区别**：
- (i) 加权 $\ell_1$：权重 $w_k$ 由数据自适应确定，小功率源获得更大惩罚
- (ii) 增广矩阵：额外行自然编码噪声信息
- (iii) 等式约束替代不等式约束：无需选择 $\epsilon$

#### (d) 设计选择与约束

- **为何用协方差拟合而非数据域 $\ell_1$**：协方差拟合有明确的统计理论支持（渐近效率），且自然处理噪声。数据域 $\ell_1$ 的动机在噪声情况下不如协方差拟合清晰。
- **乘性更新 vs SOCP 求解**：乘性更新通常更快（作者的经验），但 SOCP 形式对理解 SPICE 与 $\ell_1$ 的联系至关重要。
- **等噪声功率约束**（Eq.(36)）：$\sigma_1^2 = \cdots = \sigma_M^2 = \sigma^2$ 时的简化版本（SPICE+），使用不同的更新公式（Eq.(44)-(46)），在不相关源场景下更准确。
- **初始化**：用 periodogram 估计（Eq.(35)），保证初始解为密集（非稀疏），利于全局收敛。

#### (e) 变体

- **SPICE**（Eq.(33)-(34)）：一般情况，各传感器噪声功率不同
- **SPICE+**（Eq.(44)-(46)）：等噪声功率约束，不相关源场景更优
- **单快拍版本**：使用 Eq.(15)/(19) 替代 Eq.(13)

🔍 **批评**：协方差模型假设源不相关（$E[s_k s_j^*] = 0, k \neq j$），这限制了理论基础。虽然实验表明对相干源鲁棒，但缺乏严格的理论解释——为什么一个基于不相关假设的准则在相干场景下仍然有效？

### 🔬 实验

- **实验设置**：
  - **ULA 固定源**：$M = 10$, $T = 100$, 3 源（10°, 40°, 55°），$N = 1800$
  - **NULA 移动源**：$M = 10$, 100 快拍滑动窗口, 2 源交叉轨迹
  - 比较方法：PER, IAA, MUSIC, SPICE, SPICE+
  - 1000 次 Monte Carlo

- **主要结果**：
  - **Fig.2(a)（不相关源 RMSE vs SNR）**：
    - PER 在所有 SNR 下偏差大（由网格限制）
    - IAA 在 SNR ≥ 0 dB 时有竞争力
    - MUSIC 在不相关源时 SNR ≥ 0 dB 准确
    - **SPICE/SPICE+ 阈值 SNR 比 IAA 和 MUSIC 低约 10 dB**
    - SPICE+ 在不相关源时比 SPICE 略优
  - **Fig.2(b)（相干源 RMSE vs SNR）**：
    - MUSIC 完全失效（如预期）
    - IAA 性能大幅退化
    - **SPICE 在相干源时优于 SPICE+**
    - SPICE 在 SNR ≥ -5 dB 时提供合理估计
  - **Fig.3（移动源跟踪）**：
    - PER 跟踪失败（Fig.3(a)）
    - SPICE 和 SPICE+ 成功跟踪两条交叉轨迹（Fig.3(b)-(d)）
    - 5 次迭代即可获得良好结果；20 次无显著改善
  - **Fig.4（正弦轨迹跟踪）**：SPICE+ 准确跟踪正弦 DOA 轨迹

- **基线方法**：
  - **PER (Periodogram)**（Eq.(35)）：$p_k = |\mathbf{a}^H_k \hat{R} \mathbf{a}_k|$，有显著偏差
  - **IAA** [12]：迭代自适应方法，类似 SPICE 但无统计基础
  - **MUSIC**：需要已知 $D$，对相干源失效
  - **SPICE vs SPICE+**：前者对相干源更鲁棒，后者对不相关源更精确

- 🔍 **批评**：实验全面，有 Monte Carlo 统计分析和 RMSE 曲线。但缺少与 CRB 的直接比较。跟踪实验中源模型较简单（恒速/正弦），未测试突变场景。

### 📜 结论

- SPICE 具有三个独特优势：(1) 坚实的统计基础（协方差拟合）；(2) 无需用户选择超参数；(3) 全局收敛性。
- SPICE/SPICE+ 在不相关和相干源场景下均表现出色，阈值 SNR 比 IAA/MUSIC 低约 10 dB。
- 乘性更新公式简洁高效，适合实际应用。
- SOCP 等价形式揭示了 SPICE 与加权 $\ell_1$ 的深层联系，为理解稀疏阵列处理提供了新的视角。

🔍 **评估**：结论由理论推导和充分实验支持。无超参数这一特性对实际应用价值巨大。全局收敛性由理论保证，是相比 FOCUSS 等方法的重要优势。

---

## 🤔 个人总结

### 🙋‍♀️ 关键记录

1. **协方差拟合 = 加权 $\ell_1$**：这个等价关系是论文最深刻的发现。它说明 $\ell_1$ 稀疏估计不仅是优化启发式，而是有统计意义的——协方差拟合准则下的最优解自然是稀疏的。
2. **自适应权重 $w_k \propto 1/p_k$ 的直觉**：功率越小的网格点（可能不是源）获得越大的 $\ell_1$ 惩罚，更强地被压到零。功率大的点（可能是源）惩罚小，保留其估计。这正是 iteratively reweighted $\ell_1$ (IRL1) 的思想，但 SPICE 从统计理论自然推导出来。
3. **乘性更新的优雅**：$p_k^{(i+1)} = p_k^{(i)} \cdot f(p^{(i)})$ 的形式保证 $p_k \geq 0$（无需额外约束），且零功率保持为零（一旦某个 $p_k$ 变为零，它永远为零）。这类似于 EM 算法的乘性更新。
4. **SPICE vs SPICE+**：不相关源用 SPICE+（更精确），相干源用 SPICE（更鲁棒）。实际中可能不知道源相关性，可以两者都试或默认用 SPICE。
5. **增广矩阵的物理意义**：SPICE 的 SOCP 形式中，$\tilde{\mathbf{B}}$ 和 $\tilde{\mathbf{Y}}$ 比 $\ell_1$-SVD 多了 $M$ 行——这些行对应噪声项，物理上意味着"同时估计噪声"。

### 📌 待解决

1. **相干源的理论解释**：为何基于不相关假设的 SPICE 在相干场景下仍然有效？需要阅读 [7] 的详细分析。
2. **收敛速度**：乘性更新的收敛速率？是否可以加速（如 Anderson acceleration）？
3. **与 IAA 的精确关系**：IAA 的更新公式与 SPICE 类似，但 IAA 无统计基础。两者是否在某种极限下等价？
4. **大规模扩展**：$N > 10000$ 时 $R^{-1}$ 计算成本？可以用 Woodbury 公式或共轭梯度法避免显式求逆。

### 💭 思考启发

- **与我的研究的联系**：SPICE 是 SubspaceNet 论文中的另一个重要 baseline。SPICE 的优势（无超参数、对相干源鲁棒）正是深度学习方法也追求的目标。SubspaceNet 能否学习一个比 SPICE 更快收敛的"更新规则"？
- **deep unfolding 方向**：将 SPICE 的乘性迭代（Eq.(33)-(34)）展开为可学习的神经网络层，每层学习 $R^{-1}$ 的近似和权重修正。这可能比直接展开 ISTA/FISTA 更有阵列处理的先验。
- **SPICE + 深度学习的混合**：用 SPICE 提供粗估计（快速、鲁棒），然后用神经网络精调（提高分辨率、处理模型失配）。
- **从 SPICE 到 gridless**：SPICE 仍受网格限制。将其推广到连续域（atomic norm）是自然的延伸。

---

## 📎 附录：公式目录

- **Eq.(1)** [阵列信号模型]
  $$\mathbf{x}(t) = \sum_{k=1}^{N} \mathbf{a}(\bar{\theta}_k) s_k(t) + \mathbf{w}(t)$$
  | 符号 | 含义 | 维度/范围 |
  |------|------|-----------|
  | $N$ | 网格点数 | $N \gg M$ |
  | $T$ | 快拍数 | 正整数 |
  💡 半参数模型：用密集网格覆盖所有可能的源方向。

- **Eq.(7)-(9)** [统计假设]
  $$E[\mathbf{w}(t)] = 0, \quad E[\mathbf{w}(t)\mathbf{w}^H(t)] = \text{diag}(\sigma_1^2, \ldots, \sigma_M^2)$$
  $$E[s_k(t) s_j^*(t)] = 0 \text{ for } k \neq j$$
  💡 零均值噪声、空间不相关噪声、源间不相关。

- **Eq.(10)** [协方差矩阵模型]
  $$R = \sum_{k=1}^{N} p_k \mathbf{a}_k \mathbf{a}_k^H + \text{diag}(\sigma_1^2, \ldots, \sigma_M^2)$$
  | 符号 | 含义 | 维度/范围 |
  |------|------|-----------|
  | $p_k$ | 第 $k$ 个网格点信号功率 | $p_k \geq 0$ |
  💡 协方差由稀疏功率向量参数化。
  ← 由 Eq.(1) 和 Eq.(7)-(9)

- **Eq.(13)** [SPICE 协方差拟合准则]
  $$f(\mathbf{p}) = \|\hat{R}^{-1/2}(R(\mathbf{p}) - \hat{R})\hat{R}^{-1/2}\|_F^2$$
  💡 加权 Frobenius 范数。渐近有效估计量。

- **Eq.(15)** [单快拍准则]
  $$f_1(\mathbf{p}) = \text{tr}(R^{-1}(\mathbf{p}) \hat{R})$$
  💡 当 $T < M$ 时使用。

- **Eq.(18)** [等价目标]
  $$g(\mathbf{p}) = \text{tr}(R^{-1}\hat{R}) + \text{tr}(R\hat{R}^{-1})$$
  💡 化简后的准则。
  ← 由 Eq.(13) 展开

- **Eq.(20)** [约束优化]
  $$\min_{\mathbf{p} \geq 0} \text{tr}(R^{-1}\hat{R}) \quad \text{s.t. } \text{tr}(R\hat{R}^{-1}) = M$$
  💡 约束是加权 $\ell_1$ 型，自然诱导稀疏。

- **Eq.(22)** [增广目标]
  $$h(\mathbf{p}, \mathbf{q}) = \sum_k \left(\frac{q_k}{p_k} + p_k r_k\right)$$
  💡 引入辅助变量实现交替最小化。

- **Eq.(23)** [$\mathbf{q}$ 更新]
  $$q_k = p_k \cdot |\mathbf{a}_k^H R^{-1} \hat{\mathbf{r}}_k|$$
  ← 固定 $\mathbf{p}$

- **Eq.(31)** [$\mathbf{p}$ 更新]
  $$p_k = \sqrt{q_k / r_k}$$
  ← 固定 $\mathbf{q}$

- **Eq.(33)** [SPICE 信号功率更新（核心）]
  $$p_k^{(i+1)} = p_k^{(i)} \sqrt{\frac{|\mathbf{a}_k^H R_i^{-1} \hat{\mathbf{r}}_k|}{r_k^{(i)}}}$$
  💡 乘性更新，保证非负。SPICE 的核心。
  ← 合并 Eq.(23) 和 Eq.(31)

- **Eq.(34)** [SPICE 噪声功率更新]
  $$\sigma_m^{2,(i+1)} = \sigma_m^{2,(i)} \sqrt{\frac{|\mathbf{e}_m^H R_i^{-1} \hat{\mathbf{r}}_m|}{[\hat{R}^{-1}]_{mm}}}$$
  💡 与信号功率更新对称。

- **Eq.(35)** [Periodogram 初始化]
  $$p_k^{(0)} = |\mathbf{a}_k^H \hat{R} \mathbf{a}_k|$$
  💡 密集初始化利于全局收敛。

- **Eq.(44)-(46)** [SPICE+ 更新]
  等噪声约束版本。

- **Eq.(48)** [SOCP 等价形式]
  $$\min_{\boldsymbol{\gamma}} \sum_k w_k |\gamma_k| \quad \text{s.t. } \tilde{\mathbf{Y}} = \tilde{\mathbf{B}} \boldsymbol{\gamma}$$
  💡 SPICE = 加权 $\ell_1$ + 噪声增广。

- **Eq.(54)** [ULA 导向向量]
  $$\mathbf{a}(\theta) = [1, e^{j\pi\sin\theta}, \ldots, e^{j(M-1)\pi\sin\theta}]^T$$

**公式依赖图**：
```
Eq.(1) [阵列信号模型]
  → Eq.(7)-(9) [统计假设]
    → Eq.(10) [协方差模型 R]
      → Eq.(13) [协方差拟合准则 f]
        → Eq.(18) [等价目标 g]
          → Eq.(20) [约束优化]  (加权 ℓ1 约束)
            → Eq.(22) [增广目标 h]
              → Eq.(23) [q 更新]
              → Eq.(31) [p 更新]
                → Eq.(33)-(34) [SPICE 更新]
            → Eq.(48) [SOCP 等价]
      → Eq.(15) [单快拍准则]
Eq.(36) → Eq.(44)-(46) [SPICE+]
Eq.(35) [初始化]
```

---

---

# 论文间交叉引用

| 主题 | [3] MUSIC (L8TETDDM) | [4] $\ell_1$-SVD (9BWEP2W8) | [5] SPICE (BS5RJTZZ) |
|------|------|------|------|
| **核心范式** | 子空间方法 | 稀疏重建 | 协方差拟合 |
| **优化类型** | 特征分解 + 谱搜索 | 凸优化 (SOCP) | 交替最小化 (乘性迭代) |
| **超参数** | 需要 $D$ | 需要 $D$ + $\lambda$ | **无超参数** |
| **相干源** | ❌ 失效 | ✅ 鲁棒 | ✅ 鲁棒 |
| **计算复杂度** | 低 ($O(M^3)$) | 高 (SOCP) | 中 (矩阵逆) |
| **统计基础** | 渐近无偏 | 无严格理论 | 渐近有效 |
| **关系** | baseline | 引用 [3] 为 MUSIC | 引用 [4] 为 $\ell_1$-SVD |

**发展脉络**：MUSIC (1986) 开创子空间范式 → $\ell_1$-SVD (2005) 引入稀疏重建范式解决 MUSIC 的相干源问题 → SPICE (2011) 从统计理论统一协方差拟合与 $\ell_1$ 稀疏，消除超参数选择困难。
