# 通用项目文件夹结构（基于当前工作区提炼）

目标：在重构新项目时，尽量保持你现在的工作习惯与目录组织方式，只替换具体业务代码与数据。

技术约定（固定）：

- `outputs/` 由 Hydra 的 `hydra.run.dir` 管理（按时间戳自动创建运行目录）。
- 训练框架采用 PyTorch Lightning（`src/train` + `LightningModule` + `DataModule`）。

## 1. 推荐顶层结构

```text
project_root/
├── README.md
├── requirements.txt
├── LICENSE
├── .gitignore
├── configs/
│   ├── config.yaml
│   ├── default.yaml
│   ├── callbacks/
│   ├── data/
│   ├── model/
│   └── trainer/
├── data/
│   ├── raw/
│   └── processed/
├── src/
│   ├── data/
│   │   ├── lit_datamodule.py
│   │   └── components/
│   ├── models/
│   │   ├── lit_module.py
│   │   └── components/
│   ├── train/
│   │   ├── __main__.py
│   │   └── warmstart_*.py
│   ├── eval/
│   │   └── metrics/
│   └── utils/
├── scripts/
├── tests/
├── notebooks/
├── figures/
│   └── final/
├── outputs/
│   ├── checkpoints/
│   ├── logs/
│   └── figures/
├── docs/
│   ├── plan/
│   ├── Data/
│   ├── problem_formulation/
│   ├── reference_original/
│   ├── reference_conclu/
│   ├── <paper_or_project_name>/
│   └── prompts/
```

## 2. 各目录职责（通用约定）

- `configs/`: 所有可复现实验配置（Hydra 风格）。
- `data/raw/`: 原始数据（只读来源，不手工改内容）。
- `data/processed/`: 预处理产物、特征、缓存。
- `src/`: 核心源码，只放“可复用逻辑”，不放一次性脚本。
- `src/train/`: Lightning 训练入口与训练流程编排（推荐 `python -m src.train`）。
- `src/models/lit_module.py`: LightningModule（训练/验证步骤、优化器配置）。
- `src/data/lit_datamodule.py`: Lightning DataModule（数据加载与 batch 管理）。
- `scripts/`: 一次性或工程化脚本（转换、清洗、批处理、辅助工具）。
- `tests/`: 单测/集成测试/对比测试脚本。
- `notebooks/`: 探索、原型验证、结果复盘。
- `figures/`: 长期保留的图（论文图、关键结果图）。
- `outputs/`: Hydra 运行目录根路径（如 `outputs/YYYY-MM-DD/HH-MM-SS/`），存放每次 run 的 `.hydra/`、日志、checkpoint、中间图；可定期清理。
- `docs/`: 方法文档、计划、论文笔记、参考文献整理。
- `docs/prompts/`: 与 AI 协作的约束、提示模板、执行规范。

## 3. 重构到新项目时的“保留不变”骨架

建议你在新项目继续保留以下路径不变（只改内部文件内容）：

- `configs/{data,model,trainer,callbacks}`
- `src/{data,models,train,eval,utils}`
- `data/{raw,processed}`
- `tests/`, `scripts/`, `notebooks/`
- `figures/`, `outputs/`
- `docs/{plan,reference_original,reference_conclu}`

这样可以最大程度复用你现有的开发节奏：

- 配置驱动训练入口（`python -m src.train`）
- 数据/模型/训练职责分离
- 实验产物与长期资产（文档、图）分层

## 4. 命名与落盘建议

- 数据命名沿用参数化模式：`<scenario>_<key1>{...}_<key2>{...}.npz`（按项目需要扩展参数键名即可）。
- 图像命名与数据文件同源，便于回溯。
- `outputs/` 仅放可再生内容，`figures/final/` 放最终保留版本。
- `docs/reference_original/` 放原文，`docs/reference_conclu/` 放你的总结。

## 5. 最小迁移清单（复制到新仓库）

1. 先创建目录骨架（不拷贝旧实验产物）。
2. 拷贝 `configs/` 与 `src/` 的基础框架。
3. 保留 `tests/` 的入口脚本，先保证可跑通。
4. 再逐步迁移 `scripts/` 与 `notebooks/`。
5. 最后迁移 `docs/` 中与你新项目相关的计划与参考。
