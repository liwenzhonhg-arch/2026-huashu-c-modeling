# 代码说明

## 实现思路

本次修订只针对 Q4 检查失败，不改变既有 formulation、硬约束或指标口径。

核心修正如下：

1. Q4 统一任务候选集由 2 个扩展为 3 个，包括基线和两个相互不同的替代方案。
2. 两个替代方案分别执行一次 50000 任务全量硬约束审计，并分别输出审计 CSV。
3. 15 个情景均评价 3 个任务—储能组合，共完成至少 45 次完整评价。
4. 每个情景执行两轮顺序交替：
   - 第一轮比较基线与替代方案一，并分别重建情景储能；
   - 第二轮评价替代方案二并重建储能，再与当前 incumbent 比较。
5. 每轮记录候选、评分、是否接受和当前 incumbent，输出到 `q4_alternation_trace.csv`，同时写入情景表的 `trace` 字段。
6. Q3 和 Q4 基准储能搜索缩减为基线加 4 个代表性充放电分位数组合，以给 Q4 的 45 次情景复算保留运行时间。
7. `results.json` 增加每个情景的成本、碳排放、新能源利用率和峰值净购电功率，并在描述中记录相对统一基准的绝对变化。
8. 运行时若不能完成全部 15 个情景、每情景 3 个组合或两轮交替，将以对应约束 ID 和有限实际值主动失败，不会把不完整结果写成正式答案。

## 依赖库

无需额外安装。使用当前环境中的：

- numpy
- pandas
- matplotlib
- scikit-learn
- Excel 读取引擎

## 运行方式

python solution.py

试跑由宿主设置 `MMW_PILOT=1`，仅生成：

output/data/method_pilot.json

## 预期输出

除原有结果外，本次新增或调整：

- `output/data/q4_task_alternative_1_constraint_audit.csv`
- `output/data/q4_task_alternative_2_constraint_audit.csv`
- `output/data/q4_alternation_trace.csv`
- `output/data/q4_scenario_comparison_v41.csv`
- `output/data/results.json` 中的 15 组情景具体指标
- `output/data/method_runtime.json` 中的三候选、两轮交替和至少 45 次评价证据

最终结论仍只属于 `scenario-feasible` 启发式检查集中的 `best-found`，不声明局部最优、Pareto 最优或全局最优。