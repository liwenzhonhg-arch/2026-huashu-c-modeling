# 数学模型

## 1. 模型边界与修订原则

区域集合为

$$
\mathcal R=\{\mathrm A,\mathrm B,\mathrm C,\mathrm D,\mathrm E,\mathrm F\},
$$

任务到达、执行和能源结算时域分别为

$$
\mathcal T^{arr}=\{0,\ldots,2399\},\quad
\mathcal T^{run}=\{0,\ldots,2405\},\quad
\mathcal T^{energy}=\{0,\ldots,2406\},
$$

且 $\Delta t=1\ \mathrm h$。第 $2400$–$2405$ 小时只结清弹性任务；第 $2406$ 小时不允许任务占用，只进行能源和终端 SOC 结算。

本轮只修复 Verifier 指出的容量口径错误及问题四情景输出缺失。关键修订是将：

- GPU、IT 功率和设施功率改为任务运行期间的逐小时瞬时并发约束；
- 电费、碳排放、新能源和储能能量守恒继续使用小时重叠时长；
- 旧版问题二、问题四调度全部作废，四问从重新构造的瞬时可行基准重算；
- 问题四七个情景逐项输出检查规模、迁移数、指标和约束状态。

六区域定位及有向网络时延均为题面直接给定。本题没有几何尺寸链；物理距离、线路潮流、带宽、迁移数据量、传输能耗和传输费用不建模。

## 2. 符号说明

| 符号 | 含义 | 类型及来源 | 取值范围或单位 |
|---|---|---|---|
| $i,r,t,s,k$ | 任务、区域、小时、整数开工小时、任务类型 | 索引 | 附件集合 |
| $a_i$ | 到达时刻 | `workload_trace` 可观测 | h |
| $d_i$ | 连续执行时长，$d_i=\mathrm{EstimatedDuration\_min}_i/60$ | 可观测派生量 | h |
| $g_i$ | 运行期间持续占用 GPU | `GPU_Demand` | 等效 GPU |
| $k_i,o_i$ | 类型、来源区域 | 可观测 | 类别 |
| $f_i^{late}$ | 最晚完成时点 | 可观测；题面统一边界为 $2406$ | h |
| $\ell_i^{max},\ell_{or}$ | 最大允许时延、有向网络时延 | 可观测 | ms |
| $x_{irs}$ | 任务在区域 $r$、整数小时 $s$ 开工 | 决策变量 | $\{0,1\}$ |
| $\omega_{it}(s)$ | 任务在小时 $t$ 内的重叠时长 | 派生量 | $[0,1]$ h |
| $\chi_{it}(s)$ | 任务是否触及小时 $t$ | 派生量 | $\{0,1\}$ |
| $G_r^{max}$ | 可调度 GPU 容量 | `Available_GPU` | 等效 GPU |
| $p_k^{GPU}$ | 单位 GPU 的任务 IT 功率 | `power_mapping` | MW/GPU |
| $P_{rt}^{NA},P_{rt}^{BAI}$ | 非 AI、问题三基线 AI IT 负荷 | 可观测 | MW |
| $P_r^{IT,max},P_r^{fac,max}$ | IT、设施瞬时功率上限 | 可观测 | MW |
| $\mathrm{PUE}_r$ | 区域 PUE | 可观测 | 无量纲 |
| $G_{rt}^{inst}$ | 瞬时并发 GPU | 派生量 | GPU |
| $P_{rt}^{AI,inst}$ | 瞬时 AI IT 功率 | 派生量 | MW |
| $E_{rt}^{AI}$ | 小时内 AI IT 能量 | 派生量 | MWh |
| $P_{rt}^{AI,avg}$ | AI 小时平均功率 | 派生量 | MW |
| $R_{rt}^{av},R_{rt}^{use}$ | 可用、直接消纳新能源 | 参数/变量 | MW |
| $B_{rt},S_{rt},K_{rt}$ | 购电、外送、弃电功率 | 变量 | MW |
| $C_{rt}^{RE},C_{rt}^{G},D_{rt}$ | 新能源充电、电网充电、放电 | 变量 | MW |
| $E_{rt}$ | 时段末绝对 SOC | 状态变量 | MWh |
| $E_r^0,E_r^{min},E_r^{max}$ | 初始、最小、最大 SOC | 储能附件 | MWh |
| $C_r^{max},D_r^{max}$ | 最大充、放电功率 | 储能附件 | MW |
| $\eta_r^c,\eta_r^d$ | 充、放电效率 | 储能附件 | $(0,1]$ |
| $\pi_{rt}^{buy},\pi_{rt}^{sell}$ | 购、售电价 | 可观测 | 元/MWh |
| $c_{rt}$ | 碳强度 | 可观测 | tCO2/MWh |
| $C_{op},E_{CO2}$ | 成本、碳排放 | 指标 | 元、tCO2 |
| $N_{rt}$ | 净购电 $B_{rt}-S_{rt}$ | 派生量 | MW |
| $\widehat P_r^{peak}$ | 正向峰值净购电 | 指标 | MW |
| $Q_{service}$ | 服务质量代理 | 代理指标 | 无量纲 |
| $\tau$ | 残差容差 | 固定规则 | $10^{-6}\max(1,\text{约束尺度})$ |

真实最优调度和用户满意度不可观测，不使用准确率、召回率或混淆矩阵验证。验证依据为硬约束残差、状态连续性、有限指标复算和实际检查集合内的候选比较。

## 3. 共享任务模型：瞬时容量与重叠能量分离

任务执行区间为 $[s,s+d_i)$。其与小时 $[t,t+1)$ 的重叠时长为

$$
\omega_{it}(s)=
\max\{0,\min(s+d_i,t+1)-\max(s,t)\}. \tag{1}
$$

任务是否触及整数小时 $t$ 定义为

$$
\chi_{it}(s)=
\mathbf 1\{s\le t<s+d_i\}. \tag{2}
$$

由于 $s$ 为整数，凡满足 $s\le t<s+d_i$ 的小时，即使只重叠不足一小时，任务也在该小时持续占用完整 $g_i$ 个 GPU。候选集合为

$$
\mathcal S_{ir}=
\{s\in\mathcal T^{run}:s\ge a_i,\ 
s+d_i\le\min(f_i^{late},2406),\
\ell_{o_ir}\le\ell_i^{max}\}. \tag{3}
$$

实时任务只能取 $s=a_i$。每个任务唯一执行：

$$
\sum_{r\in\mathcal R}\sum_{s\in\mathcal S_{ir}}x_{irs}=1,
\qquad x_{irs}\in\{0,1\}. \tag{4}
$$

瞬时并发 GPU 为

$$
G_{rt}^{inst}=
\sum_i\sum_{s\in\mathcal S_{ir}}
g_i\chi_{it}(s)x_{irs}, \tag{5}
$$

硬约束为

$$
G_{rt}^{inst}\le G_r^{max}. \tag{6}
$$

瞬时 AI IT 功率为

$$
P_{rt}^{AI,inst}=
\sum_i\sum_{s\in\mathcal S_{ir}}
g_ip_{k_i}^{GPU}\chi_{it}(s)x_{irs}. \tag{7}
$$

因此必须满足

$$
P_{rt}^{NA}+P_{rt}^{AI,inst}\le P_r^{IT,max}, \tag{8}
$$

$$
\mathrm{PUE}_r
(P_{rt}^{NA}+P_{rt}^{AI,inst})
\le P_r^{fac,max}. \tag{9}
$$

第 $2406$ 小时禁止占用：

$$
\chi_{i,2406}(s)x_{irs}=0. \tag{10}
$$

能源结算不把不足一小时的任务扩张为整小时。AI IT 能量和小时平均功率分别为

$$
E_{rt}^{AI}=
\sum_i\sum_{s\in\mathcal S_{ir}}
g_ip_{k_i}^{GPU}\omega_{it}(s)x_{irs}, \tag{11}
$$

$$
P_{rt}^{AI,avg}=\frac{E_{rt}^{AI}}{\Delta t}. \tag{12}
$$

问题一、二、四用于能源结算的设施平均负荷为

$$
P_{rt}^{fac,avg}
=\mathrm{PUE}_r(P_{rt}^{NA}+P_{rt}^{AI,avg}). \tag{13}
$$

式（5）–（9）负责瞬时工程容量；式（11）–（13）负责 MWh、电费、碳排放和新能源分流。两种口径不得互换。

## 子问题 1：GPU 需求预测与最后 24 小时基础调度

### 模型思路

按区域—任务类型预测逐小时到达 GPU，并用实际到达任务生成第 $2376$–$2399$ 小时调度。预测不参与替换实际任务。

### 模型建立

到达 GPU 和 GPU-hour 为

$$
D_{rkt}=\sum_{i:o_i=r,k_i=k,a_i=t}g_i,\qquad
H_{rkt}=\sum_{i:o_i=r,k_i=k,a_i=t}g_id_i. \tag{14}
$$

固定特征为

$$
\boldsymbol\phi_{rkt}=[
D_{rk,t-1},D_{rk,t-24},D_{rk,t-168},
\bar D_{rk,t}^{24},\bar D_{rk,t}^{168},
\sin(2\pi t/24),\cos(2\pi t/24),
\sin(2\pi t/168),\cos(2\pi t/168)]^\top, \tag{15}
$$

其中

$$
\bar D_{rk,t}^{h}=\frac1h\sum_{j=1}^{h}D_{rk,t-j}. \tag{16}
$$

训练样本固定为 $t=168,\ldots,2351$。验证区间 $2352$–$2375$ 只使用 $t\le2351$ 的真实数据，测试区间 $2376$–$2399$ 只使用 $t\le2375$ 的真实数据；区间内部递归使用已预测值。

增强模型为

$$
\min_{\beta_0,\boldsymbol\beta}
\sum_t\rho_{\delta_H}
(D_{rkt}-\beta_0-\boldsymbol\beta^\top\boldsymbol\phi_{rkt})
+\alpha\|\boldsymbol\beta\|_2^2, \tag{17}
$$

$$
\widehat D_{rkt}
=\max\{0,\beta_0+\boldsymbol\beta^\top\boldsymbol\phi_{rkt}\}. \tag{18}
$$

候选为 lag24、lag168 和四个固定 Huber-Ridge 组合
$(\alpha,\delta_H/\sigma)\in\{(10^{-3},1),(10^{-3},2),(10^{-1},1),(10^{-1},2)\}$，其中
$\sigma=\max\{1,1.4826\,\mathrm{MAD}\}$。按验证 WAPE、MAE、简单模型优先序选择。

$$
\mathrm{MAE}=\frac1n\sum_t|D_t-\widehat D_t|,\quad
\mathrm{RMSE}=\sqrt{\frac1n\sum_t(D_t-\widehat D_t)^2}, \tag{19}
$$

$$
\mathrm{WAPE}=
\frac{\sum_t|D_t-\widehat D_t|}{\sum_tD_t},
\qquad \sum_tD_t>0. \tag{20}
$$

分母为零时 WAPE 输出 `metric_unavailable`，保留 MAE、RMSE。相关系数或 ACF 仅在成对有限样本数不少于 $2$ 且两序列方差均为正时计算；否则分别输出 `correlation_unavailable` 或 `autocorrelation_unavailable`。周期在 $h=2,\ldots,336$ 中取满足 $\mathrm{ACF}_h>0.3$ 且高于相邻值的最大局部峰；不存在时输出 `period_unidentifiable`。

基础调度按“实时优先、最晚完成时点升序、时长升序、TaskID 升序”处理任务。每个任务按开工小时、网络时延、区域名扫描完整候选域；接受位置前必须同时检查式（4）、（6）、（8）、（9）、（10）。

区域 GPU 利用率为

$$
U_{rt}^{GPU}
=\frac{G_{rt}^{inst}}{G_r^{max}}\times100\%. \tag{21}
$$

### 求解方法

先构造完整可行 incumbent，再进行全时域逐小时残差复核。任一任务无候选输出 `infeasible_precheck`；完整扫描仍无位置输出 `infeasible_incumbent`。不得使用旧版按 GPU-hour 平均容量生成的调度。

### 必须回答的输出

1. 分区域、分类型的任务数、GPU 总量、GPU-hour、分位数、持续时间、周期、自相关和区域相关性。
2. 验证集与测试集总体及分组 MAE、RMSE、WAPE 或结构化不可用状态。
3. 第 $2376$–$2399$ 小时实际任务的执行区域、开工和完成时刻。
4. 第 $2400$–$2405$ 小时末端任务及结清时刻。
5. 甘特图、逐小时 GPU 利用率、各区域瞬时 GPU/IT/设施峰值及最大约束残差。
6. 文件：`q1_forecast_metrics.csv`、`q1_schedule.csv`、`q1_gpu_utilization.csv`、`q1_gantt.png`。
7. 结果等级固定不高于 `scenario-feasible`，`global_optimality=not_certified`。

## 子问题 2：碳感知任务调度

### 模型思路

从问题一重新构造且通过瞬时约束的完整 incumbent 出发，对最多 $10000$ 个高 GPU-hour 弹性任务进行确定性局部改进。旧版问题二存在瞬时 GPU/IT/设施分别超限 $159/99/99$ 个区域小时，结果全部失效。

### 模型建立

任务侧满足式（1）–（13）。无储能能源平衡为

$$
B_{rt}+R_{rt}^{use}=P_{rt}^{fac,avg}, \tag{22}
$$

$$
R_{rt}^{use}+S_{rt}+K_{rt}=R_{rt}^{av}. \tag{23}
$$

$$
0\le B_{rt}\le G_r^{import,max}, \tag{24}
$$

$$
0\le S_{rt}\le
\min(R_{rt}^{av},G_r^{export,max}),\quad
R_{rt}^{use},K_{rt}\ge0. \tag{25}
$$

外送只能来自式（23）的当期新能源，不允许购电转售。成本和碳排放为

$$
C_{op}=\sum_{r,t}
(\pi_{rt}^{buy}B_{rt}-\pi_{rt}^{sell}S_{rt})\Delta t, \tag{26}
$$

$$
E_{CO2}=\sum_{r,t}c_{rt}B_{rt}\Delta t. \tag{27}
$$

平均网络时延为

$$
L_{net}=
\frac{\sum_i g_id_i\ell_{o_i,r_i}}
{\sum_i g_id_i},\qquad \sum_i g_id_i>0. \tag{28}
$$

新能源利用率为

$$
U_{RE}=
\frac{\sum_{r,t}(R_{rt}^{use}+S_{rt})\Delta t}
{\sum_{r,t}R_{rt}^{av}\Delta t},\qquad
\sum_{r,t}R_{rt}^{av}\Delta t>0. \tag{29}
$$

分母不为正时输出 `metric_unavailable` 并排除排序。还须分别报告直接消纳率、外送率和弃电率。

局部候选采用已声明的无量纲量：

$$
z_C=\frac{\sum_t\Delta E_t\pi_{rt}^{buy}}
{\max(1,E\widetilde\pi)},\quad
z_E=\frac{\sum_t\Delta E_tc_{rt}}
{\max(1,E\widetilde c)}, \tag{30}
$$

$$
z_R=\frac{\sum_t\min(\Delta E_t,R_{rt}^{res})}{\max(1,E)},\quad
z_W=\frac{s-a_i}{\max(1,\lfloor f_i^{late}-d_i\rfloor-a_i)},\quad
z_L=\frac{\ell_{o_ir}}{\max(1,\ell_i^{max})}, \tag{31}
$$

其中 $\Delta E_t=\mathrm{PUE}_rg_ip_{k_i}^{GPU}\omega_{it}(s)$，$E=\sum_t\Delta E_t$，$\widetilde\pi$、$\widetilde c$ 是附件正中位数，$R_{rt}^{res}$ 是移除当前任务后扣除非 AI 和其他 AI 负荷的剩余新能源能量。评分为

$$
score_{q2}=z_C+z_E-0.5z_R+0.5z_W+0.5z_L. \tag{32}
$$

### 求解方法

每次候选移动先同时移除旧位置的 $\chi$ 瞬时占用和 $\omega$ 重叠能量，再测试新位置。只有评分严格改善且式（4）、（6）、（8）、（9）、（10）、（22）–（25）全部满足才接受，否则恢复。最终重新扫描所有任务及区域小时。

### 必须回答的输出

1. 每任务来源区、执行区、开工、完成、等待和时延。
2. 成本、碳排放、平均及高分位时延、直接消纳率、外送率、弃电率和统一新能源利用率。
3. 相对基础调度的绝对及相对变化。
4. 迁移数量、方向及等待分布。
5. 瞬时 GPU/IT/设施峰值、超限计数和最大残差；正式结果的三项超限计数必须均为 $0$。
6. 第 $2400$–$2405$ 小时任务和能源结算。
7. 文件：`q2_schedule.csv`、`q2_energy_flow.csv`、`q2_metrics.csv`、`q2_pareto.csv`、`q2_pareto.png`。兼容表须含 `ParetoCertified=false`、`Credibility=scenario-feasible`。

## 子问题 3：固定负荷下储能协同优化

### 模型思路

不重新调度任务，固定设施负荷为

$$
P_{rt}^{fac}
=\mathrm{PUE}_r(P_{rt}^{BAI}+P_{rt}^{NA}). \tag{33}
$$

### 模型建立

$$
C_{rt}=C_{rt}^{RE}+C_{rt}^{G}, \tag{34}
$$

$$
B_{rt}+R_{rt}^{use}+D_{rt}
=P_{rt}^{fac}+C_{rt}^{G}, \tag{35}
$$

$$
R_{rt}^{use}+C_{rt}^{RE}+S_{rt}+K_{rt}
=R_{rt}^{av}. \tag{36}
$$

全部能源流非负，且

$$
B_{rt}\le G_r^{import,max},\qquad
S_{rt}\le\min(G_r^{export,max},S_r^{max}). \tag{37}
$$

SOC 递推为

$$
E_{r,-1}=E_r^0, \tag{38}
$$

$$
E_{rt}=E_{r,t-1}
+\eta_r^cC_{rt}\Delta t
-\frac{D_{rt}\Delta t}{\eta_r^d}, \tag{39}
$$

$$
E_r^{min}\le E_{rt}\le E_r^{max},\qquad
E_{r,2406}\ge E_r^0. \tag{40}
$$

充放电互斥：

$$
0\le C_{rt}\le C_r^{max}u_{rt},\quad
0\le D_{rt}\le D_r^{max}(1-u_{rt}),\quad
u_{rt}\in\{0,1\}. \tag{41}
$$

净购电、正式峰值和波动为

$$
N_{rt}=B_{rt}-S_{rt}, \tag{42}
$$

$$
\widehat P_r^{peak}=
\max_t\max\{0,N_{rt}\}, \tag{43}
$$

$$
\widehat V=
\sum_r\sum_{t=1}^{2406}|N_{rt}-N_{r,t-1}|. \tag{44}
$$

等效循环量为

$$
N_r^{cycle}=
\frac{\sum_t(C_{rt}+D_{rt})\Delta t}
{2(E_r^{max}-E_r^{min})},\qquad E_r^{max}>E_r^{min}. \tag{45}
$$

否则输出 `invalid_storage_bounds`。

### 求解方法

按区域价格 $25\%/75\%$ 分位数执行新能源优先直供、新能源充电、低价电网充电、高价放电、外送和弃电。实际启发式保守保持 $E_{rt}\ge E_r^0$，第 $2406$ 小时禁止放电。逐时复核式（35）–（41），不预设成本或碳排放改善。

### 必须回答的输出

1. 各区域逐小时新能源直供、两类充电、放电、购电、外送、弃电和净购电。
2. 绝对 SOC 轨迹及 $E_{r,2406}$。
3. 成本、碳、式（43）峰值和式（44）波动的前后变化。
4. 同时充放电小时数、同时购电与新能源外送小时数及分源说明。
5. 各区域等效循环量。
6. 文件：`q3_storage_schedule.csv`、`q3_soc.csv`、`q3_energy_flow.csv`、`q3_comparison.csv`、`q3_storage_plot.png`。

## 子问题 4：算—储—电联合情景优化

### 模型思路

任务侧使用式（1）–（13）的瞬时可行模型，能源侧使用式（34）–（41）。旧版问题四存在瞬时 GPU/IT/设施分别超限 $151/96/96$ 个区域小时且最大 GPU 超限 $265$，旧结果全部作废。

### 模型建立

任务局部评分为

$$
score_{q4}=z_C+1.5z_E-z_R+z_W+0.5z_L. \tag{46}
$$

弹性任务最大等待余量为

$$
M_W=\sum_{i\in\mathcal I^{flex}}
[\min(f_i^{late},2406)-d_i-a_i]. \tag{47}
$$

当 $M_W>0$ 时，

$$
Q_{service}
=1-\frac{\sum_{i\in\mathcal I^{flex}}(s_i-a_i)}{M_W}. \tag{48}
$$

否则输出 `service_quality_unavailable`，改报实时即时开工率、SLA 满足率和按期完成率。

联合新能源利用率为

$$
U_{RE}=
\frac{\sum_{r,t}(R_{rt}^{use}+C_{rt}^{RE}+S_{rt})\Delta t}
{\sum_{r,t}R_{rt}^{av}\Delta t}, \tag{49}
$$

仅在分母为正时计算。

七情景固定为：

$$
\{\text{baseline},\text{carbon10},\text{price0.8},
\text{renewable0.8},\text{carbon20},
\text{price1.2},\text{renewable1.2}\}. \tag{50}
$$

电价情景为

$$
\pi_{rt}'=\bar\pi_r+\kappa
(\pi_{rt}^{buy}-\bar\pi_r),\qquad
\kappa\in\{0.8,1.2\}, \tag{51}
$$

新能源情景为

$$
R_{rt}^{av\prime}=\mu R_{rt}^{av},
\qquad \mu\in\{0.8,1.2\}. \tag{52}
$$

碳情景硬目标为

$$
E_{CO2}\le0.9E_{CO2}^{base}
\quad\text{或}\quad
E_{CO2}\le0.8E_{CO2}^{base}. \tag{53}
$$

对碳情景，从同一瞬时可行 incumbent 出发，对前 $2000$ 个高 GPU-hour 弹性任务依次采用

$$
(w_E,\kappa_C)\in
\{(2,200),(4,500),(8,1000),(16,2000)\}, \tag{54}
$$

并以 $\pi+\kappa_Cc$ 驱动储能排序。每级候选都必须重新计算完整碳排放。

### 求解方法

先重新构造并验证问题四基准，再处理七情景。每个情景必须在变换后的输入上重新运行任务或能源规则，而非按比例缩放结果。每个完成情景必须通过：

$$
\max\{
\text{任务唯一性残差},
\text{瞬时GPU残差},
\text{瞬时IT残差},
\text{瞬时设施残差},
\text{能源平衡残差},
\text{SOC残差},
\text{购售电边界残差}
\}\le\tau. \tag{55}
$$

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

若 carbon10 或 carbon20 未满足式（53），状态必须为 `target_infeasible_within_declared_heuristic`，不得进入候选比较、推荐排序或折中方案。零分母指标输出 `metric_unavailable`，不使用任意 $\epsilon$ 替代分母。

### 必须回答的输出

1. 七情景逐项状态、实际检查任务数、迁移数、成本、碳、时延、服务质量代理、新能源利用率、六区域峰值和约束结果。
2. 推荐候选的任务调度、逐时能源流、储能动作和绝对 SOC。
3. 各类型迁移数量、方向、等待和时延分布。
4. 各区域新能源直供、充电、外送和弃电累计量。
5. 各情景瞬时 GPU/IT/设施峰值、超限计数和最大残差；完成情景三项超限计数必须均为 $0$。
6. 同时购电与新能源外送的小时数、能量和财务影响。
7. 文件：`q4_schedule.csv`、`q4_energy_flow.csv`、`q4_soc.csv`、`q4_pareto.csv`、`q4_scenario_comparison.csv`、`q4_pareto.png`。`q4_pareto.csv` 必须含 `ParetoCertified=false`、`Credibility=scenario-feasible`。

## 4. 共享墙钟与停止规则

单次执行共享

$$
B_{total}=300\ \mathrm s,\qquad
T_{tail}=15\ \mathrm s,\qquad
D_{search}=t_{start}+285\ \mathrm s. \tag{56}
$$

使用同一 `time.monotonic()` 起点。累计阶段截止为：输入和预测 $45$ s、问题一 $70$ s、问题二 $130$ s、问题三 $160$ s、问题四 $235$ s、七情景 $270$ s、中间产物 $285$ s、最终验证和文件输出 $300$ s。固定必答阶段超时必须携带实际耗时整次失败，不得缩减检查规模后冒充完成。最后 $15$ s 只允许最终残差复核和文件输出。

## 5. 统一验证规则

1. 每个任务恰好执行一次，实时任务在到达时刻开工。
2. 每个任务满足到达、时延、截止和第 $2406$ 小时禁占用约束。
3. 对每个任务触及的整数小时，按完整 $g_i$ 检查式（6），不得乘 $\omega$。
4. 对每个任务触及的整数小时，按完整 $g_ip_{k_i}^{GPU}$ 检查式（8）–（9）。
5. 能源成本、碳排放、新能源和储能流按式（1）、（11）–（13）的重叠能量计算。
6. 每次任务移动同时更新 $\chi$ 瞬时占用和 $\omega$ 重叠能量。
7. 问题二、四不得读取或沿用旧版超限调度。
8. 能源守恒、购售电边界、外送来源、SOC 递推、充放电互斥和终端 SOC 均逐时复核。
9. 正式峰值只按式（43）从最终净购电序列复算。
10. 所有分母先检查正性；不满足时输出结构化不可用状态并排除排序。
11. 只有通过式（55）且所有正式指标有限的候选才能标记 `completed`。
12. carbon10/20 未达硬目标必须排除候选，不能以最接近目标的方案冒充可行。
13. `global_optimality=not_certified`；局部评分和候选比较不解释为完整 Pareto 前沿。

## 6. Verifier 修复核对表

| Block issue | 修复公式或位置 | 可计算性与有限输出保证 |
|---|---|---|
| `GPU_Demand×overlap` 仅约束 GPU-hour 平均量，不能表示非整小时任务的持续占用 | 式（2）、（5）、（6） | 新增触小时指示量 $\chi_{it}(s)$；凡 $s\le t<s+d_i$ 均计完整 $g_i$，直接检查瞬时并发 GPU |
| AI IT 和设施功率错误使用重叠比例，导致 q2、q4 大量区域小时超限 | 式（7）–（9） | 瞬时 AI IT 功率使用 $g_ip_k^{GPU}\chi$；叠加 NonAI 后检查 IT 上限，再乘 PUE 检查设施上限 |
| 能源成本、碳和新能源流不能因瞬时容量修订而被整小时高估 | 式（1）、（11）–（13）、（22）–（29） | 能源计算继续使用真实重叠时长 $\omega$，单位闭合为 MWh；瞬时容量与小时能量明确分离 |
| q2 旧结果存在瞬时 GPU/IT/设施超限 $159/99/99$ 个区域小时 | 子问题二求解方法与统一验证规则第 7 条 | 旧结果明确作废；从重新构造的瞬时可行 incumbent 重算，每次移动双口径更新，正式超限计数必须全为 0 |
| q4 旧结果存在瞬时 GPU/IT/设施超限 $151/96/96$ 个区域小时，最大 GPU 超限 265 | 子问题四模型与式（55） | 七情景均从新基准重算，并逐情景输出三类超限计数和最大残差；不通过者不能标记完成 |
| q4 七情景缺少逐项状态、实际检查规模、迁移数和完整指标 | 子问题四“求解方法”及“必须回答的输出” | 固定列出 `scenario_status`、`checked_task_count`、`migration_count`、成本、碳、时延、服务代理、新能源利用率、区域峰值和约束结果 |
| carbon10/20 未达标候选可能被误纳入结果 | 式（53）及子问题四停止规则 | 未达标固定输出 `target_infeasible_within_declared_heuristic`，排除候选比较、推荐排序和兼容 Pareto 表 |