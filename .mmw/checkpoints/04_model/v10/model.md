# 数学模型

## 1. 符号说明

| 符号 | 含义 | 类型 | 取值范围 |
|------|------|------|----------|
| \(\mathcal R\) | 六个区域集合 | 题面直接给定参数 | RegionA–RegionF |
| \(\mathcal I\) | 实际到达任务集合 | 可观测参数集合 | 50000 个任务 |
| \(\mathcal K\) | 三类任务集合 | 题面直接给定参数 | 实时、批量、训练 |
| \(\mathcal T_A\) | 主到达时域 | 题面直接给定 | \(0,\ldots,2399\) |
| \(\mathcal T_C\) | 收尾时域 | 题面直接给定 | \(2400,\ldots,2405\) |
| \(2406\) | 仅作电力及储能终端结算的时点 | 题面直接给定 | 不执行任务 |
| \(a_i,d_i,f_i\) | 到达时刻、持续时间、最晚完成时点 | 可观测参数 | 附件读取 |
| \(g_i,k_i,o_i\) | GPU需求、任务类型、来源区域 | 可观测参数 | 附件读取 |
| \(\ell_{or},\ell_i^{\max}\) | 单向网络时延、任务时延上限 | 可观测参数 | ms |
| \(x_{irs}\) | 任务 \(i\) 在区域 \(r\)、时刻 \(s\) 开工 | 二元决策变量 | \(\{0,1\}\) |
| \(q_{it}(s)\) | 任务 \(i\) 在小时 \(t\) 的实际重叠比例 | 派生参数 | \([0,1]\) |
| \(G_r\) | 区域可调度GPU容量 | 可观测参数 | 正数 |
| \(p_k^{GPU}\) | 类型 \(k\) 单位GPU的IT功率 | 可观测参数 | MW/GPU |
| \(P_{rt}^{AI},P_{rt}^{nonAI}\) | AI与非AI IT负荷 | 派生变量/参数 | MW |
| \(PUE_r\) | 区域PUE | 可观测参数 | \(1.25\sim1.38\) |
| \(P_{rt}^{fac}\) | 设施侧总负荷 | 派生变量 | MW |
| \(A_{rt}^{RE}\) | 可用新能源 | 可观测参数 | 非负 |
| \(U_{rt}^{RE}\) | 直接消纳新能源 | 连续决策变量 | MW |
| \(P_{rt}^{RE,ch}\) | 新能源充电功率 | 连续决策变量 | MW |
| \(P_{rt}^{grid,ch}\) | 电网充电功率 | 连续决策变量 | MW |
| \(P_{rt}^{buy},P_{rt}^{sell}\) | 购电、外送功率 | 连续决策变量 | MW |
| \(P_{rt}^{dis},P_{rt}^{ch}\) | 放电、总充电功率 | 连续决策变量 | MW |
| \(E_{rt}\) | 小时 \(t\) 运行后的SOC | 状态变量 | MWh |
| \(P_{rt}^{curt}\) | 弃风弃光功率 | 连续决策变量 | MW |
| \(C_{\mathrm{op}}\) | 购电成本减售电收入 | 目标/指标 | 元 |
| \(E_{\mathrm{CO2}}\) | 累计购电碳排放 | 目标/指标 | tCO2 |
| \(L_{\mathrm{net}}\) | GPU-hour加权网络时延 | 目标/指标 | ms |
| \(U_{\mathrm{RE}}\) | 累计新能源利用率 | 目标/指标 | \([0,1]\) |
| \(Q_{\mathrm{service}}\) | 服务质量 | 评价指标 | \([0,1]\) |
| \(P_r^{peak}\) | 区域峰值净购电 | 辅助变量 | MW |
| \(V_r\) | 区域净购电绝对爬坡总量 | 指标 | MW |

本题不含需由图示推导的几何量，故“尺寸链、坐标原点、观测位置及空/满边界”不适用；全部空间关系仅由题面直接给定的区域集合和有向网络时延矩阵表达。

## 2. 统一边界与共享计算内核

令任务开工时刻为整数小时 \(s\)，持续时间换为小时：

$$
d_i=\frac{\mathrm{EstimatedDuration\_min}_i}{60}.
$$

任务在小时区间 \([t,t+1)\) 的实际重叠比例为

$$
q_{it}(s)=
\max\left\{0,\min(t+1,s+d_i)-\max(t,s)\right\}.
$$

这既保持任务连续、不可抢占，也避免把只覆盖部分小时的任务按完整一小时计量。候选集合定义为

$$
\Omega_i=
\left\{(r,s):
s\ge a_i,\quad s+d_i\le \min(f_i,2406),\quad
\ell_{o_i r}\le\ell_i^{\max}
\right\}.
$$

对实时任务进一步固定 \(s=a_i\)。若任一 \(\Omega_i=\varnothing\)，模型结构化报告“任务侧不可行”，不放松SLA、容量或终点约束。

任务形成的逐时负荷为

$$
P_{rt}^{AI}
=\sum_{i\in\mathcal I}\sum_{s:(r,s)\in\Omega_i}
g_i p_{k_i}^{GPU}q_{it}(s)x_{irs},
$$

$$
P_{rt}^{IT}=P_{rt}^{nonAI}+P_{rt}^{AI},\qquad
P_{rt}^{fac}=PUE_rP_{rt}^{IT}.
$$

GPU容量、IT功率和设施功率同时满足

$$
\sum_i\sum_s g_iq_{it}(s)x_{irs}\le G_r,
$$

$$
P_{rt}^{IT}\le P_r^{IT,\max},\qquad
P_{rt}^{fac}\le P_r^{fac,\max}.
$$

每个任务必须恰好执行一次：

$$
\sum_{(r,s)\in\Omega_i}x_{irs}=1,\qquad x_{irs}\in\{0,1\}.
$$

所有附件参数均由代码阶段从真实工作簿读取。预测模型系数、误差、最优目标值和调度结果此处均不预填。

---

## 子问题 1：GPU需求预测与末端基础调度

### 模型思路

先按区域—任务类型—小时构造可观测需求序列，再比较季节性朴素模型和带滞后特征的正则化回归。模型选择仅使用验证集；选择后用 \(0\sim2375\) 小时重新训练，\(2376\sim2399\) 小时只测试一次。

最后24小时基础调度不使用预测值，而使用实际到达任务。现役调度模型选用合同中的 `q1_enhanced`；`q1_baseline` 保留为预测参照、MILP热启动及限时后备方案。

### 统计模型

可选择逐小时到达GPU量

$$
D_{rkt}=\sum_{i:o_i=r,k_i=k,a_i=t}g_i
$$

或到达任务GPU-hour

$$
H_{rkt}=\sum_{i:o_i=r,k_i=k,a_i=t}g_id_i.
$$

正式预测目标须在代码开始前固定，不能依据测试表现切换。统计输出包括任务数、GPU总量、GPU-hour、均值、标准差、分位数、执行时长分布、峰值并发、小时和星期周期、自相关及区域相关性。

季节性基线为

$$
\widehat D_{rkt}^{(24)}=D_{rk,t-24},\qquad
\widehat D_{rkt}^{(168)}=D_{rk,t-168}.
$$

增强模型为非负截断的岭回归：

$$
\widehat D_{rkt}=
\max\left\{0,\beta_0+\boldsymbol\beta^\top
\mathbf z_{rkt}\right\},
$$

其中 \(\mathbf z_{rkt}\) 仅含预测时点以前可得的滞后 \(1,2,3,24,48,168\)、滚动均值、滚动标准差、小时及星期周期编码、区域和任务类型编码。参数通过

$$
\min_{\beta_0,\boldsymbol\beta}
\sum_{(r,k,t)\in\mathcal T_{\mathrm{train}}}
\left(D_{rkt}-\widehat D_{rkt}\right)^2
+\lambda\|\boldsymbol\beta\|_2^2
$$

估计。

评价指标为

$$
MAE=\frac1n\sum_j|D_j-\widehat D_j|,
$$

$$
RMSE=\sqrt{\frac1n\sum_j(D_j-\widehat D_j)^2},
$$

$$
WAPE=\frac{\sum_j|D_j-\widehat D_j|}
{\sum_j|D_j|}.
$$

若某诊断分组的真实需求总和为零，则该组WAPE标记“验证不可用”，改报MAE和有限预测率；总体WAPE仍按完整测试序列计算。

### 基础调度目标

在共享硬约束下，最小化等待时间与网络时延：

$$
\min
\sum_{i,r,s}
\left[
\omega_w(s-a_i)+\omega_\ell\ell_{o_i r}
\right]x_{irs}.
$$

为避免不同量纲随意相加，正式实现采用词典序：先最小化未完成任务数（其最优值必须为0），再最小化最大延迟，最后最小化总等待和总时延。

区域GPU利用率按实际重叠计算：

$$
Util_{rt}^{GPU}
=\frac{\sum_{i,s}g_iq_{it}(s)x_{irs}}{G_r}\times100\%.
$$

附件中44条超过100%的基准利用率仅作口径核验，不替代 \(G_r\) 硬约束。

### 求解方法与候选淘汰

按合同计划执行廉价pilot，但此模型阶段不宣称已经运行。只有增强预测同时在验证集WAPE或MAE上优于季节性基线，且最后24小时MILP在限时内产生完整可行解时，才采用 `q1_enhanced`。若预测无稳定改进则回退季节性模型；若MILP无可行解或超时，则启用 `q1_baseline` 的实时优先—最早截止—短任务优先启发式，但仅在其完成全部任务且无硬约束违约时交付。

### 可观测性与验证

预测真实标签可观测。最优调度标签不存在，因此不使用准确率或混淆矩阵；验证口径为任务唯一分配率、实时即时开工率、截止满足率、最大GPU/功率/时延违约、是否占用2406小时及求解器最优间隙。

### 必须回答的输出

1. 区域—任务类型统计表及主要时序图。
2. 训练、验证、重训和测试划分说明。
3. 季节性基线与现役模型的总体、分区域、分任务类型MAE、RMSE、WAPE。
4. 第2376–2399小时逐小时预测值和实际值。
5. 基于同期实际任务的任务级调度表：`TaskID`、来源区域、执行区域、实际开工时刻、完成时刻、任务类型、GPU需求和网络时延。
6. 跨越2399小时任务在2400–2405小时的结清方案，以及未结清任务数。
7. 最后24小时任务级甘特图。
8. 各区域2376–2405小时GPU利用率表和曲线。
9. 文件：`q1_statistics.xlsx`、`q1_forecast.xlsx`、`q1_schedule.xlsx`、`q1_gantt.png`、`q1_gpu_utilization.png`、`q1_validation.json`。

---

## 子问题 2：碳感知任务调度

### 模型思路

采用实际任务和实际逐时电力参数，联合优化任务区域与开工时段。现役候选为 `q2_enhanced`：滚动时域ε-约束MILP；`q2_baseline` 的成本最小化MILP用于确定成本参照点并在增强候选失败时回退。

问题二不优化储能；若要求与给定基准储能解耦，则令充放电为零。新能源直接供负荷、外送与弃电满足分源守恒：

$$
U_{rt}^{RE}+P_{rt}^{sell}+P_{rt}^{curt}=A_{rt}^{RE}.
$$

能源平衡为

$$
P_{rt}^{buy}+U_{rt}^{RE}
=P_{rt}^{fac}+P_{rt}^{sell}.
$$

这里 \(P^{sell}\) 仅代表新能源外送，故可以出现“电网购电供本地负荷，同时新能源外送”。数据中6030条同时购售电记录支持该分源解释，因此默认不设购售互斥；若工作簿备注明确二者为同一双向结算通道，再加入互斥变量。

### 目标与评价指标

运行成本：

$$
C_{\mathrm{op}}=
\sum_{r,t=0}^{2406}
\left(\pi_{rt}^{buy}P_{rt}^{buy}
-\pi_{rt}^{sell}P_{rt}^{sell}\right)\Delta t.
$$

碳排放：

$$
E_{\mathrm{CO2}}=
\sum_{r,t=0}^{2406}
c_{rt}P_{rt}^{buy}\Delta t.
$$

GPU-hour加权平均网络时延：

$$
L_{\mathrm{net}}=
\frac{\sum_{i,r,s}g_id_i\ell_{o_i r}x_{irs}}
{\sum_i g_id_i}.
$$

新能源利用率：

$$
U_{\mathrm{RE}}=
\frac{\sum_{r,t}(U_{rt}^{RE}+P_{rt}^{sell})\Delta t}
{\sum_{r,t}A_{rt}^{RE}\Delta t}.
$$

若累计可用新能源为零，则利用率标记“不可计算”，并改报累计利用量和弃电量，绝不输出NaN或无穷值。

以成本为主目标：

$$
\min C_{\mathrm{op}}
$$

并施加

$$
E_{\mathrm{CO2}}\le\epsilon_C,\qquad
L_{\mathrm{net}}\le\epsilon_L,\qquad
U_{\mathrm{RE}}\ge\epsilon_U.
$$

各ε阈值只从同一可行域内的单目标参照解构造。任务候选预筛不得删除任何满足到达、截止、时延及系统终点的组合。

### 滚动时域

在窗口 \(W_m=[b_m,e_m]\) 内优化尚未开工任务。已开工任务固定，并将其后续占用量

$$
R_{irt}^{(m)}
=\sum_{s<b_m}g_iq_{it}(s)x_{irs}
$$

带入窗口容量约束。窗口末端必须保留所有临近截止任务的可行开工组合；最终窗口覆盖至2406结算。

### 求解与淘汰条件

增强候选只有在宽松ε下可行、跨窗口无任务中断或重复、全部指标有限且Pareto点不被同批方案严格支配时启用。若失败，回退 `q2_baseline` 成本最小化MILP，并明确只交付单目标策略。pilot是后续代码计划，不写成已验证结果。

### 可观测性与验证

任务和电力输入可观测，但不存在已知最优迁移标签。代理验证包括任务完整性、硬约束残差、能源与新能源守恒残差、成本和碳排放复算差异、时延分布、利用率及求解间隙。

### 必须回答的输出

1. 每个任务的执行区域、开工及完成时刻。
2. 逐区域逐小时AI IT、总IT、设施负荷、新能源直接利用、购电、外送和弃电。
3. 系统成本、碳排放、平均及95分位网络时延、新能源利用率。
4. 相对基础调度的绝对变化与相对变化率。
5. 成本—碳—时延—新能源Pareto表和前沿图。
6. 按任务类型统计迁移数量、GPU-hour、平均等待和时延。
7. 文件：`q2_task_schedule.xlsx`、`q2_energy_dispatch.xlsx`、`q2_metrics.json`、`q2_pareto.csv`、`q2_pareto.png`、`q2_validation.json`。

---

## 子问题 3：固定负荷下的储能协同优化

### 模型思路

问题三严格固定任务负荷：

$$
P_{rt}^{fac}
=PUE_r\left(P_{rt}^{baseAI}+P_{rt}^{nonAI}\right).
$$

现役候选为 `q3_enhanced`，因为它能明确排除同时充放电，并线性表达峰值和波动。仅当连续LP的pilot证明全时域均无同时充放电、循环套利和异常同时交易时，才可简化为 `q3_baseline`。

### 能源分源与平衡

新能源守恒：

$$
U_{rt}^{RE}+P_{rt}^{RE,ch}
+P_{rt}^{sell}+P_{rt}^{curt}
=A_{rt}^{RE}.
$$

总充电功率：

$$
P_{rt}^{ch}=P_{rt}^{RE,ch}+P_{rt}^{grid,ch}.
$$

电力平衡：

$$
P_{rt}^{buy}+U_{rt}^{RE}+P_{rt}^{dis}
=P_{rt}^{fac}+P_{rt}^{grid,ch}+P_{rt}^{sell}.
$$

由于新能源充电已经在新能源守恒中从可用新能源分出，不能在右侧重复计入负荷。等价的附件总平衡式也可写为

$$
P_{rt}^{buy}+A_{rt}^{RE}+P_{rt}^{dis}
=P_{rt}^{fac}+P_{rt}^{ch}+P_{rt}^{sell}+P_{rt}^{curt}.
$$

两式必须在代码验收中相互核对。

### SOC动力学与物理约束

$$
E_{r,-1}=E_r^0,
$$

$$
E_{rt}=E_{r,t-1}
+\eta_r^cP_{rt}^{ch}\Delta t
-\frac{P_{rt}^{dis}\Delta t}{\eta_r^d},
\quad t=0,\ldots,2406,
$$

$$
E_r^{min}\le E_{rt}\le E_r^{max},
\qquad E_{r,2406}\ge E_r^0.
$$

引入 \(z_{rt}^{ch}\in\{0,1\}\)：

$$
0\le P_{rt}^{ch}\le P_r^{ch,\max}z_{rt}^{ch},
$$

$$
0\le P_{rt}^{dis}\le
P_r^{dis,\max}(1-z_{rt}^{ch}).
$$

购售电和外送满足附件硬边界。若业务核验认定购电供负荷与新能源外送允许并存，则不添加购售互斥；否则引入交易方向二元变量。

### 峰值和波动

定义净购电

$$
N_{rt}=P_{rt}^{buy}-P_{rt}^{sell}.
$$

峰值线性化为

$$
P_r^{peak}\ge N_{rt},\qquad\forall t.
$$

引入 \(v_{rt}\ge0\)：

$$
v_{rt}\ge N_{rt}-N_{r,t-1},
$$

$$
v_{rt}\ge -(N_{rt}-N_{r,t-1}),
$$

于是

$$
V_r=\sum_{t=1}^{2406}v_{rt}.
$$

新能源利用率按题定口径计算：

$$
U_{\mathrm{RE}}=
\frac{\sum_{r,t}
(U_{rt}^{RE}+P_{rt}^{RE,ch}+P_{rt}^{sell})\Delta t}
{\sum_{r,t}A_{rt}^{RE}\Delta t}.
$$

等效循环量仅作诊断：

$$
N_r^{EFC}=
\frac{\sum_t(P_{rt}^{ch}+P_{rt}^{dis})\Delta t}
{2E_r^{max}}.
$$

题面没有退化成本参数，因此不虚构电池寿命成本。

### 多目标求解

分别求成本、碳排、峰值和波动的单目标参照解，再使用

$$
\min C_{\mathrm{op}}
$$

满足

$$
E_{\mathrm{CO2}}\le\epsilon_C,\quad
P_r^{peak}\le\epsilon_{P,r},\quad
V_r\le\epsilon_{V,r}.
$$

工程上不接受通过终端SOC透支、无效循环或越过功率边界取得的数学极值。

### 可观测性与验证

不存在最优动作标签，基准SOC仅用于比较。验证逐时能源平衡、SOC递推、上下限、终端SOC、互斥状态、购售电边界，以及成本和碳排放复算。所有不可行情景输出有限的“不可行”状态及冲突约束，不输出NaN或Inf。

### 必须回答的输出

1. 六区域0–2406小时新能源直接利用、两类充电、放电、购电、外送、弃电与SOC。
2. 每一区域终端SOC及其相对初始SOC裕量。
3. 储能优化前后成本、碳排放、峰值净购电和绝对爬坡量。
4. 每区等效循环量、充放电小时数和同时充放电违约数。
5. 新能源利用率和各去向累计电量。
6. 文件：`q3_storage_dispatch.xlsx`、`q3_comparison.xlsx`、`q3_metrics.json`、`q3_soc.png`、`q3_grid_profile.png`、`q3_validation.json`。

---

## 子问题 4：多区域算—储—电联合优化

### 模型思路

现役模型为 `q4_enhanced`：在 `q4_baseline` 分层滚动联合MILP上实施ε约束Pareto优化和情景分析。联合模型同时包含问题一的任务决策、问题二的实际负荷映射和问题三的储能能源流。

若增强候选的宽松ε组合不可行、归一化分母无法处理、Pareto点存在明显支配，或情景修改了未经授权的输入，则淘汰增强候选并回退 `q4_baseline`，但仍须完整报告单目标结果和不可行原因。

### 联合约束

任务侧满足

$$
\sum_{(r,s)\in\Omega_i}x_{irs}=1,
$$

实时任务 \(s=a_i\)，弹性任务满足

$$
a_i\le s,\qquad s+d_i\le\min(f_i,2406).
$$

容量和负荷由共享内核计算。能源侧满足

$$
U_{rt}^{RE}+P_{rt}^{RE,ch}
+P_{rt}^{sell}+P_{rt}^{curt}=A_{rt}^{RE},
$$

$$
P_{rt}^{buy}+U_{rt}^{RE}+P_{rt}^{dis}
=P_{rt}^{fac}+P_{rt}^{grid,ch}+P_{rt}^{sell},
$$

以及全部SOC、功率、购售电和终端约束。

服务质量定义为仅由题内可观测量形成的复合指标：

$$
Q_{\mathrm{service}}
=w_1R_{\mathrm{instant}}
+w_2R_{\mathrm{SLA}}
+w_3R_{\mathrm{deadline}}
+w_4\left(1-\frac{\overline W}{W^{ref}}\right),
$$

其中实时即时开工率、SLA满足率和按期完成率在硬约束满足时均应为1；\(\overline W\) 为弹性任务平均等待时间，\(W^{ref}\) 由同一任务集基础调度给出。若 \(W^{ref}=0\)，删除该项并重新归一化其余权重，不能除零。由于前三项已是硬约束，Pareto分析同时单独报告平均等待时间，避免复合分掩盖差异。

### 多目标形式

$$
\min C_{\mathrm{op}}
$$

满足

$$
E_{\mathrm{CO2}}\le\epsilon_C,\qquad
L_{\mathrm{net}}\le\epsilon_L,
$$

$$
Q_{\mathrm{service}}\ge\epsilon_Q,\qquad
U_{\mathrm{RE}}\ge\epsilon_U,
$$

$$
P_r^{peak}\le\epsilon_{P,r},\quad \forall r.
$$

得到非支配解集合 \(\mathcal P\) 后，对所有“越小越好”指标使用

$$
z_j(y)=
\frac{F_j(y)-F_j^{ideal}}
{F_j^{nadir}-F_j^{ideal}},
$$

“越大越好”指标反向处理。若分母为零，说明该指标在候选集内为常数，将其标记为“无区分度”并从距离中删除。折中解为

$$
y^\star=\arg\min_{y\in\mathcal P}
\sqrt{\sum_j w_jz_j(y)^2}.
$$

权重必须公开，并报告等权及敏感性结果。

### 情景模型

碳约束：

$$
E_{\mathrm{CO2}}\le\alpha_CE_{\mathrm{CO2}}^{base},
$$

其中 \(\alpha_C\) 取无额外约束、分级减排和严格预算的有限网格，具体数值在代码前预声明。

电价情景保持小时结构：

$$
\pi_{rt}^{buy,sc}
=\bar\pi_r+\beta_{\mathrm{price}}
(\pi_{rt}^{buy}-\bar\pi_r).
$$

新能源情景为

$$
A_{rt}^{RE,sc}
=\max\{0,\beta_{\mathrm{RE}}A_{rt}^{RE}
+\delta_{rt}^{sc}\}.
$$

波动增强扰动 \(\delta_{rt}^{sc}\) 必须使用固定种子、零均值、预声明幅度，并保证非负；不能通过测试结果反调情景。各情景除研究因素外使用相同任务集、容量、时延、PUE、功率映射和初始SOC。

### 滚动求解与共享预算

滚动窗口传递两类状态：

1. 已开工任务在下一窗口的固定区域和剩余逐时占用；
2. 上一窗口末端绝对SOC。

代码阶段单次执行共享

$$
B_{\mathrm{total}}=300\text{ s},\qquad
T_{\mathrm{tail}}=15\text{ s},
$$

因此搜索统一截止于运行起点后

$$
D_{\mathrm{search}}=285\text{ s}.
$$

先预留数据读取、候选筛选、问题一固定测试、问题三基准复算、文件输出和验证开销；所有多目标候选共享剩余时间，不为每个子问题重复分配300秒。截止后不再启动新候选；已经启动的候选只有能在总截止前安全完成才保留，部分解不得作为正式结果。

### 可观测性与验证

联合最优策略不可观测，不使用监督学习准确率。验证包括：

- 每个任务恰好执行一次；
- 实时任务即时开工；
- 时延、到达、截止和2406边界合规；
- GPU、IT及设施功率不超限；
- 新能源守恒、区域能源平衡和SOC递推残差；
- 初始及终端SOC合规；
- 充放电互斥和购售电业务规则；
- 指标复算一致；
- Pareto非支配性；
- 缩小实例滚动解与整体MILP的目标值、可行性及最优间隙对照。

### 必须回答的输出

1. 折中方案的完整任务级调度表和逐区域逐小时能源调度表。
2. 系统成本、碳排放、网络时延、服务质量、新能源利用率和六区域峰值净购电。
3. 完整Pareto候选、非支配标记、理想点距离和最终折中方案编号。
4. 各碳约束、电价机制和新能源波动情景的绝对指标、相对变化率及可行性状态。
5. 每个情景的迁移方向、迁移任务数、迁移GPU-hour、平均等待、储能循环、购售电量和新能源去向。
6. 求解器状态、最优间隙、滚动窗口衔接残差及缩小实例对照结果。
7. 文件：`q4_joint_schedule.xlsx`、`q4_scenario_comparison.xlsx`、`q4_metrics.json`、`q4_pareto.csv`、`q4_pareto.png`、`q4_scenario_dashboard.png`、`q4_validation.json`。

## 3. 现役候选与停止规则汇总

| 子问题 | 现役候选 | 未选候选及淘汰/回退规则 |
|---|---|---|
| q1 | `q1_enhanced` | 若验证集WAPE和MAE均不优于季节性基线，预测回退 `q1_baseline`；若MILP无完整可行解，仅在启发式零违约时回退 |
| q2 | `q2_enhanced` | 宽松ε仍不可行、窗口拼接违约或Pareto点被支配时，回退 `q2_baseline` |
| q3 | `q3_enhanced` | `q3_baseline` 仅在LP自然排除同时充放电和循环套利时采用；否则淘汰LP简化 |
| q4 | `q4_enhanced` | 宽松ε不可行、情景不可比或Pareto构造失败时，回退 `q4_baseline` |

所有pilot均只是代码阶段的廉价检查计划，没有在模型阶段运行。若现役模型硬约束失败，应结构化停止并报告冲突，不得通过放松任务完成、网络时延、容量、能源守恒或终端SOC来“保证有答案”。

## 4. 统一结果审计

正式结果至少输出以下最大残差：

$$
\rho_{\mathrm{task}}
=\max_i\left|\sum_{r,s}x_{irs}-1\right|,
$$

$$
\rho_{\mathrm{energy}}
=\max_{r,t}\left|
P_{rt}^{buy}+A_{rt}^{RE}+P_{rt}^{dis}
-P_{rt}^{fac}-P_{rt}^{ch}-P_{rt}^{sell}-P_{rt}^{curt}
\right|,
$$

$$
\rho_{\mathrm{SOC}}
=\max_{r,t}\left|
E_{rt}-E_{r,t-1}
-\eta_r^cP_{rt}^{ch}\Delta t
+\frac{P_{rt}^{dis}\Delta t}{\eta_r^d}
\right|.
$$

数值容差 \(\tau_{\mathrm{num}}\) 必须由代码阶段按求解器和数据尺度预声明，不能用本次训练RMSE乘常数构造随误差自动放宽的门槛。报告必须区分“证明最优”“限时可行”“启发式可行”和“不可行”四种状态。