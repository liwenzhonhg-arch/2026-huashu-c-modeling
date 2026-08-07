# 代码说明

## 实现思路

超时的主要原因位于问题二局部搜索：原程序最多检查 20000 个候选，而每个候选都会复制 50000 行调度表，并重新遍历全部任务完成容量审计和逐时能源复算，最坏规模约为 10 亿任务次处理，无法在 300 秒内完成。

修订后保留每个候选的完整硬约束和能源复算，但采用有界候选集：

- 从等待时间最长、GPU 需求最大的 4 个任务中产生候选。
- 最多完整评价 8 个候选。
- 搜索在程序启动后 225 秒主动停止，合同中的 285 秒仍是不可逾越的硬上限。
- 剩余时间用于问题三、问题四、完整约束审计、结构化结果和 300 dpi 图表输出。
- 增加带 `flush=True` 的阶段进度输出，若再次超时，可直接定位停止阶段。
- `method_runtime.json` 记录候选上限、任务池规模、实际检查数和接受改进数。

这是有限启发式缩减，不改变任务可行域、能源方程或硬约束，也不声明局部最优、Pareto 最优或全局最优。

本题不涉及 PDE 或移动热过程，因此 PDE 调用次数为 0；没有使用 `differential_evolution` 或连续优化器。

## 依赖库

无需额外安装。使用环境已有的：

- numpy
- pandas
- matplotlib
- scikit-learn
- Excel 读取引擎

## 运行方式

python solution.py

试跑方式由宿主设置：

MMW_PILOT=1 python solution.py

## 预期输出

正式运行生成：

- `output/data/results.json`
- `output/data/sensitivity.json`
- `output/data/method_runtime.json`
- `output/data/figure_manifest.json`
- 问题一至问题四的调度、能源、审计、搜索轨迹和情景 CSV
- `output/figures/` 下的利用率、SOC和灵敏度图

试跑仅生成 `output/data/method_pilot.json`。