# **Project Architecture Context for Codex/Copilot**

## **1. High-Level Architecture**

This project follows a strict **Modular Deep Learning Engineering** standard. **Tech Stack:**

0. **Framework:** PyTorch
1. **Wrapper:** PyTorch Lightning (for training loops and hardware management)
2. **Configuration:** Hydra (for dependency injection and parameter management)

## **2. Directory Structure Standards**

All code generation must strictly adhere to this file hierarchy:

```
 project_root/
 ├── README.md                # Documentation (Installation, Usage, Architecture)
 ├── requirements.txt         # Dependencies (pip freeze > requirements.txt)
 ├── .gitignore               # Git ignore (Ignore data/ and outputs/)
 ├── Makefile                 # For automation: make train, make clean
 ├── configs/                 # [Hydra] Configuration Center
 │   ├── config.yaml          # Main entry point (defaults)
 │   ├── model/               # Model architecture configs (defines _target_)
 │   │   └── resnet.yaml      # (Example) Config for ResNet model
 │   ├── data/                # DataModule instantiation configs
 │   │   └── mnist.yaml       # (Example) Config for MNIST dataset
 │   ├── trainer/             # PL Trainer configs (min_epochs, accelerator, etc.)
 │   │   └── default.yaml
 │   └── callbacks/           # PL Callbacks (EarlyStopping, ModelCheckpoint)
 ├── data/                    # Data storage (Raw & Processed)
 │   ├── raw/                 # Immutable input data. Read directly from here if no processing is needed.
 │   └── processed/           # (Optional) Intermediate data. Use only if raw data requires cleaning/ETL.
 ├── docs/                    # Project documentation (API, Design docs)
 ├── notebooks/               # Jupyter Notebooks (EDA & Prototyping ONLY)
 │   ├── 01_data_exploration.ipynb
 │   └── 02_model_prototyping.ipynb
 ├── skills/                  # [Agent] Markdown specifications for AI skills/tools
 │   └── analysis_skill.md    # (Example) Skill description for LLM usage
 ├── outputs/                 # [Hydra] Experiment logs, checkpoints, predictions
 │   ├── multirun/            # Hydra multirun outputs (Grid Search results)
 │   └── YYYY-MM-DD/          # Single run outputs (Time-stamped folders)
 │       ├── .hydra/          # Config snapshot (reproducibility)
 │       ├── checkpoints/     # Model weights (.ckpt) for this run
 │       ├── main.log         # Console output (stdout/stderr) captured by Hydra
 │       ├── lightning_logs/  # [Local] TensorBoard event files (Use for Profiling/Embeddings/Offline)
 │       └── wandb/           # [Cloud] WandB local cache & metadata (Syncs to wandb.ai)
 ├── src/                     # [Python] Source Code
 │   ├── __init__.py
 │   ├── train.py             # Main execution script (Factory pattern)
 │   ├── evaluate.py          # Evaluation script
 │   ├── models/              # [Lightning] Model Logic
 │   │   ├── __init__.py
 │   │   ├── lit_module.py    # LightningModule Definition (Model + Loss)
 │   │   └── components/      # Pure PyTorch modules (Backbones, Blocks, Heads)
 │   ├── data/                # [Lightning] Data Logic
 │   │   ├── __init__.py
 │   │   ├── lit_datamodule.py # LightningDataModule Definition
 │   │   └── components/      # Transformations, raw dataset classes
 │   └── utils/               # Utilities
 │       ├── __init__.py
 │       └── logging_utils.py # Custom logger configurations
 ├── tests/                   # Unit tests (pytest)
 │   ├── test_model.py
 │   └── test_data.py
 └── scripts/                 # Shell scripts (e.g., for cluster submission)
     └── run_experiment.sh
```

## **3. Implementation Rules**

### **Rule #1: The Model (PyTorch Lightning)**

* **DO NOT** write raw training loops (`for epoch in range...`).
* **ALWAYS** subclass `pl.LightningModule`.
* **Decoupling:** The model `__init__` should accept backbone objects or architecture parameters, not string names.
* **Pattern:**
  ```
   class LitModel(pl.LightningModule):
       def __init__(self, backbone, learning_rate):
           super().__init__()
           self.save_hyperparameters() # Essential for checkpointing
           self.backbone = backbone    # Injected via Hydra
           # ... define heads/loss ...
   
       def training_step(self, batch, batch_idx):
           # ... compute loss ...
           self.log("train_loss", loss)
           return loss
  ```

### **Rule #2: The Data (PyTorch Lightning)**

* **DO NOT** write dataset loading logic in `train.py`.
* **ALWAYS** subclass `pl.LightningDataModule`.
* **Lifecycle:** Implement `prepare_data` (download), `setup` (split/transform), and `train/val/test_dataloader`.
* **Pattern:**
  ```
   class MyDataModule(pl.LightningDataModule):
       def __init__(self, data_dir, batch_size):
           super().__init__()
           # ...
       def setup(self, stage=None):
           # Assign self.train_set, self.val_set here
           pass
  ```

### **Rule #3: Configuration (Hydra & Dependency Injection)**

* **DO NOT** use `argparse`.
* **DO NOT** hardcode hyperparameters (LR, batch_size, layers) in Python files.
* **Instantiation:** Use the `_target_` key in YAML to define which class to instantiate.
* **YAML Structure Example (** `configs/model/my_model.yaml`):

```
   _target_: src.model_module.lit_module.LitModel
   learning_rate: 0.001
   backbone:
     _target_: torchvision.models.resnet18
     pretrained: true
```

### **Rule #4: The Entry Point (** `src/train.py`)

* The training script must be generic. It should not import specific model classes.
* It must use `hydra.utils.instantiate` to create objects from the config.
* **Pattern:**
  ```
   @hydra.main(config_path="../configs", config_name="config")
   def main(cfg):
       dm = hydra.utils.instantiate(cfg.data)
       model = hydra.utils.instantiate(cfg.model)
       trainer = hydra.utils.instantiate(cfg.trainer)
       trainer.fit(model, dm)
  ```

## **4. Instructions for Code Generation**

When asked to implement a feature:

0. **New Model:** Create the Python class in `src/models/` AND the corresponding YAML config in `configs/model/`.
1. **New Dataset:** Create the DataModule in `src/data/` AND the YAML config in `configs/data/`.
2. **Refactoring:** Convert raw PyTorch loops into `training_step` inside a `LightningModule`.
3. **Hyperparameters:** Move all magic numbers from Python code to the YAML config files.
