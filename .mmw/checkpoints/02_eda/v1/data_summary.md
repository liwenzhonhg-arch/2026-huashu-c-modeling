# 数据探索报告

## 数据概览

- `GPU_information.xlsx`
  - `GPU中心基础情况`：6 行、11 列；字段为 `Region`、`RegionRole`、`Total_GPU`、`Max_IT_Power_MW`、`PUE`、`Max_Facility_Power_MW`、`Reserved_GPU_Ratio`、`Available_GPU`、`Max_Workload_GPUh_per_h`、`CapacityLevel`、`Remarks`。数值类型包括 `int64`、`float64`，其余为字符串。
  - `字段说明`：12 行、5 列；字段为 `字段名`、`中文名称`、`单位`、`属性`、`含义与使用说明`，均为字符串。

- `network_latency.xlsx`
  - `network_latency`：36 行、4 列；字段为 `FromRegion`、`ToRegion`、`NetworkLatency_ms`、`LatencyClass`，其中时延为 `int64`，其余为字符串。
  - `字段说明`：4 行、5 列，均为字符串。
  - `时延矩阵`：6 行、7 列；`From\To` 为字符串，6 个区域时延列均为 `int64`。
  - `模型说明`：3 行、2 列，均为字符串。

- `power_mapping.xlsx`
  - `任务功率映射`：3 行、3 列；`TaskType`、`Remarks` 为字符串，`GPU_Power_MW_per_EquivalentGPU` 为 `float64`。
  - `计算口径`：5 行、2 列，均为字符串。

- `region_time_data.xlsx`
  - `region_time_data`：14442 行、26 列；包含 `Hour`、`Region`、电价、碳强度、负荷、新能源、购售电、储能状态及 `DataPeriod` 等字段。`Hour` 为 `int64`，区域和类别字段为字符串，其余主要指标为 `float64`。
  - `字段说明`：26 行、4 列，均为字符串。
  - 6 个区域各有 2407 条逐时记录。`Main_0_2399` 有 14400 条记录，`Closure_2400_2406` 有 42 条记录。

- `storage_information.xlsx`
  - `storage_information`：6 行、13 列；包含区域、储能容量、SOC 边界、充放电功率、效率及购售电边界等字段，数据类型包括字符串、`int64` 和 `float64`。
  - `字段说明`：13 行、5 列。

- `workload_trace.xlsx`
  - `Sheet1`：50000 行、11 列；字段为 `TaskID`、`TaskType`、`ArrivalHour`、`GPU_Demand`、`EstimatedDuration_min`、`DelaySensitivity`、`SourceRegion`、`MaxLatency_ms`、`LatestFinishHour`、`EarliestStartHour`、`ExecutionMode`。
  - `字段说明`：11 行、5 列。

- 已展示的数据表均无缺失值、无重复行。跨数据集检查表明，任务来源、GPU 中心、逐时数据和时延矩阵均覆盖 `RegionA` 至 `RegionF`；任务来源区域不在 GPU 信息中的数量、GPU 区域不在逐时数据中的数量及网络时延缺失有向区域对数量均为 0。

## 关键发现

- GPU 中心容量差异明显：`Total_GPU` 为 600 至 1600，均值 950；`Available_GPU` 为 540 至 1472，均值 867.5；`Max_IT_Power_MW` 为 405 至 720；PUE 为 1.25 至 1.38。

- 网络时延矩阵完整，共 36 个有向区域对。`NetworkLatency_ms` 最小值为 5，最大值为 82，均值为 42.388889，中位数为 41.5。时延类别中，`LongDistance`、`Regional`、`Local`、`InterRegional` 分别有 14、12、6、4 条记录。

- 三类任务的单位等效 GPU 功率范围为 0.08 至 0.16 MW，均值为 0.113333 MW，中位数为 0.1 MW。

- 工作负载共 50000 条。`ArrivalHour` 范围为 0 至 2399，均值为 1200.98488；`GPU_Demand` 范围为 1 至 127，均值为 29.47228，中位数为 13；`EstimatedDuration_min` 范围为 10 至 399，均值为 204.21310；`MaxLatency_ms` 范围为 20 至 150，均值为 83.11380；`LatestFinishHour` 最大值为 2406。

- 区域逐时数据覆盖完整：`Hour` 最小值为 0、最大值为 2406，每个区域均有 2407 条记录。电价均值为 538.778416 元/MWh，范围为 234.65 至 1095.84；碳强度均值为 0.441925 tCO2/MWh，范围为 0.196 至 0.6876。

- `GPU_Utilization_Percent` 均值为 37.663502，中位数为 35.607852，最大值为 135.583161；共有 44 条记录超过 100，说明该字段存在需要进一步核查的超容量状态或口径问题。

- 逐时负荷和电力指标中，`IT_Load_MW` 均值为 343.801250，`Total_Load_MW` 均值为 451.077891，`GridPurchase_MW` 均值为 286.273793，`NetGridImport_MW` 均值为 191.047635，`CarbonEmission_tCO2` 均值为 141.626331。

- 设施负荷、净购电和碳排放计算口径一致：`Total_Load_Difference_MW`、`NetGridImport_Difference_MW`、`CarbonEmission_Difference_tCO2` 绝对差大于 0.001 的行数均为 0。

- 新能源平衡式未扣除外送电量时，`Renewable_Balance_Difference_MW` 绝对差大于 0.001 的记录有 7220 条，其均值 95.226158 与 `GridSell_MW` 均值 95.226159 基本对应。因此新能源平衡核算应显式加入外送项。

- 其余主要边界检查结果较稳定：IT 功率、设施功率、SOC、充放电功率、电网购售电上限、新能源非负约束均没有违规记录；充电与放电同时为正的记录为 0。购电和售电同时为正的记录有 6030 条，需要确认这是允许的分项结算机制，还是优化模型中应禁止的同时交易。

- 各区域累计新能源利用率差异较大：RegionA、RegionB、RegionC、RegionD、RegionE、RegionF 分别为 0.086422、0.101258、0.119428、0.470552、0.609995、0.584080。RegionE 和 RegionF 的累计净购电量分别为 -102564.046218 MWh 和 -34513.041173 MWh，表现为净外送；RegionA、RegionB、RegionC 的 `GridSell_MWh` 均为 0。

- 系统逐时设施负荷均值为 2706.467348 MW，最大值为 3477.7658 MW，发生在第 2045 小时；最小值为 1697.8132 MW，发生在第 2010 小时。系统净购电最大值为 1907.6382 MW，发生在第 554 小时；最小值为 -620 MW，发生在第 2404 小时。

- 系统碳排放最大值为 1244.6154 tCO2，发生在第 554 小时；最小值为 0，发生在第 2401 小时。系统购电最小值同样为 0，发生在第 2401 小时。

- 相关性结果显示：
  - `IT_Load_MW` 与 `Total_Load_MW` 的相关系数为 0.984800。
  - `NetGridImport_MW` 与 `CarbonEmission_tCO2` 的相关系数为 0.967169。
  - `GridPurchase_MW` 与 `NetGridImport_MW` 的相关系数为 0.938797。
  - `GridPurchase_MW` 与 `CarbonEmission_tCO2` 的相关系数为 0.927900。
  - `GridSell_MW` 与 `SellPrice_CNY_per_MWh` 的相关系数为 0.920809。
  - `CarbonIntensity_tCO2_per_MWh` 与 `GridSell_MW` 的相关系数为 -0.907620。
  - `UsedRenewable_MW` 与 `CarbonIntensity_tCO2_per_MWh` 的相关系数为 -0.850272。

- 各来源区域逐小时到达 GPU 需求与本区域基线 AI 负荷呈中等正相关：RegionA 至 RegionF 的同区域相关系数依次为 0.51591、0.535514、0.510054、0.524678、0.524653、0.504138；跨区域相关性整体较弱。

- 时序异常检测基于一阶差分进行。碳强度和可用新能源在各区域的异常变化数量均为 0；GPU 利用率、IT 负荷、设施负荷、净购电及 SOC 存在不同数量的突变点，应结合电价切换、任务到达、储能动作和时域边界解释，而不应直接删除。

- 共生成 17 张 EDA 图表，覆盖 GPU 容量、网络时延、任务分布、逐时负荷、新能源、净购电、SOC、相关性和储能参数。

## 建模建议

- 任务预测应采用严格的时间顺序划分，避免随机划分造成信息泄漏。建议以逐小时、区域和任务类型组合构造任务数、GPU 需求、GPU-hour及滞后特征，并分别评估各区域和任务类型。

- `GPU_Demand` 的均值明显高于中位数，建模时宜采用对偏态和峰值更稳健的损失函数，并同时报告 MAE、RMSE 和 WAPE。对突发负荷可增加分位数预测或峰值事件分类。

- 调度模型必须使用完整的有向时延矩阵，根据任务的 `MaxLatency_ms` 筛选可执行区域。实时推理与可延迟任务应分开建模，后者还需满足不可抢占、连续执行和 `LatestFinishHour` 约束。

- GPU 容量、IT 功率和设施功率应同时约束。设施功率应由总 IT 负荷乘 PUE 计算，AI 负荷则按任务类型功率映射及任务在各小时的实际重叠时长计算。

- 新能源平衡公式应包含直接消纳、储能充电、弃电和电网外送，避免把 `GridSell_MW` 误判为平衡残差。RegionD、RegionE、RegionF 的外送行为尤其需要在模型中保留。

- 碳感知优化可利用碳强度、新能源消纳和净购电之间的强相关结构，但相关性不能替代因果或约束分析。建议将运行成本、碳排放、服务时延和新能源利用率分别计算，再通过权重、约束上限或 Pareto 前沿进行多目标比较。

- 应单独核查 44 条 GPU 利用率超过 100 的记录，并明确 `GPU_Utilization_Percent` 是基准指标、允许超配的统计量，还是实际容量约束。未明确前不宜直接将其作为硬约束输入。

- 应确认 6030 条购电和售电同时为正记录的业务含义。如果系统不允许同一地区同一时段双向交易，优化模型需加入互斥变量；如果购电与新能源外送可以并存，则应保留，并在成本和新能源利用率公式中分别核算。

- 时序异常点不应机械删除。电价一阶差分在每个区域均检测到 400 个异常变化，可能对应制度化时段切换；SOC 在部分区域大量保持不变，使 IQR 为 0，也会放大非零变化的异常标记。后续应将异常检测用于事件标注和约束复核，而非直接清洗。