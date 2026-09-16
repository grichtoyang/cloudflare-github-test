#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,re,sys,time
from datetime import datetime,timezone
from pathlib import Path
from urllib.request import Request,urlopen
from urllib.parse import urlencode

PROXY='https://twse-proxy.grichtoyang.workers.dev'
OPENAPI='https://openapi.twse.com.tw/v1'
WEB='https://www.twse.com.tw/exchangeReport'
TPEX='https://www.tpex.org.tw/openapi/v1'

def get(url,retries=3):
    for i in range(retries):
        try:
            req=Request(url,headers={'accept':'application/json','user-agent':'daily-pre-market-analysis/3.1'})
            with urlopen(req,timeout=60) as r:return json.loads(r.read().decode()),r.status
        except Exception:
            if i==retries-1:return None,None
            time.sleep(2**i)

def rows(x):
    if isinstance(x,list): return x
    if not isinstance(x,dict): return []
    for k in ('data','data1','data2','data3','data4','data5','data6','data7','data8','aaData','result','records','items'):
        if isinstance(x.get(k),list): return x[k]
    return []

def normalized_rows(x):
    if not isinstance(x,dict): return rows(x)
    data=rows(x); headers=None
    for k in ('fields','fields1','fields2','fields8','columns','headers','title'):
        if isinstance(x.get(k),list) and x[k] and all(isinstance(v,str) for v in x[k]): headers=x[k]; break
    if headers and data and isinstance(data[0],list): return [dict(zip(headers,r)) for r in data]
    return data

def num(x):
    try:
        s=re.sub(r'<[^>]+>','',str(x)).replace(',','').replace('%','').replace('－','-').replace('—','-').strip()
        return None if s in ('','--','---','N/A','null','None') else float(s)
    except Exception:return None

def val(r,keys):
    if not isinstance(r,dict): return None
    for k in keys:
        if k in r:
            n=num(r[k])
            if n is not None:return n
    return None

def findval(rs,keys):
    for r in rs:
        n=val(r,keys)
        if n is not None:return n
    return None

def breadth(rs):
    z={'up':0,'down':0,'unchanged':0,'limit_up':0,'limit_down':0}; seen=False
    for r in rs:
        c=val(r,['漲跌','漲跌價差','漲跌點數','change','Change']); p=val(r,['漲跌幅','漲跌百分比','change_percent','ChangePercent'])
        if c is None and p is None: continue
        seen=True; d=c if c is not None else p
        z['up' if d>0 else 'down' if d<0 else 'unchanged']+=1
        if p is not None and p>=9.5:z['limit_up']+=1
        if p is not None and p<=-9.5:z['limit_down']+=1
    return z if seen else {}

def totalrow(rs):
    for r in rs:
        if isinstance(r,dict) and any(t in ' '.join(map(str,r.values())) for t in ('合計','總計','Total','TOTAL')): return r
    return rs[0] if len(rs)==1 and isinstance(rs[0],dict) else {}

def main():
    p=argparse.ArgumentParser();p.add_argument('--date',required=True);p.add_argument('--output-root',default='data');a=p.parse_args();d=a.date;d8=d.replace('-','');src={}
    def pull(n,u):
        x,s=get(u);src[n]={'url':u,'status':s,'ok':s==200};return x if s==200 else None
    q=urlencode({'response':'json','date':d8,'type':'IND'})
    idx=pull('twse_openapi_index',f'{OPENAPI}/exchangeReport/MI_INDEX?{q}')
    if not normalized_rows(idx): idx=pull('twse_web_index',f'{WEB}/MI_INDEX?{q}')
    proxy=pull('twse_proxy',f'{PROXY}?date={d8}') or {};pd=proxy.get('data',{}) if isinstance(proxy,dict) else {}
    ta=pd.get('taiex',{}) if isinstance(pd,dict) else {};st=pd.get('market_statistics',{}) if isinstance(pd,dict) else {}
    inst=pull('twse_openapi_institutional',f'{OPENAPI}/fund/T86?date={d8}&selectType=ALL')
    margin=pull('twse_openapi_margin',f'{OPENAPI}/exchangeReport/MI_MARGN?response=json&date={d8}')
    sbl=pull('twse_openapi_sbl',f'{OPENAPI}/SBL/TWT96U?response=json&date={d8}')
    turn=pull('twse_openapi_turnover',f'{OPENAPI}/exchangeReport/FMTQIK?response=json&date={d8}')
    otc=pull('tpex_openapi_quotes',f'{TPEX}/tpex_mainboard_daily_close_quotes')
    otct=pull('tpex_openapi_highlight',f'{TPEX}/tpex_mainboard_highlight')
    ir=next((r for r in normalized_rows(inst) if isinstance(r,dict) and any('投信買賣超' in str(k) for k in r)),{})
    mr=totalrow(normalized_rows(margin)); sr=totalrow(normalized_rows(sbl)); tr=totalrow(normalized_rows(turn))
    ix=next((r for r in normalized_rows(idx) if isinstance(r,dict) and any(k in r for k in ('收盤指數','收盤','Close'))),{})
    def first(keys,primary,fallback):
        n=val(primary,keys); return n if n is not None else val(fallback,keys)
    foreign=val(ir,['外陸資買賣超股數(不含外資自營商)','外資及陸資買賣超股數','外資買賣超股數'])
    trust=val(ir,['投信買賣超股數','投信買賣超股數(股)']); dealer=val(ir,['自營商買賣超股數','自營商買賣超股數(股)'])
    lt=val(tr,['成交金額(元)','成交金額','成交額']) or val(st,['turnover_value','成交金額(元)','成交金額','turnover'])
    ot=sum(v for v in (val(r,['成交金額','成交金額(元)','成交額']) for r in normalized_rows(otct)) if v is not None) or val(st,['otc_turnover','櫃買成交金額'])
    listed=breadth(normalized_rows(pd.get('listed_breadth'))) or breadth(normalized_rows(pd.get('market_breadth')))
    otcb=breadth(normalized_rows(otc)) or breadth(normalized_rows(pd.get('otc_breadth')))
    data={'taiex':{'close':first(['收盤指數','收盤','Close','close'],ix,ta),'open':first(['開盤指數','開盤','Open','open'],ix,ta),'high':first(['最高指數','最高','High','high'],ix,ta),'low':first(['最低指數','最低','Low','low'],ix,ta),'change_points':first(['漲跌點數','漲跌','Change','change_points'],ix,ta),'change_percent':first(['漲跌百分比','漲跌幅','ChangePercent','change_percent'],ix,ta),'turnover_value':lt},'listed_breadth':listed,'otc_breadth':otcb,'institutional':{'unit':'shares','foreign':foreign,'investment_trust':trust,'dealer':dealer,'total':foreign+trust+dealer if None not in (foreign,trust,dealer) else None},'margin':{'financing_balance':val(mr,['融資餘額(元)','融資餘額']),'financing_change':val(mr,['融資增減(元)','融資增減']),'short_balance':val(mr,['融券餘額(張)','融券餘額']),'short_change':val(mr,['融券增減(張)','融券增減']),'maintenance_ratio':val(mr,['融資維持率(%)','融資維持率'])},'sbl':{'balance':val(sr,['借券餘額','借券餘額(張)']),'short_sale_balance':val(sr,['借券賣出餘額','借券賣出餘額(張)']),'short_sale_change':val(sr,['借券賣出增減','借券賣出增減(張)'])},'turnover':{'listed':lt,'otc':ot,'total':lt+ot if None not in (lt,ot) else None}}
    req={'taiex':['close','open','high','low','change_points','change_percent'],'listed_breadth':['up','down','unchanged','limit_up','limit_down'],'otc_breadth':['up','down','unchanged','limit_up','limit_down'],'institutional':['foreign','investment_trust','dealer','total'],'margin':['financing_balance','financing_change','short_balance','short_change','maintenance_ratio'],'sbl':['balance','short_sale_balance','short_sale_change'],'turnover':['listed','otc','total']}
    missing=[f'{g}.{k}' for g,ks in req.items() for k in ks if data[g].get(k) is None]; errors=[]
    if not normalized_rows(idx) and not pd: errors.append('twse_core_sources.empty')
    if not normalized_rows(otc) and not normalized_rows(pd.get('otc_breadth')): errors.append('tpex_quotes.empty')
    out={'ok':not missing and not errors,'source':'SPOT','date':d,'retrieved_at':datetime.now(timezone.utc).isoformat(),'timezone':'UTC','data':data,'sources':src,'missing_required':missing,'integrity_errors':errors}
    for q in (Path(a.output_root)/'snapshots'/d/'spot-snapshot.json',Path(a.output_root)/'spot'/f'{d}.json'):
        q.parent.mkdir(parents=True,exist_ok=True);q.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'date':d,'ok':out['ok'],'missing_required':missing,'integrity_errors':errors},ensure_ascii=False));return 0 if out['ok'] else 1
if __name__=='__main__':sys.exit(main())
