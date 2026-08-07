# 数学模型

## 符号说明

| 符号 | 含义 | 类型 | 取值范围、单位与来源 |
|---|---|---|---|
| \(\mathcal I,\mathcal R,\mathcal K\) | 任务、区域、任务类型集合 | 索引集合 | \(|\mathcal R|=6,\ |\mathcal K|=3\)，附件直接给定 |
| \(\mathcal T_A\) | 任务到达主时域 | 时间集合 | \(\{0,\ldots,2399\}\)，h，题面直接给定 |
| \(\mathcal T_C\) | 收尾时域 | 时间集合 | \(\{2400,\ldots,2405\}\)，h，题面直接给定 |
| \(\mathcal T_J\) | 允许任务占用的时段 | 时间集合 | \(\{0,\ldots,2405\}\)，h |
| \(\mathcal T_E\) | 电力与储能结算时段 | 时间集合 | \(\{0,\ldots,2406\}\)，h |
| \(\Delta t\) | 调度步长 | 题面参数 | \(1\) h |
| \(a_i,d_i,f_i\) | 到达时刻、连续执行时长、最晚完成时点 | 可观测参数 | \(d_i=\text{EstimatedDuration\_min}/60\)，h |
| \(g_i,k_i,o_i\) | GPU 需求、类型、来源区域 | 可观测参数 | `workload_trace.xlsx` |
| \(\ell_i^{\max},\ell_{or}\) | 最大允许时延、单向区域时延 | 可观测参数 | ms，任务表与时延表 |
| \(p_k\) | 每等效 GPU 的平均 IT 功率 | 可观测参数 | MW/GPU，`power_mapping.xlsx` |
| \(G_r^{\max}\) | 可调度 GPU 容量 | 可观测参数 | GPU，`Available_GPU` |
| \(P_r^{IT,\max},P_r^{F,\max}\) | IT、设施功率上限 | 可观测参数 | MW |
| \(\phi_r\) | PUE | 可观测参数 | 无量纲 |
| \(x_{irs}\) | 任务 \(i\) 是否在区域 \(r\) 于 \(s\) 开工 | 二元变量 | \(\{0,1\}\) |
| \(H_{it}(s)\) | 执行区间与小时 \(t\) 的重叠小时数 | 派生参数 | \([0,\Delta t]\)，h |
| \(L_{rt}^{AI},L_{rt}^{NA}\) | AI、非 AI IT 负荷 | 派生量/输入 | MW |
| \(L_{rt}^{IT},L_{rt}^{F}\) | 总 IT、设施负荷 | 派生量 | MW |
| \(R_{rt},U_{rt}\) | 可用、直接消纳新能源 | 输入/变量 | MW |
| \(C_{rt}^{R},C_{rt}^{G}\) | 新能源、电网充电功率 | q3、q4变量 | MW |
| \(D_{rt}\) | 储能放电功率 | q3、q4变量 | MW |
| \(I_{rt},X_{rt}^{R},W_{rt}\) | 购电、新能源外送、弃电 | 变量 | MW |
| \(S_{rt},S_r^0\) | 时段末 SOC、初始 SOC | 状态/参数 | MWh |
| \(N_{rt}\) | 净购电 \(I_{rt}-X_{rt}^{R}\) | 派生量 | MW |
| \(P_r^{peak}\) | 非负峰值净购电指标 | 辅助变量 | MW，\(P_r^{peak}\ge0\) |
| \(q_{rt},V_r\) | 绝对爬坡及其累计值 | 辅助量 | MW |
| \(C_{op},E_{CO2},U_{RE}\) | 成本、碳排放、新能源利用率 | 指标 | 元、tCO2、无量纲 |
| \(Q_{service}\) | 服务质量指标 | 指标 | \([0,1]\)，只聚合适用分项 |
| \(B_{total},T_{tail}\) | 总墙钟与收尾预留 | 固定运行参数 | \(300\) s、\(15\) s |
| \(D_{search}\) | 共同搜索截止 | 固定规则 | `t_start+285 s` |

本题没有需要重建的空间几何。区域、时间边界和单向时延均为题面或附件直接给定；几何尺寸链、坐标原点、观测位置及空/满边界不适用，没有待确认几何量。

## 统一时间、负荷与状态边界

任务在 \([s,s+d_i)\) 连续、不可抢占运行。重叠小时数为

$$
H_{it}(s)=
\max\!\left\{0,\min(t+1,s+d_i)-\max(t,s)\right\}.
\tag{1}
$$

\(H_{it}(s)\) 的单位是小时，不再称为无量纲比例。小时平均占用比例为 \(H_{it}(s)/\Delta t\)。候选开工集合为

$$
\mathcal S_{ir}=
\left\{s\in\mathbb Z:
s\ge a_i,\quad
s+d_i\le\min(f_i,2406),\quad
\ell_{o_ir}\le\ell_i^{\max}
\right\}.
\tag{2}
$$

实时推理另限定 \(s=a_i\)。若某任务对所有区域均无候选位置，则结构化停止并报告 `input_infeasible`，不放松时延、容量或截止约束。

任务负荷为

$$
L_{rt}^{AI}
=\sum_i\sum_{s\in\mathcal S_{ir}}
g_ip_{k_i}\frac{H_{it}(s)}{\Delta t}x_{irs},
\tag{3}
$$

$$
L_{rt}^{IT}=L_{rt}^{NA}+L_{rt}^{AI},
\qquad
L_{rt}^{F}=\phi_rL_{rt}^{IT}.
\tag{4}
$$

对 \(t\in\mathcal T_J\)：

$$
\sum_i\sum_sg_i\frac{H_{it}(s)}{\Delta t}x_{irs}\le G_r^{\max},
\quad
L_{rt}^{IT}\le P_r^{IT,\max},
\quad
L_{rt}^{F}\le P_r^{F,\max}.
\tag{5}
$$

第 2406 小时没有任务占用，只进行能源与 SOC 结算。附件中基准 GPU 利用率异常记录的确切数量在本阶段记为 `pending_code_execution`，不得在代码统计前断言。

## 子问题 1：需求预测与最后 24 小时基础调度

### 模型思路

先按区域和任务类型统计实际到达 GPU-hour，再训练未截断线性 Huber-岭模型；非负截断仅用于生成预测。最后 24 小时调度独立使用实际到达任务，预测目标与调度目标不混为一个量纲不一致的目标函数。

### 模型建立

预测标签为

$$
D_{rkt}=\sum_{i:o_i=r,k_i=k,a_i=t}g_id_i.
\tag{6}
$$

统计任务数、GPU 总量和 GPU-hour：

$$
N_{rk}=\sum_i\mathbf1(o_i=r,k_i=k),\quad
G_{rk}^{sum}=\sum_{i:o_i=r,k_i=k}g_i,\quad
H_{rk}^{GPU}=\sum_{i:o_i=r,k_i=k}g_id_i.
\tag{7}
$$

同时报告 \(g_i,d_i\) 的均值、中位数、标准差和指定分位数，以及逐小时强度、峰值并发、24/168 小时自相关。常数序列的相关系数输出 `not_applicable`，改报 MAE、量程和峰均比。

特征向量保持为

$$
z_{rkt}=
\left[
D_{rk,t-1},D_{rk,t-24},D_{rk,t-168},
\overline D_{rk,t}^{(24)},\overline D_{rk,t}^{(168)},
\sin\frac{2\pi t}{24},\cos\frac{2\pi t}{24},
\sin\frac{2\pi t}{168},\cos\frac{2\pi t}{168}
\right]^\top.
\tag{8}
$$

训练时使用未截断输出

$$
y_{rkt}^{raw}=\beta_{rk,0}+\beta_{rk}^{\top}z_{rkt},
\tag{9}
$$

$$
\min_{\beta}
\sum_{r,k,t\in\mathcal T_{train}}
\rho_\delta(D_{rkt}-y_{rkt}^{raw})
+\lambda\sum_{r,k}\|\beta_{rk}\|_2^2.
\tag{10}
$$

训练完成后才生成

$$
\widehat D_{rkt}=\max\{0,y_{rkt}^{raw}\}.
\tag{11}
$$

数据划分不变：\(0\sim2351\) 训练、\(2352\sim2375\) 验证；选定结构后用 \(0\sim2375\) 重拟合唯一正式参数，并测试 \(2376\sim2399\)。

评价指标为 MAE、RMSE 及

$$
WAPE=
\frac{\sum_j|D_j-\widehat D_j|}{\sum_jD_j},
\qquad \sum_jD_j>0.
\tag{12}
$$

若分母为零，WAPE 输出 `not_applicable`，改报 MAE；不使用任意 \(\epsilon\) 替代业务分母。

最后 24 小时实际任务满足

$$
\sum_{r}\sum_{s\in\mathcal S_{ir}}x_{irs}=1,
\qquad x_{irs}\in\{0,1\}.
\tag{13}
$$

令 \(W_{\max}\) 为所有有效候选的最大等待时间、\(L_{\max}\) 为最大候选时延。只在相应量程为正时纳入目标：

$$
\min
\sum_{i,r,s}
\left[
\frac{s-a_i}{W_{\max}}
+\omega_L\frac{\ell_{o_ir}}{L_{\max}}
\right]x_{irs}.
\tag{14}
$$

若某量程为零，删除该常数目标项。式（13）—（14）与式（2）—（5）构成独立调度 MILP。

GPU 利用率为

$$
u_{rt}^{GPU}
=
\frac{\sum_{i,s}g_iH_{it}(s)x_{irs}/\Delta t}
{G_r^{\max}}\times100\%.
\tag{15}
$$

### 求解方法

季节性朴素预测作为基线；增强模型仅在验证集 MAE 或有效 WAPE 改善时采用。调度先按实时优先、最早截止、短任务优先生成可行热启动，再运行 MILP。没有完整 MILP 可行解时，只能退回已通过全部硬约束的启发式方案并标记 `heuristic_feasible`。

### 必须回答的输出

1. 六区域、三任务类型的任务数、GPU 总量、GPU-hour、分位数、持续时长、峰值并发和周期统计。
2. 验证集与测试集的分区域、分类型及总体 MAE、RMSE、WAPE或 `not_applicable`。
3. 第 \(2376\sim2399\) 小时实际任务的正式调度表。
4. 跨越第 2399 小时任务的结清区域和时刻。
5. 最后 24 小时真实起止时刻甘特图文件。
6. 第 \(2376\sim2405\) 小时区域 GPU 利用率表和曲线。
7. 未完成任务数、最大容量违约量及求解状态。

## 子问题 2：碳感知任务迁移与开工优化

### 模型思路

问题二唯一正式能源口径是无储能分源模型。删除自由新能源充电变量，不保留条件式“固定基准充电”分支，避免没有 SOC 的虚假能源吸收。

### 模型建立

对所有 \(r\in\mathcal R,t\in\mathcal T_E\)：

$$
U_{rt}+X_{rt}^{R}+W_{rt}=R_{rt},
\tag{16}
$$

$$
I_{rt}+U_{rt}=L_{rt}^{F}.
\tag{17}
$$

其中

$$
0\le U_{rt},X_{rt}^{R},W_{rt},\quad
0\le I_{rt}\le I_{rt}^{\max},\quad
X_{rt}^{R}\le X_{rt}^{\max}.
\tag{18}
$$

式（16）已确保外送只来自新能源剩余量；\(X_{rt}^{R}\) 不再进入式（17），从而不重复计量。问题二不存在 \(C_{rt}^{R}\)、\(C_{rt}^{G}\)、\(D_{rt}\) 或 \(S_{rt}\)。

指标为

$$
C_{op}=\sum_{r,t\in\mathcal T_E}
(c_{rt}^{buy}I_{rt}-c_{rt}^{sell}X_{rt}^{R})\Delta t,
\tag{19}
$$

$$
E_{CO2}=\sum_{r,t\in\mathcal T_E}
\kappa_{rt}I_{rt}\Delta t.
\tag{20}
$$

任务集非空时，

$$
\bar L=\frac1{|\mathcal I|}
\sum_{i,r,s}\ell_{o_ir}x_{irs}.
\tag{21}
$$

若任务集为空，\(\bar L\) 输出 `not_applicable`，删除时延 ε 约束及排序维。

令

$$
R_\Sigma=\sum_{r,t\in\mathcal T_E}R_{rt}\Delta t.
\tag{22}
$$

仅当 \(R_\Sigma>0\) 时，

$$
U_{RE}=
\frac{\sum_{r,t\in\mathcal T_E}(U_{rt}+X_{rt}^{R})\Delta t}
{R_\Sigma}.
\tag{23}
$$

若 \(R_\Sigma=0\)，输出 `not_applicable`，删除 \(\varepsilon_U\) 和 Pareto 新能源维，不使用任意常数替代。

主模型为

$$
\min C_{op}
\tag{24}
$$

满足

$$
E_{CO2}\le\varepsilon_C,\quad
\bar L\le\varepsilon_L,\quad
U_{RE}\ge\varepsilon_U,
\tag{25}
$$

其中后两项仅在对应指标适用时启用，并同时满足式（2）—（5）、（13）、（16）—（18）。

### 求解方法

滚动窗口规则固定如下：窗口覆盖连续 \(168\) 小时，前 \(24\) 小时为冻结区；末个窗口延伸至 2406。已开工任务及其全部后续占用固定传递。对任务 \(i\)，若其最晚可行开工时刻

$$
s_i^{last}=\max_{r,s\in\mathcal S_{ir}}s
\tag{26}
$$

落入当前冻结区，则本窗必须确定其开工；若没有可行候选则结构化停止。窗口每次前移 24 小时，最终对拼接方案进行全时域复核。

ε 网格采用各单目标参考解形成的闭区间三点网格：理想端点、中点、可行劣化端点；只保留非支配可行解，不根据结果反向调参。若候选组合超过共享预算，按“成本基准、碳端点、时延端点、新能源端点、内部 ε 点”的固定顺序启动，未启动项标记 `not_run_due_to_budget`。

### 必须回答的输出

1. 每个任务的执行区域、开工、完成时刻和迁移时延。
2. 各区域逐小时 AI IT、总 IT、设施负荷、购电、新能源直接消纳、外送和弃电。
3. 总成本、碳排放、平均及 \(P_{95}\) 时延、新能源利用率或结构化不可用状态。
4. 相对基础调度的指标变化。
5. Pareto 解表及图。
6. 各类任务迁移、等待和截止统计。
7. 求解状态、间隙与最大约束残差。
8. 可执行调度策略。

## 子问题 3：给定负荷下的储能协同优化

### 模型思路

固定题面给定负荷：

$$
L_{rt}^{F}=\phi_r(L_{rt}^{BAI}+L_{rt}^{NA}).
\tag{27}
$$

只优化储能和能源分流。

### 模型建立

新能源守恒和设施平衡分别为

$$
U_{rt}+C_{rt}^{R}+X_{rt}^{R}+W_{rt}=R_{rt},
\tag{28}
$$

$$
I_{rt}+U_{rt}+D_{rt}
=L_{rt}^{F}+C_{rt}^{R}+C_{rt}^{G}.
\tag{29}
$$

新能源外送 \(X_{rt}^{R}\) 只出现在式（28），不在式（29）重复加入。两式合并可得附件总平衡：

$$
I_{rt}+R_{rt}+D_{rt}
=L_{rt}^{F}+C_{rt}^{R}+C_{rt}^{G}
+X_{rt}^{R}+W_{rt}.
\tag{30}
$$

绝对 SOC 满足

$$
S_{r,-1}=S_r^0,
\tag{31}
$$

$$
S_{rt}=S_{r,t-1}
+\eta_r^c(C_{rt}^{R}+C_{rt}^{G})\Delta t
-\frac{D_{rt}}{\eta_r^d}\Delta t.
\tag{32}
$$

对 \(t\in\mathcal T_E\)：

$$
S_r^{min}\le S_{rt}\le S_r^{max},\qquad
S_{r,2406}\ge S_r^0,
\tag{33}
$$

$$
C_{rt}^{R}+C_{rt}^{G}\le C_r^{max}z_{rt}^{c},
\quad
D_{rt}\le D_r^{max}(1-z_{rt}^{c}),
\quad z_{rt}^{c}\in\{0,1\}.
\tag{34}
$$

购售电边界为

$$
0\le I_{rt}\le I_{rt}^{max},\qquad
0\le X_{rt}^{R}\le X_{rt}^{max}.
\tag{35}
$$

因附件允许购电供负荷和新能源外送同时存在，不增加题面未要求的购售电互斥。

净购电、峰值和爬坡为

$$
N_{rt}=I_{rt}-X_{rt}^{R},
\tag{36}
$$

$$
N_{rt}\le P_r^{peak},\qquad P_r^{peak}\ge0,
\tag{37}
$$

$$
q_{rt}\ge N_{rt}-N_{r,t-1},\quad
q_{rt}\ge-(N_{rt}-N_{r,t-1}),\quad
V_r=\sum_{t=1}^{2406}q_{rt}.
\tag{38}
$$

新能源利用率在 \(R_\Sigma>0\) 时为

$$
U_{RE}=
\frac{\sum_{r,t}(U_{rt}+C_{rt}^{R}+X_{rt}^{R})\Delta t}
{R_\Sigma};
\tag{39}
$$

否则输出 `not_applicable`。

等效完整循环量按可用 SOC 窗口定义：

$$
N_r^{EFC}=
\frac{\sum_t[
\eta_r^c(C_{rt}^{R}+C_{rt}^{G})
+D_{rt}/\eta_r^d]\Delta t}
{2(S_r^{max}-S_r^{min})},
\quad S_r^{max}>S_r^{min}.
\tag{40}
$$

若可用窗口不为正，输出 `invalid_storage_bounds` 并停止该区域优化。

主模型为

$$
\min C_{op}
\quad\text{s.t.}\quad
E_{CO2}\le\varepsilon_C,\quad
P_r^{peak}\le\varepsilon_{P,r},\quad
V_r\le\varepsilon_{V,r}.
\tag{41}
$$

### 求解方法

比较无储能、附件基准、成本最小、碳最小、峰值最小和爬坡最小方案。连续 LP 仅作诊断基线；若出现同时充放电或无效循环，正式结果采用含式（34）的 MILP。所有指标从优化能源流重算。

### 必须回答的输出

1. 六区域第 \(0\sim2406\) 小时能源策略表。
2. 绝对 SOC 轨迹及终端状态。
3. 优化前后成本、碳排放、新能源利用率。
4. 峰值净购电及发生时刻。
5. 净购电绝对爬坡和可选标准差。
6. 等效循环量、充放电小时数、互斥违规数。
7. 能源平衡、SOC 递推残差和终端裕量。
8. 储能影响分析文件。

## 子问题 4：多区域算—储—电协同优化

### 模型思路

问题四联合使用任务变量与储能能源变量，采用与问题三完全一致的能源分源方程，避免错误向联合模型传播。

### 模型建立

设施负荷由联合调度产生：

$$
L_{rt}^{F}=
\phi_r\left[
L_{rt}^{NA}
+\sum_{i,s}g_ip_{k_i}
\frac{H_{it}(s)}{\Delta t}x_{irs}
\right].
\tag{42}
$$

任务侧满足式（2）—（5）、（13）；能源侧满足式（28）—（38）。所有任务约束只覆盖 \(\mathcal T_J\)，能源与 SOC 约束覆盖 \(\mathcal T_E\)。

对非空任务子集定义

$$
Q^{RT}=
\frac{\sum_{i\in\mathcal I_{RT}}\sum_rx_{ir,a_i}}
{|\mathcal I_{RT}|},
\tag{43}
$$

$$
Q^{SLA}=
\frac{\sum_{i,r,s}
\mathbf1(\ell_{o_ir}\le\ell_i^{max})x_{irs}}
{|\mathcal I|},
\quad
Q^{deadline}=
\frac{\sum_{i,r,s}
\mathbf1(s+d_i\le\min(f_i,2406))x_{irs}}
{|\mathcal I|}.
\tag{44}
$$

硬约束满足时，上述适用分项应为 1。对非实时任务，令总等待裕量

$$
W_\Sigma=
\sum_{i\notin\mathcal I_{RT}}
[\min(f_i,2406)-a_i-d_i].
\tag{45}
$$

仅当 \(W_\Sigma>0\) 时，

$$
\widetilde W=
\frac{\sum_{i,r,s}(s-a_i)x_{irs}}{W_\Sigma},
\qquad 0\le\widetilde W\le1.
\tag{46}
$$

定义适用分项集合 \(\mathcal A\)。实时任务为空时删除 \(Q^{RT}\)；全部任务为空时删除 \(Q^{SLA},Q^{deadline}\)；\(W_\Sigma=0\) 时删除等待分项。对 \(j\in\mathcal A\)：

$$
\bar w_j=\frac{w_j}{\sum_{m\in\mathcal A}w_m},
\qquad w_j\ge0,
\tag{47}
$$

$$
Q_{service}=
\bar w_{RT}Q^{RT}
+\bar w_{SLA}Q^{SLA}
+\bar w_DQ^{deadline}
+\bar w_W(1-\widetilde W).
\tag{48}
$$

不存在的分项不进入式（48）。因此 \(Q_{service}\in[0,1]\)。若 \(\mathcal A=\varnothing\)，输出 `not_applicable` 并删除服务质量约束和排序维。

联合优化为

$$
\min C_{op}
\tag{49}
$$

满足所有适用约束：

$$
E_{CO2}\le\varepsilon_C,\quad
\bar L\le\varepsilon_L,\quad
Q_{service}\ge\varepsilon_Q,\quad
U_{RE}\ge\varepsilon_U,\quad
P_r^{peak}\le\varepsilon_{P,r}.
\tag{50}
$$

对成本型指标，若 \(F_j^{nadir}>F_j^{ideal}\)：

$$
z_j=
\frac{F_j-F_j^{ideal}}
{F_j^{nadir}-F_j^{ideal}}.
\tag{51}
$$

效益型指标反向归一化。若两端相等，该维输出 `no_discrimination` 并从距离中删除。正式折中解为

$$
\arg\min_{m\in\mathcal P}
\sqrt{\sum_{j\in\mathcal J_{valid}}\omega_jz_{jm}^2},
\tag{52}
$$

其中 \(\mathcal P\) 为非支配可行解集，\(\mathcal J_{valid}\) 只含定义有效且有区分度的指标。

情景规则固定为：

$$
E_{CO2}\le(1-\delta_C)E_{CO2}^{base},
\quad \delta_C\in\{0,0.10,0.20\},
\tag{53}
$$

$$
c_{rt}^{buy,(\omega)}
=\bar c_r+\alpha_p^{(\omega)}
(c_{rt}^{buy}-\bar c_r),
\quad \alpha_p^{(\omega)}\in\{0.5,1,1.5\},
\tag{54}
$$

售电价格保持基准，以隔离购电峰谷机制；新能源设置：

$$
R_{rt}^{base}=R_{rt},\quad
R_{rt}^{up}=1.2R_{rt},\quad
R_{rt}^{down}=0.8R_{rt},
\tag{55}
$$

$$
R_{rt}^{volatile}
=\max\{0,\bar R_{r,h(t)}
+1.5[R_{rt}-\bar R_{r,h(t)}]\},
\tag{56}
$$

其中 \(\bar R_{r,h(t)}\) 是区域 \(r\) 与同一小时-of-day 的样本均值，可由附件直接复算。除研究因素外，任务、容量、PUE、时延、功率映射及初始 SOC 不变。

### 求解方法

沿用问题二的 168 小时窗口、24 小时冻结区和式（26）截止保护，并传递绝对 SOC。Pareto 参考解、ε 点和情景按固定顺序运行，不能根据中间结果追加任意网格。

### 共享运行预算与失败停止

Coder 单次执行统一使用

$$
B_{total}=300\text{ s},\qquad
T_{tail}=15\text{ s},\qquad
D_{search}=t_{start}+285\text{ s}.
\tag{57}
$$

使用 `time.monotonic()`。固定数据读取、问题一统计与预测、基础可行调度、必要文件输出及验收优先；问题二基准解、问题三基准解、问题四基准解随后运行；其余 ε 点和情景共享剩余时间。

每个固定任务、候选 MILP 和文件批次启动前均检查共同截止。可中断循环在内部重复检查；已启动候选只能越过 \(D_{search}\)，不能越过 \(t_{start}+300\) s。超出总截止的部分结果丢弃并记录实际耗时，不缩减固定必答工作后伪装完成。若基准可行解、能源守恒或状态衔接失败，则在对应问题结构化停止，后续依赖问题不得继续。

### 必须回答的输出

1. 正式折中方案完整任务调度表和迁移矩阵。
2. 六区域逐小时 GPU、AI IT、总 IT、设施负荷。
3. 六区域逐小时能源分配和绝对 SOC。
4. 成本、碳排放、时延、服务质量、新能源利用率。
5. 峰值净购电数值、区域和时刻。
6. Pareto 解集、理想点距离和折中依据。
7. 碳、电价、新能源情景比较表。
8. 各情景迁移、等待、循环、弃电和终端 SOC。
9. 相对基准的绝对与相对变化。
10. 可行性、求解状态、间隙和最大残差。
11. `q4_task_schedule.csv`、`q4_energy_dispatch.csv`、`q4_pareto.csv`、`q4_scenario_comparison.csv` 及相应图文件。

## 统一可观测性与验证规则

可观测变量包括任务、容量、PUE、时延、价格、碳强度、新能源、固定负荷和储能设备参数。真实全局最优调度、真实最优储能动作、主观满意度及退化成本不可观测。代理验证只使用约束残差、完成率、等待、时延、求解间隙、Pareto 非支配性和等效循环量。

正式方案检查：

$$
\left|\sum_{r,s}x_{irs}-1\right|\le\tau_{tol},
\tag{58}
$$

$$
\max_{r,t}
\left[
\sum_{i,s}g_i\frac{H_{it}(s)}{\Delta t}x_{irs}
-G_r^{max}
\right]_+
\le\tau_{tol}.
\tag{59}
$$

问题二能源残差为

$$
\max_{r,t}|U_{rt}+X_{rt}^{R}+W_{rt}-R_{rt}|
\le\tau_{tol},
\quad
\max_{r,t}|I_{rt}+U_{rt}-L_{rt}^{F}|
\le\tau_{tol}.
\tag{60}
$$

问题三、四能源残差为

$$
\max_{r,t}
|I_{rt}+R_{rt}+D_{rt}
-L_{rt}^{F}-C_{rt}^{R}-C_{rt}^{G}
-X_{rt}^{R}-W_{rt}|
\le\tau_{tol},
\tag{61}
$$

SOC 残差为

$$
\max_{r,t}
\left|
S_{rt}-S_{r,t-1}
-\eta_r^c(C_{rt}^{R}+C_{rt}^{G})\Delta t
+\frac{D_{rt}}{\eta_r^d}\Delta t
\right|
\le\tau_{tol}.
\tag{62}
$$

所有数值输出必须有限。零分母、空集合或无区分度指标输出结构化状态并排除相应约束和排序维；不得输出 `NaN`、`Inf`，也不得以任意 \(\epsilon\) 或常数伪造指标。

## 局限性

1. 任务持续时间及能源参数按确定值处理。
2. 通信仅含静态单向时延，不含题面明确排除的带宽、迁移能耗和费用。
3. PUE 使用区域常数。
4. 缺少储能退化成本，只报告按可用 SOC 窗口计算的等效循环量。
5. 滚动 MILP 可能只得到限时可行解；只有求解器证明时才称全局最优。
6. 购电供负荷与新能源外送可并存，因此采用显式分源模型，不增加未经题面授权的购售电互斥。
7. 所有附件专属数值、误差和最优方案均由后续代码从真实附件计算；本阶段不预填。

## Verifier 修复核对表

| Block issue | 修复位置 | 可计算性与物理保证 |
|---|---|---|
| q2 外送重复计入负荷侧 | 式（16）—（18） | 新能源外送只在新能源守恒出现；设施平衡固定为 \(I+U=L^F\)。 |
| q2 无 SOC 的自由新能源充电 | “子问题2—模型思路”及式（16）—（18） | q2 明确删除 \(C^R,C^G,D,S\)，不存在凭空吸收新能源的变量。 |
| q3 外送重复进入设施平衡 | 式（28）—（30） | \(X^R\) 只在新能源守恒出现；合并后严格恢复附件总平衡。 |
| 正文与 equations.json 不一致并传播至 q4 | equations.json 的 `energy_q2`、`energy_q34` 及正文式（16）—（18）、（28）—（30）、（42） | 三处采用同一唯一执行合同；q4 明确复用修正后的 q3 能源式。 |
| 服务质量可能为负且不在 \([0,1]\) | 式（43）—（48） | 等待项改为 \(1-\widetilde W\)，证明各适用分项在 \([0,1]\)，空集合按适用权重重归一化。 |
| 滚动窗口、截止保护、ε网格和情景缺少固定规则 | q2 求解方法、式（26）、q4 式（53）—（56） | 固定 168 h 窗口、24 h 冻结区、最晚开工保护、三点 ε 网格及有限情景。 |
| 多问题缺少共享总墙钟 | 式（57）及“共享运行预算与失败停止” | 固定 \(300\) s 总预算、\(15\) s 收尾和共同搜索截止；超时部分结果丢弃。 |
| 未执行代码却断言附件异常数量 | “统一时间、负荷与状态边界” | 删除确定数量，改为 `pending_code_execution`。 |
| q1 Huber 模型与结构化目标不一致、截断破坏标准凸拟合 | 式（9）—（11）及 equations.json q1 | 未截断线性输出参与 Huber-岭训练，仅最终输出截断；预测与调度为两个独立模型。 |
| 重叠“比例”与量纲不一致 | 式（1）、（3）、（5） | 改称重叠小时数，并显式除以 \(\Delta t\) 得平均占用比例。 |
| 零新能源、空任务和零量程会产生非法分母 | 式（12）、（21）—（23）、（43）—（52） | 每个分母均有正性条件；不满足时输出结构化不可用并移除对应约束和排序维。 |
| 峰值净购电可能取负 | 式（37） | 显式加入 \(P_r^{peak}\ge0\)。 |
| EFC 分母未使用可用 SOC 窗口 | 式（40） | 改为 \(2(S_r^{max}-S_r^{min})\)，边界无效时停止该区域优化。 |
| 非物理能源循环扭曲成本、碳与峰值 | 式（16）—（18）、（28）—（35） | q2 删除无状态充电；q3/q4 使用分源守恒、SOC 动态和充放电互斥。 |