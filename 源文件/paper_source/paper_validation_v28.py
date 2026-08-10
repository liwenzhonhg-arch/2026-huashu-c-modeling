from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import tempfile
from pathlib import Path

import fitz
import numpy as np
from PIL import Image

HERE = Path(__file__).resolve()
PAPER = HERE.parent
CHECKPOINTS = HERE.parents[2]
PROJECT = HERE.parents[4]
SOLVE = CHECKPOINTS / "06_solve" / "v19"
CODE = CHECKPOINTS / "05_code" / "v21"
EXPECTED_CODE = "1c7778861f312aeed36bafa2c08c8ad58b84db2b9fd6f42257260fe6f72a6b71"
EXPECTED_RESULTS = "c63996f228b4ea5aa3913d1b8cb0b15d74e0b62c66deb059815193c3f699389e"
FIGURES = [
    "fig01_q1_forecast.png", "fig02_q1_schedule.png", "fig03_q2_multiobjective.png",
    "fig04_q3_storage.png", "fig05_q4_scenarios.png", "fig06_sensitivity.png",
]
OLD_FIGURES = ["q1_forecast_actual.png", "fig_1_q1_gantt.png", "fig_1_gpu_utilization.png",
               "q1_gantt.png", "q1_gpu_utilization.png", "fig_2_storage_soc.png",
               "sensitivity_electricity_price.png", "sensitivity_renewable_level.png"]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def ast_count(obj, kind: str) -> int:
    if isinstance(obj, dict):
        return int(obj.get("t") == kind) + sum(ast_count(v, kind) for v in obj.values())
    if isinstance(obj, list):
        return sum(ast_count(v, kind) for v in obj)
    return 0


def check(condition: bool, name: str, details: str = "") -> None:
    checks[name] = {"passed": bool(condition), "details": details}
    if not condition:
        failures.append(f"{name}: {details}")


parser = argparse.ArgumentParser()
parser.add_argument("--expect-active-solve", type=int, default=18)
parser.add_argument("--expect-active-paper", type=int, default=27)
parser.add_argument("--expect-active-review", type=int, default=21)
args = parser.parse_args()
checks: dict[str, dict[str, object]] = {}
failures: list[str] = []

# Frozen inputs and active chain.
manifest = json.loads((PAPER / "paper_input_hashes.json").read_text(encoding="utf-8"))
for item in manifest["inputs"]:
    if item["source_stage"] == "code":
        path = CODE / "solution.py"
    else:
        path = SOLVE / item["path"]
    actual = sha256(path) if path.is_file() else "MISSING"
    check(actual == item["sha256"], f"frozen:{item['path']}", actual)
check(sha256(CODE / "solution.py") == EXPECTED_CODE, "code_hash", sha256(CODE / "solution.py"))
check(sha256(SOLVE / "results.json") == EXPECTED_RESULTS, "results_hash", sha256(SOLVE / "results.json"))
config = (PROJECT / ".mmw" / "config.yaml").read_text(encoding="utf-8-sig")
def active(stage: str) -> int:
    m = re.search(rf"^\s{{2}}{re.escape(stage)}:\s*(\d+)\s*$", config, re.M)
    if not m:
        raise RuntimeError(f"active version not found: {stage}")
    return int(m.group(1))
check((active("model"), active("code"), active("solve")) == (48, 21, args.expect_active_solve), "active_upstream", str((active("model"), active("code"), active("solve"))))
check(active("paper") == args.expect_active_paper and active("review") == args.expect_active_review,
      "active_paper_review", str((active("paper"), active("review"))))

# Q1 rolling-hourly extension gates.
import pandas as pd
rolling_pred = pd.read_csv(SOLVE / "q1_rolling_predictions.csv")
rolling_metric = pd.read_csv(SOLVE / "q1_rolling_window_metrics.csv")
rolling_prov = json.loads((SOLVE / "q1_rolling_hourly_provenance.json").read_text(encoding="utf-8"))
extension = json.loads((SOLVE / "solve_v19_extension_validation.json").read_text(encoding="utf-8"))
check(len(rolling_pred) == 38016, "rolling_prediction_rows", str(len(rolling_pred)))
check(int(rolling_pred["SelectedCandidateForSeries"].sum()) == 3456, "rolling_selected_rows", str(int(rolling_pred["SelectedCandidateForSeries"].sum())))
check(len(rolling_metric) == 8 and rolling_metric["RollingOrigin"].nunique() == 8, "rolling_window_metrics", str(len(rolling_metric)))
check(not rolling_pred["FeatureUsesValidationTruth"].astype(bool).any() and not rolling_pred["FinalTestUsedForSelection"].astype(bool).any(), "rolling_no_leakage_flags")
check(rolling_pred["ClosedLoopForecast"].astype(bool).all(), "rolling_closed_loop")
check(rolling_prov.get("status") == "pass" and rolling_prov.get("prediction_rows") == 38016, "rolling_provenance")
check(extension.get("status") == "pass" and extension.get("inherited_files_compared") == 113 and not extension.get("hash_mismatches"), "solve_v19_negative_diff")
check(rolling_metric["System_Aggregate_WAPE"].between(0, 1).all(), "rolling_system_wape_range", str(rolling_metric["System_Aggregate_WAPE"].tolist()))

# Assumptions and relocation.
assumptions = (PAPER / "sections" / "assumptions.tex").read_text(encoding="utf-8-sig")
check(len(re.findall(r"^\\item\s", assumptions, re.M)) == 5, "assumption_count", str(len(re.findall(r"^\\item\s", assumptions, re.M))))
check("\\begin{enumerate}" in assumptions and "\\end{enumerate}" in assumptions, "assumption_structure")
model = (PAPER / "sections" / "model_solution.tex").read_text(encoding="utf-8-sig")
analysis = (PAPER / "sections" / "problem_analysis.tex").read_text(encoding="utf-8-sig")
check("38016" in model and "3456" in model and "正式 CSV 未保存" not in model, "rolling_narrative_updated")
sensitivity = (PAPER / "sections" / "sensitivity.tex").read_text(encoding="utf-8-sig")
relocations = {
    "统一时间口径": "第 $2400$--$2405$ 小时" in model,
    "任务调度约束": "实时推理任务必须满足" in model and "批量推理与 AI 训练任务" in model,
    "能源与储能约束": "充电与放电互斥" in model and "购电与售电也互斥" in model,
    "问题三模型建立": "Q2 formal balanced" in model,
    "问题一预测与调度流程": "预测模型与正式调度严格分离" in model,
    "问题四情景设计": "每个情景只改变其声明因素" in model,
    "数据预处理": "结构零" in analysis,
    "模型检验": "统一约束审计" in sensitivity,
}
check(all(relocations.values()), "relocations", json.dumps(relocations, ensure_ascii=False))

# Symbols.
symbols = (PAPER / "sections" / "symbols.tex").read_text(encoding="utf-8-sig")
body = symbols.split("\\midrule", 1)[1].split("\\bottomrule", 1)[0]
symbol_rows = len(re.findall(r"\\\\\s*$", body, re.M))
check(symbols.count("\\section{符号说明}") == 1, "symbol_section_count")
check(symbols.count("\\begin{table}") == 1 and symbols.count("\\begin{tabular}") == 1, "symbol_table_count")
check(symbol_rows <= 20 and symbol_rows == 20, "symbol_row_count", str(symbol_rows))
check("单位/类型" not in symbols and "\\subsection" not in symbols and symbols.count("符号 & 含义") == 1,
      "symbol_two_columns_single_header")

# Figures and provenance.
tex_all = "\n".join(p.read_text(encoding="utf-8-sig") for p in sorted((PAPER / "sections").glob("*.tex")))
tex_figs = re.findall(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}", tex_all)
labels = re.findall(r"\\label\{(fig:[^}]+)\}", tex_all)
check(tex_figs == FIGURES, "latex_figure_set", json.dumps(tex_figs, ensure_ascii=False))
check(len(labels) == len(set(labels)) == 6, "duplicate_figure_labels", str(labels))
script = (PAPER / "paper_figures_v28.py").read_text(encoding="utf-8-sig")
check("solution.py" not in script and "subprocess" not in script, "plot_script_no_solver")
check(script.count("panel_label(") - 1 == 16, "subplot_label_count", str(script.count("panel_label(") - 1))
actual_figs = sorted(p.name for p in (PAPER / "figures" / "paper_v28").glob("fig*.png"))
check(actual_figs == FIGURES, "required_figure_set", str(actual_figs))
for name in FIGURES:
    path = PAPER / "figures" / "paper_v28" / name
    im = Image.open(path).convert("L")
    arr = np.asarray(im)
    check(im.width >= 1800 and im.height >= 1400 and float(arr.std()) > 5,
          f"figure_quality:{name}", f"{im.width}x{im.height}, std={arr.std():.2f}")
prov = json.loads((PAPER / "figure_provenance_v28.json").read_text(encoding="utf-8"))
prov_files = [Path(x["file"]).name for x in prov["figures"]]
check(prov_files == FIGURES, "figure_provenance_set", str(prov_files))
for fig in prov["figures"]:
    fpath = PAPER / fig["file"]
    check(sha256(fpath) == fig["sha256"], f"figure_hash:{fpath.name}", sha256(fpath))
    for src in fig["sources"]:
        check(sha256(SOLVE / src["path"]) == src["sha256"], f"figure_source:{src['path']}", src["sha256"])

# Markdown paths and reverse parse.
md = (PAPER / "paper_latex.md").read_text(encoding="utf-8-sig")
md_img = re.findall(r'<img\s+src="([^"]+)"', md) + re.findall(r'!\[[^\]]*\]\(([^)]+)\)', md)
check(len(md_img) == 6 and all((PAPER / p).is_file() for p in md_img), "markdown_image_refs", str(md_img))
check({Path(p).name for p in md_img} == set(FIGURES), "unused_required_figures", str(set(FIGURES) - {Path(p).name for p in md_img}))
check(not any(old in md for old in OLD_FIGURES), "markdown_no_old_figure_names")
check("\\input{" not in md and "\\includegraphics" not in md, "markdown_no_latex_include")
md_ids = re.findall(r'<figure id="([^"]+)"', md)
check(len(md_ids) == len(set(md_ids)) == 6, "markdown_figure_ids", str(md_ids))
check(md.count("| 符号 | 含义 |") == 1, "markdown_symbol_header_once", str(md.count("| 符号 | 含义 |")))
source = (PAPER / "paper_latex_source.tex").read_text(encoding="utf-8-sig")
check("\\input{" not in source, "expanded_source_no_input")
with tempfile.TemporaryDirectory() as td:
    latex_ast = Path(td) / "latex.json"
    md_ast = Path(td) / "md.json"
    r1 = subprocess.run(["pandoc", str(PAPER / "paper_latex_source.tex"), "-f", "latex", "-t", "json", "--citeproc", f"--bibliography={PAPER / 'references.bib'}", "-o", str(latex_ast)], capture_output=True, text=True)
    r2 = subprocess.run(["pandoc", str(PAPER / "paper_latex.md"), "-f", "gfm+tex_math_dollars+raw_html", "-t", "json", "-o", str(md_ast)], capture_output=True, text=True)
    check(r1.returncode == 0 and r2.returncode == 0, "pandoc_reverse_parse", f"{r1.returncode}/{r2.returncode}")
    if r1.returncode == 0 and r2.returncode == 0:
        la = json.loads(latex_ast.read_text(encoding="utf-8")); ma = json.loads(md_ast.read_text(encoding="utf-8"))
        check(ast_count(la, "Math") == ast_count(ma, "Math") == 128, "formula_count_match", f"{ast_count(la,'Math')}/{ast_count(ma,'Math')}")
        check(ast_count(la, "Table") == ast_count(ma, "Table") == 5, "table_count_match", f"{ast_count(la,'Table')}/{ast_count(ma,'Table')}")

# PDF compile and visual-machine gates.
pdf_path = PAPER / "main.pdf"
doc = fitz.open(pdf_path)
check(len(doc) <= 20 and len(doc) == 17, "pdf_page_count", str(len(doc)))
blank_pages = []
for i, page in enumerate(doc):
    pix = page.get_pixmap(matrix=fitz.Matrix(0.5, 0.5), colorspace=fitz.csGRAY, alpha=False)
    arr = np.frombuffer(pix.samples, dtype=np.uint8)
    dark_ratio = float((arr < 245).mean())
    if dark_ratio < 0.003:
        blank_pages.append(i + 1)
check(not blank_pages, "pdf_blank_pages", str(blank_pages))
pdf_text = "\n".join(page.get_text() for page in doc)
for token in ["0.693131", "22150.241", "c63996f2", "scenario-feasible"]:
    check(token in pdf_text and token in md and token in source, f"cross_format:{token}")
check("参考文献" in pdf_text and "# 参考文献" in md and "\\bibliography{references}" in source, "cross_format:references")
log = (PAPER / "main.log").read_text(encoding="utf-8", errors="replace")
check("Overfull \\hbox" not in log and "Underfull \\hbox" not in log, "latex_box_warnings")
check("undefined references" not in log.lower() and "LaTeX Warning" not in log, "latex_reference_warnings")
check("题号：C" in source, "team_placeholder_unchanged")

report = {
    "schema_version": 1,
    "status": "pass" if not failures else "fail",
    "paper_version": 28,
    "expected_active": {"paper": args.expect_active_paper, "review": args.expect_active_review},
    "checks": checks,
    "summary": {
        "assumption_count": 5,
        "symbol_rows": symbol_rows,
        "figure_count": len(tex_figs),
        "subplot_count": script.count("panel_label(") - 1,
        "markdown_image_refs": len(md_img),
        "missing_image_refs": sum(not (PAPER / p).is_file() for p in md_img),
        "unused_required_figures": len(set(FIGURES) - {Path(p).name for p in md_img}),
        "duplicate_figure_labels": len(labels) - len(set(labels)),
        "pdf_pages": len(doc),
        "failures": failures,
    },
}
(PAPER / "paper_validation_report_v28.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(report["summary"] | {"status": report["status"]}, ensure_ascii=False))
raise SystemExit(0 if not failures else 1)

