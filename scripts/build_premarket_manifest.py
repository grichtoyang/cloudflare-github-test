#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, sys
from datetime import date, datetime, timezone
from pathlib import Path

def now_utc(): return datetime.now(timezone.utc).isoformat().replace('+00:00','Z')
def read_json(path):
    with path.open(encoding='utf-8') as f: v=json.load(f)
    if not isinstance(v,dict): raise ValueError(f'{path} is not a JSON object')
    return v
def sha256(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def validate_snapshot(path, source, t0):
    errors=[]
    if not path.exists(): return [f'{source} snapshot missing: {path}']
    try: s=read_json(path)
    except Exception as e: return [f'{source} snapshot invalid JSON: {e}']
    if s.get('source') != source: errors.append(f'{source} source mismatch')
    if s.get('date') != t0: errors.append(f'{source} date mismatch')
    ready=s.get('validation',{}).get('ready_for_analysis')
    if ready is None: ready=s.get('ok') is True
    if ready is not True: errors.append(f'{source} snapshot not ready')
    if not isinstance(s.get('data'),dict) or not s.get('data'): errors.append(f'{source} data empty')
    return errors
def validate_manifest(path, source, t0):
    if not path.exists(): return False,[f'missing manifest: {path}'],{}
    try: m=read_json(path)
    except Exception as e: return False,[f'cannot read {path}: {e}'],{}
    errors=[]
    if (m.get('t0_trading_date') or m.get('analysis_date')) != t0: errors.append(f'{source} date mismatch')
    if m.get('source') != source: errors.append(f'{source} source mismatch')
    if m.get('ready_for_analysis') is not True: errors.append(f'{source} not ready')
    if m.get('published') is not True: errors.append(f'{source} not published')
    ref=m.get('published_snapshot')
    if not ref: errors.append(f'{source} snapshot reference missing')
    else:
        errors += validate_snapshot(Path(ref),source,t0)
        if m.get('snapshot_sha256') and sha256(Path(ref)) != m['snapshot_sha256']: errors.append(f'{source} SHA256 mismatch')
    return not errors,errors,m
def main(argv=None):
    p=argparse.ArgumentParser(); p.add_argument('--date',required=True); p.add_argument('--analysis-date',required=True); p.add_argument('--output-root',default='data'); a=p.parse_args(argv)
    try: date.fromisoformat(a.date); date.fromisoformat(a.analysis_date)
    except ValueError: print('invalid date',file=sys.stderr); return 2
    root=Path(a.output_root); out=root/'premarket'/f'{a.analysis_date}.json'
    if out.exists():
        try: old=read_json(out)
        except Exception: old={}
        if old.get('ready_for_analysis') is True and old.get('published') is True: return 3
    specs=[('TAIFEX',root/'manifests'/f'{a.date}.json'),('TWSE',root/'manifests'/f'{a.date}.twse.json'),('SPOT',root/'snapshots'/a.date/'spot-snapshot.json')]
    results={}; errors=[]
    for source,path in specs:
        if source=='SPOT':
            e=validate_snapshot(path,source,a.date); ok=not e; m={}
        else: ok,e,m=validate_manifest(path,source,a.date)
        results[source]=(ok,e,m); errors+=e
    ready=not errors
    manifest={'manifest_version':'1.4.0','manifest_type':'pre-market','analysis_date':a.analysis_date,'t0_trading_date':a.date,'created_at':now_utc(),'sources':{},'validation':{'required_sources':[x[0] for x in specs],'successful_sources':[s for s,(ok,_,__) in results.items() if ok],'validation_errors':errors},'ready_for_analysis':ready,'published':ready}
    for source,path in specs:
        ok,e,m=results[source]; ref=str(path)
        manifest['sources'][source]={'ready_for_analysis':ok,'snapshot':ref,'snapshot_sha256':sha256(path) if ok and path.exists() else None}
        if source!='SPOT': manifest['sources'][source]['manifest']=str(path)
    if not ready:
        d=root/'snapshots'/a.date/f'attempt-premarket-{datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")}'; d.mkdir(parents=True,exist_ok=True); (d/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8'); print(json.dumps(manifest,ensure_ascii=False,indent=2)); return 1
    out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8'); print(json.dumps(manifest,ensure_ascii=False,indent=2)); return 0
if __name__=='__main__': raise SystemExit(main())