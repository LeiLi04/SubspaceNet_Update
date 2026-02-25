# Task Plan: Fix Notebook Import and Path Breakages

## Metadata
- Created At: 2026-02-25
- Last Updated At: 2026-02-25

---

## Goal

修复 `notebooks/01_dataset_analysis.ipynb` 与 `notebooks/02_prototype_tests.ipynb` 中因目录迁移
（`configs/` -> `run/conf/`）和 `config/factory.py` 删除导致的路径与导入错误，
确保 notebook 可从头到尾执行。

**原则**：仅修改 notebook cells，不改 production Python 代码。

---

## Phases

| # | Phase | Status | Notes |
|---|---|---|---|
| 1 | 确认路径和替代 API | completed | `run/conf/default_config.yaml`、`config.utils.create_system_model`、`SubspaceNetLightning` 均可用 |
| 2 | 修复 `01_dataset_analysis.ipynb` | completed | 已修改 cell `a580479d`, `c9455c7e` |
| 3 | 修复 `02_prototype_tests.ipynb` | completed | 已修改 cell `36cd04a6`, `d5df831d` |
| 4 | 验证执行 | completed | 两个 notebook 均执行通过 |

---

## Phase 1 Output: Confirmed Replacements

```text
configs/                           -> run/conf/
configs/default_config.yaml        -> run/conf/default_config.yaml

from config.factory import create_system_model
-> from config.utils import create_system_model

from config.factory import create_system_model, create_model
-> from config.utils import create_system_model
   from src.model_module import SubspaceNetLightning

create_model(cfg, system_model)
-> SubspaceNetLightning(system_model=system_model)
```

---

## Phase 2 Detail: 01_dataset_analysis.ipynb

- cell `a580479d`
  - `ROOT / "configs"` -> `ROOT / "run" / "conf"`
  - 错误信息 `No YAML files found under configs/` -> `... under run/conf/`
- cell `c9455c7e`
  - `from config.factory import create_system_model` -> `from config.utils import create_system_model`
  - `ROOT / "configs" / "default_config.yaml"` -> `ROOT / "run" / "conf" / "default_config.yaml"`

## Phase 3 Detail: 02_prototype_tests.ipynb

- cell `36cd04a6`
  - 移除 `config.factory` 导入
  - 增加 `from config.utils import create_system_model`
  - 增加 `from src.model_module import SubspaceNetLightning`
  - `ROOT / 'configs' / 'default_config.yaml'` -> `ROOT / 'run' / 'conf' / 'default_config.yaml'`
- cell `d5df831d`
  - `model = create_model(cfg, system_model)` -> `model = SubspaceNetLightning(system_model=system_model)`

---

## Validation

已执行“restart + run-all 等价验证”（顺序执行全部 code cells，共享同一内核命名空间）：

```bash
uv run python -  # custom notebook executor (IPython-like, injected display)
```

结果：
- `01_dataset_analysis.ipynb`: PASS
- `02_prototype_tests.ipynb`: PASS

---

## Files Modified

- `notebooks/01_dataset_analysis.ipynb`
- `notebooks/02_prototype_tests.ipynb`
- `docs/plan/plan_notebooks01/task_plan.md`
- `docs/plan/plan_notebooks01/findings.md`
- `docs/plan/plan_notebooks01/progress.md`

## Errors Encountered

| Error | Attempt | Resolution |
|---|---:|---|
| `jupyter-nbconvert` unavailable (`Jupyter command jupyter-nbconvert not found`) | 1 | 使用自定义顺序执行器（IPython-like）完成 run-all 等价验证 |
| 自定义执行器首次失败：`display` 未定义 | 1 | 注入 `from IPython.display import display` 后通过 |
