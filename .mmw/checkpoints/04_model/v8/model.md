# 数学模型

## 1. 模型边界与统一口径

建立六区域算力任务—电力—新能源—储能联合调度模型。区域集合为

$$
\mathcal R=\{\mathrm A,\mathrm B,\mathrm C,\mathrm D,\mathrm E,\mathrm F\}.
$$

任务到达、执行和能源结算时域分别为

$$
\mathcal T^{arr}=\{0,\ldots,2399\},
$$

$$
\mathcal T^{run}=\{0,\ldots,2405\},
$$

$$
\mathcal T^{energy}=\{0,\ldots,2406\}.
$$

时间步长为 $\Delta t=1\ \mathrm h$。第 $2400$–$2405$ 小时没有新任务，只结清此前到达的弹性任务；第 $2406$ 小时不执行任务，只结算电力流和终端 SOC。所有任务不可抢占、不可拆分、不可中途迁移。

### 几何量核验

本题不涉及容器或空间尺寸链。区域位置不转换为欧氏距离，通信关系完全由附件中的有向时延矩阵表示。

| 几何或空间关系 | 证据类别 | 建模处理 |
|---|---|---|
| 六个区域的存在及功能定位 | 题面直接给定 | 作为离散区域集合 |
| 区域间单向网络时延 | 题面直接给定 | 使用附件有向时延矩阵 |
| 区域物理距离和线路拓扑 | 待确认且题目明确不要求 | 不纳入模型 |
| 网络带宽、迁移数据量、传输能耗 | 题面明确排除 | 不纳入模型 |

不存在由图示尺寸链推导的几何量，也不设置 `geometry_unconfirmed`。

## 2. 符号说明

| 符号 | 含义、单位与数据来源/代理口径 | 类型 | 取值范围 |
|---|---|---|---|
| $i,r,t,s,k$ | 任务、区域、小时、开工小时、任务类型索引 | 索引 | 附件给定集合 |
| $\mathcal I^{flex}$ | 批量推理与 AI 训练任务集合 | 派生集合 | $\mathcal I$ 的子集 |
| $a_i$ | 到达时刻，来自 `workload_trace.xlsx`，h | 可观测参数 | $0$–$2399$ |
| $d_i$ | `EstimatedDuration_min/60`，h | 可观测参数 | $>0$ |
| $g_i$ | 运行时持续占用的等效 GPU 数 | 可观测参数 | $>0$ |
| $k_i,o_i$ | 任务类型、来源区域 | 可观测参数 | 附件类别 |
| $f_i^{late}$ | 最晚完成时点，来自任务表；缺失时按题面规则核验后取 $2406$，不得把空值当作 $0$ | 可观测参数 | $\le2406$ |
| $\ell_i^{max}$ | 任务最大允许时延，ms | 可观测参数 | $\ge0$ |
| $\ell_{or}$ | 区域 $o$ 到 $r$ 的单向网络时延，ms | 可观测参数 | $\ge0$ |
| $x_{irs}$ | 任务是否在区域 $r$、时刻 $s$ 开工 | 二元变量 | $\{0,1\}$ |
| $\omega_{it}(s)$ | 任务在小时 $t$ 内的重叠时长；因 $\Delta t=1$ h，数值也等于小时占比 | 派生参数 | $[0,1]$ h |
| $G_r^{max}$ | 区域可调度 GPU 容量，来自 `GPU_information.xlsx` | 可观测参数 | $>0$ GPU |
| $p_k^{GPU}$ | 每等效 GPU 的平均 IT 功率，来自 `power_mapping.xlsx` | 可观测参数 | $>0$ MW/GPU |
| $P_{rt}^{AI}$ | 任务在该小时形成的平均 AI IT 功率 | 派生变量 | $\ge0$ MW |
| $P_{rt}^{NA}$ | 不可迁移非 AI IT 负荷 | 可观测参数 | $\ge0$ MW |
| $P_{rt}^{BAI}$ | 问题三给定的基线 AI IT 负荷 | 可观测参数 | $\ge0$ MW |
| $P_{rt}^{IT},P_{rt}^{fac}$ | 总 IT 平均功率、设施侧平均功率 | 派生变量 | $\ge0$ MW |
| $P_r^{IT,max},P_r^{fac,max}$ | IT、设施功率上限 | 可观测参数 | $>0$ MW |
| $\mathrm{PUE}_r$ | 区域 PUE | 可观测参数 | $>0$ |
| $R_{rt}^{av}$ | 可用新能源功率 | 可观测参数 | $\ge0$ MW |
| $R_{rt}^{use}$ | 新能源直接供设施负荷功率 | 连续变量 | $\ge0$ MW |
| $C_{rt}^{RE},C_{rt}^{G}$ | 新能源充电、电网充电功率 | 连续变量 | $\ge0$ MW |
| $C_{rt}$ | 储能总充电功率，$C_{rt}^{RE}+C_{rt}^{G}$ | 派生变量 | $\ge0$ MW |
| $D_{rt}$ | 储能放电功率 | 连续变量 | $\ge0$ MW |
| $B_{rt}$ | 电网购电功率，包含电网充电来源 | 连续变量 | $[0,P_{rt}^{grid,max}]$ MW |
| $S_{rt}$ | 仅由本地新能源分配得到的外送功率 | 连续变量 | 有界非负 MW |
| $K_{rt}$ | 弃风弃光功率 | 连续变量 | $\ge0$ MW |
| $P_{rt}^{grid,max}$ | 区域购电上限 | 可观测参数 | $\ge0$ MW |
| $P_{rt}^{export,max},S_r^{max}$ | 区域级外送边界、储能表外送上限 | 可观测参数 | $\ge0$ MW |
| $E_{rt}$ | 小时 $t$ 运行后的绝对 SOC | 状态变量 | $[E_r^{min},E_r^{max}]$ MWh |
| $E_r^0$ | 第 $0$ 小时运行前初始 SOC | 可观测参数 | MWh |
| $C_r^{max},D_r^{max}$ | 储能充、放电功率上限 | 可观测参数 | $\ge0$ MW |
| $\eta_r^c,\eta_r^d$ | 充、放电效率 | 可观测参数 | $(0,1]$ |
| $u_{rt}^c$ | 充放电模式变量 | 二元变量 | $\{0,1\}$ |
| $N_{rt}$ | 净购电功率，$B_{rt}-S_{rt}$ | 派生变量 | 有界实数 MW |
| $P_r^{peak}$ | 正向净购电峰值，即 $\max_t\max(0,N_{rt})$ 的线性化变量 | 辅助变量 | $\ge0$ MW |
| $z_{rt}$ | 相邻小时净购电绝对变化量 | 辅助变量 | $\ge0$ MW |
| $\pi_{rt}^{buy},\pi_{rt}^{sell}$ | 购、售电价 | 可观测参数 | 元/MWh |
| $c_{rt}$ | 电网购电碳强度 | 可观测参数 | tCO2/MWh |
| $C_{op}$ | 购电支出减新能源售电收入 | 目标/指标 | 元 |
| $E_{CO2}$ | 电网购电引起的累计碳排放 | 目标/指标 | tCO2 |
| $L_{net}$ | GPU-hour 加权平均网络时延 | 代理指标 | ms 或“不可计算” |
| $U_{RE}$ | 新能源统一口径利用率 | 指标 | $[0,1]$ 或“不可计算” |
| $M_W$ | 全部弹性任务最大可等待时间之和 | 派生量 | $\ge0$ h |
| $Q_{service}$ | 最大可等待时间归一化的服务质量代理，不是真实满意度标签 | 代理指标 | $[0,1]$ 或“不可计算” |
| $B_{total}$ | Coder 单次共享墙钟上限 | 固定参数 | $300$ s |
| $T_{tail}$ | 复核及文件输出预留 | 固定参数 | $15$ s |
| $D_{search}$ | 共用搜索截止，$t_{start}+285$ | 固定规则 | 单调时钟 |
| $H,O,H_{max}$ | 滚动窗口、重叠区、最大窗口 | 固定参数 | $168,24,336$ h |
| $N_\varepsilon^{max}$ | 每个多目标子问题最多处理的 ε 组合数 | 固定参数 | $12$ |
| $t_{solve}^{max}$ | 单个 MILP 候选求解上限 | 固定参数 | $30$ s |
| $\tau$ | 求解器数值残差容差，由代码阶段预声明并记录 | 验证参数 | 正数 |

可观测量包括任务需求、逐时电力参数、容量、PUE、功率映射、网络时延和储能设备参数。真实最优调度与最优储能动作不可观测，因此不使用准确率、召回率或混淆矩阵；代理验证采用硬约束残差、求解器状态、成本和碳排放复算及 Pareto 非支配性。

## 3. 共享任务与负荷模型

### 3.1 小时重叠和候选开工集合

若任务 $i$ 在小时 $s$ 开工，其执行区间为 $[s,s+d_i)$。与小时 $[t,t+1)$ 的重叠时长为

$$
\omega_{it}(s)=
\max\left\{0,\min(s+d_i,t+1)-\max(s,t)\right\}. \tag{1}
$$

候选开工集合为

$$
\mathcal S_{ir}=
\left\{
s\in\mathcal T^{run}:
s\ge a_i,\ 
s+d_i\le\min(f_i^{late},2406),\
\ell_{o_i r}\le\ell_i^{max}
\right\}. \tag{2}
$$

实时推理还满足 $\mathcal S_{ir}\subseteq\{a_i\}$。若任务对全部区域的候选集合均为空，则结构化输出 `infeasible_precheck` 并停止相应调度，不伪造方案。

### 3.2 唯一执行与不可抢占

$$
\sum_{r\in\mathcal R}\sum_{s\in\mathcal S_{ir}}x_{irs}=1,
\qquad x_{irs}\in\{0,1\}. \tag{3}
$$

单个二元变量同时选定区域和完整执行区间，因而任务不可拆分、不可抢占、不可中途迁移。

### 3.3 GPU-hour 与功率约束

小时 $t$ 内累计 GPU-hour 为

$$
G_{rt}=\sum_i\sum_{s\in\mathcal S_{ir}}
g_i\omega_{it}(s)x_{irs}. \tag{4}
$$

按题面规定的小时重叠折算口径，容量约束严格写为

$$
G_{rt}\le G_r^{max}\Delta t. \tag{5}
$$

式（5）比较的是一小时累计 GPU-hour 与该小时可提供的 $G_r^{max}\Delta t$，不是额外构造的任意时刻瞬时并发约束。

AI IT 负荷为该小时平均功率：

$$
P_{rt}^{AI}=
\sum_i\sum_{s\in\mathcal S_{ir}}
g_ip_{k_i}^{GPU}
\frac{\omega_{it}(s)}{\Delta t}x_{irs}. \tag{6}
$$

由于 $\Delta t=1$ h，式（6）与原数值表达一致，但量纲明确为 MW。问题一、二、四采用

$$
P_{rt}^{IT}=P_{rt}^{NA}+P_{rt}^{AI},\qquad
P_{rt}^{fac}=\mathrm{PUE}_rP_{rt}^{IT}, \tag{7}
$$

$$
P_{rt}^{IT}\le P_r^{IT,max},\qquad
P_{rt}^{fac}\le P_r^{fac,max}. \tag{8}
$$

第 $2406$ 小时禁止任务占用：

$$
\omega_{i,2406}(s)x_{irs}=0. \tag{9}
$$

## 子问题 1：GPU 需求预测与最后 24 小时基础调度

### 模型思路

采用滞后特征正则化回归预测区域—任务类型逐小时需求，再以实际到达任务求解第 $2376$–$2399$ 小时基础调度。预测只用于精度评价，不进入正式调度。

### 模型建立

定义到达 GPU 与 GPU-hour：

$$
D_{rkt}=\sum_{i:o_i=r,k_i=k,a_i=t}g_i, \tag{10}
$$

$$
H_{rkt}=\sum_{i:o_i=r,k_i=k,a_i=t}g_id_i. \tag{11}
$$

季节性基线为

$$
\widehat D_{rkt}^{(24)}=D_{rk,t-24},\qquad
\widehat D_{rkt}^{(168)}=D_{rk,t-168}. \tag{12}
$$

增强模型的特征向量为

$$
\boldsymbol\phi_{rkt}=
\left[
D_{rk,t-1},D_{rk,t-24},D_{rk,t-168},
\overline D_{rk,t}^{(24)},\overline D_{rk,t}^{(168)},
\sin\frac{2\pi t}{24},\cos\frac{2\pi t}{24},
\sin\frac{2\pi t}{168},\cos\frac{2\pi t}{168}
\right]^\top. \tag{13}
$$

先拟合可直接求解的岭回归或 Huber 回归：

$$
\min_{\beta_{0,rk},\boldsymbol\beta_{rk}}
\sum_{t\in\mathcal T_{train}}
\rho\!\left(
D_{rkt}-\beta_{0,rk}
-\boldsymbol\beta_{rk}^{\top}\boldsymbol\phi_{rkt}
\right)
+\lambda\|\boldsymbol\beta_{rk}\|_2^2, \tag{14}
$$

再对模型输出作非负截断：

$$
\widehat D_{rkt}=
\max\left\{0,
\beta_{0,rk}+\boldsymbol\beta_{rk}^{\top}\boldsymbol\phi_{rkt}
\right\}. \tag{15}
$$

评价指标为

$$
\mathrm{MAE}=\frac1n\sum_t|D_t-\widehat D_t|,\qquad
\mathrm{RMSE}=\sqrt{\frac1n\sum_t(D_t-\widehat D_t)^2}, \tag{16}
$$

$$
\mathrm{WAPE}=
\frac{\sum_t|D_t-\widehat D_t|}{\sum_tD_t},
\qquad \sum_tD_t>0. \tag{17}
$$

当 $\sum_tD_t=0$ 时，该组 WAPE 输出“验证不可用”，改报 MAE 和总体 WAPE，不输出 `NaN` 或 `Inf`。

数据划分保持为训练 $0$–$2351$、验证 $2352$–$2375$、重训 $0$–$2375$、最终测试 $2376$–$2399$。

基础调度目标为

$$
\min
\sum_i\sum_{r,s}
x_{irs}
\left[
\alpha_{k_i}(s-a_i)+\beta_{k_i}\ell_{o_i r}
\right], \tag{18}
$$

并满足式（1）–（9）。$\alpha_k,\beta_k$ 在代码阶段按候选集中等待时间和时延的固定量程归一化后预声明，不用测试结果反向调整。

GPU 利用率为

$$
U_{rt}^{GPU}=
\frac{G_{rt}}{G_r^{max}\Delta t}\times100\%. \tag{19}
$$

### 求解方法

先用“实时优先—最早截止时间优先—短任务优先”生成可行热启动，再求解 MILP。增强预测只有在验证集达到预声明选择规则后才进入最终重训；否则使用季节性基线。MILP 未返回可行解时，只能报告满足全部硬约束的启发式结果，或输出结构化不可行状态。

### 必须回答的输出

1. 区域—任务类型任务数、GPU 总量、GPU-hour、分位数、持续时间、周期、自相关和区域相关性。
2. 验证集和测试集总体及分组 MAE、RMSE、WAPE。
3. 第 $2376$–$2399$ 小时实际任务的执行区域、开工和完成时刻。
4. 第 $2400$–$2405$ 小时末端任务及结清时刻。
5. 任务级甘特图和各区域逐小时 GPU 利用率。
6. 文件：`q1_forecast_metrics.csv`、`q1_schedule.csv`、`q1_gpu_utilization.csv`、`q1_gantt.png`。
7. 结果等级：最优解、限时可行解或启发式可行解。

## 子问题 2：碳感知任务调度

### 模型思路

使用实际任务和实际逐时电力参数，通过滚动时域 ε-约束 MILP 联合决定执行区域与开工时间。问题二不配置储能决策。

### 模型建立

任务约束沿用式（1）–（9）。无储能负荷平衡为

$$
B_{rt}+R_{rt}^{use}=P_{rt}^{fac}. \tag{20}
$$

新能源守恒为

$$
R_{rt}^{use}+S_{rt}+K_{rt}=R_{rt}^{av}. \tag{21}
$$

边界为

$$
0\le B_{rt}\le P_{rt}^{grid,max}, \tag{22}
$$

$$
0\le S_{rt}\le
\min(P_{rt}^{export,max},S_r^{max}),
\qquad R_{rt}^{use},K_{rt}\ge0. \tag{23}
$$

成本和碳排放为

$$
C_{op}=\sum_{r,t}
(\pi_{rt}^{buy}B_{rt}-\pi_{rt}^{sell}S_{rt})\Delta t, \tag{24}
$$

$$
E_{CO2}=\sum_{r,t}c_{rt}B_{rt}\Delta t. \tag{25}
$$

当 $\sum_i g_id_i>0$ 时，平均时延为

$$
L_{net}=
\frac{\sum_i\sum_{r,s}g_id_i\ell_{o_i r}x_{irs}}
{\sum_i g_id_i}. \tag{26}
$$

若任务集合为空或分母为零，$L_{net}$ 输出“不可计算”，不进入 ε 约束或 Pareto 排序。

当 $\sum_{r,t}R_{rt}^{av}\Delta t>0$ 时，

$$
U_{RE}=
\frac{\sum_{r,t}(R_{rt}^{use}+S_{rt})\Delta t}
{\sum_{r,t}R_{rt}^{av}\Delta t}. \tag{27}
$$

若分母为零，输出“不可计算”，不进入新能源维度排序。

采用

$$
\min C_{op} \tag{28}
$$

并约束

$$
E_{CO2}\le\varepsilon_C,\qquad
L_{net}\le\varepsilon_L,\qquad
U_{RE}\ge\varepsilon_U, \tag{29}
$$

其中仅对指标可计算的场景施加对应约束。

### 求解方法

预删违反时延、到达、截止及系统终点的候选。滚动窗口固定为 $H=168$ h，相邻窗口重叠 $O=24$ h；若缩小实例对照失败，只允许扩大一次至 $H_{max}=336$ h，不作无上限扩窗。窗口间传递已开工任务的固定区域和后续占用、未开工任务的剩余候选集合。

每个多目标子问题最多处理 $N_\varepsilon^{max}=12$ 个 ε 组合，单个候选最多 $30$ s，并服从第 6 节共享墙钟合同。候选未完成或全时域复核失败时丢弃，不使用部分结果。

### 必须回答的输出

1. 每个任务的来源区域、执行区域、开工、完成、等待和网络时延。
2. 系统及分区域成本、碳排放、平均及高分位时延、新能源利用率。
3. 相对基础调度的绝对变化和相对变化率。
4. 三类任务迁移数量、方向和等待分布。
5. Pareto 方案表和非支配前沿图。
6. 第 $2400$–$2405$ 小时末端任务及能源结算。
7. 文件：`q2_schedule.csv`、`q2_energy_flow.csv`、`q2_metrics.csv`、`q2_pareto.csv`、`q2_pareto.png`。

## 子问题 3：固定负荷下储能协同优化

### 模型思路

不重新优化任务，设施负荷固定为

$$
P_{rt}^{fac}=
\mathrm{PUE}_r(P_{rt}^{BAI}+P_{rt}^{NA}). \tag{30}
$$

采用新能源、电网和储能分源模型，明确外送只能来自本地新能源。

### 模型建立

总充电功率为

$$
C_{rt}=C_{rt}^{RE}+C_{rt}^{G}. \tag{31}
$$

负荷侧平衡修正为

$$
B_{rt}+R_{rt}^{use}+D_{rt}
=P_{rt}^{fac}+C_{rt}^{G}. \tag{32}
$$

新能源去向守恒为

$$
R_{rt}^{use}+C_{rt}^{RE}+S_{rt}+K_{rt}
=R_{rt}^{av}. \tag{33}
$$

式（32）不再把新能源充电、外送和弃电重复放入负荷侧；式（33）把可用新能源唯一分配给直供、充电、外送和弃电。由于 $S_{rt}$ 只出现在式（33），售电严格受本地新能源来源限制，不能把电网购电转售。

全部边界显式写为

$$
0\le B_{rt}\le P_{rt}^{grid,max}, \tag{34}
$$

$$
0\le S_{rt}\le
\min(P_{rt}^{export,max},S_r^{max}), \tag{35}
$$

$$
R_{rt}^{use},C_{rt}^{RE},C_{rt}^{G},
D_{rt},K_{rt}\ge0. \tag{36}
$$

本模型允许“购电供负荷、同时外送本地新能源”，因为两种能量来源已由式（32）–（33）分开，不需要设置未决的购售互斥分支。

SOC 递推为

$$
E_{r,-1}=E_r^0, \tag{37}
$$

$$
E_{rt}=E_{r,t-1}
+\eta_r^cC_{rt}\Delta t
-\frac{D_{rt}\Delta t}{\eta_r^d}, \tag{38}
$$

$$
E_r^{min}\le E_{rt}\le E_r^{max},
\qquad E_{r,2406}\ge E_r^0. \tag{39}
$$

禁止同时充放电：

$$
0\le C_{rt}\le C_r^{max}u_{rt}^{c}, \tag{40}
$$

$$
0\le D_{rt}\le D_r^{max}(1-u_{rt}^{c}),
\qquad u_{rt}^{c}\in\{0,1\}. \tag{41}
$$

净购电和正向峰值为

$$
N_{rt}=B_{rt}-S_{rt}, \tag{42}
$$

$$
P_r^{peak}\ge N_{rt},\qquad
P_r^{peak}\ge0. \tag{43}
$$

因此，即使区域全时段净外送，峰值净购电也只能为 $0$，不会产生负的工程峰值。

波动量线性化为

$$
z_{rt}\ge N_{rt}-N_{r,t-1},\qquad
z_{rt}\ge N_{r,t-1}-N_{rt},\qquad z_{rt}\ge0, \tag{44}
$$

$$
V=\sum_r\sum_{t=1}^{2406}z_{rt}. \tag{45}
$$

成本和碳排放沿用式（24）–（25）。以成本为主目标时：

$$
\min C_{op}, \tag{46}
$$

$$
E_{CO2}\le\varepsilon_C,\qquad
P_r^{peak}\le\varepsilon_{P,r},\qquad
V\le\varepsilon_V. \tag{47}
$$

等效循环量为

$$
N_r^{cycle}=
\frac{\sum_t(C_{rt}+D_{rt})\Delta t}
{2(E_r^{max}-E_r^{min})},
\qquad E_r^{max}>E_r^{min}. \tag{48}
$$

若 $E_r^{max}\le E_r^{min}$，该区域储能参数非法，输出 `invalid_storage_bounds` 并停止该区域优化，不用任意常数替代分母。

### 求解方法

求无储能基准、成本最小、碳排放最小、峰值最小和波动最小方案，再形成有限 ε 组合。无储能基准令 $C_{rt}^{RE}=C_{rt}^{G}=D_{rt}=0$，并由式（32）–（39）检查其可行性。

每个 ε 组合启动前检查共享截止；超过截止不再启动。已启动候选若不能在总截止前完成，则中断并丢弃，不使用部分解。

### 必须回答的输出

1. 各区域逐小时新能源直供、新能源充电、电网充电、放电、购电、外送、弃电和净购电。
2. 绝对 SOC 轨迹及 $SOC(2406)$。
3. 优化前后成本、碳排放、正向峰值净购电、绝对爬坡量及变化率。
4. 同时充放电小时数、同时购售电小时数及分源口径说明。
5. 各区域等效循环量。
6. 文件：`q3_storage_schedule.csv`、`q3_soc.csv`、`q3_energy_flow.csv`、`q3_comparison.csv`、`q3_storage_plot.png`。

## 子问题 4：多区域算—储—电联合多目标优化

### 模型思路

联合决定任务区域与开工时刻、储能充放电、新能源分配及购售电。问题四使用实际任务和实际逐时电力参数重新求解，不能直接拼接问题二、三的解。

### 模型建立

任务负荷由式（1）–（9）确定。能源侧采用与问题三一致的分源结构：

$$
B_{rt}+R_{rt}^{use}+D_{rt}
=P_{rt}^{fac}+C_{rt}^{G}, \tag{49}
$$

$$
R_{rt}^{use}+C_{rt}^{RE}+S_{rt}+K_{rt}
=R_{rt}^{av}, \tag{50}
$$

$$
C_{rt}=C_{rt}^{RE}+C_{rt}^{G}. \tag{51}
$$

并显式施加

$$
0\le B_{rt}\le P_{rt}^{grid,max}, \tag{52}
$$

$$
0\le S_{rt}\le
\min(P_{rt}^{export,max},S_r^{max}), \tag{53}
$$

$$
R_{rt}^{use},C_{rt}^{RE},C_{rt}^{G},
D_{rt},K_{rt}\ge0. \tag{54}
$$

储能满足式（37）–（41），峰值满足式（42）–（43）。式（50）同时构成售电来源约束，确保 $S_{rt}$ 只能来自 $R_{rt}^{av}$。

对弹性任务定义

$$
s_i=\sum_{r}\sum_{s\in\mathcal S_{ir}}sx_{irs}. \tag{55}
$$

全部弹性任务最大可等待时间之和为

$$
M_W=
\sum_{i\in\mathcal I^{flex}}
\left[
\min(f_i^{late},2406)-d_i-a_i
\right]. \tag{56}
$$

当 $M_W>0$ 时，服务质量代理为

$$
Q_{service}
=
1-
\frac{
\sum_{i\in\mathcal I^{flex}}(s_i-a_i)
}{
M_W
}. \tag{57}
$$

式（56）明确包含 $-d_i$，表示任务最迟开工时刻与到达时刻之差。由候选集合约束可知 $0\le Q_{service}\le1$。

当 $M_W=0$ 时，不用 $\delta$ 或任意小常数替代业务分母；$Q_{service}$ 输出“不可计算”并排除服务质量维度排序，改报实时即时开工率、SLA 满足率和按期完成率。

新能源利用率为

$$
U_{RE}=
\frac{
\sum_{r,t}
(R_{rt}^{use}+C_{rt}^{RE}+S_{rt})\Delta t
}{
\sum_{r,t}R_{rt}^{av}\Delta t
},
\quad
\sum_{r,t}R_{rt}^{av}\Delta t>0. \tag{58}
$$

分母为零时输出“不可计算”，不进入该维度 ε 约束和排序。

多目标模型为

$$
\min C_{op}, \tag{59}
$$

$$
E_{CO2}\le\varepsilon_C,\quad
L_{net}\le\varepsilon_L,\quad
U_{RE}\ge\varepsilon_U,\quad
Q_{service}\ge\varepsilon_Q,\quad
P_r^{peak}\le\varepsilon_{P,r}. \tag{60}
$$

式（60）中不可计算的指标不被替换为常数，而是从该场景的约束与 Pareto 排序维度中移除，并保留结构化状态。

取得非支配集 $\mathcal P$ 后，对需要最小化且候选集中有正量程的指标 $J_m$，定义

$$
\widetilde J_m(y)=
\frac{J_m(y)-J_m^{ideal}}
{J_m^{nadir}-J_m^{ideal}}, \tag{61}
$$

其中 $J_m^{ideal}=\min_{y\in\mathcal P}J_m(y)$，$J_m^{nadir}=\max_{y\in\mathcal P}J_m(y)$。分母为零的指标没有区分力，从折中距离中删除。折中方案为

$$
y^*=
\arg\min_{y\in\mathcal P}
\sqrt{\sum_{m\in\mathcal M_{valid}}w_m\widetilde J_m(y)^2}, \tag{62}
$$

其中 $w_m\ge0$、$\sum_{m\in\mathcal M_{valid}}w_m=1$；权重在代码阶段预声明，不能查看结果后调整。

### 情景模型

碳约束情景：

$$
E_{CO2}\le(1-\rho_C)E_{CO2}^{base}, \tag{63}
$$

其中 $E_{CO2}^{base}$ 是同一任务集、同一设备边界下无额外碳预算方案按式（25）复算的排放；$\rho_C$ 使用预声明有限网格。

电价情景：

$$
\pi_{rt}^{buy,\xi}
=
\bar\pi_r+
\kappa_\xi(\pi_{rt}^{buy}-\bar\pi_r), \tag{64}
$$

其中 $\bar\pi_r$ 为区域全结算时域购电价算术平均值，$\kappa_\xi>0$ 为预声明情景倍率。

新能源情景：

$$
R_{rt}^{av,\xi}=
\max\{0,\mu_\xi R_{rt}^{av}+\sigma_\xi\zeta_{rt}^{\xi}\}. \tag{65}
$$

$\mu_\xi$ 为出力比例，$\sigma_\xi$ 为波动幅度，$\zeta_{rt}^{\xi}$ 是按固定种子生成并在每个区域内去均值的有限扰动序列。除研究因素外，任务、容量、时延、PUE、功率映射和设备边界保持不变。

### 求解方法

采用与问题二相同的 $H=168$ h、$O=24$ h 滚动窗口；仅允许一次扩大到 $H_{max}=336$ h。窗口间传递已运行任务后续占用、未开始任务剩余候选、绝对 SOC、临近截止任务以及收尾时域状态。

正式结果区分“已证明最优”“限时可行”“启发式可行”和“结构化不可行”。未完成候选、状态不连续候选或全时域复核失败候选不得进入 Pareto 集。

### 必须回答的输出

1. 每个 Pareto 方案的成本、碳排放、网络时延、服务质量代理、新能源利用率和各区域正向峰值净购电。
2. 推荐方案的完整任务调度、逐时能源流、储能动作和绝对 SOC。
3. 各任务类型迁移数量、方向、等待和时延分布。
4. 各区域新能源直供、充电、外送和弃电累计量。
5. 不同碳预算、电价及新能源情景的策略与指标变化。
6. 每个场景的可行性、最优间隙和结果等级。
7. 文件：`q4_schedule.csv`、`q4_energy_flow.csv`、`q4_soc.csv`、`q4_pareto.csv`、`q4_scenario_comparison.csv`、`q4_pareto.png`。

## 6. 共享墙钟预算与有界停止规则

Coder 单次执行共享

$$
B_{total}=300\ \mathrm s,\qquad
T_{tail}=15\ \mathrm s. \tag{66}
$$

以 `time.monotonic()` 记录 $t_{start}$，统一搜索截止为

$$
D_{search}=t_{start}+B_{total}-T_{tail}
=t_{start}+285\ \mathrm s. \tag{67}
$$

问题一的数据读取、预测拟合、最后 24 小时调度，问题二固定基准及必要扫描，问题三、四候选搜索、统一复核与文件输出共用该预算，不得分别获得 $300$ s。

执行规则如下：

1. 固定必答工作、每个 MILP 候选、ε 组合和文件生成开始前均检查同一绝对截止。
2. 搜索候选只可在当前时刻小于 $D_{search}$ 且其 $30$ s 上限可放入总剩余时间时启动。
3. 已启动候选可越过 $D_{search}$，但不得越过 $t_{start}+300$ s；否则中断并丢弃，不使用部分结果。
4. 问题二、三、四每问最多 $12$ 个 ε 组合；滚动窗口最多由 $168$ h 扩大一次到 $336$ h。
5. 到达搜索截止后停止新增方案，使用已完成且通过全时域复核的方案；若无此类方案，输出 `time_limit_no_feasible_solution`。
6. 最后 $15$ s 专用于约束复核、状态写入和必答文件输出。固定必答工作若真实超时，记录实际耗时并输出失败状态，不缩减任务后伪装完成。

## 7. 统一结果验证

代码阶段必须检查：

1. 每个任务恰好执行一次。
2. 实时任务开工等于到达时刻。
3. 单向时延不超过任务上限。
4. 任务不早于到达时刻开工。
5. 完成时点不晚于任务截止和 $2406$。
6. 任务不占用第 $2406$ 小时。
7. 式（5）、（8）的 GPU-hour、IT 平均功率和设施平均功率约束。
8. 问题三、四分别按式（32）–（36）和（49）–（54）复核分源能量守恒、购售电边界及售电来源。
9. SOC 从 `InitialSOC_MWh` 绝对递推，并满足上下限和终端约束。
10. 正向峰值满足式（43），不得输出负峰值。
11. 成本、碳排放和新能源利用率由优化流量重新计算。
12. 所有分母先检查正性；不满足时输出“不可计算”或“验证不可用”，不输出 `NaN`、`Inf`，也不以任意 $\epsilon$ 替代。
13. 情景比较使用相同任务集、时域、功率映射、PUE 和评价公式。
14. 只有在真实附件上通过硬约束和数值残差门禁的候选才能进入最终优化结果；若候选结构或滚动拼接失败，停止于相应子问题并输出结构化状态。

## Verifier 修复核对表

| Block issue | 修复位置 | 可计算性与物理保证 |
|---|---|---|
| 问题三、四新能源重复计量 | 问题三式（32）–（33）；问题四式（49）–（51） | 负荷侧只含新能源直供和电网充电负荷；可用新能源仅在直供、充电、外送、弃电间分配一次，消除重复计量 |
| 问题四服务质量公式遗漏持续时间 | 式（56）–（57）及 `equations.json` 的 $M_W$ 定义 | 分母包含 $-d_i$，严格表示最大可等待时间；$M_W=0$ 时输出不可计算并改报三项硬服务指标 |
| 峰值净购电可能为负 | 式（42）–（43）及问题四继承约束 | 同时施加 $P_r^{peak}\ge N_{rt}$ 与 $P_r^{peak}\ge0$，使指标等于正向净购电峰值 |
| 问题三、四购电、外送及售电来源约束不完整 | 问题三式（34）–（36）；问题四式（52）–（54） | 显式限制购电和外送上界及全部流量非负；$S_{rt}$ 只由新能源守恒分配，禁止电网转售套利 |
| GPU-hour 与 GPU 容量量纲不一致 | 共享模型式（4）–（6） | 容量改为 $G_{rt}\le G_r^{max}\Delta t$；AI IT 功率除以 $\Delta t$，明确为小时平均功率 |
| 滚动 ε 网格缺少固定预算和停止规则 | 第 6 节式（66）–（67） | 固定 $300$ s 总预算、$285$ s 搜索截止、窗口和 ε 组合上限；超时候选丢弃并输出有限结构化状态，不无限扩窗 |