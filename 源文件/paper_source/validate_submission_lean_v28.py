from __future__ import annotations
import argparse,hashlib,io,json,re,zipfile
import numpy as np
import pandas as pd
from datetime import datetime,timezone,timedelta
from pathlib import Path,PurePosixPath
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3];OUT=ROOT/'output'
FIGS={f'figures/{n}' for n in ['fig01_q1_forecast.png','fig02_q1_schedule.png','fig03_q2_multiobjective.png','fig04_q3_storage.png','fig05_q4_scenarios.png','fig06_sensitivity.png']}
def h(b):return hashlib.sha256(b).hexdigest()
def recompute_window_metrics(pred):
 rows=[]; selected=pred.loc[pred['SelectedCandidateForSeries'].astype(bool)].copy()
 for origin,g in selected.groupby('RollingOrigin',sort=True):
  series=[]
  for _,sg in g.groupby(['Region','TaskType'],sort=False):
   denom=float(sg['Actual_GPU'].sum());series.append(float(sg['AbsoluteError_GPU'].sum()/denom) if denom>0 else np.nan)
  hourly=g.groupby('Hour')[['Actual_GPU','Prediction_GPU']].sum()
  rows.append({'RollingOrigin':int(origin),'Macro_WAPE':float(np.nanmean(series)),'Micro_WAPE':float(g['AbsoluteError_GPU'].sum()/g['Actual_GPU'].sum()),'System_Aggregate_WAPE':float((hourly['Prediction_GPU']-hourly['Actual_GPU']).abs().sum()/hourly['Actual_GPU'].sum())})
 return pd.DataFrame(rows),len(selected)
def validate(zpath:Path):
 fail=[]
 with zipfile.ZipFile(zpath) as zf:
  names=zf.namelist();zset=set(names)
  if len(names)!=len(zset):fail.append('duplicate members')
  for n in names:
   p=PurePosixPath(n)
   if p.is_absolute() or '..' in p.parts:fail.append('unsafe '+n)
   if {x.lower() for x in p.parts}&{'.env','__pycache__','.pytest_cache','cookie','cookies'}:fail.append('forbidden '+n)
  bad=zf.testzip()
  if bad:fail.append('CRC '+bad)
  figs={n for n in names if n.startswith('figures/') and n.endswith('.png')}
  if figs!=FIGS:fail.append('figure set')
  req=FIGS|{'paper.pdf','code/solution.py','code/export_q1_rolling_hourly_v19.py','data/results.json','data/q1_rolling_predictions.csv','data/q1_rolling_window_metrics.csv','data/q1_rolling_hourly_provenance.json','data/solve_v19_extension_manifest.json','paper_source/paper_latex.md','VERSION.json','DATA_MANIFEST.json','MANIFEST.sha256'}
  if req-zset:fail.append('missing '+str(sorted(req-zset)))
  listed={}
  for line in zf.read('MANIFEST.sha256').decode().splitlines(): digest,n=line.split('  ',1);listed[n]=digest
  if set(listed)!=zset-{'MANIFEST.sha256'}:fail.append('manifest set')
  for n,d in listed.items():
   if h(zf.read(n))!=d:fail.append('manifest hash '+n)
  md=zf.read('paper_source/paper_latex.md').decode();refs=re.findall(r'<img\s+src="([^"]+)"',md)+re.findall(r'!\[[^\]]*\]\(([^)]+)\)',md)
  if set(refs)!={ '../'+n for n in FIGS}:fail.append('markdown refs '+str(refs))
  ver=json.loads(zf.read('VERSION.json'))
  if ver['versions']!={'model':48,'code':21,'solve':19,'paper':28,'review':22}:fail.append('version chain')
  if ver['frozen_hashes']['solution.py']!='1c7778861f312aeed36bafa2c08c8ad58b84db2b9fd6f42257260fe6f72a6b71':fail.append('solution hash')
  if ver['frozen_hashes']['results.json']!='c63996f228b4ea5aa3913d1b8cb0b15d74e0b62c66deb059815193c3f699389e':fail.append('results hash')
  pred=pd.read_csv(io.BytesIO(zf.read('data/q1_rolling_predictions.csv'))); pred_rows=len(pred)
  metrics_df=pd.read_csv(io.BytesIO(zf.read('data/q1_rolling_window_metrics.csv'))); recomputed,selected_rows=recompute_window_metrics(pred)
  if pred_rows!=38016:fail.append('prediction rows')
  if selected_rows!=3456:fail.append('selected prediction rows')
  if pred['FeatureUsesValidationTruth'].astype(bool).any() or pred['FinalTestUsedForSelection'].astype(bool).any() or not pred['ClosedLoopForecast'].astype(bool).all():fail.append('leakage flags')
  merged=metrics_df.merge(recomputed,on='RollingOrigin',suffixes=('_file','_recomputed'),validate='one_to_one'); recompute_max=0.0
  for metric in ('Macro_WAPE','Micro_WAPE','System_Aggregate_WAPE'):
   diff=np.abs(merged[f'{metric}_file']-merged[f'{metric}_recomputed']);recompute_max=max(recompute_max,float(diff.max()))
  if len(metrics_df)!=8 or recompute_max>1e-12:fail.append(f'window metrics recompute {recompute_max}')
  stamp=datetime.now(timezone(timedelta(hours=8))).strftime('%Y%m%dT%H%M%S%f');ex=OUT/f'package-validation-v28-{stamp}';ex.mkdir(exist_ok=False);zf.extractall(ex)
 for n,d in listed.items():
  p=ex/Path(n)
  if not p.is_file() or h(p.read_bytes())!=d:fail.append('extract '+n)
 for ref in refs:
  if not (ex/'paper_source'/ref).resolve().is_file():fail.append('extracted markdown '+ref)
 result={'schema_version':3,'status':'pass' if not fail else 'fail','zip_path':str(zpath),'zip_bytes':zpath.stat().st_size,'zip_sha256':h(zpath.read_bytes()),'member_count':len(names),'figure_count':len(figs),'prediction_rows':pred_rows,'selected_prediction_rows':selected_rows,'window_metric_rows':len(metrics_df),'metric_recompute_max_abs_residual':recompute_max,'markdown_image_refs':len(refs),'fresh_extraction_root':str(ex),'crc_passed':bad is None,'path_security_passed':not any(x.startswith(('unsafe','forbidden')) for x in fail),'manifest_passed':not any('manifest' in x or 'extract ' in x for x in fail),'size_under_20_mib':zpath.stat().st_size<20*1024*1024,'failures':fail};print(json.dumps(result,ensure_ascii=False,indent=2))
 if fail:raise SystemExit(1)
 return result
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--zip-path',type=Path,required=True);a=p.parse_args();validate(a.zip_path.resolve())