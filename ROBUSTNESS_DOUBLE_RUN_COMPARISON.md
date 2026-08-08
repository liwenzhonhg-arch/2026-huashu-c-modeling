# v16 双独立完整运行一致性

结论：`pass`。

- 输出文件数：[53, 53]
- 文件清单一致：True
- results.json SHA-256：`377f0fc8b247bf8392c5a49ea8fb428a47b029a927ac01de1a49555bcc759956` / `377f0fc8b247bf8392c5a49ea8fb428a47b029a927ac01de1a49555bcc759956`
- results.json 哈希一致：True
- method_runtime 去除 run_id 与 elapsed_seconds 后语义一致：True
- Q2/Q3/Q4 结构化语义一致：True / True / True
- 字节差异文件：data/method_runtime.json, data/q3_soc_grid_sensitivity.csv, data/sensitivity.json

详细证据：`C题技术验证/robustness-run-2/double_run_comparison.json`。
