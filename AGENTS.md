# AGENTS.md

## 仓库定位

本仓库保存“2026年第七届华数杯数学建模竞赛 C题”的完整协作快照，包含原始赛题、附件、MMW 检查点、缓存、日志、代码、求解结果、论文和导出物。

## 目录规则

- 原始赛题、`附件数据/` 和 `附件1.docx` 为输入证据，不修改、不重命名。
- `.mmw/` 为完整流水线检查点、审批和日志证据，保持版本原貌。
- `output/` 为现役代码、数据、图表、论文和提交包。
- 新说明写入根目录 Markdown；临时文件不得覆盖已有证据。
- `tests/` 仅保存本 C 题的确定性专项测试，命名为 `test_*.py`；测试缓存不进入正式交付。
- `tools/` 仅保存本 C 题的运行、校验和导出工具；正式数值仍以 active checkpoint 的 `solution.py` 为准。
- `output/runs/<run-id>/` 保存通过隔离执行与验证的不可变运行；失败运行保留为同级
  `<run-id>.incomplete/`，不得把其中任何部分提升为现役输出。
- 根目录 `output/data/` 与 `output/figures/` 只是 active solve 的快速镜像；切换现役版本时，
  旧镜像整体移入 `output/archive/<timestamp>-<version>/` 后再替换，禁止新旧文件混放。
- `output/archive/` 仅保存被现役镜像替换的历史根目录副本；不参与验证和提交包，清理需另行授权。
- `output/robustness-v<model>-code<code>-paper-v<paper>/` 保存一次现役链的不可变完整镜像；
  `output/submission-v<model>-code<code>/` 与 `output/reproducibility-v<model>-code<code>/`
  分别保存最小提交包和可复算包的展开目录，三者均不得原地覆盖。

## 协作规则

- 修改结果前必须重新运行对应流程并保留新的结构化证据。
- 运行默认不设墙钟限制；仅显式设置 `MMW_MAX_RUNTIME_SECONDS` 时允许中断，并必须保留
  `external_timeout`、`incomplete=true` 的隔离证据。
- 新算法或正式数值只能写入递增的 model/code/solve/paper/review checkpoint，已审批版本不可原地修改。
- 不把启发式可行结果写成全局最优；当前可信等级为 `scenario-feasible`。
- 不提交 `.env`、密钥、Token、Cookie、登录态或私人凭据。
- 删除、历史重写、公开发布和推送必须由仓库所有者明确确认。
