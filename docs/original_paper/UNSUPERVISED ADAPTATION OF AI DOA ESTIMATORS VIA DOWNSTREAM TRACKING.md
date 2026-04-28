# UNSUPERVISED ADAPTATION OF AI DOA ESTIMATORS VIA DOWNSTREAM TRACKING

## 文献信息

- **Author**: Shaul Konstantino; Lei Li; Nir Shlezinger; Davide Dardari
- **Journal**: ,
- **Journal Tags**:
- **Local Link**: [Konstantino 等 - UNSUPERVISED ADAPTATION OF AI DOA ESTIMATORS VIA DOWNSTREAM TRACKING.pdf](zotero://open-pdf/0_ZBRCHNL3)
- **URL**:
- **Abstract**: *Accurate direction of arrival (DoA) estimation plays a central role in a broad range of applications. While artificial intelligence (AI) has recently emerged as a powerful tool for DoA estimation in challenging scenarios, these AI methods are sensitive to distribution shifts caused by calibration drifts, hardware variations, or changing propagation conditions, and adaptation requires labeled data that may be impractical to obtain during deployment. In this work, we introduce a framework for unsupervised adaptation of AI-based DoA estimators by adopting a holistic system-level perspective. Our key insight is that localization algorithms are rarely applied in isolation, but are instead followed by downstream tracking mechanisms such as Kalman filtering. We exploit the statistical information encoded in the innovations of such tracking algorithms to construct unsupervised performance measures that guide online adaptation of the DoA estimator. We develop a dedicated learning algorithm for continual unsupervised adaptation, and demonstrate through numerical studies that our approach enables reliable and flexible AI-aided DoA estimation in time-varying environments.*
- **Tags**:
- **Note Date**: 2026/1/26 13:32:10


## 论文元数据

- **Title**: Unsupervised Adaptation of AI DoA Estimators via Downstream Tracking
- **Authors**: Shaul Konstantino; Lei Li; Nir Shlezinger; Davide Dardari
- **Year**: 2025
- **Venue**: Likely ICASSP / SPAWC submission (preprint)
- **Tags**: DOA, Unsupervised-Adaptation, SubspaceNet, Kalman-Filter, Online-Learning, MBDL, Concept-Drift
- **Zotero Key**: null
- **Source PDF**: Konstantino_等_-_UNSUPERVISED_ADAPTATION_OF_AI_DOA_ESTIMATORS_VIA_DOWNSTREAM_TRACKING.pdf

## 📜 研究核心

> Tips: 做了什么? 解决了什么问题? 创新点与不足是什么?

### ⚙️ 内容

- **Purpose**: AI/DNN-based DoA 估计器在部署阶段对**分布漂移**(calibration drift, hardware variation, propagation change)极度敏感；标准的在线适配需要带标签的 DoA 真值，但部署中真值几乎不可得。本文要解决的就是 *unsupervised* online adaptation 这一悬而未决的问题。

- **Research Question**: 在没有任何 ground-truth DoA 标签的情况下，能否构造出一个**与监督性能强相关**的代理信号来驱动在线 SGD，从而让 AI-aided DoA 估计器适配未知的统计模型变化？

- **Focus**: 一个 system-level 的视角——把 DoA 估计器**不再当作孤立模块**，而是嵌入到一个"AI estimator + downstream Bayesian tracker (Kalman)"的完整管线里，利用 tracker 的 **innovation 序列** $y_i \triangleq \tilde{\theta}_i - g_\psi(X_i)$ 既做漂移检测，也做无监督 loss。

- **Contribution**:

    1. 提出"用下游 tracking 的 innovation 统计量做无监督适配触发 + 无监督 loss"这一系统级方法论。

    2. 定义 **Mean-Squared Innovation Error (MSIE)** $\mathcal{L}_{W_i}(\psi) = \frac{1}{I}\sum |\tilde{\theta}_j - g_\psi(X_j)|^2$ 作为 surrogate loss。

    3. 给出 Algorithm 1：基于滑动窗口 innovation 方差 $\sigma_y^2(i)$ 做 chi-square 风格的漂移检测，触发后做 $S$ 步 GD。

    4. 在 SubspaceNet + Kalman 上做 Monte Carlo 实验，证明 MSIE 在曲线上能**追踪监督 RMSPE**，且无监督方法逼近监督在线学习的精度。


**Positioning paragraph**: 任务是 ULA 上多源 DoA 估计；Gap 是现有 AI-aided DoA 方法（SubspaceNet 等）训练时假设训练/部署同分布，部署时没有标签做适配，而仅有的两个无监督替代方案 [23, 24] 要么依赖强统计假设，要么只用于 model-based calibration 而非 DNN 训练；本文提出"借用下游 Kalman tracker 的 innovation 作为无监督监督信号"的范式；核心 claim 是 innovation 既能可靠地检测 distribution shift，又能作为可微的训练目标，使得无监督 online learning 在 calibration drift 场景下逼近监督上界。

### 💡 创新点

- **System-level surrogate signal**: 不同于 [23] 那种"从估计 DoA 重构协方差"的纯信号-空间一致性 loss（只在简化统计模型下成立），本文借用**已经存在于部署系统里的** downstream Kalman tracker 输出的 innovation——这是一个免费的、由"时间一致性 + 模型先验"派生的监督信号。区别于最近邻先前工作 [24]，后者只把 MUSIC 谱用于 model-based calibration，本文真正用 innovation 来训练 DNN 权重。

- **Drift-triggered adaptation as concept-drift detector**: 用 $\sigma_y^2(i)$ 是否超阈值 $\tau_\sigma$ 来决定是否更新——这是把 concept drift detection [26, 27] 套用到 DoA estimator 上，且检测的是**估计器输出的**变化而非输入信号变化，从而隐式利用了 AI 估计器对小漂移的鲁棒性，避免不必要更新。

- **MSIE loss formulation**: 把 KF 预测 $\tilde{\theta}_j$ 当作 pseudo-label 直接做 MSE，与 RMSPE 的形式高度一致，使得 supervised metric 和 unsupervised loss 的曲线行为可以直接比对（实验图 2/3 印证了这一点）。

- **与 SubspaceNet 等 hybrid 估计器天然兼容**: 因为 $g_\psi(\cdot)$ 是端到端可微的，innovation loss 能直接反传到 covariance surrogate 模块。


### 🧩 不足

#### 作者承认

- 作者明确承认 Algorithm 1 的复杂度比静态 pretrained 模型显著更高，主要来自每次触发后的 $W \cdot I \cdot S$ 步反传。原文：

    > "...its complexity is dominated by training procedure conducted once adaptation is triggered. The latter involves taking $W \cdot I \cdot S$ gradients..." (Sec. 3.3)

    影响评估：在线低延迟应用（如机载/车载雷达）下，这种"突发式重训"可能导致跟踪管线在适配期内输出退化，作者未提供 latency budget 分析。

- 作者承认超参 $W, I, S, \tau_\sigma$ 是**手工调**的，并提出未来可以用下游特征来在线自适应这些超参。

- 作者承认目前只用了 Chi-Squared 风格的方差阈值检测，提到 "alternative test statistics for triggering adaptation" 留给未来。

- 作者承认对噪声分布做了简化假设（保持 $V_i$ stationary 且 Gaussian），仅在 array response 上注入漂移。


#### 审稿批判

- **Major**:

    - **Innovation 与真值之间的耦合是循环依赖的，理论上未保证收敛性** → 漂移触发后，KF 的 $\tilde{\theta}_j$ 是基于**漂移前的 state model + 当前已退化的 $g_\psi(X_j)$** 计算出来的；用一个本身就被污染的预测当 pseudo-label 训练 estimator，再反过来喂给 KF——这种 EM-like 的循环没有任何收敛性、稳定性、bias 分析，可能在严重漂移下发散到错误吸引子。→ 威胁"无监督方法逼近监督上界"这一核心 claim 在 worst-case 下的成立。

    - **没有提供 KF 失效场景下的 fallback** → 当真实 $f(\cdot)$ 与 KF 假设的线性 state model 严重不符（突变运动、机动目标），$\tilde{\theta}_j$ 本身就是坏 label，但 $\sigma_y^2(i)$ 仍会触发，方法会朝错误方向"适配"。论文未讨论这种 model mismatch 下的鲁棒性。→ 威胁"general unsupervised adaptation"的普适性 claim。

    - **实验只覆盖了 array calibration shift 一种漂移类型** → 摘要/intro 多次承诺方法能处理 "calibration drifts, hardware variations, or changing propagation conditions"，但实验只做了 distance miscalibration + geometric noise（两者都是 steering vector 扰动），缺乏对噪声分布变化、源数变化、运动模型突变的测试。→ 威胁 C1 (Nonstationarity) 的普适性 claim。

- **Moderate**:

    - **Baseline 单薄** → 只对比了 pretrained SubspaceNet 与 supervised online learning。缺少与最相关的无监督工作 [23] (Weißer et al.) 和 [24] (Chatelier et al.) 的直接数值比较，论文 intro 把这两者作为最近邻方法批判，但实验里完全没复现它们。→ 威胁"我们的方法是当前 unsupervised DoA adaptation 最好的"这一隐含 claim。

    - **没有 supervised lower bound 的分析** → Table 1 显示无监督 (e.g., 7.51°) 与监督 (5.38°) 之间还有 ~40% 相对 gap；论文没有解释这个 gap 的来源（是 innovation 本身的 bias？是 GD 步数不够？是窗口 $I$ 太小？），也没有 ablation。

    - **MSIE 与 RMSPE 的"高度相关"只在视觉曲线上成立** → 没有计算两者的 Pearson/Spearman 相关系数，也没有理论推导何时 MSIE 是 RMSPE 的无偏代理。→ 威胁"innovation statistics serve as reliable proxies for estimation quality"这一主张。

    - **$\tau_\sigma$ 手工调** → 阈值的选择直接决定了 false-trigger 率与 missed-trigger 率，但论文连一张 ROC 都没有；不同 SNR / drift 强度下 $\tau_\sigma$ 是否需要重调？

    - **只在 ULA + 半波长 + 远场 + 非相干源 + Gaussian 噪声**这一组最理想信号假设下做实验；intro 强调 AI 方法擅长处理 "low SNR, limited snapshots, calibration errors, coherent sources"，但相干源和有色噪声两类典型的 AI 优势场景都没测。

- **Minor**:

    - 公式 (3) 中 $y_i$ 称为 "innovation"，但严格 KF 术语里 innovation 是 $z_i - H\tilde{x}_{i|i-1}$，即"观测 - 预测观测"。本文里 $y_i = \tilde{\theta}_i - g_\psi(X_i)$ 实际是 "filtered state - measurement"，即一种 "smoothing residual"，术语稍显宽松。

    - Algorithm 1 第 9 行写 $\psi \leftarrow \psi - \eta \nabla_\psi \mathcal{L}_{W_i}(\psi)$，但实际实现使用什么 optimizer (Adam? plain SGD?) 未说明。

    - "Algorithm 1 demonstrates substantial gains ranging from 3.5° to 14.46°" 这种数字混合（前者是平均 gain，后者是 17.44° → ~3° 的差），表述不严谨。

    - Fig. 2/3 的 x 轴标注是 "Window Index" 而正文叫 "block index"，命名不一致。

    - Sec. 3.2 "When ${y_i}$ is modeled as zero-mean i.i.d. Gaussian, this implements a form of Chi-Squared test for which the threshold can be computed analytically. However, in our numerical examples we tune $\tau_\sigma$ manually"——既然提到了 chi-square 解析阈值，为什么不用？至少做个对比。


---

## 🔁 研究内容

### 💧 数据

- **Array configuration**: ULA, $N=9$ antennas, 5 GHz, 半波长间距（标称）。

- **Sources**: $M=3$ narrowband, non-coherent, far-field 源；DoA 从 $[-\pi/2, \pi/2]$ 均匀采样。

- **Snapshot regimes**: 两档——$T=200$ (高观测) 与 $T=20$ (受限观测)。

- **Temporal evolution**: 100 blocks 的运动轨迹，由 $$\theta_{i+1} = \theta_i + [3, -3, 2] \odot \sin(\omega_0 \cdot t) + w_i$$ 生成，其中 $\omega_0 = [-0.15, 0.25, 0.15]$，$w_i \sim \mathcal{N}(0, 0.03^2)$。

- **Distribution shift (在随机选定 block 注入)**:

    1. **Distance miscalibration**: 均匀扰动 $\delta_n \sim \mathcal{U}(-\eta, \eta)$，$\eta \in \{0.3, 0.9, 1.2\}$。

    2. **Geometric noise**: 加性复高斯 $\epsilon_{n,\theta}$，方差 0.9。


    合成的 perturbed steering vector 为 $$[a(\theta)]_n = e^{-j 2\pi (d_n + \delta_n) \sin(\theta) / \lambda} + \epsilon_{n,\theta}$$

- **Pretraining set**: 4096 labeled samples，从理想 ULA 生成。

- **Test horizon**: 300 blocks（论文 Sec. 4.2，与 Sec. 4.1 的 100 blocks 不一致）；100 次 Monte Carlo。

- **SNR**: 评测在 $\{0, 5, 10\}$ dB，定义为 $1/\mathrm{Var}(V_i)$。

- **Noise**: $V_i$ 保持 stationary Gaussian——**漂移只在 array response 上**。


#### 🔍 数据批判

- **数据合成性强，缺乏真实测量数据** → 整个评测全在 synthetic ULA 模型上做，array imperfection 也是 toy 模型 (uniform $\delta_n$ + 加性高斯)；真实 calibration drift 通常包含频率相关、温度相关、互耦等结构化扰动 → 威胁 "robust DoA estimation in time-varying environments" 的实际 claim。

- **Drift 类型单一** → 摘要承诺覆盖 calibration / hardware / propagation 三类漂移，数据只构造了 array response 漂移（也就是 hardware 那一类的子集）→ 威胁 C1 普适性 claim。

- **DoA 运动模型与 KF 的 state model 高度匹配** → 评估时 KF 的 process noise variance 直接 plug 0.03（与生成 $w_i$ 的 std 相同），等于给 tracker 开了"上帝视角"，innovation 的统计量自然干净；真实场景里这种匹配几乎不可能，论文没做 KF model mismatch 的 ablation → 威胁"unsupervised loss 是 reliable proxy"的鲁棒性 claim。

- **训练集仅 4096 样本** → 对 SubspaceNet 这种 CNN-AE 架构而言不算小，但论文未给 train/val 划分细节、没说初始 RMSPE 在 in-distribution 上是多少，缺乏 baseline calibration 信息。

- **Block 数量披露矛盾** → Sec. 4.1 说 "Three sources move over 100 blocks"，Sec. 4.2 说 "all 300 blocks"，未解释这两个数字的关系（是 100 blocks × 3 个 SNR？还是 300 blocks 的轨迹？）。


### 👩🏻‍💻 方法

#### (a) Problem Formulation → Key Insight

**Signal model**: 在 block $i$ 内观测矩阵 $$X_i = A_i(\theta_i) [s_i(1), \ldots, s_i(T)] + V_i \quad \text{Eq.(1)}$$ 其中 $A_i(\theta) = [a_i(\theta_1), \ldots, a_i(\theta_M)]$ 是 steering matrix，理想 ULA 下 $a_i(\theta) = [1, e^{-j\pi\sin\theta}, \ldots, e^{-j\pi(N-1)\sin\theta}]^\top$。

**Temporal evolution of state (DoA)**: $$\theta_{i+1} = f(\theta_i) + w_i, \quad w_i \sim \text{i.i.d. with covariance } Q \quad \text{Eq.(2)}$$

**核心 bottleneck**: AI-aided estimator $\hat{\theta}_i = g_\psi(X_i)$ 是离线训练的，部署时若 $A_i$ 或 $P_{V_i}$ 发生漂移（C1），需要更新 $\psi$；但部署中没有 $\theta_i$ 真值（C2）。这两个 challenge 直接对立——**要适配就需要监督信号；可没有监督信号**。

**Key insight**: DoA 估计器在实际部署时**永远不孤立**——下游必有跟踪算法（KF、IMM、PF 等）。这些 tracker 内部携带了 *Markovian state evolution* 这一额外先验信息。**这个先验本身就可以充当一种"温和监督"**：tracker 通过融合多步观测得到的预测 $\tilde{\theta}_i$ 比单步估计 $\hat{\theta}_i = g_\psi(X_i)$ 在统计上更可靠（在 KF 假设满足时是 BLUE），所以两者之差 $y_i \triangleq \tilde{\theta}_i - g_\psi(X_i)$ 在"系统正常工作时"应该是均值为 0、方差较小的随机过程；一旦 $g_\psi$ 因漂移退化，$y_i$ 的方差会显著上升——这就是无监督的"漂移温度计"。

#### (b) Method Overview (Logic Flow)

整体管线（Fig. 1）四个模块串成闭环：

1. **AI-aided localization**: $\hat{\theta}_i = g_\psi(X_i)$（论文用 SubspaceNet）。

2. **Downstream tracking**: KF 利用 Eq.(2) 把 $\hat{\theta}_i$ 滤波/平滑成 $\tilde{\theta}_i$。

3. **Innovation monitoring**: 计算 $$y_i \triangleq \tilde{\theta}_i - g_\psi(X_i) \quad \text{Eq.(3)}$$ 并在长度 $I$ 的滑窗上做经验方差 $$\sigma_y^2(i) = \frac{1}{I} \sum_{j=i-I+1}^{i} |y_j|^2 \quad \text{Eq.(4)}$$

4. **Adaptation**: 若 $\sigma_y^2(i) > \tau_\sigma$，触发 GD 更新 $\psi$，loss 为 $$\mathcal{L}_{W_i}(\psi) = \frac{1}{I} \sum_{j=i-I+1}^{i} |\tilde{\theta}_j - g_\psi(X_j)|^2 \quad \text{Eq.(5)}$$


**信息流的关键中间表达**:

- $\hat{\theta}_i$（AI 单步估计） → 喂给 KF。

- $\tilde{\theta}_i$（KF 平滑结果） → 既反馈进 innovation 计算，又当 pseudo-label 用于 GD。

- $y_i$（innovation） → 既是漂移检测的输入，也间接通过 loss 反传到 $\psi$。


#### (c) Core Technical Contributions (Deep Dive)

**贡献 1：MSIE loss 设计**——直接把 KF 预测当 pseudo-label。

- **解决的问题**: 缺少真值 $\theta_i$ 时如何定义 $\nabla_\psi$ 的目标。

- **机制**: 由于 KF 在长时间窗口上是 $\hat{\theta}_{1:i}$ 的最优线性融合，$\tilde{\theta}_j$ 在期望上比 $\hat{\theta}_j$ 更接近真值（在 KF 假设满足时）；对 $\psi$ 做 MSE 拉近 $g_\psi(X_j) \to \tilde{\theta}_j$ 等价于"让单步 AI 估计向时序融合后的更优估计靠拢"。

- **为何这样设计**: MSIE 与监督 RMSPE 形式同构（都是 squared $L_2$），所以梯度方向在 KF 工作良好时与监督梯度高度一致。备选方案如 [23] 那种 "重构协方差" 路线需要严格的统计假设；备选如对比 MUSIC 谱 [24] 不是端到端可微的。


**贡献 2：Drift-triggered adaptation**——$\sigma_y^2(i) > \tau_\sigma$ 才触发。

- **解决的问题**: 持续做 GD 既计算昂贵又可能在分布稳定时引入不必要的扰动（catastrophic adaptation）。

- **机制**: $\sigma_y^2(i)$ 是 innovation 能量的滑窗 average；在 $g_\psi$ 工作良好时 $y_i$ 是小且接近零均值的，所以 $\sigma_y^2(i)$ 低；一旦 array response 漂移导致 $g_\psi(X_i)$ 系统性偏离，$y_i$ 的能量会显著上升。

- **为何这样设计**: 当 $y_i \sim \mathcal{N}(0, \sigma^2 I)$ i.i.d. 时，$\sigma_y^2(i)$ 服从 chi-square，可以解析推导阈值；论文为了避免分布假设，选择手动调 $\tau_\sigma$。这是把 concept drift detection [26, 27] 的思想应用到 DoA estimator 上的具体实例。


**贡献 3：Adaptation horizon 控制**——触发后做 $W$ 个窗口、每窗口 $S$ 步 GD。

- **解决的问题**: 单次 GD 不足以适配，无限 GD 又过拟合到当前 minibatch。

- **机制**: $W \cdot I \cdot S$ 是总反传步数预算，可以根据延迟预算调节。

- **为何这样设计**: 显式分离"触发频率"与"训练强度"，使得 hyperparameter 有明确的物理含义。


#### (d) Design Choices & Constraints

- **AI 模块选 SubspaceNet** [17]：是一个 hybrid model-based DL 方法（用 CNN-AE 生成 covariance surrogate，再交给 subspace 算法），这个选择不是偶然——它的 inductive bias 让 $g_\psi$ 在小漂移下天然有一定鲁棒性，给"drift-triggered" 策略留出余地（如果 AI 模块完全 black-box 端到端，可能漂移检测窗口还没攒够样本就崩了）。

- **KF 状态噪声方差 plug-in 0.03**：与生成数据用的 $w_i$ std 完全相同——这是 evaluation 上的强假设。

- **滑窗 $I=5$、adaptation period $W=10$、$S=5$**：均为 manual tuned，未做 sensitivity ablation。

- **漂移期间不触发 KF 重新初始化**：作者隐式假设 KF 的 covariance 估计在漂移期内仍然稳定。


#### (e) Variants

论文只给出了一种主算法 (Algorithm 1)。可能的变体（作者未实现）：

- 用 chi-square 解析阈值替代手动 $\tau_\sigma$。

- 用 IMM/PF 替代 KF 处理非线性 state model。

- 用 EMA 平滑 $\sigma_y^2(i)$ 而非滑窗均值。


#### 🔍 方法批判

- **MSIE 是 biased surrogate** → KF 输出 $\tilde{\theta}_j$ 是 $g_\psi(X_{1:j})$ 的函数，所以 $\tilde{\theta}_j - g_\psi(X_j)$ 不是真正的"误差"而是"自相关残差"。把它最小化在数学上等价于 enforce **temporal smoothness**，而非 enforce **accuracy**。在 DoA 真的发生快速变化（高 $|\dot\theta|$）的 block 上，最小化 MSIE 反而会**抑制**真实的 DoA 变化 → 威胁"MSIE 是 RMSPE 的可靠代理"主张。

- **触发器与 loss 共享同一个 $\tilde{\theta}$ 来源 → 漂移检测可能延迟** → 漂移发生瞬间，KF 还没来得及反应，$\tilde{\theta}_i$ 仍然 follow 旧轨迹；只有等 KF 也"看见"足够多漂移后的 $\hat{\theta}$，innovation 才会上升 → 检测延迟 ≈ KF 等效带宽。论文没有量化这种延迟。

- **没有处理 model mismatch** → 一旦真实运动模型偏离 Eq.(2)（机动目标），$\sigma_y^2(i)$ 会因为 KF 跟不上而误报，触发对 $g_\psi$ 的"虚假适配" → 威胁 method robustness。

- **公式 (4) 中 $|\cdot|$ 未明确是 $\ell_2$ 还是 element-wise** → 在 $M=3$ 多源场景下，association 问题（哪个 $\tilde{\theta}_j$ 配哪个 $\hat{\theta}_j$）未讨论；如果 SubspaceNet 输出的 DoA 排序与 KF 跟踪的源 ID 错位，innovation 会显著虚高。

- **Adaptation 期间的 KF 状态如何更新？** → 论文未说在 GD 触发期间（$W$ 个窗口 × $S$ 步 GD）KF 是冻结还是继续运行；如果继续运行，那么用 $g_\psi$ 不断变化的输出去更新 KF，会引入额外的不稳定性；如果冻结，那么 $W$ 个窗口期内系统是"半盲"的。

- **逻辑链漏掉了 $g_\psi$ 与 KF 的可信度耦合** → 严格说，KF 增益依赖于"测量噪声协方差"$R$，而 $R$ 在漂移后应该重新估计；论文用固定 0.03，等于隐含假设漂移不影响测量噪声—这与"漂移仅在 array response"的实验设定恰好兼容，但在更一般场景下不成立。


### 🔬 实验

- **Setup** (Sec. 4.1):

    - ULA: $N=9$, 5 GHz, $M=3$ non-coherent narrowband sources。

    - SubspaceNet 预训练在 4096 ideal-ULA 样本上。

    - KF: process noise std 0.03（与数据生成一致），observation noise variance 0.03。

    - Algorithm 1 超参：$I=5$, adaptation period $W=10$ windows, $S=5$ GD steps。

    - 每个 SNR/$T$ 配置跑 100 Monte Carlo trials。

- **Metrics**:

    - **RMSPE**: root MSPE，从 Routtenberg & Tabrikian 2011 的 periodic cost function 来。

    - **MSIE**: 论文自定义的无监督 surrogate (Eq. 5)。

- **Baselines**:

    - **Pre-trained**: 静态 SubspaceNet，不做适配（下界）。

    - **Online supervised**: 漂移后用真值 DoA 做监督 GD（不可行的上界，仅作对比）。

    - **Algorithm 1**: 本文方法。

- **Quantitative results** (Table 1, time-averaged RMSPE over 300 blocks)：

    | SNR (dB) | Pre-trained $T=20$ | Pre-trained $T=200$ | Supervised $T=20$ | Supervised $T=200$ | Alg.1 $T=20$ | Alg.1 $T=200$ |
    | --- | --- | --- | --- | --- | --- | --- |
    | 0 | 11.30° | 11.15° | 5.47° | 5.38° | **7.90°** | **7.51°** |
    | 5 | 12.37° | 12.31° | 5.65° | 5.57° | **7.95°** | **8.80°** |
    | 10 | 17.44° | 16.06° | 4.54° | 4.37° | **6.51°** | **6.47°** |

    解读：

    - Pretrained 在所有 SNR 下都受漂移影响严重；高 SNR 时反而更糟（17.44°），因为预训练模型在干净数据上学到了对小扰动敏感的表示。

    - Algorithm 1 平均比 pretrained 低 ~3.5°-11°，且随 SNR 升高 gap 越大。

    - Algorithm 1 与 supervised 的 gap 大约 2°-3°，论文称之为 "minor gap"——但相对而言是 ~40% relative error increase。

- **Ablation**: 论文**没有做** $I$, $W$, $S$, $\tau_\sigma$ 的 sensitivity 实验。

- **Per-block dynamics** (Fig. 2 for $T=200$, Fig. 3 for $T=20$):

    - Pretrained 在 distribution change 时刻 (block ~20) RMSPE 阶跃上升到 0.3 rad (~17°) 并保持。

    - Algorithm 1 在 "Training Start" 后开始下降，逐步逼近 Supervised Trained Model 曲线。

    - MSIE 曲线（下图）与 RMSPE（上图）在视觉上同步——这是论文核心定性 claim 的证据。

- **Statistical rigor**: 100 Monte Carlo 取均值，但 Table 1 没有 error bar / std；图也没有 confidence interval。


#### 🔍 实验批判

- **缺少最相关的无监督 baseline** → Intro 列出了 [23] (Weißer et al., 2023) 和 [24] (Chatelier et al., 2024) 作为最近邻无监督工作，但实验完全没复现 → 威胁 "we propose a framework for unsupervised adaptation" 的相对优越性 claim。

- **缺少超参 ablation** → $I, W, S, \tau_\sigma$ 是方法的核心 knob，论文一句"manually tuned"就带过 → 威胁"方法可工程落地"的实用性 claim。

- **MSIE-RMSPE 相关性只给定性曲线** → 没有定量指标（相关系数、$R^2$、KL 等）证明 MSIE 是 reliable proxy → 威胁 "innovation statistics serve as reliable proxies for estimation quality" 这一定量 claim。

- **没有失败案例 (failure mode) 展示** → 所有图都是"漂移→适配成功"；缺少"严重漂移→适配发散"或"误触发→精度下降"的边界案例。

- **没有 source association 测试** → $M=3$ 个移动源，DoA 排序在轨迹交叉时易混淆；KF tracking 对 association 错误极其敏感，但论文没有任何 association 处理或测试。

- **Drift 时间点固定** → "introduced at a randomly selected block"——是每条 trace 随机一次，还是 100 trials 共用同一个 block？写得不清楚，复现性受影响。

- **Setup 内部矛盾** → Sec. 4.1 写 "Three sources move over 100 blocks"，Sec. 4.2 写 "all 300 blocks of length T"——这个 100 vs 300 的不一致让人怀疑实验配置披露不完整。

- **理想化的 KF 参数** → KF 的 process noise variance 直接 plug 数据生成时的真值 0.03，这在真实场景里相当于"先知"——应做 KF mismatch 下的 sensitivity 测试。


### 📜 结论

- **主要发现**:

    - 提出的 MSIE-driven unsupervised adaptation 在 SubspaceNet + Kalman 管线上能可靠地减小 calibration drift 带来的精度损失，从 17.44° → 6.51° (10 dB SNR, $T=20$)。

    - MSIE 曲线在视觉上与监督 RMSPE 曲线同步演化，说明 innovation statistics 可作为无监督性能监控代理。

    - 方法在低 SNR (0 dB) 与有限快拍 ($T=20$) 下仍然有效。

- **作者陈述的 future work**:

    - 用下游特征自动调超参 ($I, W, S, \tau_\sigma$)。

    - 探索其他 test statistics (非 chi-square 风格) 触发适配。

- **我的评估**: 结论本身是 **partially supported**——

    - "MSIE 能驱动有效适配" → 在论文给定的窄实验设置下成立。

    - "可靠代理 estimation quality" → 缺定量证据，被夸大。

    - "robust DoA estimation in time-varying environments" → 摘要措辞过宽，实验只覆盖一种漂移类型，应限定为 "robust to array calibration drifts"。


---

## 🤔 个人总结

> Tips: 你质疑了哪些方面? 你认为如何可以改进?

### 🙋‍♀️ 关键记录

- **核心 takeaway 1**：DoA estimation 在真实部署时是嵌入在 tracking pipeline 里的——这个观察本身值得记下来。任何 "标准" DoA benchmark（孤立的 RMSE@SNR）都低估了下游 tracker 的"温和监督"潜力。今后做 MBDL DoA 工作时，应在 pipeline 终点（tracker / decision-maker）处寻找 free supervision，而不是反复在中间模块上叠 architecture。

- **核心 takeaway 2**：Innovation 当 surrogate label 这个 trick 不局限于 DoA——只要有 (a) 一个学到的 measurement model + (b) 一个相对可信的 state-evolution prior，就可以构造类似的 self-distillation loss。例如 channel estimation / target tracking / 3D 定位都适用。

- **核心 takeaway 3**：Drift-triggered (而非 always-on) 在线学习是值得借鉴的工程模式——它把"训练成本"与"真实性能退化"挂钩，避免了 always-on online learning 的 catastrophic forgetting 风险。

- **核心 takeaway 4**：SubspaceNet 这种 hybrid 架构对适配方法是友好的（梯度通畅、参数少、有 inductive bias 防止灾难性退化）；纯 end-to-end DNN 可能在同样 unsupervised loss 下表现更差——这反过来支持了 MBDL 路线。

- **关键术语**：

    - **MSIE (Mean-Squared Innovation Error)**：本文定义的 unsupervised loss，$\frac{1}{I}\sum |\tilde{\theta}_j - g_\psi(X_j)|^2$，把 KF 平滑结果当 pseudo-label。

    - **MSPE (Mean-Squared Periodic Error)**：周期化的 squared error，处理 DoA 在 $[-\pi/2, \pi/2]$ 边界附近的 wrap-around 问题（[Routtenberg & Tabrikian 2011]）。

    - **Innovation**（本文宽松用法）: tracker 平滑结果 - 单步估计；标准 KF 中通常指 measurement - predicted measurement。


### 🔧 可复用技术

#### 整体方法复用

- **方法名**：Downstream-Tracker Innovation as Unsupervised Adaptation Signal (DTI-UAS)

    - **解决的问题**（抽象化）：在一个"学到的逐时刻估计器 + 下游时序融合滤波器" pipeline 中，无需真值即可在线监测和修复 estimator 的 distribution shift。

    - **复用前提**：

        1. 下游存在一个可信的 Bayesian filter（KF / EKF / UKF / PF），其 state-evolution prior 在漂移期间仍大致成立。

        2. 上游 estimator 是端到端可微的 DNN 或 hybrid MBDL 模型，参数可在线更新。

        3. estimator 输出与 filter state 的语义在同一空间（如本文都是 DoA 角度），否则需要 differentiable 映射。

    - **迁移成本**：medium——核心算法只有几行 PyTorch；难点在于设计一个对该任务 robust 的 trigger threshold，以及确保 filter 在 GD 触发期内仍能稳定运行。

    - **潜在目标场景**：

        1. Channel estimation in time-varying wireless channels（用 LSTM / Kalman tracker 的 innovation 适配学到的 channel estimator）。

        2. Visual object tracking 中适配 detector backbone（用 motion tracker 的 residual 当 unsupervised loss）。

        3. SLAM 中适配 visual odometry 模块（用 loop-closure 残差作 surrogate label）。

    - **推荐度 ⭐⭐⭐**：直接对齐 Current Research Focus 的 **Core task (DoA estimation)** 与 **Techniques of interest (model-based DL, SubspaceNet-style hybrid architectures)**，且明确针对 **Signal regimes of interest** 中的 *array imperfections* 这一条；适配不需要离开 DoA + MBDL 主线，这是当前我最容易直接复用的整体范式。


#### 组件级复用

- **组件名**：Sliding-window innovation variance + threshold trigger（Eq. 4 + $\sigma_y^2(i) > \tau_\sigma$）

    - **在原论文中的作用**：作为 concept-drift detector，决定何时启动 GD 适配。

    - **独立解决的子问题**（抽象化）：在线检测一个时序信号是否进入 anomalous regime，且检测器只依赖低阶矩，不依赖具体分布假设。

    - **接口要求**：输入是任意标量/向量时间序列 ${y_i}$；输出是布尔触发信号。

    - **可嫁接的其他场景**：

        1. 任何 online learning 系统的 drift detector（接收机 [27]、流式异常检测、分布外检测）。

        2. 强化学习中检测 environment shift 触发 policy retraining。

    - **复用风险**：依赖 ${y_i}$ 在 nominal regime 下是 stationary 的；对突变 vs 渐变漂移检测灵敏度不同；阈值需对每个新场景重新校准。

    - **推荐度 ⭐⭐**：与 Current project 的 **Techniques of interest (subspace methods)** 关联较弱，但与 **Signal regimes of interest** 中的 *array imperfections* 直接相关；用作 trigger 时需要在 DoA 多源/低 SNR/低快拍场景下重新调阈值，所以不是 plug-and-play。

- **组件名**：MSIE loss for self-distillation against a Bayesian smoother (Eq. 5)

    - **在原论文中的作用**：触发后用作 GD 的目标函数。

    - **独立解决的子问题**：在没有真值的 supervised loss 不可用时，构造一个 differentiable surrogate，使得最小化它能拉近 estimator 输出与一个已知更优 (smoother) 的输出。

    - **接口要求**：需要 $g_\psi(\cdot)$ 端到端可微；smoother 输出 $\tilde{\theta}$ 可以 stop-gradient（论文没明说但隐含）。

    - **可嫁接的其他场景**：

        1. Self-training / pseudo-labeling 一类的 semi-supervised pipeline。

        2. Knowledge distillation 框架（teacher = smoother, student = single-shot estimator）。

        3. 任何"online estimator + offline post-processor"组合的部署管线。

    - **复用风险**：smoother 也可能 biased，盲目最小化会让 estimator 学到 smoother 的错误（confirmation bias 闭环）。

    - **推荐度 ⭐⭐⭐**：直接对齐 Current Research Focus 的 **Evaluation lens 1 (ML methodology — training)** 与 **Techniques of interest (model-based DL)**，且 loss 形式与 SubspaceNet 等 differentiable subspace 架构天然兼容；可立即在我自己的 DoA pipeline 上尝试。

- **组件名**：MSPE / RMSPE 评测指标 [Routtenberg & Tabrikian 2011]

    - **在原论文中的作用**：作为有监督性能基准。

    - **独立解决的子问题**：解决 DoA 在 $[-\pi/2, \pi/2]$ 周期边界附近的"绕圈"导致 squared error 虚高的问题。

    - **接口要求**：标量角度输入；输出是周期化后的 MSE。

    - **可嫁接的其他场景**：所有有周期边界的角度/相位估计问题（NF localization 中的方位角、相位估计、MIMO precoder 角度）。

    - **复用风险**：低；这是一个标准 metric。

    - **推荐度 ⭐⭐⭐**：这是 Current Research Focus 中 **Core task (DoA estimation)** 的标准评测工具，且与 **Theoretical tools (CRB)** 类的统计评测自然兼容；建议在自己的 DoA 工作中默认使用。


### 📌 待解决

- **闭环稳定性**：MSIE 是基于 smoother 的 self-distillation，理论上存在 estimator-smoother 闭环偏差放大的风险。在尝试复用前，需先做：

    1. 推导 MSIE 梯度与"oracle supervised loss"梯度的偏差分析。

    2. 在合成数据上构造 "smoother 也有偏差" 的 stress test。

- **缺失的实验**：

    1. 与 [23] [24] 的直接 head-to-head 数值对比。

    2. 超参 ($I, W, S, \tau_\sigma$) 的 sensitivity ablation。

    3. 真实 KF model mismatch 下的 robustness 测试（如运动模型用 CV/CA 失配）。

    4. 多源 association 鲁棒性测试。

    5. 不同漂移类型（噪声分布漂移、源数变化、相干源出现）下的泛化测试。

- **Contradictory literature**：[24] (Chatelier et al., 2024) 提出的 "physically parameterized differentiable MUSIC" 也是 unsupervised array calibration 路线，两者哲学不同——前者是 model-side 的 calibration adaptation，本文是 data-side 的 estimator adaptation。理论上两者可结合（同时校 array model 与 update DNN），论文未讨论。

- **Verify before building on**:

    - SubspaceNet repo (https://github.com/UliKonstantin/SubspaceNet) 是否真的能复现 Table 1 的数字。

    - KF 实现细节（plug-in covariance vs. adaptive estimation）。

    - "Block index" vs "Window index" 在代码里到底是哪个。


### 💭 思考启发

#### 与我研究的关联

- **ML methodology 视角**:

    - 本文展示了一个非常 **clean 的 self-distillation 模式**：把 pipeline 下游的"时序融合"模块当成 free teacher，而不是另起 augmentation/contrastive learning 那种 generic SSL 路线。这对 Current project (DoA + MBDL) 的训练设计有直接启发——我现在的 SubspaceNet-style hybrid 训练完全依赖 simulated label，但 deployment-time 完全可以引入类似的 "downstream-tracker as teacher" 损失，做 test-time adaptation。

    - 论文用 hybrid 架构 (SubspaceNet) 而非 pure DNN，这本身就支持 Current Research Focus 的 **MBDL 路线优于纯 black-box DL** 的论点：hybrid 模型在 unsupervised loss 下不容易崩塌。

- **Signal processing theory 视角**:

    - 论文的 "innovation as anomaly indicator" 与传统 array processing 的 **subspace perturbation analysis** 有深层联系——array calibration drift 本质上扰动了 signal subspace，导致 single-shot estimator 的偏差；而 KF 在状态空间内做平滑，相当于在 time-domain 上用低通滤波器抑制了这种偏差，所以 innovation 序列里集中了"高频偏差能量"。这给了我一个新的视角：**可以用 subspace perturbation 的 closed-form bound 给 $\tau_\sigma$ 一个理论选取准则**，而不是手动调。

    - 论文没有讨论 CRB——这是 Current Research Focus 中明确强调的 "Theoretical tools" 之一。一个明显的扩展是：在漂移后的 array 模型下重新推 CRB，看看 Algorithm 1 离 CRB 还有多远，这能为方法的 statistical efficiency 提供严格 benchmark。

- 直接相关的 **Signal regimes**:

    - Calibration errors ✅（论文核心）

    - Limited snapshots ($T=20$) ✅

    - Low SNR (0 dB) ✅

    - Coherent / correlated sources ❌（未测，是 Current Research Focus 中的重要 regime）

    - Unknown source number ❌（论文假设 $M=3$ 已知）

- 论文与 Current Research Focus 中提到的 SubspaceNet [17] 直接构成同一作者群的延展工作，所以这是**同一研究 line 的最新动态**，必须跟进。


#### 可能的扩展方向

1. **CRB-anchored threshold**: 用 array perturbation 后的 CRB 推导 $\sigma_y^2$ 在 nominal regime 下的解析分布，把 $\tau_\sigma$ 换成 CRB-based analytical threshold → 既消除 manual tuning，又给方法理论上界。

2. **Coupled adaptation of $g_\psi$ and array calibration**: 借鉴 [24] 的 differentiable physical model，把 array 参数 $\delta_n$ 也作为 trainable variable，与 $\psi$ 联合通过 MSIE 优化 → 既能适配 estimator，又能 *识别* 漂移参数本身（可解释性）。

3. **Replace KF with differentiable particle filter / IMM**: 当 state evolution 严重非线性或多模态（机动目标），KF 的 $\tilde{\theta}$ 本身就是坏 label；可换成 differentiable particle filter，且 filter 的内部不确定性 $\Sigma_{\tilde{\theta}}$ 可以直接给 MSIE 加权 → 解决我列在"方法批判"中的 model mismatch 问题。

4. **Coherent-source extension**: 把方法扩展到 coherent source 场景，结合 spatial smoothing 或 forward-backward averaging；innovation-driven 适配在这种场景下应该能有更大 gain，因为预训练模型对相干源极其脆弱。

5. **Test-time adaptation for near-field DoA**: 与 Current Research Focus 中提到的 [Gast et al. 2025] 的 near-field subspace methods 结合——近场 steering vector 对 calibration 更敏感，innovation-driven adaptation 可能价值更大。

6. **Multi-source association inside the loss**: 在 MSIE 中加入 Hungarian / soft-assignment，让 loss 在源 ID 错位时仍稳定，解决"方法批判"里指出的 association 风险。

7. **Frequency-domain / subspace-domain innovation**: 不只用 DoA-space innovation，还可以用 covariance-space 或 noise-subspace-projection 的 innovation 当 surrogate signal —— 利用更多 array 结构信息。


#### 后续研究问题

> 全部采用 capability-claim 形式 "Can we achieve X on Y, measured by Z?"，且锚定 Current Research Focus 的具体技术/regime。

1. **Q1 (核心 unsupervised adaptation)**: Can we achieve unsupervised online adaptation of a SubspaceNet-style hybrid DoA estimator on **coherent-source ULA scenarios with array calibration drift**, measured by RMSPE within 25% relative gap of an oracle supervised online learner over 1000 blocks?

2. **Q2 (CRB-anchored threshold)**: Can we design a **CRB-based analytical trigger threshold $\tau_\sigma$** for innovation-driven concept drift detection on DoA estimation, achieving false-trigger rate < 5% and missed-trigger rate < 10% across $\eta \in [0.1, 1.5]$ calibration perturbation strength, *without* per-scenario manual tuning?

3. **Q3 (joint estimator + array calibration adaptation)**: Can we jointly adapt $\psi$ (DNN weights) and $\delta_n$ (physical array calibration parameters) via a single innovation-based loss, achieving lower RMSPE than either alone on *unknown* drift profiles, measured on synthetic ULA with mixed phase + amplitude calibration errors?

4. **Q4 (model-mismatch robustness)**: Can the proposed method maintain RMSPE within 50% of supervised performance under **KF model mismatch** (e.g., real motion is constant-acceleration but KF assumes constant-velocity), measured over $\geq 5$ different mismatch profiles?

5. **Q5 (snapshot-efficient regime)**: Can the unsupervised adaptation maintain its supervised-gap-closing rate down to $T=5$ snapshots (extreme low-snapshot regime), measured by both RMSPE and identifiability (success rate of resolving $M=3$ closely-spaced sources)?

6. **Q6 (cross-architecture generalization)**: Can the same MSIE loss + drift trigger framework work on DA-MUSIC [18] and TransMUSIC [13] with comparable gain, measured by relative RMSPE improvement over the pretrained baseline?


---

## 📎 附录 1: 公式目录

- **Eq.(1)** [Signal Model]

    $$X_i = A_i(\theta_i) [s_i(1), \ldots, s_i(T)] + V_i$$

    | Symbol | Meaning | Dimension/Range |
    | --- | --- | --- |
    | $X_i$ | Block-$i$ snapshot matrix | $\mathbb{C}^{N \times T}$ |
    | $A_i(\theta_i)$ | Steering matrix at block $i$ | $\mathbb{C}^{N \times M}$ |
    | $\theta_i = [\theta_{i,1}, \ldots, \theta_{i,M}]$ | Source DoAs at block $i$ | $[-\pi/2, \pi/2]^M$ |
    | $s_i(t)$ | Source signals at snapshot $t$ | $\mathbb{C}^{M \times 1}$ |
    | $V_i$ | Additive noise | $\mathbb{C}^{N \times T}$, $V_i \sim P_{V_i}$ |
    | $N, M, T$ | antennas / sources / snapshots | $\mathbb{N}$ ($N=9, M=3$, $T \in \{20, 200\}$) |

    💡 标准 narrowband far-field array signal model；下游所有处理的 starting point。
    ← 直接来自 array signal processing 教科书 (Pillai 2012, [2])。

- **理想 ULA steering vector** [Inline equation, 紧随 Eq.(1)]

    $$a_i(\theta) = [1, e^{-j\pi\sin\theta}, \ldots, e^{-j\pi(N-1)\sin\theta}]^\top$$

    | Symbol | Meaning | Dimension/Range |
    | --- | --- | --- |
    | $a_i(\theta)$ | Steering vector for direction $\theta$ | $\mathbb{C}^{N \times 1}$ |

    💡 半波长 ULA 的标准 steering vector；扰动后的 perturbed 版本见 Eq.(6)。
    ← 由远场+半波长间距假设导出。

- **Eq.(2)** [State Evolution / Temporal Model]

    $$\theta_{i+1} = f(\theta_i) + w_i$$

    | Symbol | Meaning | Dimension/Range |
    | --- | --- | --- |
    | $f(\cdot)$ | (一般) 状态演化函数 | 论文未指定具体形式 |
    | $w_i$ | i.i.d. driving noise | covariance $Q$ |

    💡 Markovian state evolution，是后续 KF 设计与 MSIE loss 合理性的物理依据。
    ← Bayesian tracking 的标准状态空间假设。

- **AI-aided estimator** [Inline, Sec. 2.1 末尾]

    $$\hat{\theta}_i = g_\psi(X_i)$$

    | Symbol | Meaning | Dimension/Range |
    | --- | --- | --- |
    | $g_\psi(\cdot)$ | 可微 AI 估计器（如 SubspaceNet） | $\mathbb{C}^{N \times T} \to \mathbb{R}^M$ |
    | $\psi$ | DNN trainable parameters | $\mathbb{R}^P$ |

    💡 整篇论文的更新目标就是 $\psi$。
    ← 通用 AI/MBDL DoA 估计器抽象。

- **Eq.(3)** [Tracking Innovation / Surrogate Signal]

    $$y_i \triangleq \tilde{\theta}_i - g_\psi(X_i)$$

    | Symbol | Meaning | Dimension/Range |
    | --- | --- | --- |
    | $\tilde{\theta}_i$ | Downstream KF 预测/平滑结果 | $\mathbb{R}^M$ |
    | $y_i$ | Innovation (本文宽松定义) | $\mathbb{R}^M$ |

    💡 整个方法的支点：把 KF 平滑与 AI 单步估计的差当作 free supervision signal。
    ← 基于“KF $\tilde{\theta}_i$ 在 KF 假设下是 BLUE，可作 better label”的直觉。

- **Eq.(4)** [Sliding-Window Innovation Variance]

    $$\sigma_y^2(i) = \frac{1}{I} \sum_{j=i-I+1}^{i} |y_j|^2$$

    | Symbol | Meaning | Dimension/Range |
    | --- | --- | --- |
    | $I$ | 滑窗长度 (blocks) | $\mathbb{N}$, 实验取 5 |
    | $|\cdot|$ | 论文未明指，按上下文应为 $\ell_2$ | — |
    | $\sigma_y^2(i)$ | Block-$i$ 处的 innovation 能量平均 | $\mathbb{R}_+$ |

    💡 Concept drift detector 的 test statistic；触发判据是 $\sigma_y^2(i) > \tau_\sigma$。
    ← 由 Eq.(3) 取滑窗经验二阶矩。

- **Eq.(5)** [MSIE Loss]

    $$\mathcal{L}_{W_i}(\psi) = \frac{1}{I} \sum_{j=i-I+1}^{i} |\tilde{\theta}_j - g_\psi(X_j)|^2$$

    | Symbol | Meaning | Dimension/Range |
    | --- | --- | --- |
    | $W_i$ | Block $i$ 处的滑窗集合 ${(X_j, \tilde{\theta}_j)}_{j=i-I+1}^{i}$ | size $I$ |
    | $\mathcal{L}_{W_i}(\psi)$ | Mean-Squared Innovation Error | $\mathbb{R}_+$ |

    💡 等价于把 KF 平滑结果 $\tilde{\theta}_j$ 当 pseudo-label 做 MSE；是 RMSPE 的 unsupervised surrogate。
    ← 由 Eq.(3) 平方求和，再对 $\psi$ 取 differentiable form（注意 $\tilde{\theta}_j$ 在反传时通常 stop-gradient，论文未明示）。

- **GD update rule** [Algorithm 1, line 9]

    $$\psi \leftarrow \psi - \eta \nabla_\psi \mathcal{L}_{W_i}(\psi)$$

    | Symbol | Meaning | Dimension/Range |
    | --- | --- | --- |
    | $\eta$ | Step size / learning rate | $\mathbb{R}_+$ |
    | $S$ | GD 步数 | $\mathbb{N}$, 实验取 5 |

    💡 在每个 trigger 后做 $S$ 步 GD，整个 adaptation horizon 共做 $W \cdot I \cdot S$ 步反传。
    ← 标准 SGD 更新（论文未指定 optimizer）。

- **Eq.(6)** [Perturbed ULA Steering Vector，实验中用]

    $$[a(\theta)]_n = e^{-j 2\pi (d_n + \delta_n) \sin(\theta) / \lambda} + \epsilon_{n,\theta}$$

    | Symbol | Meaning | Dimension/Range |
    | --- | --- | --- |
    | $d_n$ | 第 $n$ 元的标称位置 | $\mathbb{R}$ (半波长间距) |
    | $\delta_n$ | 距离漂移 | $\sim \mathcal{U}(-\eta, \eta)$, $\eta \in \{0.3, 0.9, 1.2\}$ |
    | $\epsilon_{n,\theta}$ | 几何加性噪声 | $\mathcal{CN}(0, 0.9)$ |
    | $\lambda$ | 波长 | $c / 5,\text{GHz}$ |

    💡 实验注入 distribution shift 的具体模型；既在指数项里产生相位扰动，又在 steering vector 上加加性扰动。
    ← 由理想 ULA steering vector + 两类工程性 imperfection 合成。

- **Time-Averaged RMSPE** [Sec. 4.2，metric 定义]

    $$\text{RMSPE} = \sqrt{\frac{1}{I_{\text{tot}}} \sum_{i=1}^{I_{\text{tot}}} d_{\text{periodic}}(\theta_i, \hat{\theta}_i)^2}$$

    | Symbol | Meaning | Dimension/Range |
    | --- | --- | --- |
    | $d_{\text{periodic}}(\cdot, \cdot)$ | $[-\pi/2, \pi/2]$ 周期距离 | $\mathbb{R}_+$ |
    | $I_{\text{tot}}$ | 总 block 数（论文 = 300） | — |

    💡 周期化的角度估计 metric，避免 wrap-around 引起的虚高 squared error。
    ← 来自 [Routtenberg & Tabrikian, 2011]，[25]。

### Formula Dependency Map

```text
Eq.(1) [Signal Model: X_i = A(θ)S + V]
  ↓ 输入给 AI 估计器
[AI estimator: θ̂_i = g_ψ(X_i)]
  ↓ 输入给 KF
Eq.(2) [State evolution: θ_{i+1} = f(θ_i) + w_i] ─→ KF prediction θ̃_i
  ↓                                                        ↓
  └──────────────── Eq.(3) [innovation: y_i = θ̃_i - g_ψ(X_i)]
                         ↓
             ┌───────────┴───────────┐
             ↓                       ↓
      Eq.(4) [σ_y²(i)]        Eq.(5) [MSIE loss L_{W_i}(ψ)]
             ↓                       ↓
 trigger if σ_y²(i) > τ_σ     Eq.(GD update): ψ ← ψ - η ∇L
             └───────────┬───────────┘
                         ↓
                [Algorithm 1 closed loop]

实验侧:
Eq.(6) [Perturbed steering: 注入到 Eq.(1) 的 A(θ) 中产生 distribution shift]
RMSPE [评测指标，与 Eq.(5) 形式同构 → 这是 MSIE 当作 surrogate 的形式依据]
```

---

## 📝 附录 2: 引言参考

### (a) 技术全景

| Technique / Method | Core Idea (1 sentence) | Strengths | Limitations | Representative Refs |
| --- | --- | --- | --- | --- |
| **MUSIC** | 利用接收协方差矩阵的噪声子空间正交性，搜索使谱函数极大的角度 | 高分辨率、不需 grid | 需已知源数、相干源失效、依赖标定 | [1] Schmidt 1986 |
| **Subspace methods (general)** | 把信号/噪声子空间分离，在子空间结构中提取 DoA | 无 grid、有理论保证 | 需 fully calibrated array、非相干源、idealized noise | [2] Pillai 2012 |
| **Pure DNN DoA estimation (MLP/CNN/Attention)** | 端到端从 array 测量映射到 DoA | 灵活、能处理 calibration error / 低 SNR / 少快拍 | 黑箱、对分布漂移敏感、需大量标签 | [4–13] Chen 2020, Cong 2021, Feintuch 2023, Fabiani 2025, Papageorgiou 2021, Wu 2019, Lee 2022, Qin 2023, Lan 2023, Ji 2024 |
| **DNN-augmented MUSIC (DeepMUSIC, FTMR-aided)** | 用 DNN 增强 MUSIC 谱或预处理 | 保留 MUSIC 可解释性 + DL 灵活性 | 仍依赖 MUSIC 假设 | [15] Hoang 2022, [16] Elbir 2020 |
| **SubspaceNet & related** | DNN 生成 covariance surrogate 给 subspace 算法用 | 能在违反标准假设时仍工作（相干源、少快拍） | 训练分布与部署分布需匹配 | [17] Shmuel 2025, [18-21] Merkofer 2024, Xu 2024, Gast 2025, Zohar 2025 |
| **Online/continual learning for receivers** | 部署后用新数据持续训练 | 适应分布漂移 | 需要标签 | [22] Raviv 2024 |
| **Unsupervised DoA: covariance reconstruction** | 用估计的 DoA 重构 covariance 当 loss | 无标签 | 需简化统计假设 | [23] Weißer 2023 |
| **Unsupervised DoA: differentiable MUSIC for calibration** | 把 MUSIC 谱改写成可微，用作 model-based calibration 的 surrogate | 物理可解释 | 只用于 model-based calibration，不训练 DNN | [24] Chatelier 2024 |
| **Concept drift detection (general ML)** | 监测数据分布变化，触发模型更新 | 通用框架 | 通常监测 input 而非 model output | [26] Lu 2018, [27] Uzlaner 2025 |
| **Bayesian tracking (Kalman-type)** | 利用 state-space 模型时序融合估计 | 最优线性融合（KF 假设下） | 依赖正确的 motion model | 本文用作 downstream module |
| **MSPE metric** | 周期化的 squared error，处理角度 wrap-around | 标准 DoA metric | — | [25] Routtenberg & Tabrikian 2011 |

按代际/范式分组：

- **第 1 代 (经典 model-based)**：MUSIC, ESPRIT, subspace methods (Refs [1, 2])

- **第 2 代 (纯 DL)**：MLP/CNN/Attention 端到端 DoA (Refs [4–13])

- **第 3 代 (Model-Based DL / hybrid)**：DeepMUSIC, SubspaceNet, DA-MUSIC, MD-DOA 等 (Refs [15-21])

- **平行线 (online adaptation)**：[22] (general receivers), [23, 24] (DoA unsupervised)

- **平行线 (drift detection)**：[26, 27]

- **下游模块 (本文借用)**：Bayesian tracking / KF


### (b) Gap 分析

- **Gap 是什么**：尽管 AI-aided DoA 在挑战性场景下成功，但其训练-部署同分布假设在现实中**几乎必定失败**（calibration drift, hardware variation, propagation change）。理论上 online learning 能解决，但既有方法都是监督的——**部署时获取真值 DoA 不现实**。

- 关键引文：

    > "Despite their success, AI-aided DoA estimators face a critical limitation: they typically assume that the deployment data distribution closely matches the one used during training. In practice, this assumption rarely holds, as the underlying statistical models vary over time and across devices." (Sec. 1, ¶3)

    > "Attempts to relax the reliance on labels have led to limited unsupervised formulations. The work [23] proposed to reconstruct the covariance from estimated DoAs, which is valid under simplified statistical assumptions, while [24] translated MUSIC spectra into surrogate unsupervised metrics used for model-based calibration rather than DNN training." (Sec. 1, ¶3)

- **Gap 性质**：**实践 (practical) + 方法论 (methodological) 双重**：

    - Practical: 部署中没有真值——这是个客观工程约束。

    - Methodological: 现有 unsupervised 方案要么需要强统计假设 [23]，要么不能用于训练 DNN [24]——存在"无监督 + DNN-trainable"的方法论真空。

    - 不算**理论 (theoretical)** gap：论文没声称要提供新的 identifiability / CRB 结果。


### (c) 本文定位

- **如何回应 gap**：转换视角，从"局部估计器"上升到"系统级 pipeline"，借用 pipeline 已有的 downstream tracker 来产生 free supervision——既绕开了"真值不可得"，也避开了对信号统计模型的强假设。

- **相对于各类 prior art 的优势**：

    - 相对于经典 MUSIC/subspace methods：能处理 calibration drift。

    - 相对于纯 DNN / SubspaceNet 静态部署：能 online 适配分布漂移。

    - 相对于 supervised online learning：不需要部署时的真值标签。

    - 相对于 [23]（covariance reconstruction）：不依赖简化的统计假设；用 system-level signal 而非 signal-level constraint。

    - 相对于 [24]（differentiable MUSIC）：能直接驱动 DNN 训练，而不仅是 model-based calibration。

- **关键 transition**:

    > "In this work, we propose a framework for unsupervised adaptation of AI-aided DoA estimation methods by adopting a holistic system-level viewpoint. While providing an unsupervised assessment of DoA recovery in isolation is inherently challenging, we recognize that such algorithms are rarely deployed standalone." (Sec. 1, ¶4)


### (d) 引言叙事结构

1. **[Background & Importance]**: DoA 估计是无线通信、雷达、导航的基础。(¶1)

2. **[Prior Art Category 1 — 经典 model-based]**: MUSIC 和子空间方法 → 强 → 但依赖 calibrated array / non-coherent / idealized noise。(¶1)

3. **[Prior Art Category 2 — 纯 AI/DL]**: MLP/CNN/Attention → 在挑战场景下强 → 但黑箱。(¶2 前半)

4. **[Prior Art Category 3 — Model-Based DL]**: SubspaceNet, DA-MUSIC 等 → 同时具备可解释性与灵活性。(¶2 后半)

5. **[The Gap]**: 所有 AI-aided 方法假设训练-部署同分布；漂移破坏假设；online learning 需要真值；现有 unsupervised 方案 [23, 24] 局限明显。(¶3)

6. **[Proposal]**: 借用 downstream tracker 的 innovation 作为 free supervision，做 unsupervised online adaptation；提出 trigger + GD 算法。(¶4)

7. **[Key Results Preview]**: 数值实验显示方法在时变环境下可靠且灵活地工作。(¶4 末)

8. **[Paper Organization]**: Sec. 2 系统模型；Sec. 3 方法；Sec. 4 实验；Sec. 5 结论。(¶5)


这个叙事结构是一个**经典的"问题驱动 + system-level 突破"模板**——可复用：先把 prior art 按代际分组评 (步骤 2-4)，然后在 §3 集中指出"所有这些都在 estimator-level 操作"，第四步抬升到 system-level 提出 free supervision，转折非常自然。

### (e) 引用地图

| Role in Narrative | References | How Cited |
| --- | --- | --- |
| Problem importance / application | 无显式引文，仅用泛指 | “wireless communications, radar, and navigation” 作 background |
| Classical / foundational methods | [1] Schmidt 1986; [2] Pillai 2012 | Prior art：称赞 high resolution，然后批判 calibration assumption |
| Recent advances — pure DNN DoA | [4] Chen 2020; [5] Cong 2021; [6] Feintuch 2023; [7] Fabiani 2025; [8] Papageorgiou 2021; [9] Wu 2019; [10] Lee 2022; [11] Qin 2023; [12] Lan 2023; [13] Ji 2024 | 群体引用，证明“DL DoA”是活跃方向 |
| Recent advances — Model-Based DL | [14] Shlezinger & Eldar 2023; [15] Hoang 2022; [16] Elbir 2020; [17] Shmuel 2025; [18-21] Merkofer 2024, Xu 2024, Gast 2025, Zohar 2025 | 论文方法 build on SubspaceNet [17]，定位为同一 line 的延续 |
| Online / continual learning baseline | [22] Raviv 2024 | 引用为“理论上能做但需要标签”的 supervised baseline |
| Closest unsupervised prior work | [23] Weißer 2023; [24] Chatelier 2024 | 核心 gap-defining references，被点名指出局限 |
| Performance metric | [25] Routtenberg & Tabrikian 2011 | Methodological foundation for 评测 metric |
| Concept drift theory | [26] Lu 2018; [27] Uzlaner 2025 | 用于支撑“trigger-based adaptation”的方法论合法性 |
| Survey / state-of-the-art reference | [3] Al Kassir 2022 | 用于支撑“AI 在挑战性场景下成功”的 generic claim |

#### 🔍 引言批判

- **对 [23] [24] 的批判略显简化** → Intro 把 [23] 概括为"valid under simplified statistical assumptions"、把 [24] 概括为"used for model-based calibration rather than DNN training"——这两句话作为 dismissal 的依据非常粗略；尤其 [24] 的 differentiable MUSIC 框架原则上是可以驱动 DNN 的，论文没有展开为什么不行。→ 威胁"我们是 first to do unsupervised DNN-trainable DoA adaptation"的 novelty claim。

- **缺少对 Bayesian tracking + AI estimator joint design 的 prior art 调研** → 在 target tracking / SLAM 社区，"用 tracker residual 训练上游网络"已经有不少工作（如 differentiable particle filters, end-to-end tracking）。论文没有 cite 这些 cross-domain 工作，使得 "system-level viewpoint" 的 novelty 被夸大。→ 威胁 contribution 1 (system-level perspective) 的相对新颖度。

- **"distribution shifts caused by calibration drifts, hardware variations, or changing propagation conditions" 这一三连承诺与实验只有 calibration drift 的覆盖度严重不匹配**——属于 intro 的过度承诺 (overclaim)。

- **Pure DNN 与 MBDL 两类的代表性引文众多，但缺乏批判深度** → 引文 [4-13] 一口气列举十篇，没有内部区分"哪些方法在 calibration drift 上具体怎么 fail"。→ 弱化了"AI 方法对漂移敏感"这一论断的具体说服力。

- **没有引入 SubspaceNet 在 calibration drift 下的具体 failure 数据或图** → Intro 直接 assume "AI methods are sensitive to distribution shifts"，但这本来应该是 motivation 的核心数据点；放在实验里 Table 1 才看到（pretrained 17.44°）。

- **Intro narrative 的 "system-level" 抬升非常优雅，但容易让读者忽略一个事实**：如果 downstream tracker 不存在或不可信（如纯快照式定位），整个方法基础就消失了——这个边界条件 intro 没提示，等到 Sec. 3.3 才隐含承认。
