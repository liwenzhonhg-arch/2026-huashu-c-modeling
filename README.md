# 2026 年华数杯 C 题提交仓库

> **当前公开版本：Q1–Q4 已修复版本**
>
> 版本链：`model v48 / code v21 / solve v19 / paper v28 / review v22`
>
> 可信等级：`scenario-feasible`。本仓库用于队内复核与比赛提交准备；参赛编号和承诺书仍需在正式提交前确认。

`solve v19` 仅在 `solve v18` 冻结结果上扩展 Q1 rolling-origin 逐小时证据，未重新运行 Q1 调度或 Q2–Q4 优化；`solution.py` 与 `results.json` 哈希保持不变。

## 队友提交入口

`提交文件` 目录内有两个待上传文件：

1. `C参赛编号.pdf`：上传到赛氪的“参赛论文”位置。
2. `C参赛编号附件.zip`：上传到赛氪的“支撑材料”位置。

提交前必须把文件名中的“参赛编号”替换为报名系统中的 `CM******`。例如，参赛编号为 `CM2600001` 时，文件名应为：

- `CCM2600001.pdf`
- `CCM2600001附件.zip`

承诺书由队长在报名系统中单独上传，不存放在本公开仓库。

## 源文件

`源文件` 是 `提交文件/C参赛编号附件.zip` 的逐文件展开视图，便于在 GitHub 上直接浏览。它包含：

- `code/solution.py`：完整计算程序；
- `paper_source/`：论文 Markdown 与展开后的 LaTeX 源文件；
- `data/`：正式调度表、汇总结果和审计数据；
- `figures/`：论文图表；
- `evidence/`：版本、运行与验证证据；
- `README_run.txt`、`requirements.txt`、`VERSION.json`、`MANIFEST.sha256`：运行说明、依赖、版本和完整性清单。

压缩包内的 135 个文件已全部展开；完整文件名与 SHA-256 可直接查看 [`源文件/MANIFEST.sha256`](源文件/MANIFEST.sha256)。

为控制比赛附件体积，公开版本未包含官方原始题目附件及体积很大的全量搜索轨迹。正式提交以 `提交文件` 中的 PDF 与 ZIP 为准。
