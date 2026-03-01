# SubspaceNet_Update 项目结构

## 项目概述

**SubspaceNet_Update** 是一个用于**波达方向估计（DOA estimation）**和**在线无监督自适应**的深度学习辅助子空间信号处理研究代码库。该项目基于 **SubspaceNet** 论文（Shmuel et al., IEEE Trans. Vehicular Technology, 2025），该方法训练一个卷积自编码器来学习替代协方差矩阵，并将其输入经典子空间算法（MUSIC、Root-MUSIC、ESPRIT）。

### 核心研究方向

- **轨迹感知训练**：生成信号源随时间运动的阵列观测序列（随机游走、正弦加速、乘性噪声动力学）。
- **在线无监督自适应**：基于滑动窗口的在线学习循环，利用卡尔曼滤波器新息统计量作为自监督信号，在部署阶段持续优化 DNN，无需真实 DOA 标签。
- **扩展卡尔曼滤波（EKF/Batch-EKF）**：跟踪信号源轨迹并计算新息统计量（`K*y`、`y*S^{-1}*y`），用作无监督损失信号。
- **参数化评估扫描**：对 SNR、校准误差（eta）、信号源数量（M）、卡尔曼滤波噪声参数进行网格搜索。

### 研究领域

阵列信号处理、基于模型的深度学习、在线学习、DOA 估计、卡尔曼滤波。

### 核心算法

SubspaceNet、DCD-MUSIC、MUSIC、Root-MUSIC、ESPRIT、MLE、扩展卡尔曼滤波、批量 EKF、RMSPE/RMAPE/MultiMoment 损失函数。

---

## 目录结构树

```text
SubspaceNet_Update/
├── .claude/                         # Claude Code 会话日志和本地设置
├── .venv/                           # Python 虚拟环境（uv 管理）
├── DCD_MUSIC/                       # Git 子模块：上游 DCD-MUSIC 代码库（核心模型/数据/评估）
│
├── art/                             # 可视化艺术/海报素材
├── checkpoints/                     # 保存的模型权重文件（.pt）
├── cli/                             # 旧版 CLI 命令（click 框架）
├── config/                          # Python 端配置：schema、loader、utils
├── config_handler.py                # 配置桥接：Pydantic 配置 -> components 字典
├── data/                            # 数据集和 README
├── docs/                            # 项目文档
├── experiments/                     # 实验调试日志和图表
├── figures/                         # 输出图表
├── Makefile                         # 构建目标：train、test、lint、clean
├── main.py                          # 旧版 CLI 入口点（click group）
├── notebooks/                       # Jupyter 笔记本
├── outputs/                         # Hydra 运行输出（带时间戳）
├── plan/                            # 研究规划、论文笔记、参考文献
├── pyproject.toml                   # 项目元数据和依赖（uv/hatchling）
├── README.md                        # 快速入门指南
├── requirements.txt                 # Pip 依赖列表
├── run/                             # Hydra 原生流水线入口和配置
├── scripts/                         # 工具脚本（文献综述自动化）
├── simulation/                      # 卡尔曼滤波实现和仿真运行器
├── src/                             # 核心源代码
├── tests/                           # 单元测试和集成测试
└── temp/                            # 临时文件
```

---

## 文件和目录详细说明

### 顶层文件

| 文件 | 说明 |
| ---- | ---- |
| `README.md` | 快速入门指南：Hydra 入口点、旧版 CLI、常用命令、CLI 到 Hydra 的迁移映射 |
| `pyproject.toml` | 项目元数据（`subspacenet-update` v0.1.0），依赖项（torch、hydra-core、pytorch-lightning、scipy、h5py 等） |
| `requirements.txt` | Pip 格式依赖列表 |
| `Makefile` | `make train`（Hydra）、`make test`（pytest）、`make lint`（ruff+mypy）、`make clean` |
| `main.py` | 旧版 CLI 入口点：通过 Click 提供 `run`、`evaluate`、`simulate`、`online_learning` 命令；支持参数扫描（SNR、eta、M、卡尔曼噪声、4D 网格） |
| `config_handler.py` | YAML/Pydantic 配置与 `Simulation` 消费的 `components` 字典之间的桥接 |
| `findings.md` | 顶层研究发现笔记 |
| `progress.md` | 顶层进度跟踪笔记 |
| `task_plan.md` | 顶层任务规划 |
| `Structure.md` | 通用 ML 项目文件夹结构模板（可跨项目复用） |
| `supervised_trained_model_implementation_plan.md` | 有监督训练基线的规划文档 |
| `arxiv_2203.10231.txt` | SDOA-Net 论文的提取文本（参考文献） |
| `konstantino_unsupervised_adaptation_doa_estimators_downstream_tracking.txt` | 关于通过下游跟踪进行无监督自适应的核心参考论文（Konstantino et al.） |

---

### `DCD_MUSIC/`（Git 子模块）

上游 [DCD-MUSIC](https://github.com/ShlezingerLab/AI-Subspace-Methods) 仓库，包含以下标准实现：

| 路径 | 说明 |
| ---- | ---- |
| `DCD_MUSIC/src/models_pack/` | SubspaceNet、DCD-MUSIC、Deep Root-MUSIC、Trans-MUSIC、Deep Augmented MUSIC、Deep CNN、父模型 |
| `DCD_MUSIC/src/methods_pack/` | MUSIC、Root-MUSIC、ESPRIT、MLE、子空间基类 |
| `DCD_MUSIC/src/system_model.py` | 阵列系统模型（N 天线、M 信号源、SNR、近场/远场、eta 校准误差） |
| `DCD_MUSIC/src/signal_creation.py` | `Samples` 类，生成合成阵列观测数据 |
| `DCD_MUSIC/src/data_handler.py` | 数据集创建工具 |
| `DCD_MUSIC/src/evaluation.py` | 基于模型的评估，RMSPE 计算 |
| `DCD_MUSIC/data/datasets/` | diff-ESPRIT 实验的 HDF5 数据集 |

---

### `src/`（核心源代码）

#### 旧版兼容性垫片（到 `DCD_MUSIC.src` 的薄代理层）

| 文件 | 代理目标 |
| ---- | ---- |
| `src/system_model.py` | `DCD_MUSIC.src.system_model` |
| `src/models.py` | 兼容性重导出 |
| `src/signal_creation.py` | `DCD_MUSIC.src.signal_creation` |
| `src/training.py` | `DCD_MUSIC.src.training` |
| `src/evaluation.py` | `DCD_MUSIC.src.evaluation` |
| `src/criterions.py` | `DCD_MUSIC.src.criterions` |
| `src/data_handler.py` | `DCD_MUSIC.src.data_handler` |
| `src/methods.py` | `DCD_MUSIC.src.methods` |
| `src/plotting.py` | `DCD_MUSIC.src.plotting` |

#### `src/models_pack/`（模型代理）

所有文件（`subspacenet.py`、`dcd_music.py`、`deep_augmented_music.py`、`deep_cnn.py`、`deep_root_music.py`、`parent_model.py`、`trans_music.py`）均为从 `DCD_MUSIC.src.models_pack.*` 的单行兼容性导入。

#### `src/methods_pack/`（算法代理）

同样的模式：`esprit.py`、`mle.py`、`music.py`、`root_music.py`、`subspace_method.py` 均代理到 `DCD_MUSIC.src.methods_pack.*`。

#### `src/data_module/`（数据模块）

| 文件 | 说明 |
| ---- | ---- |
| `__init__.py` | 包导出 |
| `lit_datamodule.py` | `DOADataModule`（PyTorch Lightning DataModule）：构建轨迹或经典 DCD-MUSIC 数据集；确定性地划分 train/val/test（seed=42） |
| `trajectory.py` | `TrajectoryDataHandler` 和 `TrajectoryDataset`：生成多种运动模型的角度/距离轨迹（随机游走、正弦加速、乘性噪声、线性、静态）；调用 `DCD_MUSIC.Samples` 生成每步的阵列观测 `X[N,T]`；堆叠为 `[B, L, N, T]` 批次；支持 HDF5 保存/加载 |
| `components/trajectory.py` | 轨迹相关数据集组件辅助函数 |

#### `src/model_module/`（模型模块）

| 文件 | 说明 |
| ---- | ---- |
| `__init__.py` | 包导出 |
| `lit_module.py` | `LegacyModelModule`（nn.Module 包装器）和 `LegacyLightningModule`（pl.LightningModule 适配器）：处理标准和轨迹批次、近场/远场、训练/验证步骤（MSE/模型特定目标函数） |
| `subspacenet_lightning.py` | `SubspaceNetLightning`：Hydra 可实例化的 SubspaceNet Lightning 包装器；配置优化器（Adam/SGD/RMSprop）和调度器（ReduceLROnPlateau/StepLR/CosineAnnealingLR） |
| `dcd_music_lightning.py` | DCD-MUSIC 模型的 Lightning 包装器 |
| `components/kalman_filters.py` | 从 `simulation.kalman_filter` 重导出 `KalmanFilter1D`、`BatchKalmanFilter1D`、`BatchExtendedKalmanFilter1D`、`ExtendedKalmanFilter1D` |

#### `src/eval_module/`（评估模块）

| 文件 | 说明 |
| ---- | ---- |
| `__init__.py` | 包导出 |
| `evaluation.py` | `Evaluator` 类：计算 RMSPE/RMAPE 指标，运行基于模型的方法对比（ESPRIT、MUSIC 等） |
| `metrics/rmspe_loss.py` | `RMSPELoss`：排列最优 RMSPE（可选距离分量、平衡因子）；处理仅角度和角度+距离两种情况 |
| `metrics/rmape_loss.py` | `RMAPELoss`：相对平均绝对百分比误差变体 |
| `metrics/kalman_loss.py` | `KalmanLoss`：基于卡尔曼滤波新息统计量的损失函数 |
| `metrics/multimoment_innovation_consistency_loss.py` | `MultiMomentInnovationConsistencyLoss`：以 alpha/beta 权重混合 RMSPE 和 RMAPE |

#### `src/trainer_module/`（训练模块）

| 文件 | 说明 |
| ---- | ---- |
| `core.py` | 兼容性垫片，从 `simulation.runner` 重导出 `Simulation` |
| `entry.py` | 替代入口点 |
| `training.py` | 兼容性垫片，重导出 `Trainer`、`TrainingConfig`、`TrajectoryTrainer`、`OnlineTrainer` |
| `training_config.py` | `TrainingConfig` 数据类，包含超参数 |
| `trajectory_trainer.py` | `Trainer`（桩）、`TrajectoryTrainer`（逐步轨迹训练）、`OnlineTrainer` |
| `warmstart_legacy.py` | 旧版热启动模型加载工具 |
| `runtime_runner.py` | `RuntimeRunner` 基类，用于 Hydra 可实例化的运行时 |
| `sandbox.py` | `glrt_changepoint_detection`（GLRT 漂移检测）、`plot_results` 辅助函数 |
| `online_learning.py` | 数据类定义（`KalmanInnovationLoss`、`YSInvYLoss`、`TrajectoryResults`、`WindowEvaluationResult`、`LossMetrics`、`WindowMetrics`、`StepMetrics`、`DOAMetrics`）以及在线学习编排 |

#### `src/trainer_module/simulation/`（仿真编排）

| 文件 | 说明 |
| ---- | ---- |
| `runner.py` | `Simulation` 类：主控制器；组合 `DataPipeline`、`TrainingPipeline`、`EvalPipeline`、`OnlineLearningPipeline`；暴露 `run()`、`run_training()`、`run_evaluation()`、`execute_online_learning()`、`run_scenario()` |
| `data_pipeline.py` | `DataPipeline`：创建/加载轨迹或 DCD-MUSIC 数据集；生成 train/val/test 数据加载器 |
| `training_pipeline.py` | `TrainingPipeline`：运行 Lightning 或旧版轨迹训练，加载预训练权重 |
| `eval_pipeline.py` | `EvalPipeline`：评估 DNN 模型和经典子空间方法；记录 RMSPE/RMAPE；运行卡尔曼滤波后处理 |
| `eval_reporting.py` | `log_evaluation_results`：格式化并打印评估结果表格 |
| `online_learning.py` | `OnlineLearningPipeline`：委托给 `online_learning_parts` 执行完整的多轨迹在线学习循环 |

#### `src/trainer_module/online_learning_parts/`（在线学习流水线）

| 文件 | 说明 |
| ---- | ---- |
| `pipeline.py` | `run_online_learning_impl`：多轨迹在线学习主循环；平均结果；调用 GLRT 漂移检测；调用绘图 |
| `pipeline_run.py` | `_run_single_trajectory_online_learning_impl`：在单条轨迹上运行完整的窗口化在线学习 |
| `pipeline_train.py` | `_online_training_window_impl`：在单个滑动窗口上使用选定损失函数训练 DNN（kalman_innovation、y_s_inv_y、unsupervised_rmape/rmspe、multimoment） |
| `step_processor.py` | `StepProcessor`：处理单个轨迹时间步（DNN 前向传播、EKF 预测+更新、计算所有损失信号） |
| `losses.py` | 在线学习的损失函数注册表和辅助函数 |
| `metrics.py` | 每窗口/每步的指标计算 |
| `metrics_aggregate.py` | 跨窗口和轨迹聚合指标 |

#### `src/utils/`（工具模块）

| 文件 | 说明 |
| ---- | ---- |
| `io.py` | `save_model_state`，模型加载工具 |
| `logging_utils.py` | `setup_logging_from_config`：从 `LoggingConfig` 配置日志记录器 |
| `plotting.py` | 绘图函数：`plot_online_learning_results`、`plot_averaged_online_learning_results`、`plot_online_learning_results_structured`、`plot_scenario_results`、`plot_2d_kalman_noise_sweep`、`plot_loss_vs_scenario`、`plot_eta_comparison_4d_grid`、`plot_performance_improvement_table` |
| `utils.py` | `average_online_learning_results_across_trajectories`、`log_window_summary`、`save_model_state`、`log_online_learning_window_summary` |

---

### `simulation/`（卡尔曼滤波和仿真基础设施）

#### `simulation/kalman_filter/`（卡尔曼滤波实现）

| 文件 | 说明 |
| ---- | ---- |
| `base.py` | `KalmanFilter1D`：用于 DOA 跟踪的标准一维卡尔曼滤波；恒速（随机游走）模型；标量 Q、R、P 的预测/更新 |
| `batch.py` | `BatchKalmanFilter1D`：使用 PyTorch 张量的向量化卡尔曼滤波，用于 B 条轨迹 × M 个信号源 |
| `batch_extended.py` | `BatchExtendedKalmanFilter1D`：支持非线性状态模型的批量 EKF 版本 |
| `extended.py` | `ExtendedKalmanFilter1D`：带可插拔 `StateEvolutionModel` 的 EKF；支持正弦加速和乘性噪声动力学；返回新息 `y`、卡尔曼增益 `K`、`K*y`、`y*S^{-1}*y`、新息协方差 `S` |

#### `simulation/kalman_filter/models/`（状态演化模型）

| 文件 | 说明 |
| ---- | ---- |
| `base.py` | 抽象 `StateEvolutionModel`，提供 `f()`、`F_jacobian()`、`noise_variance()`、`advance_time()` 接口 |
| `sine_accel.py` | `SineAccelStateModel`：振荡模型 `theta_{k+1} = theta_k + kappa * sin(omega_0 * t) + eta_k`；每个信号源有独立的 omega_0、kappa 数组 |
| `mult_noise.py` | `MultNoiseStateModel`：乘性噪声动力学 `theta_{k+1} = theta_k * (1 + amp * sin(omega_0 * t)) + eta_k` |

#### `simulation/losses/`（损失函数）

| 文件 | 说明 |
| ---- | ---- |
| `kalman_loss.py` | 基于卡尔曼滤波的损失函数（基于新息、`y*S^{-1}*y`） |

#### `simulation/runners/`（运行器）

| 文件 | 说明 |
| ---- | ---- |
| `data.py` | 数据流水线运行器 |
| `training.py` | 训练运行器 |
| `evaluation.py` | 评估运行器 |
| `Online_learning.py` | 在线学习运行器 |
| `sandbox.py` | 实验性/沙箱运行器 |

#### `simulation/scenarios.py`

参数扫描场景定义。

---

### `config/`（Python 端配置）

| 文件 | 说明 |
| ---- | ---- |
| `schema.py` | Pydantic `Config` 模型及所有子 schema：`SystemModelConfig`（N、M、T、SNR、field_type、eta、bias）、`DatasetConfig`、`ModelConfig`、`ModelParamsConfig`、`TrainingConfig`、`SimulationConfig`、`EvaluationConfig`、`TrajectoryConfig`、`KalmanFilterConfig`、`OnlineLearningConfig`（含 `OnlineLearningLossConfig`）、`LoggingConfig`、`ScenarioConfig`、`ScenarioDefinition` |
| `loader.py` | `save_config`、`apply_overrides`、`load_config` — YAML 加载和覆盖应用 |
| `utils.py` | `create_system_model`：从 Hydra `DictConfig` 构建 `SystemModel` 的工厂函数 |

---

### `run/`（Hydra 流水线入口）

| 路径 | 说明 |
| ---- | ---- |
| `run/pipeline/training/train.py` | 主 Hydra 入口点：`@hydra.main` -> 通过 `_target_` 实例化 `data`、`model`、`trainer`；构造 `Simulation`；分发到 `scenario_map[scenario]()` |
| `run/conf/config.yaml` | 根 Hydra 配置：从 `default`、`system_model`、`dataset`、`training`、`simulation`、`data`、`model`（subspacenet）、`trainer`、`callbacks`、`runtime` 组装默认配置；设置 `hydra.run.dir` 为带时间戳的 `outputs/` |
| `run/conf/default_config.yaml` | 完整 YAML 配置：系统模型（N=8、M=3、T=200、SNR=10）、数据集（256 样本）、模型（SubspaceNet、ESPRIT diff 方法、RMSPE 损失、tau=8）、训练（Adam、ReduceLROnPlateau）、仿真标志、轨迹（随机游走、std=5°）、卡尔曼滤波、日志 |
| `run/conf/model/subspacenet.yaml` | `_target_: src.model_module.subspacenet_lightning.SubspaceNetLightning`，包含所有超参数 |
| `run/conf/model/dcd_music.yaml` | DCD-MUSIC Lightning 模型配置 |
| `run/conf/training/`、`run/conf/dataset/`、`run/conf/trainer/` 等 | Hydra 组合的子配置组 |
| `run/conf/training_config/` | 场景特定训练配置（如 `Random_basemodel_training_config.yaml`、`SineAccel_base_model_Online_learning_snr_sweep_config.yaml`） |
| `run/conf/eval/` | 评估场景配置（SNR 扫描、信号源数量扫描、校准误差扫描） |
| `run/conf/online_learning_*.yaml` | 不同损失类型的在线学习配置（无监督 RMAPE、RMSPE、`y*S^{-1}*y`、multimoment） |

---

### `cli/`（旧版 CLI）

| 文件 | 说明 |
| ---- | ---- |
| `commands/show.py` | Click 命令，用于显示配置 |
| `commands/save.py` | Click 命令，用于保存配置 |
| `options.py` | 共享 CLI 选项：`config_option`（-c）、`output_option`（-o）、`override_option`（-O） |

---

### `tests/`（单元测试和集成测试）

| 路径 | 说明 |
| ---- | ---- |
| `integration/test_hydra_bridge.py` | Hydra 配置组合和组件实例化桥接的集成测试 |
| `kalman_filter/test_extended.py` | `ExtendedKalmanFilter1D` 的单元测试 |
| `kalman_filter/test_helpers.py` | 卡尔曼滤波测试辅助函数 |
| `kalman_filter/test_models.py` | `SineAccelStateModel`、`MultNoiseStateModel` 的测试 |
| `kalman_filter/standalone_test_extended.py` | 独立（无 pytest）EKF 测试 |
| `kalman_filter/standalone_test_models.py` | 独立状态模型测试 |
| `online_learning/test_integration_contracts.py` | 在线学习流水线接口的契约测试 |
| `online_learning/test_losses.py` | 损失函数单元测试（RMSPE、RMAPE、MultiMoment、KalmanInnovation、YSInvY） |
| `online_learning/test_metrics_aggregate.py` | 指标聚合测试 |
| `online_learning/test_step_processor.py` | `StepProcessor` 单元测试 |

---

### `docs/`（文档）

| 路径 | 说明 |
| ---- | ---- |
| `docs/DOA_structure.md` | 包含 Mermaid 时序图的全面架构描述，涵盖训练/评估/在线学习流水线 |
| `docs/PROJECT_MEMORY.md` | 会话记忆模板，用于记录决策、变更和下一步计划 |
| `docs/Preliminary_knowledge/` | 平面波及信号处理前置知识笔记 |
| `docs/Notes/` | AI 对话笔记（codex、gpt、cc） |
| `docs/reference_conclu/` | 系统化文献综述（PRISMA 流程图、搜索 CSV、筛选清单、全文阅读、论文数字化图表） |

---

### `plan/`（研究规划）

| 路径 | 说明 |
| ---- | ---- |
| `plan/research-proposal.md` | 完整研究提案：SubspaceNet 的多尺度无监督在线自适应；问题陈述、三时间尺度框架、架构、实验 |
| `plan/literature-review.md` | 系统性文献综述文档 |
| `plan/SPICE.md` | SPICE 算法笔记（基于协方差拟合的稀疏参数估计） |
| `plan/paper-notes/` | 约 28 篇论文的结构化笔记（SubspaceNet、DCD-MUSIC、TransMUSIC、DA-MUSIC、DeepFPC、算法展开、DOA 综述、域自适应方法、GNN-DOA、无网格无监督 DOA、近场等） |
| `plan/references.bib` | BibTeX 参考文献库 |

---

### 其他目录

| 路径 | 说明 |
| ---- | ---- |
| `data/` | 数据集目录，含 README；通过 DCD_MUSIC 子模块提供 HDF5 数据集 |
| `experiments/` | 调试日志（`ekf_debug_*.txt`）和轨迹验证图表 |
| `figures/` | 研究级图表（分组柱状图、帕累托前沿、雷达图、小提琴图、ROC、PR 曲线、热力图等） |
| `art/` | 海报生成脚本和创意素材 |
| `notebooks/` | 用于探索性分析的 Jupyter 笔记本（如 `preliminary_knowledge.ipynb`） |
| `scripts/` | 文献综述自动化脚本（筛选、去重、OCR、PDF 转文本） |
| `checkpoints/` | 保存的模型权重文件（`.pt`） |
| `outputs/` | Hydra 带时间戳的运行输出 |
| `temp/` | 临时文件 |

---

## 核心调用链

```text
Hydra 入口：  run/pipeline/training/train.py
    -> config/utils.py::create_system_model()
    -> hydra.utils.instantiate(cfg.data)  -> src/data_module/lit_datamodule.py::DOADataModule
    -> hydra.utils.instantiate(cfg.model) -> src/model_module/subspacenet_lightning.py::SubspaceNetLightning
                                              -> DCD_MUSIC/src/models_pack/subspacenet.py::SubspaceNet
    -> hydra.utils.instantiate(cfg.trainer) -> pl.Trainer
    -> src/trainer_module/simulation/runner.py::Simulation
        -> DataPipeline / TrainingPipeline / EvalPipeline / OnlineLearningPipeline
            -> src/trainer_module/online_learning_parts/pipeline.py（多轨迹循环）
                -> step_processor.py（DNN 前向传播 + EKF 预测/更新）
                -> simulation/kalman_filter/extended.py::ExtendedKalmanFilter1D
                -> src/eval_module/metrics/（RMSPE / RMAPE / MultiMoment 损失）
```
