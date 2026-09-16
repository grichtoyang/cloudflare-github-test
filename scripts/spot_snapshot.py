#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,os,re,sys,time
from datetime import datetime,timezone
from pathlib import Path
from urllib.request import Request,urlopen

PROXY=os.getenv('TWSE_PROXY_BASE_URL','https://twse-proxy.grichtoyang.workers.dev')

def get(url):
    try:
        r=urlopen(Request(url,headers={'accept':'application/json','user-agent':'daily-pre-market-analysis/1.0'}),timeout=45)
        return json.loads(r.read().decode()),r.status
    except Exception:return None,None

def num(v):
    try:
        s=str(v).replace(',','').replace('%','').replace('－','-').replace('—','-').strip()
        if s in ('','--','---','null','None','N/A'):return None
        return float(s)
    except Exception:return None

def walk(x):
    if isinstance(x,dict):
        yield x
        for v in x.values():yield from walk(v)
    elif isinstance(x,list):
        for v in x:yield from walk(v)

def find(x,names):
    names={n.lower() for n in names}
    for d in walk(x):
        for k,v in d.items():
            if str(k).lower() in names:
                n=num(v)
                if n is not None:return n
    return None

def section(x,names):
    names={n.lower() for n in names}
    for d in walk(x):
        for k,v in d.items():
            if str(k).lower() in names and isinstance(v,dict):return v
    return {}

def main():
    p=argparse.ArgumentParser();p.add_argument('--date',required=True);p.add_argument('--output-root',default='data');a=p.parse_args();d=a.date
    root=Path(a.output_root); tw=root/'twse'/f'{d}.json'
    base={}
    if tw.exists():
        try:base=json.loads(tw.read_text(encoding='utf-8'))
        except Exception:base={}
    if not base:
        base,_=get(PROXY.rstrip('/')+'?date='+d.replace('-',''))
    data0=base.get('data',base) if isinstance(base,dict) else {}
    ta=section(data0,['taiex','index','taiEx']) or data0
    ms=section(data0,['market_statistics','marketStatistics','成交統計']) or data0
    br=section(data0,['advance_decline','breadth','market_breadth','上市漲跌家數']) or data0
    inst=section(data0,['institutional','三大法人']) or data0
    mar=section(data0,['margin','融資融券']) or data0
    sbl=section(data0,['sbl','借券']) or data0
    turn=section(data0,['turnover','成交金額']) or data0
    def f(sec,keys):return find(sec,keys) if sec else find(data0,keys)
    foreign=f(inst,['foreign','外資買賣超','外陸資買賣超股數','外資'])
    trust=f(inst,['investment_trust','投信買賣超','投信'])
    dealer=f(inst,['dealer','自營商買賣超','自營商'])
    lt=f(turn,['listed','上市成交金額','上市市場成交金額','成交金額(元)'])
    ot=f(turn,['otc','櫃買成交金額','上櫃成交金額'])
    data={'taiex':{'close':f(ta,['close','收盤指數','收盤']),'open':f(ta,['open','開盤指數','開盤']),'high':f(ta,['high','最高指數','最高']),'low':f(ta,['low','最低指數','最低']),'change_points':f(ta,['change_points','漲跌點數','漲跌']),'change_percent':f(ta,['change_percent','漲跌百分比','漲跌幅'])},'listed_breadth':{'up':f(br,['listed_up','up','上漲家數']),'down':f(br,['listed_down','down','下跌家數']),'unchanged':f(br,['listed_unchanged','unchanged','持平家數']),'limit_up':f(br,['listed_limit_up','limit_up','漲停家數']),'limit_down':f(br,['listed_limit_down','limit_down','跌停家數'])},'otc_breadth':{'up':f(data0,['otc_up','櫃買上漲家數']),'down':f(data0,['otc_down','櫃買下跌家數']),'unchanged':f(data0,['otc_unchanged','櫃買持平家數']),'limit_up':f(data0,['otc_limit_up','櫃買漲停家數']),'limit_down':f(data0,['otc_limit_down','櫃買跌停家數'])},'institutional':{'unit':'shares','foreign':foreign,'investment_trust':trust,'dealer':dealer,'total':foreign+trust+dealer if None not in (foreign,trust,dealer) else None},'margin':{'financing_balance':f(mar,['financing_balance','融資餘額']),'financing_change':f(mar,['financing_change','融資增減']),'short_balance':f(mar,['short_balance','融券餘額']),'short_change':f(mar,['short_change','融券增減']),'maintenance_ratio':f(mar,['maintenance_ratio','融資維持率'])},'sbl':{'balance':f(sbl,['balance','借券餘額']),'short_sale_balance':f(sbl,['short_sale_balance','借券賣出餘額']),'short_sale_change':f(sbl,['short_sale_change','借券賣出增減'])},'turnover':{'listed':lt,'otc':ot,'total':lt+ot if None not in (lt,ot) else None}}
    req={'taiex':['close','open','high','low','change_points','change_percent'],'listed_breadth':['up','down','unchanged','limit_up','limit_down'],'otc_breadth':['up','down','unchanged','limit_up','limit_down'],'institutional':['foreign','investment_trust','dealer','total'],'margin':['financing_balance','financing_change','short_balance','short_change','maintenance_ratio'],'sbl':['balance','short_sale_balance','short_sale_change'],'turnover':['listed','otc','total']}
    missing=[f'{g}.{k}' for g,ks in req.items() for k in ks if data[g].get(k) is None]
    out={'ok':not missing,'source':'SPOT','date':d,'retrieved_at':datetime.now(timezone.utc).isoformat(),'timezone':'UTC','data':data,'sources':{'twse_snapshot':str(tw)},'missing_required':missing,'integrity_errors':[]}
    for q in (root/'snapshots'/d/'spot-snapshot.json',root/'spot'/f'{d}.json'):
        q.parent.mkdir(parents=True,exist_ok=True);q.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'date':d,'ok':out['ok'],'missing_required':missing,'integrity_errors':[]},ensure_ascii=False));return 0 if out['ok'] else 1
if __name__=='__main__':sys.exit(main())
