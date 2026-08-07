# 数学模型

## 符号说明

| 符号 | 含义 | 类型 | 取值范围、单位与来源 |
|------|------|------|----------------------|
| \(i,r,k,t,s\) | 任务、区域、类型、小时、开工时刻索引 | 索引 | \(r\in R,\ t=0,\ldots,2406\)；题面直接给定 |
| \(I,I_R,I_E\) | 全任务、实时任务、弹性任务集合 | 集合 | \(I_E=\{i:k_i\in\{\mathrm{BatchInference},\mathrm{AITraining}\}\}\) |
| \(x_{irs}\) | 任务 \(i\) 在区域 \(r\)、时刻 \(s\) 开工 | 二元决策变量 | \(\{0,1\}\) |
| \(\omega_{it}(s)\) | 任务从 \(s\) 开工后与小时区间 \([t,t+1)\) 的重叠时长 | 派生参数 | \([0,1]\) h |
| \(g_i,d_i,a_i,f_i\) | GPU需求、分钟时长、到达时刻和最晚完成时点 | 附件参数 | GPU、min、h、h |
| \(o_i,k_i,L_i^{max}\) | 来源区域、任务类型、最大允许网络时延 | 附件参数 | 无、无、ms |
| \(G_r\) | 区域可调度GPU容量 | 附件参数 | 正数，等效GPU单元 |
| \(p_k\) | 单位等效GPU的任务IT功率 | 附件参数 | MW/等效GPU单元 |
| \(P_{rt}^{AI},P_{rt}^{IT},P_{rt}^{F}\) | AI、总IT和设施负荷 | 派生变量 | MW |
| \(N_{rt},B_{rt}\) | 非AI IT负荷、问题三给定基线AI IT负荷 | 附件参数 | MW |
| \(G_{rt},E_{rt}^{sell}\) | 电网购电、外送功率 | 决策变量 | MW |
| \(U_{rt}^{RE},C_{rt}^{RE},K_{rt}\) | 新能源直接利用、新能源充电、弃电 | 决策变量 | MW |
| \(C_{rt}^{G},D_{rt}\) | 电网充电、储能放电 | 决策变量 | MW |
| \(S_{rt}\) | 小时 \(t\) 运行后的SOC | 状态变量 | MWh |
| \(S_r^0,S_r^{min},S_r^{cap}\) | 初始SOC、安全下限、额定容量 | 附件参数 | MWh |
| \(S_r^{max}\) | 优化中的SOC上限 | 附件映射 | \(S_r^{max}=S_r^{cap}=\mathrm{StorageCapacity\_MWh}_r\) |
| \(I_r^{max}\) | 最大购电功率 | 附件参数 | \(\mathrm{MaxGridImport\_MW}_r\)，MW |
| \(X_r^{grid},X_r^{sell}\) | 区域电网外送上限、储能表外送上限 | 附件参数 | MW |
| \(E_r^{max}\) | 实际生效外送上限 | 派生参数 | \(\min(X_r^{grid},X_r^{sell})\)，MW |
| \(M_{rt}\) | 净购电功率 | 派生变量 | \(G_{rt}-E_{rt}^{sell}\)，MW |
| \(P_r^{peak}\) | 区域峰值正净购电 | 辅助变量 | \(\max_t\max(M_{rt},0)\)，MW |
| \(q_{rt},V_r\) | 相邻小时净购电绝对变化及总绝对爬坡量 | 辅助变量、指标 | MW |
| \(C_{op},E_{CO2},L_{net},U_{RE}\) | 成本、碳排放、平均网络时延、新能源利用率 | 目标或指标 | 元、tCO2、ms、无量纲 |
| \(Q_F,Q_R,Q_L,W,Q_{service}\) | 按期完成率、实时即时开工率、SLA满足率、等待惩罚、服务质量 | 指标 | \([0,1]\) |
| \(Throughput_r,EFC_r\) | 储能吞吐量、等效循环量 | 指标 | MWh、次 |
| \(\varepsilon_C,\varepsilon_L,\varepsilon_U,\varepsilon_{P,r},\varepsilon_{V,r},\varepsilon_Q\) | ε约束阈值 | 参数 | 分别为tCO2、ms、无量纲、MW、MW、无量纲 |
| \(H,\Delta\) | 滚动窗口长度和推进步长 | 算法参数 | 正整数小时，代码阶段固定并写入结果元数据 |
| \(\tau\) | 求解及残差检查容差 | 数值参数 | 代码阶段固定，所有模型统一使用 |

几何量不适用于本题；无容器、尺寸链、坐标原点或观测位置需要确认。设备容量、网络和能源参数均由题面附件直接给定，不从图示推导。

统一定义重叠时长：

$$
\omega_{it}(s)=
\max\left\{0,\min(t+1,s+d_i/60)-\max(t,s)\right\}\quad(\mathrm h).
\tag{1}
$$

任务不可抢占。任务可占用第2405小时，但必须满足 \(s+d_i/60\le2406\)，不得占用第2406小时。

所有比例和相对变化使用以下有限输出规则。对于分子 \(A\)、分母 \(B\)：

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
\mathrm{unavailable},&B=0.
\end{cases}
\tag{2}
$$

相对变化定义为：

$$
\operatorname{RelChange}(Y,Y^0)=
\begin{cases}
100(Y-Y^0)/|Y^0|\%,&Y^0\ne0,\\
\mathrm{null},&Y^0=0,
\end{cases}
\tag{3}
$$

并始终同时报告绝对变化 \(Y-Y^0\)。不可用项不参与情景排序，不输出 `NaN`、`Inf` 或任意替代常数。

## 子问题 1：需求预测与最后24小时基础调度

### 模型思路

保留现役 `q1_enhanced`：正则化时序回归负责预测，MILP负责实际任务调度。`q1_baseline` 为季节性朴素预测基准。增强预测若在验证集MAE和WAPE上均不优于基线，则采用基线；调度求解若没有通过全部硬约束的可行解，则结构化报告不可行，不用违规启发式强行填充结果。

预测标签是由实际任务聚合得到的逐小时区域—类型GPU需求，真实可观测。调度不存在真实“最优方案”标签，不能用分类准确率验证。

### 模型建立

按区域、任务类型统计任务数、GPU总量、GPU分位数、GPU-hour、持续时间分位数、到达强度和峰值并发：

$$
D_{rkt}=\sum_{i:o_i=r,k_i=k,a_i=t}g_i,\qquad
H_{rkt}=\sum_{i:k_i=k}g_i\omega_{it}(a_i).
\tag{4}
$$

回归特征包含 \(1,24,168\) 小时滞后、滚动均值、小时和星期周期编码。对每个 \((r,k)\)：

$$
\widehat{\boldsymbol\beta}_{rk}
=\arg\min_{\boldsymbol\beta}
\sum_{t\in\mathcal T_{tr}}
(D_{rkt}-\boldsymbol z_t^\top\boldsymbol\beta)^2
+\lambda\|\boldsymbol\beta\|_2^2,
\qquad
\widehat D_{rkt}=\max(0,\boldsymbol z_t^\top\widehat{\boldsymbol\beta}_{rk}).
\tag{5}
$$

训练区间为0–2351，验证区间为2352–2375。选定特征与 \(\lambda\) 后用0–2375重新训练，对2376–2399进行一次24步递归预测：测试区间内需要短滞后时使用此前预测值，不使用2376–2399的真实标签构造后续预测特征。实际标签只在24步全部生成后用于评价。

$$
MAE=\frac1n\sum|D-\widehat D|,\qquad
RMSE=\sqrt{\frac1n\sum(D-\widehat D)^2},
\tag{6}
$$

$$
WAPE=\operatorname{Ratio}
\left(\sum|D-\widehat D|,\sum D\right).
\tag{7}
$$

若 \(\sum D=0\)，WAPE按式(2)输出 `null` 和 `unavailable`，仍报告MAE、RMSE及绝对误差总量。

相关系数仅在样本数 \(n\ge2\) 且两序列样本方差均为正时计算：

$$
\rho_{XY}=
\frac{\sum_j(X_j-\bar X)(Y_j-\bar Y)}
{\sqrt{\sum_j(X_j-\bar X)^2\sum_j(Y_j-\bar Y)^2}}.
\tag{8}
$$

否则输出 `correlation=null, status=unavailable`，并改报可计算的均值、标准差、绝对差和周期分组统计，不据此宣称相关或不相关。

最后24小时基础调度使用实际到达任务。合法候选集合为：

$$
\mathcal F_i=
\left\{(r,s):
s\ge a_i,\ 
s+d_i/60\le\min(f_i,2406),\
\ell_{o_ir}\le L_i^{max}
\right\},
\tag{9}
$$

实时任务进一步要求 \(s=a_i\)。约束为：

$$
\sum_{(r,s)\in\mathcal F_i}x_{irs}=1,
\tag{10}
$$

$$
L_{rt}^{GPU}=\sum_{i,s}g_i\omega_{it}(s)x_{irs}\le G_r,
\tag{11}
$$

$$
P_{rt}^{AI}=\sum_{i,s}g_ip_{k_i}\omega_{it}(s)x_{irs},
\tag{12}
$$

$$
P_{rt}^{IT}=N_{rt}+P_{rt}^{AI}\le P_r^{IT,max},
\qquad
PUE_rP_{rt}^{IT}\le P_r^{F,max}.
\tag{13}
$$

统一采用线性绝对偏差MILP。令 \(\bar L_{rt}^{GPU}\) 为由区域可调度容量比例确定的负载均衡目标，其值在求解前由附件容量和该小时总GPU占用唯一计算，不是决策变量。定义：

$$
u_{rt}\ge L_{rt}^{GPU}-\bar L_{rt}^{GPU},\qquad
u_{rt}\ge\bar L_{rt}^{GPU}-L_{rt}^{GPU},\qquad u_{rt}\ge0.
\tag{14}
$$

目标函数为：

$$
\min\ 
\alpha\sum_{i,r,s}(s-a_i)x_{irs}
+\beta\sum_{r,t}u_{rt}.
\tag{15}
$$

### 求解方法

先完成预测结构比较，再生成满足式(9)–(13)的启发式热启动并求解MILP。只有求解器返回可行整数解且全部约束残差不超过 \(\tau\) 时，结果才可标为“限时可行”；仅达到时间上限但没有可行解时结构化停止。

### 必须回答的输出

1. 区域—任务类型统计表及周期、自相关、相关性分析；相关系数不可计算时附状态和代理统计。
2. 2376–2399小时逐组和总体MAE、RMSE、WAPE及WAPE状态。
3. 实际到达任务的 `TaskID、SourceRegion、ExecutionRegion、StartTime、FinishTime、TaskType、GPU_Demand` 调度表。
4. 覆盖2376–2405的最后24小时任务甘特图，明确收尾任务。
5. 各区域逐小时GPU占用、利用率及最大容量裕度。
6. 任务唯一执行、即时开工、时延、截止、GPU/IT/设施容量和“不占用2406小时”的验证文件。

## 子问题 2：碳感知任务调度

### 模型思路

保留 `q2_enhanced`，以滚动时域ε-约束MILP生成Pareto方案；`q2_baseline` 提供成本参照解。宽松ε仍不可行或没有通过残差检查的可行解时结构化停止。

### 模型建立

任务与容量约束沿用式(9)–(13)，输入改为0–2399全部实际任务。设施负荷为：

$$
P_{rt}^{F}=PUE_r\left(
N_{rt}+\sum_{i,s}g_ip_{k_i}\omega_{it}(s)x_{irs}
\right).
\tag{16}
$$

问题二不含储能：

$$
U_{rt}^{RE}+E_{rt}^{sell}+K_{rt}=A_{rt}^{RE},
\tag{17}
$$

$$
G_{rt}+U_{rt}^{RE}=P_{rt}^{F},
\tag{18}
$$

$$
0\le G_{rt}\le I_r^{max},\qquad
0\le E_{rt}^{sell}\le E_r^{max}.
\tag{19}
$$

若附件确认新能源外送与购电供负荷可以并存，则不设置购售互斥，二者按来源分别核算。

$$
C_{op}=\sum_{r,t}
(c_{rt}G_{rt}-c_{rt}^{sell}E_{rt}^{sell}),
\qquad
E_{CO2}=\sum_{r,t}\kappa_{rt}G_{rt},
\tag{20}
$$

$$
L_{net}=\frac1{|I|}
\sum_{i,r,s}\ell_{o_ir}x_{irs}.
\tag{21}
$$

令

$$
Q_{RE}=\sum_{r,t}(U_{rt}^{RE}+E_{rt}^{sell}),
\qquad
A_{RE}^{tot}=\sum_{r,t}A_{rt}^{RE}.
\tag{22}
$$

当 \(A_{RE}^{tot}>0\) 时，\(U_{RE}=Q_{RE}/A_{RE}^{tot}\)；否则按式(2)输出不可用状态和绝对利用量 \(Q_{RE}=0\)，且该情景不施加 \(\varepsilon_U\) 约束、不参与新能源利用率排序。

主模型为：

$$
\min C_{op}
\tag{23}
$$

$$
\text{s.t.}\quad
E_{CO2}\le\varepsilon_C,\quad
L_{net}\le\varepsilon_L,\quad
U_{RE}\ge\varepsilon_U
\quad(A_{RE}^{tot}>0).
\tag{24}
$$

滚动窗口 \(w\) 的起点记为 \(b_w\)。若任务已在此前窗口确定开工且 \(s_i^*<b_w\)，则正式承诺约束为：

$$
x_{ir_i^*s_i^*}=1,\qquad
x_{irs}=0\quad\forall(r,s)\ne(r_i^*,s_i^*),
\tag{25}
$$

其当前及后续小时占用固定为：

$$
L_{irt}^{committed}=g_i\omega_{it}(s_i^*),\qquad
P_{irt}^{committed}=g_ip_{k_i}\omega_{it}(s_i^*).
\tag{26}
$$

这些固定占用必须进入式(11)–(13)和式(16)。尚未开工的任务仅能从满足 \(s\ge b_w\) 的剩余合法候选中选择；已经开工的任务不得在新窗口重新选区、取消或修改开工时刻。

### 求解方法

先分别求成本、碳、时延和新能源单目标参照值，再在参照值构成的有限可行区间上生成固定ε网格。每个窗口固定 \(H,\Delta\)，并按式(25)–(26)传递承诺。只有具有整数可行解且残差不超过 \(\tau\) 的限时结果可以进入Pareto集合。

### 必须回答的输出

1. 全任务执行区域、开工与完成时刻的调度策略文件。
2. 总成本、碳排放、平均及高分位时延、新能源利用率或不可用状态。
3. 相对基础调度的绝对变化与按式(3)计算的变化率。
4. Pareto前沿及选定折中方案。
5. 各任务类型的迁移量、等待时间和区域负荷。
6. 全部任务、容量、功率、能源、新能源守恒及窗口承诺残差报告。

## 子问题 3：固定负荷储能协同优化

### 模型思路

保留 `q3_enhanced`。问题三固定任务调度和IT负荷，仅优化储能、购售电及新能源分配。二元状态禁止同时充放电。

### 模型建立

固定设施负荷：

$$
P_{rt}^{F}=PUE_r(B_{rt}+N_{rt}).
\tag{27}
$$

能源分流和平衡为：

$$
U_{rt}^{RE}+C_{rt}^{RE}
+E_{rt}^{sell}+K_{rt}=A_{rt}^{RE},
\tag{28}
$$

$$
G_{rt}+U_{rt}^{RE}+D_{rt}
=P_{rt}^{F}+C_{rt}^{G}.
\tag{29}
$$

总充电功率为 \(C_{rt}=C_{rt}^{RE}+C_{rt}^{G}\)。SOC递推为：

$$
S_{r,-1}=S_r^0,
\qquad
S_{rt}=S_{r,t-1}
+\eta_r^cC_{rt}
-\frac{D_{rt}}{\eta_r^d}.
\tag{30}
$$

`StorageCapacity_MWh` 与SOC上限的确定映射为：

$$
S_r^{max}=S_r^{cap}
=\mathrm{StorageCapacity\_MWh}_r.
\tag{31}
$$

边界为：

$$
S_r^{min}\le S_{rt}\le S_r^{max},
\qquad
S_{r,2406}\ge S_r^0,
\tag{32}
$$

$$
0\le C_{rt}\le C_r^{max}z_{rt},\qquad
0\le D_{rt}\le D_r^{max}(1-z_{rt}),
\qquad z_{rt}\in\{0,1\}.
\tag{33}
$$

购电和外送边界明确为：

$$
0\le G_{rt}\le I_r^{max},
\qquad
0\le E_{rt}^{sell}
\le E_r^{max}
=\min(X_r^{grid},X_r^{sell}).
\tag{34}
$$

净购电、峰值和波动定义为：

$$
M_{rt}=G_{rt}-E_{rt}^{sell},
\tag{35}
$$

$$
P_r^{peak}\ge M_{rt},\qquad P_r^{peak}\ge0.
\tag{36}
$$

因此 \(P_r^{peak}=\max_t\max(M_{rt},0)\)，全时段净外送时峰值正净购电为0，不产生负峰值。

$$
q_{rt}\ge M_{rt}-M_{r,t-1},\qquad
q_{rt}\ge M_{r,t-1}-M_{rt},
\tag{37}
$$

$$
V_r=\sum_{t=1}^{2406}q_{rt}.
\tag{38}
$$

采用ε约束：

$$
\min C_{op}
\tag{39}
$$

$$
\text{s.t.}\quad
E_{CO2}\le\varepsilon_C,\quad
P_r^{peak}\le\varepsilon_{P,r},\quad
V_r\le\varepsilon_{V,r}
\quad(\forall r).
\tag{40}
$$

新能源绝对利用量为：

$$
Q_{RE}^{(3)}
=\sum_{r,t}
(U_{rt}^{RE}+C_{rt}^{RE}+E_{rt}^{sell}).
\tag{41}
$$

当 \(\sum A_{rt}^{RE}>0\) 时：

$$
U_{RE}=
\frac{Q_{RE}^{(3)}}{\sum_{r,t}A_{rt}^{RE}}.
\tag{42}
$$

否则按式(2)输出不可用状态并报告 \(Q_{RE}^{(3)}=0\)。成本、碳、峰值和爬坡量的相对变化均按式(3)处理零基准。

### 求解方法

分别求成本、碳、削峰和减小绝对爬坡方案。以附件基准轨迹和无储能反事实为对照，但不将附件基准SOC固定进优化模型。

### 必须回答的输出

1. 六区域0–2406小时充电、放电、购电、售电、新能源各去向及SOC策略文件。
2. 各区域初始SOC、终端SOC和边界裕度。
3. 储能前后成本、碳排放、峰值正净购电及绝对爬坡量。
4. 各指标绝对变化和按式(3)计算的相对变化率或不可用状态。
5. 同时充放电、购售电口径、能量平衡、SOC递推、购售电边界和终端条件验证报告。

## 子问题 4：算—储—电联合多目标优化

### 模型思路

保留 `q4_enhanced`，由带正式承诺传递的分层滚动联合MILP实现。`q4_baseline` 是成本基准。宽松ε不可行、归一化分母为零却未排除，或候选被同批方案严格支配时，不把该候选纳入Pareto前沿。

### 模型建立

联合模型同时保留问题二的 \(x_{irs}\) 和问题三的能源变量。设施负荷为：

$$
P_{rt}^{F}=PUE_r\left(
N_{rt}+\sum_{i,s}g_ip_{k_i}\omega_{it}(s)x_{irs}
\right).
\tag{43}
$$

任务约束采用式(9)–(13)，滚动承诺采用式(25)–(26)，能源、SOC、购售电、峰值和爬坡约束采用式(28)–(38)。

对弹性任务定义最大可等待时间：

$$
h_i=\min(f_i,2406)-\frac{d_i}{60}-a_i,
\qquad i\in I_E.
\tag{44}
$$

若 \(h_i<0\)，任务在题面时限下不可行，模型结构化停止。若 \(h_i>0\)，归一化等待为：

$$
w_i=\frac{s_i-a_i}{h_i}.
\tag{45}
$$

若 \(h_i=0\)，唯一合法开工时刻为 \(s_i=a_i\)，定义 \(w_i=0\)；若此候选不存在，则模型不可行。由合法候选集合可得 \(0\le w_i\le1\)。

总体等待惩罚为：

$$
W=
\begin{cases}
\dfrac1{|I_E|}\sum_{i\in I_E}w_i,&|I_E|>0,\\
0,&|I_E|=0.
\end{cases}
\tag{46}
$$

空弹性任务集合时，\(W=0\) 表示没有等待损失，并标记 `not_applicable`，不是用任意小量替代分母。

定义：

$$
Q_F=\frac1{|I|}
\sum_{i\in I}
\mathbf 1\left(
s_i+\frac{d_i}{60}\le\min(f_i,2406)
\right),
\tag{47}
$$

$$
Q_R=
\begin{cases}
\dfrac1{|I_R|}\sum_{i\in I_R}\mathbf1(s_i=a_i),&|I_R|>0,\\
1,&|I_R|=0,
\end{cases}
\tag{48}
$$

$$
Q_L=\frac1{|I|}
\sum_{i\in I}
\mathbf1(\ell_{o_ir_i}\le L_i^{max}).
\tag{49}
$$

若全任务集合为空，则 \(Q_F,Q_L\) 均定义为1并标记 `not_applicable`；此时任务指标不参与不同调度方案的区分。服务质量为：

$$
Q_{service}
=\frac{Q_F+Q_R+Q_L+(1-W)}4,
\qquad 0\le Q_{service}\le1.
\tag{50}
$$

由于硬约束要求全部任务按期、实时任务即时开工且时延合规，\(Q_F,Q_R,Q_L\) 在正常非空可行实例中均为1，\(Q_{service}\) 主要反映弹性任务等待差异。

主模型为：

$$
\min C_{op}
\tag{51}
$$

$$
\text{s.t.}\quad
E_{CO2}\le\varepsilon_C,\quad
L_{net}\le\varepsilon_L,\quad
U_{RE}\ge\varepsilon_U,
\tag{52}
$$

$$
Q_{service}\ge\varepsilon_Q,\qquad
P_r^{peak}\le\varepsilon_{P,r}\quad(\forall r).
\tag{53}
$$

其中仅当可用新能源总量为正时施加 \(U_{RE}\ge\varepsilon_U\)；零新能源情景按式(2)标为不可用并退出该指标排序。

对非支配方案 \(m\)，仅使用同一可行域内理想值和最差值归一化：

$$
z_{jm}=
\frac{F_{jm}-F_j^{best}}
{F_j^{worst}-F_j^{best}}
\quad\text{if }F_j^{worst}>F_j^{best}.
\tag{54}
$$

若分母为零，该指标标记 `no_discrimination` 并从距离中移除。剩余指标权重重新归一化至和为1：

$$
D_m=\sqrt{\sum_{j\in J_{valid}}w_jz_{jm}^2},
\qquad
w_j\ge0,\quad
\sum_{j\in J_{valid}}w_j=1.
\tag{55}
$$

储能吞吐量和等效循环量定义为：

$$
Throughput_r=
\sum_{t=0}^{2406}
(C_{rt}^{RE}+C_{rt}^{G}+D_{rt}),
\tag{56}
$$

$$
EFC_r=
\begin{cases}
\dfrac{\sum_{t=0}^{2406}D_{rt}}{2S_r^{cap}},
&S_r^{cap}>0,\\
\mathrm{null},&S_r^{cap}=0.
\end{cases}
\tag{57}
$$

当 \(S_r^{cap}=0\) 时，\(EFC_r\) 状态为 `unavailable`，并报告吞吐量绝对值，不输出非有限结果。

情景保持单因素可比：

- 碳约束：无额外约束、分级减排、严格预算；
- 电价：原始价格、峰谷差扩大或缩小、售电价格变化；
- 新能源：基准、整体升降、波动增强，并保证 \(A_{rt}^{RE}\ge0\)。

### 求解方法

先剔除违反时延、到达、截止和2406边界的组合，再按式(25)–(26)滚动求解并传递运行任务与绝对SOC。缩小实例与一次性整体MILP对照。正式结果标注为“证明最优”“限时可行”或“启发式可行”，并报告最优间隙；后两类也必须通过全部硬约束残差检查。

所有附件参数、预测误差、最优目标值和情景结果均由代码阶段从真实附件计算，不预填结果。

### 必须回答的输出

1. 联合任务调度、逐时能源流和SOC完整方案文件。
2. 成本、碳排放、时延、服务质量、新能源利用率及六区域峰值正净购电。
3. Pareto前沿、折中解、权重和式(54)–(55)的归一化口径。
4. 各碳约束、电价机制和新能源情景的绝对指标、相对变化或不可用状态。
5. 各情景任务迁移方向、等待时间、式(56)的储能吞吐量、式(57)的等效循环量及新能源去向。
6. 任务、网络、容量、功率、能源、新能源、SOC、终端状态和式(25)–(26)窗口衔接验证文件。
7. 求解状态、运行时间、最优间隙及小规模整体MILP对照结果。

## 模型局限性

模型使用确定性任务时长、小时级开工和固定PUE，未描述任务时长误差、网络拥塞、线路潮流、传输能耗及储能退化成本；这些均缺少题面数据或被明确排除。调度没有真实最优标签，结论只能由机制约束、求解界和情景一致性支持。

6030条同时购售电记录表明“购电供负荷与新能源外送并存”可能是合法分源行为，代码阶段必须核对工作簿说明；在口径未确认前，不把购售互斥无条件设为硬约束。44条基准GPU利用率超过100%的记录仅作异常核验，正式容量约束始终使用 `Available_GPU`、最大IT功率及最大设施功率。

## Verifier 修复核对表

| Block issue | 修复位置 | 可计算性与有限输出保证 |
|---|---|---|
| 问题四 \(W\) 未定义 | 式(44)–(46)、式(50) | 明确定义每个弹性任务的可等待时间、零等待窗口、空弹性任务集合以及 \(0\le W\le1\)，使 \(Q_{service}\) 可直接进入MILP |
| 相对变化率和新能源利用率零分母 | 式(2)–(3)、式(22)、式(41)–(42)、式(52) | 分母为零时输出 `null` 与结构化状态，同时报告绝对量并排除对应排序或ε约束，禁止产生NaN/Inf |
| 问题一MILP与MIQP不一致；问题三遗漏爬坡约束 | 式(14)–(15)、式(37)–(40) | 问题一统一为线性绝对偏差MILP；问题三正式加入 \(V_r\le\varepsilon_{V,r}\) |
| 问题三、四缺少购电外送上限及容量映射 | 式(31)、式(34)，问题四明确继承式(28)–(38) | 固定 \(S_r^{max}=StorageCapacity\_MWh_r\)，外送上限取两个附件字段的最小值，并逐式限制购电、外送 |
| 滚动窗口承诺未形成正式约束 | 式(25)–(26) | 已开工任务固定区域和开工变量，后续GPU与功率占用固定进入容量约束；未开工任务仅从剩余合法候选选择 |
| 测试滞后口径及常数序列相关系数未定义 | 式(5)后的递归预测规则、式(8) | 2376–2399采用24步递归预测，不泄漏测试真实标签；样本不足或方差为零时相关系数输出不可用并改报有限代理统计 |