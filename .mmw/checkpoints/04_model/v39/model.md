# 数学模型

## 符号说明

| 符号 | 含义 | 类型及数据来源 | 取值范围/单位 |
|---|---|---|---|
| \(i,r,t,s,k\) | 任务、区域、小时、整数开工时刻、任务类型索引 | 索引 | \(r\in\mathcal R,\ t=0,\ldots,2406\) |
| \(\mathcal R,\mathcal K\) | 六区域、三任务类型集合 | 题面直接给定 | 无 |
| \(\mathcal S\) | 有限整数开工时刻集合 | 题面小时粒度推导 | \(\{0,\ldots,2405\}\) |
| \(a_i,d_i,h_i\) | 到达小时、持续分钟、持续小时 | `workload_trace.xlsx`及 \(h_i=d_i/60\) | h、min、h |
| \(g_i,k_i,o_i\) | GPU需求、任务类型、来源区域 | `workload_trace.xlsx` | GPU、无、无 |
| \(F_i,W_i^{\max}\) | 有效截止、最大允许等待 | 附件及派生 | h |
| \(\ell_i^{\max},\ell_{or}\) | 最大允许时延、单向区域时延 | 工作负载和网络附件 | ms |
| \(\Delta t\) | 时段长度 | 题面直接给定 | \(1\) h |
| \(\omega_{it}(s),\chi_{it}(s)\) | 实际重叠时长、瞬时占用指示 | 派生 | h、\(\{0,1\}\) |
| \(\Omega_i\) | 任务完整有限候选集合 | 派生 | 区域—整数时刻对 |
| \(x_{irs}\) | 是否在区域 \(r\) 于 \(s\) 开工 | 决策变量 | \(\{0,1\}\) |
| \(q_{ir},s_i,c_i,\ell_i\) | 区域指示、开工、完成、实际时延 | 派生 | 无、h、h、ms |
| \(G_r^{\max}\) | 可调度GPU容量 | `GPU_information.xlsx` | 等效GPU |
| \(P_r^{IT,\max},P_r^{F,\max}\) | IT、设施瞬时功率上限 | `GPU_information.xlsx` | MW |
| \(p_k^{GPU},\pi_r\) | 每GPU平均IT功率、PUE | 功率映射及GPU附件 | MW/GPU、无量纲 |
| \(L_{rt}^{N},L_{rt}^{BAI}\) | NonAI、问题三Baseline AI负荷 | `region_time_data.xlsx` | MW |
| \(L_{rt}^{AI,cap},L_{rt}^{AI,avg}\) | AI瞬时、小时平均IT功率 | 派生 | MW |
| \(L_{rt}^{F,cap},L_{rt}^{F,avg}\) | 瞬时、小时平均设施负荷 | 派生 | MW |
| \(R^{av},R^{use},R^{ch},R^{sell},R^{curt}\) | 可用、直用、充电、外送、弃用新能源 | 输入或变量 | MW |
| \(G^{load},G^{ch},G^{buy},G^{sell}\) | 电网供负荷、充电、购电、外送 | 变量 | MW |
| \(C_{rt},D_{rt},S_{rt}\) | 储能充电、放电、时段末SOC | 变量 | MW、MW、MWh |
| \(B_r,S_r^0,S_r^{min},S_r^{max}\) | 额定容量、初始SOC、SOC边界 | 储能附件 | MWh |
| \(\eta_r^c,\eta_r^d,C_r^{\max},D_r^{\max}\) | 效率及充放功率上限 | 储能附件 | 无量纲、MW |
| \(I_r^{\max},X_r^{grid},X_r^{storage}\) | 购电、区域外送、储能外送边界 | 附件 | MW |
| \(E_r^{\max}\) | 共同外送上限 | 派生 | MW |
| \(y_{rt}^{grid},u_{rt}^{c}\) | 购售、充放互斥变量 | 决策变量 | \(\{0,1\}\) |
| \(c_{rt}^{buy},c_{rt}^{sell},\kappa_{rt}\) | 购价、售价、碳强度 | 区域逐时附件 | 元/MWh、tCO2/MWh |
| \(N_{rt},P_r^{peak},z_{rt},V_r\) | 净购电、非负购电峰值、爬坡辅助量、总绝对爬坡 | 派生或变量 | MW |
| \(D_{rkt}\) | 区域—类型—小时GPU到达需求 | 工作负载聚合 | GPU |
| \(\beta,\gamma,\alpha_r,\delta_k\) | 滞后系数、周期系数、区域及类型固定效应 | 待拟合 | 与设计矩阵相容 |
| \(r_0,k_0\) | 固定效应基准组 | 固定 | RegionA、RealTimeInference |
| \(\sigma_{rk},\rho_\delta,\lambda\) | 标准化尺度、Huber损失、正则参数 | 训练数据或固定网格 | GPU、无量纲 |
| \(C_{\mathrm{op}},E_{\mathrm{CO2}}\) | 运行成本、购电碳排放 | 指标 | 元、tCO2 |
| \(L_{\mathrm{net}},U_{\mathrm{RE}},Q_{\mathrm{service}}\) | 网络时延、新能源利用率、服务质量 | 指标 | ms、无量纲 |
| \(b^0,b^3,b^4\) | 问题二、三、四成本最优基准 | 优化产生 | 方案 |
| \(m_j^{loose},m_j^{ideal}\) | 指标宽松端点和理想端点 | 基准及单目标锚点 | 与指标一致 |
| \(E^0\) | 问题四统一基准碳排放 | 派生 | tCO2 |
| \(H\) | 滚动窗口长度 | 固定 | \(168\) h |
| \(B_{\mathrm{total}},T_{\mathrm{tail}}\) | 总墙钟预算、终检预留 | 固定合同 | 300 s、15 s |
| \(D_{\mathrm{search}},D_{\mathrm{total}}\) | 搜索截止、总截止 | 单调时钟派生 | \(t_{\mathrm{start}}+285\)、\(t_{\mathrm{start}}+300\) |
| \(T_{\mathrm{call}}\) | 单次求解动态硬时限 | 运行时派生 | s |
| \(\tau_{\mathrm{num}}\) | 归一化审计容差 | 固定 | \(10^{-6}\) |

附件数值、回归系数、预测误差、锚点和优化结果均由代码阶段读取真实附件后计算；当前不预填任何拟合或最优结果。

## 统一任务、容量与能源边界

任务到达、结清和终端时域为

$$
\mathcal T_A=\{0,\ldots,2399\},\quad
\mathcal T_C=\{2400,\ldots,2405\},\quad
\mathcal S=\{0,\ldots,2405\},\quad
t_{\mathrm{terminal}}=2406.
\tag{1}
$$

若 `LatestFinishHour` 为合法有限值则使用该值；若数据字典明确为空或不适用于该弹性任务，则取2406；其余非法值结构化停止。定义

$$
h_i=\frac{d_i}{60},\qquad
F_i=\min\{f_i^{valid},2406\},\qquad
W_i^{\max}=F_i-a_i-h_i.
\tag{2}
$$

任务与小时区间 \([t,t+1)\) 的重叠时长和瞬时占用为

$$
\omega_{it}(s)=
\max\{0,\min(t+\Delta t,s+h_i)-\max(t,s)\},
\tag{3}
$$

$$
\chi_{it}(s)=\mathbf1\{\omega_{it}(s)>0\}.
\tag{4}
$$

完整有限候选集合为

$$
\Omega_i=
\{(r,s):r\in\mathcal R,\ s\in\mathcal S,\ s\in\mathbb Z,\
s\ge a_i,\ s+h_i\le F_i,\
\ell_{o_ir}\le\ell_i^{\max},\
\omega_{i,2406}(s)=0\}.
\tag{5}
$$

若输入数据本身使 \(\Omega_i=\varnothing\)，输出任务ID及各排除原因并结构化停止。唯一执行及派生状态为

$$
\sum_{(r,s)\in\Omega_i}x_{irs}=1,\qquad
q_{ir}=\sum_{s:(r,s)\in\Omega_i}x_{irs},
\tag{6}
$$

$$
s_i=\sum_{r,s}sx_{irs},\quad
c_i=s_i+h_i,\quad
\ell_i=\sum_r\ell_{o_ir}q_{ir}.
\tag{7}
$$

实时任务满足

$$
s_i=a_i,\qquad i\in\mathcal I_{\mathrm{RT}}.
\tag{8}
$$

瞬时容量使用 \(\chi\)：

$$
\sum_{i,s}g_i\chi_{it}(s)x_{irs}\le G_r^{\max},
\tag{9}
$$

$$
L_{rt}^{AI,cap}=\sum_{i,s}g_ip_{k_i}^{GPU}\chi_{it}(s)x_{irs},
\tag{10}
$$

$$
L_{rt}^{N}+L_{rt}^{AI,cap}\le P_r^{IT,\max},\qquad
\pi_r(L_{rt}^{N}+L_{rt}^{AI,cap})\le P_r^{F,\max}.
\tag{11}
$$

小时能源结算使用 \(\omega\)：

$$
E_{rt}^{AI}=\sum_{i,s}g_ip_{k_i}^{GPU}\omega_{it}(s)x_{irs},
\tag{12}
$$

$$
L_{rt}^{AI,avg}=\frac{E_{rt}^{AI}}{\Delta t},\qquad
L_{rt}^{F,avg}=\pi_r(L_{rt}^{N}+L_{rt}^{AI,avg}).
\tag{13}
$$

共同外送边界及购售互斥为

$$
E_r^{\max}=\min\{X_r^{grid},X_r^{storage}\},
\tag{14}
$$

$$
0\le G_{rt}^{buy}\le I_r^{\max}y_{rt}^{grid},\qquad
0\le G_{rt}^{sell}\le E_r^{\max}(1-y_{rt}^{grid}),
\quad y_{rt}^{grid}\in\{0,1\}.
\tag{15}
$$

运行成本和碳排放为

$$
C_{\mathrm{op}}=\sum_{r,t}
(c_{rt}^{buy}G_{rt}^{buy}-c_{rt}^{sell}G_{rt}^{sell})\Delta t,
\tag{16}
$$

$$
E_{\mathrm{CO2}}=\sum_{r,t}
\kappa_{rt}G_{rt}^{buy}\Delta t.
\tag{17}
$$

## 联合 \(\varepsilon\) 路径

对最小化指标 \(m_j\)，由成本基准和单目标锚点构造

$$
m_j^{loose}=\max\{m_j^{base},m_j^{single}\},\qquad
m_j^{ideal}=\min\{m_j^{base},m_j^{single}\},
\tag{18}
$$

$$
\varepsilon_j(a)=m_j^{loose}
-a(m_j^{loose}-m_j^{ideal}),\qquad
a\in\{0,0.25,0.5,0.75,1\}.
\tag{19}
$$

对最大化指标 \(U\)：

$$
U^{loose}=\min\{U^{base},U^{single}\},\qquad
U^{ideal}=\max\{U^{base},U^{single}\},
\tag{20}
$$

$$
U\ge U^{loose}+a(U^{ideal}-U^{loose}).
\tag{21}
$$

必要锚点失败或超时不得猜测阈值。不可行路径作为有限结果报告，不放宽题面硬约束。

## 子问题 1：需求预测与末端基础调度

### 模型思路

统计区域—类型GPU与GPU-hour需求，比较24小时、168小时季节性模型和Huber回归。末端调度使用实际到达任务。确定性贪心只作为快速初始解生成器，不再把贪心候选耗尽解释为原调度不可行。

### 模型建立

聚合需求为

$$
D_{rkt}^{GPU}=\sum_{i:o_i=r,k_i=k,a_i=t}g_i,\qquad
D_{rkt}^{GPUh}=\sum_{i:o_i=r,k_i=k,a_i=t}g_ih_i.
\tag{22}
$$

季节性候选为

$$
\widehat D_{rkt}^{(24)}=D_{rk,t-24},\qquad
\widehat D_{rkt}^{(168)}=D_{rk,t-168}.
\tag{23}
$$

Huber候选为

$$
\widehat D_{rkt}=
\max\left\{0,\beta_0+
\sum_{\ell\in\{1,2,3,24,48,168\}}\beta_\ell D_{rk,t-\ell}
+\gamma^\top z_t+\alpha_r+\delta_k\right\},
\quad t\ge168.
\tag{24}
$$

为消除截距、完整区域固定效应和完整类型固定效应之间的线性相关，固定基准组：

$$
\alpha_{\mathrm{RegionA}}=0,\qquad
\delta_{\mathrm{RealTimeInference}}=0.
\tag{25}
$$

因此其余固定效应表示相对基准组的差异，参数表示唯一可识别。训练、验证、重训和测试区间为

$$
\mathcal T_{\mathrm{selection}}=\{168,\ldots,2351\},\quad
\mathcal T_{\mathrm{validation}}=\{2352,\ldots,2375\},
\tag{26}
$$

$$
\mathcal T_{\mathrm{finalfit}}=\{168,\ldots,2375\},\quad
\mathcal T_{\mathrm{test}}=\{2376,\ldots,2399\}.
\tag{27}
$$

训练尺度为

$$
\sigma_{rk}=
\max\left\{
\sqrt{\frac1{n_{rk}}\sum_{t\in\mathcal T_{\mathrm{selection}}}
(D_{rkt}-\bar D_{rk})^2},1\ {\rm GPU}
\right\}.
\tag{28}
$$

令 \(u=(D-\widehat D)/\sigma_{rk}\)，Huber损失为

$$
\rho_\delta(u)=
\begin{cases}
u^2/2,&|u|\le\delta,\\
\delta(|u|-\delta/2),&|u|>\delta.
\end{cases}
\tag{29}
$$

拟合问题为

$$
\min_{\beta,\gamma,\alpha,\delta_k}
\sum_{r,k,t\in\mathcal T_{\mathrm{selection}}}
\rho_\delta(u_{rkt})+\lambda\|\theta\|_2^2,
\tag{30}
$$

$$
\delta\in\{0.5,1,1.5,2\},\qquad
\lambda\in\{0,10^{-4},10^{-3},10^{-2},10^{-1},1\},
\tag{31}
$$

其中 \(\theta\) 包含除截距外的可识别系数。按WAPE、MAE、RMSE及固定枚举顺序选模：

$$
MAE=\frac1n\sum_j|y_j-\widehat y_j|,\qquad
RMSE=\sqrt{\frac1n\sum_j(y_j-\widehat y_j)^2},
\tag{32}
$$

$$
WAPE=\frac{\sum_j|y_j-\widehat y_j|}{\sum_j|y_j|}.
\tag{33}
$$

WAPE分母为0时输出 `validation_unavailable`，保留MAE、RMSE和可计算的总体WAPE。

前序任务集合为

$$
\mathcal I^{<2376}=\{i:a_i<2376\}.
\tag{34}
$$

先按

$$
\operatorname{key}(i)=
(\mathbf1\{i\notin\mathcal I_{\mathrm{RT}}\},F_i,-h_i,TaskID_i)
\tag{35}
$$

排序，并在当前不违反式(5)–(11)的候选集合 \(\Phi_i\) 中按

$$
\arg\min_{(r,s)\in\Phi_i}^{lex}
[s-a_i,\ell_{o_ir},U_{irs}^{post},RegionName(r),s]
\tag{36}
$$

生成贪心初始解。

关键修订是：若任一步出现 \(\Phi_i=\varnothing\)，立即放弃该贪心前缀，在全部前序任务和完整候选域 \(\Omega_i\) 上求一次全局可行性MILP：

$$
\min 0
\tag{37}
$$

满足全部前序任务的式(5)–(11)。只有求解器给出已证明的 `infeasible` 才能报告前序调度不可行；若达到时间限制但未获得可行解或不可行证明，则输出 `feasibility_unresolved`，不得误报为不可行。若得到可行解，则以该解替代贪心方案继续计算。

冻结跨越2376时点的已执行占用：

$$
\mathcal I^{pre}=
\{i:a_i<2376,\ s_i^0+h_i>2376\},\qquad
\mathcal I^{end}=\{i:2376\le a_i\le2399\}.
\tag{38}
$$

$$
b_{rt}^{GPU}=\sum_{\substack{i\in\mathcal I^{pre}\\r_i^0=r}}
g_i\chi_{it}(s_i^0),\qquad
b_{rt}^{AI,cap}=\sum_{\substack{i\in\mathcal I^{pre}\\r_i^0=r}}
g_ip_{k_i}^{GPU}\chi_{it}(s_i^0).
\tag{39}
$$

末端容量为

$$
b_{rt}^{GPU}+
\sum_{i\in\mathcal I^{end},s}g_i\chi_{it}(s)x_{irs}
\le G_r^{\max},
\tag{40}
$$

$$
L_{rt}^{N}+b_{rt}^{AI,cap}
+\sum_{i\in\mathcal I^{end},s}
g_ip_{k_i}^{GPU}\chi_{it}(s)x_{irs}
\le P_r^{IT,\max},
\tag{41}
$$

并对式(41)左侧乘 \(\pi_r\) 后不超过 \(P_r^{F,\max}\)。末端目标为

$$
\min_{\mathrm{lex}}
\left[
\sum_{i\in\mathcal I^{end}}(s_i-a_i),
\sum_{i\in\mathcal I^{end}}\ell_i,
U^{\max},
\text{任务ID—区域—开工时刻}
\right].
\tag{42}
$$

### 求解方法

先完成统计和预测选模；再用贪心生成前序初始解，贪心失败时调用式(37)的完整可行性MILP。取得完整前序可行解后，冻结真实跨界占用并求末端MILP，最后对全部实际任务复核唯一执行、到达、实时开工、截止、时延、GPU、IT、设施功率和2406禁占用。

### 可观测性

需求标签可观测；全局最优调度标签不可观测。以求解器状态、完整轨迹及物理约束复算作为代理验证。

### 必须回答的输出

1. 区域—任务类型GPU、GPU-hour及描述统计表。
2. 三类预测候选的验证集比较和最终选模记录。
3. 测试集总体及分组MAE、RMSE、WAPE。
4. 前序贪心状态、必要时的全局可行性MILP状态。
5. 第2376–2399小时实际任务的区域、开工和完成时刻。
6. 2376时点前序占用及跨越2399小时的结清结果。
7. 最后24小时调度甘特图文件。
8. 区域逐时GPU利用率表和曲线。
9. 全部任务的完整可行性审计表。
10. `full_horizon_feasible`及不可行、未决状态的证据。

## 子问题 2：碳感知任务调度

### 模型思路

联合选择全部实际任务的执行区域和整数开工时刻。问题二不使用储能，成本、碳排和新能源结算均使用小时实际重叠量。

### 模型建立

无储能条件为

$$
R_{rt}^{ch}=G_{rt}^{ch}=C_{rt}=D_{rt}=0.
\tag{43}
$$

能源分配为

$$
R_{rt}^{use}+R_{rt}^{sell}+R_{rt}^{curt}=R_{rt}^{av},
\tag{44}
$$

$$
G_{rt}^{buy}+R_{rt}^{use}=L_{rt}^{F,avg},\qquad
G_{rt}^{sell}=R_{rt}^{sell}.
\tag{45}
$$

网络时延和新能源利用率为

$$
L_{\mathrm{net}}=
\frac{\sum_{i,r,s}g_ih_i\ell_{o_ir}x_{irs}}
{\sum_i g_ih_i},
\tag{46}
$$

$$
U_{\mathrm{RE}}^{q2}=
\frac{\sum_{r,t}(R_{rt}^{use}+R_{rt}^{sell})\Delta t}
{\sum_{r,t}R_{rt}^{av}\Delta t}.
\tag{47}
$$

分母不正时指标输出“不可计算”，并排除对应路径约束和排序。成本基准 \(b^0\) 按

$$
[C_{\mathrm{op}},E_{\mathrm{CO2}},L_{\mathrm{net}},
-U_{\mathrm{RE}}^{q2},\text{任务ID—区域—开工时刻}]
\tag{48}
$$

词典序唯一化。正式路径为

$$
\min C_{\mathrm{op}},
\tag{49}
$$

$$
E_{\mathrm{CO2}}\le\varepsilon_C(a),\quad
L_{\mathrm{net}}\le\varepsilon_L(a),\quad
U_{\mathrm{RE}}^{q2}\ge\varepsilon_U(a).
\tag{50}
$$

### 滚动窗口提交边界

设窗口起点为 \(\tau\)。仅冻结窗口起点前已经开工但尚未完成的任务：

$$
\mathcal I_{\tau}^{run}
=\{i:s_i<\tau<c_i\}.
\tag{51}
$$

对 \(i\in\mathcal I_{\tau}^{run}\)，固定其执行区域、原开工时刻和剩余占用，因为任务不可抢占且不可迁移。尚未开工任务集合为

$$
\mathcal I_{\tau}^{pending}
=\{i:a_i<\tau,\ s_i\ge\tau\}
\cup\{i:\tau\le a_i<\tau+H\}.
\tag{52}
$$

对所有 \(i\in\mathcal I_{\tau}^{pending}\)，不继承前一窗口中的暂定区域或未来开工时刻，而重新保留

$$
\Omega_i^\tau=
\{(r,s)\in\Omega_i:s\ge\tau\}
\tag{53}
$$

中的全部合法候选。只有实际开工决策进入不可撤销状态。因此滚动求解不会提前固定尚未开工任务的区域。

### 求解方法

求成本基准和三个必要锚点后生成五条168小时滚动路径。每个窗口仅提交已开工任务，待开工任务在下一窗口重新优化。仅保留完整拼接且通过全时域复算的候选，报告 `global_optimality_certificate=false`。

### 可观测性

全局最优标签不可观测；任务、功率、成本、碳排、时延和新能源利用量可直接复算。

### 必须回答的输出

1. 全部实际任务的执行区域、开工和完成时刻。
2. 区域逐时AI IT电量、总IT和设施负荷。
3. 逐时购电、新能源直用、外送和弃电。
4. 成本、碳排、平均及高分位时延、新能源利用率。
5. 相对问题一基础调度的绝对及相对变化。
6. 五条路径候选表、非支配关系和图。
7. 各任务类型迁移数、GPU-hour、等待和时延。
8. 窗口中已开工/未开工任务状态及衔接审计。
9. `full_horizon_feasible`与`global_optimality_certificate=false`。

## 子问题 3：固定负荷下的储能协同优化

### 模型思路

固定 `Baseline_AI_IT_Load_MW` 和 `NonAI_IT_Load_MW`，只优化新能源、储能和购售电。

### 模型建立

设施负荷为

$$
L_{rt}^{F,avg}=\pi_r(L_{rt}^{BAI}+L_{rt}^{N}).
\tag{54}
$$

能源分源为

$$
R_{rt}^{use}+R_{rt}^{ch}+R_{rt}^{sell}+R_{rt}^{curt}
=R_{rt}^{av},
\tag{55}
$$

$$
G_{rt}^{load}+R_{rt}^{use}+D_{rt}=L_{rt}^{F,avg},
\tag{56}
$$

$$
C_{rt}=R_{rt}^{ch}+G_{rt}^{ch},\quad
G_{rt}^{buy}=G_{rt}^{load}+G_{rt}^{ch},\quad
G_{rt}^{sell}=R_{rt}^{sell}.
\tag{57}
$$

SOC为

$$
S_{r,-1}=S_r^0,
\tag{58}
$$

$$
S_{rt}=S_{r,t-1}
+\eta_r^cC_{rt}\Delta t
-\frac{D_{rt}\Delta t}{\eta_r^d},
\tag{59}
$$

$$
S_r^{min}\le S_{rt}\le S_r^{max},\qquad
S_{r,2406}\ge S_r^0.
\tag{60}
$$

充放电互斥为

$$
0\le C_{rt}\le u_{rt}^cC_r^{\max},\qquad
0\le D_{rt}\le(1-u_{rt}^c)D_r^{\max}.
\tag{61}
$$

净购电及峰值口径修订为

$$
N_{rt}=G_{rt}^{buy}-G_{rt}^{sell},
\tag{62}
$$

$$
P_r^{peak}\ge0,\qquad
P_r^{peak}\ge N_{rt}\quad\forall t.
\tag{63}
$$

因此“区域峰值净购电功率”明确表示非负购电容量需求；若全时域均为净外送，则峰值购电为0，而不是负数。爬坡量为

$$
z_{rt}\ge N_{rt}-N_{r,t-1},\qquad
z_{rt}\ge-(N_{rt}-N_{r,t-1}),
\tag{64}
$$

$$
V_r=\sum_{t=1}^{2406}z_{rt}.
\tag{65}
$$

最终复算口径为

$$
\widehat P_r^{peak}=
\max\{0,\max_tN_{rt}\},\qquad
\widehat V_r=\sum_{t=1}^{2406}|N_{rt}-N_{r,t-1}|.
\tag{66}
$$

成本基准 \(b^3\) 及锚点生成路径：

$$
\min_{\mathrm{lex}}
\left[C_{\mathrm{op}},
\sum_rP_r^{peak}+\sum_{r,t}z_{rt}\right],
\tag{67}
$$

$$
E_{\mathrm{CO2}}\le\varepsilon_C(a),\quad
P_r^{peak}\le\varepsilon_{P,r}(a),\quad
V_r\le\varepsilon_{V,r}(a).
\tag{68}
$$

新能源利用率和等效完整循环量为

$$
U_{\mathrm{RE}}^{q3}=
\frac{\sum_{r,t}(R_{rt}^{use}+R_{rt}^{ch}+R_{rt}^{sell})\Delta t}
{\sum_{r,t}R_{rt}^{av}\Delta t},
\tag{69}
$$

$$
N_r^{EFC}=
\frac{\sum_t(C_{rt}+D_{rt})\Delta t}{2B_r}.
\tag{70}
$$

\(B_r\) 严格取 `StorageCapacity_MWh`；若 \(B_r\le0\)，EFC输出“不适用”。

### 求解方法

先求无储能参照、成本基准和必要锚点，再生成最多五条路径。所有峰值结果按式(66)复算。

### 可观测性

最优储能动作不可观测；能源守恒、SOC、终端状态、互斥、净购电及非负购电峰值可验证。

### 必须回答的输出

1. 各区域0–2406小时新能源、充放电、购售电和弃电策略。
2. SOC轨迹和终端SOC。
3. 储能前后成本、碳排、非负峰值购电和绝对爬坡量。
4. 指标绝对及相对变化。
5. 各区域EFC。
6. SOC、充放电和净购电曲线。
7. 能源、SOC、购售、充放互斥及终端审计。
8. 新能源利用率核验。
9. 锚点、路径、求解和非全局最优状态。

## 子问题 4：多区域算—储—电联合优化

### 模型思路

联合决定任务区域、开工时刻、能源流和储能动作，权衡成本、碳排、时延、服务质量、新能源利用率和非负峰值购电。

### 模型建立

设施负荷为

$$
L_{rt}^{F,avg}=
\pi_r\left[
L_{rt}^{N}+
\frac1{\Delta t}\sum_{i,s}
g_ip_{k_i}^{GPU}\omega_{it}(s)x_{irs}
\right].
\tag{71}
$$

能源、SOC、互斥和非负峰值使用式(14)–(17)、式(55)–(66)。新能源利用率为

$$
U_{\mathrm{RE}}^{q4}=
\frac{\sum_{r,t}
(R_{rt}^{use}+R_{rt}^{ch}+R_{rt}^{sell})\Delta t}
{\sum_{r,t}R_{rt}^{av}\Delta t}.
\tag{72}
$$

服务质量分量为

$$
Q_{\mathrm{RT}}=
\frac{\#\{i\in\mathcal I_{\mathrm{RT}}:s_i=a_i\}}
{\#\mathcal I_{\mathrm{RT}}},
\tag{73}
$$

$$
Q_{\mathrm{SLA}}=
\frac{\#\{i:\ell_i\le\ell_i^{\max}\}}{\#\mathcal I},
\qquad
Q_{\mathrm{deadline}}=
\frac{\#\{i:c_i\le F_i\}}{\#\mathcal I},
\tag{74}
$$

$$
Q_{\mathrm{wait}}=
1-\frac{\sum_{i\in\mathcal I_{\mathrm{wait}}}(s_i-a_i)}
{\sum_{i\in\mathcal I_{\mathrm{wait}}}W_i^{\max}},
\tag{75}
$$

其中

$$
\mathcal I_{\mathrm{wait}}=
\{i:i\notin\mathcal I_{\mathrm{RT}},
\Omega_i\ne\varnothing,W_i^{\max}\ge0\}.
\tag{76}
$$

只把分母为正的分量纳入 \(J_{\mathrm{def}}\)：

$$
Q_{\mathrm{service}}=
\frac1{|J_{\mathrm{def}}|}
\sum_{j\in J_{\mathrm{def}}}Q_j.
\tag{77}
$$

若 \(J_{\mathrm{def}}=\varnothing\)，输出“不可计算”并退出相关路径及排序。

统一基准 \(b^4\) 为

$$
[C_{\mathrm{op}},E_{\mathrm{CO2}},L_{\mathrm{net}},
1-Q_{\mathrm{service}},1-U_{\mathrm{RE}}^{q4},
\sum_rP_r^{peak},
\text{任务ID—区域—开工时刻}]
\tag{78}
$$

词典序最小方案，并定义

$$
E^0=E_{\mathrm{CO2}}(b^4).
\tag{79}
$$

正式路径为

$$
\min C_{\mathrm{op}},
\tag{80}
$$

$$
E_{\mathrm{CO2}}\le\varepsilon_C(a),\quad
L_{\mathrm{net}}\le\varepsilon_L(a),
\tag{81}
$$

$$
1-Q_{\mathrm{service}}\le\varepsilon_{1-Q}(a),\quad
1-U_{\mathrm{RE}}^{q4}\le\varepsilon_{1-U}(a),
\tag{82}
$$

$$
P_r^{peak}\le\varepsilon_{P,r}(a),\qquad
P_r^{peak}\ge0.
\tag{83}
$$

滚动窗口严格采用式(51)–(53)：只冻结已经开工任务，尚未开工任务保留全部剩余合法区域—开工候选。

有限候选损失为

$$
y_m=(C_{\mathrm{op}},E_{\mathrm{CO2}},L_{\mathrm{net}},
1-Q_{\mathrm{service}},1-U_{\mathrm{RE}}^{q4},
\widehat P_1^{peak},\ldots,\widehat P_6^{peak})_m.
\tag{84}
$$

只对可计算且极差为正的维度归一化：

$$
\bar y_{jm}=
\frac{y_{jm}-\min_ny_{jn}}
{\max_ny_{jn}-\min_ny_{jn}},
\tag{85}
$$

$$
m^*=\arg\min_m
\sqrt{\frac1{|J_{\mathrm{disc}}|}
\sum_{j\in J_{\mathrm{disc}}}\bar y_{jm}^2}.
\tag{86}
$$

若 \(J_{\mathrm{disc}}=\varnothing\)，按成本、碳排、时延和固定候选编号词典序选择。

### 情景模型

碳约束为

$$
E_{\mathrm{CO2}}\le(1-\rho_C)E^0,\qquad
\rho_C\in\{0,0.1,0.2,0.3\}.
\tag{87}
$$

购电峰谷价差为

$$
c_{rt}^{buy,sc}=
\bar c_r+\delta_P(c_{rt}^{buy}-\bar c_r),
\quad
\delta_P\in\{0.75,1,1.25\},
\tag{88}
$$

$$
\bar c_r=\frac1{2407}\sum_{t=0}^{2406}c_{rt}^{buy}.
\tag{89}
$$

售电机制为

$$
c_{rt}^{sell,sc}=\delta_Sc_{rt}^{sell},
\qquad \delta_S\in\{0,0.5,1\}.
\tag{90}
$$

新能源水平为

$$
R_{rt}^{av,level}=\max\{0,\delta_RR_{rt}^{av}\},
\qquad \delta_R\in\{0.8,1,1.2\}.
\tag{91}
$$

波动增强情景为

$$
R_{rt}^{av,vol}=
\max\{0,R_{rt}^{av}+\sigma_{sc}\xi_{rt}\},
\tag{92}
$$

随机种子为2026，\(\xi_{rt}\) 在各区域标准化为样本均值0、样本方差1；有正新能源样本时

$$
\sigma_{sc}=0.1\operatorname{mean}
\{R_{rt}^{av}:R_{rt}^{av}>0\},
\tag{93}
$$

否则 \(\sigma_{sc}=0\)。各情景均相对同一 \(b^4\) 重新求解。

### 求解方法

采用168小时滚动联合MILP，按式(51)–(53)提交任务状态。先求统一基准和必要锚点，再生成五条路径并重求情景。正式结论限定为实际完整完成的候选集 `best-found`。

### 可观测性

全局最优标签不可观测；任务、能源、SOC、成本、碳排、等待、新能源利用率和非负峰值购电均可复算。

### 必须回答的输出

1. 折中方案逐任务区域、开工、完成、等待和时延。
2. 各区域逐时AI IT电量、设施负荷、新能源、储能、购售电和SOC。
3. 成本、碳排、时延、服务质量、新能源利用率和非负峰值购电。
4. 五条路径候选表、非支配关系和折中方案。
5. 不同碳约束下的指标、迁移、循环和可行性变化。
6. 不同峰谷价差及售电机制下的策略变化。
7. 新能源水平和波动增强情景变化。
8. 各情景相对统一基准的绝对及相对变化。
9. 各任务类型迁移数、GPU-hour、等待和时延。
10. 各区域峰值、爬坡量和EFC。
11. 锚点、预算、窗口衔接、互斥和求解状态审计。
12. 候选图、负荷与SOC曲线、迁移流向图和情景图。
13. `full_horizon_feasible`与`global_optimality_certificate=false`。

## 共享300秒预算与动态硬时限

所有子问题共享一次运行预算：

$$
B_{\mathrm{total}}=300\ {\rm s},\qquad
T_{\mathrm{tail}}=15\ {\rm s},
\tag{94}
$$

$$
D_{\mathrm{search}}=t_{\mathrm{start}}+285,\qquad
D_{\mathrm{total}}=t_{\mathrm{start}}+300.
\tag{95}
$$

在每次可中断MILP调用前读取单调时钟 \(t_{\mathrm{now}}\)，计算

$$
T_{\mathrm{call}}=
\max\left\{0,
\min(D_{\mathrm{search}},D_{\mathrm{total}}-T_{\mathrm{tail}})
-t_{\mathrm{now}}
\right\}.
\tag{96}
$$

只有 \(T_{\mathrm{call}}>0\) 才能启动，并必须把 \(T_{\mathrm{call}}\) 作为求解器的硬 `time_limit`。求解器返回后再次检查单调时钟；超时、被中断或仅有未完成部分结果的调用不得进入正式候选。

执行优先级固定为：输入校验和预测固定工作、问题一必答调度及全局可行性回退、问题二基准与正式输出、问题三、问题四及情景、文件输出和终检。后序搜索不得占用 \(T_{\mathrm{tail}}\)。固定必答工作若真实超时，输出实际耗时、停止位置和未完成清单，不得缩减时域或任务伪装完成。

## 统一结果审计

任务审计为

$$
i\in\mathcal I_{\mathrm{RT}}\Rightarrow s_i=a_i,\quad
a_i\le s_i,\quad c_i\le F_i,\quad
\ell_i\le\ell_i^{\max},
\tag{97}
$$

$$
s_i\in\mathcal S,\qquad
\omega_{i,2406}(s_i)=0.
\tag{98}
$$

问题二能源残差为

$$
e_{rt}^{q2}=
G_{rt}^{buy}+R_{rt}^{av}
-L_{rt}^{F,avg}-G_{rt}^{sell}-R_{rt}^{curt}.
\tag{99}
$$

问题三、四能源和SOC残差为

$$
e_{rt}^{energy}=
G_{rt}^{buy}+R_{rt}^{av}+D_{rt}
-L_{rt}^{F,avg}-C_{rt}
-G_{rt}^{sell}-R_{rt}^{curt},
\tag{100}
$$

$$
e_{rt}^{SOC}=
S_{rt}-S_{r,t-1}
-\eta_r^cC_{rt}\Delta t
+\frac{D_{rt}\Delta t}{\eta_r^d}.
\tag{101}
$$

连续残差满足

$$
\widetilde e_j=\frac{|e_j|}{s_j}\le10^{-6},
\tag{102}
$$

其中尺度优先取附件硬上限；缺失或非正时，在求解前固定为

$$
s_j=\max\{1,\max|\text{对应输入量}|\}.
\tag{103}
$$

只有全部任务、瞬时容量、能源、SOC、购售和充放互斥、两项外送边界、2406禁占用、终端SOC及式(102)均通过时，才令 `full_horizon_feasible=true`。峰值审计还必须满足

$$
P_r^{peak}\ge0,\qquad
\left|P_r^{peak}-\max\{0,\max_tN_{rt}\}\right|
\le\tau_{\mathrm{num}}s_r.
\tag{104}
$$

## 局限性与停止规则

1. 任务、电价、碳强度和新能源按附件或明确情景处理。
2. 网络只使用单向时延，不建立带宽、迁移能耗、迁移费用或线路潮流。
3. PUE、功率映射、购售边界和储能参数严格读取附件。
4. 测试集不参与选模；含168阶滞后的模型只在 \(t\ge168\) 构造。
5. 贪心只是初始解方法；只有完整可行性MILP证明不可行时才输出 `infeasible`。
6. 完整可行性MILP超时且无证明时输出 `feasibility_unresolved`。
7. 滚动窗口只固定已开工任务；尚未开工任务保留全部剩余合法候选。
8. 指标分母不正时输出“不可计算”或“不适用”，不以任意小常数替代。
9. 五条路径是有限候选，不代表完整连续Pareto前沿。
10. 超时或未完整完成的锚点、窗口及候选不得进入正式比较。
11. 所有优化结论限定为完成候选集上的best-found。
12. 未执行的外部调研不得作为参数或阈值来源。

## Verifier 修复核对表

| Block issue | 修复公式/约束位置 | 如何保证可计算和有限输出 |
|---|---|---|
| 问题一贪心候选耗尽被错误视为完整调度不可行 | 式(34)–(42)，尤其是式(37) | 贪心仅生成初始解；候选耗尽后在全部前序任务及完整 \(\Omega_i\) 上求可行性MILP。只有求解器证明 `infeasible` 才停止；超时无证明输出有限状态 `feasibility_unresolved`。 |
| 共享300秒预算未转化为每次MILP的动态硬时限 | 式(94)–(96) | 每次基准、锚点、窗口、路径、情景及回退MILP均接收由共同绝对截止计算的硬 `time_limit`；\(T_{\mathrm{call}}\le0\) 不启动，超时部分解丢弃，并固定保留15秒输出与终检时间。 |
| 滚动时域可能提前固定尚未开工任务的区域 | 式(51)–(53) | 只冻结窗口起点前已开工且未完成任务的区域和剩余占用；尚未开工任务重新保留全部剩余合法区域—开工候选，避免错误缩小可行域。 |
| Huber截距、完整区域固定效应和完整任务类型固定效应不可识别 | 式(24)–(25)、式(30) | 固定 \(\alpha_{\mathrm{RegionA}}=0\) 与 \(\delta_{\mathrm{RealTimeInference}}=0\)，其余系数均解释为相对基准效应，使设计矩阵参数化可识别且重训结果可复现。 |
| 峰值变量可能在全时域净外送时为负 | 式(62)–(68)、式(83)、式(104) | 增加 \(P_r^{peak}\ge0\)，并统一按 \(\max\{0,\max_tN_{rt}\}\) 复算“峰值购电功率”；全时域净外送时输出0，不产生无工程意义的负峰值。 |