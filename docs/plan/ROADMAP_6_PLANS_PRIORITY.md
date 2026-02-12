# 代码提升优先级路线图（6 Plans）

## 目标

在不打断现有可运行路径的前提下，按“收益最大化 + 风险可控 + 工时可执行”顺序推进 6 个改进计划。

## 评估标准

- 收益（Benefit）：5 最高，1 最低
- 风险（Risk）：5 最高，1 最低
- 工作量（Effort）：5 最大，1 最小
- 推荐优先指数：Benefit / (Risk + Effort)

## 优先级总表

| Rank | 计划 | Benefit | Risk | Effort | 优先指数 | 结论 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | plan_测试金字塔补齐 | 5 | 2 | 3 | 1.00 | 先做，回归防护网最高收益 |
| 2 | plan_配置系统强类型化 | 5 | 2 | 3 | 1.00 | 先做，前移配置错误 |
| 3 | plan_数据与轨迹生成治理 | 5 | 3 | 4 | 0.71 | 紧随其后，消除 near/far 数据歧义 |
| 4 | plan_评估与指标可信度 | 4 | 2 | 3 | 0.80 | 与 2/3 并行可行，保障结果可信 |
| 5 | plan_项目结构与技术债清理 | 4 | 3 | 4 | 0.57 | 在功能稳定后推进 |
| 6 | plan_训练性能与资源优化 | 3 | 2 | 3 | 0.60 | 最后做，建立在正确性稳定之后 |

## 推荐执行顺序（Wave）

### Wave 1（稳定性优先）

1. plan_测试金字塔补齐
2. plan_配置系统强类型化

产出：
- near/far + legacy/hydra/lightning 最小回归矩阵
- config 组合合法性校验（field_type × diff_method × objective）

### Wave 2（正确性与可信度）

1. plan_数据与轨迹生成治理
2. plan_评估与指标可信度

产出：
- trajectory 标签契约统一（推荐 angle+range 明确化）
- 训练/验证/评估指标口径一致

### Wave 3（可维护性与效率）

1. plan_项目结构与技术债清理
2. plan_训练性能与资源优化

产出：
- bridge/fallback 收敛、壳代码清理、大文件拆分
- DataLoader/AMP/日志策略优化与 profile 基线

## 每个计划的完成门槛（Definition of Done）

### plan_测试金字塔补齐
- 至少 3 条集成 smoke 持续可跑（far-lightning / near-lightning / legacy）
- 关键输出字段断言稳定（status、trained_model、保存路径）

### plan_配置系统强类型化
- Hydra canonical 配置可独立运行，不依赖临时 `+override`
- near-field 非法配置在启动前失败（显式报错）

### plan_数据与轨迹生成治理
- `trajectory` 数据契约文档化并在训练路径单一实现
- 乱码注释清理完成，核心数据流注释一致

### plan_评估与指标可信度
- train/val/eval 指标口径统一并可追溯
- 关键指标计算函数有最小单测覆盖

### plan_项目结构与技术债清理
- 关键壳模块（pass/NotImplemented）消减
- 训练主链路文件复杂度明显下降（可拆分）

### plan_训练性能与资源优化
- 给出优化前后基线对比（耗时、吞吐、显存/内存）
- 非阻塞 warning（例如 workers）有明确策略

## 建议起手顺序（本周可执行）

1. 从 `plan_高收益收敛` 延伸：先开 `plan_测试金字塔补齐`
2. 然后开 `plan_配置系统强类型化`
3. 之后进入 `plan_数据与轨迹生成治理`

以上顺序可以在不改大框架的情况下，最快降低回归风险并提高可维护性。
