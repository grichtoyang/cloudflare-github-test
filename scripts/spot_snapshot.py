#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,os,sys
from datetime import datetime,timezone
from pathlib import Path
from urllib.request import Request,urlopen

PROXY=os.getenv('TWSE_PROXY_BASE_URL','https://twse-proxy.grichtoyang.workers.dev')

def get(url):
    try:
        r=urlopen(Request(url,headers={'accept':'application/json','user-agent':'daily-pre-market-analysis/1.0'}),timeout=45)
        return json.loads(r.read().decode())
    except Exception:
        return {}

def num(v):
    try:
        s=str(v).replace(',','').replace('%','').replace('－','-').replace('—','-').strip()
        if s in ('','--','---','null','None','N/A'): return None
        return float(s)
    except Exception: return None

def walk(x):
    if isinstance(x,dict):
        yield x
        for v in x.values(): yield from walk(v)
    elif isinstance(x,list):
        for v in x: yield from walk(v)

def find(x,names):
    names={n.lower() for n in names}
    for d in walk(x):
        for k,v in d.items():
            if str(k).lower() in names:
                n=num(v)
                if n is not None: return n
    return None

def main():
    p=argparse.ArgumentParser(); p.add_argument('--date',required=True); p.add_argument('--output-root',default='data'); a=p.parse_args()
    root=Path(a.output_root); d=a.date; tw=root/'twse'/f'{d}.json'
    base={}
    if tw.exists():
        try: base=json.loads(tw.read_text(encoding='utf-8'))
        except Exception: pass
    if not base: base=get(PROXY.rstrip('/')+'?date='+d.replace('-',''))
    raw=base.get('data',base) if isinstance(base,dict) else {}
    taiex=raw.get('taiex',{}) if isinstance(raw,dict) else {}
    ms=raw.get('market_statistics',{}) if isinstance(raw,dict) else {}
    breadth=raw.get('advance_decline',{}) if isinstance(raw,dict) else {}
    data={
      'taiex': {'close':find(taiex,['close']),'open':None,'high':None,'low':None,'change_points':find(taiex,['change']),'change_percent':find(taiex,['change_percent'])},
      'listed_breadth': {'up':find(breadth,['up']),'down':find(breadth,['down']),'unchanged':find(breadth,['unchanged']),'limit_up':find(breadth,['limit_up']),'limit_down':find(breadth,['limit_down'])},
      'otc_breadth': {'up':None,'down':None,'unchanged':None,'limit_up':None,'limit_down':None},
      'institutional': {'unit':'shares','foreign':None,'investment_trust':None,'dealer':None,'total':None},
      'margin': {'financing_balance':None,'financing_change':None,'short_balance':None,'short_change':None,'maintenance_ratio':None},
      'sbl': {'balance':None,'short_sale_balance':None,'short_sale_change':None},
      'turnover': {'listed':find(ms,['turnover_value']),'otc':None,'total':find(ms,['turnover_value'])}
    }
    required={'taiex':['close']}
    missing=[f'{g}.{k}' for g,ks in required.items() for k in ks if data[g].get(k) is None]
    unavailable=[f'{g}.{k}' for g,values in data.items() for k,v in values.items() if v is None and not (g=='taiex' and k=='close')]
    out={'ok':not missing,'source':'SPOT','date':d,'retrieved_at':datetime.now(timezone.utc).isoformat(),'timezone':'UTC','data':data,'sources':{'twse_snapshot':str(tw)},'missing_required':missing,'unavailable_fields':unavailable,'integrity_errors':[]}
    for path in (root/'snapshots'/d/'spot-snapshot.json',root/'spot'/f'{d}.json'):
        path.parent.mkdir(parents=True,exist_ok=True); path.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'date':d,'ok':out['ok'],'missing_required':missing,'unavailable_fields':unavailable,'integrity_errors':[]},ensure_ascii=False))
    return 0 if out['ok'] else 1

if __name__=='__main__': sys.exit(main())
