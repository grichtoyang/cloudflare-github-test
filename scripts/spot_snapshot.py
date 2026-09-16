#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,os,sys,re
from datetime import datetime,timezone
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request,urlopen

TWSE_API='https://openapi.twse.com.tw/v1'; TWSE_RWD='https://www.twse.com.tw/rwd/zh'; TPEX_API='https://www.tpex.org.tw/openapi/v1'

def num(v):
    if v is None:return None
    s=str(v).replace(',','').replace('%','').replace('－','-').replace('—','-').strip()
    if s in ('','--','---','N/A','null','None'):return None
    m=re.search(r'-?\d+(?:\.\d+)?',s)
    return float(m.group()) if m else None

def get(url):
    try:
        r=urlopen(Request(url,headers={'accept':'application/json','user-agent':'daily-pre-market-analysis/1.4'}),timeout=45)
        return json.loads(r.read().decode('utf-8'))
    except Exception:return None

def rows(p):
    if isinstance(p,list):return p
    if not isinstance(p,dict):return []
    fields=p.get('fields') or p.get('fields8') or p.get('columns') or []
    data=p.get('data') or p.get('data8') or p.get('aaData') or p.get('records') or []
    if isinstance(fields,list) and isinstance(data,list):
        out=[]
        for row in data:
            if isinstance(row,dict):out.append(row)
            elif isinstance(row,list):out.append({str(fields[i]):v for i,v in enumerate(row) if i<len(fields)})
        if out:return out
    for k in ('data','aaData','results','result','records'):
        if isinstance(p.get(k),list):return p[k]
    return []

def norm(s):return re.sub(r'[^a-z0-9一-龥]','',str(s).lower())

def val(row,names):
    if not isinstance(row,dict):return None
    ns=[norm(x) for x in names]
    for k,v in row.items():
        if any(n and (n==norm(k) or n in norm(k)) for n in ns):
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
        text=' '.join(str(v) for v in r.values()) if isinstance(r,dict) else ' '.join(map(str,r))
        if '上漲' in text or '上升' in text:
            out['up']=out['up'] if out['up'] is not None else val(r,('上漲家數','上漲','上升','up'))
            out['limit_up']=out['limit_up'] if out['limit_up'] is not None else val(r,('漲停','limitup'))
        if '下跌' in text:
            out['down']=out['down'] if out['down'] is not None else val(r,('下跌家數','下跌','down'))
            out['limit_down']=out['limit_down'] if out['limit_down'] is not None else val(r,('跌停','limitdown'))
        if '持平' in text or '平盤' in text:
            out['unchanged']=out['unchanged'] if out['unchanged'] is not None else val(r,('持平家數','持平','平盤','unchanged'))
    return out

def amount(p):
    for r in rows(p):
        text=' '.join(str(v) for v in r.values()) if isinstance(r,dict) else ' '.join(map(str,r))
        if '總計' in text or '合計' in text:
            x=val(r,('成交金額','成交額','成交金額(元)','amount','turnover'))
            if x is not None:return x
    return find(p,('成交金額','成交額','成交金額(元)','amount','turnover'))

def add(a,b):return a+b if a is not None and b is not None else None

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--date',required=True);ap.add_argument('--output-root',default='data');a=ap.parse_args();d=a.date;date8=d.replace('-','');root=Path(a.output_root)
    tw=root/'twse'/f'{d}.json';base={}
    if tw.exists():
        try:base=json.loads(tw.read_text(encoding='utf-8'))
        except Exception:pass
    raw=base.get('data',base) if isinstance(base,dict) else {};t=raw.get('taiex',{});br=raw.get('advance_decline',{})
    t86,u86=fetch([rwd('fund/T86',date8,{'selectType':'ALL'})]);mi,umi=fetch([f'{TWSE_API}/exchangeReport/MI_MARGN?date={date8}']);sbl,usbl=fetch([f'{TWSE_API}/SBL/TWT96U?date={date8}']);listed,ul=fetch([f'{TWSE_API}/exchangeReport/FMTQIK?date={date8}'])
    oq,uo=fetch([f'{TPEX_API}/tpex_mainboard_quotes?date={date8}',f'{TPEX_API}/tpex_mainboard_quotes']);om,um=fetch([f'{TPEX_API}/tpex_mainboard_margin_balance?date={date8}',f'{TPEX_API}/tpex_mainboard_margin_balance']);osbl,uos=fetch([f'{TPEX_API}/tpex_margin_sbl?date={date8}',f'{TPEX_API}/tpex_margin_sbl']);oh,uh=fetch([f'{TPEX_API}/tpex_mainborad_highlight?date={date8}',f'{TPEX_API}/tpex_mainborad_highlight'])
    listed_total=amount(listed);otc_total=amount(oh)
    lb=breadth(br);ob=breadth(oq)
    data={'taiex':{'close':num(t.get('close')),'open':num(t.get('open')),'high':num(t.get('high')),'low':num(t.get('low')),'change_points':num(t.get('change',t.get('change_points'))),'change_percent':num(t.get('change_percent')),'turnover_value':listed_total},'listed_breadth':lb,'otc_breadth':ob,'institutional':{'unit':'shares','foreign':find(t86,('外陸資買賣超','外資及陸資買賣超','外資買賣超','foreign')),'investment_trust':find(t86,('投信買賣超','investmenttrust')),'dealer':find(t86,('自營商買賣超','dealer')),'total':find(t86,('三大法人買賣超合計','三大法人合計','合計買賣超'))},'margin':{'financing_balance':add(find(mi,('融資餘額','financingbalance')),find(om,('融資餘額','融資餘額(元)','financingbalance'))),'financing_change':add(find(mi,('融資增減','融資增減(元)','financingchange')),find(om,('融資增減','融資增減(元)','financingchange'))),'short_balance':add(find(mi,('融券餘額','shortbalance')),find(om,('融券餘額','融券餘額(張)','shortbalance'))),'short_change':add(find(mi,('融券增減','shortchange')),find(om,('融券增減','融券增減','shortchange'))),'maintenance_ratio':find(mi,('融資維持率','maintenanceratio'))},'sbl':{'balance':add(find(sbl,('借券餘額','balance')),find(osbl,('借券餘額','balance'))),'short_sale_balance':add(find(sbl,('借券賣出餘額','shortsalebalance')),find(osbl,('借券賣出餘額','借券賣出餘額','shortsalebalance'))),'short_sale_change':add(find(sbl,('借券賣出增減','shortsalechange')),find(osbl,('借券賣出增減','shortsalechange')))},'turnover':{'listed':listed_total,'otc':otc_total,'total':add(listed_total,otc_total)}}
    missing=[f'taiex.{k}' for k in ('close','change_points','change_percent') if data['taiex'][k] is None];unavailable=[f'{g}.{k}' for g,v in data.items() for k,x in v.items() if x is None]
    out={'ok':not missing and not unavailable,'source':'SPOT','date':d,'retrieved_at':datetime.now(timezone.utc).isoformat(),'timezone':'UTC','data':data,'sources':{'twse_snapshot':str(tw),'twse_t86':u86,'twse_margin':umi,'twse_sbl':usbl,'twse_turnover':ul,'tpex_breadth':uo,'tpex_margin':um,'tpex_sbl':uos,'tpex_turnover':uh},'missing_required':missing,'unavailable_fields':unavailable,'integrity_errors':[]}
    for p in (root/'snapshots'/d/'spot-snapshot.json',root/'spot'/f'{d}.json'):
        p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'date':d,'ok':out['ok'],'missing_required':missing,'unavailable_fields':unavailable,'integrity_errors':[]},ensure_ascii=False));return 0 if out['ok'] else 1

if __name__=='__main__':sys.exit(main())
