# 鲁棒性修复最终验证

现役链：`model v43 / code v16 / solve v13 / paper v21 / review v15`；可信等级：`scenario-feasible`。

## 正式运行

- run-1：默认无墙钟，754.3743 秒，求解退出码 0，验证退出码 0。
- run-2：默认无墙钟，793.7084 秒，求解退出码 0，验证退出码 0。
- 两次均输出 53 个文件；文件清单一致；`results.json` SHA-256 均为
  `377f0fc8b247bf8392c5a49ea8fb428a47b029a927ac01de1a49555bcc759956`。
- 除真实运行耗时字段外，Q2、Q3、Q4 结构化语义一致；最大正约束残差为
  `1.1368683772161605e-13`。
- 便携证据：`ROBUSTNESS_DOUBLE_RUN_COMPARISON.md`、
  `tests/evidence/double_run_comparison.json`；完整运行现场仅保存在本机 `output/runs/`。

## 墙钟隔离

命令：

```powershell
python tools/run_official.py --case-root . --code .mmw/checkpoints/05_code/v16/solution.py `
  --run-dir ../C题技术验证/robustness-timeout-v2 --max-runtime-seconds 1
```

预期退出码 124；实际退出码 124。当前 v16 在 `q1.greedy_schedule` 内部中断，
`termination_status=external_timeout`、`incomplete=true`，且证据中的代码哈希与 active v16 一致。
便携证据：`tests/evidence/timeout_method_runtime.json`；完整失败现场仅保存在本机
`output/runs/robustness-timeout-v2.incomplete/`。

## 自动验证

| 命令 | 退出码 | 结果 |
|---|---:|---|
| `python -m py_compile .mmw/checkpoints/05_code/v16/solution.py validate_results.py tools/run_official.py tools/build_delivery.py` | 0 | 语法通过 |
| `pytest -q tests` | 0 | 6 passed |
| `python validate_results.py .` | 0 | 根目录 active/export 门禁通过 |
| `python validate_results.py <submission-extract-check-v2> --run-only` | 0 | 提交包解压验证通过 |
| `python validate_results.py <reproducibility-extract-check-v4> --run-only` | 0 | 可复算包解压验证通过；墙钟证据代码哈希与 active v16 一致 |
| 两个解压目录的 `MANIFEST.sha256` 逐文件复核 | 0 | 54 / 69 个受清单约束文件通过 |
| `git diff --check` | 0 | 通过 |

## 最终包

- `output/submission.zip`：55 个文件，SHA-256
  `7173eca2ab6a155ba92c201a3ef5c9213f0a3adc94ebccade58c5bc39292ff54`。
- `output/reproducibility.zip`：70 个文件，SHA-256
  `4c4ba4c85c0117191b352e92ddaf6dc18c913a32bb4d881b9ce4f999caf227fb`。
- 两包均通过 CRC、重复成员、绝对路径/路径穿越、`.env`、Cookie、缓存和登录态检查。

未执行 Git commit、push、rebase、reset、删除或清理。
