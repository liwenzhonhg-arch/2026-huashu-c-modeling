# 实际落地与鲁棒性修复前基线

记录时间：2026-08-08T12:58:29.160100+08:00

现役链：`model v42 / code v15 / solve v12 / paper v20 / review v14`。

## 现役检查点文件 SHA-256

- `.mmw/checkpoints/04_model/v42/equations.json` `6dd6d10d64d14efa2f465b7fe45378fc82a86789adcfe3a110951e4d0a005645`
- `.mmw/checkpoints/04_model/v42/meta.json` `1ff688bdd9e6f41ef39be2ae65bbbc1fbf91911755ab26c175194ac0e9588c72`
- `.mmw/checkpoints/04_model/v42/method_contract.json` `91872ff91531ffaaa3d73743d799e3e9c3893d5b0b3a25b6983bb0854342b8a2`
- `.mmw/checkpoints/04_model/v42/model.md` `9478d61c36b58cc5b267558648286bfe89f29032904827af755f54aa9e7ce6bb`
- `.mmw/checkpoints/04_model/v42/params.json` `c33741451785b427f09627a11eff146e733c2f7d04ea5d52701c0e89cbc80812`
- `.mmw/checkpoints/04_model/v42/revision_history.json` `7ed3d46ae1454321649b94aca3d582476d2f24d2cd3e1af9a535a69ae449c552`
- `.mmw/checkpoints/04_model/v42/status.json` `98d748b75d86bd19fdb03b39149f74fad6bbdcb596b9e72b2323d268432bac3f`
- `.mmw/checkpoints/04_model/v42/verify_report.md` `66623a620b1b53bc854d03d3e0c2c59029686f324bea2fd6d987e5ae842c22b8`
- `.mmw/checkpoints/04_model/v42/verify_status.json` `f863d1159a9c92308b63366fb5e427d6d3b0f1da34e431be7157d94c77717bb2`
- `.mmw/checkpoints/05_code/v15/attempt_history.json` `00a6990dfe792d11759980f958ce3e9c0795c44f2263c237638ab8313a2ed142`
- `.mmw/checkpoints/05_code/v15/code_explanation.md` `0c60b002a92e1e08cd4a820ae7123dbfebdde9eca33d69a78fdcbbbf51892168`
- `.mmw/checkpoints/05_code/v15/meta.json` `6e70a155765bf56d6b49232a084826478d2d8b710d9641616d9efa08ecf26098`
- `.mmw/checkpoints/05_code/v15/method_contract.json` `32a59542643d396b455ae2e87a931b59ce8c989b4a04f3ff66ec6955cb699d48`
- `.mmw/checkpoints/05_code/v15/method_pilot.json` `999445a61604298853979d4fd4e1fa31b678276f73623249913859ff82214447`
- `.mmw/checkpoints/05_code/v15/method_runtime.json` `bedcfc73f113093af3492349a3f9b6758eae465f79f8f538feaed093ab33f82d`
- `.mmw/checkpoints/05_code/v15/results_preview.json` `691e95d6f0450c63c6b0468a55453af778dfe949316eadadc63a5ad8a0a4daa0`
- `.mmw/checkpoints/05_code/v15/run_log.txt` `cc99d5a348990c7ec33842395363f769472864d19538801231703fc364c61a97`
- `.mmw/checkpoints/05_code/v15/solution.py` `9d72512be2ff73f3eb12544ce59f860823df934f6c6c1a3c0372218bd7fec636`
- `.mmw/checkpoints/05_code/v15/status.json` `835356f1cd254712a17504571e7667ebf0a6f3c382820288d689209b39865849`
- `.mmw/checkpoints/06_solve/v12/data_tables.json` `cb82aebb3b5ba3386a54e0a396b718c490f2aabb344dfbef7b0f6ec1c127702b`
- `.mmw/checkpoints/06_solve/v12/deliverables_manifest.json` `44136fa355b3678a1146ad16f7e8649e94fb4fc21fe77e8310c060f61caaff8a`
- `.mmw/checkpoints/06_solve/v12/figure_manifest.json` `58d41f196738257b9387f1b961702127ccdb884851dea2b1ae6eadc35d637a85`
- `.mmw/checkpoints/06_solve/v12/figures_list.json` `388d35bfaa3f0ca6b24f0fab72cc02a9d9f34fe9dc702502ee1e02245d52bbd0`
- `.mmw/checkpoints/06_solve/v12/interpretation.md` `36359359433bcae56c50e404ad352ff98b183d7ee647555d6d43b9f0597c48c0`
- `.mmw/checkpoints/06_solve/v12/meta.json` `ce6f10f3aa6d91c97f05414b6edf4854edd8b54a52a781fe9f3be644d044dfab`
- `.mmw/checkpoints/06_solve/v12/method_contract.json` `d7b5c81661c8226b159e9d031c95d5cadec92a2b327791e0f6c2fb3b01dffc48`
- `.mmw/checkpoints/06_solve/v12/method_runtime.json` `bedcfc73f113093af3492349a3f9b6758eae465f79f8f538feaed093ab33f82d`
- `.mmw/checkpoints/06_solve/v12/method_validation.json` `59c1618ccd243718a7584c40ac1e1658d0d7c62ec5a201a56aa2ef9ac8bb0914`
- `.mmw/checkpoints/06_solve/v12/results.json` `691e95d6f0450c63c6b0468a55453af778dfe949316eadadc63a5ad8a0a4daa0`
- `.mmw/checkpoints/06_solve/v12/run_log.txt` `cc99d5a348990c7ec33842395363f769472864d19538801231703fc364c61a97`
- `.mmw/checkpoints/06_solve/v12/sensitivity.json` `095605183e85cb99c4ca515ceeb246ec12a1ac39e1006dceb9c648e4489c4fa6`
- `.mmw/checkpoints/06_solve/v12/status.json` `070ebf289b3c148ee6a8d3f8cc0e7eb03ba377a00b6b0b54769b50a080cc96e9`
- `.mmw/checkpoints/07_paper/v20/abstract_iterations.json` `6fb671a2905f54d547ffab8a5b24654b1f20118f934066bf54dd44aa0261c490`
- `.mmw/checkpoints/07_paper/v20/abstract_score.json` `7041376de81bda523261e4c8a8536b05dd38e80a2a3f5e114d94460913d5a263`
- `.mmw/checkpoints/07_paper/v20/cumcmthesis.cls` `a4625fc08688420d34dff6b34d368f2de45da93fb8cd3ee67b5ea729e622ce90`
- `.mmw/checkpoints/07_paper/v20/layout_report.json` `38c8c64429325cf81f2220d680edf571ba897d62d933d44ddedbc5bd66a107b0`
- `.mmw/checkpoints/07_paper/v20/main.tex` `3b7d9d4399a8446d580fdcfff17d7fbd7aa6c45d9670cebd14de2140ba6edd07`
- `.mmw/checkpoints/07_paper/v20/meta.json` `9a82d32708df3f363fa62ac1694376e1117b25f847fe44cc5c12f59913efd7ca`
- `.mmw/checkpoints/07_paper/v20/method_contract.json` `d7b5c81661c8226b159e9d031c95d5cadec92a2b327791e0f6c2fb3b01dffc48`
- `.mmw/checkpoints/07_paper/v20/method_traceability.json` `094ea6a609d85ee3e0c19fde0e394f853c2a8e25bacd4701846d04faf5abd399`
- `.mmw/checkpoints/07_paper/v20/paper.pdf` `c442be7f4098734bcf56148a94279911846fd95693293aeca12f308c10179b55`
- `.mmw/checkpoints/07_paper/v20/readability_gate.json` `c90d6770528ec97ef463ab63e1529a39b2e917e195246cfc7a0132e95dddc803`
- `.mmw/checkpoints/07_paper/v20/references.bib` `243325bd72d6fcab9cda28818dabf4608b838deeb68a59a59c35018add80b7bf`
- `.mmw/checkpoints/07_paper/v20/sections/abstract.tex` `fbb21cede4c652e319b422976f20729cdf666a6b6a80d25c3591d6d3902bf4d1`
- `.mmw/checkpoints/07_paper/v20/sections/appendix.tex` `cabe06e2e70ca12cb9ab1c944b5395ce5f99f10cc60dfbf5fb9d2b89e4555d8f`
- `.mmw/checkpoints/07_paper/v20/sections/assumptions.tex` `0d9e101c3d52a45aa28c6bfd9862f766367c4cd44cf408b37be5b3c3189b5b36`
- `.mmw/checkpoints/07_paper/v20/sections/evaluation.tex` `a021e51fbfce0c7885fe8fd5e4ab3fa95c72faa65c8e95163e4b0cf2ffcb3026`
- `.mmw/checkpoints/07_paper/v20/sections/model_solution.tex` `0d970f81b9f2375f73376996cf38f6628518e7c45e73348beaf6b94b0c09c83f`
- `.mmw/checkpoints/07_paper/v20/sections/problem_analysis.tex` `2ccdcc97bd260eb407cc2e371788d1268c23b256bea76bdf9d01c9ccf42936a7`
- `.mmw/checkpoints/07_paper/v20/sections/problem_restatement.tex` `4426a4f5ac0ba1262d1b8d9f006060ce89b0f3eaafc0c6bfeb4af4d353560792`
- `.mmw/checkpoints/07_paper/v20/sections/sensitivity.tex` `1d7006384241fe0a7a78956301f3447e4a087b9d00255aeb70719695f1e5743c`
- `.mmw/checkpoints/07_paper/v20/sections/symbols.tex` `dcc106687ce0a92fe240efabfd337cedd0d9af35ea8909df17554707358ef844`
- `.mmw/checkpoints/07_paper/v20/solution.py` `9d72512be2ff73f3eb12544ce59f860823df934f6c6c1a3c0372218bd7fec636`
- `.mmw/checkpoints/07_paper/v20/status.json` `e96ecc3d90864a4101120536ba54f56ccb9a287e8045f616eaf357124fdb74c7`
- `.mmw/checkpoints/08_review/v14/checklist.json` `1e251eeb0ac7c8ebd041b9cf7cd5799f52ee038a60459f1a312036ad1b44c931`
- `.mmw/checkpoints/08_review/v14/layout_review.json` `515e70b806f992dca59abe763c7caaeaccb36d55a1f0307a4baac311395ee0b6`
- `.mmw/checkpoints/08_review/v14/meta.json` `3917acb23766539c41731e8bcdb83d20d9689e411068585ffee73664ac957ffd`
- `.mmw/checkpoints/08_review/v14/method_consistency.json` `787b05422903466b8a5c951278e0bdf02ea63a10236141dee7211281fa8e4d1f`
- `.mmw/checkpoints/08_review/v14/numeric_audit.md` `e0139f93a814cd76b4bac56dfaca4b04f26f9ed207932359ccea8fe66234ab45`
- `.mmw/checkpoints/08_review/v14/numeric_audit_builtin.md` `99fb037327988738b54ab0b96f347d30a17bbc43b8defbc9d670103bfb76f996`
- `.mmw/checkpoints/08_review/v14/numeric_provenance.json` `6a445be85a9abda5c0353bba0ec94de4fcb08fc98c35a05bfac11d111850d090`
- `.mmw/checkpoints/08_review/v14/readability_gate.json` `fbb9111e43339571954636a34bc5be47f37429d1287c25ec4befcfe7e9538e9f`
- `.mmw/checkpoints/08_review/v14/review.md` `9f35e94ca2952155a5d28dad1f2bc2ad1d93583a23c1b63ca86f0ffd324ec715`
- `.mmw/checkpoints/08_review/v14/status.json` `cb8aeaa29b617e008a4c9b8d1a14819b41b9868a40a552891f0334c1e91e7bd5`

## 根目录现役交付物 SHA-256

- `README.md` `c963a930b814bde90997897b029cbb4154157634d2f9db008cf8c0ae5fc8c2fd`
- `output/CURRENT_DELIVERY.md` `df19c3fe98b7fe293ff37222ee6fce5f1013bd7b24134e4bffbd0da9aa24af31`
- `output/code/solution.py` `d131306c5dca306012fc33c3edad40baf77b7992796e075aa5b49f73eb610ec2`
- `output/data/results.json` `8fe6ac1f258c26a69d6ed0a8acafb3642348c4f4dd53c8e800364e13de740c71`
- `output/data/sensitivity.json` `608fb52039463c05561ea7c47647eb8f60fc889c8cab1d71342a2f336aac866b`
- `output/paper.pdf` `c442be7f4098734bcf56148a94279911846fd95693293aeca12f308c10179b55`
- `output/submission.zip` `1bf0e195d4402d82624b6e28e891902b44f2199f1bd1e611b05f7f3ed842536c`
- `output/benchmark.json` `b27777ea56060717491b307949fa5c5bbd3da98f61146b026bb95d7173d3000d`
- `output/paper_manifest.json` `69c5bb470393f5a4606c89bde2a152be50cc93c94a82555c913bbb717b743805`

## submission.zip 修复前清单

- `paper.pdf` (1279071 bytes, CRC32=3e12cc0e)
- `code/solution.py` (149439 bytes, CRC32=a392bfde)
- `data/results.json` (32398 bytes, CRC32=7cb49537)
- `data/sensitivity.json` (1548 bytes, CRC32=776a4286)
- `verification/benchmark.json` (1022 bytes, CRC32=927cec53)
- `verification/layout_quality.json` (1141 bytes, CRC32=f3f32497)
- `verification/numeric_audit.md` (12024 bytes, CRC32=508893eb)
- `verification/method/model_method_contract.json` (4980 bytes, CRC32=1629cbcd)
- `verification/method/code_method_contract.json` (6240 bytes, CRC32=12ff2eb4)
- `verification/method/solve_method_contract.json` (6395 bytes, CRC32=d31cf23c)
- `verification/method/solve_method_runtime.json` (2729 bytes, CRC32=04729393)
- `verification/method/solve_method_validation.json` (1098 bytes, CRC32=7c3fafb4)
- `verification/method/paper_method_contract.json` (6395 bytes, CRC32=d31cf23c)
- `verification/method/paper_method_traceability.json` (890 bytes, CRC32=d9816419)
- `verification/method/review_method_consistency.json` (150 bytes, CRC32=17d78785)
- `figures/fig_1_gpu_utilization.png` (446309 bytes, CRC32=892781de)
- `figures/fig_2_storage_soc.png` (141538 bytes, CRC32=bc9e3c21)
- `figures/sensitivity_electricity_price.png` (171060 bytes, CRC32=7d3706a3)
- `figures/sensitivity_renewable_level.png` (179982 bytes, CRC32=af6da835)
- `figures/data/fig_1_gpu_utilization.csv` (2914 bytes, CRC32=a60fec27)
- `figures/data/fig_2_storage_soc.csv` (100204 bytes, CRC32=1d119c9c)
- `figures/data/sensitivity_electricity_price.csv` (201 bytes, CRC32=d3393991)
- `figures/data/sensitivity_renewable_level.csv` (200 bytes, CRC32=1e63549c)
- `figures/figure_manifest.json` (1771 bytes, CRC32=4e9b6e7a)
