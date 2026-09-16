#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, re, sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

TWSE_PROXY = "https://twse-proxy.grichtoyang.workers.dev"
TPEX_BASE = "https://www.tpex.org.tw/openapi/v1"

def fetch(url, timeout=30):
    req = Request(url, headers={"accept":"application/json","user-agent":"daily-pre-market-analysis/1.0"})
    with urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8")), r.status

def num(v):
    if v is None: return None
    s = re.sub(r"<[^>]+>", "", str(v)).replace(",", "").replace("%", "").strip()
    if s in {"", "--", "---", "－", "—", "N/A", "null", "None"}: return None
    try: return float(s) if any(c in s for c in ".eE") else int(s)
    except ValueError: return None

def find(obj, aliases):
    if isinstance(obj, dict):
        for k,v in obj.items():
            if str(k).strip() in aliases:
                n=num(v)
                if n is not None: return n
        for v in obj.values():
            n=find(v, aliases)
            if n is not None: return n
    elif isinstance(obj,list):
        for v in obj:
            n=find(v, aliases)
            if n is not None: return n
    return None

def collect(date):
    sources={}
    def get(name,url):
        try:
            payload,status=fetch(url); sources[name]={"url":url,"status":status,"ok":True}; return payload
        except Exception as e:
            sources[name]={"url":url,"status":None,"ok":False,"error":str(e)}; return None
    twse=get("twse_proxy",f"{TWSE_PROXY}?date={date.replace('-','')}")
    tpex={n:get(n,u) for n,u in {
      "tpex_breadth":f"{TPEX_BASE}/tpex_mainboard_daily_close_quotes",
      "tpex_margin":f"{TPEX_BASE}/tpex_mainboard_margin_balance",
      "tpex_sbl":f"{TPEX_BASE}/tpex_margin_sbl",
      "tpex_turnover":f"{TPEX_BASE}/tpex_mainboard_highlight"}.items()}
    d=twse.get("data",{}) if isinstance(twse,dict) else {}
    taiex=d.get("taiex") or {}; stats=d.get("market_statistics") or {}; breadth=d.get("advance_decline") or {}
    spot={
      "taiex":{k:find(taiex,a) for k,a in {
        "close":{"close","收盤指數","收盤"},"open":{"open","開盤指數","開盤"},"high":{"high","最高指數","最高"},"low":{"low","最低指數","最低"},"change_points":{"change_points","漲跌點數","change"},"change_percent":{"change_percent","漲跌百分比","change_pct"}}.items()},
      "listed_breadth":{k:find(breadth,a) for k,a in {"up":{"up","advance","上漲家數"},"down":{"down","decline","下跌家數"},"unchanged":{"unchanged","持平","平盤家數"},"limit_up":{"limit_up","漲停家數"},"limit_down":{"limit_down","跌停家數"}}.items()},
      "otc_breadth":{k:find(tpex["tpex_breadth"],a) for k,a in {"up":{"上漲家數","上漲","up"},"down":{"下跌家數","下跌","down"},"unchanged":{"平盤家數","平盤","unchanged"},"limit_up":{"漲停家數","漲停","limit_up"},"limit_down":{"跌停家數","跌停","limit_down"}}.items()},
      "institutional":{k:find(twse,a) for k,a in {"foreign":{"外資買賣超","外資及陸資買賣超","foreign"},"investment_trust":{"投信買賣超","投信","investment_trust"},"dealer":{"自營商買賣超","自營商","dealer"},"total":{"三大法人買賣超","合計","total"}}.items()},
      "margin":{k:find({"twse":twse,"tpex":tpex["tpex_margin"]},a) for k,a in {"financing_balance":{"融資餘額","融資金額"},"financing_change":{"融資增減","融資增減金額"},"short_balance":{"融券餘額","融券張數"},"short_change":{"融券增減","融券增減張數"},"maintenance_ratio":{"融資維持率"}}.items()},
      "sbl":{k:find({"twse":twse,"tpex":tpex["tpex_sbl"]},a) for k,a in {"balance":{"借券餘額"},"short_balance":{"借券賣出餘額"},"short_change":{"借券賣出增減"}}.items()},
      "turnover":{k:find({"twse":twse,"tpex":tpex["tpex_turnover"]},a) for k,a in {"listed":{"上市成交金額"},"otc":{"上櫃成交金額"},"total":{"上市櫃成交金額合計"}}.items()}}
    spot["taiex"]["turnover_value"]=find(stats,{"turnover_value","成交金額(元)","成交金額","turnover"})
    required=[]
    for group,keys in {"taiex":["close","open","high","low","change_points","change_percent","turnover_value"],"listed_breadth":["up","down","unchanged","limit_up","limit_down"],"otc_breadth":["up","down","unchanged","limit_up","limit_down"],"institutional":["foreign","investment_trust","dealer","total"],"margin":["financing_balance","financing_change","short_balance","short_change","maintenance_ratio"],"sbl":["balance","short_balance","short_change"],"turnover":["listed","otc","total"]}.items():
        required += [f"{group}.{k}" for k in keys]
    missing=[p for p in required if spot[p.split('.')[0]].get(p.split('.')[1]) is None]
    return {"ok":not missing,"source":"SPOT","date":date,"retrieved_at":datetime.now(timezone.utc).isoformat(),"timezone":"UTC","data":spot,"sources":sources,"missing_required":missing}

def main():
    p=argparse.ArgumentParser(); p.add_argument('--date',required=True); p.add_argument('--output-root',default='data'); a=p.parse_args(); payload=collect(a.date)
    for path in [Path(a.output_root)/'snapshots'/a.date/'spot-snapshot.json',Path(a.output_root)/'spot'/f'{a.date}.json']:
        path.parent.mkdir(parents=True,exist_ok=True); path.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'date':a.date,'ok':payload['ok'],'missing_required':payload['missing_required']},ensure_ascii=False)); return 0 if payload['ok'] else 1
if __name__=='__main__': sys.exit(main())
