# 数学模型

## 1. 模型边界与统一口径

区域集合为

$$
\mathcal R=\{\mathrm A,\mathrm B,\mathrm C,\mathrm D,\mathrm E,\mathrm F\}.
$$

任务到达、执行和能源结算时域分别为

$$
\mathcal T^{arr}=\{0,\ldots,2399\},\qquad
\mathcal T^{run}=\{0,\ldots,2405\},
$$

$$
\mathcal T^{energy}=\{0,\ldots,2406\},\qquad
\Delta t=1\ \mathrm h.
$$

第 $2400$–$2405$ 小时不产生新任务，只结清弹性任务；第 $2406$ 小时不执行任务，只进行电力和终端 SOC 结算。原始字段 `EstimatedDuration_min` 在进入任何重叠、GPU-hour、功率或截止约束前统一换算为 $d_i=\mathrm{EstimatedDuration\_min}_i/60$ h。所有任务不可抢占、不可拆分、不可中途迁移。

本题不涉及容器或空间尺寸链。六区域及功能定位为题面直接给定；区域间通信关系使用附件中的有向时延矩阵。物理距离和线路拓扑待确认且题面明确不要求，网络带宽、迁移数据量、传输能耗和传输费用由题面明确排除。

## 2. 符号说明

| 符号 | 含义 | 类型 | 取值范围或单位 |
|------|------|------|----------|
| $i,r,t,s,k$ | 任务、区域、小时、开工小时、任务类型索引 | 索引 | 附件集合 |
| $\mathcal I^{flex}$ | 批量推理和 AI 训练任务集合 | 派生集合 | $\mathcal I$ 子集 |
| $a_i,d_i,g_i$ | 到达时刻、连续执行时长、持续占用 GPU | 可观测参数 | h、h、等效 GPU |
| $k_i,o_i$ | 任务类型、来源区域 | 可观测参数 | 附件类别 |
| $f_i^{late}$ | 最晚完成时点；缺失时依题面规则核验后取 $2406$ | 可观测参数 | h |
| $\ell_i^{max},\ell_{or}$ | 最大允许时延、来源区至执行区单向时延 | 可观测参数 | ms |
| $x_{irs}$ | 任务是否在区域 $r$、小时 $s$ 开工 | 二元变量 | $\{0,1\}$ |
| $\omega_{it}(s)$ | 任务与小时 $t$ 的重叠时长 | 派生参数 | $[0,1]$ h |
| $G_r^{max}$ | 可调度 GPU 容量 | 可观测参数 | 等效 GPU |
| $p_k^{GPU}$ | 每等效 GPU 平均 IT 功率 | 可观测参数 | MW/GPU |
| $P_{rt}^{AI},P_{rt}^{NA},P_{rt}^{BAI}$ | 调度 AI、固定非 AI、问题三基线 AI IT 功率 | 派生量/参数 | MW |
| $P_{rt}^{IT},P_{rt}^{fac}$ | 总 IT、设施平均功率 | 派生变量 | MW |
| $P_r^{IT,max},P_r^{fac,max}$ | IT、设施功率上限 | 可观测参数 | MW |
| $\mathrm{PUE}_r$ | 区域 PUE | 可观测参数 | 无量纲 |
| $R_{rt}^{av},R_{rt}^{use}$ | 可用新能源、新能源直接供负荷功率 | 参数/变量 | MW |
| $C_{rt}^{RE},C_{rt}^{G},C_{rt}$ | 新能源充电、电网充电、总充电功率 | 变量/派生量 | MW |
| $D_{rt}$ | 储能放电功率 | 连续变量 | MW |
| $B_{rt},S_{rt},K_{rt}$ | 电网购电、新能源外送、弃电功率 | 连续变量 | MW |
| $P_{rt}^{grid,max}$ | 区域购电上限 | 可观测参数 | MW |
| $P_{rt}^{export,q2},P_{rt}^{export,max},S_r^{max}$ | 问题二由新能源可用量导出的外送上界、问题三四外送边界、储能表外送上限 | 可观测参数 | MW |
| $E_{rt},E_r^0$ | 时段末绝对 SOC、初始 SOC | 状态/参数 | MWh |
| $E_r^{min},E_r^{max}$ | SOC 下限和上限 | 可观测参数 | MWh |
| $C_r^{max},D_r^{max}$ | 最大充、放电功率 | 可观测参数 | MW |
| $\eta_r^c,\eta_r^d$ | 充、放电效率 | 可观测参数 | $(0,1]$ |
| $u_{rt}^c$ | 充放电模式变量 | 二元变量 | $\{0,1\}$ |
| $N_{rt}$ | 净购电功率，$B_{rt}-S_{rt}$ | 派生变量 | MW |
| $P_r^{peak}$ | 峰值约束辅助变量，不作为正式报告值 | 辅助变量 | MW |
| $\widehat P_r^{peak}$ | 由最终净购电序列复算的正向峰值 | 正式指标 | MW |
| $z_{rt},V$ | 净购电绝对变化辅助量及总爬坡量 | 辅助量/指标 | MW |
| $\pi_{rt}^{buy},\pi_{rt}^{sell}$ | 购、售电价 | 可观测参数 | 元/MWh |
| $c_{rt}$ | 电网购电碳强度 | 可观测参数 | tCO2/MWh |
| $C_{op},E_{CO2}$ | 运行成本、累计碳排放 | 目标/指标 | 元、tCO2 |
| $A_L,W_L,L_{net}$ | 时延加权和、总 GPU-hour 权重、平均时延 | 派生指标 | GPU·h·ms、GPU·h、ms |
| $A_U,W_U,U_{RE}$ | 新能源利用量、可用量、利用率 | 派生指标 | MWh、MWh、无量纲 |
| $M_W,Q_{service}$ | 最大总等待余量、服务质量代理 | 派生量/代理 | h、无量纲 |
| $A_C^{(j)}$ | 截至第 $j$ 个提交区的累计碳排放 | 滚动状态 | tCO2 |
| $A_L^{(j)}$ | 已提交任务的时延加权和 | 滚动状态 | GPU·h·ms |
| $A_U^{(j)}$ | 已提交小时的新能源利用量 | 滚动状态 | MWh |
| $A_W^{(j)}$ | 已提交弹性任务的累计等待时间 | 滚动状态 | h |
| $\underline A_{L,rem}^{(j)}$ | 未提交任务最小可达时延加权和 | 确定性下界 | GPU·h·ms |
| $\overline A_{U,rem}^{(j)}$ | 未提交小时最大可利用新能源量 | 确定性上界 | MWh |
| $\underline A_{W,rem}^{(j)}$ | 未提交弹性任务最小可达等待量 | 确定性下界 | h |
| $H,O,F$ | 窗口、重叠区、每轮提交区长度 | 固定参数 | $168,24,144$ h |
| $B_{total},T_{tail},D_{search}$ | 总预算、尾部预留、搜索截止 | 固定规则 | $300$ s、$15$ s、$t_{start}+285$ s |

任务需求、容量、PUE、功率映射、时延、电力参数和储能参数均可观测。真实最优调度、储能动作和用户满意度不可观测，因此不使用监督学习准确率、召回率或混淆矩阵；验证口径为硬约束残差、状态连续性、指标复算和 Pareto 非支配性。

## 3. 共享任务与负荷模型

任务 $i$ 在 $s$ 开工时，执行区间为 $[s,s+d_i)$，与小时 $[t,t+1)$ 的重叠时长为

$$
\omega_{it}(s)=
\max\{0,\min(s+d_i,t+1)-\max(s,t)\}. \tag{1}
$$

候选开工集合为

$$
\mathcal S_{ir}=
\left\{
s\in\mathcal T^{run}:
s\ge a_i,\ 
s+d_i\le\min(f_i^{late},2406),\
\ell_{o_i r}\le\ell_i^{max}
\right\}. \tag{2}
$$

实时推理满足 $\mathcal S_{ir}\subseteq\{a_i\}$。若某任务在全部区域的候选集合均为空，则输出 `infeasible_precheck` 并停止相应调度。

每个任务唯一执行：

$$
\sum_{r\in\mathcal R}\sum_{s\in\mathcal S_{ir}}x_{irs}=1,
\qquad x_{irs}\in\{0,1\}. \tag{3}
$$

小时 GPU-hour 及容量约束为

$$
G_{rt}=\sum_i\sum_{s\in\mathcal S_{ir}}
g_i\omega_{it}(s)x_{irs}, \tag{4}
$$

$$
G_{rt}\le G_r^{max}\Delta t. \tag{5}
$$

AI IT 平均功率必须显式除以时间步长：

$$
P_{rt}^{AI}=
\sum_i\sum_{s\in\mathcal S_{ir}}
g_ip_{k_i}^{GPU}
\frac{\omega_{it}(s)}{\Delta t}x_{irs}. \tag{6}
$$

问题一、二、四采用

$$
P_{rt}^{IT}=P_{rt}^{NA}+P_{rt}^{AI},\qquad
P_{rt}^{fac}=\mathrm{PUE}_rP_{rt}^{IT}, \tag{7}
$$

$$
P_{rt}^{IT}\le P_r^{IT,max},\qquad
P_{rt}^{fac}\le P_r^{fac,max}. \tag{8}
$$

第 $2406$ 小时禁止任务占用：

$$
\omega_{i,2406}(s)x_{irs}=0. \tag{9}
$$

## 子问题 1：GPU 需求预测与最后 24 小时基础调度

### 模型思路

采用具有固定历史长度的正则化回归预测区域—任务类型逐小时需求。为消除早期滞后特征未定义问题，只在具有完整 $168$ 小时历史的样本上拟合。预测仅用于精度评价，最后 24 小时调度仍以实际任务为输入。

### 模型建立

到达 GPU 与 GPU-hour 为

$$
D_{rkt}=\sum_{i:o_i=r,k_i=k,a_i=t}g_i, \tag{10}
$$

$$
H_{rkt}=\sum_{i:o_i=r,k_i=k,a_i=t}g_id_i. \tag{11}
$$

季节性基线为

$$
\widehat D_{rkt}^{(24)}=D_{rk,t-24},\qquad
\widehat D_{rkt}^{(168)}=D_{rk,t-168}. \tag{12}
$$

历史均值严格使用预测时点以前的数据：

$$
\overline D_{rk,t}^{(h)}
=\frac1h\sum_{j=1}^{h}D_{rk,t-j},
\qquad h\in\{24,168\}. \tag{13}
$$

特征向量为

$$
\boldsymbol\phi_{rkt}=
\left[
D_{rk,t-1},D_{rk,t-24},D_{rk,t-168},
\overline D_{rk,t}^{(24)},\overline D_{rk,t}^{(168)},
\sin\frac{2\pi t}{24},\cos\frac{2\pi t}{24},
\sin\frac{2\pi t}{168},\cos\frac{2\pi t}{168}
\right]^\top. \tag{14}
$$

有效训练集明确限定为

$$
\mathcal T_{train}^{*}=\{168,\ldots,2351\}. \tag{15}
$$

不定义负时刻数据，不用未来值、跨边界回填或任意常数补齐早期特征。验证和测试均采用固定预测起点的 24 小时递归预测：验证起点为 2352，只能使用 $t\le2351$ 的真实观测；测试起点为 2376，只能使用 $t\le2375$ 的真实观测。预测区间内若式（13）–（14）需要较早时点，则使用本轮已经生成的预测值递推，严禁读取验证或测试区间内的真实需求作为后续小时特征。

回归模型为

$$
\min_{\beta_{0,rk},\boldsymbol\beta_{rk}}
\sum_{t\in\mathcal T_{train}^{*}}
\rho_{\delta_H}\!\left(
D_{rkt}-\beta_{0,rk}
-\boldsymbol\beta_{rk}^{\top}\boldsymbol\phi_{rkt}
\right)
+\lambda\|\boldsymbol\beta_{rk}\|_2^2, \tag{16}
$$

$$
\widehat D_{rkt}=
\max\left\{0,
\beta_{0,rk}+\boldsymbol\beta_{rk}^{\top}\boldsymbol\phi_{rkt}
\right\}. \tag{17}
$$

$\lambda$ 固定从 $\{0,10^{-4},10^{-3},10^{-2},10^{-1},1\}$ 选择。对每个区域—任务类型训练序列，令 $\sigma_{rk}=\max\{1,1.4826\,\mathrm{MAD}(D_{rk,t})\}$，Huber 参数固定从 $\delta_H/\sigma_{rk}\in\{0.5,1,1.5,2\}$ 选择。只在 $2352$–$2375$ 验证集上按“可计算 WAPE 最小、MAE 最小、$\lambda$ 较小、$\delta_H/\sigma_{rk}$ 较小”的字典序唯一选型；若该分组 WAPE 不可计算，则从 MAE 开始比较。不能使用测试集或最终优化结果调整。增强模型与两个季节基线的最终选择也固定：对每个区域—任务类型，在固定起点递归验证集上按“可计算 WAPE、MAE、模型优先序”的字典序最小化，完全相同时优先序为 24 小时季节基线、168 小时季节基线、增强回归。若 WAPE 不可计算则从 MAE 比较。仅当增强回归胜出时用 $168$–$2375$ 重训；否则保留胜出的季节基线。

误差指标为

$$
\mathrm{MAE}=\frac1n\sum_t|D_t-\widehat D_t|,
\qquad
\mathrm{RMSE}=
\sqrt{\frac1n\sum_t(D_t-\widehat D_t)^2}. \tag{18}
$$

当 $\sum_tD_t>0$ 时，

$$
\mathrm{WAPE}=
\frac{\sum_t|D_t-\widehat D_t|}{\sum_tD_t}. \tag{19}
$$

否则该分组 WAPE 输出“验证不可用”，改报 MAE、RMSE 和可计算的总体 WAPE。

对任意两个序列 $X,Y$，先删除非有限值并形成成对有效样本。仅当有效样本数 $n_{XY}\ge2$ 且两序列样本方差均为正时计算 Pearson 相关系数：

$$
\rho_{XY}=
\frac{\sum_{j=1}^{n_{XY}}(X_j-\bar X)(Y_j-\bar Y)}
{\sqrt{\sum_j(X_j-\bar X)^2}
 \sqrt{\sum_j(Y_j-\bar Y)^2}}. \tag{20}
$$

否则输出 `correlation_unavailable`，不得输出 `NaN`、`Inf` 或宣称相关性验证通过。

滞后 $h$ 的自相关仅在成对有效样本数至少为 $2$ 且原序列与滞后序列方差均为正时计算：

$$
\operatorname{ACF}_h(X)
=\operatorname{Corr}\bigl((X_{h+1},\ldots,X_n),
(X_1,\ldots,X_{n-h})\bigr). \tag{21}
$$

否则输出 `autocorrelation_unavailable`。缺失值必须先按成对删除处理；不得用任意常数填充后计算相关系数。

基础调度目标为

$$
\min
\sum_i\sum_{r,s}
x_{irs}
\left[
\alpha_{k_i}(s-a_i)+\beta_{k_i}\ell_{o_i r}
\right], \tag{22}
$$

其中先按任务类型计算 $S_k=\operatorname{median}_i\max\{1,f_i^{late}-d_i-a_i\}$ h、$L_k=\operatorname{median}_i\max\{1,\ell_i^{max}\}$ ms，并固定 $u_{RT}=0,u_{Batch}=0.5,u_{Training}=0.7$；取 $\alpha_k=u_k/S_k$、$\beta_k=(1-u_k)/L_k$。因此式（22）无量纲，且权重完全由输入和预声明常数生成，不按结果调参；同值解按 `TaskID`、执行区域、开工小时字典序确定。并满足式（1）–（9）。GPU 利用率为

$$
U_{rt}^{GPU}=
\frac{G_{rt}}{G_r^{max}\Delta t}\times100\%. \tag{23}
$$

### 求解方法

先用“实时优先—最早截止时间优先—短任务优先”生成可行热启动，再求解 MILP。增强预测只有在验证集达到预声明选择规则后才进入最终重训，否则使用季节性基线。若 MILP 求解器证明不可行，则直接输出结构化不可行证书，不再声称启发式可满足同一硬约束；若只是达到时间上限且没有 incumbent，才允许报告经全部硬约束残差验证通过的热启动启发式解，并明确标记 `feasible_heuristic_timeout`。

### 必须回答的输出

1. 区域—任务类型任务数、GPU 总量、GPU-hour、分位数、持续时间、周期、自相关和区域相关性；不可计算项必须附状态及原因。
2. 验证集和测试集总体及分组 MAE、RMSE、WAPE。
3. 第 $2376$–$2399$ 小时实际任务的执行区域、开工和完成时刻。
4. 第 $2400$–$2405$ 小时末端任务及结清时刻。
5. 任务级甘特图和各区域逐小时 GPU 利用率。
6. 文件：`q1_forecast_metrics.csv`、`q1_schedule.csv`、`q1_gpu_utilization.csv`、`q1_gantt.png`。
7. 结果等级：最优解、限时可行解或启发式可行解。

## 子问题 2：碳感知任务调度

### 模型思路

以实际任务和逐时电力参数为输入，通过带全时域累计预算和唯一提交区的滚动 ε-约束 MILP 决定执行区域与开工时间。问题二不配置储能。

### 模型建立

任务约束沿用式（1）–（9）。能源平衡为

$$
B_{rt}+R_{rt}^{use}=P_{rt}^{fac}, \tag{24}
$$

$$
R_{rt}^{use}+S_{rt}+K_{rt}=R_{rt}^{av}. \tag{25}
$$

边界为

$$
0\le B_{rt}\le P_{rt}^{fac}, \tag{26}
$$

$$
P_{rt}^{export,q2}:=R_{rt}^{av},\qquad
0\le S_{rt}\le P_{rt}^{export,q2},
\qquad R_{rt}^{use},K_{rt}\ge0. \tag{27}
$$

附件适用表明确 `storage_information.xlsx` 仅用于问题三、四，因此问题二不读取 `SellLimit_MW`、`MaxGridImport_MW` 或 `MaxGridExport_MW`。问题二无储能，式（24）自然给出 $B_{rt}\le P_{rt}^{fac}$；式（25）给出可实施的区域逐时最大外送功率 $P_{rt}^{export,q2}=R_{rt}^{av}$，不会售出电网购电。

成本和碳排放为

$$
C_{op}=\sum_{r,t}
(\pi_{rt}^{buy}B_{rt}-\pi_{rt}^{sell}S_{rt})\Delta t, \tag{28}
$$

$$
E_{CO2}=\sum_{r,t}c_{rt}B_{rt}\Delta t. \tag{29}
$$

定义时延分子和正分母：

$$
A_L=\sum_i\sum_{r,s}
g_id_i\ell_{o_i r}x_{irs},
\qquad
W_L=\sum_i g_id_i. \tag{30}
$$

当 $W_L>0$ 时，

$$
L_{net}=\frac{A_L}{W_L}; \tag{31}
$$

否则输出“不可计算”，并移除相应 ε 约束和 Pareto 维度。

新能源指标定义为

$$
A_U=\sum_{r,t}(R_{rt}^{use}+S_{rt})\Delta t,
\qquad
W_U=\sum_{r,t}R_{rt}^{av}\Delta t. \tag{32}
$$

当 $W_U>0$ 时，

$$
U_{RE}=\frac{A_U}{W_U}; \tag{33}
$$

否则输出“不可计算”。在问题二的授权数据边界内，$S_{rt}$ 没有独立外送容量字段且可吸收全部未直用新能源；因此任一可行解都有 $R_{rt}^{use}+S_{rt}+K_{rt}=R_{rt}^{av}$。若成本目标使 $K_{rt}=0$，统一口径的 $U_{RE}$ 将退化为 100%，不得把它作为优化改善或 Pareto 维度。除统一口径外，必须同时报告直接消纳率 $\sum R^{use}/W_U$、外送率 $\sum S/W_U$、弃电率 $\sum K/W_U$ 及三者逐时分布。

多目标模型采用

$$
\min C_{op}, \tag{34}
$$

$$
E_{CO2}\le\varepsilon_C,\qquad
A_L\le\varepsilon_LW_L. \tag{35}
$$

时延约束仅在 $W_L>0$ 时施加；问题二的 $U_{RE}$ 只作退化诊断，不进入 ε 约束。

### 滚动时域累计契约

令第 $j$ 个求解窗口为

$$
b_1=0,\qquad b_{j+1}=b_j+F,\qquad
W_j=[b_j,e_j],\quad e_j=\min(b_j+H-1,2406), \tag{36}
$$

其中 $H=168$ h、$O=24$ h，每轮提交长度为

$$
F=H-O=144\ \mathrm h. \tag{37}
$$

非末窗口的唯一提交区为

$$
F_j=[b_j,\min(b_j+F-1,2406)], \tag{38}
$$

最后窗口提交全部尚未提交时段。重叠的 $O$ 小时只是下一窗口的预览区：其中任务和能源决策不写入正式方案、不计入累计指标，进入下一窗口后重新优化。这样每个小时恰好由一个提交区计数。

提交 $F_j$ 后：

1. 冻结其中全部能源流。
2. 冻结已开工任务的执行区域、开工时刻及其跨窗口后续占用。
3. 未开工任务只携带尚可行的剩余候选集合。
4. 跨边界任务后续 GPU 和功率占用作为下一窗口固定占用，不再次选择任务，也不重复计入任务级时延。

累计碳排放状态为

$$
A_C^{(j)}
=\sum_{r}\sum_{t\in\cup_{h\le j}F_h}
c_{rt}B_{rt}\Delta t,
\qquad
A_C^{(j)}\le\varepsilon_C. \tag{39}
$$

对未提交时域使用只含不可迁移非 AI 负荷的解析碳下界

$$
\underline A_{C,rem}^{(j)}=\sum_r\sum_{t\notin\cup_{h\le j}F_h}c_{rt}\max\{0,\mathrm{PUE}_rP_{rt}^{NA}-R_{rt}^{av}\}\Delta t,\qquad
A_C^{(j)}+\underline A_{C,rem}^{(j)}\le\varepsilon_C. \tag{39a}
$$

该下界忽略未提交 AI 负荷，因而只作必要条件，不冒充精确剩余碳排放。

已提交任务的时延加权和为

$$
A_L^{(j)}
=\sum_{i:\,s_i\text{已提交}}
g_id_i\ell_{o_i,r_i}. \tag{40}
$$

未提交任务的最小可达时延下界为

$$
\underline A_{L,rem}^{(j)}
=
\sum_{i:\,s_i\text{未提交}}
g_id_i
\min_{r,s\in\mathcal S_{ir}^{rem}}\ell_{o_i r}. \tag{41}
$$

若任一剩余候选集合为空，立即输出 `infeasible_precheck`。每个窗口必须满足

$$
A_L^{(j)}+\underline A_{L,rem}^{(j)}
\le\varepsilon_LW_L. \tag{42}
$$

已提交小时的新能源利用量为

$$
A_U^{(j)}
=\sum_r\sum_{t\in\cup_{h\le j}F_h}
(R_{rt}^{use}+S_{rt})\Delta t. \tag{43}
$$

未提交小时的最大可能新能源利用量采用无需新增自由参数的物理上界

$$
\overline A_{U,rem}^{(j)}
=
\sum_r\sum_{t\notin\cup_{h\le j}F_h}
R_{rt}^{av}\Delta t. \tag{44}
$$

问题二不设置新能源 ε 约束；式（43）–（44）只累计直用、外送和弃电分流，用于披露统一利用率的退化。每个 ε 组合启动时先生成一份满足全部任务、能源、碳和时延约束的全时域可行 incumbent；构造失败则该组合输出 `no_verified_full_horizon_incumbent`。每次冻结前将本轮提交区与 incumbent 尾部拼接，并线性扫描复核式（1）–（9）、（24）–（31）、（35）、（39a）和（42）；只有完整拼接仍满足碳与时延 ε 才替换 incumbent，否则拒绝本轮提交。全时域拼接完成后按式（28）–（33）复算。

### 求解方法

窗口间严格按式（36）–（44）传递累计状态，并执行式（39a）的剩余碳下界和全时域 incumbent 证书；问题二不执行新能源 ε 门禁。若缩小实例整体 MILP 对照失败，只允许将 $H$ 扩大一次至 $336$ h。每个多目标子问题最多处理 $12$ 个 ε 组合，单候选最多 $30$ s，并服从共享墙钟合同。

### 必须回答的输出

1. 每个任务的来源区域、执行区域、开工、完成、等待和网络时延。
2. 系统及分区域成本、碳排放、平均及高分位时延、新能源利用率。
3. 相对基础调度的绝对变化和相对变化率。
4. 三类任务迁移数量、方向和等待分布。
5. Pareto 方案表和非支配前沿图。
6. 第 $2400$–$2405$ 小时末端任务及能源结算。
7. 文件：`q2_schedule.csv`、`q2_energy_flow.csv`、`q2_metrics.csv`、`q2_pareto.csv`、`q2_pareto.png`。

## 子问题 3：固定负荷下储能协同优化

### 模型思路

问题三不重新优化任务，设施负荷固定为

$$
P_{rt}^{fac}=
\mathrm{PUE}_r(P_{rt}^{BAI}+P_{rt}^{NA}). \tag{46}
$$

### 模型建立

总充电功率为

$$
C_{rt}=C_{rt}^{RE}+C_{rt}^{G}. \tag{47}
$$

负荷侧和新能源侧平衡分别为

$$
B_{rt}+R_{rt}^{use}+D_{rt}
=P_{rt}^{fac}+C_{rt}^{G}, \tag{48}
$$

$$
R_{rt}^{use}+C_{rt}^{RE}+S_{rt}+K_{rt}
=R_{rt}^{av}. \tag{49}
$$

边界为

$$
0\le B_{rt}\le P_{rt}^{grid,max}, \tag{50}
$$

$$
0\le S_{rt}\le
\min(P_{rt}^{export,max},S_r^{max}), \tag{51}
$$

$$
R_{rt}^{use},C_{rt}^{RE},C_{rt}^{G},D_{rt},K_{rt}\ge0. \tag{52}
$$

SOC 递推为

$$
E_{r,-1}=E_r^0, \tag{53}
$$

$$
E_{rt}=E_{r,t-1}
+\eta_r^cC_{rt}\Delta t
-\frac{D_{rt}\Delta t}{\eta_r^d}, \tag{54}
$$

$$
E_r^{min}\le E_{rt}\le E_r^{max},
\qquad E_{r,2406}\ge E_r^0. \tag{55}
$$

禁止同时充放电：

$$
0\le C_{rt}\le C_r^{max}u_{rt}^{c}, \tag{56}
$$

$$
0\le D_{rt}\le D_r^{max}(1-u_{rt}^{c}),
\qquad u_{rt}^{c}\in\{0,1\}. \tag{57}
$$

净购电及峰值约束辅助变量为

$$
N_{rt}=B_{rt}-S_{rt}, \tag{58}
$$

$$
P_r^{peak}\ge N_{rt},\qquad P_r^{peak}\ge0. \tag{59}
$$

由于 $P_r^{peak}$ 在非峰值主目标候选中可能松弛，正式报告值不得直接读取该变量，而必须由最终净购电序列复算：

$$
\widehat P_r^{peak}
=
\max_{t\in\mathcal T^{energy}}
\max\{0,B_{rt}-S_{rt}\}. \tag{60}
$$

式（59）只用于 ε 约束，式（60）是比较、绘图和文件输出的唯一峰值口径。

净购电波动为

$$
z_{rt}\ge N_{rt}-N_{r,t-1},\qquad
z_{rt}\ge N_{r,t-1}-N_{rt},\qquad z_{rt}\ge0, \tag{61}
$$

$$
V=\sum_r\sum_{t=1}^{2406}z_{rt},\qquad
\widehat V=\sum_r\sum_{t=1}^{2406}|N_{rt}-N_{r,t-1}|. \tag{62}
$$

以成本为主目标时：

$$
\min C_{op}, \tag{63}
$$

$$
E_{CO2}\le\varepsilon_C,\qquad
P_r^{peak}\le\varepsilon_{P,r},\qquad
V\le\varepsilon_V. \tag{64}
$$

等效循环量为

$$
N_r^{cycle}=
\frac{\sum_t(C_{rt}+D_{rt})\Delta t}
{2(E_r^{max}-E_r^{min})},
\qquad E_r^{max}>E_r^{min}. \tag{65}
$$

若 $E_r^{max}\le E_r^{min}$，输出 `invalid_storage_bounds` 并停止该区域优化。

### 求解方法

求无储能基准、成本最小、碳排放最小、峰值最小和波动最小方案，再形成有限 ε 组合；其中峰值最小锚点的唯一标量目标固定为 $\min\sum_{r\in\mathcal R}P_r^{peak}$，同值时按区域顺序逐个最小化。$V$ 只用于模型中的波动 ε 约束；比较、Pareto、绘图和输出的波动量统一从最终净购电序列复算为 $\widehat V$。最终峰值全部按式（60）复算。模型不设置购电与新能源外送互斥，因为两者在题面分源守恒中来源不同；但每个 $S_{rt}>0$ 必须由式（49）的本时段可用新能源分流逐时验证，严禁电网购电转售。允许购电供负荷与本地新能源外送同时发生时，必须统计小时数、能量和财务影响；若售电价较高导致该行为，只解释为分源守恒与价格机制结果，不得称为协同效率提升。

### 必须回答的输出

1. 各区域逐小时新能源直供、新能源充电、电网充电、放电、购电、外送、弃电和净购电。
2. 绝对 SOC 轨迹及 $SOC(2406)$。
3. 优化前后成本、碳排放、按式（60）复算的正向峰值净购电、绝对爬坡量及变化率。
4. 同时充放电小时数、同时购电与新能源外送小时数及分源口径说明。
5. 各区域等效循环量。
6. 文件：`q3_storage_schedule.csv`、`q3_soc.csv`、`q3_energy_flow.csv`、`q3_comparison.csv`、`q3_storage_plot.png`。

## 子问题 4：多区域算—储—电联合多目标优化

### 模型思路

联合决定任务区域、开工时刻、储能充放电、新能源分配及购售电，使用实际任务和实际逐时参数重新求解。

### 模型建立

任务负荷由式（1）–（9）确定。能源侧采用

$$
B_{rt}+R_{rt}^{use}+D_{rt}
=P_{rt}^{fac}+C_{rt}^{G}, \tag{66}
$$

$$
R_{rt}^{use}+C_{rt}^{RE}+S_{rt}+K_{rt}
=R_{rt}^{av}, \tag{67}
$$

$$
C_{rt}=C_{rt}^{RE}+C_{rt}^{G}, \tag{68}
$$

并满足式（50）–（57）。净购电与峰值约束采用式（58）–（59），正式峰值采用式（60）。

对弹性任务定义开工时刻

$$
s_i=\sum_r\sum_{s\in\mathcal S_{ir}}sx_{irs}. \tag{69}
$$

最大总等待余量为

$$
M_W=
\sum_{i\in\mathcal I^{flex}}
[\min(f_i^{late},2406)-d_i-a_i]. \tag{70}
$$

当 $M_W>0$ 时，

$$
Q_{service}
=
1-
\frac{\sum_{i\in\mathcal I^{flex}}(s_i-a_i)}
{M_W}. \tag{71}
$$

当 $M_W=0$ 时输出“不可计算”，并改报实时即时开工率、SLA 满足率和按期完成率。

新能源利用率为

$$
U_{RE}=
\frac{\sum_{r,t}
(R_{rt}^{use}+C_{rt}^{RE}+S_{rt})\Delta t}
{W_U},
\qquad
W_U=\sum_{r,t}R_{rt}^{av}\Delta t>0. \tag{72}
$$

当 $W_U=0$ 时输出“不可计算”，不进入对应 ε 约束和排序。

多目标模型为

$$
\min C_{op}, \tag{73}
$$

$$
E_{CO2}\le\varepsilon_C,\quad
L_{net}\le\varepsilon_L,\quad
U_{RE}\ge\varepsilon_U,\quad
Q_{service}\ge\varepsilon_Q,\quad
P_r^{peak}\le\varepsilon_{P,r}. \tag{74}
$$

### 全时域滚动预算

问题四沿用式（36）–（44）的窗口索引、唯一提交区、冻结规则、碳累计量和时延累计量，但明确不使用仅针对问题二无储能情形的式（39a）；问题四的碳可达性直接由含储能的完整全时域 incumbent 证书保证。新能源剩余可达约束在本问按含储能口径重新定义为

$$
A_{U,4}^{(j)}=\sum_r\sum_{t\in\cup_{h\le j}F_h}(R_{rt}^{use}+C_{rt}^{RE}+S_{rt})\Delta t,\qquad
A_{U,4}^{(j)}+\sum_r\sum_{t\notin\cup_{h\le j}F_h}R_{rt}^{av}\Delta t\ge\varepsilon_UW_U. \tag{79b}
$$

此外，已提交弹性任务的累计等待量为

$$
A_W^{(j)}
=
\sum_{i\in\mathcal I^{flex}:\,s_i\text{已提交}}
(s_i-a_i). \tag{75}
$$

未提交弹性任务的最小可达等待量为

$$
\underline A_{W,rem}^{(j)}
=
\sum_{i\in\mathcal I^{flex}:\,s_i\text{未提交}}
\left[
\min_{r,s\in\mathcal S_{ir}^{rem}}s-a_i
\right]. \tag{76}
$$

服务质量剩余预算约束为

$$
A_W^{(j)}+\underline A_{W,rem}^{(j)}
\le(1-\varepsilon_Q)M_W. \tag{77}
$$

已提交时段的正向峰值为

$$
P_{r,comm}^{peak,(j)}
=
\max_{t\in\cup_{h\le j}F_h}\max\{0,N_{rt}\}, \tag{78}
$$

并满足

$$
P_{r,comm}^{peak,(j)}\le\varepsilon_{P,r}. \tag{79}
$$

重叠预览区不进入式（75）和式（78），防止等待量和峰值重复计数。令 $t_j=\max F_j$；每次冻结提交区末状态前还必须满足终端 SOC 剩余可达约束

$$
E_{r,t_j}+\eta_r^c C_r^{max}(2406-t_j)\Delta t\ge E_r^0,
\qquad E_{r,2406}\ge E_r^0. \tag{79a}
$$

式（79a）仅作快速必要条件。求解开始时先生成并保留一份覆盖全部任务、$0$–$2406$ 能源/SOC 以及当前碳、时延、新能源、服务质量和区域峰值 ε 约束的完整可行 incumbent；若在预留基准时间内无法构造并通过复核，则停止问题四并输出 `no_verified_full_horizon_incumbent`，不得开始滚动提交。每次冻结 $F_j$ 前，不重求全余域任务 MILP：只把本轮任务提交区与 incumbent 的未提交任务尾部拼接；能源流和 SOC 尾部不得直接复用旧轨迹，而要从新的 $E_{r,t_j}$ 起点按式（47）–（57）逐时前向重构一条满足购售电、充放电和终端 SOC 的可行能源尾部。随后以一次 $O(|\mathcal I|+|\mathcal R||\mathcal T|)$ 扫描复算任务唯一性、容量、功率、能源守恒、购售电边界、逐时 SOC、$E_{r,2406}\ge E_r^0$、累计碳、时延、新能源利用率、服务质量和各区域峰值；本题规模上界为 $50000+6\times2407$ 条主记录。只有重构后的完整证书全部残差通过才用它替换 incumbent；若能源尾部重构或任何全局 ε 失败，则拒绝本轮提交并原样保留上一份状态相容的完整可行 incumbent。首次基准证书实测耗时记为 $t_{cert}^{pilot}$，后续保守预留 $t_{cert}^{max}=\max\{5t_{cert}^{pilot},2\mathrm s\}$。证书摘要和最大残差写入运行日志。最终方案必须按式（28）–（33）、（53）–（60）、（70）–（72）进行全时域复算。

### 折中方案的统一方向

对需要最小化的成本、碳排放、时延和峰值定义

$$
J_C=C_{op},\qquad
J_E=E_{CO2},\qquad
J_L=L_{net},\qquad
J_P=\sum_r\widehat P_r^{peak}. \tag{80}
$$

将需要最大化的新能源利用率和服务质量转换为最小化方向：

$$
J_U=1-U_{RE},\qquad
J_Q=1-Q_{service}. \tag{81}
$$

不可计算的指标从折中距离中移除。对可计算且候选集中具有正量程的指标，

$$
\widetilde J_m(y)=
\frac{J_m(y)-J_m^{ideal}}
{J_m^{nadir}-J_m^{ideal}}, \tag{82}
$$

其中

$$
J_m^{ideal}=\min_{y\in\mathcal P}J_m(y),\qquad
J_m^{nadir}=\max_{y\in\mathcal P}J_m(y). \tag{83}
$$

若 $J_m^{nadir}=J_m^{ideal}$，该指标没有区分力，从距离中删除。折中方案为

$$
y^*=
\arg\min_{y\in\mathcal P}
\sqrt{
\sum_{m\in\mathcal M_{valid}}
w_m\widetilde J_m(y)^2
}, \tag{84}
$$

对所有可计算且有正量程的指标固定取等权 $w_m=1/|\mathcal M_{valid}|$，不在查看结果后调权。问题二至四的 ε 组合也使用同一封闭规则：先求各约束指标的单目标理想锚点 $J_m^{ideal}$ 和成本最小基准 $J_m^{base}$；对第 $n=1,\ldots,12$ 个组合及第 $m$ 个约束指标，固定

$$
q_{nm}=\frac{((c_m(n-1)+b_m)\bmod 12)+0.5}{12},\quad
(c_m)=(1,5,7,11,1),\ (b_m)=(0,2,4,6,8). \tag{84a}
$$

最小化指标的上限取 $\varepsilon_{nm}=J_m^{ideal}+q_{nm}(J_m^{base}-J_m^{ideal})$；最大化指标的下限取 $\varepsilon_{nm}=J_m^{ideal}-q_{nm}(J_m^{ideal}-J_m^{base})$。各问按式（35）、（64）、（74）的约束族顺序取前若干维，固定最多 12 个组合。六个区域峰值约束视为一个峰值约束族，共用同一 $q_{nP}$，但逐区域生成 $\varepsilon_{P,r,n}=P_{r}^{ideal}+q_{nP}(P_{r}^{base}-P_{r}^{ideal})$；$P_r^{ideal}$ 来自唯一峰值锚点的区域复算值，$P_r^{base}$ 来自成本基准，故不需要第六至第十个独立网格维度。锚点不可行、非有限或量程为零时记录原因并移除该维，不使用 NaN 或事后人工网格。

### 情景模型

碳约束情景为

$$
E_{CO2}\le(1-\rho_C)E_{CO2}^{base}, \tag{85}
$$

其中 $E_{CO2}^{base}$ 为同任务、同设备边界下无额外碳预算方案按式（29）复算的排放。

电价情景为

$$
\pi_{rt}^{buy,\xi}
=
\bar\pi_r+
\kappa_\xi(\pi_{rt}^{buy}-\bar\pi_r), \tag{86}
$$

其中

$$
\bar\pi_r=
\frac1{|\mathcal T^{energy}|}
\sum_{t\in\mathcal T^{energy}}\pi_{rt}^{buy}. \tag{87}
$$

新能源情景为

$$
R_{rt}^{av,\xi}
=
\max\{0,\mu_\xi R_{rt}^{av}
+\sigma_\xi\zeta_{rt}^{\xi}\}. \tag{88}
$$

$\zeta_{rt}^{\xi}$ 使用固定种子 `20260807` 生成并按区域去均值。七情景执行优先级固定为“基准、碳10%、低峰谷差、新能源偏低、碳20%、高峰谷差、新能源偏高”；每个情景启动前执行同一 $D_{search}$ 剩余时间检查，未启动写入 `scenario_status=budget_not_started`，已启动但未形成完整证书写入 `scenario_status=incomplete_discarded`。只运行以下七个预声明情景 $(\rho_C,\kappa_\xi,\mu_\xi,\sigma_\xi)$：基准 $(0,1,1,0)$、碳收紧10% $(0.1,1,1,0)$、碳收紧20% $(0.2,1,1,0)$、低峰谷差 $(0,0.8,1,0)$、高峰谷差 $(0,1.2,1,0)$、新能源偏低 $(0,1,0.8,0.05\bar R_r)$、新能源偏高 $(0,1,1.2,0.05\bar R_r)$，其中 $\bar R_r$ 为该区域附件可用新能源均值。该式仅作为统计压力测试，不解释为装机容量预测；不得查看优化结果后调整情景参数。

### 求解方法

采用式（36）–（44）、（75）–（79b）的滚动契约。窗口间传递已提交决策、跨边界任务固定占用、绝对 SOC、累计碳、累计时延、累计新能源利用量、累计等待量和已实现峰值。未完成候选、累计状态不连续候选或全时域复核失败候选不得进入 Pareto 集。

### 必须回答的输出

1. 每个 Pareto 方案的成本、碳排放、网络时延、服务质量代理、新能源利用率和按式（60）复算的各区域正向峰值净购电。
2. 推荐方案的完整任务调度、逐时能源流、储能动作和绝对 SOC。
3. 各任务类型迁移数量、方向、等待和时延分布。
4. 各区域新能源直供、充电、外送和弃电累计量。
5. 不同碳预算、电价及新能源情景的策略与指标变化。
6. 每个场景的可行性、滚动窗口局部求解器间隙和结果等级；局部间隙不得称为全时域全局最优性间隙，全局最优性固定标记 `not_certified`。
7. 单独报告同时购电与新能源外送的小时数、能量和财务影响；该现象只解释为题面分源守恒与价格机制结果，不得称为协同效率提升。
8. 文件：`q4_schedule.csv`、`q4_energy_flow.csv`、`q4_soc.csv`、`q4_pareto.csv`、`q4_scenario_comparison.csv`、`q4_pareto.png`。

## 6. 共享墙钟预算与停止规则

Coder 单次执行共享

$$
B_{total}=300\ \mathrm s,\qquad
T_{tail}=15\ \mathrm s, \tag{89}
$$

$$
D_{search}=t_{start}+285\ \mathrm s. \tag{90}
$$

以 `time.monotonic()` 记录实际耗时。数据读取、问题一固定工作、问题二至四基准、全部单目标锚点和 ε 候选都必须在 $D_{search}$ 前完成；启动其中任何一项前均检查其保守求解与证书耗时能否放入剩余搜索时间，不能放入则跳过并记录 `budget_not_started`。最后 15 秒只做已完成 incumbent 的最终复核和文件输出。

执行优先级为：

1. 数据读取、输入校验和问题一必答结果。
2. 问题二、三、四各自一个可行基准。
3. 各问必要的单目标锚点。
4. 仅以剩余时间增加 ε 候选。

每个候选启动前计算

$$
N_{launch}
=
\min\left\{
N_\varepsilon^{max}-N_{done},
\left\lfloor
\frac{D_{search}-t_{now}}
{t_{solve}^{max}+t_{cert}^{max}}
\right\rfloor
\right\}. \tag{91}
$$

固定 $t_{solve}^{max}=30$ s，式（91）的单候选预算取 $t_{solve}^{max}+t_{cert}^{max}$。仅当 $N_{launch}\ge1$ 且求解加拼接证书的保守上限能够完整放入 $D_{search}-t_{now}$ 时启动新候选；传给求解器的 `time_limit` 不超过 $\min\{30,D_{search}-t_{now}-t_{cert}^{max}\}$ s。任何求解或证书检查均不得越过 $D_{search}$；剩余时间不足即停止新增候选并保留最近的完整可行 incumbent。最后 $15$ s 仅用于最终确定性全时域复核和文件输出。式（91）只是启动上限，不要求机械完成全部 $12$ 个组合。

## 7. 统一验证规则

代码阶段必须检查：

1. 每个任务恰好执行一次，实时任务开工等于到达时刻。
2. 时延、到达、截止和第 $2406$ 小时禁占用约束。
3. GPU-hour、IT 平均功率和设施平均功率约束。
4. 问题二至四的能源守恒、购售电边界和售电来源。
5. SOC 绝对递推、上下限、充放电互斥和终端 SOC。
6. 滚动提交区不重叠且完整覆盖正式时域；每小时能源流只计数一次。
7. 已提交任务不再次选择，跨边界任务后续占用连续。
8. 累计碳、时延、新能源利用量和等待量与最终全时域复算一致。
9. 正式峰值只能按式（60）复算，不直接采用辅助变量。
10. 相关性和自相关仅在有效样本、正方差条件满足时计算；否则输出结构化不可用状态。
11. 所有分母先检查正性；不满足时输出“不可计算”或“验证不可用”，不得输出 `NaN`、`Inf` 或以任意 $\epsilon$ 替代。
12. 最大化指标必须按式（81）转换后进入折中距离。
13. 只有通过完整全时域复核的候选才能进入 Pareto 集和最终结果。

## Verifier 修复核对表

| Block issue | 修复位置 | 可计算性与有限输出保证 |
|---|---|---|
| 预测模型早期滞后与滚动均值未定义 | 式（13）–（17） | 有效训练起点固定为 $t=168$；滚动均值只用预测时点以前的完整历史，不定义负时刻、不回填未来值，设计矩阵不会因早期滞后产生 NaN |
| 问题二、四滚动时域缺少全局 ε 预算和重叠决策传递 | 式（36）–（44）、（75）–（79b） | 固定唯一提交区 $F=H-O$；重叠区只预览、不计数；冻结已提交任务和能源流，并传递累计碳、时延、新能源、等待量和峰值状态及剩余可达界，最终再作全时域复算 |
| 自相关、区域相关性缺少常数序列、样本不足和缺失值保护 | 式（20）–（21） | 仅在成对有限样本数至少为 $2$ 且两序列方差均为正时计算；否则输出结构化不可用状态，禁止 NaN、Inf 和虚假验证通过 |
| 问题四折中距离未统一最大化指标方向 | 式（80）–（84） | 成本、碳、时延、峰值保持最小化；新能源利用率和服务质量分别转换为 $1-U_{RE}$、$1-Q_{service}$，再统一归一化 |
| 峰值辅助变量在非峰值主目标候选中可能松弛 | 式（58）–（60）及式（80） | $P_r^{peak}$ 只用于约束；比较、绘图、Pareto 指标和文件输出统一由最终净购电序列复算 $\widehat P_r^{peak}=\max_t\max(0,B_{rt}-S_{rt})$ |