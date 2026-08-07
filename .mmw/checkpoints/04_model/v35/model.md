# 数学模型

## 符号说明

| 符号 | 含义 | 类型及来源 | 取值范围/单位 |
|---|---|---|---|
| \(i,r,t,s,k\) | 任务、区域、小时、候选开工小时、任务类型索引 | 索引 | \(r\in\mathcal R,\ t=0,\ldots,2406\) |
| \(\mathcal R,\mathcal K\) | 六区域集合、三任务类型集合 | 题面直接给定 | 无 |
| \(a_i,d_i,g_i\) | 到达小时、连续执行时长、GPU需求 | `workload_trace.xlsx` | h、min、等效GPU |
| \(o_i,k_i\) | 来源区域、任务类型 | 附件输入 | 无 |
| \(f_i^{\max},\ell_i^{\max}\) | 最晚完成时点、最大允许网络时延 | 附件输入 | h、ms |
| \(\ell_{or}\) | 来源区域 \(o\) 至执行区域 \(r\) 的单向网络时延 | `network_latency.xlsx` | ms |
| \(\Delta t\) | 时段长度 | 题面直接给定 | \(1\) h |
| \(\omega_{it}(s)\) | 任务在小时 \(t\) 内的实际重叠时长 | 派生参数 | h |
| \(\alpha_{it}(s)\) | 时段平均占用比例 \(\omega_{it}(s)/\Delta t\) | 派生参数 | \([0,1]\) |
| \(x_{irs}\) | 任务是否选择区域 \(r\)、时刻 \(s\) 开工 | 二元变量 | \(\{0,1\}\) |
| \(q_{ir}\) | 任务是否在区域 \(r\) 执行 | \(q_{ir}=\sum_sx_{irs}\) | \(\{0,1\}\) |
| \(s_i,c_i,\ell_i\) | 实际开工时刻、完成时刻、实际网络时延 | 由 \(x_{irs}\) 唯一派生 | h、h、ms |
| \(G_r^{\max}\) | 可调度GPU容量 | `Available_GPU` | 等效GPU |
| \(P_r^{IT,\max},P_r^{F,\max}\) | IT功率、设施功率上限 | `GPU_information.xlsx` | MW |
| \(p_k^{GPU}\) | 类型 \(k\) 每等效GPU平均IT功率 | `power_mapping.xlsx` | MW/等效GPU |
| \(\pi_r\) | 区域PUE | `GPU_information.xlsx` | 无量纲 |
| \(L_{rt}^{N},L_{rt}^{BAI}\) | NonAI、问题三Baseline AI IT负荷 | `region_time_data.xlsx` | MW |
| \(L_{rt}^{AI},L_{rt}^{IT},L_{rt}^{F}\) | AI IT、总IT、设施负荷 | 派生量 | MW |
| \(b_{rt}^{GPU},b_{rt}^{AI}\) | 前序已承诺任务的固定GPU、AI IT占用 | 经审计的前序基础调度 | 等效GPU、MW |
| \(R_{rt}^{av}\) | 可用新能源 | `region_time_data.xlsx` | MW |
| \(R_{rt}^{use},R_{rt}^{ch},R_{rt}^{sell},R_{rt}^{curt}\) | 直接消纳、储能充电、外送、弃电 | 非负变量 | MW |
| \(G_{rt}^{load},G_{rt}^{ch}\) | 电网供负荷、从电网给储能充电 | 非负变量 | MW |
| \(G_{rt}^{buy},G_{rt}^{sell}\) | 区域总购电、总售电功率 | 非负变量 | MW |
| \(y_{rt}^{grid}\) | 购售电互斥状态；1允许购电，0允许售电 | 二元变量 | \(\{0,1\}\) |
| \(C_{rt},D_{rt}\) | 储能总充电、放电功率 | 非负变量 | MW |
| \(S_{rt}\) | 小时 \(t\) 运行后的SOC | 状态变量 | MWh |
| \(B_r\) | 储能额定容量 | `StorageCapacity_MWh` | MWh |
| \(S_r^0,S_r^{min},S_r^{max}\) | 初始SOC及安全上下限 | `storage_information.xlsx` | MWh |
| \(\eta_r^c,\eta_r^d\) | 充放电效率 | `storage_information.xlsx` | \((0,1]\) |
| \(C_r^{\max},D_r^{\max}\) | 充放电功率上限 | `storage_information.xlsx` | MW |
| \(I_r^{\max},E_r^{\max}\) | 区域购电、外送硬上限 | `MaxGridImport_MW`、`MaxGridExport_MW`或附件对应字段 | MW |
| \(N_{rt}\) | 净购电功率 \(G_{rt}^{buy}-G_{rt}^{sell}\) | 派生量 | MW |
| \(P_r^{peak},z_{rt},V_r\) | 峰值辅助量、绝对爬坡辅助量、爬坡总量 | 辅助变量 | MW |
| \(C_{\mathrm{op}},E_{\mathrm{CO2}}\) | 运行成本、购电碳排放 | 目标或指标 | 元、tCO2 |
| \(L_{\mathrm{net}}\) | GPU-hour加权平均网络时延 | 指标 | ms |
| \(U_{\mathrm{RE}}\) | 新能源利用率 | 指标 | \([0,1]\) |
| \(Q_{\mathrm{service}}\) | 服务质量 | 指标 | \([0,1]\) |
| \(A_C,A_L,A_W,A_U,A_R\) | 已冻结部分的累计碳、时延分子、GPU-hour、新能源利用量、可用量 | 滚动状态 | tCO2、GPU·h·ms、GPU·h、MWh、MWh |
| \(H\) | 固定滚动窗口长度 | 预声明 | \(168\) h |
| \(\varepsilon_C,\varepsilon_L,\varepsilon_U,\varepsilon_Q\) | 碳、时延、新能源利用率、服务质量阈值 | 单目标参照解生成 | 对应指标单位 |
| \(\varepsilon_{P,r},\varepsilon_{V,r}\) | 峰值净购电、爬坡量阈值 | 单目标参照解生成 | MW |
| \(B_{\mathrm{total}},T_{\mathrm{tail}},D_{\mathrm{search}}\) | 总墙钟预算、收尾预留、搜索截止 | 固定运行合同 | 300 s、15 s、\(t_{\mathrm{start}}+285\) s |

附件数值、预测误差和优化结果均由代码阶段读取真实附件后计算，本阶段不预填。

## 统一模型边界

任务到达、结清和终端时域为

$$
\mathcal T_A=\{0,\ldots,2399\},\qquad
\mathcal T_C=\{2400,\ldots,2405\}.
\tag{1}
$$

第2406小时不产生或执行任务，只进行电力和SOC终端结算。任务完成时点可以等于2406，但执行区间必须属于 \([0,2406)\)。

任务重叠时长与平均占用比例为

$$
\omega_{it}(s)=
\max\left\{0,\min(t+\Delta t,s+d_i/60)-\max(t,s)\right\},
\tag{2}
$$

$$
\alpha_{it}(s)=\frac{\omega_{it}(s)}{\Delta t}\in[0,1].
\tag{3}
$$

GPU容量和MW功率使用无量纲比例 \(\alpha\)，GPU-hour统计使用 \(\omega\)。

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

实时任务额外要求 \(s=a_i\)。若 \(\Omega_i=\varnothing\)，输出无可行候选任务表并在对应调度问题结构化停止。

每个任务唯一执行：

$$
\sum_{(r,s)\in\Omega_i}x_{irs}=1.
\tag{5}
$$

实际执行区域、开工时刻、完成时刻和时延必须由同一组二元变量唯一派生：

$$
q_{ir}=\sum_{s:(r,s)\in\Omega_i}x_{irs},
\qquad
s_i=\sum_{(r,s)\in\Omega_i}s\,x_{irs},
\tag{6}
$$

$$
c_i=s_i+\frac{d_i}{60},
\qquad
\ell_i=\sum_{r\in\mathcal R}\ell_{o_ir}q_{ir}.
\tag{7}
$$

因此所有等待时间、服务质量、甘特图和任务审计只能读取式(6)–(7)，不得另设自由的 \(s_i\)。

GPU容量约束为

$$
\sum_{i,s}g_i\alpha_{it}(s)x_{irs}\le G_r^{\max}.
\tag{8}
$$

任务负荷映射为

$$
L_{rt}^{AI}
=\sum_{i,s}g_ip_{k_i}^{GPU}\alpha_{it}(s)x_{irs},
\tag{9}
$$

$$
L_{rt}^{IT}=L_{rt}^{N}+L_{rt}^{AI},
\qquad
L_{rt}^{F}=\pi_rL_{rt}^{IT},
\tag{10}
$$

$$
L_{rt}^{IT}\le P_r^{IT,\max},
\qquad
L_{rt}^{F}\le P_r^{F,\max}.
\tag{11}
$$

运行成本和购电碳排放为

$$
C_{\mathrm{op}}
=\sum_{r,t}
\left(c_{rt}^{buy}G_{rt}^{buy}
-c_{rt}^{sell}G_{rt}^{sell}\right)\Delta t,
\tag{12}
$$

$$
E_{\mathrm{CO2}}
=\sum_{r,t}\kappa_{rt}G_{rt}^{buy}\Delta t.
\tag{13}
$$

问题二至问题四统一施加区域购售电边界与互斥约束：

$$
0\le G_{rt}^{buy}\le I_r^{\max}y_{rt}^{grid},
\tag{14}
$$

$$
0\le G_{rt}^{sell}\le E_r^{\max}(1-y_{rt}^{grid}),
\qquad
y_{rt}^{grid}\in\{0,1\}.
\tag{15}
$$

式(14)–(15)不依赖价格关系，直接排除同一地区同一小时同时购售电，避免售电价异常或情景变换引发非预期套利。

## 子问题 1：需求预测与末端基础调度

### 模型思路

区域—任务类型—小时需求分别用季节性朴素模型和滞后正则化回归预测。最后24小时基础调度使用实际到达任务，并传递2376时点仍未完成的全部前序已承诺任务。前序承诺只有通过完整任务、容量和功率审计后才能冻结。

### 模型建立

需求统计量为

$$
D_{rkt}^{GPU}=\sum_{i:o_i=r,k_i=k,a_i=t}g_i,
\qquad
D_{rkt}^{GPUh}
=\sum_{i:o_i=r,k_i=k,a_i=t}g_i\frac{d_i}{60}.
\tag{16}
$$

季节性候选为

$$
\widehat D_{rkt}^{(24)}=D_{rk,t-24},
\qquad
\widehat D_{rkt}^{(168)}=D_{rk,t-168}.
\tag{17}
$$

增强候选为

$$
\widehat D_{rkt}
=\max\left\{0,\beta_0+
\sum_{\ell\in\{1,2,3,24,48,168\}}\beta_\ell D_{rk,t-\ell}
+\gamma^\top z_t+\alpha_r+\delta_k\right\},
\tag{18}
$$

$$
\min_{\beta,\gamma,\alpha,\delta}
\sum_{r,k,t\in\mathcal T_{\mathrm{train}}}
\rho(D_{rkt}-\widehat D_{rkt})
+\lambda\|\beta\|_2^2.
\tag{19}
$$

其中 \(z_t\) 仅含预测时点以前可得的小时、星期周期编码和滚动统计。数据划分为

$$
\mathcal T_{\mathrm{train}}=0{:}2351,\quad
\mathcal T_{\mathrm{val}}=2352{:}2375,\quad
\mathcal T_{\mathrm{test}}=2376{:}2399.
\tag{20}
$$

评价指标为

$$
MAE=\frac1n\sum_j|y_j-\hat y_j|,
\qquad
RMSE=\sqrt{\frac1n\sum_j(y_j-\hat y_j)^2},
\tag{21}
$$

$$
WAPE=\frac{\sum_j|y_j-\hat y_j|}{\sum_j|y_j|}.
\tag{22}
$$

式(22)仅在分母为正时计算；否则该分组输出“验证不可用”，并保留MAE、RMSE及分母为正的总体WAPE。

设前序基础调度给出区域 \(r_i^0\) 和开工时刻 \(s_i^0\)。在冻结前，必须逐项验证

$$
a_i\le s_i^0,\quad
s_i^0+d_i/60\le\min(f_i^{\max},2406),\quad
\ell_{o_ir_i^0}\le\ell_i^{\max},
\tag{23}
$$

并验证实时即时开工、唯一执行、逐时GPU、IT功率、设施功率以及第2406小时禁占用。任一前序承诺未通过时，停止末端模型并输出前序承诺审计失败表。

定义

$$
\mathcal I^{pre}
=\left\{i:a_i<2376,\ s_i^0+d_i/60>2376\right\}.
\tag{24}
$$

它同时覆盖2376时已开工未完成任务，以及已到达但承诺在2376时或以后开工的任务。固定占用为

$$
b_{rt}^{GPU}
=\sum_{i\in\mathcal I^{pre}:r_i^0=r}
g_i\alpha_{it}(s_i^0),
\tag{25}
$$

$$
b_{rt}^{AI}
=\sum_{i\in\mathcal I^{pre}:r_i^0=r}
g_ip_{k_i}^{GPU}\alpha_{it}(s_i^0).
\tag{26}
$$

最后24小时实际到达任务集合为

$$
\mathcal I^{end}=\{i:2376\le a_i\le2399\}.
\tag{27}
$$

这些任务满足式(4)–(7)，且

$$
b_{rt}^{GPU}
+\sum_{i\in\mathcal I^{end},s}
g_i\alpha_{it}(s)x_{irs}
\le G_r^{\max}.
\tag{28}
$$

末端AI IT、总IT和设施负荷显式绑定为

$$
L_{rt}^{AI,end}
=b_{rt}^{AI}
+\sum_{i\in\mathcal I^{end},s}
g_ip_{k_i}^{GPU}\alpha_{it}(s)x_{irs},
\tag{29}
$$

$$
L_{rt}^{IT,end}=L_{rt}^{N}+L_{rt}^{AI,end},
\qquad
L_{rt}^{F,end}=\pi_rL_{rt}^{IT,end}.
\tag{30}
$$

对应功率硬约束为

$$
L_{rt}^{IT,end}\le P_r^{IT,\max},
\qquad
L_{rt}^{F,end}\le P_r^{F,\max},
\quad t=2376,\ldots,2405.
\tag{31}
$$

最大GPU利用率绑定为

$$
U^{\max}\ge
\frac{b_{rt}^{GPU}+
\sum_{i\in\mathcal I^{end},s}g_i\alpha_{it}(s)x_{irs}}
{G_r^{\max}}.
\tag{32}
$$

若某区域 \(G_r^{\max}=0\)，该区域不生成任务候选；利用率输出“不适用”，不执行除零。

采用词典序目标

$$
\min\left[
\sum_{i\in\mathcal I^{end}}(s_i-a_i),\
\sum_{i,r,s}\ell_{o_ir}x_{irs},\
U^{\max}
\right],
\tag{33}
$$

其中 \(s_i\) 严格由式(6)确定，故等待目标有界且与真实调度一致。

### 求解方法

验证集按WAPE、MAE选择预测结构，模型确定后用0–2375小时重新训练并测试。前序基础调度先覆盖所有 \(a_i<2376\) 的任务，通过式(23)及容量、功率审计后，再按式(24)–(26)冻结跨界承诺并求解末端MILP。无完整可行解时结构化停止。

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
8. 前序承诺、任务、时延、GPU、IT功率、设施功率及2406禁占用审计表。

## 子问题 2：碳感知任务调度

### 模型思路

联合优化实际任务的执行区域、开工时刻和无储能能源分配。新能源采用分源变量，且通过式(14)–(15)执行区域购售电边界与互斥。

### 模型建立

任务满足式(4)–(11)。问题二不使用储能，即

$$
R_{rt}^{ch}=G_{rt}^{ch}=C_{rt}=D_{rt}=0.
\tag{34}
$$

新能源分源及负荷平衡为

$$
R_{rt}^{use}+R_{rt}^{sell}+R_{rt}^{curt}=R_{rt}^{av},
\tag{35}
$$

$$
G_{rt}^{buy}+R_{rt}^{use}=L_{rt}^{F},
\qquad
G_{rt}^{sell}=R_{rt}^{sell}.
\tag{36}
$$

并施加

$$
0\le G_{rt}^{buy}\le I_r^{\max}y_{rt}^{grid},
\quad
0\le G_{rt}^{sell}\le E_r^{\max}(1-y_{rt}^{grid}),
\quad y_{rt}^{grid}\in\{0,1\}.
\tag{37}
$$

GPU-hour加权平均网络时延为

$$
L_{\mathrm{net}}
=\frac{\sum_{i,r,s}g_i(d_i/60)\ell_{o_ir}x_{irs}}
{\sum_i g_i(d_i/60)}.
\tag{38}
$$

任务集非空且 \(g_i,d_i>0\) 时分母为正；否则输出“不可计算”，并退出相关时延约束和候选排序。

问题二新能源利用率为

$$
U_{\mathrm{RE}}^{q2}
=\frac{\sum_{r,t}(R_{rt}^{use}+R_{rt}^{sell})\Delta t}
{\sum_{r,t}R_{rt}^{av}\Delta t}.
\tag{39}
$$

分母为0时输出“不可计算”，另报新能源利用量和弃电量，并排除新能源利用率约束与排序维度。

ε约束模型为

$$
\min C_{\mathrm{op}},
\tag{40}
$$

$$
E_{\mathrm{CO2}}\le\varepsilon_C,\qquad
L_{\mathrm{net}}\le\varepsilon_L,\qquad
U_{\mathrm{RE}}^{q2}\ge\varepsilon_U.
\tag{41}
$$

### 滚动累计预算

窗口 \(w\) 前已固定的累计量为

$$
A_C^{w-1}
=\sum_{\text{已固定时段}}
\kappa_{rt}G_{rt}^{buy}\Delta t,
\tag{42}
$$

$$
A_L^{w-1}
=\sum_{\text{已固定任务}}
g_i(d_i/60)\ell_i,
\qquad
A_W^{w-1}
=\sum_{\text{已固定任务}}g_i(d_i/60),
\tag{43}
$$

$$
A_U^{w-1}
=\sum_{\text{已固定时段}}
(R_{rt}^{use}+R_{rt}^{sell})\Delta t,
\quad
A_R^{w-1}
=\sum_{\text{已固定时段}}R_{rt}^{av}\Delta t.
\tag{44}
$$

每窗碳约束为

$$
A_C^{w-1}+\Delta A_C^w\le\varepsilon_C.
\tag{45}
$$

时延预算为

$$
A_L^{w-1}+\Delta A_L^w
\le
\varepsilon_L
\left(A_W^{w-1}+\Delta A_W^w+W_{\mathrm{rem}}^{LB}\right),
\tag{46}
$$

其中

$$
W_{\mathrm{rem}}^{LB}
=\sum_{i\in\mathcal I_{\mathrm{rem}}}g_i(d_i/60)
\tag{47}
$$

由尚未冻结任务数据精确计算，与执行区域无关。

新能源终端可达性约束为

$$
A_U^{w-1}+\Delta A_U^w+R_{\mathrm{rem}}^{av}
\ge\varepsilon_U A_R^{total},
\tag{48}
$$

其中 \(R_{\mathrm{rem}}^{av}\) 是当前窗口后剩余可用新能源总量，\(A_R^{total}\) 是完整时域可用新能源总量。最终窗口按式(39)精确复算。

### 求解方法

先求各单目标参照值。仅计算五条预声明联合路径

$$
a\in\{0,0.25,0.5,0.75,1\},
\tag{49}
$$

所有有效阈值同时按同一 \(a\) 在参照端点间插值，最多形成5个有限候选，不作多维笛卡尔积，也不宣称得到完整连续Pareto前沿。

固定 \(H=168\) 小时滚动求解，并传递式(42)–(44)状态。拼接后进行全时域精确复算；失败则结构化停止。

滚动方法是预算内启发式分解。每个窗口的求解器间隙仅表示该窗口MILP在给定边界状态下的间隙，不是拼接方案相对全时域MILP的全局最优间隙。结果必须分别报告：

$$
\texttt{full\_horizon\_feasible}\in\{\texttt{true},\texttt{false}\},
\qquad
\texttt{global\_optimality\_certificate}=\texttt{false}.
\tag{50}
$$

### 可观测性

输入可观测，真实最优标签不可观测。采用任务硬约束、累计预算、式(35)–(37)守恒、全时域指标复算及窗口求解状态验证。全时域复算只证明所得轨迹可行，不证明全时域全局最优。

### 必须回答的输出

1. 全部实际任务的区域、开工和完成时刻。
2. 区域逐时AI IT、总IT和设施负荷。
3. 逐时购电、新能源直接消纳、外送和弃电策略。
4. 成本、碳排放、平均及高分位时延、新能源利用率。
5. 相对基础调度的绝对及相对变化。
6. 五条联合路径有限候选表和候选图文件。
7. 各任务类型迁移数、迁移GPU-hour、等待和时延。
8. 累计预算、购售电边界与互斥、完整可行性、窗口求解状态和窗口间隙审计。
9. `global_optimality_certificate=false`及其适用口径。

## 子问题 3：固定负荷下的储能协同优化

### 模型思路

固定Baseline AI IT与NonAI IT负荷，仅优化新能源分配、储能、购售电。新能源利用率计入新能源充电，区域购售电能力和购售互斥作为逐区域逐小时硬约束。

### 模型建立

设施负荷为

$$
L_{rt}^{F}=\pi_r(L_{rt}^{BAI}+L_{rt}^{N}).
\tag{51}
$$

新能源分源、负荷及充电分解为

$$
R_{rt}^{use}+R_{rt}^{ch}
+R_{rt}^{sell}+R_{rt}^{curt}=R_{rt}^{av},
\tag{52}
$$

$$
G_{rt}^{load}+R_{rt}^{use}+D_{rt}=L_{rt}^{F},
\tag{53}
$$

$$
C_{rt}=R_{rt}^{ch}+G_{rt}^{ch},
\quad
G_{rt}^{buy}=G_{rt}^{load}+G_{rt}^{ch},
\quad
G_{rt}^{sell}=R_{rt}^{sell}.
\tag{54}
$$

区域购售电硬边界及互斥为

$$
0\le G_{rt}^{buy}\le I_r^{\max}y_{rt}^{grid},
\tag{55}
$$

$$
0\le G_{rt}^{sell}\le E_r^{\max}(1-y_{rt}^{grid}),
\qquad
y_{rt}^{grid}\in\{0,1\}.
\tag{56}
$$

SOC约束为

$$
S_{r,-1}=S_r^0,
\tag{57}
$$

$$
S_{rt}=S_{r,t-1}
+\eta_r^cC_{rt}\Delta t
-\frac{D_{rt}\Delta t}{\eta_r^d},
\tag{58}
$$

$$
S_r^{min}\le S_{rt}\le S_r^{max},
\qquad
S_{r,2406}\ge S_r^0.
\tag{59}
$$

充放电互斥为

$$
0\le C_{rt}\le u_{rt}^{c}C_r^{max},
\tag{60}
$$

$$
0\le D_{rt}\le(1-u_{rt}^{c})D_r^{max},
\qquad
u_{rt}^{c}\in\{0,1\}.
\tag{61}
$$

净购电、峰值和爬坡为

$$
N_{rt}=G_{rt}^{buy}-G_{rt}^{sell},
\qquad
P_r^{peak}\ge N_{rt},
\tag{62}
$$

$$
z_{rt}\ge N_{rt}-N_{r,t-1},
\quad
z_{rt}\ge-(N_{rt}-N_{r,t-1}),
\quad
V_r=\sum_{t=1}^{2406}z_{rt}.
\tag{63}
$$

正式方案采用词典序目标

$$
\min\left[
C_{\mathrm{op}},\
\sum_rP_r^{peak}+\sum_{r,t}z_{rt}
\right],
\tag{64}
$$

并满足

$$
E_{\mathrm{CO2}}\le\varepsilon_C,\quad
P_r^{peak}\le\varepsilon_{P,r},\quad
V_r\le\varepsilon_{V,r}.
\tag{65}
$$

最终从净购电轨迹复算

$$
\widehat P_r^{peak}=\max_tN_{rt},
\qquad
\widehat V_r=\sum_{t=1}^{2406}|N_{rt}-N_{r,t-1}|.
\tag{66}
$$

新能源利用率为

$$
U_{\mathrm{RE}}^{q3}
=
\frac{\sum_{r,t}
(R_{rt}^{use}+R_{rt}^{ch}+R_{rt}^{sell})\Delta t}
{\sum_{r,t}R_{rt}^{av}\Delta t}.
\tag{67}
$$

分母为0时输出“不可计算”并排除该排序维度。

\(B_r\) 明确定义为 `storage_information.xlsx` 中的 `StorageCapacity_MWh`。等效完整循环量为

$$
N_r^{EFC}
=\frac{\sum_t(C_{rt}+D_{rt})\Delta t}{2B_r}.
\tag{68}
$$

仅当 \(B_r>0\) 时计算；若 \(B_r=0\) 或该区域无储能，输出“不适用”。

### 求解方法

先求无储能参照，再求成本、碳排、峰值和爬坡单目标参照解；计算最多5条联合ε路径上的有限候选。正式解执行式(64)的二级目标，并按式(66)复算峰值与爬坡。

滚动或分解求解时，各窗口求解器间隙仅作为窗口级诊断；最终全时域复算验证可行性，固定报告 `global_optimality_certificate=false`，不把窗口间隙解释为全时域全局最优性证明。

### 可观测性

最优动作不可观测；附件SOC仅作基准对照。通过能源平衡、SOC递推、终端状态、购售电边界、购售电互斥、充放电互斥及净购电轨迹复算验证。

### 必须回答的输出

1. 各区域0–2406小时新能源、充放电、购售电和弃电策略。
2. 绝对SOC轨迹和终端SOC。
3. 储能前后成本、碳排放、复算峰值净购电和绝对爬坡量。
4. 指标绝对及相对变化。
5. 各区域等效完整循环量。
6. SOC、充放电和净购电曲线文件。
7. 能源、SOC、购售电边界与互斥、充放电互斥和终端状态审计文件。
8. 含新能源充电的新能源利用率口径核验。
9. 窗口级求解状态、窗口间隙及 `global_optimality_certificate=false`。

## 子问题 4：多区域算—储—电联合优化

### 模型思路

联合决定任务迁移、开工、新能源分配、储能和购售电。任务时刻全部由 \(x_{irs}\) 派生；购售电硬边界与互斥逐区域逐小时生效；滚动窗口显式传递全时域指标累计状态。

### 模型建立

任务满足式(4)–(11)，能源和储能满足式(52)–(63)，并逐时满足式(55)–(56)。

新能源利用率为

$$
U_{\mathrm{RE}}^{q4}
=
\frac{\sum_{r,t}
(R_{rt}^{use}+R_{rt}^{ch}+R_{rt}^{sell})\Delta t}
{\sum_{r,t}R_{rt}^{av}\Delta t}.
\tag{69}
$$

分母为0时输出“不可计算”，并排除相关约束、归一化和排序维度。

服务质量分量全部使用式(6)–(7)派生的真实任务状态：

$$
Q_{\mathrm{RT}}
=\frac{\#\{i\in RT:s_i=a_i\}}{\#RT},
\quad
Q_{\mathrm{SLA}}
=\frac{\#\{i:\ell_i\le\ell_i^{max}\}}{\#\mathcal I},
\tag{70}
$$

$$
Q_{\mathrm{deadline}}
=\frac{\#\{i:c_i\le f_i^{max}\}}{\#\mathcal I},
\tag{71}
$$

$$
Q_{\mathrm{wait}}
=1-
\frac{\sum_{i\notin RT}(s_i-a_i)}
{\sum_{i\notin RT}(f_i^{max}-a_i-d_i/60)}.
\tag{72}
$$

仅保留分母为正的分量集合 \(J_{\mathrm{def}}\)，并令

$$
Q_{\mathrm{service}}
=\sum_{j\in J_{\mathrm{def}}}\widetilde w_jQ_j,
\qquad
\widetilde w_j=
\frac{1/4}{\sum_{h\in J_{\mathrm{def}}}1/4}.
\tag{73}
$$

若 \(J_{\mathrm{def}}=\varnothing\)，输出“不可计算”并退出相关约束和排序。

联合ε模型为

$$
\min C_{\mathrm{op}},
\tag{74}
$$

$$
E_{\mathrm{CO2}}\le\varepsilon_C,\quad
L_{\mathrm{net}}\le\varepsilon_L,\quad
Q_{\mathrm{service}}\ge\varepsilon_Q,
\tag{75}
$$

$$
U_{\mathrm{RE}}^{q4}\ge\varepsilon_U,
\qquad
P_r^{peak}\le\varepsilon_{P,r}.
\tag{76}
$$

统一定义越小越好的候选损失向量

$$
y_m=
\left(
C_{\mathrm{op}},E_{\mathrm{CO2}},L_{\mathrm{net}},
1-Q_{\mathrm{service}},1-U_{\mathrm{RE}}^{q4},
\widehat P_1^{peak},\ldots,\widehat P_6^{peak}
\right)_m.
\tag{77}
$$

在实际完成的有限候选集合 \(\mathcal M_{\mathrm{done}}\) 中，

$$
y_j^{ideal}=\min_{m\in\mathcal M_{\mathrm{done}}}y_{jm},
\qquad
y_j^{nadir}=\max_{m\in\mathcal M_{\mathrm{done}}}y_{jm}.
\tag{78}
$$

仅对 \(y_j^{nadir}>y_j^{ideal}\) 的维度计算

$$
\bar y_{jm}
=\frac{y_{jm}-y_j^{ideal}}
{y_j^{nadir}-y_j^{ideal}}.
\tag{79}
$$

令这些维度组成 \(J_{\mathrm{disc}}\)，折中方案为

$$
m^*=
\arg\min_{m\in\mathcal M_{\mathrm{done}}}
\sqrt{
\sum_{j\in J_{\mathrm{disc}}}
\frac{\bar y_{jm}^2}{|J_{\mathrm{disc}}|}
}.
\tag{80}
$$

若 \(J_{\mathrm{disc}}=\varnothing\)，按成本、碳排、时延固定词典序选择。该选择仅作用于五条联合路径中完整求解且通过全时域复算的有限候选，不代表完整连续Pareto前沿。

### 滚动累计状态

问题四累计新能源利用量为

$$
A_U^{w}
=A_U^{w-1}
+\sum_{(r,t)\in w}
(R_{rt}^{use}+R_{rt}^{ch}+R_{rt}^{sell})\Delta t.
\tag{81}
$$

服务质量分别传递各分量已确定的分子和分母；任务的执行区域与开工时刻均冻结后才计入。等待质量使用等价线性预算

$$
\sum_{i\notin RT}(s_i-a_i)
\le
(1-\varepsilon_{\mathrm{wait}})
\sum_{i\notin RT}
(f_i^{max}-a_i-d_i/60).
\tag{82}
$$

每窗传递累计等待量和剩余允许等待量。实时、SLA和截止分量传递已满足计数、已确定计数和剩余任务数，并使用终端可达上下界剪枝。最终窗口后按式(69)–(80)全时域复算。

### 情景模型

碳约束为

$$
E_{\mathrm{CO2}}\le(1-\rho_C)E^0,
\qquad
\rho_C\in\{0,0.1,0.2,0.3\},
\tag{83}
$$

其中 \(E^0\) 是附件基准参数下、统一任务与能源口径重新计算所得基准碳排放；未得到有限可行基准时不生成该情景并结构化停止。

购电峰谷价差情景为

$$
c_{rt}^{buy,sc}
=\bar c_r+\delta_P(c_{rt}^{buy}-\bar c_r),
\quad
\delta_P\in\{0.75,1,1.25\},
\tag{84}
$$

$$
\bar c_r=\frac1{2407}\sum_{t=0}^{2406}c_{rt}^{buy}.
\tag{85}
$$

售电价格机制情景为

$$
c_{rt}^{sell,sc}
=\delta_Sc_{rt}^{sell},
\qquad
\delta_S\in\{0,0.5,1\}.
\tag{86}
$$

所有价格情景仍受式(55)–(56)约束，不会因价格变化产生同时购售电。

新能源水平情景为

$$
R_{rt}^{av,level}
=\max(0,\delta_RR_{rt}^{av}),
\qquad
\delta_R\in\{0.8,1,1.2\}.
\tag{87}
$$

波动增强情景为

$$
R_{rt}^{av,vol}
=\max(0,R_{rt}^{av}+\sigma_{sc}\xi_{rt}),
\tag{88}
$$

其中随机种子固定为2026，各区域 \(\xi_{rt}\) 标准化为样本均值0、样本方差1，且

$$
\sigma_{sc}
=0.1\operatorname{mean}
\{R_{rt}^{av}:R_{rt}^{av}>0\}.
\tag{89}
$$

若区域无正新能源样本，则取 \(\sigma_{sc}=0\)。结果同时报告扰动前后实际均值，波动情景限定解释为“含截断效应的波动增强”。

### 求解方法

1. 删除违反到达、时延、截止和2406边界的候选。
2. 求单目标参照值，并生成式(49)的五条联合路径有限候选。
3. 固定 \(H=168\) 小时，传递任务占用、绝对SOC及累计碳、时延、新能源和服务质量状态。
4. 每窗实施剩余预算和终端可达性约束；拼接失败则结构化停止。
5. 对完整轨迹进行全时域精确复算，仅保留可行候选，再按式(77)–(80)选择折中解。
6. 分别重新求解式(83)–(89)的情景。
7. 全部子问题共享
   \(B_{\mathrm{total}}=300\) s，
   \(D_{\mathrm{search}}=t_{\mathrm{start}}+285\) s，
   \(T_{\mathrm{tail}}=15\) s。使用单调时钟记录实际耗时；每项固定工作、窗口和候选启动前检查共同截止，未完整完成的候选丢弃。
8. 各窗口求解器间隙仅报告为 `window_gap`。最终全时域复算只证明所得轨迹可行，统一报告
   `global_optimality_certificate=false`，不得解释为全时域MILP全局最优证书。

### 可观测性

联合策略无真实最优标签。任务、能源流、SOC、购售电边界、成本和碳排均可复算；验证使用硬约束、累计预算、窗口衔接、守恒残差、有限候选非支配性及单因素情景响应。

### 必须回答的输出

1. 折中方案逐任务区域、开工、完成、等待和时延。
2. 各区域逐时AI IT、设施负荷、新能源、储能、购售电和SOC。
3. 成本、碳排、时延、服务质量、新能源利用率和复算峰值净购电。
4. 五条联合路径有限候选表、非支配关系和折中方案。
5. 不同碳约束下的指标、迁移、循环和可行性变化。
6. 不同购电峰谷价差及售电价格机制下的策略变化。
7. 新能源上升、下降和波动增强情景变化。
8. 各情景相对统一基准的绝对及相对变化。
9. 各任务类型迁移数、GPU-hour、等待和时延。
10. 各区域复算峰值、爬坡量和等效循环量。
11. 累计预算、窗口衔接、购售电边界与互斥、求解状态和窗口间隙审计。
12. 候选图、负荷与SOC曲线、迁移流向图和情景比较图文件。
13. `full_horizon_feasible`与`global_optimality_certificate=false`。

## 统一结果审计

任务审计为

$$
\sum_{r,s}x_{irs}=1,\quad
s_i=\sum_{r,s}s\,x_{irs},\quad
c_i=s_i+d_i/60,
\tag{90}
$$

$$
i\in RT\Rightarrow s_i=a_i,
\quad
a_i\le s_i,\quad
c_i\le\min(f_i^{max},2406),\quad
\ell_i\le\ell_i^{max}.
\tag{91}
$$

问题二能源残差为

$$
e_{\max}^{q2}
=\max_{r,t}
\left|
G_{rt}^{buy}+R_{rt}^{av}
-L_{rt}^{F}-G_{rt}^{sell}-R_{rt}^{curt}
\right|.
\tag{92}
$$

问题三、四能源残差为

$$
e_{\max}^{energy}
=\max_{r,t}
\left|
G_{rt}^{buy}+R_{rt}^{av}+D_{rt}
-L_{rt}^{F}-C_{rt}-G_{rt}^{sell}-R_{rt}^{curt}
\right|.
\tag{93}
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
\tag{94}
$$

购售电边界及互斥审计为

$$
e_{\max}^{grid}
=\max_{r,t}
\left\{
\max(0,G_{rt}^{buy}-I_r^{\max}),
\max(0,G_{rt}^{sell}-E_r^{\max}),
\min(G_{rt}^{buy},G_{rt}^{sell})
\right\}.
\tag{95}
$$

正式结果同时报告式(90)–(95)、最大GPU/功率/SOC违约、2406执行任务数、未完成任务数、累计预算残差、窗口求解状态和窗口间隙。峰值与爬坡仅报告式(66)复算值。全时域可行性只在所有残差不超过预声明数值容差 \(\tau_{num}\) 且全部离散约束成立时标记为真。

## 局限性与停止规则

1. 任务、电价、碳强度和新能源按确定值处理。
2. 网络只采用题面单向时延，不增加带宽、迁移能耗或线路潮流。
3. PUE和GPU功率严格读取附件。
4. 测试集不参与预测调参。
5. 外部搜索未执行，未作为参数来源。
6. 若出现空候选集、前序承诺审计失败、累计预算终端不可达、滚动拼接失败或无完整可行解，在对应位置结构化停止。
7. 新能源、任务或服务质量分母为0时输出“不可计算”或“不适用”，并退出相应约束及排序维度，不使用任意小常数代替业务分母。
8. 五条联合ε路径只构成预算内预声明有限候选集，不代表完整连续Pareto前沿。
9. 滚动窗口求解器间隙只适用于单个窗口MILP；最终全时域复算只能证明所得拼接轨迹可行，不能证明其为全时域全局最优解。
10. 未完整完成或超过共同总截止的候选不进入指标比较、非支配筛选或正式结果。

## Verifier 修复核对表

| Block issue | 修复位置 | 可计算性与有限输出保证 |
|---|---|---|
| 实际开工时刻 \(s_i\) 未与 \(x_{irs}\) 绑定，等待目标和服务质量可能脱离调度或无界 | 式(6)–(7)、式(33)、式(70)–(73)、式(90)–(91) | 以 \(s_i=\sum s x_{irs}\) 唯一派生开工时刻，并定义 \(c_i\)、\(q_{ir}\)、\(\ell_i\)；所有等待、完成、时延、服务质量和审计均读取同一派生状态，因此目标有界且与真实选择一致。 |
| 问题三缺少区域购电与外送功率硬上限，问题四继承了不完整模型 | 统一式(14)–(15)，问题三式(55)–(56)，问题四明确继承式(52)–(63)，审计式(95) | \(G^{buy}\) 和 \(G^{sell}\) 分别受附件区域上限约束；任何越界方案均不可行，并由有限残差 \(e_{\max}^{grid}\) 复核。 |
| 正式方程没有同时购售电互斥或可执行价格触发规则，存在套利风险 | 式(14)–(15)、式(37)、式(55)–(56) | 二元状态 \(y_{rt}^{grid}\) 在所有价格与情景下直接排除同一区域同一小时同时购售电，不依赖价格数据能否自然排除套利。 |
| 问题一设施功率约束未明确绑定固定前序占用与末端任务占用；等效循环公式中的 \(B_r\) 未定义 | 式(29)–(31)、符号表、式(68) | 末端AI IT、总IT和设施负荷逐层显式等式绑定后再施加上限；\(B_r\) 明确定义为 `StorageCapacity_MWh`，且只在 \(B_r>0\) 时计算EFC，否则输出“不适用”。 |
| 滚动窗口和五条联合ε路径不能提供全时域全局最优性证明 | 式(49)–(50)、问题二至四求解方法、局限性第8–10项 | 输出明确限定为五条预声明路径上的有限完整候选；窗口gap仅作窗口诊断，正式报告 `global_optimality_certificate=false`。全时域复算只判定有限的可行/不可行状态，不产生虚假的全局最优性结论。 |