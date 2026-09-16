#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,os,sys
from datetime import datetime,timezone
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request,urlopen

TWSE_PROXY=os.getenv('TWSE_PROXY_BASE_URL','https://twse-proxy.grichtoyang.workers.dev')
TWSE_API='https://openapi.twse.com.tw/v1'; TWSE_RWD='https://www.twse.com.tw/rwd/zh'; TPEX_API='https://www.tpex.org.tw/openapi/v1'

def num(v):
    if v is None:return None
    s=str(v).replace(',','').replace('%','').replace('－','-').replace('—','-').strip()
    if s in ('','--','---','N/A','null','None'):return None
    try:return float(s)
    except:return None

def get(url):
    try:
        r=urlopen(Request(url,headers={'accept':'application/json','user-agent':'daily-pre-market-analysis/1.3'}),timeout=45)
        return json.loads(r.read().decode('utf-8'))
    except:return None

def matrix(p):
    if not isinstance(p,dict): return []
    fields=p.get('fields') or p.get('columns') or []
    data=p.get('data') or p.get('aaData') or p.get('records') or []
    if not isinstance(fields,list) or not isinstance(data,list): return []
    out=[]
    for row in data:
        if isinstance(row,list): out.append({str(fields[i]):v for i,v in enumerate(row) if i<len(fields)})
        elif isinstance(row,dict): out.append(row)
    return out

def rows(p):
    if isinstance(p,list): return p
    if not isinstance(p,dict): return []
    m=matrix(p)
    if m:return m
    for k in ('data','aaData','results','result','records'):
        if isinstance(p.get(k),list): return p[k]
    return []

def val(row,names):
    if not isinstance(row,dict):return None
    for k,v in row.items():
        key=str(k).replace(' ','').lower()
        if any(str(n).replace(' ','').lower() in key for n in names):
            x=num(v)
            if x is not None:return x
    return None

def find(p,names):
    for r in rows(p):
        x=val(r,names)
        if x is not None:return x
    return None

def fetch(urls):
    for u in urls:
        p=get(u)
        if p is not None:return p,u
    return None,None

def rwd(path,date8,extra=None):
    q={'date':date8,'response':'json'}
    if extra:q.update(extra)
    return f'{TWSE_RWD}/{path}?{urlencode(q)}'

def breadth(p):
    out={k:None for k in ('up','down','unchanged','limit_up','limit_down')}
    for r in rows(p):
        text=' '.join(str(v) for v in (r.values() if isinstance(r,dict) else r))
        if '上漲' in text or '上升' in text: out['up']=out['up'] or find({'data':[r]},('上漲','上升','up')); out['limit_up']=out['limit_up'] or find({'data':[r]},('漲停','limitup'))
        if '下跌' in text: out['down']=out['down'] or find({'data':[r]},('下跌','down')); out['limit_down']=out['limit_down'] or find({'data':[r]},('跌停','limitdown'))
        if '持平' in text or '平盤' in text: out['unchanged']=out['unchanged'] or find({'data':[r]},('持平','平盤','unchanged'))
    return out

def amount(p):
    for r in rows(p):
        text=' '.join(str(v) for v in (r.values() if isinstance(r,dict) else r))
        if '總計' in text or '合計' in text:return val(r,('成交金額','成交額','amount','turnover'))
    return find(p,('成交金額','成交額','amount','turnover'))

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--date',required=True);ap.add_argument('--output-root',default='data');a=ap.parse_args(); d=a.date; date8=d.replace('-',''); root=Path(a.output_root)
    tw=root/'twse'/f'{d}.json'; base={}
    if tw.exists():
        try:base=json.loads(tw.read_text(encoding='utf-8'))
        except:pass
    raw=base.get('data',base) if isinstance(base,dict) else {}; t=raw.get('taiex',{}); stats=raw.get('market_statistics',{}); br=raw.get('advance_decline',{})
    t86,u86=fetch([rwd('fund/T86',date8,{'selectType':'ALL'})]); mi,u_mi=fetch([f'{TWSE_API}/exchangeReport/MI_MARGN?date={date8}']); sbl,u_sbl=fetch([f'{TWSE_API}/SBL/TWT96U?date={date8}']); listed,u_list=fetch([f'{TWSE_API}/exchangeReport/FMTQIK?date={date8}'])
    oq,uo=fetch([f'{TPEX_API}/tpex_mainboard_quotes?date={date8}',f'{TPEX_API}/tpex_mainboard_quotes']); om,um=fetch([f'{TPEX_API}/tpex_mainboard_margin_balance?date={date8}',f'{TPEX_API}/tpex_mainboard_margin_balance']); osbl,us=fetch([f'{TPEX_API}/tpex_margin_sbl?date={date8}',f'{TPEX_API}/tpex_margin_sbl']); oh,uh=fetch([f'{TPEX_API}/tpex_mainborad_highlight?date={date8}',f'{TPEX_API}/tpex_mainborad_highlight'])
    listed_total=amount(listed); otc_total=amount(oh)
    data={'taiex':{'close':num(t.get('close')),'open':num(t.get('open')),'high':num(t.get('high')),'low':num(t.get('low')),'change_points':num(t.get('change',t.get('change_points'))),'change_percent':num(t.get('change_percent')),'turnover_value':listed_total},'listed_breadth':breadth(br),'otc_breadth':breadth(oq),'institutional':{'unit':'shares','foreign':find(t86,('外陸資買賣超','外資及陸資買賣超','foreign')),'investment_trust':find(t86,('投信買賣超','investmenttrust')),'dealer':find(t86,('自營商買賣超','dealer')),'total':find(t86,('三大法人買賣超合計','合計買賣超','total'))},'margin':{'financing_balance':find(mi,('融資餘額','financingbalance')),'financing_change':find(mi,('融資增減','financingchange')),'short_balance':find(mi,('融券餘額','shortbalance')),'short_change':find(mi,('融券增減','shortchange')),'maintenance_ratio':find(mi,('融資維持率','maintenanceratio'))},'sbl':{'balance':find(sbl,('借券餘額','balance')),'short_sale_balance':find(sbl,('借券賣出餘額','shortsalebalance')),'short_sale_change':find(sbl,('借券賣出增減','shortsalechange'))},'turnover':{'listed':listed_total,'otc':otc_total,'total':(listed_total or 0)+(otc_total or 0) if listed_total is not None or otc_total is not None else None}}
    missing=[f'taiex.{k}' for k in ('close','change_points','change_percent') if data['taiex'][k] is None]; unavailable=[f'{g}.{k}' for g,v in data.items() for k,x in v.items() if x is None]
    out={'ok':not missing and not unavailable,'source':'SPOT','date':d,'retrieved_at':datetime.now(timezone.utc).isoformat(),'timezone':'UTC','data':data,'sources':{'twse_snapshot':str(tw),'twse_t86':u86,'twse_margin':u_mi,'twse_sbl':u_sbl,'twse_turnover':u_list,'tpex_breadth':uo,'tpex_margin':um,'tpex_sbl':us,'tpex_turnover':uh},'missing_required':missing,'unavailable_fields':unavailable,'integrity_errors':[]}
    for p in (root/'snapshots'/d/'spot-snapshot.json',root/'spot'/f'{d}.json'):
        p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'date':d,'ok':out['ok'],'missing_required':missing,'unavailable_fields':unavailable,'integrity_errors':[]},ensure_ascii=False)); return 0 if out['ok'] else 1

if __name__=='__main__':sys.exit(main())
