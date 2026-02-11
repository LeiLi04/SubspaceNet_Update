# PROJECT_MEMORY 使用规范

本文件用于沉淀项目的“外置长期记忆”。
每次与 Codex 协作后，**按一次会话追加一条记录**（append-only，不覆盖历史）。

## 记录原则

- 一次会话对应一条记录。
- 先写结论，再写细节，保证可快速扫描。
- 只记录“可复现、可决策、可交接”的信息。
- 尽量附带文件路径、命令、指标，避免模糊描述。

## 每次必填元素（Required）

1. `DateTime`：日期时间（建议精确到分钟）。
2. `Session Goal`：本次目标（一句话）。
3. `Changes`：改动内容（文件路径 + 做了什么）。
4. `Decision`：关键决策（选了什么方案）。
5. `Rationale`：决策原因（为什么这么做）。
6. `Validation`：验证方式与结果（测试/脚本/人工检查）。
7. `Risks`：已知风险或未解决问题。
8. `Next Steps`：下一步（可直接执行的 TODO 列表）。

## 建议补充元素（Optional）

- `Commands`：关键命令（可复制执行）。
- `Metrics`：关键指标（如 loss、acc、耗时、显存）。
- `Dependencies`：新增/变更依赖与版本。
- `Data/Model`：使用的数据版本、模型 checkpoint、配置文件。
- `References`：相关 issue、PR、文档链接。

## 记录模板（复制使用）

```md
## [YYYY-MM-DD HH:mm] Session: <简短标题>

### DateTime
- <YYYY-MM-DD HH:mm>

### Session Goal
- <本次要解决的问题>

### Changes
- `<path/to/file1>`: <改动说明>
- `<path/to/file2>`: <改动说明>

### Decision
- <采用的方案>

### Rationale
- <原因1>
- <原因2>

### Validation
- <执行了什么验证>
- <结果：通过/失败 + 关键信息>

### Risks
- <风险或遗留问题1>
- <风险或遗留问题2>

### Next Steps
- [ ] <下一步1>
- [ ] <下一步2>

### Commands (Optional)
```bash
<command 1>
<command 2>
```

### Metrics (Optional)

- <指标名>: <数值>

```

## 命名与格式建议

- 统一使用Rome时间或 UTC，并保持一致。
- 文件路径使用仓库相对路径（如 `src/data/trajectory.py`）。
- `Next Steps` 必须是可执行动作，避免“继续优化”这类空泛描述。
```
