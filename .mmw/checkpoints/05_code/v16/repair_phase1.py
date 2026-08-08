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

# Remove all shadowed top-level functions, retaining Python's actual last definition.
tree = ast.parse(source)
groups = collections.defaultdict(list)
for node in tree.body:
    if isinstance(node, ast.FunctionDef):
        groups[node.name].append(node)
lines = source.splitlines(keepends=True)
shadowed = [node for nodes in groups.values() for node in nodes[:-1]]
for node in sorted(shadowed, key=lambda item: item.lineno, reverse=True):
    del lines[node.lineno - 1:node.end_lineno]
source = "".join(lines)

source = source.replace("import hashlib\n", "import hashlib\nimport uuid\n")
old_constants = '''DATA_DIR = Path("附件数据")
RESULT_DIR = Path("output/data")
FIGURE_DIR = Path("output/figures")
FIGURE_DATA_DIR = RESULT_DIR / "figure_data"
REGIONS = [f"Region{x}" for x in "ABCDEF"]
TASK_TYPES = ["RealTimeInference", "BatchInference", "AITraining"]
PROGRAM_START = time.monotonic()
_runtime_text = os.getenv("MMW_MAX_RUNTIME_SECONDS", "").strip()
MAX_RUNTIME_SECONDS = float(_runtime_text) if _runtime_text else None
if MAX_RUNTIME_SECONDS is not None and MAX_RUNTIME_SECONDS <= 0:
    raise ValueError("MMW_MAX_RUNTIME_SECONDS 必须为正数")
SEARCH_LIMIT = (
    PROGRAM_START + MAX_RUNTIME_SECONDS
    if MAX_RUNTIME_SECONDS is not None else float("inf")
)
TOTAL_LIMIT = SEARCH_LIMIT
SEED = 2026
TOL = 1e-6
Q4_MOVE_LIMIT = 12000
Q2_MOVE_LIMIT = 50000
Q2_TASK_POOL_SIZE = 50000
Q4_TASK_NEIGHBOR_LIMIT = 600
Q2_SCHEME_BUDGET = 10000
Q4_MAX_ROUNDS = 8
Q4_NO_IMPROVEMENT_ROUNDS = 2
Q4_IMPROVEMENT_TOL = 1e-8
PILOT_MODE = os.getenv("MMW_PILOT", "").strip() == "1"
'''
new_constants = '''DATA_DIR = Path(os.getenv("MMW_DATA_DIR", "附件数据"))
OUTPUT_ROOT = Path(os.getenv("MMW_OUTPUT_ROOT", "output"))
RESULT_DIR = OUTPUT_ROOT / "data"
FIGURE_DIR = OUTPUT_ROOT / "figures"
FIGURE_DATA_DIR = RESULT_DIR / "figure_data"
REGIONS = [f"Region{x}" for x in "ABCDEF"]
TASK_TYPES = ["RealTimeInference", "BatchInference", "AITraining"]
PROGRAM_START = time.monotonic()
_runtime_text = os.getenv("MMW_MAX_RUNTIME_SECONDS", "").strip()
try:
    MAX_RUNTIME_SECONDS = float(_runtime_text) if _runtime_text else None
except ValueError as exc:
    raise ValueError("RUNTIME-001: MMW_MAX_RUNTIME_SECONDS 必须是正数") from exc
if MAX_RUNTIME_SECONDS is not None and (
    not np.isfinite(MAX_RUNTIME_SECONDS) or MAX_RUNTIME_SECONDS <= 0
):
    raise ValueError("RUNTIME-001: MMW_MAX_RUNTIME_SECONDS 必须是有限正数")
DEADLINE = PROGRAM_START + MAX_RUNTIME_SECONDS if MAX_RUNTIME_SECONDS is not None else None
SEED = 2026
TOL = 1e-6
SOC_STATE_COUNT = 21
SOC_SENSITIVITY_STATE_COUNTS = (15, 21, 31)
Q4_MOVE_LIMIT = 12000
Q2_MOVE_LIMIT = 50000
Q2_TASK_POOL_SIZE = 50000
Q4_TASK_NEIGHBOR_LIMIT = 600
Q2_SCHEME_BUDGET = 10000
Q2_STABILITY_BUDGETS = (5000, 10000)
Q2_MAX_CANDIDATES_PER_TASK = 8
Q4_MAX_ROUNDS = 8
Q4_NO_IMPROVEMENT_ROUNDS = 2
Q4_IMPROVEMENT_TOL = 1e-8
PILOT_MODE = os.getenv("MMW_PILOT", "").strip() == "1"
RUN_ID = os.getenv("MMW_RUN_ID", "").strip() or uuid.uuid4().hex
'''
if old_constants not in source:
    raise RuntimeError("constants block not found")
source = source.replace(old_constants, new_constants)

runtime_helpers = '''
class ExternalTimeout(RuntimeError):
    pass


def check_deadline(loop_id, iteration=0):
    if DEADLINE is not None and time.monotonic() >= DEADLINE:
        elapsed = time.monotonic() - PROGRAM_START
        raise ExternalTimeout(
            f"RUNTIME-002: external_timeout in {loop_id} at iteration={iteration}; "
            f"elapsed_seconds={elapsed:.6f}"
        )


def sha256_file(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def run_identity():
    input_hashes = {
        key: sha256_file(path) for key, path in FILES.items() if path.exists()
    }
    aggregate = hashlib.sha256(
        json.dumps(input_hashes, sort_keys=True).encode("utf-8")
    ).hexdigest()
    return {
        "run_id": RUN_ID,
        "code_sha256": sha256_file(Path(__file__).resolve()),
        "input_sha256": input_hashes,
        "input_set_sha256": aggregate,
    }


def write_timeout_evidence(exc):
    RESULT_DIR.mkdir(parents=True, exist_ok=True)
    evidence = {
        "schema_version": 2,
        "algorithm_class": "heuristic",
        "termination_status": "external_timeout",
        "incomplete": True,
        "feasible": False,
        "result_level": "unverified",
        "deadline_seconds": MAX_RUNTIME_SECONDS,
        "elapsed_seconds": time.monotonic() - PROGRAM_START,
        "failure": str(exc),
        **run_identity(),
    }
    with (RESULT_DIR / "method_runtime.json").open("w", encoding="utf-8") as handle:
        json.dump(evidence, handle, ensure_ascii=False, indent=2)
'''
source = source.replace(
    "\ndef fail(constraint_id, actual, threshold, message):\n",
    "\n" + textwrap.dedent(runtime_helpers).strip() +
    "\n\n\ndef fail(constraint_id, actual, threshold, message):\n",
    1,
)

validate_inputs = '''
def validate_inputs(d):
    required = {
        "gpu": {"Region", "Available_GPU", "Max_IT_Power_MW", "PUE", "Max_Facility_Power_MW"},
        "latency": {"FromRegion", "ToRegion", "NetworkLatency_ms"},
        "power": {"TaskType", "GPU_Power_MW_per_EquivalentGPU"},
        "region": {"Hour", "Region", "ElectricityPrice_CNY_per_MWh", "SellPrice_CNY_per_MWh", "CarbonIntensity_tCO2_per_MWh", "AvailableRenewable_MW", "NonAI_IT_Load_MW"},
        "storage": {"Region", "StorageCapacity_MWh", "MinSOC_MWh", "InitialSOC_MWh", "MaxChargePower_MW", "MaxDischargePower_MW", "ChargeEfficiency", "DischargeEfficiency", "SellLimit_MW", "MaxGridImport_MW", "MaxGridExport_MW"},
        "workload": {"TaskID", "TaskType", "ArrivalHour", "GPU_Demand", "EstimatedDuration_min", "SourceRegion", "MaxLatency_ms", "LatestFinishHour", "EarliestStartHour"},
    }
    for key, columns in required.items():
        missing = sorted(columns - set(d[key].columns))
        if missing:
            raise RuntimeError(f"INPUT-001: {key} 缺少必需列 {missing}")
        if d[key].isna().any().any():
            locations = np.argwhere(d[key].isna().to_numpy())[:5].tolist()
            raise RuntimeError(f"INPUT-002: {key} 存在静默NaN, locations={locations}")

    gpu, storage, rt = d["gpu"], d["storage"], d["region"]
    workload, latency, power = d["workload"], d["latency"], d["power"]
    for key, frame, columns in (
        ("gpu", gpu, ["Region"]), ("storage", storage, ["Region"]),
        ("region", rt, ["Region", "Hour"]),
        ("latency", latency, ["FromRegion", "ToRegion"]),
        ("power", power, ["TaskType"]), ("workload", workload, ["TaskID"]),
    ):
        duplicates = int(frame.duplicated(columns).sum())
        if duplicates:
            raise RuntimeError(f"INPUT-003: {key} 重复键 {columns}, count={duplicates}")
    if set(gpu["Region"]) != set(REGIONS) or set(storage["Region"]) != set(REGIONS):
        raise RuntimeError("INPUT-004: GPU或储能区域集合不完整")
    if set(workload["TaskType"]) - set(TASK_TYPES):
        raise RuntimeError(f"INPUT-005: 非法TaskType={sorted(set(workload['TaskType']) - set(TASK_TYPES))}")
    if set(workload["SourceRegion"]) - set(REGIONS):
        raise RuntimeError(f"INPUT-006: 非法SourceRegion={sorted(set(workload['SourceRegion']) - set(REGIONS))}")

    task_numeric = ["TaskID", "ArrivalHour", "GPU_Demand", "EstimatedDuration_min", "MaxLatency_ms", "LatestFinishHour", "EarliestStartHour"]
    numeric = workload[task_numeric].apply(pd.to_numeric, errors="coerce")
    if not np.isfinite(numeric.to_numpy(float)).all():
        raise RuntimeError("INPUT-007: 任务数值列存在非有限值")
    if (numeric[["GPU_Demand", "EstimatedDuration_min"]] <= 0).any().any():
        raise RuntimeError("INPUT-008: GPU_Demand和持续时间必须为正")
    duration_h = numeric["EstimatedDuration_min"] / 60.0
    latest_start = np.minimum(numeric["LatestFinishHour"], 2406.0) - duration_h
    if (numeric["ArrivalHour"] > latest_start + TOL).any():
        bad = workload.loc[numeric["ArrivalHour"] > latest_start + TOL, "TaskID"].head().tolist()
        raise RuntimeError(f"INPUT-009: 到达晚于可行最迟开始, TaskID={bad}")
    if (numeric["EarliestStartHour"] < numeric["ArrivalHour"] - TOL).any() or (numeric["EarliestStartHour"] > latest_start + TOL).any():
        raise RuntimeError("INPUT-010: EarliestStartHour不在可行时间窗")
    if (numeric["ArrivalHour"] < 0).any() or (numeric["ArrivalHour"] > 2399).any() or (numeric["LatestFinishHour"] < 0).any() or (numeric["LatestFinishHour"] > 2406).any():
        raise RuntimeError("INPUT-011: 任务时刻超出0..2406允许范围")

    expected_pairs = {(left, right) for left in REGIONS for right in REGIONS}
    actual_pairs = set(map(tuple, latency[["FromRegion", "ToRegion"]].itertuples(index=False, name=None)))
    if actual_pairs != expected_pairs:
        raise RuntimeError(f"INPUT-012: 延迟矩阵有向组合不完整, missing={sorted(expected_pairs - actual_pairs)}, extra={sorted(actual_pairs - expected_pairs)}")
    latency_values = pd.to_numeric(latency["NetworkLatency_ms"], errors="coerce").to_numpy(float)
    if not np.isfinite(latency_values).all() or (latency_values < 0).any():
        raise RuntimeError("INPUT-013: 延迟矩阵存在非有限值或负值")
    if set(power["TaskType"]) != set(TASK_TYPES):
        raise RuntimeError("INPUT-014: 功耗映射未覆盖全部任务类型")
    power_values = pd.to_numeric(power["GPU_Power_MW_per_EquivalentGPU"], errors="coerce").to_numpy(float)
    if not np.isfinite(power_values).all() or (power_values <= 0).any():
        raise RuntimeError("INPUT-015: 功耗映射存在非有限值或非正值")

    nonnegative = {
        "gpu": ["Available_GPU", "Max_IT_Power_MW", "Max_Facility_Power_MW"],
        "region": ["Hour", "ElectricityPrice_CNY_per_MWh", "SellPrice_CNY_per_MWh", "CarbonIntensity_tCO2_per_MWh", "AvailableRenewable_MW", "NonAI_IT_Load_MW"],
        "storage": ["StorageCapacity_MWh", "MinSOC_MWh", "InitialSOC_MWh", "MaxChargePower_MW", "MaxDischargePower_MW", "SellLimit_MW", "MaxGridImport_MW", "MaxGridExport_MW"],
    }
    for key, columns in nonnegative.items():
        values = d[key][columns].apply(pd.to_numeric, errors="coerce").to_numpy(float)
        if not np.isfinite(values).all() or (values < 0).any():
            raise RuntimeError(f"INPUT-016: {key} 存在非有限值或非法负值")

    gpu_index, storage_index = gpu.set_index("Region"), storage.set_index("Region")
    for region in REGIONS:
        grow, srow = gpu_index.loc[region], storage_index.loc[region]
        if float(grow["PUE"]) < 1:
            fail("INPUT-017", grow["PUE"], 1, region)
        eta_c, eta_d = float(srow["ChargeEfficiency"]), float(srow["DischargeEfficiency"])
        if not (0 < eta_c <= 1 and 0 < eta_d <= 1):
            raise RuntimeError(f"INPUT-018: {region} 储能效率不在(0,1]")
        values = [float(srow["MinSOC_MWh"]), float(srow["InitialSOC_MWh"]), storage_soc_max(srow), float(srow["StorageCapacity_MWh"])]
        if not (0 <= values[0] <= values[1] <= values[2] <= values[3]):
            raise RuntimeError(f"INPUT-019: {region} SOC边界顺序非法 {values}")
        q2_grid_limit(d, region, "MaxGridImport_MW")
        q2_grid_limit(d, region, "MaxGridExport_MW")
    required_hours = set(range(2407))
    if len(rt) != len(REGIONS) * 2407:
        fail("INPUT-020", len(rt), len(REGIONS) * 2407, "逐时数据行数错误")
    for region in REGIONS:
        hours = set(pd.to_numeric(rt.loc[rt["Region"].eq(region), "Hour"]).astype(int))
        if hours != required_hours:
            raise RuntimeError(f"INPUT-021: {region} 小时覆盖不完整")
'''
source = replace_func(source, "validate_inputs", validate_inputs)

# Q2 energy schema has explicit baseline and optimized semantics.
source = source.replace("GridPurchaseOpt_MW", "OptimizedGridPurchase_MW")
source = source.replace("GridSellOpt_MW", "OptimizedGridSell_MW")
source = source.replace("CurtailmentOpt_MW", "OptimizedCurtailment_MW")
needle = '''def no_storage_energy(d, schedule):
    rt = d["region"].copy().sort_values(["Region", "Hour"]).reset_index(drop=True)
'''
replacement = '''def no_storage_energy(d, schedule):
    rt = d["region"].copy().sort_values(["Region", "Hour"]).reset_index(drop=True)
    rt = rt.rename(columns={
        "GridPurchase_MW": "BaselineGridPurchase_MW",
        "GridSell_MW": "BaselineGridSell_MW",
        "Curtailment_MW": "BaselineCurtailment_MW",
    })
'''
if needle not in source:
    raise RuntimeError("no_storage_energy anchor not found")
source = source.replace(needle, replacement, 1)

q2_helpers = '''
def _q2_stratified_order(workload, schedule, scheme_index):
    priority = schedule.reset_index().rename(columns={"index": "_row_index"}).copy()
    priority["_GPUh"] = priority["GPU_Demand"] * (priority["FinishHour"] - priority["StartHour"])
    priority["_arrival_bin"] = (pd.to_numeric(priority["ArrivalHour"]).astype(int) % 24 // 6).astype(int)
    priority["_gpuh_bin"] = pd.qcut(priority["_GPUh"].rank(method="first"), 4, labels=False).astype(int)
    priority["_wait_bin"] = pd.qcut(priority["WaitHour"].rank(method="first"), 4, labels=False).astype(int)
    keys = ["TaskType", "SourceRegion", "_arrival_bin", "_gpuh_bin", "_wait_bin"]
    groups = []
    for key, group in priority.groupby(keys, sort=True, observed=True):
        values = group.sort_values(["TaskID", "_row_index"])["_row_index"].astype(int).tolist()
        if values:
            rotate = scheme_index % len(values)
            groups.append((tuple(str(value) for value in key), values[rotate:] + values[:rotate]))
    groups.sort(key=lambda item: item[0])
    ordered, position = [], 0
    while True:
        added = False
        for _, values in groups:
            if position < len(values):
                ordered.append(values[position])
                added = True
        if not added:
            break
        position += 1
    if ordered:
        block = int(np.ceil(len(ordered) / 5.0))
        offset = (scheme_index * block) % len(ordered)
        ordered = ordered[offset:] + ordered[:offset]
    return ordered, priority.set_index("_row_index")[keys]


def _q2_candidate_order(d, task, old, starts, scheme, scheme_index):
    region_time = d["region"].set_index(["Region", "Hour"])
    latency = d["latency"].set_index(["FromRegion", "ToRegion"])["NetworkLatency_ms"]
    candidates = []
    for start in starts:
        for region in REGIONS:
            if region == old["ExecutionRegion"] and start == int(old["StartHour"]):
                continue
            actual_latency = float(latency.loc[(task["SourceRegion"], region)])
            if actual_latency > float(task["MaxLatency_ms"]) + TOL:
                continue
            signal = region_time.loc[(region, min(2406, max(0, int(start))))]
            if scheme == "cost_min":
                key = (float(signal["ElectricityPrice_CNY_per_MWh"]), actual_latency, start, region)
            elif scheme == "carbon_min":
                key = (float(signal["CarbonIntensity_tCO2_per_MWh"]), actual_latency, start, region)
            elif scheme == "renewable_max":
                key = (-float(signal["AvailableRenewable_MW"]), actual_latency, start, region)
            elif scheme == "service_first":
                key = (start - float(task["ArrivalHour"]), actual_latency, region, start)
            else:
                key = (float(signal["ElectricityPrice_CNY_per_MWh"]) / 1000.0 + float(signal["CarbonIntensity_tCO2_per_MWh"]) - float(signal["AvailableRenewable_MW"]) / 1000.0 + actual_latency / 100.0, start, region)
            candidates.append((key, start, region, actual_latency))
    candidates.sort(key=lambda item: item[0])
    if candidates:
        rotate = scheme_index % len(candidates)
        candidates = candidates[rotate:] + candidates[:rotate]
    return candidates[:Q2_MAX_CANDIDATES_PER_TASK]
'''
source = source.replace(
    "\ndef _optimize_q2_scheme(d, workload, baseline_schedule, scheme, budget, offset):\n",
    "\n" + textwrap.dedent(q2_helpers).strip() +
    "\n\n\ndef _optimize_q2_scheme(d, workload, baseline_schedule, scheme, budget, offset):\n",
    1,
)

optimize_q2 = '''
def _optimize_q2_scheme(d, workload, baseline_schedule, scheme, budget, offset):
    scheme_index = ["cost_min", "carbon_min", "renewable_max", "service_first", "balanced"].index(scheme)
    schedule = baseline_schedule.copy().reset_index(drop=True)
    context = _q2_context(d, schedule)
    task_source = workload.set_index("TaskID")
    power = d["power"].set_index("TaskType")["GPU_Power_MW_per_EquivalentGPU"].to_dict()
    ordered, strata = _q2_stratified_order(workload, schedule, scheme_index)
    checked = accepted = 0
    visited, trace = set(), []
    for task_no, row_idx in enumerate(ordered):
        check_deadline(f"q2.{scheme}.task", task_no)
        if checked >= budget:
            break
        old = schedule.loc[row_idx].copy()
        task = task_source.loc[old["TaskID"]]
        duration = float(old["FinishHour"] - old["StartHour"])
        arrival = int(task["ArrivalHour"])
        latest_start = int(np.floor(min(float(task["LatestFinishHour"]), 2406.0) - duration + TOL))
        starts = [arrival] if task["TaskType"] == "RealTimeInference" else sorted(set([
            arrival, int(old["StartHour"]), max(arrival, int(old["StartHour"]) - 6),
            max(arrival, int(old["StartHour"]) - 1), min(latest_start, int(old["StartHour"]) + 1),
            min(latest_start, int(old["StartHour"]) + 6), latest_start,
        ]))
        candidates = _q2_candidate_order(d, task, old, starts, scheme, scheme_index)
        if not candidates:
            continue
        visited.add(int(old["TaskID"]))
        stratum = strata.loc[row_idx]
        for _, start, region, actual_latency in candidates:
            check_deadline(f"q2.{scheme}.candidate", checked)
            if checked >= budget:
                break
            checked += 1
            finish = start + duration
            task_power = float(old["GPU_Demand"]) * float(power[task["TaskType"]])
            deltas = _move_deltas(old["ExecutionRegion"], float(old["StartHour"]), float(old["FinishHour"]), region, float(start), finish, float(old["GPU_Demand"]), task_power, context)
            weight = float(old["GPU_Demand"]) * duration
            service_delta = weight * (actual_latency - float(old["NetworkLatency_ms"]) + 10.0 * (start - float(old["StartHour"])))
            delta, reason = _evaluate_incremental_move(context, deltas, service_delta)
            accepted_move, score = False, None
            old_region = str(old["ExecutionRegion"])
            if delta is not None:
                score = finite(_q2_score(scheme, delta), "q2_candidate_score")
                if score < -1e-12:
                    gpu_delta, power_delta, facility_delta = deltas
                    for key, value in gpu_delta.items():
                        context["used_gpu"][key] += value
                    for key, value in power_delta.items():
                        context["used_power"][key] += value
                    for key, value in facility_delta.items():
                        context["facility"][key] += value
                    schedule.at[row_idx, "ExecutionRegion"] = region
                    schedule.at[row_idx, "StartHour"] = start
                    schedule.at[row_idx, "FinishHour"] = finish
                    schedule.at[row_idx, "WaitHour"] = start - arrival
                    schedule.at[row_idx, "NetworkLatency_ms"] = actual_latency
                    accepted += 1
                    accepted_move, reason = True, "accepted"
                    old = schedule.loc[row_idx].copy()
            trace.append({
                "scheme": scheme, "candidate_no": checked, "TaskID": int(task.name),
                "from_region": old_region, "to_region": region, "start_hour": start,
                "status": reason, "score": score,
                "delta_cost_CNY": None if delta is None else delta["cost"],
                "delta_carbon_tCO2": None if delta is None else delta["carbon"],
                "delta_renewable_used_MWh": None if delta is None else delta["renewable_used"],
                "accepted": accepted_move,
                "stratum_task_type": str(stratum["TaskType"]),
                "stratum_source_region": str(stratum["SourceRegion"]),
                "stratum_arrival_bin": int(stratum["_arrival_bin"]),
                "stratum_gpuh_bin": int(stratum["_gpuh_bin"]),
                "stratum_wait_bin": int(stratum["_wait_bin"]),
            })
    flow, cost, carbon, renewable = no_storage_energy(d, schedule)
    feasible, used_gpu = schedule_candidate_feasible(d, workload, schedule)
    if not feasible:
        raise RuntimeError(f"CON-Q2-1: {scheme} 全量任务审计失败")
    audit = build_constraint_audit(d, workload, schedule, used_gpu)
    if not audit["constraint_satisfied"].all():
        raise RuntimeError(f"CON-Q2-1: {scheme} 全量约束残差失败")
    latency_value, service_quality, migrated = service_metrics(schedule)
    summary = {
        "scheme": scheme, "declared_candidate_limit": int(budget),
        "checked_candidates": int(checked), "unique_tasks_visited": int(len(visited)),
        "task_coverage_rate": float(len(visited) / len(schedule)),
        "accepted_improvements": int(accepted),
        "termination_status": "candidate_budget_reached" if checked >= budget else "candidate_space_exhausted",
        "full_task_audit_count": 1, "full_task_audit_passed": True,
        "cost_CNY": cost, "carbon_tCO2": carbon, "renewable_utilization": renewable,
        "network_latency_ms": latency_value, "service_quality": service_quality,
        "migration_count": migrated,
        "stratification": "TaskType|SourceRegion|ArrivalHour6h|GPUhQuartile|WaitQuartile",
        "max_candidates_per_task": Q2_MAX_CANDIDATES_PER_TASK,
        "scheme_traversal_offset": int(scheme_index * np.ceil(len(schedule) / 5.0)),
    }
    return schedule, flow, summary, pd.DataFrame(trace), audit
'''
source = replace_func(source, "_optimize_q2_scheme", optimize_q2)

q2_local_search = '''
def q2_local_search(d, workload, baseline_schedule, max_candidates=Q2_MOVE_LIMIT):
    global Q2_SCHEME_RESULTS, Q2_SCHEME_AUDITS
    _, baseline_cost, baseline_carbon, baseline_re = no_storage_energy(d, baseline_schedule)
    _, nonai_cost, nonai_carbon, _ = no_storage_energy(d, baseline_schedule.iloc[0:0].copy())
    schemes = ["cost_min", "carbon_min", "renewable_max", "service_first", "balanced"]
    per_scheme = max(1, int(max_candidates // len(schemes)))
    all_trace, Q2_SCHEME_RESULTS, Q2_SCHEME_AUDITS = [], {}, {}
    schedule_hashes = {}
    for index, scheme in enumerate(schemes):
        check_deadline("q2.scheme", index)
        schedule, flow, summary, trace, audit = _optimize_q2_scheme(d, workload, baseline_schedule, scheme, per_scheme, index)
        summary.update({
            "baseline_cost_CNY": baseline_cost, "baseline_carbon_tCO2": baseline_carbon,
            "baseline_renewable_utilization": baseline_re, "nonAI_cost_CNY": nonai_cost,
            "nonAI_carbon_tCO2": nonai_carbon,
            "AI_incremental_cost_CNY": summary["cost_CNY"] - nonai_cost,
            "AI_incremental_carbon_tCO2": summary["carbon_tCO2"] - nonai_carbon,
        })
        digest = _schedule_hash(schedule)
        summary["schedule_sha256"] = digest
        summary["duplicate_of"] = schedule_hashes.get(digest)
        schedule_hashes.setdefault(digest, scheme)
        Q2_SCHEME_RESULTS[scheme] = {"schedule": schedule, "flow": flow, "summary": summary}
        Q2_SCHEME_AUDITS[scheme] = audit
        all_trace.append(trace)
    selected = Q2_SCHEME_RESULTS["balanced"]
    summary = dict(selected["summary"])
    trace = pd.concat(all_trace, ignore_index=True)
    unique_tasks = int(trace["TaskID"].dropna().astype(int).nunique())
    summary.update({
        "declared_candidate_limit": int(max_candidates),
        "checked_candidates": int(sum(value["summary"]["checked_candidates"] for value in Q2_SCHEME_RESULTS.values())),
        "unique_tasks_visited": unique_tasks, "task_coverage_rate": float(unique_tasks / len(workload)),
        "all_schemes_accepted_improvements": int(sum(value["summary"]["accepted_improvements"] for value in Q2_SCHEME_RESULTS.values())),
        "status": "improved" if summary["accepted_improvements"] else "searched_no_improvement",
        "task_pool_size": len(workload), "baseline_latency_ms": service_metrics(baseline_schedule)[0],
        "final_latency_ms": summary["network_latency_ms"],
        "baseline_wait_h": float(baseline_schedule["WaitHour"].sum()),
        "final_wait_h": float(selected["schedule"]["WaitHour"].sum()),
        "final_cost_CNY": summary["cost_CNY"], "final_carbon_tCO2": summary["carbon_tCO2"],
    })
    return (selected["schedule"], selected["flow"], summary["cost_CNY"], summary["carbon_tCO2"], summary["renewable_utilization"], summary, trace)


def run_q2_budget_stability(d, workload, baseline_schedule):
    rows = []
    schemes = ["cost_min", "carbon_min", "renewable_max", "service_first", "balanced"]
    for budget in Q2_STABILITY_BUDGETS:
        for index, scheme in enumerate(schemes):
            check_deadline("q2.stability", budget + index)
            if budget == Q2_SCHEME_BUDGET:
                summary = dict(Q2_SCHEME_RESULTS[scheme]["summary"])
            else:
                _, _, summary, _, _ = _optimize_q2_scheme(d, workload, baseline_schedule, scheme, budget, index)
            rows.append({
                "budget_per_scheme": budget, "scheme": scheme,
                "checked_candidates": summary["checked_candidates"],
                "unique_tasks_visited": summary["unique_tasks_visited"],
                "task_coverage_rate": summary["task_coverage_rate"],
                "accepted_improvements": summary["accepted_improvements"],
                "cost_CNY": summary["cost_CNY"], "carbon_tCO2": summary["carbon_tCO2"],
                "renewable_utilization": summary["renewable_utilization"],
                "network_latency_ms": summary["network_latency_ms"],
                "service_quality": summary["service_quality"],
            })
    frame = pd.DataFrame(rows)
    high = frame.loc[frame["budget_per_scheme"].eq(max(Q2_STABILITY_BUDGETS))].set_index("scheme")
    low = frame.loc[frame["budget_per_scheme"].eq(min(Q2_STABILITY_BUDGETS))].set_index("scheme")
    for scheme in schemes:
        scale = max(abs(float(high.loc[scheme, "cost_CNY"])), 1.0)
        frame.loc[frame["scheme"].eq(scheme), "high_vs_low_cost_relative_change"] = abs(float(high.loc[scheme, "cost_CNY"]) - float(low.loc[scheme, "cost_CNY"])) / scale
    return frame
'''
source = replace_func(source, "q2_local_search", q2_local_search)

PATH.write_text(source, encoding="utf-8")
tree = ast.parse(source)
counts = collections.Counter(
    node.name for node in tree.body if isinstance(node, ast.FunctionDef)
)
duplicates = {name: count for name, count in counts.items() if count > 1}
if duplicates:
    raise RuntimeError(f"duplicate functions remain: {duplicates}")
print(f"phase1 complete: {PATH}, functions={sum(counts.values())}")
