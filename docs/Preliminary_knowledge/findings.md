# Findings

## Metadata
- Created At: 2026-02-20 14:10:10 CET
- Last Updated At: 2026-02-20 14:16:37 CET

## Discoveries
- [2026-02-20 14:10:10 CET] 当前目录已有 `preliminary_knowledge.md` 与 `preliminary_knowledge.ipynb`，后者由单 markdown + 单 code cell 组成。
- [2026-02-20 14:11:16 CET] 源 Markdown 文件未包含围栏代码块（```），因此无法直接提取现成代码片段。
- [2026-02-20 14:11:16 CET] 采用“按标题分段 + 每段附一个代码单元”的策略可最大化 code block 数量且保留原文完整性。
- [2026-02-20 14:11:16 CET] 新 notebook 统计为 89 个 markdown cells + 90 个 code cells（总计 179）。 
- [2026-02-20 14:15:47 CET] 用户反馈旧 code cells 缺乏意义，要求替换为“公式运算/图像生成”代码。
- [2026-02-20 14:15:47 CET] 已按章节标题语义分流：`ULA/steering/相位`、`窄带宽带`、`协方差`、`MUSIC/DoA`、`复高斯` 等类别使用对应数学与可视化模板。
- [2026-02-20 14:15:47 CET] 默认兜底代码也包含可计算公式（如积分能量）和图像绘制，避免出现空泛占位代码。 
- [2026-02-20 14:16:37 CET] 已校验新 notebook：`code_cells=90` 且 `formula_or_plot_cells=90`，满足“代码块需为公式运算或图像生成”要求。 
