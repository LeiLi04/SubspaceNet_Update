# SubspaceNet_Update 项目结构说明（树状图 + 文件用途）

## 说明
- 扫描范围：`/Users/lilei/PycharmProjects/SubspaceNet_Update`
- 本文覆盖：核心源码、配置、测试、脚本、文档与主要产物目录
- 为保持可读性，以下内容省略了 `.git/`、`__pycache__/`、`.DS_Store` 与大量重复日志文件的逐条展开

---

## 1) 顶层结构

```text
SubspaceNet_Update/
├── README.md                                   # 项目总说明：新旧入口、Hydra 迁移、常用命令
├── Structure.md                                # 目标工程结构模板与职责约定
├── requirements.txt                            # Python 依赖清单
├── .gitignore                                  # Git 忽略规则
├── .gitmodules                                 # Git 子模块声明（包含 DCD_MUSIC）
├── main.py                                     # 兼容 Click CLI 主入口（run/evaluate/simulate）
├── config_handler.py                           # 旧配置装配与组件初始化桥接
├── supervised_trained_model_implementation_plan.md  # 监督训练实现计划文档
├── arxiv_2203.10231.txt                        # 论文/资料文本
├── konstantino_unsupervised_adaptation_doa_estimators_downstream_tracking.txt # 论文资料文本
├── DCD_MUSIC/                                  # 外部/子模块方法实现（对照与复用）
├── art/                                        # 项目视觉素材与生成脚本
├── cli/                                        # Click CLI 参数与命令实现
├── config/                                     # 配置读取与 schema（旧路径）
├── configs/                                    # Hydra 配置中心（主配置路径）
├── data/                                       # 数据目录（raw/processed）
├── docs/                                       # 文档、计划、参考资料、知识笔记
├── experiments/                                # 实验 runner、debug 日志、结果图
├── figures/                                    # 分析图与论文图
├── notebooks/                                  # Jupyter 笔记本
├── outputs/                                    # 训练输出（checkpoints/logs/figures）
├── scripts/                                    # 辅助脚本
├── simulation/                                 # 仿真与 Kalman 滤波模块
├── skills_test/                                # 技能/标注测试目录
├── src/                                        # 主源码（data/models/train/eval/utils）
├── tests/                                      # 单元/集成测试
└── utils/                                      # 通用工具（旧路径）
```

---

## 2) 运行与配置层

```text
configs/
├── config.yaml                                 # Hydra 主入口：defaults 组合与输出目录策略
├── default.yaml                                # 默认总配置
├── default_config.yaml                         # 兼容旧入口的默认配置
├── train_model_config.yaml                     # 训练场景主配置
├── online_learning_config.yaml                 # 在线学习主配置
├── online_learning_unsupervised_rmape_config.yaml  # 无监督在线学习（RMAPE）
├── online_learning_unsupervised_rmspe_config.yaml  # 无监督在线学习（RMSPE）
├── online_learning_y_s_inv_y_config.yaml       # 特定损失/策略在线学习配置
├── ARCHIVE_INDEX.md                            # 历史配置索引
├── callbacks/default.yaml                      # 回调配置
├── data/default.yaml                           # DataModule 参数
├── dataset/default.yaml                        # 数据集参数
├── model/default.yaml                          # 模型参数
├── runtime/default.yaml                        # 运行时参数
├── simulation/default.yaml                     # 仿真参数
├── system_model/default.yaml                   # 系统模型参数
├── trainer/default.yaml                        # Lightning Trainer 参数
├── training/default.yaml                       # 训练参数
├── training_config/
│   ├── default_config.yaml                     # 训练配置默认值
│   ├── nonlinear_tracking_training_config.yaml # 非线性跟踪训练配置
│   └── random_walk_training_config.yaml        # 随机游走训练配置
├── evaluation_configs/
│   ├── README.md                               # 评估配置说明
│   ├── default_eval_config.yaml                # 默认评估配置
│   ├── snr_sweep_config.yaml                   # SNR 扫描配置
│   ├── source_count_config.yaml                # 源数量扫描配置
│   └── calibration_sweep_error_config.yaml     # 校准误差扫描配置
├── Legacy/                                     # 旧版配置存档
│   ├── README.md                               # 旧配置说明
│   ├── eta_scenario.yaml                       # eta 场景配置
│   ├── nonlinear_tracking_config.yaml          # 非线性跟踪旧配置
│   └── nonlinear_trajectory_config.yaml        # 非线性轨迹旧配置
└── Used_for_paper/                             # 论文复现实验配置
    ├── README.md                               # 论文配置说明
    ├── Random_base_model_training_snr_scenario_config.yaml
    ├── Random_basemodel_training_config.yaml
    ├── SineAccel_base_model_Online_learning_snr_sweep_config.yaml
    └── online_learning_config.yaml
```

补充：

```text
config/
├── __init__.py                                 # 包初始化
├── loader.py                                   # 配置加载与覆盖
├── schema.py                                   # 配置模型/schema
└── factory.py                                  # 配置对象工厂
```

```text
cli/
├── options.py                                  # CLI 公共选项（config/output/override）
└── commands/
    ├── __init__.py                             # 命令导出
    ├── save.py                                 # 保存配置命令
    └── show.py                                 # 展示配置命令
```

---

## 3) 主源码层（`src/`）

```text
src/
├── __init__.py                                 # 源码包初始化
├── train.py                                    # 训练入口（兼容/桥接）
├── train_entry.py                              # 训练入口桥接文件
├── training.py                                 # 训练流程封装（旧兼容）
├── data_handler.py                             # 数据处理入口（旧兼容）
├── methods.py                                  # 方法封装入口（旧兼容）
├── models.py                                   # 模型封装入口（旧兼容）
├── system_model.py                             # 系统模型定义（旧兼容）
├── signal_creation.py                          # 信号生成逻辑
├── plotting.py                                 # 可视化工具
├── criterions.py                               # 损失/评价函数入口
├── evaluation.py                               # 评估入口（旧兼容）
├── data/
│   ├── __init__.py                             # data 子包初始化
│   ├── lit_datamodule.py                       # Lightning DataModule
│   ├── trajectory.py                           # 轨迹生成/处理
│   └── components/
│       ├── __init__.py                         # data 组件初始化
│       └── trajectory.py                       # 轨迹组件实现
├── models/
│   ├── __init__.py                             # models 子包初始化
│   ├── lit_module.py                           # LightningModule 封装
│   └── components/
│       ├── __init__.py                         # 模型组件初始化
│       └── kalman_filters.py                   # Kalman 相关模块组件
├── models_pack/                                # 具体模型实现集合
│   ├── __init__.py                             # 包初始化
│   ├── parent_model.py                         # 模型基类
│   ├── subspacenet.py                          # SubspaceNet 模型
│   ├── deep_augmented_music.py                 # Deep Augmented MUSIC
│   ├── deep_root_music.py                      # Deep Root-MUSIC
│   ├── deep_cnn.py                             # CNN 基线模型
│   ├── dcd_music.py                            # DCD-MUSIC 模型
│   └── trans_music.py                          # Transformer/MUSIC 变体
├── methods_pack/                               # 经典 DoA 方法实现
│   ├── __init__.py                             # 包初始化
│   ├── subspace_method.py                      # 子空间法基类/公共逻辑
│   ├── music.py                                # MUSIC 算法
│   ├── root_music.py                           # Root-MUSIC 算法
│   ├── esprit.py                               # ESPRIT 算法
│   └── mle.py                                  # MLE 算法
├── eval/
│   ├── __init__.py                             # eval 子包初始化
│   ├── evaluation.py                           # 评估流程主逻辑
│   └── metrics/
│       ├── __init__.py                         # 指标包初始化
│       ├── rmspe_loss.py                       # RMSPE 指标
│       ├── rmape_loss.py                       # RMAPE 指标
│       ├── kalman_loss.py                      # Kalman 相关损失
│       └── multimoment_innovation_consistency_loss.py  # 创新一致性损失
├── train/
│   ├── __init__.py                             # train 子包初始化
│   ├── __main__.py                             # `python -m src.train` 入口
│   ├── entry.py                                # 训练入口（导入 main.cli）
│   ├── core.py                                 # Simulation 核心编排
│   ├── training.py                             # 训练执行逻辑
│   ├── online_learning.py                      # 在线学习主流程
│   ├── warmstart_legacy.py                     # 旧 warmstart 兼容逻辑
│   ├── runtime_runner.py                       # 运行时执行器
│   ├── sandbox.py                              # 沙盒实验逻辑
│   ├── component_factories.py                  # 训练组件工厂
│   └── online_learning_parts/
│       ├── __init__.py                         # 在线学习子模块初始化
│       ├── losses.py                           # 在线学习损失
│       ├── metrics.py                          # 在线学习指标
│       ├── metrics_aggregate.py                # 指标聚合
│       ├── step_processor.py                   # 单步处理器
│       ├── pipeline.py                         # pipeline 编排
│       ├── pipeline_run.py                     # pipeline 运行封装
│       └── pipeline_train.py                   # pipeline 训练封装
└── utils/
    ├── __init__.py                             # utils 子包初始化
    ├── io.py                                   # I/O 工具
    ├── utils.py                                # 通用辅助函数
    ├── plotting.py                             # 通用绘图函数
    └── logging_utils.py                        # 日志初始化与配置
```

---

## 4) 仿真、测试与脚本层

```text
simulation/
├── __init__.py                                 # 仿真包初始化
├── core.py                                     # 仿真核心逻辑
├── scenarios.py                                # 场景定义
├── kalman_filter.py                            # Kalman 过滤兼容入口
├── losses/
│   ├── __init__.py                             # 损失包初始化
│   └── kalman_loss.py                          # Kalman 损失
├── kalman_filter/
│   ├── __init__.py                             # Kalman 子包初始化
│   ├── base.py                                 # KF 基础实现
│   ├── extended.py                             # EKF 实现
│   ├── batch.py                                # Batch KF
│   ├── batch_extended.py                       # Batch EKF
│   └── models/
│       ├── __init__.py                         # 模型子包初始化
│       ├── base.py                             # 状态模型基类
│       ├── mult_noise.py                       # 多噪声状态模型
│       └── sine_accel.py                       # 正弦加速度状态模型
└── runners/
    ├── __init__.py                             # runners 初始化
    ├── training.py                             # 训练 runner
    ├── evaluation.py                           # 评估 runner
    ├── data.py                                 # 数据 runner
    ├── sandbox.py                              # 沙盒 runner
    ├── Online_learning.py                      # 在线学习 runner
    └── 0.png                                   # 示例/调试图片
```

```text
tests/
├── integration/
│   └── test_hydra_bridge.py                    # Hydra 桥接集成测试
├── kalman_filter/
│   ├── test_extended.py                        # EKF 单测
│   ├── test_models.py                          # Kalman 模型单测
│   ├── test_helpers.py                         # 测试辅助函数
│   ├── standalone_test_extended.py             # 独立 EKF 验证脚本
│   └── standalone_test_models.py               # 独立模型验证脚本
└── online_learning/
    ├── test_integration_contracts.py           # 在线学习契约/接口测试
    ├── test_losses.py                          # 在线学习损失测试
    ├── test_metrics_aggregate.py               # 指标聚合测试
    └── test_step_processor.py                  # step processor 测试
```

```text
scripts/
├── .gitkeep                                    # 保持空目录
└── check_structure.sh                          # 项目目录规范检查脚本
```

```text
experiments/
├── runner.py                                   # 参数扫描/批量实验运行器
├── debug_logs/                                 # EKF 调试日志（历史运行文本）
└── results/                                    # 实验结果图（在线学习对比、轨迹验证等）
```

---

## 5) 文档、数据、产物层

```text
data/
├── README/README.md                            # 数据目录使用说明
├── raw/.gitkeep                                # 原始数据占位
└── processed/.gitkeep                          # 处理后数据占位
```

```text
notebooks/
├── .gitkeep                                    # 占位
├── preliminary.ipynb                           # 初步探索笔记
├── 01_dataset_analysis.ipynb                   # 数据集分析
├── 02_prototype_tests.ipynb                    # 原型测试
└── 03_Figure_vs.ipynb                          # 图表对比实验
```

```text
figures/
├── final/                                      # 最终图（留空/后续存放）
├── 03_figure_vs/                               # Figure-vs 主题图目录
├── dataset_distribution_violins.png            # 数据分布小提琴图
├── dataset_doa_mean_ci.png                     # DoA 均值置信区间图
├── dataset_doa_trajectory.png                  # DoA 轨迹图
├── dataset_noise_snr_distribution.png          # 噪声/SNR 分布图
├── dataset_source_count_distribution.png       # 源数量分布图
├── prototype_pareto_runtime_rmspe.png          # 原型帕累托图
└── prototype_rmspe_barh.png                    # RMSPE 横向柱图
```

```text
outputs/
├── checkpoints/                                # 训练权重输出
├── logs/                                       # 运行日志输出
└── figures/                                    # 运行期图像输出
```

```text
docs/
├── DOA_structure.md                            # DoA 结构笔记
├── PROJECT_MEMORY.md                           # 项目记忆/上下文记录
├── constructure_schedule.md                    # 架构规范与生成规则
├── Data/.gitkeep                               # 数据文档占位
├── problem_formulation/.gitkeep                # 问题定义文档占位
├── prompts/.gitkeep                            # Prompt 模板占位
├── reference_conclu/.gitkeep                   # 文献结论占位
├── reference_original/                         # 原始论文（pdf/md）
├── Preliminary_knowledge/                      # 预备知识文档与 notebook
│   ├── preliminary_knowledge.md                # 知识笔记正文
│   ├── preliminary_knowledge.ipynb             # 公式/图像化 notebook
│   ├── task_plan.md                            # 该子任务 planning 文件
│   ├── findings.md                             # 该子任务发现记录
│   └── progress.md                             # 该子任务进度日志
├── constructure/
│   ├── constructure.md                         # 本文件：项目树状结构与用途说明
│   ├── task_plan.md                            # 本次结构梳理计划
│   ├── findings.md                             # 本次结构梳理发现
│   └── progress.md                             # 本次结构梳理进度
├── ml_paper_writing/                           # 论文写作材料（tex/bib/pptx）
├── plan/                                       # 多个计划任务归档（每个计划含 task_plan/findings/progress）
└── literature/                                 # 文献综述主工作区（检索、筛选、图、脚本、计划）
```

补充：

```text
art/
├── generate_subspacenet_canvas.py              # 画布图生成脚本
├── starfield_viewer.html                       # 星空可视化 HTML
├── starfield_philosophy.md                     # 星空视觉设计说明
├── subspacenet_canvas_philosophy.md            # 画布设计说明
└── subspacenet_canvas_poster_1920x1080.png     # 海报图像
```

```text
DCD_MUSIC/
├── README.md                                   # 子模块说明
├── requirments.txt                             # 子模块依赖（拼写保留原样）
├── main.py                                     # 子模块主入口
├── train_dcd.py                                # 子模块训练脚本
├── run_simulation.py                           # 子模块仿真脚本
├── .gitignore                                  # 子模块忽略规则
└── data/ + src/                                # 子模块数据与源码目录
```

```text
utils/
├── __init__.py                                 # 包初始化
├── logging_utils.py                            # 日志工具（旧路径）
├── plotting.py                                 # 绘图工具（旧路径）
└── utils.py                                    # 通用工具（旧路径）
```

---

## 6) 你可以如何使用这份结构图
- 想找训练主流程：优先看 `src/train/core.py`、`src/train/training.py`、`src/train/online_learning.py`。
- 想改模型：看 `src/models/lit_module.py` 与 `src/models_pack/*.py`。
- 想改 DoA 经典算法：看 `src/methods_pack/*.py`。
- 想改配置：从 `configs/config.yaml` 开始，按 defaults 追踪到各子配置。
- 想跑验证：看 `tests/` 对应子目录。

