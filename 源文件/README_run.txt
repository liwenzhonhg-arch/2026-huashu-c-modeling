2026年第七届华数杯数学建模竞赛 C题 支撑材料（精简版）

版本链：model v48 / code v21 / solve v18 / paper v26 / review v20
可信等级：scenario-feasible

一、目录
code/solution.py            完整计算程序
data/                        论文关键结果、正式调度、约束审计与敏感性结果
figures/                     论文使用的正式图表
paper_source/                公式保留Markdown与展开LaTeX源文件
evidence/                    双次运行、benchmark、数值与版式检查证据
requirements.txt             Python依赖
MANIFEST.sha256              包内文件哈希

二、输入
程序默认从solution.py同级工作目录的“附件数据”文件夹读取官方原始赛题数据。
官方原始数据依竞赛说明不重复打包。需要以下文件：
GPU_information.xlsx
network_latency.xlsx
power_mapping.xlsx
region_time_data.xlsx
storage_information.xlsx
workload_trace.xlsx

三、运行
PowerShell：
  python -m pip install -r requirements.txt
  Remove-Item Env:MMW_MAX_RUNTIME_SECONDS -ErrorAction SilentlyContinue
  $env:PYTHONIOENCODING='utf-8'
  python .\code\solution.py

如从包根运行，请将官方“附件数据”文件夹置于包根。程序在output目录生成结果。
完整复算耗时较长；正式提交不要求现场重新执行两次。

四、精简原则
本包保留完整源程序、正式结果、关键审计和论文图表；不包含数百MB的逐候选搜索轨迹、重复候选池、全量场景逐时明细及官方原始数据。被删减内容仅为可再生的中间证据，不改变论文、正式结果和代码。
