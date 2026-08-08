# v17/v18 -> v19 迁移冻结表

- v17: {'pages': 16, 'chars': 38555, 'sections': 30, 'figures': 5, 'tables': 5, 'citations': 3}
- v18: {'pages': 7, 'chars': 14263, 'sections': 16, 'figures': 3, 'tables': 1, 'citations': 2}

|章节|来源|v19动作|
|---|---|---|
|摘要|v18 factual core|rewrite with current Q1-Q4 results, finite-search and scenario-feasible boundary|
|问题重述|v17|retain structure; remove submission/compliance claims|
|问题分析|v17+v18|restore four-question reasoning; replace old fixed-search descriptions with current closed-loop/five-scheme/DP/dynamic-alternation methods|
|模型假设|v17|retain only assumptions consistent with model42/code15/solve12|
|符号说明|v17|retain shared notation; align terminal SOC equality and service metrics|
|模型建立与求解|v17 equations + v18 current contract + solve12 tables|rewrite; include Q1 forecast comparison, Q2 five schemes and decomposition, Q3 seven policies, Q4 algorithm and 17 scenarios|
|检验与灵敏度|v18 + solve12 evidence|expand dual-run, constraint residual, price/renewable, terminal SOC and high-cycle interpretation|
|评价与推广|v17 structure + current evidence|rewrite strengths/limitations without optimality overclaim|
|附录|v17 structure|current algorithm pseudocode and evidence paths; no final-submission packaging|

## 不可变输入 SHA-256

- code_v15_solution.py: `9d72512be2ff73f3eb12544ce59f860823df934f6c6c1a3c0372218bd7fec636`
- solve_v12_results.json: `691e95d6f0450c63c6b0468a55453af778dfe949316eadadc63a5ad8a0a4daa0`
- solve_v12_method_contract.json: `d7b5c81661c8226b159e9d031c95d5cadec92a2b327791e0f6c2fb3b01dffc48`
