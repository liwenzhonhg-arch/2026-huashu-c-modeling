# 2026 华数杯 C题：面向算电协同的多目标调度优化研究

本目录保存赛题输入、MMW 检查点、两次完整复算证据、现役交付和可复算包。

## 当前结论

- 现役链：`model v43 / code v16 / solve v13 / paper v21 / review v15`。
- 50,000 条任务通过完整硬约束审计；Q4 的联合基准和 17 个情景统一使用 21 个 SOC 状态。
- Q2 为确定性分层有限启发式，Q3 使用统一加权极小极大理想点距离选择；均不宣称全局最优。
- 正式运行默认无墙钟限制；仅显式设置 `MMW_MAX_RUNTIME_SECONDS` 时中断并产生 `incomplete` 隔离证据。
- 可信等级为 `scenario-feasible`：没有独立 Oracle 或全局最优证书。
- 论文 16 页；封面参赛队号仍为空，正式参赛前由队伍填写真实队号并重新编译。

## 快速入口

- 根验证：`python validate_results.py .`
- 论文：`output/paper.pdf`
- 最小提交包：`output/submission.zip`
- 可复算包：`output/reproducibility.zip`
- 求解程序：`output/code/solution.py`
- 结构化结果：`output/data/results.json`
- 双次复算：`ROBUSTNESS_DOUBLE_RUN_COMPARISON.md`
- 基准边界：`output/benchmark.json`

## 目录

- `附件数据/`：六个原始 Excel 附件，只读输入。
- `.mmw/`：版本化流水线检查点。
- `output/runs/`：通过或明确标为 incomplete 的隔离运行证据。
- `output/data/`、`output/figures/`：active solve 快速镜像，图表数据在 `output/data/figure_data/`。
- `output/archive/`：被替换的旧根交付，只归档不清理。
- `tests/`、`tools/`：本 C 题专项验证与确定性运行/导出工具。
