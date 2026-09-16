#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, re
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

TZ = ZoneInfo("Asia/Taipei")
MISSING = "資料未取得"

def num(v):
    if v is None: return None
    s = re.sub(r"<[^>]+>", "", str(v)).replace(",", "").replace("%", "").strip()
    if s in {"", "--", "---", "N/A", "null", "None", "－", "—"}: return None
    try: return float(s) if any(c in s for c in ".eE") else int(s)
    except ValueError: return None

def fmt(v):
    if v is None: return MISSING
    if isinstance(v, float): return f"{v:,.2f}".rstrip("0").rstrip(".")
    return f"{v:,}" if isinstance(v, int) else str(v)

def table(rows, headers):
    return "| " + " | ".join(headers) + " |\n|" + "|".join(["---"] * len(headers)) + "|\n" + "".join("| " + " | ".join(fmt(x) for x in row) + " |\n" for row in rows)

def load(root, date):
    path = root / f"data/spot/{date}.json"
    if not path.exists(): raise SystemExit(f"找不到現貨資料：{path}")
    return json.loads(path.read_text(encoding="utf-8"))

def generate(p, date):
    d = p.get("data", {})
    t = d.get("taiex", {}); lb = d.get("listed_breadth", {}); ob = d.get("otc_breadth", {})
    turnover = num(t.get("turnover_value")); turnover = turnover / 100000000 if turnover is not None else None
    rows = [("加權指數", t.get("close"), "點"), ("開盤", t.get("open"), "點"), ("最高", t.get("high"), "點"), ("最低", t.get("low"), "點"), ("收盤", t.get("close"), "點"), ("漲跌點數", t.get("change_points"), "點"), ("漲跌幅", t.get("change_percent"), "%"), ("成交金額", turnover, "億元")]
    breadth = [("上漲家數", "up"), ("下跌家數", "down"), ("平盤家數", "unchanged"), ("漲停家數", "limit_up"), ("跌停家數", "limit_down")]
    lines = [f"# DATA_REPORT_{date.replace('-', '')}", "", f"- 報告日期：`{date}`", f"- T0 交易日期：`{date}`", f"- 資料產出時間：`{datetime.now(TZ).strftime('%Y-%m-%d %H:%M:%S')}`", "- 時區：`Asia/Taipei`", "", "---", "", "## 一、現貨", "", "### 1. 台股大盤行情", "", "**資料來源：** `Cloudflare Worker：twse-proxy`", "", table(rows, ("項目", "數值", "單位")), "", "### 2. 市場漲跌家數", "", "#### 2.1 上市公司", "", "**資料來源：** `Cloudflare Worker：twse-proxy`", "", table([(n, lb.get(k)) for n,k in breadth], ("項目", "家數")), "", "#### 2.2 上櫃公司", "", "**資料來源：** `TPEX OpenAPI`", "", table([(n, ob.get(k)) for n,k in breadth], ("項目", "家數")), "", "### 3. 三大法人現貨買賣超", "", table([(n, MISSING, "億元") for n in ("外資", "投信", "自營商", "三大法人合計")], ("法人別", "買賣超金額", "單位")), "", "### 4. 融資融券", "", table([(n, MISSING, u) for n,u in (("融資餘額","億元"),("融資增減","億元"),("融券餘額","張"),("融券增減","張"),("融資維持率","%"))], ("項目", "數值", "單位")), "", "### 5. 借券資料", "", table([(n, MISSING, "張") for n in ("借券餘額","借券賣出餘額","借券賣出增減")], ("項目", "數值", "單位")), "", "### 6. 市場成交結構", "", table([(n, MISSING, "億元") for n in ("上市成交金額","上櫃成交金額","上市櫃成交金額合計")], ("項目", "數值", "單位")), "", "## 二、重要市場", "", "本階段暫不處理。", "", "## 三、資料完整性檢查", "", f"- 現貨資料來源檔案：`data/spot/{date}.json`", f"- 原始來源數：{len(p.get('sources', {}))}", "- 本報告僅整理資料，不提供交易判斷。", ""]
    return "\n".join(lines)

def main():
    a=argparse.ArgumentParser(); a.add_argument('--date', required=True); x=a.parse_args(); root=Path(__file__).resolve().parents[1]; out=root/f'reports/{x.date}.md'; out.parent.mkdir(exist_ok=True); out.write_text(generate(load(root,x.date),x.date),encoding='utf-8'); print(f'OK: {out}')
if __name__ == '__main__': main()
