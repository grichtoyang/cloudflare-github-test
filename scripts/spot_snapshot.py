#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,sys,re
from datetime import datetime,timezone
from pathlib import Path

def num(v):
    if v is None:return None
    s=str(v).replace(',','').replace('%','').replace('－','-').replace('—','-').strip()
    if s in ('','--','---','N/A','null','None','除息','-'):return None
    m=re.search(r'-?\d+(?:\.\d+)?',s)
    return float(m.group()) if m else None

def load(root,name,date):
    candidates=[root/'raw'/f'{name}_{date}.json',root/'twse'/f'{date}.json'] if name.startswith('twse_') else [root/'raw'/f'{name}_{date}.json']
    for p in candidates:
        if not p.exists():continue
        try:
            x=json.loads(p.read_text(encoding='utf-8'))
            if p.parent.name=='twse':
                data=x.get('data',{})
                return {'twse_snapshot':True,'data':data}
            return x.get('payload') if isinstance(x,dict) else x
        except Exception: pass
    return None

def rows(x):
    if isinstance(x,list): return x
    if isinstance(x,dict):
        fields=x.get('fields') or x.get('columns') or []; data=x.get('data') or x.get('records') or x.get('aaData') or []
        if fields and data:return [{str(fields[i]):v for i,v in enumerate(r) if i<len(fields)} if isinstance(r,list) else r for r in data]
        return data if isinstance(data,list) else []
    return []

def field(r,*names):
    if not isinstance(r,dict):return None
    for n in names:
        if n in r:return num(r[n])
    for k,v in r.items():
        nk=re.sub(r'[^a-z0-9一-龥]','',str(k).lower())
        if any(re.sub(r'[^a-z0-9一-龥]','',str(n).lower())==nk for n in names):return num(v)
    return None

def first(x,pred=lambda r:True):return next((r for r in rows(x) if isinstance(r,dict) and pred(r)),{})
def total(x,*names):
    vals=[field(r,*names) for r in rows(x)]; vals=[v for v in vals if v is not None]
    return sum(vals) if vals else None
def add(a,b):return a+b if a is not None and b is not None else (a if b is None else b)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--date',required=True);ap.add_argument('--output-root',default='data');a=ap.parse_args();d=a.date;root=Path(a.output_root)
    twse=load(root,'twse_mi_index',d)
    twse_data=twse.get('data',{}) if isinstance(twse,dict) and twse.get('twse_snapshot') else {}
    mi=load(root,'twse_mi_index',d); bread=load(root,'twse_listed_breadth',d); t86=load(root,'twse_t86',d); margin=load(root,'twse_margin',d); sbl=load(root,'twse_sbl',d); turn=load(root,'twse_turnover',d); om=load(root,'tpex_margin',d); os=load(root,'tpex_sbl',d); oh=load(root,'tpex_highlight',d)
    if twse_data:
        taiex=twse_data.get('taiex',{}); stats=twse_data.get('market_statistics',{}); breadth=twse_data.get('advance_decline',{})
        data={'taiex':{'close':num(taiex.get('close')),'open':None,'high':None,'low':None,'change_points':num(taiex.get('change')),'change_percent':num(taiex.get('change_percent')),'turnover_value':table_value(stats,'總計(1~15)','成交金額(元)')},'listed_breadth':{'up':table_value(breadth,'上漲(漲停)','股票'),'down':table_value(breadth,'下跌(跌停)','股票'),'unchanged':table_value(breadth,'持平','股票'),'limit_up':None,'limit_down':None}}
    else:
        idx=first(mi,lambda r:r.get('指數')=='發行量加權股價指數'); listed=first(bread,lambda r:r.get('類型')=='股票'); tr=first(turn) ; data={'taiex':{'close':field(idx,'收盤指數'),'open':None,'high':None,'low':None,'change_points':field(idx,'漲跌點數'),'change_percent':field(idx,'漲跌百分比'),'turnover_value':field(tr,'TradeValue')},'listed_breadth':{'up':field(listed,'上漲'),'down':field(listed,'下跌'),'unchanged':field(listed,'持平'),'limit_up':field(listed,'漲停'),'limit_down':field(listed,'跌停')}}
    data.update({'otc_breadth':{},'institutional':{},'margin':{},'sbl':{},'turnover':{'listed':data['taiex']['turnover_value'],'otc':None,'total':data['taiex']['turnover_value']}})
    unavailable=[f'{g}.{k}' for g,v in data.items() for k,x in v.items() if x is None and not (g=='taiex' and k in ('open','high','low'))]
    out={'ok':not unavailable,'source':'SPOT','date':d,'retrieved_at':datetime.now(timezone.utc).isoformat(),'timezone':'UTC','data':data,'missing_required':[],'unavailable_fields':unavailable,'integrity_errors':[]}
    for p in (root/'snapshots'/d/'spot-snapshot.json',root/'spot'/f'{d}.json'):
        p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'date':d,'ok':out['ok'],'missing_required':[],'unavailable_fields':unavailable,'integrity_errors':[]},ensure_ascii=False));return 0 if out['ok'] else 1

def table_value(table,label,column):
    fields=table.get('fields',[]) if isinstance(table,dict) else []; rows_=table.get('data',[]) if isinstance(table,dict) else []
    try:i=fields.index(column)
    except ValueError:return None
    for r in rows_:
        if r and str(r[0]).strip()==label:return num(r[i]) if len(r)>i else None
    return None
if __name__=='__main__':sys.exit(main())
