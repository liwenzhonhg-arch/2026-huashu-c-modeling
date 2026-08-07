# 数学模型

## 符号说明

| 符号 | 含义 | 类型及数据来源 | 取值范围/单位 |
|---|---|---|---|
| \(i,r,t,s,k\) | 任务、区域、小时、开工时刻、任务类型索引 | 索引 | \(r\in\mathcal R,\ t=0,\ldots,2406\) |
| \(\mathcal R,\mathcal K\) | 六区域和三任务类型集合 | 题面直接给定 | 无 |
| \(a_i,d_i,h_i\) | 到达小时、持续分钟、持续小时，\(h_i=d_i/60\) | 工作负载附件 | h、min、h |
| \(g_i,k_i,o_i\) | GPU需求、任务类型、来源区域 | 工作负载附件 | GPU、无、无 |
| \(f_i^{\max},F_i\) | 附件截止、有效截止 | 输入及派生 | h |
| \(W_i^{\max}\) | 有效最大允许等待时间 | 派生 | h |
| \(\ell_i^{\max},\ell_{or}\) | 最大允许时延、单向区域时延 | 工作负载及网络附件 | ms |
| \(\Delta t\) | 小时时段长度 | 题面直接给定 | \(1\) h |
| \(\omega_{it}(s)\) | 任务与小时的实际重叠时长 | 派生 | h |
| \(\chi_{it}(s)\) | 小时内是否存在瞬时占用 | 派生 | \(\{0,1\}\) |
| \(x_{irs}\) | 任务是否在区域 \(r\) 于 \(s\) 开工 | 决策变量 | \(\{0,1\}\) |
| \(q_{ir},s_i,c_i,\ell_i\) | 执行区域、开工、完成、实际时延 | 派生 | 无、h、h、ms |
| \(G_r^{\max}\) | 可调度GPU容量 | GPU附件 | 等效GPU |
| \(P_r^{IT,\max},P_r^{F,\max}\) | 瞬时IT和设施功率上限 | GPU附件 | MW |
| \(p_k^{GPU},\pi_r\) | 每GPU平均IT功率、PUE | 功率映射及GPU附件 | MW/GPU、无量纲 |
| \(L_{rt}^{N},L_{rt}^{BAI}\) | NonAI、问题三Baseline AI小时平均IT负荷 | 区域逐时附件 | MW |
| \(L_{rt}^{AI,cap}\) | AI任务在小时内可能同时出现的瞬时IT功率 | 派生 | MW |
| \(E_{rt}^{AI}\) | AI任务在小时 \(t\) 的实际IT电量 | 派生 | MWh |
| \(L_{rt}^{AI,avg}\) | AI任务小时平均IT功率 \(E_{rt}^{AI}/\Delta t\) | 派生 | MW |
| \(L_{rt}^{F,cap},L_{rt}^{F,avg}\) | 瞬时设施功率、小时平均设施负荷 | 派生 | MW |
| \(R^{av},R^{use},R^{ch},R^{sell},R^{curt}\) | 可用、直用、充电、外送、弃用新能源 | 输入或变量 | MW |
| \(G^{load},G^{ch},G^{buy},G^{sell}\) | 电网供负荷、充电、总购电、总外送 | 变量 | MW |
| \(C_{rt},D_{rt},S_{rt}\) | 储能充电、放电、时段末SOC | 变量 | MW、MW、MWh |
| \(B_r,S_r^0,S_r^{min},S_r^{max}\) | 储能容量、初始SOC和上下限 | 储能附件 | MWh |
| \(\eta_r^c,\eta_r^d,C_r^{\max},D_r^{\max}\) | 效率与充放电上限 | 储能附件 | 无量纲、MW |
| \(I_r^{\max}\) | `MaxGridImport_MW` | 区域附件 | MW |
| \(X_r^{grid},X_r^{storage}\) | `MaxGridExport_MW`、`SellLimit_MW` | 区域及储能附件 | MW |
| \(E_r^{\max}\) | 两项外送硬边界的共同上限 | 派生 | MW |
| \(y_{rt}^{grid},u_{rt}^{c}\) | 购售、充放互斥变量 | 二元变量 | \(\{0,1\}\) |
| \(c_{rt}^{buy},c_{rt}^{sell},\kappa_{rt}\) | 购价、售价、碳强度 | 区域逐时附件 | 元/MWh、tCO2/MWh |
| \(N_{rt},P_r^{peak},z_{rt},V_r\) | 净购电、峰值、爬坡辅助量、绝对爬坡量 | 派生或变量 | MW |
| \(D_{rkt}\) | 区域—类型—小时GPU到达需求 | 工作负载聚合 | GPU |
| \(\sigma_{rk},\rho_\delta,\lambda\) | 训练尺度、Huber损失、正则参数 | 封闭计算或固定网格 | GPU、无量纲 |
| \(C_{\mathrm{op}},E_{\mathrm{CO2}}\) | 运行成本、购电碳排放 | 指标 | 元、tCO2 |
| \(L_{\mathrm{net}},U_{\mathrm{RE}},Q_{\mathrm{service}}\) | 时延、新能源利用率、服务质量 | 指标 | ms、无量纲 |
| \(b^0,b^3,b^4\) | 问题二、三、四的固定成本最优硬约束基准 | 优化产生，非预填参数 | 方案 |
| \(m_j^{loose},m_j^{ideal}\) | 指标 \(j\) 的宽松和理想锚点值 | 基准及单目标锚点 | 与指标一致 |
| \(\varepsilon_j(a)\) | 第 \(a\) 条路径的阈值 | 封闭插值 | 与指标一致 |
| \(E^0\) | 问题四统一基准 \(b^4\) 的碳排放 | 派生 | tCO2 |
| \(H\) | 滚动窗口长度 | 固定 | \(168\) h |
| \(\tau_{num}\) | 归一化审计容差 | 固定 | \(10^{-6}\) |
| \(B_{\mathrm{total}},T_{\mathrm{tail}}\) | 共享总预算、终检预留 | 固定运行合同 | 300 s、15 s |

附件数值、预测误差、锚点和优化结果均由代码阶段从真实附件计算；本阶段不预填拟合或优化结果。

## 统一任务、容量与能源边界

任务到达、结清和终端时域为

$$
\mathcal T_A=\{0,\ldots,2399\},\quad
\mathcal T_C=\{2400,\ldots,2405\},\quad
t_{\mathrm{terminal}}=2406.
\tag{1}
$$

第2406小时不执行任务，只结算电力与SOC。定义

$$
h_i=\frac{d_i}{60},\quad
F_i=\min(f_i^{\max},2406),\quad
W_i^{\max}=F_i-a_i-h_i.
\tag{2}
$$

任务与小时的实际重叠及瞬时占用为

$$
\omega_{it}(s)=
\max\{0,\min(t+\Delta t,s+h_i)-\max(t,s)\},
\tag{3}
$$

$$
\chi_{it}(s)=\mathbf1\{\omega_{it}(s)>0\}.
\tag{4}
$$

候选集合、唯一执行和派生时刻为

$$
\Omega_i=\{(r,s):\ell_{o_ir}\le\ell_i^{\max},
\ s\ge a_i,\ s+h_i\le F_i\},
\tag{5}
$$

$$
\sum_{(r,s)\in\Omega_i}x_{irs}=1,\quad
q_{ir}=\sum_sx_{irs},\quad
s_i=\sum_{r,s}sx_{irs},
\tag{6}
$$

$$
c_i=s_i+h_i,\qquad
\ell_i=\sum_r\ell_{o_ir}q_{ir}.
\tag{7}
$$

实时任务额外满足 \(s_i=a_i\)。若任一 \(\Omega_i=\varnothing\)，输出无可行候选任务表并结构化停止。

瞬时GPU和功率容量必须使用 \(\chi\)：

$$
\sum_{i,s}g_i\chi_{it}(s)x_{irs}\le G_r^{\max},
\tag{8}
$$

$$
L_{rt}^{AI,cap}=
\sum_{i,s}g_ip_{k_i}^{GPU}\chi_{it}(s)x_{irs},
\tag{9}
$$

$$
L_{rt}^{IT,cap}=L_{rt}^{N}+L_{rt}^{AI,cap},\qquad
L_{rt}^{F,cap}=\pi_rL_{rt}^{IT,cap},
\tag{10}
$$

$$
L_{rt}^{IT,cap}\le P_r^{IT,\max},\qquad
L_{rt}^{F,cap}\le P_r^{F,\max}.
\tag{11}
$$

小时能源结算必须使用 \(\omega\)：

$$
E_{rt}^{AI}=
\sum_{i,s}g_ip_{k_i}^{GPU}\omega_{it}(s)x_{irs},
\qquad
L_{rt}^{AI,avg}=\frac{E_{rt}^{AI}}{\Delta t},
\tag{12}
$$

$$
L_{rt}^{F,avg}
=\pi_r\left(L_{rt}^{N}+L_{rt}^{AI,avg}\right).
\tag{13}
$$

因此，\(\chi\) 只进入瞬时GPU、IT和设施容量；\(\omega\) 进入GPU-hour、MWh、能源平衡、成本和碳排放。任务GPU-hour为 \(g_ih_i\)。

共同外送边界固定为

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

若某区域没有储能且附件未给 `SellLimit_MW`，仅当数据字典明确该限制不适用时取 \(X_r^{storage}=+\infty\)，从而仍执行 `MaxGridExport_MW`；字段缺失且无法判断适用性时结构化停止。

成本与碳排放为

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

## 联合 \(\varepsilon\) 路径的统一封闭规则

对每个子问题，先在该问题全部题面硬约束下求成本最优基准，并用预声明的指标顺序及任务ID—区域—开工时刻顺序进行词典序破同，使基准唯一。对需要控制的指标 \(m_j\)：

- 最小化指标使用成本基准值与单目标最优值构造端点；
- 最大化指标先改写为损失，例如新能源利用率使用 \(1-U_{\mathrm{RE}}\)，服务质量使用 \(1-Q_{\mathrm{service}}\)；
- 统一令

$$
m_j^{loose}=\max\{m_j^{base},m_j^{single}\},\qquad
m_j^{ideal}=\min\{m_j^{base},m_j^{single}\}.
\tag{18}
$$

五条路径 \(a\in\mathcal A_\varepsilon=\{0,0.25,0.5,0.75,1\}\) 的阈值唯一规定为

$$
\varepsilon_j(a)=
m_j^{loose}-a(m_j^{loose}-m_j^{ideal}),
\qquad
m_j\le\varepsilon_j(a).
\tag{19}
$$

对原始最大化指标 \(U\)，等价写为

$$
U\ge
U^{loose}+a(U^{ideal}-U^{loose}),
\tag{20}
$$

其中 \(U^{loose}=\min(U^{base},U^{single})\)，
\(U^{ideal}=\max(U^{base},U^{single})\)。

必要锚点必须完整求解成功；失败、超时或指标不可计算时，不得猜测阈值。若该指标属于题面必需比较项，则结构化停止；若仅属于折中排序的可选分量，则标记“不可计算”并从路径约束与排序中删除。路径不可行是合法结果，但不得用放宽阈值伪造可行候选。

## 子问题 1：需求预测与末端基础调度

### 模型思路

统计区域—任务类型GPU与GPU-hour需求，比较季节性朴素模型和标准化Huber回归。最后24小时调度只使用实际到达任务，并将已审计的前序跨界任务作为固定占用。

### 模型建立

$$
D_{rkt}^{GPU}=\sum_{i:o_i=r,k_i=k,a_i=t}g_i,\qquad
D_{rkt}^{GPUh}=\sum_{i:o_i=r,k_i=k,a_i=t}g_ih_i.
\tag{21}
$$

季节性候选为

$$
\widehat D_{rkt}^{(24)}=D_{rk,t-24},\qquad
\widehat D_{rkt}^{(168)}=D_{rk,t-168}.
\tag{22}
$$

Huber回归候选为

$$
\widehat D_{rkt}=\max\left\{0,\beta_0+
\sum_{\ell\in\{1,2,3,24,48,168\}}\beta_\ell D_{rk,t-\ell}
+\gamma^\top z_t+\alpha_r+\delta_k\right\}.
\tag{23}
$$

其中 \(z_t\) 为由小时索引确定的小时、星期周期特征。训练尺度为

$$
\sigma_{rk}=\max\left\{
\sqrt{\frac1{n_{rk}}\sum_{t\in\mathcal T_{train}}
(D_{rkt}-\bar D_{rk})^2},1\ {\rm GPU}\right\}.
\tag{24}
$$

定义 \(u_{rkt}=(D_{rkt}-\widehat D_{rkt})/\sigma_{rk}\)，则

$$
\rho_\delta(u)=
\begin{cases}
u^2/2,&|u|\le\delta,\\
\delta(|u|-\delta/2),&|u|>\delta,
\end{cases}
\tag{25}
$$

$$
\min\sum_{r,k,t\in\mathcal T_{train}}\rho_\delta(u_{rkt})
+\lambda\|\beta\|_2^2,
\tag{26}
$$

$$
\delta\in\{0.5,1,1.5,2\},\qquad
\lambda\in\Lambda=\{0,10^{-4},10^{-3},10^{-2},10^{-1},1\}.
\tag{27}
$$

训练、验证、测试区间分别为 \(0{:}2351\)、\(2352{:}2375\)、\(2376{:}2399\)。评价指标为

$$
MAE=\frac1n\sum_j|y_j-\hat y_j|,\qquad
RMSE=\sqrt{\frac1n\sum_j(y_j-\hat y_j)^2},
\tag{28}
$$

$$
WAPE=\frac{\sum_j|y_j-\hat y_j|}{\sum_j|y_j|}.
\tag{29}
$$

WAPE分母为0时，该分组输出“验证不可用”，保留MAE、RMSE和可计算的总体WAPE。

设审计通过的前序方案为 \((r_i^0,s_i^0)\)，定义

$$
\mathcal I^{pre}=\{i:a_i<2376,\ s_i^0+h_i>2376\},\quad
\mathcal I^{end}=\{i:2376\le a_i\le2399\}.
\tag{30}
$$

固定占用为

$$
b_{rt}^{GPU}=\sum_{i\in\mathcal I^{pre}:r_i^0=r}
g_i\chi_{it}(s_i^0),
\tag{31}
$$

$$
b_{rt}^{AI,cap}=\sum_{i\in\mathcal I^{pre}:r_i^0=r}
g_ip_{k_i}^{GPU}\chi_{it}(s_i^0).
\tag{32}
$$

末端容量为

$$
b_{rt}^{GPU}+
\sum_{i\in\mathcal I^{end},s}g_i\chi_{it}(s)x_{irs}
\le G_r^{\max},
\tag{33}
$$

$$
L_{rt}^{AI,end,cap}=b_{rt}^{AI,cap}+
\sum_{i\in\mathcal I^{end},s}g_ip_{k_i}^{GPU}
\chi_{it}(s)x_{irs},
\tag{34}
$$

$$
L_{rt}^{N}+L_{rt}^{AI,end,cap}\le P_r^{IT,\max},
\quad
\pi_r(L_{rt}^{N}+L_{rt}^{AI,end,cap})\le P_r^{F,\max}.
\tag{35}
$$

词典序目标为

$$
\min\left[
\sum_{i\in\mathcal I^{end}}(s_i-a_i),
\sum_{i,r,s}\ell_{o_ir}x_{irs},
U^{\max}\right],
\tag{36}
$$

$$
U^{\max}\ge
\frac{b_{rt}^{GPU}+
\sum_{i\in\mathcal I^{end},s}g_i\chi_{it}(s)x_{irs}}
{G_r^{\max}}.
\tag{37}
$$

若 \(G_r^{\max}=0\)，该区域不生成任务候选，利用率输出“不适用”。

### 求解方法

验证集依次按WAPE、MAE、RMSE和固定候选枚举顺序选模；结构确定后用0–2375小时重训。前序方案通过唯一执行、到达、实时即时开工、截止、时延、瞬时GPU、瞬时IT、设施功率和2406禁占用审计后，求解末端MILP。

### 可观测性

预测需求标签真实可观测；最优调度标签不可观测，只以硬约束、容量和完整轨迹复算验证。

### 必须回答的输出

1. 区域—任务类型统计表。
2. 验证集候选比较、Huber候选及最终选模规则。
3. 测试集总体及分组MAE、RMSE、WAPE。
4. 第2376–2399小时实际任务调度方案。
5. 前序跨界承诺及跨越2399小时任务结清结果。
6. 最后24小时调度甘特图文件。
7. 区域逐时GPU利用率表和曲线。
8. 前序承诺、任务、时延、瞬时GPU、IT、设施功率及2406禁占用审计表。

## 子问题 2：碳感知任务调度

### 模型思路

任务硬容量使用瞬时指示量 \(\chi\)，能源、成本和碳排放使用实际重叠时长 \(\omega\)。问题二不使用储能。

### 模型建立

任务满足式(2)–(13)。无储能条件为

$$
R_{rt}^{ch}=G_{rt}^{ch}=C_{rt}=D_{rt}=0.
\tag{38}
$$

新能源与负荷平衡为

$$
R_{rt}^{use}+R_{rt}^{sell}+R_{rt}^{curt}=R_{rt}^{av},
\tag{39}
$$

$$
G_{rt}^{buy}+R_{rt}^{use}=L_{rt}^{F,avg},\qquad
G_{rt}^{sell}=R_{rt}^{sell}.
\tag{40}
$$

式(40)中的 \(L_{rt}^{F,avg}\) 必须由式(12)–(13)计算，不能以 \(L_{rt}^{F,cap}\) 替代。

GPU-hour加权平均时延为

$$
L_{\mathrm{net}}=
\frac{\sum_{i,r,s}g_ih_i\ell_{o_ir}x_{irs}}
{\sum_i g_ih_i}.
\tag{41}
$$

新能源利用率为

$$
U_{\mathrm{RE}}^{q2}=
\frac{\sum_{r,t}(R_{rt}^{use}+R_{rt}^{sell})\Delta t}
{\sum_{r,t}R_{rt}^{av}\Delta t}.
\tag{42}
$$

式(41)或式(42)分母不正时，对应指标输出“不可计算”，并退出相关路径约束和排序。

定义 \(b^0\) 为全部问题二硬约束下，按

$$
[C_{\mathrm{op}},E_{\mathrm{CO2}},L_{\mathrm{net}},
-U_{\mathrm{RE}}^{q2},\text{任务ID—区域—开工序}]
\tag{43}
$$

词典序唯一化的成本最优方案。分别求碳最优、时延最优和新能源利用率最优锚点，按式(18)–(20)得到

$$
\varepsilon_C(a),\qquad
\varepsilon_L(a),\qquad
\varepsilon_U(a).
\tag{44}
$$

五条正式模型为

$$
\min C_{\mathrm{op}},
\tag{45}
$$

$$
E_{\mathrm{CO2}}\le\varepsilon_C(a),\quad
L_{\mathrm{net}}\le\varepsilon_L(a),\quad
U_{\mathrm{RE}}^{q2}\ge\varepsilon_U(a).
\tag{46}
$$

滚动窗口传递累计碳、时延分子与分母、新能源利用量与可用量；窗口结束后必须用完整轨迹重新计算式(16)–(17)、式(41)–(42)。

### 求解方法

固定 \(H=168\) 小时。先完成基准与三个必要锚点，再按式(19)–(20)生成五条唯一阈值路径。只保留完整求解、拼接可行且通过全时域复算的候选，固定报告 `global_optimality_certificate=false`。

### 可观测性

真实全局最优标签不可观测；以任务硬约束、瞬时容量、基于 \(\omega\) 的小时能源、购售边界和完整轨迹复算验证。

### 必须回答的输出

1. 全部实际任务的区域、开工和完成时刻。
2. 区域逐时AI IT电量、AI小时平均IT、总IT和设施负荷。
3. 逐时购电、新能源直用、外送和弃电策略。
4. 成本、碳排、平均及高分位时延、新能源利用率。
5. 相对基础调度的绝对及相对变化。
6. 五条联合路径有限候选表和图。
7. 各任务类型迁移数、GPU-hour、等待和时延。
8. 累计预算、购售边界与互斥、窗口状态和间隙审计。
9. `full_horizon_feasible`与`global_optimality_certificate=false`。

## 子问题 3：固定负荷下的储能协同优化

### 模型思路

固定附件中的Baseline AI和NonAI小时平均IT负荷，仅优化新能源、储能和购售电。

### 模型建立

$$
L_{rt}^{F,avg}=\pi_r(L_{rt}^{BAI}+L_{rt}^{N}).
\tag{47}
$$

给定负荷若超过附件IT或设施硬上限，输出具体区域、小时和超限量并结构化停止。

能源分源为

$$
R_{rt}^{use}+R_{rt}^{ch}+R_{rt}^{sell}+R_{rt}^{curt}
=R_{rt}^{av},
\tag{48}
$$

$$
G_{rt}^{load}+R_{rt}^{use}+D_{rt}=L_{rt}^{F,avg},
\tag{49}
$$

$$
C_{rt}=R_{rt}^{ch}+G_{rt}^{ch},\quad
G_{rt}^{buy}=G_{rt}^{load}+G_{rt}^{ch},\quad
G_{rt}^{sell}=R_{rt}^{sell}.
\tag{50}
$$

购售边界使用式(14)–(15)。SOC为

$$
S_{r,-1}=S_r^0,
\tag{51}
$$

$$
S_{rt}=S_{r,t-1}+\eta_r^cC_{rt}\Delta t
-\frac{D_{rt}\Delta t}{\eta_r^d},
\tag{52}
$$

$$
S_r^{min}\le S_{rt}\le S_r^{max},\qquad
S_{r,2406}\ge S_r^0.
\tag{53}
$$

充放电互斥为

$$
0\le C_{rt}\le u_{rt}^cC_r^{\max},\quad
0\le D_{rt}\le(1-u_{rt}^c)D_r^{\max},\quad
u_{rt}^c\in\{0,1\}.
\tag{54}
$$

净购电、峰值和爬坡量为

$$
N_{rt}=G_{rt}^{buy}-G_{rt}^{sell},\qquad
P_r^{peak}\ge N_{rt},
\tag{55}
$$

$$
z_{rt}\ge N_{rt}-N_{r,t-1},\quad
z_{rt}\ge-(N_{rt}-N_{r,t-1}),\quad
V_r=\sum_{t=1}^{2406}z_{rt}.
\tag{56}
$$

最终必须从 \(N\) 复算

$$
\widehat P_r^{peak}=\max_tN_{rt},\qquad
\widehat V_r=\sum_{t=1}^{2406}|N_{rt}-N_{r,t-1}|.
\tag{57}
$$

定义 \(b^3\) 为全部问题三硬约束下按成本、碳、峰值和爬坡词典序唯一化的成本最优方案。分别求碳、每个区域峰值和每个区域爬坡量的单目标锚点，按式(18)–(19)生成

$$
\varepsilon_C(a),\quad
\varepsilon_{P,r}(a),\quad
\varepsilon_{V,r}(a).
\tag{58}
$$

正式目标与约束为

$$
\min_{\mathrm{lex}}\left[
C_{\mathrm{op}},\sum_rP_r^{peak}+\sum_{r,t}z_{rt}\right],
\tag{59}
$$

$$
E_{\mathrm{CO2}}\le\varepsilon_C(a),\quad
P_r^{peak}\le\varepsilon_{P,r}(a),\quad
V_r\le\varepsilon_{V,r}(a).
\tag{60}
$$

新能源利用率和等效循环为

$$
U_{\mathrm{RE}}^{q3}=
\frac{\sum(R^{use}+R^{ch}+R^{sell})\Delta t}
{\sum R^{av}\Delta t},
\tag{61}
$$

$$
N_r^{EFC}=
\frac{\sum_t(C_{rt}+D_{rt})\Delta t}{2B_r}.
\tag{62}
$$

式(61)分母为0时输出“不可计算”；式(62)仅在 \(B_r>0\) 时计算，否则输出“不适用”。

### 求解方法

先求无储能参照、成本基准和式(58)所需锚点，再生成最多五条路径。所有锚点和候选共用300秒预算；必要锚点未完成时结构化停止，不使用部分结果。

### 可观测性

最优储能动作不可观测；附件SOC只作基准对照，以能源守恒、SOC递推、终端SOC、互斥和净购电轨迹验证。

### 必须回答的输出

1. 各区域0–2406小时新能源、充放电、购售电和弃电策略。
2. 绝对SOC轨迹和终端SOC。
3. 储能前后成本、碳排、峰值净购电和绝对爬坡量。
4. 指标绝对及相对变化。
5. 各区域等效完整循环量。
6. SOC、充放电和净购电曲线。
7. 能源、SOC、购售和充放互斥及终端状态审计。
8. 含新能源充电的新能源利用率核验。
9. 锚点状态、路径状态、窗口间隙及非全局最优声明。

## 子问题 4：多区域算—储—电联合优化

### 模型思路

联合决定任务执行区域、开工时刻、小时能源流和储能动作；瞬时容量与实际小时能源严格分离。

### 模型建立

任务满足式(2)–(13)，能源和储能满足式(14)–(17)、式(48)–(56)，其中问题四设施小时平均负荷必须按式(12)–(13)由实际任务重叠量计算。

新能源利用率为

$$
U_{\mathrm{RE}}^{q4}=
\frac{\sum(R^{use}+R^{ch}+R^{sell})\Delta t}
{\sum R^{av}\Delta t}.
\tag{63}
$$

有效等待集合为

$$
\mathcal I_{wait}=
\{i:i\notin RT,\ \Omega_i\ne\varnothing,\ W_i^{\max}\ge0\}.
\tag{64}
$$

服务质量分量为

$$
Q_{\mathrm{RT}}=
\frac{\#\{i\in RT:s_i=a_i\}}{\#RT},\quad
Q_{\mathrm{SLA}}=
\frac{\#\{i:\ell_i\le\ell_i^{\max}\}}{\#\mathcal I},
\tag{65}
$$

$$
Q_{\mathrm{deadline}}=
\frac{\#\{i:c_i\le F_i\}}{\#\mathcal I},
\tag{66}
$$

$$
Q_{\mathrm{wait}}=
1-\frac{\sum_{i\in\mathcal I_{wait}}(s_i-a_i)}
{\sum_{i\in\mathcal I_{wait}}W_i^{\max}}.
\tag{67}
$$

每个分量仅在其分母为正时计算。令 \(J_{\mathrm{def}}\) 为可计算分量集合：

$$
Q_{\mathrm{service}}=
\frac1{|J_{\mathrm{def}}|}
\sum_{j\in J_{\mathrm{def}}}Q_j.
\tag{68}
$$

若 \(J_{\mathrm{def}}=\varnothing\)，服务质量输出“不可计算”并退出路径约束与候选排序。等待路径约束等价为

$$
\sum_{i\in\mathcal I_{wait}}(s_i-a_i)
\le
(1-\varepsilon_{\mathrm{wait}})
\sum_{i\in\mathcal I_{wait}}W_i^{\max}.
\tag{69}
$$

定义统一基准 \(b^4\) 为全部题面硬约束下按

$$
[C_{\mathrm{op}},E_{\mathrm{CO2}},L_{\mathrm{net}},
1-Q_{\mathrm{service}},1-U_{\mathrm{RE}}^{q4},
\sum_rP_r^{peak},\text{任务ID—区域—开工序}]
\tag{70}
$$

词典序唯一化的成本最优方案，并固定

$$
E^0=E_{\mathrm{CO2}}(b^4).
\tag{71}
$$

分别最小化 \(E_{\mathrm{CO2}}\)、\(L_{\mathrm{net}}\)、
\(1-Q_{\mathrm{service}}\)、\(1-U_{\mathrm{RE}}^{q4}\) 和每个 \(P_r^{peak}\)，按式(18)–(20)生成五条路径阈值。正式模型为

$$
\min C_{\mathrm{op}},
\tag{72}
$$

$$
E_{\mathrm{CO2}}\le\varepsilon_C(a),\quad
L_{\mathrm{net}}\le\varepsilon_L(a),\quad
1-Q_{\mathrm{service}}\le\varepsilon_{1-Q}(a),
\tag{73}
$$

$$
1-U_{\mathrm{RE}}^{q4}\le\varepsilon_{1-U}(a),\qquad
P_r^{peak}\le\varepsilon_{P,r}(a).
\tag{74}
$$

有限候选损失为

$$
y_m=(C_{\mathrm{op}},E_{\mathrm{CO2}},L_{\mathrm{net}},
1-Q_{\mathrm{service}},1-U_{\mathrm{RE}}^{q4},
\widehat P_1^{peak},\ldots,\widehat P_6^{peak})_m.
\tag{75}
$$

只保留可计算且候选极差为正的维度 \(J_{\mathrm{disc}}\)，并定义

$$
\bar y_{jm}=
\frac{y_{jm}-\min_ny_{jn}}
{\max_ny_{jn}-\min_ny_{jn}},
\tag{76}
$$

$$
m^*=\arg\min_m
\sqrt{\frac1{|J_{\mathrm{disc}}|}
\sum_{j\in J_{\mathrm{disc}}}\bar y_{jm}^2}.
\tag{77}
$$

若 \(J_{\mathrm{disc}}=\varnothing\)，按成本、碳排、时延和固定候选编号词典序选择。

情景定义为

$$
E_{\mathrm{CO2}}\le(1-\rho_C)E^0,\qquad
\rho_C\in\{0,0.1,0.2,0.3\},
\tag{78}
$$

$$
c_{rt}^{buy,sc}=\bar c_r+
\delta_P(c_{rt}^{buy}-\bar c_r),\quad
\delta_P\in\{0.75,1,1.25\},
\tag{79}
$$

$$
c_{rt}^{sell,sc}=\delta_Sc_{rt}^{sell},\quad
\delta_S\in\{0,0.5,1\},
\tag{80}
$$

$$
R_{rt}^{av,level}=\max(0,\delta_RR_{rt}^{av}),\quad
\delta_R\in\{0.8,1,1.2\},
\tag{81}
$$

$$
R_{rt}^{av,vol}=
\max(0,R_{rt}^{av}+\sigma_{sc}\xi_{rt}).
\tag{82}
$$

随机种子固定为2026；\(\xi_{rt}\) 在各区域内标准化为样本均值0、样本方差1；若正新能源样本存在，

$$
\sigma_{sc}=0.1\operatorname{mean}
\{R_{rt}^{av}:R_{rt}^{av}>0\},
\tag{83}
$$

否则 \(\sigma_{sc}=0\)。所有情景相对同一 \(b^4\) 比较，不重新定义 \(E^0\)。

### 求解方法

固定168小时滚动联合MILP，传递未完成任务占用、SOC、累计碳、时延分子与分母、新能源量和有效等待量。先求统一基准及必要锚点，再按封闭公式生成五条路径；完整复算后选折中方案并逐一重求情景。结果仅是实际完成候选集上的best-found。

所有子问题共享

$$
B_{\mathrm{total}}=300\ {\rm s},\quad
T_{\mathrm{tail}}=15\ {\rm s},\quad
D_{\mathrm{search}}=t_{\mathrm{start}}+285\ {\rm s}.
\tag{84}
$$

使用单调时钟记录实际耗时。每个固定任务、锚点、窗口和候选启动前检查同一截止；已启动任务可越过搜索截止，但必须在总截止前完成，否则中断并丢弃，不使用部分结果。

### 可观测性

联合全局最优标签不可观测；任务、瞬时容量、实际小时能源、SOC、成本、碳排、购售边界和等待量均可由附件与决策复算。

### 必须回答的输出

1. 折中方案逐任务区域、开工、完成、等待和时延。
2. 各区域逐时AI IT电量、小时平均设施负荷、新能源、储能、购售电和SOC。
3. 成本、碳排、时延、服务质量、新能源利用率和峰值净购电。
4. 五条联合路径有限候选表、非支配关系和折中方案。
5. 不同碳约束下的指标、迁移、循环和可行性变化。
6. 不同购电峰谷价差及售电机制下的策略变化。
7. 新能源上升、下降和波动增强情景变化。
8. 各情景相对统一基准 \(b^4\) 的绝对及相对变化。
9. 各任务类型迁移数、GPU-hour、等待和时延。
10. 各区域峰值、爬坡量和等效循环量。
11. 锚点状态、累计预算、窗口衔接、购售边界与互斥、求解状态和窗口间隙审计。
12. 候选图、负荷与SOC曲线、迁移流向图和情景比较图。
13. `full_horizon_feasible`与`global_optimality_certificate=false`。

## 统一结果审计

任务审计核验

$$
i\in RT\Rightarrow s_i=a_i,\quad
a_i\le s_i,\quad c_i\le F_i,\quad
\ell_i\le\ell_i^{\max},
\tag{85}
$$

以及式(8)–(13)中的瞬时容量与小时能源口径。

问题二能源残差为

$$
e_{rt}^{q2}=
G_{rt}^{buy}+R_{rt}^{av}
-L_{rt}^{F,avg}-G_{rt}^{sell}-R_{rt}^{curt}.
\tag{86}
$$

问题三、四能源和SOC残差为

$$
e_{rt}^{energy}=
G_{rt}^{buy}+R_{rt}^{av}+D_{rt}
-L_{rt}^{F,avg}-C_{rt}-G_{rt}^{sell}-R_{rt}^{curt},
\tag{87}
$$

$$
e_{rt}^{SOC}=S_{rt}-S_{r,t-1}
-\eta_r^cC_{rt}\Delta t+
\frac{D_{rt}\Delta t}{\eta_r^d}.
\tag{88}
$$

所有连续残差归一化为

$$
\widetilde e_j=\frac{|e_j|}{s_j}\le
\tau_{num}=10^{-6}.
\tag{89}
$$

GPU、MW和MWh残差的 \(s_j\) 优先取附件对应硬上限；硬上限缺失或非正时，在求解前固定为

$$
s_j=\max\{1,\max|\text{对应输入量}|\}.
\tag{90}
$$

比例和计数残差取 \(s_j=1\)。不得查看结果后调整尺度。离散约束必须满足求解器整数可行性条件。

只有全部适用残差通过、所有离散约束成立、两项外送硬边界均满足、第2406小时执行任务数为0且未完成任务数为0时，才令 `full_horizon_feasible=true`。

## 局限性与停止规则

1. 任务、电价、碳强度和新能源按确定值处理。
2. 网络仅使用单向时延，不增加带宽、迁移能耗、传输费用或线路潮流。
3. PUE、GPU功率、容量、购售边界和储能参数严格读取附件。
4. 测试集不参与预测调参。
5. 外部搜索未执行，不作为参数来源。
6. 空候选、输入硬边界矛盾、必要锚点失败、累计预算不可达、滚动拼接失败或无完整可行解时结构化停止。
7. 任一业务指标分母不正时输出“不可计算”或“不适用”，不使用任意小常数替代。
8. 五条路径仅构成有限候选集，不代表完整连续Pareto前沿。
9. 窗口间隙只适用于对应窗口；全时域复算只能证明所得轨迹可行。
10. 超过共同截止或未完整完成的锚点、窗口及候选不得进入正式比较。

## Verifier 修复核对表

| Block issue | 修复公式/约束位置 | 可计算性与有限输出保证 |
|---|---|---|
| 分数小时任务以 \(\chi\) 按整小时结算能源 | 式(3)–(4)、式(9)–(13)、式(39)–(40)、式(86)–(87) | \(\chi\) 只用于瞬时容量；小时AI电量固定使用 \(g_ip_k^{GPU}\omega_{it}(s)\)，能源平衡、成本和碳排均使用由其得到的小时平均设施负荷。 |
| 瞬时功率与MWh口径未分离，式(12)未进入问题二、四 | 式(9)–(13)、问题二式(40)、问题四式(72)–(74)及统一审计 | 明确定义 \(L^{AI,cap}\)、\(E^{AI}\)、\(L^{AI,avg}\)、\(L^{F,cap}\)、\(L^{F,avg}\)，容量与结算不再共用同一负荷量。 |
| 五条联合 \(\varepsilon\) 路径缺少锚点、上下界和封闭公式 | 式(18)–(20)、问题二式(43)–(46)、问题三式(58)–(60)、问题四式(70)–(74) | 基准和单目标锚点均唯一规定，端点通过min/max有序化，五个 \(a\) 值直接生成唯一阈值；必要锚点失败时结构化停止。 |
| 碳情景基准 \(E^0\) 未唯一规定 | 式(70)–(71)、式(78) | \(E^0\) 固定为统一硬约束成本最优基准 \(b^4\) 的碳排放；所有碳、价格和新能源情景均相对同一基准。 |
| Huber正则参数 \(\lambda\) 网格未声明 | 式(26)–(27)及 `params.json` | 固定网格为 \(\{0,10^{-4},10^{-3},10^{-2},10^{-1},1\}\)，按验证集指标和固定顺序选择，可直接复现。 |
| `MaxGridExport_MW` 与 `SellLimit_MW` 未共同执行 | 式(14)–(15)、式(50) | 统一定义 \(E_r^{\max}=\min(X_r^{grid},X_r^{storage})\)，等价于同时满足两项外送硬边界；字段适用性不明时停止。 |
| 定向修订遗漏四个子问题章节 | “子问题1”至“子问题4”完整章节 | 四个子问题均重新列出模型思路、模型建立、求解方法、可观测性和必须回答的输出，没有引用旧版本省略内容。 |