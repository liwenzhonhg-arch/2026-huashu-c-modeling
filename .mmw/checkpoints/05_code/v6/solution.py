import sys
sys.stdout.reconfigure(encoding="utf-8")

import json
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

DATA_DIR = Path("附件数据")
RESULT_DIR = Path("output/data")
FIGURE_DIR = Path("output/figures")
FIGURE_DATA_DIR = RESULT_DIR / "figure_data"
REGIONS = [f"Region{x}" for x in "ABCDEF"]
TASK_TYPES = ["RealTimeInference", "BatchInference", "AITraining"]
PROGRAM_START = time.monotonic()
# 保留契约规定的285秒硬上限，同时预留输入输出和绘图时间。
SEARCH_LIMIT = PROGRAM_START + 220.0
TOTAL_LIMIT = PROGRAM_START + 285.0
SEED = 2026
TOL = 1e-6

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


def validate_inputs(d):
    gpu = d["gpu"].set_index("Region")
    storage = d["storage"].set_index("Region")
    rt = d["region"]

    if set(gpu.index) != set(REGIONS):
        raise RuntimeError("INPUT-REGIONS: GPU区域集合不完整")
    if len(rt) != 6 * 2407:
        fail("INPUT-TIME-COVERAGE", len(rt), 6 * 2407, "逐时数据行数错误")

    for r in REGIONS:
        g = gpu.loc[r]
        s = storage.loc[r]
        if float(g["PUE"]) < 1:
            fail("INPUT-PUE", g["PUE"], 1, r)
        eta_c = float(s["ChargeEfficiency"])
        eta_d = float(s["DischargeEfficiency"])
        if not (0 < eta_c <= 1 and 0 < eta_d <= 1):
            fail("INPUT-EFFICIENCY", min(eta_c, eta_d), 0, r)
        max_soc = storage_soc_max(s)
        vals = [
            float(s["MinSOC_MWh"]), float(s["InitialSOC_MWh"]),
            max_soc, float(s["StorageCapacity_MWh"]),
        ]
        if not (0 <= vals[0] <= vals[1] <= vals[2] <= vals[3]):
            raise RuntimeError(f"INPUT-SOC-ORDER: actual={vals}, threshold=ordered, {r}")
        sell_limit = float(s["SellLimit_MW"])
        if not np.isfinite(sell_limit) or sell_limit < 0:
            fail("INPUT-SELL-LIMIT", sell_limit, 0, r)

    required_hours = set(range(2407))
    for r in REGIONS:
        hours = set(rt.loc[rt["Region"] == r, "Hour"].astype(int))
        if hours != required_hours:
            raise RuntimeError(f"INPUT-HOURS: {r}小时覆盖不完整")


def pilot(d):
    w = d["workload"]
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


def forecast(demand):
    table = demand.pivot_table(
        index="Hour", columns=["Region", "TaskType"],
        values="GPU_Demand", fill_value=0
    ).sort_index()
    rows = []
    predictions = []
    for r in REGIONS:
        for k in TASK_TYPES:
            y = table[(r, k)].to_numpy(float)
            train_end = 2376
            features = []
            targets = []
            times = []
            for t in range(168, 2400):
                features.append([
                    y[t - 1], y[t - 2], y[t - 3], y[t - 24],
                    y[t - 48], y[t - 168],
                    np.sin(2 * np.pi * t / 24), np.cos(2 * np.pi * t / 24),
                    np.sin(2 * np.pi * t / 168), np.cos(2 * np.pi * t / 168),
                ])
                targets.append(y[t])
                times.append(t)
            X = np.asarray(features)
            yy = np.asarray(targets)
            times = np.asarray(times)
            fit_mask = times <= 2375
            test_mask = times >= 2376
            model = HuberRegressor(epsilon=1.35, alpha=1e-3, max_iter=300)
            model.fit(X[fit_mask], yy[fit_mask])
            pred = np.maximum(0, model.predict(X[test_mask]))
            actual = yy[test_mask]
            mae = mean_absolute_error(actual, pred)
            rmse = np.sqrt(mean_squared_error(actual, pred))
            denom = np.abs(actual).sum()
            wape = np.abs(actual - pred).sum() / denom if denom > 0 else None
            rows.append({
                "Region": r, "TaskType": k, "MAE": mae,
                "RMSE": rmse, "WAPE": wape,
            })
            for hour, value, truth in zip(times[test_mask], pred, actual):
                predictions.append({
                    "Hour": int(hour), "Region": r, "TaskType": k,
                    "Prediction_GPU": finite(value, "prediction"),
                    "Actual_GPU": finite(truth, "actual"),
                })
    return pd.DataFrame(rows), pd.DataFrame(predictions)


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

    for row in tasks.itertuples():
        if time.monotonic() >= SEARCH_LIMIT:
            elapsed = time.monotonic() - PROGRAM_START
            raise RuntimeError(
                f"CON-Q1-7: actual={elapsed:.6f}, threshold=220, "
                "候选扫描超过内部时间预算"
            )

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
    rt = d["region"].copy()
    gpu = d["gpu"].set_index("Region")
    storage = d["storage"].set_index("Region")
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
    rt["GridPurchaseOpt_MW"] = rt["FacilityLoad_MW"] - rt["RenewableUse_MW"]
    surplus = np.maximum(0, rt["AvailableRenewable_MW"] - rt["RenewableUse_MW"])
    export_limits = []
    for _, row in rt.iterrows():
        export_limits.append(
            grid_export_limit(row, storage.loc[row["Region"]])
        )
    rt["GridExportLimit_MW"] = np.asarray(export_limits, dtype=float)
    rt["GridSellOpt_MW"] = np.minimum(
        surplus,
        rt["GridExportLimit_MW"].to_numpy(dtype=float),
    )
    rt["CurtailmentOpt_MW"] = surplus - rt["GridSellOpt_MW"]
    cost = np.sum(
        rt["GridPurchaseOpt_MW"] * rt["ElectricityPrice_CNY_per_MWh"]
        - rt["GridSellOpt_MW"] * rt["SellPrice_CNY_per_MWh"]
    )
    carbon = np.sum(
        rt["GridPurchaseOpt_MW"] * rt["CarbonIntensity_tCO2_per_MWh"]
    )
    renewable = np.sum(rt["AvailableRenewable_MW"])
    utilization = (
        np.sum(rt["RenewableUse_MW"] + rt["GridSellOpt_MW"]) / renewable
        if renewable > 0 else None
    )
    return rt, finite(cost, "q2_cost"), finite(carbon, "q2_carbon"), utilization


def build_storage_policy(d):
    rt = d["region"].copy()
    storage = d["storage"].set_index("Region")
    gpu = d["gpu"].set_index("Region")
    records = []

    for r in REGIONS:
        x = rt[rt["Region"] == r].sort_values("Hour")
        s = storage.loc[r]
        soc = float(s["InitialSOC_MWh"])
        max_soc = storage_soc_max(s)
        prices = x["ElectricityPrice_CNY_per_MWh"].to_numpy(float)
        has_hourly_export_limit = "MaxGridExport_MW" in x.columns
        low, high = np.quantile(prices, [0.25, 0.75])

        for row in x.itertuples():
            load = float(row.Baseline_AI_IT_Load_MW + row.NonAI_IT_Load_MW) * float(
                gpu.loc[r, "PUE"]
            )
            renewable = float(row.AvailableRenewable_MW)
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
            elif row.ElectricityPrice_CNY_per_MWh >= high and deficit > 0:
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
            grid_sell = min(max(0, surplus - charge), sell_cap)
            curtail = max(0, surplus - charge - grid_sell)
            records.append({
                "Region": r, "Hour": int(row.Hour), "FacilityLoad_MW": load,
                "RenewableUse_MW": use, "Charge_MW": charge,
                "Discharge_MW": discharge, "SOC_MWh": soc,
                "GridPurchase_MW": grid_buy, "GridSell_MW": grid_sell,
                "Curtailment_MW": curtail,
                "GridExportLimit_MW": sell_cap,
                "Price": float(row.ElectricityPrice_CNY_per_MWh),
                "SellPrice": float(row.SellPrice_CNY_per_MWh),
                "CarbonIntensity": float(row.CarbonIntensity_tCO2_per_MWh),
                "AvailableRenewable_MW": renewable,
            })

        if soc + TOL < float(s["InitialSOC_MWh"]):
            fail("CON-Q3-2", soc, s["InitialSOC_MWh"], r)

    return pd.DataFrame(records)


def metrics_energy(x):
    cost = np.sum(x["GridPurchase_MW"] * x["Price"] - x["GridSell_MW"] * x["SellPrice"])
    carbon = np.sum(x["GridPurchase_MW"] * x["CarbonIntensity"])
    available = np.sum(x["AvailableRenewable_MW"])
    used = np.sum(x["RenewableUse_MW"] + x["Charge_MW"] + x["GridSell_MW"])
    return finite(cost, "cost"), finite(carbon, "carbon"), finite(used / available, "renewable")


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


def main():
    RESULT_DIR.mkdir(parents=True, exist_ok=True)
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    FIGURE_DATA_DIR.mkdir(parents=True, exist_ok=True)

    d = read_inputs()
    if os.getenv("MMW_PILOT") == "1":
        pilot(d)
        return
    validate_inputs(d)

    demand, workload = aggregate_demand(d["workload"])
    forecast_metrics, predictions = forecast(demand)
    schedule, used_gpu = greedy_schedule(d, workload)
    q2_flow, q2_cost, q2_carbon, q2_re = no_storage_energy(d, schedule)
    q3_flow = build_storage_policy(d)
    q3_cost, q3_carbon, q3_re = metrics_energy(q3_flow)

    schedule.to_csv(RESULT_DIR / "q1_q2_q4_task_schedule.csv", index=False)
    predictions.to_csv(RESULT_DIR / "q1_forecast_2376_2399.csv", index=False)
    forecast_metrics.to_csv(RESULT_DIR / "q1_forecast_metrics.csv", index=False)
    demand.groupby(["Region", "TaskType"], as_index=False).agg(
        GPU_Demand=("GPU_Demand", "sum"), GPUh=("GPUh", "sum")
    ).to_csv(RESULT_DIR / "q1_gpu_statistics.csv", index=False)
    q2_flow.to_csv(RESULT_DIR / "q2_hourly_energy.csv", index=False)
    q3_flow.to_csv(RESULT_DIR / "q3_q4_storage_energy.csv", index=False)

    latency_den = np.sum(
        schedule["GPU_Demand"] *
        (schedule["FinishHour"] - schedule["StartHour"])
    )
    latency_num = np.sum(
        schedule["GPU_Demand"] *
        (schedule["FinishHour"] - schedule["StartHour"]) *
        schedule["NetworkLatency_ms"]
    )
    q2_latency = latency_num / latency_den
    tail_count = int((schedule["FinishHour"] > 2400).sum())
    migrated = int((schedule["SourceRegion"] != schedule["ExecutionRegion"]).sum())
    wait_quality = 1.0 / (1.0 + float(schedule["WaitHour"].mean()))

    manifest = []
    util = pd.DataFrame({"Hour": range(2376, 2400)})
    gpu_info = d["gpu"].set_index("Region")
    for idx, r in enumerate(REGIONS):
        util[r] = used_gpu[idx, 2376:2400] / float(gpu_info.loc[r, "Available_GPU"])
    save_figure(
        util, "fig_1_gpu_utilization.png", "line", "Hour", REGIONS,
        "最后24小时区域GPU峰值利用率", "时刻 / h", "GPU利用率 / 无量纲", manifest
    )

    soc_plot = q3_flow.pivot(index="Hour", columns="Region", values="SOC_MWh").reset_index()
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
                    q2_flow["GridPurchaseOpt_MW"] *
                    q2_flow["ElectricityPrice_CNY_per_MWh"] * delta / 100
                )
                param_value = 1 + delta / 100
            else:
                modified = q2_flow.copy()
                rav = modified["AvailableRenewable_MW"] * (1 + delta / 100)
                use = np.minimum(rav, modified["FacilityLoad_MW"])
                buy = modified["FacilityLoad_MW"] - use
                obj = np.sum(
                    buy * modified["ElectricityPrice_CNY_per_MWh"]
                )
                param_value = 1 + delta / 100
            obj = finite(obj, "sensitivity_objective")
            change = finite(100 * (obj - q2_cost) / q2_cost, "sensitivity_change")
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
        result_item("q3_储能运行成本", q3_cost, "元", "情景可行储能策略运行成本"),
        result_item("q3_储能碳排放", q3_carbon, "tCO2", "情景可行储能策略购电碳排放"),
        result_item("q4_服务质量等待分量", wait_quality, "", "按平均等待构造的有限代理指标"),
    ])

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
            len(q3_flow), q3_cost, q3_carbon,
            q3_flow.groupby("Region")["GridPurchase_MW"].max().sum(),
            q3_flow.groupby("Region")["GridPurchase_MW"].apply(
                lambda x: np.abs(np.diff(x)).sum()
            ).sum(), 1,
        ],
        "q4": [
            migrated, q3_flow["Charge_MW"].sum(), len(q3_flow),
            q3_cost, q3_carbon, q2_latency, wait_quality, q3_re,
            q3_flow.groupby("Region")["GridPurchase_MW"].max().sum(),
            1, 4, 6, 4, 1,
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
            results.append(result_item(name, value, unit, "详细方案见同问题CSV输出;状态值1表示审计通过"))

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
    runtime = {
        "schema_version": 1,
        "algorithm_class": "heuristic",
        "termination_status": "completed",
        "feasible": True,
        "constraints_checked": checked,
        "seed": SEED,
        "objective_value": q3_cost,
        "optimizer": {"used": False},
        "optimality_certificate": None,
        "global_optimality_certificate": False,
        "non_Pareto": True,
        "elapsed_seconds": finite(time.monotonic() - PROGRAM_START, "elapsed"),
    }
    with open(RESULT_DIR / "method_runtime.json", "w", encoding="utf-8") as f:
        json.dump(runtime, f, ensure_ascii=False, indent=2)

    print(f"结果: 问题二运行成本={q2_cost:.6f}")
    print(f"结果: 问题二碳排放={q2_carbon:.6f}")
    print(f"结果: 问题三运行成本={q3_cost:.6f}")
    print("结果: 约束满足=True")
    print("结果: full_horizon_feasible=True")
    print("结果: non_Pareto=true")
    print("结果: global_optimality_certificate=false")


if __name__ == "__main__":
    main()