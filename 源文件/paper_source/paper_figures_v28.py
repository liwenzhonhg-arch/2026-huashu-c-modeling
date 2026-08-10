from __future__ import annotations

import hashlib
import json
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.collections import LineCollection
from matplotlib.lines import Line2D

HERE = Path(__file__).resolve()
PAPER_DIR = HERE.parent
CHECKPOINTS_DIR = HERE.parents[2]
PROJECT_DIR = HERE.parents[4]
SOLVE_DIR = CHECKPOINTS_DIR / "06_solve" / "v19"
FIGURE_DIR = PAPER_DIR / "figures" / "paper_v28"
HASH_MANIFEST = PAPER_DIR / "paper_input_hashes.json"
FIGURE_DIR.mkdir(parents=True, exist_ok=True)

PALETTE = {
    "blue": "#2F5D8C",
    "orange": "#D07A32",
    "green": "#3C8D6B",
    "red": "#B54C4C",
    "purple": "#7768AE",
    "cyan": "#4C91A6",
    "gray": "#777777",
    "light": "#E9EEF3",
}
REGION_COLORS = [PALETTE[k] for k in ("blue", "orange", "green", "red", "purple", "cyan")]

mpl.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Microsoft YaHei", "SimHei", "Noto Sans CJK SC", "DejaVu Sans"],
    "axes.unicode_minus": False,
    "font.size": 9,
    "axes.titlesize": 10,
    "axes.labelsize": 9,
    "xtick.labelsize": 8,
    "ytick.labelsize": 8,
    "legend.fontsize": 8,
    "axes.linewidth": 0.8,
    "lines.linewidth": 1.5,
    "savefig.dpi": 300,
    "figure.dpi": 120,
})


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def validate_inputs() -> None:
    manifest = json.loads(HASH_MANIFEST.read_text(encoding="utf-8"))
    failures = []
    for item in manifest["inputs"]:
        if item.get("source_stage") != "solve":
            continue
        rel = item["path"]
        path = SOLVE_DIR / rel
        if not path.is_file():
            failures.append(f"missing: {path}")
            continue
        actual = sha256(path)
        if actual != item["sha256"]:
            failures.append(f"hash mismatch: {path}: {actual} != {item['sha256']}")
    if failures:
        raise RuntimeError("Frozen input validation failed:\n" + "\n".join(failures))


def panel_label(ax: plt.Axes, label: str) -> None:
    ax.text(-0.085, 1.035, label, transform=ax.transAxes, fontsize=10, fontweight="bold", va="bottom")


def finish(fig: plt.Figure, filename: str) -> None:
    fig.savefig(FIGURE_DIR / filename, dpi=300, bbox_inches="tight", pad_inches=0.08, facecolor="white")
    plt.close(fig)


def oriented_minmax(values: np.ndarray, higher_is_better: bool) -> np.ndarray:
    values = np.asarray(values, dtype=float)
    lo, hi = np.nanmin(values), np.nanmax(values)
    if np.isclose(hi, lo):
        return np.ones_like(values)
    score = (values - lo) / (hi - lo)
    return score if higher_is_better else 1.0 - score


def add_heatmap(ax: plt.Axes, matrix: np.ndarray, rows: list[str], cols: list[str], fmt: str = ".2f") -> None:
    im = ax.imshow(matrix, vmin=0, vmax=1, cmap=mpl.colors.LinearSegmentedColormap.from_list(
        "paper_seq", ["#F3F5F7", "#AFC8D9", PALETTE["blue"]]
    ), aspect="auto")
    ax.set_xticks(np.arange(len(cols)), labels=cols)
    ax.set_yticks(np.arange(len(rows)), labels=rows)
    ax.tick_params(top=True, bottom=False, labeltop=True, labelbottom=False, length=0)
    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            color = "white" if matrix[i, j] > 0.62 else "#222222"
            ax.text(j, i, format(matrix[i, j], fmt), ha="center", va="center", fontsize=7.5, color=color)
    for spine in ax.spines.values():
        spine.set_visible(False)
    return im


def figure_q1_forecast() -> None:
    forecast = pd.read_csv(SOLVE_DIR / "q1_forecast_2376_2399.csv")
    roll_summary = pd.read_csv(SOLVE_DIR / "q1_rolling_window_metrics.csv")
    system = forecast.groupby("Hour", as_index=False)[["Prediction_GPU", "Actual_GPU"]].sum()

    fig, axes = plt.subplots(2, 1, figsize=(7.2, 6.0), constrained_layout=True)
    ax = axes[0]
    ax.plot(system["Hour"], system["Actual_GPU"], color=PALETTE["blue"], marker="o", markersize=3, label="实际值")
    ax.plot(system["Hour"], system["Prediction_GPU"], color=PALETTE["orange"], marker="s", markersize=2.7, label="预测值")
    ax.set(title="最后 24 小时系统汇总 GPU 需求", xlabel="小时", ylabel="GPU 需求")
    ax.grid(alpha=0.22); ax.legend(ncol=2, frameon=False, loc="upper left"); panel_label(ax, "(a)")

    ax = axes[1]; x = np.arange(len(roll_summary))
    ax.plot(x, roll_summary["Macro_WAPE"], marker="o", color=PALETTE["red"], label="Macro-WAPE")
    ax.plot(x, roll_summary["Micro_WAPE"], marker="s", color=PALETTE["green"], label="Micro-WAPE")
    ax.plot(x, roll_summary["System_Aggregate_WAPE"], marker="^", color=PALETTE["purple"], label="系统聚合 WAPE")
    ax.set_xticks(x, [str(int(v)) for v in roll_summary["RollingOrigin"]], rotation=25)
    ax.set(title="无泄漏 rolling-origin 三口径逐窗检验", xlabel="验证窗口起点", ylabel="WAPE")
    ax.grid(alpha=0.22); ax.legend(ncol=3, frameon=False, loc="upper center")
    ax.text(0.99, 0.04, "最终测试不参与选模；不使用逐窗胜者", transform=ax.transAxes, ha="right", va="bottom", color=PALETTE["gray"], fontsize=8)
    panel_label(ax, "(b)"); finish(fig, "fig01_q1_forecast.png")


def figure_q1_schedule() -> None:
    gantt = pd.read_csv(SOLVE_DIR / "q1_gantt.csv")
    util = pd.read_csv(SOLVE_DIR / "q1_gpu_utilization.csv")
    region_order = [f"Region{c}" for c in "ABCDEF"]
    type_order = ["RealTimeInference", "BatchInference", "AITraining"]
    type_labels = {"RealTimeInference": "实时推理", "BatchInference": "批量推理", "AITraining": "AI 训练"}
    type_colors = {"RealTimeInference": PALETTE["blue"], "BatchInference": PALETTE["orange"], "AITraining": PALETTE["green"]}
    gantt["ExecutionRegion"] = pd.Categorical(gantt["ExecutionRegion"], region_order, ordered=True)
    gantt = gantt.sort_values(["ExecutionRegion", "StartHour", "FinishHour", "TaskID"]).reset_index(drop=True)

    fig, axes = plt.subplots(2, 1, figsize=(7.2, 6.2), constrained_layout=True)
    ax = axes[0]
    segments_by_type = {k: [] for k in type_order}
    for idx, row in gantt.iterrows():
        segments_by_type[row["TaskType"]].append([(row["StartHour"], idx), (row["FinishHour"], idx)])
    for task_type in type_order:
        ax.add_collection(LineCollection(segments_by_type[task_type], colors=type_colors[task_type], linewidths=0.9, alpha=0.9))
    centers, boundaries, start = [], [], 0
    for region in region_order:
        count = int((gantt["ExecutionRegion"] == region).sum())
        centers.append(start + max(count - 1, 0) / 2)
        start += count
        boundaries.append(start - 0.5)
    for boundary in boundaries[:-1]:
        ax.axhline(boundary, color="#D8D8D8", linewidth=0.6)
    ax.set_xlim(gantt["StartHour"].min() - 0.5, gantt["FinishHour"].max() + 0.5)
    ax.set_ylim(-1, len(gantt))
    ax.set_yticks(centers, [x.replace("Region", "区域 ") for x in region_order])
    ax.set(title="538 个末端实际任务甘特图（Q1 独立基础调度）", xlabel="小时", ylabel="执行区域")
    handles = [Line2D([0], [0], color=type_colors[k], lw=2, label=type_labels[k]) for k in type_order]
    ax.legend(handles=handles, ncol=3, frameon=False, loc="upper right")
    ax.grid(axis="x", alpha=0.2)
    panel_label(ax, "(a)")

    ax = axes[1]
    for color, region in zip(REGION_COLORS, region_order):
        ax.plot(util["Hour"], 100 * util[region], marker="o", markersize=2.4, color=color, label=region.replace("Region", "区域 "))
    ax.axhline(100, color=PALETTE["red"], linestyle="--", linewidth=0.9, label="容量上限")
    ax.set(title="六区域 GPU 利用率", xlabel="小时", ylabel="利用率/%", ylim=(0, 105))
    ax.grid(alpha=0.22)
    ax.legend(ncol=4, frameon=False, loc="upper center")
    panel_label(ax, "(b)")
    finish(fig, "fig02_q1_schedule.png")


def figure_q2_multiobjective() -> None:
    schemes = pd.read_csv(SOLVE_DIR / "q2_named_scheme_comparison.csv")
    stability = pd.read_csv(SOLVE_DIR / "q2_budget_stability.csv")
    order = ["cost_min", "carbon_direct", "renewable_max", "service_first", "balanced"]
    labels = {"cost_min": "成本优先", "carbon_direct": "碳优先", "renewable_max": "新能源优先", "service_first": "服务优先", "balanced": "平衡"}
    schemes = schemes.set_index("scheme").loc[order].reset_index()
    matrix = np.column_stack([
        oriented_minmax(schemes["cost_CNY"].to_numpy(), False),
        oriented_minmax(schemes["carbon_tCO2"].to_numpy(), False),
        oriented_minmax(schemes["renewable_utilization"].to_numpy(), True),
        oriented_minmax(schemes["network_latency_ms"].to_numpy(), False),
        oriented_minmax(schemes["service_quality"].to_numpy(), True),
    ])

    fig, axes = plt.subplots(2, 1, figsize=(7.2, 6.2), constrained_layout=True)
    ax = axes[0]
    add_heatmap(ax, matrix, [labels[x] for x in order], ["成本", "碳排放", "新能源率", "网络时延", "服务质量"])
    ax.set_title("五种方案的同向 min-max 展示分数（1 为该指标较优）", pad=24)
    panel_label(ax, "(a)")

    ax = axes[1]
    b = stability[stability["scheme"] == "balanced"].sort_values("PassID")
    x = b["attempted_candidates"] / 10000
    line1 = ax.plot(x, 100 * b["relative_improvement"], marker="o", color=PALETTE["blue"], label="本轮目标相对改进")[0]
    ax.set(title="formal balanced 搜索收敛关系", xlabel="累计候选数/万", ylabel="目标相对改进/%")
    ax.grid(alpha=0.22)
    ax2 = ax.twinx()
    line2 = ax2.plot(x, b["accepted"], marker="s", color=PALETTE["orange"], label="本轮接受改进数")[0]
    ax2.set_ylabel("接受改进数")
    ax.legend([line1, line2], [line1.get_label(), line2.get_label()], frameon=False, loc="upper right")
    panel_label(ax, "(b)")
    finish(fig, "fig03_q2_multiobjective.png")


def _system_variation(df: pd.DataFrame) -> float:
    total = 0.0
    for _, g in df.sort_values(["Region", "Hour"]).groupby("Region"):
        total += np.abs(np.diff(g["NetGrid_MW"].to_numpy(dtype=float))).sum()
    return float(total)


def figure_q3_storage() -> None:
    before = pd.read_csv(SOLVE_DIR / "q3_no_storage_baseline.csv")
    after = pd.read_csv(SOLVE_DIR / "q3_storage_energy.csv")
    audit = pd.read_csv(SOLVE_DIR / "q3_metric_recomputation_audit.csv")
    summary = pd.read_csv(SOLVE_DIR / "q3_search_summary.csv").iloc[0]
    regions = [f"Region{c}" for c in "ABCDEF"]

    before_hour = before.groupby("Hour", as_index=False)["NetGrid_MW"].sum()
    after_hour = after.groupby("Hour", as_index=False)["NetGrid_MW"].sum()
    peak_before = before.groupby("Region")["NetGrid_MW"].apply(lambda s: max(float(s.max()), 0.0)).reindex(regions)
    peak_after = after.groupby("Region")["NetGrid_MW"].apply(lambda s: max(float(s.max()), 0.0)).reindex(regions)
    variation_before, variation_after = _system_variation(before), _system_variation(after)
    curt_before = float(before["RenewableCurtailment_MW"].sum())
    curt_after = float(after["RenewableCurtailment_MW"].sum())
    improvements = [
        100 * (peak_before.sum() - peak_after.sum()) / peak_before.sum(),
        100 * (variation_before - variation_after) / variation_before,
        100 * (curt_before - curt_after) / curt_before,
    ]

    # Cross-check plotted recomputations against formal audit rows.
    selected = audit[audit["policy"] == summary["selected_policy"]].iloc[0]
    if not np.isclose(variation_after, selected["net_grid_ramp_MW"], rtol=0, atol=1e-6):
        raise RuntimeError("Q3 variation recomputation does not match formal audit")

    fig, axes = plt.subplots(2, 2, figsize=(7.2, 6.4), constrained_layout=True)
    ax = axes[0, 0]
    ax.plot(before_hour["Hour"], before_hour["NetGrid_MW"], color=PALETTE["gray"], alpha=0.75, label="无储能")
    ax.plot(after_hour["Hour"], after_hour["NetGrid_MW"], color=PALETTE["blue"], alpha=0.85, label="平衡储能")
    ax.axhline(0, color="#999999", linewidth=0.7)
    ax.set(title="系统净电网功率曲线", xlabel="小时", ylabel="净购电功率/MW")
    ax.legend(frameon=False)
    ax.grid(alpha=0.18)
    panel_label(ax, "(a)")

    ax = axes[0, 1]
    for color, region in zip(REGION_COLORS, regions):
        g = after[after["Region"] == region]
        ax.plot(g["Hour"], g["SOC_MWh"], color=color, label=region.replace("Region", "区域 "))
    ax.set(title="六区域 SOC 轨迹", xlabel="小时", ylabel="SOC/MWh")
    ax.legend(ncol=2, frameon=False)
    ax.grid(alpha=0.18)
    panel_label(ax, "(b)")

    ax = axes[1, 0]
    x = np.arange(len(regions)); width = 0.38
    ax.bar(x - width / 2, peak_before, width, color="#A9A9A9", label="无储能")
    ax.bar(x + width / 2, peak_after, width, color=PALETTE["blue"], label="平衡储能")
    ax.set_xticks(x, [r.replace("Region", "区域 ") for r in regions])
    ax.set(title="各区域非负峰值净购电对比", ylabel="峰值/MW")
    ax.legend(frameon=False)
    ax.grid(axis="y", alpha=0.18)
    panel_label(ax, "(c)")

    ax = axes[1, 1]
    names = ["峰值净购电", "净电网波动", "弃电量"]
    bars = ax.bar(names, improvements, color=[PALETTE["blue"], PALETTE["green"], PALETTE["orange"]])
    ax.axhline(0, color="#888888", linewidth=0.7)
    ax.set(title="储能优化后的归一化改善", ylabel="相对基准改善/%")
    ax.grid(axis="y", alpha=0.18)
    for bar, val in zip(bars, improvements):
        ax.text(bar.get_x() + bar.get_width() / 2, val + (1 if val >= 0 else -1), f"{val:.1f}%", ha="center", va="bottom" if val >= 0 else "top", fontsize=8)
    panel_label(ax, "(d)")
    finish(fig, "fig04_q3_storage.png")


def _mark_status(ax: plt.Axes, x: np.ndarray, y: np.ndarray, status: np.ndarray, mechanism: np.ndarray | None = None) -> None:
    failed = status != "completed"
    inactive = np.zeros_like(failed, dtype=bool) if mechanism is None else ~mechanism
    if np.any(inactive & ~failed):
        ax.scatter(x[inactive & ~failed], y[inactive & ~failed], s=52, facecolors="white", edgecolors=PALETTE["gray"], linewidth=1.1, zorder=5)
    if np.any(failed):
        ax.scatter(x[failed], y[failed], s=58, marker="x", color=PALETTE["gray"], linewidth=1.5, zorder=6)


def figure_q4_scenarios() -> None:
    q4 = pd.read_csv(SOLVE_DIR / "q4_scenario_comparison.csv")
    joint = pd.read_csv(SOLVE_DIR / "q4_joint_storage_energy.csv")
    baseline = q4[q4["scenario_type"] == "baseline"].iloc[0]
    joint_renewable = float((joint["RenewableDirectUse_MW"].sum() + joint["RenewableCharge_MW"].sum() + joint["RenewableSell_MW"].sum()) / joint["AvailableRenewable_MW"].sum())
    joint_carbon = float((joint["GridPurchase_MW"] * joint["CarbonIntensity"]).sum())
    if not np.isclose(joint_renewable, baseline["renewable_utilization"], atol=1e-10):
        raise RuntimeError("Q4 joint energy renewable utilization does not match baseline")
    if not np.isclose(joint_carbon, baseline["carbon_tCO2"], atol=1e-8):
        raise RuntimeError("Q4 joint energy carbon does not match baseline")

    fig, axes = plt.subplots(2, 2, figsize=(7.2, 6.5), constrained_layout=True)

    c = q4[q4["scenario_type"] == "carbon_constraint"].sort_values("level")
    x = 100 * c["level"].to_numpy(dtype=float)
    status = c["status"].to_numpy()
    mechanism = c["mechanism_active"].astype(str).str.lower().eq("true").to_numpy()
    ax = axes[0, 0]
    l1 = ax.plot(x, c["cost_CNY"] / 1e8, color=PALETTE["blue"], marker="o", label="成本")[0]
    _mark_status(ax, x, (c["cost_CNY"] / 1e8).to_numpy(), status, mechanism)
    ax.set(title="碳约束强度响应", xlabel="碳削减目标/%", ylabel="成本/亿元")
    ax.grid(alpha=0.18)
    ax2 = ax.twinx()
    l2 = ax2.plot(x, c["carbon_tCO2"], color=PALETTE["orange"], marker="s", label="实际碳排放")[0]
    ax2.plot(x, c["carbon_target_tCO2"], color=PALETTE["gray"], linestyle="--", linewidth=1, label="碳目标")
    _mark_status(ax2, x, c["carbon_tCO2"].to_numpy(), status, mechanism)
    ax2.set_ylabel("碳排放/tCO$_2$")
    ax.legend([l1, l2], [l1.get_label(), l2.get_label()], frameon=False, loc="best")
    panel_label(ax, "(a)")

    p = q4[q4["scenario_type"] == "price_spread"].sort_values("level")
    x = p["level"].to_numpy(dtype=float)
    status = p["status"].to_numpy(); mechanism = p["mechanism_active"].astype(str).str.lower().eq("true").to_numpy()
    ax = axes[0, 1]
    l1 = ax.plot(x, p["cost_CNY"] / 1e8, color=PALETTE["blue"], marker="o", label="成本")[0]
    _mark_status(ax, x, (p["cost_CNY"] / 1e8).to_numpy(), status, mechanism)
    ax.set(title="峰谷电价响应", xlabel="峰谷价差系数", ylabel="成本/亿元")
    ax.grid(alpha=0.18)
    ax2 = ax.twinx()
    l2 = ax2.plot(x, p["net_grid_ramp_MW"], color=PALETTE["green"], marker="s", label="净电网波动")[0]
    _mark_status(ax2, x, p["net_grid_ramp_MW"].to_numpy(), status, mechanism)
    ax2.set_ylabel("净电网波动/MW")
    ax.legend([l1, l2], [l1.get_label(), l2.get_label()], frameon=False, loc="best")
    panel_label(ax, "(b)")

    r = q4[q4["scenario_type"] == "renewable_level"].sort_values("level")
    x = r["level"].to_numpy(dtype=float)
    status = r["status"].to_numpy(); mechanism = r["mechanism_active"].astype(str).str.lower().eq("true").to_numpy()
    ax = axes[1, 0]
    l1 = ax.plot(x, 100 * r["renewable_utilization"], color=PALETTE["green"], marker="o", label="新能源利用率")[0]
    _mark_status(ax, x, (100 * r["renewable_utilization"]).to_numpy(), status, mechanism)
    ax.set(title="新能源水平响应", xlabel="新能源水平系数", ylabel="新能源利用率/%")
    ax.grid(alpha=0.18)
    ax2 = ax.twinx()
    l2 = ax2.plot(x, r["grid_purchase_MWh"], color=PALETTE["orange"], marker="s", label="购电量")[0]
    _mark_status(ax2, x, r["grid_purchase_MWh"].to_numpy(), status, mechanism)
    ax2.set_ylabel("购电量/MWh")
    ax.legend([l1, l2], [l1.get_label(), l2.get_label()], frameon=False, loc="best")
    panel_label(ax, "(c)")

    reps = pd.concat([
        q4[q4["scenario_type"] == "baseline"].head(1),
        q4[(q4["scenario_type"] == "renewable_level") & np.isclose(q4["level"], 0.8)].head(1),
        q4[(q4["scenario_type"] == "renewable_volatility") & np.isclose(q4["seed"], 2027)].head(1),
    ], ignore_index=True)
    rep_names = ["联合基准", "新能源 0.8", "波动种子 2027"]
    matrix = np.column_stack([
        oriented_minmax(reps["carbon_tCO2"], False),
        oriented_minmax(reps["peak_net_grid_purchase_MW"], False),
        oriented_minmax(reps["net_grid_ramp_MW"], False),
        oriented_minmax(reps["renewable_utilization"], True),
        oriented_minmax(reps["service_quality"], True),
    ])
    ax = axes[1, 1]
    add_heatmap(ax, matrix, rep_names, ["低碳", "低峰值", "低波动", "高新能源率", "高服务质量"])
    ax.set_title("代表性情景的同向 min-max 展示分数", pad=24)
    panel_label(ax, "(d)")
    fig.text(0.5, -0.012, "空心点：机制未激活；×：非 completed（声明搜索内未找到目标）", ha="center", fontsize=8, color=PALETTE["gray"])
    finish(fig, "fig05_q4_scenarios.png")


def figure_sensitivity() -> None:
    price = pd.read_csv(SOLVE_DIR / "figure_data" / "sensitivity_electricity_price.csv")
    renewable = pd.read_csv(SOLVE_DIR / "figure_data" / "sensitivity_renewable_level.csv")
    fig, axes = plt.subplots(2, 1, figsize=(7.2, 5.8), constrained_layout=True)
    datasets = [
        (axes[0], price, "购电价格参数灵敏度", PALETTE["blue"], True),
        (axes[1], renewable, "新能源水平参数灵敏度", PALETTE["green"], False),
    ]
    for ax, data, title, color, show_delta in datasets:
        extended = pd.concat([
            data[["delta_pct", "objective"]],
            pd.DataFrame({"delta_pct": [0], "objective": [data["baseline"].iloc[0]]}),
        ]).sort_values("delta_pct")
        if show_delta:
            y = extended["objective"] - data["baseline"].iloc[0]
            ylabel = "相对基准成本变化/元"
        else:
            y = extended["objective"] / 1e8
            ylabel = "净成本/亿元"
        ax.plot(extended["delta_pct"], y, marker="o", color=color)
        ax.axvline(0, color=PALETTE["gray"], linestyle="--", linewidth=0.8)
        ax.axhline(0, color=PALETTE["gray"], linestyle=":", linewidth=0.7) if show_delta else None
        ax.set(title=title, xlabel="参数变化/%", ylabel=ylabel)
        ax.grid(alpha=0.2)
    panel_label(axes[0], "(a)")
    panel_label(axes[1], "(b)")
    finish(fig, "fig06_sensitivity.png")


def main() -> None:
    validate_inputs()
    figure_q1_forecast()
    figure_q1_schedule()
    figure_q2_multiobjective()
    figure_q3_storage()
    figure_q4_scenarios()
    figure_sensitivity()
    generated = sorted(p.name for p in FIGURE_DIR.glob("fig*.png"))
    expected = [
        "fig01_q1_forecast.png", "fig02_q1_schedule.png", "fig03_q2_multiobjective.png",
        "fig04_q3_storage.png", "fig05_q4_scenarios.png", "fig06_sensitivity.png",
    ]
    if generated != expected:
        raise RuntimeError(f"Unexpected generated figure set: {generated}")
    source_map = {
        "fig01_q1_forecast.png": ["q1_forecast_2376_2399.csv", "q1_rolling_predictions.csv", "q1_rolling_window_metrics.csv"],
        "fig02_q1_schedule.png": ["q1_gantt.csv", "q1_gpu_utilization.csv"],
        "fig03_q2_multiobjective.png": ["q2_named_scheme_comparison.csv", "q2_budget_stability.csv"],
        "fig04_q3_storage.png": ["q3_storage_energy.csv", "q3_no_storage_baseline.csv", "q3_metric_recomputation_audit.csv", "q3_search_summary.csv"],
        "fig05_q4_scenarios.png": ["q4_scenario_comparison.csv", "q4_joint_storage_energy.csv"],
        "fig06_sensitivity.png": ["figure_data/sensitivity_electricity_price.csv", "figure_data/sensitivity_renewable_level.csv"],
    }
    provenance = {"paper_version": 28, "solve_version": 19, "figures": []}
    for name in expected:
        provenance["figures"].append({
            "file": f"figures/paper_v28/{name}",
            "sha256": sha256(FIGURE_DIR / name),
            "sources": [{"path": src, "sha256": sha256(SOLVE_DIR / src)} for src in source_map[name]],
        })
    (PAPER_DIR / "figure_provenance_v28.json").write_text(
        json.dumps(provenance, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({"status": "ok", "figures": generated, "provenance": "figure_provenance_v28.json"}, ensure_ascii=False))


if __name__ == "__main__":
    main()
