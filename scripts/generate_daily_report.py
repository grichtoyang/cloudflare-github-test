#!/usr/bin/env python3
"""Generate the daily report. V1.0 currently validates and reports spot data only."""
from __future__ import annotations
import argparse, json, re
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

MISSING = "資料未取得"
TZ = ZoneInfo("Asia/Taipei")


def number(value):
    if value is None or value == "":
        return None
    if isinstance(value, (int, float)):
        return value
    text = re.sub(r"<[^>]*>", "", str(value)).replace(",", "").replace("%", "").strip()
    if text in {"", "--", "---", "N/A", "null", "None", "－", "—"}:
        return None
    try:
        return float(text) if any(c in text for c in ".eE") else int(text)
    except ValueError:
        return None


def fmt(value):
    if value is None:
        return MISSING
    if isinstance(value, float):
        return f"{value:,.2f}".rstrip("0").rstrip(".")
    if isinstance(value, int):
        return f"{value:,}"
    return str(value).replace("|", "/").replace("\n", " ")


def unwrap(value):
    """Unwrap GitHub collector envelopes whose content is JSON text."""
    if isinstance(value, dict) and isinstance(value.get("content"), str):
        try:
            return unwrap(json.loads(value["content"]))
        except json.JSONDecodeError:
            return value
    if isinstance(value, dict):
        return {k: unwrap(v) for k, v in value.items()}
    if isinstance(value, list):
        return [unwrap(v) for v in value]
    return value


def load(root, date):
    paths = [root / f"data/snapshots/{date}/twse-snapshot.json",
             root / f"data/snapshots/{date}/snapshot.json",
             root / f"data/twse/{date}.json",
             root / f"data/premarket/{date}.json"]
    result = []
    for path in paths:
        if path.exists():
            try:
                result.append((path, unwrap(json.loads(path.read_text(encoding="utf-8")))))
            except Exception as exc:
                result.append((path, {"_load_error": str(exc)}))
    if not result:
        raise SystemExit(f"找不到資料：{date}")
    return result


def dict_at(root, *keys):
    node = root
    for key in keys:
        if not isinstance(node, dict):
            return {}
        node = node.get(key, {})
    return node if isinstance(node, dict) else {}


def first(mapping, *keys):
    for key in keys:
        if key in mapping:
            value = number(mapping[key])
            if value is not None:
                return value
    return None


def table(rows, headers):
    text = "| " + " | ".join(headers) + " |\n|" + "|".join(["---"] * len(headers)) + "|\n"
    return text + "".join("| " + " | ".join(fmt(v) for v in row) + " |\n" for row in rows)


def generate(objects, date):
    twse = next((data for path, data in objects if path.name == "twse-snapshot.json"), {})
    market = dict_at(twse, "data", "data")
    taiex = dict_at(market, "taiex")
    breadth = dict_at(market, "market_summary", "stocks") or dict_at(market, "stocks")
    rows = [
        ("加權指數", first(taiex, "close", "value"), "點"),
        ("收盤", first(taiex, "close", "value"), "點"),
        ("漲跌點數", first(taiex, "change_points", "change"), "點"),
        ("漲跌幅", first(taiex, "change_percent", "change_pct"), "%"),
        ("成交金額", (first(taiex, "turnover", "trading_value") or 0) / 100000000 if first(taiex, "turnover", "trading_value") is not None else None, "億元"),
    ]
    listed = [("上漲家數", first(breadth, "advance", "advances", "up", "up_count")),
              ("下跌家數", first(breadth, "decline", "declines", "down", "down_count")),
              ("平盤家數", first(breadth, "unchanged", "unchanged_count", "flat")),
              ("漲停家數", first(breadth, "limit_up", "limitup")),
              ("跌停家數", first(breadth, "limit_down", "limitdown"))]
    source = ", ".join(str(path) for path, _ in objects)
    lines = [f"# 每日市場資料報告｜{date}", "", f"- 報告日期：`{date}`", f"- T0 交易日期：`{date}`", f"- 資料產出時間：`{datetime.now(TZ).strftime('%Y-%m-%d %H:%M:%S %z')}`", "- 時區：`Asia/Taipei`", "", f"> 資料來源：`{source}`", "> 本報告僅整理資料，不提供交易判斷。", "", "---", "", "## 一、現貨", "", "### 1. 台股大盤行情", "", table(rows, ("項目", "數值", "單位")), "", "### 2. 市場漲跌家數", "", "#### 2.1 上市公司", "", table([(name, value) for name, value in listed], ("項目", "家數")), "", "#### 2.2 上櫃公司", "", table([(name, MISSING) for name, _ in listed], ("項目", "家數")), "", "### 3. 三大法人現貨買賣超", "", table([(name, MISSING, "億元") for name in ("外資", "投信", "自營商", "三大法人合計")], ("項目", "數值", "單位")), "", "### 4. 融資融券", "", table([(name, MISSING, unit) for name, unit in (("融資餘額", "億元"), ("融資增減", "億元"), ("融券餘額", "張"), ("融券增減", "張"), ("融資維持率", "%"))], ("項目", "數值", "單位")), "", "### 5. 借券資料", "", table([(name, MISSING, "張") for name in ("借券餘額", "借券賣出餘額", "借券賣出增減")], ("項目", "數值", "單位")), "", "### 6. 市場成交結構", "", table([(name, MISSING, "億元") for name in ("上市成交金額", "上櫃成交金額", "上市櫃成交金額合計")], ("項目", "數值", "單位")), "", "## 二、台指期與選擇權", "", "本版本暫不處理。", "", "## 三、資料完整性檢查", "", f"- 已載入資料檔案：{len(objects)}", "- 現貨欄位採資料集內明確欄位解析，不跨資料集模糊抓取。", ""]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(); parser.add_argument("--date", required=True); args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    output = root / f"reports/{args.date}.md"
    output.write_text(generate(load(root, args.date), args.date), encoding="utf-8")
    print(f"OK: {output}")


if __name__ == "__main__":
    main()
