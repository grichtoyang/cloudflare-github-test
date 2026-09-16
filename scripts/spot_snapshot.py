#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,os,sys
from datetime import datetime,timezone
from pathlib import Path
from urllib.request import Request,urlopen

PROXY=os.getenv('TWSE_PROXY_BASE_URL','https://twse-proxy.grichtoyang.workers.dev')

def num(v):
    if v is None:return None
    s=str(v).replace(',','').replace('%','').replace('－','-').replace('—','-').strip()
    if s in ('','--','---','null','None','N/A'):return None
    try:return float(s)
    except Exception:return None

def get(url):
    try:
        r=urlopen(Request(url,headers={'accept':'application/json','user-agent':'daily-pre-market-analysis/1.0'}),timeout=45)
        return json.loads(r.read().decode())
    except Exception:return {}

def first_num(d,*keys):
    if not isinstance(d,dict):return None
    for k in keys:
        if k in d:
            v=num(d[k])
            if v is not None:return v
    return None

def breadth_values(obj):
    out={k:None for k in ('up','down','unchanged','limit_up','limit_down')}
    rows=obj.get('data',[]) if isinstance(obj,dict) else []
    for row in rows:
        if not isinstance(row,list) or len(row)<2:continue
        label=str(row[0]).strip(); text=str(row[1]).strip()
        base=text.split('(',1)[0]
        if label.startswith('上漲'):
            out['up']=num(base)
            if '(' in text:out['limit_up']=num(text.split('(',1)[1].rstrip(')'))
        elif label.startswith('下跌'):
            out['down']=num(base)
            if '(' in text:out['limit_down']=num(text.split('(',1)[1].rstrip(')'))
        elif label=='持平':out['unchanged']=num(text)
    return out

def main():
    p=argparse.ArgumentParser();p.add_argument('--date',required=True);p.add_argument('--output-root',default='data');a=p.parse_args()
    root=Path(a.output_root);d=a.date;tw=root/'twse'/f'{d}.json';base={}
    if tw.exists():
        try:base=json.loads(tw.read_text(encoding='utf-8'))
        except Exception:pass
    if not base:base=get(PROXY.rstrip('/')+'?date='+d.replace('-',''))
    raw=base.get('data',base) if isinstance(base,dict) else {}
    t=raw.get('taiex',{}) if isinstance(raw,dict) else {}
    ms=raw.get('market_statistics',{}) if isinstance(raw,dict) else {}
    b=raw.get('advance_decline',{}) if isinstance(raw,dict) else {}
    bv=breadth_values(b)
    total=None
    for row in ms.get('data',[]) if isinstance(ms,dict) else []:
        if isinstance(row,list) and row and str(row[0]).startswith('總計') and len(row)>1:total=num(row[1])
    data={'taiex':{'close':first_num(t,'close','收盤指數'),'open':first_num(t,'open','開盤指數'),'high':first_num(t,'high','最高指數'),'low':first_num(t,'low','最低指數'),'change_points':first_num(t,'change','漲跌點數'),'change_percent':first_num(t,'change_percent','漲跌百分比')},'listed_breadth':bv,'otc_breadth':{k:None for k in bv},'institutional':{'unit':'shares','foreign':None,'investment_trust':None,'dealer':None,'total':None},'margin':{'financing_balance':None,'financing_change':None,'short_balance':None,'short_change':None,'maintenance_ratio':None},'sbl':{'balance':None,'short_sale_balance':None,'short_sale_change':None},'turnover':{'listed':total,'otc':None,'total':total}}
    missing=[f'taiex.{k}' for k in ('close','change_points','change_percent') if data['taiex'][k] is None]
    unavailable=[f'{g}.{k}' for g,v in data.items() for k,x in v.items() if x is None]
    out={'ok':not missing,'source':'SPOT','date':d,'retrieved_at':datetime.now(timezone.utc).isoformat(),'timezone':'UTC','data':data,'sources':{'twse_snapshot':str(tw)},'missing_required':missing,'unavailable_fields':unavailable,'integrity_errors':[]}
    for path in (root/'snapshots'/d/'spot-snapshot.json',root/'spot'/f'{d}.json'):
        path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'date':d,'ok':out['ok'],'missing_required':missing,'unavailable_fields':unavailable,'integrity_errors':[]},ensure_ascii=False))
    return 0 if out['ok'] else 1

if __name__=='__main__':sys.exit(main())
