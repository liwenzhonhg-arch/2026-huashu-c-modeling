from __future__ import annotations
import argparse,hashlib,json,zipfile
from datetime import datetime,timezone,timedelta
from pathlib import Path
HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[3]; OUT=ROOT/'output'; SOLVE=ROOT/'.mmw/checkpoints/06_solve/v19'; REVIEW=ROOT/'.mmw/checkpoints/08_review/v22'
FIGS=['fig01_q1_forecast.png','fig02_q1_schedule.png','fig03_q2_multiobjective.png','fig04_q3_storage.png','fig05_q4_scenarios.png','fig06_sensitivity.png']
PAPER_FILES=['paper_latex.md','paper_latex_source.tex','main.tex','references.bib','cumcmthesis.cls','paper_figures_v28.py','paper_validation_v28.py','paper_input_hashes.json','figure_provenance_v28.json','paper_validation_report_v28.json','layout_review.json','readability_gate.json','paper_manifest.json','method_traceability.json','build_submission_lean_v28.py','validate_submission_lean_v28.py']
EVIDENCE=['double_run_comparison.json','numeric_audit.md','numeric_audit_builtin.md','numeric_provenance.json','run_validation.json','method_consistency.json','q1_rolling_hourly_provenance.json','solve_v19_extension_validation.json','paper_validation_report_v28.json','layout_review.json','readability_gate.json']
NEW_DATA=['q1_rolling_predictions.csv','q1_rolling_window_metrics.csv','q1_rolling_hourly_provenance.json','solve_v19_extension_validation.json','solve_v19_extension_manifest.json']
FIXED=(2026,8,10,0,0,0)
def h(b): return hashlib.sha256(b).hexdigest()
def add(d,n,b):
 n=n.replace('\\','/')
 if n in d: raise ValueError('duplicate '+n)
 d[n]=b
def build(zip_path:Path,state:str):
 with zipfile.ZipFile(OUT/'submission_lean.zip') as zf: data_names=sorted(n for n in zf.namelist() if n.startswith('data/') and not n.endswith('/'))
 for n in NEW_DATA:
  q='data/'+n
  if q not in data_names:data_names.append(q)
 files={}; add(files,'paper.pdf',(HERE/'paper.pdf').read_bytes()); add(files,'code/solution.py',(ROOT/'.mmw/checkpoints/05_code/v21/solution.py').read_bytes()); add(files,'code/export_q1_rolling_hourly_v19.py',(SOLVE/'export_q1_rolling_hourly_v19.py').read_bytes())
 for n in sorted(data_names): add(files,n,(SOLVE/n.removeprefix('data/')).read_bytes())
 for n in FIGS:add(files,'figures/'+n,(HERE/'figures/paper_v28'/n).read_bytes())
 for n in PAPER_FILES:
  b=(HERE/n).read_bytes()
  if n=='paper_latex.md': b=b.replace(b'figures/paper_v28/',b'../figures/')
  if n in {'paper_latex_source.tex','main.tex'}: b=b.replace(b'figures/paper_v28/',b'../figures/')
  add(files,'paper_source/'+n,b)
 for p in sorted((HERE/'sections').glob('*.tex')): add(files,'paper_source/sections/'+p.name,p.read_bytes())
 for n in EVIDENCE:add(files,'evidence/'+n,(REVIEW/n).read_bytes())
 add(files,'requirements.txt',Path(r'F:\claude_project\code\Mathematical_Modeling_Workflow\requirements.txt').read_bytes())
 add(files,'README_run.txt',('2026 华数杯 C 题 Q1 rolling-origin 逐小时证据扩展精简包\n现役目标链：model v48 / code v21 / solve v19 / paper v28 / review v22。\nsolve v19 仅新增 Q1 预测证据；未运行 Q1 调度或 Q2-Q4 求解。\n可信等级仍为 scenario-feasible。\n').encode())
 version={'schema_version':5,'created_at':datetime.now(timezone(timedelta(hours=8))).isoformat(),'case':'2026-HSC-C','delivery':'q1-rolling-hourly-evidence-extension','promotion_state':state,'versions':{'model':48,'code':21,'solve':19,'paper':28,'review':22},'frozen_hashes':{'solution.py':h(files['code/solution.py']),'results.json':h(files['data/results.json'])},'rolling_prediction_rows':38016,'selected_prediction_rows':3456,'rolling_window_count':8,'full_q1_q4_solve_rerun':False,'q1_scheduling_rerun':False,'credibility':'scenario-feasible'}
 add(files,'VERSION.json',(json.dumps(version,ensure_ascii=False,indent=2)+'\n').encode())
 dm={'schema_version':5,'active_chain_target':version['versions'],'scope':'lean-q1-rolling-v28','files':[{'path':n,'bytes':len(b),'sha256':h(b)} for n,b in sorted(files.items())],'excluded_preserved_residue_note':'历史大 ZIP、旧图、全量搜索轨迹和验证残留不进入本包。'}
 add(files,'DATA_MANIFEST.json',(json.dumps(dm,ensure_ascii=False,indent=2)+'\n').encode()); add(files,'MANIFEST.sha256',''.join(f'{h(b)}  {n}\n' for n,b in sorted(files.items())).encode())
 tmp=zip_path.with_suffix('.tmp.zip')
 with zipfile.ZipFile(tmp,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as zf:
  for n,b in sorted(files.items()):
   info=zipfile.ZipInfo(n,FIXED);info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o100644<<16;zf.writestr(info,b)
 tmp.replace(zip_path); result={'status':'pass','state':state,'path':str(zip_path),'bytes':zip_path.stat().st_size,'sha256':h(zip_path.read_bytes()),'members':len(files),'data_files':len(data_names),'figures':6};print(json.dumps(result,ensure_ascii=False,indent=2));return result
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--zip-path',type=Path,required=True);p.add_argument('--state',choices=['candidate','active'],required=True);a=p.parse_args();build(a.zip_path.resolve(),a.state)