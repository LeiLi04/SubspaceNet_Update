# UNSUPERVISED ADAPTATION OF AI DOA ESTIMATORS VIA DOWNSTREAM TRACKING

| **Author:**Shaul Konstantino; Lei Li; Nir Shlezinger; Davide Dardari;                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Journal:,**                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| **Journal Tags:**                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
| **Local Link:**[Konstantino 等 - UNSUPERVISED ADAPTATION OF AI DOA ESTIMATORS VIA DOWNSTREAM TRACKING.pdf](zotero://open-pdf/0_ZBRCHNL3)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| **URL:**                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| **Abstract:***Accurate direction of arrival (DoA) estimation plays a central role in a broad range of applications. While artificial intelligence (AI) has recently emerged as a powerful tool for DoA estimation in challenging scenarios, these AI methods are sensitive to distribution shifts caused by calibration drifts, hardware variations, or changing propagation conditions, and adaptation requires labeled data that may be impractical to obtain during deployment. In this work, we introduce a framework for unsupervised adaptation of AI-based DoA estimators by adopting a holistic system-level perspective. Our key insight is that localization algorithms are rarely applied in isolation, but are instead followed by downstream tracking mechanisms such as Kalman filtering. We exploit the statistical information encoded in the innovations of such tracking algorithms to construct unsupervised performance measures that guide online adaptation of the DoA estimator. We develop a dedicated learning algorithm for continual unsupervised adaptation, and demonstrate through numerical studies that our approach enables reliable and flexible AI-aided DoA estimation in time-varying environments.* |
| **Tags:**                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
| **Note Date:**2026/1/26 13:32:10                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |

## 📜 Research Core

---

> Tips: What was done, what problem was solved, innovations and shortcomings?

---

# ⚙️ 内容概要

本文提出一种面向部署阶段的无监督在线自适应框架，用于在分布漂移存在时持续提升 AI 辅助 DoA 估计器的性能。核心思路是将 DoA 估计器重新置于“系统链路”中审视，因为 DoA 输出通常会进入下游跟踪器（如卡尔曼滤波器 Kalman Filter）。作者利用跟踪器的**新息 (innovation)** 统计量构造无监督度量与损失，从而在无标签条件下触发并驱动在线更新 DNN 参数。

# 💡 创新点

* **系统级无监督信号来源** ：不直接评估 DoA 估计误差，而是利用下游跟踪的统计一致性进行“间接监督”，将难以无监督的 DoA 评估转化为可监测的新息统计。
* **创新统计量驱动的漂移检测与触发更新** ：使用滑窗内新息能量均值作为触发指标，超过阈值后再进行短时梯度更新，避免持续训练带来的不稳定与算力负担。
* **提出并使用 MSIE 作为无监督训练目标** ：以跟踪器的预测结果作为“伪标签”，定义 **平均平方新息误差 (Mean-Squared Innovation Error, MSIE)** ，通过在线最小化该指标来对齐估计器 (estimator) 与跟踪器 (tracker)。
* **在资源受限场景下保持自适应能力** ：在少快照 **$T=20$** 的条件下也展示了明显增益，并且 MSIE 曲线能较好地跟踪监督均方根相位误差 (RMSPE) 的趋势。

# 🧩 不足之处

* **对下游跟踪器质量与模型假设敏感** ：新息是否可靠取决于跟踪器的状态转移模型与噪声设定是否匹配。一旦跟踪器自身失配，可能将错误信号反馈给 DNN，形成“自我强化的偏差”。
* **触发阈值与超参数依赖人工调参** ：文中明确提到阈值需手动调整，以避免对新息分布作强假设。窗口长度、梯度下降 (GD) 步数、步长、触发频率等也依靠经验设定，在线鲁棒性与可迁移性仍需系统化方案。
* **无监督目标可能出现“对齐跟踪器而非对齐真值”** ：MSIE 最小化保证了估计器与跟踪器的一致性，但一致不等于正确。尤其是多源、多目标关联、遮挡、交换等问题可能使一致性成为误导信号。
* **实验范围偏向仿真与特定漂移形式** ：主要针对阵列响应漂移，噪声分布保持高斯且固定，是否覆盖真实硬件多因素漂移与非高斯干扰仍需扩展验证。

# 🔁 研究内容

## 💧 数据

* **阵列与信号** ：均匀线阵 (ULA)，天线数 **$N=9$**，载频 **$5\text{ GHz}$**，信源数 **$M=3$**，DoA 在 **$[-\pi/2, \pi/2]$** 范围内均匀生成。
* **快照** ：两种方案，**$T=200$** 与 **$T=20$**，分别代表充足与受限观测。
* **时变性** ：在 **$100$** 个数据块 (block) 内按给定非线性轨迹变化，并叠加高斯驱动噪声。
* **分布漂移** ：随机数据块引入校准漂移，包含：
* 距离失配 **$\delta_n$** 服从均匀扰动，幅度 **$\eta$** 取 **$\{0.3, 0.9, 1.2\}$**。
* 几何噪声 **$\epsilon_{n,\theta}$** 为复高斯噪声，方差 **$0.9$**。
* 并据此形成扰动导向矩阵 (steering matrix)。

## 👩🏻‍💻 方法

**系统模型与公式逐条记录与分析：**

1. **接收信号模型**
   **$X_i = A_i(\theta_i)[s_i(1), \dots, s_i(T)] + V_i$**
   *解释* ：第 **$i$** 个数据块的观测矩阵 **$X_i$** 由导向矩阵 **$A_i(\theta_i)$** 与源信号快照矩阵相乘得到，再叠加噪声 **$V_i$**。该式将 DoA 估计问题明确为从 **$X_i$** 反推 **$\theta_i$**。
2. **状态演化模型**
   **$\theta_{i+1} = f(\theta_i) + w_i$**
   其中 **$w_i \sim \text{i.i.d.}$**，协方差为 **$Q$**。
   *解释* ：DoA 在数据块间按马尔可夫结构演化。此处 **$f$** 允许非线性，**$Q$** 描述 DoA 变化的不确定性。该结构为卡尔曼类跟踪器提供了理论依据。
3. **AI DoA 估计器**
   **$\hat{\theta}_i = g_\psi(X_i)$**
   *解释* ：DNN 参数为 **$\psi$**，这是需要在线适配的对象。
4. **新息 (Innovation) 定义**
   **$y_i \triangleq \tilde{\theta}_i - g_\psi(X_i)$**
   *解释* ：**$\tilde{\theta}_i$** 是跟踪器的预测或先验一致估计，**$g_\psi(X_i)$** 是当前 DNN 输出。两者的差异反映了估计器与“时间一致性”之间的偏离。该变量是全文无监督信号的核心。
5. **新息能量滑窗统计**
   **$\sigma_y^2(i) = \frac{1}{I} \sum_{j=i-I+1}^{i} \|y_j\|^2$**
   *解释* ：利用长度为 **$I$** 的滑窗对新息的平方范数取均值，得到短期一致性指标。若新息近似零均值且稳定，该量应维持在“名义水平”；分布漂移会导致该统计量上升。
6. **触发规则**
   当 **$\sigma_y^2(i) \gt \tau_\sigma$** 时触发自适应。
   *解释* ：**$\tau_\sigma$** 为阈值。文中提到若假设 **$y_i$** 为零均值高斯分布，可对应卡方检验，但实验中选择手动调参以避免强分布假设。
7. **无监督损失 MSIE**
   **$L_{W_i}(\psi) = \frac{1}{I} \sum_{j=i-I+1}^{i} \|\tilde{\theta}_j - g_\psi(X_j)\|^2$**
   *解释* ：将跟踪器输出 **$\tilde{\theta}_j$** 视为“伪标签”，在窗口内计算均方误差，直接驱动 DNN 输出向跟踪器对齐。关键假设是跟踪器的时间一致性信息足以提供可用的监督信号。
8. **漂移后导向矢量扰动模型**
   **$[a(\theta)]_n = e^{-j 2\pi (d_n + \delta_n) \sin(\theta) / \lambda} + \epsilon_{n,\theta}$**
   *解释* ：**$d_n$** 是名义阵元位置或间距项，**$\delta_n$** 表示距离失配导致的相位误差。加性项 **$\epsilon_{n,\theta}$** 代表几何噪声污染。此式说明漂移会扭曲阵列流形，导致预训练模型失效。

 **Algorithm 1 机制** ：流程包括推断、跟踪、计算新息、更新统计量，并在触发后对 **$L_{W_i}(\psi)$** 执行若干步梯度下降 (GD)。

# 🔬 实验

* **估计器设置** ：使用 SubspaceNet 作为 AI DoA 估计器，DNN 采用卷积自编码器结构，预训练数据来自理想 ULA 的 **$4096$** 个有标签样本。
* **跟踪器设置** ：下游跟踪器为卡尔曼滤波器 (Kalman Filter)，设置状态噪声方差与观测噪声方差均为 **$0.03$**。
* **自适应超参** ：滑窗 **$I=5$**，触发后适配周期为 **$10$** 个窗口，每次触发进行 **$S=5$** 次 GD 更新。
* **指标与结果** ：
* **Table 1** 展示了分布变化后不同 SNR 下的时间平均 RMSPE。Algorithm 1 明显优于静态预训练模型，且接近“在线监督学习”基线。
  ![]()
* **Fig. 2 与 Fig. 3** 展示了漂移发生后触发自适应的过程，性能逐步恢复，MSIE 与 RMSPE 的趋势保持高度一致。
  ![]()

# 📜 结论

作者得出结论：利用下游跟踪的新息可以构建有效的无监督度量与损失，在无标签部署场景下实现 AI DoA 估计器的在线自适应，能够应对校准漂移与环境变化，并在低 SNR 与少快照场景下保持显著性能增益。

# 🤔 个人总结

### 我质疑的点

* 新息统计上升不一定意味着估计器漂移，也可能是跟踪器失配或目标机动导致。需要区分“观测漂移”和“运动模型不准”。
* MSIE 使用跟踪器输出作为伪标签，存在将错误先验强行灌入网络的风险，需要机制保证伪标签的可信度。

### 可改进方向

* **联合自适应** ：同步在线估计跟踪器的参数（如 **$Q, R$**），避免将所有漂移归因于估计器。
* **稳健触发统计量** ：考虑使用白化新息 (whitened innovation)、CUSUM 或 GLRT 监测，减少误触发。
* **伪标签置信度加权** ：根据跟踪器的后验协方差为不同数据块引入权重，降低低置信度时的梯度影响(这个地方， 我提出来了， Sep25，还不错啊哈哈哈哈)。

# 🙋‍♀️ 关键记录

* **系统级洞察** ：DoA 估计不是孤立模块，下游跟踪提供无监督“监督信号”。
* **关键量** ：新息 **$y_i$** 及其滑窗统计 **$\sigma_y^2(i)$**。
* **关键损失** ：MSIE **$L_{W_i}(\psi)$**。
* **关键结果** ：在漂移后显著降低 RMSPE，逼近在线监督学习。

# 📌 待解决问题

* 多源场景下的数据关联与目标交换对新息可解释性及 MSIE 稳定性的影响。
* 漂移来自非高斯干扰时，**$\sigma_y^2$** 触发机制的敏感性与有效性。
* 如何实现超参数（如 **$\tau_\sigma, I, S$**）的自动化选择策略。

# 💭 思想启示

将“下游任务的统计一致性”作为上游模型的无监督学习信号是一种可迁移的范式。若将“预测下一个样本”与“并行 AI 参数化时间演化”纳入框架，可形成闭环：估计器提供观测，预测器提供动态先验，跟踪器负责融合并输出可监测的新息，从而反哺两者的自适应。

---

请问您是否需要我将以上内容导出为 .md 文件，或者对其中的特定公式进行更深入的解析？
