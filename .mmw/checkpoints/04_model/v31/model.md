# 数学模型

## 1. 模型边界

区域集合、任务类型集合分别为

$$
\mathcal R=\{\mathrm A,\mathrm B,\mathrm C,\mathrm D,\mathrm E,\mathrm F\},
$$

$$
\mathcal K=\{\mathrm{RealTimeInference},
\mathrm{BatchInference},\mathrm{AITraining}\}.
$$

任务到达、执行和能源结算时域为

$$
\mathcal T^{arr}=\{0,\ldots,2399\},\quad
\mathcal T^{run}=\{0,\ldots,2405\},\quad
\mathcal T^{energy}=\{0,\ldots,2406\},
$$

时间步长为 $\Delta t=1\ \mathrm h$。第 $2400$–$2405$ 小时不产生新任务，只结清主时域内到达的弹性任务；第 $2406$ 小时不安排任务，只进行电力与储能终端结算。

六区域定位、有向网络时延和全部设备容量均为题面或附件直接给定。本题不含几何尺寸链，不建立线路潮流、网络带宽、迁移数据量、传输能耗或传输费用模型。

本版只修复以下六项阻断问题：

1. 预测选型后按题面要求使用截至第 $2375$ 小时的数据重新训练；
2. 为实时任务缺失 `LatestFinishHour` 定义确定性回退，对弹性任务缺失截止字段结构化停止；
3. 在问题三、四加入购电与外送互斥约束；
4. 最后 $24$ 小时容量核算纳入第 $2376$ 小时前已开工且仍在运行的存量任务；
5. 各类约束残差先按本类物理尺度归一化，再汇总最大残差；
6. 未经本轮代码复核的旧调度具体超限计数改为 `pending_code_execution`。

真实最优调度、真实 Pareto 前沿和用户满意度标签不可观测。因此不使用准确率、召回率或混淆矩阵验证，而以预测误差、硬约束残差、状态连续性和实际检查集合内的指标比较作为代理验证口径。

## 2. 符号说明

| 符号 | 含义 | 类型、来源或代理口径 | 取值范围或单位 |
|---|---|---|---|
| $i,r,t,s,k$ | 任务、区域、小时、整数开工小时、任务类型 | 索引 | 附件集合 |
| $\mathcal I^{RT}$ | 实时推理任务集合 | `TaskType=RealTimeInference` | 无 |
| $\mathcal I^{flex}$ | 批量推理和训练任务集合 | 附件任务类型 | 无 |
| $a_i$ | 到达时刻 | `ArrivalHour`，可观测 | h |
| $d_i$ | 连续执行时长 | $d_i=\mathrm{EstimatedDuration\_min}_i/60$ | h |
| $g_i$ | 运行期间持续占用 GPU | `GPU_Demand` | 等效 GPU |
| $k_i,o_i$ | 任务类型、来源区域 | `TaskType`、`SourceRegion` | 类别 |
| $f_i^{late}$ | 附件记录的最晚完成时点 | `LatestFinishHour`，可能缺失 | h |
| $\bar f_i$ | 有效最晚完成时点 | 由式（1）确定 | h |
| $\ell_i^{max}$ | 最大允许网络时延 | `MaxLatency_ms` | ms |
| $\ell_{or}$ | 来源区 $o$ 至执行区 $r$ 的单向时延 | `network_latency.xlsx` | ms |
| $x_{irs}$ | 任务 $i$ 在区域 $r$、小时 $s$ 开工 | 决策变量 | $\{0,1\}$ |
| $\omega_{it}(s)$ | 任务与小时 $t$ 的重叠时长 | 式（3） | $[0,1]$ h |
| $\chi_{it}(s)$ | 任务是否触及小时 $t$ | 式（4） | $\{0,1\}$ |
| $G_r^{max}$ | 可调度 GPU 容量 | `Available_GPU` | 等效 GPU |
| $p_k^{GPU}$ | 类型 $k$ 每等效 GPU 的平均 IT 功率 | `power_mapping.xlsx` | MW/GPU |
| $P_{rt}^{NA}$ | 不可迁移非 AI IT 负荷 | `NonAI_IT_Load_MW` | MW |
| $P_{rt}^{BAI}$ | 问题三给定基线 AI IT 负荷 | `Baseline_AI_IT_Load_MW` | MW |
| $P_r^{IT,max}$ | 区域 IT 瞬时功率上限 | `Max_IT_Power_MW` | MW |
| $P_r^{fac,max}$ | 区域设施瞬时功率上限 | `Max_Facility_Power_MW` | MW |
| $\mathrm{PUE}_r$ | 区域能源使用效率 | `PUE` | 无量纲 |
| $G_{rt}^{inst}$ | 瞬时并发 GPU | 派生量 | GPU |
| $P_{rt}^{AI,inst}$ | 瞬时 AI IT 功率 | 派生量 | MW |
| $E_{rt}^{AI}$ | 小时内 AI IT 能量 | 派生量 | MWh |
| $P_{rt}^{AI,avg}$ | AI 小时平均功率 | $E_{rt}^{AI}/\Delta t$ | MW |
| $R_{rt}^{av}$ | 可用新能源功率 | `AvailableRenewable_MW` | MW |
| $R_{rt}^{use}$ | 直接消纳新能源 | 决策变量 | MW |
| $B_{rt}$ | 电网购电功率 | 决策变量 | MW |
| $S_{rt}$ | 新能源外送功率 | 决策变量 | MW |
| $K_{rt}$ | 弃风弃光功率 | 决策变量 | MW |
| $C_{rt}^{RE},C_{rt}^{G}$ | 新能源充电、电网充电功率 | 决策变量 | MW |
| $C_{rt}$ | 储能总充电功率 | $C_{rt}^{RE}+C_{rt}^{G}$ | MW |
| $D_{rt}$ | 储能放电功率 | 决策变量 | MW |
| $E_{rt}$ | 时段末绝对 SOC | 状态变量 | MWh |
| $E_r^0$ | 第 $0$ 小时运行前 SOC | `InitialSOC_MWh` | MWh |
| $E_r^{min},E_r^{max}$ | SOC 下限、上限 | 储能附件 | MWh |
| $C_r^{max},D_r^{max}$ | 最大充、放电功率 | 储能附件 | MW |
| $\eta_r^c,\eta_r^d$ | 充、放电效率 | 储能附件 | $(0,1]$ |
| $G_r^{import,max}$ | 区域购电上限 | 附件直接给定 | MW |
| $G_r^{export,max}$ | 区域外送上限 | 附件直接给定 | MW |
| $S_r^{max}$ | 储能信息表外送上限 | `SellLimit_MW` | MW |
| $\bar S_r$ | 问题三、四有效外送上限 | $\min(G_r^{export,max},S_r^{max})$ | MW |
| $u_{rt}$ | 充放电模式变量 | $1$ 允许充电，$0$ 允许放电 | $\{0,1\}$ |
| $v_{rt}$ | 购售电模式变量 | $1$ 允许购电，$0$ 允许外送 | $\{0,1\}$ |
| $\pi_{rt}^{buy},\pi_{rt}^{sell}$ | 购、售电价 | `region_time_data.xlsx` | 元/MWh |
| $c_{rt}$ | 购电碳强度 | `CarbonIntensity_tCO2_per_MWh` | tCO2/MWh |
| $C_{op}$ | 系统运行电费净成本 | 指标 | 元 |
| $E_{CO2}$ | 碳排放量 | 指标 | tCO2 |
| $N_{rt}$ | 净购电功率 | $B_{rt}-S_{rt}$ | MW |
| $\widehat P_r^{peak}$ | 正向峰值净购电 | 指标 | MW |
| $\widehat V$ | 净购电绝对爬坡量 | 指标 | MW |
| $Q_{service}$ | 服务质量代理 | 弹性任务等待余量利用程度 | 无量纲 |
| $\varepsilon_j$ | 第 $j$ 类约束归一化残差 | 式（59） | 无量纲 |
| $\tau_0$ | 归一化残差容差 | 固定为 $10^{-6}$ | 无量纲 |

附件关键字段进入模型前必须为有限数值，并满足容量非负、PUE 为正、效率属于 $(0,1]$。任务到达、时长、GPU、时延或功率映射缺失时输出 `invalid_task_input` 并停止相关任务优化；不得把缺失值补为零。

## 3. 共享任务模型：瞬时容量与重叠能量分离

### 3.1 有效截止与候选集合

为避免实时任务的 `LatestFinishHour` 缺失使候选集合不可计算，定义

$$
\bar f_i=
\begin{cases}
\min(f_i^{late},2406),
& f_i^{late}\text{ 为有限数值},\\
2406,
& i\in\mathcal I^{RT}\text{ 且 }f_i^{late}\text{ 缨失},\\
\texttt{invalid\_elastic\_deadline},
& i\in\mathcal I^{flex}\text{ 且 }f_i^{late}\text{ 缺失}.
\end{cases} \tag{1}
$$

第三种分支触发结构化停止，不让 `NaN` 进入任何比较或 $\min$ 运算。执行候选集合为

$$
\mathcal S_{ir}=
\left\{
s\in\mathcal T^{run}:
s\ge a_i,\quad
s+d_i\le\bar f_i,\quad
\ell_{o_ir}\le\ell_i^{max}
\right\}. \tag{2}
$$

实时任务再限制 $s=a_i$。若某任务所有区域的候选集合均为空，则输出 `infeasible_precheck`。

### 3.2 瞬时占用与小时能量

任务执行区间为 $[s,s+d_i)$。与小时 $[t,t+1)$ 的重叠时长为

$$
\omega_{it}(s)=
\max\{0,\min(s+d_i,t+1)-\max(s,t)\}. \tag{3}
$$

触小时指示量为

$$
\chi_{it}(s)=
\mathbf 1\{s\le t<s+d_i\}. \tag{4}
$$

每个任务唯一执行：

$$
\sum_{r\in\mathcal R}\sum_{s\in\mathcal S_{ir}}x_{irs}=1,
\qquad x_{irs}\in\{0,1\}. \tag{5}
$$

瞬时并发 GPU 为

$$
G_{rt}^{inst}
=\sum_i\sum_{s\in\mathcal S_{ir}}
g_i\chi_{it}(s)x_{irs}, \tag{6}
$$

并满足

$$
G_{rt}^{inst}\le G_r^{max}. \tag{7}
$$

瞬时 AI IT 功率为

$$
P_{rt}^{AI,inst}
=\sum_i\sum_{s\in\mathcal S_{ir}}
g_ip_{k_i}^{GPU}\chi_{it}(s)x_{irs}. \tag{8}
$$

IT 和设施瞬时功率约束为

$$
P_{rt}^{NA}+P_{rt}^{AI,inst}
\le P_r^{IT,max}, \tag{9}
$$

$$
\mathrm{PUE}_r
\left(P_{rt}^{NA}+P_{rt}^{AI,inst}\right)
\le P_r^{fac,max}. \tag{10}
$$

第 $2406$ 小时不得被任务占用：

$$
\chi_{i,2406}(s)x_{irs}=0. \tag{11}
$$

小时 AI IT 能量和平均功率为

$$
E_{rt}^{AI}
=\sum_i\sum_{s\in\mathcal S_{ir}}
g_ip_{k_i}^{GPU}\omega_{it}(s)x_{irs}, \tag{12}
$$

$$
P_{rt}^{AI,avg}=\frac{E_{rt}^{AI}}{\Delta t}. \tag{13}
$$

问题一、二、四的设施平均负荷为

$$
P_{rt}^{fac,avg}
=\mathrm{PUE}_r
\left(P_{rt}^{NA}+P_{rt}^{AI,avg}\right). \tag{14}
$$

式（6）–（10）用于工程瞬时容量，式（12）–（14）用于 MWh、电费、碳排放和新能源分流，两者不得互换。

## 子问题 1：GPU 需求预测与最后 24 小时基础调度

### 模型思路

按区域—任务类型构造逐小时到达 GPU 序列，先完成预测结构选择，再按题面要求使用截至第 $2375$ 小时的全部有效历史重新训练选定结构。第 $2376$–$2399$ 小时预测只用于评价；正式调度使用实际到达任务。

最后 $24$ 小时不能作为孤立窗口调度。先在完整任务时域上构造基准调度，再将第 $2376$ 小时前已开工且仍在运行的任务作为存量占用带入最后 $24$ 小时容量核算。

### 模型建立

区域—类型—小时的到达 GPU 与 GPU-hour 为

$$
D_{rkt}
=\sum_{i:o_i=r,k_i=k,a_i=t}g_i, \tag{15}
$$

$$
H_{rkt}
=\sum_{i:o_i=r,k_i=k,a_i=t}g_id_i. \tag{16}
$$

特征向量为

$$
\boldsymbol\phi_{rkt}=
\left[
D_{rk,t-1},D_{rk,t-24},D_{rk,t-168},
\bar D_{rk,t}^{24},\bar D_{rk,t}^{168},
\sin\frac{2\pi t}{24},\cos\frac{2\pi t}{24},
\sin\frac{2\pi t}{168},\cos\frac{2\pi t}{168}
\right]^\top, \tag{17}
$$

其中

$$
\bar D_{rk,t}^{h}
=\frac1h\sum_{j=1}^{h}D_{rk,t-j}. \tag{18}
$$

Huber 损失定义为

$$
\rho_\delta(e)=
\begin{cases}
\dfrac12e^2,&|e|\le\delta,\\
\delta\left(|e|-\dfrac12\delta\right),&|e|>\delta.
\end{cases} \tag{19}
$$

增强预测模型为

$$
\min_{\beta_0,\boldsymbol\beta}
\sum_t
\rho_{\delta_H}
\left(D_{rkt}-\beta_0-\boldsymbol\beta^\top\boldsymbol\phi_{rkt}\right)
+\alpha\|\boldsymbol\beta\|_2^2, \tag{20}
$$

$$
\widehat D_{rkt}
=\max\left\{0,\beta_0+\boldsymbol\beta^\top\boldsymbol\phi_{rkt}\right\}. \tag{21}
$$

候选包括 lag24、lag168 和四个 Huber-Ridge 组合

$$
(\alpha,\delta_H/\sigma)
\in
\{(10^{-3},1),(10^{-3},2),(10^{-1},1),(10^{-1},2)\}, \tag{22}
$$

其中

$$
\sigma=\max\{1,1.4826\,\mathrm{MAD}\}. \tag{23}
$$

预测流程严格分为两个拟合阶段。

模型选择阶段使用截至第 $2351$ 小时可构造的全部有效特征样本；由于最大滞后为 $168$，实际回归索引为

$$
t=168,\ldots,2351. \tag{24}
$$

在第 $2352$–$2375$ 小时进行固定起点递归验证，区间内部只能使用预测值，不读取该区间真实未来值。按验证 WAPE、MAE 和简单模型优先序选择唯一结构及超参数。

选型完成后，不保留选型阶段参数。使用截至第 $2375$ 小时可构造的全部有效样本重新拟合选定结构：

$$
t=168,\ldots,2375. \tag{25}
$$

由该最终拟合参数递归预测第 $2376$–$2399$ 小时，测试区间内部不得读取真实未来需求。

评价指标为

$$
\mathrm{MAE}
=\frac1n\sum_t|D_t-\widehat D_t|, \tag{26}
$$

$$
\mathrm{RMSE}
=\sqrt{\frac1n\sum_t(D_t-\widehat D_t)^2}, \tag{27}
$$

$$
\mathrm{WAPE}
=\frac{\sum_t|D_t-\widehat D_t|}
{\sum_tD_t},
\qquad \sum_tD_t>0. \tag{28}
$$

若 $\sum_tD_t=0$，WAPE 输出 `metric_unavailable`，仍报告有限的 MAE 和 RMSE。相关系数和 ACF 仅在成对有限样本数不少于 $2$ 且两序列方差均为正时计算，否则输出 `correlation_unavailable` 或 `autocorrelation_unavailable`。周期在 $h=2,\ldots,336$ 中取满足 $\mathrm{ACF}_h>0.3$ 且高于相邻值的最大局部峰；不存在时输出 `period_unidentifiable`。

基础调度按“实时优先、有效截止 $\bar f_i$ 升序、时长升序、TaskID 升序”处理任务。每个任务按开工小时、网络时延、区域名扫描完整候选域，接受前检查式（5）、（7）、（9）–（11）。

定义第 $2376$ 小时的存量运行任务集合为

$$
\mathcal I_{2376}^{carry}
=
\{i:a_i<2376,\ s_i<2376<s_i+d_i\}. \tag{29}
$$

第 $2376$–$2399$ 小时的容量、功率和利用率复核使用完整式（6）–（10），求和范围同时包含：

$$
\mathcal I_{2376}^{carry}
\cup
\{i:2376\le a_i\le2399\}. \tag{30}
$$

存量任务的执行区域和开工时刻由完整基准调度确定，不在最后 $24$ 小时局部窗口内重新迁移。这样可避免遗漏跨越第 $2376$ 小时边界的既有占用。

区域 GPU 利用率为

$$
U_{rt}^{GPU}
=\frac{G_{rt}^{inst}}{G_r^{max}}\times100\%,
\qquad G_r^{max}>0. \tag{31}
$$

若 $G_r^{max}\le0$，输出 `invalid_gpu_capacity` 并停止该区域调度。

### 求解方法

1. 检查任务关键字段、容量和功率映射是否有限。
2. 执行模型选择阶段拟合与固定起点验证。
3. 使用截至第 $2375$ 小时的全部有效样本重新训练唯一选定结构。
4. 对第 $2376$–$2399$ 小时递归预测并评价。
5. 在完整执行时域上构造基础调度。
6. 将式（29）的存量任务带入最后 $24$ 小时容量复核。
7. 若某任务无候选，输出 `infeasible_precheck`；完整扫描后仍无法放置则输出 `infeasible_incumbent`。

### 必须回答的输出

1. 分区域、分任务类型的任务数、GPU 总量、GPU-hour、分位数、持续时间、周期、自相关和区域相关性。
2. 验证集与测试集总体及分组 MAE、RMSE、WAPE或结构化不可用状态。
3. 第 $2376$–$2399$ 小时实际到达任务的执行区域、开工和完成时刻。
4. 第 $2376$ 小时前已开工但在最后 $24$ 小时仍运行的存量任务清单及其资源占用。
5. 第 $2400$–$2405$ 小时末端任务及结清时刻。
6. 最后 $24$ 小时甘特图、逐小时 GPU 利用率、各区域瞬时 GPU/IT/设施峰值及归一化最大约束残差。
7. 文件：`q1_forecast_metrics.csv`、`q1_schedule.csv`、`q1_gpu_utilization.csv`、`q1_gantt.png`。
8. 结果等级不高于 `scenario-feasible`，`global_optimality=not_certified`。

## 子问题 2：碳感知任务调度

### 模型思路

从重新构造且通过瞬时容量复核的完整基础调度出发，对最多 $10000$ 个高 GPU-hour 弹性任务进行确定性局部改进。旧调度不复用；其具体超限计数不作为本轮模型阶段事实，状态记为 `pending_code_execution`，由代码阶段使用真实附件重新复核。

### 模型建立

任务侧满足式（1）–（14）。无储能能源平衡为

$$
B_{rt}+R_{rt}^{use}
=P_{rt}^{fac,avg}, \tag{32}
$$

$$
R_{rt}^{use}+S_{rt}+K_{rt}
=R_{rt}^{av}. \tag{33}
$$

购售电边界为

$$
0\le B_{rt}\le G_r^{import,max}, \tag{34}
$$

$$
0\le S_{rt}
\le\min(R_{rt}^{av},G_r^{export,max}), \tag{35}
$$

$$
R_{rt}^{use}\ge0,\qquad K_{rt}\ge0. \tag{36}
$$

式（33）保证问题二的外送仅来自当期新能源。

成本和碳排放为

$$
C_{op}
=\sum_{r,t}
\left(
\pi_{rt}^{buy}B_{rt}
-\pi_{rt}^{sell}S_{rt}
\right)\Delta t, \tag{37}
$$

$$
E_{CO2}
=\sum_{r,t}c_{rt}B_{rt}\Delta t. \tag{38}
$$

GPU-hour 加权平均网络时延为

$$
L_{net}
=
\frac{\sum_i g_id_i\ell_{o_i,r_i}}
{\sum_i g_id_i},
\qquad \sum_i g_id_i>0. \tag{39}
$$

分母不正时输出 `metric_unavailable`。

统一新能源利用率为

$$
U_{RE}
=
\frac{\sum_{r,t}(R_{rt}^{use}+S_{rt})\Delta t}
{\sum_{r,t}R_{rt}^{av}\Delta t},
\qquad
\sum_{r,t}R_{rt}^{av}\Delta t>0. \tag{40}
$$

分母不正时输出 `metric_unavailable` 并排除排序；同时分别报告直接消纳率、外送率和弃电率。

对候选任务 $i$ 在区域 $r$、时刻 $s$ 的设施能量增量定义为

$$
\Delta E_t
=\mathrm{PUE}_rg_ip_{k_i}^{GPU}\omega_{it}(s),\qquad
E=\sum_t\Delta E_t. \tag{41}
$$

移除当前任务后，其余负荷记为 $P_{rt}^{fac,avg,-i}$。剩余新能源能量为

$$
R_{rt}^{res,E}
=
\max\left\{
0,
(R_{rt}^{av}-P_{rt}^{fac,avg,-i})\Delta t
\right\}, \tag{42}
$$

单位为 MWh。

设 $\widetilde\pi$、$\widetilde c$ 分别为附件中严格正购电价格和严格正碳强度的中位数。若相应严格正样本集合为空，则评分结构不可计算，输出 `q2_score_unavailable` 并停止问题二局部优化。否则定义

$$
z_C
=\frac{\sum_t\Delta E_t\pi_{rt}^{buy}}
{\max(1,E\widetilde\pi)}, \tag{43}
$$

$$
z_E
=\frac{\sum_t\Delta E_tc_{rt}}
{\max(1,E\widetilde c)}, \tag{44}
$$

$$
z_R
=\frac{\sum_t\min(\Delta E_t,R_{rt}^{res,E})}
{\max(1,E)}, \tag{45}
$$

$$
z_W
=\frac{s-a_i}
{\max\{1,\lfloor\bar f_i-d_i\rfloor-a_i\}}, \tag{46}
$$

$$
z_L
=\frac{\ell_{o_ir}}
{\max(1,\ell_i^{max})}. \tag{47}
$$

局部评分为

$$
score_{q2}
=z_C+z_E-0.5z_R+0.5z_W+0.5z_L. \tag{48}
$$

### 求解方法

每次移动先移除旧位置对应的 $\chi$ 瞬时占用和 $\omega$ 重叠能量，再检查新位置。只有评分严格改善且式（5）、（7）、（9）–（11）、（32）–（36）全部满足才接受，否则完整恢复旧状态。

实际检查任务数记录已经完成整次候选扫描并完成接受或恢复的数量。达到共享截止后不得把预设的 $10000$ 写成实际检查量。最终重新扫描所有任务和区域小时。

### 必须回答的输出

1. 每个任务的来源区、执行区、开工、完成、等待和网络时延。
2. 成本、碳排放、平均及高分位时延、直接消纳率、外送率、弃电率和统一新能源利用率。
3. 相对基础调度的绝对和相对变化。
4. 实际检查任务数、迁移数量、迁移方向及等待分布。
5. 瞬时 GPU、IT、设施峰值，三类超限计数及归一化最大约束残差；正式完成结果的三项超限计数必须均为 $0$。
6. 第 $2400$–$2405$ 小时任务和能源结算。
7. 文件：`q2_schedule.csv`、`q2_energy_flow.csv`、`q2_metrics.csv`、`q2_pareto.csv`、`q2_pareto.png`。
8. `q2_pareto.csv` 含 `ParetoCertified=false`、`Credibility=scenario-feasible`。

## 子问题 3：固定负荷下储能协同优化

### 模型思路

问题三不重新调度任务，固定设施负荷为

$$
P_{rt}^{fac}
=\mathrm{PUE}_r
(P_{rt}^{BAI}+P_{rt}^{NA}). \tag{49}
$$

在能源平衡、SOC、充放电互斥和购电—外送互斥约束下生成可行储能策略。购电与外送互斥从模型层消除同一区域同一小时的购售套利，而不是只在结果中报告。

### 模型建立

总充电功率为

$$
C_{rt}=C_{rt}^{RE}+C_{rt}^{G}. \tag{50}
$$

负荷侧和新能源侧平衡分别为

$$
B_{rt}+R_{rt}^{use}+D_{rt}
=P_{rt}^{fac}+C_{rt}^{G}, \tag{51}
$$

$$
R_{rt}^{use}+C_{rt}^{RE}+S_{rt}+K_{rt}
=R_{rt}^{av}. \tag{52}
$$

所有能源流均非负。有效外送上限为

$$
\bar S_r
=\min(G_r^{export,max},S_r^{max}). \tag{53}
$$

SOC 初值与递推为

$$
E_{r,-1}=E_r^0, \tag{54}
$$

$$
E_{rt}
=E_{r,t-1}
+\eta_r^cC_{rt}\Delta t
-\frac{D_{rt}\Delta t}{\eta_r^d}. \tag{55}
$$

SOC 与终端约束为

$$
E_r^{min}\le E_{rt}\le E_r^{max}, \tag{56}
$$

$$
E_{r,2406}\ge E_r^0. \tag{57}
$$

充放电互斥为

$$
0\le C_{rt}\le C_r^{max}u_{rt}, \tag{58}
$$

$$
0\le D_{rt}\le D_r^{max}(1-u_{rt}),
\qquad u_{rt}\in\{0,1\}. \tag{59}
$$

购电与外送互斥为

$$
0\le B_{rt}
\le G_r^{import,max}v_{rt}, \tag{60}
$$

$$
0\le S_{rt}
\le\bar S_r(1-v_{rt}),
\qquad v_{rt}\in\{0,1\}. \tag{61}
$$

因此任一 $(r,t)$ 不可能同时满足 $B_{rt}>0$ 和 $S_{rt}>0$。第 $2406$ 小时禁止放电：

$$
D_{r,2406}=0. \tag{62}
$$

成本和碳排放仍按式（37）、（38）计算。净购电、正向峰值和波动为

$$
N_{rt}=B_{rt}-S_{rt}, \tag{63}
$$

$$
\widehat P_r^{peak}
=\max_t\max\{0,N_{rt}\}, \tag{64}
$$

$$
\widehat V
=\sum_r\sum_{t=1}^{2406}
|N_{rt}-N_{r,t-1}|. \tag{65}
$$

等效循环量为

$$
N_r^{cycle}
=
\frac{\sum_t(C_{rt}+D_{rt})\Delta t}
{2(E_r^{max}-E_r^{min})},
\qquad E_r^{max}>E_r^{min}. \tag{66}
$$

若 $E_r^{max}\le E_r^{min}$，输出 `invalid_storage_bounds` 并停止该区域储能优化。

### 求解方法

按各区域价格的 $25\%$ 和 $75\%$ 分位数执行：

1. 新能源优先直供；
2. 剩余新能源优先充电；
3. 低价时段允许电网充电；
4. 高价时段允许放电；
5. 剩余新能源只在 $v_{rt}=0$ 时外送，否则弃电；
6. 购电只在 $v_{rt}=1$ 时发生；
7. 第 $2406$ 小时只允许终端结算和必要充电，不允许放电。

逐时前向更新绝对 SOC，并复核式（51）–（62）。不预设成本或碳排放一定改善。

### 必须回答的输出

1. 各区域逐小时新能源直供、两类充电、放电、购电、外送、弃电和净购电。
2. 绝对 SOC 轨迹及 $E_{r,2406}$。
3. 成本、碳排放、式（64）峰值和式（65）波动的前后变化。
4. 同时充放电小时数和同时购电外送小时数；通过约束的正式结果两者均应为 $0$。
5. 各区域等效循环量或结构化不可用状态。
6. 文件：`q3_storage_schedule.csv`、`q3_soc.csv`、`q3_energy_flow.csv`、`q3_comparison.csv`、`q3_storage_plot.png`。

## 子问题 4：算—储—电联合情景优化

### 模型思路

任务侧使用式（1）–（14）的瞬时可行模型，能源侧使用式（50）–（62）。所有情景均从重新构造的可行基准开始，在变换后的真实输入上重新运行任务和能源规则，不按比例缩放既有结果。

旧问题四调度不复用；具体历史超限计数标记为 `pending_code_execution`，正式计数必须由代码阶段在真实附件上重新计算。

### 模型建立

问题四任务局部评分为

$$
score_{q4}
=z_C+1.5z_E-z_R+z_W+0.5z_L, \tag{67}
$$

其中 $z_C,z_E,z_R,z_W,z_L$ 由式（43）–（47）完整定义。

弹性任务总等待余量为

$$
M_W
=\sum_{i\in\mathcal I^{flex}}
(\bar f_i-d_i-a_i). \tag{68}
$$

当 $M_W>0$ 时，服务质量代理为

$$
Q_{service}
=1-
\frac{\sum_{i\in\mathcal I^{flex}}(s_i-a_i)}
{M_W}. \tag{69}
$$

若 $M_W\le0$，输出 `service_quality_unavailable`，并改报实时任务即时开工率、SLA 满足率和按期完成率；该场景不以不可用的 $Q_{service}$ 参与排序。

联合新能源利用率为

$$
U_{RE}
=
\frac{
\sum_{r,t}
(R_{rt}^{use}+C_{rt}^{RE}+S_{rt})\Delta t
}{
\sum_{r,t}R_{rt}^{av}\Delta t
},
\qquad
\sum_{r,t}R_{rt}^{av}\Delta t>0. \tag{70}
$$

分母不正时输出 `metric_unavailable` 并排除该指标对应的排序。

七情景为

$$
\{
\mathrm{baseline},
\mathrm{carbon10},
\mathrm{price0.8},
\mathrm{renewable0.8},
\mathrm{carbon20},
\mathrm{price1.2},
\mathrm{renewable1.2}
\}. \tag{71}
$$

设区域原始购电价算术平均为

$$
\bar\pi_r
=\frac1{2407}\sum_{t=0}^{2406}\pi_{rt}^{buy}. \tag{72}
$$

电价波动情景为

$$
\pi_{rt}^{buy\prime}
=\bar\pi_r+
\kappa(\pi_{rt}^{buy}-\bar\pi_r),
\qquad \kappa\in\{0.8,1.2\}. \tag{73}
$$

变换结果必须为有限值；题面附件若允许负电价则保留其真实经济含义，否则出现负值时输出 `invalid_price_scenario`，不作任意截断。

新能源情景为

$$
R_{rt}^{av\prime}
=\mu R_{rt}^{av},
\qquad \mu\in\{0.8,1.2\}. \tag{74}
$$

基准情景碳排放为 $E_{CO2}^{base}$，由基准联合方案按式（38）计算。碳情景硬约束为

$$
E_{CO2}\le0.9E_{CO2}^{base}
\quad(\mathrm{carbon10}), \tag{75}
$$

$$
E_{CO2}\le0.8E_{CO2}^{base}
\quad(\mathrm{carbon20}). \tag{76}
$$

碳情景从同一瞬时可行 incumbent 出发，对高 GPU-hour 弹性任务按不超过 $2000$ 个的实际可完成检查规模，依次使用

$$
(w_E,\kappa_C)
\in
\{(2,200),(4,500),(8,1000),(16,2000)\}, \tag{77}
$$

并以 $\pi+\kappa_Cc$ 驱动储能排序。每级完成后重新计算完整碳排放。

问题四购电和外送继续满足式（60）、（61）。因此价格情景、碳情景和新能源情景均不允许同一区域同一小时同时购电与外送。

### 求解方法

1. 重新构造并验证联合基准。
2. 按式（71）的固定顺序运行七个情景。
3. 每个情景在变换后的输入上重新运行任务局部改进和能源规则。
4. `checked_task_count` 只记录已经完整评价且完成接受或恢复的任务数。
5. 每个候选移动同时更新 $\chi$ 瞬时占用与 $\omega$ 重叠能量。
6. 每个完成情景执行逐类归一化残差验证。
7. carbon10 或 carbon20 未满足式（75）、（76）时，状态为 `target_infeasible_within_declared_heuristic`，排除候选比较、推荐排序和 Pareto 兼容表。

每个情景行必须包含：

- `scenario_status`
- `checked_task_count`
- `migration_count`
- `cost`
- `carbon`
- `latency`
- `service_quality_proxy`
- `renewable_utilization`
- 六区域 `regional_peak_import`
- `instant_gpu_violation_count`
- `instant_it_violation_count`
- `instant_facility_violation_count`
- `max_constraint_residual`
- `constraint_result`

### 必须回答的输出

1. 七情景逐项状态、实际检查任务数、迁移数、成本、碳、时延、服务质量代理、新能源利用率、六区域峰值和约束结果。
2. 推荐候选的任务调度、逐时能源流、储能动作和绝对 SOC。
3. 各任务类型迁移数量、方向、等待和时延分布。
4. 各区域新能源直供、充电、外送和弃电累计量。
5. 各情景瞬时 GPU、IT、设施峰值、超限计数和归一化最大残差；完成情景的三项超限计数必须均为 $0$。
6. 同时购电与新能源外送的小时数和能量；通过式（60）、（61）的正式结果两者均为 $0$，相应套利财务影响为 $0$。
7. 文件：`q4_schedule.csv`、`q4_energy_flow.csv`、`q4_soc.csv`、`q4_pareto.csv`、`q4_scenario_comparison.csv`、`q4_pareto.png`。
8. `q4_pareto.csv` 含 `ParetoCertified=false`、`Credibility=scenario-feasible`。

## 4. 逐类归一化残差门禁

不同量纲的原始残差不能直接求最大值。对每类约束 $j$，先定义非负违反量 $r_j^+$，再按该类物理尺度 $s_j$ 归一化：

$$
\varepsilon_j
=
\frac{r_j^+}{\max(1,s_j)}. \tag{78}
$$

各类尺度固定为：

- GPU 容量：$s_{rt}^{GPU}=G_r^{max}$；
- IT 功率：$s_{rt}^{IT}=P_r^{IT,max}$；
- 设施功率：$s_{rt}^{fac}=P_r^{fac,max}$；
- 购电边界：$s_r^{import}=G_r^{import,max}$；
- 外送边界：问题二取 $G_r^{export,max}$，问题三、四取 $\bar S_r$；
- 能源平衡：取该等式两侧所有非负流量绝对值的最大值；
- SOC 递推：取 $\max(1,E_r^{max})$；
- SOC 上下界与终端约束：取 $\max(1,E_r^{max}-E_r^{min},E_r^0)$；
- 任务唯一性、二元互斥和第 $2406$ 小时禁占用：尺度取 $1$；
- 到达、截止和网络时延：分别取 $\max(1,\bar f_i-a_i)$ 与 $\max(1,\ell_i^{max})$。

综合残差定义为

$$
\varepsilon_{\max}
=\max_j\varepsilon_j. \tag{79}
$$

完成候选必须满足

$$
\varepsilon_{\max}\le\tau_0,
\qquad \tau_0=10^{-6}. \tag{80}
$$

`max_constraint_residual` 输出式（79）的无量纲值。各类原始残差仍需分别输出并保留原单位，便于定位错误，但不得跨单位直接比较。

若任一尺度所依赖的物理容量缺失、非有限或不满足定义域，输出相应 `invalid_constraint_scale` 并停止，不用任意常数替代附件容量。

## 5. 共享墙钟与停止规则

单次执行共享

$$
B_{total}=300\ \mathrm s,\qquad
T_{tail}=15\ \mathrm s,\qquad
D_{search}=t_{start}+285\ \mathrm s. \tag{81}
$$

所有阶段使用同一 `time.monotonic()` 起点。累计绝对截止为：

| 阶段 | 自 $t_{start}$ 起累计截止 |
|---|---:|
| 输入与预测 | $45$ s |
| 问题一 | $70$ s |
| 问题二 | $130$ s |
| 问题三 | $160$ s |
| 问题四基准 | $235$ s |
| 七情景 | $270$ s |
| 中间产物 | $285$ s |
| 最终验证与文件 | $300$ s |

阶段提前结束的剩余时间可供后续阶段使用，但后续阶段仍不得越过自身绝对截止。每个候选开始前检查其所属阶段截止、共同搜索截止和总截止；循环内部再次检查时间。

达到搜索截止时：

1. 未启动候选不得启动；
2. 已启动且可中断的候选立即中断并恢复旧状态；
3. 已启动但未在总截止前完整结束的候选丢弃；
4. 不得使用部分结果；
5. 最后 $15$ 秒只允许完整残差复核和文件输出。

固定必答阶段若真实超时，必须携带实际耗时输出 `runtime_contract_failed`，不得减少检查规模后冒充完成。实际检查任务数只能记录完整完成的任务。

## 6. 统一验证规则

1. 每个任务恰好执行一次；实时任务在到达时刻开工。
2. 实时任务缺失 `LatestFinishHour` 时按式（1）使用 $2406$；弹性任务缺失该字段时结构化停止。
3. 每个任务满足到达、时延、有效截止和第 $2406$ 小时禁占用约束。
4. 对任务触及的每个整数小时，按完整 $g_i$ 检查 GPU 容量，不乘 $\omega$。
5. 对任务触及的每个整数小时，按完整 $g_ip_{k_i}^{GPU}$ 检查 IT 和设施瞬时功率。
6. 能源成本、碳排放、新能源和储能流按真实重叠时长 $\omega$ 计算。
7. 第 $2376$–$2399$ 小时容量复核必须包含式（29）的存量运行任务。
8. 每次任务移动同时更新 $\chi$ 瞬时占用与 $\omega$ 重叠能量。
9. 问题二、四从重新构造的完整可行调度开始，不读取旧调度；旧具体超限计数为 `pending_code_execution`。
10. 能源守恒、购售电边界、外送来源、SOC 递推、充放电互斥、购电外送互斥和终端 SOC 均逐时复核。
11. 正式峰值只按式（64）从最终净购电序列复算。
12. 不同单位的原始残差必须按式（78）归一化后才能汇总。
13. 所有业务分母先检查正性；不满足时输出结构化不可用状态，不以 $\epsilon$ 替代。
14. 只有满足式（80）且所有必需指标有限的候选才能标记 `completed`。
15. carbon10、carbon20 未达硬目标时必须排除，不能用最接近目标的方案冒充可行。
16. `global_optimality=not_certified`；局部评分和有限候选比较不解释为完整 Pareto 前沿。

## 7. Verifier 修复核对表

| Block issue | 修复公式或约束位置 | 可计算性与有限输出保证 |
|---|---|---|
| 预测模型选型后未使用截至第2375小时的数据重新训练 | 子问题一式（24）、（25）及求解步骤2–4 | 明确区分 `selection_fit` 与 `final_fit`；验证只负责选型，最终参数由截至2375小时的全部有效样本重新拟合，测试区间递归预测且不读取真实未来值 |
| 所有任务直接使用 `LatestFinishHour`，实时任务字段缺失时候选集合不可计算 | 式（1）、（2） | 实时任务缺失时确定性取2406；弹性任务缺失时输出 `invalid_elastic_deadline` 并停止，NaN不进入 `min`、比较或候选集合 |
| 问题三、四未落实购电与外送互斥，存在套利风险 | 式（60）、（61），问题四继续强制使用同组约束 | 二元变量 $v_{rt}$ 使同一区域同一小时至多一种方向为正；正式结果同时购电外送小时数和套利影响均为0 |
| 最后24小时未明确计入第2376小时前已开工但仍运行的存量任务 | 式（29）、（30） | 先构造完整基准调度，再把跨越2376边界的任务连同既定区域和开工时刻带入容量、IT及设施功率复核，避免低估占用 |
| 不同量纲的原始约束残差被直接统一取最大值 | 式（78）–（80） | GPU、MW、MWh、时延及无量纲约束分别按本类物理尺度归一化；`max_constraint_residual` 只汇总无量纲残差，原始残差另行保留单位 |
| 模型阶段未运行代码却引用旧版具体超限计数 | 问题二、问题四模型思路及统一验证规则第9条 | 删除本轮已验证式的具体计数声明，统一标为 `pending_code_execution`；正式超限数量只允许由代码阶段在真实附件上复算 |