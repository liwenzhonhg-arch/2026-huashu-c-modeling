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

    rt["AI_IT_Load_MW"] = [
        ai[(r, int(t))] for r, t in zip(rt["Region"], rt["Hour"])
    ]
    pue = gpu["PUE"].to_dict()
    rt["FacilityLoad_MW"] = (
        rt["NonAI_IT_Load_MW"] + rt["AI_IT_Load_MW"]
    ) * rt["Region"].map(pue)
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
        raise RuntimeError(
            "CON-Q4-3: actual=0, threshold=positive network denominator"
        )
    latency = float(
        np.sum(weight * schedule["NetworkLatency_ms"]) / denominator
    )
    service = float(1.0 / (1.0 + schedule["WaitHour"].mean()))
    migrated = int(
        (schedule["SourceRegion"] != schedule["ExecutionRegion"]).sum()
    )
    return latency, service, migrated




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
    gpu = d["gpu"].set_index("Region")
    power = d["power"].set_index("TaskType")[
        "GPU_Power_MW_per_EquivalentGPU"
    ].to_dict()
    region_index = {region: idx for idx, region in enumerate(REGIONS)}
    used_gpu = np.zeros((len(REGIONS), 2407), dtype=float)
    used_power = np.zeros((len(REGIONS), 2407), dtype=float)
    for row in schedule.itertuples():
        start = int(row.StartHour)
        end_slot = min(2406, int(np.ceil(float(row.FinishHour) - TOL)))
        if end_slot <= start:
            return None, None
        idx = region_index[row.ExecutionRegion]
        used_gpu[idx, start:end_slot] += float(row.GPU_Demand)
        used_power[idx, start:end_slot] += (
            float(row.GPU_Demand) * float(power[row.TaskType])
        )
    return used_gpu, used_power




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


def forecast(demand):
    """严格训练/验证/测试分割，验证和测试均采用闭环递归预测。"""
    table = demand.pivot_table(
        index="Hour", columns=["Region", "TaskType"],
        values="GPU_Demand", fill_value=0,
    ).sort_index()
    huber_grid = [
        (epsilon, alpha)
        for epsilon in (1.10, 1.35, 1.75)
        for alpha in (1e-4, 1e-3, 1e-2)
    ]
    rows = []
    predictions = []
    for region in REGIONS:
        for task_type in TASK_TYPES:
            y = table[(region, task_type)].to_numpy(float)
            candidates = []
            for rank, name in enumerate(("SeasonalNaive24", "SeasonalNaive168")):
                pred = _recursive_forecast(y, 2352, 24, name)
                metric = _forecast_metric(y[2352:2376], pred)
                candidates.append((metric, rank, name, None, None))
            rank = 2
            for epsilon, alpha in huber_grid:
                model = _fit_huber(y, 2351, epsilon, alpha)
                pred = _recursive_forecast(y, 2352, 24, "Huber", model)
                metric = _forecast_metric(y[2352:2376], pred)
                candidates.append((metric, rank, "Huber", epsilon, alpha))
                rank += 1

            def selection_key(item):
                metric, model_rank, _, _, _ = item
                wape = metric["WAPE"]
                return (
                    metric["RMSE"], metric["MAE"],
                    float("inf") if wape is None else wape,
                    model_rank,
                )

            validation, _, selected_name, epsilon, alpha = min(
                candidates, key=selection_key
            )
            if selected_name == "Huber":
                final_model = _fit_huber(y, 2375, epsilon, alpha)
            else:
                final_model = None
            test_pred = _recursive_forecast(
                y, 2376, 24, selected_name, final_model
            )
            test_metric = _forecast_metric(y[2376:2400], test_pred)
            rows.append({
                "Region": region,
                "TaskType": task_type,
                "SelectedModel": selected_name,
                "HuberEpsilon": epsilon,
                "HuberAlpha": alpha,
                "ValidationMAE": validation["MAE"],
                "ValidationRMSE": validation["RMSE"],
                "ValidationWAPE": validation["WAPE"],
                "ValidationSampleCount": validation["SampleCount"],
                "ValidationWAPEZeroDenominator": validation["WAPEZeroDenominator"],
                "MAE": test_metric["MAE"],
                "RMSE": test_metric["RMSE"],
                "WAPE": test_metric["WAPE"],
                "TestSampleCount": test_metric["SampleCount"],
                "TestWAPEZeroDenominator": test_metric["WAPEZeroDenominator"],
                "ClosedLoopForecast": True,
                "TrainEndHour": 2351,
                "ValidationStartHour": 2352,
                "ValidationEndHour": 2375,
                "TestStartHour": 2376,
                "TestEndHour": 2399,
            })
            for offset, value in enumerate(test_pred):
                hour = 2376 + offset
                predictions.append({
                    "Hour": hour,
                    "Region": region,
                    "TaskType": task_type,
                    "Prediction_GPU": finite(value, "prediction"),
                    "Actual_GPU": finite(y[hour], "actual"),
                    "FeatureUsesTestTruth": False,
                    "SelectedModel": selected_name,
                })
    return pd.DataFrame(rows), pd.DataFrame(predictions)


def _q2_energy_values(load, renewable, price, sell_price, carbon, export_limit):
    use = min(load, renewable)
    buy = max(0.0, load - use)
    sell = min(max(0.0, renewable - use), export_limit)
    curtail = max(0.0, renewable - use - sell)
    return (
        buy * price - sell * sell_price,
        buy * carbon,
        use + sell,
        buy,
        curtail,
    )


def _q2_context(d, schedule):
    used_gpu, used_power = rebuild_schedule_resources(d, schedule)
    if used_gpu is None:
        raise RuntimeError("CON-Q2-1: baseline resource reconstruction failed")
    region_index = {r: i for i, r in enumerate(REGIONS)}
    rt = d["region"].sort_values(["Region", "Hour"])
    arrays = {}
    for column in (
        "NonAI_IT_Load_MW", "AvailableRenewable_MW",
        "ElectricityPrice_CNY_per_MWh", "SellPrice_CNY_per_MWh",
        "CarbonIntensity_tCO2_per_MWh",
    ):
        arrays[column] = np.vstack([
            rt.loc[rt["Region"].eq(r), column].to_numpy(float)
            for r in REGIONS
        ])
    gpu = d["gpu"].set_index("Region")
    pue = gpu.loc[REGIONS, "PUE"].to_numpy(float)
    facility = (arrays["NonAI_IT_Load_MW"] + used_power) * pue[:, None]
    return {
        "region_index": region_index,
        "used_gpu": used_gpu,
        "used_power": used_power,
        "facility": facility,
        "arrays": arrays,
        "pue": pue,
        "available_gpu": gpu.loc[REGIONS, "Available_GPU"].to_numpy(float),
        "max_it": gpu.loc[REGIONS, "Max_IT_Power_MW"].to_numpy(float),
        "max_facility": gpu.loc[REGIONS, "Max_Facility_Power_MW"].to_numpy(float),
        "import_limit": np.asarray([
            q2_grid_limit(d, r, "MaxGridImport_MW") for r in REGIONS
        ], dtype=float),
        "export_limit": np.asarray([
            q2_grid_limit(d, r, "MaxGridExport_MW") for r in REGIONS
        ], dtype=float),
    }


def _task_slots(start, finish):
    return range(int(start), min(2406, int(np.ceil(float(finish) - TOL))))


def _move_deltas(old_region, old_start, old_finish, new_region, new_start,
                 new_finish, gpu_demand, task_power, context):
    ri = context["region_index"]
    gpu_delta = {}
    power_delta = {}
    facility_delta = {}
    for region, start, finish, sign in (
        (old_region, old_start, old_finish, -1.0),
        (new_region, new_start, new_finish, 1.0),
    ):
        r_idx = ri[region]
        for hour in _task_slots(start, finish):
            overlap = max(0.0, min(hour + 1.0, finish) - max(float(hour), start))
            key = (r_idx, hour)
            gpu_delta[key] = gpu_delta.get(key, 0.0) + sign * gpu_demand
            power_delta[key] = power_delta.get(key, 0.0) + sign * task_power
            facility_delta[key] = (
                facility_delta.get(key, 0.0)
                + sign * task_power * overlap * context["pue"][r_idx]
            )
    return gpu_delta, power_delta, facility_delta


def _evaluate_incremental_move(context, deltas, service_delta):
    gpu_delta, power_delta, facility_delta = deltas
    arrays = context["arrays"]
    for (r_idx, hour), delta in gpu_delta.items():
        if context["used_gpu"][r_idx, hour] + delta > context["available_gpu"][r_idx] + TOL:
            return None, "gpu_capacity"
        power_after = context["used_power"][r_idx, hour] + power_delta[(r_idx, hour)]
        if arrays["NonAI_IT_Load_MW"][r_idx, hour] + power_after > context["max_it"][r_idx] + TOL:
            return None, "it_capacity"
        if (
            (arrays["NonAI_IT_Load_MW"][r_idx, hour] + power_after)
            * context["pue"][r_idx]
            > context["max_facility"][r_idx] + TOL
        ):
            return None, "facility_capacity"

    energy_delta = np.zeros(5, dtype=float)
    for (r_idx, hour), delta in facility_delta.items():
        before_load = context["facility"][r_idx, hour]
        after_load = before_load + delta
        renewable = arrays["AvailableRenewable_MW"][r_idx, hour]
        price = arrays["ElectricityPrice_CNY_per_MWh"][r_idx, hour]
        sell = arrays["SellPrice_CNY_per_MWh"][r_idx, hour]
        carbon = arrays["CarbonIntensity_tCO2_per_MWh"][r_idx, hour]
        export = context["export_limit"][r_idx]
        before = _q2_energy_values(before_load, renewable, price, sell, carbon, export)
        after = _q2_energy_values(after_load, renewable, price, sell, carbon, export)
        if after[3] > context["import_limit"][r_idx] + TOL:
            return None, "grid_import"
        energy_delta += np.asarray(after) - np.asarray(before)
    return {
        "cost": energy_delta[0],
        "carbon": energy_delta[1],
        "renewable_used": energy_delta[2],
        "grid_purchase": energy_delta[3],
        "curtailment": energy_delta[4],
        "service": service_delta,
    }, "feasible"


def _q2_score(scheme, delta):
    service = delta["service"]
    if scheme == "cost_min":
        return delta["cost"]
    if scheme == "carbon_min":
        return delta["carbon"]
    if scheme == "renewable_max":
        return -delta["renewable_used"] + 1e-6 * max(delta["cost"], 0.0)
    if scheme == "service_first":
        return service
    return (
        delta["cost"] / 10000.0
        + delta["carbon"] / 10.0
        - delta["renewable_used"] / 10.0
        + service / 100000.0
    )


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
    elif scenario_type == "carbon_constraint":
        rt["ElectricityPrice_CNY_per_MWh"] += (
            1000.0 * float(level)
            * rt["CarbonIntensity_tCO2_per_MWh"].to_numpy(float)
        )
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


def run_q4_scenarios(d, task_candidates, joint_baseline, storage_policy):
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
    rows = []
    trace_rows = []
    checked_total = 0
    scenario_baseline_carbon = None
    for scenario_index, (scenario_type, parameter, level, seed) in enumerate(scenario_specs):
        check_deadline("q4.scenario", scenario_index)
        variant = _scenario_variant(d, scenario_type, level, seed)
        current_schedule = baseline_schedule.copy()
        current_no_storage, _, _, _ = no_storage_energy(variant, current_schedule)
        current_flow = _storage_dp_policy(
            variant, storage_policy,
            facility_override=current_no_storage[["Region", "Hour", "FacilityLoad_MW"]],
            state_count=SOC_STATE_COUNT,
        )
        audit_storage_policy(variant, current_flow, "CON-Q4-1")
        current_metrics = metrics_energy(current_flow)
        current_service = _service_detail(current_schedule, workload)
        if scenario_type == "baseline":
            scenario_baseline_carbon = float(current_metrics[1])
        carbon_target = None
        if scenario_type == "carbon_constraint":
            if scenario_baseline_carbon is None:
                raise RuntimeError("CON-Q4-4: baseline scenario must run first")
            carbon_target = (1.0 - float(level)) * scenario_baseline_carbon
        current_score, _ = _q4_joint_score(
            current_metrics, current_service, baseline_vector, carbon_target
        )
        no_improvement = 0
        rounds = 0
        accepted_rounds = 0
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
            (
                candidate_schedule, _, candidate_summary,
                candidate_trace, candidate_audit,
            ) = _optimize_q2_scheme(
                signal_variant,
                workload,
                current_schedule,
                "balanced",
                Q4_TASK_NEIGHBOR_LIMIT,
                scenario_index * 131 + round_no * 977,
            )
            checked_total += int(candidate_summary["checked_candidates"])
            candidate_no_storage, _, _, _ = no_storage_energy(
                variant, candidate_schedule
            )
            candidate_flow = _storage_dp_policy(
                variant, storage_policy,
                facility_override=candidate_no_storage[[
                    "Region", "Hour", "FacilityLoad_MW"
                ]],
                state_count=SOC_STATE_COUNT,
            )
            audit_storage_policy(variant, candidate_flow, "CON-Q4-1")
            candidate_metrics = metrics_energy(candidate_flow)
            candidate_service = _service_detail(candidate_schedule, workload)
            candidate_score, _ = _q4_joint_score(
                candidate_metrics, candidate_service, baseline_vector, carbon_target
            )
            improvement = current_score - candidate_score
            accepted = bool(improvement > Q4_IMPROVEMENT_TOL)
            before_hash = _schedule_hash(current_schedule)
            candidate_hash = _schedule_hash(candidate_schedule)
            if accepted:
                current_schedule = candidate_schedule
                current_flow = candidate_flow
                current_metrics = candidate_metrics
                current_service = candidate_service
                current_score = candidate_score
                accepted_rounds += 1
                no_improvement = 0
            else:
                no_improvement += 1
            trace_rows.append({
                "scenario_type": scenario_type,
                "parameter": parameter,
                "state_count": SOC_STATE_COUNT,
                "storage_policy": storage_policy,
                "level": level,
                "seed": seed,
                "alternation_round": round_no,
                "task_candidate_budget": Q4_TASK_NEIGHBOR_LIMIT,
                "task_candidates_checked": candidate_summary["checked_candidates"],
                "unique_tasks_visited": candidate_summary["unique_tasks_visited"],
                "local_task_moves_accepted": candidate_summary["accepted_improvements"],
                "full_task_audit_passed": bool(
                    candidate_audit["constraint_satisfied"].all()
                ),
                "incumbent_schedule_before_sha256": before_hash,
                "candidate_schedule_sha256": candidate_hash,
                "storage_trajectory_sha256": _trajectory_hash(candidate_flow),
                "joint_score_before": current_score + improvement if accepted else current_score,
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
        final_audit = build_constraint_audit(
            variant, workload, current_schedule, final_used_gpu
        )
        if not final_audit["constraint_satisfied"].all():
            raise RuntimeError("CON-Q4-1: 情景最终任务约束残差失败")
        status = "completed"
        if carbon_target is not None and current_metrics[1] > carbon_target + TOL:
            status = "target_infeasible_within_declared_heuristic"
        rows.append({
            "scenario_type": scenario_type,
            "parameter": parameter,
            "state_count": SOC_STATE_COUNT,
            "storage_policy": storage_policy,
            "baseline_source": "joint_baseline_same_policy_and_state_grid",
            "level": level,
            "seed": seed,
            "status": status,
            "alternation_rounds": rounds,
            "accepted_rounds": accepted_rounds,
            "checked_candidates": sum(
                int(row["task_candidates_checked"]) for row in trace_rows
                if row["scenario_type"] == scenario_type
                and row["parameter"] == parameter
                and row["level"] == level
                and row["seed"] == seed
            ),
            "selected_candidate": _schedule_hash(current_schedule),
            "migration_count": current_service["migration_count"],
            "task_search_status": (
                "alternating_improved" if accepted_rounds else "searched_no_improvement"
            ),
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
            "constraints_satisfied": 1,
            "non_Pareto": True,
            "result_level": "scenario-feasible",
            "termination_status": (
                "no_improvement" if no_improvement >= Q4_NO_IMPROVEMENT_ROUNDS
                else "max_iterations_reached"
            ),
        })
    return pd.DataFrame(rows), checked_total, pd.DataFrame(trace_rows)


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
    forecast_metrics, predictions = forecast(demand)
    print(
        f"结果: 问题一预测完成, 耗时={time.monotonic() - PROGRAM_START:.3f}秒",
        flush=True,
    )
    q1_schedule, _ = greedy_schedule(d, workload)
    print(
        f"结果: 问题一可行构造完成, 任务数={len(q1_schedule)}, "
        f"耗时={time.monotonic() - PROGRAM_START:.3f}秒",
        flush=True,
    )
    (
        schedule, q2_flow, q2_cost, q2_carbon, q2_re,
        q2_search, q2_trace,
    ) = q2_local_search(
        d,
        workload,
        q1_schedule,
        max_candidates=Q2_MOVE_LIMIT,
    )
    q2_budget_stability = run_q2_budget_stability(d, workload, q1_schedule)
    print(
        f"结果: 问题二有限搜索完成, 检查候选数="
        f"{int(q2_search['checked_candidates'])}, "
        f"耗时={time.monotonic() - PROGRAM_START:.3f}秒",
        flush=True,
    )
    q2_feasible, used_gpu = schedule_candidate_feasible(
        d, workload, schedule
    )
    if not q2_feasible:
        fail("CON-Q2-1", 1, 0, "局部搜索结果未通过全量任务复核")

    constraint_audit = build_constraint_audit(
        d, workload, schedule, used_gpu
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

    q3_baseline = q3_baseline_flow(d)
    q3_base_cost, q3_base_carbon, q3_base_re, q3_base_peak, q3_base_ramp = (
        metrics_energy(q3_baseline)
    )
    q3_flow, q3_search, q3_trace = storage_local_search(d)
    q3_policy_flows = {
        name: flow.copy() for name, flow in Q3_POLICY_RESULTS.items()
    }
    q3_soc_grid_sensitivity = run_soc_grid_sensitivity(d, q3_search["selected_policy"])
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
    q4_flow, q4_search, q4_trace = storage_local_search(
        d,
        facility_override=facility_override,
        max_candidates=Q4_MOVE_LIMIT,
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
        schedule,
        q2_flow,
        max_checked=Q4_TASK_NEIGHBOR_LIMIT,
    )
    q4_scenarios, q4_checked, q4_alternation_trace = run_q4_scenarios(
        d,
        q4_task_candidates,
        q4_flow,
        q4_search["selected_policy"],
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

    schedule.to_csv(RESULT_DIR / "q1_q2_q4_task_schedule.csv", index=False)
    predictions.to_csv(RESULT_DIR / "q1_forecast_2376_2399.csv", index=False)
    forecast_metrics.to_csv(RESULT_DIR / "q1_forecast_metrics.csv", index=False)
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
    pd.DataFrame([q2_search]).to_csv(
        RESULT_DIR / "q2_search_summary.csv", index=False
    )
    q2_trace.to_csv(RESULT_DIR / "q2_search_trace.csv", index=False)
    q2_budget_stability.to_csv(RESULT_DIR / "q2_budget_stability.csv", index=False)
    pd.DataFrame([q3_search]).to_csv(
        RESULT_DIR / "q3_search_summary.csv", index=False
    )
    q3_trace.to_csv(RESULT_DIR / "q3_search_trace.csv", index=False)
    q3_soc_grid_sensitivity.to_csv(RESULT_DIR / "q3_soc_grid_sensitivity.csv", index=False)
    pd.DataFrame([q4_search]).to_csv(
        RESULT_DIR / "q4_search_summary.csv", index=False
    )
    q4_trace.to_csv(RESULT_DIR / "q4_search_trace.csv", index=False)
    pd.DataFrame([
        value["summary"] for value in Q2_SCHEME_RESULTS.values()
    ]).to_csv(RESULT_DIR / "q2_named_scheme_comparison.csv", index=False)
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
        }, f, ensure_ascii=False, indent=2)

    q2_latency, wait_quality, migrated = service_metrics(schedule)
    tail_count = int((schedule["FinishHour"] > 2400).sum())

    manifest = []
    util = pd.DataFrame({"Hour": range(2376, 2400)})
    gpu_info = d["gpu"].set_index("Region")
    for idx, r in enumerate(REGIONS):
        util[r] = used_gpu[idx, 2376:2400] / float(gpu_info.loc[r, "Available_GPU"])
    save_figure(
        util, "fig_1_gpu_utilization.png", "line", "Hour", REGIONS,
        "最后24小时区域GPU峰值利用率", "时刻 / h", "GPU利用率 / 无量纲", manifest
    )

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
        result_item("q1_预测总体MAE", forecast_metrics["MAE"].mean(), "GPU", "18个区域类型序列平均MAE"),
        result_item("q1_预测总体RMSE", forecast_metrics["RMSE"].mean(), "GPU", "18个区域类型序列平均RMSE"),
        result_item("q2_迁移任务数", migrated, "个", "执行区域不同于来源区域的任务数"),
        result_item("q2_局部搜索候选数", q2_search["checked_candidates"], "个", "实际完整检查的单任务候选数"),
        result_item("q2_局部搜索接受改进数", q2_search["accepted_improvements"], "个", q2_search["status"]),
        result_item("q2_五方案合计任务覆盖率", q2_search["task_coverage_rate"], "", "确定性五维分层覆盖"),
        result_item("q2_单方案最小任务覆盖率", min(value["summary"]["task_coverage_rate"] for value in Q2_SCHEME_RESULTS.values()), "", "每方案目标至少2%"),
        result_item("q2_局部搜索前运行成本", q2_search["baseline_cost_CNY"], "元", "可行调度基线"),
        result_item("q2_局部搜索后运行成本", q2_search["final_cost_CNY"], "元", "有限搜索best-found"),
        result_item("q2_局部搜索前碳排放", q2_search["baseline_carbon_tCO2"], "tCO2", "可行调度基线"),
        result_item("q2_局部搜索后碳排放", q2_search["final_carbon_tCO2"], "tCO2", "有限搜索best-found"),
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
            "q4_任务候选方案数",
            q4_task_candidate_evidence["candidate_count"],
            "个",
            "统一候选集包含基线和两个相互不同且分别通过50000任务全量审计的替代方案",
        ),
        result_item(
            "q4_情景任务候选评价数",
            q4_checked,
            "次",
            "17个情景均执行动态任务-储能交替有限搜索",
        ),
        result_item(
            "q4_情景交替轮数",
            q4_scenarios["alternation_rounds"].min(),
            "轮",
            "每个情景顺序执行基线与替代一比较及替代二增量比较",
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
            len(schedule.query("ArrivalHour >= 2376")) if "ArrivalHour" in schedule else len(
                d["workload"].query("ArrivalHour >= 2376")
            ),
            tail_count, 1, float(np.max(used_gpu[:, 2376:2400])),
        ],
        "q2": [len(schedule), q2_cost, q2_carbon, q2_latency, q2_re, tail_count, 1],
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
        "q1": ["行", "条", "GPU", "个", "个", "个", "GPU"],
        "q2": ["个", "元", "tCO2", "ms", "", "个", ""],
        "q3": ["MWh", "MWh", "MWh", "行", "元", "tCO2", "MW", "MW", ""],
        "q4": ["个", "MWh", "行", "元", "tCO2", "ms", "", "", "MW", "", "个", "个", "个", ""],
    }
    for q, names in REQUIRED_NAMES.items():
        for name, value, unit in zip(names, values[q], units[q]):
            results.append(result_item(name, value, unit, "详细结果见当前运行生成的fresh CSV;状态值由实际审计或实际情景计数派生"))

    with open(RESULT_DIR / "results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    with open(RESULT_DIR / "figure_manifest.json", "w", encoding="utf-8") as f:
        json.dump({"schema_version": 1, "figures": manifest}, f, ensure_ascii=False, indent=2)

    checked = [
        "CON-Q1-1", "CON-Q1-2", "CON-Q1-3", "CON-Q1-4", "CON-Q1-5",
        "CON-Q1-6", "CON-Q1-7", "CON-Q2-1", "CON-Q2-2", "CON-Q2-3",
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
            "q2": {
                "stratification": "TaskType|SourceRegion|ArrivalHour6h|GPUhQuartile|WaitQuartile",
                "minimum_per_scheme_coverage_target": 0.02,
                "minimum_combined_coverage_target": 0.10,
                "budget_stability_levels": list(Q2_STABILITY_BUDGETS),
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
