# 代码说明

## 实现思路

根因不是变量未定义或矩阵奇异，而是试跑与正式运行仍共享同一个 `main()` 入口。上一版虽然在 `main()` 内通过 `return` 提前退出，但托管器的写路径检查无法从入口结构上证明试跑不会继续进入正式输出流程，因此仍判定试跑触及 `results.json`。

本次修正把试跑分派提升到程序最外层：

1. 启动时只计算一次 `PILOT_MODE`，并兼容环境变量两侧空白。
2. `MMW_PILOT=1` 时直接执行 `pilot(read_inputs())`，不调用 `main()`。
3. 正式 `main()` 增加反向门禁；试跑模式若因其他调用路径进入正式入口，会立即抛出带实际值和阈值的异常。
4. 试跑路径只读取题目列出的真实附件、执行有限检查，并写入 `output/data/method_pilot.json`。
5. 试跑路径不会执行正式结果目录初始化之后的预测、调度、储能、情景、CSV、JSON 或绘图代码。
6. 50000 任务调度器、预测逻辑、正式能源计算和情景计算均未修改。

本错误与矩阵求逆无关。代码没有使用 `inv(X.T @ X)`；Huber 回归由 scikit-learn 实现，因此不需要增加矩阵求逆补丁。

## 依赖库

无需额外安装。使用：

- numpy
- pandas
- matplotlib
- scikit-learn
- Excel 读取引擎

## 运行方式

正式运行：

python solution.py

PowerShell 试跑：

$env:MMW_PILOT = "1"
python solution.py

## 预期输出

试跑仅写入：

- `output/data/method_pilot.json`

试跑不创建、覆盖或删除：

- `results.json`
- `sensitivity.json`
- `method_runtime.json`
- `figure_manifest.json`
- 正式 CSV
- 正式图表

正式运行输出保持不变。