#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path


def num(value):
    if value is None:
        return None
    text = str(value).replace(",", "").replace("%", "").replace("－", "-").replace("—", "-").strip()
    if text in {"", "--", "---", "N/A", "null", "None", "除息", "-"}:
        return None
    match = re.search(r"-?\d+(?:\.\d+)?", text)
    return float(match.group()) if match else None


def load_raw(root: Path, name: str, date: str):
    path = root / "raw" / f"{name}_{date}.json"
    if not path.exists():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        return payload.get("payload") if isinstance(payload, dict) else payload
    except Exception:
        return None


def load_twse(root: Path, date: str):
    path = root / "twse" / f"{date}.json"
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        return payload.get("data", {}) if isinstance(payload, dict) else {}
    except Exception:
        return {}


def rows(value):
    if isinstance(value, list):
        return value
    if isinstance(value, dict):
        fields = value.get("fields") or value.get("columns") or []
        data = value.get("data") or value.get("records") or value.get("aaData") or []
        if fields and data:
            return [
                {str(fields[i]): item for i, item in enumerate(row) if i < len(fields)}
                if isinstance(row, list) else row
                for row in data
            ]
        return data if isinstance(data, list) else []
    return []


def normal_key(value):
    return re.sub(r"[^a-z0-9一-龥]", "", str(value).lower())


def field(row, *names):
    if not isinstance(row, dict):
        return None
    wanted = {normal_key(name) for name in names}
    for key, value in row.items():
        if normal_key(key) in wanted:
            return num(value)
    return None


def first(value, predicate=lambda row: True):
    return next((row for row in rows(value) if isinstance(row, dict) and predicate(row)), {})


def total(value, *names):
    values = [field(row, *names) for row in rows(value)]
    values = [item for item in values if item is not None]
    return sum(values) if values else None


def add(left, right):
    if left is None:
        return right
    if right is None:
        return left
    return left + right


def table_value(table, labels, columns):
    if not isinstance(table, dict):
        return None
    fields = table.get("fields", [])
    data = table.get("data", [])
    if not fields or not data:
        return None
    column_indexes = [fields.index(column) for column in columns if column in fields]
    if not column_indexes:
        return None
    wanted = {str(label).strip() for label in labels}
    for row in data:
        if row and str(row[0]).strip() in wanted:
            for index in column_indexes:
                if len(row) > index:
                    value = num(row[index])
                    if value is not None:
                        return value
    return None


def source_date_errors(raw, expected, name):
    errors = []
    for row in rows(raw):
        if not isinstance(row, dict):
            continue
        for key in ("日期", "出表日期", "資料日期", "Date"):
            if key in row and row[key]:
                actual = str(row[key]).replace("-", "")
                expected8 = expected.replace("-", "")
                if len(actual) == 7 and actual.startswith("1"):
                    actual = str(int(actual[:3]) + 1911) + actual[3:]
                if actual != expected8:
                    errors.append(f"{name}.date_mismatch:{row[key]}!= {expected}")
                return errors
    return errors


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", required=True)
    parser.add_argument("--output-root", default="data")
    args = parser.parse_args()
    date = args.date
    root = Path(args.output_root)

    twse = load_twse(root, date)
    taiex = twse.get("taiex", {})
    stats = twse.get("market_statistics", {})
    breadth_snapshot = twse.get("advance_decline", {})

    mi = load_raw(root, "twse_mi_index", date)
    breadth = load_raw(root, "twse_listed_breadth", date)
    t86 = load_raw(root, "twse_t86", date)
    margin = load_raw(root, "twse_margin", date)
    sbl = load_raw(root, "twse_sbl", date)
    turnover = load_raw(root, "twse_turnover", date)
    tpex_quotes = load_raw(root, "tpex_quotes", date)
    tpex_margin = load_raw(root, "tpex_margin", date)
    tpex_sbl = load_raw(root, "tpex_sbl", date)
    tpex_highlight = load_raw(root, "tpex_highlight", date)

    index_row = first(mi, lambda row: row.get("指數") == "發行量加權股價指數")
    listed_row = first(breadth, lambda row: row.get("類型") == "股票")
    turnover_row = first(turnover)
    otc_summary = first(tpex_highlight)

    close = num(taiex.get("close")) or field(index_row, "收盤指數")
    raw_change = num(taiex.get("change")) or field(index_row, "漲跌點數")
    direction = str(taiex.get("direction", "") or index_row.get("漲跌", "")).strip()
    change = raw_change
    if raw_change is not None and direction in {"-", "跌", "負"}:
        change = -abs(raw_change)
    elif raw_change is not None and direction in {"+", "漲", "正"}:
        change = abs(raw_change)
    change_percent = num(taiex.get("change_percent")) or field(index_row, "漲跌百分比")
    if change is not None and change_percent is not None and change != 0:
        change_percent = abs(change_percent) if change > 0 else -abs(change_percent)

    listed_up = table_value(breadth_snapshot, ["上漲(漲停)"], ["股票"]) or field(listed_row, "上漲")
    listed_down = table_value(breadth_snapshot, ["下跌(跌停)"], ["股票"]) or field(listed_row, "下跌")
    listed_flat = table_value(breadth_snapshot, ["持平"], ["股票"]) or field(listed_row, "持平")
    listed_limit_up = field(listed_row, "漲停")
    listed_limit_down = field(listed_row, "跌停")
    listed_turnover = table_value(stats, ["總計(1~15)", "總計"], ["成交金額(元)"]) or field(turnover_row, "TradeValue", "成交金額")

    otc_up = field(otc_summary, "PriceRiseCompanyNumbers", "上漲家數", "上漲")
    otc_down = field(otc_summary, "PriceDeclineCompanyNumbers", "下跌家數", "下跌")
    otc_flat = field(otc_summary, "PriceFlatCompanyNumbers", "持平家數", "持平")
    otc_limit_up = field(otc_summary, "LimitUpCompanyNumbers", "漲停家數", "漲停")
    otc_limit_down = field(otc_summary, "LimitDownCompanyNumbers", "跌停家數", "跌停")
    otc_turnover = field(otc_summary, "DailyTradingValue", "成交金額", "成交值")
    if otc_turnover is not None and otc_turnover < 1_000_000_000:
        otc_turnover *= 1_000_000

    tw_fin_balance = total(margin, "融資今日餘額")
    tp_fin_balance = total(tpex_margin, "MarginPurchaseBalance", "融資餘額")
    tw_fin_change = add(total(margin, "融資買進"), -total(margin, "融資賣出")) if total(margin, "融資買進") is not None and total(margin, "融資賣出") is not None else None
    tp_fin_change = total(tpex_margin, "MarginPurchase", "融資增減")
    tw_short_balance = total(margin, "融券今日餘額")
    tp_short_balance = total(tpex_margin, "ShortSaleBalance", "融券餘額")
    tw_short_change = add(total(margin, "融券賣出"), -total(margin, "融券買進")) if total(margin, "融券賣出") is not None and total(margin, "融券買進") is not None else None
    tp_short_change = total(tpex_margin, "ShortSale", "融券增減")

    data = {
        "taiex": {"close": close, "open": None, "high": None, "low": None, "change_points": change, "change_percent": change_percent, "turnover_value": listed_turnover},
        "listed_breadth": {"up": listed_up, "down": listed_down, "unchanged": listed_flat, "limit_up": listed_limit_up, "limit_down": listed_limit_down},
        "otc_breadth": {"up": otc_up, "down": otc_down, "unchanged": otc_flat, "limit_up": otc_limit_up, "limit_down": otc_limit_down},
        "institutional": {"unit": "shares", "foreign": total(t86, "外陸資買賣超股數(不含外資自營商)"), "investment_trust": total(t86, "投信買賣超股數"), "dealer": total(t86, "自營商買賣超股數"), "total": total(t86, "三大法人買賣超股數")},
        "margin": {"financing_balance": add(tw_fin_balance, tp_fin_balance), "financing_change": add(tw_fin_change, tp_fin_change), "short_balance": add(tw_short_balance, tp_short_balance), "short_change": add(tw_short_change, tp_short_change), "maintenance_ratio": None},
        "sbl": {"balance": total(sbl, "SecuritiesBorrowingBalanceOfTheMarketDay", "借券餘額"), "short_sale_balance": None, "short_sale_change": None},
        "turnover": {"listed": listed_turnover, "otc": otc_turnover, "total": add(listed_turnover, otc_turnover)},
    }

    unavailable = [
        "taiex.open", "taiex.high", "taiex.low", "margin.maintenance_ratio",
        "sbl.short_sale_balance", "sbl.short_sale_change",
    ]
    missing_required = [
        f"{group}.{key}"
        for group, values in data.items()
        for key, value in values.items()
        if value is None and key != "unit" and f"{group}.{key}" not in unavailable
    ]

    integrity_errors = []
    for name, raw in (("twse_mi_index", mi), ("twse_listed_breadth", breadth), ("twse_margin", margin), ("twse_sbl", sbl), ("twse_turnover", turnover)):
        integrity_errors.extend(source_date_errors(raw, date, name))
    if close is not None and change is not None and change_percent is not None and close != change:
        previous = close - change
        if previous != 0:
            expected = change / previous * 100
            if abs(expected - change_percent) > 0.15:
                integrity_errors.append("taiex.change_percent_mismatch")
    inst = data["institutional"]
    if all(inst.get(key) is not None for key in ("foreign", "investment_trust", "dealer", "total")):
        if abs(inst["foreign"] + inst["investment_trust"] + inst["dealer"] - inst["total"]) > 0.5:
            integrity_errors.append("institutional.total_mismatch")
    turn = data["turnover"]
    if all(turn.get(key) is not None for key in ("listed", "otc", "total")):
        if abs(turn["listed"] + turn["otc"] - turn["total"]) > 1:
            integrity_errors.append("turnover.total_mismatch")

    output = {
        "ok": not unavailable and not missing_required and not integrity_errors,
        "source": "SPOT",
        "date": date,
        "retrieved_at": datetime.now(timezone.utc).isoformat(),
        "timezone": "UTC",
        "data": data,
        "missing_required": missing_required,
        "unavailable_fields": unavailable,
        "integrity_errors": integrity_errors,
    }
    for path in (root / "snapshots" / date / "spot-snapshot.json", root / "spot" / f"{date}.json"):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"date": date, "ok": output["ok"], "missing_required": missing_required, "unavailable_fields": unavailable, "integrity_errors": integrity_errors}, ensure_ascii=False))
    return 0 if output["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
