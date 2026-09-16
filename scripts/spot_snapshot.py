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
    p=root/'raw'/f'{name}_{date}.json'
    if not p.exists():return None
    try:
        x=json.loads(p.read_text(encoding='utf-8'))
        return x.get('payload') if isinstance(x,dict) else x
    except Exception:return None

def rows(x):
    if isinstance(x,list):return x
    if isinstance(x,dict):
        fields=x.get('fields') or x.get('columns') or []
        data=x.get('data') or x.get('records') or x.get('aaData') or []
        if fields and data:
            return [{str(fields[i]):v for i,v in enumerate(r) if i<len(fields)} if isinstance(r,list) else r for r in data]
        return data if isinstance(data,list) else []
    return []

def find_row(x,predicate):
    return next((r for r in rows(x) if isinstance(r,dict) and predicate(r)),None)

def field(r,*names):
    if not isinstance(r,dict):return None
    for n in names:
        if n in r:return num(r[n])
    for k,v in r.items():
        nk=re.sub(r'[^a-z0-9一-龥]','',str(k).lower())
        if any(re.sub(r'[^a-z0-9一-龥]','',str(n).lower()) in nk for n in names):
            x=num(v)
            if x is not None:return x
    return None

def total_field(x,*names):
    for r in rows(x):
        v=field(r,*names)
        if v is not None:return v
    return None

def add(a,b):return a+b if a is not None and b is not None else (a if b is None else b)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--date',required=True);ap.add_argument('--output-root',default='data');a=ap.parse_args();d=a.date;root=Path(a.output_root)
    mi=load(root,'twse_mi_index',d);bread=load(root,'twse_listed_breadth',d);t86=load(root,'twse_t86',d);margin=load(root,'twse_margin',d);sbl=load(root,'twse_sbl',d);turn=load(root,'twse_turnover',d)
    oq=load(root,'tpex_quotes',d);om=load(root,'tpex_margin',d);os=load(root,'tpex_sbl',d);oh=load(root,'tpex_highlight',d)
    idx=find_row(mi,lambda r:'發行量加權股價指數'==r.get('指數')) or {}
    listed=find_row(bread,lambda r:True) or {}
    otc=find_row(oh,lambda r:True) or {}
    tr=find_row(turn,lambda r:r.get('Date','').endswith(d.replace('-','')[4:])) or (rows(turn)[-1] if rows(turn) else {})
    inst=rows(t86)
    institutional_total=sum(field(r,'三大法人買賣超股數') or 0 for r in inst) if inst else None
    data={
      'taiex':{'close':field(idx,'收盤指數'),'open':None,'high':None,'low':None,'change_points':field(idx,'漲跌點數'),'change_percent':field(idx,'漲跌百分比'),'turnover_value':field(tr,'TradeValue','成交金額')},
      'listed_breadth':{'up':field(listed,'上漲家數','PriceRiseCompanyNumbers','上漲'),'down':field(listed,'下跌家數','PriceDeclineCompanyNumbers','下跌'),'unchanged':field(listed,'持平家數','PriceFlatCompanyNumbers','持平'),'limit_up':field(listed,'漲停家數','LimitUpCompanyNumbers','漲停'),'limit_down':field(listed,'跌停家數','LimitDownCompanyNumbers','跌停')},
      'otc_breadth':{'up':field(otc,'PriceRiseCompanyNumbers','上漲家數'),'down':field(otc,'PriceDeclineCompanyNumbers','下跌家數'),'unchanged':field(otc,'PriceFlatCompanyNumbers','持平家數'),'limit_up':field(otc,'LimitUpCompanyNumbers','漲停家數'),'limit_down':field(otc,'LimitDownCompanyNumbers','跌停家數')},
      'institutional':{'unit':'shares','foreign':sum(field(r,'外陸資買賣超股數(不含外資自營商)') or 0 for r in inst) if inst else None,'investment_trust':sum(field(r,'投信買賣超股數') or 0 for r in inst) if inst else None,'dealer':sum(field(r,'自營商買賣超股數') or 0 for r in inst) if inst else None,'total':institutional_total},
      'margin':{'financing_balance':add(total_field(margin,'融資今日餘額'),total_field(om,'MarginPurchaseBalance')),'financing_change':add(total_field(margin,'融資今日餘額')-total_field(margin,'融資前日餘額') if total_field(margin,'融資今日餘額') is not None and total_field(margin,'融資前日餘額') is not None else None,total_field(om,'MarginPurchase')),'short_balance':add(total_field(margin,'融券今日餘額'),total_field(om,'ShortSaleBalance')),'short_change':add(total_field(margin,'融券今日餘額')-total_field(margin,'融券前日餘額') if total_field(margin,'融券今日餘額') is not None and total_field(margin,'融券前日餘額') is not None else None,total_field(om,'ShortSale')),'maintenance_ratio':None},
      'sbl':{'balance':total_field(os,'SecuritiesBorrowingBalanceOfTheMarketDay','借券餘額'),'short_sale_balance':total_field(sbl,'借券賣出餘額','SaleBalanceOfTheMarketDay'),'short_sale_change':total_field(sbl,'借券賣出增減')},
      'turnover':{'listed':field(tr,'TradeValue'),'otc':field(otc,'DailyTradingValue'),'total':add(field(tr,'TradeValue'),field(otc,'DailyTradingValue'))}
    }
    # OHLC and maintenance ratio are not supplied by the collected official endpoints; keep them explicit but optional.
    optional={'taiex.open','taiex.high','taiex.low','margin.maintenance_ratio','sbl.balance','sbl.short_sale_balance','sbl.short_sale_change'}
    unavailable=[f'{g}.{k}' for g,v in data.items() for k,x in v.items() if x is None and f'{g}.{k}' not in optional and k!='unit']
    out={'ok':not unavailable,'source':'SPOT','date':d,'retrieved_at':datetime.now(timezone.utc).isoformat(),'timezone':'UTC','data':data,'missing_required':[],'unavailable_fields':unavailable,'integrity_errors':[]}
    for p in (root/'snapshots'/d/'spot-snapshot.json',root/'spot'/f'{d}.json'):
        p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'date':d,'ok':out['ok'],'missing_required':[],'unavailable_fields':unavailable,'integrity_errors':[]},ensure_ascii=False));return 0 if out['ok'] else 1
if __name__=='__main__':sys.exit(main())
