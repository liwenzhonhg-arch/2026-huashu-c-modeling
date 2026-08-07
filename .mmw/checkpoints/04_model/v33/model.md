# 数学模型

## 符号说明

| 符号 | 含义 | 类型及数据来源 | 取值范围/单位 |
|---|---|---|---|
| \(i,r,t,s,k\) | 任务、区域、小时、候选开工小时、任务类型索引 | 索引 | \(r\in\mathcal R,\ t=0,\ldots,2406\) |
| \(\mathcal R\) | 六个区域集合 | 题面直接给定 | RegionA–RegionF |
| \(\mathcal K\) | 三类任务集合 | 题面直接给定 | 实时、批量、训练 |
| \(a_i\) | 任务到达小时 | `workload_trace.xlsx` | h |
| \(d_i\) | 不可抢占连续执行时长 | `EstimatedDuration_min` | min，\(d_i>0\) |
| \(g_i\) | 持续占用的等效GPU数量 | `GPU_Demand` | 等效GPU单元 |
| \(o_i,k_i\) | 来源区域、任务类型 | 附件输入 | 无 |
| \(f_i^{\max}\) | 最晚完成时点 | 附件输入 | h，且不晚于2406 |
| \(\ell_i^{\max}\) | 最大允许网络时延 | 附件输入 | ms |
| \(\ell_{or}\) | 区域 \(o\) 到 \(r\) 的单向网络时延 | `network_latency.xlsx` | ms |
| \(x_{irs}\) | 任务是否在区域 \(r\)、整数小时 \(s\) 开工 | 二元决策变量 | \(\{0,1\}\) |
| \(\omega_{it}(s)\) | 任务在小时 \(t\) 内的重叠时长；因时段长为1小时，数值亦为占用比例 | 派生参数 | \([0,1]\) h |
| \(G_r^{\max}\) | 可调度GPU容量 | `Available_GPU` | 等效GPU单元 |
| \(P_r^{IT,\max},P_r^{F,\max}\) | IT及设施功率上限 | `GPU_information.xlsx` | MW |
| \(p_k^{GPU}\) | 类型 \(k\) 每等效GPU的IT功率 | `power_mapping.xlsx` | MW/等效GPU |
| \(\pi_r\) | 区域PUE | 附件输入 | 无量纲，\(\pi_r\ge1\) |
| \(L_{rt}^{N}\) | 不可迁移NonAI IT负荷 | `region_time_data.xlsx` | MW |
| \(L_{rt}^{BAI}\) | 问题三固定Baseline AI IT负荷 | 同上 | MW |
| \(L_{rt}^{AI},L_{rt}^{IT},L_{rt}^{F}\) | AI IT、总IT、设施负荷 | 派生量 | MW |
| \(b_{rt}^{GPU}\) | 第2376小时前已开工任务在末端时段的固定GPU占用 | 由第0–2375小时基础调度及重叠公式计算 | 等效GPU |
| \(b_{rt}^{AI}\) | 上述任务形成的固定AI IT负荷 | 由功率映射计算 | MW |
| \(R_{rt}^{av}\) | 可用新能源 | `region_time_data.xlsx` | MW |
| \(R_{rt}^{use},R_{rt}^{ch},R_{rt}^{sell},R_{rt}^{curt}\) | 新能源直接消纳、充电、外送、弃电 | 连续决策变量 | MW，非负 |
| \(G_{rt}^{load},G_{rt}^{ch}\) | 电网供负荷、充电功率 | 连续决策变量 | MW，非负 |
| \(G_{rt}^{buy},G_{rt}^{sell}\) | 总购电、新能源外送功率 | 连续决策变量 | MW，非负 |
| \(C_{rt},D_{rt}\) | 储能总充电、放电功率 | 连续决策变量 | MW，非负 |
| \(S_{rt}\) | 小时 \(t\) 运行后的绝对SOC | 状态变量 | MWh |
| \(S_r^0\) | 第0小时运行前初始SOC | `InitialSOC_MWh` | MWh |
| \(S_r^{min},S_r^{max}\) | SOC上下限 | 储能附件 | MWh |
| \(\eta_r^c,\eta_r^d\) | 充、放电效率 | 储能附件 | \((0,1]\) |
| \(C_r^{\max},D_r^{\max}\) | 最大充、放电功率 | 储能附件 | MW |
| \(I_r^{\max},E_r^{\max}\) | 最大购电、外送功率 | 附件输入 | MW |
| \(N_{rt}\) | 净购电功率 | 派生量 | MW |
| \(P_r^{peak}\) | 区域峰值净购电 | 辅助变量 | MW |
| \(z_{rt}\) | 相邻小时净购电绝对变化 | 辅助变量 | MW |
| \(C_{\mathrm{op}}\) | 购电支出减新能源外送收益 | 目标/指标 | 元 |
| \(E_{\mathrm{CO2}}\) | 购电碳排放 | 目标/指标 | tCO2 |
| \(L_{\mathrm{net}}\) | GPU-hour加权平均网络时延 | 指标 | ms |
| \(U_{\mathrm{RE}}\) | 新能源利用率 | 指标 | \([0,1]\) |
| \(Q_{\mathrm{service}}\) | 服务质量 | 指标 | \([0,1]\) |
| \(V_r\) | 净购电绝对爬坡总量 | 指标 | MW |
| \(U^{\max}\) | 最大逐时GPU利用率比例 | 调度辅助变量 | \([0,1]\) |
| \(H\) | 固定滚动窗口长度 | 求解前固定 | 168 h |
| \(\varepsilon_C,\varepsilon_L,\varepsilon_U,\varepsilon_Q,\varepsilon_{P,r},\varepsilon_{V,r}\) | 多目标阈值 | 由单目标参照区间按固定锚点生成 | 对应指标单位 |

附件数值、拟合参数、误差和优化结果在模型阶段均为待读取或待求解量，不预填结果。

## 统一边界与共享模型

### 时域

$$
\mathcal T_A=\{0,\ldots,2399\},\qquad
\mathcal T_C=\{2400,\ldots,2405\}.
$$

第2406小时不产生任务，也不执行未完成任务，仅进行电力与SOC终端结算。任务完成时点可等于2406，但执行区间必须包含于 \([0,2406)\)。

本题没有容器、截面或空间尺寸链。区域、时间端点及网络位置均为题面直接给定；不存在图示推导或待确认几何量。

### 不可抢占任务重叠

任务在整数小时 \(s\) 开工，运行 \(d_i/60\) 小时，其在 \([t,t+1)\) 内的重叠为

$$
\omega_{it}(s)=
\max\left\{0,
\min\left(t+1,s+\frac{d_i}{60}\right)-\max(t,s)
\right\}.
\tag{1}
$$

候选集合为

$$
\Omega_i=
\left\{(r,s):
\ell_{o_ir}\le\ell_i^{\max},\
s\ge a_i,\
s+\frac{d_i}{60}\le\min(f_i^{\max},2406)
\right\}.
\tag{2}
$$

实时任务额外要求 \(s=a_i\)。若 \(\Omega_i=\varnothing\)，输出“任务无可行候选”并停止对应调度，不伪造结果。

### 负荷映射

$$
L_{rt}^{AI}
=
\sum_i\sum_{s:(r,s)\in\Omega_i}
g_ip_{k_i}^{GPU}\omega_{it}(s)x_{irs},
\tag{3}
$$

$$
L_{rt}^{IT}=L_{rt}^{N}+L_{rt}^{AI},
\qquad
L_{rt}^{F}=\pi_rL_{rt}^{IT}.
\tag{4}
$$

### 成本与碳排放

$$
C_{\mathrm{op}}
=
\sum_{r,t}
\left(c_{rt}^{buy}G_{rt}^{buy}
-c_{rt}^{sell}G_{rt}^{sell}\right)\Delta t,
\tag{5}
$$

$$
E_{\mathrm{CO2}}
=
\sum_{r,t}\kappa_{rt}G_{rt}^{buy}\Delta t.
\tag{6}
$$

## 子问题 1：需求预测与末端基础调度

### 模型思路

将任务聚合为区域—类型—小时序列，比较季节性朴素模型和滞后特征正则化回归。模型选择只使用训练集和验证集；确定结构后用0–2375小时重训，对2376–2399小时作一次最终测试。

最后24小时调度使用实际到达任务。为避免低估资源占用，先形成第0–2375小时基础调度；其中在2376时仍未结束的任务不重新决策，而是作为2376–2405小时固定占用。

### 模型建立

#### 需求统计

$$
D_{rkt}^{GPU}
=
\sum_{i:o_i=r,k_i=k,a_i=t}g_i,
\tag{7}
$$

$$
D_{rkt}^{GPUh}
=
\sum_{i:o_i=r,k_i=k,a_i=t}
g_i\frac{d_i}{60}.
\tag{8}
$$

统计任务数、GPU总量、GPU-hour、均值、中位数、标准差、四分位数、峰值、时长分位数、小时到达强度、峰值并发、自相关及区域相关性。任一相关序列为常数时，相关系数输出“验证不可用”，改报MAE、绝对差和共同非零时段比例。

#### 预测模型

季节性候选为

$$
\widehat D_{rkt}^{(24)}=D_{rk,t-24},
\qquad
\widehat D_{rkt}^{(168)}=D_{rk,t-168}.
\tag{9}
$$

增强候选为

$$
\widehat D_{rkt}
=
\max\left\{
0,\beta_0+
\sum_{\ell\in\mathcal L}\beta_\ell D_{rk,t-\ell}
+\gamma^\top z_t+\alpha_r+\delta_k
\right\},
\tag{10}
$$

其中 \(\mathcal L=\{1,2,3,24,48,168\}\)，\(z_t\) 仅含可由过去数据得到的小时、星期周期编码、滚动均值和滚动标准差。拟合目标为

$$
\min_{\beta,\gamma,\alpha,\delta}
\sum_{r,k,t\in\mathcal T_{\mathrm{train}}}
\rho(D_{rkt}-\widehat D_{rkt})
+\lambda\|\beta\|_2^2.
\tag{11}
$$

时间划分固定为

$$
\mathcal T_{\mathrm{train}}=0{:}2351,\quad
\mathcal T_{\mathrm{val}}=2352{:}2375,\quad
\mathcal T_{\mathrm{test}}=2376{:}2399.
\tag{12}
$$

评价指标为

$$
MAE=\frac1n\sum_j|y_j-\hat y_j|,
\qquad
RMSE=\sqrt{\frac1n\sum_j(y_j-\hat y_j)^2},
\tag{13}
$$

$$
WAPE=\frac{\sum_j|y_j-\hat y_j|}{\sum_j|y_j|}.
\tag{14}
$$

式(14)仅在 \(\sum_j|y_j|>0\) 时计算；否则分组WAPE标记“验证不可用”，保留MAE、RMSE及分母为正的全测试集总体WAPE。

#### 前序任务固定占用

设 \(\mathcal I^{carry}\) 为第2376小时前已开工且完成时点晚于2376的任务。根据第0–2375小时基础调度的固定执行区域 \(r_i^0\) 和开工时刻 \(s_i^0\)，定义

$$
b_{rt}^{GPU}
=
\sum_{i\in\mathcal I^{carry}:r_i^0=r}
g_i\omega_{it}(s_i^0),
\tag{15}
$$

$$
b_{rt}^{AI}
=
\sum_{i\in\mathcal I^{carry}:r_i^0=r}
g_ip_{k_i}^{GPU}\omega_{it}(s_i^0).
\tag{16}
$$

若不存在前序延续任务，式(15)–(16)由空和自然得到0，仍可直接执行。

#### 末端基础调度MILP

对第2376–2399小时实际到达任务集合 \(\mathcal I^{end}\)：

$$
\sum_{(r,s)\in\Omega_i}x_{irs}=1,\qquad i\in\mathcal I^{end}.
\tag{17}
$$

GPU约束为

$$
b_{rt}^{GPU}
+
\sum_{i\in\mathcal I^{end}}\sum_s
g_i\omega_{it}(s)x_{irs}
\le G_r^{\max},
\quad t=2376,\ldots,2405.
\tag{18}
$$

IT功率与设施功率约束为

$$
L_{rt}^{N}+b_{rt}^{AI}
+
\sum_{i\in\mathcal I^{end}}\sum_s
g_ip_{k_i}^{GPU}\omega_{it}(s)x_{irs}
\le P_r^{IT,\max},
\tag{19}
$$

$$
\pi_rL_{rt}^{IT}\le P_r^{F,\max}.
\tag{20}
$$

开工时刻为

$$
s_i=\sum_{r,s}s\,x_{irs}.
\tag{21}
$$

最大利用率显式绑定为

$$
U^{\max}\ge
\frac{
b_{rt}^{GPU}
+\sum_{i\in\mathcal I^{end}}\sum_s
g_i\omega_{it}(s)x_{irs}
}{
G_r^{\max}
},
\quad\forall r,\ t=2376,\ldots,2405.
\tag{22}
$$

区域逐时GPU利用率百分数为

$$
U_{rt}^{GPU}
=
100\%
\frac{
b_{rt}^{GPU}
+\sum_{i\in\mathcal I^{end},s}
g_i\omega_{it}(s)x_{irs}
}{
G_r^{\max}
}.
\tag{23}
$$

采用词典序目标：

$$
\min
\left[
\sum_{i\in\mathcal I^{end}}(s_i-a_i),\
\sum_{i,r,s}\ell_{o_ir}x_{irs},\
U^{\max}
\right].
\tag{24}
$$

### 求解方法

1. 核验字段、单位、TaskID唯一性和时间覆盖。
2. 以验证集WAPE和MAE选择预测结构；若增强模型两项均不优于最佳季节性模型，则选择季节性模型。
3. 用0–2375小时重新训练确定结构，并对2376–2399小时测试。
4. 先形成第0–2375小时基础调度，计算式(15)–(16)。
5. 以“实时优先—最早截止—短任务优先”形成热启动，再求解式(17)–(24)。
6. 若MILP限时但已有完整可行解，标记“限时可行解”；无可行解则结构化停止。

### 可观测性

需求标签可观测。最优调度标签不可观测，以唯一执行率、实时即时开工率、截止满足率、最大时延违约、容量违约和2406禁占用数量代理验证。

### 必须回答的输出

1. 区域—任务类型统计表。
2. 验证集候选比较与最终选模规则。
3. 第2376–2399小时总体及分组MAE、RMSE、WAPE。
4. 最后24小时实际任务唯一调度方案。
5. 跨越2399小时任务的结清结果和未结清任务数。
6. 最后24小时真实起止时间甘特图文件。
7. 各区域逐时GPU利用率表和曲线文件。
8. 前序固定占用、任务、时延、GPU、IT功率、设施功率和2406禁占用审计表。

## 子问题 2：碳感知任务调度

### 模型思路

联合决定全部实际任务的执行区域和开工时刻，并优化购电、新能源直接消纳、外送和弃电。新能源外送来自 \(R^{av}\) 的分源，不能再次作为负荷侧用电，因此负荷侧平衡不包含售电项。

### 模型建立

任务唯一执行及GPU、IT、设施功率约束采用式(2)–(4)、(17)–(20)。

新能源分源守恒为

$$
R_{rt}^{use}+R_{rt}^{sell}+R_{rt}^{curt}
=R_{rt}^{av}.
\tag{25}
$$

负荷供能平衡为

$$
G_{rt}^{buy}+R_{rt}^{use}=L_{rt}^{F}.
\tag{26}
$$

新能源外送定义为

$$
G_{rt}^{sell}=R_{rt}^{sell}.
\tag{27}
$$

购售电边界为

$$
0\le G_{rt}^{buy}\le I_r^{\max},
\qquad
0\le G_{rt}^{sell}\le E_r^{\max}.
\tag{28}
$$

式(25)–(27)等价于总平衡

$$
G_{rt}^{buy}+R_{rt}^{av}
=
L_{rt}^{F}+G_{rt}^{sell}+R_{rt}^{curt},
\tag{29}
$$

不会产生额外购电支撑新能源外送。正式主模型按附件采用分源外送，不把购售电互斥作为前置条件。

平均网络时延为

$$
L_{\mathrm{net}}
=
\frac{
\sum_{i,r,s}g_i(d_i/60)\ell_{o_ir}x_{irs}
}{
\sum_i g_i(d_i/60)
}.
\tag{30}
$$

由于 \(g_i>0,d_i>0\) 且任务集非空，式(30)分母为正；空任务集时标记“不可计算”，不参与Pareto排序。

新能源利用率为

$$
U_{\mathrm{RE}}
=
\frac{
\sum_{r,t}(R_{rt}^{use}+R_{rt}^{sell})\Delta t
}{
\sum_{r,t}R_{rt}^{av}\Delta t
}.
\tag{31}
$$

若分母为0，输出“不可计算”，另报新能源利用量和弃电量，并将该指标从Pareto排序中删除。

ε约束模型为

$$
\min C_{\mathrm{op}},
\tag{32}
$$

$$
E_{\mathrm{CO2}}\le\varepsilon_C,\qquad
L_{\mathrm{net}}\le\varepsilon_L,\qquad
U_{\mathrm{RE}}\ge\varepsilon_U.
\tag{33}
$$

### 求解方法

先在同一可行域内分别求成本、碳排放、时延和新能源利用率的单目标参照值。对每个非退化指标区间，以

$$
\mathcal A_\varepsilon=\{0,0.25,0.5,0.75,1\}
\tag{34}
$$

在线性区间生成阈值；若上下参照值相同，则固定该值并删除对应ε维度。

滚动窗口固定为 \(H=168\) 小时。已开工任务的连续占用传入下一窗口，最终窗口覆盖2400–2406。拼接后进行全时域审计；拼接失败则结构化停止，不在失败后无界扩大窗口。

### 可观测性

任务、电价、碳强度、新能源和时延可观测；真实最优调度标签不可观测。验证采用最大约束残差、求解状态、最优间隙、成本碳排复算、式(25)和式(29)守恒残差及网络时延分布。

### 必须回答的输出

1. 全部实际任务的执行区域、开工和完成时刻。
2. 区域逐时AI IT、总IT和设施负荷。
3. 区域逐时购电、新能源直接消纳、外送和弃电策略。
4. 成本、碳排放、平均及高分位时延、新能源利用率。
5. 相对基础调度的绝对变化和相对变化率。
6. Pareto表和Pareto图文件。
7. 各任务类型迁移数量、迁移GPU-hour、等待时间和时延。
8. 完整可行性审计、求解状态和最优间隙。

## 子问题 3：固定负荷下的储能协同优化

### 模型思路

问题三固定附件给出的Baseline AI IT和NonAI IT负荷，只优化新能源分配、储能、购电和外送。

### 模型建立

$$
L_{rt}^{F}
=
\pi_r(L_{rt}^{BAI}+L_{rt}^{N}).
\tag{35}
$$

新能源分源守恒为

$$
R_{rt}^{use}+R_{rt}^{ch}
+R_{rt}^{sell}+R_{rt}^{curt}
=R_{rt}^{av}.
\tag{36}
$$

负荷侧平衡、充电分解和购售电定义为

$$
G_{rt}^{load}+R_{rt}^{use}+D_{rt}=L_{rt}^{F},
\tag{37}
$$

$$
C_{rt}=R_{rt}^{ch}+G_{rt}^{ch},
\tag{38}
$$

$$
G_{rt}^{buy}=G_{rt}^{load}+G_{rt}^{ch},
\qquad
G_{rt}^{sell}=R_{rt}^{sell}.
\tag{39}
$$

等价总平衡为

$$
G_{rt}^{buy}+R_{rt}^{av}+D_{rt}
=
L_{rt}^{F}+C_{rt}+G_{rt}^{sell}+R_{rt}^{curt}.
\tag{40}
$$

初始状态和SOC递推为

$$
S_{r,-1}=S_r^0,
\tag{41}
$$

$$
S_{rt}
=
S_{r,t-1}
+\eta_r^cC_{rt}\Delta t
-\frac{D_{rt}\Delta t}{\eta_r^d}.
\tag{42}
$$

$$
S_r^{min}\le S_{rt}\le S_r^{max},
\qquad
S_{r,2406}\ge S_r^0.
\tag{43}
$$

充放电功率及互斥为

$$
0\le C_{rt}\le u_{rt}^{c}C_r^{max},
\tag{44}
$$

$$
0\le D_{rt}\le(1-u_{rt}^{c})D_r^{max},
\qquad u_{rt}^{c}\in\{0,1\}.
\tag{45}
$$

购售电边界采用式(28)。净购电、峰值及爬坡量为

$$
N_{rt}=G_{rt}^{buy}-G_{rt}^{sell},
\tag{46}
$$

$$
P_r^{peak}\ge N_{rt},\qquad\forall t,
\tag{47}
$$

$$
z_{rt}\ge N_{rt}-N_{r,t-1},
\qquad
z_{rt}\ge-(N_{rt}-N_{r,t-1}),
\tag{48}
$$

$$
V_r=\sum_{t=1}^{2406}z_{rt}.
\tag{49}
$$

ε约束模型为

$$
\min C_{\mathrm{op}},
\tag{50}
$$

$$
E_{\mathrm{CO2}}\le\varepsilon_C,\quad
P_r^{peak}\le\varepsilon_{P,r},\quad
V_r\le\varepsilon_{V,r}.
\tag{51}
$$

等效完整循环量为

$$
N_r^{EFC}
=
\frac{\sum_t(C_{rt}+D_{rt})\Delta t}{2B_r},
\tag{52}
$$

其中 \(B_r>0\)；无储能区域不计算该指标并标记“不适用”。

### 求解方法

先求无储能参照，再求成本、碳排放、峰值和爬坡量单目标参照解，并按式(34)生成有限ε网格。附件基准SOC仅用于对比，不作为优化轨迹约束。

### 可观测性

最优储能动作不可观测，基准SOC可观测但不是优化标签。代理验证包括能源平衡、SOC递推、终端SOC、边界、互斥和成本碳排复算。

### 必须回答的输出

1. 各区域0–2406小时新能源直接消纳、充电、购电、放电、外送和弃电策略。
2. 各区域绝对SOC轨迹和终端SOC。
3. 储能前后成本、碳排放、峰值净购电和绝对爬坡量。
4. 指标绝对变化和相对变化率。
5. 各区域等效完整循环量。
6. SOC、充放电和净购电曲线文件。
7. 能源守恒、SOC递推、边界、互斥和终端状态审计文件。
8. 新能源分源外送口径核验结论。

## 子问题 4：多区域算—储—电联合优化

### 模型思路

联合决定任务迁移、开工时刻、新能源分配、储能和购售电。采用固定窗口滚动联合MILP，通过预声明ε网格生成Pareto方案。

### 模型建立

联合模型同时满足式(2)–(4)、式(17)–(20)、式(36)–(48)。

服务质量定义为

$$
Q_{\mathrm{service}}
=
\sum_{j\in J_{\mathrm{def}}}\widetilde w_jQ_j.
\tag{53}
$$

四个初始权重固定为

$$
w_1=w_2=w_3=w_4=\frac14.
\tag{54}
$$

分量为

$$
Q_{\mathrm{RT}}
=
\frac{\#\{i\in RT:s_i=a_i\}}{\#RT},
\tag{55}
$$

$$
Q_{\mathrm{SLA}}
=
\frac{\#\{i:\ell_{o_ir_i}\le\ell_i^{max}\}}{\#\mathcal I},
\tag{56}
$$

$$
Q_{\mathrm{deadline}}
=
\frac{\#\{i:s_i+d_i/60\le f_i^{max}\}}{\#\mathcal I},
\tag{57}
$$

$$
Q_{\mathrm{wait}}
=
1-
\frac{\sum_{i\notin RT}(s_i-a_i)}
{\sum_{i\notin RT}(f_i^{max}-a_i-d_i/60)}.
\tag{58}
$$

仅将分母为正的分量纳入 \(J_{\mathrm{def}}\)。删除无定义分量后按确定性规则

$$
\widetilde w_j
=
\frac{w_j}{\sum_{h\in J_{\mathrm{def}}}w_h}.
\tag{59}
$$

若 \(J_{\mathrm{def}}=\varnothing\)，服务质量标记“不可计算”，对应场景不参与含该指标的Pareto排序。

联合ε约束模型为

$$
\min C_{\mathrm{op}},
\tag{60}
$$

$$
E_{\mathrm{CO2}}\le\varepsilon_C,\quad
L_{\mathrm{net}}\le\varepsilon_L,\quad
Q_{\mathrm{service}}\ge\varepsilon_Q,
\tag{61}
$$

$$
U_{\mathrm{RE}}\ge\varepsilon_U,\qquad
P_r^{peak}\le\varepsilon_{P,r}.
\tag{62}
$$

对Pareto方案 \(m\)：

$$
\bar z_{jm}
=
\frac{z_{jm}-z_j^{ideal}}
{z_j^{nadir}-z_j^{ideal}}.
\tag{63}
$$

仅将 \(z_j^{nadir}>z_j^{ideal}\) 的指标纳入 \(J_{\mathrm{disc}}\)。其理想点距离权重在求解前固定为等权：

$$
w_j^{P}=\frac1{|J_{\mathrm{disc}}|}.
\tag{64}
$$

折中方案为

$$
m^*
=
\arg\min_m
\sqrt{\sum_{j\in J_{\mathrm{disc}}}
w_j^{P}\bar z_{jm}^2}.
\tag{65}
$$

若 \(J_{\mathrm{disc}}=\varnothing\)，所有候选在所选指标上无区分度，按成本、碳排放、时延的固定词典序选择，不计算虚假的归一化距离。

### 情景模型

碳约束采用

$$
E_{\mathrm{CO2}}\le(1-\rho_C)E^0,
\qquad
\rho_C\in\{0,0.1,0.2,0.3\},
\tag{66}
$$

其中 \(E^0\) 是原始输入、无额外碳约束的可行基准排放；若基准不可行则停止情景分析。

电价情景为

$$
c_{rt}^{buy,sc}
=
\bar c_r+
\delta_P(c_{rt}^{buy}-\bar c_r),
\qquad
\delta_P\in\{0.75,1,1.25\},
\tag{67}
$$

其中

$$
\bar c_r=\frac1{2407}\sum_{t=0}^{2406}c_{rt}^{buy}.
\tag{68}
$$

新能源整体水平情景为

$$
R_{rt}^{av,level}
=
\max(0,\delta_RR_{rt}^{av}),
\qquad
\delta_R\in\{0.8,1,1.2\}.
\tag{69}
$$

波动增强情景统一为

$$
R_{rt}^{av,vol}
=
\max\left(0,R_{rt}^{av}+\sigma_{sc}\xi_{rt}\right),
\tag{70}
$$

其中 \(\xi_{rt}\) 使用随机种子2026一次生成，并在所有方案间复用；各区域序列标准化为样本均值0、样本方差1。幅度固定为

$$
\sigma_{sc}
=
0.1\,
\operatorname{mean}\{R_{rt}^{av}:R_{rt}^{av}>0\}.
\tag{71}
$$

若某区域无正新能源样本，则 \(\sigma_{sc}=0\)，该区域波动情景与基准一致并明确标注，而不输出NaN。

### 求解方法

1. 剔除违反时延、到达、截止和2406边界的候选。
2. 求各单目标参照解，按式(34)生成有限ε网格。
3. 固定使用 \(H=168\) 小时滚动窗口，传递运行任务占用及绝对SOC。
4. 拼接后执行全时域硬约束审计；失败则结构化停止，不临时扩大窗口。
5. 按式(53)–(65)生成非支配方案并选择折中方案。
6. 按式(66)–(71)独立重求各情景。
7. 全部子问题共享 \(B_{\mathrm{total}}=300\) s；以单调时钟记录耗时，统一搜索截止为 \(D_{\mathrm{search}}=t_{\mathrm{start}}+285\) s，末15秒用于文件输出和终检。候选启动前检查同一截止，未完整完成的候选丢弃。

### 可观测性

联合策略无真实最优标签。任务、等待、时延、负荷、能源流、SOC、成本和碳排放均可复算。验证采用硬约束、状态衔接、守恒残差、最优间隙、Pareto非支配性及情景单因素一致性。

### 必须回答的输出

1. 折中方案逐任务执行区域、开工、完成、等待和迁移时延。
2. 各区域逐时AI IT、设施负荷、新能源分配、储能、购售电和SOC。
3. 成本、碳排放、网络时延、服务质量、新能源利用率及区域峰值净购电。
4. 完整Pareto表、非支配关系和理想点折中方案。
5. 不同碳约束下的指标、迁移、储能循环及可行性变化。
6. 不同峰谷价差和售电价格机制下的策略变化。
7. 新能源上升、下降和波动增强情景变化。
8. 每个情景相对统一基准的绝对变化和相对变化率。
9. 各任务类型迁移数、迁移GPU-hour、等待和时延。
10. 各区域峰值净购电、爬坡量和等效循环量。
11. 滚动窗口衔接审计、求解状态和最优间隙。
12. Pareto图、负荷与SOC曲线、迁移流向图和情景比较图文件。

## 统一结果审计

任务约束审计包括

$$
\sum_{r,s}x_{irs}=1,\quad
i\in RT\Rightarrow s_i=a_i,
\tag{72}
$$

$$
a_i\le s_i,\qquad
s_i+d_i/60\le\min(f_i^{max},2406),
\tag{73}
$$

$$
\ell_{o_ir_i}\le\ell_i^{max}.
\tag{74}
$$

问题二能源守恒残差为

$$
e_{\max}^{q2}
=
\max_{r,t}
\left|
G_{rt}^{buy}+R_{rt}^{av}
-L_{rt}^{F}-G_{rt}^{sell}-R_{rt}^{curt}
\right|.
\tag{75}
$$

问题三、四能源守恒残差为

$$
e_{\max}^{energy}
=
\max_{r,t}
\left|
G_{rt}^{buy}+R_{rt}^{av}+D_{rt}
-L_{rt}^{F}-C_{rt}-G_{rt}^{sell}-R_{rt}^{curt}
\right|.
\tag{76}
$$

SOC递推残差为

$$
e_{\max}^{SOC}
=
\max_{r,t}
\left|
S_{rt}-S_{r,t-1}
-\eta_r^cC_{rt}\Delta t
+\frac{D_{rt}\Delta t}{\eta_r^d}
\right|.
\tag{77}
$$

正式结果同时报告式(72)–(77)、最大GPU/功率/SOC违约、2406小时执行任务数、未完成任务数、求解状态和最优间隙。限时但完整可行的结果仅标为“限时可行解”。

## 局限性与升级路线

1. 任务、电价、碳强度和新能源按确定值处理；取得概率预测后可升级为固定情景集随机优化。
2. 网络只使用题面单向时延矩阵，不建立带宽、迁移数据量、传输能耗、费用或线路潮流。
3. PUE和单位GPU功率严格使用附件映射，结论限定于相同设备及数据口径。
4. 预测测试集不用于调参。
5. 外部搜索未执行，未解决的调研主题不作为参数或验证依据。
6. 若真实附件产生空候选集、基准不可行、滚动拼接失败或无完整可行解，在相应步骤结构化停止，不通过放宽硬约束制造结果。

## Verifier 修复核对表

| Block issue | 修复位置 | 可计算性与有限输出保证 |
|---|---|---|
| 问题二新能源外送被重复计入负荷平衡 | 式(25)–(29) | 外送只在新能源分源中扣除；负荷平衡式(26)不含售电，避免额外购电支撑外送；式(75)可直接复算守恒残差。 |
| 问题一未计入2376小时前已开工任务占用 | 式(15)–(20) | 用完整前序基础调度计算固定GPU与AI IT占用，并加入末端GPU、IT和设施功率约束；空延续集合自然给出0。 |
| \(U^{\max}\) 未与逐时利用率绑定 | 式(22)–(24) | 对每个区域和末端小时设置显式线性上界，第三层词典序目标因此具有确定含义；式(23)明确百分数输出。 |
| 问题二结构化方程缺少外送、弃电及分源守恒 | 式(25)–(28)及 `equations.json` q2 | 明确列出 \(R^{sell},R^{curt},G^{sell}\) 的变量、守恒、等式和上下界，Coder可直接实现全部必答能源流。 |
| 新能源波动公式不一致 | 式(69)–(71) | 整体水平与波动增强分成两个明确情景；正文与结构化模型统一采用 \(R^{av}+\sigma\xi\)，并固定种子、标准化和零正样本分支。 |
| 多目标权重未固定 | 式(54)、(59)、(64)–(65) | 服务质量初始等权；无定义分量按确定性规则重归一；有效Pareto指标等权，零区间指标删除，避免零分母。 |
| ε网格未固定 | 式(34) | 单目标参照区间上固定使用五个锚点；退化区间固定为唯一值并删除该维度。 |
| 滚动窗口失败后可能无界扩大 | 各子问题求解方法及 \(H=168\) | 窗口长度在求解前固定；拼接失败结构化停止，不追加无界窗口，并受300秒共享预算约束。 |