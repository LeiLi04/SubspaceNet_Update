# SubspaceNet Update — Project Map

> 生成日期：2026-03-09 | 快速导航地图，供代码阅读前定向使用

---

## 项目一句话定义

**深度学习 + 经典子空间方法的混合 DOA（到达方向）估计框架**，支持远场/近场、离线训练、在线自适应，基于 Hydra + PyTorch Lightning 构建。

---

## 目录结构（3层）

```
SubspaceNet_Update/
├── main.py                          # Legacy CLI 入口（Click）
├── config_handler.py                # Legacy 配置组合
├── run/                             # ← 主入口（Hydra + Lightning）
│   ├── pipeline/training/train.py   # PRIMARY 训练脚本
│   └── conf/                        # Hydra 配置树
│       ├── config.yaml              # 根配置（组合默认值）
│       ├── system_model/            # 阵列参数（N, M, T, SNR）
│       ├── dataset/                 # 数据集配置
│       ├── model/                   # 模型选择配置
│       ├── trainer/                 # Lightning Trainer 配置
│       ├── training/                # 优化器、调度器
│       ├── simulation/              # 流程控制（train/eval/online）
│       └── evaluation_configs/      # 预制评估场景
│
├── src/                             # 核心模块
│   ├── data_module/                 # 数据层
│   ├── model_module/                # 模型层
│   ├── trainer_module/              # 训练编排层
│   ├── eval_module/                 # 评估层
│   ├── methods_pack/                # 经典基线方法
│   └── utils/                       # 通用工具
│
├── config/                          # Pydantic 配置 Schema
├── DCD_MUSIC/                       # Git 子模块：外部模型库
│   └── src/
│       ├── models_pack/             # SubspaceNet、DCDMUSIC 实现
│       ├── signal_creation.py       # 信号生成（Samples）
│       └── system_model.py          # 系统参数
├── simulation/                      # 卡尔曼滤波 + 损失函数
├── experiments/                     # 实验运行器
├── notebooks/                       # Jupyter 分析笔记
├── data/                            # 数据集目录
├── checkpoints/                     # 模型检查点
├── outputs/                         # 训练输出
└── plan/                            # 本文件所在位置
```

---

## 模块职责一览

| 模块 | 职责 | 核心类 |
|------|------|--------|
| `src/data_module` | 数据集合成、轨迹生成、数据加载 | `DOADataModule`, `TrajectoryDataHandler`, `TrajectoryDataset` |
| `src/model_module` | 模型 Lightning 封装 | `SubspaceNetLightning`, `DCDMusicLightning`, `LegacyLightningModule` |
| `src/trainer_module` | 训练/评估/在线学习编排 | `Simulation`, `TrainingPipeline`, `EvalPipeline`, `OnlineLearningPipeline` |
| `src/eval_module` | 指标计算、与基线方法对比 | `Evaluator`, `RMSPELoss` |
| `src/methods_pack` | 经典基线方法封装 | `MUSIC`, `ESPRIT`, `RootMUSIC` |
| `src/utils` | I/O、日志、可视化 | `save_model_state`, `setup_logging`, `plot_scenario_results` |
| `config/` | 配置 Schema 与加载 | Pydantic 模型 + Hydra 集成 |
| `simulation/` | 卡尔曼滤波、信号处理 | `KalmanFilter1D`, `ExtendedKalmanFilter1D` |
| `DCD_MUSIC/` | 底层模型实现（子模块） | `SubspaceNet`, `DCDMUSIC`, `Samples` |

---

## 关键类签名

```python
# 数据层
class DOADataModule(pl.LightningDataModule):
    def setup(stage: str = None) -> None       # 构建 train/val/test datasets
    def train_dataloader() -> DataLoader
    def val_dataloader() -> DataLoader
    def test_dataloader() -> DataLoader

# 模型层
class SubspaceNetLightning(LegacyLightningModule):
    def __init__(tau, diff_method, train_loss_type, field_type,
                 learning_rate, system_model)
    def forward(x, sources_num=None) -> θ_pred
    def training_step(batch, batch_idx) -> loss
    def configure_optimizers() -> optimizer [+ scheduler]

class DCDMusicLightning(LegacyLightningModule):  # 近场版本，含距离估计
    def forward(x, sources_num=None) -> (θ_pred, r_pred, source_count_est)

# 编排层
class Simulation:
    def run() -> Dict              # 全流程：训练 → 评估 → 在线学习
    def run_training() -> Dict
    def run_evaluation() -> Dict
    def execute_online_learning() -> Dict

# 评估层
class Evaluator:
    def evaluate(test_dataloader) -> Dict[str, Any]
    # 输出：RMSPE、准确率，NN vs 基线方法对比
```

---

## 数据流（端到端）

```
Hydra Config
    │
    ├─ SystemModelConfig (N=8传感器, M=3信源, T=200快拍, SNR, field_type)
    └─ TrajectoryConfig (轨迹类型: random_walk / sine_accel 等)
           │
           ▼
TrajectoryDataHandler.create_dataset()
    │  FOR t in [0, L):
    │    生成 θ_t → Samples.samples_creation() → X_t ∈ ℝ^(N×T)
    │
    └─ TrajectoryDataset → DOADataModule
           │  60/20/20 split
           ▼
DataLoader: batch [B, L, N, T] + labels [B, L, M]
           │
           ▼
SubspaceNetLightning.forward(x)
    │  DCD_MUSIC.SubspaceNet: 可微子空间方法 (tau阶ESPRIT)
    └─ θ_pred ∈ ℝ^(B×M)
           │
           ▼
Loss (RMSPE) → backward → optimizer.step()
           │
           ▼
Evaluator.evaluate()
    ├─ NN predictions vs MUSIC / ESPRIT / Root-MUSIC
    ├─ 可选：Kalman Filter 平滑
    └─ 输出 metrics → outputs/
           │
           ▼
OnlineLearningPipeline（可选）
    │  滑动窗口检测 loss > threshold → 局部更新模型
    └─ 适应新轨迹分布
```

---

## 信号处理背景（30秒版）

| 概念 | 说明 |
|------|------|
| **DOA 估计** | 从传感器阵列接收信号推断信源方向角 θ |
| **远场** | 信号模型：X = A(θ)S + N，A 只依赖角度 |
| **近场** | 信号模型扩展：A(θ, r)，A 同时依赖角度和距离 |
| **MUSIC / ESPRIT** | 经典子空间方法，作为 NN 的对比基线 |
| **SubspaceNet** | 可微子空间方法嵌入 NN，端到端训练 |
| **在线学习** | 部署后实时自适应，EKF 辅助无监督更新 |

---

## 入口命令

```bash
# 主要入口（Hydra）
python run/pipeline/training/train.py +scenario=training

# Legacy CLI
python main.py run -c run/conf/default_config.yaml

# 评估
python main.py evaluate -m <model_path> --scenario snr --values -10 -5 0 5 10
```

---

## 关键配置参数

| 配置组 | 重要参数 | 含义 |
|--------|----------|------|
| `system_model` | `N, M, T, SNR, field_type, eta` | 阵列几何、信号参数 |
| `dataset` | `samples_size, test_validation_train_split` | 数据集大小与划分 |
| `model` | `type: SubspaceNet / DCD-MUSIC` | 模型选择 |
| `training` | `epochs, batch_size, learning_rate, optimizer` | 训练超参 |
| `simulation` | `train_model, evaluate_model, load_model` | 流程开关 |
| `trajectory` | `trajectory_type, trajectory_length` | 轨迹类型与长度 |
| `online_learning` | `window_size, loss_threshold, learning_rate` | 在线自适应参数 |
