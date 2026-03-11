# 三阶段精读笔记：Cooperative Localization, Velocity Estimation and Synchronization in DISAC Systems

> **作者**: Bingqing Li, Jie Yang, Hua Zhang, Le Liang, Haotian Wang, Shi Jin (Southeast University, Purple Mountain Laboratories)
> **Zotero Item Key**: 692JF3SH (父条目 Review_Mar3), 附件 Key: AGNTI5YU
> **类型**: Conference Paper (under review)
> **关键词**: Distributed ISAC (DISAC), Cooperative Localization, Velocity Estimation, Asynchronous Systems, Transformer, Time Offset (TO), Carrier Frequency Offset (CFO)

---

## 📜 研究核心

> Tips: 做了什么，解决了什么问题，创新点和不足？

### ⚙️ 内容

- **目的**: 解决分布式 ISAC (DISAC) 系统中因缺乏严格时钟同步而导致的定位和速度估计退化问题。在异步多 AP 系统中，时间偏移 (TO) 和载波频率偏移 (CFO) 与延迟/Doppler 耦合，严重影响感知精度。
- **研究问题**: 如何在存在 TO/CFO 和密集 NLOS 多径的异步 DISAC 系统中，联合估计移动 UE 的位置、速度和同步参数？
- **研究对象**: 下行 MISO-OFDM 多 AP 分布式感知系统中，基于 CSI 的联合定位-测速-同步框架。
- **贡献声明**:
  1. 提出物理感知特征提取模块: 权重共享 ResNet 提取 CSI 特征 + 空间嵌入编码 AP 坐标。
  2. 设计基于 Transformer 的全局聚合模块: 利用可学习 LVS token（类比 BERT 的 [CLS]）跨多 AP 观测执行一致性检查，联合估计目标状态和同步偏移。
  3. 仿真验证在异步多径场景下显著优于 ML、WLS 和 DNN 基线。

**定位综述**: ISAC 演进为 DISAC（多 AP 分布式）→ 关键挑战是异步同步（TO/CFO 与延迟/Doppler 耦合）→ 现有方法: 跨天线/参考路径法仅解决 AP 间同步，ML [9] 假设 LOS 且忽略速度，DNN [10] 假设完美同步且无空间感知 → 提出一致性驱动 Transformer 框架，利用多视角一致性解耦全局参数与链路级 NLOS 干扰。

### 💡 创新点

1. **一致性驱动设计哲学**: 核心洞察是目标位置、速度和同步偏移在所有 AP 观测中保持一致（位置/速度不变性 + 同步偏移共享）。Transformer 的 self-attention 自然适合发现这种跨观测的一致模式，同时边缘化链路特有的 NLOS 噪声。这比简单 DNN 拼接或传统估计器更具物理合理性。
2. **空间嵌入策略**: 将 AP 的 2D 物理坐标编码为高维向量并与 CSI 特征相加（Eq.(7)-(8)），赋予网络空间几何感知能力。这使得模型能泛化到未见过的 AP 拓扑（Setup B）和未见过的场景（Setup C），而非过拟合特定网络布局。
3. **参数空间重新参数化**: 将 $\tau_o$（微秒级）和 $f_{D,o}$（Hz 级）转换为 $r_o = c \cdot \tau_o$（米级）和 $v_o = \lambda \cdot f_{D,o}$（m/s 级），统一到与位置/速度同量纲的空间，缓解梯度优化的数值病态（Eq.(5)）。
4. **权重共享 + 可学习 LVS token**: 权重共享减少参数量并学习通用 CSI 特征；LVS token 类比 BERT [CLS]，作为全局状态的聚合器。

### 🧩 不足

**作者自认**:
- 未明确讨论局限性（短会议论文风格）。

**审稿人视角批评**:

1. **[Major] 仅 3 AP 评估**: 主要实验仅用 $K=3$ AP，Fig. 4 扩展到 10 AP 但仅在 Setup A 下。分布式系统的核心优势在于大规模 AP 协作，3 AP 过少。
2. **[Major] 缺少与 CRB 的对比**: 未给出 Cramér-Rao Bound 或任何理论性能下界，无法判断算法距最优还有多大差距。
3. **[Major] 训练/测试数据均来自仿真**: 使用 Sionna 射线追踪生成数据，无实测验证。仿真到实测的域迁移 (sim-to-real gap) 未讨论。
4. **[Moderate] TO/CFO 范围有限**: TO $\in [-20, 20]$ ns, CFO $\in [-10, 10]$ Hz，范围较小。实际系统中 TO 可达微秒级（特别是无 GPS 辅助的 UE），CFO 可达 kHz 级。
5. **[Moderate] 计算复杂度未分析**: Transformer 的 self-attention 为 $O(K^2)$（$K$ 为 AP 数），ResNet 特征提取为主要计算量，但未给出推理时间或 FLOPs。在资源受限的 UE 端是否可行？
6. **[Minor] 损失函数中 $\lambda$ 的选择**: $\lambda \in [0,1]$ 平衡位置和速度损失，但最优值如何选择未讨论（可能需要昂贵的超参搜索）。
7. **[Minor] 仅 2D 定位/速度**: 未扩展到 3D，限制了在 UAV 等场景的适用性。

---

## 🔁 研究内容

### 💧 数据

- **数据类型**: 仿真数据（NVIDIA Sionna 射线追踪）
- **场景**: 4 个不同的复杂城市环境，从 OpenStreetMap 导入 Blender
- **系统参数**:
  - $K = 10$ AP（每个 $N_t = 4$ 天线 ULA）
  - OFDM: $M = 14$ 符号, $N = 64$ 子载波
  - 载波频率 $f_c = 2.8$ GHz, 子载波间隔 $\Delta f = 15$ kHz
  - UE 速度 $\in [0, 30]$ m/s, 方向均匀分布 $[0, 2\pi]$
  - TO $\in [-20, 20]$ ns, CFO $\in [-10, 10]$ Hz
  - 每 AP 保留最强 3 条路径
- **实验配置**:
  - Setup A (Fixed-AP): 单场景固定 3 AP 训练/测试
  - Setup B (Random-AP): 同场景随机 3 AP 训练，未见 3 AP 组合测试
  - Setup C (Cross-Scene): 3 场景训练，第 4 场景 zero-shot 测试
- **训练**: Adam, 3000 epochs, batch 256, lr $10^{-4}$, weight decay $10^{-4}$

🔍 **批评**: 训练数据量未说明（每场景多少样本？）。$K=3$ AP 可能不足以体现分布式系统优势。TO/CFO 范围较保守。缺少不同 SNR 下的 CDF 分析。

### 👩🏻‍💻 方法

#### (a) 问题建模 → 核心洞察

**系统模型**: 下行 MISO-OFDM，$K$ 个分布式 AP（已知位置 $b_k$，AP 间通过有线回传严格同步），1 个移动单天线 UE（与 AP 网络异步）。

**信道模型**: 含 TO 和 CFO 的多径信道（Eq.(2)）：

$$h^k(t, \tau) = \sum_{l=1}^{L_k} \beta_l^k \delta(t - \tau_l^k - \tau_o(t)) e^{j2\pi(f_{D,l}^k + f_{D,o}(t))t} a^H(\theta_l^k)$$

其中 $\tau_o(t)$ 和 $f_{D,o}(t)$ 是所有 AP 和路径共享的 TO 和 CFO——**这是一致性的数学基础**。

**核心困难**: TO $\tau_o$ 与路径延迟 $\tau_l^k$ 耦合（两者相加出现在指数项），CFO $f_{D,o}$ 与路径 Doppler $f_{D,l}^k$ 耦合。传统方法需先分离路径参数再估计位置，但 NLOS 环境下路径分离困难，错误会级联传播。

**核心洞察**: 不需要显式分离路径参数。利用三重一致性:
1. **位置一致性**: $(u_x, u_y)$ 在所有 AP 观测中相同
2. **速度一致性**: $(v_x, v_y)$ 在所有 AP 观测中相同
3. **同步一致性**: $(\tau_o, f_{D,o})$ 在所有 AP 链路中相同

Transformer 的 self-attention 天然适合从多视角特征中提取这些全局不变量，同时抑制链路特有的 NLOS 干扰。

#### (b) 方法概览（逻辑流）

**Pipeline** (Fig. 1):

输入（$K$ 个 AP 的 CSI 张量 $H^k \in \mathbb{C}^{N_t \times M \times N}$, AP 坐标 $b_k$）
→ **Step 1: 物理感知特征提取**
  - 复数 CSI 拆分为实虚部 $\bar{H}^k \in \mathbb{R}^{2N_t \times M \times N}$
  - 权重共享 ResNet 提取 CSI 特征 $f^k \in \mathbb{R}^{d_{model}}$（Eq.(6)）
  - 空间编码器将 AP 坐标映射为空间嵌入 $e^k \in \mathbb{R}^{d_{model}}$（Eq.(7)）
  - 逐元素相加: $z^k = f^k + e^k$（Eq.(8)）
→ **Step 2: 注意力全局聚合**
  - 构建输入序列 $Z_{in} = [z_{LVS}; z^1; \ldots; z^K]$（Eq.(9)），LVS token 为可学习参数
  - 3 层 Transformer encoder（8 头 self-attention）处理
  - 提取更新后的 LVS token $z'_{LVS}$
  - MLP 回归头输出 $\hat{\eta} = [\hat{u}_x, \hat{u}_y, \hat{v}_x, \hat{v}_y, \hat{r}_o, \hat{v}_o]^T$（Eq.(11)）
→ **Loss**: 加权 MSE 平衡位置和速度（Eq.(12)）

**信息流**: 每个 AP 的 CSI 独立通过共享 ResNet 提取局部特征 → 空间嵌入注入全局几何信息 → Transformer 跨 AP 聚合发现一致性模式 → LVS token 蒸馏为全局估计。

#### (c) 核心技术贡献（深入分析）

**1. 物理感知特征提取**

- **权重共享 ResNet**: 所有 AP 使用同一个 ResNet（Conv + 2 Residual Blocks），输出 $d_{model} = 256$ 维特征。共享权重迫使网络学习通用的 CSI → 特征映射，而非 AP 特定的模式。这对 Setup B/C 的泛化至关重要。
- **空间嵌入**: 2 层 MLP 将 $b_k \in \mathbb{R}^2$ 映射到 $\mathbb{R}^{256}$。类比 Transformer 中的位置编码 (positional encoding)，但这里编码的是物理空间中的 AP 位置。通过 element-wise addition（Eq.(8)）融合，使特征同时包含信道信息和空间参考。
- **为什么 addition 而非 concatenation**: Addition 保持维度不变，且在 Transformer 中 Q/K/V 投影可以隐式分离或混合两种信息。

**2. Transformer 全局聚合**

- **LVS Token**: 可学习向量 $z_{LVS} \in \mathbb{R}^{256}$，初始化随机，训练中学习成为"全局状态查询器"。通过 self-attention 与所有 AP 特征交互，dot-product 作为一致性度量——与全局状态一致的 AP 获得更高注意力权重。
- **一致性解耦机制**: 位置/速度/同步偏移作为所有 AP 共享的 common-mode 信号，NLOS 干扰作为 AP 特有的 differential-mode 噪声。Self-attention 的加权求和天然倾向于提取 common-mode（多 AP 一致的部分），边缘化 differential-mode（各 AP 不同的部分）。
- **多头注意力**: 8 头允许不同头关注不同类型的一致性（位置相关 vs 速度相关 vs 同步相关）。

**3. 参数重新参数化（Eq.(5)）**

$$\eta = [u_x, u_y, r_o, v_x, v_y, v_o]^T$$

- $r_o = c \cdot \tau_o$: TO（纳秒级）转为距离偏置（米级）
- $v_o = \lambda \cdot f_{D,o}$: CFO（Hz 级）转为速度偏置（m/s 级）
- 统一量纲避免梯度优化的数值病态

**4. 损失函数（Eq.(12)）**

$$L = \lambda\left[(\hat{u}_x - u_x)^2 + (\hat{u}_y - u_y)^2 + (\hat{r}_o - r_o)^2\right] + (1-\lambda)\left[(\hat{v}_x - v_x)^2 + (\hat{v}_y - v_y)^2 + (\hat{v}_o - v_o)^2\right]$$

位置相关项（含 $r_o$）和速度相关项（含 $v_o$）分组加权，$\lambda$ 平衡两组。注意 $r_o$ 和 $v_o$ 分别归入位置和速度组，因为重新参数化后量纲一致。

#### (d) 设计选择与约束

- **为什么 Transformer 而非 GNN/RNN**: Transformer 的 self-attention 无需预定义图结构（GNN 需要），且能并行处理所有 AP（RNN 需顺序）。全局注意力允许任意 AP 对交互。
- **为什么权重共享而非独立网络**: 独立网络参数量 $K$ 倍增长，且无法泛化到未见 AP。共享权重强制学习通用 CSI 特征。
- **仅保留 3 条最强路径**: 降低输入维度，但可能丢失有用的弱反射信息。
- **Block-wise constant TO/CFO**: 假设 TO/CFO 在一个处理时隙（14 符号 ≈ 1ms）内恒定，对于晶振漂移合理。

#### (e) 变体

三种实验配置构成隐式变体:
- **Setup A (Fixed-AP)**: 最简单，固定拓扑
- **Setup B (Random-AP)**: 测试拓扑泛化
- **Setup C (Cross-Scene)**: 测试场景泛化（zero-shot）

🔍 **批评**:
- Transformer 作为黑盒聚合器，缺少可解释性分析（如注意力权重可视化——哪些 AP 被赋予更高权重？LOS AP vs NLOS AP？）。
- "一致性驱动"的表述很好但缺少理论支撑——未证明 self-attention 确实能最优地提取 common-mode 信号。
- 空间嵌入用简单 addition 融合，可能不如 FiLM (Feature-wise Linear Modulation) 等条件化方法有效。
- 无消融实验分离各组件贡献（空间嵌入、权重共享、LVS token、重新参数化各自贡献多少？）。

### 🔬 实验

**Setup**:
- 3 种配置（A/B/C），SNR 从 0-30 dB 扫描
- Baselines: ML [9], WLS [13], DNN [10], Proposed
- 指标: 定位 RMSE (m), 测速 RMSE (m/s)

**定量结果**:

- **图 2（定位 RMSE vs SNR, K=3）**:
  - **Setup A**: Proposed ≈ 0.5-1m（SNR 20-30dB），DNN ≈ 1-2m，ML/WLS ≈ 5-10m
  - **Setup B**: Proposed 性能略微下降但稳定（≈ 1-2m），DNN 严重退化（≈ 5m+），ML/WLS 变化不大
  - **Setup C**: Proposed 保持可用精度（≈ 2-3m），DNN 完全失效（≈ 10m+），证明 zero-shot 泛化能力
  - WLS 受限于路径分离误差传播，ML 受限于 LOS-only 假设

- **图 3（测速 RMSE vs SNR, K=3）**:
  - Proposed 在所有 Setup 中一致最优
  - ML 在 Fixed-AP 中意外优于 DNN（直接搜索速度空间）
  - DNN 在 Random-AP 和 Cross-Scene 中比传统方法还差（过拟合拓扑）

- **图 4（RMSE vs AP 数量, SNR=20dB, Setup A）**:
  - 定位和测速 RMSE 均随 AP 数量单调递减
  - 2→5 AP 性能提升最显著（定位从 ~3m 降到 ~0.8m）
  - 5→10 AP 边际收益递减

🔍 **批评**:
- 缺少 CRB 对比——无法判断 Proposed 距理论最优的差距。
- 无消融实验: 空间嵌入、权重共享、LVS token、Transformer 层数等贡献不明。
- 图 2/3 未给出误差条或置信区间。
- 同步参数（$r_o, v_o$）的估计精度未单独报告——这是论文声明的核心贡献之一。
- Setup B/C 中 DNN 的严重退化部分可能是因为未给 DNN 相同的空间嵌入——对比不完全公平。
- 未与更强的 DL 基线对比（如 PointNet、Set Transformer 等处理集合数据的架构）。

### 📜 结论

- **主要发现**: 一致性驱动 Transformer 在异步 DISAC 中显著优于 ML、WLS、DNN 基线，在拓扑泛化 (Setup B) 和场景泛化 (Setup C) 中保持鲁棒性。
- **作者提出的未来工作**: 未明确提出。
- **评估**: 实验结果令人信服地展示了方法的优势，但缺少理论分析（CRB）、消融实验和同步参数估计精度。"显著优于"的声明在缺少 CRB 的情况下仅是相对于有限基线的比较。

---

## 🤔 个人总结

> Tips: 你对哪些方面有疑问，觉得可以怎么改进？

### 🙋‍♀️ 关键记录

1. **一致性作为设计原则**: 多分布式观测中的全局不变量（位置、速度、同步偏移）可通过 Transformer 的 self-attention 提取。这一思想可迁移至其他分布式感知问题——任何具有跨观测不变量的场景都可借鉴。
2. **空间嵌入 = 物理感知的位置编码**: 将传感器/AP 的物理坐标编码为嵌入向量，使网络感知空间几何。这解决了 DL 方法常见的"几何盲"问题，是提升泛化能力的关键。
3. **参数重新参数化**: 将不同量纲的物理量统一到相同数量级（$\tau_o \to r_o = c\tau_o$, $f_{D,o} \to v_o = \lambda f_{D,o}$），是多任务学习中处理异构输出的标准技巧。
4. **LVS Token 设计**: 类比 BERT [CLS]，用可学习 token 聚合集合输入的全局信息。适用于任何需要从不定数量观测中提取全局状态的任务。
5. **权重共享的泛化优势**: 共享特征提取器 + 空间嵌入编码位置 = 模型可处理任意 AP 配置，而非绑定到特定拓扑。这是 SubspaceNet 类方法可借鉴的设计。

### 📌 待解决

1. **CRB 分析**: 异步 DISAC 系统中联合定位-测速-同步的 CRB 是什么？与 Proposed 方法的差距？
2. **注意力可解释性**: LVS token 对不同 AP 的注意力权重是否与 AP-UE 几何（距离、LOS/NLOS）相关？可视化分析对理解一致性机制至关重要。
3. **消融**: 空间嵌入去掉后性能下降多少？权重共享 vs 独立提取器？LVS token vs mean pooling？
4. **Sim-to-real gap**: Sionna 射线追踪数据训练的模型能否直接用于实测？需要域适应？
5. **同步参数估计精度**: $r_o$ 和 $v_o$ 的 RMSE 未报告，这是论文的核心贡献之一。
6. **大规模 AP 可扩展性**: Transformer self-attention 为 $O((K+1)^2)$，$K=10$ 时可接受，但 $K=100$+ 时可能需要稀疏注意力或层次聚合。

### 💭 思考启发

- **与我的研究的联系**: 本文解决分布式阵列（多 AP）的定位问题，与我的 DOA 估计研究高度相关。SubspaceNet 处理单阵列 DOA，本文处理多阵列联合定位——可视为 DOA 估计的多视角扩展。
- **延伸想法**:
  - **SubspaceNet + 空间嵌入**: 在 SubspaceNet 中加入阵列几何的空间嵌入，使模型能泛化到不同阵列构型（ULA → UCA → 任意阵列）。
  - **一致性驱动 DOA**: 多个子阵列（如大规模 MIMO 分组）的 DOA 估计中，信号方向是子阵列间的不变量。可用类似 Transformer + 一致性 token 设计聚合多子阵列信息。
  - **异步 DOA**: 如果分布式阵列间存在相位/时间偏移，如何在 SubspaceNet 框架中处理？本文的同步参数重新参数化和一致性解耦方法提供了参考。
  - **权重共享 feature extractor**: SubspaceNet 目前为单一输入单一输出，扩展到多阵列时可借鉴权重共享策略。
- **后续研究方向**: 设计一个 Transformer-based 分布式 DOA 估计框架，利用多子阵列一致性（共同 DOA 角度）解耦各子阵列的互耦和校准误差。

---

## 📎 附录 1: 公式目录

### Eq.(1) OFDM 发射信号

$$x^k(t) = \frac{1}{\sqrt{N}} \sum_{m=0}^{M-1} \sum_{n=0}^{N-1} x^k_{m,n} e^{j2\pi\Delta f \cdot nt} \cdot \text{rect}\left(\frac{t - mT_s}{T_s}\right)$$

| 符号 | 含义 | 维度/范围 |
|------|------|-----------|
| $x^k_{m,n}$ | 第 $k$ AP 在第 $m$ 符号第 $n$ 子载波的发射信号向量 | $\mathbb{C}^{N_t \times 1}$ |
| $\Delta f$ | 子载波间隔 | 15 kHz |
| $T_s = T + T_{CP}$ | OFDM 符号总时长（含 CP） | — |
| $T = 1/\Delta f$ | 有用符号时长 | — |
| $N$ | 子载波数 | 64 |
| $M$ | OFDM 符号数 | 14 |

💡 标准 OFDM 基带发射信号模型。

### Eq.(2) 含 TO 和 CFO 的时域信道

$$h^k(t, \tau) = \sum_{l=1}^{L_k} \beta_l^k \delta(t - \tau_l^k - \tau_o(t)) e^{j2\pi(f_{D,l}^k + f_{D,o}(t))t} a^H(\theta_l^k)$$

| 符号 | 含义 | 维度/范围 |
|------|------|-----------|
| $\tau_o(t)$ | 时变 TO（所有 AP/路径共享） | $[-20, 20]$ ns |
| $f_{D,o}(t)$ | 时变 CFO（所有 AP/路径共享） | $[-10, 10]$ Hz |
| $\beta_l^k$ | 第 $k$ AP 第 $l$ 路径复增益 | $\mathbb{C}$ |
| $\tau_l^k$ | 第 $l$ 路径延迟 | s |
| $f_{D,l}^k$ | 第 $l$ 路径 Doppler 频移 | Hz |
| $\theta_l^k$ | 第 $l$ 路径 AOD | rad |
| $a(\theta_l^k)$ | ULA 阵列响应向量 | $\mathbb{C}^{N_t}$ |
| $L_k$ | 第 $k$ AP 的多径数 | — |

💡 关键: $\tau_o$ 和 $f_{D,o}$ 独立于 $k$ 和 $l$（一致性的数学基础）。$\tau_o$ 与 $\tau_l^k$ 在指数中相加耦合。
← 标准含同步偏移的无线信道模型。

### Eq.(3) 接收信号

$$y^k_{m,n} = h^k_{m,n} x^k_{m,n} + w^k_{m,n}$$

💡 标准线性接收模型。

### Eq.(4) 频域信道响应

$$h^k_{m,n} = \sum_{l=1}^{L_k} \beta_l^k e^{-j2\pi n\Delta f(\tau_l^k + \tau_o)} e^{j2\pi m T_s(f_{D,l}^k + f_{D,o})} a^H(\theta_l^k)$$

💡 Eq.(2) 在 OFDM 子载波-符号域的离散形式。$\tau_o$ 和 $f_{D,o}$ 采用 block-wise constant 假设。
← 由 Eq.(2) 在 OFDM 基下离散化。

### Eq.(5) 重新参数化的估计向量

$$\eta = [u_x, u_y, r_o, v_x, v_y, v_o]^T$$

| 符号 | 含义 | 维度/范围 |
|------|------|-----------|
| $r_o = c \cdot \tau_o$ | TO 等效距离偏置 | m（约 $\pm 6$m） |
| $v_o = \lambda \cdot f_{D,o}$ | CFO 等效速度偏置 | m/s（约 $\pm 1$m/s） |

💡 统一量纲，缓解数值病态。

### Eq.(6) CSI 特征提取

$$f^k = f_{\text{ResNet}}(\bar{H}^k; \Theta_{\text{ResNet}})$$

| 符号 | 含义 | 维度/范围 |
|------|------|-----------|
| $\bar{H}^k = [\Re(H^k); \Im(H^k)]$ | 实虚部拼接的实值 CSI | $\mathbb{R}^{2N_t \times M \times N}$ |
| $f^k$ | CSI 特征向量 | $\mathbb{R}^{d_{model}}, d_{model}=256$ |
| $\Theta_{\text{ResNet}}$ | 所有 AP 共享的 ResNet 参数 | — |

💡 权重共享: 同一个 ResNet 处理所有 AP 的 CSI。

### Eq.(7) 空间嵌入

$$e^k = f_{\text{SE}}(b_k; \Theta_{\text{SE}})$$

| 符号 | 含义 | 维度/范围 |
|------|------|-----------|
| $b_k = [a_k, b_k]^T$ | 第 $k$ AP 的 2D 坐标 | $\mathbb{R}^2$ |
| $e^k$ | 空间嵌入向量 | $\mathbb{R}^{d_{model}}$ |
| $f_{\text{SE}}$ | 2 层 MLP 空间编码器 | — |

💡 类比 Transformer 的位置编码，但编码的是物理空间位置。

### Eq.(8) 物理感知特征融合

$$z^k = f^k + e^k$$

💡 逐元素相加融合 CSI 特征和空间嵌入。

### Eq.(9) Transformer 输入序列

$$Z_{in} = [z_{\text{LVS}}; z^1; \ldots; z^K] \in \mathbb{R}^{(K+1) \times d_{model}}$$

| 符号 | 含义 | 维度/范围 |
|------|------|-----------|
| $z_{\text{LVS}}$ | 可学习 LVS token | $\mathbb{R}^{d_{model}}$（随机初始化，训练学习） |

💡 类比 BERT [CLS] token，作为全局状态聚合器。

### Eq.(10) Self-Attention

$$\text{Attention}(Q, K, V) = \text{softmax}\left(\frac{QK^T}{\sqrt{d_{model}}}\right)V$$

💡 标准 scaled dot-product attention。

### Eq.(11) 最终估计

$$\hat{\eta} = f_{\text{Head}}(z'_{\text{LVS}}; \Theta_{\text{Head}}) = [\hat{u}_x, \hat{u}_y, \hat{v}_x, \hat{v}_y, \hat{r}_o, \hat{v}_o]^T$$

💡 MLP 回归头从更新后的 LVS token 输出 6 维估计。

### Eq.(12) 损失函数

$$L(\eta, \hat{\eta}) = \lambda\left[(\hat{u}_x - u_x)^2 + (\hat{u}_y - u_y)^2 + (\hat{r}_o - r_o)^2\right] + (1-\lambda)\left[(\hat{v}_x - v_x)^2 + (\hat{v}_y - v_y)^2 + (\hat{v}_o - v_o)^2\right]$$

| 符号 | 含义 | 维度/范围 |
|------|------|-----------|
| $\lambda$ | 位置-速度损失平衡系数 | $[0, 1]$ |

💡 $r_o$ 归入位置组，$v_o$ 归入速度组，因重新参数化后量纲一致。

---

### 公式依赖图

```
Eq.(1) [OFDM 发射信号]
  → Eq.(2) [含 TO/CFO 的时域信道]  (信号经过信道)
    → Eq.(4) [频域信道响应]  (OFDM 离散化)
      → Eq.(3) [接收信号]  (信道 × 发射 + 噪声)

Eq.(2) 中的 τ_o, f_{D,o} → Eq.(5) [重新参数化] (量纲统一)

--- 网络架构 ---
Eq.(3) 的 CSI H^k → Eq.(6) [ResNet 特征提取]  (复数→实值→特征)
AP 坐标 b_k → Eq.(7) [空间嵌入]  (MLP 编码)
Eq.(6) + Eq.(7) → Eq.(8) [特征融合]  (element-wise addition)
  → Eq.(9) [Transformer 输入]  (+ LVS token)
    → Eq.(10) [Self-Attention]  (多头注意力)
      → Eq.(11) [最终估计]  (MLP 回归头)

Eq.(5) + Eq.(11) → Eq.(12) [损失函数]  (加权 MSE)
```

---

## 📝 附录 2: 引言参考

### (a) 技术全景（先行技术综述）

| 技术/方法 | 核心思想 | 优势 | 局限 | 代表文献 |
|-----------|---------|------|------|----------|
| ISAC（集中式） | 单基站共享硬件/频谱 | 硬件效率高 | 覆盖受限、单视角 | [1] Lu 2024, [2] Yang 2025 |
| DISAC（分布式） | 多 AP 协作感知 | 空间分辨率高、遮挡缓解、广域感知 | 同步困难 | [3] Strinati 2024 |
| 跨天线同步法 | 利用收发天线间信号消除 TO | 适用于双基地 | 仅解决 AP 间同步，不适用 UE | [5] Ni 2021, [6] Li 2022 |
| 参考路径同步法 | 利用已知 LOS 路径校准 TO | 简单有效 | 需要稳定 LOS/静态参考 | [7] Pegoraro 2024, [8] Wei 2024 |
| ML 联合同步+定位 [9] | 最大似然穷搜 | 理论最优（AWGN） | 假设 LOS，忽略速度，NLOS 敏感 | [9] Dey 2025 |
| DNN 定位+测速 [10] | CNN 直接回归 | 多径鲁棒 | 假设完美同步，无空间感知 | [10] Wang 2025 |
| **Proposed** | **一致性驱动 Transformer** | **异步鲁棒、NLOS 鲁棒、拓扑泛化** | **仅仿真、缺 CRB** | 本文 |

**范式演进**: 集中式 ISAC → DISAC → AP 间同步已解决（有线回传） → UE-AP 同步仍是瓶颈 → 模型驱动方法 (ML) 受限于 LOS 假设 → 数据驱动方法 (DNN) 缺乏空间/同步感知 → 本文: 物理感知 + 一致性驱动 Transformer

### (b) 缺口分析

- **核心缺口 1**: UE 与分布式 AP 间的同步远比 AP 间同步困难——UE 移动、仅靠无线链路、无稳定 LOS。
  > "synchronization between a mobile UE and distributed APs is significantly more challenging. The UE must rely solely on wireless links, which are subject to multipath fading and time-varying interference" (Section I)

- **核心缺口 2**: 现有 ML 方法 [9] 假设单一 LOS 路径，忽略速度; DNN [10] 假设完美同步，无空间几何感知。
  > "[9] relies on the idealized assumption of a single dominant LOS path and neglects the estimation of UE velocity" (Section I)
  > "[10] operates under the idealized assumption of perfect synchronization and a lack of awareness regarding the spatial geometry" (Section I)

- **缺口性质**: 理论性（未建模异步）+ 实践性（NLOS 多径环境不适用）。

### (c) 方法定位

- **定位策略**: "we propose a consistency-driven Transformer framework for joint localization, velocity estimation, and synchronization of mobile UEs in DISAC systems."
- **相对优势**:
  - 对比 ML [9]: 不需要 LOS 假设，同时估计速度和同步
  - 对比 DNN [10]: 引入空间嵌入和一致性聚合，处理异步
  - 对比传统同步方法 [5]-[8]: 直接解决 UE-AP 同步（而非 AP-AP）

### (d) 引言逻辑流（叙事结构）

```
1. [背景与重要性]: ISAC 是下一代无线网络关键技术 → DISAC 提供广域空间分辨率
2. [核心挑战]: 分布式节点间时钟同步 → TO 和 CFO 与延迟/Doppler 耦合 → 限制感知精度
3. [先行技术类别 1]: AP 间同步方法（跨天线、参考路径） → 可通过有线回传解决 → 但 UE-AP 同步仍难
4. [先行技术类别 2]: ML 联合同步+定位 [9] → 假设 LOS, 忽略速度
5. [先行技术类别 3]: DNN 定位+测速 [10] → 假设完美同步, 无空间感知
6. [缺口]: 无方法能在异步 NLOS 环境下联合估计位置+速度+同步
7. [提案]: 一致性驱动 Transformer → 物理感知特征 + 多视角一致性聚合
8. [贡献预览]: 3 点贡献
```

### (e) 参考文献图谱

| 叙事角色 | 参考文献 | 引用方式 |
|----------|----------|----------|
| ISAC 背景 | [1] Lu 2024, [2] Yang 2025 | 领域重要性 |
| DISAC 架构 | [3] Strinati 2024 | 动机（分布式优势） |
| 同步挑战综述 | [4] Wu 2024 | 问题定义 |
| AP 间同步方法 | [5] Ni 2021, [6] Li 2022 (跨天线), [7] Pegoraro 2024, [8] Wei 2024 (参考路径) | 先行技术（已解决但不适用 UE） |
| 最近竞争方法 | [9] Dey 2025 (ML 联合同步+定位), [10] Wang 2025 (DNN 定位+测速) | 直接比较对象，识别缺口 |
| Block-wise TO/CFO | [11] Han 2025 | 技术假设支撑 |
| BERT [CLS] token | [12] Devlin 2019 | 网络设计灵感 |
| WLS 基线 | [13] Yang 2021 | 实验对比 |

🔍 **批评**: 引言逻辑清晰，问题定义明确。但有几个问题: (1) [9] 和 [10] 均为 2025 年 arXiv 预印本，说明该方向非常新但引用的工作尚未经过同行评审; (2) 未引用经典定位方法（如 Chan-Ho TDOA、ESPRIT）作为理论背景; (3) 未讨论其他 DL 用于定位的工作（如 fingerprinting-based、graph neural network-based），仅引用一篇 DNN [10] 作为 DL 基线不够全面; (4) [2] 和 [13] 为同课题组自引。

---

*笔记生成日期: 2026-03-03*
*Zotero Item Key: 692JF3SH (父条目), AGNTI5YU (附件)*
*关联笔记: [reading-notes-Review_Mar3.md](reading-notes-Review_Mar3.md) (CWLS 定位), [reading-notes-331-31543-SBFD-NTN.md](reading-notes-331-31543-SBFD-NTN.md) (SBFD NTN)*
