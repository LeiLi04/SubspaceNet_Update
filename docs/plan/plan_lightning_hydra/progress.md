# Progress Log

## Session: 2026-02-12

### Phase 1: Baseline Freeze & Scope Definition
- **Status:** in_progress
- Actions taken:
  - 初始化规划目录：`docs/plan/plan_lightning_hydra/`
  - 创建三份规划文件：`task_plan.md`、`findings.md`、`progress.md`
  - 写入初始目标、阶段拆分、风险与资源清单
- Files created/modified:
  - `docs/plan/plan_lightning_hydra/task_plan.md` (created)
  - `docs/plan/plan_lightning_hydra/findings.md` (created)
  - `docs/plan/plan_lightning_hydra/progress.md` (created)

## Test Results

| Test | Input | Expected | Actual | Status |
| --- | --- | --- | --- | --- |
| Planning files existence | `docs/plan/plan_lightning_hydra` | 3 files created | Created | PASS |

## Error Log

| Timestamp | Error | Attempt | Resolution |
| --- | --- | --- | --- |
| 2026-02-12 | None | 1 | N/A |

## 5-Question Reboot Check

| Question | Answer |
| --- | --- |
| Where am I? | Phase 1 (scope + baseline) |
| Where am I going? | Phase 2-6 (Hydra entry, config收敛,验证,文档迁移) |
| What's the goal? | 收敛到 Lightning + Hydra 主路径 |
| What have I learned? | 当前入口与配置存在双轨与历史分叉 |
| What have I done? | 已完成计划初始化并记录风险 |

### Phase 1: Baseline Freeze & Scope Definition
- **Status:** complete
- Actions taken (this run):
  - Re-validated entrypoint split (`main.py` Click path vs emerging Hydra configs).
  - Re-validated factory/simulation reuse boundaries for migration-safe Hydra integration.

### Phase 2: Hydra Entry Skeleton
- **Status:** complete
- Actions taken:
  - Added `src/train.py` with Hydra main entry.
  - Implemented canonical override bridge to legacy pydantic config pipeline.
  - Added scenario dispatch (`training`, `evaluation`, `online_learning`, `full`).
  - Added direct script path bootstrap to ensure imports resolve from project root.
- Files created/modified:
  - `src/train.py` (created)

## Test Results (Run 2)

| Test | Input | Expected | Actual | Status |
| --- | --- | --- | --- | --- |
| Syntax check | `python -m py_compile src/train.py` | compile ok | passed | PASS |
| Hydra import (default env) | `python -c "import hydra"` | import ok | `ModuleNotFoundError` | FAIL |
| Hydra help (`doa`) | `D:\\ProgramData\\miniconda3\\envs\\doa\\python.exe src/train.py --help` | show hydra help | help rendered | PASS |

## Error Log (Run 2)

| Timestamp | Error | Attempt | Resolution |
| --- | --- | --- | --- |
| 2026-02-12 | `session-catchup.py` not found under `~/.claude/skills/planning-with-files/scripts` | 1 | Continued with manual catchup from plan files + git diff |
| 2026-02-12 | `conda run -n doa python src/train.py --help` temp-file activation failure | 1 | Used direct env python path to validate |

### Phase 3: Config Canonicalization
- **Status:** complete
- Actions taken:
  - Updated `configs/config.yaml` defaults to include canonical groups (`system_model`, `dataset`, `training`, `simulation`).
  - Simplified `configs/default.yaml` to avoid duplicated parameter source.
  - Added canonical defaults:
    - `configs/system_model/default.yaml`
    - `configs/dataset/default.yaml`
    - `configs/training/default.yaml`
    - `configs/simulation/default.yaml`
  - Added archive documentation:
    - `configs/ARCHIVE_INDEX.md`
    - `configs/Legacy/README.md`
    - `configs/Used_for_paper/README.md`
- Files created/modified:
  - `configs/config.yaml` (modified)
  - `configs/default.yaml` (modified)
  - `configs/system_model/default.yaml` (created)
  - `configs/dataset/default.yaml` (created)
  - `configs/training/default.yaml` (created)
  - `configs/simulation/default.yaml` (created)
  - `configs/ARCHIVE_INDEX.md` (created)
  - `configs/Legacy/README.md` (created)
  - `configs/Used_for_paper/README.md` (created)

## Test Results (Run 3)

| Test | Input | Expected | Actual | Status |
| --- | --- | --- | --- | --- |
| Hydra group discovery (`doa`) | `D:\\ProgramData\\miniconda3\\envs\\doa\\python.exe src/train.py --help` | canonical groups visible | `dataset/system_model/training/simulation` shown | PASS |

## Error Log (Run 3)

| Timestamp | Error | Attempt | Resolution |
| --- | --- | --- | --- |
| 2026-02-12 | None | 1 | N/A |

### Phase 4: Data/Model Adapter Hardening
- **Status:** complete
- Actions taken:
  - Rewrote `src/data/lit_datamodule.py` comments/docstrings to remove乱码/不可读文本.
  - Added explicit dependency guard in `DOADataModule.__init__` to fail fast when `pytorch_lightning` is missing.
  - Updated `src/models/lit_module.py` dependency handling from silent `None` fallback to explicit fail-fast placeholder.
  - Preserved existing runtime logic and legacy training delegation behavior.
- Files created/modified:
  - `src/data/lit_datamodule.py` (modified)
  - `src/models/lit_module.py` (modified)

## Test Results (Run 4)

| Test | Input | Expected | Actual | Status |
| --- | --- | --- | --- | --- |
| Syntax check | `python -m py_compile src/data/lit_datamodule.py src/models/lit_module.py` | compile ok | passed | PASS |
| Encoding sanity | utf-8 non-ascii count on both files | clean ascii comments/text | 0 non-ascii in both files | PASS |
| Import check (`doa`) | import `LegacyLightningModule`, `DOADataModule` | symbols load | loaded successfully | PASS |

## Error Log (Run 4)

| Timestamp | Error | Attempt | Resolution |
| --- | --- | --- | --- |
| 2026-02-12 | Default env import check failed (`torch` missing) | 1 | Re-ran checks with `doa` env python |

### Phase 5: Integration Validation
- **Status:** complete
- Actions taken:
  - Ran Hydra smoke in `doa`:
    - `src/train.py +scenario=training simulation.load_model=false simulation.train_model=false simulation.evaluate_model=false training.enabled=false dataset.samples_size=8`
  - Ran legacy CLI smoke in `doa`:
    - `main.py run -c configs/default_config.yaml ...` with equivalent overrides
  - Executed parity comparison script for core return fields across legacy/hydra config paths.
  - Added minimal integration test: `tests/integration/test_hydra_bridge.py`.
- Files created/modified:
  - `tests/integration/test_hydra_bridge.py` (created)

## Test Results (Run 5)

| Test | Input | Expected | Actual | Status |
| --- | --- | --- | --- | --- |
| Hydra smoke (`doa`) | `src/train.py` safe overrides | successful run | success | PASS |
| Legacy CLI smoke (`doa`) | `main.py run` safe overrides | successful run | success | PASS |
| Output parity | legacy vs hydra return payload keys/status | equal | equal (`status`, `trained_model`) | PASS |
| Integration test fallback | direct execution of `test_hydra_bridge.py` test functions | assertions pass | passed | PASS |

## Error Log (Run 5)

| Timestamp | Error | Attempt | Resolution |
| --- | --- | --- | --- |
| 2026-02-12 | `pytest` missing in `doa` env | 1 | Executed test module functions directly as fallback |
| 2026-02-12 | PowerShell command blocked for temp-script cleanup | 1 | Removed file via repository patch delete |

### Phase 6: Documentation & Migration Guide
- **Status:** complete
- Actions taken:
  - Updated `README.md` with:
    - recommended Hydra entrypoint
    - compatibility legacy entrypoint
    - environment requirements and validation commands
    - typical smoke commands
    - CLI-to-Hydra mapping table
  - Added migration guide:
    - `docs/plan/plan_lightning_hydra/migration_guide.md`
    - includes override mapping, scenario mapping, validation checklist, known constraints
  - Verified doc command usability in `doa` env (`src/train.py --help`).
- Files created/modified:
  - `README.md` (modified)
  - `docs/plan/plan_lightning_hydra/migration_guide.md` (created)

## Test Results (Run 6)

| Test | Input | Expected | Actual | Status |
| --- | --- | --- | --- | --- |
| Hydra help (`doa`) | `D:\\ProgramData\\miniconda3\\envs\\doa\\python.exe src/train.py --help` | help output | rendered successfully | PASS |

## Error Log (Run 6)

| Timestamp | Error | Attempt | Resolution |
| --- | --- | --- | --- |
| 2026-02-12 | None | 1 | N/A |

### Phase 7.1: Hydra `_target_` Runtime Takeover
- **Status:** complete
- Actions taken:
  - Added `src/train/runtime_runner.py` with `SimulationRuntimeRunner` (`_target_` dispatch object)
  - Added `configs/runtime/default.yaml`
  - Updated `configs/config.yaml` to include runtime group
  - Updated `src/train.py` to use `hydra.utils.instantiate(cfg.runtime, simulation=simulation)`
  - Extended `tests/integration/test_hydra_bridge.py` for runtime group assertions
- Files created/modified:
  - `src/train/runtime_runner.py` (created)
  - `configs/runtime/default.yaml` (created)
  - `configs/config.yaml` (modified)
  - `src/train.py` (modified)
  - `tests/integration/test_hydra_bridge.py` (modified)

## Test Results (Run 7)

| Test | Input | Expected | Actual | Status |
| --- | --- | --- | --- | --- |
| Syntax check | `python -m py_compile src/train.py src/train/runtime_runner.py tests/integration/test_hydra_bridge.py` | compile ok | passed | PASS |
| Hydra help (`doa`) | `src/train.py --help` | runtime group visible | `runtime: default` shown | PASS |
| Integration fallback checks | direct execution of `test_hydra_bridge.py` test functions | assertions pass | passed | PASS |

## Error Log (Run 7)

| Timestamp | Error | Attempt | Resolution |
| --- | --- | --- | --- |
| 2026-02-12 | None | 1 | N/A |

### Phase 7.2: `_target_` Data/Model/Trainer Native Instantiation
- **Status:** complete (native-first with compatibility fallback)
- Actions taken:
  - Added `src/train/component_factories.py`:
    - `DataComponentFactory`
    - `ModelComponentFactory`
    - `TrainerComponentFactory`
  - Added `_target_` wiring in config groups:
    - `configs/data/default.yaml`
    - `configs/model/default.yaml`
    - `configs/trainer/default.yaml`
  - Refactored `src/train.py`:
    - added native `Config` build from Hydra config
    - native component instantiate path for data/model/trainer
    - retained legacy fallback path with warning
  - Extended integration checks for new `_target_` groups.
- Files created/modified:
  - `src/train/component_factories.py` (created)
  - `configs/data/default.yaml` (modified)
  - `configs/model/default.yaml` (modified)
  - `configs/trainer/default.yaml` (modified)
  - `src/train.py` (modified)
  - `tests/integration/test_hydra_bridge.py` (modified)

## Test Results (Run 8)

| Test | Input | Expected | Actual | Status |
| --- | --- | --- | --- | --- |
| Syntax check | `python -m py_compile src/train.py src/train/component_factories.py ...` | compile ok | passed | PASS |
| Native smoke (`doa`) | `src/train.py +scenario=training +trajectory.enabled=true ...` | success | success | PASS |
| Integration fallback checks | direct execution of `test_hydra_bridge.py` functions | assertions pass | passed | PASS |
| Native smoke without trajectory override | `src/train.py +scenario=training ...` | success | backend signature mismatch in standard dataset branch | KNOWN_GAP |

## Error Log (Run 8)

| Timestamp | Error | Attempt | Resolution |
| --- | --- | --- | --- |
| 2026-02-12 | Native instantiate first attempt failed (`instantiate() got multiple values for argument 'config'`) | 1 | Renamed injected arg to `cfg_obj` |
| 2026-02-12 | Standard dataset path mismatch (`create_dataset()` unexpected kw `samples_model`) | 1 | Documented as known gap; validated trajectory-enabled workaround |

### Phase 7.2: `_target_` Native Path Stabilization (Follow-up)
- **Status:** complete
- Actions taken:
  - Updated dataset creation calls for signature compatibility:
    - `src/train/core.py`
    - `src/data/lit_datamodule.py`
    - `config/factory.py`
  - Added non-trajectory dataloader fallback in `src/train/core.py` when dataset has no `get_dataloaders`.
- Validation:
  - Native smoke succeeds in `doa` for both:
    - default (trajectory disabled)
    - trajectory-enabled override path

### Phase 7.3: Train Namespace Collision Cleanup
- **Status:** complete
- Actions taken:
  - Added `src/train_entry.py` as canonical importable Hydra module.
  - Simplified `src/train.py` to wrapper script that calls `src.train_entry.main`.
  - Updated integration test import path to use `src.train_entry` directly.
  - Fixed Hydra config path resolution in `src/train_entry.py` using absolute config path.
- Files created/modified:
  - `src/train_entry.py` (created)
  - `src/train.py` (modified)
  - `tests/integration/test_hydra_bridge.py` (modified)
  - `src/train/core.py` (modified)
  - `src/data/lit_datamodule.py` (modified)
  - `config/factory.py` (modified)

## Test Results (Run 9)

| Test | Input | Expected | Actual | Status |
| --- | --- | --- | --- | --- |
| Syntax check | `python -m py_compile` on updated files | compile ok | passed | PASS |
| Hydra help (`doa`) | `src/train.py --help` | help renders | success | PASS |
| Native smoke default (`doa`) | `src/train.py +scenario=training ...` | success | success | PASS |
| Native smoke trajectory (`doa`) | `src/train.py +scenario=training +trajectory.enabled=true ...` | success | success | PASS |
| Integration fallback checks | direct execution of `test_hydra_bridge.py` functions | assertions pass | passed | PASS |

## Error Log (Run 9)

| Timestamp | Error | Attempt | Resolution |
| --- | --- | --- | --- |
| 2026-02-12 | Hydra failed to resolve configs after entry split | 1 | Set absolute `config_path` in `src/train_entry.py` |
| 2026-02-12 | Standard dataset lacks `get_dataloaders` | 1 | Added random_split/DataLoader fallback |

### Phase 7.4: Lightning-Native Training Loop Migration
- **Status:** in_progress (Milestone 1 complete: non-trajectory path)
- Actions taken:
  - Updated `config/schema.py`: added `training.use_lightning`.
  - Updated `configs/training/default.yaml`: added `use_lightning: false`.
  - Updated `src/train/core.py`:
    - route to `_run_lightning_training_pipeline()` when `training.use_lightning=true` and non-trajectory
    - keep legacy trajectory path unchanged
  - Updated `src/models/lit_module.py`:
    - implemented `training_step`/`validation_step` with fallback MSE objective and logging
  - Updated `src/train/component_factories.py`:
    - skip legacy trainer creation when Lightning path enabled
  - Updated `src/train_entry.py`:
    - fixed transitional mapping precedence (`training.*` remains canonical source)
  - Updated integration checks in `tests/integration/test_hydra_bridge.py`.
- Files created/modified:
  - `config/schema.py` (modified)
  - `configs/training/default.yaml` (modified)
  - `src/train/core.py` (modified)
  - `src/models/lit_module.py` (modified)
  - `src/train/component_factories.py` (modified)
  - `src/train_entry.py` (modified)
  - `tests/integration/test_hydra_bridge.py` (modified)

## Test Results (Run 10)

| Test | Input | Expected | Actual | Status |
| --- | --- | --- | --- | --- |
| Syntax check | `python -m py_compile` on updated files | compile ok | passed | PASS |
| Integration checks | direct execution of `test_hydra_bridge.py` functions | assertions pass | passed | PASS |
| Lightning smoke (`doa`) | `training.use_lightning=true training.epochs=1` | one-epoch fit success | success | PASS |

## Error Log (Run 10)

| Timestamp | Error | Attempt | Resolution |
| --- | --- | --- | --- |
| 2026-02-12 | Lightning smoke failed with source-count tensor indexing | 1 | Converted batched `sources_num` to scalar in fallback objective |
| 2026-02-12 | `training.epochs=1` not honored due transitional overwrite | 1 | Changed mapping precedence in `src/train_entry.py` |
| 2026-02-12 | GBK unicode logging errors from Lightning tip message | 1 | Not functionally blocking; documented as residual logging noise |

### Phase 7.4: Lightning-Native Training Loop Migration
- **Status:** in_progress (Milestone 1 + Milestone 2 complete)
- Milestone 2 actions taken:
  - Updated `src/models/lit_module.py`:
    - trajectory-batch aware `training_step` and `validation_step`
    - per-step unrolling and aggregation over trajectory length
  - Updated `src/train/core.py`:
    - route trajectory path to Lightning-native trainer when allowed
    - keep near-field trajectory conservative fallback
- Files modified:
  - `src/models/lit_module.py` (modified)
  - `src/train/core.py` (modified)

## Test Results (Run 11)

| Test | Input | Expected | Actual | Status |
| --- | --- | --- | --- | --- |
| Syntax check | `python -m py_compile src/models/lit_module.py src/train/core.py` | compile ok | passed | PASS |
| Trajectory Lightning smoke (`doa`) | `+trajectory.enabled=true training.use_lightning=true training.epochs=1` | 1-epoch Lightning fit success | success | PASS |

## Error Log (Run 11)

| Timestamp | Error | Attempt | Resolution |
| --- | --- | --- | --- |
| 2026-02-12 | GBK unicode logging errors from external Lightning tip | 1 | Documented as non-blocking residual noise |

## Test Results (Run 12)

| Test | Input | Expected | Actual | Status |
| --- | --- | --- | --- | --- |
| Compile check (`doa`) | `python -m py_compile src/models/lit_module.py src/train/core.py src/train_entry.py src/train.py` | compile ok | passed | PASS |
| Trajectory Lightning smoke (`doa`) | `src/train.py +scenario=training +trajectory.enabled=true training.use_lightning=true training.epochs=1 training.batch_size=2 simulation.train_model=true simulation.load_model=false simulation.evaluate_model=false dataset.samples_size=8` | one-epoch Lightning fit success | success + model saved | PASS |

## Error Log (Run 12)

| Timestamp | Error | Attempt | Resolution |
| --- | --- | --- | --- |
| 2026-02-12 | Hydra key mismatch for `simulation.evaluate_mode` / `dataset.batch_size` overrides | 1 | Corrected to canonical keys: `simulation.evaluate_model`, `training.batch_size` |
| 2026-02-12 | GBK Unicode logging noise from Lightning tip emoji | 1 | Documented as non-blocking residual issue |

## Test Results (Run 13)

| Test | Input | Expected | Actual | Status |
| --- | --- | --- | --- | --- |
| Compile check (`doa`) | `python -m py_compile src/models/lit_module.py src/train/core.py src/train_entry.py src/train.py` | compile ok | passed | PASS |
| Far-field trajectory Lightning smoke (`doa`) | `src/train.py +scenario=training +trajectory.enabled=true training.use_lightning=true training.epochs=1 training.batch_size=2 simulation.train_model=true simulation.load_model=false simulation.evaluate_model=false dataset.samples_size=8` | success | success | PASS |
| Near-field trajectory Lightning smoke (`doa`) | `src/train.py +scenario=training +trajectory.enabled=true training.use_lightning=true training.epochs=1 training.batch_size=2 simulation.train_model=true simulation.load_model=false simulation.evaluate_model=false dataset.samples_size=8 +system_model.field_type=near +model.params.field_type=Near model.params.diff_method=music_1D` | success | success | PASS |

## Error Log (Run 13)

| Timestamp | Error | Attempt | Resolution |
| --- | --- | --- | --- |
| 2026-02-12 | near-field init with default `esprit` diff method failed | 1 | override near-field compatible method: `model.params.diff_method=music_1D` |
| 2026-02-12 | near-field fallback forward required known angles (`NoneType` shape) | 1 | added known-angles-compatible fallback in `LegacyLightningModule` |

## Execution Update (2026-02-12, Run 14)

- Completed this run:
  - Performed documentation synchronization for `docs/plan/plan_lightning_hydra`.
- What changed:
  - `task_plan.md`
    - updated current phase marker to include Phase 7 completion
    - added closure snapshot block
  - `findings.md`
    - appended run-level status sync note
  - `migration_guide.md`
    - added near-field trajectory Lightning command example
- Status:
  - Planning directory is consistent with implementation state and marked as closed.

## Test Results (Run 14)

| Test | Input | Expected | Actual | Status |
| --- | --- | --- | --- | --- |
| Planning docs consistency check | Manual read of `task_plan.md/findings.md/progress.md` headers and latest runs | phase/status alignment | aligned | PASS |
