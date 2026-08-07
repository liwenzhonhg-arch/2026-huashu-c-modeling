# 代码说明

## 实现思路

错误根因不是运行异常，而是问题四的候选域实现不足：原代码在15个情景中始终使用同一个任务方案，每个情景只评价一个储能候选，因而没有实际执行任务方案比较。

补丁仅修复该问题：

1. 从问题二同类单任务邻域中构造一个与基线不同的任务方案。
2. 对替代方案执行一次完整的50000任务时限、时延、GPU、IT功率和设施功率审计。
3. 建立包含“基线任务方案”和“替代任务方案”的统一候选集。
4. 每个问题四情景都对两个任务候选分别重建设施负荷和储能策略，并重新审计能源平衡、SOC、互斥和购售电边界。
5. 每个情景记录 `checked_candidates`、`selected_candidate`、`migration_count` 和 `task_search_status`。
6. `method_runtime.json` 增加替代任务全量审计和逐情景双候选比较证据。

情景仍属于有限启发式搜索。即使所有情景最终都选择基线，也只报告 `searched_no_improvement`，不声明局部最优、Pareto最优或全局最优。

## 依赖库

无需额外安装。

## 运行方式

python solution.py

## 预期输出

除原有输出外，新增或增强：

- `output/data/q4_alternative_task_constraint_audit.csv`
- `output/data/q4_scenario_comparison_v41.csv` 中的任务候选选择证据
- `output/data/method_runtime.json` 中的 `q4_task_candidate_set` 和 `q4_scenarios` 搜索证据
- `output/data/results.json` 中的问题四任务候选数和情景候选评价数