from pathlib import Path
import ast
import collections
import textwrap


PATH = Path(__file__).with_name("solution.py")


def replace_func(source, name, replacement):
    tree = ast.parse(source)
    nodes = [
        node for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name == name
    ]
    if len(nodes) != 1:
        raise RuntimeError((name, len(nodes)))
    node = nodes[0]
    lines = source.splitlines(keepends=True)
    lines[node.lineno - 1:node.end_lineno] = [
        textwrap.dedent(replacement).strip() + "\n\n"
    ]
    return "".join(lines)


source = PATH.read_text(encoding="utf-8")

source = source.replace(
    '''    for row in tasks.itertuples():
        if time.monotonic() >= SEARCH_LIMIT:
            elapsed = time.monotonic() - PROGRAM_START
            raise RuntimeError(
                f"CON-Q1-7: actual={elapsed:.6f}, "
                f"threshold={MAX_RUNTIME_SECONDS}, external_timeout incomplete"
            )
''',
    '''    for task_no, row in enumerate(tasks.itertuples()):
        check_deadline("q1.greedy_schedule", task_no)
''',
    1,
)

storage_search = '''
def storage_local_search(d, facility_override=None, max_candidates=12000):
    global Q3_POLICY_RESULTS, Q3_TERMINAL_SENSITIVITY
    policy_names = ["no_action", "cost_min", "carbon_min", "renewable_max", "peak_min", "ramp_min", "balanced"]
    flows = {"no_action": _no_action_policy(d, facility_override=facility_override)}
    for index, name in enumerate(policy_names[1:]):
        check_deadline("q3.policy", index)
        flows[name] = _storage_dp_policy(d, name, facility_override=facility_override, state_count=SOC_STATE_COUNT)
    rows, seen_hashes = [], {}
    storage = d["storage"].set_index("Region")
    for name in policy_names:
        flow = flows[name]
        audit_storage_policy(d, flow, "CON-Q3-1")
        cost, carbon, renewable, peak, ramp = metrics_energy(flow)
        trajectory_hash = _trajectory_hash(flow)
        duplicate_of = seen_hashes.get(trajectory_hash)
        if duplicate_of is None:
            seen_hashes[trajectory_hash] = name
        internal_throughput = float(sum(
            flow.loc[flow["Region"].eq(region), "Charge_MW"].sum() * float(storage.loc[region, "ChargeEfficiency"])
            + flow.loc[flow["Region"].eq(region), "Discharge_MW"].sum() / float(storage.loc[region, "DischargeEfficiency"])
            for region in REGIONS
        ))
        equivalent_cycles = float(sum(
            (
                flow.loc[flow["Region"].eq(region), "Charge_MW"].sum() * float(storage.loc[region, "ChargeEfficiency"])
                + flow.loc[flow["Region"].eq(region), "Discharge_MW"].sum() / float(storage.loc[region, "DischargeEfficiency"])
            ) / (2.0 * storage_soc_max(storage.loc[region]))
            for region in REGIONS
        ))
        rows.append({
            "policy": name, "state_count": SOC_STATE_COUNT,
            "cost_CNY": cost, "carbon_tCO2": carbon,
            "renewable_utilization": renewable, "peak_MW": peak, "ramp_MW": ramp,
            "charge_MWh": float(flow["Charge_MW"].sum()),
            "discharge_MWh": float(flow["Discharge_MW"].sum()),
            "internal_throughput_MWh": internal_throughput,
            "equivalent_full_cycles_sum": equivalent_cycles,
            "trajectory_sha256": trajectory_hash, "duplicate_of": duplicate_of,
        })
    nondominated = _pareto_nondominated(rows)
    for row, flag in zip(rows, nondominated):
        row["nondominated"] = bool(flag)
    metric_names = ["cost_CNY", "carbon_tCO2", "renewable_utilization", "peak_MW", "ramp_MW"]
    weights = np.asarray([0.30, 0.25, 0.15, 0.15, 0.15], dtype=float)
    eligible = [
        index for index, row in enumerate(rows)
        if row["nondominated"] and row["duplicate_of"] is None
    ]
    matrix = np.asarray([
        [rows[index]["cost_CNY"], rows[index]["carbon_tCO2"],
         -rows[index]["renewable_utilization"], rows[index]["peak_MW"],
         rows[index]["ramp_MW"]]
        for index in eligible
    ], dtype=float)
    ideal, worst = matrix.min(axis=0), matrix.max(axis=0)
    safe_span = np.where(worst - ideal > 1e-12, worst - ideal, 1.0)
    normalized = (matrix - ideal) / safe_span
    distances = np.sqrt(np.sum(weights * normalized ** 2, axis=1))
    for row in rows:
        row.update({
            "normalized_cost": np.nan, "normalized_carbon": np.nan,
            "normalized_renewable_loss": np.nan, "normalized_peak": np.nan,
            "normalized_ramp": np.nan, "ideal_distance": np.nan,
            "decision_eligible": False,
        })
    for local_index, row_index in enumerate(eligible):
        rows[row_index].update({
            "normalized_cost": normalized[local_index, 0],
            "normalized_carbon": normalized[local_index, 1],
            "normalized_renewable_loss": normalized[local_index, 2],
            "normalized_peak": normalized[local_index, 3],
            "normalized_ramp": normalized[local_index, 4],
            "ideal_distance": distances[local_index],
            "decision_eligible": True,
        })
    chosen_local = min(
        range(len(eligible)),
        key=lambda index: (float(distances[index]), rows[eligible[index]]["policy"]),
    )
    selected_name = rows[eligible[chosen_local]]["policy"]
    selected = flows[selected_name]
    base = rows[0]
    final = next(row for row in rows if row["policy"] == selected_name)
    trace = pd.DataFrame(rows)
    summary = {
        "status": "pareto_selected", "checked_candidates": len(rows),
        "unique_trajectories": len(seen_hashes),
        "accepted_improvements": int(selected_name != "no_action"),
        "selected_policy": selected_name, "state_count": SOC_STATE_COUNT,
        "decision_method": "weighted_minmax_ideal_point_distance",
        "decision_weights": json.dumps(dict(zip(metric_names, weights)), ensure_ascii=False, sort_keys=True),
        "decision_ideal_point": json.dumps(ideal.tolist()),
        "selection_reason": f"在全部不重复非支配策略中理想点加权距离最小({float(distances[chosen_local]):.12g})",
        "selected_ideal_distance": float(distances[chosen_local]),
        "baseline_cost_CNY": base["cost_CNY"], "final_cost_CNY": final["cost_CNY"],
        "baseline_carbon_tCO2": base["carbon_tCO2"],
        "final_carbon_tCO2": final["carbon_tCO2"],
        "baseline_peak_MW": base["peak_MW"], "final_peak_MW": final["peak_MW"],
        "baseline_ramp_MW": base["ramp_MW"], "final_ramp_MW": final["ramp_MW"],
        "charge_MWh": final["charge_MWh"], "discharge_MWh": final["discharge_MWh"],
        "internal_throughput_MWh": final["internal_throughput_MWh"],
        "equivalent_full_cycles_sum": final["equivalent_full_cycles_sum"],
        "termination_status": "candidate_space_exhausted",
    }
    Q3_POLICY_RESULTS = {name: flows[name] for name in policy_names}
    if facility_override is None:
        relaxed = _storage_dp_policy(
            d, "cost_min", facility_override=None,
            terminal_mode="free", state_count=SOC_STATE_COUNT,
        )
        Q3_TERMINAL_SENSITIVITY = {
            "interpretation": "题面未给出退化成本或循环寿命参数；本项仅为敏感性，不是官方参数",
            "initial_equal": next(row for row in rows if row["policy"] == "cost_min"),
            "terminal_free": {
                "metrics": metrics_energy(relaxed),
                "terminal_soc": relaxed.groupby("Region").tail(1)[["Region", "SOC_MWh"]].to_dict("records"),
            },
        }
    return selected, summary, trace


def run_soc_grid_sensitivity(d, selected_policy):
    rows = []
    storage = d["storage"].set_index("Region")
    for state_count in SOC_SENSITIVITY_STATE_COUNTS:
        check_deadline("q3.grid_sensitivity", state_count)
        started = time.monotonic()
        flow = _storage_dp_policy(d, selected_policy, state_count=state_count)
        audit = audit_storage_policy(d, flow, "CON-Q3-1")
        cost, carbon, renewable, peak, ramp = metrics_energy(flow)
        throughput = float(sum(
            flow.loc[flow["Region"].eq(region), "Charge_MW"].sum() * float(storage.loc[region, "ChargeEfficiency"])
            + flow.loc[flow["Region"].eq(region), "Discharge_MW"].sum() / float(storage.loc[region, "DischargeEfficiency"])
            for region in REGIONS
        ))
        cycles = float(sum(
            (
                flow.loc[flow["Region"].eq(region), "Charge_MW"].sum() * float(storage.loc[region, "ChargeEfficiency"])
                + flow.loc[flow["Region"].eq(region), "Discharge_MW"].sum() / float(storage.loc[region, "DischargeEfficiency"])
            ) / (2.0 * storage_soc_max(storage.loc[region]))
            for region in REGIONS
        ))
        rows.append({
            "state_count": state_count, "selected_policy": selected_policy,
            "cost_CNY": cost, "carbon_tCO2": carbon,
            "renewable_utilization": renewable,
            "peak_grid_purchase_MW": peak, "ramp_MW": ramp,
            "runtime_seconds": time.monotonic() - started,
            "internal_throughput_MWh": throughput,
            "equivalent_full_cycles_sum": cycles,
            "max_constraint_residual": float(np.maximum(audit.drop(columns="Region").to_numpy(float), 0.0).max()),
            "official_configuration": state_count == SOC_STATE_COUNT,
            "interpretation": "理想设备情景；题面未给退化成本和循环上限",
        })
    frame = pd.DataFrame(rows)
    reference = frame.loc[frame["state_count"].eq(max(SOC_SENSITIVITY_STATE_COUNTS))].iloc[0]
    for metric in ["cost_CNY", "carbon_tCO2", "renewable_utilization", "peak_grid_purchase_MW"]:
        frame[f"{metric}_relative_error_vs_31"] = (
            frame[metric] - float(reference[metric])
        ).abs() / max(abs(float(reference[metric])), 1.0)
    return frame
'''
source = replace_func(source, "storage_local_search", storage_search)

# Deadline checks inside dynamic programming.
old = '''    for region in REGIONS:
        x = rt.loc[rt["Region"].eq(region)].sort_values("Hour").reset_index(drop=True)
'''
new = '''    for region_no, region in enumerate(REGIONS):
        check_deadline("storage.region", region_no)
        x = rt.loc[rt["Region"].eq(region)].sort_values("Hour").reset_index(drop=True)
'''
if old not in source:
    raise RuntimeError("storage region loop anchor not found")
source = source.replace(old, new, 1)
old = '''        for t, row in enumerate(x.itertuples()):
            load = float(row.FacilityLoad_MW)
'''
new = '''        for t, row in enumerate(x.itertuples()):
            if t % 24 == 0:
                check_deadline(f"storage.{region}", t)
            load = float(row.FacilityLoad_MW)
'''
if old not in source:
    raise RuntimeError("storage time loop anchor not found")
source = source.replace(old, new, 1)

# Q4 uses the same explicit state grid and storage policy as the joint baseline.
source = source.replace(
    "def run_q4_scenarios(d, task_candidates, joint_baseline):",
    "def run_q4_scenarios(d, task_candidates, joint_baseline, storage_policy):",
    1,
)
source = source.replace(
    '''    for scenario_index, (scenario_type, parameter, level, seed) in enumerate(scenario_specs):
        variant = _scenario_variant''',
    '''    for scenario_index, (scenario_type, parameter, level, seed) in enumerate(scenario_specs):
        check_deadline("q4.scenario", scenario_index)
        variant = _scenario_variant''',
    1,
)
source = source.replace(
    '''            variant, "balanced",
            facility_override=current_no_storage[["Region", "Hour", "FacilityLoad_MW"]],
            state_count=15,
''',
    '''            variant, storage_policy,
            facility_override=current_no_storage[["Region", "Hour", "FacilityLoad_MW"]],
            state_count=SOC_STATE_COUNT,
''',
    1,
)
source = source.replace(
    '''        for round_no in range(1, Q4_MAX_ROUNDS + 1):
            rounds = round_no
''',
    '''        for round_no in range(1, Q4_MAX_ROUNDS + 1):
            check_deadline(f"q4.{scenario_type}.round", round_no)
            rounds = round_no
''',
    1,
)
source = source.replace(
    '''                variant, "balanced",
                facility_override=candidate_no_storage[[
                    "Region", "Hour", "FacilityLoad_MW"
                ]],
                state_count=15,
''',
    '''                variant, storage_policy,
                facility_override=candidate_no_storage[[
                    "Region", "Hour", "FacilityLoad_MW"
                ]],
                state_count=SOC_STATE_COUNT,
''',
    1,
)
source = source.replace(
    '''            "scenario_type": scenario_type,
            "parameter": parameter,
''',
    '''            "scenario_type": scenario_type,
            "parameter": parameter,
            "state_count": SOC_STATE_COUNT,
            "storage_policy": storage_policy,
            "baseline_source": "joint_baseline_same_policy_and_state_grid",
''',
    1,
)

# Main entrypoint, structured evidence, and runtime provenance.
source = source.replace(
    '''    if time.monotonic() >= TOTAL_LIMIT:
        fail("CON-Q4-6", time.monotonic() - PROGRAM_START, MAX_RUNTIME_SECONDS, "external_timeout incomplete")
    RESULT_DIR.mkdir(parents=True, exist_ok=True)
''',
    '''    if "MMW_OUTPUT_ROOT" not in os.environ:
        raise RuntimeError("RUN-ISOLATION-001: 正式运行必须由tools/run_official.py提供隔离输出目录")
    check_deadline("main.start")
    RESULT_DIR.mkdir(parents=True, exist_ok=True)
''',
    1,
)
source = source.replace(
    '''    print(
        f"结果: 问题二有限搜索完成, 检查候选数="
''',
    '''    q2_budget_stability = run_q2_budget_stability(d, workload, q1_schedule)
    print(
        f"结果: 问题二有限搜索完成, 检查候选数="
''',
    1,
)
source = source.replace(
    '''    q3_policy_flows = {
        name: flow.copy() for name, flow in Q3_POLICY_RESULTS.items()
    }
''',
    '''    q3_policy_flows = {
        name: flow.copy() for name, flow in Q3_POLICY_RESULTS.items()
    }
    q3_soc_grid_sensitivity = run_soc_grid_sensitivity(d, q3_search["selected_policy"])
''',
    1,
)
source = source.replace(
    '''        q4_task_candidates,
        q4_flow,
    )
''',
    '''        q4_task_candidates,
        q4_flow,
        q4_search["selected_policy"],
    )
''',
    1,
)
source = source.replace(
    '''    if len(q4_scenarios) != 17:
''',
    '''    baseline_scenario = q4_scenarios.iloc[0]
    baseline_metrics = np.asarray([
        baseline_scenario["cost_CNY"], baseline_scenario["carbon_tCO2"],
        baseline_scenario["renewable_utilization"],
        baseline_scenario["peak_grid_purchase_MW"], baseline_scenario["ramp_MW"],
    ], dtype=float)
    joint_metrics = np.asarray([q4_cost, q4_carbon, q4_re, q4_peak, q4_ramp], dtype=float)
    q4_baseline_consistent = bool(np.allclose(baseline_metrics, joint_metrics, rtol=1e-12, atol=1e-8))
    if not q4_baseline_consistent:
        raise RuntimeError(f"CON-Q4-7: 21状态情景基准与联合基准不一致: scenario={baseline_metrics.tolist()}, joint={joint_metrics.tolist()}")
    if not q4_scenarios["state_count"].eq(SOC_STATE_COUNT).all():
        raise RuntimeError("CON-Q4-7: Q4情景状态数不统一")
    if len(q4_scenarios) != 17:
''',
    1,
)
source = source.replace(
    '''    if time.monotonic() >= TOTAL_LIMIT:
        fail("CON-Q4-6", time.monotonic() - PROGRAM_START, MAX_RUNTIME_SECONDS, "external_timeout incomplete")

''',
    '''    check_deadline("main.before_output")

''',
    1,
)
source = source.replace(
    'RESULT_DIR / "q4_scenario_comparison_v42.csv"',
    'RESULT_DIR / "q4_scenario_comparison.csv"',
    1,
)
source = source.replace(
    '''    q2_trace.to_csv(RESULT_DIR / "q2_search_trace.csv", index=False)
''',
    '''    q2_trace.to_csv(RESULT_DIR / "q2_search_trace.csv", index=False)
    q2_budget_stability.to_csv(RESULT_DIR / "q2_budget_stability.csv", index=False)
''',
    1,
)
source = source.replace(
    '''    q3_trace.to_csv(RESULT_DIR / "q3_search_trace.csv", index=False)
''',
    '''    q3_trace.to_csv(RESULT_DIR / "q3_search_trace.csv", index=False)
    q3_soc_grid_sensitivity.to_csv(RESULT_DIR / "q3_soc_grid_sensitivity.csv", index=False)
''',
    1,
)
source = source.replace(
    '''    with open(RESULT_DIR / "q3_terminal_soc_sensitivity.json", "w", encoding="utf-8") as f:
        json.dump(q3_terminal_sensitivity, f, ensure_ascii=False, indent=2)
''',
    '''    with open(RESULT_DIR / "q3_terminal_soc_sensitivity.json", "w", encoding="utf-8") as f:
        json.dump(q3_terminal_sensitivity, f, ensure_ascii=False, indent=2)
    with open(RESULT_DIR / "q4_baseline_consistency.json", "w", encoding="utf-8") as f:
        json.dump({
            "status": "pass", "state_count": SOC_STATE_COUNT,
            "storage_policy": q4_search["selected_policy"],
            "joint_metrics": joint_metrics.tolist(),
            "scenario_baseline_metrics": baseline_metrics.tolist(),
            "same_data_source": True,
        }, f, ensure_ascii=False, indent=2)
''',
    1,
)
source = source.replace(
    '''        "schema_version": 1,
        "algorithm_class": "heuristic",
''',
    '''        "schema_version": 2,
        "algorithm_class": "heuristic",
        **run_identity(),
        "result_level": "scenario-feasible",
        "official_soc_state_count": SOC_STATE_COUNT,
        "default_wallclock_limit": None,
        "explicit_wallclock_limit_seconds": MAX_RUNTIME_SECONDS,
''',
    1,
)
source = source.replace(
    '''            "q2": {
                "declared_candidate_limit": int(
''',
    '''            "q2": {
                "stratification": "TaskType|SourceRegion|ArrivalHour6h|GPUhQuartile|WaitQuartile",
                "minimum_per_scheme_coverage_target": 0.02,
                "minimum_combined_coverage_target": 0.10,
                "budget_stability_levels": list(Q2_STABILITY_BUDGETS),
                "declared_candidate_limit": int(
''',
    1,
)
source = source.replace(
    '''            "q3": {
                "status": q3_search["status"],
''',
    '''            "q3": {
                "status": q3_search["status"],
                "state_count": SOC_STATE_COUNT,
                "decision_method": q3_search["decision_method"],
                "selected_ideal_distance": q3_search["selected_ideal_distance"],
''',
    1,
)
source = source.replace(
    '''            "q4_baseline": {
                "status": q4_search["status"],
''',
    '''            "q4_baseline": {
                "status": q4_search["status"],
                "state_count": SOC_STATE_COUNT,
                "baseline_consistent_with_scenarios": q4_baseline_consistent,
''',
    1,
)
source = source.replace(
    '''        result_item("q2_局部搜索接受改进数", q2_search["accepted_improvements"], "个", q2_search["status"]),
''',
    '''        result_item("q2_局部搜索接受改进数", q2_search["accepted_improvements"], "个", q2_search["status"]),
        result_item("q2_五方案合计任务覆盖率", q2_search["task_coverage_rate"], "", "确定性五维分层覆盖"),
        result_item("q2_单方案最小任务覆盖率", min(value["summary"]["task_coverage_rate"] for value in Q2_SCHEME_RESULTS.values()), "", "每方案目标至少2%"),
''',
    1,
)
source = source.replace(
    '''        result_item("q4_联合基准峰值净购电功率", q4_peak, "MW", "六区域非负峰值之和"),
''',
    '''        result_item("q4_联合基准峰值净购电功率", q4_peak, "MW", "六区域非负峰值之和"),
        result_item("q4_统一SOC状态数", SOC_STATE_COUNT, "个", "联合基准与17个情景使用同一显式配置"),
''',
    1,
)
old_tail = '''if __name__ == "__main__":
    if PILOT_MODE:
        pilot(read_inputs())
    else:
        main()
'''
new_tail = '''if __name__ == "__main__":
    try:
        if PILOT_MODE:
            pilot(read_inputs())
        else:
            main()
    except ExternalTimeout as exc:
        write_timeout_evidence(exc)
        print(f"结果: termination_status=external_timeout; incomplete=true; {exc}", flush=True)
        raise SystemExit(124)
'''
if old_tail not in source:
    raise RuntimeError("main tail not found")
source = source.replace(old_tail, new_tail)

if "SEARCH_LIMIT" in source or "TOTAL_LIMIT" in source:
    raise RuntimeError("stale wall-clock identifiers remain")
source = source.replace(
    "_schedule_candidate_feasible_reference = schedule_candidate_feasible\n"
    "_build_constraint_audit_reference = build_constraint_audit\n\n\n",
    "",
    1,
)
PATH.write_text(source, encoding="utf-8")
tree = ast.parse(source)
counts = collections.Counter(
    node.name for node in tree.body if isinstance(node, ast.FunctionDef)
)
duplicates = {name: count for name, count in counts.items() if count > 1}
if duplicates:
    raise RuntimeError(f"duplicate functions remain: {duplicates}")
print(f"phase2 complete: {PATH}, functions={sum(counts.values())}")
