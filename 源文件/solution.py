import sys
sys.stdout.reconfigure(encoding="utf-8")

import json
import hashlib
import uuid
import os
import time
from pathlib import Path

import numpy as np
import pandas as pd

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from cycler import cycler

plt.rcParams.update({
    # 中文与符号
    "font.sans-serif": ["SimHei", "Microsoft YaHei"],
    "axes.unicode_minus": False,
    # 尺寸与导出
    "figure.figsize": (8, 5),        # 单图标准;并排双图用 (10, 4)
    "savefig.dpi": 300,
    "savefig.bbox": "tight",
    "savefig.pad_inches": 0.05,
    # 字号层级（标题 > 轴标签 > 刻度/图例）
    "axes.titlesize": 14,
    "axes.labelsize": 12,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "legend.fontsize": 10,
    # 线条与标记
    "lines.linewidth": 1.8,
    "lines.markersize": 5,
    "axes.linewidth": 0.8,
    # 网格与边框
    "axes.grid": True,
    "grid.linestyle": "--",
    "grid.linewidth": 0.5,
    "grid.alpha": 0.35,
    "axes.spines.top": False,
    "axes.spines.right": False,
    # 统一配色循环（色盲友好，打印灰度可分辨）
    "axes.prop_cycle": cycler(color=[
        "#4C72B0", "#DD8452", "#55A868", "#C44E52",
        "#8172B3", "#937860", "#DA8BC3", "#8C8C8C"]),
    # 图例
    "legend.frameon": False,
})

from sklearn.linear_model import HuberRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error

DATA_DIR = Path(os.getenv("MMW_DATA_DIR", "附件数据"))
OUTPUT_ROOT = Path(os.getenv("MMW_OUTPUT_ROOT", "output"))
RESULT_DIR = OUTPUT_ROOT / "data"
FIGURE_DIR = OUTPUT_ROOT / "figures"
FIGURE_DATA_DIR = RESULT_DIR / "figure_data"
REGIONS = [f"Region{x}" for x in "ABCDEF"]
TASK_TYPES = ["RealTimeInference", "BatchInference", "AITraining"]
Q1_ROLLING_ORIGINS = (2184, 2208, 2232, 2256, 2280, 2304, 2328, 2352)
Q1_HUBER_GRID = tuple(
    (epsilon, alpha)
    for epsilon in (1.10, 1.35, 1.75)
    for alpha in (1e-4, 1e-3, 1e-2)
)
Q1_FORECAST_HORIZON = 24
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
Q2_MOVE_LIMIT = 120000
Q2_TASK_POOL_SIZE = 50000
Q4_TASK_NEIGHBOR_LIMIT = 600
Q2_SCHEME_BUDGET = 120000
Q2_STABILITY_BUDGETS = (10000, 20000, 40000, 50000, 80000, 120000)
Q2_MAX_CANDIDATES_PER_TASK = 3
Q2_MAX_PASSES = 6
Q2_CANDIDATE_AUDIT_PER_SCHEME_PASS = 10
Q2_DIRECT_SCHEMES = ("cost_min", "carbon_direct", "renewable_max", "service_first", "balanced")
Q2_BALANCED_WEIGHTS = {"cost": 0.25, "carbon": 0.25, "renewable_used": 0.25, "service": 0.25}
Q2_SERVICE_WAIT_FACTOR = 10.0
Q2_CARBON_REFINEMENT_BUDGET = 20000
Q2_CONVERGENCE_MAIN_RTOL = 0.001
Q2_CONVERGENCE_AUX_RTOL = 0.01  # diagnostic only; never blocks convergence
Q2_CONVERGENCE_ACCEPTED_RATE = 0.001
Q2_CONVERGENCE_INTERVALS = 2
Q2_STABILITY_THRESHOLDS = {
    "cost_CNY": 0.005,
    "carbon_tCO2": 0.05,
    "renewable_utilization": 0.005,
    "network_latency_ms": 0.05,
    "service_quality": 0.05,
    "migration_count": 0.10,
    "task_coverage_rate": 0.10,
    "accepted_improvements": 0.10,
}
Q4_STORAGE_POLICIES = ("cost_min", "balanced", "renewable_max")
Q4_DECISION_WEIGHTS = np.asarray([0.20, 0.20, 0.30, 0.15, 0.15], dtype=float)
Q4_MAX_ROUNDS = 8
Q4_NO_IMPROVEMENT_ROUNDS = 2
Q4_IMPROVEMENT_TOL = 1e-8
PILOT_MODE = os.getenv("MMW_PILOT", "").strip() == "1"
RUN_ID = os.getenv("MMW_RUN_ID", "").strip() or uuid.uuid4().hex

FILES = {
    "gpu": DATA_DIR / "GPU_information.xlsx",
    "latency": DATA_DIR / "network_latency.xlsx",
    "power": DATA_DIR / "power_mapping.xlsx",
    "region": DATA_DIR / "region_time_data.xlsx",
    "storage": DATA_DIR / "storage_information.xlsx",
    "workload": DATA_DIR / "workload_trace.xlsx",
}

REQUIRED_NAMES = {
    "q1": [
        "q1_不同区域不同任务类型的GPU需求统计结果",
        "q1_第2376至2399小时GPU需求预测结果",
        "q1_短期预测模型及测试精度指标",
        "q1_第2376至2399小时实际到达任务的执行区域与开工完成时刻方案",
        "q1_跨越第2399小时任务在第2400至2405小时内的结清方案",
        "q1_最后24小时调度甘特图",
        "q1_最后24小时各区域GPU利用率",
    ],
    "q2": [
        "q2_实际任务的执行区域与开工完成时刻调度策略",
        "q2_系统运行成本", "q2_碳排放量", "q2_网络时延指标",
        "q2_新能源利用率", "q2_第2400至2405小时末端弹性任务结清及能源结算结果",
        "q2_GPU容量_IT功率_设施功率_网络时延和完成时限约束验证结果",
    ],
    "q3": [
        "q3_各区域逐时储能充电功率", "q3_各区域逐时储能放电功率",
        "q3_各区域逐时SOC及第2406小时终端SOC",
        "q3_各区域逐时购电售电与新能源分配策略",
        "q3_储能优化前后运行成本及变化量", "q3_储能优化前后碳排放及变化量",
        "q3_储能优化前后各区域峰值净购电功率及变化量",
        "q3_储能优化前后负荷波动程度及变化量",
        "q3_SOC上下限_充放电功率_效率_购售电边界和终端状态约束验证结果",
    ],
    "q4": [
        "q4_任务迁移与开工时段联合调度策略", "q4_储能充放电与终端SOC策略",
        "q4_区域购电售电与新能源分配策略", "q4_系统运行成本",
        "q4_碳排放量", "q4_网络时延指标", "q4_服务质量指标",
        "q4_新能源利用率", "q4_各区域峰值净购电功率",
        "q4_多目标权衡关系或Pareto方案",
        "q4_不同碳约束场景下的策略与指标变化",
        "q4_不同电价机制场景下的策略与指标变化",
        "q4_不同新能源波动场景下的策略与指标变化",
        "q4_GPU容量_IT功率_设施功率_网络时延_任务完成时限_储能和购售电边界约束验证结果",
    ],
}


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


def fail(constraint_id, actual, threshold, message):
    raise RuntimeError(
        f"{constraint_id}: actual={float(actual):.12g}, "
        f"threshold={float(threshold):.12g}, {message}"
    )


def finite(value, name):
    value = float(value)
    if not np.isfinite(value):
        raise RuntimeError(f"{name}: actual=nonfinite, threshold=finite")
    return value


def read_inputs():
    for path in FILES.values():
        if not path.exists():
            print(f"读取失败: {path}")
            print(f"父目录内容: {[p.name for p in path.parent.iterdir()]}")
            raise FileNotFoundError(path)

    data = {
        "gpu": pd.read_excel(FILES["gpu"], sheet_name="GPU中心基础情况"),
        "latency": pd.read_excel(FILES["latency"], sheet_name="network_latency"),
        "power": pd.read_excel(FILES["power"], sheet_name="任务功率映射"),
        "region": pd.read_excel(FILES["region"], sheet_name="region_time_data"),
        "storage": pd.read_excel(FILES["storage"], sheet_name="storage_information"),
        "workload": pd.read_excel(FILES["workload"], sheet_name="Sheet1"),
    }
    for key, frame in data.items():
        if frame.empty:
            raise RuntimeError(f"INPUT-{key}: actual=0, threshold=>0")
    return data


def storage_soc_max(storage_row):
    """
    返回储能SOC上限。

    附件数据字典未要求独立的MaxSOC_MWh字段。若工作簿提供该字段则使用；
    否则按照储能物理边界，以StorageCapacity_MWh作为SOC上限。
    """
    if "MaxSOC_MWh" in storage_row.index:
        value = pd.to_numeric(storage_row["MaxSOC_MWh"], errors="coerce")
        if pd.notna(value):
            return finite(value, "MaxSOC_MWh")
    return finite(storage_row["StorageCapacity_MWh"], "StorageCapacity_MWh")


def grid_export_limit(region_row, storage_row):
    """
    返回当前区域的并网上网功率上限。

    storage_information中的SellLimit_MW是区域售电上限。若逐时数据还提供
    MaxGridExport_MW，则同时满足两个边界并取较小值。
    """
    sell_limit = finite(storage_row["SellLimit_MW"], "SellLimit_MW")
    if sell_limit < 0:
        fail("INPUT-SELL-LIMIT", sell_limit, 0, "售电上限不得为负")

    if "MaxGridExport_MW" in region_row.index:
        hourly_limit = pd.to_numeric(
            region_row["MaxGridExport_MW"], errors="coerce"
        )
        if pd.notna(hourly_limit):
            hourly_limit = finite(hourly_limit, "MaxGridExport_MW")
            if hourly_limit < 0:
                fail("INPUT-GRID-EXPORT-LIMIT", hourly_limit, 0, "并网上限不得为负")
            return min(sell_limit, hourly_limit)
    return sell_limit


def q2_grid_limit(data, region, field):
    """
    读取问题二适用的区域购售电硬边界。

    边界字段可能位于逐时区域表、GPU区域表或储能信息表。问题二仅读取
    MaxGridImport_MW和MaxGridExport_MW，不读取SellLimit_MW或SOC字段。
    """
    sources = [
        ("region_time_data", data["region"]),
        ("GPU_information", data["gpu"]),
        ("storage_information", data["storage"]),
    ]
    found_values = []

    for source_name, frame in sources:
        if field not in frame.columns or "Region" not in frame.columns:
            continue
        values = pd.to_numeric(
            frame.loc[frame["Region"] == region, field],
            errors="coerce",
        ).dropna()
        if values.empty:
            continue
        unique_values = np.unique(values.to_numpy(dtype=float))
        if not np.isfinite(unique_values).all():
            raise RuntimeError(
                f"CON-Q2-3: actual=nonfinite_{field}, threshold=finite, "
                f"source={source_name}, region={region}"
            )
        if np.any(unique_values < 0):
            fail(
                "CON-Q2-3",
                float(np.min(unique_values)),
                0,
                f"{field}不得为负, source={source_name}, region={region}",
            )
        if len(unique_values) != 1:
            raise RuntimeError(
                f"CON-Q2-3: actual={len(unique_values)}, threshold=1, "
                f"{field}在{source_name}中不是区域级常量, region={region}"
            )
        found_values.append((source_name, float(unique_values[0])))

    if not found_values:
        raise RuntimeError(
            f"CON-Q2-3: actual=missing_{field}, threshold=finite, "
            f"region={region}"
        )
    return min(value for _, value in found_values)


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



def pilot(d):
    w = d["workload"]
    sample = w.head(min(48, len(w))).copy()
    duration = pd.to_numeric(
        sample["EstimatedDuration_min"], errors="coerce"
    ) / 60.0
    arrival = pd.to_numeric(sample["ArrivalHour"], errors="coerce")
    finish = pd.to_numeric(sample["LatestFinishHour"], errors="coerce")
    legal_window = (
        duration.notna()
        & arrival.notna()
        & finish.notna()
        & (duration > 0)
        & (arrival + duration <= np.minimum(finish, 2406) + TOL)
    )
    checks = [
        {
            "id": "PILOT-DATA-ROWS",
            "passed": bool(len(w) > 0),
            "actual": int(len(w)),
            "threshold": "workload rows > 0",
        },
        {
            "id": "PILOT-FINITE-DEMAND",
            "passed": bool(np.isfinite(pd.to_numeric(w["GPU_Demand"])).all()),
            "actual": "all_finite",
            "threshold": "100 percent finite",
        },
        {
            "id": "PILOT-TIME-COVERAGE",
            "passed": bool(d["region"].groupby("Region")["Hour"].nunique().min() == 2407),
            "actual": int(d["region"].groupby("Region")["Hour"].nunique().min()),
            "threshold": "2407 hours per region",
        },
        {
            "id": "PILOT-LATENCY-COVERAGE",
            "passed": bool(len(d["latency"]) == 36),
            "actual": int(len(d["latency"])),
            "threshold": "36 directed pairs",
        },
        {
            "id": "PILOT-FINITE-POWER-MAPPING",
            "passed": bool(
                np.isfinite(pd.to_numeric(
                    d["power"]["GPU_Power_MW_per_EquivalentGPU"],
                    errors="coerce",
                )).all()
            ),
            "actual": int(len(d["power"])),
            "threshold": "3 finite task power coefficients",
        },
        {
            "id": "PILOT-LEGAL-TASK-WINDOW",
            "passed": bool(legal_window.all()),
            "actual": int(legal_window.sum()),
            "threshold": f"{len(sample)} sampled tasks have legal finite windows",
        },
    ]
    if not all(c["passed"] for c in checks):
        raise RuntimeError("PILOT: 真实输入检查失败")
    RESULT_DIR.mkdir(parents=True, exist_ok=True)
    with open(RESULT_DIR / "method_pilot.json", "w", encoding="utf-8") as f:
        json.dump({
            "schema_version": 1,
            "status": "pass",
            "budget_seconds": 30,
            "checks": checks,
        }, f, ensure_ascii=False, indent=2)


def aggregate_demand(w):
    base = pd.MultiIndex.from_product(
        [REGIONS, TASK_TYPES, range(2400)],
        names=["Region", "TaskType", "Hour"],
    ).to_frame(index=False)
    x = w.assign(
        Region=w["SourceRegion"],
        Hour=pd.to_numeric(w["ArrivalHour"]).astype(int),
        GPU_Demand=pd.to_numeric(w["GPU_Demand"]),
        Duration_h=pd.to_numeric(w["EstimatedDuration_min"]) / 60.0,
    )
    x["GPUh"] = x["GPU_Demand"] * x["Duration_h"]
    agg = x.groupby(["Region", "TaskType", "Hour"], as_index=False).agg(
        GPU_Demand=("GPU_Demand", "sum"), GPUh=("GPUh", "sum")
    )
    return base.merge(agg, how="left").fillna(0), x




def greedy_schedule(d, workload):
    """
    使用按开始时刻递增的确定性候选扫描。

    容量检查采用NumPy区间切片，避免在任务、时刻和区域上执行三重Python循环。
    """
    gpu = d["gpu"].set_index("Region")
    latency = {
        (x.FromRegion, x.ToRegion): float(x.NetworkLatency_ms)
        for x in d["latency"].itertuples()
    }
    power = d["power"].set_index("TaskType")[
        "GPU_Power_MW_per_EquivalentGPU"
    ].to_dict()
    rt = d["region"].set_index(["Region", "Hour"])
    horizon = 2406
    used_gpu = np.zeros((len(REGIONS), 2407), dtype=float)
    used_power = np.zeros((len(REGIONS), 2407), dtype=float)
    result = []

    available_gpu = gpu.loc[REGIONS, "Available_GPU"].to_numpy(dtype=float)
    max_it_power = gpu.loc[REGIONS, "Max_IT_Power_MW"].to_numpy(dtype=float)
    max_facility_power = gpu.loc[
        REGIONS, "Max_Facility_Power_MW"
    ].to_numpy(dtype=float)
    pue = gpu.loc[REGIONS, "PUE"].to_numpy(dtype=float)

    nonai = np.empty((len(REGIONS), 2407), dtype=float)
    for r_idx, region in enumerate(REGIONS):
        region_rows = (
            d["region"].loc[
                d["region"]["Region"] == region,
                ["Hour", "NonAI_IT_Load_MW"],
            ]
            .sort_values("Hour")
        )
        nonai[r_idx, :] = region_rows["NonAI_IT_Load_MW"].to_numpy(dtype=float)

    latency_matrix = np.empty((len(REGIONS), len(REGIONS)), dtype=float)
    for source_idx, source in enumerate(REGIONS):
        for target_idx, target in enumerate(REGIONS):
            latency_matrix[source_idx, target_idx] = latency[(source, target)]

    region_index = {region: idx for idx, region in enumerate(REGIONS)}
    power_by_type = {
        task_type: float(value) for task_type, value in power.items()
    }

    tasks = workload.copy()
    tasks["Duration_h"] = (
        pd.to_numeric(tasks["EstimatedDuration_min"], errors="raise") / 60.0
    )
    tasks["FinishLimit"] = np.minimum(
        pd.to_numeric(tasks["LatestFinishHour"], errors="raise"),
        horizon,
    )
    tasks = tasks.sort_values(
        ["TaskType", "FinishLimit", "Duration_h", "GPU_Demand", "TaskID"],
        ascending=[False, True, False, False, True],
    )

    for task_no, row in enumerate(tasks.itertuples()):
        check_deadline("q1.greedy_schedule", task_no)

        h = float(row.Duration_h)
        arrival = int(row.ArrivalHour)
        latest = float(row.FinishLimit)
        gpu_demand = float(row.GPU_Demand)
        task_power = gpu_demand * power_by_type[row.TaskType]
        source_idx = region_index[row.SourceRegion]
        latency_row = latency_matrix[source_idx]
        legal_regions = np.flatnonzero(
            latency_row <= float(row.MaxLatency_ms) + TOL
        )

        latest_start = min(horizon - 1, int(np.floor(latest - h + TOL)))
        if row.TaskType == "RealTimeInference":
            starts = (arrival,)
        elif latest_start >= arrival:
            starts = range(arrival, latest_start + 1)
        else:
            starts = ()

        selected = None
        for s in starts:
            end = s + h
            if end > latest + TOL or end > horizon + TOL:
                continue

            end_slot = int(np.ceil(end - TOL))
            if end_slot <= s or end_slot > horizon:
                continue

            interval = slice(s, end_slot)
            feasible_at_start = []
            for r_idx in legal_regions:
                gpu_after = used_gpu[r_idx, interval] + gpu_demand
                power_after = used_power[r_idx, interval] + task_power
                if np.any(gpu_after > available_gpu[r_idx] + TOL):
                    continue
                if np.any(
                    nonai[r_idx, interval] + power_after
                    > max_it_power[r_idx] + TOL
                ):
                    continue
                if np.any(
                    (nonai[r_idx, interval] + power_after) * pue[r_idx]
                    > max_facility_power[r_idx] + TOL
                ):
                    continue

                peak = float(np.max(gpu_after / available_gpu[r_idx]))
                feasible_at_start.append(
                    (float(latency_row[r_idx]), peak, int(r_idx))
                )

            if feasible_at_start:
                # 开始时刻按升序扫描，因此首个可行时刻已使等待时间最小。
                lat, _, r_idx = min(feasible_at_start)
                selected = (s, end, end_slot, r_idx, lat)
                break

        if selected is None:
            raise RuntimeError(
                f"CON-Q1-7: TaskID={row.TaskID}, actual=0, threshold=>0, "
                "feasibility_unresolved"
            )

        start, finish, end_slot, r_idx, lat = selected
        region = REGIONS[r_idx]
        interval = slice(start, end_slot)
        used_gpu[r_idx, interval] += gpu_demand
        used_power[r_idx, interval] += task_power
        result.append({
            "TaskID": row.TaskID, "TaskType": row.TaskType,
            "SourceRegion": row.SourceRegion, "ExecutionRegion": region,
            "ArrivalHour": arrival,
            "StartHour": start, "FinishHour": finish,
            "WaitHour": start - arrival, "NetworkLatency_ms": lat,
            "GPU_Demand": gpu_demand,
        })

    return pd.DataFrame(result), used_gpu


def no_storage_energy(d, schedule):
    rt = d["region"].copy().sort_values(["Region", "Hour"]).reset_index(drop=True)
    rt = rt.rename(columns={
        "GridPurchase_MW": "BaselineGridPurchase_MW",
        "GridSell_MW": "BaselineGridSell_MW",
        "Curtailment_MW": "BaselineCurtailment_MW",
    })
    gpu = d["gpu"].set_index("Region")
    power = d["power"].set_index("TaskType")[
        "GPU_Power_MW_per_EquivalentGPU"
    ].to_dict()
    ai = {(r, t): 0.0 for r in REGIONS for t in range(2407)}

    for row in schedule.itertuples():
        duration = row.FinishHour - row.StartHour
        for t in range(int(row.StartHour), min(2406, int(np.ceil(row.FinishHour)))):
            overlap = max(0.0, min(t + 1, row.FinishHour) - max(t, row.StartHour))
            ai[(row.ExecutionRegion, t)] += row.GPU_Demand * power[row.TaskType] * overlap

    rt["AI_IT_Energy_MWh"] = [
        ai[(r, int(t))] for r, t in zip(rt["Region"], rt["Hour"])
    ]
    rt["AI_IT_AveragePower_MW"] = rt["AI_IT_Energy_MWh"]
    rt["AI_IT_Load_MW"] = rt["AI_IT_AveragePower_MW"]
    pue = gpu["PUE"].to_dict()
    rt["NonAI_IT_Energy_MWh"] = rt["NonAI_IT_Load_MW"]
    rt["FacilityAveragePower_MW"] = (
        rt["NonAI_IT_Energy_MWh"] + rt["AI_IT_Energy_MWh"]
    ) * rt["Region"].map(pue)
    rt["FacilityLoad_MW"] = rt["FacilityAveragePower_MW"]
    rt["RenewableUse_MW"] = np.minimum(
        rt["AvailableRenewable_MW"], rt["FacilityLoad_MW"]
    )
    rt["OptimizedGridPurchase_MW"] = rt["FacilityLoad_MW"] - rt["RenewableUse_MW"]
    surplus = np.maximum(0, rt["AvailableRenewable_MW"] - rt["RenewableUse_MW"])
    import_limits = {
        region: q2_grid_limit(d, region, "MaxGridImport_MW")
        for region in REGIONS
    }
    export_limits = {
        region: q2_grid_limit(d, region, "MaxGridExport_MW")
        for region in REGIONS
    }
    rt["GridImportLimit_MW"] = rt["Region"].map(import_limits).astype(float)
    rt["GridExportLimit_MW"] = rt["Region"].map(export_limits).astype(float)

    import_residual = (
        rt["OptimizedGridPurchase_MW"] - rt["GridImportLimit_MW"]
    )
    max_import_residual = float(import_residual.max())
    if max_import_residual > TOL:
        fail(
            "CON-Q2-3",
            max_import_residual,
            TOL,
            "问题二购电功率超过MaxGridImport_MW",
        )

    rt["OptimizedGridSell_MW"] = np.minimum(
        surplus,
        rt["GridExportLimit_MW"].to_numpy(dtype=float),
    )
    rt["OptimizedCurtailment_MW"] = surplus - rt["OptimizedGridSell_MW"]

    mutex_residual = float(np.max(np.minimum(
        rt["OptimizedGridPurchase_MW"].to_numpy(dtype=float),
        rt["OptimizedGridSell_MW"].to_numpy(dtype=float),
    )))
    if mutex_residual > TOL:
        fail(
            "CON-Q2-3",
            mutex_residual,
            TOL,
            "问题二出现同时购电和售电",
        )

    cost = np.sum(
        rt["OptimizedGridPurchase_MW"] * rt["ElectricityPrice_CNY_per_MWh"]
        - rt["OptimizedGridSell_MW"] * rt["SellPrice_CNY_per_MWh"]
    )
    carbon = np.sum(
        rt["OptimizedGridPurchase_MW"] * rt["CarbonIntensity_tCO2_per_MWh"]
    )
    renewable = np.sum(rt["AvailableRenewable_MW"])
    utilization = (
        np.sum(rt["RenewableUse_MW"] + rt["OptimizedGridSell_MW"]) / renewable
        if renewable > 0 else None
    )
    return rt, finite(cost, "q2_cost"), finite(carbon, "q2_carbon"), utilization


def q3_baseline_flow(d):
    rt = d["region"].copy().sort_values(["Region", "Hour"]).reset_index(drop=True)
    gpu = d["gpu"].set_index("Region")
    storage = d["storage"].set_index("Region")
    rt["FacilityLoad_MW"] = [
        (
            float(row.Baseline_AI_IT_Load_MW)
            + float(row.NonAI_IT_Load_MW)
        ) * float(gpu.loc[row.Region, "PUE"])
        for row in rt.itertuples()
    ]
    rt["RenewableUse_MW"] = np.minimum(
        rt["AvailableRenewable_MW"], rt["FacilityLoad_MW"]
    )
    rt["Charge_MW"] = 0.0
    rt["Discharge_MW"] = 0.0
    rt["SOC_MWh"] = [
        float(storage.loc[r, "InitialSOC_MWh"]) for r in rt["Region"]
    ]
    rt["GridPurchase_MW"] = rt["FacilityLoad_MW"] - rt["RenewableUse_MW"]
    surplus = np.maximum(
        0.0, rt["AvailableRenewable_MW"] - rt["RenewableUse_MW"]
    )
    rt["GridSell_MW"] = [
        min(
            float(value),
            grid_export_limit(row, storage.loc[row["Region"]]),
        )
        for value, (_, row) in zip(surplus, rt.iterrows())
    ]
    rt["Curtailment_MW"] = surplus - rt["GridSell_MW"]
    rt["Price"] = rt["ElectricityPrice_CNY_per_MWh"]
    rt["SellPrice"] = rt["SellPrice_CNY_per_MWh"]
    rt["CarbonIntensity"] = rt["CarbonIntensity_tCO2_per_MWh"]
    rt["GridExportLimit_MW"] = rt["GridSell_MW"] + rt["Curtailment_MW"]
    return rt


def normalize_facility_override(facility_override):
    required = {"Region", "Hour", "FacilityLoad_MW"}
    if facility_override is None:
        return None
    if not required.issubset(facility_override.columns):
        missing = sorted(required.difference(facility_override.columns))
        raise RuntimeError(
            f"CON-Q4-1: actual=missing_columns_{missing}, "
            "threshold=Region_Hour_FacilityLoad_MW"
        )
    override = facility_override[list(required)].copy()
    if override.duplicated(["Region", "Hour"]).any():
        raise RuntimeError(
            "CON-Q4-1: actual=duplicate_region_hour, threshold=unique"
        )
    if len(override) != len(REGIONS) * 2407:
        fail(
            "CON-Q4-1",
            len(override),
            len(REGIONS) * 2407,
            "联合设施负荷覆盖不完整",
        )
    values = pd.to_numeric(override["FacilityLoad_MW"], errors="coerce")
    if not np.isfinite(values).all() or (values < -TOL).any():
        raise RuntimeError(
            "CON-Q4-1: actual=nonfinite_or_negative, "
            "threshold=finite_nonnegative"
        )
    override["FacilityLoad_MW"] = values
    return override


def build_storage_policy(
    d,
    facility_override=None,
    price_scale=1.0,
    sell_scale=1.0,
    renewable_scale=1.0,
    renewable_override=None,
    charge_quantile=0.25,
    discharge_quantile=0.75,
    carbon_weight=0.0,
):
    rt = d["region"].copy().sort_values(["Region", "Hour"]).reset_index(drop=True)
    storage = d["storage"].set_index("Region")
    gpu = d["gpu"].set_index("Region")
    override = normalize_facility_override(facility_override)
    if override is not None:
        rt = rt.merge(
            override,
            on=["Region", "Hour"],
            how="left",
            validate="one_to_one",
        )
    if renewable_override is not None:
        renewable_override = np.asarray(renewable_override, dtype=float)
        if renewable_override.shape != (len(rt),):
            raise RuntimeError(
                "CON-Q4-4: actual=renewable_shape, threshold=14442"
            )
        if not np.isfinite(renewable_override).all():
            raise RuntimeError(
                "CON-Q4-4: actual=nonfinite_renewable, threshold=finite"
            )
        rt["ScenarioRenewable_MW"] = np.maximum(0.0, renewable_override)
    else:
        rt["ScenarioRenewable_MW"] = np.maximum(
            0.0, rt["AvailableRenewable_MW"] * float(renewable_scale)
        )
    records = []

    for r in REGIONS:
        x = rt[rt["Region"] == r].sort_values("Hour")
        s = storage.loc[r]
        soc = float(s["InitialSOC_MWh"])
        max_soc = storage_soc_max(s)
        raw_prices = x["ElectricityPrice_CNY_per_MWh"].to_numpy(float)
        mean_price = float(np.mean(raw_prices))
        prices = mean_price + float(price_scale) * (raw_prices - mean_price)
        carbon = x["CarbonIntensity_tCO2_per_MWh"].to_numpy(float)
        dispatch_signal = prices + float(carbon_weight) * carbon
        has_hourly_export_limit = "MaxGridExport_MW" in x.columns
        low, high = np.quantile(dispatch_signal, [charge_quantile, discharge_quantile])

        for local_idx, row in enumerate(x.itertuples()):
            if facility_override is None:
                load = (
                    float(row.Baseline_AI_IT_Load_MW)
                    + float(row.NonAI_IT_Load_MW)
                ) * float(gpu.loc[r, "PUE"])
            else:
                load = float(row.FacilityLoad_MW)
            renewable = float(row.ScenarioRenewable_MW)
            price = float(prices[local_idx])
            signal = float(dispatch_signal[local_idx])
            use = min(load, renewable)
            deficit = load - use
            surplus = renewable - use
            charge = 0.0
            discharge = 0.0

            if surplus > 0 and soc < max_soc:
                charge = min(
                    surplus, float(s["MaxChargePower_MW"]),
                    (max_soc - soc) / float(s["ChargeEfficiency"]),
                )
            elif signal >= high and deficit > 0:
                discharge = min(
                    deficit, float(s["MaxDischargePower_MW"]),
                    max(0, (soc - float(s["MinSOC_MWh"])) * float(s["DischargeEfficiency"])),
                )

            soc += charge * float(s["ChargeEfficiency"])
            soc -= discharge / float(s["DischargeEfficiency"])
            grid_buy = deficit - discharge
            region_row = pd.Series({
                "MaxGridExport_MW": (
                    getattr(row, "MaxGridExport_MW")
                    if has_hourly_export_limit
                    else np.nan
                )
            })
            sell_cap = grid_export_limit(region_row, s)
            sell_cap = max(0.0, sell_cap)
            grid_sell = min(max(0, surplus - charge), sell_cap)
            curtail = max(0, surplus - charge - grid_sell)
            records.append({
                "Region": r, "Hour": int(row.Hour), "FacilityLoad_MW": load,
                "RenewableUse_MW": use, "Charge_MW": charge,
                "Discharge_MW": discharge, "SOC_MWh": soc,
                "GridPurchase_MW": grid_buy, "GridSell_MW": grid_sell,
                "Curtailment_MW": curtail,
                "GridExportLimit_MW": sell_cap,
                "Price": price,
                "SellPrice": float(row.SellPrice_CNY_per_MWh) * float(sell_scale),
                "CarbonIntensity": float(row.CarbonIntensity_tCO2_per_MWh),
                "AvailableRenewable_MW": renewable,
            })

        if soc + TOL < float(s["InitialSOC_MWh"]):
            fail("CON-Q3-2", soc, s["InitialSOC_MWh"], r)

    return pd.DataFrame(records)


def metrics_energy(x):
    cost = np.sum(
        x["GridPurchase_MW"] * x["Price"]
        - x["GridSell_MW"] * x["SellPrice"]
    )
    carbon = np.sum(x["GridPurchase_MW"] * x["CarbonIntensity"])
    available = float(np.sum(x["AvailableRenewable_MW"]))
    used = float(np.sum(
        x["RenewableUse_MW"] + x["Charge_MW"] + x["GridSell_MW"]
    ))
    if available <= 0:
        raise RuntimeError(
            "CON-Q3-7: actual=0, threshold=positive renewable denominator"
        )
    peak = float(
        x.groupby("Region")["GridPurchase_MW"].max().clip(lower=0).sum()
    )
    ramp = float(
        x.groupby("Region")["GridPurchase_MW"].apply(
            lambda values: np.abs(np.diff(values.to_numpy(float))).sum()
        ).sum()
    )
    return (
        finite(cost, "cost"),
        finite(carbon, "carbon"),
        finite(used / available, "renewable"),
        finite(peak, "peak"),
        finite(ramp, "ramp"),
    )




def audit_storage_policy(d, flow, constraint_prefix):
    storage = d["storage"].set_index("Region")
    rows = []
    for r in REGIONS:
        x = flow.loc[flow["Region"] == r].sort_values("Hour")
        s = storage.loc[r]
        previous = float(s["InitialSOC_MWh"])
        max_energy_residual = 0.0
        max_soc_residual = 0.0
        max_bound_residual = 0.0
        max_mutex_residual = 0.0
        for row in x.itertuples():
            energy_residual = (
                float(row.GridPurchase_MW)
                + float(row.AvailableRenewable_MW)
                + float(row.Discharge_MW)
                - float(row.FacilityLoad_MW)
                - float(row.Charge_MW)
                - float(row.GridSell_MW)
                - float(row.Curtailment_MW)
            )
            expected_soc = (
                previous
                + float(s["ChargeEfficiency"]) * float(row.Charge_MW)
                - float(row.Discharge_MW) / float(s["DischargeEfficiency"])
            )
            max_energy_residual = max(max_energy_residual, abs(energy_residual))
            max_soc_residual = max(
                max_soc_residual, abs(float(row.SOC_MWh) - expected_soc)
            )
            max_bound_residual = max(
                max_bound_residual,
                float(s["MinSOC_MWh"]) - float(row.SOC_MWh),
                float(row.SOC_MWh) - storage_soc_max(s),
                float(row.Charge_MW) - float(s["MaxChargePower_MW"]),
                float(row.Discharge_MW) - float(s["MaxDischargePower_MW"]),
                float(row.GridSell_MW) - float(row.GridExportLimit_MW),
                -float(row.GridPurchase_MW),
            )
            max_mutex_residual = max(
                max_mutex_residual,
                min(float(row.Charge_MW), float(row.Discharge_MW)),
                min(float(row.GridPurchase_MW), float(row.GridSell_MW)),
            )
            previous = float(row.SOC_MWh)
        terminal_residual = float(s["InitialSOC_MWh"]) - previous
        rows.append({
            "Region": r,
            "max_energy_abs_residual_MW": max_energy_residual,
            "max_soc_abs_residual_MWh": max_soc_residual,
            "max_storage_bound_residual": max_bound_residual,
            "max_mutex_residual_MW": max_mutex_residual,
            "terminal_soc_residual_MWh": terminal_residual,
        })
    audit = pd.DataFrame(rows)
    max_residual = float(np.max(np.maximum(
        audit.drop(columns="Region").to_numpy(float), 0.0
    )))
    if max_residual > TOL:
        fail(
            constraint_prefix,
            max_residual,
            TOL,
            "储能或能源硬约束审计失败",
        )
    return audit


def service_metrics(schedule):
    duration = schedule["FinishHour"] - schedule["StartHour"]
    weight = schedule["GPU_Demand"] * duration
    denominator = float(weight.sum())
    if denominator <= 0:
        raise RuntimeError("CON-Q4-3: actual=0, threshold=positive network denominator")
    latency = float(np.sum(weight * schedule["NetworkLatency_ms"]) / denominator)
    objective = float(np.sum(weight * (schedule["NetworkLatency_ms"] + Q2_SERVICE_WAIT_FACTOR * schedule["WaitHour"])) / denominator)
    service = float(1.0 / (1.0 + objective))
    migrated = int((schedule["SourceRegion"] != schedule["ExecutionRegion"]).sum())
    return latency, service, migrated


def q2_service_objective(schedule):
    duration = schedule["FinishHour"].to_numpy(float) - schedule["StartHour"].to_numpy(float)
    weight = schedule["GPU_Demand"].to_numpy(float) * duration
    denominator = float(weight.sum())
    if denominator <= 0:
        raise RuntimeError("Q2-SERVICE-001: nonpositive GPU-hour denominator")
    penalty = schedule["NetworkLatency_ms"].to_numpy(float) + Q2_SERVICE_WAIT_FACTOR * schedule["WaitHour"].to_numpy(float)
    return float(np.dot(weight, penalty) / denominator)


def scenario_storage_flow(
    d,
    candidate,
    scenario_type,
    level,
    volatile,
    baseline_flow=None,
):
    if (
        scenario_type == "baseline"
        and candidate["candidate_id"] == "task_baseline"
        and baseline_flow is not None
    ):
        return baseline_flow.copy()
    kwargs = {
        "facility_override": candidate["facility_override"],
    }
    if scenario_type == "price_spread":
        kwargs["price_scale"] = level
    elif scenario_type == "sell_mechanism":
        kwargs["sell_scale"] = level
    elif scenario_type == "renewable_level":
        kwargs["renewable_scale"] = level
    elif scenario_type == "renewable_volatility":
        kwargs["renewable_override"] = volatile
    elif scenario_type == "carbon_constraint":
        # 碳约束水平直接进入储能调度信号。该规则只在声明候选集中搜索，
        # 未达到目标时仍报告within_declared_heuristic。
        kwargs["carbon_weight"] = 1000.0 * float(level)
    return build_storage_policy(d, **kwargs)




def rebuild_schedule_resources(d, schedule):
    """Separate instantaneous capacity states from overlap-based hourly energy."""
    power = d["power"].set_index("TaskType")["GPU_Power_MW_per_EquivalentGPU"].to_dict()
    region_index = {region: idx for idx, region in enumerate(REGIONS)}
    gpu_state = np.zeros((len(REGIONS), 2407), dtype=float)
    power_state = np.zeros((len(REGIONS), 2407), dtype=float)
    energy_state = np.zeros((len(REGIONS), 2407), dtype=float)
    for row in schedule.itertuples():
        idx = region_index[row.ExecutionRegion]
        task_power = float(row.GPU_Demand) * float(power[row.TaskType])
        overlaps = list(_task_hour_overlaps(float(row.StartHour), float(row.FinishHour)))
        if not overlaps:
            return None
        for hour, overlap in overlaps:
            gpu_state[idx, hour] += float(row.GPU_Demand)
            power_state[idx, hour] += task_power
            energy_state[idx, hour] += task_power * overlap
    return {"used_gpu_instant": gpu_state, "used_it_power_instant_mw": power_state, "ai_energy_mwh": energy_state}


def q2_search_metrics(schedule, cost, carbon):
    latency, _, _ = service_metrics(schedule)
    wait = finite(schedule["WaitHour"].sum(), "q2_wait")
    return np.array([cost, carbon, latency, wait], dtype=float)






def save_figure(data, file_name, kind, x, y, title, x_label, y_label, manifest):
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    FIGURE_DATA_DIR.mkdir(parents=True, exist_ok=True)
    csv_name = Path(file_name).with_suffix(".csv").name
    data.to_csv(FIGURE_DATA_DIR / csv_name, index=False)
    fig, ax = plt.subplots(constrained_layout=True)
    for col in ([y] if isinstance(y, str) else y):
        ax.plot(data[x], data[col], label=col)
    ax.set_title(title)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    if not isinstance(y, str) or len(y) > 1:
        ax.legend()
    fig.savefig(FIGURE_DIR / file_name)
    plt.close(fig)
    manifest.append({
        "file": file_name, "kind": kind,
        "data_file": f"figure_data/{csv_name}",
        "x": x, "y": y, "title": title,
        "x_label": x_label, "y_label": y_label,
        "caption": title,
    })


def save_q1_gantt(schedule, manifest):
    """Render the 538 task terminal-window schedule in six region panels."""
    required = {
        "TaskID", "TaskType", "ExecutionRegion", "StartHour", "FinishHour"
    }
    if not required <= set(schedule.columns):
        raise RuntimeError("Q1-GANTT-001: gantt data columns incomplete")
    data_path = RESULT_DIR / "q1_gantt.csv"
    schedule.to_csv(data_path, index=False)
    colors = {
        "RealTimeInference": "#4C72B0",
        "BatchInference": "#DD8452",
        "AITraining": "#55A868",
    }
    fig, axes = plt.subplots(
        len(REGIONS), 1, figsize=(14, 16), sharex=True, constrained_layout=True
    )
    for axis, region in zip(axes, REGIONS):
        group = schedule.loc[schedule["ExecutionRegion"].eq(region)].sort_values(
            ["StartHour", "FinishHour", "TaskType", "TaskID"]
        ).reset_index(drop=True)
        for index, row in group.iterrows():
            axis.barh(
                index,
                float(row["FinishHour"]) - float(row["StartHour"]),
                left=float(row["StartHour"]),
                height=0.82,
                color=colors[str(row["TaskType"])],
                edgecolor="none",
                alpha=0.82,
            )
        axis.set_ylabel(f"{region}\n任务序号")
        axis.set_ylim(-1, max(1, len(group)))
        axis.set_yticks([])
        axis.axvline(2400, color="#C44E52", linestyle="--", linewidth=1.2)
        axis.text(2400.05, max(0.5, len(group) * 0.92), "收尾时域", color="#C44E52")
    axes[-1].set_xlim(2376, 2406)
    axes[-1].set_xlabel("实际开工与完成时刻 / h")
    handles = [
        plt.Line2D([0], [0], color=colors[name], linewidth=6, label=name)
        for name in TASK_TYPES
    ]
    axes[0].legend(handles=handles, loc="upper right", ncol=3)
    fig.suptitle("问题一：第2376--2399小时实际到达任务调度甘特图")
    figure_path = FIGURE_DIR / "q1_gantt.png"
    fig.savefig(figure_path)
    plt.close(fig)
    manifest.append({
        "file": "q1_gantt.png",
        "kind": "gantt",
        "data_file": "q1_gantt.csv",
        "x": ["StartHour", "FinishHour"],
        "y": ["ExecutionRegion", "TaskType", "TaskID"],
        "title": "问题一：第2376--2399小时实际到达任务调度甘特图",
        "caption": "六个执行区域分面；完整任务级起止时刻见q1_gantt.csv",
    })


def result_item(name, value, unit, desc):
    return {
        "name": name, "value": finite(value, name),
        "unit": unit, "desc": desc,
    }


Q2_SCHEME_RESULTS = {}
Q2_SCHEME_AUDITS = {}
Q3_POLICY_RESULTS = {}
Q3_TERMINAL_SENSITIVITY = {}


def _forecast_features(history, t):
    return [
        history[t - 1], history[t - 2], history[t - 3],
        history[t - 24], history[t - 48], history[t - 168],
        np.sin(2 * np.pi * t / 24), np.cos(2 * np.pi * t / 24),
        np.sin(2 * np.pi * t / 168), np.cos(2 * np.pi * t / 168),
    ]


def _recursive_forecast(y, origin, horizon, model_name, model=None):
    history = list(np.asarray(y[:origin], dtype=float))
    result = []
    seasonal_lag = 24 if model_name == "SeasonalNaive24" else 168
    for t in range(origin, origin + horizon):
        if model_name.startswith("SeasonalNaive"):
            value = history[t - seasonal_lag]
        else:
            value = float(model.predict(np.asarray([
                _forecast_features(history, t)
            ], dtype=float))[0])
        value = max(0.0, finite(value, "recursive_prediction"))
        history.append(value)
        result.append(value)
    return np.asarray(result, dtype=float)


def _fit_huber(y, end_inclusive, epsilon, alpha):
    times = np.arange(168, end_inclusive + 1)
    x = np.asarray([
        _forecast_features(y, int(t)) for t in times
    ], dtype=float)
    target = np.asarray(y[168:end_inclusive + 1], dtype=float)
    model = HuberRegressor(
        epsilon=float(epsilon),
        alpha=float(alpha),
        max_iter=500,
        tol=1e-6,
    )
    model.fit(x, target)
    return model


def _forecast_metric(actual, prediction):
    actual = np.asarray(actual, dtype=float)
    prediction = np.asarray(prediction, dtype=float)
    errors = np.abs(actual - prediction)
    denom = float(np.abs(actual).sum())
    return {
        "MAE": float(errors.mean()),
        "RMSE": float(np.sqrt(np.mean((actual - prediction) ** 2))),
        "WAPE": float(errors.sum() / denom) if denom > 0 else None,
        "SampleCount": int(len(actual)),
        "WAPEZeroDenominator": bool(denom <= 0),
    }


def _forecast_candidate_specs():
    specs = [
        {"CandidateRank": 0, "CandidateModel": "SeasonalNaive24", "HuberEpsilon": None, "HuberAlpha": None},
        {"CandidateRank": 1, "CandidateModel": "SeasonalNaive168", "HuberEpsilon": None, "HuberAlpha": None},
    ]
    for epsilon, alpha in Q1_HUBER_GRID:
        specs.append({
            "CandidateRank": len(specs),
            "CandidateModel": "Huber",
            "HuberEpsilon": float(epsilon),
            "HuberAlpha": float(alpha),
        })
    return specs


def _candidate_id(spec):
    if spec["CandidateModel"] != "Huber":
        return spec["CandidateModel"]
    return f"Huber(epsilon={spec['HuberEpsilon']:.2f},alpha={spec['HuberAlpha']:.4g})"


def _forecast_summary(predictions, metrics):
    actual = predictions["Actual_GPU"].to_numpy(float)
    predicted = predictions["Prediction_GPU"].to_numpy(float)
    absolute_error = np.abs(actual - predicted)
    micro_denom = float(np.abs(actual).sum())
    system = predictions.groupby("Hour", as_index=False).agg(
        Actual_GPU=("Actual_GPU", "sum"),
        Prediction_GPU=("Prediction_GPU", "sum"),
    )
    system_error = np.abs(
        system["Actual_GPU"].to_numpy(float)
        - system["Prediction_GPU"].to_numpy(float)
    )
    system_denom = float(np.abs(system["Actual_GPU"].to_numpy(float)).sum())
    macro_values = metrics.loc[~metrics["TestWAPEZeroDenominator"], "WAPE"].to_numpy(float)
    if len(macro_values) != len(metrics):
        raise RuntimeError("Q1-WAPE-001: zero-denominator series prevents complete Macro-WAPE")
    rows = [
        {
            "Metric": "Macro-WAPE",
            "Value": float(macro_values.mean()),
            "Unit": "ratio",
            "Definition": "18条区域-任务类型序列分别计算WAPE后取算术平均；对低基数序列敏感",
        },
        {
            "Metric": "Micro-WAPE",
            "Value": float(absolute_error.sum() / micro_denom),
            "Unit": "ratio",
            "Definition": "全部18x24观测绝对误差之和除以真实值之和；按需求规模加权",
        },
        {
            "Metric": "System Aggregate WAPE",
            "Value": float(system_error.sum() / system_denom),
            "Unit": "ratio",
            "Definition": "先按小时聚合18条序列再计算WAPE；反映系统总量但允许高低估抵消",
        },
        {
            "Metric": "Overall MAE",
            "Value": float(absolute_error.mean()),
            "Unit": "GPU",
            "Definition": "全部18x24观测的平均绝对误差",
        },
        {
            "Metric": "Overall RMSE",
            "Value": float(np.sqrt(np.mean((actual - predicted) ** 2))),
            "Unit": "GPU",
            "Definition": "全部18x24观测的均方根误差",
        },
    ]
    return pd.DataFrame(rows)


def forecast(demand):
    """Eight-origin closed-loop selection followed by one final test evaluation."""
    table = demand.pivot_table(
        index="Hour", columns=["Region", "TaskType"],
        values="GPU_Demand", fill_value=0,
    ).sort_index()
    specs = _forecast_candidate_specs()
    metric_rows = []
    prediction_rows = []
    rolling_rows = []
    candidate_rows = []
    selection_rows = []
    for region in REGIONS:
        for task_type in TASK_TYPES:
            y = table[(region, task_type)].to_numpy(float)
            per_candidate = []
            for spec in specs:
                candidate_id = _candidate_id(spec)
                window_rows = []
                for origin in Q1_ROLLING_ORIGINS:
                    if spec["CandidateModel"] == "Huber":
                        model = _fit_huber(
                            y, origin - 1,
                            spec["HuberEpsilon"], spec["HuberAlpha"],
                        )
                    else:
                        model = None
                    pred = _recursive_forecast(
                        y, origin, Q1_FORECAST_HORIZON,
                        spec["CandidateModel"], model,
                    )
                    metric = _forecast_metric(
                        y[origin:origin + Q1_FORECAST_HORIZON], pred
                    )
                    row = {
                        "Region": region,
                        "TaskType": task_type,
                        "CandidateID": candidate_id,
                        **spec,
                        "RollingOrigin": int(origin),
                        "TrainStartHour": 0,
                        "TrainEndHour": int(origin - 1),
                        "ValidationStartHour": int(origin),
                        "ValidationEndHour": int(origin + Q1_FORECAST_HORIZON - 1),
                        **metric,
                        "ClosedLoopForecast": True,
                        "FeatureUsesValidationTruth": False,
                        "FinalTestUsedForSelection": False,
                    }
                    window_rows.append(row)
                    rolling_rows.append(row.copy())
                per_candidate.append((spec, candidate_id, window_rows))

            # Rank every candidate inside every origin to expose selection stability.
            by_origin = {origin: [] for origin in Q1_ROLLING_ORIGINS}
            for spec, candidate_id, windows in per_candidate:
                for row in windows:
                    by_origin[row["RollingOrigin"]].append(row)
            for origin, window_candidates in by_origin.items():
                ordered = sorted(window_candidates, key=lambda row: (
                    row["RMSE"], row["MAE"],
                    float("inf") if row["WAPE"] is None else row["WAPE"],
                    row["CandidateRank"],
                ))
                for rank, row in enumerate(ordered, start=1):
                    row["WindowRank"] = rank
                    # Keep rolling_rows synchronized with the mutable window row.
                    match = next(
                        target for target in rolling_rows
                        if target["Region"] == region
                        and target["TaskType"] == task_type
                        and target["CandidateID"] == row["CandidateID"]
                        and target["RollingOrigin"] == origin
                    )
                    match["WindowRank"] = rank

            summaries = []
            for spec, candidate_id, windows in per_candidate:
                wapes = [row["WAPE"] for row in windows if row["WAPE"] is not None]
                summary = {
                    "Region": region,
                    "TaskType": task_type,
                    "CandidateID": candidate_id,
                    **spec,
                    "WindowCount": len(windows),
                    "MeanRMSE": float(np.mean([row["RMSE"] for row in windows])),
                    "MeanMAE": float(np.mean([row["MAE"] for row in windows])),
                    "MeanWAPE": float(np.mean(wapes)) if wapes else None,
                    "StdRMSE": float(np.std([row["RMSE"] for row in windows])),
                    "WindowRankMin": int(min(row["WindowRank"] for row in windows)),
                    "WindowRankMax": int(max(row["WindowRank"] for row in windows)),
                    "WindowRankStd": float(np.std([row["WindowRank"] for row in windows])),
                    "WindowWinnerCount": int(sum(row["WindowRank"] == 1 for row in windows)),
                    "FinalTestUsedForSelection": False,
                }
                summaries.append(summary)
                candidate_rows.append(summary.copy())

            selected = min(summaries, key=lambda row: (
                row["MeanRMSE"], row["MeanMAE"],
                float("inf") if row["MeanWAPE"] is None else row["MeanWAPE"],
                row["CandidateRank"],
            ))
            selected_windows = next(
                windows for spec, candidate_id, windows in per_candidate
                if candidate_id == selected["CandidateID"]
            )
            official_validation = next(
                row for row in selected_windows if row["RollingOrigin"] == 2352
            )
            selected_name = selected["CandidateModel"]
            epsilon = selected["HuberEpsilon"]
            alpha = selected["HuberAlpha"]
            final_model = (
                _fit_huber(y, 2375, epsilon, alpha)
                if selected_name == "Huber" else None
            )
            test_pred = _recursive_forecast(
                y, 2376, Q1_FORECAST_HORIZON, selected_name, final_model
            )
            test_metric = _forecast_metric(y[2376:2400], test_pred)
            metric_rows.append({
                "Region": region,
                "TaskType": task_type,
                "SelectedModel": selected_name,
                "SelectedCandidateID": selected["CandidateID"],
                "HuberEpsilon": epsilon,
                "HuberAlpha": alpha,
                "RollingWindowCount": len(Q1_ROLLING_ORIGINS),
                "RollingMeanMAE": selected["MeanMAE"],
                "RollingMeanRMSE": selected["MeanRMSE"],
                "RollingMeanWAPE": selected["MeanWAPE"],
                "ValidationMAE": official_validation["MAE"],
                "ValidationRMSE": official_validation["RMSE"],
                "ValidationWAPE": official_validation["WAPE"],
                "ValidationSampleCount": official_validation["SampleCount"],
                "ValidationWAPEZeroDenominator": official_validation["WAPEZeroDenominator"],
                "MAE": test_metric["MAE"],
                "RMSE": test_metric["RMSE"],
                "WAPE": test_metric["WAPE"],
                "TestSampleCount": test_metric["SampleCount"],
                "TestWAPEZeroDenominator": test_metric["WAPEZeroDenominator"],
                "ClosedLoopForecast": True,
                "TrainEndHour": 2351,
                "ValidationStartHour": 2352,
                "ValidationEndHour": 2375,
                "FinalFitEndHour": 2375,
                "TestStartHour": 2376,
                "TestEndHour": 2399,
                "FinalTestUsedForSelection": False,
            })
            selection_rows.append({
                "Region": region,
                "TaskType": task_type,
                "SelectedCandidateID": selected["CandidateID"],
                "SelectionCriterion": "MeanRMSE,MeanMAE,MeanWAPE,fixed_candidate_rank",
                "RollingOrigins": "|".join(map(str, Q1_ROLLING_ORIGINS)),
                "WindowCount": len(Q1_ROLLING_ORIGINS),
                "SelectedMeanRMSE": selected["MeanRMSE"],
                "SelectedMeanMAE": selected["MeanMAE"],
                "SelectedMeanWAPE": selected["MeanWAPE"],
                "SelectedWindowWinnerCount": selected["WindowWinnerCount"],
                "SelectedWindowWinnerShare": selected["WindowWinnerCount"] / len(Q1_ROLLING_ORIGINS),
                "SelectedWindowRankMin": selected["WindowRankMin"],
                "SelectedWindowRankMax": selected["WindowRankMax"],
                "SelectedWindowRankStd": selected["WindowRankStd"],
                "ModelSelectionStableAllWindows": selected["WindowWinnerCount"] == len(Q1_ROLLING_ORIGINS),
                "FinalTestUsedForSelection": False,
            })
            for offset, value in enumerate(test_pred):
                hour = 2376 + offset
                prediction_rows.append({
                    "Hour": hour,
                    "Region": region,
                    "TaskType": task_type,
                    "Prediction_GPU": finite(value, "prediction"),
                    "Actual_GPU": finite(y[hour], "actual"),
                    "FeatureUsesTestTruth": False,
                    "SelectedModel": selected_name,
                    "SelectedCandidateID": selected["CandidateID"],
                })
    metrics = pd.DataFrame(metric_rows)
    predictions = pd.DataFrame(prediction_rows)
    rolling = pd.DataFrame(rolling_rows)
    candidates = pd.DataFrame(candidate_rows)
    selection = pd.DataFrame(selection_rows)
    summary = _forecast_summary(predictions, metrics)
    return metrics, predictions, rolling, candidates, selection, summary

def _q2_energy_values(load, renewable, price, sell_price, carbon, export_limit):
    """One-hour settlement from average MW (numerically MWh for dt=1 h)."""
    use = min(load, renewable)
    buy = max(0.0, load - use)
    sell = min(max(0.0, renewable - use), export_limit)
    curtail = max(0.0, renewable - use - sell)
    return buy * price - sell * sell_price, buy * carbon, use + sell, buy, curtail


def _task_hour_overlaps(start, finish):
    for hour in range(max(0, int(np.floor(float(start)))), min(2406, int(np.ceil(float(finish) - TOL)))):
        overlap = max(0.0, min(hour + 1.0, float(finish)) - max(float(hour), float(start)))
        if overlap > TOL:
            yield hour, overlap


def _q2_context(d, schedule):
    resources = rebuild_schedule_resources(d, schedule)
    if resources is None:
        raise RuntimeError("CON-Q2-1: baseline resource reconstruction failed")
    rt = d["region"].sort_values(["Region", "Hour"])
    arrays = {column: np.vstack([rt.loc[rt["Region"].eq(r), column].to_numpy(float) for r in REGIONS]) for column in (
        "NonAI_IT_Load_MW", "AvailableRenewable_MW", "ElectricityPrice_CNY_per_MWh",
        "SellPrice_CNY_per_MWh", "CarbonIntensity_tCO2_per_MWh")}
    gpu = d["gpu"].set_index("Region")
    pue = gpu.loc[REGIONS, "PUE"].to_numpy(float)
    duration = schedule["FinishHour"].to_numpy(float) - schedule["StartHour"].to_numpy(float)
    denominator = float(np.dot(schedule["GPU_Demand"].to_numpy(float), duration))
    if denominator <= 0:
        raise RuntimeError("Q2-SERVICE-001: nonpositive GPU-hour denominator")
    return {
        "region_index": {r: i for i, r in enumerate(REGIONS)}, **resources,
        "facility_average_power_mw": (arrays["NonAI_IT_Load_MW"] + resources["ai_energy_mwh"]) * pue[:, None],
        "arrays": arrays, "pue": pue, "service_denominator": denominator,
        "available_gpu": gpu.loc[REGIONS, "Available_GPU"].to_numpy(float),
        "max_it": gpu.loc[REGIONS, "Max_IT_Power_MW"].to_numpy(float),
        "max_facility": gpu.loc[REGIONS, "Max_Facility_Power_MW"].to_numpy(float),
        "import_limit": np.asarray([q2_grid_limit(d, r, "MaxGridImport_MW") for r in REGIONS]),
        "export_limit": np.asarray([q2_grid_limit(d, r, "MaxGridExport_MW") for r in REGIONS]),
    }


def _move_deltas(old_region, old_start, old_finish, new_region, new_start, new_finish, gpu_demand, task_power, context):
    result = {name: {} for name in ("used_gpu_instant", "used_it_power_instant_mw", "ai_energy_mwh", "facility_average_power_mw")}
    for region, start, finish, sign in ((old_region, old_start, old_finish, -1.0), (new_region, new_start, new_finish, 1.0)):
        r_idx = context["region_index"][region]
        for hour, overlap in _task_hour_overlaps(start, finish):
            key = r_idx, hour
            result["used_gpu_instant"][key] = result["used_gpu_instant"].get(key, 0.0) + sign * gpu_demand
            result["used_it_power_instant_mw"][key] = result["used_it_power_instant_mw"].get(key, 0.0) + sign * task_power
            energy = sign * task_power * overlap
            result["ai_energy_mwh"][key] = result["ai_energy_mwh"].get(key, 0.0) + energy
            result["facility_average_power_mw"][key] = result["facility_average_power_mw"].get(key, 0.0) + energy * context["pue"][r_idx]
    return result


def _evaluate_incremental_move(context, deltas, service_delta):
    arrays = context["arrays"]
    for (r_idx, hour), gpu_delta in deltas["used_gpu_instant"].items():
        gpu_after = context["used_gpu_instant"][r_idx, hour] + gpu_delta
        if gpu_after > context["available_gpu"][r_idx] + TOL or gpu_after < -TOL:
            return None, "gpu_capacity"
        it_after = arrays["NonAI_IT_Load_MW"][r_idx, hour] + context["used_it_power_instant_mw"][r_idx, hour] + deltas["used_it_power_instant_mw"].get((r_idx, hour), 0.0)
        if it_after > context["max_it"][r_idx] + TOL or it_after < -TOL:
            return None, "it_capacity"
        if it_after * context["pue"][r_idx] > context["max_facility"][r_idx] + TOL:
            return None, "facility_capacity"
    energy_delta = np.zeros(5)
    for (r_idx, hour), value in deltas["facility_average_power_mw"].items():
        before_load = context["facility_average_power_mw"][r_idx, hour]
        after_load = before_load + value
        args = (arrays["AvailableRenewable_MW"][r_idx, hour], arrays["ElectricityPrice_CNY_per_MWh"][r_idx, hour], arrays["SellPrice_CNY_per_MWh"][r_idx, hour], arrays["CarbonIntensity_tCO2_per_MWh"][r_idx, hour], context["export_limit"][r_idx])
        before, after = _q2_energy_values(before_load, *args), _q2_energy_values(after_load, *args)
        if after[3] > context["import_limit"][r_idx] + TOL:
            return None, "grid_import"
        energy_delta += np.asarray(after) - np.asarray(before)
    return {"cost": float(energy_delta[0]), "carbon": float(energy_delta[1]), "renewable_used": float(energy_delta[2]), "grid_purchase": float(energy_delta[3]), "curtailment": float(energy_delta[4]), "service": float(service_delta)}, "feasible"


def _apply_q2_deltas(context, deltas):
    for state, changes in deltas.items():
        for key, value in changes.items():
            context[state][key] += value


def _normalized_q2_components(delta, normalization):
    result = {}
    for name, sign in (("cost", 1.0), ("carbon", 1.0), ("renewable_used", -1.0), ("service", 1.0)):
        item = normalization["objectives"][name]
        result[name] = sign * float(delta[name]) / float(item["scale"]) if item["active"] else 0.0
    return result


def _q2_score(scheme, delta, normalization):
    normalized = _normalized_q2_components(delta, normalization)
    if scheme == "cost_min": score = delta["cost"]
    elif scheme == "carbon_direct": score = delta["carbon"]
    elif scheme == "renewable_max": score = -delta["renewable_used"]
    elif scheme == "service_first": score = delta["service"]
    elif scheme == "balanced": score = sum(Q2_BALANCED_WEIGHTS[name] * normalized[name] for name in Q2_BALANCED_WEIGHTS)
    else: raise ValueError(f"unknown Q2 scheme: {scheme}")
    return float(score), normalized


def _q2_candidate_options(d, task, old, latency=None):
    arrival, duration = int(task["ArrivalHour"]), float(old["FinishHour"] - old["StartHour"])
    latest, old_start = int(np.floor(min(float(task["LatestFinishHour"]), 2406.0) - duration + TOL)), int(old["StartHour"])
    starts = [arrival] if task["TaskType"] == "RealTimeInference" else sorted(set(max(arrival, min(latest, x)) for x in (arrival, latest, old_start, old_start-12, old_start-6, old_start-1, old_start+1, old_start+6, old_start+12, (arrival+latest)//2)))
    if latency is None:
        latency = d["latency"].set_index(["FromRegion", "ToRegion"])["NetworkLatency_ms"]
    regions = [r for r in REGIONS if float(latency.loc[(task["SourceRegion"], r)]) <= float(task["MaxLatency_ms"]) + TOL]
    stable = int(hashlib.sha256(f"{SEED}|{int(task.name)}".encode()).hexdigest()[:16], 16)
    if regions: shift=stable%len(regions); regions=regions[shift:]+regions[:shift]
    if starts: shift=(stable//17)%len(starts); starts=starts[shift:]+starts[:shift]
    options=[]
    for k in range(max(1, len(starts)*len(regions))):
        if not starts or not regions: break
        item=(int(starts[(k//max(1,len(regions))+k)%len(starts)]), str(regions[k%len(regions)]))
        if item not in options and item != (int(old["StartHour"]), str(old["ExecutionRegion"])):
            options.append((*item, float(latency.loc[(task["SourceRegion"], item[1])])))
    return options or [(int(old["StartHour"]), str(old["ExecutionRegion"]), float(old["NetworkLatency_ms"]))]


def build_q2_common_candidate_pool(d, workload, baseline_schedule, limit=Q2_MOVE_LIMIT):
    """Build an objective-independent and globally semantic-unique base pool."""
    schedule = baseline_schedule.copy().reset_index(drop=True)
    source = workload.set_index("TaskID")
    by_task = schedule.reset_index().set_index("TaskID")
    task_ids = sorted(map(int, by_task.index))
    latency = d["latency"].set_index(["FromRegion", "ToRegion"])["NetworkLatency_ms"]
    power = d["power"].set_index("TaskType")["GPU_Power_MW_per_EquivalentGPU"].to_dict()
    cache = {}
    for task_id in task_ids:
        old, task = by_task.loc[task_id], source.loc[task_id]
        baseline_key = (str(old["ExecutionRegion"]), int(old["StartHour"]))
        unique, seen = [], {baseline_key}
        for start, region, candidate_latency in _q2_candidate_options(d, task, old, latency):
            key = (str(region), int(start))
            if key in seen:
                continue
            seen.add(key)
            unique.append((int(start), str(region), float(candidate_latency)))
        cache[task_id] = unique[: max(0, Q2_MAX_CANDIDATES_PER_TASK - 1)]

    rows, semantic_seen, order = [], set(), 0
    for layer in range(1, Q2_MAX_CANDIDATES_PER_TASK + 1):
        for task_id in task_ids:
            if len(rows) >= int(limit):
                break
            old, task, alternatives = by_task.loc[task_id], source.loc[task_id], cache[task_id]
            if layer == 1:
                start, region = int(old["StartHour"]), str(old["ExecutionRegion"])
                candidate_latency, is_baseline = float(old["NetworkLatency_ms"]), True
            else:
                rank = layer - 2
                if rank >= len(alternatives):
                    continue
                start, region, candidate_latency = alternatives[rank]
                is_baseline = False
            semantic_key = (task_id, region, start)
            if semantic_key in semantic_seen:
                continue
            semantic_seen.add(semantic_key)
            order += 1
            gpu_demand = float(old["GPU_Demand"])
            rows.append({
                "CandidateID": f"Q2C{order:06d}", "BaseCandidateID": f"Q2C{order:06d}",
                "TaskID": task_id, "ScheduleRowIndex": int(old["index"]), "Region": region,
                "OriginalRegion": str(old["ExecutionRegion"]), "OriginalStart": float(old["StartHour"]),
                "CandidateStart": int(start), "Duration": float(old["FinishHour"]-old["StartHour"]),
                "GPUType": str(task["TaskType"]), "GPU_Demand": gpu_demand,
                "TaskPower_MW": gpu_demand * float(power[task["TaskType"]]),
                "CandidateLayer": layer, "GenerationOrder": order,
                "DeterministicOrderKey": f"seed={SEED}|task={task_id}|layer={layer}", "Seed": SEED,
                "CandidateLatency_ms": candidate_latency, "TaskConstraintFeasible": True,
                "IsBaselineAssignment": is_baseline, "HasAlternativeCandidate": bool(alternatives),
                "NoAlternative": not bool(alternatives),
            })
        if len(rows) >= int(limit):
            break
    pool = pd.DataFrame(rows)
    pool["HighPowerTask"] = pool["TaskPower_MW"].ge(float(pool["TaskPower_MW"].quantile(0.90)))
    pool["HighGPUDemandTask"] = pool["GPU_Demand"].ge(float(pool["GPU_Demand"].quantile(0.90)))
    if len(pool) != int(limit):
        raise RuntimeError(f"Q2-POOL-020: expected {int(limit)} unique base candidates, got {len(pool)}")
    if not pool["BaseCandidateID"].is_unique:
        raise RuntimeError("Q2-POOL-021: duplicate BaseCandidateID")
    duplicate_count = int(pool.duplicated(["TaskID", "Region", "CandidateStart"]).sum())
    if duplicate_count:
        raise RuntimeError(f"Q2-POOL-022: {duplicate_count} semantic duplicate candidates")
    return pool


def _candidate_delta_inputs(d, schedule, task_source, power, candidate, context):
    row_idx=int(candidate.ScheduleRowIndex); old=schedule.loc[row_idx]; task=task_source.loc[int(candidate.TaskID)]
    duration=float(old["FinishHour"]-old["StartHour"]); new_start=float(candidate.CandidateStart); new_finish=new_start+duration
    task_power=float(old["GPU_Demand"])*float(power[task["TaskType"]])
    deltas=_move_deltas(str(old["ExecutionRegion"]),float(old["StartHour"]),float(old["FinishHour"]),str(candidate.Region),new_start,new_finish,float(old["GPU_Demand"]),task_power,context)
    service_delta=float(old["GPU_Demand"])*duration/context["service_denominator"]*(float(candidate.CandidateLatency_ms)-float(old["NetworkLatency_ms"])+Q2_SERVICE_WAIT_FACTOR*(new_start-float(old["StartHour"])))
    return row_idx,old,task,duration,new_start,new_finish,deltas,service_delta


def derive_q2_objective_normalization(d, workload, baseline_schedule, pool):
    context=_q2_context(d,baseline_schedule); source=workload.set_index("TaskID"); power=d["power"].set_index("TaskType")["GPU_Power_MW_per_EquivalentGPU"].to_dict()
    values={name:[] for name in ("cost","carbon","renewable_used","service")}; flags=[]; reasons=[]
    zero={name:0.0 for name in ("cost","carbon","renewable_used","grid_purchase","curtailment","service")}
    for c in pool.itertuples(index=False):
        inputs=_candidate_delta_inputs(d,baseline_schedule,source,power,c,context); old=inputs[1]
        delta,reason=(zero,"no_change") if (str(c.Region)==str(old["ExecutionRegion"]) and abs(float(c.CandidateStart)-float(old["StartHour"]))<=TOL) else _evaluate_incremental_move(context,inputs[-2],inputs[-1])
        flags.append(delta is not None); reasons.append(reason)
        if delta is not None:
            for name in values: values[name].append(float(delta[name]))
    pool=pool.copy(); pool["BaselineResourceFeasible"]=flags; pool["BaselineRejectReason"]=reasons
    objectives={}
    for name,direction in (("cost","min"),("carbon","min"),("renewable_used","max"),("service","min")):
        v=np.asarray(values[name]); ideal=float(v.min() if direction=="min" else v.max()); nadir=float(v.max() if direction=="min" else v.min()); span=abs(nadir-ideal)
        objectives[name]={"direction":direction,"unit":{"cost":"CNY","carbon":"tCO2","renewable_used":"MWh","service":"weighted_service_unit"}[name],"ideal":ideal,"nadir":nadir,"scale":float(span if span>1e-12 else 1.0),"active":bool(span>1e-12),"weight":Q2_BALANCED_WEIGHTS[name],"minimum":float(v.min()),"maximum":float(v.max())}
    return {"schema_version":2,"source":"all baseline-feasible common-candidate deltas","candidate_count":len(pool),"baseline_feasible_count":int(sum(flags)),"method":"public ideal/nadir range","objectives":objectives,"weights_sum":1.0,"hand_tuned_to_final_result":False},pool


def q2_renewable_used_mwh(flow):
    return float((flow["RenewableUse_MW"].to_numpy(float)+flow["OptimizedGridSell_MW"].to_numpy(float)).sum())


def _summarize_q2_schedule(d, workload, schedule, normalization):
    flow,cost,carbon,renewable=no_storage_energy(d,schedule); feasible,used_gpu=schedule_candidate_feasible(d,workload,schedule)
    if not feasible: raise RuntimeError("CON-Q2-1: checkpoint full task audit failed")
    audit=build_constraint_audit(d,workload,schedule,used_gpu)
    if not audit["constraint_satisfied"].all(): raise RuntimeError("CON-Q2-1: checkpoint residual failed")
    latency,quality,migrated=service_metrics(schedule)
    numeric=audit.drop(columns=["Region","constraint_satisfied"],errors="ignore").to_numpy(float)
    return flow,audit,{"cost_CNY":float(cost),"carbon_tCO2":float(carbon),"renewable_utilization":float(renewable),"renewable_used_MWh":q2_renewable_used_mwh(flow),"network_latency_ms":float(latency),"service_objective":q2_service_objective(schedule),"service_quality":float(quality),"migration_count":int(migrated),"schedule_sha256":_schedule_hash(schedule),"full_task_audit_passed":True,"max_constraint_residual":float(np.maximum(numeric,0.0).max())}


def _append_csv_rows(path, rows):
    if rows:
        path = Path(path)
        pd.DataFrame(rows).to_csv(path, mode="a", header=not path.exists(), index=False)
        rows.clear()


def _q2_main_value(scheme, metrics):
    if scheme == "cost_min": return float(metrics["cost_CNY"])
    if scheme == "carbon_direct": return float(metrics["carbon_tCO2"])
    if scheme == "renewable_max": return -float(metrics["renewable_used_MWh"])
    if scheme == "service_first": return float(metrics["service_objective"])
    if scheme == "balanced": return float(metrics["balanced_full_score"])
    raise ValueError(scheme)


def _context_checkpoint_audit(d, workload, schedule, context, cumulative, baseline, normalization, scheme, pass_id):
    rebuilt = rebuild_schedule_resources(d, schedule)
    if rebuilt is None:
        raise RuntimeError(f"Q2-CONTEXT-001: rebuild failed {scheme} pass {pass_id}")
    rt = d["region"].sort_values(["Region", "Hour"])
    nonai = np.vstack([rt.loc[rt["Region"].eq(r), "NonAI_IT_Load_MW"].to_numpy(float) for r in REGIONS])
    expected_facility = (nonai + rebuilt["ai_energy_mwh"]) * context["pue"][:, None]
    residuals, locations = {}, {}
    for name, expected in (("used_gpu_instant", rebuilt["used_gpu_instant"]), ("used_it_power_instant_mw", rebuilt["used_it_power_instant_mw"]), ("ai_energy_mwh", rebuilt["ai_energy_mwh"]), ("facility_average_power_mw", expected_facility)):
        diff = np.abs(context[name] - expected)
        idx = np.unravel_index(int(np.argmax(diff)), diff.shape)
        residuals[name] = float(diff[idx]); locations[name] = f"{REGIONS[idx[0]]}:hour={idx[1]}"
    flow, audit, full = _summarize_q2_schedule(d, workload, schedule, normalization)
    full_balanced = _full_balanced_score(full, baseline, normalization)
    aggregate = {
        "cost_CNY": abs(float(cumulative["cost"])-float(full["cost_CNY"])),
        "carbon_tCO2": abs(float(cumulative["carbon"])-float(full["carbon_tCO2"])),
        "renewable_used_MWh": abs(float(cumulative["renewable_used"])-float(full["renewable_used_MWh"])),
        "service_objective": abs(float(cumulative["service"])-float(full["service_objective"])),
        "balanced_full_score": abs(float(cumulative["balanced_score"])-float(full_balanced)),
    }
    residuals.update(aggregate); locations.update({k: "aggregate" for k in aggregate})
    scales = {
        "used_gpu_instant": max(float(np.max(np.abs(rebuilt["used_gpu_instant"]))), 1.0),
        "used_it_power_instant_mw": max(float(np.max(np.abs(rebuilt["used_it_power_instant_mw"]))), 1.0),
        "ai_energy_mwh": max(float(np.max(np.abs(rebuilt["ai_energy_mwh"]))), 1.0),
        "facility_average_power_mw": max(float(np.max(np.abs(expected_facility))), 1.0),
        "cost_CNY": max(abs(float(full["cost_CNY"])), 1.0),
        "carbon_tCO2": max(abs(float(full["carbon_tCO2"])), 1.0),
        "renewable_used_MWh": max(abs(float(full["renewable_used_MWh"])), 1.0),
        "service_objective": max(abs(float(full["service_objective"])), 1.0),
        "balanced_full_score": max(abs(float(full_balanced)), 1.0),
    }
    relative = {k: residuals[k]/scales[k] for k in residuals}
    worst = max(residuals, key=residuals.get)
    passed = all(residuals[k] <= 1e-6 or relative[k] <= 1e-8 for k in residuals)
    row = {"Scheme": scheme, "PassID": int(pass_id), "schedule_sha256": full["schedule_sha256"], "max_constraint_residual": full["max_constraint_residual"], "context_full_recompute_residual": max(residuals.values()), "max_absolute_residual": max(residuals.values()), "max_relative_residual": max(relative.values()), "worst_quantity": worst, "worst_location": locations[worst], "audit_passed": bool(passed)}
    for k, v in residuals.items(): row[f"abs_residual_{k}"] = v
    for k, v in relative.items(): row[f"rel_residual_{k}"] = v
    if not passed:
        raise RuntimeError(f"Q2-CONTEXT-002: {scheme} pass {pass_id} drift {row}")
    return row, full, flow, audit


def _candidate_pressure(context, deltas):
    capacity_ratio = grid_ratio = 0.0; grid_violation = False
    arrays = context["arrays"]
    for key, gpu_delta in deltas["used_gpu_instant"].items():
        r, hour = key
        gpu = context["used_gpu_instant"][key] + gpu_delta
        it = arrays["NonAI_IT_Load_MW"][key] + context["used_it_power_instant_mw"][key] + deltas["used_it_power_instant_mw"].get(key, 0.0)
        capacity_ratio = max(capacity_ratio, gpu/max(context["available_gpu"][r], 1e-12), it/max(context["max_it"][r], 1e-12), it*context["pue"][r]/max(context["max_facility"][r], 1e-12))
    for key, value in deltas["facility_average_power_mw"].items():
        r, hour = key; after_load = context["facility_average_power_mw"][key] + value
        args = (arrays["AvailableRenewable_MW"][key], arrays["ElectricityPrice_CNY_per_MWh"][key], arrays["SellPrice_CNY_per_MWh"][key], arrays["CarbonIntensity_tCO2_per_MWh"][key], context["export_limit"][r])
        buy = _q2_energy_values(after_load, *args)[3]
        ratio = buy/max(context["import_limit"][r], 1e-12)
        grid_ratio = max(grid_ratio, ratio); grid_violation = grid_violation or buy > context["import_limit"][r] + TOL
    return float(capacity_ratio), float(grid_ratio), bool(grid_violation)


def _candidate_full_recompute_audit(d, workload, schedule, context, candidate, inputs, delta, reason, accepted_move, scheme, pass_id, forced_case=None):
    row_idx, old, task, duration, new_start, new_finish, deltas, service_delta = inputs
    before_flow, before_cost, before_carbon, _ = no_storage_energy(d, schedule)
    before_re = q2_renewable_used_mwh(before_flow); before_service = q2_service_objective(schedule)
    after = schedule.copy().reset_index(drop=True)
    after.at[row_idx, "ExecutionRegion"] = str(candidate.Region); after.at[row_idx, "StartHour"] = new_start; after.at[row_idx, "FinishHour"] = new_finish
    after.at[row_idx, "WaitHour"] = new_start-float(task["ArrivalHour"]); after.at[row_idx, "NetworkLatency_ms"] = float(candidate.CandidateLatency_ms)
    after_flow, after_cost, after_carbon, _ = no_storage_energy(d, after)
    feasible_task, used_gpu = schedule_candidate_feasible(d, workload, after)
    after_resources = rebuild_schedule_resources(d, after)
    if after_resources is None:
        raise RuntimeError("Q2-DELTA-020: full candidate resource rebuild failed")
    rt = d["region"].sort_values(["Region", "Hour"])
    nonai = np.vstack([rt.loc[rt["Region"].eq(r), "NonAI_IT_Load_MW"].to_numpy(float) for r in REGIONS])
    after_facility = (nonai+after_resources["ai_energy_mwh"])*context["pue"][:, None]
    full_grid_ok = True
    for r_idx in range(len(REGIONS)):
        for hour in range(after_facility.shape[1]):
            args = (context["arrays"]["AvailableRenewable_MW"][r_idx, hour], context["arrays"]["ElectricityPrice_CNY_per_MWh"][r_idx, hour], context["arrays"]["SellPrice_CNY_per_MWh"][r_idx, hour], context["arrays"]["CarbonIntensity_tCO2_per_MWh"][r_idx, hour], context["export_limit"][r_idx])
            if _q2_energy_values(after_facility[r_idx, hour], *args)[3] > context["import_limit"][r_idx] + TOL:
                full_grid_ok = False; break
        if not full_grid_ok: break
    zero = {name: 0.0 for name in ("cost", "carbon", "renewable_used", "grid_purchase", "curtailment", "service")}
    incremental = zero if reason == "no_change" else delta
    residuals = {}
    if incremental is not None:
        residuals.update({
            "cost_CNY": abs(float(incremental["cost"])-(after_cost-before_cost)),
            "carbon_tCO2": abs(float(incremental["carbon"])-(after_carbon-before_carbon)),
            "renewable_used_MWh": abs(float(incremental["renewable_used"])-(q2_renewable_used_mwh(after_flow)-before_re)),
            "service_objective": abs(float(incremental["service"])-(q2_service_objective(after)-before_service)),
        })
    for state, expected in (("used_gpu_instant", after_resources["used_gpu_instant"]), ("used_it_power_instant_mw", after_resources["used_it_power_instant_mw"]), ("ai_energy_mwh", after_resources["ai_energy_mwh"]), ("facility_average_power_mw", after_facility)):
        predicted = context[state].copy()
        for key, value in deltas[state].items(): predicted[key] += value
        residuals[state] = float(np.max(np.abs(predicted-expected)))
    cap_ratio, grid_ratio, grid_violation = _candidate_pressure(context, deltas)
    categories = set()
    if forced_case: categories.add(forced_case)
    if accepted_move: categories.add("accepted")
    elif reason == "no_change": categories.add("no_change")
    elif reason in {"gpu_capacity", "it_capacity", "facility_capacity"}: categories.add("capacity_rejected")
    elif reason == "grid_import": categories.add("grid_rejected")
    else: categories.add("feasible_but_rejected")
    if grid_violation: categories.add("grid_rejected")
    if float(candidate.Duration) < 1-TOL: categories.add("duration_lt_1h")
    if abs(float(candidate.Duration)-round(float(candidate.Duration))) > TOL: categories.add("fractional_duration")
    else: categories.add("integer_duration")
    if 1+TOL < float(candidate.Duration) < 2-TOL: categories.add("fractional_cross_two_hours")
    if abs(float(candidate.CandidateStart)+float(candidate.Duration)-round(float(candidate.CandidateStart)+float(candidate.Duration))) <= TOL: categories.add("hour_boundary")
    if float(candidate.CandidateStart) < 2400 < float(candidate.CandidateStart)+float(candidate.Duration): categories.add("cross_2399_2400")
    if str(candidate.Region) != str(old["ExecutionRegion"]): categories.add("region_migration")
    if bool(candidate.IsBaselineAssignment) and (str(old["ExecutionRegion"]) != str(candidate.Region) or abs(float(old["StartHour"])-float(candidate.CandidateStart)) > TOL): categories.add("return_to_baseline")
    if bool(candidate.HighPowerTask): categories.add("high_power_task")
    if bool(candidate.HighGPUDemandTask): categories.add("high_gpu_demand_task")
    categories.add("random_fixed_seed")
    max_abs = max(residuals.values()) if residuals else 0.0
    scale = max(abs(after_cost-before_cost), abs(after_carbon-before_carbon), abs(q2_renewable_used_mwh(after_flow)-before_re), abs(q2_service_objective(after)-before_service), 1.0)
    max_rel = max_abs/scale
    rejection_consistent = bool((incremental is not None and feasible_task and full_grid_ok) or (incremental is None and not (feasible_task and full_grid_ok)))
    return {"case": forced_case or sorted(categories)[0], "sample_categories": "|".join(sorted(categories)), "Scheme": scheme, "PassID": int(pass_id), "CandidateID": str(candidate.BaseCandidateID), "BaseCandidateID": str(candidate.BaseCandidateID), "TaskID": int(candidate.TaskID), "Duration": float(candidate.Duration), "CandidateStart": float(candidate.CandidateStart), "incremental_reason": reason, "accepted": bool(accepted_move), "full_task_feasible": bool(feasible_task), "full_grid_feasible": bool(full_grid_ok), "rejection_consistent": rejection_consistent, "capacity_pressure_ratio": cap_ratio, "grid_import_pressure_ratio": grid_ratio, **{f"abs_residual_{k}": v for k, v in residuals.items()}, "max_absolute_residual": max_abs, "max_relative_residual": max_rel, "worst_quantity": max(residuals, key=residuals.get) if residuals else "none"}


def _audit_fixed_positions(pool, scheme, pass_id):
    rng = np.random.default_rng(SEED + 1000*Q2_DIRECT_SCHEMES.index(scheme) + pass_id)
    selected = rng.choice(len(pool), size=min(Q2_CANDIDATE_AUDIT_PER_SCHEME_PASS, len(pool)), replace=False)
    return set(pool.iloc[selected]["BaseCandidateID"].astype(str))


def _optimize_q2_scheme(d, workload, baseline_schedule, scheme, pool, normalization, max_passes=Q2_MAX_PASSES, candidate_limit=None, stage="direct", stream_direct=False, collect_trace=False, baseline_metrics=None):
    schedule = baseline_schedule.copy().reset_index(drop=True); context = _q2_context(d, schedule)
    source = workload.set_index("TaskID"); power = d["power"].set_index("TaskType")["GPU_Power_MW_per_EquivalentGPU"].to_dict()
    base_pool = pool.iloc[:len(pool) if candidate_limit is None else int(candidate_limit)].copy()
    if baseline_metrics is None: _, _, baseline_metrics = _summarize_q2_schedule(d, workload, baseline_schedule, normalization)
    cumulative = {"cost": baseline_metrics["cost_CNY"], "carbon": baseline_metrics["carbon_tCO2"], "renewable_used": baseline_metrics["renewable_used_MWh"], "service": baseline_metrics["service_objective"], "balanced_score": 0.0}
    snapshots, schedules, context_rows, candidate_audits, collected = [], {}, [], [], []
    cumulative_attempted = cumulative_feasible = cumulative_accepted = state_no = 0; trace_objective = 0.0
    previous_main = _q2_main_value(scheme, {**baseline_metrics, "balanced_full_score": 0.0})
    stable_flags, convergence_pass, convergence_reason = [], None, None
    sequence_hasher, pass_hashes = hashlib.sha256(), []
    pass_trace_path = RESULT_DIR/"q2_pass_search_trace.csv"; legacy_trace_path = RESULT_DIR/"q2_search_trace.csv"; balanced_path = RESULT_DIR/"q2_balanced_score_audit.csv"
    for pass_id in range(1, int(max_passes)+1):
        pass_before = previous_main; pass_accepted = pass_feasible = pass_no_change = 0
        audit_targets = _audit_fixed_positions(base_pool, scheme, pass_id) if stage == "direct" else set()
        dynamic_needed = {"accepted", "feasible_but_rejected", "capacity_rejected", "grid_rejected", "no_change", "return_to_baseline"} if stage == "direct" else set()
        pass_rows, legacy_rows, balanced_rows, audited_ids = [], [], [], set()
        pass_hasher = hashlib.sha256()
        for c in base_pool.itertuples(index=False):
            check_deadline(f"q2.{stage}.{scheme}.pass{pass_id}")
            cumulative_attempted += 1; attempt_id = f"P{pass_id:02d}-{c.BaseCandidateID}"
            sequence_hasher.update((attempt_id+"\n").encode()); pass_hasher.update((str(c.BaseCandidateID)+"\n").encode())
            inputs = _candidate_delta_inputs(d, schedule, source, power, c, context)
            row_idx, old, task, duration, new_start, new_finish, deltas, service_delta = inputs
            before_score = float(trace_objective); accepted_move = False
            is_no_change = str(c.Region) == str(old["ExecutionRegion"]) and abs(new_start-float(old["StartHour"])) <= TOL
            if is_no_change:
                delta = {name: 0.0 for name in ("cost", "carbon", "renewable_used", "grid_purchase", "curtailment", "service")}
                reason = "no_change"; normalized = {name: 0.0 for name in Q2_BALANCED_WEIGHTS}; score = 0.0; pass_no_change += 1
            else:
                delta, reason = _evaluate_incremental_move(context, deltas, service_delta)
                if delta is None: normalized = {name: np.nan for name in Q2_BALANCED_WEIGHTS}; score = np.nan
                else:
                    pass_feasible += 1; cumulative_feasible += 1; score, normalized = _q2_score(scheme, delta, normalization)
                    if score < -1e-12: accepted_move = True; reason = "accepted"
            categories_now = set()
            if accepted_move: categories_now.add("accepted")
            elif reason == "no_change": categories_now.add("no_change")
            elif reason in {"gpu_capacity", "it_capacity", "facility_capacity"}: categories_now.add("capacity_rejected")
            elif delta is not None: categories_now.add("feasible_but_rejected")
            if "grid_rejected" in dynamic_needed and reason in {"gpu_capacity", "it_capacity", "facility_capacity"} and _candidate_pressure(context, deltas)[2]: categories_now.add("grid_rejected")
            if bool(c.IsBaselineAssignment) and (str(old["ExecutionRegion"]) != str(c.Region) or abs(float(old["StartHour"])-float(c.CandidateStart)) > TOL): categories_now.add("return_to_baseline")
            do_audit = stage == "direct" and (str(c.BaseCandidateID) in audit_targets or bool(categories_now & dynamic_needed)) and str(c.BaseCandidateID) not in audited_ids
            if do_audit:
                audit_row = _candidate_full_recompute_audit(d, workload, schedule, context, c, inputs, delta, reason, accepted_move, scheme, pass_id, "random_feasible_move" if str(c.BaseCandidateID) in audit_targets else None)
                candidate_audits.append(audit_row); audited_ids.add(str(c.BaseCandidateID)); dynamic_needed -= set(audit_row["sample_categories"].split("|"))
            if accepted_move:
                _apply_q2_deltas(context, deltas)
                schedule.at[row_idx, "ExecutionRegion"] = str(c.Region); schedule.at[row_idx, "StartHour"] = new_start; schedule.at[row_idx, "FinishHour"] = new_finish
                schedule.at[row_idx, "WaitHour"] = new_start-float(task["ArrivalHour"]); schedule.at[row_idx, "NetworkLatency_ms"] = float(c.CandidateLatency_ms)
                for name in ("cost", "carbon", "renewable_used", "service"): cumulative[name] += float(delta[name])
                cumulative["balanced_score"] += float(score if scheme == "balanced" else 0.0)
                trace_objective += float(score)
                pass_accepted += 1; cumulative_accepted += 1; state_no += 1
            trace_row = {"Stage": stage, "Scheme": scheme, "AttemptID": attempt_id, "PassID": pass_id, "CandidateID": str(c.BaseCandidateID), "BaseCandidateID": str(c.BaseCandidateID), "TaskID": int(c.TaskID), "attempted": True, "feasible": bool(delta is not None), "accepted": bool(accepted_move), "reject_reason": str(reason), "delta_main": np.nan if delta is None else float(score), "StateID": f"{scheme}:accepted-{state_no}"}
            if stream_direct: pass_rows.append(trace_row)
            detail = {**trace_row, "CandidateStart": float(c.CandidateStart), "CandidateRegion": str(c.Region), "delta_cost": np.nan if delta is None else delta["cost"], "delta_carbon": np.nan if delta is None else delta["carbon"], "delta_renewable": np.nan if delta is None else delta["renewable_used"], "delta_service": np.nan if delta is None else delta["service"], "normalized_cost": normalized["cost"], "normalized_carbon": normalized["carbon"], "normalized_renewable": normalized["renewable_used"], "normalized_service": normalized["service"], "cost_contribution": Q2_BALANCED_WEIGHTS["cost"]*normalized["cost"], "carbon_contribution": Q2_BALANCED_WEIGHTS["carbon"]*normalized["carbon"], "renewable_contribution": Q2_BALANCED_WEIGHTS["renewable_used"]*normalized["renewable_used"], "service_contribution": Q2_BALANCED_WEIGHTS["service"]*normalized["service"], "total_score": score, "objective_before": before_score, "objective_after": float(trace_objective)}
            if stream_direct and pass_id == 1: legacy_rows.append(detail)
            if stream_direct and pass_id == 1 and scheme == "balanced": balanced_rows.append(detail)
            if collect_trace: collected.append(detail)
            if len(pass_rows) >= 5000: _append_csv_rows(pass_trace_path, pass_rows)
            if len(legacy_rows) >= 5000: _append_csv_rows(legacy_trace_path, legacy_rows)
            if len(balanced_rows) >= 5000: _append_csv_rows(balanced_path, balanced_rows)
        _append_csv_rows(pass_trace_path, pass_rows); _append_csv_rows(legacy_trace_path, legacy_rows); _append_csv_rows(balanced_path, balanced_rows)
        pass_hashes.append({"PassID": pass_id, "base_candidate_sequence_sha256": pass_hasher.hexdigest()})
        cumulative["balanced_score"] = _full_balanced_score({"cost_CNY": cumulative["cost"], "carbon_tCO2": cumulative["carbon"], "renewable_used_MWh": cumulative["renewable_used"], "service_objective": cumulative["service"]}, baseline_metrics, normalization)
        context_row, full, flow, audit = _context_checkpoint_audit(d, workload, schedule, context, cumulative, baseline_metrics, normalization, scheme, pass_id)
        full["balanced_full_score"] = _full_balanced_score(full, baseline_metrics, normalization)
        current_main = _q2_main_value(scheme, full)
        relative_improvement = max(0.0, pass_before-current_main)/max(abs(pass_before), abs(current_main), 1.0 if scheme in {"cost_min", "balanced"} else 1e-12)
        accepted_rate = pass_accepted/max(1, len(base_pool)); hard_ok = bool(full["full_task_audit_passed"] and context_row["audit_passed"])
        stable = bool(relative_improvement <= Q2_CONVERGENCE_MAIN_RTOL and accepted_rate <= Q2_CONVERGENCE_ACCEPTED_RATE and hard_ok)
        stable_flags.append(stable)
        if convergence_pass is None and hard_ok and pass_accepted == 0: convergence_pass, convergence_reason = pass_id, "zero_acceptance_full_pass"
        if convergence_pass is None and len(stable_flags) >= Q2_CONVERGENCE_INTERVALS and all(stable_flags[-Q2_CONVERGENCE_INTERVALS:]): convergence_pass, convergence_reason = pass_id, "main_objective_and_accepted_rate_stable"
        auxiliary_changes = {name: _relative_change(snapshots[-1][name], full[name], 1.0 if name == "cost_CNY" else 1e-12) if snapshots else np.nan for name in ("cost_CNY", "carbon_tCO2", "renewable_used_MWh", "service_objective")}
        snapshot = {**full, "Scheme": scheme, "scheme": scheme, "PassID": pass_id, "base_candidate_count": len(base_pool), "attempted": len(base_pool), "feasible": pass_feasible, "no_change": pass_no_change, "accepted": pass_accepted, "rejected": len(base_pool)-pass_accepted, "objective_before": pass_before, "objective_after": current_main, "relative_improvement": relative_improvement, "accepted_rate": accepted_rate, "attempted_candidates": cumulative_attempted, "feasible_candidates": cumulative_feasible, "accepted_improvements": cumulative_accepted, "checked_candidates": cumulative_attempted, "task_coverage_rate": float(base_pool["TaskID"].nunique()/len(workload)), "alternative_task_coverage_rate": float(base_pool.loc[~base_pool["IsBaselineAssignment"], "TaskID"].nunique()/len(workload)), "context_full_recompute_residual": context_row["context_full_recompute_residual"], "context_full_recompute_relative_residual": context_row["max_relative_residual"], "termination_reason": convergence_reason if convergence_pass == pass_id else "pass_completed", "converged_by_this_pass": bool(convergence_pass is not None and convergence_pass <= pass_id), "max_auxiliary_relative_change": float(np.nanmax(list(auxiliary_changes.values()))) if snapshots else np.nan}
        snapshots.append(snapshot); context_rows.append(context_row); schedules[pass_id] = schedule.copy(); previous_main = current_main
    if convergence_pass is None: convergence_reason = "max_passes_reached"
    if stage == "direct" and len(candidate_audits) < Q2_CANDIDATE_AUDIT_PER_SCHEME_PASS*int(max_passes): raise RuntimeError(f"Q2-DELTA-021: insufficient samples for {scheme}")
    return {"terminal_schedule": schedule, "snapshots": pd.DataFrame(snapshots), "trace": pd.DataFrame(collected), "checkpoint_schedules": schedules, "context_audit": pd.DataFrame(context_rows), "candidate_audit": pd.DataFrame(candidate_audits), "convergence_pass": convergence_pass, "termination_reason": convergence_reason, "attempt_sequence_sha256": sequence_hasher.hexdigest(), "pass_sequence_hashes": pass_hashes}


def _relative_change(left,right,floor=1e-12):
    return abs(float(right)-float(left))/max(abs(float(left)),abs(float(right)),float(floor))


def _full_balanced_score(metrics, baseline, normalization, weights=None):
    weights=Q2_BALANCED_WEIGHTS if weights is None else weights
    delta={"cost":metrics["cost_CNY"]-baseline["cost_CNY"],"carbon":metrics["carbon_tCO2"]-baseline["carbon_tCO2"],"renewable_used":metrics["renewable_used_MWh"]-baseline["renewable_used_MWh"],"service":metrics["service_objective"]-baseline["service_objective"]}
    normalized=_normalized_q2_components(delta,normalization)
    return float(sum(weights[name]*normalized[name] for name in weights))


def _evaluate_common_convergence(frame):
    rows, convergence_passes = [], {}
    main = {"cost_min":"cost_CNY", "carbon_direct":"carbon_tCO2", "renewable_max":"renewable_used_MWh", "service_first":"service_objective", "balanced":"balanced_full_score"}
    for scheme in Q2_DIRECT_SCHEMES:
        group = frame.loc[frame["scheme"].eq(scheme)].sort_values("PassID")
        matched = group.loc[group["converged_by_this_pass"].astype(bool)]
        convergence_passes[scheme] = None if matched.empty else int(matched.iloc[0]["PassID"])
        for row in group.itertuples(index=False):
            rows.append({"scheme": scheme, "PassID": int(row.PassID), "pass_complete": int(row.attempted) == int(row.base_candidate_count), "main_metric": main[scheme], "main_relative_improvement": float(row.relative_improvement), "accepted_move_rate": float(row.accepted_rate), "auxiliary_max_relative_change": float(row.max_auxiliary_relative_change) if np.isfinite(row.max_auxiliary_relative_change) else np.nan, "hard_and_context_audit_passed": bool(row.full_task_audit_passed and (row.context_full_recompute_residual <= 1e-6 or row.context_full_recompute_relative_residual <= 1e-8)), "auxiliary_metrics_blocking": False, "scheme_converged_by_this_pass": bool(row.converged_by_this_pass)})
    if all(v is not None for v in convergence_passes.values()):
        common = max(convergence_passes.values()); status = "converged"; reason = "all direct schemes satisfied declared neighborhood-stability rule by common completed pass"
    else:
        common = int(frame["PassID"].max()); status = "nonconverged"
        reason = "max common pass reached; nonconverged schemes=" + "|".join(k for k,v in convergence_passes.items() if v is None)
    return (common, status, reason, convergence_passes), pd.DataFrame(rows)


def run_q2_weight_sensitivity(direct,baseline,normalization):
    scenarios={"equal":(.25,.25,.25,.25),"cost_tilt":(.40,.20,.20,.20),"carbon_tilt":(.20,.40,.20,.20),"renewable_tilt":(.20,.20,.40,.20),"service_tilt":(.20,.20,.20,.40)}; names=("cost","carbon","renewable_used","service"); rows=[]
    for label,vector in scenarios.items():
        weights=dict(zip(names,vector)); scores={s:_full_balanced_score(v["summary"],baseline,normalization,weights) for s,v in direct.items()}; selected=min(scores,key=lambda s:(scores[s],s))
        for scheme,score in scores.items(): rows.append({"weight_scenario":label,"scheme":scheme,**{f"weight_{n}":weights[n] for n in names},"score":score,"selected":scheme==selected,"selected_scheme":selected,"schedule_sha256":direct[scheme]["summary"]["schedule_sha256"],"formal_balanced_schedule":scheme=="balanced","q4_baseline_changed_from_formal_balanced":selected!="balanced"})
    return pd.DataFrame(rows)


def run_q2_incremental_consistency_audit(d,workload,baseline_schedule,pool):
    context=_q2_context(d,baseline_schedule); source=workload.set_index("TaskID"); power=d["power"].set_index("TaskType")["GPU_Power_MW_per_EquivalentGPU"].to_dict()
    categories={"duration_lt_1h":lambda c:c.Duration<1-TOL,"fractional_cross_two_hours":lambda c:1+TOL<c.Duration<2-TOL,"integer_duration":lambda c:abs(c.Duration-round(c.Duration))<=TOL,"hour_boundary":lambda c:abs(c.CandidateStart+c.Duration-round(c.CandidateStart+c.Duration))<=TOL,"cross_2399_2400":lambda c:c.CandidateStart<2400<c.CandidateStart+c.Duration}
    rows=[]; used=set()
    for label,predicate in categories.items():
        for c in pool.itertuples(index=False):
            if c.BaseCandidateID in used or c.IsBaselineAssignment or not predicate(c): continue
            inputs=_candidate_delta_inputs(d,baseline_schedule,source,power,c,context); delta,reason=_evaluate_incremental_move(context,inputs[-2],inputs[-1])
            if delta is not None:
                rows.append(_candidate_full_recompute_audit(d,workload,baseline_schedule,context,c,inputs,delta,reason,False,"baseline_edge_audit",0,label)); used.add(c.BaseCandidateID); break
    rng=np.random.default_rng(SEED)
    for index in rng.choice(len(pool),size=min(512,len(pool)),replace=False):
        c=next(pool.iloc[[int(index)]].itertuples(index=False))
        if c.BaseCandidateID in used or c.IsBaselineAssignment: continue
        inputs=_candidate_delta_inputs(d,baseline_schedule,source,power,c,context); delta,reason=_evaluate_incremental_move(context,inputs[-2],inputs[-1])
        if delta is not None:
            rows.append(_candidate_full_recompute_audit(d,workload,baseline_schedule,context,c,inputs,delta,reason,False,"baseline_edge_audit",0,"random_feasible_move")); used.add(c.BaseCandidateID)
        if sum(x["case"]=="random_feasible_move" for x in rows)>=16: break
    # The production data make the grid-import cap redundant under the tighter
    # facility cap.  Exercise the grid rejection branch as an explicit negative
    # control by tightening only the audit copy of the import limit.
    for c in pool.loc[~pool["IsBaselineAssignment"]].itertuples(index=False):
        inputs=_candidate_delta_inputs(d,baseline_schedule,source,power,c,context)
        delta,reason=_evaluate_incremental_move(context,inputs[-2],inputs[-1])
        if delta is None: continue
        audit_context=dict(context); audit_context["import_limit"]=np.zeros_like(context["import_limit"])
        audit_delta,audit_reason=_evaluate_incremental_move(audit_context,inputs[-2],inputs[-1])
        if audit_delta is None and audit_reason=="grid_import":
            row=_candidate_full_recompute_audit(d,workload,baseline_schedule,audit_context,c,inputs,audit_delta,audit_reason,False,"negative_control",0,"grid_rejected")
            row["audit_mode"]="tightened_import_limit_negative_control"; rows.append(row); break
    missing=sorted(set(categories)-{x["case"] for x in rows})
    if missing: raise RuntimeError(f"Q2-DELTA-001: missing edge cases {missing}")
    return pd.DataFrame(rows)


def _optimize_q2_carbon_multistart(d,workload,pool,normalization,direct,formal_pass):
    origins=["cost_min","balanced","carbon_direct"]; runs=[]
    for origin in origins:
        run=_optimize_q2_scheme(d,workload,direct[origin]["schedule"],"carbon_direct",pool,normalization,max_passes=1,candidate_limit=Q2_CARBON_REFINEMENT_BUDGET,stage=f"carbon_multistart_refinement:{origin}",collect_trace=True,baseline_metrics=direct[origin]["summary"])
        runs.append((origin,run["terminal_schedule"],run["snapshots"].iloc[-1].to_dict(),run["trace"]))
    chosen=min(runs,key=lambda x:(x[2]["carbon_tCO2"],x[2]["cost_CNY"],x[2]["service_objective"],_schedule_hash(x[1]))); origin,schedule,metrics,_=chosen
    flow,audit,full=_summarize_q2_schedule(d,workload,schedule,normalization); full.update(metrics); full["schedule_sha256"]=_schedule_hash(schedule)
    audit_json={"schema_version":2,"status":"pass","origins":origins,"selected_origin":origin,"inherited_direct_pass":formal_pass,"new_candidate_budget_per_origin":Q2_CARBON_REFINEMENT_BUDGET,"total_new_candidates":Q2_CARBON_REFINEMENT_BUDGET*len(origins),"replaces_carbon_direct":False,"selected_schedule_sha256":full["schedule_sha256"],"runs":[{"origin":x[0],"inherited_schedule_sha256":direct[x[0]]["summary"]["schedule_sha256"],"final_schedule_sha256":_schedule_hash(x[1]),"carbon_tCO2":x[2]["carbon_tCO2"],"cost_CNY":x[2]["cost_CNY"],"accepted_improvements":int(x[2]["accepted_improvements"])} for x in runs]}
    return {"schedule":schedule,"flow":flow,"summary":full,"trace":pd.concat([x[3] for x in runs],ignore_index=True),"audit":audit,"audit_json":audit_json}


def q2_local_search(d,workload,baseline_schedule,max_candidates=Q2_MOVE_LIMIT):
    global Q2_SCHEME_RESULTS,Q2_SCHEME_AUDITS,Q2_COMMON_POOL,Q2_CANDIDATE_COVERAGE,Q2_COMMON_PROVENANCE,Q2_NORMALIZATION,Q2_BALANCED_AUDIT,Q2_WEIGHT_SENSITIVITY,Q2_CARBON_DIRECT_AUDIT,Q2_CARBON_MULTISTART_AUDIT,Q2_CARBON_REFINEMENT_COMPARISON,Q2_INCREMENTAL_AUDIT,Q2_INCREMENTAL_SUMMARY,Q2_CONVERGENCE_AUDIT,Q2_FORMAL_BUDGET,Q2_FORMAL_PASS,Q2_STABILITY_STATUS,Q2_STABILITY_REASON,Q2_SNAPSHOT_FRAME,Q2_CARBON_REFINEMENT_RESULT,Q2_CONTEXT_CHECKPOINT_AUDIT,Q2_CONTEXT_CHECKPOINT_SUMMARY,Q2_SEMANTIC_UNIQUENESS,Q2_TASK_CANDIDATE_AVAILABILITY,Q2_ATTEMPT_SEQUENCE_HASHES,Q2_PASS_STABILITY
    for generated in (RESULT_DIR/"q2_pass_search_trace.csv", RESULT_DIR/"q2_search_trace.csv", RESULT_DIR/"q2_balanced_score_audit.csv"):
        if generated.exists(): raise RuntimeError(f"RUN-ISOLATION-002: output already exists {generated}")
    pool=build_q2_common_candidate_pool(d,workload,baseline_schedule,max_candidates); normalization,pool=derive_q2_objective_normalization(d,workload,baseline_schedule,pool); Q2_COMMON_POOL,Q2_NORMALIZATION=pool,normalization
    semantic_cols=["TaskID","Region","CandidateStart"]
    task_alt=pool.groupby("TaskID")["IsBaselineAssignment"].apply(lambda s:bool((~s).any())).rename("HasAlternativeCandidate")
    task_counts=pool.groupby("TaskID").agg(BaseCandidateCount=("BaseCandidateID","size"),EffectiveAlternativeCandidateCount=("IsBaselineAssignment",lambda s:int((~s).sum())))
    Q2_TASK_CANDIDATE_AVAILABILITY=task_counts.join(task_alt).reset_index()
    layer_rows=[{"CandidateLayer":int(layer),"rows":len(group),"unique_semantic_candidates":int(group.drop_duplicates(semantic_cols).shape[0]),"effective_alternative_candidates":int((~group["IsBaselineAssignment"]).sum())} for layer,group in pool.groupby("CandidateLayer",sort=True)]
    Q2_SEMANTIC_UNIQUENESS={"schema_version":1,"total_rows":len(pool),"unique_candidate_ids":int(pool["BaseCandidateID"].nunique()),"unique_semantic_candidates":int(pool.drop_duplicates(semantic_cols).shape[0]),"duplicate_semantic_candidates":int(pool.duplicated(semantic_cols).sum()),"tasks_with_duplicates":int(pool.loc[pool.duplicated(semantic_cols,keep=False),"TaskID"].nunique()),"tasks_examined":int(pool["TaskID"].nunique()),"tasks_with_alternatives":int(Q2_TASK_CANDIDATE_AVAILABILITY["HasAlternativeCandidate"].sum()),"tasks_without_alternatives":int((~Q2_TASK_CANDIDATE_AVAILABILITY["HasAlternativeCandidate"]).sum()),"per_layer":layer_rows}
    pool_hash=hashlib.sha256(pool.to_csv(index=False).encode()).hexdigest()
    Q2_COMMON_PROVENANCE={"schema_version":2,"seed":SEED,"base_candidate_count":len(pool),"candidate_count":len(pool),"semantic_key":semantic_cols,"ordering":"objective-independent deterministic baseline-once then non-exhausted alternative layers","max_candidate_layers":Q2_MAX_CANDIDATES_PER_TASK,"max_passes":Q2_MAX_PASSES,"first_layer_task_count":int(pool.loc[pool["CandidateLayer"].eq(1),"TaskID"].nunique()),"candidate_pool_sha256":pool_hash,"candidate_id_prefix_shared_by_all_direct_schemes":True,"base_candidate_order_shared_by_all_direct_schemes":True,"generation_depends_on_objective":False,"no_change_counts_as_effective_alternative":False}
    coverage=[]
    for budget in Q2_STABILITY_BUDGETS:
        prefix=pool.iloc[:budget]
        coverage.append({"candidate_budget":budget,"candidate_id_first":prefix.iloc[0]["BaseCandidateID"],"candidate_id_last":prefix.iloc[-1]["BaseCandidateID"],"different_TaskID":int(prefix["TaskID"].nunique()),"task_coverage_rate":float(prefix["TaskID"].nunique()/len(workload)),"tasks_with_effective_alternative":int(prefix.loc[~prefix["IsBaselineAssignment"],"TaskID"].nunique()),"effective_alternative_task_coverage_rate":float(prefix.loc[~prefix["IsBaselineAssignment"],"TaskID"].nunique()/len(workload)),"candidate_layers":"|".join(map(str,sorted(prefix["CandidateLayer"].unique()))),"baseline_resource_feasible":int(prefix["BaselineResourceFeasible"].sum())})
    Q2_CANDIDATE_COVERAGE=pd.DataFrame(coverage)
    _,_,baseline=_summarize_q2_schedule(d,workload,baseline_schedule,normalization); baseline["balanced_full_score"]=0.0
    direct_runs={}; snapshots=[]; context_audits=[]; candidate_audits=[]; attempt_hashes={}
    for scheme in Q2_DIRECT_SCHEMES:
        run=_optimize_q2_scheme(d,workload,baseline_schedule,scheme,pool,normalization,max_passes=Q2_MAX_PASSES,stage="direct",stream_direct=True,baseline_metrics=baseline)
        direct_runs[scheme]=run; snapshots.append(run["snapshots"]); context_audits.append(run["context_audit"]); candidate_audits.append(run["candidate_audit"])
        attempt_hashes[scheme]={"attempt_sequence_sha256":run["attempt_sequence_sha256"],"passes":run["pass_sequence_hashes"],"base_candidate_count":len(pool),"completed_passes":Q2_MAX_PASSES,"attempted_evaluations":len(pool)*Q2_MAX_PASSES}
    snapshot_frame=pd.concat(snapshots,ignore_index=True); convergence,Q2_CONVERGENCE_AUDIT=_evaluate_common_convergence(snapshot_frame)
    formal_pass,status,reason,convergence_passes=convergence
    Q2_FORMAL_PASS=formal_pass; Q2_FORMAL_BUDGET=len(pool)*formal_pass; Q2_STABILITY_STATUS=status; Q2_STABILITY_REASON=reason; Q2_SNAPSHOT_FRAME=snapshot_frame; Q2_PASS_STABILITY=snapshot_frame.copy(); Q2_CONTEXT_CHECKPOINT_AUDIT=pd.concat(context_audits,ignore_index=True)
    Q2_ATTEMPT_SEQUENCE_HASHES={"schema_version":1,"shared_order":len({v["attempt_sequence_sha256"] for v in attempt_hashes.values()})==1,"schemes":attempt_hashes}
    Q2_SCHEME_RESULTS={}; Q2_SCHEME_AUDITS={}
    for scheme in Q2_DIRECT_SCHEMES:
        schedule=direct_runs[scheme]["checkpoint_schedules"][formal_pass]; flow,audit,metrics=_summarize_q2_schedule(d,workload,schedule,normalization)
        snap=direct_runs[scheme]["snapshots"].loc[direct_runs[scheme]["snapshots"]["PassID"].eq(formal_pass)].iloc[0].to_dict(); metrics.update(snap)
        scheme_converged=direct_runs[scheme]["convergence_pass"] is not None and direct_runs[scheme]["convergence_pass"]<=formal_pass
        metrics.update({"scheme":scheme,"declared_candidate_limit":len(pool),"base_candidate_count":len(pool),"completed_passes":formal_pass,"formal_pass":formal_pass,"formal_budget":len(pool)*formal_pass,"formal_pass_rule":"earliest_common_converged_pass_else_highest_common_completed_pass","scheme_convergence_pass":direct_runs[scheme]["convergence_pass"],"scheme_termination_reason":direct_runs[scheme]["termination_reason"],"metric_stability_status":"converged" if scheme_converged else "nonconverged","baseline_cost_CNY":baseline["cost_CNY"],"baseline_carbon_tCO2":baseline["carbon_tCO2"],"baseline_renewable_utilization":baseline["renewable_utilization"],"baseline_renewable_used_MWh":baseline["renewable_used_MWh"],"baseline_service_objective":baseline["service_objective"],"result_level":"scenario-feasible","termination_status":"neighborhood_converged" if scheme_converged else "max_passes_nonconverged"})
        Q2_SCHEME_RESULTS[scheme]={"schedule":schedule,"flow":flow,"summary":metrics}; Q2_SCHEME_AUDITS[scheme]=audit
    Q2_CARBON_DIRECT_AUDIT={"schema_version":2,"status":"pass","starts_from":"q1_baseline","formal_pass":formal_pass,"base_candidate_count":len(pool),"candidate_pool_sha256":pool_hash,"candidate_sequence_equal_to_other_direct_schemes":True,"schedule_sha256":Q2_SCHEME_RESULTS["carbon_direct"]["summary"]["schedule_sha256"]}
    refinement=_optimize_q2_carbon_multistart(d,workload,pool,normalization,Q2_SCHEME_RESULTS,formal_pass); Q2_CARBON_REFINEMENT_RESULT=refinement; Q2_CARBON_MULTISTART_AUDIT=refinement["audit_json"]
    direct_carbon=Q2_SCHEME_RESULTS["carbon_direct"]["summary"]
    Q2_CARBON_REFINEMENT_COMPARISON=pd.DataFrame([{"result":"carbon_direct","formal_fair_comparison":True,"starts_from":"q1_baseline","inherited_passes":0,"new_candidate_evaluations":len(pool)*formal_pass,**{k:direct_carbon[k] for k in ("cost_CNY","carbon_tCO2","renewable_utilization","service_objective","service_quality","schedule_sha256")}}, {"result":"carbon_multistart_refinement","formal_fair_comparison":False,"starts_from":refinement["audit_json"]["selected_origin"],"inherited_passes":formal_pass,"new_candidate_evaluations":Q2_CARBON_REFINEMENT_BUDGET,**{k:refinement["summary"][k] for k in ("cost_CNY","carbon_tCO2","renewable_utilization","service_objective","service_quality","schedule_sha256")}}])
    Q2_WEIGHT_SENSITIVITY=run_q2_weight_sensitivity(Q2_SCHEME_RESULTS,baseline,normalization); Q2_BALANCED_AUDIT=None
    edge_audit=run_q2_incremental_consistency_audit(d,workload,baseline_schedule,pool); Q2_INCREMENTAL_AUDIT=pd.concat(candidate_audits+[edge_audit],ignore_index=True)
    for category,column in (("capacity_boundary_highest_pressure","capacity_pressure_ratio"),("grid_boundary_highest_pressure","grid_import_pressure_ratio")):
        idx=Q2_INCREMENTAL_AUDIT[column].astype(float).idxmax(); existing=str(Q2_INCREMENTAL_AUDIT.at[idx,"sample_categories"]); Q2_INCREMENTAL_AUDIT.at[idx,"sample_categories"]="|".join(sorted(set(existing.split("|"))|{category}))
    direct_counts=Q2_INCREMENTAL_AUDIT.loc[Q2_INCREMENTAL_AUDIT["Scheme"].isin(Q2_DIRECT_SCHEMES)].groupby("Scheme").size().to_dict()
    category_counts={}
    for cell in Q2_INCREMENTAL_AUDIT["sample_categories"].astype(str):
        for category in cell.split("|"): category_counts[category]=category_counts.get(category,0)+1
    worst_idx=Q2_INCREMENTAL_AUDIT["max_absolute_residual"].astype(float).idxmax(); worst=Q2_INCREMENTAL_AUDIT.loc[worst_idx]
    Q2_INCREMENTAL_SUMMARY={"status":"pass","sample_count":len(Q2_INCREMENTAL_AUDIT),"category_counts":category_counts,"scheme_counts":{k:int(v) for k,v in direct_counts.items()},"max_absolute_residual":float(Q2_INCREMENTAL_AUDIT["max_absolute_residual"].max()),"max_relative_residual":float(Q2_INCREMENTAL_AUDIT["max_relative_residual"].max()),"worst_candidate_id":str(worst["BaseCandidateID"]),"worst_pass_id":int(worst["PassID"]),"worst_metric":str(worst["worst_quantity"]),"cumulative_state_max_drift":float(Q2_CONTEXT_CHECKPOINT_AUDIT["max_absolute_residual"].max()),"absolute_tolerance":1e-6,"relative_tolerance":1e-8}
    if any(int(direct_counts.get(s,0))<50 for s in Q2_DIRECT_SCHEMES): raise RuntimeError(f"Q2-DELTA-022: per-scheme audit count {direct_counts}")
    required={"accepted","feasible_but_rejected","capacity_rejected","grid_rejected","no_change","duration_lt_1h","fractional_duration","integer_duration","fractional_cross_two_hours","hour_boundary","cross_2399_2400","region_migration","return_to_baseline","high_power_task","high_gpu_demand_task","random_fixed_seed"}
    missing=sorted(required-set(category_counts))
    if missing: raise RuntimeError(f"Q2-DELTA-023: missing audit categories {missing}")
    if Q2_INCREMENTAL_SUMMARY["max_absolute_residual"]>1e-6 and Q2_INCREMENTAL_SUMMARY["max_relative_residual"]>1e-8: raise RuntimeError(f"Q2-DELTA-024: {Q2_INCREMENTAL_SUMMARY}")
    Q2_CONTEXT_CHECKPOINT_SUMMARY={"status":"pass","checkpoint_count":len(Q2_CONTEXT_CHECKPOINT_AUDIT),"expected_checkpoint_count":len(Q2_DIRECT_SCHEMES)*Q2_MAX_PASSES,"max_absolute_residual":float(Q2_CONTEXT_CHECKPOINT_AUDIT["max_absolute_residual"].max()),"max_relative_residual":float(Q2_CONTEXT_CHECKPOINT_AUDIT["max_relative_residual"].max()),"all_passed":bool(Q2_CONTEXT_CHECKPOINT_AUDIT["audit_passed"].all()),"absolute_tolerance":1e-6,"relative_tolerance":1e-8}
    selected=Q2_SCHEME_RESULTS["balanced"]; summary=dict(selected["summary"])
    summary.update({"scheme":"balanced","declared_candidate_limit":max_candidates,"base_candidate_count":len(pool),"completed_passes":formal_pass,"checked_candidates":len(pool)*formal_pass*len(Q2_DIRECT_SCHEMES),"unique_tasks_visited":int(pool["TaskID"].nunique()),"task_coverage_rate":float(pool["TaskID"].nunique()/len(workload)),"alternative_task_coverage_rate":float(pool.loc[~pool["IsBaselineAssignment"],"TaskID"].nunique()/len(workload)),"all_schemes_accepted_improvements":sum(v["summary"]["accepted_improvements"] for v in Q2_SCHEME_RESULTS.values()),"task_pool_size":len(workload),"common_candidate_pool_sha256":pool_hash,"formal_pass":formal_pass,"formal_budget":len(pool)*formal_pass,"metric_stability_status":status,"stability_reason":reason,"status":"neighborhood_converged" if status=="converged" else "max_passes_nonconverged","final_cost_CNY":summary["cost_CNY"],"final_carbon_tCO2":summary["carbon_tCO2"]})
    return selected["schedule"],selected["flow"],summary["cost_CNY"],summary["carbon_tCO2"],summary["renewable_utilization"],summary,pd.DataFrame()


def run_q2_budget_stability(d,workload,baseline_schedule):
    frame=Q2_SNAPSHOT_FRAME.copy().sort_values(["scheme","PassID"]).reset_index(drop=True); metrics=("cost_CNY","carbon_tCO2","renewable_utilization","renewable_used_MWh","network_latency_ms","service_objective","service_quality","migration_count","task_coverage_rate","accepted_improvements"); rows=[]
    for scheme in Q2_DIRECT_SCHEMES:
        group=frame.loc[frame["scheme"].eq(scheme)].sort_values("PassID")
        for metric in metrics:
            values=group[metric].to_numpy(float); floor=1.0 if metric in {"cost_CNY","migration_count","accepted_improvements"} else 1e-12; changes=[_relative_change(values[i-1],values[i],floor) for i in range(1,len(values))]; high=_relative_change(values[0],values[-1],floor); threshold=Q2_CONVERGENCE_MAIN_RTOL if metric in {"cost_CNY","carbon_tCO2","renewable_used_MWh","service_objective"} else Q2_CONVERGENCE_AUX_RTOL
            rows.append({"scheme":scheme,"metric":metric,"lowest_pass":int(group["PassID"].min()),"highest_pass":int(group["PassID"].max()),"adjacent_relative_changes":"|".join(f"{x:.15g}" for x in changes),"high_vs_low_relative_change":high,"maximum_relative_change":max(changes+[high]),"threshold":threshold,"auxiliary_diagnostic_only":metric not in {"cost_CNY","carbon_tCO2","renewable_used_MWh","service_objective"},"converged":bool(max(changes[-Q2_CONVERGENCE_INTERVALS:])<=threshold)})
    metric_frame=pd.DataFrame(rows)
    converged=metric_frame.loc[metric_frame["converged"], ["scheme","metric"]].astype(str).agg(": ".join,axis=1).tolist()
    nonconverged=metric_frame.loc[~metric_frame["converged"], ["scheme","metric"]].astype(str).agg(": ".join,axis=1).tolist()
    return frame,metric_frame,{"metric_stability_status":Q2_STABILITY_STATUS,"formal_pass":Q2_FORMAL_PASS,"formal_budget":Q2_FORMAL_BUDGET,"max_passes":Q2_MAX_PASSES,"criterion":"zero accepted full pass OR two consecutive passes main objective plus accepted rate plus hard/context audits; auxiliary metrics diagnostic only","reason":Q2_STABILITY_REASON,"common_base_candidate_order":True,"converged_metrics":"|".join(converged),"nonconverged_metrics":"|".join(nonconverged)}


def _optimize_q4_task_neighborhood(d, workload, baseline_schedule, budget, offset):
    """Dynamic Q4-only neighborhood; deliberately separate from fair Q2 direct runs."""
    schedule = baseline_schedule.copy().reset_index(drop=True)
    context = _q2_context(d, schedule)
    task_source = workload.set_index("TaskID")
    power = d["power"].set_index("TaskType")["GPU_Power_MW_per_EquivalentGPU"].to_dict()
    latency = d["latency"].set_index(["FromRegion", "ToRegion"])["NetworkLatency_ms"]
    row_order = np.roll(np.arange(len(schedule), dtype=int), int(offset) % len(schedule))
    checked = accepted = 0
    trace = []
    for task_no, row_idx in enumerate(row_order[:int(budget)]):
        check_deadline("q4.task_neighborhood")
        old = schedule.loc[int(row_idx)].copy()
        task = task_source.loc[int(old["TaskID"])]
        options = _q2_candidate_options(d, task, old, latency)
        option_rank = (int(offset) + task_no) % len(options)
        start, region, actual_latency = options[option_rank]
        checked += 1
        duration = float(old["FinishHour"] - old["StartHour"])
        finish = float(start) + duration
        task_power = float(old["GPU_Demand"]) * float(power[task["TaskType"]])
        deltas = _move_deltas(
            str(old["ExecutionRegion"]), float(old["StartHour"]), float(old["FinishHour"]),
            str(region), float(start), finish, float(old["GPU_Demand"]), task_power, context,
        )
        service_delta = (
            float(old["GPU_Demand"]) * duration / context["service_denominator"]
            * (float(actual_latency) - float(old["NetworkLatency_ms"])
               + Q2_SERVICE_WAIT_FACTOR * (float(start) - float(old["StartHour"])))
        )
        delta, reason = _evaluate_incremental_move(context, deltas, service_delta)
        accepted_move = False
        score = np.nan
        if delta is not None:
            score, _ = _q2_score("balanced", delta, Q2_NORMALIZATION)
            if score < -1e-12:
                _apply_q2_deltas(context, deltas)
                schedule.at[int(row_idx), "ExecutionRegion"] = str(region)
                schedule.at[int(row_idx), "StartHour"] = float(start)
                schedule.at[int(row_idx), "FinishHour"] = finish
                schedule.at[int(row_idx), "WaitHour"] = float(start) - float(task["ArrivalHour"])
                schedule.at[int(row_idx), "NetworkLatency_ms"] = float(actual_latency)
                accepted += 1
                accepted_move = True
                reason = "accepted"
        trace.append({
            "candidate_no": checked, "TaskID": int(task.name), "candidate_start": float(start),
            "candidate_region": str(region), "option_rank": int(option_rank), "status": reason,
            "score": score, "accepted": accepted_move, "neighborhood_offset": int(offset),
        })
    flow, audit, metrics = _summarize_q2_schedule(d, workload, schedule, Q2_NORMALIZATION)
    metrics.update({
        "scheme": "q4_dynamic_balanced_neighborhood", "checked_candidates": int(checked),
        "attempted_candidates": int(checked), "accepted_improvements": int(accepted),
        "unique_tasks_visited": int(checked), "task_coverage_rate": float(checked / len(schedule)),
        "termination_status": "candidate_budget_reached" if checked == int(budget) else "candidate_space_exhausted",
        "neighborhood_offset": int(offset),
    })
    return schedule, flow, metrics, pd.DataFrame(trace), audit



def _storage_base(d, facility_override=None, price_scale=1.0, sell_scale=1.0,
                  renewable_scale=1.0, renewable_override=None):
    rt = d["region"].copy().sort_values(["Region", "Hour"]).reset_index(drop=True)
    gpu = d["gpu"].set_index("Region")
    override = normalize_facility_override(facility_override)
    if override is not None:
        rt = rt.merge(override, on=["Region", "Hour"], how="left", validate="one_to_one")
    else:
        rt["FacilityLoad_MW"] = [
            (float(row.Baseline_AI_IT_Load_MW) + float(row.NonAI_IT_Load_MW))
            * float(gpu.loc[row.Region, "PUE"])
            for row in rt.itertuples()
        ]
    if renewable_override is not None:
        values = np.asarray(renewable_override, dtype=float)
        if values.shape != (len(rt),):
            raise RuntimeError("CON-Q4-4: renewable override shape")
        rt["ScenarioRenewable_MW"] = np.maximum(0.0, values)
    else:
        rt["ScenarioRenewable_MW"] = np.maximum(
            0.0, rt["AvailableRenewable_MW"].to_numpy(float) * renewable_scale
        )
    for region in REGIONS:
        mask = rt["Region"].eq(region)
        raw = rt.loc[mask, "ElectricityPrice_CNY_per_MWh"].to_numpy(float)
        rt.loc[mask, "ScenarioPrice"] = np.mean(raw) + price_scale * (raw - np.mean(raw))
    rt["ScenarioSellPrice"] = rt["SellPrice_CNY_per_MWh"] * sell_scale
    return rt


def _no_action_policy(d, facility_override=None, **scenario):
    rt = _storage_base(d, facility_override=facility_override, **scenario)
    storage = d["storage"].set_index("Region")
    rows = []
    for row in rt.itertuples():
        s = storage.loc[row.Region]
        load = float(row.FacilityLoad_MW)
        renewable = float(row.ScenarioRenewable_MW)
        use = min(load, renewable)
        buy = max(0.0, load - use)
        sell_limit = grid_export_limit(pd.Series({
            "MaxGridExport_MW": getattr(row, "MaxGridExport_MW", np.nan)
        }), s)
        sell = min(max(0.0, renewable - use), sell_limit)
        rows.append({
            "Region": row.Region, "Hour": int(row.Hour),
            "FacilityLoad_MW": load, "RenewableUse_MW": use,
            "Charge_MW": 0.0, "Discharge_MW": 0.0,
            "SOC_MWh": float(s["InitialSOC_MWh"]),
            "GridPurchase_MW": buy, "GridSell_MW": sell,
            "Curtailment_MW": max(0.0, renewable - use - sell),
            "GridExportLimit_MW": sell_limit,
            "Price": float(row.ScenarioPrice),
            "SellPrice": float(row.ScenarioSellPrice),
            "CarbonIntensity": float(row.CarbonIntensity_tCO2_per_MWh),
            "AvailableRenewable_MW": renewable,
        })
    return pd.DataFrame(rows)


def _storage_dp_policy(d, objective, facility_override=None, state_count=21,
                       terminal_mode="initial", **scenario):
    rt = _storage_base(d, facility_override=facility_override, **scenario)
    storage = d["storage"].set_index("Region")
    records = []
    for region_no, region in enumerate(REGIONS):
        check_deadline("storage.region", region_no)
        x = rt.loc[rt["Region"].eq(region)].sort_values("Hour").reset_index(drop=True)
        s = storage.loc[region]
        minimum = float(s["MinSOC_MWh"])
        maximum = storage_soc_max(s)
        initial = float(s["InitialSOC_MWh"])
        states = np.unique(np.r_[np.linspace(minimum, maximum, state_count), initial])
        initial_index = int(np.where(np.isclose(states, initial))[0][0])
        n = len(states)
        before = states[:, None]
        after = states[None, :]
        delta_soc = after - before
        charge = np.maximum(delta_soc, 0.0) / float(s["ChargeEfficiency"])
        discharge = np.maximum(-delta_soc, 0.0) * float(s["DischargeEfficiency"])
        transition_ok = (
            (charge <= float(s["MaxChargePower_MW"]) + TOL)
            & (discharge <= float(s["MaxDischargePower_MW"]) + TOL)
        )
        dp = np.full(n, np.inf)
        dp[initial_index] = 0.0
        predecessors = np.full((len(x), n), -1, dtype=np.int16)
        baseline_buy = np.maximum(
            0.0,
            x["FacilityLoad_MW"].to_numpy(float)
            - x["ScenarioRenewable_MW"].to_numpy(float),
        )
        previous_reference = np.r_[baseline_buy[0], baseline_buy[:-1]]
        for t, row in enumerate(x.itertuples()):
            if t % 24 == 0:
                check_deadline(f"storage.{region}", t)
            load = float(row.FacilityLoad_MW)
            renewable = float(row.ScenarioRenewable_MW)
            net = load + charge - renewable - discharge
            buy = np.maximum(net, 0.0)
            surplus = np.maximum(-net, 0.0)
            export_limit = grid_export_limit(pd.Series({
                "MaxGridExport_MW": getattr(row, "MaxGridExport_MW", np.nan)
            }), s)
            sell = np.minimum(surplus, export_limit)
            curtail = surplus - sell
            feasible = transition_ok & (
                buy <= float(s["MaxGridImport_MW"]) + TOL
            )
            step_cost = (
                buy * float(row.ScenarioPrice)
                - sell * float(row.ScenarioSellPrice)
            )
            step_carbon = buy * float(row.CarbonIntensity_tCO2_per_MWh)
            if objective == "cost_min":
                step = step_cost
            elif objective == "carbon_min":
                step = step_carbon * 1000.0
            elif objective == "renewable_max":
                step = curtail * 1000.0 + np.maximum(step_cost, 0.0) * 1e-6
            elif objective == "peak_min":
                step = buy ** 2
            elif objective == "ramp_min":
                step = np.abs(buy - previous_reference[t]) * 1000.0 + buy ** 2 * 1e-3
            else:
                step = (
                    step_cost / 1000.0
                    + step_carbon * 50.0
                    + curtail * 10.0
                    + buy ** 2 * 0.01
                )
            total = dp[:, None] + np.where(feasible, step, np.inf)
            best_prev = np.argmin(total, axis=0)
            new_dp = total[best_prev, np.arange(n)]
            predecessors[t] = best_prev
            dp = new_dp
            if not np.isfinite(dp).any():
                raise RuntimeError(f"CON-Q3-1: {region} {objective} DP无可行状态")
        if terminal_mode == "initial":
            final_index = initial_index
        else:
            final_index = int(np.argmin(dp))
        if not np.isfinite(dp[final_index]):
            raise RuntimeError(f"CON-Q3-2: {region} {objective} 终端状态不可达")
        path = np.empty(len(x), dtype=np.int16)
        current_index = final_index
        for t in range(len(x) - 1, -1, -1):
            path[t] = current_index
            current_index = int(predecessors[t, current_index])
        previous_soc = initial
        for t, row in enumerate(x.itertuples()):
            soc = float(states[int(path[t])])
            delta = soc - previous_soc
            charge_value = max(delta, 0.0) / float(s["ChargeEfficiency"])
            discharge_value = max(-delta, 0.0) * float(s["DischargeEfficiency"])
            load = float(row.FacilityLoad_MW)
            renewable = float(row.ScenarioRenewable_MW)
            use = min(load, renewable)
            net = load + charge_value - renewable - discharge_value
            buy_value = max(0.0, net)
            surplus = max(0.0, -net)
            sell_limit = grid_export_limit(pd.Series({
                "MaxGridExport_MW": getattr(row, "MaxGridExport_MW", np.nan)
            }), s)
            sell_value = min(surplus, sell_limit)
            records.append({
                "Region": region, "Hour": int(row.Hour),
                "FacilityLoad_MW": load, "RenewableUse_MW": use,
                "Charge_MW": charge_value, "Discharge_MW": discharge_value,
                "SOC_MWh": soc, "GridPurchase_MW": buy_value,
                "GridSell_MW": sell_value,
                "Curtailment_MW": max(0.0, surplus - sell_value),
                "GridExportLimit_MW": sell_limit,
                "Price": float(row.ScenarioPrice),
                "SellPrice": float(row.ScenarioSellPrice),
                "CarbonIntensity": float(row.CarbonIntensity_tCO2_per_MWh),
                "AvailableRenewable_MW": renewable,
            })
            previous_soc = soc
    return pd.DataFrame(records)


def _trajectory_hash(flow):
    columns = ["Region", "Hour", "Charge_MW", "Discharge_MW", "SOC_MWh"]
    payload = flow[columns].round(9).to_csv(index=False).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _pareto_nondominated(metric_rows):
    values = np.asarray([
        [row["cost_CNY"], row["carbon_tCO2"], -row["renewable_utilization"],
         row["peak_MW"], row["ramp_MW"]]
        for row in metric_rows
    ], dtype=float)
    result = []
    for i in range(len(values)):
        dominated = any(
            np.all(values[j] <= values[i] + 1e-9)
            and np.any(values[j] < values[i] - 1e-9)
            for j in range(len(values)) if j != i
        )
        result.append(not dominated)
    return result


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
    relaxed = _storage_dp_policy(
        d, "cost_min", facility_override=facility_override,
        terminal_mode="free", state_count=SOC_STATE_COUNT,
    )
    Q3_TERMINAL_SENSITIVITY = {
        "interpretation": "题面未给出退化成本或循环寿命参数；本项仅为敏感性，不是官方参数",
        "facility_source": "formal_q2_balanced",
        "initial_equal": next(row for row in rows if row["policy"] == "cost_min"),
        "terminal_free": {
            "metrics": metrics_energy(relaxed),
            "terminal_soc": relaxed.groupby("Region").tail(1)[["Region", "SOC_MWh"]].to_dict("records"),
        },
    }
    return selected, summary, trace


def run_soc_grid_sensitivity(d, selected_policy, facility_override=None):
    rows = []
    storage = d["storage"].set_index("Region")
    for state_count in SOC_SENSITIVITY_STATE_COUNTS:
        check_deadline("q3.grid_sensitivity", state_count)
        started = time.monotonic()
        flow = _storage_dp_policy(
            d, selected_policy, facility_override=facility_override,
            state_count=state_count,
        )
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



def _service_detail(schedule, workload):
    latency_value, service_quality, migrated = service_metrics(schedule)
    source = workload.set_index("TaskID")
    finish_limits = schedule["TaskID"].map(source["LatestFinishHour"]).clip(upper=2406)
    on_time = schedule["FinishHour"].to_numpy(float) <= finish_limits.to_numpy(float) + TOL
    realtime = schedule["TaskType"].eq("RealTimeInference")
    realtime_sla = (
        float(np.mean(schedule.loc[realtime, "WaitHour"].to_numpy(float) <= TOL))
        if realtime.any() else 1.0
    )
    waits = schedule["WaitHour"].to_numpy(float)
    return {
        "network_latency_ms": latency_value,
        "service_quality": service_quality,
        "migration_count": migrated,
        "realtime_sla_rate": realtime_sla,
        "on_time_rate": float(np.mean(on_time)),
        "max_wait_h": float(np.max(waits)),
        "p95_wait_h": float(np.quantile(waits, 0.95)),
        "mean_wait_h": float(np.mean(waits)),
    }


def build_q4_task_candidate_set(
    d, workload, baseline_schedule, baseline_flow,
    max_checked=Q4_TASK_NEIGHBOR_LIMIT,
):
    """Q4 不再预先冻结三个方案；这里只绑定共同起点，邻域在每轮重建。"""
    baseline = baseline_schedule.copy().reset_index(drop=True)
    feasible, used_gpu = schedule_candidate_feasible(d, workload, baseline)
    if not feasible:
        raise RuntimeError("CON-Q4-1: 共同任务起点未通过50000任务审计")
    audit = build_constraint_audit(d, workload, baseline, used_gpu)
    if not audit["constraint_satisfied"].all():
        raise RuntimeError("CON-Q4-1: 共同任务起点约束残差失败")
    candidates = [{
        "candidate_id": "dynamic_common_baseline",
        "schedule": baseline,
        "facility_override": baseline_flow[
            ["Region", "Hour", "FacilityLoad_MW"]
        ].copy(),
        "task_search_status": "dynamic_neighborhood_rebuilt_each_round",
        "full_task_audit_passed": True,
    }]
    evidence = {
        "status": "dynamic_alternating_enabled",
        "neighbor_candidates_checked": 0,
        "candidate_count": 1,
        "different_candidate_count": 0,
        "full_task_audits": 1,
        "max_rounds": Q4_MAX_ROUNDS,
        "no_improvement_rounds": Q4_NO_IMPROVEMENT_ROUNDS,
        "candidate_budget_per_round": int(max_checked),
        "fixed_candidate_set": False,
        "alternative_constraint_residuals": {},
        "alternative_max_constraint_residual": 0.0,
    }
    return candidates, evidence, {}


def _scenario_variant(d, scenario_type, level, seed=None):
    variant = {key: value.copy() for key, value in d.items()}
    rt = variant["region"].copy().sort_values(["Region", "Hour"]).reset_index(drop=True)
    if scenario_type == "price_spread":
        for region in REGIONS:
            mask = rt["Region"].eq(region)
            values = rt.loc[mask, "ElectricityPrice_CNY_per_MWh"].to_numpy(float)
            rt.loc[mask, "ElectricityPrice_CNY_per_MWh"] = (
                np.mean(values) + float(level) * (values - np.mean(values))
            )
    elif scenario_type == "sell_mechanism":
        rt["SellPrice_CNY_per_MWh"] *= float(level)
    elif scenario_type == "renewable_level":
        rt["AvailableRenewable_MW"] = np.maximum(
            0.0, rt["AvailableRenewable_MW"].to_numpy(float) * float(level)
        )
    elif scenario_type == "renewable_volatility":
        rng = np.random.default_rng(int(seed))
        for region in REGIONS:
            mask = rt["Region"].eq(region)
            values = rt.loc[mask, "AvailableRenewable_MW"].to_numpy(float)
            noise = rng.normal(size=len(values))
            noise = (noise - noise.mean()) / max(noise.std(ddof=1), 1e-12)
            positive = values[values > 0]
            sigma = 0.10 * float(positive.mean()) if len(positive) else 0.0
            rt.loc[mask, "AvailableRenewable_MW"] = np.maximum(
                0.0, values + sigma * noise
            )
    elif scenario_type == "renewable_shortage_pressure":
        rt["AvailableRenewable_MW"] = np.maximum(
            0.0, rt["AvailableRenewable_MW"].to_numpy(float) * float(level)
        )
    elif scenario_type == "carbon_constraint":
        # 碳约束由候选可行性筛选实现，不把约束偷换成碳价。
        pass
    variant["region"] = rt
    return variant


def _q4_joint_score(metrics, service, baseline, carbon_target=None):
    vector = np.asarray([
        metrics[0], metrics[1], -metrics[2], metrics[3], metrics[4],
        service["network_latency_ms"], service["mean_wait_h"],
    ], dtype=float)
    base = np.asarray(baseline, dtype=float)
    scale = np.maximum(np.abs(base), 1.0)
    score = float(np.mean((vector - base) / scale))
    if carbon_target is not None and metrics[1] > carbon_target + TOL:
        score += 1000.0 * (metrics[1] - carbon_target) / max(abs(carbon_target), 1.0)
    return score, vector


def _schedule_hash(schedule):
    payload = schedule[[
        "TaskID", "ExecutionRegion", "StartHour", "FinishHour"
    ]].sort_values("TaskID").to_csv(index=False).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _select_q4_storage_policy(d, facility_override, carbon_target=None,
                              precomputed=None):
    """按 Q4 自身权重在三个不重复政策方向中选择，不继承 Q3 的名称。"""
    flows = {}
    rows = []
    for policy in Q4_STORAGE_POLICIES:
        flow = (
            precomputed[policy].copy()
            if precomputed is not None and policy in precomputed
            else _storage_dp_policy(
                d, policy, facility_override=facility_override,
                state_count=SOC_STATE_COUNT,
            )
        )
        audit_storage_policy(d, flow, "CON-Q4-1")
        metrics = metrics_energy(flow)
        flows[policy] = flow
        rows.append({
            "policy": policy,
            "cost_CNY": metrics[0],
            "carbon_tCO2": metrics[1],
            "renewable_utilization": metrics[2],
            "peak_MW": metrics[3],
            "ramp_MW": metrics[4],
            "trajectory_sha256": _trajectory_hash(flow),
        })
    feasible_indices = [
        index for index, row in enumerate(rows)
        if carbon_target is None or row["carbon_tCO2"] <= carbon_target + TOL
    ]
    target_feasible = bool(feasible_indices)
    if not feasible_indices:
        minimum_carbon = min(row["carbon_tCO2"] for row in rows)
        feasible_indices = [
            index for index, row in enumerate(rows)
            if row["carbon_tCO2"] <= minimum_carbon + TOL
        ]
    # 归一化尺度固定取完整三政策集合，避免收紧约束时因重标度反转偏好。
    matrix_all = np.asarray([
        [row["cost_CNY"], row["carbon_tCO2"],
         -row["renewable_utilization"], row["peak_MW"], row["ramp_MW"]]
        for row in rows
    ], dtype=float)
    matrix = matrix_all[feasible_indices]
    ideal, worst = matrix_all.min(axis=0), matrix_all.max(axis=0)
    span = np.where(worst - ideal > 1e-12, worst - ideal, 1.0)
    normalized = (matrix - ideal) / span
    distances = np.sqrt(np.sum(Q4_DECISION_WEIGHTS * normalized ** 2, axis=1))
    for row in rows:
        row.update({"decision_eligible": False, "ideal_distance": np.nan})
    for local, index in enumerate(feasible_indices):
        rows[index]["decision_eligible"] = True
        rows[index]["ideal_distance"] = float(distances[local])
    selected_local = min(
        range(len(feasible_indices)),
        key=lambda local: (
            float(distances[local]), rows[feasible_indices[local]]["policy"]
        ),
    )
    selected_index = feasible_indices[selected_local]
    selected_policy = rows[selected_index]["policy"]
    trace = pd.DataFrame(rows)
    summary = {
        "status": "q4_policy_selected" if target_feasible else "carbon_target_infeasible_within_policy_set",
        "selected_policy": selected_policy,
        "decision_method": "q4_weighted_ideal_distance_over_cost_balanced_renewable_policies",
        "decision_weights": "cost=0.20|carbon=0.20|renewable=0.30|peak=0.15|ramp=0.15",
        "checked_candidates": len(rows),
        "accepted_improvements": 1,
        "unique_trajectories": int(trace["trajectory_sha256"].nunique()),
        "storage_policy_candidate_count": len(rows),
        "carbon_target_tCO2": carbon_target,
        "target_feasible": target_feasible,
        "selected_ideal_distance": float(distances[selected_local]),
        "state_count": SOC_STATE_COUNT,
        "result_level": "scenario-feasible",
    }
    return flows[selected_policy], summary, trace


def _q4_mechanism_state(scenario_type, level, flow, carbon_target,
                        carbon_reference, stress_mode):
    purchase = float(flow["GridPurchase_MW"].sum())
    selling = float(flow["GridSell_MW"].sum())
    if scenario_type == "carbon_constraint":
        active = bool(carbon_reference > TOL and float(level) > 0)
        constraint = (
            f"carbon_tCO2<={carbon_target:.12g}" if carbon_target is not None
            else "inactive_zero_carbon_reference"
        )
    elif scenario_type == "price_spread":
        active = bool(abs(float(level) - 1.0) > TOL and purchase > TOL)
        constraint = "price_spread_active" if active else "inactive_zero_purchase_or_reference_level"
    elif scenario_type == "sell_mechanism":
        active = bool(abs(float(level) - 1.0) > TOL and selling > TOL)
        constraint = "sell_price_active" if active else "inactive_zero_export_or_reference_level"
    elif scenario_type == "renewable_level":
        active = bool(abs(float(level) - 1.0) > TOL)
        constraint = (
            "renewable_supply_perturbation_active" if active
            else "reference_renewable_level_no_perturbation"
        )
    elif scenario_type == "renewable_volatility":
        active = True
        constraint = "renewable_volatility_perturbation_active"
    else:
        active = False
        constraint = "baseline_no_extra_constraint"
    return active, constraint, purchase, selling


def _summarize_q4_families(frame, carbon_reference, stress_mode):
    rows = []
    metric_columns = [
        "cost_CNY", "carbon_tCO2", "renewable_utilization",
        "peak_grid_purchase_MW", "ramp_MW", "network_latency_ms",
        "service_quality",
    ]
    for family, group in frame.groupby("scenario_type", sort=False):
        unique_schedule = int(group["selected_candidate"].nunique())
        unique_storage = int(group["storage_trajectory_sha256"].nunique())
        unique_metrics = int(group[metric_columns].round(9).drop_duplicates().shape[0])
        degenerate = bool(
            len(group) > 1 and unique_schedule == 1
            and unique_storage == 1 and unique_metrics == 1
        )
        if not degenerate:
            reason = "none"
        elif family == "carbon_constraint" and carbon_reference <= TOL:
            reason = "zero_carbon_reference"
        elif not group["mechanism_active"].astype(bool).any():
            reason = "constraint_or_mechanism_inactive"
        elif int(group["storage_policy_candidate_count"].max()) < 3:
            reason = "insufficient_policy_neighborhood"
        else:
            reason = "all_legal_candidates_identical_within_declared_search"
        rows.append({
            "scenario_type": family,
            "scenario_count": len(group),
            "unique_schedule_count": unique_schedule,
            "unique_storage_trajectory_count": unique_storage,
            "unique_metric_combination_count": unique_metrics,
            "active_constraint_or_mechanism": bool(group["mechanism_active"].astype(bool).any()),
            "active_constraints": "|".join(sorted(set(group["active_constraint"].astype(str)))),
            "accepted_rounds": int(group["accepted_rounds"].sum()),
            "storage_policy_candidate_count": int(group["storage_policy_candidate_count"].max()),
            "degenerate_scenario": degenerate,
            "degeneracy_reason": reason,
            "carbon_reference_mode": (
                "renewable_shortage_pressure" if family == "carbon_constraint" and stress_mode
                else "normal_baseline"
            ),
        })
        mask = frame["scenario_type"].eq(family)
        frame.loc[mask, "degenerate_scenario"] = degenerate
        frame.loc[mask, "degeneracy_reason"] = reason
    return pd.DataFrame(rows)


def run_q4_scenarios(d, task_candidates, joint_baseline):
    baseline_schedule = task_candidates[0]["schedule"].copy().reset_index(drop=True)
    workload = d["workload"].copy()
    scenario_specs = [
        ("baseline", "baseline", 1.0, None),
        ("carbon_constraint", "carbon_reduction", 0.0, None),
        ("carbon_constraint", "carbon_reduction", 0.1, None),
        ("carbon_constraint", "carbon_reduction", 0.2, None),
        ("carbon_constraint", "carbon_reduction", 0.3, None),
        ("price_spread", "price_scale", 0.75, None),
        ("price_spread", "price_scale", 1.0, None),
        ("price_spread", "price_scale", 1.25, None),
        ("sell_mechanism", "sell_scale", 0.0, None),
        ("sell_mechanism", "sell_scale", 0.5, None),
        ("sell_mechanism", "sell_scale", 1.0, None),
        ("renewable_level", "renewable_scale", 0.8, None),
        ("renewable_level", "renewable_scale", 1.0, None),
        ("renewable_level", "renewable_scale", 1.2, None),
        ("renewable_volatility", "seed", 2026.0, 2026),
        ("renewable_volatility", "seed", 2027.0, 2027),
        ("renewable_volatility", "seed", 2028.0, 2028),
    ]
    reference_metrics = metrics_energy(joint_baseline)
    reference_service = _service_detail(baseline_schedule, workload)
    baseline_vector = np.asarray([
        reference_metrics[0], reference_metrics[1], -reference_metrics[2],
        reference_metrics[3], reference_metrics[4],
        reference_service["network_latency_ms"], reference_service["mean_wait_h"],
    ], dtype=float)
    normal_carbon_reference = float(reference_metrics[1])
    stress_mode = bool(normal_carbon_reference <= TOL)
    if stress_mode:
        pressure_variant = _scenario_variant(d, "renewable_shortage_pressure", 0.8)
        pressure_no_storage, _, _, _ = no_storage_energy(pressure_variant, baseline_schedule)
        pressure_flow, _, _ = _select_q4_storage_policy(
            pressure_variant,
            pressure_no_storage[["Region", "Hour", "FacilityLoad_MW"]],
        )
        carbon_reference = float(metrics_energy(pressure_flow)[1])
    else:
        carbon_reference = normal_carbon_reference
    rows, trace_rows = [], []
    checked_total = 0
    for scenario_index, (scenario_type, parameter, level, seed) in enumerate(scenario_specs):
        check_deadline("q4.scenario", scenario_index)
        if scenario_type == "carbon_constraint" and stress_mode:
            variant = _scenario_variant(d, "renewable_shortage_pressure", 0.8)
            baseline_source = "renewable_shortage_pressure_scale_0.8"
        else:
            variant = _scenario_variant(d, scenario_type, level, seed)
            baseline_source = "normal_joint_baseline"
        carbon_target = (
            (1.0 - float(level)) * carbon_reference
            if scenario_type == "carbon_constraint" else None
        )
        current_schedule = baseline_schedule.copy()
        current_no_storage, _, _, _ = no_storage_energy(variant, current_schedule)
        current_flow, current_policy_summary, _ = _select_q4_storage_policy(
            variant,
            current_no_storage[["Region", "Hour", "FacilityLoad_MW"]],
            carbon_target=carbon_target,
        )
        current_metrics = metrics_energy(current_flow)
        current_service = _service_detail(current_schedule, workload)
        current_score, _ = _q4_joint_score(
            current_metrics, current_service, baseline_vector, carbon_target
        )
        no_improvement = 0
        rounds = 0
        accepted_rounds = 0
        scenario_checked = 0
        for round_no in range(1, Q4_MAX_ROUNDS + 1):
            check_deadline(f"q4.{scenario_type}.round", round_no)
            rounds = round_no
            signal_variant = {key: value.copy() for key, value in variant.items()}
            signal_rt = signal_variant["region"].copy().sort_values(
                ["Region", "Hour"]
            ).reset_index(drop=True)
            storage_signal = current_flow.sort_values(
                ["Region", "Hour"]
            ).reset_index(drop=True)
            signal_rt["ElectricityPrice_CNY_per_MWh"] = (
                signal_rt["ElectricityPrice_CNY_per_MWh"].to_numpy(float)
                + 200.0 * signal_rt["CarbonIntensity_tCO2_per_MWh"].to_numpy(float)
                + 5.0 * storage_signal["GridPurchase_MW"].to_numpy(float)
                - 5.0 * storage_signal["Curtailment_MW"].to_numpy(float)
            )
            signal_variant["region"] = signal_rt
            candidate_schedule, _, candidate_summary, _, candidate_audit = _optimize_q4_task_neighborhood(
                signal_variant, workload, current_schedule,
                Q4_TASK_NEIGHBOR_LIMIT, scenario_index * 131 + round_no * 977,
            )
            scenario_checked += int(candidate_summary["checked_candidates"])
            checked_total += int(candidate_summary["checked_candidates"])
            candidate_no_storage, _, _, _ = no_storage_energy(variant, candidate_schedule)
            candidate_flow, candidate_policy_summary, _ = _select_q4_storage_policy(
                variant,
                candidate_no_storage[["Region", "Hour", "FacilityLoad_MW"]],
                carbon_target=carbon_target,
            )
            candidate_metrics = metrics_energy(candidate_flow)
            candidate_service = _service_detail(candidate_schedule, workload)
            candidate_score, _ = _q4_joint_score(
                candidate_metrics, candidate_service, baseline_vector, carbon_target
            )
            improvement = current_score - candidate_score
            # baseline 是正常条件下的共同参照，只评价邻域，不改写参照本身。
            accepted = bool(
                scenario_type != "baseline"
                and improvement > Q4_IMPROVEMENT_TOL
            )
            before_hash = _schedule_hash(current_schedule)
            score_before = current_score
            if accepted:
                current_schedule = candidate_schedule
                current_flow = candidate_flow
                current_metrics = candidate_metrics
                current_service = candidate_service
                current_score = candidate_score
                current_policy_summary = candidate_policy_summary
                accepted_rounds += 1
                no_improvement = 0
            else:
                no_improvement += 1
            trace_rows.append({
                "scenario_type": scenario_type,
                "parameter": parameter,
                "state_count": SOC_STATE_COUNT,
                "storage_policy": candidate_policy_summary["selected_policy"],
                "storage_policy_candidate_count": candidate_policy_summary["storage_policy_candidate_count"],
                "level": level,
                "seed": seed,
                "alternation_round": round_no,
                "task_candidate_budget": Q4_TASK_NEIGHBOR_LIMIT,
                "task_candidates_checked": candidate_summary["checked_candidates"],
                "unique_tasks_visited": candidate_summary["unique_tasks_visited"],
                "local_task_moves_accepted": candidate_summary["accepted_improvements"],
                "full_task_audit_passed": bool(candidate_audit["constraint_satisfied"].all()),
                "incumbent_schedule_before_sha256": before_hash,
                "candidate_schedule_sha256": _schedule_hash(candidate_schedule),
                "storage_trajectory_sha256": _trajectory_hash(candidate_flow),
                "joint_score_before": score_before,
                "joint_score_candidate": candidate_score,
                "improvement": improvement,
                "accepted": accepted,
                "incumbent_schedule_after_sha256": _schedule_hash(current_schedule),
                "neighborhood_rebuilt_from_previous_storage": True,
            })
            if no_improvement >= Q4_NO_IMPROVEMENT_ROUNDS:
                break
        final_feasible, final_used_gpu = schedule_candidate_feasible(
            variant, workload, current_schedule
        )
        if not final_feasible:
            raise RuntimeError("CON-Q4-1: 情景最终任务方案全量审计失败")
        final_audit = build_constraint_audit(variant, workload, current_schedule, final_used_gpu)
        if not final_audit["constraint_satisfied"].all():
            raise RuntimeError("CON-Q4-1: 情景最终任务约束残差失败")
        status = "completed"
        if carbon_target is not None and current_metrics[1] > carbon_target + TOL:
            status = "target_infeasible_within_declared_heuristic"
        mechanism_active, active_constraint, purchase, selling = _q4_mechanism_state(
            scenario_type, level, current_flow, carbon_target,
            carbon_reference, stress_mode,
        )
        rows.append({
            "scenario_type": scenario_type,
            "parameter": parameter,
            "state_count": SOC_STATE_COUNT,
            "storage_policy": current_policy_summary["selected_policy"],
            "storage_policy_candidate_count": current_policy_summary["storage_policy_candidate_count"],
            "storage_policy_selection_rule": current_policy_summary["decision_method"],
            "baseline_source": baseline_source,
            "carbon_reference_mode": "renewable_shortage_pressure" if scenario_type == "carbon_constraint" and stress_mode else "normal_baseline",
            "carbon_reference_tCO2": carbon_reference if scenario_type == "carbon_constraint" else np.nan,
            "carbon_target_tCO2": carbon_target,
            "level": level,
            "seed": seed,
            "status": status,
            "alternation_rounds": rounds,
            "accepted_rounds": accepted_rounds,
            "checked_candidates": scenario_checked,
            "common_start_count": 1,
            "fixed_candidate_set": False,
            "dynamic_neighborhood_rebuilt_each_round": True,
            "selected_candidate": _schedule_hash(current_schedule),
            "storage_trajectory_sha256": _trajectory_hash(current_flow),
            "migration_count": current_service["migration_count"],
            "task_search_status": "alternating_improved" if accepted_rounds else "searched_no_improvement",
            "cost_CNY": current_metrics[0],
            "carbon_tCO2": current_metrics[1],
            "network_latency_ms": current_service["network_latency_ms"],
            "service_quality": current_service["service_quality"],
            "realtime_sla_rate": current_service["realtime_sla_rate"],
            "on_time_rate": current_service["on_time_rate"],
            "max_wait_h": current_service["max_wait_h"],
            "p95_wait_h": current_service["p95_wait_h"],
            "mean_wait_h": current_service["mean_wait_h"],
            "renewable_utilization": current_metrics[2],
            "peak_grid_purchase_MW": current_metrics[3],
            "ramp_MW": current_metrics[4],
            "grid_purchase_MWh": purchase,
            "grid_sell_MWh": selling,
            "mechanism_active": mechanism_active,
            "active_constraint": active_constraint,
            "constraints_satisfied": 1,
            "non_Pareto": True,
            "result_level": "scenario-feasible",
            "termination_status": "no_improvement" if no_improvement >= Q4_NO_IMPROVEMENT_ROUNDS else "max_iterations_reached",
        })
    frame = pd.DataFrame(rows)
    family_summary = _summarize_q4_families(frame, carbon_reference, stress_mode)
    return frame, checked_total, pd.DataFrame(trace_rows), family_summary


def main():
    print("结果: 正式求解开始", flush=True)
    print(
        f"结果: 问题二完整复算候选上限={Q2_MOVE_LIMIT}",
        flush=True,
    )
    if PILOT_MODE:
        raise RuntimeError(
            "PILOT-DISPATCH: actual=1, threshold=0, "
            "试跑不得进入正式求解入口"
        )
    if "MMW_OUTPUT_ROOT" not in os.environ:
        raise RuntimeError("RUN-ISOLATION-001: 正式运行必须由tools/run_official.py提供隔离输出目录")
    check_deadline("main.start")
    RESULT_DIR.mkdir(parents=True, exist_ok=True)

    d = read_inputs()
    print(
        f"结果: 输入读取完成, 耗时={time.monotonic() - PROGRAM_START:.3f}秒",
        flush=True,
    )
    validate_inputs(d)
    print(
        f"结果: 输入校验完成, 耗时={time.monotonic() - PROGRAM_START:.3f}秒",
        flush=True,
    )

    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    FIGURE_DATA_DIR.mkdir(parents=True, exist_ok=True)

    demand, workload = aggregate_demand(d["workload"])
    forecast_metrics, predictions, q1_rolling_validation, q1_candidate_summary, q1_model_selection, q1_forecast_summary = forecast(demand)
    print(
        f"结果: 问题一预测完成, 耗时={time.monotonic() - PROGRAM_START:.3f}秒",
        flush=True,
    )
    q1_schedule_full, q1_used_gpu = greedy_schedule(d, workload)
    print(
        f"结果: 问题一可行构造完成, 任务数={len(q1_schedule_full)}, "
        f"耗时={time.monotonic() - PROGRAM_START:.3f}秒",
        flush=True,
    )
    q1_feasible, q1_recomputed_used_gpu = schedule_candidate_feasible(
        d, workload, q1_schedule_full
    )
    if not q1_feasible or not np.allclose(
        q1_used_gpu, q1_recomputed_used_gpu, rtol=0.0, atol=TOL
    ):
        fail("CON-Q1-7", 1, 0, "问题一基础调度或GPU占用独立复算失败")
    q1_constraint_audit = build_constraint_audit(
        d, workload, q1_schedule_full, q1_recomputed_used_gpu
    )
    (
        q2_balanced_schedule, q2_flow, q2_cost, q2_carbon, q2_re,
        q2_search, q2_trace,
    ) = q2_local_search(
        d,
        workload,
        q1_schedule_full,
        max_candidates=Q2_MOVE_LIMIT,
    )
    (
        q2_budget_stability,
        q2_metric_stability,
        q2_stability_summary,
    ) = run_q2_budget_stability(d, workload, q1_schedule_full)
    print(
        f"结果: 问题二有限搜索完成, 检查候选数="
        f"{int(q2_search['checked_candidates'])}, "
        f"耗时={time.monotonic() - PROGRAM_START:.3f}秒",
        flush=True,
    )
    q2_feasible, q2_used_gpu = schedule_candidate_feasible(
        d, workload, q2_balanced_schedule
    )
    if not q2_feasible:
        fail("CON-Q2-1", 1, 0, "局部搜索结果未通过全量任务复核")

    constraint_audit = build_constraint_audit(
        d, workload, q2_balanced_schedule, q2_used_gpu
    )
    task_max_residual = float(np.max(np.maximum(
        constraint_audit.drop(
            columns=["Region", "constraint_satisfied"]
        ).to_numpy(float),
        0.0,
    )))
    if task_max_residual > TOL:
        fail(
            "CON-Q2-1",
            task_max_residual,
            TOL,
            "任务或容量硬约束审计失败",
        )

    # Q3 is explicitly bound to the repaired formal Q2 balanced facility load;
    # all five direct schedule hashes are recorded in q3_input_binding.json.
    q3_facility_override = q2_flow[
        ["Region", "Hour", "FacilityLoad_MW"]
    ].copy()
    q3_baseline = _no_action_policy(
        d, facility_override=q3_facility_override
    )
    q3_base_cost, q3_base_carbon, q3_base_re, q3_base_peak, q3_base_ramp = (
        metrics_energy(q3_baseline)
    )
    q3_flow, q3_search, q3_trace = storage_local_search(
        d, facility_override=q3_facility_override
    )
    q3_policy_flows = {
        name: flow.copy() for name, flow in Q3_POLICY_RESULTS.items()
    }
    q3_soc_grid_sensitivity = run_soc_grid_sensitivity(
        d, q3_search["selected_policy"],
        facility_override=q3_facility_override,
    )
    q3_terminal_sensitivity = dict(Q3_TERMINAL_SENSITIVITY)
    q3_cost, q3_carbon, q3_re, q3_peak, q3_ramp = metrics_energy(q3_flow)
    q3_audit = audit_storage_policy(d, q3_flow, "CON-Q3-1")
    print(
        f"结果: 问题三储能搜索完成, 检查候选数="
        f"{int(q3_search['checked_candidates'])}, "
        f"耗时={time.monotonic() - PROGRAM_START:.3f}秒",
        flush=True,
    )

    facility_override = q2_flow[
        ["Region", "Hour", "FacilityLoad_MW"]
    ].copy()
    q4_flow, q4_search, q4_trace = _select_q4_storage_policy(
        d, facility_override
    )
    q4_audit = audit_storage_policy(d, q4_flow, "CON-Q4-1")
    q4_cost, q4_carbon, q4_re, q4_peak, q4_ramp = metrics_energy(q4_flow)
    (
        q4_task_candidates,
        q4_task_candidate_evidence,
        q4_alternative_audits,
    ) = build_q4_task_candidate_set(
        d,
        workload,
        q2_balanced_schedule,
        q2_flow,
        max_checked=Q4_TASK_NEIGHBOR_LIMIT,
    )
    (
        q4_scenarios,
        q4_checked,
        q4_alternation_trace,
        q4_scenario_family_summary,
    ) = run_q4_scenarios(
        d,
        q4_task_candidates,
        q4_flow,
    )
    baseline_scenario = q4_scenarios.iloc[0]
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
        fail("CON-Q4-4", len(q4_scenarios), 17, "规定情景未全部生成")
    if q4_checked < 45:
        fail("CON-Q4-5", q4_checked, 45, "情景候选评价总数不足")
    if (
        (q4_scenarios["checked_candidates"] < 3).any()
        or (q4_scenarios["alternation_rounds"] < 2).any()
        or (q4_scenarios["constraints_satisfied"] != 1).any()
    ):
        raise RuntimeError(
            "CON-Q4-5: actual=0, threshold=1, "
            "存在未完成动态邻域重建或两轮交替评价的情景"
        )
    print(
        f"结果: 问题四任务候选数="
        f"{q4_task_candidate_evidence['candidate_count']}, "
        f"情景候选评价数={q4_checked}, "
        f"最少交替轮数={int(q4_scenarios['alternation_rounds'].min())}, "
        f"耗时={time.monotonic() - PROGRAM_START:.3f}秒",
        flush=True,
    )

    check_deadline("main.before_output")

    q1_schedule_terminal = q1_schedule_full.loc[
        q1_schedule_full["ArrivalHour"].between(2376, 2399)
    ].sort_values(["ArrivalHour", "TaskID"]).reset_index(drop=True)
    if len(q1_schedule_terminal) != 538:
        fail("CON-Q1-8", len(q1_schedule_terminal), 538, "最终24小时实际到达任务数不一致")
    q1_schedule_full.to_csv(RESULT_DIR / "q1_schedule_full.csv", index=False)
    q1_schedule_terminal.to_csv(RESULT_DIR / "q1_schedule.csv", index=False)
    predictions.to_csv(RESULT_DIR / "q1_forecast_2376_2399.csv", index=False)
    forecast_metrics.to_csv(RESULT_DIR / "q1_forecast_metrics.csv", index=False)
    q1_forecast_summary.to_csv(RESULT_DIR / "q1_forecast_summary.csv", index=False)
    q1_rolling_validation.to_csv(RESULT_DIR / "q1_rolling_validation.csv", index=False)
    q1_candidate_summary.to_csv(RESULT_DIR / "q1_candidate_summary.csv", index=False)
    q1_model_selection.to_csv(RESULT_DIR / "q1_model_selection.csv", index=False)
    q1_constraint_audit.to_csv(RESULT_DIR / "q1_constraint_audit.csv", index=False)
    demand.groupby(["Region", "TaskType"], as_index=False).agg(
        GPU_Demand=("GPU_Demand", "sum"), GPUh=("GPUh", "sum")
    ).to_csv(RESULT_DIR / "q1_gpu_statistics.csv", index=False)
    q2_flow.to_csv(RESULT_DIR / "q2_hourly_energy.csv", index=False)
    q3_baseline.to_csv(RESULT_DIR / "q3_no_storage_baseline.csv", index=False)
    q3_flow.to_csv(RESULT_DIR / "q3_storage_energy.csv", index=False)
    q4_flow.to_csv(RESULT_DIR / "q4_joint_storage_energy.csv", index=False)
    constraint_audit.to_csv(RESULT_DIR / "constraint_audit.csv", index=False)
    q3_audit.to_csv(RESULT_DIR / "q3_constraint_audit.csv", index=False)
    q4_audit.to_csv(RESULT_DIR / "q4_constraint_audit.csv", index=False)
    for candidate_id, audit in q4_alternative_audits.items():
        audit.to_csv(
            RESULT_DIR / f"q4_{candidate_id}_constraint_audit.csv",
            index=False,
        )
    q4_scenarios.to_csv(
        RESULT_DIR / "q4_scenario_comparison.csv", index=False
    )
    q4_alternation_trace.to_csv(
        RESULT_DIR / "q4_alternation_trace.csv", index=False
    )
    q4_scenario_family_summary.to_csv(
        RESULT_DIR / "q4_scenario_family_summary.csv", index=False
    )
    pd.DataFrame([q2_search]).to_csv(
        RESULT_DIR / "q2_search_summary.csv", index=False
    )
    # Direct pass traces are streamed during Q2 to bound memory.  The legacy
    # q2_search_trace.csv contains the complete first pass; the new pass trace
    # contains all declared passes.  Carbon refinement remains explicitly separate.
    Q2_CARBON_REFINEMENT_RESULT["trace"].to_csv(
        RESULT_DIR / "q2_carbon_multistart_refinement_trace.csv", index=False
    )
    Q2_COMMON_POOL.to_csv(
        RESULT_DIR / "q2_common_candidate_pool.csv", index=False
    )
    Q2_COMMON_POOL.to_csv(
        RESULT_DIR / "q2_common_base_candidate_pool.csv", index=False
    )
    Q2_COMMON_PROVENANCE["candidate_pool_sha256"] = sha256_file(
        RESULT_DIR / "q2_common_candidate_pool.csv"
    )
    with open(
        RESULT_DIR / "q2_common_candidate_provenance.json", "w", encoding="utf-8"
    ) as f:
        json.dump(Q2_COMMON_PROVENANCE, f, ensure_ascii=False, indent=2)
    Q2_CANDIDATE_COVERAGE.to_csv(
        RESULT_DIR / "q2_candidate_coverage.csv", index=False
    )
    with open(
        RESULT_DIR / "q2_objective_normalization.json", "w", encoding="utf-8"
    ) as f:
        json.dump(Q2_NORMALIZATION, f, ensure_ascii=False, indent=2)
    if Q2_BALANCED_AUDIT is not None:
        Q2_BALANCED_AUDIT.to_csv(
            RESULT_DIR / "q2_balanced_score_audit.csv", index=False
        )
    with open(RESULT_DIR / "q2_candidate_semantic_uniqueness.json", "w", encoding="utf-8") as f:
        json.dump(Q2_SEMANTIC_UNIQUENESS, f, ensure_ascii=False, indent=2)
    Q2_TASK_CANDIDATE_AVAILABILITY.to_csv(
        RESULT_DIR / "q2_task_candidate_availability.csv", index=False
    )
    with open(RESULT_DIR / "q2_attempt_sequence_hashes.json", "w", encoding="utf-8") as f:
        json.dump(Q2_ATTEMPT_SEQUENCE_HASHES, f, ensure_ascii=False, indent=2)
    Q2_PASS_STABILITY.to_csv(RESULT_DIR / "q2_pass_stability.csv", index=False)
    Q2_CONTEXT_CHECKPOINT_AUDIT.to_csv(
        RESULT_DIR / "q2_context_checkpoint_audit.csv", index=False
    )
    with open(RESULT_DIR / "q2_context_checkpoint_summary.json", "w", encoding="utf-8") as f:
        json.dump(Q2_CONTEXT_CHECKPOINT_SUMMARY, f, ensure_ascii=False, indent=2)
    Q2_WEIGHT_SENSITIVITY.to_csv(
        RESULT_DIR / "q2_weight_sensitivity.csv", index=False
    )
    with open(
        RESULT_DIR / "q2_carbon_direct_audit.json", "w", encoding="utf-8"
    ) as f:
        json.dump(Q2_CARBON_DIRECT_AUDIT, f, ensure_ascii=False, indent=2)
    with open(
        RESULT_DIR / "q2_carbon_multistart_audit.json", "w", encoding="utf-8"
    ) as f:
        json.dump(Q2_CARBON_MULTISTART_AUDIT, f, ensure_ascii=False, indent=2)
    Q2_CARBON_REFINEMENT_COMPARISON.to_csv(
        RESULT_DIR / "q2_carbon_refinement_comparison.csv", index=False
    )
    Q2_INCREMENTAL_AUDIT.to_csv(
        RESULT_DIR / "q2_incremental_full_recompute_audit.csv", index=False
    )
    with open(
        RESULT_DIR / "q2_incremental_full_recompute_summary.json", "w", encoding="utf-8"
    ) as f:
        json.dump(Q2_INCREMENTAL_SUMMARY, f, ensure_ascii=False, indent=2)
    Q2_CONVERGENCE_AUDIT.to_csv(
        RESULT_DIR / "q2_convergence_audit.csv", index=False
    )
    with open(
        RESULT_DIR / "q2_formal_budget_decision.json", "w", encoding="utf-8"
    ) as f:
        json.dump({
            "status": Q2_STABILITY_STATUS,
            "formal_pass": Q2_FORMAL_PASS,
            "formal_budget": Q2_FORMAL_BUDGET,
            "base_candidate_count": len(Q2_COMMON_POOL),
            "highest_common_pass": Q2_MAX_PASSES,
            "reason": Q2_STABILITY_REASON,
            "max_passes": Q2_MAX_PASSES,
            "rule": "earliest_common_converged_pass_else_highest_common_completed_pass",
            "auxiliary_metrics_blocking": False,
        }, f, ensure_ascii=False, indent=2)
    q2_budget_stability.to_csv(RESULT_DIR / "q2_budget_stability.csv", index=False)
    q2_metric_stability.to_csv(RESULT_DIR / "q2_metric_stability.csv", index=False)
    pd.DataFrame([q2_stability_summary]).to_csv(
        RESULT_DIR / "q2_stability_summary.csv", index=False
    )
    pd.DataFrame([q3_search]).to_csv(
        RESULT_DIR / "q3_search_summary.csv", index=False
    )
    q3_trace.to_csv(RESULT_DIR / "q3_search_trace.csv", index=False)
    q3_soc_grid_sensitivity.to_csv(RESULT_DIR / "q3_soc_grid_sensitivity.csv", index=False)
    pd.DataFrame([q4_search]).to_csv(
        RESULT_DIR / "q4_search_summary.csv", index=False
    )
    q4_trace.to_csv(RESULT_DIR / "q4_search_trace.csv", index=False)
    q2_comparison_rows = []
    seen_q2_hashes = {}
    for scheme, value in Q2_SCHEME_RESULTS.items():
        row = dict(value["summary"])
        schedule_hash = str(row["schedule_sha256"])
        row["duplicate_of"] = seen_q2_hashes.get(schedule_hash)
        seen_q2_hashes.setdefault(schedule_hash, scheme)
        q2_comparison_rows.append(row)
    pd.DataFrame(q2_comparison_rows).to_csv(
        RESULT_DIR / "q2_named_scheme_comparison.csv", index=False
    )
    for scheme, value in Q2_SCHEME_RESULTS.items():
        value["schedule"].to_csv(
            RESULT_DIR / f"q2_schedule_{scheme}.csv", index=False
        )
        value["flow"].to_csv(
            RESULT_DIR / f"q2_energy_{scheme}.csv", index=False
        )
        Q2_SCHEME_AUDITS[scheme].to_csv(
            RESULT_DIR / f"q2_constraint_audit_{scheme}.csv", index=False
        )
    Q2_CARBON_REFINEMENT_RESULT["schedule"].to_csv(
        RESULT_DIR / "q2_schedule_carbon_multistart_refinement.csv", index=False
    )
    Q2_CARBON_REFINEMENT_RESULT["flow"].to_csv(
        RESULT_DIR / "q2_energy_carbon_multistart_refinement.csv", index=False
    )
    Q2_CARBON_REFINEMENT_RESULT["audit"].to_csv(
        RESULT_DIR / "q2_constraint_audit_carbon_multistart_refinement.csv",
        index=False,
    )
    with open(RESULT_DIR / "q3_input_binding.json", "w", encoding="utf-8") as f:
        json.dump({
            "status": "pass",
            "formal_budget": Q2_FORMAL_BUDGET,
            "direct_schedule_sha256": {
                scheme: value["summary"]["schedule_sha256"]
                for scheme, value in Q2_SCHEME_RESULTS.items()
            },
            "selected_task_schedule": "balanced",
            "selected_schedule_file_sha256": sha256_file(
                RESULT_DIR / "q2_schedule_balanced.csv"
            ),
            "selected_energy_file_sha256": sha256_file(
                RESULT_DIR / "q2_energy_balanced.csv"
            ),
        }, f, ensure_ascii=False, indent=2)
    q3_all_trajectories = pd.concat([
        flow.assign(policy=name) for name, flow in q3_policy_flows.items()
    ], ignore_index=True)
    q3_all_trajectories.to_csv(
        RESULT_DIR / "q3_all_policy_trajectories.csv", index=False
    )
    with open(RESULT_DIR / "q3_terminal_soc_sensitivity.json", "w", encoding="utf-8") as f:
        json.dump(q3_terminal_sensitivity, f, ensure_ascii=False, indent=2)
    with open(RESULT_DIR / "q4_baseline_consistency.json", "w", encoding="utf-8") as f:
        json.dump({
            "status": "pass", "state_count": SOC_STATE_COUNT,
            "storage_policy": q4_search["selected_policy"],
            "joint_metrics": joint_metrics.tolist(),
            "scenario_baseline_metrics": baseline_metrics.tolist(),
            "same_data_source": True,
            "q2_formal_budget": Q2_FORMAL_BUDGET,
            "q2_balanced_schedule_sha256": _schedule_hash(
                q2_balanced_schedule
            ),
            "q2_balanced_schedule_file_sha256": sha256_file(
                RESULT_DIR / "q2_schedule_balanced.csv"
            ),
            "q2_balanced_energy_file_sha256": sha256_file(
                RESULT_DIR / "q2_energy_balanced.csv"
            ),
        }, f, ensure_ascii=False, indent=2)

    q2_latency, wait_quality, migrated = service_metrics(q2_balanced_schedule)
    q2_tail_count = int((q2_balanced_schedule["FinishHour"] > 2400).sum())
    q1_tail_count = int((q1_schedule_terminal["FinishHour"] > 2400).sum())

    manifest = []
    q1_utilization = pd.DataFrame({"Hour": range(2376, 2400)})
    gpu_info = d["gpu"].set_index("Region")
    for idx, region in enumerate(REGIONS):
        q1_utilization[region] = (
            q1_used_gpu[idx, 2376:2400]
            / float(gpu_info.loc[region, "Available_GPU"])
        )
    q1_utilization.to_csv(RESULT_DIR / "q1_gpu_utilization.csv", index=False)
    q1_gantt = q1_schedule_terminal[[
        "TaskID", "TaskType", "SourceRegion", "ExecutionRegion",
        "ArrivalHour", "StartHour", "FinishHour", "WaitHour",
        "NetworkLatency_ms", "GPU_Demand",
    ]].copy()
    save_q1_gantt(q1_gantt, manifest)
    save_figure(
        q1_utilization, "q1_gpu_utilization.png", "line", "Hour", REGIONS,
        "问题一：最后24小时区域GPU利用率", "时刻 / h", "GPU利用率 / 无量纲", manifest
    )
    q1_peak_utilization = float(q1_utilization[REGIONS].to_numpy(float).max())
    q1_mean_utilization = float(q1_utilization[REGIONS].to_numpy(float).mean())

    soc_plot = q4_flow.pivot(index="Hour", columns="Region", values="SOC_MWh").reset_index()
    save_figure(
        soc_plot, "fig_2_storage_soc.png", "line", "Hour", REGIONS,
        "区域储能SOC轨迹", "时刻 / h", "SOC / MWh", manifest
    )

    sensitivity = {"baseline": {"objective": q2_cost, "objective_name": "系统运行成本"},
                   "experiments": []}
    for param, factors in {
        "electricity_price": [-20, -10, 10, 20],
        "renewable_level": [-20, -10, 10, 20],
    }.items():
        rows = []
        for delta in factors:
            if param == "electricity_price":
                obj = q2_cost + np.sum(
                    q2_flow["OptimizedGridPurchase_MW"] *
                    q2_flow["ElectricityPrice_CNY_per_MWh"] * delta / 100
                )
                param_value = 1 + delta / 100
            else:
                rav = np.maximum(
                    0.0,
                    q2_flow["AvailableRenewable_MW"].to_numpy(float)
                    * (1 + delta / 100),
                )
                use = np.minimum(
                    rav, q2_flow["FacilityLoad_MW"].to_numpy(float)
                )
                buy = q2_flow["FacilityLoad_MW"].to_numpy(float) - use
                surplus = np.maximum(0.0, rav - use)
                sell = np.minimum(
                    surplus,
                    q2_flow["GridExportLimit_MW"].to_numpy(float),
                )
                obj = np.sum(
                    buy
                    * q2_flow["ElectricityPrice_CNY_per_MWh"].to_numpy(float)
                    - sell
                    * q2_flow["SellPrice_CNY_per_MWh"].to_numpy(float)
                )
                param_value = 1 + delta / 100
            obj = finite(obj, "sensitivity_objective")
            if abs(q2_cost) <= TOL:
                raise RuntimeError(
                    "SENSITIVITY-BASELINE: actual=0, "
                    "threshold=nonzero baseline objective"
                )
            change = finite(
                100.0 * (obj - q2_cost) / abs(q2_cost),
                "sensitivity_change",
            )
            sensitivity["experiments"].append({
                "param": param, "delta_pct": delta,
                "param_value": param_value,
                "objective": obj, "change_pct": change,
            })
            rows.append({"delta_pct": delta, "objective": obj, "baseline": q2_cost})
        frame = pd.DataFrame(rows)
        file_name = f"sensitivity_{param}.png"
        save_figure(
            frame, file_name, "line", "delta_pct", ["objective", "baseline"],
            f"{param}灵敏度", "扰动幅度 / %", "系统运行成本 / 元", manifest
        )

    sensitivity["q2_budget_stability"] = q2_budget_stability.to_dict("records")
    sensitivity["q2_metric_stability"] = q2_metric_stability.to_dict("records")
    sensitivity["q2_stability_summary"] = q2_stability_summary
    sensitivity["q3_soc_grid"] = q3_soc_grid_sensitivity.to_dict("records")
    sensitivity["storage_parameter_boundary"] = (
        "题面未给出退化成本或循环寿命参数；吞吐量和等效循环仅作为理想设备敏感性证据"
    )
    with open(RESULT_DIR / "sensitivity.json", "w", encoding="utf-8") as f:
        json.dump(sensitivity, f, ensure_ascii=False, indent=2)

    results = []
    workload_missing = int(d["workload"].isna().sum().sum())
    results.extend([
        result_item("q1_原始行数", len(d["workload"]), "条", "工作负载原始任务数"),
        result_item("q1_有效行数", len(workload), "条", "通过输入校验的任务数"),
        result_item("q1_缺失数量", workload_missing, "个", "工作负载缺失单元格数"),
        result_item("q1_缺失率", workload_missing / d["workload"].size, "", "缺失单元格比例"),
        result_item("q1_预测总体MAE", float(q1_forecast_summary.loc[q1_forecast_summary["Metric"].eq("Overall MAE"), "Value"].iloc[0]), "GPU", "全部18x24观测总体MAE"),
        result_item("q1_预测总体RMSE", float(q1_forecast_summary.loc[q1_forecast_summary["Metric"].eq("Overall RMSE"), "Value"].iloc[0]), "GPU", "全部18x24观测总体RMSE"),
        result_item("q1_预测Macro_WAPE", float(q1_forecast_summary.loc[q1_forecast_summary["Metric"].eq("Macro-WAPE"), "Value"].iloc[0]), "", "18条序列WAPE算术平均；对低基数序列敏感"),
        result_item("q1_预测Micro_WAPE", float(q1_forecast_summary.loc[q1_forecast_summary["Metric"].eq("Micro-WAPE"), "Value"].iloc[0]), "", "432个观测按真实需求规模加权"),
        result_item("q1_预测System_Aggregate_WAPE", float(q1_forecast_summary.loc[q1_forecast_summary["Metric"].eq("System Aggregate WAPE"), "Value"].iloc[0]), "", "逐小时先聚合18序列；允许高估低估抵消"),
        result_item("q1_rolling_origin窗口数", len(Q1_ROLLING_ORIGINS), "个", "完全位于最终测试之前的expanding-window验证"),
        result_item("q1_rolling_origin候选评估数", len(q1_rolling_validation), "次", "18序列x11候选x8原点"),
        result_item("q1_基础调度峰值GPU利用率", q1_peak_utilization, "", "由Q1完整50000任务基础调度独立复算"),
        result_item("q1_基础调度平均GPU利用率", q1_mean_utilization, "", "Q1完整调度在6区域x24小时的算术平均"),
        result_item("q2_迁移任务数", migrated, "个", "执行区域不同于来源区域的任务数"),
        result_item("q2_局部搜索候选数", q2_search["checked_candidates"], "个", "实际完整检查的单任务候选数"),
        result_item("q2_局部搜索接受改进数", q2_search["accepted_improvements"], "个", q2_search["status"]),
        result_item("q2_公共前缀任务覆盖率", q2_search["task_coverage_rate"], "", "五种直接方案共用完全相同的 CandidateID 前缀"),
        result_item("q2_单方案最小任务覆盖率", min(value["summary"]["task_coverage_rate"] for value in Q2_SCHEME_RESULTS.values()), "", "每方案均使用正式公共预算前缀"),
        result_item("q2_局部搜索前运行成本", q2_search["baseline_cost_CNY"], "元", "可行调度基线"),
        result_item("q2_局部搜索后运行成本", q2_search["final_cost_CNY"], "元", "有限搜索best-found"),
        result_item("q2_局部搜索前碳排放", q2_search["baseline_carbon_tCO2"], "tCO2", "可行调度基线"),
        result_item("q2_局部搜索后碳排放", q2_search["final_carbon_tCO2"], "tCO2", "有限搜索best-found"),
        result_item(
            "q2_多目标稳定性未收敛指标数",
            len([value for value in q2_stability_summary["nonconverged_metrics"].split("|") if value]),
            "个",
            f"metric_stability_status={q2_stability_summary['metric_stability_status']}; nonconverged_metrics={q2_stability_summary['nonconverged_metrics'] or 'none'}",
        ),
        result_item("q3_储能搜索候选数", q3_search["checked_candidates"], "个", "实际完整审计的储能候选数"),
        result_item("q3_储能搜索接受改进数", q3_search["accepted_improvements"], "个", q3_search["status"]),
        result_item("q3_无储能基线运行成本", q3_base_cost, "元", "固定Baseline AI负荷的无储能比较状态"),
        result_item("q3_含储能运行成本", q3_cost, "元", "固定Baseline AI负荷的含储能策略"),
        result_item("q3_储能运行成本变化量", q3_cost - q3_base_cost, "元", "含储能减无储能基线"),
        result_item("q3_无储能基线碳排放", q3_base_carbon, "tCO2", "固定负荷无储能碳排放"),
        result_item("q3_含储能碳排放", q3_carbon, "tCO2", "固定负荷含储能碳排放"),
        result_item("q3_储能碳排放变化量", q3_carbon - q3_base_carbon, "tCO2", "含储能减无储能基线"),
        result_item("q3_无储能峰值净购电功率", q3_base_peak, "MW", "六区域非负峰值之和"),
        result_item("q3_含储能峰值净购电功率", q3_peak, "MW", "六区域非负峰值之和"),
        result_item("q3_峰值净购电变化量", q3_peak - q3_base_peak, "MW", "含储能减无储能基线"),
        result_item("q3_无储能绝对爬坡量", q3_base_ramp, "MW", "六区域逐时绝对变化量之和"),
        result_item("q3_含储能绝对爬坡量", q3_ramp, "MW", "六区域逐时绝对变化量之和"),
        result_item("q3_绝对爬坡变化量", q3_ramp - q3_base_ramp, "MW", "含储能减无储能基线"),
        result_item("q4_联合基准运行成本", q4_cost, "元", "使用任务调度派生设施负荷的联合基准"),
        result_item("q4_联合基准碳排放", q4_carbon, "tCO2", "使用任务调度派生设施负荷的联合基准"),
        result_item("q4_联合基准新能源利用率", q4_re, "", "联合基准新能源利用率"),
        result_item("q4_联合基准峰值净购电功率", q4_peak, "MW", "六区域非负峰值之和"),
        result_item("q4_统一SOC状态数", SOC_STATE_COUNT, "个", "联合基准与17个情景使用同一显式配置"),
        result_item(
            "q4_共同起始任务方案数",
            q4_task_candidate_evidence["candidate_count"],
            "个",
            "各情景共享一个经50000任务全量审计的起点；替代调度在各情景各轮动态重建，fixed_candidate_set=false",
        ),
        result_item(
            "q4_情景任务候选评价数",
            q4_checked,
            "次",
            "17个情景均按上一轮储能状态动态重建任务邻域并重新选择储能政策",
        ),
        result_item(
            "q4_情景最小交替轮数",
            q4_scenarios["alternation_rounds"].min(),
            "轮",
            "各情景实际完成轮数的最小值",
        ),
        result_item(
            "q4_情景最大交替轮数",
            q4_scenarios["alternation_rounds"].max(),
            "轮",
            "各情景实际完成轮数的最大值",
        ),
        result_item(
            "q4_情景交替总轮数",
            q4_scenarios["alternation_rounds"].sum(),
            "轮",
            "17个情景实际完成轮数之和",
        ),
        result_item(
            "q4_情景接受轮数",
            q4_scenarios["accepted_rounds"].sum(),
            "轮",
            "联合目标严格改善后接受的动态任务-储能交替轮数",
        ),
        result_item(
            "q4_完成情景数",
            int(q4_scenarios["constraints_satisfied"].sum()),
            "个",
            "规定的17个情景均完成动态邻域复算与硬约束审计",
        ),
        result_item(
            "q4_网络时延",
            q2_latency,
            "ms",
            "联合基准任务方案的GPU小时加权单向网络时延",
        ),
        result_item("q4_服务质量等待分量", wait_quality, "", "按平均等待构造的有限代理指标"),
    ])

    scenario_metric_columns = {
        "运行成本": ("cost_CNY", "元"),
        "碳排放": ("carbon_tCO2", "tCO2"),
        "新能源利用率": ("renewable_utilization", ""),
        "峰值净购电功率": ("peak_grid_purchase_MW", "MW"),
    }
    scenario_baseline = q4_scenarios.iloc[0]
    for scenario_index, scenario_row in q4_scenarios.iterrows():
        scenario_key = (
            f"{scenario_row['scenario_type']}_{scenario_row['parameter']}_"
            f"{scenario_row['level']}"
        )
        for metric_name, (column, unit) in scenario_metric_columns.items():
            value = finite(scenario_row[column], f"q4_{scenario_key}_{metric_name}")
            baseline_value = finite(
                scenario_baseline[column],
                f"q4_baseline_{metric_name}",
            )
            results.append(result_item(
                f"q4_情景{scenario_index + 1}_{metric_name}",
                value,
                unit,
                f"{scenario_key};相对统一基准绝对变化="
                f"{value - baseline_value:.12g};"
                f"selected_candidate={scenario_row['selected_candidate']}",
            ))

    scenario_completed = q4_scenarios["checked_candidates"].astype(int)
    carbon_count = int(scenario_completed[
        q4_scenarios["scenario_type"].eq("carbon_constraint")
    ].sum())
    price_count = int(scenario_completed[
        q4_scenarios["scenario_type"].isin(["price_spread", "sell_mechanism"])
    ].sum())
    renewable_count = int(scenario_completed[
        q4_scenarios["scenario_type"].isin(
            ["renewable_level", "renewable_volatility"]
        )
    ].sum())
    values = {
        "q1": [
            len(demand), len(predictions), forecast_metrics["RMSE"].mean(),
            len(q1_schedule_terminal),
            q1_tail_count, 1, q1_peak_utilization,
        ],
        "q2": [len(q2_balanced_schedule), q2_cost, q2_carbon, q2_latency, q2_re, q2_tail_count, 1],
        "q3": [
            q3_flow["Charge_MW"].sum(), q3_flow["Discharge_MW"].sum(),
            q3_flow.query("Hour == 2406")["SOC_MWh"].sum(),
            len(q3_flow), q3_cost - q3_base_cost,
            q3_carbon - q3_base_carbon,
            q3_peak - q3_base_peak,
            q3_ramp - q3_base_ramp,
            int((q3_audit.drop(columns="Region").to_numpy(float) <= TOL).all()),
        ],
        "q4": [
            migrated, q4_flow["Charge_MW"].sum(), len(q4_flow),
            q4_cost, q4_carbon, q2_latency, wait_quality, q4_re,
            q4_peak,
            int(q4_checked > 0),
            carbon_count,
            price_count,
            renewable_count,
            int(
                constraint_audit["constraint_satisfied"].all()
                and (q4_audit.drop(columns="Region").to_numpy(float) <= TOL).all()
            ),
        ],
    }
    units = {
        "q1": ["行", "条", "GPU", "个", "个", "个", ""],
        "q2": ["个", "元", "tCO2", "ms", "", "个", ""],
        "q3": ["MWh", "MWh", "MWh", "行", "元", "tCO2", "MW", "MW", ""],
        "q4": ["个", "MWh", "行", "元", "tCO2", "ms", "", "", "MW", "", "个", "个", "个", ""],
    }
    for q, names in REQUIRED_NAMES.items():
        for name, value, unit in zip(names, values[q], units[q]):
            results.append(result_item(name, value, unit, "详细结果见当前运行生成的fresh CSV;状态值由实际审计或实际情景计数派生"))

    schedule_provenance = {
        "schema_version": 1,
        "q1_method": "greedy_schedule_full_horizon_scenario_feasible_incumbent",
        "q2_method": "balanced_finite_search_from_q1_incumbent",
        "q1_schedule_full": {
            "file": "q1_schedule_full.csv",
            "sha256": sha256_file(RESULT_DIR / "q1_schedule_full.csv"),
            "task_count": int(len(q1_schedule_full)),
        },
        "q1_schedule_terminal": {
            "file": "q1_schedule.csv",
            "sha256": sha256_file(RESULT_DIR / "q1_schedule.csv"),
            "task_count": int(len(q1_schedule_terminal)),
            "arrival_window": [2376, 2399],
        },
        "q2_balanced_schedule": {
            "file": "q2_schedule_balanced.csv",
            "sha256": sha256_file(RESULT_DIR / "q2_schedule_balanced.csv"),
            "task_count": int(len(q2_balanced_schedule)),
        },
        "figures": {
            "q1_gantt.png": {
                "data_file": "q1_gantt.csv",
                "data_sha256": sha256_file(RESULT_DIR / "q1_gantt.csv"),
                "figure_sha256": sha256_file(FIGURE_DIR / "q1_gantt.png"),
                "generator": "save_q1_gantt",
            },
            "q1_gpu_utilization.png": {
                "data_file": "q1_gpu_utilization.csv",
                "data_sha256": sha256_file(RESULT_DIR / "q1_gpu_utilization.csv"),
                "figure_sha256": sha256_file(FIGURE_DIR / "q1_gpu_utilization.png"),
                "generator": "save_figure_from_q1_full_used_gpu",
            },
        },
    }
    schedule_provenance["q1_q2_distinct"] = (
        schedule_provenance["q1_schedule_full"]["sha256"]
        != schedule_provenance["q2_balanced_schedule"]["sha256"]
    )
    if not schedule_provenance["q1_q2_distinct"]:
        raise RuntimeError("Q1-PROVENANCE-001: Q1 full schedule silently equals Q2 balanced")
    with open(RESULT_DIR / "schedule_provenance.json", "w", encoding="utf-8") as handle:
        json.dump(schedule_provenance, handle, ensure_ascii=False, indent=2)

    with open(RESULT_DIR / "results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    with open(RESULT_DIR / "figure_manifest.json", "w", encoding="utf-8") as f:
        json.dump({"schema_version": 1, "figures": manifest}, f, ensure_ascii=False, indent=2)

    checked = [
        "CON-Q1-1", "CON-Q1-2", "CON-Q1-3", "CON-Q1-4", "CON-Q1-5",
        "CON-Q1-6", "CON-Q1-7", "CON-Q1-8", "CON-Q2-1", "CON-Q2-2", "CON-Q2-3",
        "CON-Q2-4", "CON-Q2-5", "CON-Q2-6", "CON-Q3-1", "CON-Q3-2",
        "CON-Q3-3", "CON-Q3-4", "CON-Q3-5", "CON-Q3-6", "CON-Q3-7",
        "CON-Q4-1", "CON-Q4-2", "CON-Q4-3", "CON-Q4-4", "CON-Q4-5",
        "CON-Q4-6",
    ]
    audit_numeric = constraint_audit.drop(
        columns=["Region", "constraint_satisfied"]
    )
    actual_maxima = {
        col: finite(audit_numeric[col].max(), col)
        for col in audit_numeric.columns
    }
    storage_maxima = {
        "q3_max_constraint_residual": finite(
            np.max(np.maximum(
                q3_audit.drop(columns="Region").to_numpy(float), 0.0
            )),
            "q3_max_constraint_residual",
        ),
        "q4_max_constraint_residual": finite(
            np.max(np.maximum(
                q4_audit.drop(columns="Region").to_numpy(float), 0.0
            )),
            "q4_max_constraint_residual",
        ),
    }
    feasible = bool(
        constraint_audit["constraint_satisfied"].all()
        and storage_maxima["q3_max_constraint_residual"] <= TOL
        and storage_maxima["q4_max_constraint_residual"] <= TOL
    )
    if not feasible:
        fail(
            "CON-Q4-1",
            max(
                task_max_residual,
                storage_maxima["q3_max_constraint_residual"],
                storage_maxima["q4_max_constraint_residual"],
            ),
            TOL,
            "最终联合候选硬约束失败",
        )
    runtime = {
        "schema_version": 2,
        "algorithm_class": "heuristic",
        **run_identity(),
        "result_level": "scenario-feasible",
        "official_soc_state_count": SOC_STATE_COUNT,
        "default_wallclock_limit": None,
        "explicit_wallclock_limit_seconds": MAX_RUNTIME_SECONDS,
        "termination_status": "completed",
        "incomplete": False,
        "feasible": feasible,
        "constraints_checked": checked,
        "seed": SEED,
        "objective_value": q4_cost,
        "constraint_tolerance": TOL,
        "constraint_actual_maxima": actual_maxima,
        "storage_constraint_actual_maxima": storage_maxima,
        "q4_scenarios_checked": int(q4_checked),
        "search_evidence": {
            "q1": {
                "rolling_origins": list(Q1_ROLLING_ORIGINS),
                "rolling_horizon_hours": Q1_FORECAST_HORIZON,
                "candidate_count_per_series": len(_forecast_candidate_specs()),
                "rolling_candidate_evaluations": int(len(q1_rolling_validation)),
                "full_schedule_task_count": int(len(q1_schedule_full)),
                "terminal_schedule_task_count": int(len(q1_schedule_terminal)),
                "tail_settlement_task_count": q1_tail_count,
                "peak_gpu_utilization": q1_peak_utilization,
                "mean_gpu_utilization": q1_mean_utilization,
                "final_test_used_for_selection": False,
            },
            "q2": {
                "candidate_order": "objective-independent deterministic round-robin layers",
                "common_candidate_prefix": True,
                "candidate_pool_sha256": q2_search["common_candidate_pool_sha256"],
                "formal_budget": int(q2_search["formal_budget"]),
                "budget_stability_levels": list(Q2_STABILITY_BUDGETS),
                "metric_stability_status": q2_stability_summary["metric_stability_status"],
                "converged_metrics": q2_stability_summary["converged_metrics"],
                "nonconverged_metrics": q2_stability_summary["nonconverged_metrics"],
                "declared_candidate_limit": int(
                    q2_search["declared_candidate_limit"]
                ),
                "task_pool_size": int(q2_search["task_pool_size"]),
                "status": q2_search["status"],
                "checked_candidates": int(q2_search["checked_candidates"]),
                "accepted_improvements": int(q2_search["accepted_improvements"])
            },
            "q3": {
                "status": q3_search["status"],
                "state_count": SOC_STATE_COUNT,
                "decision_method": q3_search["decision_method"],
                "selected_ideal_distance": q3_search["selected_ideal_distance"],
                "checked_candidates": int(q3_search["checked_candidates"]),
                "accepted_improvements": int(q3_search["accepted_improvements"])
            },
            "q4_baseline": {
                "status": q4_search["status"],
                "state_count": SOC_STATE_COUNT,
                "baseline_consistent_with_scenarios": q4_baseline_consistent,
                "checked_candidates": int(q4_search["checked_candidates"]),
                "accepted_improvements": int(q4_search["accepted_improvements"])
            },
            "q4_task_candidate_set": {
                "status": q4_task_candidate_evidence["status"],
                "candidate_count": int(
                    q4_task_candidate_evidence["candidate_count"]
                ),
                "different_candidate_count": int(
                    q4_task_candidate_evidence[
                        "different_candidate_count"
                    ]
                ),
                "neighbor_candidates_checked": int(
                    q4_task_candidate_evidence[
                        "neighbor_candidates_checked"
                    ]
                ),
                "full_task_audits": int(
                    q4_task_candidate_evidence["full_task_audits"]
                ),
                "fixed_candidate_set": bool(q4_task_candidate_evidence["fixed_candidate_set"]),
                "dynamic_neighborhood_rebuilt_each_round": True,
                "alternative_constraint_residuals": {
                    candidate_id: finite(value, candidate_id)
                    for candidate_id, value in
                    q4_task_candidate_evidence[
                        "alternative_constraint_residuals"
                    ].items()
                },
                "alternative_max_constraint_residual": finite(
                    q4_task_candidate_evidence[
                        "alternative_max_constraint_residual"
                    ],
                    "q4_alternative_max_constraint_residual",
                ),
            },
            "q4_scenarios": {
                "scenario_count": int(len(q4_scenarios)),
                "minimum_alternation_rounds": int(q4_scenarios["alternation_rounds"].min()),
                "maximum_alternation_rounds": int(q4_scenarios["alternation_rounds"].max()),
                "total_alternation_rounds": int(q4_scenarios["alternation_rounds"].sum()),
                "accepted_alternation_rounds": int(q4_scenarios["accepted_rounds"].sum()),
                "storage_policy_candidates": list(Q4_STORAGE_POLICIES),
                "scenario_family_degenerate_count": int(q4_scenario_family_summary["degenerate_scenario"].astype(bool).sum()),
                "required_minimum_checked_candidates_per_scenario": (
                    Q4_TASK_NEIGHBOR_LIMIT * Q4_NO_IMPROVEMENT_ROUNDS
                ),
                "checked_candidates": int(q4_checked),
                "minimum_candidates_per_completed_scenario": int(
                    q4_scenarios.loc[
                        q4_scenarios["constraints_satisfied"].eq(1),
                        "checked_candidates",
                    ].min()
                ),
                "candidate_limit_per_round": Q4_TASK_NEIGHBOR_LIMIT,
                "max_rounds_per_scenario": Q4_MAX_ROUNDS,
                "all_scenarios_rebuilt_dynamic_neighborhood": bool(
                    (
                        q4_scenarios.loc[
                            q4_scenarios["constraints_satisfied"].eq(1),
                            "checked_candidates",
                        ] >= 3
                    ).all()
                ),
                "all_scenarios_completed_two_alternation_rounds": bool(
                    (q4_scenarios["alternation_rounds"] >= 2).all()
                ),
                "trace_rows": int(len(q4_alternation_trace)),
                "random_seeds": [2026, 2027, 2028],
            }
        },
        "optimizer": {"used": False},
        "global_optimality_certificate": False,
        "non_Pareto": True,
        "elapsed_seconds": finite(time.monotonic() - PROGRAM_START, "elapsed"),
    }
    with open(RESULT_DIR / "method_runtime.json", "w", encoding="utf-8") as f:
        json.dump(runtime, f, ensure_ascii=False, indent=2)

    print(f"结果: 问题二运行成本={q2_cost:.6f}", flush=True)
    print(f"结果: 问题二碳排放={q2_carbon:.6f}", flush=True)
    print(f"结果: 问题二局部搜索状态={q2_search['status']}", flush=True)
    print(f"结果: 问题二检查候选数={int(q2_search['checked_candidates'])}", flush=True)
    print(f"结果: 问题三运行成本={q3_cost:.6f}", flush=True)
    print(f"结果: 问题三储能搜索状态={q3_search['status']}", flush=True)
    print(f"结果: 问题三检查候选数={int(q3_search['checked_candidates'])}", flush=True)
    print(f"结果: 问题四联合运行成本={q4_cost:.6f}", flush=True)
    print(f"结果: 问题四联合搜索状态={q4_search['status']}", flush=True)
    print(f"结果: 约束满足={feasible}", flush=True)
    print(f"结果: full_horizon_feasible={feasible}", flush=True)
    print("结果: non_Pareto=true", flush=True)
    print("结果: global_optimality_certificate=false", flush=True)


def _fast_schedule_resources(d, schedule):
    """与逐任务区间累加等价的差分数组实现。"""
    region_index = {region: index for index, region in enumerate(REGIONS)}
    power = d["power"].set_index("TaskType")[
        "GPU_Power_MW_per_EquivalentGPU"
    ].to_dict()
    starts = schedule["StartHour"].to_numpy(float)
    finishes = schedule["FinishHour"].to_numpy(float)
    start_slots = starts.astype(int)
    end_slots = np.minimum(2406, np.ceil(finishes - TOL).astype(int))
    if (
        np.any(starts < -TOL)
        or np.any(np.abs(starts - start_slots) > TOL)
        or np.any(end_slots <= start_slots)
        or np.any(end_slots > 2406)
    ):
        return None, None
    region_slots = schedule["ExecutionRegion"].map(region_index)
    if region_slots.isna().any():
        return None, None
    region_slots = region_slots.to_numpy(int)
    gpu_values = schedule["GPU_Demand"].to_numpy(float)
    power_values = gpu_values * schedule["TaskType"].map(power).to_numpy(float)
    gpu_diff = np.zeros((len(REGIONS), 2408), dtype=float)
    power_diff = np.zeros_like(gpu_diff)
    np.add.at(gpu_diff, (region_slots, start_slots), gpu_values)
    np.add.at(gpu_diff, (region_slots, end_slots), -gpu_values)
    np.add.at(power_diff, (region_slots, start_slots), power_values)
    np.add.at(power_diff, (region_slots, end_slots), -power_values)
    return (
        np.cumsum(gpu_diff, axis=1)[:, :2407],
        np.cumsum(power_diff, axis=1)[:, :2407],
    )


def _joined_schedule(workload, schedule):
    source = workload[[
        "TaskID", "SourceRegion", "ArrivalHour", "LatestFinishHour",
        "MaxLatency_ms",
    ]].copy()
    authoritative = [column for column in source.columns if column != "TaskID"]
    base = schedule.drop(
        columns=[column for column in authoritative if column in schedule.columns]
    )
    return base.merge(source, on="TaskID", how="left", validate="one_to_one")


def schedule_candidate_feasible(d, workload, schedule):
    if len(schedule) != len(workload) or schedule["TaskID"].duplicated().any():
        return False, None
    if set(schedule["TaskID"]) != set(workload["TaskID"]):
        return False, None
    joined = _joined_schedule(workload, schedule)
    if joined["SourceRegion"].isna().any():
        return False, None
    start = joined["StartHour"].to_numpy(float)
    arrival = joined["ArrivalHour"].to_numpy(float)
    finish = joined["FinishHour"].to_numpy(float)
    finish_limit = np.minimum(
        joined["LatestFinishHour"].to_numpy(float), 2406.0
    )
    realtime = joined["TaskType"].eq("RealTimeInference").to_numpy()
    if (
        np.any(start < arrival - TOL)
        or np.any(np.abs(start[realtime] - arrival[realtime]) > TOL)
        or np.any(finish > finish_limit + TOL)
    ):
        return False, None
    latency = d["latency"].set_index(["FromRegion", "ToRegion"])[
        "NetworkLatency_ms"
    ]
    actual_latency = np.asarray([
        latency.loc[(source_region, execution_region)]
        for source_region, execution_region in zip(
            joined["SourceRegion"], joined["ExecutionRegion"]
        )
    ], dtype=float)
    if np.any(actual_latency > joined["MaxLatency_ms"].to_numpy(float) + TOL):
        return False, None
    used_gpu, used_power = _fast_schedule_resources(d, schedule)
    if used_gpu is None:
        return False, None
    gpu = d["gpu"].set_index("Region")
    nonai = d["region"].pivot(
        index="Region", columns="Hour", values="NonAI_IT_Load_MW"
    ).reindex(index=REGIONS, columns=range(2407)).to_numpy(float)
    for index, region in enumerate(REGIONS):
        if np.max(used_gpu[index] - float(gpu.loc[region, "Available_GPU"])) > TOL:
            return False, None
        it_load = nonai[index] + used_power[index]
        if np.max(it_load - float(gpu.loc[region, "Max_IT_Power_MW"])) > TOL:
            return False, None
        if np.max(
            it_load * float(gpu.loc[region, "PUE"])
            - float(gpu.loc[region, "Max_Facility_Power_MW"])
        ) > TOL:
            return False, None
    return True, used_gpu


def build_constraint_audit(d, workload, schedule, used_gpu):
    joined = _joined_schedule(workload, schedule)
    latency = d["latency"].set_index(["FromRegion", "ToRegion"])[
        "NetworkLatency_ms"
    ]
    joined["_latency_residual"] = [
        float(latency.loc[(source, execution)]) - float(limit)
        for source, execution, limit in zip(
            joined["SourceRegion"], joined["ExecutionRegion"], joined["MaxLatency_ms"]
        )
    ]
    joined["_deadline_residual"] = joined["FinishHour"].to_numpy(float) - np.minimum(
        joined["LatestFinishHour"].to_numpy(float), 2406.0
    )
    joined["_realtime_residual"] = np.where(
        joined["TaskType"].eq("RealTimeInference"),
        np.abs(joined["StartHour"].to_numpy(float) - joined["ArrivalHour"].to_numpy(float)),
        0.0,
    )
    joined["_terminal_residual"] = joined["FinishHour"].to_numpy(float) - 2406.0
    _, used_power = _fast_schedule_resources(d, schedule)
    gpu = d["gpu"].set_index("Region")
    nonai = d["region"].pivot(
        index="Region", columns="Hour", values="NonAI_IT_Load_MW"
    ).reindex(index=REGIONS, columns=range(2407)).to_numpy(float)
    unique_residual = float(max(
        int(schedule["TaskID"].duplicated().sum()),
        len(set(workload["TaskID"]) - set(schedule["TaskID"])),
        len(set(schedule["TaskID"]) - set(workload["TaskID"])),
    ))
    rows = []
    for index, region in enumerate(REGIONS):
        group = joined.loc[joined["ExecutionRegion"].eq(region)]
        def maximum(column):
            return float(group[column].max()) if len(group) else 0.0
        it_load = nonai[index] + used_power[index]
        row = {
            "Region": region,
            "max_gpu_residual": float(np.max(
                used_gpu[index] - float(gpu.loc[region, "Available_GPU"])
            )),
            "max_it_residual_MW": float(np.max(
                it_load - float(gpu.loc[region, "Max_IT_Power_MW"])
            )),
            "max_facility_residual_MW": float(np.max(
                it_load * float(gpu.loc[region, "PUE"])
                - float(gpu.loc[region, "Max_Facility_Power_MW"])
            )),
            "task_unique_residual": unique_residual,
            "max_latency_residual_ms": max(0.0, maximum("_latency_residual")),
            "max_deadline_residual_h": max(0.0, maximum("_deadline_residual")),
            "max_realtime_start_residual_h": maximum("_realtime_residual"),
            "max_terminal_2406_residual_h": max(0.0, maximum("_terminal_residual")),
        }
        row["constraint_satisfied"] = bool(
            max(value for key, value in row.items() if key != "Region") <= TOL
        )
        rows.append(row)
    return pd.DataFrame(rows)


if __name__ == "__main__":
    try:
        if PILOT_MODE:
            pilot(read_inputs())
        else:
            main()
    except ExternalTimeout as exc:
        write_timeout_evidence(exc)
        print(f"结果: termination_status=external_timeout; incomplete=true; {exc}", flush=True)
        raise SystemExit(124)
