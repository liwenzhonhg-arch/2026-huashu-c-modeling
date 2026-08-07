# 数学模型

## 符号说明

| 符号 | 含义 | 类型 | 取值范围、单位与来源 |
|------|------|------|----------------------|
| \(\mathcal R,\mathcal K\) | 区域、任务类型集合 | 题面直接给定参数 | 六区域、三类任务 |
| \(\mathcal I\) | 实际到达任务集合 | 可观测集合 | `workload_trace.xlsx` |
| \(\mathcal T_A,\mathcal T_C\) | 主到达、收尾时域 | 题面直接给定 | \(0{:}2399\)、\(2400{:}2405\)，h |
| \(\Delta t\) | 电力时间步长 | 固定参数 | \(1\) h |
| \(a_i,d_i,f_i\) | 到达、连续执行时长、最晚完成时点 | 可观测/派生参数 | \(d_i=\mathrm{EstimatedDuration\_min}_i/60\)，h |
| \(g_i,k_i,o_i\) | GPU需求、类型、来源区域 | 可观测参数 | 任务附件 |
| \(\ell_{or},\ell_i^{\max}\) | 单向时延、任务时延上限 | 可观测参数 | `network_latency.xlsx`、任务附件，ms |
| \(x_{irs}\) | 任务在区域 \(r\)、整数时刻 \(s\) 开工 | 二元决策变量 | \(\{0,1\}\) |
| \(q_{it}(s)\) | 任务在小时 \(t\) 的重叠时长 | 派生参数 | \([0,1]\)，h |
| \(G_r\) | 可调度GPU容量 | 可观测参数 | `GPU_information.xlsx` |
| \(p_k^{GPU}\) | 单位等效GPU的IT功率 | 可观测参数 | `power_mapping.xlsx`，MW/GPU |
| \(P_{rt}^{AI},P_{rt}^{nonAI},P_{rt}^{IT}\) | AI、非AI及总IT负荷 | 派生变量/参数 | MW |
| \(PUE_r,P_{rt}^{fac}\) | PUE、设施负荷 | 参数/派生变量 | \(P_{rt}^{fac}=PUE_rP_{rt}^{IT}\)，MW |
| \(A_{rt}^{RE},U_{rt}^{RE}\) | 可用、直接消纳新能源 | 参数/决策变量 | MW |
| \(P_{rt}^{RE,ch},P_{rt}^{grid,ch}\) | 新能源、电网充电 | 连续决策变量 | MW |
| \(P_{rt}^{ch},P_{rt}^{dis}\) | 总充电、放电功率 | 连续决策变量 | MW |
| \(P_{rt}^{buy},P_{rt}^{sell}\) | 购电、新能源外送 | 连续决策变量 | MW |
| \(P_{rt}^{curt}\) | 弃风弃光 | 连续决策变量 | MW |
| \(E_{rt},E_r^0\) | 时段末SOC、初始SOC | 状态/参数 | MWh；初值来自 `InitialSOC_MWh` |
| \(\pi_{rt}^{buy},\pi_{rt}^{sell},c_{rt}\) | 购价、售价、碳强度 | 可观测参数 | 区域逐时附件 |
| \(P_{rt}^{grid,\max},P_{rt}^{export,\max}\) | 购电、外送硬上限 | 可观测参数 | `MaxGridImport_MW`、`MaxGridExport_MW` |
| \(C_{\mathrm{op}},E_{\mathrm{CO2}}\) | 净运行成本、购电碳排放 | 目标/指标 | 元、tCO2 |
| \(L_{\mathrm{net}}\) | GPU-hour加权平均网络时延 | 指标 | ms |
| \(U_{\mathrm{RE}}\) | 新能源利用率 | 指标 | \([0,1]\)或结构化不可用 |
| \(N_{rt},P_r^{peak},V_r\) | 净购电、峰值、绝对爬坡总量 | 派生量 | MW、MW、MW |
| \(Q_{\mathrm{service}}\) | 服务质量 | 指标 | \([0,1]\) |
| \(H_{\mathrm{roll}},H_{\mathrm{commit}}\) | 窗口长度、每窗固定长度 | 固定算法参数 | \(24\) h、\(6\) h |
| \(B_{\mathrm{total}},D_{\mathrm{search}}\) | 总预算、共同搜索截止 | 固定运行参数 | \(300\) s、起点后 \(285\) s |

本题没有几何量，尺寸链、坐标原点、观测位置及空/满边界均不适用。

## 统一任务与负荷内核

任务在小时区间 \([t,t+1)\) 的实际重叠时长为

$$
q_{it}(s)=\max\{0,\min(t+1,s+d_i)-\max(t,s)\}. \tag{1}
$$

合法候选集合为

$$
\Omega_i=\{(r,s):s\ge a_i,\ s+d_i\le\min(f_i,2406),\
\ell_{o_ir}\le\ell_i^{\max}\}. \tag{2}
$$

实时任务另固定 \(s=a_i\)。若 \(\Omega_i=\varnothing\)，结构化输出 `task_infeasible` 并停止相关调度，不放松硬约束。每个任务恰执行一次：

$$
\sum_{(r,s)\in\Omega_i}x_{irs}=1,\qquad x_{irs}\in\{0,1\}. \tag{3}
$$

负荷和容量为

$$
P_{rt}^{AI}=\sum_{i,s}g_ip_{k_i}^{GPU}q_{it}(s)x_{irs},\quad
P_{rt}^{IT}=P_{rt}^{nonAI}+P_{rt}^{AI},\quad
P_{rt}^{fac}=PUE_rP_{rt}^{IT}, \tag{4}
$$

$$
\sum_{i,s}g_iq_{it}(s)x_{irs}\le G_r,\quad
P_{rt}^{IT}\le P_r^{IT,\max},\quad
P_{rt}^{fac}\le P_r^{fac,\max}. \tag{5}
$$

任务不得占用第2406小时。

## 子问题 1：GPU需求预测与末端基础调度

### 模型思路

按区域—任务类型—小时聚合需求，比较24小时、168小时季节性基线与标准岭回归。使用 \(0\!-\!2351\) 小时训练、\(2352\!-\!2375\) 小时验证；选型后用 \(0\!-\!2375\) 小时重训，\(2376\!-\!2399\) 小时仅测试一次。最后24小时调度必须使用实际到达任务。

### 模型建立

$$
D_{rkt}=\sum_{i:o_i=r,k_i=k,a_i=t}g_i,\qquad
H_{rkt}=\sum_{i:o_i=r,k_i=k,a_i=t}g_id_i. \tag{6}
$$

季节性基线为

$$
\widehat D_{rkt}^{(24)}=D_{rk,t-24},\qquad
\widehat D_{rkt}^{(168)}=D_{rk,t-168}. \tag{7}
$$

修正后的增强模型明确采用“标准岭回归拟合后截零”：

$$
(\widehat\beta_0,\widehat{\boldsymbol\beta})
=\arg\min_{\beta_0,\boldsymbol\beta}
\sum_{\mathcal T_{\mathrm{train}}}
(D_{rkt}-\beta_0-\boldsymbol\beta^\top\mathbf z_{rkt})^2
+\lambda\|\boldsymbol\beta\|_2^2, \tag{8}
$$

$$
\widehat D_{rkt}=\max\{0,\widehat\beta_0+
\widehat{\boldsymbol\beta}^{\top}\mathbf z_{rkt}\}. \tag{9}
$$

特征只含预测时点以前的滞后、滚动统计及周期编码。评价使用MAE、RMSE和

$$
WAPE=\frac{\sum_j|D_j-\widehat D_j|}{\sum_j|D_j|}. \tag{10}
$$

仅当分母为正时计算WAPE；否则输出 `validation_unavailable`，改报MAE和有限预测率。

基础调度按词典序依次最小化：未完成任务数、最大延迟、总等待、总网络时延。第一项目标最优值必须为0。GPU利用率为

$$
Util_{rt}^{GPU}=
\frac{\sum_{i,s}g_iq_{it}(s)x_{irs}}{G_r}\times100\%. \tag{11}
$$

### 求解方法

增强预测须在验证集优于季节性基线才采用。MILP必须返回完整可行解；否则仅可交付满足全部硬约束的后备启发式解，并标记为 `heuristic_feasible`。

### 必须回答的输出

1. 区域—任务类型统计表及主要时序图。
2. 数据划分和模型比较结果。
3. 总体、分区域、分类型MAE、RMSE、WAPE。
4. 第2376–2399小时预测值与实际值。
5. 实际任务的任务级调度表。
6. 跨越2399小时任务的结清方案及未结清数。
7. 最后24小时甘特图。
8. 各区域2376–2405小时GPU利用率。
9. `q1_statistics.xlsx`、`q1_forecast.xlsx`、`q1_schedule.xlsx`、`q1_gantt.png`、`q1_gpu_utilization.png`、`q1_validation.json`。

## 子问题 2：无储能的碳感知任务调度

### 模型思路

以实际任务及实际逐时电力参数联合优化执行区域和开工时刻。问题二不优化储能，故充电、放电及SOC均不进入决策变量。

### 模型建立

新能源去向守恒修正为

$$
U_{rt}^{RE}+P_{rt}^{sell}+P_{rt}^{curt}=A_{rt}^{RE}. \tag{12}
$$

本地负荷平衡为

$$
P_{rt}^{buy}+U_{rt}^{RE}=P_{rt}^{fac}. \tag{13}
$$

联立可得且仅得附件总平衡：

$$
P_{rt}^{buy}+A_{rt}^{RE}
=P_{rt}^{fac}+P_{rt}^{sell}+P_{rt}^{curt}. \tag{14}
$$

因此外送只记账一次。问题二明确固定

$$
P_{rt}^{ch}=P_{rt}^{dis}=P_{rt}^{RE,ch}
=P_{rt}^{grid,ch}=0. \tag{15}
$$

购售电硬边界为

$$
0\le P_{rt}^{buy}\le P_{rt}^{grid,\max},\qquad
0\le P_{rt}^{sell}\le
\min(P_{rt}^{export,\max},S_r^{\max}). \tag{16}
$$

成本、碳排放、加权平均时延和新能源利用率分别为

$$
C_{\mathrm{op}}=\sum_{r,t}
(\pi_{rt}^{buy}P_{rt}^{buy}-\pi_{rt}^{sell}P_{rt}^{sell})\Delta t, \tag{17}
$$

$$
E_{\mathrm{CO2}}=\sum_{r,t}c_{rt}P_{rt}^{buy}\Delta t, \tag{18}
$$

$$
L_{\mathrm{net}}=
\frac{\sum_{i,r,s}g_id_i\ell_{o_ir}x_{irs}}
{\sum_i g_id_i}, \tag{19}
$$

$$
U_{\mathrm{RE}}=
\frac{\sum_{r,t}(U_{rt}^{RE}+P_{rt}^{sell})\Delta t}
{\sum_{r,t}A_{rt}^{RE}\Delta t}. \tag{20}
$$

式(19)、(20)仅在分母为正时计算；否则输出 `metric_unavailable`，该场景不参与对应Pareto排序，并分别改报任务数或新能源利用电量、弃电量。

优化模型为

$$
\min C_{\mathrm{op}}
\quad\text{s.t.}\quad
E_{\mathrm{CO2}}\le\epsilon_C,\ 
L_{\mathrm{net}}\le\epsilon_L,\ 
U_{\mathrm{RE}}\ge\epsilon_U, \tag{21}
$$

并满足式(2)–(5)、(12)–(16)。

### 求解方法

采用24小时窗口，每次固定前6小时决策，相邻窗口重叠18小时；已开工任务的区域和后续占用必须固定传递。候选生成只能剔除违反到达、截止、时延或2406边界的组合。

### 必须回答的输出

1. 每个任务的执行区域、开工及完成时刻。
2. 逐区域逐小时AI IT、总IT、设施负荷、直接利用、购电、外送和弃电。
3. 成本、碳排放、平均及95分位时延、新能源利用率。
4. 相对基础调度的绝对和相对变化。
5. Pareto表和前沿图。
6. 分任务类型迁移、GPU-hour、等待和时延统计。
7. `q2_task_schedule.xlsx`、`q2_energy_dispatch.xlsx`、`q2_metrics.json`、`q2_pareto.csv`、`q2_pareto.png`、`q2_validation.json`。

## 子问题 3：固定负荷下的储能协同优化

### 模型思路

严格固定题面给定负荷：

$$
P_{rt}^{fac}=PUE_r(P_{rt}^{baseAI}+P_{rt}^{nonAI}). \tag{22}
$$

仅优化新能源分配、储能、购售电和弃电。

### 模型建立

修正后的新能源分源和电力平衡为

$$
U_{rt}^{RE}+P_{rt}^{RE,ch}
+P_{rt}^{sell}+P_{rt}^{curt}=A_{rt}^{RE}, \tag{23}
$$

$$
P_{rt}^{buy}+U_{rt}^{RE}+P_{rt}^{dis}
=P_{rt}^{fac}+P_{rt}^{grid,ch}, \tag{24}
$$

$$
P_{rt}^{ch}=P_{rt}^{RE,ch}+P_{rt}^{grid,ch}. \tag{25}
$$

将式(23)代入式(24)，恰得

$$
P_{rt}^{buy}+A_{rt}^{RE}+P_{rt}^{dis}
=P_{rt}^{fac}+P_{rt}^{ch}
+P_{rt}^{sell}+P_{rt}^{curt}, \tag{26}
$$

故外送不再重复计算。

SOC动力学为

$$
E_{r,-1}=E_r^0,\quad
E_{rt}=E_{r,t-1}+\eta_r^cP_{rt}^{ch}\Delta t
-\frac{P_{rt}^{dis}\Delta t}{\eta_r^d}, \tag{27}
$$

$$
E_r^{min}\le E_{rt}\le E_r^{max},\qquad
E_{r,2406}\ge E_r^0. \tag{28}
$$

充放电互斥为

$$
0\le P_{rt}^{ch}\le P_r^{ch,\max}z_{rt}^{ch},\qquad
0\le P_{rt}^{dis}\le P_r^{dis,\max}(1-z_{rt}^{ch}). \tag{29}
$$

购售电继续满足式(16)。定义

$$
N_{rt}=P_{rt}^{buy}-P_{rt}^{sell},\qquad
P_r^{peak}\ge N_{rt}, \tag{30}
$$

$$
v_{rt}\ge N_{rt}-N_{r,t-1},\quad
v_{rt}\ge-(N_{rt}-N_{r,t-1}),\quad
V_r=\sum_{t=1}^{2406}v_{rt}. \tag{31}
$$

新能源利用率为

$$
U_{\mathrm{RE}}=
\frac{\sum_{r,t}(U_{rt}^{RE}+P_{rt}^{RE,ch}+P_{rt}^{sell})\Delta t}
{\sum_{r,t}A_{rt}^{RE}\Delta t}. \tag{32}
$$

零分母分支与式(20)相同。优化采用

$$
\min C_{\mathrm{op}}
\quad\text{s.t.}\quad
E_{\mathrm{CO2}}\le\epsilon_C,\ 
P_r^{peak}\le\epsilon_{P,r},\
V_r\le\epsilon_{V,r}. \tag{33}
$$

### 求解方法

使用含充放电互斥的MILP。不存在最优动作标签；通过式(23)–(29)残差、终端SOC、交易边界、成本及碳排复算验证。不可行情景输出有限状态和冲突约束，不输出NaN或Inf。

### 必须回答的输出

1. 六区域0–2406小时全部能源流及SOC。
2. 每区终端SOC及相对初始SOC裕量。
3. 优化前后成本、碳排放、峰值净购电和绝对爬坡量。
4. 每区等效循环量、充放电小时数及同时充放电违约数。
5. 新能源利用率和各去向累计电量。
6. `q3_storage_dispatch.xlsx`、`q3_comparison.xlsx`、`q3_metrics.json`、`q3_soc.png`、`q3_grid_profile.png`、`q3_validation.json`。

## 子问题 4：多区域算—储—电联合优化

### 模型思路

联合使用式(2)–(5)的任务约束和式(23)–(31)的修正能源约束，统一优化任务迁移、开工时段、新能源分配、储能与购售电。

### 模型建立

服务质量四个分量为实时即时开工率 \(R_{\mathrm{instant}}\)、SLA满足率 \(R_{\mathrm{SLA}}\)、按期完成率 \(R_{\mathrm{deadline}}\) 和等待得分

$$
S_W=\min\left\{1,\max\left\{0,1-\frac{\overline W}{W^{ref}}\right\}\right\}. \tag{34}
$$

其中 \(\overline W\) 是弹性任务平均等待时间，\(W^{ref}\) 是同一任务集基础调度的平均等待时间。若 \(W^{ref}=0\)，删除等待项；若任一比率对应任务集合为空，该项记为 `not_applicable`。剩余项权重重新归一化，不以任意小数替代业务分母。

固定原始权重为

$$
(w_1,w_2,w_3,w_4)=(0.25,0.25,0.25,0.25), \tag{35}
$$

$$
Q_{\mathrm{service}}=
w_1R_{\mathrm{instant}}+
w_2R_{\mathrm{SLA}}+
w_3R_{\mathrm{deadline}}+
w_4S_W. \tag{36}
$$

因此 \(Q_{\mathrm{service}}\in[0,1]\)。正式多目标模型为

$$
\min C_{\mathrm{op}}
$$

$$
\text{s.t.}\quad
E_{\mathrm{CO2}}\le\epsilon_C,\quad
L_{\mathrm{net}}\le\epsilon_L,\quad
Q_{\mathrm{service}}\ge\epsilon_Q,\quad
U_{\mathrm{RE}}\ge\epsilon_U,\quad
P_r^{peak}\le\epsilon_{P,r}. \tag{37}
$$

情景参数固定为：

$$
\alpha_C\in\{1.0,0.9,0.8\},\quad
\beta_{\mathrm{price}}\in\{0.75,1.0,1.25\},\quad
\beta_{\mathrm{RE}}\in\{0.8,1.0,1.2\}. \tag{38}
$$

电价情景保持小时结构：

$$
\pi_{rt}^{buy,sc}=
\bar\pi_r+\beta_{\mathrm{price}}
(\pi_{rt}^{buy}-\bar\pi_r). \tag{39}
$$

新能源情景为

$$
A_{rt}^{RE,sc}=
\max\{0,\beta_{\mathrm{RE}}A_{rt}^{RE}+\delta_{rt}^{sc}\}. \tag{40}
$$

扰动使用固定种子2026、零均值，标准差固定为各区域正新能源出力小时均值的10%；截断只保证物理非负，不用于调整优化结果。

### 封闭滚动求解与共享预算

窗口长度固定为24小时，每窗仅承诺前6小时，重叠18小时；最后窗口延伸到2406。窗口间传递：

1. 已开工任务的固定区域及全部后续占用；
2. 窗口末端绝对SOC；
3. 尚未开工任务及其原始截止时点。

单轮运行使用 `time.monotonic()`，共同合同为

$$
B_{\mathrm{total}}=300\text{ s},\qquad
D_{\mathrm{search}}=t_{\mathrm{start}}+285\text{ s}. \tag{41}
$$

每次MILP启动前令

$$
T_{\mathrm{limit}}=
\max\{0,\min(30,\ D_{\mathrm{search}}-\mathrm{time.monotonic}())\}\text{ s}. \tag{42}
$$

当 \(T_{\mathrm{limit}}=0\) 时不再启动候选。已启动求解必须在其time limit内返回；仅接受求解器成功或预声明的“限时但已有完整可行整数解”状态，超时无完整解、未完成窗口或部分结果均丢弃。285秒后只允许验证和文件输出，且必须在300秒前结束。固定必答工作若超时，记录实际耗时并结构化失败，不缩减任务集伪装完成。

### 必须回答的输出

1. 折中方案完整任务调度表和逐区域逐小时能源表。
2. 成本、碳排、时延、服务质量、新能源利用率和六区域峰值净购电。
3. Pareto候选、非支配标记、理想点距离及折中方案编号。
4. 各情景绝对指标、相对变化率和可行性状态。
5. 各情景迁移、等待、储能循环、购售电量和新能源去向。
6. 求解状态、最优间隙、窗口衔接残差及缩小实例对照。
7. `q4_joint_schedule.xlsx`、`q4_scenario_comparison.xlsx`、`q4_metrics.json`、`q4_pareto.csv`、`q4_pareto.png`、`q4_scenario_dashboard.png`、`q4_validation.json`。

## 统一结果审计

正式结果至少复算

$$
\rho_{\mathrm{task}}=
\max_i\left|\sum_{r,s}x_{irs}-1\right|, \tag{43}
$$

$$
\rho_{\mathrm{energy}}=
\max_{r,t}\left|
P_{rt}^{buy}+A_{rt}^{RE}+P_{rt}^{dis}
-P_{rt}^{fac}-P_{rt}^{ch}-P_{rt}^{sell}-P_{rt}^{curt}
\right|, \tag{44}
$$

$$
\rho_{\mathrm{SOC}}=
\max_{r,t}\left|
E_{rt}-E_{r,t-1}-\eta_r^cP_{rt}^{ch}\Delta t
+\frac{P_{rt}^{dis}\Delta t}{\eta_r^d}
\right|. \tag{45}
$$

数值容差由代码阶段按求解器和数据尺度预声明，不由本次误差自适应放宽。报告区分 `optimal`、`time_limit_feasible`、`heuristic_feasible`、`infeasible` 和 `metric_unavailable`。

## Verifier 修复核对表

| Block issue | 修复位置 | 可计算性与物理保证 |
|---|---|---|
| 问题二外送重复计算 | 式(12)–(14) | 分源守恒只记录一次外送；代数消元严格恢复附件总平衡。 |
| 问题三分源错误且问题四继承 | 式(23)–(26)，问题四继承该组公式 | 新能源充电只在新能源分源中扣除，电网充电只在负荷平衡中出现；消元后与附件总平衡完全一致。 |
| 问题二正文无储能但方程含储能 | 式(15)及问题二变量定义 | 四类储能功率固定为零且不作为问题二优化变量，正文、方程与结构化JSON一致。 |
| 服务质量等待项可能为负 | 式(34)–(36) | 等待得分双侧截断至 \([0,1]\)；零参考值或空任务集合删除对应项并重新归一化，禁止零除。 |
| 滚动窗口和剩余时间限制不封闭 | 式(41)–(42)及“封闭滚动求解” | 固定24小时窗口、6小时承诺、18小时重叠；每次求解使用由共同截止直接计算的有限time limit，未完成候选不进入正式结果。 |