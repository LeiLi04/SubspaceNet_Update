# Findings: Konstantino Original Paper vs Current Repository

## DateTime

- 2026-04-26 02:31 CEST

## Scope

- 本次只对照 `docs/original_paper/` 下的 Konstantino 原始论文材料：
  - `docs/original_paper/Konstantino 等 - UNSUPERVISED ADAPTATION OF AI DOA ESTIMATORS VIA DOWNSTREAM TRACKING.pdf`
  - `docs/original_paper/UNSUPERVISED ADAPTATION OF AI DOA ESTIMATORS VIA DOWNSTREAM TRACKING.md`
- 不纳入 `docs/reference_original/` 中其他参考论文。

## Overall Conclusion

- 当前仓库**是围绕 Konstantino et al. 的 tracking-innovation unsupervised adaptation 思路搭建的实验性实现/扩展**。
- 它不是论文 Algorithm 1 的严格逐项复现。
- 已实现的核心方向包括：
  - SubspaceNet 作为 AI DoA estimator。
  - Kalman/EKF 作为 downstream tracker。
  - 记录 innovation、Kalman gain、innovation covariance、`y*S^-1*y` 等统计量。
  - 在线窗口训练，支持用 EKF 输出作为 pseudo-label 的无监督损失。
  - 额外加入 supervised online upper-bound 对照、GLRT 分析、`y*S^-1*y` 指标等扩展。
- 与论文仍有关键差异：
  - 原始 note 中总结的 `sigma_y^2(i) > tau_sigma` 触发逻辑，以及 `plan_whiten_innov.md` 中进一步设计的白化新息触发逻辑，当前都尚未严格接入为代码里的真正触发器。
  - 当前实际启动 online learning 更依赖配置项 `time_to_learn`。
  - 代码中有一些实验性/重构痕迹，需要通过一次 smoke run 确认 far-field online training 是否完整执行。

## Paper Core Extracted From Note

Konstantino 论文的核心管线可以概括为：

```text
X_i -> g_psi(X_i) -> Kalman tracker -> innovation y_i
                         |
                         +-> drift detection
                         +-> unsupervised adaptation loss
```

论文 note 中明确写到：

- AI/DNN DoA estimator 部署时会遇到 calibration drift、hardware variation、propagation change 等分布漂移。
- 部署阶段缺少 ground-truth DoA label，因此需要无监督 adaptation。
- 下游 tracking 机制中的 innovation 可作为 surrogate signal。
- MSIE loss:

```text
L_Wi(psi) = (1/I) * sum_j |theta_tilde_j - g_psi(X_j)|^2
```

- Algorithm 1 使用滑动窗口 innovation 方差 `sigma_y^2(i)` 与阈值 `tau_sigma` 比较，触发后执行若干步 gradient update。

## Repository Mapping

| Paper Component | Repository Evidence | Status |
| --- | --- | --- |
| AI DoA estimator `g_psi` | `DCD_MUSIC/src/models_pack/subspacenet.py` | 已有。SubspaceNet 用 CNN 生成 surrogate covariance，再接 ESPRIT/MUSIC/Root-MUSIC。 |
| Training/eval orchestration | `src/trainer_module/`, `run/conf/` | 已有。仓库已从 legacy CLI 向 Hydra/Lightning 迁移。 |
| Downstream Kalman tracking | `simulation/kalman_filter/extended.py`, `simulation/kalman_filter/batch_extended.py` | 已有。支持 EKF、batch EKF、状态预测和更新。 |
| Innovation statistics | `ExtendedKalmanFilter1D.update()` 返回 `innovation`, `K`, `K*y`, `y*S^-1*y`, `S` | 已有，而且比原论文记录更多统计量。 |
| Online learning pipeline | `src/trainer_module/online_learning.py`, `src/trainer_module/online_learning_parts/` | 已有。窗口级 evaluation/training 已拆分成多个模块。 |
| Unsupervised pseudo-label loss | `src/trainer_module/online_learning_parts/losses.py` 中 `unsupervised_rmspe` / `unsupervised_rmape` | 部分对齐。用 EKF 输出与 pre-EKF 预测构造训练目标，接近 MSIE。 |
| Drift-triggered adaptation | `src/trainer_module/online_learning_parts/pipeline_run.py` | 未严格对齐。当前真正触发主要是 `time_to_learn`；`sigma_y^2 > tau_sigma` 是 original note 中总结的原论文触发逻辑，白化新息触发是 `plan_whiten_innov.md` 的改进方案。 |
| Calibration drift / eta | `DCD_MUSIC/src/system_model.py`, online configs 中 `eta_increment`, `max_eta` | 已有。支持 steering vector distance mismatch / geometry noise 参数。 |

## Important Code Observations

1. `DCD_MUSIC/src/models_pack/subspacenet.py`
   - `SubspaceNet.forward()` 先从输入 snapshots 构造 lagged covariance representation。
   - CNN/deconv 输出 complex surrogate covariance `Rz`。
   - `Rz` 被送入可微 ESPRIT/MUSIC/Root-MUSIC。
   - 这与论文中使用 SubspaceNet 作为 base AI estimator 的设定一致。

2. `simulation/kalman_filter/extended.py`
   - `predict()` 使用 state model 做 EKF 预测。
   - `update()` 计算：
     - innovation `y = z - x`
     - innovation covariance `S = P + R`
     - Kalman gain `K = P / S`
     - `K*y`
     - normalized innovation squared 风格的 `y*S^-1*y`
   - 这些量足够支持原论文的 innovation monitoring，也支持 `plan_whiten_innov.md` 里的白化新息方案。

3. `src/trainer_module/online_learning_parts/losses.py`
   - `training_loss_type == "unsupervised_rmspe"` 时，训练损失为 EKF output vs pre-EKF model output。
   - 这与 MSIE 的 pseudo-label 逻辑相近。
   - 也提供 supervised loss 作为 upper-bound 对照。

4. `src/trainer_module/online_learning_parts/pipeline_run.py`
   - 当前窗口 loss 超过 `loss_threshold` 时只记录日志。
   - 设置 `self.drift_detected = True` 的逻辑被注释掉。
   - 实际 online learning 从 `time_to_learn` 指定的窗口启动。
   - 因此当前结果更像“已知漂移时间后的在线适配实验”，还不是“innovation 自动检测触发适配”的完整闭环。

5. `run/conf/Used_for_paper/SineAccel_base_model_Online_learning_snr_sweep_config.yaml`
   - 参数与论文 note 高度接近：
     - `N: 9`
     - `M: 3`
     - `T: 200`
     - `trajectory_type: sine_accel_nonlinear`
     - `sine_accel_omega0: [-0.15, 0.25, 0.15]`
     - `sine_accel_kappa: [3, -3, 2]`
     - `sine_accel_noise_std: 0.03`
     - `trajectory_length: 300`
   - 这说明该配置很可能就是为了复现实验设定或构建其扩展实验。

## Alignment Assessment

| Area | Alignment | Notes |
| --- | --- | --- |
| Problem setting | High | DOA + SubspaceNet + drift + online adaptation 与论文一致。 |
| Base estimator | High | 使用 SubspaceNet，符合论文实验骨干。 |
| Kalman tracker | High | 已有 EKF/KF，且输出 innovation 相关统计。 |
| MSIE-like loss | Medium | `unsupervised_rmspe` 接近 MSIE，但实现细节用 EKF updated output 和 pre-EKF output。需确认是否应改为论文定义的 predicted/filtered state。 |
| Drift detection trigger | Low/Medium | 有 threshold/GLRT 相关代码和文档，但当前真正触发并非论文 `sigma_y^2 > tau_sigma`。 |
| Monte Carlo protocol | Medium | 支持 dataset_size 多轨迹和 scenario sweep，但是否完全复现 100 次 MC、SNR `{0,5,10}`、eta `{0.3,0.9,1.2}` 需要进一步跑配置核实。注意原论文 Sec.4.1 写 "100 blocks"、Sec.4.2 写 "300 blocks"，存在自洽性问题；本仓库选择了 `trajectory_length=300`。 |
| Paper exactness | Medium/Low | 更像研究代码和扩展框架，不是官方复现。 |

## Risks / Gaps

- **触发机制缺口**：需要把当前 `loss_threshold`、original note 中的 `sigma_y^2` 统计量，或 `plan_whiten_innov.md` 中的白化新息统计量真正接到 `self.drift_detected = True`，否则无法证明“无监督检测触发”。
- **统计量定义需统一**：原论文 Eq.3 把 innovation 定义为 `y_i = theta_tilde_i - g_psi(X_i)`（即 filtered state − measurement，是一种 smoothing residual），并不是标准 KF 术语下的 `z - H * x_pred`；仓库 `extended.py:update()` 返回的 `y` 是 `update()` 内部按标准 KF 卷积出来的 innovation。两者方向相反但平方损失/二次型 `y^T S^-1 y` 等价，文档与代码注释需统一约定，避免在白化新息触发器实现时出现符号歧义。
- **训练目标需核查**：当前 `unsupervised_rmspe` 用 `window_ekf_preds` vs `window_pre_ekf_preds`，需要确认 `window_ekf_preds` 是 updated state 还是 prediction state；论文 MSIE 更强调 tracker 输出作为 pseudo-label。
- **潜在 shape bug**：`pipeline_train.py` 中 far-field 路径有访问 `angles_pred_tensor.size(2)` 的逻辑，但前面常将预测整理为二维 `[1, num_sources]`。需要 smoke run 验证是否导致 training step 被跳过。
- **配置参数单位**：论文里角度/噪声描述混合 degree/radian，仓库也存在 degree/radian 转换，需要统一记录，避免 KF 参数与轨迹生成不一致。

## Recommended Next Steps

- [ ] 跑一个最小 online-learning smoke test，确认 `unsupervised_rmspe` 路径能完成至少 1 个训练窗口。
- [ ] 修复或确认 `pipeline_train.py` 中 `angles_pred_tensor.size(2)` 的 shape 访问。
- [ ] 将 drift trigger 从 `time_to_learn` 改为真正的 innovation statistic 触发，至少先实现论文原版滑窗 `sigma_y^2 > tau_sigma`。
- [ ] 再实现 `plan_whiten_innov.md` 中的白化统计量 `c_i = y_i^T S_i^-1 y_i` 作为改进版触发器。
- [ ] 固定一套对齐论文的实验配置：`N=9, M=3, T in {20,200}, SNR in {0,5,10}, eta in {0.3,0.9,1.2}, trajectory_length=300`。
- [ ] 输出对比表：static pretrained / supervised online / unsupervised MSIE / whitened-trigger MSIE。

## Decision

- 后续应把本仓库定位为：**Konstantino tracking-innovation adaptation 的复现基础 + 白化新息触发机制扩展**。
- 不应把它描述为“两个 original papers 的实现”。
- 当前最值得优先补齐的是 drift detection trigger，而不是继续扩展新的 loss。
