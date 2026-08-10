from __future__ import annotations
import argparse, hashlib, importlib.util, json, os
from pathlib import Path
import numpy as np
import pandas as pd

EXPECTED_SOLUTION = "1c7778861f312aeed36bafa2c08c8ad58b84db2b9fd6f42257260fe6f72a6b71"
EXPECTED_RESULTS = "c63996f228b4ea5aa3913d1b8cb0b15d74e0b62c66deb059815193c3f699389e"

def sha256(path: Path) -> str:
    h=hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''): h.update(block)
    return h.hexdigest()

def load_solution(path: Path, data_dir: Path):
    os.environ['MMW_DATA_DIR']=str(data_dir)
    spec=importlib.util.spec_from_file_location('frozen_solution_v21',path)
    if spec is None or spec.loader is None: raise RuntimeError('cannot load frozen solution')
    module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module

def compute_metrics(selected: pd.DataFrame) -> pd.DataFrame:
    rows=[]
    for origin,g in selected.groupby('RollingOrigin',sort=True):
        series=[]
        for _,sg in g.groupby(['Region','TaskType'],sort=False):
            denom=float(sg['Actual_GPU'].sum())
            series.append(None if denom<=0 else float(sg['AbsoluteError_GPU'].sum()/denom))
        macro=float(np.mean([x for x in series if x is not None]))
        actual_sum=float(g['Actual_GPU'].sum())
        micro=float(g['AbsoluteError_GPU'].sum()/actual_sum)
        hourly=g.groupby('Hour',sort=True)[['Actual_GPU','Prediction_GPU']].sum()
        system=float((hourly['Prediction_GPU']-hourly['Actual_GPU']).abs().sum()/hourly['Actual_GPU'].sum())
        rows.append({'RollingOrigin':int(origin),'ValidationStartHour':int(origin),'ValidationEndHour':int(origin+23),'Macro_WAPE':macro,'Micro_WAPE':micro,'System_Aggregate_WAPE':system,'SeriesCount':18,'HourlyPointCount':24,'ObservationCount':int(len(g)),'ClosedLoopForecast':True,'FeatureUsesValidationTruth':False,'FinalTestUsedForSelection':False,'SelectedCandidateRule':'8-window MeanRMSE,MeanMAE,MeanWAPE,fixed_candidate_rank'})
    return pd.DataFrame(rows)

def export(case_root: Path, output_dir: Path, source_solve: Path) -> dict:
    solution=case_root/'.mmw/checkpoints/05_code/v21/solution.py'; results=source_solve/'results.json'
    if sha256(solution)!=EXPECTED_SOLUTION: raise RuntimeError('solution hash drift')
    if sha256(results)!=EXPECTED_RESULTS: raise RuntimeError('results hash drift')
    m=load_solution(solution,case_root/'附件数据')
    d=m.read_inputs(); m.validate_inputs(d); demand,_=m.aggregate_demand(d['workload'])
    table=demand.pivot_table(index='Hour',columns=['Region','TaskType'],values='GPU_Demand',fill_value=0).sort_index()
    selection=pd.read_csv(source_solve/'q1_model_selection.csv')
    selected_map={(r.Region,r.TaskType):r.SelectedCandidateID for r in selection.itertuples(index=False)}
    specs=m._forecast_candidate_specs(); rows=[]
    for region in m.REGIONS:
      for task_type in m.TASK_TYPES:
        y=table[(region,task_type)].to_numpy(float); selected_id=selected_map[(region,task_type)]
        for spec in specs:
          candidate_id=m._candidate_id(spec)
          for origin in m.Q1_ROLLING_ORIGINS:
            model=(m._fit_huber(y,origin-1,spec['HuberEpsilon'],spec['HuberAlpha']) if spec['CandidateModel']=='Huber' else None)
            pred=m._recursive_forecast(y,origin,m.Q1_FORECAST_HORIZON,spec['CandidateModel'],model)
            for offset,value in enumerate(pred):
              hour=int(origin+offset); actual=float(y[hour]); prediction=float(value)
              rows.append({'Region':region,'TaskType':task_type,'CandidateID':candidate_id,'CandidateRank':int(spec['CandidateRank']),'CandidateModel':spec['CandidateModel'],'HuberEpsilon':spec['HuberEpsilon'],'HuberAlpha':spec['HuberAlpha'],'RollingOrigin':int(origin),'TrainStartHour':0,'TrainEndHour':int(origin-1),'ValidationStartHour':int(origin),'ValidationEndHour':int(origin+m.Q1_FORECAST_HORIZON-1),'Hour':hour,'Actual_GPU':actual,'Prediction_GPU':prediction,'AbsoluteError_GPU':abs(prediction-actual),'SelectedCandidateForSeries':bool(candidate_id==selected_id),'ClosedLoopForecast':True,'FeatureUsesValidationTruth':False,'FinalTestUsedForSelection':False})
    frame=pd.DataFrame(rows).sort_values(['Region','TaskType','CandidateRank','RollingOrigin','Hour'],kind='mergesort').reset_index(drop=True)
    expected_rows=len(m.REGIONS)*len(m.TASK_TYPES)*len(specs)*len(m.Q1_ROLLING_ORIGINS)*m.Q1_FORECAST_HORIZON
    if len(frame)!=expected_rows: raise RuntimeError(f'row count {len(frame)} != {expected_rows}')
    selected=frame.loc[frame['SelectedCandidateForSeries']].copy(); expected_selected=len(m.REGIONS)*len(m.TASK_TYPES)*len(m.Q1_ROLLING_ORIGINS)*m.Q1_FORECAST_HORIZON
    if len(selected)!=expected_selected: raise RuntimeError('selected prediction row count mismatch')
    source=pd.read_csv(source_solve/'q1_rolling_validation.csv'); recomputed=[]
    for keys,g in frame.groupby(['Region','TaskType','CandidateID','RollingOrigin'],sort=False):
      denom=float(g['Actual_GPU'].sum()); err=g['Prediction_GPU']-g['Actual_GPU']
      recomputed.append({'Region':keys[0],'TaskType':keys[1],'CandidateID':keys[2],'RollingOrigin':int(keys[3]),'MAE':float(g['AbsoluteError_GPU'].mean()),'RMSE':float(np.sqrt(np.mean(np.square(err)))),'WAPE':np.nan if denom<=0 else float(g['AbsoluteError_GPU'].sum()/denom)})
    rec=pd.DataFrame(recomputed); merged=source.merge(rec,on=['Region','TaskType','CandidateID','RollingOrigin'],suffixes=('_source','_recomputed'),validate='one_to_one'); residuals={}
    for metric in ('MAE','RMSE','WAPE'):
      a=merged[f'{metric}_source'].to_numpy(float); b=merged[f'{metric}_recomputed'].to_numpy(float); mask=np.isnan(a)&np.isnan(b); diff=np.abs(a[~mask]-b[~mask]); residuals[metric]=float(diff.max(initial=0.0))
      if not np.allclose(a[~mask],b[~mask],rtol=1e-11,atol=1e-11): raise RuntimeError(f'{metric} reproduction failed')
    window=compute_metrics(selected); output_dir.mkdir(parents=True,exist_ok=True)
    pred_path=output_dir/'q1_rolling_predictions.csv'; metric_path=output_dir/'q1_rolling_window_metrics.csv'
    frame.to_csv(pred_path,index=False,float_format='%.15g'); window.to_csv(metric_path,index=False,float_format='%.15g')
    input_hashes={p.name:sha256(p) for p in sorted((case_root/'附件数据').glob('*.xlsx'))}
    report={'schema_version':1,'status':'pass','base_solve_version':18,'solve_version':19,'scope':'Q1 rolling-origin hourly prediction evidence only; no scheduling or Q2-Q4 solve','solution_sha256':sha256(solution),'results_sha256':sha256(results),'input_sha256':input_hashes,'rolling_origins':[int(x) for x in m.Q1_ROLLING_ORIGINS],'horizon_hours':int(m.Q1_FORECAST_HORIZON),'candidate_count':len(specs),'series_count':18,'prediction_rows':len(frame),'selected_prediction_rows':len(selected),'window_metric_rows':len(window),'metric_reproduction_max_abs_residual':residuals,'q1_rolling_validation_sha256':sha256(source_solve/'q1_rolling_validation.csv'),'q1_model_selection_sha256':sha256(source_solve/'q1_model_selection.csv'),'outputs':{pred_path.name:{'bytes':pred_path.stat().st_size,'sha256':sha256(pred_path)},metric_path.name:{'bytes':metric_path.stat().st_size,'sha256':sha256(metric_path)}},'no_leakage':{'closed_loop':True,'feature_uses_validation_truth':False,'final_test_used_for_selection':False,'per_window_winner_used_for_aggregate_curve':False}}
    (output_dir/'q1_rolling_hourly_provenance.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2)); return report

if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--case-root',type=Path,required=True); p.add_argument('--output-dir',type=Path,required=True); p.add_argument('--source-solve',type=Path,required=True); a=p.parse_args(); export(a.case_root.resolve(),a.output_dir.resolve(),a.source_solve.resolve())