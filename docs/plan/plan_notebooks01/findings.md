# Findings: Notebook Import and Path Breakages

## Metadata
- Created At: 2026-02-25
- Last Updated At: 2026-02-25

---

## Root Cause Summary

两份 notebook 的失败由两类变更引起：

1. 配置目录迁移：`configs/` -> `run/conf/`
2. API 迁移：`config/factory.py` 删除，`create_system_model` 迁移到 `config.utils`，`create_model` 不再可用

---

## Notebook 01 (`notebooks/01_dataset_analysis.ipynb`)

### 问题 A：配置扫描路径失效（cell `a580479d`）

- 原代码扫描 `ROOT / "configs"`，目录已迁移。
- 修复为 `ROOT / "run" / "conf"`，并同步错误提示文本。

### 问题 B：factory 导入与默认配置路径失效（cell `c9455c7e`）

- 原导入：`from config.factory import create_system_model`（失效）
- 原路径：`ROOT / "configs" / "default_config.yaml"`（失效）
- 修复：
  - `from config.utils import create_system_model`
  - `ROOT / "run" / "conf" / "default_config.yaml"`

---

## Notebook 02 (`notebooks/02_prototype_tests.ipynb`)

### 问题 C：factory 双导入失效 + 默认配置路径失效（cell `36cd04a6`）

- 原导入：`from config.factory import create_system_model, create_model`
- 原路径：`ROOT / 'configs' / 'default_config.yaml'`
- 修复：
  - `from config.utils import create_system_model`
  - `from src.model_module import SubspaceNetLightning`
  - `ROOT / 'run' / 'conf' / 'default_config.yaml'`

### 问题 D：`create_model(...)` 调用失效（cell `d5df831d`）

- 原调用：`model = create_model(cfg, system_model)`
- 修复：`model = SubspaceNetLightning(system_model=system_model)`

---

## Validation Findings

- 环境无 `jupyter-nbconvert`，无法直接执行 `nbconvert --execute`。
- 使用“IPython-like 顺序执行器”验证（共享内核命名空间 + 注入 `display`）：
  - `01_dataset_analysis.ipynb`：PASS
  - `02_prototype_tests.ipynb`：PASS

---

## Final Scope Check

仅修改以下文件：
- `notebooks/01_dataset_analysis.ipynb`
- `notebooks/02_prototype_tests.ipynb`
- `docs/plan/plan_notebooks01/task_plan.md`
- `docs/plan/plan_notebooks01/findings.md`
- `docs/plan/plan_notebooks01/progress.md`

未修改 production Python 源码。
