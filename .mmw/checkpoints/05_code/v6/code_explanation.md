# 代码说明

## 实现思路

程序严格读取题目列出的六个真实 Excel 文件，不生成模拟数据。主要流程如下：

1. 校验区域、小时覆盖、PUE、储能效率和 SOC 物理边界。
2. 在 `MMW_PILOT=1` 时执行真实数据可读性、有限性、时域及网络覆盖试跑，只生成 `method_pilot.json`。
3. 聚合区域、任务类型和小时级 GPU、GPU-hour 需求。
4. 使用滞后特征和 Huber 回归预测第 2376 至 2399 小时 GPU 需求，并计算 MAE、RMSE 和可计算的 WAPE。
5. 按实时优先、截止约束、网络时延、GPU、IT 功率和设施功率约束构造全任务确定性可行调度。
6. 按实际分钟重叠量计算 AI IT 电量，并生成无储能新能源优先能源方案。
7. 使用真实基准 AI 负荷和 NonAI 负荷构造储能情景策略，逐时递推 SOC。
8. 输出任务方案、预测、能源流、储能轨迹、关键指标、运行证据、图表数据和灵敏度结果。
9. 最终结果明确属于有限启发式搜索得到的 `scenario-feasible best-found`，不声明 Pareto 前沿或全局最优。

详细逐时方案保存在 CSV 文件中；`results.json` 中的同名契约结果给出相应规模、核心指标或通过状态，并在 `desc` 中指向详细文件。

## 依赖库

无需额外安装。使用当前环境提供的：

- numpy
- pandas
- matplotlib
- scikit-learn
- openpyxl

## 运行方式

python solution.py

试跑方式：

set MMW_PILOT=1
python solution.py

## 预期输出

正式运行产生：

- `output/data/results.json`
- `output/data/sensitivity.json`
- `output/data/method_runtime.json`
- `output/data/figure_manifest.json`
- `output/data/q1_gpu_statistics.csv`
- `output/data/q1_forecast_2376_2399.csv`
- `output/data/q1_forecast_metrics.csv`
- `output/data/q1_q2_q4_task_schedule.csv`
- `output/data/q2_hourly_energy.csv`
- `output/data/q3_q4_storage_energy.csv`
- `output/data/figure_data/*.csv`
- `output/figures/*.png`

试跑仅产生：

- `output/data/method_pilot.json`

控制台打印运行成本、碳排放及最终约束状态。输入缺失、任务无合法候选、储能终端状态不满足或出现非有限结果时，程序会给出约束 ID、实际值和阈值后终止，不会写出伪造的正式结果。