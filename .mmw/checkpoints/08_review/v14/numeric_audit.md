# review v14 数值出处复核

- 内置审计：共提取 390，匹配 257，缩放匹配 55，高置信待复核 76。
- 二次复核：已确认 76，未确认 0。
- 复核范围：solve v12 冻结 CSV/JSON、双运行证据，以及由冻结 Q1 指标逐类型重算的均值；旧论文图表不作为数值证据。

|论文原值|章节|结论|出处/判断|
|---:|---|---|---|
|`4.218017\times10^8`|sections/abstract.tex|verified|data/q2_named_scheme_comparison.csv:cost_CNY; direct; scientific rounded 6 digits; evidence value=-421801700|
|`485`|sections/evaluation.tex|verified|data/q2_search_summary.csv:final_wait_h; direct; evidence value=485|
|`48,168`|sections/model_solution.tex|parser|comma-separated lag list 48 and 168, not number 48168|
|`35.3032`|sections/model_solution.tex|verified|evidence/q1-naive-comparison.csv:mean_series_MAE; direct; rounded 4dp; evidence value=35.3032|
|`46.9509`|sections/model_solution.tex|verified|evidence/q1-naive-comparison.csv:mean_series_RMSE; direct; rounded 4dp; evidence value=46.9509|
|`1.0809`|sections/model_solution.tex|verified|evidence/q1-naive-comparison.csv:mean_series_WAPE; direct; rounded 4dp; evidence value=1.0809|
|`35.9120`|sections/model_solution.tex|verified|evidence/q1-naive-comparison.csv:mean_series_MAE; direct; rounded 3dp; evidence value=35.912|
|`46.9954`|sections/model_solution.tex|verified|evidence/q1-naive-comparison.csv:mean_series_RMSE; direct; rounded 4dp; evidence value=46.9954|
|`1.2171`|sections/model_solution.tex|verified|evidence/q1-naive-comparison.csv:mean_series_WAPE; direct; rounded 4dp; evidence value=1.2171|
|`0.8231`|sections/model_solution.tex|verified|evidence/q1-naive-comparison.csv:mean_series_WAPE; direct; rounded 4dp; evidence value=0.8231|
|`3.1140`|sections/model_solution.tex|verified|output/technical-repair-v42-code15/data/q1_forecast_metrics.csv (solve12 SHA-256 f950f4...):MAE; six-region mean for RealTimeInference; recomputed=3.1140184073|
|`4.3412`|sections/model_solution.tex|verified|output/technical-repair-v42-code15/data/q1_forecast_metrics.csv (solve12 SHA-256 f950f4...):RMSE; six-region mean for RealTimeInference; recomputed=4.3411501184|
|`0.8465`|sections/model_solution.tex|verified|output/technical-repair-v42-code15/data/q1_forecast_metrics.csv (solve12 SHA-256 f950f4...):WAPE; six-region mean for RealTimeInference; recomputed=0.8465243696|
|`12.7318`|sections/model_solution.tex|verified|output/technical-repair-v42-code15/data/q1_forecast_metrics.csv (solve12 SHA-256 f950f4...):MAE; six-region mean for BatchInference; recomputed=12.7318302203|
|`16.9469`|sections/model_solution.tex|verified|output/technical-repair-v42-code15/data/q1_forecast_metrics.csv (solve12 SHA-256 f950f4...):RMSE; six-region mean for BatchInference; recomputed=16.9468812748|
|`0.7328`|sections/model_solution.tex|verified|output/technical-repair-v42-code15/data/q1_forecast_metrics.csv (solve12 SHA-256 f950f4...):WAPE; six-region mean for BatchInference; recomputed=0.7327799308|
|`60.9217`|sections/model_solution.tex|verified|output/technical-repair-v42-code15/data/q1_forecast_metrics.csv (solve12 SHA-256 f950f4...):MAE; six-region mean for AITraining; recomputed=60.9216671075|
|`82.2330`|sections/model_solution.tex|verified|output/technical-repair-v42-code15/data/q1_forecast_metrics.csv (solve12 SHA-256 f950f4...):RMSE; six-region mean for AITraining; recomputed=82.2330450593|
|`0.8899`|sections/model_solution.tex|verified|output/technical-repair-v42-code15/data/q1_forecast_metrics.csv (solve12 SHA-256 f950f4...):WAPE; six-region mean for AITraining; recomputed=0.8898759866|
|`27.5`|sections/model_solution.tex|verified|derived:q1 MAE reduction vs SeasonalNaive24; derived percentage; rounded 1dp; evidence value=27.5|
|`-4.2334`|sections/model_solution.tex|verified|data/q2_named_scheme_comparison.csv:cost_CNY; direct; 亿元 rounded 4dp; evidence value=-4.2334|
|`10.2851`|sections/model_solution.tex|verified|data/q2_named_scheme_comparison.csv:carbon_tCO2; direct; rounded 4dp; evidence value=10.2851|
|`6.2235`|sections/model_solution.tex|verified|data/q2_named_scheme_comparison.csv:network_latency_ms; direct; rounded 4dp; evidence value=6.2235|
|`368`|sections/model_solution.tex|verified|data/q2_named_scheme_comparison.csv:migration_count; direct; evidence value=368|
|`422`|sections/model_solution.tex|verified|data/q2_named_scheme_comparison.csv:accepted_improvements; direct; evidence value=422|
|`0.679078`|sections/model_solution.tex|verified|data/q2_named_scheme_comparison.csv:renewable_utilization; direct; rounded 6dp; evidence value=0.679078|
|`5.1594`|sections/model_solution.tex|verified|data/q2_named_scheme_comparison.csv:network_latency_ms; direct; rounded 4dp; evidence value=5.1594|
|`209`|sections/model_solution.tex|verified|data/q2_named_scheme_comparison.csv:migration_count; direct; evidence value=209|
|`-4.2230`|sections/model_solution.tex|verified|data/q2_named_scheme_comparison.csv:cost_CNY; direct; 亿元 rounded 3dp; evidence value=-4.223|
|`7.0758`|sections/model_solution.tex|verified|data/q2_named_scheme_comparison.csv:network_latency_ms; direct; rounded 4dp; evidence value=7.0758|
|`574`|sections/model_solution.tex|verified|data/q2_named_scheme_comparison.csv:migration_count; direct; evidence value=574|
|`0.679078`|sections/model_solution.tex|verified|data/q2_named_scheme_comparison.csv:renewable_utilization; direct; rounded 6dp; evidence value=0.679078|
|`5.1594`|sections/model_solution.tex|verified|data/q2_named_scheme_comparison.csv:network_latency_ms; direct; rounded 4dp; evidence value=5.1594|
|`209`|sections/model_solution.tex|verified|data/q2_named_scheme_comparison.csv:migration_count; direct; evidence value=209|
|`485`|sections/model_solution.tex|verified|data/q2_search_summary.csv:final_wait_h; direct; evidence value=485|
|`25.8055`|sections/model_solution.tex|verified|data/q2_energy_cost_min.csv:buy_MWh aggregate; aggregate; rounded 4dp; evidence value=25.8055|
|`1343742.0294`|sections/model_solution.tex|verified|data/q2_energy_cost_min.csv:sell_MWh aggregate; aggregate; rounded 4dp; evidence value=1343742.0294|
|`0.8516`|sections/model_solution.tex|verified|data/q2_energy_cost_min.csv:buy_expense_CNY aggregate; aggregate; 万元 rounded 4dp; evidence value=0.8516|
|`4.2335`|sections/model_solution.tex|verified|data/q2_energy_cost_min.csv:sell_revenue_CNY aggregate; aggregate; 亿元 rounded 4dp; evidence value=4.2335|
|`-4.2334`|sections/model_solution.tex|verified|data/q2_named_scheme_comparison.csv:cost_CNY; direct; 亿元 rounded 4dp; evidence value=-4.2334|
|`40.4664`|sections/model_solution.tex|verified|data/q4_search_summary.csv:baseline_peak_MW; direct; rounded 4dp; evidence value=40.4664|
|`1329591.2956`|sections/model_solution.tex|verified|data/q2_energy_carbon_min.csv:sell_MWh aggregate; aggregate; rounded 4dp; evidence value=1329591.2956|
|`40.4664`|sections/model_solution.tex|verified|data/q4_search_summary.csv:baseline_peak_MW; direct; rounded 4dp; evidence value=40.4664|
|`1339961.0855`|sections/model_solution.tex|verified|data/q2_energy_renewable_max.csv:sell_MWh aggregate; aggregate; rounded 4dp; evidence value=1339961.0855|
|`4.2231`|sections/model_solution.tex|verified|data/q2_energy_renewable_max.csv:sell_revenue_CNY aggregate; aggregate; 亿元 rounded 4dp; evidence value=4.2231|
|`-4.2230`|sections/model_solution.tex|verified|data/q2_named_scheme_comparison.csv:cost_CNY; direct; 亿元 rounded 3dp; evidence value=-4.223|
|`40.4664`|sections/model_solution.tex|verified|data/q4_search_summary.csv:baseline_peak_MW; direct; rounded 4dp; evidence value=40.4664|
|`1329591.2956`|sections/model_solution.tex|verified|data/q2_energy_carbon_min.csv:sell_MWh aggregate; aggregate; rounded 4dp; evidence value=1329591.2956|
|`43.7999`|sections/model_solution.tex|verified|data/q2_energy_balanced.csv:buy_MWh aggregate; aggregate; rounded 4dp; evidence value=43.7999|
|`1337864.0359`|sections/model_solution.tex|verified|data/q2_energy_balanced.csv:sell_MWh aggregate; aggregate; rounded 4dp; evidence value=1337864.0359|
|`1.4424`|sections/model_solution.tex|verified|data/q2_energy_balanced.csv:buy_expense_CNY aggregate; aggregate; 万元 rounded 4dp; evidence value=1.4424|
|`4.2182`|sections/model_solution.tex|verified|data/q2_energy_balanced.csv:sell_revenue_CNY aggregate; aggregate; 亿元 rounded 4dp; evidence value=4.2182|
|`0.679150`|sections/model_solution.tex|verified|data/q3_search_trace.csv:renewable_utilization; direct; rounded 5dp; evidence value=0.67915|
|`0.711735`|sections/model_solution.tex|verified|data/q3_search_trace.csv:renewable_utilization; direct; rounded 6dp; evidence value=0.711735|
|`4.6997`|sections/model_solution.tex|verified|data/q3_search_trace.csv:carbon_tCO2; direct; rounded 4dp; evidence value=4.6997|
|`11.4975`|sections/model_solution.tex|verified|data/q3_search_trace.csv:carbon_tCO2; direct; rounded 4dp; evidence value=11.4975|
|`2.146`|sections/model_solution.tex|verified|data/q3_search_trace.csv:equivalent_full_cycles_sum; direct; rounded 3dp; evidence value=2.146|
|`2.7455`|sections/model_solution.tex|verified|data/q3_search_trace.csv:peak_MW; direct; rounded 4dp; evidence value=2.7455|
|`15.2020`|sections/model_solution.tex|verified|data/q3_search_trace.csv:ramp_MW; direct; rounded 3dp; evidence value=15.202|
|`1568.882`|sections/model_solution.tex|verified|data/q3_search_trace.csv:equivalent_full_cycles_sum; direct; rounded 3dp; evidence value=1568.882|
|`2.146`|sections/model_solution.tex|verified|data/q3_search_trace.csv:equivalent_full_cycles_sum; direct; rounded 3dp; evidence value=2.146|
|`40.9020`|sections/model_solution.tex|verified|data/q3_search_trace.csv:peak_MW; direct; rounded 3dp; evidence value=40.902|
|`81.8040`|sections/model_solution.tex|verified|data/q3_search_trace.csv:ramp_MW; direct; rounded 3dp; evidence value=81.804|
|`2.496`|sections/model_solution.tex|verified|data/q3_search_trace.csv:equivalent_full_cycles_sum; direct; rounded 3dp; evidence value=2.496|
|`1568.242`|sections/model_solution.tex|verified|data/q3_search_trace.csv:equivalent_full_cycles_sum; direct; rounded 3dp; evidence value=1568.242|
|`1800`|sections/model_solution.tex|verified|data/q4_scenario_comparison_v42.csv:checked_candidates; direct; evidence value=1800|
|`58.075356`|sections/model_solution.tex|verified|data/q4_alternation_trace.csv:joint_score_before; direct; rounded 6dp; evidence value=58.075356|
|`0.101290`|sections/model_solution.tex|verified|data/q4_alternation_trace.csv:joint_score_before; direct; rounded 5dp; evidence value=0.10129|
|`303.034335`|sections/model_solution.tex|verified|data/q4_alternation_trace.csv:joint_score_before; direct; rounded 6dp; evidence value=303.034335|
|`294.820472`|sections/model_solution.tex|verified|data/q4_alternation_trace.csv:joint_score_before; direct; rounded 6dp; evidence value=294.820472|
|`582`|sections/model_solution.tex|verified|data/q4_scenario_comparison_v42.csv:migration_count; direct; evidence value=582|
|`583`|sections/model_solution.tex|verified|data/q4_scenario_comparison_v42.csv:migration_count; direct; evidence value=583|
|`1706.49`|sections/sensitivity.tex|verified|evidence\run-comparison.json/run_2_elapsed_seconds; direct; rounded 2dp; evidence value=1706.49|
|`1568.242`|sections/sensitivity.tex|verified|data/q3_search_trace.csv:equivalent_full_cycles_sum; direct; rounded 3dp; evidence value=1568.242|
|`-298.6499`|sections/sensitivity.tex|parser|TeX range separator `--` attached to positive upper endpoint; +298.6499 and +852.0600 are in frozen solve12 q4_scenario_comparison_v42.csv|
|`-852.0600`|sections/sensitivity.tex|parser|TeX range separator `--` attached to positive upper endpoint; +298.6499 and +852.0600 are in frozen solve12 q4_scenario_comparison_v42.csv|

## 结论

内置审计的 76 个高置信待复核项全部完成出处确认；数值来自冻结 solve v12、双运行证据或可复算派生，区间连字符与逗号分隔滞后列表属于解析器误识别。未确认数为 0。
