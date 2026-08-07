# 数学模型

## 符号说明

| 符号 | 含义 | 类型 | 取值范围、单位与来源 |
|------|------|------|----------------------|
| \(i,r,k,t,s\) | 任务、区域、类型、小时、开工时刻索引 | 索引 | \(r\in R,\ t=0,\ldots,2406\)；题面直接给定 |
| \(\Delta t\) | 单个离散时段长度 | 固定参数 | \(\Delta t=1\mathrm h\)，题面直接给定 |
| \(I,I_R,I_E\) | 全任务、实时任务、弹性任务集合 | 集合 | \(I_E=\{i:k_i\in\{\mathrm{BatchInference},\mathrm{AITraining}\}\}\) |
| \(x_{irs}\) | 任务 \(i\) 在区域 \(r\)、时刻 \(s\) 开工 | 二元决策变量 | \(\{0,1\}\) |
| \(\omega_{it}(s)\) | 任务从 \(s\) 开工后与时段 \([t,t+\Delta t)\) 的重叠时长 | 派生参数 | \([0,\Delta t]\)，h |
| \(\phi_{it}(s)\) | 任务在时段 \(t\) 内的占用比例 | 派生参数 | \(\omega_{it}(s)/\Delta t\in[0,1]\)，无量纲 |
| \(g_i,d_i,a_i,f_i\) | GPU需求、分钟时长、到达时刻和最晚完成时点 | 附件参数 | GPU、min、h、h |
| \(o_i,k_i,L_i^{max}\) | 来源区域、任务类型、最大允许网络时延 | 附件参数 | 无、无、ms |
| \(G_r\) | 区域可调度GPU容量 | 附件参数 | 等效GPU单元 |
| \(p_k\) | 单位等效GPU的任务IT功率 | 附件参数 | MW/等效GPU单元 |
| \(P_{rt}^{AI},P_{rt}^{IT},P_{rt}^{F}\) | 时段平均AI功率、总IT功率和设施负荷 | 派生变量 | MW |
| \(N_{rt},B_{rt}\) | 非AI IT负荷、问题三给定基线AI IT负荷 | 附件参数 | MW |
| \(G_{rt},E_{rt}^{sell}\) | 电网购电、外送功率 | 决策变量 | MW |
| \(U_{rt}^{RE},C_{rt}^{RE},K_{rt}\) | 新能源直接利用、新能源充电、弃电 | 决策变量 | MW |
| \(C_{rt}^{G},D_{rt}\) | 电网充电、储能放电 | 决策变量 | MW |
| \(S_{rt}\) | 小时 \(t\) 运行后的SOC | 状态变量 | MWh |
| \(S_r^0,S_r^{min},S_r^{cap}\) | 初始SOC、安全下限、额定容量 | 附件参数 | MWh |
| \(S_r^{max}\) | 优化中的SOC上限 | 附件映射 | \(S_r^{max}=S_r^{cap}\)，MWh |
| \(I_r^{max}\) | 最大购电功率 | 附件参数 | \(\mathrm{MaxGridImport\_MW}_r\)，MW |
| \(X_r^{grid},X_r^{sell}\) | 区域电网外送上限、储能表外送上限 | 附件参数 | MW |
| \(E_r^{max}\) | 实际生效外送上限 | 派生参数 | \(\min(X_r^{grid},X_r^{sell})\)，MW |
| \(M_{rt}\) | 净购电功率 | 派生变量 | \(G_{rt}-E_{rt}^{sell}\)，MW |
| \(P_r^{peak}\) | 区域峰值正净购电 | 辅助变量 | MW |
| \(q_{rt}\) | 净购电绝对变化的线性上界 | 辅助变量 | MW |
| \(V_r^{model}\) | MILP内绝对爬坡量上界 | 辅助指标 | MW |
| \(V_r^{report}\) | 从最终净购电轨迹直接复算的绝对爬坡量 | 正式指标 | MW |
| \(C_{op},E_{CO2},L_{net},U_{RE}\) | 成本、碳排放、平均网络时延、新能源利用率 | 目标或指标 | 元、tCO2、ms、无量纲 |
| \(Q_F,Q_R,Q_L,W,Q_{service}\) | 按期完成率、实时即时开工率、SLA满足率、等待惩罚、服务质量 | 指标 | \([0,1]\) |
| \(Throughput_r,EFC_r\) | 储能总吞吐能量、等效循环次数 | 指标 | MWh、次 |
| \(\varepsilon_C,\varepsilon_L,\varepsilon_U,\varepsilon_{P,r},\varepsilon_{V,r},\varepsilon_Q\) | 全时域ε约束阈值 | 参数 | tCO2、ms、无量纲、MW、MW、无量纲 |
| \(b_w,H,\Delta\) | 第 \(w\) 个窗口起点、详细窗口长度和推进步长 | 算法量 | h；\(H,\Delta\) 在代码阶段固定并写入同组结果元数据 |
| \(C_w^{past},E_w^{past},L_w^{past},Q_w^{past}\) | 窗口开始前已承诺前缀的成本、碳、时延总和、新能源利用能量 | 累计状态 | 元、tCO2、ms、MWh |
| \(C_w^{tail},E_w^{tail},L_w^{tail},Q_w^{tail}\) | 当前候选详细窗口及终端延续部分的对应总量 | 派生量 | 元、tCO2、ms、MWh |
| \(\tau\) | 求解及残差检查容差 | 数值参数 | 代码阶段固定，同组模型统一使用 |
| \(B_{total},T_{tail},D_{search}\) | 共享墙钟、尾部预留和共同搜索截止 | 运行合同 | \(300\mathrm s,15\mathrm s,t_{start}+285\mathrm s\) |

几何量不适用于本题；无容器、尺寸链、坐标原点或观测位置需要确认。设备容量、网络和能源参数均由题面附件直接给定，不从图示推导。

统一定义重叠时长和时段占用比例：

$$
\omega_{it}(s)=
\max\left\{0,\min(t+\Delta t,s+d_i/60)-\max(t,s)\right\},
\qquad \Delta t=1\mathrm h,
\tag{1}
$$

$$
\phi_{it}(s)=\frac{\omega_{it}(s)}{\Delta t}\in[0,1].
\tag{2}
$$

\(\omega\) 用于计算GPU-hour和能量，\(\phi\) 用于计算时段平均GPU占用和平均功率。任务不可抢占；任务可占用第2405小时，但必须满足 \(s+d_i/60\le2406\)，不得占用第2406小时。

所有比例和相对变化采用有限输出规则：

$$
\operatorname{Ratio}(A,B)=
\begin{cases}
A/B,&B>0,\\
\mathrm{null},&B=0,
\end{cases}
\quad
\operatorname{status}=
\begin{cases}
\mathrm{available},&B>0,\\
\mathrm{unavailable},&B=0,
\end{cases}
\tag{3}
$$

$$
\operatorname{RelChange}(Y,Y^0)=
\begin{cases}
100(Y-Y^0)/|Y^0|\%,&Y^0\ne0,\\
\mathrm{null},&Y^0=0.
\end{cases}
\tag{4}
$$

相对变化不可用时仍报告绝对变化 \(Y-Y^0\)，且该相对指标不参与情景排序，不输出 `NaN`、`Inf` 或任意替代常数。

## 子问题 1：需求预测与最后24小时基础调度

### 模型思路

保留现役 `q1_enhanced`：正则化时序回归负责预测，MILP负责实际任务调度；`q1_baseline` 为季节性朴素预测基准。增强预测若在验证集MAE和WAPE上均不优于基线，则采用基线。调度没有通过全部硬约束的整数可行解时，结构化报告不可行。

预测标签由实际任务聚合得到，真实可观测。调度不存在真实“最优方案”标签，不使用分类准确率验证。

### 模型建立

按区域、任务类型统计逐小时到达GPU需求和实际运行GPU-hour：

$$
D_{rkt}=\sum_{i:o_i=r,\ k_i=k,\ a_i=t}g_i,
\tag{5}
$$

$$
H_{rkt}=
\sum_{i:o_i=r,\ k_i=k}
g_i\omega_{it}(a_i).
\tag{6}
$$

式(6)显式加入 \(o_i=r\)，避免不同区域错误地共享同一类型GPU-hour统计。其单位为GPU·h。

回归特征包含 \(1,24,168\) 小时滞后、滚动均值、小时和星期周期编码。对每个 \((r,k)\)：

$$
\widehat{\boldsymbol\beta}_{rk}
=\arg\min_{\boldsymbol\beta}
\sum_{t\in\mathcal T_{tr}}
(D_{rkt}-\boldsymbol z_t^\top\boldsymbol\beta)^2
+\lambda\|\boldsymbol\beta\|_2^2,
\qquad
\widehat D_{rkt}=\max(0,\boldsymbol z_t^\top\widehat{\boldsymbol\beta}_{rk}).
\tag{7}
$$

训练区间为0–2351，验证区间为2352–2375。选定特征与 \(\lambda\) 后用0–2375重新训练，对2376–2399进行一次24步递归预测；测试区间内需要短滞后时使用此前预测值，不使用测试真实标签。

$$
MAE=\frac1n\sum|D-\widehat D|,
\qquad
RMSE=\sqrt{\frac1n\sum(D-\widehat D)^2},
\tag{8}
$$

$$
WAPE=\operatorname{Ratio}
\left(\sum|D-\widehat D|,\sum D\right).
\tag{9}
$$

若 \(\sum D=0\)，WAPE输出 `null` 和 `unavailable`，仍报告MAE、RMSE和绝对误差总量。

相关系数仅在 \(n\ge2\) 且两序列样本方差均为正时计算：

$$
\rho_{XY}=
\frac{\sum_j(X_j-\bar X)(Y_j-\bar Y)}
{\sqrt{\sum_j(X_j-\bar X)^2\sum_j(Y_j-\bar Y)^2}}.
\tag{10}
$$

否则输出 `correlation=null, status=unavailable`，改报均值、标准差、绝对差和周期分组统计。

最后24小时基础调度使用实际到达任务。合法候选集合为：

$$
\mathcal F_i=
\left\{(r,s):
s\ge a_i,\
s+d_i/60\le\min(f_i,2406),\
\ell_{o_ir}\le L_i^{max}
\right\},
\tag{11}
$$

实时任务进一步要求 \(s=a_i\)。任务唯一执行：

$$
\sum_{(r,s)\in\mathcal F_i}x_{irs}=1.
\tag{12}
$$

时段平均GPU占用为：

$$
L_{rt}^{GPU}
=\sum_{i,s}g_i\phi_{it}(s)x_{irs}
\le G_r.
\tag{13}
$$

时段平均AI IT功率为：

$$
P_{rt}^{AI}
=\sum_{i,s}g_ip_{k_i}\phi_{it}(s)x_{irs}.
\tag{14}
$$

因此：

$$
P_{rt}^{IT}=N_{rt}+P_{rt}^{AI}\le P_r^{IT,max},
\qquad
PUE_rP_{rt}^{IT}\le P_r^{F,max}.
\tag{15}
$$

令 \(\bar L_{rt}^{GPU}\) 为求解前由区域容量比例和该小时总GPU占用唯一计算的负载均衡目标：

$$
u_{rt}\ge L_{rt}^{GPU}-\bar L_{rt}^{GPU},
\qquad
u_{rt}\ge\bar L_{rt}^{GPU}-L_{rt}^{GPU},
\qquad u_{rt}\ge0.
\tag{16}
$$

目标函数为：

$$
\min\
\alpha\sum_{i,r,s}(s-a_i)x_{irs}
+\beta\sum_{r,t}u_{rt}.
\tag{17}
$$

### 求解方法

先完成预测结构比较，再生成满足式(11)–(15)的启发式热启动并求解MILP。只有求解器返回整数可行解且全部约束残差不超过 \(\tau\) 时才输出调度结果；仅达到时间上限但没有可行解时结构化停止。

### 必须回答的输出

1. 区域—任务类型统计表及周期、自相关、相关性分析。
2. 2376–2399小时逐组和总体MAE、RMSE、WAPE及状态。
3. 实际到达任务的 `TaskID、SourceRegion、ExecutionRegion、StartTime、FinishTime、TaskType、GPU_Demand` 调度表。
4. 覆盖2376–2405的最后24小时任务甘特图，明确收尾任务。
5. 各区域逐小时平均GPU占用、利用率及最大容量裕度。
6. 任务唯一执行、即时开工、时延、截止、GPU/IT/设施容量和“不占用2406小时”的验证文件。

## 子问题 2：碳感知任务调度

### 模型思路

保留 `q2_enhanced`，以滚动时域ε-约束MILP生成Pareto方案；`q2_baseline` 提供成本参照解。滚动窗口除固定已经执行的决定外，还必须带有覆盖全部剩余任务的终端延续方案，并对碳、平均时延和新能源利用率实行全时域累计记账。局部窗口可行但不存在全局可行延续的候选不得提交。

### 模型建立

任务和容量约束沿用式(11)–(15)，输入改为0–2399全部实际任务。设施负荷为：

$$
P_{rt}^{F}=PUE_r\left(
N_{rt}+\sum_{i,s}g_ip_{k_i}\phi_{it}(s)x_{irs}
\right).
\tag{18}
$$

问题二不含储能：

$$
U_{rt}^{RE}+E_{rt}^{sell}+K_{rt}=A_{rt}^{RE},
\tag{19}
$$

$$
G_{rt}+U_{rt}^{RE}=P_{rt}^{F},
\tag{20}
$$

$$
0\le G_{rt}\le I_r^{max},
\qquad
0\le E_{rt}^{sell}\le E_r^{max}.
\tag{21}
$$

购售电分源并存规则必须由附件字段说明确认。若附件明确允许“电网购电供负荷与新能源富余外送”同时发生，则保留式(19)–(21)；若不能确认，代码阶段结构化停止并输出 `energy_source_accounting_unconfirmed`，不得仅依赖价格关系排除虚假套利。

功率乘以 \(\Delta t\) 后形成能量、成本和碳排放：

$$
C_{op}=\sum_{r,t}
(c_{rt}G_{rt}-c_{rt}^{sell}E_{rt}^{sell})\Delta t,
\tag{22}
$$

$$
E_{CO2}=\sum_{r,t}\kappa_{rt}G_{rt}\Delta t,
\tag{23}
$$

$$
L_{net}=\frac1{|I|}
\sum_{i,r,s}\ell_{o_ir}x_{irs},
\qquad |I|>0.
\tag{24}
$$

若 \(|I|=0\)，平均时延输出 `null, status=not_applicable`，且不施加 \(\varepsilon_L\)。

新能源利用能量及其分母为：

$$
Q_{RE}=\sum_{r,t}
(U_{rt}^{RE}+E_{rt}^{sell})\Delta t,
\qquad
A_{RE}^{tot}=\sum_{r,t}A_{rt}^{RE}\Delta t.
\tag{25}
$$

$$
U_{RE}=
\begin{cases}
Q_{RE}/A_{RE}^{tot},&A_{RE}^{tot}>0,\\
\mathrm{null},&A_{RE}^{tot}=0.
\end{cases}
\tag{26}
$$

主模型为：

$$
\min C_{op}
\tag{27}
$$

$$
E_{CO2}\le\varepsilon_C,
\qquad
L_{net}\le\varepsilon_L\quad(|I|>0),
\qquad
U_{RE}\ge\varepsilon_U\quad(A_{RE}^{tot}>0).
\tag{28}
$$

#### 滚动承诺与全局预算闭环

窗口 \(w\) 的起点为 \(b_w\)。此前已经提交的任务集合记为 \(I_w^{past}\)。若任务 \(i\) 已确定在 \((r_i^*,s_i^*)\) 开工，则：

$$
x_{ir_i^*s_i^*}=1,
\qquad
x_{irs}=0\quad
\forall(r,s)\ne(r_i^*,s_i^*).
\tag{29}
$$

其后续占用固定为：

$$
L_{irt}^{committed}
=g_i\phi_{it}(s_i^*),
\qquad
P_{irt}^{committed}
=g_ip_{k_i}\phi_{it}(s_i^*).
\tag{30}
$$

窗口开始前已承诺前缀的累计量由已提交轨迹直接计算：

$$
C_w^{past}
=\sum_{(r,t)\in\mathcal P_w}
(c_{rt}G_{rt}-c_{rt}^{sell}E_{rt}^{sell})\Delta t,
\tag{31}
$$

$$
E_w^{past}
=\sum_{(r,t)\in\mathcal P_w}
\kappa_{rt}G_{rt}\Delta t,
\tag{32}
$$

$$
L_w^{past}
=\sum_{i\in I_w^{past}}\ell_{o_ir_i^*},
\qquad
Q_w^{past}
=\sum_{(r,t)\in\mathcal P_w}
(U_{rt}^{RE}+E_{rt}^{sell})\Delta t,
\tag{33}
$$

其中 \(\mathcal P_w=\{(r,t):t<b_w\}\)。

每次滚动求解除详细优化区间 \([b_w,b_w+H)\) 外，还设置终端延续变量，覆盖所有尚未完成任务从详细窗口末端至第2405小时的剩余合法候选。详细窗口与终端延续共同满足式(11)–(21)，并形成：

$$
C_w^{tail},\ E_w^{tail},\ L_w^{tail},\ Q_w^{tail},
\tag{34}
$$

其计算式分别与式(22)、式(23)、网络时延总和及式(25)相同，但只对尚未承诺部分求和。全局预算约束为：

$$
E_w^{past}+E_w^{tail}\le\varepsilon_C,
\tag{35}
$$

$$
L_w^{past}+L_w^{tail}\le |I|\varepsilon_L
\qquad(|I|>0),
\tag{36}
$$

$$
Q_w^{past}+Q_w^{tail}
\ge\varepsilon_UA_{RE}^{tot}
\qquad(A_{RE}^{tot}>0).
\tag{37}
$$

窗口末可调度性要求存在至少一个终端延续方案，使所有未完成任务均有唯一合法候选，并在每个剩余时段满足GPU、IT功率、设施功率和能源边界：

$$
\exists\ x^{tail},G^{tail},U^{RE,tail},E^{sell,tail},K^{tail}
\quad\text{s.t. 式(11)–(21)、(35)–(37)成立}.
\tag{38}
$$

若式(38)不可行，本窗口候选不得提交。每次仅固定前 \(\Delta\) 小时内实际开工的决定；终端延续仅作可行性证书，下一窗口重新优化。最终拼接后必须从完整轨迹重新计算式(22)–(26)和全部残差；任一全局ε约束超过 \(\tau\) 时，方案作废。

### 求解方法

先分别求成本、碳、时延和新能源单目标参照值，再生成固定ε网格。每个比较组固定相同的 \(H,\Delta,\tau\)，并写入元数据。窗口间传递正式承诺、累计指标和绝对能源状态。只有具有整数可行解、终端延续可行且最终全量复算通过的结果可以进入Pareto集合。

### 必须回答的输出

1. 全任务执行区域、开工与完成时刻的调度策略文件。
2. 总成本、碳排放、平均及高分位时延、新能源利用率或不可用状态。
3. 相对基础调度的绝对变化与按式(4)计算的变化率。
4. Pareto前沿及选定折中方案。
5. 各任务类型的迁移量、等待时间和区域负荷。
6. 全部任务、容量、功率、能源、新能源守恒、全局预算和窗口延续残差报告。

## 子问题 3：固定负荷储能协同优化

### 模型思路

保留 `q3_enhanced`。问题三固定任务调度和IT负荷，仅优化储能、购售电及新能源分配。二元状态禁止同时充放电。所有储能状态变化和能量指标显式乘以 \(\Delta t\)。

### 模型建立

固定设施负荷：

$$
P_{rt}^{F}=PUE_r(B_{rt}+N_{rt}).
\tag{39}
$$

能源分流和平衡为：

$$
U_{rt}^{RE}+C_{rt}^{RE}
+E_{rt}^{sell}+K_{rt}=A_{rt}^{RE},
\tag{40}
$$

$$
G_{rt}+U_{rt}^{RE}+D_{rt}
=P_{rt}^{F}+C_{rt}^{G}.
\tag{41}
$$

总充电功率为 \(C_{rt}=C_{rt}^{RE}+C_{rt}^{G}\)。SOC递推为：

$$
S_{r,-1}=S_r^0,
\tag{42}
$$

$$
S_{rt}=S_{r,t-1}
+\left[
\eta_r^c(C_{rt}^{RE}+C_{rt}^{G})
-\frac{D_{rt}}{\eta_r^d}
\right]\Delta t.
\tag{43}
$$

SOC上限映射为：

$$
S_r^{max}=S_r^{cap}
=\mathrm{StorageCapacity\_MWh}_r.
\tag{44}
$$

边界为：

$$
S_r^{min}\le S_{rt}\le S_r^{max},
\qquad
S_{r,2406}\ge S_r^0,
\tag{45}
$$

$$
0\le C_{rt}^{RE}+C_{rt}^{G}\le C_r^{max}z_{rt},
\tag{46}
$$

$$
0\le D_{rt}\le D_r^{max}(1-z_{rt}),
\qquad z_{rt}\in\{0,1\}.
\tag{47}
$$

购售电边界为：

$$
0\le G_{rt}\le I_r^{max},
\qquad
0\le E_{rt}^{sell}
\le E_r^{max}
=\min(X_r^{grid},X_r^{sell}).
\tag{48}
$$

购售电分源规则采用问题二的确认或结构化停止口径。

净购电和峰值定义为：

$$
M_{rt}=G_{rt}-E_{rt}^{sell},
\tag{49}
$$

$$
P_r^{peak}\ge M_{rt},
\qquad P_r^{peak}\ge0.
\tag{50}
$$

爬坡线性化变量满足：

$$
q_{rt}\ge M_{rt}-M_{r,t-1},
\qquad
q_{rt}\ge M_{r,t-1}-M_{rt},
\tag{51}
$$

$$
V_r^{model}=\sum_{t=1}^{2406}q_{rt}.
\tag{52}
$$

优化约束为：

$$
\min C_{op}
\tag{53}
$$

$$
E_{CO2}\le\varepsilon_C,
\qquad
P_r^{peak}\le\varepsilon_{P,r},
\qquad
V_r^{model}\le\varepsilon_{V,r}.
\tag{54}
$$

由于成本目标不保证 \(q_{rt}\) 自动取最小值，正式报告不得直接使用 \(V_r^{model}\)。求解后从最终净购电轨迹复算：

$$
V_r^{report}
=\sum_{t=1}^{2406}
|M_{rt}-M_{r,t-1}|.
\tag{55}
$$

并验证：

$$
V_r^{report}\le V_r^{model}+\tau,
\qquad
V_r^{report}\le\varepsilon_{V,r}+\tau.
\tag{56}
$$

若任一条件不成立，候选不进入正式结果。专门的最小爬坡参照模型以 \(\min\sum_{r,t}q_{rt}\) 为目标，此时 \(q_{rt}\) 在最优解中等于绝对差。

成本和碳排放为：

$$
C_{op}=\sum_{r,t}
(c_{rt}G_{rt}-c_{rt}^{sell}E_{rt}^{sell})\Delta t,
\tag{57}
$$

$$
E_{CO2}=\sum_{r,t}
\kappa_{rt}G_{rt}\Delta t.
\tag{58}
$$

新能源利用能量为：

$$
Q_{RE}^{(3)}
=\sum_{r,t}
(U_{rt}^{RE}+C_{rt}^{RE}+E_{rt}^{sell})\Delta t.
\tag{59}
$$

$$
U_{RE}=
\begin{cases}
\dfrac{Q_{RE}^{(3)}}
{\sum_{r,t}A_{rt}^{RE}\Delta t},
&\sum_{r,t}A_{rt}^{RE}\Delta t>0,\\
\mathrm{null},
&\sum_{r,t}A_{rt}^{RE}\Delta t=0.
\end{cases}
\tag{60}
$$

储能总吞吐能量和等效循环次数统一采用总吞吐量口径：

$$
Throughput_r=
\sum_{t=0}^{2406}
(C_{rt}^{RE}+C_{rt}^{G}+D_{rt})\Delta t,
\tag{61}
$$

$$
EFC_r=
\begin{cases}
\dfrac{Throughput_r}{2S_r^{cap}},
&S_r^{cap}>0,\\
\mathrm{null},
&S_r^{cap}=0.
\end{cases}
\tag{62}
$$

该定义以一次完整充放电的总吞吐能量 \(2S_r^{cap}\) 为一个等效循环，不再使用“仅放电能量除以两倍容量”的错误口径。容量为零时状态为 `unavailable`，仍报告吞吐量绝对值。

### 求解方法

分别求成本、碳、削峰和减小绝对爬坡方案。以附件基准轨迹和无储能反事实为对照，但不将附件基准SOC固定进优化模型。正式指标全部从最终轨迹复算。

### 必须回答的输出

1. 六区域0–2406小时充电、放电、购电、售电、新能源各去向及SOC策略文件。
2. 各区域初始SOC、终端SOC和边界裕度。
3. 储能前后成本、碳排放、峰值正净购电及 \(V_r^{report}\)。
4. 各指标绝对变化和按式(4)计算的相对变化率或不可用状态。
5. 同时充放电、购售电口径、能量平衡、SOC递推、购售电边界、终端条件和爬坡复算验证报告。
6. 式(61)的吞吐量和式(62)的EFC。

## 子问题 4：算—储—电联合多目标优化

### 模型思路

保留 `q4_enhanced`，由带正式承诺、全局预算记账和终端延续的滚动联合MILP实现。服务质量中的完成、实时即时开工和时延合规已是硬约束，不再把对应指示函数直接放入MILP，而是化简为关于等待惩罚 \(W\) 的线性约束。

### 模型建立

设施负荷为：

$$
P_{rt}^{F}=PUE_r\left(
N_{rt}+\sum_{i,s}g_ip_{k_i}\phi_{it}(s)x_{irs}
\right).
\tag{63}
$$

任务约束采用式(11)–(15)，滚动承诺、全局预算和终端延续采用式(29)–(38)，能源、SOC、购售电、峰值和爬坡约束采用式(40)–(56)。

对弹性任务定义最大可等待时间：

$$
h_i=\min(f_i,2406)-\frac{d_i}{60}-a_i,
\qquad i\in I_E.
\tag{64}
$$

若 \(h_i<0\)，任务不可行并结构化停止。若 \(h_i>0\)，直接由开工变量定义线性的归一化等待：

$$
w_i=
\sum_{(r,s)\in\mathcal F_i}
\frac{s-a_i}{h_i}x_{irs}.
\tag{65}
$$

若 \(h_i=0\)，唯一合法开工时刻必须为 \(s=a_i\)，并定义 \(w_i=0\)；若该候选不存在则模型不可行。由合法候选集合可得 \(0\le w_i\le1\)。

$$
W=
\begin{cases}
\dfrac1{|I_E|}\sum_{i\in I_E}w_i,&|I_E|>0,\\
0,&|I_E|=0.
\end{cases}
\tag{66}
$$

空弹性任务集合时标记 `status=not_applicable`，且 \(W\) 不用于区分方案。

正常非空可行实例已经通过硬约束保证：

$$
Q_F=1,\qquad Q_R=1,\qquad Q_L=1.
\tag{67}
$$

因此服务质量无需指示变量：

$$
Q_{service}
=\frac{Q_F+Q_R+Q_L+(1-W)}4
=1-\frac W4.
\tag{68}
$$

服务质量约束可直接线性化为：

$$
Q_{service}\ge\varepsilon_Q
\iff
W\le4(1-\varepsilon_Q).
\tag{69}
$$

当全任务集合为空时，\(Q_F,Q_R,Q_L\) 取1并标记 `not_applicable`，任务服务指标退出方案区分，不产生零分母。

联合主模型为：

$$
\min C_{op}
\tag{70}
$$

$$
E_{CO2}\le\varepsilon_C,
\qquad
L_{net}\le\varepsilon_L\quad(|I|>0),
\qquad
U_{RE}\ge\varepsilon_U\quad(A_{RE}^{tot}>0),
\tag{71}
$$

$$
W\le4(1-\varepsilon_Q),
\qquad
P_r^{peak}\le\varepsilon_{P,r}
\quad(\forall r).
\tag{72}
$$

滚动窗口同时携带：

- 已承诺任务及其后续GPU和功率占用；
- 已实现成本、碳、时延总和和新能源利用能量；
- 当前绝对SOC；
- 覆盖所有尚未完成任务和剩余能源时段的终端延续方案。

终端延续必须满足任务唯一执行、截止、2406禁占用、GPU/IT/设施容量、能源平衡、SOC、购售电边界以及式(35)–(37)的全局预算。不存在延续时，不提交当前窗口决定。

对非支配方案 \(m\)，仅使用同一可行域内理想值和最差值归一化：

$$
z_{jm}=
\frac{F_{jm}-F_j^{best}}
{F_j^{worst}-F_j^{best}}
\quad
\text{if }F_j^{worst}>F_j^{best}.
\tag{73}
$$

若分母为零，该指标标记 `no_discrimination` 并从距离中移除。剩余权重重新归一化：

$$
D_m=\sqrt{\sum_{j\in J_{valid}}w_jz_{jm}^2},
\qquad
w_j\ge0,\quad
\sum_{j\in J_{valid}}w_j=1.
\tag{74}
$$

问题四沿用式(61)–(62)的吞吐量和EFC定义。

情景保持单因素可比：

- 碳约束：无额外约束、分级减排、严格预算；
- 电价：原始价格、峰谷差扩大或缩小、售电价格变化；
- 新能源：基准、整体升降、波动增强，并保证 \(A_{rt}^{RE}\ge0\)。

### 求解方法

先剔除违反时延、到达、截止和2406边界的候选，再按式(29)–(38)滚动求解。每次只提交前 \(\Delta\) 小时内实际开工和能源动作；其余终端延续在下一窗口重算。

最终拼接方案必须重新计算：

$$
C_{op},E_{CO2},L_{net},U_{RE},Q_{service},
P_r^{peak},V_r^{report},Throughput_r,EFC_r,
\tag{75}
$$

并重新检查全部任务、容量、能源、SOC和全局ε约束。任一残差超过 \(\tau\) 时方案作废。

缩小实例与一次性整体MILP对照。正式结果标注为“证明最优”“限时可行”或“启发式可行”，并报告最优间隙；所有类别均须通过最终全量复算。

### 必须回答的输出

1. 联合任务调度、逐时能源流和SOC完整方案文件。
2. 成本、碳排放、时延、服务质量、新能源利用率及六区域峰值正净购电。
3. Pareto前沿、折中解、权重和式(73)–(74)的归一化口径。
4. 各碳约束、电价机制和新能源情景的绝对指标、相对变化或不可用状态。
5. 各情景任务迁移方向、等待时间、储能吞吐量、EFC及新能源去向。
6. 任务、网络、容量、功率、能源、新能源、SOC、终端状态、全局预算和窗口衔接验证文件。
7. 求解状态、运行时间、最优间隙及小规模整体MILP对照结果。

## 执行与验证合同

所有附件参数、预测误差、目标值和情景结果均由代码阶段读取真实附件后计算，不预填结果。

Coder单次执行共享墙钟为：

$$
B_{total}=300\mathrm s,\qquad
T_{tail}=15\mathrm s,\qquad
D_{search}=t_{start}+285\mathrm s.
\tag{76}
$$

标定、问题一、问题二固定参照与ε网格、问题三、问题四、指标复算和文件输出共用该预算。使用单调时钟记录实际耗时；每个候选启动前检查共同截止，已启动候选若不能在总截止前完成则中断并丢弃，不使用部分结果。

代码阶段必须固定并记录 \(H,\Delta,\tau\)，同一比较组不得改变。验证顺序为：

1. 读取附件并检查必需字段、单位、时间范围和候选集合。
2. 检查每个任务是否至少存在一个式(11)合法候选；失败则在进入优化前结构化停止。
3. 比较问题一增强预测与季节性朴素基线；按验证集MAE和可用WAPE选定唯一结构，再用0–2375重训。
4. 核验购售电分源字段说明；不能确认时在问题二能源模型前停止。
5. 求解各子问题；只有成功整数终点进入候选集合。
6. 对最终拼接方案全量复算式(22)–(26)、式(43)、式(49)、式(55)、式(57)–(62)及所有硬约束。
7. 任一残差超过 \(\tau\)、全局ε约束失败或终端延续不存在时，候选作废；不通过截断、全零指标或更换任意常数制造可行结果。

## 模型局限性

模型使用确定性任务时长、小时级候选开工和固定PUE，未描述任务时长误差、网络拥塞、线路潮流、传输能耗及储能退化成本；这些量缺少题面数据或被题面明确排除。调度没有真实最优标签，结论只能由机制约束、求解界、最终全量复算和情景一致性支持。

“同时购售电记录数”和“基准GPU利用率超过100%的记录数”在当前阶段均标记为 `pending_code_execution`。在附件读取程序完成复算前，不把“6030条”和“44条”写作已经验证的数据事实。正式容量约束始终使用 `Available_GPU`、最大IT功率和最大设施功率；购售电并存规则必须由附件字段说明确认。

## Verifier 修复核对表

| Block issue | 修复位置 | 可计算性与有限输出保证 |
|---|---|---|
| 式(4)区域—任务类型GPU-hour遗漏区域条件 | 式(5)–(6) | \(D_{rkt}\) 与 \(H_{rkt}\) 均显式加入 \(o_i=r\)，区域统计不再错误复用其他区域任务 |
| EFC用放电量除以两倍容量 | 式(61)–(62) | 统一采用总充放电吞吐能量除以 \(2S_r^{cap}\)；容量为零时输出 `null/unavailable` 和绝对吞吐量 |
| GPU占用、AI功率及能量量纲不一致 | 式(1)–(2)、(13)–(15)、(18)、(22)–(23)、(43)、(57)–(61)、(63) | 用无量纲占用比例 \(\phi=\omega/\Delta t\) 计算平均GPU和MW；用功率乘 \(\Delta t\) 计算MWh、成本、碳和SOC变化 |
| 滚动模型缺少全局ε预算和窗口末可调度性 | 式(29)–(38)，问题四式(71)–(72)及求解方法 | 显式累计已实现指标，剩余详细窗口与终端延续共同满足全局预算；不存在覆盖全部剩余任务的合法延续时禁止提交 |
| 服务质量指示函数未线性化 | 式(64)–(69) | 利用已有按期完成、实时即时开工和时延硬约束令 \(Q_F=Q_R=Q_L=1\)，将服务质量化为线性约束 \(W\le4(1-\varepsilon_Q)\) |
| 爬坡松弛变量可能不等于真实绝对变化 | 式(51)–(56) | MILP内保留上界约束，正式报告从最终轨迹直接复算 \(V_r^{report}\)，并同时检查模型上界和ε阈值 |
| 同时购售电和超容量具体记录数缺少执行证据 | 模型局限性、执行与验证合同 | 两项均改为 `pending_code_execution`；附件程序复算前不声称具体记录数已经得到验证 |