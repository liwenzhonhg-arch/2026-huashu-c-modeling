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
| \(L_{rt}^{BAI}\) | 问题三给定的基准 AI IT 负荷 | 可观测输入 | MW，`Baseline_AI_IT_Load_MW` |
| \(L_{rt}^{IT},L_{rt}^{F}\) | 总 IT、设施负荷 | 派生量 | MW |
| \(R_{rt},U_{rt}\) | 可用、直接消纳新能源 | 输入/变量 | MW |
| \(C_{rt}^{R},C_{rt}^{G}\) | 新能源、电网充电功率 | q3、q4变量 | MW |
| \(D_{rt}\) | 储能放电功率 | q3、q4变量 | MW |
| \(I_{rt},X_{rt}^{R},W_{rt}\) | 购电、新能源外送、弃电 | 变量 | MW |
| \(S_{rt},S_r^0\) | 时段末 SOC、初始 SOC | 状态/参数 | MWh |
| \(\eta_r^c,\eta_r^d\) | 充、放电效率 | 可观测参数 | \((0,1]\)，无量纲 |
| \(C_r^{\max},D_r^{\max}\) | 最大充、放电功率 | 可观测参数 | MW |
| \(S_r^{min},S_r^{max}\) | SOC 上、下界 | 可观测参数 | MWh |
| \(I_{rt}^{max},X_{rt}^{max}\) | 最大购电、外送功率 | 可观测参数 | MW |
| \(c_{rt}^{buy},c_{rt}^{sell}\) | 购、售电价 | 可观测参数 | 元/MWh |
| \(\kappa_{rt}\) | 电网碳强度 | 可观测参数 | tCO2/MWh |
| \(N_{rt}\) | 净购电 \(I_{rt}-X_{rt}^{R}\) | 派生量 | MW |
| \(P_r^{peak}\) | 非负峰值净购电指标 | 辅助变量 | MW，\(P_r^{peak}\ge0\) |
| \(q_{rt},V_r\) | 绝对爬坡及累计绝对爬坡 | 辅助量 | MW |
| \(C_{op},E_{CO2},U_{RE}\) | 成本、碳排放、新能源利用率 | 指标 | 元、tCO2、无量纲 |
| \(Q_{service}\) | 服务质量指标 | 指标 | \([0,1]\)，只聚合适用分项 |
| \(\varepsilon_C,\varepsilon_L,\varepsilon_U\) | 碳、时延、新能源利用率门槛 | 预声明参数 | 由同一可行域参考解生成 |
| \(\varepsilon_{P,r},\varepsilon_{V,r}\) | 峰值和爬坡门槛 | 预声明参数 | MW |
| \(\varepsilon_Q\) | 服务质量下限 | 预声明参数 | 无量纲 |
| \(\tau_{tol}\) | 数值约束残差容差 | 运行合同参数 | 求解前固定，单位随约束 |
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

\(H_{it}(s)\) 的单位是小时，小时平均占用比例为 \(H_{it}(s)/\Delta t\)。候选开工集合为

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

特征向量为

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

数据划分为 \(0\sim2351\) 训练、\(2352\sim2375\) 验证；选定结构后用 \(0\sim2375\) 重拟合唯一正式参数，并测试 \(2376\sim2399\)。

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

若 \(G_r^{\max}\le0\)，该区域利用率输出 `not_applicable`；若同时存在要求在该区域执行的任务，则输出 `input_infeasible`。

### 求解方法

季节性朴素预测作为基线；增强模型仅在验证集 MAE 或有效 WAPE 改善时采用。调度先按实时优先、最早截止、短任务优先生成可行热启动，再运行 MILP。没有完整 MILP 可行解时，只能退回已通过全部硬约束的启发式方案并标记 `heuristic_feasible`。

### 必须回答的输出

1. 六区域、三任务类型的任务数、GPU 总量、GPU-hour、分位数、持续时长、峰值并发和周期统计。
2. 验证集与测试集的分区域、分类型及总体 MAE、RMSE、WAPE 或 `not_applicable`。
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
0\le X_{rt}^{R}\le X_{rt}^{\max}.
\tag{18}
$$

式（16）确保外送只来自新能源；\(X_{rt}^{R}\) 不进入式（17），从而不重复计量。问题二不存在 \(C_{rt}^{R}\)、\(C_{rt}^{G}\)、\(D_{rt}\) 或 \(S_{rt}\)。

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

若任务集为空，\(\bar L\) 输出 `not_applicable`，删除时延约束及排序维。

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

若 \(R_\Sigma=0\)，输出 `not_applicable`，删除 \(\varepsilon_U\) 和 Pareto 新能源维。

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

滚动窗口覆盖连续 \(168\) 小时，前 \(24\) 小时为冻结区；末个窗口延伸至 2406。已开工任务及其全部后续占用固定传递。对任务 \(i\)，若其最晚可行开工时刻

$$
s_i^{last}=\max_{r,s\in\mathcal S_{ir}}s
\tag{26}
$$

落入当前冻结区，则本窗必须确定其开工；若候选集合为空则结构化停止。窗口每次前移 24 小时，最终对拼接方案进行全时域复核。

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

只优化储能、购售电和新能源分流。新能源充电 \(C_{rt}^{R}\) 先从新能源可用量中分配，因此不能再次作为负荷侧需要由 \(I_{rt}+U_{rt}+D_{rt}\) 供应的需求。

### 模型建立

新能源分配守恒为

$$
U_{rt}+C_{rt}^{R}+X_{rt}^{R}+W_{rt}=R_{rt}.
\tag{28}
$$

修正后的负荷侧平衡为

$$
I_{rt}+U_{rt}+D_{rt}
=L_{rt}^{F}+C_{rt}^{G}.
\tag{29}
$$

式（29）右侧只包含电网充电 \(C_{rt}^{G}\)。新能源充电 \(C_{rt}^{R}\) 已在式（28）中由 \(R_{rt}\) 分配，不能在式（29）重复计入。

将式（28）代入式（29），严格得到附件统一总平衡：

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

同时要求全部能源流非负，并满足

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

其中 \(C_{op}\) 与 \(E_{CO2}\) 分别按式（19）、（20）计算。

### 求解方法

比较无储能、附件基准、成本最小、碳最小、峰值最小和爬坡最小方案。连续 LP 仅作诊断基线；若出现同时充放电或无效循环，正式结果采用含式（34）的 MILP。所有指标从优化能源流重算。

验收同时检查以下三套相容残差：

$$
e_{rt}^{R}=U_{rt}+C_{rt}^{R}+X_{rt}^{R}+W_{rt}-R_{rt},
\tag{42}
$$

$$
e_{rt}^{L}=I_{rt}+U_{rt}+D_{rt}-L_{rt}^{F}-C_{rt}^{G},
\tag{43}
$$

$$
e_{rt}^{B}=I_{rt}+R_{rt}+D_{rt}
-L_{rt}^{F}-C_{rt}^{R}-C_{rt}^{G}-X_{rt}^{R}-W_{rt}.
\tag{44}
$$

要求

$$
\max_{r,t}|e_{rt}^{R}|\le\tau_{tol},\quad
\max_{r,t}|e_{rt}^{L}|\le\tau_{tol},\quad
\max_{r,t}|e_{rt}^{B}|\le\tau_{tol}.
\tag{45}
$$

由式（28）—（30）可知三者相容，且 \(C_{rt}^{R}\) 只计量一次。

### 必须回答的输出

1. 六区域第 \(0\sim2406\) 小时能源策略表。
2. 绝对 SOC 轨迹及终端状态。
3. 优化前后成本、碳排放、新能源利用率。
4. 峰值净购电及发生时刻。
5. 净购电绝对爬坡和可选标准差。
6. 等效循环量、充放电小时数、互斥违规数。
7. 新能源分配、负荷侧分源、总能源平衡、SOC 递推残差和终端裕量。
8. 储能影响分析文件。

## 子问题 4：多区域算—储—电协同优化

### 模型思路

问题四联合使用任务变量与储能能源变量，并复用问题三修正后的唯一分源合同：新能源充电只在新能源分配式和 SOC 式中出现，不再进入负荷侧平衡。

### 模型建立

设施负荷由联合调度产生：

$$
L_{rt}^{F}=
\phi_r\left[
L_{rt}^{NA}
+\sum_{i,s}g_ip_{k_i}
\frac{H_{it}(s)}{\Delta t}x_{irs}
\right].
\tag{46}
$$

任务侧满足式（2）—（5）、（13）；能源侧满足修正后的式（28）—（38）。具体而言，问题四必须同时满足

$$
U_{rt}+C_{rt}^{R}+X_{rt}^{R}+W_{rt}=R_{rt},
\tag{47}
$$

$$
I_{rt}+U_{rt}+D_{rt}=L_{rt}^{F}+C_{rt}^{G},
\tag{48}
$$

以及由式（47）—（48）推出的总平衡

$$
I_{rt}+R_{rt}+D_{rt}
=L_{rt}^{F}+C_{rt}^{R}+C_{rt}^{G}
+X_{rt}^{R}+W_{rt}.
\tag{49}
$$

所有任务约束只覆盖 \(\mathcal T_J\)，能源与 SOC 约束覆盖 \(\mathcal T_E\)。式（47）—（49）构成问题四唯一执行合同，不再引用旧的、把 \(C_{rt}^{R}\) 重复列为负荷需求的方程。

对非空任务子集定义

$$
Q^{RT}=
\frac{\sum_{i\in\mathcal I_{RT}}\sum_rx_{ir,a_i}}
{|\mathcal I_{RT}|},
\tag{50}
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
\tag{51}
$$

硬约束满足时，上述适用分项应为 1。对非实时任务，令总等待裕量

$$
W_\Sigma=
\sum_{i\notin\mathcal I_{RT}}
[\min(f_i,2406)-a_i-d_i].
\tag{52}
$$

仅当 \(W_\Sigma>0\) 时，

$$
\widetilde W=
\frac{\sum_{i\notin\mathcal I_{RT}}\sum_{r,s}(s-a_i)x_{irs}}
{W_\Sigma},
\qquad 0\le\widetilde W\le1.
\tag{53}
$$

定义适用分项集合 \(\mathcal A\)。实时任务为空时删除 \(Q^{RT}\)；全部任务为空时删除 \(Q^{SLA},Q^{deadline}\)；\(W_\Sigma=0\) 时删除等待分项。对 \(j\in\mathcal A\)：

$$
\bar w_j=\frac{w_j}{\sum_{m\in\mathcal A}w_m},
\qquad w_j\ge0.
\tag{54}
$$

只有当 \(\sum_{m\in\mathcal A}w_m>0\) 时定义归一化权重；否则服务质量输出 `not_applicable` 并从约束及排序维删除。

$$
Q_{service}=
\bar w_{RT}Q^{RT}
+\bar w_{SLA}Q^{SLA}
+\bar w_DQ^{deadline}
+\bar w_W(1-\widetilde W).
\tag{55}
$$

不存在的分项不进入式（55），故 \(Q_{service}\in[0,1]\)。

联合优化为

$$
\min C_{op}
\tag{56}
$$

满足所有适用约束：

$$
E_{CO2}\le\varepsilon_C,\quad
\bar L\le\varepsilon_L,\quad
Q_{service}\ge\varepsilon_Q,\quad
U_{RE}\ge\varepsilon_U,\quad
P_r^{peak}\le\varepsilon_{P,r}.
\tag{57}
$$

对成本型指标，若 \(F_j^{nadir}>F_j^{ideal}\)：

$$
z_j=
\frac{F_j-F_j^{ideal}}
{F_j^{nadir}-F_j^{ideal}}.
\tag{58}
$$

其中 \(F_j^{ideal}\) 为同一可行域内指标 \(j\) 的单目标最优值，\(F_j^{nadir}\) 为已求得非支配可行解集中该指标的最差有限值。效益型指标反向归一化。若两端相等，该维输出 `no_discrimination` 并从距离中删除。

正式折中解为

$$
\arg\min_{m\in\mathcal P}
\sqrt{\sum_{j\in\mathcal J_{valid}}\omega_jz_{jm}^2},
\tag{59}
$$

其中 \(\mathcal P\) 为非支配可行解集，\(\mathcal J_{valid}\) 只含定义有效且有区分度的指标，\(\omega_j\ge0\) 且在有效指标上归一化。若 \(\mathcal J_{valid}=\varnothing\)，输出 `no_discriminating_metric`，不虚构折中排序。

情景规则固定为：

$$
E_{CO2}\le(1-\delta_C)E_{CO2}^{base},
\quad \delta_C\in\{0,0.10,0.20\},
\tag{60}
$$

其中 \(E_{CO2}^{base}\) 为同一模型在基准价格、基准新能源及无附加碳收紧情景下得到的有限可行排放量；若基准场景不可行，问题四结构化停止，不生成碳约束情景。

$$
c_{rt}^{buy,(\omega)}
=\bar c_r+\alpha_p^{(\omega)}
(c_{rt}^{buy}-\bar c_r),
\quad \alpha_p^{(\omega)}\in\{0.5,1,1.5\},
\tag{61}
$$

其中

$$
\bar c_r=\frac{1}{|\mathcal T_E|}
\sum_{t\in\mathcal T_E}c_{rt}^{buy}.
\tag{62}
$$

售电价格保持基准，以隔离购电峰谷机制；新能源设置：

$$
R_{rt}^{base}=R_{rt},\quad
R_{rt}^{up}=1.2R_{rt},\quad
R_{rt}^{down}=0.8R_{rt},
\tag{63}
$$

$$
R_{rt}^{volatile}
=\max\{0,\bar R_{r,h(t)}
+1.5[R_{rt}-\bar R_{r,h(t)}]\},
\tag{64}
$$

其中 \(\bar R_{r,h(t)}\) 是区域 \(r\) 与同一小时-of-day 的样本均值，可由附件直接复算。除研究因素外，任务、容量、PUE、时延、功率映射及初始 SOC 不变。

### 求解方法

沿用问题二的 168 小时窗口、24 小时冻结区和式（26）截止保护，并传递绝对 SOC。Pareto 参考解、ε 点和情景按固定顺序运行，不能根据中间结果追加任意网格。

问题四验收复用式（42）—（45），但其中 \(L_{rt}^{F}\) 按式（46）由联合任务调度计算。若新能源分配残差、负荷侧分源残差、总平衡残差或 SOC 递推残差任一超过 \(\tau_{tol}\)，该候选不得进入 Pareto 集、情景比较或正式结果。

### 共享运行预算与失败停止

Coder 单次执行统一使用

$$
B_{total}=300\text{ s},\qquad
T_{tail}=15\text{ s},\qquad
D_{search}=t_{start}+285\text{ s}.
\tag{65}
$$

使用 `time.monotonic()`。固定数据读取、问题一统计与预测、基础可行调度、必要文件输出及验收优先；问题二基准解、问题三基准解、问题四基准解随后运行；其余 ε 点和情景共享剩余时间。

每个固定任务、候选 MILP 和文件批次启动前均检查共同截止。可中断循环在内部重复检查；已启动候选只能越过 \(D_{search}\)，不能越过 \(t_{start}+300\) s。超出总截止的部分结果丢弃并记录实际耗时，不缩减固定必答工作后伪装完成。若基准可行解、式（28）—（30）或式（47）—（49）的能源守恒、SOC 状态衔接失败，则在对应问题结构化停止，后续依赖问题不得继续。

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
\tag{66}
$$

$$
\max_{r,t}
\left[
\sum_{i,s}g_i\frac{H_{it}(s)}{\Delta t}x_{irs}
-G_r^{max}
\right]_+
\le\tau_{tol}.
\tag{67}
$$

问题二能源残差为

$$
\max_{r,t}|U_{rt}+X_{rt}^{R}+W_{rt}-R_{rt}|
\le\tau_{tol},
\quad
\max_{r,t}|I_{rt}+U_{rt}-L_{rt}^{F}|
\le\tau_{tol}.
\tag{68}
$$

问题三、四除检查总平衡外，必须检查两条原始分源方程：

$$
\max_{r,t}
|U_{rt}+C_{rt}^{R}+X_{rt}^{R}+W_{rt}-R_{rt}|
\le\tau_{tol},
\tag{69}
$$

$$
\max_{r,t}
|I_{rt}+U_{rt}+D_{rt}-L_{rt}^{F}-C_{rt}^{G}|
\le\tau_{tol},
\tag{70}
$$

$$
\max_{r,t}
|I_{rt}+R_{rt}+D_{rt}
-L_{rt}^{F}-C_{rt}^{R}-C_{rt}^{G}
-X_{rt}^{R}-W_{rt}|
\le\tau_{tol}.
\tag{71}
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
\tag{72}
$$

式（69）与式（70）相加并消去 \(U_{rt}\) 后即得式（71），因此模型定义与验收合同一致，不再要求 \(C_{rt}^{R}=0\)。

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

| Block issue | 修复公式/约束位置 | 可计算性与物理保证 |
|---|---|---|
| 问题三式（28）与原式（29）合并后重复计入 \(C_{rt}^{R}\) | 保留式（28），将负荷侧平衡修正为式（29）：\(I_{rt}+U_{rt}+D_{rt}=L_{rt}^{F}+C_{rt}^{G}\) | \(C_{rt}^{R}\) 只在新能源分配式和 SOC 递推中出现；不再作为需要由购电、直接新能源或放电再次供应的负荷。 |
| 原式不能推出声称的总平衡 | 式（30） | 将修正后的式（28）代入式（29），可严格推出 \(I+R+D=L^F+C^R+C^G+X^R+W\)，每条能源流只计量一次。 |
| 问题四复用错误的 q3 能源方程 | 式（47）—（49） | 问题四显式写出修正后的新能源分配式、负荷侧平衡式和推导总平衡，不再引用含重复计量的旧合同。 |
| q3/q4 原始分源方程与验收式不一致 | 式（42）—（45）、式（69）—（71） | 同时检查新能源分配残差、负荷侧分源残差和总平衡残差；三者代数相容，非零新能源充电可正常通过验收。 |
| 重复计量可能制造虚假能源需求、增加购电或弃电并压制新能源充电 | 式（28）—（30）、式（47）—（49）及 SOC 式（32） | 新能源充电从 \(R_{rt}\) 中分配，并以 \(\eta_r^cC_{rt}^{R}\Delta t\) 唯一进入 SOC；既不凭空增加设施需求，也不丢失其储能贡献。 |