import argparse
import ast
import hashlib
import json
import re
import sys
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def semantic_python(path):
    return ast.dump(ast.parse(Path(path).read_text(encoding="utf-8")), include_attributes=False)


def data_directory(root):
    for candidate in (root / "data", root / "output" / "data"):
        if candidate.is_dir():
            return candidate
    raise AssertionError(f"missing data directory below {root}")


def active_versions(config_path):
    text = config_path.read_text(encoding="utf-8")
    block = text.split("active_versions:", 1)[1]
    values = {}
    for line in block.splitlines():
        match = re.match(r"^  ([a-z]+):\s*(\d+)\s*$", line)
        if match:
            values[match.group(1)] = int(match.group(2))
        elif line and not line.startswith(" "):
            break
    return values


def validate_run(root):
    data = data_directory(root)
    runtime = json.loads((data / "method_runtime.json").read_text(encoding="utf-8"))
    require(runtime.get("termination_status") == "completed", "RUN-001: run did not complete")
    require(runtime.get("incomplete") is False, "RUN-002: runtime incomplete")
    require(runtime.get("feasible") is True, "RUN-003: runtime infeasible")
    require(runtime.get("result_level") == "scenario-feasible", "RUN-004: result level drift")
    require(runtime.get("official_soc_state_count") == 21, "RUN-005: official SOC state count")
    require(runtime.get("default_wallclock_limit") is None, "RUN-006: default wallclock is not None")

    code_candidates = [root / "solution.py", root / "code" / "solution.py", root / "output" / "code" / "solution.py"]
    code = next((path for path in code_candidates if path.is_file()), None)
    require(code is not None, "RUN-007: solution.py missing from run")
    require(sha256(code) == runtime["code_sha256"], "RUN-008: runtime code hash mismatch")

    forecast = pd.read_csv(data / "q1_forecast_metrics.csv")
    prediction = pd.read_csv(data / "q1_forecast_2376_2399.csv")
    require(len(forecast) == 18 and len(prediction) == 432, "Q1-001: forecast coverage")
    require(forecast["ClosedLoopForecast"].astype(bool).all(), "Q1-002: forecast is not closed loop")
    require((~prediction["FeatureUsesTestTruth"].astype(bool)).all(), "Q1-003: test truth leakage")

    schemes = {"cost_min", "carbon_min", "renewable_max", "service_first", "balanced"}
    q2 = pd.read_csv(data / "q2_named_scheme_comparison.csv")
    require(set(q2["scheme"]) == schemes, "Q2-001: named schemes incomplete")
    require((q2["checked_candidates"] == 10000).all(), "Q2-002: per-scheme budget mismatch")
    require((q2["task_coverage_rate"] >= 0.02).all(), "Q2-003: per-scheme coverage below 2 percent")
    q2_summary = pd.read_csv(data / "q2_search_summary.csv").iloc[0]
    require(float(q2_summary["task_coverage_rate"]) >= 0.10, "Q2-004: combined coverage below 10 percent")
    require(q2["full_task_audit_passed"].astype(bool).all(), "Q2-005: full audit failed")
    hashes = {}
    for scheme in schemes:
        audit = pd.read_csv(data / f"q2_constraint_audit_{scheme}.csv")
        require(audit["constraint_satisfied"].astype(bool).all(), f"Q2-006: {scheme} audit")
        schedule_hash = str(q2.loc[q2["scheme"].eq(scheme), "schedule_sha256"].iloc[0])
        duplicate_of = q2.loc[q2["scheme"].eq(scheme), "duplicate_of"].iloc[0]
        if schedule_hash in hashes:
            require(str(duplicate_of) == hashes[schedule_hash], f"Q2-007: {scheme} duplicate unlabelled")
        else:
            hashes[schedule_hash] = scheme
    stability = pd.read_csv(data / "q2_budget_stability.csv")
    require(set(stability["budget_per_scheme"]) == {5000, 10000}, "Q2-008: stability budgets")
    require(set(stability["scheme"]) == schemes and len(stability) == 10, "Q2-009: stability rows")
    energy = pd.read_csv(data / "q2_hourly_energy.csv", nrows=1)
    explicit = {"BaselineGridPurchase_MW", "OptimizedGridPurchase_MW", "BaselineGridSell_MW", "OptimizedGridSell_MW"}
    require(explicit <= set(energy.columns), "Q2-010: explicit energy schema missing")
    require(not ({"GridPurchase_MW", "GridPurchaseOpt_MW", "GridSell_MW", "GridSellOpt_MW"} & set(energy.columns)), "Q2-011: ambiguous energy schema remains")

    q3 = pd.read_csv(data / "q3_search_trace.csv")
    require(len(q3) == 7 and "no_action" in set(q3["policy"]), "Q3-001: policy set")
    q3_summary = pd.read_csv(data / "q3_search_summary.csv").iloc[0]
    require(q3_summary["decision_method"] == "weighted_minmax_ideal_point_distance", "Q3-002: decision method")
    selected = q3_summary["selected_policy"]
    selected_row = q3.loc[q3["policy"].eq(selected)].iloc[0]
    require(bool(selected_row["nondominated"]) and bool(selected_row["decision_eligible"]), "Q3-003: selected plan eligibility")
    eligible = q3.loc[q3["decision_eligible"].astype(bool)]
    require(np.isclose(float(selected_row["ideal_distance"]), float(eligible["ideal_distance"].min())), "Q3-004: selected distance not minimum")
    grid = pd.read_csv(data / "q3_soc_grid_sensitivity.csv")
    require(set(grid["state_count"]) == {15, 21, 31}, "Q3-005: grid sensitivity counts")
    require(int(grid["official_configuration"].astype(bool).sum()) == 1, "Q3-006: official grid label")
    require((grid["max_constraint_residual"] <= 1e-6).all(), "Q3-007: grid sensitivity residual")

    for name in ("constraint_audit.csv", "q3_constraint_audit.csv", "q4_constraint_audit.csv"):
        audit = pd.read_csv(data / name)
        numeric = audit.select_dtypes(include=[np.number]).drop(columns=["constraint_satisfied"], errors="ignore")
        require(float(np.maximum(numeric.to_numpy(float), 0.0).max()) <= 1e-6, f"AUDIT-001: {name}")

    q4 = pd.read_csv(data / "q4_scenario_comparison.csv")
    trace = pd.read_csv(data / "q4_alternation_trace.csv")
    require(len(q4) == 17, "Q4-001: scenario count")
    require(q4["state_count"].eq(21).all(), "Q4-002: scenario state count mismatch")
    require(q4["constraints_satisfied"].eq(1).all(), "Q4-003: scenario constraints")
    require((q4["alternation_rounds"] >= 2).all(), "Q4-004: alternation rounds")
    require(trace["neighborhood_rebuilt_from_previous_storage"].astype(bool).all(), "Q4-005: dynamic neighborhood")
    consistency = json.loads((data / "q4_baseline_consistency.json").read_text(encoding="utf-8"))
    require(consistency.get("status") == "pass" and consistency.get("state_count") == 21, "Q4-006: baseline consistency evidence")
    require(np.allclose(consistency["joint_metrics"], consistency["scenario_baseline_metrics"], rtol=1e-12, atol=1e-8), "Q4-007: dual baseline remains")
    results = {item["name"]: item["value"] for item in json.loads((data / "results.json").read_text(encoding="utf-8"))}
    baseline = q4.iloc[0]
    require(np.isclose(float(results["q4_联合基准运行成本"]), float(baseline["cost_CNY"])), "Q4-008: results cost source")
    require(np.isclose(float(results["q4_联合基准碳排放"]), float(baseline["carbon_tCO2"])), "Q4-009: results carbon source")
    require(int(results["q4_统一SOC状态数"]) == 21, "Q4-010: results state count")

    report = {
        "status": "pass", "root": str(root),
        "run_id": runtime["run_id"], "code_sha256": runtime["code_sha256"],
        "results_sha256": sha256(data / "results.json"),
        "q2_min_scheme_coverage": float(q2["task_coverage_rate"].min()),
        "q2_combined_coverage": float(q2_summary["task_coverage_rate"]),
        "q3_selected_policy": selected,
        "q4_state_count": int(q4["state_count"].iloc[0]),
        "q4_scenarios": len(q4),
    }
    return report


def validate_active(case_root):
    versions = active_versions(case_root / ".mmw" / "config.yaml")
    required = {"model", "code", "solve", "paper", "review"}
    require(required <= versions.keys(), "EXPORT-001: active versions missing")
    chain = f"model v{versions['model']} / code v{versions['code']} / solve v{versions['solve']} / paper v{versions['paper']} / review v{versions['review']}"
    require(chain in (case_root / "README.md").read_text(encoding="utf-8"), "EXPORT-002: README chain mismatch")
    require(chain in (case_root / "output" / "CURRENT_DELIVERY.md").read_text(encoding="utf-8"), "EXPORT-003: CURRENT_DELIVERY chain mismatch")
    active_code = case_root / ".mmw" / "checkpoints" / "05_code" / f"v{versions['code']}" / "solution.py"
    root_code = case_root / "output" / "code" / "solution.py"
    require(semantic_python(active_code) == semantic_python(root_code), "EXPORT-004: root solution semantics mismatch")
    active_solve = case_root / ".mmw" / "checkpoints" / "06_solve" / f"v{versions['solve']}"
    for name in ("results.json", "sensitivity.json", "method_runtime.json"):
        require(sha256(active_solve / name) == sha256(case_root / "output" / "data" / name), f"EXPORT-005: {name} mismatch")
    active_paper = case_root / ".mmw" / "checkpoints" / "07_paper" / f"v{versions['paper']}" / "paper.pdf"
    require(sha256(active_paper) == sha256(case_root / "output" / "paper.pdf"), "EXPORT-006: paper mismatch")
    stage_paths = {
        "model": "04_model", "code": "05_code", "solve": "06_solve",
        "paper": "07_paper", "review": "08_review",
    }
    for stage, directory in stage_paths.items():
        status_path = case_root / ".mmw" / "checkpoints" / directory / f"v{versions[stage]}" / "status.json"
        status = json.loads(status_path.read_text(encoding="utf-8"))
        require(status.get("status") == "approved", f"EXPORT-007: active {stage} not approved")
    submission = case_root / "output" / "submission.zip"
    with zipfile.ZipFile(submission) as archive:
        names = set(archive.namelist())
        require({"paper.pdf", "code/solution.py", "data/results.json", "data/sensitivity.json", "data/method_runtime.json"} <= names, "EXPORT-008: submission members")
        require(hashlib.sha256(archive.read("paper.pdf")).hexdigest() == sha256(active_paper), "EXPORT-009: zip paper mismatch")
        require(ast.dump(ast.parse(archive.read("code/solution.py").decode("utf-8")), include_attributes=False) == semantic_python(active_code), "EXPORT-010: zip code semantics mismatch")
        require(hashlib.sha256(archive.read("data/results.json")).hexdigest() == sha256(active_solve / "results.json"), "EXPORT-011: zip results mismatch")
    reproducibility = case_root / "output" / "reproducibility.zip"
    with zipfile.ZipFile(reproducibility) as archive:
        names = set(archive.namelist())
        required_repro = {"solution.py", "validate_results.py", "requirements.txt", "README.md", "RUNME.md", "MANIFEST.sha256",
                          "data/results.json", "data/sensitivity.json", "data/method_runtime.json",
                          "data/q2_search_trace.csv", "data/q3_all_policy_trajectories.csv",
                          "data/q4_scenario_comparison.csv", "data/q4_alternation_trace.csv",
                          "data/figure_manifest.json", "evidence/benchmark.json", "evidence/method_consistency.json"}
        require(required_repro <= names, "EXPORT-012: reproducibility members")
        require(hashlib.sha256(archive.read("solution.py")).hexdigest() == sha256(active_code), "EXPORT-013: reproducibility code mismatch")
        require(hashlib.sha256(archive.read("data/results.json")).hexdigest() == sha256(active_solve / "results.json"), "EXPORT-014: reproducibility results mismatch")
        for name in names:
            parts = Path(name).parts
            require(not Path(name).is_absolute() and ".." not in parts, f"EXPORT-015: unsafe ZIP member {name}")
            lower = {part.lower() for part in parts}
            require(not ({".env", "__pycache__", ".pytest_cache", "cookie", "cookies"} & lower), f"EXPORT-016: forbidden ZIP member {name}")
            require(not name.lower().endswith((".pyc", ".pyo")), f"EXPORT-017: cache ZIP member {name}")
    benchmark = json.loads((case_root / "output" / "benchmark.json").read_text(encoding="utf-8"))
    require(benchmark.get("version") == versions["solve"] and benchmark.get("review_version") == versions["review"], "EXPORT-018: benchmark version drift")
    require(benchmark.get("certification", {}).get("level") == "scenario-feasible", "EXPORT-019: certification drift")
    return {"active_chain": chain, "submission_sha256": sha256(submission), "reproducibility_sha256": sha256(reproducibility)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("root", nargs="?", default=".")
    parser.add_argument("--run-only", action="store_true")
    args = parser.parse_args()
    root = Path(args.root).resolve()
    report = validate_run(root)
    if not args.run_only:
        report.update(validate_active(root))
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(json.dumps({"status": "fail", "error": str(exc)}, ensure_ascii=False, indent=2))
        raise
