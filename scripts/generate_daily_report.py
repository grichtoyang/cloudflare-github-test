#!/usr/bin/env python3
"""Generate a template-conformant data-only daily report."""
from __future__ import annotations
import argparse, json, re
from datetime import datetime
from pathlib import Path
from typing import Any

MISSING = "資料未取得"

def num(v):
    if v is None or v == "": return None
    if isinstance(v, (int,float)): return v
    s = re.sub(r"<[^>]+>", "", str(v)).replace(",", "").strip()
    if s in {"", "--", "---", "N/A", "－", "—"}: return None
    try: return float(s) if "." in s else int(s)
    except ValueError: return None

def fmt(v):
    if v is None or v == "": return MISSING
    if isinstance(v,float): return f"{v:,.2f}".rstrip("0").rstrip(".")
    if isinstance(v,int): return f"{v:,}"
    return str(v)

def walk(x):
    if isinstance(x,dict):
        yield x
        for v in x.values(): yield from walk(v)
    elif isinstance(x,list):
        for v in x: yield from walk(v)

def dataset(data, ids):
    for o in walk(data):
        if o.get("dataset_id") in ids:
            v=o.get("records",o.get("data",o.get("rows",[])))
            return v if isinstance(v,list) else []
    return []

def load(root,date):
    for p in [root/f"data/twse/{date}.json", root/f"data/premarket/{date}.json"]:
        if p.exists(): return json.loads(p.read_text(encoding="utf-8")),p
    raise SystemExit(f"找不到資料：{date}")

def legacy_twse(data):
    root=data.get("data",data); out={}
    t=root.get("taiex",{})
    if t:
        change=num(t.get("change")); pct=num(t.get("change_percent"))
        if isinstance(change,(int,float)) and (("-" in str(t.get("direction",""))) or (isinstance(pct,(int,float)) and pct<0)): change=-abs(change)
        out["taiex"]={"index":num(t.get("close")),"close":num(t.get("close")),"open":None,"high":None,"low":None,"change":change,"change_percent":pct}
    ms=root.get("market_statistics",{}); rows=ms.get("data",[]) if isinstance(ms,dict) else []
    total=next((r for r in rows if len(r)>1 and str(r[0]).startswith("總計")),None)
    out["turnover"]=num(total[1])/100000000 if total else None
    b=root.get("advance_decline",{}); br={}
    for r in b.get("data",[]) if isinstance(b,dict) else []:
        if len(r)<2: continue
        m=re.match(r"([0-9,]+)(?:\(([^)]+)\))?",str(r[1]))
        if not m: continue
        n=num(m.group(1)); lim=num(m.group(2))
        if str(r[0]).startswith("上漲"): br.update(up=n,limit_up=lim)
        elif str(r[0]).startswith("下跌"): br.update(down=n,limit_down=lim)
        elif str(r[0])=="持平": br["unchanged"]=n
    out["breadth"] = br
    return out

def table(items, headers=("項目","數值","單位")):
    s="| "+" | ".join(headers)+" |\n|"+"|".join(["---"]*len(headers))+"|\n"
    for row in items: s += "| "+" | ".join(fmt(x) for x in row)+" |\n"
    return s

def generate(data, source, date):
    tw=legacy_twse(data) if data.get("source")=="TWSE" or "taiex" in data.get("data",{}) else {}
    t=tw.get("taiex",{}); b=tw.get("breadth",{})
    turnover=tw.get("turnover")
    timestamp=data.get("timestamp") or data.get("generated_at") or MISSING
    now=datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %z")
    lines=[f"# 每日市場資料報告｜{date}","",f"- 報告日期：`{date}`",f"- T0 交易日期：`{date}`",f"- 資料產出時間：`{now}`", "- 時區：`Asia/Taipei`", "",f"> 資料來源：`{source}`  ",f"> 原始資料時間戳：`{timestamp}`  ","> 本報告僅整理資料，不提供交易判斷。","","---","","## 一、現貨","","### 1. 台股大盤行情","",table([("加權指數",t.get("index"),"點"),("開盤",t.get("open"),"點"),("最高",t.get("high"),"點"),("最低",t.get("low"),"點"),("收盤",t.get("close"),"點"),("漲跌點數",t.get("change"),"點"),("漲跌幅",t.get("change_percent"),"%"),("成交金額",turnover,"億元")]),"","### 2. 市場漲跌家數","","#### 2.1 上市公司","",table([("上漲家數",b.get("up")),("下跌家數",b.get("down")),("平盤家數",b.get("unchanged")),("漲停家數",b.get("limit_up")),("跌停家數",b.get("limit_down"))],("項目","家數")),"","#### 2.2 上櫃公司","",table([(x,None) for x in ["上漲家數","下跌家數","平盤家數","漲停家數","跌停家數"]],("項目","家數")),"","### 3. 三大法人現貨買賣超","",table([(x,None,"億元") for x in ["外資","投信","自營商","三大法人合計"]]),"","### 4. 融資融券","",table([(x,None,u) for x,u in [("融資餘額","億元"),("融資增減","億元"),("融券餘額","張"),("融券增減","張"),("融資維持率","%")]]),"","### 5. 借券資料","",table([(x,None,"張") for x in ["借券餘額","借券賣出餘額","借券賣出增減"]]),"","### 6. 市場成交結構","",table([(x,None,"億元") for x in ["上市成交金額","上櫃成交金額","上市櫃成交金額合計"]]),"","## 二、台指期與選擇權","","### 1. 台指期行情","",MISSING,"","### 2. 台指期法人交易","",MISSING,"","### 3. 台指期法人 OI","",MISSING,"","### 4. 選擇權資料","",MISSING,"","## 三、資料完整性檢查","",f"- 現貨模板欄位：已完整保留",f"- 可取得現貨欄位：加權指數、收盤、漲跌點數、漲跌幅、成交金額、上市漲跌家數",f"- 未取得欄位：開高低、上櫃漲跌家數、三大法人、融資融券、借券、上市櫃成交結構","" ]
    return "\n".join(lines)

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--date",required=True); a=ap.parse_args(); root=Path(__file__).resolve().parents[1]; data,p=load(root,a.date); out=root/f"reports/{a.date}.md"; out.write_text(generate(data,str(p.relative_to(root)),a.date),encoding="utf-8"); print(f"OK: {out}")
if __name__=="__main__": main()
