# 数学模型

## 符号说明

| 符号 | 含义 | 类型 | 取值范围、单位与来源 |
|------|------|------|----------------------|
| \(\mathcal R,\mathcal K,\mathcal I\) | 区域、任务类型、实际任务集合 | 参数 | 六区域、三类型、任务附件 |
| \(\mathcal T_A,\mathcal T_C,T_E\) | 到达域、收尾域、结算时点 | 题面给定 | \(0{:}2399\)、\(2400{:}2405\)、\(2406\)，h |
| \(\Delta t\) | 电力时段长度 | 固定参数 | \(1\rm\,h\) |
| \(a_i,d_i,f_i,g_i,k_i,o_i\) | 到达、时长、截止、GPU、类型、来源 | 可观测参数 | 任务附件；\(d_i=\mathrm{EstimatedDuration\_min}_i/60\) |
| \(\ell_{or},\ell_i^{\max}\) | 单向网络时延、任务上限 | 可观测参数 | ms，网络与任务附件 |
| \(x_{irs}\) | 任务在区域 \(r\)、时刻 \(s\) 开工 | 二元变量 | \(\{0,1\}\) |
| \(q_{it}(s)\) | 任务与时段 \(t\) 的重叠时长 | 派生量 | h |
| \(G_r,p_k^{GPU}\) | GPU容量、单位GPU功率 | 参数 | GPU；MW/GPU |
| \(P^{AI},P^{nonAI},P^{IT},P^{fac}\) | AI、非AI、总IT及设施平均功率 | 变量/参数 | MW |
| \(A^{RE},U^{RE},P^{RE,ch},P^{grid,ch}\) | 可用、直用新能源及两类充电 | 参数/变量 | MW |
| \(P^{buy},P^{sell},P^{curt},P^{ch},P^{dis}\) | 购、售、弃、充、放功率 | 变量 | MW |
| \(y^{trade},z^{ch}\) | 购售、充放状态 | 二元变量 | \(\{0,1\}\) |
| \(E_{rt},E_r^0\) | 时段末SOC、初始SOC | 状态/参数 | MWh |
| \(N_{rt},P_r^{peak},V_r\) | 净购电、非负峰值购电、绝对爬坡量 | 派生量 | MW、MW、MW |
| \(C_{\rm op},E_{\rm CO2},L_{\rm net},U_{\rm RE}\) | 成本、碳排、时延、新能源利用率 | 指标 | 元、tCO2、ms、无量纲 |
| \(E_{\rm CO2}^{ref}\) | 无碳上限成本最小联合基准方案的复算排放 | 代理基准 | tCO2；由真实附件求得 |
| \(B_{\rm total},D_{\rm search},T_{\rm tail}\) | 共享总预算、搜索截止、尾部预留 | 固定参数 | \(300,285,15\rm\,s\) |

本题没有几何量，几何证据要求不适用。

## 统一任务与负荷内核

$$
q_{it}(s)=\max\{0,\min(t+\Delta t,s+d_i)-\max(t,s)\}. \tag{1}
$$

$$
\Omega_i=\{(r,s):s\ge a_i,\ s+d_i\le\min(f_i,2406),\
\ell_{o_ir}\le\ell_i^{\max}\}. \tag{2}
$$

实时任务固定 \(s=a_i\)。若 \(\Omega_i=\varnothing\)，输出 `task_infeasible`。任务恰执行一次：

$$
\sum_{(r,s)\in\Omega_i}x_{irs}=1,\qquad x_{irs}\in\{0,1\}. \tag{3}
$$

修正量纲后的小时平均功率、GPU-hour容量为

$$
P_{rt}^{AI}=\frac1{\Delta t}\sum_{i,s}g_ip_{k_i}^{GPU}q_{it}(s)x_{irs},\quad
P_{rt}^{IT}=P_{rt}^{nonAI}+P_{rt}^{AI},\quad
P_{rt}^{fac}=PUE_rP_{rt}^{IT}, \tag{4}
$$

$$
\sum_{i,s}g_iq_{it}(s)x_{irs}\le G_r\Delta t,\quad
P_{rt}^{IT}\le P_r^{IT,\max},\quad
P_{rt}^{fac}\le P_r^{fac,\max}. \tag{5}
$$

## 子问题 1：GPU需求预测与末端基础调度

### 模型思路

保持原数据划分、季节性基线、岭回归和实际任务末端调度不变。

### 模型建立

$$
D_{rkt}=\sum_{i:o_i=r,k_i=k,a_i=t}g_i,\qquad
H_{rkt}=\sum_{i:o_i=r,k_i=k,a_i=t}g_id_i. \tag{6}
$$

$$
\widehat D_{rkt}^{(24)}=D_{rk,t-24},\qquad
\widehat D_{rkt}^{(168)}=D_{rk,t-168}. \tag{7}
$$

$$
(\widehat\beta_0,\widehat{\boldsymbol\beta})
=\arg\min\sum(D_{rkt}-\beta_0-\boldsymbol\beta^\top\mathbf z_{rkt})^2
+\lambda\|\boldsymbol\beta\|_2^2,\quad
\widehat D_{rkt}=\max(0,\widehat\beta_0+\widehat{\boldsymbol\beta}^\top\mathbf z_{rkt}). \tag{8}
$$

$$
WAPE=\frac{\sum|D-\widehat D|}{\sum|D|}. \tag{9}
$$

仅当分母为正时报告WAPE，否则输出 `validation_unavailable`，正式指标只保留MAE和RMSE；删除未定义的“有限预测率”。

修正后的GPU利用率为

$$
Util_{rt}^{GPU}=
\frac{\sum_{i,s}g_iq_{it}(s)x_{irs}}{G_r\Delta t}\times100\%. \tag{10}
$$

仅当 \(G_r\Delta t>0\) 时计算，否则输出 `metric_unavailable`。

### 求解方法

训练、验证、重训和测试区间保持不变；调度按词典序最小化未完成数、最大延迟、总等待和总时延。

### 必须回答的输出

保持原9项输出及文件名不变。

## 子问题 2：无储能碳感知调度

### 模型建立

$$
U_{rt}^{RE}+P_{rt}^{sell}+P_{rt}^{curt}=A_{rt}^{RE},\qquad
P_{rt}^{buy}+U_{rt}^{RE}=P_{rt}^{fac}. \tag{11}
$$

储能量固定为零。为无条件排除套利，增加正式购售互斥：

$$
0\le P_{rt}^{buy}\le P_{rt}^{grid,\max}y_{rt}^{trade},\quad
0\le P_{rt}^{sell}\le M_{rt}^{sell}(1-y_{rt}^{trade}),\quad
M_{rt}^{sell}=\min(P_{rt}^{export,\max},S_r^{\max}). \tag{12}
$$

成本、碳排、时延和新能源利用率沿用原定义；比率分母非正时输出 `metric_unavailable` 并排除对应Pareto排序。

### 求解方法

Pareto扫描封闭为7个候选：成本、碳、时延、新能源四个单目标参照点，以及在参照点归一化区间内取 \(25\%、50\%、75\%\) 的三组联动预算。归一化区间退化的指标从联动预算中删除，不以任意小数替代。顺序固定为四个参照点后三级折中点。

滚动窗口中，承诺区间内已经确定区域和开工时刻的全部任务均冻结，包括尚未开工任务。

### 必须回答的输出

保持原7项输出及文件名不变。

## 子问题 3：固定负荷储能优化

### 模型建立

能源分流、SOC和充放电互斥保持原式。购售电采用式(12)。修正峰值定义：

$$
N_{rt}=P_{rt}^{buy}-P_{rt}^{sell},\qquad
P_r^{peak}\ge0,\qquad P_r^{peak}\ge N_{rt}\quad\forall t. \tag{13}
$$

因此 \(P_r^{peak}=\max_t\max(0,N_{rt})\)，全时段净外送时峰值购电为0而非负数。

### 求解方法

固定7个候选：成本、碳、峰值、波动四个参照点及 \(25\%、50\%、75\%\) 三组联动预算；退化指标处理同问题二。

### 必须回答的输出

保持原6项输出及文件名不变。

## 子问题 4：多区域算—储—电联合优化

### 模型建立

服务质量定义保持不变。碳情景映射补为

$$
E_{\mathrm{CO2}}^{ref}
=\sum_{r,t}c_{rt}P_{rt}^{buy,ref}\Delta t,\qquad
\epsilon_C^{sc}=\alpha_CE_{\mathrm{CO2}}^{ref},\quad
\alpha_C\in\{1,0.9,0.8\}. \tag{14}
$$

参考方案是在基准电价、基准新能源下，取消碳预算但保留全部题面硬约束所得的成本最小完整可行联合方案；若该方案不存在，情景分析结构化停止。

滚动窗口末端 \(\tau\) 加入保守SOC可达性保护：

$$
E_{r\tau}+\eta_r^cP_r^{ch,\max}(2406-\tau)\Delta t\ge E_r^0. \tag{15}
$$

它只使用剩余时段最大可充电量，是终端约束的必要可达条件，不替代最终 \(E_{r,2406}\ge E_r^0\)。窗口同时冻结承诺段内全部任务决策。

基准Pareto固定7个候选；27个情景按 \((\alpha_C,\beta_{\rm price},\beta_{\rm RE})\) 字典序求解，不追加随机候选。

### 共享预算

四问使用同一单调时钟：

$$
B_{\rm total}=300\rm\,s,\qquad
D_{\rm search}=t_{\rm start}+285\rm\,s,\qquad
T_{\rm tail}=15\rm\,s. \tag{16}
$$

执行顺序固定为：数据校验与预测、问题一必答调度、问题二7点扫描、问题三7点扫描、问题四7点基准扫描、问题四27情景、统一验证与输出。每个固定任务、候选和求解器启动前均检查共同截止；仅当其显式time limit可落在总截止前才启动。单次求解上限为

$$
T_{\rm limit}=\max\{0,\min(30,D_{\rm search}-\mathrm{time.monotonic}())\}. \tag{17}
$$

搜索截止后仅执行验证和输出。已启动候选若不能在300秒前返回完整可行解则中断并丢弃；固定必答工作真实超时则记录耗时并结构化失败，不缩减候选集伪装完成。

### 必须回答的输出

保持原7项输出及文件名不变。

## 统一结果审计

除原任务、能源、SOC残差外，新增

$$
\rho_{\rm trade}=\max_{r,t}\min(P_{rt}^{buy},P_{rt}^{sell}),\qquad
\rho_{\rm peak}=\max_r\max(0,-P_r^{peak}), \tag{18}
$$

以及窗口承诺一致性和式(15)可达性残差。容差由代码阶段预声明，不按本次误差放宽。

## Verifier 修复核对表

| Block issue | 修复位置 | 可计算性与物理保证 |
|---|---|---|
| 功率、能量、GPU与GPU-hour混用 | 式(4)、(5)、(10) | AI能量除以 \(\Delta t\) 得平均功率；GPU容量乘 \(\Delta t\)；利用率成为无量纲比例。 |
| \(\alpha_C\) 未接入碳约束 | 式(14) | 用完整可行参考方案复算排放，并以 \(\epsilon_C^{sc}=\alpha_CE_{\rm CO2}^{ref}\) 生成可复算情景。 |
| 购售电未互斥 | 式(12) | 二元交易状态在问题二至四统一禁止同小时购售电，不依赖价格条件。 |
| 未冻结已承诺未开工任务 | 问题二、四求解方法 | 承诺段内全部区域与开工决策冻结，后续窗口不能改写。 |
| 联合储能缺少终端SOC可达性 | 式(15) | 每个窗口保留以最大充电能力返回初始SOC的必要余量，并最终执行原终端SOC硬约束。 |
| Pareto候选与预算不封闭 | 各问固定7候选、27情景及式(16)–(17) | 候选数、顺序和共同截止固定；四问、验证、输出共享300秒。 |
| 峰值净购电可为负 | 式(13) | 峰值定义为 \(\max_t\max(0,N_{rt})\)，全时段外送时有限输出0。 |
| “有限预测率”无定义 | 式(9)后的分支 | 删除该正式指标；WAPE不可用时仅报告定义完备的MAE、RMSE和结构化状态。 |