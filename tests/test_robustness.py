import ast
import collections
import hashlib
import importlib.util
import json
from pathlib import Path

import pandas as pd


CASE = Path(__file__).resolve().parents[1]
SOLUTION = CASE / ".mmw" / "checkpoints" / "05_code" / "v16" / "solution.py"


def source_tree():
    return ast.parse(SOLUTION.read_text(encoding="utf-8"))


def function_node(name):
    return next(node for node in source_tree().body if isinstance(node, ast.FunctionDef) and node.name == name)


def test_no_duplicate_top_level_functions():
    counts = collections.Counter(
        node.name for node in source_tree().body if isinstance(node, ast.FunctionDef)
    )
    assert not {name: count for name, count in counts.items() if count > 1}


def test_default_wallclock_and_internal_checks():
    text = SOLUTION.read_text(encoding="utf-8")
    assert 'MMW_MAX_RUNTIME_SECONDS", ""' in text
    assert "SEARCH_LIMIT" not in text and "TOTAL_LIMIT" not in text
    for name in ("_optimize_q2_scheme", "_storage_dp_policy", "run_q4_scenarios"):
        calls = [
            node for node in ast.walk(function_node(name))
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
            and node.func.id == "check_deadline"
        ]
        assert calls, f"deadline check missing from {name}"


def test_single_q4_state_configuration_and_explicit_q2_schema():
    text = SOLUTION.read_text(encoding="utf-8")
    assert "SOC_STATE_COUNT = 21" in text
    assert "state_count=15" not in text
    assert "GridPurchaseOpt_MW" not in text and "GridSellOpt_MW" not in text
    assert "BaselineGridPurchase_MW" in text
    assert "OptimizedGridPurchase_MW" in text


def test_full_input_validation_and_stratified_order():
    spec = importlib.util.spec_from_file_location("case_solution_v16", SOLUTION)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.DATA_DIR = CASE / "附件数据"
    module.FILES = {
        "gpu": module.DATA_DIR / "GPU_information.xlsx",
        "latency": module.DATA_DIR / "network_latency.xlsx",
        "power": module.DATA_DIR / "power_mapping.xlsx",
        "region": module.DATA_DIR / "region_time_data.xlsx",
        "storage": module.DATA_DIR / "storage_information.xlsx",
        "workload": module.DATA_DIR / "workload_trace.xlsx",
    }
    data = module.read_inputs()
    module.validate_inputs(data)
    schedule = pd.read_csv(
        CASE / "output" / "technical-repair-v42-code15" / "data" /
        "q2_schedule_balanced.csv"
    )
    order, strata = module._q2_stratified_order(data["workload"], schedule, 0)
    assert len(order) == len(schedule) == 50000
    assert len(set(order)) == 50000
    assert set(strata.columns) == {
        "TaskType", "SourceRegion", "_arrival_bin", "_gpuh_bin", "_wait_bin"
    }


def test_q3_uniform_decision_has_no_name_shortcut():
    source = ast.get_source_segment(
        SOLUTION.read_text(encoding="utf-8"), function_node("storage_local_search")
    )
    assert 'balanced_row["nondominated"]' not in source
    assert "weighted_minmax_ideal_point_distance" in source
    assert "ideal_distance" in source


def test_current_code_has_isolated_internal_timeout_evidence():
    evidence_path = (
        CASE / "tests" / "evidence" / "timeout_method_runtime.json"
    )
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    assert evidence["termination_status"] == "external_timeout"
    assert evidence["incomplete"] is True and evidence["feasible"] is False
    assert "q1.greedy_schedule" in evidence["failure"]
    assert evidence["code_sha256"] == hashlib.sha256(SOLUTION.read_bytes()).hexdigest()
