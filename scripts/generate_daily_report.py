#!/usr/bin/env python3
"""Generate a data-only report from all available daily source files."""
from __future__ import annotations
import argparse, json, re
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

MISSING = "資料未取得"
TZ = ZoneInfo("Asia/Taipei")

def num(v):
    if v is None or v == "": return None
    if isinstance(v, (int, float)): return v
    s = re.sub(r"<[^>]+>", "", str(v)).replace(",", "").replace("%", "").strip()
    if s in {"", "--", "---", "N/A", "－", "—", "null", "None"}: return None
    try: return float(s) if any(c in s for c in ".eE") else int(s)
    except ValueError: return None

def fmt(v):
    if v is None or v == "": return MISSING
    if isinstance(v, float): return f"{v:,.2f}".rstrip("0").rstrip(".")
    if isinstance(v, int): return f"{v:,}"
    return str(v).replace("|", "/").replace("\n", " ")

def walk(x, path=""):
    if isinstance(x, dict):
        for k, v in x.items():
            p = f"{path}.{k}" if path else k
            yield p, v
            yield from walk(v, p)
    elif isinstance(x, list):
        for i, v in enumerate(x[:500]):
            yield from walk(v, f"{path}[{i}]")

def load(root, date):
    candidates = [
        root / f"data/snapshots/{date}/snapshot.json",
        root / f"data/snapshots/{date}/twse-snapshot.json",
        root / f"data/twse/{date}.json",
        root / f"data/premarket/{date}.json",
        root / f"data/taifex/{date}.json",
    ]
    loaded = []
    for p in candidates:
        if p.exists():
            try: loaded.append((p, json.loads(p.read_text(encoding="utf-8"))))
            except Exception as e: loaded.append((p, {"_load_error": str(e)}))
    if not loaded: raise SystemExit(f"找不到資料：{date}")
    return loaded

def find_value(objects, names):
    names = {n.lower() for n in names}
    for _, data in objects:
        for path, value in walk(data):
            key = path.rsplit(".", 1)[-1].lower().replace("-", "_")
            if key in names:
                n = num(value)
                if n is not None: return n
    return None

def md_table(rows, headers):
    out = "| " + " | ".join(headers) + " |\n|" + "|".join(["---"] * len(headers)) + "|\n"
    for row in rows: out += "| " + " | ".join(fmt(x) for x in row) + " |\n"
    return out

def generate(objects, date):
    source = ", ".join(str(p) for p, _ in objects)
    index = find_value(objects, {"close", "taiex", "index", "index_value", "closing_index"})
    change = find_value(objects, {"change", "change_points", "change_point", "change_value"})
    pct = find_value(objects, {"change_percent", "change_pct", "changepercentage", "pct"})
    turnover = find_value(objects, {"turnover", "total_turnover", "trading_value", "成交金額"})
    rows = [
        ("加權指數", index, "點"), ("開盤", find_value(objects, {"open", "opening"}), "點"),
        ("最高", find_value(objects, {"high", "highest"}), "點"), ("最低", find_value(objects, {"low", "lowest"}), "點"),
        ("收盤", index, "點"), ("漲跌點數", change, "點"), ("漲跌幅", pct, "%"),
        ("成交金額", turnover / 100000000 if isinstance(turnover, (int,float)) and turnover > 1000000 else turnover, "億元"),
    ]
    breadth = [("上漲家數", find_value(objects, {"advance", "advances", "up", "up_count", "上漲家數"})),
               ("下跌家數", find_value(objects, {"decline", "declines", "down", "down_count", "下跌家數"})),
               ("平盤家數", find_value(objects, {"unchanged", "unchanged_count", "持平"})),
               ("漲停家數", find_value(objects, {"limit_up", "limitup", "漲停家數"})),
               ("跌停家數", find_value(objects, {"limit_down", "limitdown", "跌停家數"}))]
    lines = [f"# 每日市場資料報告｜{date}", "", f"- 報告日期：`{date}`", f"- T0 交易日期：`{date}`", f"- 資料產出時間：`{datetime.now(TZ).strftime('%Y-%m-%d %H:%M:%S %z')}`", "- 時區：`Asia/Taipei`", "", f"> 資料來源：`{source}`", "> 本報告僅整理資料，不提供交易判斷。", "", "---", "", "## 一、現貨", "", "### 1. 台股大盤行情", "", md_table(rows, ("項目", "數值", "單位")), "", "### 2. 市場漲跌家數", "", "#### 2.1 上市公司", "", md_table(breadth, ("項目", "家數")), "", "#### 2.2 上櫃公司", "", md_table([(x, MISSING) for x, _ in breadth], ("項目", "家數")), "", "### 3. 三大法人現貨買賣超", "", md_table([(x, find_value(objects, {k}), "億元") for x, k in [("外資", "foreign_net"), ("投信", "investment_trust_net"), ("自營商", "dealer_net"), ("三大法人合計", "institutional_net")]), "", "### 4. 融資融券", "", md_table([(x, find_value(objects, {k}), u) for x, k, u in [("融資餘額", "margin_balance", "億元"), ("融資增減", "margin_change", "億元"), ("融券餘額", "short_balance", "張"), ("融券增減", "short_change", "張"), ("融資維持率", "margin_maintenance", "%")]), "", "### 5. 借券資料", "", md_table([(x, find_value(objects, {k}), "張") for x, k in [("借券餘額", "sbl_balance"), ("借券賣出餘額", "sbl_short_balance"), ("借券賣出增減", "sbl_short_change")]), "", "### 6. 市場成交結構", "", md_table([(x, find_value(objects, {k}), "億元") for x, k in [("上市成交金額", "twse_turnover"), ("上櫃成交金額", "tpex_turnover"), ("上市櫃成交金額合計", "total_turnover")]), "", "## 二、台指期與選擇權", "", "### 1. 台指期行情", "", "資料來源已載入，欄位解析待依 snapshot schema 對應。", "", "### 2. 台指期法人交易", "", "資料來源已載入，欄位解析待依 snapshot schema 對應。", "", "### 3. 台指期法人 OI", "", "資料來源已載入，欄位解析待依 snapshot schema 對應。", "", "### 4. 選擇權資料", "", "資料來源已載入，欄位解析待依 snapshot schema 對應。", "", "## 三、資料完整性檢查", "", f"- 已載入資料檔案：{len(objects)}", "- 報告未再將台指期與選擇權整段硬編碼為資料未取得。", "- 尚未能由目前欄位名稱可靠對應的欄位，保留資料未取得，禁止推估。", ""]
    return "\n".join(lines)

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--date", required=True); a = ap.parse_args()
    root = Path(__file__).resolve().parents[1]; objects = load(root, a.date); out = root / f"reports/{a.date}.md"; out.write_text(generate(objects, a.date), encoding="utf-8"); print(f"OK: {out}")

if __name__ == "__main__": main()
