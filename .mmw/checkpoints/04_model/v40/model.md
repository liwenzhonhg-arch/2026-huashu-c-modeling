# 数学模型

## 1. 符号说明

| 符号 | 含义 | 类型及来源 | 取值范围/单位 |
|---|---|---|---|
| \(i,r,t,s,k\) | 任务、区域、小时、整数开工时刻、任务类型索引 | 索引 | \(r\in\mathcal R,\ t=0,\ldots,2406\) |
| \(\mathcal R\) | 六区域集合 | 题面直接给定 | RegionA–RegionF |
| \(\mathcal K\) | 三类任务集合 | 题面直接给定 | 无 |
| \(\mathcal T_A\) | 任务到达主时域 | 题面直接给定 | \(\{0,\ldots,2399\}\) |
| \(\mathcal T_C\) | 末端结清时域 | 题面直接给定 | \(\{2400,\ldots,2405\}\) |
| \(\mathcal T_E\) | 电力与储能结算时域 | 题面直接给定 | \(\{0,\ldots,2406\}\) |
| \(\mathcal S\) | 合法整数开工时刻 | 小时粒度推导 | \(\{0,\ldots,2405\}\) |
| \(\Delta t\) | 时段长度 | 题面直接给定 | \(1\) h |
| \(a_i,d_i,h_i\) | 到达小时、持续分钟、持续小时 | 工作负载附件；\(h_i=d_i/60\) | h、min、h |
| \(g_i,k_i,o_i\) | GPU需求、类型、来源区域 | `workload_trace.xlsx` | GPU、无、无 |
| \(F_i,W_i^{\max}\) | 有效截止、最大允许等待 | 附件及派生 | h |
| \(\ell_i^{\max},\ell_{or}\) | 最大允许时延、区域单向时延 | 工作负载、网络附件 | ms |
| \(\omega_{it}(s)\) | 任务与小时的实际重叠时长 | 派生 | h |
| \(\chi_{it}(s)\) | 任务在小时内是否有瞬时占用 | 派生 | \(\{0,1\}\) |
| \(\Omega_i\) | 任务完整合法区域—开工候选域 | 派生 | 有限集合 |
| \(x_{irs}\) | 任务是否在区域 \(r\) 于 \(s\) 开工 | 构造决策 | \(\{0,1\}\) |
| \(s_i,c_i,r_i\) | 实际开工、完成、执行区域 | 派生 | h、h、区域 |
| \(G_r^{\max}\) | 可调度GPU容量 | `GPU_information.xlsx` | 等效GPU |
| \(P_r^{IT,\max},P_r^{F,\max}\) | 最大IT、设施瞬时功率 | GPU附件 | MW |
| \(p_k^{GPU},\pi_r\) | 单位GPU功率、PUE | 功率映射、GPU附件 | MW/GPU、无量纲 |
| \(L_{rt}^{N}\) | NonAI固定IT负荷 | `region_time_data.xlsx` | MW |
| \(L_{rt}^{BAI}\) | 问题三Baseline AI IT负荷 | 同上 | MW |
| \(L_{rt}^{AI,cap}\) | AI瞬时IT功率 | 派生 | MW |
| \(E_{rt}^{AI}\) | AI小时电量 | 派生 | MWh |
| \(L_{rt}^{F,avg}\) | 小时平均设施负荷 | 派生 | MW |
| \(R_{rt}^{av},R_{rt}^{use}\) | 可用、直接使用新能源 | 输入或动作 | MW |
| \(R_{rt}^{ch},R_{rt}^{sell},R_{rt}^{curt}\) | 新能源充电、外送、弃电 | 动作 | MW |
| \(G_{rt}^{load},G_{rt}^{ch}\) | 电网供负荷、给储能充电 | 动作 | MW |
| \(G_{rt}^{buy},G_{rt}^{sell}\) | 电网购电、区域外送 | 动作 | MW |
| \(C_{rt},D_{rt},S_{rt}\) | 总充电、放电、时段末SOC | 动作或状态 | MW、MW、MWh |
| \(B_r,S_r^0,S_r^{min},S_r^{max}\) | 储能容量、初值和边界 | 储能附件 | MWh |
| \(\eta_r^c,\eta_r^d\) | 充放电效率 | 储能附件 | 无量纲 |
| \(C_r^{\max},D_r^{\max}\) | 最大充放电功率 | 储能附件 | MW |
| \(I_r^{\max}\) | 区域购电上限 | 区域附件 | MW |
| \(X_r^{grid}\) | `MaxGridExport_MW` | 区域附件 | MW |
| \(X_r^{storage}\) | `SellLimit_MW` | 储能附件，仅问题三、四 | MW |
| \(c_{rt}^{buy},c_{rt}^{sell}\) | 购、售电价格 | 区域附件 | 元/MWh |
| \(\kappa_{rt}\) | 购电碳强度 | 区域附件 | tCO2/MWh |
| \(N_{rt}\) | 净购电功率 | 派生 | MW |
| \(P_r^{peak},V_r\) | 非负峰值购电、绝对爬坡量 | 派生 | MW |
| \(D_{rkt}\) | 区域—类型—小时GPU到达需求 | 工作负载聚合 | GPU |
| \(u_{rkt}\) | Huber模型未截断线性输出 | 待拟合 | GPU |
| \(z_t\) | 固定四维周期特征 | 确定性计算 | 无量纲 |
| \(\sigma_{rk}\) | 响应标准化尺度 | 训练集计算 | GPU |
| \(C_{\mathrm{op}},E_{\mathrm{CO2}}\) | 成本、购电碳排放 | 复算指标 | 元、tCO2 |
| \(L_{\mathrm{net}},U_{\mathrm{RE}}\) | GPU-hour加权时延、新能源利用率 | 有条件指标 | ms、无量纲 |
| \(Q_j\) | 服务质量分量 | 有条件指标 | 无量纲 |
| \(a_{jm}\) | 候选 \(m\) 的第 \(j\) 个正式指标 | 完整轨迹复算 | 随指标 |
| \(d_j\) | 候选差值的有限正中位绝对尺度 | 候选集计算 | 随指标 |
| \(\Psi_m\) | 仅用于候选排序的代理评分 | 派生 | 无量纲 |
| \(N_{\mathrm{back}},N_{\mathrm{move}}^q\) | 回溯节点、局部候选评价上限 | 固定合同 | 次 |
| \(B_{\mathrm{total}},T_{\mathrm{tail}}\) | 总预算、输出终检预留 | 固定合同 | 300 s、15 s |
| \(D_{\mathrm{search}},D_{\mathrm{total}}\) | 搜索截止、总截止 | 单调时钟 | \(t_0+285,t_0+300\) |
| \(\tau_{\mathrm{num}}\) | 归一化审计容差 | 固定 | \(10^{-6}\) |

附件参数、预测系数、误差、任务方案和能源方案均由代码阶段从真实附件计算；本阶段不预填结果。

## 2. 统一任务与物理边界

有效截止定义为

$$
h_i=\frac{d_i}{60},\qquad
F_i=\min\{f_i^{valid},2406\},\qquad
W_i^{\max}=F_i-a_i-h_i.
\tag{1}
$$

`LatestFinishHour` 合法时采用其值；仅当数据字典明确该字段不适用或允许空缺时取2406。其他非法值结构化停止。

任务与小时区间 \([t,t+1)\) 的重叠量为

$$
\omega_{it}(s)=
\max\{0,\min(t+1,s+h_i)-\max(t,s)\},
\tag{2}
$$

$$
\chi_{it}(s)=\mathbf 1\{\omega_{it}(s)>0\}.
\tag{3}
$$

完整整数候选域为

$$
\Omega_i=
\left\{(r,s):
\begin{array}{l}
r\in\mathcal R,\ s\in\mathcal S,\ s\ge a_i,\\
s+h_i\le F_i,\ \ell_{o_ir}\le\ell_i^{\max},\\
\omega_{i,2406}(s)=0
\end{array}
\right\}.
\tag{4}
$$

若 \(\Omega_i=\varnothing\)，输出任务ID及逐项排除原因并结构化停止。唯一执行及实时要求为

$$
\sum_{(r,s)\in\Omega_i}x_{irs}=1,\qquad
s_i=\sum_{r,s}sx_{irs},\qquad c_i=s_i+h_i,
\tag{5}
$$

$$
s_i=a_i,\qquad i\in\mathcal I_{\mathrm{RT}}.
\tag{6}
$$

必须保留瞬时容量口径：

$$
\sum_{i,s}g_i\chi_{it}(s)x_{irs}\le G_r^{\max},
\tag{7}
$$

$$
L_{rt}^{AI,cap}=
\sum_{i,s}g_ip_{k_i}^{GPU}\chi_{it}(s)x_{irs},
\tag{8}
$$

$$
L_{rt}^{N}+L_{rt}^{AI,cap}\le P_r^{IT,\max},
\qquad
\pi_r(L_{rt}^{N}+L_{rt}^{AI,cap})\le P_r^{F,\max}.
\tag{9}
$$

小时能源结算必须使用实际重叠量：

$$
E_{rt}^{AI}=
\sum_{i,s}g_ip_{k_i}^{GPU}\omega_{it}(s)x_{irs},
\tag{10}
$$

$$
L_{rt}^{AI,avg}=\frac{E_{rt}^{AI}}{\Delta t},
\qquad
L_{rt}^{F,avg}=\pi_r(L_{rt}^{N}+L_{rt}^{AI,avg}).
\tag{11}
$$

## 3. 有限指标与评分规则

成本和碳排放统一复算为

$$
C_{\mathrm{op}}=
\sum_{r,t}
(c_{rt}^{buy}G_{rt}^{buy}
-c_{rt}^{sell}G_{rt}^{sell})\Delta t,
\tag{12}
$$

$$
E_{\mathrm{CO2}}=
\sum_{r,t}\kappa_{rt}G_{rt}^{buy}\Delta t.
\tag{13}
$$

网络时延分母为

$$
W_{\mathrm{net}}=\sum_i g_ih_i.
\tag{14}
$$

只有 \(W_{\mathrm{net}}>0\) 才计算

$$
L_{\mathrm{net}}=
\frac{\sum_i g_ih_i\ell_{o_ir_i}}{W_{\mathrm{net}}}.
\tag{15}
$$

否则输出

{"status":"metric_unavailable","metric":"L_net","reason":"nonpositive_gpu_hour_denominator"}

并从评分、约束和排序中删除该维，禁止产生 `NaN` 或 `Inf`。

新能源分母为

$$
W_{\mathrm{RE}}=\sum_{r,t}R_{rt}^{av}\Delta t.
\tag{16}
$$

仅当 \(W_{\mathrm{RE}}>0\) 时计算

$$
U_{\mathrm{RE}}=
\frac{\sum_{r,t}
(R_{rt}^{use}+R_{rt}^{ch}+R_{rt}^{sell})\Delta t}
{W_{\mathrm{RE}}}.
\tag{17}
$$

否则返回结构化不可用状态并删除该评分维度。

设完整可行候选集为 \(\mathcal M\)，候选 \(m\) 的指标为 \(a_{jm}\)。以当前基准候选 \(m_0\) 为参照，收集真实差值

$$
\mathcal D_j=
\{|a_{jm}-a_{j,m_0}|:
m\in\mathcal M,\ 
a_{jm},a_{j,m_0}\text{有限},\
|a_{jm}-a_{j,m_0}|>0\}.
\tag{18}
$$

若 \(\mathcal D_j\ne\varnothing\)，定义

$$
d_j=\operatorname{median}(\mathcal D_j)>0.
\tag{19}
$$

否则该维无辨别力，退出评分。对最小化指标定义

$$
\Psi_m=\sum_{j\in J_{\mathrm{score}}}
w_j\frac{a_{jm}-a_{j,m_0}}{d_j},
\qquad
w_j=\frac1{|J_{\mathrm{score}}|}.
\tag{20}
$$

若 \(J_{\mathrm{score}}=\varnothing\)，按成本、碳排、任务ID—区域—开工时刻的固定词典序选择。该评分只排序已通过硬约束的候选，不能替代正式指标，也不构成Pareto或全局最优证明。

## 子问题 1：需求预测与基础算力调度

### 模型思路

统计区域—类型GPU和GPU-hour需求；比较24小时季节性、168小时季节性和标准线性Huber回归。Huber训练使用未截断线性输出，训练后才截为非负预测。全部实际任务直接在完整整数候选域上作确定性全时域构造，候选耗尽时对有限局部冲突集回溯。

### 模型建立

需求聚合为

$$
D_{rkt}^{GPU}
=\sum_{i:o_i=r,k_i=k,a_i=t}g_i,
\qquad
D_{rkt}^{GPUh}
=\sum_{i:o_i=r,k_i=k,a_i=t}g_ih_i.
\tag{21}
$$

季节性候选为

$$
\widehat D_{rkt}^{(24)}=D_{rk,t-24},
\qquad
\widehat D_{rkt}^{(168)}=D_{rk,t-168}.
\tag{22}
$$

周期特征固定为

$$
z_t=
\left[
\sin\frac{2\pi t}{24},
\cos\frac{2\pi t}{24},
\sin\frac{2\pi t}{168},
\cos\frac{2\pi t}{168}
\right]^\top.
\tag{23}
$$

这四列天然位于 \([-1,1]\)，不再缩放。对每个滞后连续特征，仅用选择训练集计算均值 \(\mu_\ell\) 和标准差 \(s_\ell\)：

$$
D'_{rk,t-\ell}=
\begin{cases}
(D_{rk,t-\ell}-\mu_\ell)/s_\ell,&s_\ell>0,\\
0,&s_\ell=0.
\end{cases}
\tag{24}
$$

未截断线性输出为

$$
u_{rkt}=
\beta_0+
\sum_{\ell\in\{1,2,3,24,48,168\}}
\beta_\ell D'_{rk,t-\ell}
+\gamma^\top z_t+\alpha_r+\delta_k.
\tag{25}
$$

固定基准组以消除共线性：

$$
\alpha_{\mathrm{RegionA}}=0,\qquad
\delta_{\mathrm{RealTimeInference}}=0.
\tag{26}
$$

响应尺度为

$$
\sigma_{rk}=
\max\left\{
\sqrt{\frac1{n_{rk}}
\sum_{t=168}^{2351}
(D_{rkt}-\bar D_{rk})^2},
1
\right\},
\tag{27}
$$

其中数值 \(1\) 的单位为等效GPU。Huber损失为

$$
\rho_\delta(v)=
\begin{cases}
v^2/2,&|v|\le\delta,\\
\delta(|v|-\delta/2),&|v|>\delta.
\end{cases}
\tag{28}
$$

训练目标是标准凸Huber回归：

$$
\min_{\beta,\gamma,\alpha,\delta_k}
\sum_{r,k,t=168}^{2351}
\rho_\delta\!\left(
\frac{D_{rkt}-u_{rkt}}{\sigma_{rk}}
\right)
+\lambda\|\theta\|_2^2.
\tag{29}
$$

训练完成后才作非负后处理：

$$
\widehat D_{rkt}=\max\{0,u_{rkt}\}.
\tag{30}
$$

因此非负截断不进入训练损失。参数网格为

$$
\delta\in\{0.5,1,1.5,2\},\qquad
\lambda\in\{0,10^{-4},10^{-3},10^{-2},10^{-1},1\}.
\tag{31}
$$

区间固定为：选择训练 \(168\)–\(2351\)，验证 \(2352\)–\(2375\)，选模后重训 \(168\)–\(2375\)，测试 \(2376\)–\(2399\)。

$$
MAE=\frac1n\sum_j|y_j-\widehat y_j|,
\qquad
RMSE=\sqrt{\frac1n\sum_j(y_j-\widehat y_j)^2}.
\tag{32}
$$

只有 \(\sum_j|y_j|>0\) 时计算

$$
WAPE=\frac{\sum_j|y_j-\widehat y_j|}
{\sum_j|y_j|}.
\tag{33}
$$

每个分组和总体分别执行该门禁。

### 求解方法

任务按

$$
\operatorname{key}(i)=
(\mathbf1\{i\notin\mathcal I_{\mathrm{RT}}\},
F_i,-h_i,-g_i,TaskID_i)
\tag{34}
$$

确定性排序。对每个任务，在完整 \(\Omega_i\) 中按

$$
(s-a_i,\ell_{o_ir},
U_{irs}^{post},RegionName(r),s)
\tag{35}
$$

词典序尝试，并逐项检查式(5)–(9)。

若当前任务没有可接纳候选，冲突集定义为：当前任务以及与其任一候选在区域和时间上重叠、并实际占用GPU或功率容量的已排任务。只在该有限冲突集的完整候选域上深度优先回溯，节点上限

$$
N_{\mathrm{back}}=2000.
\tag{36}
$$

按固定任务顺序和固定候选顺序展开。找到完整可行分配即替换原局部安排；达到节点上限或共同搜索截止仍无解时输出 `feasibility_unresolved`，不得声称原问题不可行。只有输入级 \(\Omega_i=\varnothing\) 可直接结构化停止。

最后24小时展示采用实际到达任务；跨越2399小时的任务继续在2400–2405结清，且不得占用2406小时。

### 可观测性

GPU和GPU-hour到达需求可观测；全局最优调度标签不可观测。调度结果仅称为通过全时域复核的 `scenario-feasible incumbent`。

### 必须回答的输出

1. 区域—任务类型GPU、GPU-hour及描述统计表。
2. 三类预测候选验证比较和选模记录。
3. 测试集总体及分组MAE、RMSE、WAPE或结构化不可用状态。
4. 全部任务构造状态、回溯节点数和停止原因。
5. 第2376–2399小时实际任务的区域、开工和完成时刻。
6. 跨越2399小时任务的2400–2405结清结果。
7. 最后24小时调度甘特图文件。
8. 区域逐时GPU利用率表和曲线。
9. 全部任务的唯一执行、截止、时延、GPU、IT、设施功率和2406禁占用审计。
10. `full_horizon_feasible`或`feasibility_unresolved`。

## 子问题 2：无储能碳感知任务调度

### 模型思路

以问题一完整可行方案为基线，通过单任务迁移和开工时刻变更作有界局部搜索。问题二不读取储能SOC或 `SellLimit_MW`；区域外送只受 `MaxGridExport_MW` 约束。

### 模型建立

问题二无储能：

$$
R_{rt}^{ch}=G_{rt}^{ch}=C_{rt}=D_{rt}=0.
\tag{37}
$$

新能源分配和负荷平衡为

$$
R_{rt}^{use}+R_{rt}^{sell}+R_{rt}^{curt}
=R_{rt}^{av},
\tag{38}
$$

$$
G_{rt}^{buy}+R_{rt}^{use}=L_{rt}^{F,avg},
\qquad
G_{rt}^{sell}=R_{rt}^{sell}.
\tag{39}
$$

问题二外送上限明确为

$$
X_r^{q2}=X_r^{grid},
\tag{40}
$$

$$
0\le G_{rt}^{buy}\le I_r^{\max}y_{rt}^{grid},
\qquad
0\le G_{rt}^{sell}\le
X_r^{grid}(1-y_{rt}^{grid}),
\quad y_{rt}^{grid}\in\{0,1\}.
\tag{41}
$$

确定性直接新能源优先规则为

$$
R_{rt}^{use}=\min\{R_{rt}^{av},L_{rt}^{F,avg}\},
\tag{42}
$$

$$
G_{rt}^{buy}=L_{rt}^{F,avg}-R_{rt}^{use}.
\tag{43}
$$

若 \(G_{rt}^{buy}>0\)，则

$$
G_{rt}^{sell}=0,\qquad
R_{rt}^{curt}=R_{rt}^{av}-R_{rt}^{use}.
\tag{44}
$$

若 \(G_{rt}^{buy}=0\)，则

$$
G_{rt}^{sell}=
\min\{X_r^{grid},R_{rt}^{av}-R_{rt}^{use}\},
\tag{45}
$$

$$
R_{rt}^{curt}=
R_{rt}^{av}-R_{rt}^{use}-G_{rt}^{sell}.
\tag{46}
$$

若式(43)超过 \(I_r^{\max}\)，该任务候选不可行。该分支覆盖新能源不足、恰好满足和富余三种状态。

指标使用式(12)–(17)。高分位时延仅在存在有限任务时按确定排序统计；空任务集返回 `metric_unavailable`。

### 求解方法

从基线出发，枚举单任务的其他 \((r,s)\in\Omega_i\)。每个候选均重新计算受影响小时的式(7)–(11)和式(38)–(46)，并完整复算所有指标。最多评价

$$
N_{\mathrm{move}}^{q2}=20000
\tag{47}
$$

个候选。只接受硬约束全部通过且式(20)改善的候选；相同评分按成本、碳排、时延、任务ID—区域—开工词典序选择。结果为有限搜索 `best-found`，明确 `non-Pareto=true`、`global_optimality_certificate=false`。

### 可观测性

能源流和正式指标可由任务方案及附件直接复算；分母不正的指标不执行除法。

### 必须回答的输出

1. 全部实际任务的执行区域、开工和完成时刻。
2. 区域逐时AI IT电量、总IT和设施负荷。
3. 逐时购电、新能源直用、外送和弃电。
4. 成本、碳排、有效时延统计和新能源利用率。
5. 相对问题一基线的绝对及相对变化；基线为0时相对变化标记不可用。
6. 已检查候选数、接受动作和有限搜索轨迹。
7. 各任务类型迁移数、GPU-hour、等待和时延。
8. 全时域任务、容量和能源审计。
9. `full_horizon_feasible`、`non-Pareto=true`、`global_optimality_certificate=false`。

## 子问题 3：固定负荷下的储能协同优化

### 模型思路

固定题面指定负荷，先构造无储能可行基线，再按小时前向生成充放电动作。每次修改立即递推SOC并检查终端SOC可达性，避免滚动窗口状态拼接。

### 模型建立

设施负荷为

$$
L_{rt}^{F,avg}=
\pi_r(L_{rt}^{BAI}+L_{rt}^{N}).
\tag{48}
$$

能源分流为

$$
R_{rt}^{use}+R_{rt}^{ch}
+R_{rt}^{sell}+R_{rt}^{curt}=R_{rt}^{av},
\tag{49}
$$

$$
G_{rt}^{load}+R_{rt}^{use}+D_{rt}
=L_{rt}^{F,avg},
\tag{50}
$$

$$
C_{rt}=R_{rt}^{ch}+G_{rt}^{ch},
\quad
G_{rt}^{buy}=G_{rt}^{load}+G_{rt}^{ch},
\quad
G_{rt}^{sell}=R_{rt}^{sell}.
\tag{51}
$$

SOC状态为

$$
S_{r,-1}=S_r^0,
\tag{52}
$$

$$
S_{rt}=S_{r,t-1}
+\eta_r^cC_{rt}\Delta t
-\frac{D_{rt}\Delta t}{\eta_r^d},
\tag{53}
$$

$$
S_r^{min}\le S_{rt}\le S_r^{max},
\qquad
S_{r,2406}\ge S_r^0.
\tag{54}
$$

功率及互斥为

$$
0\le C_{rt}\le C_r^{\max},\qquad
0\le D_{rt}\le D_r^{\max},\qquad
C_{rt}D_{rt}=0.
\tag{55}
$$

实现时用确定性分支而非乘积约束：每小时动作状态只能取 `idle`、`charge`、`discharge` 之一。

问题三、四共同外送边界为

$$
X_r^{q34}=\min\{X_r^{grid},X_r^{storage}\},
\tag{56}
$$

$$
0\le G_{rt}^{buy}\le I_r^{\max}y_{rt}^{grid},
\qquad
0\le G_{rt}^{sell}\le
X_r^{q34}(1-y_{rt}^{grid}).
\tag{57}
$$

无储能基线取

$$
C_{rt}=D_{rt}=0,\qquad S_{rt}=S_r^0,
\tag{58}
$$

其余能源按问题二的新能源优先规则计算，但外送上限替换为 \(X_r^{q34}\)。若该基线违反购电边界，则输出 `baseline_infeasible` 并停止问题三，不能用储能虚构永久供能。

每次在时刻 \(t\) 提议动作后，除检查当前SOC外，还检查终端可达性：

$$
S_{rt}
+\sum_{u=t+1}^{2406}
\eta_r^cC_r^{\max}\Delta t
\ge S_r^0.
\tag{59}
$$

这是必要的前向可达性条件；不满足则立即拒绝候选。最终仍必须用实际逐时价格、负荷、购电边界和SOC完整前推验证，式(59)不替代终端审计。

净购电、峰值和爬坡为

$$
N_{rt}=G_{rt}^{buy}-G_{rt}^{sell},
\tag{60}
$$

$$
P_r^{peak}=\max\{0,\max_{t\in\mathcal T_E}N_{rt}\},
\tag{61}
$$

$$
V_r=\sum_{t=1}^{2406}|N_{rt}-N_{r,t-1}|.
\tag{62}
$$

储能等效完整循环仅在 \(B_r>0\) 时计算：

$$
N_r^{EFC}=
\frac{\sum_t(C_{rt}+D_{rt})\Delta t}{2B_r}.
\tag{63}
$$

否则输出 `not_applicable`。

### 求解方法

按区域、小时、动作类型和固定功率候选顺序进行前向局部搜索。充放功率候选由

$$
\{0,\ 0.25P^{\max},\ 0.5P^{\max},
\ 0.75P^{\max},\ P^{\max}\}
\tag{64}
$$

与当前负荷、新能源余量、SOC边界截断后形成，重复值去重。最多评价

$$
N_{\mathrm{move}}^{q3}=12000
\tag{65}
$$

个完整候选。每个候选执行式(49)–(59)及完整末端审计，再按成本、碳排、峰值、爬坡和新能源未利用率的式(18)–(20)评分。保留最后一个完整可行incumbent。

### 可观测性

最优动作不可观测；状态和指标可复算。结论最高为 `scenario-feasible`。

### 必须回答的输出

1. 各区域0–2406小时新能源、充放电、购售电和弃电策略。
2. SOC轨迹和终端SOC。
3. 储能前后成本、碳排、非负峰值购电和绝对爬坡量。
4. 指标绝对及相对变化。
5. 各区域EFC或不适用状态。
6. SOC、充放电和净购电曲线。
7. 能源、SOC、购售、充放互斥及终端审计。
8. 新能源利用率或结构化不可用状态。
9. 基线状态、候选数、停止原因及非全局最优状态。

## 子问题 4：多区域算—储—电联合优化

### 模型思路

从问题二任务方案和问题三能源方案构造联合可行incumbent，交替尝试任务迁移、开工调整和储能动作调整。删除滚动MILP、窗口SOC拼接和 \(\varepsilon\) 路径。

### 模型建立

联合设施负荷为

$$
L_{rt}^{F,avg}=
\pi_r\left[
L_{rt}^{N}
+\frac1{\Delta t}
\sum_{i,s}g_ip_{k_i}^{GPU}
\omega_{it}(s)x_{irs}
\right].
\tag{66}
$$

任务侧必须满足式(4)–(10)，能源侧必须满足式(49)–(57)，SOC必须满足式(52)–(55)和终端条件。

服务质量分量严格先检查分母。若 \(|\mathcal I_{\mathrm{RT}}|>0\)，定义

$$
Q_{\mathrm{RT}}=
\frac{\#\{i\in\mathcal I_{\mathrm{RT}}:s_i=a_i\}}
{|\mathcal I_{\mathrm{RT}}|};
\tag{67}
$$

若 \(|\mathcal I|>0\)，定义

$$
Q_{\mathrm{SLA}}=
\frac{\#\{i:\ell_{o_ir_i}\le\ell_i^{\max}\}}{|\mathcal I|},
\qquad
Q_{\mathrm{deadline}}=
\frac{\#\{i:c_i\le F_i\}}{|\mathcal I|}.
\tag{68}
$$

令

$$
\mathcal I_{\mathrm{wait}}=
\{i:i\notin\mathcal I_{\mathrm{RT}},\ W_i^{\max}>0\},
\tag{69}
$$

$$
W_{\mathrm{wait}}=
\sum_{i\in\mathcal I_{\mathrm{wait}}}W_i^{\max}.
\tag{70}
$$

只有 \(W_{\mathrm{wait}}>0\) 才定义

$$
Q_{\mathrm{wait}}=
1-
\frac{\sum_{i\in\mathcal I_{\mathrm{wait}}}(s_i-a_i)}
{W_{\mathrm{wait}}}.
\tag{71}
$$

各分量分母不正时不执行除法，分别返回 `metric_unavailable`。由于式(6)、时延和截止硬约束使前三项在可行候选中恒为1，它们只作为合规审计；联合排序的服务维度仅使用有正分母且有候选差异的 \(1-Q_{\mathrm{wait}}\)。若没有有效服务维度，服务指标退出评分。

联合局部搜索评分采用

$$
a_m=\left(
C_{\mathrm{op}},
E_{\mathrm{CO2}},
L_{\mathrm{net}},
1-Q_{\mathrm{wait}},
1-U_{\mathrm{RE}},
P_1^{peak},\ldots,P_6^{peak}
\right)_m,
\tag{72}
$$

但只保留有定义、有限且存在正尺度的维度，再按式(18)–(20)排序。

### 情景模型

所有具体情景均从同一联合可行基线独立重构，不迁移其他情景的储能状态或任务动作。

碳目标情景为

$$
E_{\mathrm{CO2}}\le
(1-\rho_C)E_{\mathrm{CO2}}^{base},
\qquad
\rho_C\in\{0,0.1,0.2,0.3\}.
\tag{73}
$$

若有界局部搜索未找到达标候选，输出

target_infeasible_within_declared_heuristic

该状态不等于原问题数学不可行。

购电峰谷价差情景为

$$
\bar c_r=\frac1{2407}
\sum_{t=0}^{2406}c_{rt}^{buy},
\tag{74}
$$

$$
c_{rt}^{buy,sc}
=\bar c_r+\delta_P(c_{rt}^{buy}-\bar c_r),
\qquad
\delta_P\in\{0.75,1,1.25\}.
\tag{75}
$$

售电机制为

$$
c_{rt}^{sell,sc}=
\delta_Sc_{rt}^{sell},
\qquad
\delta_S\in\{0,0.5,1\}.
\tag{76}
$$

新能源水平为

$$
R_{rt}^{av,level}=
\max\{0,\delta_RR_{rt}^{av}\},
\qquad
\delta_R\in\{0.8,1,1.2\}.
\tag{77}
$$

波动增强情景使用固定种子2026。对每个区域，先将伪随机序列标准化为截断前样本均值0、样本方差1，记为 \(\xi_{rt}\)。若存在正新能源样本，

$$
\sigma_r^{sc}
=0.1\operatorname{mean}
\{R_{rt}^{av}:R_{rt}^{av}>0\};
\tag{78}
$$

否则 \(\sigma_r^{sc}=0\)。生成

$$
R_{rt}^{av,vol}=
\max\{0,R_{rt}^{av}+\sigma_r^{sc}\xi_{rt}\}.
\tag{79}
$$

式(79)是明确的非负截断情景；截断后的扰动不再声称具有零均值或指定方差。

“七情景完整输出”按七类结果组组织：

1. 基准情景；
2. 碳约束组；
3. 峰谷价差组；
4. 售电机制组；
5. 新能源水平组；
6. 新能源波动增强组；
7. 各组相对统一基准的综合比较组。

每组内必须列出题面指定的全部参数水平及其状态，不得因无改进或预算耗尽而静默删除。

### 求解方法

交替邻域包括：

1. 单任务改为 \(\Omega_i\) 中另一执行区域；
2. 单任务改为另一合法整数开工时刻；
3. 单区域单小时充电动作调整；
4. 单区域单小时放电动作调整。

每个候选都从固定入口状态 \(S_{r,-1}=S_r^0\) 完整前推至2406，重新计算式(7)–(17)、式(49)–(72)，并检查全部硬约束。最多评价

$$
N_{\mathrm{move}}^{q4}=12000
\tag{80}
$$

个完整候选。只保留完整复核通过的incumbent，不使用部分轨迹。

### 可观测性

联合全局最优标签不可观测。输出为实际检查集合中的 `best-found`，并明确：

non_Pareto=true
global_optimality_certificate=false
result_level=scenario-feasible

### 必须回答的输出

1. 折中方案逐任务区域、开工、完成、等待和时延。
2. 各区域逐时AI IT电量、设施负荷、新能源、储能、购售电和SOC。
3. 成本、碳排、有效时延、服务质量、新能源利用率和非负峰值购电。
4. 有界局部搜索候选表、接受轨迹和最终代理排序。
5. 不同碳约束下的指标、迁移、循环和状态。
6. 不同峰谷价差及售电机制下的策略变化。
7. 新能源水平和波动增强情景变化。
8. 七类情景组相对统一基准的绝对及相对变化。
9. 各任务类型迁移数、GPU-hour、等待和时延。
10. 各区域峰值、爬坡量和EFC。
11. 预算、动作、互斥、SOC可达性和停止状态审计。
12. 候选图、负荷与SOC曲线、迁移流向图和情景图。
13. `full_horizon_feasible`、`non_Pareto=true`、`global_optimality_certificate=false`。

## 4. 共享300秒执行合同

单次代码运行使用

$$
B_{\mathrm{total}}=300\ {\rm s},
\qquad
T_{\mathrm{tail}}=15\ {\rm s},
\tag{81}
$$

$$
D_{\mathrm{search}}=t_{\mathrm{start}}+285,
\qquad
D_{\mathrm{total}}=t_{\mathrm{start}}+300.
\tag{82}
$$

所有固定任务、回溯节点、局部候选和文件输出前均读取 `time.monotonic()`。搜索动作仅在

$$
t_{\mathrm{now}}<D_{\mathrm{search}}
\tag{83}
$$

时启动；循环内部再次检查。已启动但不能在 \(D_{\mathrm{total}}\) 前完成的候选中断并丢弃，不使用部分结果。

执行优先级为：

1. 输入校验、统计和预测；
2. 问题一完整任务可行构造；
3. 问题二基线与局部搜索；
4. 问题三基线与局部搜索；
5. 问题四基线、正式方案及七类情景组；
6. 文件输出和完整审计。

预算耗尽时，每项必答结果必须输出 `completed`、`timeout`、`not_run_budget_exhausted` 或 `feasibility_unresolved`，并记录实际耗时和停止位置。不得缩减时域、删减任务或把未完成结果伪装成正式方案。

## 5. 统一完整约束审计

任务审计为

$$
a_i\le s_i,\qquad
c_i\le F_i,\qquad
\ell_{o_ir_i}\le\ell_i^{\max},
\tag{84}
$$

$$
i\in\mathcal I_{\mathrm{RT}}
\Rightarrow s_i=a_i,
\qquad
\omega_{i,2406}(s_i)=0.
\tag{85}
$$

问题二能源残差为

$$
e_{rt}^{q2}=
G_{rt}^{buy}+R_{rt}^{av}
-L_{rt}^{F,avg}
-G_{rt}^{sell}-R_{rt}^{curt}.
\tag{86}
$$

问题三、四能源和SOC残差为

$$
e_{rt}^{energy}=
G_{rt}^{buy}+R_{rt}^{av}+D_{rt}
-L_{rt}^{F,avg}-C_{rt}
-G_{rt}^{sell}-R_{rt}^{curt},
\tag{87}
$$

$$
e_{rt}^{SOC}=
S_{rt}-S_{r,t-1}
-\eta_r^cC_{rt}\Delta t
+\frac{D_{rt}\Delta t}{\eta_r^d}.
\tag{88}
$$

对每类残差，尺度优先使用对应附件硬上限；缺失或不正时在搜索前固定为

$$
s_j=\max\{1,\max|\text{对应有效输入量}|\}.
\tag{89}
$$

审计条件为

$$
\frac{|e_j|}{s_j}\le10^{-6}.
\tag{90}
$$

只有唯一执行、实时开工、截止、时延、瞬时GPU、瞬时IT、瞬时设施功率、能源守恒、SOC、终端SOC、购售互斥、充放互斥、适用外送上限和2406禁占用全部通过，才能输出 `full_horizon_feasible=true`。

## 6. 局限性与停止规则

1. 结果是确定性有限搜索中的 `best-found`，不是Pareto前沿或全局最优解。
2. 问题二只使用 `MaxGridExport_MW`；问题三、四使用 \(\min(\text{MaxGridExport},\text{SellLimit})\)。
3. 网络仅使用附件单向时延，不建模带宽、迁移数据量、传输能耗、传输费用或线路潮流。
4. 预测测试集不参与选模；所有连续滞后特征的标准化参数只由选择训练集计算。
5. 任一业务分母不正时输出结构化不可用状态，不用任意小常数替代。
6. 局部回溯或搜索耗尽只说明 `feasibility_unresolved` 或未在声明启发式内找到目标，不证明数学不可行。
7. 无储能基线不可行时，问题三、四在对应基线处结构化停止，不用储能创造不可持续能量。
8. 服务质量中的实时、SLA和截止达标率作为硬约束审计；候选排序主要由有效等待指标提供区分力。
9. 新能源波动截断后的统计量按实际生成序列复算，不宣称保持截断前均值或方差。
10. 未执行的外部调研不作为参数、阈值或算法性能依据。

## 7. Verifier 修复核对表

| Block issue | 修复公式/约束位置 | 如何保证可计算和有限输出 |
|---|---|---|
| 问题二错误引用储能 `SellLimit_MW` | 式(40)–(46) | 问题二明确令 \(X_r^{q2}=X_r^{grid}\)，不读取SOC、储能容量或 `SellLimit_MW`；问题三、四才在式(56)取两个适用外送上限的最小值。 |
| 网络时延及服务质量存在零分母 | 式(14)–(17)、式(67)–(71) | 所有指标均先检查分母严格为正，再执行除法；不满足时输出 `metric_unavailable` 并退出评分、约束及排序维度，不产生 `NaN`、`Inf` 或任意替代常数。 |
| 周期特征 \(z_t\) 未定义 | 式(23)–(24) | 固定为24小时与168小时正余弦四维向量；四维周期特征不缩放，全部连续滞后特征使用训练集均值和标准差标准化，零方差列固定为0，设计矩阵可唯一复现。 |
| 滚动窗口能源时段、SOC和已提交动作传递不封闭 | 式(48)–(65)、式(66)–(80) | 删除不会在300秒内执行的滚动MILP和窗口SOC拼接；每个候选均从 \(S_{r,-1}=S_r^0\) 对0–2406全时域前向重算，并检查终端可达性及完整SOC轨迹。 |
| 非负截断位于Huber训练损失中且算法不明确 | 式(25)–(30) | 训练使用未截断线性输出 \(u_{rkt}\) 的标准凸Huber目标；仅在拟合完成后令 \(\widehat D=\max(0,u)\)，训练算法和预测后处理彻底分离。 |