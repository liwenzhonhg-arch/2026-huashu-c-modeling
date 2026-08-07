# 2026 华数杯 C题：面向算电协同的多目标调度优化研究

本仓库是比赛工作目录的完整协作快照，供队员查看、复算和继续修改。仓库刻意保留 `.mmw` 检查点、缓存、日志、各版 LaTeX 构建产物及失败/审批记录，以保证过程可追溯。

## 当前结论

- 流水线八阶段均已审批。
- 现役版本：`analyze v1 / eda v1 / research v1 / model v41 / code v14 / solve v11 / paper v17 / review v11`。
- 50,000 条任务通过完整硬约束审计。
- 最终论文为 16 页。
- 可信等级为 `scenario-feasible`：程序和约束证据真实可复算，但没有独立 Oracle 或全局最优证书。
- 当前封面参赛队号仍为空，正式提交前需要填写真实队号并重新编译。

## 快速入口

- 最终论文：`output/paper.pdf`
- 完整提交包：`output/submission.zip`
- 求解程序：`output/code/solution.py`
- 结构化结果：`output/data/results.json`
- 灵敏度结果：`output/data/sensitivity.json`
- 基准验证：`output/benchmark.json`
- PDF版式报告：`output/layout_quality.json`
- 决策记录：`.mmw/decisions.jsonl`

## 主要目录

- `附件数据/`：六个原始 Excel 数据附件。
- `.mmw/`：MMW 全阶段检查点、配置、日志和审批记录。
- `output/data/`：调度、能源、场景、约束和灵敏度结果。
- `output/figures/`：论文图表及图表数据。
- `output/latex_build/`：各版论文编译现场。
- `output/paper.pdf`：现役论文。

## 关键事实边界

问题二、问题三和问题四均采用有限启发式候选搜索。没有发现改进不等于不存在更优方案；情景内没有达到碳目标也不构成数学不可行性证明。论文和说明必须保留这一边界。

## 协作建议

每位队员使用独立分支，修改后通过 Pull Request 合并；不要直接覆盖其他队员的运行证据。赛题及附件的权利归相应赛事组织方和原作者。
