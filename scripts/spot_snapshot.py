#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

TWSE_PROXY = "https://twse-proxy.grichtoyang.workers.dev"
TWSE = "https://openapi.twse.com.tw/v1"
TPEX = "https://www.tpex.org.tw/openapi/v1"


def fetch(url: str, retries: int = 3):
    last = None
    for attempt in range(retries):
        try:
            request = Request(url, headers={"accept": "application/json", "user-agent": "daily-pre-market-analysis/2.4"})
            with urlopen(request, timeout=60) as response:
                return json.loads(response.read().decode()), response.status
        except Exception as exc:
            last = exc
            if attempt < retries - 1:
                time.sleep(2 ** attempt)
    raise last


def number(value):
    if value is None:
        return None
    text = re.sub(r"<[^>]+>", "", str(value)).replace(",", "").replace("%", "").strip()
    if text in {"", "--", "---", "－", "—", "N/A", "null", "None"}:
        return None
    try:
        return float(text)
    except (TypeError, ValueError):
        return None


def rows(payload):
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        for key in ("data", "data1", "data8", "aaData", "result"):
            candidate = payload.get(key)
            if isinstance(candidate, list):
                return candidate
    return []


def value(row, names):
    if not isinstance(row, dict):
        return None
    for name in names:
        if name in row:
            parsed = number(row[name])
            if parsed is not None:
                return parsed
    return None


def breadth(items):
    result = {"up": 0, "down": 0, "unchanged": 0, "limit_up": 0, "limit_down": 0}
    seen = False
    for item in items:
        change = value(item, ["漲跌", "漲跌價差", "change", "Change"])
        percent = value(item, ["漲跌幅", "漲跌百分比", "change_percent", "ChangePercent"])
        if change is None and percent is None:
            continue
        seen = True
        if percent is not None and percent >= 9.5:
            result["limit_up"] += 1
        if percent is not None and percent <= -9.5:
            result["limit_down"] += 1
        direction = change if change is not None else percent
        result["up" if direction > 0 else "down" if direction < 0 else "unchanged"] += 1
    return result if seen else {}


def total(items, names):
    values = [value(item, names) for item in items]
    values = [item for item in values if item is not None]
    return sum(values) if values else None


def total_row(items):
    for item in items:
        if not isinstance(item, dict):
            continue
        label = " ".join(str(v) for v in item.values() if isinstance(v, (str, int, float)))
        if any(token in label for token in ("合計", "總計", "Total", "TOTAL")):
            return item
    return items[0] if len(items) == 1 else {}


def source_date(payload):
    if not isinstance(payload, dict):
        return None
    for key in ("date", "日期", "資料日期", "交易日期", "Date", "dateTime"):
        candidate = payload.get(key)
        if candidate:
            return str(candidate).replace("/", "-")[:10]
    return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", required=True)
    parser.add_argument("--output-root", default="data")
    args = parser.parse_args()
    date = args.date
    date8 = date.replace("-", "")
    sources = {}

    def get(name, url):
        try:
            payload, status = fetch(url)
            sources[name] = {"url": url, "status": status, "ok": status == 200}
            return payload if status == 200 else None
        except Exception as exc:
            sources[name] = {"url": url, "status": None, "ok": False, "error": str(exc)}
            return None

    proxy = get("twse_proxy", f"{TWSE_PROXY}?date={date8}") or {}
    proxy_date = proxy.get("date") if isinstance(proxy, dict) else None
    proxy_valid = isinstance(proxy, dict) and proxy.get("ok") is True and proxy_date == date
    if "twse_proxy" in sources:
        sources["twse_proxy"].update({"date": proxy_date, "date_match": proxy_valid})

    payload = proxy.get("data", {}) if isinstance(proxy, dict) else {}
    taiex = payload.get("taiex") or {}
    statistics = payload.get("market_statistics") or {}

    inst_payload = get("twse_institutional", f"{TWSE}/fund/T86?date={date8}&selectType=ALL")
    margin_payload = get("twse_margin", f"{TWSE}/exchangeReport/MI_MARGN?response=json&date={date8}")
    sbl_payload = get("twse_sbl", f"{TWSE}/SBL/TWT96U?response=json&date={date8}")
    turnover_payload = get("twse_turnover", f"{TWSE}/exchangeReport/FMTQIK?response=json&date={date8}")
    otc_quotes_payload = get("tpex_quotes", f"{TPEX}/tpex_mainboard_daily_close_quotes")
    otc_turnover_payload = get("tpex_mainboard_highlight", f"{TPEX}/tpex_mainboard_highlight")

    inst = rows(inst_payload)
    margin = rows(margin_payload)
    sbl = rows(sbl_payload)
    turnover = rows(turnover_payload)
    otc_quotes = rows(otc_quotes_payload)
    otc_turnover = rows(otc_turnover_payload)

    institutional_row = next((row for row in inst if isinstance(row, dict) and any(key in row for key in ("外陸資買賣超股數(不含外資自營商)", "投信買賣超股數", "自營商買賣超股數"))), {})
    margin_row = total_row(margin)
    sbl_row = total_row(sbl)
    turnover_row = total_row(turnover)

    foreign = value(institutional_row, ["外陸資買賣超股數(不含外資自營商)"])
    investment_trust = value(institutional_row, ["投信買賣超股數"])
    dealer = value(institutional_row, ["自營商買賣超股數"])

    listed = breadth(rows(payload.get("listed_breadth")))
    otc = breadth(otc_quotes)
    listed_turnover = value(turnover_row, ["成交金額(元)", "成交金額"])
    otc_turnover_value = total(otc_turnover, ["成交金額", "成交金額(元)", "成交額"])

    data = {
        "taiex": {key: value(taiex, names) for key, names in {
            "close": ["close", "收盤指數", "收盤"], "open": ["open", "開盤指數", "開盤"],
            "high": ["high", "最高指數", "最高"], "low": ["low", "最低指數", "最低"],
            "change_points": ["change_points", "漲跌點數", "change"],
            "change_percent": ["change_percent", "漲跌百分比", "change_pct"],
        }.items()},
        "listed_breadth": listed,
        "otc_breadth": otc,
        "institutional": {"unit": "shares", "foreign": foreign, "investment_trust": investment_trust, "dealer": dealer,
                          "total": foreign + investment_trust + dealer if None not in (foreign, investment_trust, dealer) else None},
        "margin": {key: value(margin_row, names) for key, names in {
            "financing_balance": ["融資餘額(元)", "融資餘額"], "financing_change": ["融資增減(元)", "融資增減"],
            "short_balance": ["融券餘額(張)", "融券餘額"], "short_change": ["融券增減(張)", "融券增減"],
            "maintenance_ratio": ["融資維持率(%)", "融資維持率"],
        }.items()},
        "sbl": {key: value(sbl_row, names) for key, names in {
            "balance": ["借券餘額", "借券餘額(張)"], "short_sale_balance": ["借券賣出餘額", "借券賣出餘額(張)"],
            "short_sale_change": ["借券賣出增減", "借券賣出增減(張)"],
        }.items()},
        "turnover": {"listed": listed_turnover, "otc": otc_turnover_value,
                     "total": listed_turnover + otc_turnover_value if None not in (listed_turnover, otc_turnover_value) else None},
    }
    data["taiex"]["turnover_value"] = value(statistics, ["turnover_value", "成交金額(元)", "成交金額", "turnover"])

    required = {
        "taiex": ["close", "open", "high", "low", "change_points", "change_percent", "turnover_value"],
        "listed_breadth": ["up", "down", "unchanged", "limit_up", "limit_down"],
        "otc_breadth": ["up", "down", "unchanged", "limit_up", "limit_down"],
        "institutional": ["foreign", "investment_trust", "dealer", "total"],
        "margin": ["financing_balance", "financing_change", "short_balance", "short_change", "maintenance_ratio"],
        "sbl": ["balance", "short_sale_balance", "short_sale_change"],
        "turnover": ["listed", "otc", "total"],
    }
    missing = [f"{group}.{field}" for group, fields in required.items() for field in fields if data.get(group, {}).get(field) is None]
    integrity_errors = []
    if not proxy_valid:
        integrity_errors.append("twse_proxy.date_mismatch_or_not_ok")
    if not listed:
        integrity_errors.append("twse_proxy.listed_breadth.empty_or_unverified")
    if not otc_quotes:
        integrity_errors.append("tpex_quotes.empty")
    if not inst:
        integrity_errors.append("twse_institutional.empty")
    if not margin:
        integrity_errors.append("twse_margin.empty")
    if not sbl:
        integrity_errors.append("twse_sbl.empty")
    if not turnover:
        integrity_errors.append("twse_turnover.empty")
    for name, raw in (("tpex_quotes", otc_quotes_payload), ("tpex_mainboard_highlight", otc_turnover_payload)):
        if source_date(raw) != date:
            integrity_errors.append(f"{name}.date_unverified_or_mismatch")

    out = {"ok": not missing and not integrity_errors, "source": "SPOT", "date": date,
           "retrieved_at": datetime.now(timezone.utc).isoformat(), "timezone": "UTC", "data": data,
           "sources": sources, "missing_required": missing, "integrity_errors": integrity_errors}
    for path in (Path(args.output_root) / "snapshots" / date / "spot-snapshot.json", Path(args.output_root) / "spot" / f"{date}.json"):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"date": date, "ok": out["ok"], "missing_required": missing, "integrity_errors": integrity_errors}, ensure_ascii=False))
    return 0 if out["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
