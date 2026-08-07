# 数学模型

## 符号说明

| 符号 | 含义 | 类型及数据来源 | 取值范围/单位 |
|---|---|---|---|
| \(i,r,t,s,k\) | 任务、区域、小时、整数开工时刻、任务类型索引 | 索引 | \(r\in\mathcal R,\ t=0,\ldots,2406\) |
| \(\mathcal R,\mathcal K\) | 六区域和三任务类型集合 | 题面直接给定 | 无 |
| \(\mathcal S\) | 有限整数开工时刻集合 | 题面小时粒度推导 | \(\{0,\ldots,2405\}\) |
| \(a_i,d_i,h_i\) | 到达小时、持续分钟、持续小时，\(h_i=d_i/60\) | `workload_trace.xlsx` | h、min、h |
| \(g_i,k_i,o_i\) | GPU需求、任务类型、来源区域 | `workload_trace.xlsx` | GPU、无、无 |
| \(f_i^{valid},F_i\) | 有效附件截止、统一有效截止 | 输入清洗及派生 | h |
| \(W_i^{\max}\) | 最大允许等待时间 | 派生 | h |
| \(\ell_i^{\max},\ell_{or}\) | 最大允许时延、区域单向时延 | 工作负载及网络附件 | ms |
| \(\Delta t\) | 小时时段长度 | 题面直接给定 | \(1\) h |
| \(\omega_{it}(s)\) | 任务与小时的实际重叠时长 | 派生 | h |
| \(\chi_{it}(s)\) | 小时内是否存在瞬时占用 | 派生 | \(\{0,1\}\) |
| \(\Omega_i\) | 任务有限整数候选集合 | 派生 | 区域—整数时刻对 |
| \(x_{irs}\) | 任务是否在区域 \(r\) 于整数时刻 \(s\) 开工 | 决策变量 | \(\{0,1\}\) |
| \(q_{ir},s_i,c_i,\ell_i\) | 执行区域指示、开工、完成、实际时延 | 派生 | 无、h、h、ms |
| \(G_r^{\max}\) | 可调度GPU容量 | `GPU_information.xlsx` | 等效GPU |
| \(P_r^{IT,\max},P_r^{F,\max}\) | 瞬时IT和设施功率上限 | `GPU_information.xlsx` | MW |
| \(p_k^{GPU},\pi_r\) | 每GPU平均IT功率、PUE | 功率映射及GPU附件 | MW/GPU、无量纲 |
| \(L_{rt}^{N},L_{rt}^{BAI}\) | NonAI、问题三Baseline AI小时平均IT负荷 | `region_time_data.xlsx` | MW |
| \(L_{rt}^{AI,cap}\) | AI任务瞬时IT功率 | 派生 | MW |
| \(E_{rt}^{AI}\) | AI任务在小时 \(t\) 的IT电量 | 派生 | MWh |
| \(L_{rt}^{AI,avg}\) | AI任务小时平均IT功率 | 派生 | MW |
| \(L_{rt}^{F,cap},L_{rt}^{F,avg}\) | 瞬时设施功率、小时平均设施负荷 | 派生 | MW |
| \(R^{av},R^{use},R^{ch},R^{sell},R^{curt}\) | 可用、直用、充电、外送、弃用新能源 | 输入或变量 | MW |
| \(G^{load},G^{ch},G^{buy},G^{sell}\) | 电网供负荷、充电、总购电、总外送 | 变量 | MW |
| \(C_{rt},D_{rt},S_{rt}\) | 储能充电、放电、时段末SOC | 变量 | MW、MW、MWh |
| \(B_r,S_r^0,S_r^{min},S_r^{max}\) | 储能容量、初始SOC和上下限 | `storage_information.xlsx` | MWh |
| \(\eta_r^c,\eta_r^d,C_r^{\max},D_r^{\max}\) | 充放电效率和功率上限 | 储能附件 | 无量纲、MW |
| \(I_r^{\max}\) | 区域最大购电功率 | 区域附件 | MW |
| \(X_r^{grid},X_r^{storage}\) | 电网外送上限、储能附件外送上限 | 区域及储能附件 | MW |
| \(E_r^{\max}\) | 同时执行两项外送边界后的上限 | 派生 | MW |
| \(y_{rt}^{grid},u_{rt}^{c}\) | 购售互斥、充放互斥变量 | 决策变量 | \(\{0,1\}\) |
| \(c_{rt}^{buy},c_{rt}^{sell},\kappa_{rt}\) | 购价、售价、碳强度 | 区域逐时附件 | 元/MWh、tCO2/MWh |
| \(N_{rt},P_r^{peak},z_{rt},V_r\) | 净购电、峰值、爬坡辅助量、绝对爬坡量 | 派生或变量 | MW |
| \(D_{rkt}\) | 区域—类型—小时GPU到达需求 | 工作负载聚合 | GPU |
| \(\mathcal T_{selection}\) | 候选模型选择拟合样本 | 固定 | \(168{:}2351\) |
| \(\mathcal T_{validation}\) | 调参验证样本 | 固定 | \(2352{:}2375\) |
| \(\mathcal T_{finalfit}\) | 选模后最终重训样本 | 固定 | \(168{:}2375\) |
| \(\mathcal T_{test}\) | 最终预测测试样本 | 固定 | \(2376{:}2399\) |
| \(\sigma_{rk},\rho_\delta,\lambda\) | 训练尺度、Huber损失、正则参数 | 训练数据或固定网格 | GPU、无量纲 |
| \((r_i^0,s_i^0)\) | 模型内部确定性生成的前序基础调度 | 派生，不是外部输入 | 区域、整数小时 |
| \(C_{\mathrm{op}},E_{\mathrm{CO2}}\) | 运行成本、购电碳排放 | 评价指标 | 元、tCO2 |
| \(L_{\mathrm{net}},U_{\mathrm{RE}},Q_{\mathrm{service}}\) | 时延、新能源利用率、服务质量 | 评价指标 | ms、无量纲 |
| \(b^0,b^3,b^4\) | 问题二、三、四的唯一成本基准 | 优化产生 | 方案 |
| \(m_j^{loose},m_j^{ideal}\) | 指标 \(j\) 的宽松和理想端点 | 基准及单目标锚点 | 与指标一致 |
| \(\varepsilon_j(a)\) | 第 \(a\) 条路径的阈值 | 封闭插值 | 与指标一致 |
| \(E^0\) | 问题四统一基准 \(b^4\) 的碳排放 | 派生 | tCO2 |
| \(H\) | 滚动窗口长度 | 固定 | \(168\) h |
| \(\tau_{num}\) | 归一化审计容差 | 固定 | \(10^{-6}\) |
| \(B_{\mathrm{total}},T_{\mathrm{tail}}\) | 共享总预算、终检预留 | 固定运行合同 | 300 s、15 s |

附件数值、预测误差、锚点和优化结果均由代码阶段读取真实附件后计算；当前模型阶段不预填拟合参数、RMSE、\(R^2\)、最优方案或可行性结论。

## 统一任务、容量与能源边界

任务到达、结清、整数开工和终端时域分别为

$$
\mathcal T_A=\{0,\ldots,2399\},\quad
\mathcal T_C=\{2400,\ldots,2405\},\quad
\mathcal S=\{0,\ldots,2405\},\quad
t_{\mathrm{terminal}}=2406.
\tag{1}
$$

第2406小时不产生任务、不安排任务，只结算电力和储能终端状态。对 `LatestFinishHour`，若字段为合法有限值，则令 \(f_i^{valid}=f_i^{\max}\)；若附件数据字典明确该字段对该弹性任务不适用或为空，则唯一取 \(f_i^{valid}=2406\)；其余非法值结构化停止。定义

$$
h_i=\frac{d_i}{60},\qquad
F_i=\min\{f_i^{valid},2406\},\qquad
W_i^{\max}=F_i-a_i-h_i.
\tag{2}
$$

任务与小时区间 \([t,t+1)\) 的实际重叠时长及瞬时占用为

$$
\omega_{it}(s)=
\max\{0,\min(t+\Delta t,s+h_i)-\max(t,s)\},
\tag{3}
$$

$$
\chi_{it}(s)=\mathbf 1\{\omega_{it}(s)>0\}.
\tag{4}
$$

所有任务的候选集合显式限定为有限整数集合：

$$
\Omega_i=
\left\{
(r,s):
\begin{array}{l}
r\in\mathcal R,\ s\in\mathcal S,\ s\in\mathbb Z,\\
s\ge a_i,\ s+h_i\le F_i,\\
\ell_{o_ir}\le\ell_i^{\max},\\
\omega_{i,2406}(s)=0
\end{array}
\right\}.
\tag{5}
$$

由于 \(s+h_i\le F_i\le2406\)，最后一项同时显式闭合“第2406小时不得执行任务”的边界。若 \(\Omega_i=\varnothing\)，输出任务ID、到达、时长、截止、可用区域及排除原因，并结构化停止。

唯一执行和派生状态为

$$
\sum_{(r,s)\in\Omega_i}x_{irs}=1,\qquad
q_{ir}=\sum_{s:(r,s)\in\Omega_i}x_{irs},
\tag{6}
$$

$$
s_i=\sum_{(r,s)\in\Omega_i}sx_{irs},\qquad
c_i=s_i+h_i,\qquad
\ell_i=\sum_r\ell_{o_ir}q_{ir}.
\tag{7}
$$

实时推理任务额外满足

$$
s_i=a_i,\qquad i\in\mathcal I_{\mathrm{RT}}.
\tag{8}
$$

瞬时GPU、IT和设施容量仅使用 \(\chi\)：

$$
\sum_{i}\sum_{s:(r,s)\in\Omega_i}
g_i\chi_{it}(s)x_{irs}\le G_r^{\max},
\tag{9}
$$

$$
L_{rt}^{AI,cap}=
\sum_i\sum_{s:(r,s)\in\Omega_i}
g_ip_{k_i}^{GPU}\chi_{it}(s)x_{irs},
\tag{10}
$$

$$
L_{rt}^{IT,cap}=L_{rt}^{N}+L_{rt}^{AI,cap},\qquad
L_{rt}^{F,cap}=\pi_rL_{rt}^{IT,cap},
\tag{11}
$$

$$
L_{rt}^{IT,cap}\le P_r^{IT,\max},\qquad
L_{rt}^{F,cap}\le P_r^{F,\max}.
\tag{12}
$$

小时能源结算仅使用实际重叠时长 \(\omega\)：

$$
E_{rt}^{AI}=
\sum_i\sum_{s:(r,s)\in\Omega_i}
g_ip_{k_i}^{GPU}\omega_{it}(s)x_{irs},
\tag{13}
$$

$$
L_{rt}^{AI,avg}=\frac{E_{rt}^{AI}}{\Delta t},\qquad
L_{rt}^{F,avg}=
\pi_r\left(L_{rt}^{N}+L_{rt}^{AI,avg}\right).
\tag{14}
$$

因此，\(\chi\) 只负责瞬时GPU和功率可行性；\(\omega\) 负责GPU-hour、MWh、能源平衡、成本和碳排放。任务总GPU-hour为 \(g_ih_i\)。

共同外送上限为

$$
E_r^{\max}=\min\{X_r^{grid},X_r^{storage}\},
\tag{15}
$$

$$
0\le G_{rt}^{buy}\le I_r^{\max}y_{rt}^{grid},
\qquad
0\le G_{rt}^{sell}\le
E_r^{\max}(1-y_{rt}^{grid}),
\quad y_{rt}^{grid}\in\{0,1\}.
\tag{16}
$$

若无储能区域未给 `SellLimit_MW`，只有数据字典明确该限制不适用时才取 \(X_r^{storage}=+\infty\)；字段缺失且适用性无法判断时结构化停止。

运行成本与碳排放定义为

$$
C_{\mathrm{op}}=
\sum_{r,t}
\left(c_{rt}^{buy}G_{rt}^{buy}
-c_{rt}^{sell}G_{rt}^{sell}\right)\Delta t,
\tag{17}
$$

$$
E_{\mathrm{CO2}}=
\sum_{r,t}\kappa_{rt}G_{rt}^{buy}\Delta t.
\tag{18}
$$

## 联合 \(\varepsilon\) 路径的统一封闭规则

每个子问题先在其全部题面硬约束下求成本最优基准，并按预声明指标顺序以及“任务ID—区域—开工时刻”顺序词典序破同，使基准唯一。

对最小化指标 \(m_j\)，由成本基准值和对应单目标最优值构造

$$
m_j^{loose}=
\max\{m_j^{base},m_j^{single}\},\qquad
m_j^{ideal}=
\min\{m_j^{base},m_j^{single}\}.
\tag{19}
$$

五条路径 \(a\in\mathcal A_\varepsilon=\{0,0.25,0.5,0.75,1\}\) 使用

$$
\varepsilon_j(a)=
m_j^{loose}-a\left(m_j^{loose}-m_j^{ideal}\right),
\qquad m_j\le\varepsilon_j(a).
\tag{20}
$$

对最大化指标 \(U\)，先转为损失 \(1-U\)，或等价地定义

$$
U^{loose}=\min\{U^{base},U^{single}\},\qquad
U^{ideal}=\max\{U^{base},U^{single}\},
\tag{21}
$$

$$
U\ge U^{loose}
+a\left(U^{ideal}-U^{loose}\right).
\tag{22}
$$

必要锚点必须完整求解成功。失败、超时或指标不可计算时不得猜测阈值：题面必需比较指标失败则结构化停止；仅用于可选折中排序的指标标记为“不可计算”，并从路径约束和排序中删除。路径不可行是合法有限结果，不得放宽阈值伪造可行候选。

## 子问题 1：需求预测与末端基础调度

### 模型思路

先统计区域—任务类型的GPU需求和GPU-hour需求，再比较24小时季节性、168小时季节性和标准化Huber回归。所有含168阶滞后的回归样本从 \(t=168\) 开始，禁止负索引初始化。最后24小时使用实际到达任务；其资源背景由模型内部先生成的完整前序基础调度确定，不读取外部前序方案。

### 模型建立

区域—类型—小时聚合需求为

$$
D_{rkt}^{GPU}=
\sum_{i:o_i=r,k_i=k,a_i=t}g_i,
\qquad
D_{rkt}^{GPUh}=
\sum_{i:o_i=r,k_i=k,a_i=t}g_ih_i.
\tag{23}
$$

季节性候选为

$$
\widehat D_{rkt}^{(24)}=D_{rk,t-24},
\quad t\ge24,
\qquad
\widehat D_{rkt}^{(168)}=D_{rk,t-168},
\quad t\ge168.
\tag{24}
$$

候选比较统一在验证区间 \(2352{:}2375\) 进行，因此两种季节性候选的历史值均真实可观测，不需要任何补零或循环填充。

Huber回归候选为

$$
\widehat D_{rkt}=
\max\left\{
0,\,
\beta_0+
\sum_{\ell\in\{1,2,3,24,48,168\}}
\beta_\ell D_{rk,t-\ell}
+\gamma^\top z_t+\alpha_r+\delta_k
\right\},
\quad t\ge168,
\tag{25}
$$

其中 \(z_t\) 是由小时编号唯一计算的小时和星期正余弦周期特征；\(\alpha_r,\delta_k\) 分别为区域和任务类型固定效应。模型不构造任何 \(t<0\) 的滞后量。

候选选择拟合、验证、最终重训和测试集合固定为

$$
\mathcal T_{\mathrm{selection}}=\{168,\ldots,2351\},
\quad
\mathcal T_{\mathrm{validation}}=\{2352,\ldots,2375\},
\tag{26}
$$

$$
\mathcal T_{\mathrm{finalfit}}=\{168,\ldots,2375\},
\quad
\mathcal T_{\mathrm{test}}=\{2376,\ldots,2399\}.
\tag{27}
$$

选择阶段的标准化尺度仅由 \(\mathcal T_{\mathrm{selection}}\) 计算：

$$
\sigma_{rk}=
\max\left\{
\sqrt{\frac1{n_{rk}}
\sum_{t\in\mathcal T_{\mathrm{selection}}}
(D_{rkt}-\bar D_{rk})^2},
1\ {\rm GPU}
\right\}.
\tag{28}
$$

令 \(u_{rkt}=(D_{rkt}-\widehat D_{rkt})/\sigma_{rk}\)，Huber损失为

$$
\rho_\delta(u)=
\begin{cases}
u^2/2,&|u|\le\delta,\\
\delta(|u|-\delta/2),&|u|>\delta,
\end{cases}
\tag{29}
$$

选择阶段求解

$$
\min
\sum_{r,k}
\sum_{t\in\mathcal T_{\mathrm{selection}}}
\rho_\delta(u_{rkt})
+\lambda\|\beta\|_2^2,
\tag{30}
$$

$$
\delta\in\{0.5,1,1.5,2\},\qquad
\lambda\in
\{0,10^{-4},10^{-3},10^{-2},10^{-1},1\}.
\tag{31}
$$

验证集依次按WAPE、MAE、RMSE和固定候选枚举顺序选模。选定结构和超参数后，在 \(\mathcal T_{\mathrm{finalfit}}\) 上重新拟合全部系数，再递推预测 \(2376{:}2399\)。预测时每个滞后量只取预测时点之前的实际已观测值或先前预测值，禁止读取未来测试标签。

评价指标为

$$
MAE=\frac1n\sum_j|y_j-\widehat y_j|,
\qquad
RMSE=\sqrt{\frac1n\sum_j(y_j-\widehat y_j)^2},
\tag{32}
$$

$$
WAPE=
\frac{\sum_j|y_j-\widehat y_j|}
{\sum_j|y_j|}.
\tag{33}
$$

当WAPE分母为0时，该分组输出 `validation_unavailable`，保留MAE、RMSE及可计算的总体WAPE，不用任意小常数替代分母。若某候选在统一验证窗口没有完整预测，则该候选标记为不可用并排除选模。

#### 前序完整基础调度的确定性生成

定义全部前序任务集合

$$
\mathcal I^{<2376}=\{i:a_i<2376\}.
\tag{34}
$$

前序方案 \((r_i^0,s_i^0)\) 不是外部输入。先按以下唯一键排序全部前序任务：

$$
\operatorname{key}(i)=
\left(
\mathbf1\{i\notin\mathcal I_{\mathrm{RT}}\},
F_i,
-h_i,
TaskID_i
\right).
\tag{35}
$$

即实时任务优先，其后按有效截止升序、持续时间降序、TaskID升序。对排序后的每个任务 \(i\)，在完整有限整数候选域 \(\Omega_i\) 内，删除会违反式(9)–(12)瞬时GPU、IT或设施容量的候选，得到当前可行位置集 \(\Phi_i\)。实时任务的候选还必须满足 \(s=a_i\)。

若 \(\Phi_i=\varnothing\)，输出该任务的候选耗尽原因、冲突区域、冲突小时及GPU/IT/设施超限量，并结构化停止。否则按

$$
(r_i^0,s_i^0)=
\arg\min_{(r,s)\in\Phi_i}^{lex}
\left[
s-a_i,\,
\ell_{o_ir},\,
U_{irs}^{post},\,
RegionName(r),\,
s
\right],
\tag{36}
$$

选择唯一位置，其中放置后的最大GPU利用率为

$$
U_{irs}^{post}=
\max_{\substack{r'\in\mathcal R\\t=0,\ldots,2405}}
\frac{
B_{r't}^{GPU}
+g_i\chi_{it}(s)\mathbf1\{r'=r\}
}{G_{r'}^{\max}}.
\tag{37}
$$

\(B_{r't}^{GPU}\) 是当前已放置前序任务的瞬时GPU占用；若 \(G_{r'}^{\max}=0\)，该区域不生成任务候选，其利用率输出“不适用”。该规则在同一输入上产生唯一、可复现的完整前序基础方案。

从完整前序方案提取跨越2376时点的固定任务：

$$
\mathcal I^{pre}=
\{i:a_i<2376,\ s_i^0+h_i>2376\},
\quad
\mathcal I^{end}=
\{i:2376\le a_i\le2399\}.
\tag{38}
$$

固定瞬时占用为

$$
b_{rt}^{GPU}=
\sum_{\substack{i\in\mathcal I^{pre}\\r_i^0=r}}
g_i\chi_{it}(s_i^0),
\tag{39}
$$

$$
b_{rt}^{AI,cap}=
\sum_{\substack{i\in\mathcal I^{pre}\\r_i^0=r}}
g_ip_{k_i}^{GPU}\chi_{it}(s_i^0).
\tag{40}
$$

末端调度在 \(t=2376,\ldots,2405\) 满足

$$
b_{rt}^{GPU}+
\sum_{i\in\mathcal I^{end}}
\sum_{s:(r,s)\in\Omega_i}
g_i\chi_{it}(s)x_{irs}
\le G_r^{\max},
\tag{41}
$$

$$
L_{rt}^{AI,end,cap}=
b_{rt}^{AI,cap}+
\sum_{i\in\mathcal I^{end}}
\sum_{s:(r,s)\in\Omega_i}
g_ip_{k_i}^{GPU}\chi_{it}(s)x_{irs},
\tag{42}
$$

$$
L_{rt}^{N}+L_{rt}^{AI,end,cap}
\le P_r^{IT,\max},
\qquad
\pi_r(L_{rt}^{N}+L_{rt}^{AI,end,cap})
\le P_r^{F,\max}.
\tag{43}
$$

末端基础调度采用词典序目标

$$
\min_{\mathrm{lex}}
\left[
\sum_{i\in\mathcal I^{end}}(s_i-a_i),
\sum_{i\in\mathcal I^{end}}\ell_i,
U^{\max},
\text{任务ID—区域—开工时刻}
\right],
\tag{44}
$$

$$
U^{\max}\ge
\frac{
b_{rt}^{GPU}
+\sum_{i\in\mathcal I^{end}}\sum_s
g_i\chi_{it}(s)x_{irs}
}{G_r^{\max}},
\quad G_r^{\max}>0.
\tag{45}
$$

### 求解方法

先完成需求统计和候选预测模型选择，再按式(35)–(37)生成全部 \(a_i<2376\) 任务的完整基础可行调度。只有完整前序方案通过唯一执行、实时即时开工、截止、时延、瞬时GPU、IT、设施功率和2406禁占用审计后，才提取固定跨界占用并求解末端MILP。

最终代码必须把前序方案和末端方案拼成全部实际任务的统一轨迹，并对附件中的全部任务逐一复核式(5)–(14)。不得只审计 \(\mathcal I^{pre}\) 或 \(\mathcal I^{end}\)。

### 可观测性

GPU和GPU-hour需求标签可由实际到达数据观测。最优调度标签不可观测，因此不使用监督准确率；以任务唯一执行、时延、截止、瞬时容量、实际重叠能源和完整全时域轨迹作为代理验证。

### 必须回答的输出

1. 区域—任务类型GPU、GPU-hour及描述统计表。
2. 24小时、168小时季节性模型与Huber候选的验证集比较。
3. `selection_fit=168..2351`、`validation=2352..2375`、`final_fit=168..2375`及最终选模记录。
4. 测试集总体及分组MAE、RMSE、WAPE。
5. 全部前序任务的确定性基础调度生成状态和失败任务表。
6. 第2376–2399小时实际到达任务的区域、开工和完成时刻。
7. 2376时点仍占用资源的前序任务及跨越2399小时任务结清结果。
8. 最后24小时调度甘特图文件。
9. 区域逐时GPU利用率表和曲线。
10. 全部实际任务的唯一执行、到达、实时开工、截止、时延、瞬时GPU、IT、设施功率及2406禁占用审计表。

## 子问题 2：碳感知任务调度

### 模型思路

以全部实际任务和逐时电力参数为输入，在有限整数候选域中联合选择执行区域和开工时刻。瞬时容量使用 \(\chi\)，能源、成本和碳排放使用 \(\omega\)。问题二不使用储能。

### 模型建立

任务满足式(2)–(14)。无储能条件为

$$
R_{rt}^{ch}=G_{rt}^{ch}=C_{rt}=D_{rt}=0.
\tag{46}
$$

新能源分配及负荷平衡为

$$
R_{rt}^{use}+R_{rt}^{sell}+R_{rt}^{curt}
=R_{rt}^{av},
\tag{47}
$$

$$
G_{rt}^{buy}+R_{rt}^{use}
=L_{rt}^{F,avg},
\qquad
G_{rt}^{sell}=R_{rt}^{sell}.
\tag{48}
$$

式(48)中的 \(L_{rt}^{F,avg}\) 必须由式(13)–(14)计算，不得用瞬时容量负荷 \(L_{rt}^{F,cap}\) 替代。

GPU-hour加权平均网络时延为

$$
L_{\mathrm{net}}=
\frac{
\sum_{i,r,s}g_ih_i\ell_{o_ir}x_{irs}
}{
\sum_i g_ih_i
}.
\tag{49}
$$

新能源利用率为

$$
U_{\mathrm{RE}}^{q2}=
\frac{
\sum_{r,t}
(R_{rt}^{use}+R_{rt}^{sell})\Delta t
}{
\sum_{r,t}R_{rt}^{av}\Delta t
}.
\tag{50}
$$

式(49)或式(50)分母不正时，相应指标输出“不可计算”，并退出相关路径约束和候选排序。

定义 \(b^0\) 为全部问题二硬约束下按

$$
[C_{\mathrm{op}},E_{\mathrm{CO2}},L_{\mathrm{net}},
-U_{\mathrm{RE}}^{q2},
\text{任务ID—区域—开工时刻}]
\tag{51}
$$

词典序唯一化的成本最优方案。分别求碳排最优、时延最优和新能源利用率最优锚点，按式(19)–(22)生成

$$
\varepsilon_C(a),\qquad
\varepsilon_L(a),\qquad
\varepsilon_U(a).
\tag{52}
$$

五条正式模型为

$$
\min C_{\mathrm{op}},
\tag{53}
$$

$$
E_{\mathrm{CO2}}\le\varepsilon_C(a),\qquad
L_{\mathrm{net}}\le\varepsilon_L(a),\qquad
U_{\mathrm{RE}}^{q2}\ge\varepsilon_U(a).
\tag{54}
$$

### 求解方法

固定 \(H=168\) 小时滚动求解。窗口传递未完成任务及其固定区域和剩余占用、累计碳、时延分子与分母、新能源利用量和可用量。先完成成本基准及三个必要锚点，再生成五条路径。仅保留完整求解、窗口拼接可行并通过全时域复算的候选。

结果限定为实际完成候选集上的best-found，并固定报告 `global_optimality_certificate=false`。

### 可观测性

真实全局最优标签不可观测；任务硬约束、瞬时容量、基于 \(\omega\) 的小时能源、购售边界、成本、碳排和新能源利用量均可从附件与完整轨迹复算。

### 必须回答的输出

1. 全部实际任务的执行区域、开工和完成时刻。
2. 区域逐时AI IT电量、AI小时平均IT、总IT和设施负荷。
3. 逐时购电、新能源直用、外送和弃电策略。
4. 成本、碳排、平均及高分位网络时延、新能源利用率。
5. 相对问题一基础调度的绝对及相对变化。
6. 五条联合路径有限候选表、非支配关系和图。
7. 各任务类型迁移数、GPU-hour、等待和时延。
8. 累计预算、购售边界与互斥、窗口状态和窗口间隙审计。
9. `full_horizon_feasible`与`global_optimality_certificate=false`。

## 子问题 3：固定负荷下的储能协同优化

### 模型思路

固定附件中的 `Baseline_AI_IT_Load_MW` 和 `NonAI_IT_Load_MW`，仅优化新能源分配、储能充放电及购售电，不重新调度任务。

### 模型建立

设施小时平均负荷固定为

$$
L_{rt}^{F,avg}
=\pi_r(L_{rt}^{BAI}+L_{rt}^{N}).
\tag{55}
$$

若给定IT负荷或设施负荷超过附件硬上限，输出区域、小时及超限量并结构化停止。

能源分源为

$$
R_{rt}^{use}+R_{rt}^{ch}
+R_{rt}^{sell}+R_{rt}^{curt}
=R_{rt}^{av},
\tag{56}
$$

$$
G_{rt}^{load}+R_{rt}^{use}+D_{rt}
=L_{rt}^{F,avg},
\tag{57}
$$

$$
C_{rt}=R_{rt}^{ch}+G_{rt}^{ch},
\quad
G_{rt}^{buy}=G_{rt}^{load}+G_{rt}^{ch},
\quad
G_{rt}^{sell}=R_{rt}^{sell}.
\tag{58}
$$

购售边界使用式(15)–(16)。SOC动态为

$$
S_{r,-1}=S_r^0,
\tag{59}
$$

$$
S_{rt}=S_{r,t-1}
+\eta_r^cC_{rt}\Delta t
-\frac{D_{rt}\Delta t}{\eta_r^d},
\tag{60}
$$

$$
S_r^{min}\le S_{rt}\le S_r^{max},
\qquad
S_{r,2406}\ge S_r^0.
\tag{61}
$$

充放电互斥为

$$
0\le C_{rt}\le u_{rt}^cC_r^{\max},
\qquad
0\le D_{rt}\le(1-u_{rt}^c)D_r^{\max},
\quad u_{rt}^c\in\{0,1\}.
\tag{62}
$$

净购电、峰值和绝对爬坡量为

$$
N_{rt}=G_{rt}^{buy}-G_{rt}^{sell},
\qquad
P_r^{peak}\ge N_{rt},
\tag{63}
$$

$$
z_{rt}\ge N_{rt}-N_{r,t-1},
\qquad
z_{rt}\ge-(N_{rt}-N_{r,t-1}),
\tag{64}
$$

$$
V_r=\sum_{t=1}^{2406}z_{rt}.
\tag{65}
$$

最终必须从净购电轨迹复算

$$
\widehat P_r^{peak}=\max_tN_{rt},
\qquad
\widehat V_r=
\sum_{t=1}^{2406}|N_{rt}-N_{r,t-1}|.
\tag{66}
$$

定义 \(b^3\) 为全部问题三硬约束下按成本、碳、峰值、爬坡和固定变量顺序词典序唯一化的成本最优方案。分别求碳、每个区域峰值和每个区域爬坡量的单目标锚点，生成

$$
\varepsilon_C(a),\qquad
\varepsilon_{P,r}(a),\qquad
\varepsilon_{V,r}(a).
\tag{67}
$$

正式目标及路径约束为

$$
\min_{\mathrm{lex}}
\left[
C_{\mathrm{op}},
\sum_rP_r^{peak}+\sum_{r,t}z_{rt}
\right],
\tag{68}
$$

$$
E_{\mathrm{CO2}}\le\varepsilon_C(a),
\quad
P_r^{peak}\le\varepsilon_{P,r}(a),
\quad
V_r\le\varepsilon_{V,r}(a).
\tag{69}
$$

新能源利用率和等效完整循环量为

$$
U_{\mathrm{RE}}^{q3}=
\frac{
\sum_{r,t}
(R_{rt}^{use}+R_{rt}^{ch}+R_{rt}^{sell})\Delta t
}{
\sum_{r,t}R_{rt}^{av}\Delta t
},
\tag{70}
$$

$$
N_r^{EFC}=
\frac{\sum_t(C_{rt}+D_{rt})\Delta t}{2B_r}.
\tag{71}
$$

式(70)分母为0时输出“不可计算”；式(71)仅在 \(B_r>0\) 时计算，否则输出“不适用”。

### 求解方法

先求无储能参照、成本基准和式(67)所需锚点，再生成最多五条路径。必要锚点未完成时结构化停止，不使用部分结果。所有输出必须从最终能源流和SOC轨迹重新计算。

### 可观测性

最优储能动作不可观测；附件SOC仅作为基准状态对照。能源守恒、SOC递推、终端SOC、互斥和净购电轨迹均可直接验证。

### 必须回答的输出

1. 各区域0–2406小时新能源、充放电、购售电和弃电策略。
2. 绝对SOC轨迹和终端SOC。
3. 储能前后成本、碳排、峰值净购电和绝对爬坡量。
4. 指标绝对及相对变化。
5. 各区域等效完整循环量。
6. SOC、充放电和净购电曲线。
7. 能源、SOC、购售、充放互斥及终端状态审计。
8. 含新能源充电的新能源利用率核验。
9. 锚点状态、路径状态、窗口间隙及非全局最优声明。

## 子问题 4：多区域算—储—电联合优化

### 模型思路

联合决定任务执行区域、整数开工时刻、逐时能源流和储能动作，并统一权衡成本、碳排、网络时延、服务质量、新能源利用率和区域峰值净购电。

### 模型建立

任务满足式(2)–(14)，能源和储能满足式(15)–(18)、式(56)–(65)。问题四设施小时平均负荷必须由实际任务重叠电量计算：

$$
L_{rt}^{F,avg}
=\pi_r\left[
L_{rt}^{N}+
\frac1{\Delta t}
\sum_i\sum_s
g_ip_{k_i}^{GPU}\omega_{it}(s)x_{irs}
\right].
\tag{72}
$$

新能源利用率为

$$
U_{\mathrm{RE}}^{q4}=
\frac{
\sum_{r,t}
(R_{rt}^{use}+R_{rt}^{ch}+R_{rt}^{sell})\Delta t
}{
\sum_{r,t}R_{rt}^{av}\Delta t
}.
\tag{73}
$$

有效等待任务集合为

$$
\mathcal I_{\mathrm{wait}}=
\{i:i\notin\mathcal I_{\mathrm{RT}},
\ \Omega_i\ne\varnothing,\ W_i^{\max}\ge0\}.
\tag{74}
$$

服务质量分量为

$$
Q_{\mathrm{RT}}=
\frac{\#\{i\in\mathcal I_{\mathrm{RT}}:s_i=a_i\}}
{\#\mathcal I_{\mathrm{RT}}},
\tag{75}
$$

$$
Q_{\mathrm{SLA}}=
\frac{\#\{i:\ell_i\le\ell_i^{\max}\}}{\#\mathcal I},
\qquad
Q_{\mathrm{deadline}}=
\frac{\#\{i:c_i\le F_i\}}{\#\mathcal I},
\tag{76}
$$

$$
Q_{\mathrm{wait}}=
1-
\frac{
\sum_{i\in\mathcal I_{\mathrm{wait}}}(s_i-a_i)
}{
\sum_{i\in\mathcal I_{\mathrm{wait}}}W_i^{\max}
}.
\tag{77}
$$

每个分量只在其分母为正时计算。令 \(J_{\mathrm{def}}\) 为可计算分量集合，则

$$
Q_{\mathrm{service}}=
\frac1{|J_{\mathrm{def}}|}
\sum_{j\in J_{\mathrm{def}}}Q_j.
\tag{78}
$$

若 \(J_{\mathrm{def}}=\varnothing\)，服务质量输出“不可计算”并退出路径约束和候选排序。实时开工、SLA和截止分量主要承担硬约束审计作用；在全部硬约束可行方案中，等待分量用于区分弹性调度质量。

等待质量下界可线性写为

$$
\sum_{i\in\mathcal I_{\mathrm{wait}}}(s_i-a_i)
\le
(1-\varepsilon_{\mathrm{wait}})
\sum_{i\in\mathcal I_{\mathrm{wait}}}W_i^{\max}.
\tag{79}
$$

定义统一基准 \(b^4\) 为全部题面硬约束下按

$$
[
C_{\mathrm{op}},
E_{\mathrm{CO2}},
L_{\mathrm{net}},
1-Q_{\mathrm{service}},
1-U_{\mathrm{RE}}^{q4},
\sum_rP_r^{peak},
\text{任务ID—区域—开工时刻}
]
\tag{80}
$$

词典序唯一化的成本最优方案，并固定

$$
E^0=E_{\mathrm{CO2}}(b^4).
\tag{81}
$$

分别最小化 \(E_{\mathrm{CO2}}\)、\(L_{\mathrm{net}}\)、\(1-Q_{\mathrm{service}}\)、\(1-U_{\mathrm{RE}}^{q4}\) 和每个 \(P_r^{peak}\)，按式(19)–(22)生成五条路径阈值。正式模型为

$$
\min C_{\mathrm{op}},
\tag{82}
$$

$$
E_{\mathrm{CO2}}\le\varepsilon_C(a),
\qquad
L_{\mathrm{net}}\le\varepsilon_L(a),
\tag{83}
$$

$$
1-Q_{\mathrm{service}}
\le\varepsilon_{1-Q}(a),
\qquad
1-U_{\mathrm{RE}}^{q4}
\le\varepsilon_{1-U}(a),
\tag{84}
$$

$$
P_r^{peak}\le\varepsilon_{P,r}(a),
\qquad r\in\mathcal R.
\tag{85}
$$

有限候选损失向量为

$$
y_m=
(C_{\mathrm{op}},E_{\mathrm{CO2}},L_{\mathrm{net}},
1-Q_{\mathrm{service}},1-U_{\mathrm{RE}}^{q4},
\widehat P_1^{peak},\ldots,\widehat P_6^{peak})_m.
\tag{86}
$$

仅保留可计算且候选极差为正的维度 \(J_{\mathrm{disc}}\)，定义

$$
\bar y_{jm}=
\frac{y_{jm}-\min_ny_{jn}}
{\max_ny_{jn}-\min_ny_{jn}},
\tag{87}
$$

$$
m^*=
\arg\min_m
\sqrt{
\frac1{|J_{\mathrm{disc}}|}
\sum_{j\in J_{\mathrm{disc}}}\bar y_{jm}^2
}.
\tag{88}
$$

若 \(J_{\mathrm{disc}}=\varnothing\)，按成本、碳排、时延和固定候选编号词典序选择，不使用任意 \(\epsilon\) 制造分母。

### 情景模型

所有情景相对同一基准 \(b^4\) 比较，不重新定义 \(E^0\)。

碳约束情景为

$$
E_{\mathrm{CO2}}\le(1-\rho_C)E^0,
\qquad
\rho_C\in\{0,0.1,0.2,0.3\}.
\tag{89}
$$

购电峰谷价差情景为

$$
c_{rt}^{buy,sc}
=\bar c_r+
\delta_P(c_{rt}^{buy}-\bar c_r),
\qquad
\bar c_r=
\frac1{2407}\sum_{t=0}^{2406}c_{rt}^{buy},
\tag{90}
$$

$$
\delta_P\in\{0.75,1,1.25\}.
\tag{91}
$$

售电机制情景为

$$
c_{rt}^{sell,sc}
=\delta_Sc_{rt}^{sell},
\qquad
\delta_S\in\{0,0.5,1\}.
\tag{92}
$$

新能源水平情景为

$$
R_{rt}^{av,level}
=\max\{0,\delta_RR_{rt}^{av}\},
\qquad
\delta_R\in\{0.8,1,1.2\}.
\tag{93}
$$

新能源波动增强情景为

$$
R_{rt}^{av,vol}
=\max\{0,R_{rt}^{av}+\sigma_{sc}\xi_{rt}\}.
\tag{94}
$$

随机种子固定为2026；对每个区域，\(\xi_{rt}\) 由固定伪随机序列标准化为样本均值0、样本方差1。若该区域存在正新能源样本，则

$$
\sigma_{sc}
=0.1\operatorname{mean}
\{R_{rt}^{av}:R_{rt}^{av}>0\};
\tag{95}
$$

否则 \(\sigma_{sc}=0\)，该区域波动增强情景与基准新能源序列一致并明确标注“无正新能源样本”。

七类报告口径为：碳约束、低峰谷价差、基准峰谷价差、高峰谷价差、无售电、折价售电、原价售电；新能源下降、基准、上升及波动增强作为独立新能源情景组另行完整报告。各情景均重新求解，不把基准决策机械复制为情景结果。

### 求解方法

固定168小时滚动联合MILP，传递未完成任务及剩余占用、SOC、累计碳、时延分子与分母、新能源利用量、可用量和有效等待量。先求统一基准及必要锚点，再按封闭公式生成五条路径；完整复算后选择折中方案并逐一重求情景。

所有子问题共享单次代码运行预算

$$
B_{\mathrm{total}}=300\ {\rm s},\qquad
T_{\mathrm{tail}}=15\ {\rm s},
\qquad
D_{\mathrm{search}}=t_{\mathrm{start}}+285\ {\rm s}.
\tag{96}
$$

代码使用 `time.monotonic()` 记录实际耗时。标定、问题一固定工作、问题二、问题三、问题四、情景候选和文件输出共用同一总截止。每个固定任务、锚点、窗口和候选启动前检查共同截止；可中断循环在内部再次检查。已启动候选可越过搜索截止，但必须在总截止前完整结束，否则中断并丢弃，不使用部分结果。固定必答工作若超时，携带实际耗时结构化失败，不缩减任务后伪装完成。

### 可观测性

联合全局最优标签不可观测。任务轨迹、瞬时容量、小时能源、SOC、成本、碳排、购售边界、等待量和情景输入均可从附件与决策复算，故使用机制一致性、完整轨迹和有限候选比较作为代理验证。

### 必须回答的输出

1. 折中方案逐任务区域、开工、完成、等待和时延。
2. 各区域逐时AI IT电量、小时平均设施负荷、新能源、储能、购售电和SOC。
3. 成本、碳排、时延、服务质量、新能源利用率和峰值净购电。
4. 五条联合路径有限候选表、非支配关系和折中方案。
5. 不同碳约束下的指标、迁移、循环和可行性变化。
6. 不同购电峰谷价差及售电机制下的策略变化。
7. 新能源上升、下降、基准和波动增强情景变化。
8. 各情景相对统一基准 \(b^4\) 的绝对及相对变化。
9. 各任务类型迁移数、GPU-hour、等待和时延。
10. 各区域峰值、爬坡量和等效循环量。
11. 锚点状态、累计预算、窗口衔接、购售边界与互斥、求解状态和窗口间隙审计。
12. 候选图、负荷与SOC曲线、迁移流向图和情景比较图。
13. `full_horizon_feasible`与`global_optimality_certificate=false`。

## 统一结果审计

任务审计对全部实际任务逐项核验

$$
i\in\mathcal I_{\mathrm{RT}}\Rightarrow s_i=a_i,
\qquad
a_i\le s_i,
\qquad
c_i\le F_i,
\qquad
\ell_i\le\ell_i^{\max},
\tag{97}
$$

$$
s_i\in\mathcal S,\qquad
\omega_{i,2406}(s_i)=0,
\tag{98}
$$

以及式(9)–(14)中的瞬时容量与小时能源口径。问题一必须审计完整前序方案与末端方案拼接后的全部任务，问题二和问题四必须审计全部实际任务，不得只抽查窗口或末端子集。

问题二能源残差为

$$
e_{rt}^{q2}=
G_{rt}^{buy}+R_{rt}^{av}
-L_{rt}^{F,avg}
-G_{rt}^{sell}
-R_{rt}^{curt}.
\tag{99}
$$

问题三、四能源和SOC残差为

$$
e_{rt}^{energy}=
G_{rt}^{buy}+R_{rt}^{av}+D_{rt}
-L_{rt}^{F,avg}
-C_{rt}
-G_{rt}^{sell}
-R_{rt}^{curt},
\tag{100}
$$

$$
e_{rt}^{SOC}=
S_{rt}-S_{r,t-1}
-\eta_r^cC_{rt}\Delta t
+\frac{D_{rt}\Delta t}{\eta_r^d}.
\tag{101}
$$

所有连续残差归一化为

$$
\widetilde e_j=\frac{|e_j|}{s_j}
\le\tau_{num}=10^{-6}.
\tag{102}
$$

GPU、MW和MWh残差的尺度 \(s_j\) 优先取附件对应硬上限；硬上限缺失或非正时，必须在求解前固定为

$$
s_j=
\max\{1,\max|\text{对应输入量}|\}.
\tag{103}
$$

比例和计数残差取 \(s_j=1\)。不得查看结果后调整尺度。离散约束必须满足求解器整数可行性条件。

只有下列条件全部满足，才令 `full_horizon_feasible=true`：

1. 所有适用连续残差通过式(102)；
2. 所有二元变量和整数开工时刻满足离散可行性；
3. 全部任务唯一执行，实时任务即时开工，时延和截止均满足；
4. 全时域瞬时GPU、IT和设施功率不超限；
5. `MaxGridExport_MW` 与 `SellLimit_MW` 两项边界均满足；
6. 购售电和充放电互斥均满足；
7. 第2406小时执行任务数为0，未完成任务数为0；
8. 问题三和问题四满足终端SOC约束。

## 局限性与停止规则

1. 任务、电价、碳强度和新能源按附件确定值或明确情景值处理。
2. 网络只使用单向时延，不建立带宽、迁移数据量、传输能耗、传输费用或线路潮流。
3. PUE、GPU功率、容量、购售边界和储能参数严格读取附件。
4. 预测测试集不参与模型选择或调参。
5. 所有含168阶滞后的回归样本从 \(t=168\) 开始；禁止负索引、补零、循环填充或其他临时初始化。
6. 前序基础方案由式(35)–(37)在模型内部确定性生成，不接受未经同一规则验证的外部前序文件。
7. 空候选、前序任务无可行位置、输入硬边界矛盾、必要锚点失败、预算超时、滚动拼接失败或无完整可行解时结构化停止。
8. 任一业务指标分母不正时输出“不可计算”或“不适用”，不使用任意小常数替代。
9. 五条路径仅是有限候选集，不代表完整连续Pareto前沿。
10. 窗口间隙只说明对应窗口求解状态；全时域复算只能证明所得轨迹可行。
11. 超过共同截止或未完整完成的锚点、窗口及候选不得进入正式比较。
12. 当前未执行外部搜索，未执行搜索不得作为参数、算法性能或经验阈值来源。

## Verifier 修复核对表

| Block issue | 修复公式/约束位置 | 如何保证可计算和有限输出 |
|---|---|---|
| Huber回归在训练早期引用 \(t<0\) 的滞后需求 | 式(25)–(31)，尤其是式(26)–(27) | 所有含lag168的候选只在 \(t\ge168\) 构造；`selection_fit`固定为168–2351，验证为2352–2375，选模后`final_fit`固定为168–2375，再预测2376–2399。明确禁止负索引、补零和循环初始化。 |
| 开工索引 \(s\) 未限定为有限整数集合 | 式(1)、式(5)–(8)、式(98) | 显式定义 \(\mathcal S=\{0,\ldots,2405\}\subset\mathbb Z\)，每个 \(\Omega_i\) 因而是有限可枚举集合；同时要求到达、有效截止、网络时延和 \(\omega_{i,2406}(s)=0\)，使MILP索引及2406禁占用边界闭合。 |
| 问题一依赖未给生成规则的外部前序方案 | 式(34)–(43)及问题一求解方法 | 前序方案改为模型内部生成：全部 \(a_i<2376\) 任务按实时优先、截止、时长、TaskID确定性排序，在完整整数候选域内按同一 \(\chi\) 瞬时GPU/IT/设施、时延和截止约束逐项放置；无位置立即结构化失败。随后冻结2376后仍占用资源的前序任务，并与最后24小时任务共同检查容量。 |
| 前序占用可能导致末端容量冲突 | 式(39)–(43) | 用前序完整方案直接计算固定GPU和AI瞬时功率占用，并把它们加入末端GPU、IT和设施功率约束，不允许末端任务重复使用已占资源。 |
| 仅审计末端子集可能遗漏完整轨迹错误 | 问题一求解方法、统一审计式(97)–(103) | 强制将前序和末端方案拼接后，对附件中的全部实际任务进行0–2406全时域复核；只有全部任务、容量、能源和终端约束通过，才可输出`full_horizon_feasible=true`。 |