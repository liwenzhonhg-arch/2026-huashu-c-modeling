# 数学模型

## 符号说明

| 符号 | 含义 | 类型及数据来源 | 取值范围/单位 |
|---|---|---|---|
| \(i,r,t,s,k\) | 任务、区域、小时、开工时刻、任务类型索引 | 索引 | \(r\in\mathcal R,\ t=0,\ldots,2406\) |
| \(\mathcal R,\mathcal K\) | 六区域和三任务类型集合 | 题面直接给定 | 无 |
| \(a_i,d_i,h_i\) | 到达小时、持续分钟、持续小时 \(h_i=d_i/60\) | `workload_trace.xlsx` | h、min、h |
| \(g_i,k_i,o_i\) | GPU需求、任务类型、来源区域 | `workload_trace.xlsx` | 等效GPU、无、无 |
| \(f_i^{\max}\) | 附件最晚完成时点 | `LatestFinishHour` | h |
| \(F_i\) | 有效最晚完成时点 \(\min(f_i^{\max},2406)\) | 派生参数 | h |
| \(W_i^{\max}\) | 有效最大允许等待时间 \(F_i-a_i-h_i\) | 派生参数 | h |
| \(\ell_i^{\max},\ell_{or}\) | 任务时延上限、区域间单向时延 | 工作负载及网络附件 | ms |
| \(\Delta t\) | 时段长度 | 题面直接给定 | \(1\) h |
| \(\omega_{it}(s)\) | 任务与小时的实际重叠时长 | 派生参数 | h |
| \(\chi_{it}(s)\) | 瞬时占用指示量 \(\mathbf1\{\omega_{it}(s)>0\}\) | 派生参数 | \(\{0,1\}\) |
| \(x_{irs}\) | 任务是否在区域 \(r\) 于 \(s\) 开工 | 二元变量 | \(\{0,1\}\) |
| \(q_{ir},s_i,c_i,\ell_i\) | 执行区域、开工、完成和实际时延 | 由 \(x\) 唯一派生 | 无、h、h、ms |
| \(G_r^{\max}\) | 可调度GPU容量 | `Available_GPU` | 等效GPU |
| \(P_r^{IT,\max},P_r^{F,\max}\) | IT和设施功率上限 | GPU附件 | MW |
| \(p_k^{GPU},\pi_r\) | 每GPU平均IT功率、PUE | 功率映射及GPU附件 | MW/GPU、无量纲 |
| \(L_{rt}^{N},L_{rt}^{BAI}\) | NonAI负荷、问题三Baseline AI负荷 | 区域逐时附件 | MW |
| \(L_{rt}^{AI},L_{rt}^{IT},L_{rt}^{F}\) | AI IT、总IT和设施负荷 | 派生量 | MW |
| \(R^{av},R^{use},R^{ch},R^{sell},R^{curt}\) | 可用、直用、充电、外送、弃用新能源 | 输入或变量 | MW |
| \(G^{load},G^{ch},G^{buy},G^{sell}\) | 电网供负荷、充电、总购电、总售电 | 非负变量 | MW |
| \(C_{rt},D_{rt},S_{rt}\) | 储能充电、放电、时段末SOC | 变量 | MW、MW、MWh |
| \(B_r,S_r^0,S_r^{min},S_r^{max}\) | 容量、初始SOC及上下限 | 储能附件 | MWh |
| \(\eta_r^c,\eta_r^d,C_r^{\max},D_r^{\max}\) | 效率及充放电上限 | 储能附件 | 无量纲、MW |
| \(I_r^{\max},E_r^{\max}\) | 区域购电与外送上限 | 区域/储能附件 | MW |
| \(y_{rt}^{grid},u_{rt}^c\) | 购售、充放互斥状态 | 二元变量 | \(\{0,1\}\) |
| \(c_{rt}^{buy},c_{rt}^{sell},\kappa_{rt}\) | 购价、售价、碳强度 | 区域逐时附件 | 元/MWh、tCO2/MWh |
| \(N_{rt},P_r^{peak},z_{rt},V_r\) | 净购电、峰值、爬坡辅助量及总爬坡 | 派生或辅助变量 | MW |
| \(D_{rkt}\) | 区域—类型—小时GPU到达需求 | 工作负载聚合 | 等效GPU |
| \(\sigma_{rk}\) | Huber标准化尺度 | 训练集封闭计算 | 等效GPU |
| \(\rho_\delta\) | Huber损失，\(\delta\in\{0.5,1,1.5,2\}\) | 预声明 | 无量纲 |
| \(C_{\mathrm{op}},E_{\mathrm{CO2}}\) | 成本和购电碳排 | 指标 | 元、tCO2 |
| \(L_{\mathrm{net}},U_{\mathrm{RE}},Q_{\mathrm{service}}\) | 时延、新能源利用率、服务质量 | 指标 | ms、\([0,1]\)、\([0,1]\) |
| \(H\) | 滚动窗口长度 | 固定参数 | \(168\) h |
| \(\tau_{num}\) | 归一化审计容差 | 固定参数 | \(10^{-6}\) |
| \(B_{\mathrm{total}},T_{\mathrm{tail}},D_{\mathrm{search}}\) | 总预算、收尾预留、搜索截止 | 运行合同 | 300 s、15 s、起点后285 s |

附件数值、预测误差和优化结果由代码阶段从真实附件计算；未知参数在本阶段均不预填。

## 统一任务、容量与能源边界

任务到达、结清和终端时域为

$$
\mathcal T_A=\{0,\ldots,2399\},\qquad
\mathcal T_C=\{2400,\ldots,2405\}.
\tag{1}
$$

第2406小时只结算电力和SOC。任务允许在时点2406完成，但不得占用第2406小时。

定义

$$
h_i=\frac{d_i}{60},\qquad
F_i=\min(f_i^{\max},2406),\qquad
W_i^{\max}=F_i-a_i-h_i.
\tag{2}
$$

任务在小时 \(t\) 内的实际重叠时长和瞬时占用指示量为

$$
\omega_{it}(s)=
\max\{0,\min(t+\Delta t,s+h_i)-\max(t,s)\},
\tag{3}
$$

$$
\chi_{it}(s)=\mathbf1\{\omega_{it}(s)>0\}.
\tag{4}
$$

\(\chi\) 用于GPU和功率硬容量，防止小时内短任务因平均化而造成瞬时超限；\(\omega\) 仅用于GPU-hour和MWh核算。

候选集合为

$$
\Omega_i=\{(r,s):\ell_{o_ir}\le\ell_i^{\max},\
s\ge a_i,\ s+h_i\le F_i\},
\tag{5}
$$

实时任务额外满足 \(s=a_i\)。若 \(\Omega_i=\varnothing\)，输出无可行候选任务表并结构化停止。

任务绑定为

$$
\sum_{(r,s)\in\Omega_i}x_{irs}=1,\qquad
q_{ir}=\sum_{s:(r,s)\in\Omega_i}x_{irs},
\tag{6}
$$

$$
s_i=\sum_{(r,s)\in\Omega_i}s\,x_{irs},\qquad
c_i=s_i+h_i,\qquad
\ell_i=\sum_r\ell_{o_ir}q_{ir}.
\tag{7}
$$

瞬时容量和功率约束为

$$
\sum_{i,s}g_i\chi_{it}(s)x_{irs}\le G_r^{\max},
\tag{8}
$$

$$
L_{rt}^{AI}=\sum_{i,s}g_ip_{k_i}^{GPU}\chi_{it}(s)x_{irs},
\tag{9}
$$

$$
L_{rt}^{IT}=L_{rt}^{N}+L_{rt}^{AI},\qquad
L_{rt}^{F}=\pi_rL_{rt}^{IT},
\tag{10}
$$

$$
L_{rt}^{IT}\le P_r^{IT,\max},\qquad
L_{rt}^{F}\le P_r^{F,\max}.
\tag{11}
$$

任务GPU-hour和分小时AI IT电量分别为

$$
W_i^{GPU}=g_ih_i,\qquad
E_{irt}^{AI}=\sum_sg_ip_{k_i}^{GPU}\omega_{it}(s)x_{irs}.
\tag{12}
$$

运行成本、碳排以及区域购售互斥为

$$
C_{\mathrm{op}}=\sum_{r,t}
(c_{rt}^{buy}G_{rt}^{buy}-c_{rt}^{sell}G_{rt}^{sell})\Delta t,
\tag{13}
$$

$$
E_{\mathrm{CO2}}=\sum_{r,t}\kappa_{rt}G_{rt}^{buy}\Delta t,
\tag{14}
$$

$$
0\le G_{rt}^{buy}\le I_r^{\max}y_{rt}^{grid},\quad
0\le G_{rt}^{sell}\le E_r^{\max}(1-y_{rt}^{grid}),\quad
y_{rt}^{grid}\in\{0,1\}.
\tag{15}
$$

## 子问题 1：需求预测与末端基础调度

### 模型思路

分别统计区域、任务类型和小时需求；比较季节性朴素模型与标准化Huber回归。最后24小时调度只使用实际到达任务，并将通过完整审计的前序跨界任务作为固定瞬时占用。

### 模型建立

需求统计为

$$
D_{rkt}^{GPU}=\sum_{i:o_i=r,k_i=k,a_i=t}g_i,\qquad
D_{rkt}^{GPUh}=\sum_{i:o_i=r,k_i=k,a_i=t}g_ih_i.
\tag{16}
$$

季节性候选为

$$
\widehat D_{rkt}^{(24)}=D_{rk,t-24},\qquad
\widehat D_{rkt}^{(168)}=D_{rk,t-168}.
\tag{17}
$$

回归候选为

$$
\widehat D_{rkt}=\max\left\{0,\beta_0+
\sum_{\ell\in\{1,2,3,24,48,168\}}\beta_\ell D_{rk,t-\ell}
+\gamma^\top z_t+\alpha_r+\delta_k\right\}.
\tag{18}
$$

训练尺度固定为

$$
\sigma_{rk}=
\max\left\{
\sqrt{\frac1{n_{rk}}\sum_{t\in\mathcal T_{train}}
(D_{rkt}-\bar D_{rk})^2},\,1\ {\rm GPU}
\right\},
\tag{19}
$$

标准化残差 \(u_{rkt}=(D_{rkt}-\widehat D_{rkt})/\sigma_{rk}\)，Huber损失固定为

$$
\rho_\delta(u)=
\begin{cases}
\frac12u^2,&|u|\le\delta,\\
\delta(|u|-\frac12\delta),&|u|>\delta,
\end{cases}
\quad
\delta\in\{0.5,1,1.5,2\}.
\tag{20}
$$

优化目标为

$$
\min_{\beta,\gamma,\alpha,\delta_k}
\sum_{r,k,t\in\mathcal T_{train}}\rho_\delta(u_{rkt})
+\lambda\|\beta\|_2^2.
\tag{21}
$$

训练、验证、测试区间分别为 \(0{:}2351\)、\(2352{:}2375\)、\(2376{:}2399\)。评价采用

$$
MAE=\frac1n\sum_j|y_j-\hat y_j|,\quad
RMSE=\sqrt{\frac1n\sum_j(y_j-\hat y_j)^2},
\tag{22}
$$

$$
WAPE=\frac{\sum_j|y_j-\hat y_j|}{\sum_j|y_j|}.
\tag{23}
$$

WAPE分母为0时输出“验证不可用”，并保留MAE、RMSE和可计算的总体WAPE。

设经审计的前序方案为 \((r_i^0,s_i^0)\)，定义

$$
\mathcal I^{pre}=\{i:a_i<2376,\ s_i^0+h_i>2376\},
\quad
\mathcal I^{end}=\{i:2376\le a_i\le2399\}.
\tag{24}
$$

固定瞬时占用为

$$
b_{rt}^{GPU}=\sum_{i\in\mathcal I^{pre}:r_i^0=r}
g_i\chi_{it}(s_i^0),
\tag{25}
$$

$$
b_{rt}^{AI}=\sum_{i\in\mathcal I^{pre}:r_i^0=r}
g_ip_{k_i}^{GPU}\chi_{it}(s_i^0).
\tag{26}
$$

末端硬约束为

$$
b_{rt}^{GPU}+
\sum_{i\in\mathcal I^{end},s}g_i\chi_{it}(s)x_{irs}
\le G_r^{\max},
\tag{27}
$$

$$
L_{rt}^{AI,end}=b_{rt}^{AI}+
\sum_{i\in\mathcal I^{end},s}
g_ip_{k_i}^{GPU}\chi_{it}(s)x_{irs},
\tag{28}
$$

$$
L_{rt}^{IT,end}=L_{rt}^{N}+L_{rt}^{AI,end}\le P_r^{IT,\max},
\quad
\pi_rL_{rt}^{IT,end}\le P_r^{F,\max}.
\tag{29}
$$

词典序目标为

$$
\min\left[
\sum_{i\in\mathcal I^{end}}(s_i-a_i),\
\sum_{i,r,s}\ell_{o_ir}x_{irs},\
U^{\max}
\right],
\tag{30}
$$

其中

$$
U^{\max}\ge
\frac{b_{rt}^{GPU}+
\sum_{i\in\mathcal I^{end},s}g_i\chi_{it}(s)x_{irs}}
{G_r^{\max}}.
\tag{31}
$$

若 \(G_r^{\max}=0\)，该区域不生成候选，利用率输出“不适用”。

### 求解方法

验证集按WAPE、再按MAE选择结构与 \((\delta,\lambda)\)；结构确定后用0–2375重训。前序方案必须通过唯一执行、到达、即时开工、时延、截止、瞬时GPU、瞬时IT功率、设施功率和2406禁占用审计，之后求末端MILP。

### 可观测性

需求标签可观测；最优调度标签不可观测，以硬约束和归一化残差验证。

### 必须回答的输出

1. 区域—任务类型统计表。
2. 验证集候选比较、Huber候选及最终选模规则。
3. 测试集总体及分组MAE、RMSE、WAPE。
4. 第2376–2399小时实际任务调度方案。
5. 前序跨界承诺及跨越2399小时任务结清结果。
6. 最后24小时甘特图文件。
7. 区域逐时GPU利用率表和曲线。
8. 前序承诺、任务、时延、瞬时GPU、IT、设施功率及2406禁占用审计表。

## 子问题 2：碳感知任务调度

### 模型思路

联合优化执行区域、开工时刻及无储能能源分配，任务容量使用瞬时占用，能耗统计使用实际重叠小时。

### 模型建立

任务满足式(5)–(11)。问题二无储能：

$$
R_{rt}^{ch}=G_{rt}^{ch}=C_{rt}=D_{rt}=0.
\tag{32}
$$

能源分配为

$$
R_{rt}^{use}+R_{rt}^{sell}+R_{rt}^{curt}=R_{rt}^{av},
\tag{33}
$$

$$
G_{rt}^{buy}+R_{rt}^{use}=L_{rt}^{F},\qquad
G_{rt}^{sell}=R_{rt}^{sell},
\tag{34}
$$

并满足式(15)。

GPU-hour加权平均时延为

$$
L_{\mathrm{net}}=
\frac{\sum_{i,r,s}g_ih_i\ell_{o_ir}x_{irs}}
{\sum_i g_ih_i}.
\tag{35}
$$

分母不正时输出“不可计算”，退出时延约束和排序。新能源利用率为

$$
U_{\mathrm{RE}}^{q2}=
\frac{\sum_{r,t}(R_{rt}^{use}+R_{rt}^{sell})\Delta t}
{\sum_{r,t}R_{rt}^{av}\Delta t}.
\tag{36}
$$

分母为0时输出“不可计算”并退出相关约束和排序。

ε约束模型为

$$
\min C_{\mathrm{op}},
\tag{37}
$$

$$
E_{\mathrm{CO2}}\le\varepsilon_C,\quad
L_{\mathrm{net}}\le\varepsilon_L,\quad
U_{\mathrm{RE}}^{q2}\ge\varepsilon_U.
\tag{38}
$$

滚动窗口传递累计碳 \(A_C\)、时延分子 \(A_L\)、GPU-hour \(A_W\)、新能源利用量 \(A_U\) 和可用量 \(A_R\)。每窗满足

$$
A_C^{w-1}+\Delta A_C^w\le\varepsilon_C,
\tag{39}
$$

$$
A_L^{w-1}+\Delta A_L^w
\le\varepsilon_L(A_W^{w-1}+\Delta A_W^w+W_{rem}),
\tag{40}
$$

$$
A_U^{w-1}+\Delta A_U^w+R_{rem}^{av}
\ge\varepsilon_UA_R^{total},
\tag{41}
$$

其中 \(W_{rem}=\sum_{i\in\mathcal I_{rem}}g_ih_i\)。

### 求解方法

固定 \(H=168\) 小时滚动求解，只计算

$$
a\in\{0,0.25,0.5,0.75,1\}
\tag{42}
$$

五条联合ε路径。拼接后全时域复算；该方法只给出有限候选best-found，固定报告 `global_optimality_certificate=false`。

### 可观测性

真实最优标签不可观测；以任务约束、能源守恒、购售边界和完整轨迹复算验证。

### 必须回答的输出

1. 全部实际任务的区域、开工和完成时刻。
2. 区域逐时AI IT、总IT和设施负荷。
3. 逐时购电、新能源直用、外送和弃电策略。
4. 成本、碳排、平均及高分位时延、新能源利用率。
5. 相对基础调度的绝对及相对变化。
6. 五条联合路径有限候选表和图。
7. 各任务类型迁移数、GPU-hour、等待和时延。
8. 累计预算、购售边界与互斥、窗口状态和间隙审计。
9. `full_horizon_feasible`与`global_optimality_certificate=false`。

## 子问题 3：固定负荷下的储能协同优化

### 模型思路

固定Baseline AI与NonAI负荷，仅优化新能源、储能及购售电。

### 模型建立

$$
L_{rt}^{F}=\pi_r(L_{rt}^{BAI}+L_{rt}^{N}).
\tag{43}
$$

能源分源为

$$
R_{rt}^{use}+R_{rt}^{ch}+R_{rt}^{sell}+R_{rt}^{curt}
=R_{rt}^{av},
\tag{44}
$$

$$
G_{rt}^{load}+R_{rt}^{use}+D_{rt}=L_{rt}^{F},
\tag{45}
$$

$$
C_{rt}=R_{rt}^{ch}+G_{rt}^{ch},\quad
G_{rt}^{buy}=G_{rt}^{load}+G_{rt}^{ch},\quad
G_{rt}^{sell}=R_{rt}^{sell}.
\tag{46}
$$

式(15)逐区域逐时生效。SOC为

$$
S_{r,-1}=S_r^0,
\tag{47}
$$

$$
S_{rt}=S_{r,t-1}+\eta_r^cC_{rt}\Delta t
-\frac{D_{rt}\Delta t}{\eta_r^d},
\tag{48}
$$

$$
S_r^{min}\le S_{rt}\le S_r^{max},\qquad
S_{r,2406}\ge S_r^0.
\tag{49}
$$

充放电互斥为

$$
0\le C_{rt}\le u_{rt}^cC_r^{\max},\quad
0\le D_{rt}\le(1-u_{rt}^c)D_r^{\max},\quad
u_{rt}^c\in\{0,1\}.
\tag{50}
$$

净购电、峰值和爬坡为

$$
N_{rt}=G_{rt}^{buy}-G_{rt}^{sell},\qquad
P_r^{peak}\ge N_{rt},
\tag{51}
$$

$$
z_{rt}\ge\pm(N_{rt}-N_{r,t-1}),\qquad
V_r=\sum_{t=1}^{2406}z_{rt}.
\tag{52}
$$

正式目标为

$$
\min\left[C_{\mathrm{op}},
\sum_rP_r^{peak}+\sum_{r,t}z_{rt}\right],
\tag{53}
$$

并满足

$$
E_{\mathrm{CO2}}\le\varepsilon_C,\quad
P_r^{peak}\le\varepsilon_{P,r},\quad
V_r\le\varepsilon_{V,r}.
\tag{54}
$$

正式报告从 \(N\) 复算

$$
\widehat P_r^{peak}=\max_tN_{rt},\qquad
\widehat V_r=\sum_{t=1}^{2406}|N_{rt}-N_{r,t-1}|.
\tag{55}
$$

新能源利用率和等效循环为

$$
U_{\mathrm{RE}}^{q3}=
\frac{\sum(R^{use}+R^{ch}+R^{sell})\Delta t}
{\sum R^{av}\Delta t},
\tag{56}
$$

$$
N_r^{EFC}=\frac{\sum_t(C_{rt}+D_{rt})\Delta t}{2B_r}.
\tag{57}
$$

式(56)分母为0时不可计算；式(57)仅在 \(B_r>0\) 时计算，否则输出“不适用”。

### 求解方法

先求无储能及成本、碳、峰值、爬坡参照，再生成最多五条联合ε路径；完整轨迹复算可行性，固定报告 `global_optimality_certificate=false`。

### 可观测性

最优动作不可观测；附件SOC只作基准对照。以能源、SOC、终端状态及互斥约束验证。

### 必须回答的输出

1. 各区域0–2406小时新能源、充放电、购售电和弃电策略。
2. 绝对SOC轨迹和终端SOC。
3. 储能前后成本、碳排、峰值净购电和绝对爬坡量。
4. 指标绝对及相对变化。
5. 各区域等效完整循环量。
6. SOC、充放电和净购电曲线。
7. 能源、SOC、购售和充放互斥及终端状态审计。
8. 含新能源充电的新能源利用率核验。
9. 窗口状态、窗口间隙及非全局最优声明。

## 子问题 4：多区域算—储—电联合优化

### 模型思路

联合决定任务、能源和储能。硬容量统一使用 \(\chi\)，等待服务质量统一使用系统终点截断后的 \(W_i^{\max}\)。

### 模型建立

任务满足式(5)–(11)，能源和储能满足式(44)–(52)。

新能源利用率为

$$
U_{\mathrm{RE}}^{q4}=
\frac{\sum(R^{use}+R^{ch}+R^{sell})\Delta t}
{\sum R^{av}\Delta t}.
\tag{58}
$$

定义有效等待任务集合

$$
\mathcal I_{wait}=
\{i:i\notin RT,\ \Omega_i\ne\varnothing,\ W_i^{\max}\ge0\}.
\tag{59}
$$

服务质量分量为

$$
Q_{\mathrm{RT}}=
\frac{\#\{i\in RT:s_i=a_i\}}{\#RT},\quad
Q_{\mathrm{SLA}}=
\frac{\#\{i:\ell_i\le\ell_i^{\max}\}}{\#\mathcal I},
\tag{60}
$$

$$
Q_{\mathrm{deadline}}=
\frac{\#\{i:c_i\le F_i\}}{\#\mathcal I},
\tag{61}
$$

$$
Q_{\mathrm{wait}}=
1-\frac{\sum_{i\in\mathcal I_{wait}}(s_i-a_i)}
{\sum_{i\in\mathcal I_{wait}}W_i^{\max}}.
\tag{62}
$$

式(62)仅在总分母为正时计算；否则输出“不可计算”并移出服务质量。仅保留分母为正的分量集合 \(J_{\mathrm{def}}\)，令

$$
Q_{\mathrm{service}}=
\frac1{|J_{\mathrm{def}}|}
\sum_{j\in J_{\mathrm{def}}}Q_j.
\tag{63}
$$

若 \(J_{\mathrm{def}}=\varnothing\)，服务质量不可计算并退出相关约束和排序。

联合ε模型为

$$
\min C_{\mathrm{op}},
\tag{64}
$$

$$
E_{\mathrm{CO2}}\le\varepsilon_C,\quad
L_{\mathrm{net}}\le\varepsilon_L,\quad
Q_{\mathrm{service}}\ge\varepsilon_Q,
\tag{65}
$$

$$
U_{\mathrm{RE}}^{q4}\ge\varepsilon_U,\qquad
P_r^{peak}\le\varepsilon_{P,r}.
\tag{66}
$$

滚动等待预算和终端审计统一为

$$
\sum_{i\in\mathcal I_{wait}}(s_i-a_i)
\le(1-\varepsilon_{\mathrm{wait}})
\sum_{i\in\mathcal I_{wait}}W_i^{\max}.
\tag{67}
$$

窗口只对已经冻结执行决策的任务累计实际等待，对未冻结任务传递由式(2)计算的剩余允许等待量；不得使用未截断的 \(f_i^{\max}\)。

有限候选统一损失为

$$
y_m=(C_{\mathrm{op}},E_{\mathrm{CO2}},L_{\mathrm{net}},
1-Q_{\mathrm{service}},1-U_{\mathrm{RE}}^{q4},
\widehat P_1^{peak},\ldots,\widehat P_6^{peak})_m.
\tag{68}
$$

只保留可计算且在已完成候选间极差为正的维度 \(J_{\mathrm{disc}}\)，按

$$
\bar y_{jm}=
\frac{y_{jm}-\min_n y_{jn}}
{\max_n y_{jn}-\min_n y_{jn}},
\tag{69}
$$

$$
m^*=\arg\min_m
\sqrt{\frac1{|J_{\mathrm{disc}}|}
\sum_{j\in J_{\mathrm{disc}}}\bar y_{jm}^2}.
\tag{70}
$$

若 \(J_{\mathrm{disc}}=\varnothing\)，按成本、碳、时延词典序选择。

情景为

$$
E_{\mathrm{CO2}}\le(1-\rho_C)E^0,\quad
\rho_C\in\{0,0.1,0.2,0.3\},
\tag{71}
$$

$$
c_{rt}^{buy,sc}=\bar c_r+
\delta_P(c_{rt}^{buy}-\bar c_r),\quad
\delta_P\in\{0.75,1,1.25\},
\tag{72}
$$

$$
c_{rt}^{sell,sc}=\delta_Sc_{rt}^{sell},\quad
\delta_S\in\{0,0.5,1\},
\tag{73}
$$

$$
R_{rt}^{av,level}=\max(0,\delta_RR_{rt}^{av}),\quad
\delta_R\in\{0.8,1,1.2\},
\tag{74}
$$

$$
R_{rt}^{av,vol}=\max(0,R_{rt}^{av}+\sigma_{sc}\xi_{rt}),
\tag{75}
$$

其中随机种子为2026，\(\xi_{rt}\) 在各区域内标准化为样本均值0、样本方差1，\(\sigma_{sc}=0.1\operatorname{mean}\{R_{rt}^{av}:R_{rt}^{av}>0\}\)；无正样本时 \(\sigma_{sc}=0\)。

### 求解方法

固定168小时滚动联合MILP，传递任务占用、SOC、碳、时延、新能源和服务质量状态。仅计算五条联合ε路径；完整轨迹复算后按式(68)–(70)选折中方案，再分别重求式(71)–(75)的七类情景组。结果限定为实际完成候选上的best-found，不声称连续Pareto前沿或全时域全局最优。

所有子问题共享

$$
B_{\mathrm{total}}=300\ {\rm s},\quad
T_{\mathrm{tail}}=15\ {\rm s},\quad
D_{\mathrm{search}}=t_{\mathrm{start}}+285\ {\rm s}.
\tag{76}
$$

每个固定任务、窗口和候选启动前均用单调时钟检查共同截止；未完整完成的候选丢弃。

### 可观测性

联合最优标签不可观测；任务、瞬时容量、能源流、SOC、成本、碳排和等待容量均可从附件与决策复算。

### 必须回答的输出

1. 折中方案逐任务区域、开工、完成、等待和时延。
2. 各区域逐时AI IT、设施负荷、新能源、储能、购售电和SOC。
3. 成本、碳排、时延、服务质量、新能源利用率和峰值净购电。
4. 五条联合路径有限候选表、非支配关系和折中方案。
5. 不同碳约束下的指标、迁移、循环和可行性变化。
6. 不同购电峰谷价差及售电机制下的策略变化。
7. 新能源上升、下降和波动增强情景变化。
8. 各情景相对统一基准的绝对及相对变化。
9. 各任务类型迁移数、GPU-hour、等待和时延。
10. 各区域峰值、爬坡量和等效循环量。
11. 累计预算、窗口衔接、购售边界与互斥、求解状态和窗口间隙审计。
12. 候选图、负荷与SOC曲线、迁移流向图和情景比较图。
13. `full_horizon_feasible`与`global_optimality_certificate=false`。

## 统一结果审计

任务审计使用式(5)–(11)，并核验

$$
i\in RT\Rightarrow s_i=a_i,\quad
a_i\le s_i,\quad c_i\le F_i,\quad
\ell_i\le\ell_i^{\max}.
\tag{77}
$$

问题二能源残差为

$$
e_{rt}^{q2}=G_{rt}^{buy}+R_{rt}^{av}
-L_{rt}^{F}-G_{rt}^{sell}-R_{rt}^{curt}.
\tag{78}
$$

问题三、四能源和SOC残差为

$$
e_{rt}^{energy}=G_{rt}^{buy}+R_{rt}^{av}+D_{rt}
-L_{rt}^{F}-C_{rt}-G_{rt}^{sell}-R_{rt}^{curt},
\tag{79}
$$

$$
e_{rt}^{SOC}=S_{rt}-S_{r,t-1}
-\eta_r^cC_{rt}\Delta t+\frac{D_{rt}\Delta t}{\eta_r^d}.
\tag{80}
$$

所有连续残差先归一化：

$$
\widetilde e_j=\frac{|e_j|}{s_j},
\qquad
\widetilde e_j\le\tau_{num}=10^{-6}.
\tag{81}
$$

GPU、MW、MWh残差的 \(s_j\) 优先取对应附件硬上限；硬上限缺失或非正时，封闭取

$$
s_j=\max\{1,\max|\text{对应输入量}|\}.
\tag{82}
$$

比例和计数残差取 \(s_j=1\)。尺度在求解前由输入固定，禁止查看结果后调整阈值。离散约束必须精确满足求解器整数可行性条件，不能仅用连续残差替代。

等待质量最终审计重新计算式(2)、式(59)、式(62)和式(67)。若有效等待总量为0，则 \(Q_{\mathrm{wait}}\) 输出结构化“不可计算”，不产生NaN、Inf，也不参与服务质量约束或候选排序。

只有全部适用归一化残差不超过 \(10^{-6}\)、所有离散约束成立、2406执行任务数为0且未完成任务数为0时，才令 `full_horizon_feasible=true`。

## 局限性与停止规则

1. 任务、电价、碳强度和新能源按确定值处理。
2. 网络只采用题面单向时延，不增加带宽、迁移能耗或线路潮流。
3. PUE、GPU功率和容量严格读取附件。
4. 测试集不参与预测调参。
5. 外部搜索未执行，未作为参数来源。
6. 空候选、前序审计失败、累计预算不可达、滚动拼接失败或无完整可行解时结构化停止。
7. 任一指标分母不正时输出“不可计算”或“不适用”，并退出相应约束与排序，不使用任意小常数替代业务分母。
8. 五条联合ε路径只构成有限候选集，不代表完整连续Pareto前沿。
9. 窗口求解间隙只适用于对应窗口；全时域复算只能证明所得轨迹可行。
10. 超过共同截止或未完整完成的候选不得进入正式比较。

## Verifier 修复核对表

| Block issue | 修复公式/约束位置 | 可计算性与有限输出保证 |
|---|---|---|
| 等待质量未按2406截断有效截止 | 式(2)、式(59)、式(62)、式(67)及统一审计 | 固定 \(F_i=\min(f_i^{\max},2406)\)、\(W_i^{\max}=F_i-a_i-h_i\)；只纳入 \(W_i^{\max}\ge0\) 且候选非空任务。总分母为0时输出“不可计算”并移出约束和排序。 |
| 预测损失 \(\rho\) 未定义 | 式(19)–(21) | 在代码前固定标准化残差及分段Huber损失；\(\delta\) 只从预声明有限集合 \(\{0.5,1,1.5,2\}\) 选择，不允许事后改变损失形式。 |
| 数值容差 \(\tau_{num}\) 未固定 | 式(81)–(82) | 固定 \(\tau_{num}=10^{-6}\)；GPU、MW、MWh残差先除以求解前确定的有限正尺度，禁止根据结果调阈值。 |
| 人工复核发现平均占用会掩盖小时内瞬时超限 | 式(3)–(12)、式(25)–(29) | 定义 \(\chi_{it}(s)=\mathbf1\{\omega_{it}(s)>0\}\)；GPU、AI IT和设施功率硬容量全部使用 \(g_i\chi\) 与 \(g_ip_k^{GPU}\chi\)，\(\omega\) 仅用于GPU-hour和MWh。 |