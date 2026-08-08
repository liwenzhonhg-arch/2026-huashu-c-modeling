import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition, message):
    if not condition:
        raise AssertionError(message)


root = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path.cwd()
data = root / "output" / "data"
require(data.is_dir(), f"missing output/data: {data}")

runtime = json.loads((data / "method_runtime.json").read_text(encoding="utf-8"))
require(runtime["feasible"] is True, "runtime feasible is not true")
require(runtime.get("incomplete") is False, "runtime is incomplete")
require(runtime["termination_status"] == "completed", "run did not complete")

forecast = pd.read_csv(data / "q1_forecast_metrics.csv")
prediction = pd.read_csv(data / "q1_forecast_2376_2399.csv")
require(len(forecast) == 18, "Q1 must contain 18 series")
require(len(prediction) == 432, "Q1 must contain 18*24 predictions")
require(forecast["ClosedLoopForecast"].astype(bool).all(), "Q1 is not closed-loop")
require(
    (~prediction["FeatureUsesTestTruth"].astype(bool)).all(),
    "Q1 test truth leaked into features",
)
require((forecast["ValidationSampleCount"] == 24).all(), "Q1 validation sample count")
require((forecast["TestSampleCount"] == 24).all(), "Q1 test sample count")

q2 = pd.read_csv(data / "q2_named_scheme_comparison.csv")
required_schemes = {
    "cost_min", "carbon_min", "renewable_max", "service_first", "balanced"
}
require(set(q2["scheme"]) == required_schemes, "Q2 named schemes incomplete")
require(int(q2["checked_candidates"].sum()) == 50000, "Q2 candidate count")
require(q2["full_task_audit_passed"].astype(bool).all(), "Q2 full audit failed")
for scheme in required_schemes:
    audit = pd.read_csv(data / f"q2_constraint_audit_{scheme}.csv")
    require(audit["constraint_satisfied"].astype(bool).all(), f"Q2 {scheme} audit")

q3 = pd.read_csv(data / "q3_search_trace.csv")
require("no_action" in set(q3["policy"]), "Q3 no_action absent")
require(len(q3) == 7, "Q3 policy count must be seven")
require(q3["trajectory_sha256"].nunique() >= 2, "Q3 trajectories all identical")
selected = pd.read_csv(data / "q3_search_summary.csv").iloc[0]["selected_policy"]
selected_row = q3.loc[q3["policy"].eq(selected)].iloc[0]
require(bool(selected_row["nondominated"]), "Q3 selected policy is dominated")

for name in ("constraint_audit.csv", "q3_constraint_audit.csv", "q4_constraint_audit.csv"):
    audit = pd.read_csv(data / name)
    numeric = audit.select_dtypes(include=[np.number]).drop(
        columns=["constraint_satisfied"], errors="ignore"
    )
    require(float(np.maximum(numeric.to_numpy(float), 0.0).max()) <= 1e-6,
            f"{name} positive residual exceeds tolerance")

q4 = pd.read_csv(data / "q4_scenario_comparison_v42.csv")
trace = pd.read_csv(data / "q4_alternation_trace.csv")
require(len(q4) == 17, "Q4 scenario count")
require(set(q4.loc[q4["scenario_type"].eq("renewable_volatility"), "seed"]) ==
        {2026.0, 2027.0, 2028.0}, "Q4 random seeds")
require((q4["alternation_rounds"] >= 2).all(), "Q4 alternation rounds")
require((q4["constraints_satisfied"] == 1).all(), "Q4 constraints")
require(trace["neighborhood_rebuilt_from_previous_storage"].astype(bool).all(),
        "Q4 did not rebuild dynamic neighborhoods")
require(trace["full_task_audit_passed"].astype(bool).all(), "Q4 full task audit")
require((q4["realtime_sla_rate"] >= 1.0 - 1e-12).all(), "Q4 realtime SLA")
require((q4["on_time_rate"] >= 1.0 - 1e-12).all(), "Q4 deadline rate")

hashes = {
    name: sha256(data / name)
    for name in (
        "results.json",
        "method_runtime.json",
        "q1_forecast_metrics.csv",
        "q2_named_scheme_comparison.csv",
        "q3_search_trace.csv",
        "q4_scenario_comparison_v42.csv",
        "q4_alternation_trace.csv",
    )
}
report = {
    "status": "pass",
    "root": str(root),
    "q1_series": len(forecast),
    "q2_candidates": int(q2["checked_candidates"].sum()),
    "q2_unique_task_coverage_max": float(q2["task_coverage_rate"].max()),
    "q3_unique_trajectories": int(q3["trajectory_sha256"].nunique()),
    "q3_selected_policy": selected,
    "q4_scenarios": len(q4),
    "q4_trace_rows": len(trace),
    "hashes": hashes,
}
print(json.dumps(report, ensure_ascii=False, indent=2))
