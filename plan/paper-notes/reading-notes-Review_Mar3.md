# 三阶段精读笔记：A Constrained Weighted Least-Squares Algorithm for Hybrid 1-D Space-Angle and TDOA Localization

> **作者**: Abdulellah Almalki, Huaping Liu (Oregon State University); Yanbin Zou (Shantou University)
> **Zotero Key**: 692JF3SH
> **类型**: Journal Article (under review)
> **关键词**: Localization, 1-D Space Angle (SA), TDOA, CWLS, Lagrange Multiplier

---

## 📜 研究核心

> Tips: 做了什么，解决了什么问题，创新点和不足？

### ⚙️ 内容

- **目的**: 解决利用多个线性阵列提供的一维空间角 (1-D SA) 与时间差到达 (TDOA) 混合测量进行三维目标定位的问题。线性阵列相比平面阵列具有更小的空间占用，适合空间受限场景。
- **研究问题**: 如何在混合 1-D SA 与 TDOA 测量下，高效且精确地估计三维目标位置，同时逼近 Cramér–Rao 下界 (CRLB)？
- **研究对象**: 混合 1-D SA + TDOA 三维定位问题中的约束加权最小二乘 (CWLS) 求解框架。
- **贡献声明**:
  1. 提出了一种 CWLS 算法，联合利用 1-D SA 和 TDOA 的互补几何结构进行混合定位。
  2. 该算法在低噪声条件下逼近 CRLB-Hybrid 下界，证明了估计效率。

**定位综述**: 目标三维定位问题 → 现有 1-D SA 方法 (SDP, WLS) 存在次优性或强噪声退化 → 现有混合 SA+TDOA 方法 ([18] WLS-Hu 忽略约束, [19] TSWLS-Xing 线性近似退化) → 提出 CWLS 框架，通过 Lagrange 乘子法精确施加辅助变量与目标位置的几何约束，实现高精度且计算高效的定位。

### 💡 创新点

1. **显式约束施加**: 不同于 WLS-Hu [18] 忽略辅助变量 $\|u - s_1\|$ 与目标位置 $u$ 之间的内在约束，本文将此约束显式纳入 CWLS 目标函数。这确保了估计的几何一致性，直接改善了估计精度。与 [18] 的无约束 WLS 及 [19] 的两阶段近似方法不同。
2. **Lagrange 乘子高效求解**: 将 CWLS 问题转化为通过 Lagrange 乘子法求解的 6 阶多项式方程，避免了 SDP 方法的高计算复杂度，同时保持接近最优的估计性能。
3. **融合互补几何**: 1-D SA 定义锥面，TDOA 定义双曲面，两者联合提供更强的几何约束，在角度或时间噪声增大时仍保持鲁棒性。

### 🧩 不足

**作者自认**:
- 文中未明确讨论局限性（典型的短会议/信件风格论文）。

**审稿人视角批评**:

1. **[Major] 传感器数量与几何依赖**: 仅使用 $M=4$ 传感器，未讨论传感器数量、几何布局对性能的影响。阵列几何退化（共面、共线）时算法表现未知。
2. **[Major] 缺少实测数据验证**: 仅有仿真结果，无真实环境实验（如室内 UWB 定位、无人机场景）。实际环境中的多径、NLOS 影响未考虑。
3. **[Moderate] 噪声模型简单**: 假设 SA 噪声 i.i.d. 高斯、TDOA 噪声高斯且协方差矩阵已知（对角 1、非对角 0.5），未讨论非高斯噪声或未知协方差的鲁棒性。
4. **[Moderate] 迭代次数与收敛性未讨论**: Algorithm 1 仅执行两次迭代（初始 + 一次细化），未分析收敛性或多次迭代的效果。
5. **[Minor] 与 SDP 方法缺少直接对比**: 引言中讨论了多种 SDP 方法 [7][9][10]，但实验仅对比 WLS-Hu [18] 和 TSWLS-Xing [19]，缺少与 SDP 方法的计算复杂度和精度对比。
6. **[Minor] 计算复杂度分析缺失**: 未给出算法的 FLOPs 或运行时间分析。

---

## 🔁 研究内容

### 💧 数据

- **数据类型**: 纯仿真数据（蒙特卡洛实验）
- **传感器配置**: $M = 4$ 传感器，位置见 Table I（空间分布在约 $\pm 500$m 范围内，高度 50-200m）
- **目标区域**: $[-2000, 2000]\text{m} \times [-2000, 2000]\text{m} \times [0, 1000]\text{m}$
- **实验参数**:
  - 10 个随机目标位置，每个位置 1000 次蒙特卡洛实现
  - SA 噪声: $e_i \sim \mathcal{N}(0, \sigma_a^2)$，协方差 $Q_e = \sigma_a^2 I_M$
  - TDOA 噪声: $n_{i1} \sim \mathcal{N}(0, \sigma_d^2 R)$，$R$ 为 $(M-1) \times (M-1)$ 矩阵（对角 1，非对角 0.5）
  - 图 2: 固定 $\sigma_a = 0.5°$，$\sigma_d$ 从 $-20$ 到 $10$ dBm 变化
  - 图 3: 固定 $\sigma_d = 1$m，$\sigma_a$ 从 $-40$ 到 $-10$ dBrad 变化
- **评价指标**: RMSE (Root Mean Square Error)，与 CRLB 对比

🔍 **批评**: 10 个目标位置样本偏少，无法充分展示算法在不同几何构型下的稳定性。缺少高 SNR 区域的 bias 分析。传感器数量固定为 4，未探索可扩展性。

### 👩🏻‍💻 方法

#### (a) 问题建模 → 核心洞察

本文处理的是**混合 1-D SA + TDOA 三维定位**问题。

**信号模型**: 三维空间中有 $M$ 个传感器（线性阵列），位置已知为 $s_i = [x_i, y_i, z_i]^T$，目标位置未知 $u = [x, y, z]^T$。每个传感器的归一化姿态向量为：

$$g_i = [\cos\theta_i \cos\phi_i, \sin\theta_i \cos\phi_i, \sin\phi_i]^T \quad \text{Eq.(1)}$$

每个传感器测量一维空间角（1-D SA），定义一个以传感器为顶点、姿态向量为轴的锥面：

$$\psi_i = \psi_i^0 + e_i \quad \text{Eq.(2)}$$

其中真实角度 $\psi_i^0 = \cos^{-1}\left(\frac{g_i^T(u - s_i)}{\|u - s_i\|}\right)$（Eq.(3)），$e_i$ 为测量噪声。

**核心困难**: 1-D SA 测量方程（Eq.(4)-(6)）和 TDOA 测量方程（Eq.(7)-(10)）都是非线性的，直接联合求解困难。现有方法要么忽略辅助变量约束（[18]），要么依赖两阶段线性近似（[19]），导致次优解。

**核心洞察（Key Insight）**: 引入辅助变量 $\|u - s_1\|$（目标到参考传感器的距离），将非线性 SA 和 TDOA 方程通过代数变换统一为关于扩展变量 $y = [(u-s_1)^T, \|u-s_1\|]^T$ 的伪线性方程组（Eq.(13a)-(13b)）。关键在于**显式施加约束** $y^T P y = 0$（即 $\|u-s_1\|^2 = (u-s_1)^T(u-s_1)$），确保辅助变量与位置变量的几何一致性。

#### (b) 方法概览（逻辑流）

因为上述洞察，作者提出了 CWLS + Lagrange 乘子法框架：

**Pipeline**: 输入（SA 测量 $\psi_i$, TDOA 测量 $r_{i1}$, 传感器参数） → **Step 1**: 线性化（SA 方程取 cos + Taylor 展开 Eq.(5)-(6)；TDOA 方程平方消元 Eq.(8)-(10)） → **Step 2**: 联合合并为矩阵方程 $Ay = b + D\epsilon$（Eq.(14)） → **Step 3**: 构建 CWLS 问题（目标函数 + 约束，Eq.(16)） → **Step 4**: Lagrange 乘子法求解，转化为 6 阶多项式（Eq.(24)-(26)） → **Step 5**: 求多项式实数根，选择最小代价函数的解 → **Step 6**: 迭代细化加权矩阵 $W$ → 输出 $u^*$

**信息流**: SA 测量通过 Eq.(6) 贡献位置-距离关系，TDOA 测量通过 Eq.(10) 贡献另一组位置-距离关系。两者堆叠为统一线性系统，加权矩阵 $W$ 编码测量精度信息。

#### (c) 核心技术贡献（深入分析）

**1. 非线性方程线性化**

- SA 方程线性化: 对 Eq.(3) 两边取 cos，利用 $\cos(\psi_i^0) = \cos(\psi_i - e_i) \approx \cos\psi_i + e_i \sin\psi_i$（Eq.(5)，小角度近似），得到 Eq.(6)。
- TDOA 方程线性化: 将 Eq.(8) 两边平方，忽略噪声二阶项，得到 Eq.(9)-(10)。
- 为什么这样设计: 平方操作消除了 $\|u - s_i\|$ 的非线性，代价是引入了 $\|u - s_1\|$ 作为额外未知量，但通过约束 $y^T P y = 0$ 恢复这一信息。

**2. CWLS 问题构建（Eq.(16)）**

$$\arg\min_y (Ay - b)^T W (Ay - b) \quad \text{s.t.} \quad y^T P y = 0$$

- $P = \text{diag}([1,1,1,-1])$ 编码约束 $\|(u-s_1)\|^2 - \|u-s_1\|^2 = 0$（Eq.(17b)）
- 加权矩阵 $W = (E[D\epsilon\epsilon^T D^T])^{-1}$（Eq.(17a)），与真实目标位置相关

**3. Lagrange 乘子法求解**

- Lagrangian: $L(y, \lambda) = (Ay-b)^T W (Ay-b) + \lambda y^T P y$（Eq.(18)）
- 对 $y$ 求导置零: $y = (A^T W A + \lambda P)^{-1} A^T W b$（Eq.(19)）
- 代入约束 Eq.(16b)，利用同时对角化（Eq.(21)）简化为 6 阶多项式（Eq.(24)-(26)）
- 为什么 6 阶: $A^T W A$（$4 \times 4$）与 $P$ 同时对角化产生 4 个特征值，约束方程展开后为 6 次多项式

**4. 迭代细化**

- 初始 $W$ 使用 $W = \text{diag}(Q_d^{-1}, Q_e^{-1})$（Eq.(28)，忽略 $D$ 矩阵中的位置依赖项）
- 第一轮估计后，用 $u^*$ 更新 $D$ 矩阵，重新计算 $W$，再执行一次求解

#### (d) 设计选择与约束

- **为什么选 Lagrange 乘子而非 SDP**: Lagrange 乘子产生精确解（在多项式根中选择），而 SDP 是松弛近似。计算上，求解 6 阶多项式远快于 SDP。
- **两次迭代**: 仅执行初始化 + 一次细化，未进行完整收敛迭代，可能是为简化和避免收敛性讨论。
- **参考传感器选择**: 默认第一个传感器为 TDOA 参考，未讨论参考传感器选择对性能的影响。

#### (e) 变体

无显式变体。Algorithm 1 为唯一版本。

🔍 **批评**:
- 线性化中的 Taylor 展开（Eq.(5)）和平方操作忽略二阶噪声项，在高噪声下会引入模型失配。这解释了图 3 中高 $\sigma_a$ 时偏离 CRLB 的现象。
- 约束 $y^T P y = 0$ 要求精确满足 $\|u-s_1\|$ 关系，但线性化后的 $y$ 只是近似满足，约束强度可能在高噪声下过强导致偏差。
- 缺少对 $A^T W A$ 条件数的讨论——当传感器几何退化时，矩阵可能病态。

### 🔬 实验

**Setup**:
- 4 传感器（Table I），10 个随机目标位置，每个 1000 次蒙特卡洛
- 性能指标: RMSE (m)
- Baseline:
  - **CRLB-Hybrid**: 混合 SA+TDOA 的 Cramér–Rao 下界（理论最优）
  - **CRLB-1-D AOA**: 仅用 1-D SA 的 CRLB
  - **CRLB-TDOA**: 仅用 TDOA 的 CRLB
  - **WLS-Hu [18]**: 无约束 WLS 方法，忽略辅助变量与位置的约束
  - **TSWLS-Xing [19]**: 两阶段 WLS，先无约束 WLS 再 Taylor 展开细化

**定量结果**:

- **图 2**（固定 $\sigma_a = 0.5°$，$\sigma_d$ 变化）:
  - Proposed 在 $\sigma_d \leq 5$ dBm 时紧贴 CRLB-Hybrid
  - WLS-Hu 在所有噪声水平下 RMSE 明显偏高（约 2-5 倍）
  - TSWLS-Xing 在低噪声时接近 CRLB 但性能不如 Proposed

- **图 3**（固定 $\sigma_d = 1$m，$\sigma_a$ 变化）:
  - TSWLS-Xing 在 $\sigma_a = -20$ dBrad 时开始偏离 CRLB
  - Proposed 在 $\sigma_a \leq -15$ dBrad 时保持近最优性能
  - Proposed 比 TSWLS-Xing 多保持约 5dB 的最优区间

**消融**: 无正式消融实验。通过 CRLB-1-D AOA 和 CRLB-TDOA 单模态下界间接说明混合测量的增益。

🔍 **批评**:
- 仅两组实验（固定一个噪声变另一个），缺少同时变化两个噪声的二维性能曲面。
- 未给出 bias 分析或估计量的有限样本统计特性。
- 10 个目标位置过少，RMSE 的方差/置信区间未报告。
- 缺少计算时间对比，无法评估 Lagrange 乘子法相对 SDP 的实际加速比。
- Baseline 选择不够全面——缺少 [7][9][10] 中的 SDP 方法。

### 📜 结论

- **主要发现**: CWLS 算法通过显式约束和 Lagrange 乘子法高效求解混合 1-D SA + TDOA 定位问题，在低噪声条件下逼近 CRLB-Hybrid，一致优于 WLS-Hu 和 TSWLS-Xing。
- **作者提出的未来工作**: 未明确提出。
- **评估**: 结论由仿真结果支持，但"逼近 CRLB"的声明缺乏理论证明（如渐近无偏性证明）。在中高噪声区域（$\sigma_a > -15$ dBrad），算法偏离 CRLB，文中未充分讨论该限制。

---

## 🤔 个人总结

> Tips: 你对哪些方面有疑问，觉得可以怎么改进？

### 🙋‍♀️ 关键记录

1. **CWLS + Lagrange 乘子范式**: 将非线性定位问题通过引入辅助变量转为伪线性系统 + 二次约束，再通过 Lagrange 乘子转化为多项式求根。这是定位领域的经典技巧（参见 Chan-Ho 方法 [3]），可迁移至其他非线性估计问题。
2. **同时对角化技巧**: Eq.(21) 中 $A^T W A$ 和 $P$ 的同时对角化将复杂的矩阵求逆简化为标量运算，是将约束优化转为多项式的关键步骤。
3. **1-D SA 的锥面几何**: 每个 SA 测量定义一个以传感器为顶点的锥面（非平面角），多个锥面的交集确定目标三维位置。这与传统 2-D AOA（射线交叉）有本质几何差异。
4. **迭代加权细化**: 初始 $W$ 忽略位置依赖项，一次估计后用粗估计更新权重。这种"plug-in"策略在 WLS 类算法中普遍使用。
5. **6 阶多项式**: 4 维扩展变量 + 1 个二次约束 → 6 阶多项式。多项式阶数由问题维度决定，实数根筛选 + 代价函数选择为标准流程。

### 📌 待解决

1. **线性化误差的理论界**: Eq.(5) 的 Taylor 展开和 Eq.(9) 的忽略二阶项在什么噪声水平下失效？需要建立近似误差与 CRLB 偏离的关系。
2. **阵列几何对性能的影响**: 当传感器接近共面或共线时，$A^T W A$ 的条件数如何变化？是否存在可观测性条件？
3. **NLOS 和异常值鲁棒性**: 实际场景中 SA 和 TDOA 测量可能受 NLOS 污染，当前高斯噪声模型无法处理。
4. **与深度学习方法的对比**: 是否可以用神经网络直接学习 SA+TDOA → 位置的映射？与模型驱动方法的精度/泛化对比值得探讨。
5. **多次迭代 vs. 两次迭代**: 是否多次迭代能在中噪声区域进一步提升？收敛性证明缺失。

### 💭 思考启发

- **与我的研究的联系**: 作为 DOA 估计研究者，1-D SA 本质上是 DOA 的锥角表示。本文的 CWLS 框架可应用于 DOA+TDOA 混合定位场景。SubspaceNet 项目中若结合 TDOA 信息，可考虑类似的约束优化策略。
- **延伸想法**:
  - 将 CWLS 约束嵌入深度学习损失函数（model-based deep learning），类似于 SubspaceNet 中将子空间约束嵌入网络。
  - 1-D SA 的锥面几何可推广到近场定位（球面波模型），锥面变为更复杂的曲面。
  - 将 Lagrange 乘子法推广到动态场景（目标跟踪），每步利用上一步估计初始化。
- **后续研究方向**: 混合异构测量（SA + TDOA + RSS）的统一约束优化框架，理论分析渐近效率条件。

---

## 📎 附录 1: 公式目录

### Eq.(1) 传感器姿态向量

$$g_i = [\cos\theta_i \cos\phi_i, \sin\theta_i \cos\phi_i, \sin\phi_i]^T$$

| 符号 | 含义 | 维度/范围 |
|------|------|-----------|
| $g_i$ | 第 $i$ 个传感器的归一化姿态向量 | $\mathbb{R}^3$, $\|g_i\| = 1$ |
| $\theta_i$ | 方位角 | $[-\pi, \pi]$ |
| $\phi_i$ | 俯仰角 | $[-\pi/2, \pi/2]$ |

💡 球坐标系下单位方向向量的标准参数化。

### Eq.(2) 1-D SA 测量模型

$$\psi_i = \psi_i^0 + e_i$$

| 符号 | 含义 | 维度/范围 |
|------|------|-----------|
| $\psi_i$ | 第 $i$ 个传感器的 SA 测量值 | $[0, \pi]$ |
| $\psi_i^0$ | 真实空间角 | $[0, \pi]$ |
| $e_i$ | 测量噪声 | $e_i \sim \mathcal{N}(0, \sigma_a^2)$ |

💡 加性高斯噪声模型，SA 定义为传感器姿态向量与目标方向的夹角。

### Eq.(3) 真实空间角定义

$$\psi_i^0 = \cos^{-1}\left(\frac{g_i^T(u - s_i)}{\|u - s_i\|}\right)$$

| 符号 | 含义 | 维度/范围 |
|------|------|-----------|
| $u$ | 目标位置 | $\mathbb{R}^3$ |
| $s_i$ | 第 $i$ 个传感器位置 | $\mathbb{R}^3$ |

💡 SA 为姿态向量与目标-传感器连线的夹角（锥面定义）。
← 由锥面几何直接定义。

### Eq.(4) 线性化 SA 方程（无噪声）

$$\cos\psi_i^0 \|u - s_i\| = g_i^T(u - s_i)$$

💡 Eq.(3) 取 cos 后乘以距离，消除反余弦非线性。
← 由 Eq.(3) 两边取 cos 推导。

### Eq.(5) 噪声 Taylor 展开

$$\cos\psi_i^0 = \cos(\psi_i - e_i) \approx \cos\psi_i + e_i \sin\psi_i$$

💡 一阶 Taylor 展开处理噪声项，有效性依赖 $e_i$ 足够小。
← 对 $\cos(x - \delta) \approx \cos x + \delta \sin x$ 展开。

### Eq.(6) 线性化 SA 方程（含噪声）

$$\cos\psi_i \|u - s_i\| + e_i \sin\psi_i \|u - s_i\| = g_i^T(u - s_i)$$

💡 将 Eq.(5) 代入 Eq.(4)，得到含噪声的伪线性 SA 方程。
← 由 Eq.(4) + Eq.(5) 代入推导。

### Eq.(7) TDOA 测量模型

$$r_{i1} = \|u - s_i\| - \|u - s_1\| + n_{i1}, \quad i = 2, \ldots, M$$

| 符号 | 含义 | 维度/范围 |
|------|------|-----------|
| $r_{i1}$ | 距离差测量（第 $i$ 个与第 1 个传感器） | $\mathbb{R}$ |
| $n_{i1}$ | TDOA 噪声 | $n \sim \mathcal{N}(0, \sigma_d^2 R)$ |

💡 标准 TDOA 模型，第 1 个传感器为参考。
← 基本 TDOA 定义。

### Eq.(8) TDOA 等式变换

$$r_{i1} + \|u - s_1\| = \|u - s_1 + s_1 - s_i\| + n_{i1}$$

💡 将 $\|u - s_i\|$ 替换为通过参考传感器表达。
← 由 Eq.(7) 移项。

### Eq.(9) 平方展开

$$r_{i1}^2 + 2r_{i1}\|u - s_1\| \approx 2(u - s_1)^T(s_1 - s_i) + \|s_1 - s_i\|^2 + 2\|u - s_i\|n_{i1}$$

💡 平方消除绝对值/范数的非线性，忽略 $n_{i1}^2$。
← 由 Eq.(8) 两边平方展开，忽略二阶噪声项。

### Eq.(10) 整理后的 TDOA 伪线性方程

$$(u - s_1)^T(s_i - s_1) + r_{i1}\|u - s_1\| \approx 0.5(\|s_1 - s_i\|^2 - r_{i1}^2) + \|u - s_i\|n_{i1}$$

💡 标准形式，左侧为关于 $y$ 的线性函数。
← 由 Eq.(9) 整理。

### Eq.(11) SA 与 TDOA 联合方程

$$\cos\psi_i(r_{i1} + \|u - s_1\| - n_{i1}) + e_i \sin\psi_i \|u - s_i\| = g_i^T(u - s_1 + s_1 - s_i)$$

💡 将 TDOA 距离关系代入 SA 方程。
← 由 Eq.(7) 代入 Eq.(6)。

### Eq.(12) 整理后的联合 SA-TDOA 方程

$$g_i^T(u - s_1) - \cos\psi_i\|u - s_1\| = g_i^T(s_i - s_1) + r_{i1}\cos\psi_i - n_{i1}\cos\psi_i + e_i\sin\psi_i\|u - s_i\|$$

💡 关于 $y = [(u-s_1)^T, \|u-s_1\|]^T$ 的伪线性形式。
← 由 Eq.(11) 整理。

### Eq.(13a) 堆叠 TDOA 方程

$$(u - s_1)^T(s_i - s_1) + r_{i1}\|u - s_1\| \approx 0.5(\|s_1 - s_i\|^2 - r_{i1}^2) + \|u - s_i\|n_{i1}, \quad i = 2, \ldots, M$$

### Eq.(13b) 堆叠 SA 方程

$$(u - s_1)^T g_i - \cos\psi_i\|u - s_1\| = g_i^T(s_i - s_1) + r_{i1}\cos\psi_i - n_{i1}\cos\psi_i + e_i\sin\psi_i\|u - s_i\|, \quad i = 1, \ldots, M$$

💡 $r_{11} = 0$, $n_{11} = 0$（$i=1$ 时退化为纯 SA 方程）。

### Eq.(14) 矩阵方程

$$Ay = b + D\epsilon$$

| 符号 | 含义 | 维度/范围 |
|------|------|-----------|
| $A$ | 系数矩阵 | $\mathbb{R}^{(2M-1) \times 4}$ |
| $y$ | 扩展位置变量 $[(u-s_1)^T, \|u-s_1\|]^T$ | $\mathbb{R}^4$ |
| $b$ | 已知常数向量 | $\mathbb{R}^{2M-1}$ |
| $D$ | 噪声加权矩阵 | $\mathbb{R}^{(2M-1) \times (2M-1)}$ |
| $\epsilon$ | 联合噪声向量 $[n^T, e^T]^T$ | $\mathbb{R}^{2M-1}$ |

💡 将 Eq.(13a)-(13b) 统一为标准伪线性形式。

### Eq.(15a)-(15l) 矩阵元素定义

详见正文 Eq.(15)，定义了 $A$, $b$, $D$ 的每个分块。关键:
- $A$ 的前 $M-1$ 行来自 TDOA（Eq.(15b)），后 $M$ 行来自 SA（Eq.(15d)）
- $D$ 包含 $D_{11}$（TDOA 距离加权）、$D_{21}$（SA-TDOA 交叉）、$D_{22}$（SA 距离-角度加权）

### Eq.(16) CWLS 问题

$$\arg\min_y (Ay - b)^T W (Ay - b) \quad \text{s.t.} \quad y^T P y = 0$$

💡 核心优化问题：加权最小二乘 + 二次等式约束。

### Eq.(17a) 加权矩阵

$$W = (E[D\epsilon\epsilon^T D^T])^{-1}$$

### Eq.(17b) 约束矩阵

$$P = \text{diag}([1, 1, 1, -1])$$

💡 $y^T P y = 0$ 等价于 $\|u - s_1\|^2 = (u-s_1)^T(u-s_1)$。

### Eq.(18) Lagrangian

$$L(y, \lambda) = (Ay - b)^T W (Ay - b) + \lambda y^T P y$$

💡 引入 Lagrange 乘子 $\lambda$ 处理等式约束。

### Eq.(19) CWLS 解

$$y = (A^T W A + \lambda P)^{-1} A^T W b$$

💡 对 $y$ 求导置零得到的闭式解（$\lambda$ 待定）。
← 由 Eq.(18) 对 $y$ 求导 $= 0$。

### Eq.(20) 约束方程

$$b^T W A (A^T W A + \lambda P)^{-1} P (A^T W A + \lambda P)^{-1} A^T W b = 0$$

💡 将 Eq.(19) 代入约束 $y^T P y = 0$。

### Eq.(21a)-(21b) 同时对角化

$$X^T A^T W A X = I_4, \quad X^T P X = \Lambda = \text{diag}([\gamma_1, \gamma_2, \gamma_3, \gamma_4])$$

💡 因为 $A^T W A$ 正定、$P$ 对称，可同时对角化。
← 线性代数标准结论。

### Eq.(22) 简化的逆矩阵

$$(A^T W A + \lambda P)^{-1} = X(I_4 + \lambda\Lambda)^{-1} X^T$$

← 由 Eq.(21) 直接推导。

### Eq.(23) 简化的约束方程

$$b^T W A X (I_4 + \lambda\Lambda)^{-1} \Lambda (I_4 + \lambda\Lambda)^{-1} X^T A^T W b = 0$$

← 由 Eq.(22) 代入 Eq.(20)。

### Eq.(24) 标量形式

$$\sum_{i=1}^{4} \frac{\gamma_i a_i^2}{(1 + \lambda\gamma_i)^2} = 0$$

其中 $a = X^T A^T W b$。

💡 将矩阵约束转化为标量和。

### Eq.(25) 展开形式

$$\sum_{i=1}^{4} \gamma_i a_i^2 \prod_{j \neq i} (1 + \lambda\gamma_j)^2 = 0$$

💡 通分后的多项式形式。

### Eq.(26) 6 阶多项式

$$\sum_{i=1}^{4} c_i \prod_{j \neq i} (1 + 2\lambda\gamma_j + \lambda^2\gamma_j^2) = 0$$

其中 $c_i = \gamma_i a_i^2$。

💡 展开后为 $\lambda$ 的 6 阶多项式，系数详见 [20]。

### Eq.(27) 代价函数

$$c_f^{(l)} = (A\hat{y}_l - b)^T W (A\hat{y}_l - b)$$

💡 用于在多个实数根中选择最优解。

### Eq.(28) 初始加权矩阵近似

$$W = \begin{bmatrix} Q_d^{-1} & 0 \\ 0 & Q_e^{-1} \end{bmatrix}$$

💡 忽略 $D$ 矩阵中的位置依赖项，作为初始迭代的粗略近似。

---

### 公式依赖图

```
Eq.(1) [传感器姿态向量]
  → Eq.(3) [真实空间角定义]  (代入姿态向量)
    → Eq.(4) [线性化 SA（无噪声）]  (两边取 cos)

Eq.(2) [SA 测量模型]
  → Eq.(5) [噪声 Taylor 展开]  (一阶展开)
    → Eq.(6) [线性化 SA（含噪声）]  (Eq.(4) + Eq.(5))

Eq.(7) [TDOA 测量模型]
  → Eq.(8) [TDOA 等式变换]  (移项)
    → Eq.(9) [平方展开]  (两边平方)
      → Eq.(10) [TDOA 伪线性方程]  (整理)

Eq.(6) + Eq.(7) → Eq.(11) [联合方程]  (TDOA 代入 SA)
  → Eq.(12) [整理后的联合方程]
    → Eq.(13a)-(13b) [堆叠方程]
      → Eq.(14) [矩阵方程 Ay = b + Dε]
        → Eq.(15) [矩阵元素定义]

Eq.(14) → Eq.(16) [CWLS 问题]  (加权 + 约束)
  → Eq.(17) [W 和 P 定义]
    → Eq.(18) [Lagrangian]  (引入乘子)
      → Eq.(19) [CWLS 解]  (对 y 求导)
        → Eq.(20) [约束方程]  (代入约束)
          → Eq.(21) [同时对角化]
            → Eq.(22) [简化逆]
              → Eq.(23)-(24)-(25)-(26) [6 阶多项式]
                → Eq.(27) [代价函数选最优根]

Eq.(28) [初始 W 近似] → Algorithm 1 迭代
```

---

## 📝 附录 2: 引言参考

### (a) 技术全景（先行技术综述）

| 技术/方法 | 核心思想 | 优势 | 局限 | 代表文献 |
|-----------|---------|------|------|----------|
| TOA | 信号到达时间测距 | 直接距离测量 | 需要时钟同步 | [1] Guvenc & Chong 2009, [2] Sun et al. 2022 |
| TDOA | 信号到达时间差 | 无需时钟同步 | 需要参考传感器 | [3] Chan & Ho 1994, [4] Su et al. 2018 |
| AOA (2-D) | 平面阵列测方位角+俯仰角 | 射线交叉几何简单 | 需要平面阵列（空间占用大） | [5] Wang & Ho 2015, [6] Zou et al. 2023 |
| 1-D SA (SDP) | 线性阵列测单一空间角，SDP 松弛求解 | 阵列紧凑 | 次优解，计算量大 | [7] Zou et al. 2020, [9] Sun et al. 2022, [10] Alamdari et al. 2022 |
| 1-D SA (IWLS) | 迭代 WLS 求解 1-D SA 定位 | 计算轻量 | 仅用 SA 信息 | [11] Zou et al. 2025 |
| Hybrid AOA+TDOA | 联合角度和时延 | 互补几何，更高精度 | 现有方法次优 | [12]-[17] |
| Hybrid 1-D SA+TDOA (WLS-Hu) | 无约束 WLS | 简单 | 忽略辅助变量约束，次优 | [18] Hu et al. 2021 |
| Hybrid 1-D SA+TDOA (TSWLS-Xing) | 两阶段 WLS + Taylor 细化 | 闭式解 | 强噪声下线性近似退化 | [19] Xing et al. 2024 |

**范式演进**: 单模态测量 (TOA/TDOA/AOA) → 混合测量 (AOA+TDOA) → 紧凑阵列混合测量 (1-D SA+TDOA)

### (b) 缺口分析

- **核心缺口**: 现有 1-D SA + TDOA 方法存在估计次优性:
  - [18] WLS-Hu 忽略了辅助变量 $\|u-s_1\|$ 与目标位置的内在约束
  - [19] TSWLS-Xing 依赖线性近似，强噪声下退化

- **关键引文**:
  > "their formulation neglects the intrinsic constraint between the redundant variable and the actual target position, which results in suboptimal estimation performance" (关于 [18])
  > "Its performance can degrade under strong noise due to reliance on linear approximations." (关于 [19])

- **缺口性质**: 实践性（估计精度和噪声鲁棒性不足）+ 理论性（未充分利用几何约束）。

### (c) 方法定位

- **定位策略**: "To overcome these limitations of existing works on this topic, this paper proposes an enhanced hybrid localization framework based on constrained weighted least squares (CWLS)."
- **相对优势**:
  - 对比无约束 WLS [18]: 显式施加几何约束
  - 对比两阶段 TSWLS [19]: 联合优化（非分步近似）
  - 对比 SDP 方法 [7][9][10]: 通过 Lagrange 乘子法精确求解（非松弛近似），计算更高效

### (d) 引言逻辑流（叙事结构）

```
1. [背景与重要性]: 精确定位在跟踪、导航、监控中至关重要 → 各种无线定位技术 (TOA, TDOA, AOA)
2. [先行技术类别 1]: 1-D SA 定位 → 线性阵列的空间优势 → 锥面几何 → SDP/IWLS 方法
3. [先行技术类别 2]: 混合 AOA+TDOA → 广泛研究但多用 2-D 角度
4. [缺口]: 1-D SA+TDOA 混合定位关注不足 → [18] 忽略约束 → [19] 线性近似退化
5. [提案]: 提出 CWLS 框架，显式约束 + Lagrange 乘子高效求解
6. [贡献预览]: (1) CWLS 算法利用互补几何, (2) 逼近 CRLB
7. [文章组织]: Section II (SA 模型) → III (CWLS 推导) → IV (仿真) → V (结论)
```

### (e) 参考文献图谱

| 叙事角色 | 参考文献 | 引用方式 |
|----------|----------|----------|
| 问题重要性/应用 | — | 背景陈述（无具体引用） |
| 经典测量技术 | [1] Guvenc 2009 (TOA), [3] Chan 1994 (TDOA), [5] Wang 2015 (AOA) | 奠基技术介绍 |
| 1-D SA 定位方法 | [7] Zou 2020 (首次 SDP), [9] Sun 2022 (SDP+Taylor), [10] Alamdari 2022 (凸优化), [11] Zou 2025 (IWLS) | 先行技术（先赞后批） |
| 混合 AOA+TDOA | [12]-[17] (批量引用) | 相关工作分类 |
| 最近竞争方法（Gap 识别） | [18] Hu 2021 (WLS-Hu), [19] Xing 2024 (TSWLS-Xing) | 直接比较对象，识别缺口 |
| 技术基础 | [20] Zou 2024 (3-D AOA CWLS), [21] Zou 2020 (TDOA 协方差模型) | 本文方法的基础构建块 |

🔍 **批评**: 引言叙事合理但略显模板化。对 [18] 和 [19] 的批评准确但较为简短。未讨论深度学习在定位中的应用（近年来研究热点），也未引用 CRB 推导的相关文献。先行技术综述以 Zou 课题组自身工作为主（[7][11][20][21]），可能存在引用偏见。

---

*笔记生成日期: 2026-03-03*
*Zotero Item Key: 692JF3SH*
