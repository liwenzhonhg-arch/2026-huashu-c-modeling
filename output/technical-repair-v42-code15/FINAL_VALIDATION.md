# C 题技术修复最终验证

## 现役版本

- model v42
- code v15
- solve v12
- paper v18
- review v12

## 可复算证据

- 两次隔离运行自然完成：1687.58 s、1706.49 s。
- 冻结脚本 SHA-256：`846f527be95d5c6ba7ebe7b03e7fe50a814b7d3cf905c2070d4a33d59ecf1f3d`。
- 48 个正式输出文件逐字节一致；`method_runtime.json` 只在真实 `elapsed_seconds` 上不同，去除该字段后语义一致。
- `results.json` SHA-256：`691e95d6f0450c63c6b0468a55453af778dfe949316eadadc63a5ad8a0a4daa0`。
- 仓库测试：542 passed；C 题专项测试：4 passed。
- 最终 benchmark：`scenario-feasible`，overall_passed=true；Oracle 不可用。

## 核心结果

- Q1：18 条闭环序列，平均 MAE 25.5892 GPU、RMSE 34.5070 GPU、WAPE 0.8231。
- Q2：五个方向合计评价 50,000 个候选，覆盖 2,148 个不同任务；平衡方案成本 -421,801,727.45 元、碳排放 16.516041 tCO2、新能源利用率 0.679962。
- Q3：7 个策略、6 条唯一轨迹；平衡方案在声明候选集中非支配，成本 -458,584,632.33 元、碳排放 0.224084 tCO2。
- Q4：17 个情景、37 轮、22,200 个候选；基准情景实时 SLA 与按期完成率均为 1。

## 判断边界

结果只可称为 `scenario-feasible`。Q2/Q4 是预声明预算内 best-found，Q3 是离散 SOC 候选集 Pareto；不存在全局最优证书。题面未给储能退化成本与循环寿命上限，高循环储能轨迹不能直接作为真实设备控制指令。

## 主要文件

- `C题论文_v18.pdf`（SHA-256 `53293e8f0f2b88bc25b200841cf58d89521f94d30ccd922a95d704af7a80a3bf`）
- `solution.py`
- `data/results.json`
- `evidence/run-comparison.json`
- `evidence/benchmark-v12.json`
- `evidence/review-v12.md`
- `evidence/paper-v18-final-contact-sheet.png`
