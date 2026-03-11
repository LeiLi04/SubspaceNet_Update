# 三阶段精读笔记：Analysis of Out-of-Band Emissions in Sub-Band Full Duplex 5G-NTN operating at FR1

> **作者**: Taha Ahmed Khan, Eva Lagunas (Interdisciplinary Centre for Security, Reliability and Trust (SnT), University of Luxembourg)
> **Zotero Item Key**: 692JF3SH (父条目 Review_Mar3), 附件 Key: KJXKHRIV
> **类型**: Conference Paper (under review)
> **关键词**: Sub-band Full Duplex (SBFD), Non-Terrestrial Networks (NTN), 5G-Advanced, TDD, FR1, Out-of-Band Emissions

---

## 📜 研究核心

> Tips: 做了什么，解决了什么问题，创新点和不足？

### ⚙️ 内容

- **目的**: 研究 Sub-band Full Duplex (SBFD) 在 LEO 卫星 5G-NTN 系统中的可行性，重点分析带外 (OOB) 辐射引起的系统内干扰。传统 TDD 在 NTN 中因长传播延迟（2-13ms）导致保护间隔过长，频谱效率极低。
- **研究问题**: 在 LEO-based 5G-NTN 中采用 SBFD 时，上行与下行间的 OOB 辐射泄漏对系统性能的影响如何？保护带 (Guard Band) 的大小如何平衡干扰抑制与吞吐量？
- **研究对象**: 双 LEO 卫星（600km 轨道）、双波束场景下 SBFD 系统的 SINR 和可达速率。
- **贡献声明**:
  1. 首次分析 SBFD 在 5G-NTN 中的 OOB 辐射影响（此前仅有地面场景研究）。
  2. 建立了基于球面地球几何、3GPP TR 38.811 天线模型和 NR SEM/BEM 的系统级仿真框架。
  3. 通过仿真揭示：下行为噪声受限（OOB 泄漏远低于噪声底），保护带主要影响可用下行带宽；上行由跨波束 UL→UL 干扰和天线滚降主导，对保护带不敏感。

**定位综述**: 5G NTN 需在 FR1 TDD 频段运行 → TDD 在 NTN 中因长延迟导致保护间隔消耗 60-95% 帧资源 → SBFD（频域分离 UL/DL）可规避时域同步问题 → 但 SBFD 引入新的频域干扰（OOB 泄漏、跨波束 CLI） → 本文首次量化这些干扰在 NTN 场景中的影响。

### 💡 创新点

1. **首次将 SBFD 应用于 NTN 分析**: 现有 SBFD 研究 [8][9] 均针对地面网络。本文将 SBFD 延伸到 LEO 卫星场景，考虑了球面地球几何、长距离传播损耗和卫星天线波束模型，这些是地面场景不涉及的因素。
2. **完整的干扰分类与建模**: 系统性地分类了 4 种跨波束干扰（UL→DL, UL→UL, DL→DL, DL→UL），分别建模 UE 频谱发射掩模 (SEM) 和卫星带外发射限值 (BEM)，并基于合理假设简化分析（忽略 $I_{DL \to UL}$ 和自干扰）。
3. **揭示关键权衡**: 保护带增大 → 不改善 DL SINR（已是噪声受限） → 但降低 DL 吞吐量（压缩可用带宽）。这一非直觉结论对 SBFD-NTN 的频谱规划有实际意义。

### 🧩 不足

**作者自认**:
- 假设自干扰已被充分消除（未建模 SI 残留），future work 建议联合优化保护带、带宽分配和干扰协调。

**审稿人视角批评**:

1. **[Major] 场景过于简化**: 仅 2 颗卫星、2 个波束、1 个 UE。实际 LEO 星座可能有数十颗卫星和密集波束，干扰环境远更复杂。缺少对多波束/多卫星的可扩展性讨论。
2. **[Major] 忽略关键干扰源**: 自干扰 (SI) 假设完全消除，但在卫星平台上实现 149 dB SI 消除极具挑战性。$I_{DL \to UL}$ 直接置零（Eq.(19)）缺乏充分论证。
3. **[Moderate] 无对比基准方法**: 仅展示 SBFD 的绝对性能，未与传统 TDD（不同 TDD pattern）或 FDD 的吞吐量做定量对比。"SBFD presents a viable pathway" 的结论缺乏对比支撑。
4. **[Moderate] UE-UE 耦合损耗模型粗糙**: $L_{UE-UE}$ 仅用自由空间路径损耗 (FSPL)，未考虑 UE 间近距离的多径效应或地面反射。文中未给出 UE-UE 距离的具体取值。
5. **[Minor] 天线模型局限**: 使用简单 Bessel reflector 模型，实际 LEO 卫星可能使用相控阵或多馈源天线，旁瓣特性差异大。
6. **[Minor] 缺少 CDF/统计分析**: 所有结果仅展示确定性曲线（单一 UE 位置扫描），无随机 UE 分布下的 CDF 或 Monte Carlo 分析。

---

## 🔁 研究内容

### 💧 数据

- **数据类型**: 纯仿真（MATLAB 系统级仿真）
- **场景参数**:
  - 2 颗 LEO 卫星，高度 $h_{sat} = 600$ km
  - 载波频率 $f_c = 3.55$ GHz（FR1 mid-band, n77-n78）
  - 总带宽 $B_{tot} = 100$ MHz
  - 每波束 UL 带宽 $B_{UL} = 10$ MHz（固定）
  - 保护带 $GB \in \{0, 5, 10, 15\}$ MHz
  - 每波束 DL 带宽 $B_{DL}(GB) = (B_{tot} - 2B_{UL} - 2GB)/2$
  - UE 从波束中心 ($\theta_{DL} = 0°$) 移向波束边缘 ($\theta_{DL} \approx 3°$)
- **链路预算参数**（Table III）:
  - DL EIRPSD: $-26$ dBW/Hz
  - UE UL EIRP: $23$ dBm
  - UE 天线增益: $0$ dBi（全向）
  - UE 噪声系数: $7$ dB
  - 卫星噪声系数: $1$ dB
  - 天线模型: TR 38.811 Bessel reflector ($a = 10\lambda$)
- **评价指标**: DL/UL SINR, 干噪比 I/N, 可达吞吐量 (Mbit/s)

🔍 **批评**: 单 UE 确定性扫描，无随机化。UE-UE 距离（决定 UL→DL 泄漏的关键参数）未明确给定或参数化。缺少不同轨道高度或不同波束间距的敏感性分析。

### 👩🏻‍💻 方法

#### (a) 问题建模 → 核心洞察

**背景问题**: 传统 TDD 在 NTN 中因往返时延 (RTT) 导致保护间隔占帧资源 60-95%（Fig. 1），频谱效率极低。

**核心洞察**: SBFD 将时域双工问题转化为频域双工——在同一时隙内用不同子带同时传输 UL 和 DL（Fig. 2）。这消除了对长保护间隔的需求，但引入频域跨链路干扰 (CLI)。本文通过系统级链路预算分析，量化这些 CLI 在 NTN 双波束场景下的影响。

**信号模型起点**: 球面地球几何下的斜距计算（Eq.(1)），自由空间路径损耗（Eq.(2)），以及 3GPP TR 38.811 Bessel reflector 天线增益模型（Eq.(5)-(6)）。

#### (b) 方法概览（逻辑流）

**Pipeline**: 场景定义（2 LEO 卫星 + 1 UE） → 频率规划（SBFD 子带分配，Eq.(3)-(4)） → 下行信号模型（Eq.(7)-(9)） → 上行信号模型（Eq.(10)-(11)） → 干扰建模（4 种 CLI 分量，Eq.(12)-(19)） → SINR 计算（Eq.(20)-(21)） → 可达吞吐量（Eq.(22)-(23)） → 参数扫描分析

**信息流**:
- DL 路径: 卫星 1 → FSPL → UE 接收，干扰来自 UE2 的 UL OOB 泄漏 ($I_{UL \to DL}$) 和卫星 2 的 DL OOB 泄漏 ($I_{DL \to DL}$)
- UL 路径: UE → FSPL → 卫星 1 接收，干扰来自卫星 2 波束内 UE 的同频 UL 信号 ($I_{UL \to UL}$)，忽略 $I_{DL \to UL}$

#### (c) 核心技术贡献（深入分析）

**1. SBFD 频率规划模型**

DL 带宽随保护带变化:
$$B_{DL}(GB) = \frac{B_{tot} - 2B_{UL} - 2GB}{2} \quad \text{Eq.(3)}$$

两个 DL 子带间的频率间隔:
$$\Delta f_{DL2 \to DL1} = 2GB + 2B_{UL} \quad \text{Eq.(4)}$$

UL 子带位于载波中央，DL 子带位于两侧（Fig. 4）。Beam 1 的 UL 靠近 Beam 2 的 DL，最大化同波束 UL-DL 频率间隔。

**2. 天线增益模型（Bessel reflector）**

$$G_{norm}(\theta) = \begin{cases} 1, & \theta = 0 \\ 4\left|\frac{J_1(ka\sin\theta)}{ka\sin\theta}\right|^2, & \theta > 0 \end{cases} \quad \text{Eq.(5)}$$

其中 $k = 2\pi/\lambda$, $a = 10\lambda$。该模型捕获了随离轴角增大的快速增益衰减，直接决定跨波束干扰水平。

**3. UL→DL 干扰建模（OOB 泄漏）**

基于 3GPP TS 38.101-1 UE SEM:
- 将 SEM 限值转为功率谱密度: $PSD_{UE}(\Delta f)$（Eq.(12)）
- 在保护带到 DL 带宽范围内积分泄漏功率:

$$P_{UL \to DL}^{(OOB)} = \int_{GB}^{GB+B_{DL}} 10^{PSD_{UE}(\Delta f)/10} d\Delta f \quad \text{Eq.(13)}$$

- 通过 UE-UE FSPL 耦合得到接收干扰（Eq.(14)）。

这是整篇论文最关键的干扰分量——但仿真结果表明在该场景下远低于噪声底。

**4. DL→DL 干扰建模（Out-of-block 发射）**

基于 ECC Report 281 卫星 BEM:
- 将 BEM 限值转为 PSD: $PSD_{sat}(\Delta f)$（Eq.(16)）
- 在 $\Delta f_{DL2 \to DL1}$ 范围内积分（Eq.(17)）
- 考虑卫星发射增益差和传播损耗（Eq.(18)）

**5. UL→UL 干扰（同频跨波束）**

$$I_{UL \to UL} = EIRP_{UL} + G_{sat,rx}(\phi_{UL}) - L_{fs}(f, d_{UL,cross}) \quad \text{Eq.(15)}$$

同频干扰，无 OOB 衰减，仅靠天线空间隔离和路径损耗。

**6. DL→UL 干扰（忽略）**

假设卫星天线指向地球，卫星间耦合极低: $I_{DL \to UL} \approx 0$（Eq.(19)）。

#### (d) 设计选择与约束

- **为什么忽略自干扰**: 卫星 SI 消除是已知技术问题 [10]，本文聚焦于较少研究的 CLI。合理但限制了结论的完整性。
- **FSPL 作为最坏情况**: 不考虑多径等衰减效应，FSPL 给出干扰功率的上界。
- **仅 FR1 mid-band**: 不涉及 FR2 (mmWave)，因为 n77/n78 是全球 5G 部署最广泛的频段。
- **UE 全向天线**: 简化假设，实际 UE 可能有天线方向性。

#### (e) 变体

无显式变体。保护带 $GB \in \{0, 5, 10, 15\}$ MHz 作为参数扫描。

🔍 **批评**:
- 方法本质上是标准链路预算分析，技术深度有限——无闭式分析、无优化、无新算法。
- OOB 泄漏建模依赖 3GPP SEM/BEM 标准值，未考虑实际发射机非线性特性的差异。
- 缺少对 UE-UE 距离的参数化分析，这是决定 UL→DL 干扰是否显著的关键参数。文中结论"UL→DL 远低于噪声底"可能在 UE 近距场景下不成立（文末简要提及但未量化）。

### 🔬 实验

**Setup**:
- MATLAB 系统级仿真
- 参数见 Table III
- UE 从波束中心扫到边缘（$\theta_{DL}: 0° \to 3°$）
- 4 种 GB 配置: 0, 5, 10, 15 MHz

**定量结果**:

- **图 6（DL SINR vs $\theta_{DL}$）**:
  - 所有 GB 值的 DL SINR 曲线完全重叠
  - 波束中心 SINR ≈ 24-25 dB，波束边缘 ≈ 4-5 dB
  - 结论: DL 为噪声受限，保护带对 DL SINR 无影响

- **图 7（DL I/N）**:
  - UL→DL 和 DL→DL 的 I/N 均远低于 0 dB（< -20 dB）
  - 验证了噪声受限结论

- **图 8（UL SINR vs $\theta_{DL}$）**:
  - UL SNR（无干扰基线）与 UL SINR（含 UL→UL）曲线差距很小
  - UL→UL 干扰在大部分 $\theta_{DL}$ 范围内低于或接近噪声底
  - 边缘退化主要由天线滚降驱动
  - UL 曲线对 GB 不敏感（因 UL→UL 为同频干扰）

- **Table IV（吞吐量汇总）**:

  | GB (MHz) | DL 中心 (Mbit/s) | DL 边缘 | UL 中心 | UL 边缘 |
  |----------|------------------|---------|---------|---------|
  | 无干扰 | 163.08 | 11.62 | 5.87 | 0.101 |
  | 0 | 163.08 | 11.62 | 5.84 | 0.101 |
  | 5 | 142.69 | 10.17 | 5.84 | 0.101 |
  | 10 | 122.31 | 8.71 | 5.84 | 0.101 |
  | 15 | 101.92 | 7.26 | 5.84 | 0.101 |

  - DL 吞吐量随 GB 增大线性下降（带宽减小 Eq.(3)）
  - UL 吞吐量几乎不受 GB 影响
  - GB=15 MHz 时 DL 吞吐量比 GB=0 降低约 37%

🔍 **批评**:
- 结论"OOB 泄漏远低于噪声底"过度依赖特定场景假设（2 卫星、UE 距离远）。
- 缺少 UE-UE 距离的参数化分析（文末仅定性提及 worst-case proximity 可能改变结论）。
- 无与传统 TDD 的吞吐量对比——无法量化 SBFD 的实际增益。
- 无误差分析或 Monte Carlo 随机化。
- 图 6 中所有曲线重叠本质上说明实验设置未充分测试系统的极限。

### 📜 结论

- **主要发现**: 在双波束 LEO-NTN 场景下，DL 为噪声受限（UL→DL 和 DL→DL OOB 泄漏远低于噪声底），保护带不改善 DL SINR 但降低 DL 吞吐量；UL 由 UL→UL 跨波束干扰和天线滚降主导，与保护带无关。
- **作者提出的未来工作**: 联合优化保护带选择和干扰协调；考虑 worst-case UE proximity 场景。
- **评估**: 结论在给定假设下由仿真支持，但结论的普适性存疑——改变 UE-UE 距离、增加卫星数量、考虑 SI 残留可能根本改变结论。"SBFD presents a viable pathway" 的声明在缺乏与 TDD/FDD 对比的情况下支撑不足。

---

## 🤔 个人总结

> Tips: 你对哪些方面有疑问，觉得可以怎么改进？

### 🙋‍♀️ 关键记录

1. **SBFD 核心思想**: 将时域双工转为频域双工，在同一时隙内用不同子带同时进行 UL 和 DL。消除长保护间隔需求，但引入 OOB 泄漏和跨链路干扰。
2. **NTN 中 TDD 的根本问题**: LEO 600km 的单向延迟约 2ms，双向 RTT ≈ 4ms，保护间隔需两倍最大传播延迟（最高 13ms），消耗 60-95% 帧资源。这是 SBFD 应用于 NTN 的核心动机。
3. **3GPP TR 38.811 天线模型**: Bessel reflector 模型（Eq.(5)），$a = 10\lambda$ 对应约 0.85m 反射器半径（3.55 GHz），主瓣约 3°。天线滚降是边缘性能退化的主要原因。
4. **SEM/BEM 泄漏建模方法**: 将标准文档中的频谱掩模转为 PSD，在频偏范围内积分——这是标准的 OOB 干扰评估方法，可复用于其他频谱共存分析。
5. **关键权衡**: 保护带在噪声受限区域无 SINR 增益但降低吞吐量。仅在 UE 近距（UL→DL 泄漏超过噪声底）时保护带才有 SINR 收益。

### 📌 待解决

1. **UE-UE 距离敏感性**: 论文最大盲点。UL→DL 泄漏通过 UE-UE FSPL 耦合，距离减小 10dB 泄漏增加 20dB，很容易超过噪声底。需参数化分析临界距离。
2. **SI 消除在卫星平台的可行性**: 149 dB 消除在地面 gNB 已是挑战，卫星上的功放非线性和平台振动会使 SI 残留更高。
3. **多卫星密集星座场景**: Starlink 等系统可能有多颗卫星同时在视角内，UL→UL 和 DL→DL 干扰可能被低估。
4. **与 FDD 的公平对比**: NTN 传统使用 FDD，SBFD 需证明在总频谱效率上优于 FDD 才有实际意义。
5. **实际发射机 OOB 特性**: SEM 是最低合规标准，实际发射机的 OOB 可能更低——反过来也可能因功放非线性而更高。

### 💭 思考启发

- **与我的研究的联系**: 本文涉及卫星信号处理和天线波束模型，与 DOA 估计中的阵列信号模型有间接联系。SBFD 中的跨波束干扰建模方法（积分 OOB PSD）可借鉴用于分析 DOA 估计中的带外干扰影响。
- **延伸想法**:
  - 在 SBFD-NTN 场景下，DOA 估计可用于波束管理——通过精确 DOA 跟踪优化波束指向，减小跨波束干扰。
  - 本文的链路预算框架可扩展为 DOA-aided SBFD 系统：利用 DOA 信息自适应调整保护带和子带分配。
  - SBFD 的频域干扰结构可建模为 DOA 估计中的彩色噪声，影响子空间方法的性能。
- **后续研究方向**: 考虑密集 LEO 星座下的 SBFD 干扰管理，结合波束成形和 DOA 估计的联合优化。

---

## 📎 附录 1: 公式目录

### Eq.(1) 斜距计算

$$d(\theta) = \sqrt{R_E^2 + (R_E + h_{sat})^2 - 2R_E(R_E + h_{sat})\cos\theta}$$

| 符号 | 含义 | 维度/范围 |
|------|------|-----------|
| $d(\theta)$ | 卫星到 UE 的斜距 | km |
| $R_E$ | 地球半径 | 6371 km |
| $h_{sat}$ | 卫星轨道高度 | 600 km |
| $\theta$ | 离轴角（卫星星下点与 UE 方向的夹角） | $[0°, \sim3°]$ |

💡 球面地球几何下的斜距公式（余弦定理）。

### Eq.(2) 自由空间路径损耗 (FSPL)

$$L_{fs}(f, d) = 32.45 + 20\log_{10}(d) + 20\log_{10}(f)$$

| 符号 | 含义 | 维度/范围 |
|------|------|-----------|
| $d$ | 距离 | km |
| $f$ | 载波频率 | MHz |
| $L_{fs}$ | 路径损耗 | dB |

💡 标准 FSPL 公式（dB 形式），$d$ 单位 km, $f$ 单位 MHz。

### Eq.(3) DL 带宽

$$B_{DL}(GB) = \frac{B_{tot} - 2B_{UL} - 2GB}{2}$$

| 符号 | 含义 | 维度/范围 |
|------|------|-----------|
| $B_{tot}$ | 总载波带宽 | 100 MHz |
| $B_{UL}$ | 每波束 UL 带宽 | 10 MHz |
| $GB$ | 保护带宽 | $\{0, 5, 10, 15\}$ MHz |

💡 SBFD 频率规划: 总带宽 = 2×DL + 2×UL + 2×GB（因两个波束各占一个 UL 子带）。
← 由 Fig. 4 频率规划直接推导。

### Eq.(4) DL 子带间频率间隔

$$\Delta f_{DL2 \to DL1} = 2GB + 2B_{UL}$$

💡 两个 DL 子带被中央 2 个 UL 子带和 2 个保护带隔开。
← 由频率布局 (Fig. 4) 推导。

### Eq.(5) 卫星天线归一化增益

$$G_{norm}(\theta) = \begin{cases} 1, & \theta = 0 \\ 4\left|\frac{J_1(ka\sin\theta)}{ka\sin\theta}\right|^2, & \theta > 0 \end{cases}$$

| 符号 | 含义 | 维度/范围 |
|------|------|-----------|
| $J_1(\cdot)$ | 第一类 Bessel 函数（一阶） | — |
| $k = 2\pi/\lambda$ | 波数 | rad/m |
| $a = 10\lambda$ | 天线反射面半径 | m |

💡 3GPP TR 38.811 Bessel reflector 模型，描述圆形孔径天线的辐射方向图。

### Eq.(6) 天线增益 (dB)

$$G_{sat}(\theta)[\text{dB}] = 10\log_{10}(G_{norm}(\theta))$$

💡 dB 转换。

### Eq.(7) DL EIRP

$$EIRP_{DL} = EIRPSD_{DL} + 10\log_{10}(B_{DL})$$

| 符号 | 含义 | 维度/范围 |
|------|------|-----------|
| $EIRPSD_{DL}$ | DL 等效全向辐射功率谱密度 | $-26$ dBW/Hz |

💡 从 PSD 到总功率的转换。

### Eq.(8) DL 接收信号功率

$$S_{DL} = EIRP_{DL} + G_{sat}(\theta) + G_{UE} - L_{fs}(f, d)$$

💡 标准链路预算方程。

### Eq.(9) UE 热噪声

$$N_{UE} = k_B T_0 B_{DL} F_{UE}$$

| 符号 | 含义 | 维度/范围 |
|------|------|-----------|
| $k_B$ | Boltzmann 常数 | $1.38 \times 10^{-23}$ J/K |
| $T_0$ | 参考温度 | 290 K |
| $F_{UE} = 10^{NF_{UE}/10}$ | UE 噪声因子 | $NF_{UE} = 7$ dB |

### Eq.(10) UL 接收信号功率

$$S_{UL} = EIRP_{UL} + G_{sat}(\theta) - L_{fs}(f, d)$$

💡 与 Eq.(8) 的差异: UL EIRP 远低于 DL ($23$ dBm vs $-26$ dBW/Hz × BW)，且无 UE 天线增益项。

### Eq.(11) 卫星热噪声

$$N_{sat} = k_B T_0 B_{UL} F_{sat}$$

| 符号 | 含义 | 维度/范围 |
|------|------|-----------|
| $F_{sat} = 10^{NF_{sat}/10}$ | 卫星噪声因子 | $NF_{sat} = 1$ dB |

### Eq.(12) UE OOB PSD

$$PSD_{UE}(\Delta f) = \frac{P_{SEM}(\Delta f) - 30 - 10\log_{10}(RBW(\Delta f))}{1} \quad [\text{dBW/Hz}]$$

| 符号 | 含义 | 维度/范围 |
|------|------|-----------|
| $P_{SEM}(\Delta f)$ | 频谱发射掩模限值 | dBm（来自 3GPP TS 38.101-1） |
| $RBW(\Delta f)$ | 测量分辨带宽 | Hz |

💡 将 SEM 限值（dBm/RBW）转换为 PSD (dBW/Hz)。
← 由 3GPP SEM 规范定义。

### Eq.(13) UL→DL OOB 泄漏功率

$$P_{UL \to DL}^{(OOB)} = \int_{GB}^{GB + B_{DL}} 10^{PSD_{UE}(\Delta f)/10} d\Delta f$$

💡 在保护带 GB 到 DL 带宽范围内积分 UE OOB PSD（线性域积分）。

### Eq.(14) UL→DL 接收干扰

$$I_{UL \to DL} = 10\log_{10}(P_{UL \to DL}^{(OOB)}) - L_{UE-UE} + G_{UE}$$

| 符号 | 含义 | 维度/范围 |
|------|------|-----------|
| $L_{UE-UE}$ | UE 间 FSPL | dB |

💡 OOB 泄漏功率经 UE-UE 耦合后到达受害 UE。

### Eq.(15) UL→UL 干扰

$$I_{UL \to UL} = EIRP_{UL} + G_{sat,rx}(\phi_{UL}) - L_{fs}(f, d_{UL,cross})$$

💡 同频跨波束干扰，无 OOB 衰减。

### Eq.(16) 卫星 OOB PSD

$$PSD_{sat}(\Delta f) = \frac{P_{BEM}(\Delta f) - 30 - 10\log_{10}(5 \times 10^6)}{1} \quad [\text{dBW/Hz}]$$

| 符号 | 含义 | 维度/范围 |
|------|------|-----------|
| $P_{BEM}(\Delta f)$ | Block-Edge Mask 限值 | dBm/5MHz（来自 ECC Report 281） |

### Eq.(17) DL→DL OOB 泄漏功率

$$P_{DL \to DL}^{(OOB)} = \int_{\Delta f_{DL2 \to DL1}}^{\Delta f_{DL2 \to DL1} + B_{DL}} 10^{PSD_{sat}(\Delta f)/10} d\Delta f$$

💡 卫星 2 的 DL 带外发射泄漏到卫星 1 的 DL 带内。

### Eq.(18) DL→DL 接收干扰

$$I_{DL \to DL} = 10\log_{10}(P_{DL \to DL}^{(OOB)}) + (G_{sat,tx}(\theta_2) - G_{sat,tx}(0)) + G_{UE} - L_{fs}(f, d_2)$$

💡 包含卫星 2 相对于波束中心的增益差。

### Eq.(19) DL→UL 干扰（忽略）

$$I_{DL \to UL} \approx 0$$

💡 假设卫星天线指向地球，卫星间耦合可忽略。

### Eq.(20) DL SINR

$$SINR_{DL} = \frac{S_{DL}}{I_{UL \to DL} + I_{DL \to DL} + N_{UE}}$$

### Eq.(21) UL SINR

$$SINR_{UL} = \frac{S_{UL}}{I_{DL \to UL} + I_{UL \to UL} + N_{sat}}$$

### Eq.(22) DL 可达吞吐量

$$R_{DL} = B_{DL} \cdot \log_2(1 + SINR_{DL})$$

### Eq.(23) UL 可达吞吐量

$$R_{UL} = B_{UL} \cdot \log_2(1 + SINR_{UL})$$

---

### 公式依赖图

```
Eq.(1) [斜距计算]
  → Eq.(2) [FSPL]  (代入距离)

Eq.(5)-(6) [天线增益模型]

Eq.(3) [DL 带宽] ← B_tot, B_UL, GB
Eq.(4) [DL 子带间隔] ← GB, B_UL

--- 下行链路 ---
Eq.(7) [DL EIRP] ← EIRPSD + Eq.(3)
  → Eq.(8) [DL 接收功率] ← + Eq.(6) + Eq.(2)
Eq.(9) [UE 噪声] ← Eq.(3)

--- 上行链路 ---
Eq.(10) [UL 接收功率] ← EIRP_UL + Eq.(6) + Eq.(2)
Eq.(11) [卫星噪声]

--- 干扰建模 ---
Eq.(12) [UE OOB PSD] ← 3GPP SEM
  → Eq.(13) [UL→DL 泄漏功率] ← + Eq.(3) 积分范围
    → Eq.(14) [UL→DL 接收干扰] ← + L_UE-UE

Eq.(16) [卫星 OOB PSD] ← ECC BEM
  → Eq.(17) [DL→DL 泄漏功率] ← + Eq.(4) 积分范围
    → Eq.(18) [DL→DL 接收干扰] ← + Eq.(6) + Eq.(2)

Eq.(15) [UL→UL 干扰] ← EIRP_UL + Eq.(6) + Eq.(2)
Eq.(19) [DL→UL ≈ 0]

--- SINR & 吞吐量 ---
Eq.(8) + Eq.(14) + Eq.(18) + Eq.(9) → Eq.(20) [DL SINR]
  → Eq.(22) [DL 吞吐量] ← + Eq.(3)

Eq.(10) + Eq.(19) + Eq.(15) + Eq.(11) → Eq.(21) [UL SINR]
  → Eq.(23) [UL 吞吐量]
```

---

## 📝 附录 2: 引言参考

### (a) 技术全景（先行技术综述）

| 技术/方法 | 核心思想 | 优势 | 局限 | 代表文献 |
|-----------|---------|------|------|----------|
| TDD (地面) | 时域分离 UL/DL | 灵活资源分配、信道互易性 | 需要时间同步 | — |
| TDD (NTN) | 时域分离 + 长保护间隔 | 与地面兼容 | 保护间隔消耗 60-95% 资源 | [4] Lee 2025, [5] Traspadini 2024, [6] Kang 2023 |
| FDD | 频域分离 UL/DL | 无时域同步问题 | 需要成对频谱、无信道互易性 | — |
| SBFD (地面) | 同一时隙内频域分离 UL/DL | UL 吞吐量 4× 边缘提升, 32% 平均提升 | 自干扰消除需 149 dB | [7] Fei 2024, [8] Mokhtari 2023, [9] Li 2024 |
| Full Duplex (卫星) | 收发同频同时 | 频谱效率翻倍 | SI 消除极具挑战 | [10] Lagunas 2025 |

**范式演进**: TDD（时域分离）→ FDD（频域分离）→ SBFD（时隙内频域分离）→ 应用于 NTN（本文首次分析）

### (b) 缺口分析

- **核心缺口**: SBFD 在地面网络中已展示显著性能提升 [8][9]，但从未在 NTN 中被研究。NTN 的独特挑战（长传播延迟、卫星天线模型、球面几何）使得地面 SBFD 分析结果不可直接迁移。

- **关键引文**:
  > "While SBFD performance has been analyzed for terrestrial networks [9], [8], its application to NTN has never been explored." (Section I)
  > "Unlike previous works that consider terrestrial base stations, we model a scenario with two satellites in LEO orbit" (Section I)

- **缺口性质**: 实践性——缺少 NTN 场景的系统级性能分析。

### (c) 方法定位

- **定位策略**: "This paper aims at analyzing the intra-system interference generated by out-of-band (OOB) emissions between uplink and downlink of a 5G-NTN employing SBFD in FR1."
- **相对优势**:
  - 相比地面 SBFD 研究 [8][9]: 首次考虑 NTN 特有因素
  - 相比 TDD-NTN [4][5]: 提出替代方案解决保护间隔效率问题
  - 相比卫星全双工 [10]: 降低硬件要求（SBFD 自干扰消除需求低于全双工）

### (d) 引言逻辑流（叙事结构）

```
1. [背景与重要性]: 地面 5G 主要用 TDD，FR1 mid-band (n77/n78) → 全球 5G 部署的核心频段
2. [NTN 整合需求]: NTN 对全球覆盖至关重要 → 3GPP Release 15 起纳入 NTN → 必须用 TDD 模式保持 UE 兼容性
3. [TDD-NTN 的致命缺陷]: 长传播延迟 → 保护间隔长达 13ms → 消耗 60-95% 帧资源 → 频谱效率极低
4. [SBFD 作为解决方案]: SBFD 将时域同步问题转为频域干扰管理 → 地面已证明 4× UL 边缘吞吐量提升
5. [缺口]: SBFD 在 NTN 中从未被研究
6. [提案]: 分析 SBFD 在 LEO 5G-NTN 中的 OOB 干扰影响 → 双卫星场景 → 评估可达速率和频谱效率
7. [文章组织]: Section II (SBFD vs TDD) → III (系统模型) → IV (仿真) → V (结论)
```

### (e) 参考文献图谱

| 叙事角色 | 参考文献 | 引用方式 |
|----------|----------|----------|
| 5G NTN 重要性 | [1] Lin 2021, [2] Ramírez-Arroyo 2025 | 背景动机 |
| 3GPP NTN 标准 | [3] 3GPP TR 38.811 | 技术基础 |
| TDD-NTN 延迟问题 | [4] Lee 2025, [5] Traspadini 2024, [6] Kang 2023 | 问题描述（先赞后批） |
| SBFD 地面性能 | [7] Fei 2024 (3GPP Rel-18), [8] Mokhtari 2023 (性能评估), [9] Li 2024 (标准进展) | 先行技术（仅地面，引出缺口） |
| 全双工卫星 | [10] Lagunas 2025 | 相关工作 + SI 消除背景 |
| UE SEM 标准 | [11] ETSI TS 138 101-1 | 技术工具 |
| 卫星 BEM 标准 | [12] ECC Report 281 | 技术工具 |

🔍 **批评**: 引言结构清晰、逻辑连贯，TDD-NTN 痛点阐述充分。但存在几个问题: (1) 对 FDD-NTN 方案的讨论过于简略——仅一句"FDD has traditionally been favored"，未说明为什么 SBFD 比 FDD 更有前景; (2) 参考文献以预印本 (arXiv) 为主，可能反映该方向较新但也降低了引用权威性; (3) [10] 的作者 Lagunas 与本文作者相同（自引），这是该领域的核心文献但应注明。

---

*笔记生成日期: 2026-03-03*
*Zotero Item Key: 692JF3SH (父条目), KJXKHRIV (附件)*
*关联笔记: [reading-notes-Review_Mar3.md](reading-notes-Review_Mar3.md) (CWLS 定位论文)*
