#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,re,sys,time
from datetime import datetime,timezone
from pathlib import Path
from urllib.request import Request,urlopen

TWSE_PROXY='https://twse-proxy.grichtoyang.workers.dev'
TWSE='https://openapi.twse.com.tw/v1'
TPEX='https://www.tpex.org.tw/openapi/v1'

def fetch(url,retries=3):
    last=None
    for i in range(retries):
        try:
            r=Request(url,headers={'accept':'application/json','user-agent':'daily-pre-market-analysis/2.2'})
            with urlopen(r,timeout=60) as x:return json.loads(x.read().decode()),x.status
        except Exception as e:
            last=e
            if i<retries-1: time.sleep(2**i)
    raise last

def n(v):
    if v is None:return None
    s=re.sub(r'<[^>]+>','',str(v)).replace(',','').replace('%','').strip()
    if s in ('','--','---','－','—','N/A','null','None'):return None
    try:return float(s)
    except:return None

def rows(x):
    if isinstance(x,list):return x
    if isinstance(x,dict):
        for k in ('data','data1','data8','aaData','result'):
            if isinstance(x.get(k),list):return x[k]
    return []

def val(row,names):
    if not isinstance(row,dict):return None
    for k in names:
        if k in row:return n(row[k])
    return None

def aggregate_breadth(rs):
    up=down=unchanged=limit_up=limit_down=0
    seen=False
    for r in rs:
        change=val(r,['漲跌','漲跌價差','change','Change'])
        pct=val(r,['漲跌幅','漲跌百分比','change_percent','ChangePercent'])
        if change is None and pct is None: continue
        seen=True
        if pct is not None and pct>=9.5: limit_up+=1
        if pct is not None and pct<=-9.5: limit_down+=1
        if change is not None:
            if change>0: up+=1
            elif change<0: down+=1
            else: unchanged+=1
        elif pct is not None:
            if pct>0: up+=1
            elif pct<0: down+=1
            else: unchanged+=1
    return {'up':up,'down':down,'unchanged':unchanged,'limit_up':limit_up,'limit_down':limit_down} if seen else {}

def aggregate_sum(rs,names):
    vals=[val(r,names) for r in rs]
    vals=[x for x in vals if x is not None]
    return sum(vals) if vals else None

def main():
    p=argparse.ArgumentParser();p.add_argument('--date',required=True);p.add_argument('--output-root',default='data');a=p.parse_args();d8=a.date.replace('-','');src={}
    def get(name,url):
        try:
            x,s=fetch(url);src[name]={'url':url,'status':s,'ok':True};return x
        except Exception as e:
            src[name]={'url':url,'status':None,'ok':False,'error':str(e)};return None
    proxy=get('twse_proxy',f'{TWSE_PROXY}?date={d8}') or {}
    pd=proxy.get('data',{}) if isinstance(proxy,dict) else {};ta=pd.get('taiex') or {};st=pd.get('market_statistics') or {};br=pd.get('advance_decline') or {}
    inst=rows(get('twse_institutional',f'{TWSE}/fund/T86?date={d8}&selectType=ALL'))
    mar=rows(get('twse_margin',f'{TWSE}/exchangeReport/MI_MARGN?response=json&date={d8}'))
    sbl=rows(get('twse_sbl',f'{TWSE}/SBL/TWT96U?response=json&date={d8}'))
    fmt=rows(get('twse_turnover',f'{TWSE}/exchangeReport/FMTQIK?response=json&date={d8}'))
    oq=rows(get('tpex_quotes',f'{TPEX}/tpex_mainboard_daily_close_quotes'))
    om=rows(get('tpex_margin',f'{TPEX}/tpex_mainboard_margin_balance'))
    os=rows(get('tpex_sbl',f'{TPEX}/tpex_margin_sbl'))
    ot=rows(get('tpex_turnover',f'{TPEX}/tpex_mainboard_highlight'))
    i=next((r for r in inst if isinstance(r,dict) and any(k in r for k in ['外陸資買賣超股數(不含外資自營商)','外資買賣超金額(元)','外陸資買賣超金額(元)'])),{})
    m=mar[0] if mar else {};s=sbl[0] if sbl else {};f=fmt[0] if fmt else {}
    foreign=val(i,['外陸資買賣超股數(不含外資自營商)','外資買賣超金額(元)','外陸資買賣超金額(元)']);trust=val(i,['投信買賣超股數','投信買賣超金額(元)']);dealer=val(i,['自營商買賣超股數','自營商買賣超金額(元)'])
    listed=aggregate_breadth(rows(pd.get('listed_breadth'))) or aggregate_breadth(rows(pd.get('market_statistics')))
    otc=aggregate_breadth(oq)
    data={'taiex':{k:val(ta,v) for k,v in {'close':['close','收盤指數','收盤'],'open':['open','開盤指數','開盤'],'high':['high','最高指數','最高'],'low':['low','最低指數','最低'],'change_points':['change_points','漲跌點數','change'],'change_percent':['change_percent','漲跌百分比','change_pct']}.items()},'listed_breadth':listed,'otc_breadth':otc,'institutional':{'foreign':foreign,'investment_trust':trust,'dealer':dealer,'total':foreign+trust+dealer if None not in (foreign,trust,dealer) else None},'margin':{k:val(m,v) for k,v in {'financing_balance':['融資餘額(元)','融資餘額'],'financing_change':['融資增減(元)','融資增減'],'short_balance':['融券餘額(張)','融券餘額'],'short_change':['融券增減(張)','融券增減'],'maintenance_ratio':['融資維持率(%)','融資維持率']}.items()},'sbl':{k:val(s,v) for k,v in {'balance':['借券餘額','借券餘額(張)'],'short_sale_balance':['借券賣出餘額','借券賣出餘額(張)'],'short_sale_change':['借券賣出增減','借券賣出增減(張)']}.items()},'turnover':{'listed':val(f,['成交金額(元)','成交金額']),'otc':aggregate_sum(ot,['成交金額','成交金額(元)','成交額']),'total':None}}
    data['taiex']['turnover_value']=val(st,['turnover_value','成交金額(元)','成交金額','turnover'])
    if data['turnover']['listed'] is not None and data['turnover']['otc'] is not None:data['turnover']['total']=data['turnover']['listed']+data['turnover']['otc']
    req={"taiex":['close','open','high','low','change_points','change_percent','turnover_value'],"listed_breadth":['up','down','unchanged','limit_up','limit_down'],"otc_breadth":['up','down','unchanged','limit_up','limit_down'],"institutional":['foreign','investment_trust','dealer','total'],"margin":['financing_balance','financing_change','short_balance','short_change','maintenance_ratio'],"sbl":['balance','short_sale_balance','short_sale_change'],"turnover":['listed','otc','total']}
    missing=[f'{g}.{k}' for g,ks in req.items() for k in ks if data.get(g,{}).get(k) is None]
    out={'ok':not missing,'source':'SPOT','date':a.date,'retrieved_at':datetime.now(timezone.utc).isoformat(),'timezone':'UTC','data':data,'sources':src,'missing_required':missing}
    for path in (Path(a.output_root)/'snapshots'/a.date/'spot-snapshot.json',Path(a.output_root)/'spot'/f'{a.date}.json'):
        path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'date':a.date,'ok':out['ok'],'missing_required':missing},ensure_ascii=False));return 0 if out['ok'] else 1
if __name__=='__main__':sys.exit(main())
