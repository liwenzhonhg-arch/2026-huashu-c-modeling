# 数学模型

## 符号说明

| 符号 | 含义 | 类型及来源 | 取值范围/单位 |
|---|---|---|---|
| \(i,r,t,s,k\) | 任务、区域、小时、开工小时、任务类型索引 | 索引 | \(r\in\mathcal R,\ t=0,\ldots,2406\) |
| \(\mathcal R,\mathcal K\) | 六区域集合、三任务类型集合 | 题面直接给定 | 无 |
| \(a_i,d_i,g_i\) | 到达小时、连续执行时长、GPU需求 | `workload_trace.xlsx` | h、min、等效GPU |
| \(o_i,k_i\) | 来源区域、任务类型 | 附件输入 | 无 |
| \(f_i^{\max},\ell_i^{\max}\) | 最晚完成时点、最大时延 | 附件输入 | h、ms |
| \(\ell_{or}\) | 单向网络时延 | `network_latency.xlsx` | ms |
| \(\Delta t\) | 时段长度 | 题面直接给定 | \(1\) h |
| \(\omega_{it}(s)\) | 任务与时段的重叠时长 | 派生参数 | h |
| \(\alpha_{it}(s)\) | 时段平均占用比例，\(\omega_{it}(s)/\Delta t\) | 派生参数 | \([0,1]\) |
| \(x_{irs}\) | 任务是否在区域 \(r\)、小时 \(s\) 开工 | 二元变量 | \(\{0,1\}\) |
| \(G_r^{\max}\) | 可调度GPU容量 | `Available_GPU` | 等效GPU |
| \(P_r^{IT,\max},P_r^{F,\max}\) | IT、设施功率上限 | `GPU_information.xlsx` | MW |
| \(p_k^{GPU}\) | 每等效GPU平均IT功率 | `power_mapping.xlsx` | MW/等效GPU |
| \(\pi_r\) | PUE | 附件输入 | 无量纲 |
| \(L_{rt}^{N},L_{rt}^{BAI}\) | NonAI、问题三Baseline AI IT负荷 | `region_time_data.xlsx` | MW |
| \(L_{rt}^{AI},L_{rt}^{IT},L_{rt}^{F}\) | AI IT、总IT、设施负荷 | 派生量 | MW |
| \(b_{rt}^{GPU},b_{rt}^{AI}\) | 前序已承诺任务的固定GPU、AI IT占用 | 前序基础调度推导 | 等效GPU、MW |
| \(R_{rt}^{av}\) | 可用新能源 | 附件输入 | MW |
| \(R_{rt}^{use},R_{rt}^{ch},R_{rt}^{sell},R_{rt}^{curt}\) | 直接消纳、充电、外送、弃电 | 非负变量 | MW |
| \(G_{rt}^{load},G_{rt}^{ch}\) | 电网供负荷、给储能充电 | 非负变量 | MW |
| \(G_{rt}^{buy},G_{rt}^{sell}\) | 总购电、售电 | 非负变量 | MW |
| \(C_{rt},D_{rt}\) | 总充电、放电功率 | 非负变量 | MW |
| \(S_{rt}\) | 小时 \(t\) 运行后的SOC | 状态变量 | MWh |
| \(S_r^0,S_r^{min},S_r^{max}\) | 初始SOC及上下限 | 储能附件 | MWh |
| \(\eta_r^c,\eta_r^d\) | 充放电效率 | 储能附件 | \((0,1]\) |
| \(C_r^{\max},D_r^{\max}\) | 充放电功率上限 | 储能附件 | MW |
| \(I_r^{\max},E_r^{\max}\) | 购电、外送上限 | 附件输入 | MW |
| \(N_{rt}\) | 净购电功率 | \(G^{buy}-G^{sell}\) | MW |
| \(P_r^{peak},z_{rt},V_r\) | 峰值、绝对爬坡辅助量、爬坡总量 | 辅助变量 | MW |
| \(C_{\mathrm{op}},E_{\mathrm{CO2}}\) | 运行成本、购电碳排放 | 目标/指标 | 元、tCO2 |
| \(L_{\mathrm{net}}\) | GPU-hour加权平均时延 | 指标 | ms |
| \(U_{\mathrm{RE}}\) | 新能源利用率 | 指标 | \([0,1]\) |
| \(Q_{\mathrm{service}}\) | 服务质量 | 指标 | \([0,1]\) |
| \(A_C,A_L,A_W,A_U,A_R\) | 已确定窗口的累计碳、时延分子、GPU-hour、新能源利用量、可用量 | 滚动状态 | tCO2、GPU·h·ms、GPU·h、MWh、MWh |
| \(H\) | 固定滚动窗口长度 | 预声明 | \(168\) h |
| \(\varepsilon_C,\varepsilon_L,\varepsilon_U,\varepsilon_Q,\varepsilon_{P,r},\varepsilon_{V,r}\) | 全时域指标阈值 | 单目标参照解生成 | 对应指标单位 |

附件数值、预测误差和优化结果均由代码阶段读取真实附件后计算，本阶段不预填。

## 统一模型边界

任务到达、结清和终端时域为

$$
\mathcal T_A=\{0,\ldots,2399\},\qquad
\mathcal T_C=\{2400,\ldots,2405\}.
\tag{1}
$$

第2406小时不产生或执行任务，只进行电力和SOC终端结算。任务完成时点可等于2406，但执行区间必须包含于 \([0,2406)\)。

任务重叠时长及无量纲占用比例分别为

$$
\omega_{it}(s)=
\max\left\{0,
\min(t+\Delta t,s+d_i/60)-\max(t,s)
\right\},
\tag{2}
$$

$$
\alpha_{it}(s)=\frac{\omega_{it}(s)}{\Delta t}\in[0,1].
\tag{3}
$$

GPU容量和MW功率均使用 \(\alpha\)；GPU-hour统计使用 \(\omega\)，从而量纲闭合。

候选集合为

$$
\Omega_i=
\left\{(r,s):
\ell_{o_ir}\le\ell_i^{\max},\
s\ge a_i,\
s+d_i/60\le\min(f_i^{\max},2406)
\right\}.
\tag{4}
$$

实时任务额外满足 \(s=a_i\)。若某任务 \(\Omega_i=\varnothing\)，对应调度结构化停止并输出无可行候选任务表。

统一任务约束为

$$
\sum_{(r,s)\in\Omega_i}x_{irs}=1,
\tag{5}
$$

$$
\sum_{i,s}g_i\alpha_{it}(s)x_{irs}\le G_r^{\max}.
\tag{6}
$$

负荷映射为

$$
L_{rt}^{AI}
=\sum_{i,s}g_ip_{k_i}^{GPU}\alpha_{it}(s)x_{irs},
\tag{7}
$$

$$
L_{rt}^{IT}=L_{rt}^{N}+L_{rt}^{AI},
\qquad
L_{rt}^{F}=\pi_rL_{rt}^{IT},
\tag{8}
$$

$$
L_{rt}^{IT}\le P_r^{IT,\max},
\qquad
L_{rt}^{F}\le P_r^{F,\max}.
\tag{9}
$$

成本和碳排放为

$$
C_{\mathrm{op}}
=\sum_{r,t}
\left(c_{rt}^{buy}G_{rt}^{buy}
-c_{rt}^{sell}G_{rt}^{sell}\right)\Delta t,
\tag{10}
$$

$$
E_{\mathrm{CO2}}
=\sum_{r,t}\kappa_{rt}G_{rt}^{buy}\Delta t.
\tag{11}
$$

## 子问题 1：需求预测与末端基础调度

### 模型思路

区域—类型—小时需求分别用季节性朴素模型和滞后正则化回归预测。最后24小时基础调度使用实际到达任务，并传递2376时点仍未完成的全部前序已承诺任务：既包括已开工任务，也包括已安排在2376时或之后开工的任务。

### 模型建立

需求统计量为

$$
D_{rkt}^{GPU}=\sum_{i:o_i=r,k_i=k,a_i=t}g_i,
\qquad
D_{rkt}^{GPUh}
=\sum_{i:o_i=r,k_i=k,a_i=t}g_i\frac{d_i}{60}.
\tag{12}
$$

季节性候选为

$$
\widehat D_{rkt}^{(24)}=D_{rk,t-24},
\qquad
\widehat D_{rkt}^{(168)}=D_{rk,t-168}.
\tag{13}
$$

增强候选为

$$
\widehat D_{rkt}
=\max\left\{0,\beta_0+
\sum_{\ell\in\{1,2,3,24,48,168\}}\beta_\ell D_{rk,t-\ell}
+\gamma^\top z_t+\alpha_r+\delta_k\right\},
\tag{14}
$$

$$
\min_{\beta,\gamma,\alpha,\delta}
\sum_{r,k,t\in\mathcal T_{\mathrm{train}}}
\rho(D_{rkt}-\widehat D_{rkt})
+\lambda\|\beta\|_2^2.
\tag{15}
$$

其中 \(z_t\) 仅含过去可得的小时、星期周期编码及滚动统计。数据划分为

$$
\mathcal T_{\mathrm{train}}=0{:}2351,\quad
\mathcal T_{\mathrm{val}}=2352{:}2375,\quad
\mathcal T_{\mathrm{test}}=2376{:}2399.
\tag{16}
$$

评价指标为

$$
MAE=\frac1n\sum_j|y_j-\hat y_j|,
\qquad
RMSE=\sqrt{\frac1n\sum_j(y_j-\hat y_j)^2},
\tag{17}
$$

$$
WAPE=\frac{\sum_j|y_j-\hat y_j|}{\sum_j|y_j|}.
\tag{18}
$$

仅当式(18)分母为正时计算；否则该分组输出“验证不可用”，保留MAE、RMSE及分母为正的总体WAPE。

设前序基础调度给出固定区域 \(r_i^0\)、开工时刻 \(s_i^0\)。定义

$$
\mathcal I^{pre}
=\left\{i:a_i<2376,\ s_i^0+d_i/60>2376\right\}.
\tag{19}
$$

式(19)覆盖2376时已开工未完成任务，以及已到达但承诺在2376时或以后开工的任务。固定占用为

$$
b_{rt}^{GPU}
=\sum_{i\in\mathcal I^{pre}:r_i^0=r}
g_i\alpha_{it}(s_i^0),
\tag{20}
$$

$$
b_{rt}^{AI}
=\sum_{i\in\mathcal I^{pre}:r_i^0=r}
g_ip_{k_i}^{GPU}\alpha_{it}(s_i^0).
\tag{21}
$$

对最后24小时实际到达任务集合
\(\mathcal I^{end}=\{i:2376\le a_i\le2399\}\)，有

$$
\sum_{(r,s)\in\Omega_i}x_{irs}=1,\qquad i\in\mathcal I^{end},
\tag{22}
$$

$$
b_{rt}^{GPU}
+\sum_{i\in\mathcal I^{end},s}
g_i\alpha_{it}(s)x_{irs}
\le G_r^{\max},
\tag{23}
$$

$$
L_{rt}^{N}+b_{rt}^{AI}
+\sum_{i\in\mathcal I^{end},s}
g_ip_{k_i}^{GPU}\alpha_{it}(s)x_{irs}
\le P_r^{IT,\max},
\tag{24}
$$

$$
\pi_rL_{rt}^{IT}\le P_r^{F,\max},
\qquad t=2376,\ldots,2405.
\tag{25}
$$

最大GPU利用率显式绑定为

$$
U^{\max}\ge
\frac{b_{rt}^{GPU}+
\sum_{i\in\mathcal I^{end},s}g_i\alpha_{it}(s)x_{irs}}
{G_r^{\max}}.
\tag{26}
$$

采用词典序目标

$$
\min\left[
\sum_{i\in\mathcal I^{end}}(s_i-a_i),\
\sum_{i,r,s}\ell_{o_ir}x_{irs},\
U^{\max}
\right].
\tag{27}
$$

### 求解方法

验证集按WAPE、MAE选择预测结构，确定后用0–2375小时重训并测试。前序基础调度先覆盖所有 \(a_i<2376\) 的任务，随后按式(19)–(21)冻结全部跨界承诺，再求末端MILP。无完整可行解时结构化停止。

### 可观测性

需求标签可观测；最优调度标签不可观测，以唯一执行率、实时即时开工率、截止满足率、最大时延违约、容量及功率残差验证。

### 必须回答的输出

1. 区域—任务类型统计表。
2. 验证集候选比较和最终选模规则。
3. 测试集总体及分组MAE、RMSE、WAPE。
4. 第2376–2399小时实际任务调度方案。
5. 所有前序跨界承诺和跨越2399小时任务的结清结果。
6. 最后24小时甘特图文件。
7. 各区域逐时GPU利用率表和曲线文件。
8. 任务、时延、GPU、IT功率、设施功率及2406禁占用审计表。

## 子问题 2：碳感知任务调度

### 模型思路

联合优化实际任务的执行区域、开工时刻和无储能能源分配。采用新能源分源，外送新能源不能同时满足负荷。

### 模型建立

任务满足式(4)–(9)。新能源分源及负荷平衡为

$$
R_{rt}^{use}+R_{rt}^{sell}+R_{rt}^{curt}=R_{rt}^{av},
\tag{28}
$$

$$
G_{rt}^{buy}+R_{rt}^{use}=L_{rt}^{F},
\qquad
G_{rt}^{sell}=R_{rt}^{sell},
\tag{29}
$$

$$
0\le G_{rt}^{buy}\le I_r^{\max},
\qquad
0\le G_{rt}^{sell}\le E_r^{\max}.
\tag{30}
$$

平均网络时延为

$$
L_{\mathrm{net}}
=\frac{\sum_{i,r,s}g_i(d_i/60)\ell_{o_ir}x_{irs}}
{\sum_i g_i(d_i/60)}.
\tag{31}
$$

任务集非空且 \(g_i,d_i>0\) 时分母为正；空任务集时输出“不可计算”并退出相关Pareto排序。

问题二无储能，新能源利用率为

$$
U_{\mathrm{RE}}^{q2}
=\frac{\sum_{r,t}(R_{rt}^{use}+R_{rt}^{sell})\Delta t}
{\sum_{r,t}R_{rt}^{av}\Delta t}.
\tag{32}
$$

分母为0时输出“不可计算”，另报利用量和弃电量。

ε约束模型为

$$
\min C_{\mathrm{op}},
\tag{33}
$$

$$
E_{\mathrm{CO2}}\le\varepsilon_C,\qquad
L_{\mathrm{net}}\le\varepsilon_L,\qquad
U_{\mathrm{RE}}^{q2}\ge\varepsilon_U.
\tag{34}
$$

### 滚动累计预算

设窗口 \(w\) 前已固定的累计量为

$$
A_C^{w-1}=\sum_{\text{已固定时段}}\kappa_{rt}G_{rt}^{buy}\Delta t,
\tag{35}
$$

$$
A_L^{w-1}=\sum_{\text{已固定任务}}g_i(d_i/60)\ell_{o_ir_i},
\quad
A_W^{w-1}=\sum_{\text{已固定任务}}g_i(d_i/60),
\tag{36}
$$

$$
A_U^{w-1}=\sum_{\text{已固定时段}}(R_{rt}^{use}+R_{rt}^{sell})\Delta t,
\quad
A_R^{w-1}=\sum_{\text{已固定时段}}R_{rt}^{av}\Delta t.
\tag{37}
$$

每窗碳约束为

$$
A_C^{w-1}+\Delta A_C^w\le\varepsilon_C.
\tag{38}
$$

对已在当前窗口确定执行区域的任务，时延预算为

$$
A_L^{w-1}+\Delta A_L^w
\le
\varepsilon_L\left(A_W^{w-1}+\Delta A_W^w+W_{\mathrm{rem}}^{LB}\right),
\tag{39}
$$

其中 \(W_{\mathrm{rem}}^{LB}\) 是尚未确定任务GPU-hour总量；该量由任务数据精确计算，与执行区域无关。新能源利用率采用终端可达性约束

$$
A_U^{w-1}+\Delta A_U^w+R_{\mathrm{rem}}^{av}
\ge\varepsilon_U A_R^{total},
\tag{40}
$$

其中 \(R_{\mathrm{rem}}^{av}\) 为当前窗口后剩余可用新能源总量，\(A_R^{total}\) 为完整时域可用新能源总量。最后窗口将式(40)收紧为精确终端约束。

### 求解方法

先求单目标ideal和nadir参照值。只采用五条联合锚点路径 \(a\in\{0,0.25,0.5,0.75,1\}\)：所有有效阈值同时按同一 \(a\) 插值，最多5个候选，不作多维笛卡尔积。固定 \(H=168\) 小时并传递式(35)–(37)状态；窗口内执行式(38)–(40)，拼接后全时域精确复算。失败即结构化停止。

### 可观测性

输入可观测，真实最优标签不可观测。采用任务硬约束、累计预算、式(28)–(30)守恒、全时域指标复算、求解状态和最优间隙验证。

### 必须回答的输出

1. 全部实际任务的区域、开工和完成时刻。
2. 区域逐时AI IT、总IT和设施负荷。
3. 逐时购电、新能源直接消纳、外送和弃电策略。
4. 成本、碳排放、平均及高分位时延、新能源利用率。
5. 相对基础调度的绝对及相对变化。
6. Pareto表和Pareto图文件。
7. 各任务类型迁移数、迁移GPU-hour、等待和时延。
8. 累计预算、完整可行性、求解状态和最优间隙审计。

## 子问题 3：固定负荷下的储能协同优化

### 模型思路

固定Baseline AI IT与NonAI IT负荷，仅优化新能源分配、储能、购售电。新能源利用率严格计入新能源充电。

### 模型建立

$$
L_{rt}^{F}=\pi_r(L_{rt}^{BAI}+L_{rt}^{N}).
\tag{41}
$$

新能源分源、负荷与充电分解为

$$
R_{rt}^{use}+R_{rt}^{ch}
+R_{rt}^{sell}+R_{rt}^{curt}=R_{rt}^{av},
\tag{42}
$$

$$
G_{rt}^{load}+R_{rt}^{use}+D_{rt}=L_{rt}^{F},
\tag{43}
$$

$$
C_{rt}=R_{rt}^{ch}+G_{rt}^{ch},
\quad
G_{rt}^{buy}=G_{rt}^{load}+G_{rt}^{ch},
\quad
G_{rt}^{sell}=R_{rt}^{sell}.
\tag{44}
$$

SOC约束为

$$
S_{r,-1}=S_r^0,
\tag{45}
$$

$$
S_{rt}=S_{r,t-1}
+\eta_r^cC_{rt}\Delta t
-\frac{D_{rt}\Delta t}{\eta_r^d},
\tag{46}
$$

$$
S_r^{min}\le S_{rt}\le S_r^{max},
\qquad
S_{r,2406}\ge S_r^0.
\tag{47}
$$

充放电互斥为

$$
0\le C_{rt}\le u_{rt}^{c}C_r^{max},
\quad
0\le D_{rt}\le(1-u_{rt}^{c})D_r^{max},
\quad u_{rt}^{c}\in\{0,1\}.
\tag{48}
$$

净购电、峰值和爬坡为

$$
N_{rt}=G_{rt}^{buy}-G_{rt}^{sell},
\quad
P_r^{peak}\ge N_{rt},
\tag{49}
$$

$$
z_{rt}\ge N_{rt}-N_{r,t-1},
\quad
z_{rt}\ge-(N_{rt}-N_{r,t-1}),
\quad
V_r=\sum_{t=1}^{2406}z_{rt}.
\tag{50}
$$

为消除辅助变量松弛，所有正式方案采用词典序目标

$$
\min\left[
C_{\mathrm{op}},\
\sum_rP_r^{peak}+\sum_{r,t}z_{rt}
\right],
\tag{51}
$$

并满足

$$
E_{\mathrm{CO2}}\le\varepsilon_C,\quad
P_r^{peak}\le\varepsilon_{P,r},\quad
V_r\le\varepsilon_{V,r}.
\tag{52}
$$

最终报告不直接读取可能受容差影响的辅助变量，而由净购电轨迹复算

$$
\widehat P_r^{peak}=\max_tN_{rt},
\qquad
\widehat V_r=\sum_{t=1}^{2406}|N_{rt}-N_{r,t-1}|.
\tag{53}
$$

新能源利用率为

$$
U_{\mathrm{RE}}^{q3}
=
\frac{\sum_{r,t}
(R_{rt}^{use}+R_{rt}^{ch}+R_{rt}^{sell})\Delta t}
{\sum_{r,t}R_{rt}^{av}\Delta t}.
\tag{54}
$$

分母为0时输出“不可计算”，不参与排序。

等效完整循环量为

$$
N_r^{EFC}
=\frac{\sum_t(C_{rt}+D_{rt})\Delta t}{2B_r}.
\tag{55}
$$

仅对 \(B_r>0\) 的储能区域计算，否则标记“不适用”。

### 求解方法

先求无储能参照，再求成本、碳排、峰值和爬坡单目标参照解；采用最多5条联合ε路径。正式解执行二级目标(51)，并按式(53)复算峰值和爬坡。

### 可观测性

最优动作不可观测；附件SOC仅作基准对照。通过能源平衡、SOC递推、终端状态、边界、互斥及净购电轨迹复算验证。

### 必须回答的输出

1. 各区域0–2406小时新能源、充放电、购售电和弃电策略。
2. 绝对SOC轨迹和终端SOC。
3. 储能前后成本、碳排放、复算峰值净购电和绝对爬坡量。
4. 指标绝对及相对变化。
5. 各区域等效完整循环量。
6. SOC、充放电和净购电曲线文件。
7. 能源、SOC、边界、互斥和终端状态审计文件。
8. 含新能源充电的新能源利用率口径核验。

## 子问题 4：多区域算—储—电联合优化

### 模型思路

联合决定任务迁移、开工、新能源分配、储能和购售电。滚动窗口显式传递全时域指标累计状态；Pareto指标先统一转换为“越小越好”的损失量。

### 模型建立

联合模型满足式(4)–(9)、(42)–(50)。新能源利用率为

$$
U_{\mathrm{RE}}^{q4}
=
\frac{\sum_{r,t}
(R_{rt}^{use}+R_{rt}^{ch}+R_{rt}^{sell})\Delta t}
{\sum_{r,t}R_{rt}^{av}\Delta t}.
\tag{56}
$$

服务质量分量为

$$
Q_{\mathrm{RT}}
=\frac{\#\{i\in RT:s_i=a_i\}}{\#RT},
\quad
Q_{\mathrm{SLA}}
=\frac{\#\{i:\ell_{o_ir_i}\le\ell_i^{max}\}}{\#\mathcal I},
\tag{57}
$$

$$
Q_{\mathrm{deadline}}
=\frac{\#\{i:s_i+d_i/60\le f_i^{max}\}}{\#\mathcal I},
\tag{58}
$$

$$
Q_{\mathrm{wait}}
=1-
\frac{\sum_{i\notin RT}(s_i-a_i)}
{\sum_{i\notin RT}(f_i^{max}-a_i-d_i/60)}.
\tag{59}
$$

仅保留分母为正的分量集合 \(J_{\mathrm{def}}\)，并令

$$
Q_{\mathrm{service}}
=\sum_{j\in J_{\mathrm{def}}}\widetilde w_jQ_j,
\qquad
\widetilde w_j=
\frac{1/4}{\sum_{h\in J_{\mathrm{def}}}1/4}.
\tag{60}
$$

若 \(J_{\mathrm{def}}=\varnothing\)，服务质量输出“不可计算”并退出相关排序。

联合ε模型为

$$
\min C_{\mathrm{op}},
\tag{61}
$$

$$
E_{\mathrm{CO2}}\le\varepsilon_C,\quad
L_{\mathrm{net}}\le\varepsilon_L,\quad
Q_{\mathrm{service}}\ge\varepsilon_Q,
\tag{62}
$$

$$
U_{\mathrm{RE}}^{q4}\ge\varepsilon_U,\qquad
P_r^{peak}\le\varepsilon_{P,r}.
\tag{63}
$$

统一定义越小越好的Pareto损失向量

$$
y_m=
\left(
C_{\mathrm{op}},E_{\mathrm{CO2}},L_{\mathrm{net}},
1-Q_{\mathrm{service}},1-U_{\mathrm{RE}}^{q4},
\widehat P_1^{peak},\ldots,\widehat P_6^{peak}
\right)_m.
\tag{64}
$$

对每一有效损失维度，

$$
\bar y_{jm}
=
\frac{y_{jm}-y_j^{ideal}}
{y_j^{nadir}-y_j^{ideal}},
\qquad
y_j^{ideal}=\min_m y_{jm},
\quad
y_j^{nadir}=\max_m y_{jm}.
\tag{65}
$$

仅保留 \(y_j^{nadir}>y_j^{ideal}\) 的维度 \(J_{\mathrm{disc}}\)，折中方案为

$$
m^*=
\arg\min_m
\sqrt{\sum_{j\in J_{\mathrm{disc}}}
\frac{1}{|J_{\mathrm{disc}}|}\bar y_{jm}^2}.
\tag{66}
$$

若 \(J_{\mathrm{disc}}=\varnothing\)，按成本、碳排、时延固定词典序选择。

### 滚动累计状态

除式(35)–(37)外，问题四将新能源利用量改为

$$
A_U^{w}
=A_U^{w-1}
+\sum_{(r,t)\in w}
(R_{rt}^{use}+R_{rt}^{ch}+R_{rt}^{sell})\Delta t.
\tag{67}
$$

服务质量分别传递各分量已确定的分子和分母；只有任务执行区域及开工时刻均已冻结后才计入。等待质量使用等价线性预算

$$
\sum_{i\notin RT}(s_i-a_i)
\le
(1-\varepsilon_{\mathrm{wait}})
\sum_{i\notin RT}(f_i^{max}-a_i-d_i/60).
\tag{68}
$$

每窗传递已累计等待量和剩余允许等待量。实时、SLA、截止分量同样传递已满足计数、已确定计数和剩余任务数，并用终端可达上下界剪枝。最终窗口对式(60)、(62)作精确全时域约束与复算。

### 情景模型

碳约束为

$$
E_{\mathrm{CO2}}\le(1-\rho_C)E^0,
\qquad
\rho_C\in\{0,0.1,0.2,0.3\}.
\tag{69}
$$

购电峰谷价差情景为

$$
c_{rt}^{buy,sc}
=\bar c_r+\delta_P(c_{rt}^{buy}-\bar c_r),
\quad
\delta_P\in\{0.75,1,1.25\},
\tag{70}
$$

$$
\bar c_r=\frac1{2407}\sum_{t=0}^{2406}c_{rt}^{buy}.
\tag{71}
$$

售电价格机制情景为

$$
c_{rt}^{sell,sc}
=\delta_Sc_{rt}^{sell},
\qquad
\delta_S\in\{0,0.5,1\}.
\tag{72}
$$

三档分别表示不允许获得售电收益、半额售电收益和附件基准售电机制；物理外送仍受 \(E_r^{\max}\) 约束。

新能源水平情景为

$$
R_{rt}^{av,level}
=\max(0,\delta_RR_{rt}^{av}),
\qquad
\delta_R\in\{0.8,1,1.2\}.
\tag{73}
$$

波动增强情景为

$$
R_{rt}^{av,vol}
=\max(0,R_{rt}^{av}+\sigma_{sc}\xi_{rt}),
\tag{74}
$$

其中随机种子固定为2026，各区域 \(\xi\) 标准化为样本均值0、样本方差1，

$$
\sigma_{sc}
=0.1\operatorname{mean}\{R_{rt}^{av}:R_{rt}^{av}>0\}.
\tag{75}
$$

无正样本区域取 \(\sigma_{sc}=0\)。由于截断可能改变均值，结果必须同时报告扰动前后实际新能源均值，波动情景解释限定为“含截断效应的波动增强”。

### 求解方法

1. 删除违反到达、时延、截止及2406边界的候选。
2. 求单目标参照值并生成最多5条联合ε路径。
3. 固定 \(H=168\) 小时，传递任务占用、绝对SOC及式(35)–(40)、(67)–(68)累计状态。
4. 每窗实施剩余预算和终端可达性约束；拼接失败结构化停止。
5. 对最终轨迹全时域精确复算并按式(64)–(66)选折中解。
6. 分别重求式(69)–(75)情景。
7. 全部子问题共享 \(B_{\mathrm{total}}=300\) s，统一搜索截止为 \(t_{\mathrm{start}}+285\) s，末15秒输出文件和终检；未完整完成候选丢弃。

### 可观测性

联合策略无真实最优标签。任务、能源流、SOC、成本和碳排均可复算；验证使用硬约束、累计预算、窗口衔接、守恒残差、非支配性及单因素情景响应。

### 必须回答的输出

1. 折中方案逐任务区域、开工、完成、等待和时延。
2. 各区域逐时AI IT、设施负荷、新能源、储能、购售电和SOC。
3. 成本、碳排、时延、服务质量、新能源利用率和复算峰值净购电。
4. Pareto表、非支配关系和折中方案。
5. 不同碳约束下的指标、迁移、循环和可行性变化。
6. 不同购电峰谷价差及售电价格机制下的策略变化。
7. 新能源上升、下降和波动增强情景变化。
8. 各情景相对统一基准的绝对及相对变化。
9. 各任务类型迁移数、GPU-hour、等待和时延。
10. 各区域复算峰值、爬坡量和等效循环量。
11. 累计预算、窗口衔接、求解状态和最优间隙审计。
12. Pareto图、负荷与SOC曲线、迁移流向图和情景比较图文件。

## 统一结果审计

任务审计为

$$
\sum_{r,s}x_{irs}=1,\quad
i\in RT\Rightarrow s_i=a_i,
\tag{76}
$$

$$
a_i\le s_i,\quad
s_i+d_i/60\le\min(f_i^{max},2406),\quad
\ell_{o_ir_i}\le\ell_i^{max}.
\tag{77}
$$

问题二能源残差为

$$
e_{\max}^{q2}
=\max_{r,t}
\left|
G_{rt}^{buy}+R_{rt}^{av}
-L_{rt}^{F}-G_{rt}^{sell}-R_{rt}^{curt}
\right|.
\tag{78}
$$

问题三、四能源残差为

$$
e_{\max}^{energy}
=\max_{r,t}
\left|
G_{rt}^{buy}+R_{rt}^{av}+D_{rt}
-L_{rt}^{F}-C_{rt}-G_{rt}^{sell}-R_{rt}^{curt}
\right|.
\tag{79}
$$

SOC残差为

$$
e_{\max}^{SOC}
=\max_{r,t}
\left|
S_{rt}-S_{r,t-1}
-\eta_r^cC_{rt}\Delta t
+\frac{D_{rt}\Delta t}{\eta_r^d}
\right|.
\tag{80}
$$

正式结果同时报告式(76)–(80)、最大GPU/功率/SOC违约、2406执行任务数、未完成任务数、累计预算残差、求解状态和最优间隙。峰值及爬坡仅报告式(53)复算值。

## 局限性与停止规则

1. 任务、电价、碳强度和新能源按确定值处理。
2. 网络只采用题面单向时延，不增加带宽、迁移能耗或线路潮流。
3. PUE和GPU功率严格读取附件。
4. 测试集不参与预测调参。
5. 外部搜索未执行，未作为参数来源。
6. 若出现空候选集、累计预算终端不可达、滚动拼接失败或无完整可行解，在对应位置结构化停止。
7. 新能源、任务或服务质量分母为0时输出“不可计算”或“不适用”，并退出相应Pareto维度，不使用任意小常数替代业务分母。

## Verifier 修复核对表

| Block issue | 修复位置 | 可计算性与有限输出保证 |
|---|---|---|
| 问题三、四新能源利用率遗漏新能源充电 | 式(54)、式(56)、式(67) | 分子统一计入 \(R^{use}+R^{ch}+R^{sell}\)；分母为0时输出“不可计算”并退出排序。 |
| 问题一遗漏2376前到达但尚未开工任务 | 式(19)–(24) | \(\mathcal I^{pre}\) 按“到达早于2376且完成晚于2376”定义，同时覆盖已开工与已承诺未开工任务，并全部进入固定容量和功率占用。 |
| Pareto归一化未统一指标方向 | 式(64)–(66) | 最大化指标改为损失 \(1-Q_{\mathrm{service}}\)、\(1-U_{\mathrm{RE}}\)，所有维度均越小越好；零区间维度删除，避免零分母。 |
| 滚动窗口缺少全时域ε累计量和剩余预算 | 式(35)–(40)、式(67)–(68) | 显式传递碳、时延分子、GPU-hour、新能源利用量、可用量及服务计数；每窗约束剩余预算和终端可达性，最终全时域精确复算。 |
| 问题四缺少售电价格机制情景 | 式(72) | 固定 \(\delta_S\in\{0,0.5,1\}\)，覆盖无售电收益、半额和基准机制，且保留物理外送边界。 |
| 重叠时长直接用于MW和GPU容量导致量纲错误 | 式(2)–(3)、式(6)–(7)、式(20)–(26) | 显式区分小时量 \(\omega\) 与无量纲比例 \(\alpha=\omega/\Delta t\)；容量和功率使用 \(\alpha\)，GPU-hour使用 \(\omega\)。 |
| 峰值和爬坡辅助变量可能松弛 | 式(51)–(53) | 正式方案加入二级最小化消除松弛；最终峰值和爬坡仍从净购电轨迹直接复算，不依赖辅助变量取值。 |