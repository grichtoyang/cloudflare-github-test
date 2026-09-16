#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

TWSE_PROXY = os.getenv("TWSE_PROXY_BASE_URL", "https://twse-proxy.grichtoyang.workers.dev")
TWSE_API = "https://openapi.twse.com.tw/v1"
TWSE_RWD = "https://www.twse.com.tw/rwd/zh"
TPEX_API = "https://www.tpex.org.tw/openapi/v1"


def num(value):
    if value is None:
        return None
    s = str(value).replace(",", "").replace("%", "").replace("－", "-").replace("—", "-").strip()
    if s in {"", "--", "---", "N/A", "null", "None"}:
        return None
    try:
        return float(s)
    except ValueError:
        return None


def get_json(url):
    try:
        req = Request(url, headers={"accept": "application/json", "user-agent": "daily-pre-market-analysis/1.2"})
        with urlopen(req, timeout=45) as response:
            return json.loads(response.read().decode("utf-8"))
    except Exception:
        return None


def rows(payload):
    if isinstance(payload, list):
        return payload
    if not isinstance(payload, dict):
        return []
    for key in ("data", "aaData", "results", "result", "records"):
        value = payload.get(key)
        if isinstance(value, list):
            return value
    return []


def flatten(payload):
    out = []
    for row in rows(payload):
        if isinstance(row, dict):
            out.append({str(k): v for k, v in row.items()})
        elif isinstance(row, list):
            out.append({str(i): v for i, v in enumerate(row)})
    return out


def find_value(payload, candidates):
    candidates = tuple(c.lower() for c in candidates)
    for row in flatten(payload):
        for key, value in row.items():
            key_l = key.lower().replace(" ", "")
            if any(c.replace(" ", "") in key_l for c in candidates):
                value_n = num(value)
                if value_n is not None:
                    return value_n
    return None


def fetch_first(urls):
    for url in urls:
        payload = get_json(url)
        if payload is not None:
            return payload, url
    return None, None


def rwd(path, date8, extra=None):
    params = {"date": date8, "response": "json"}
    if extra:
        params.update(extra)
    return f"{TWSE_RWD}/{path}?{urlencode(params)}"


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", required=True)
    parser.add_argument("--output-root", default="data")
    args = parser.parse_args(argv)
    d = args.date
    date8 = d.replace("-", "")
    root = Path(args.output_root)

    base = {}
    twse_file = root / "twse" / f"{d}.json"
    if twse_file.exists():
        try:
            base = json.loads(twse_file.read_text(encoding="utf-8"))
        except Exception:
            base = {}
    raw = base.get("data", base) if isinstance(base, dict) else {}
    taiex = raw.get("taiex", {}) if isinstance(raw, dict) else {}
    stats = raw.get("market_statistics", {}) if isinstance(raw, dict) else {}
    breadth = raw.get("advance_decline", {}) if isinstance(raw, dict) else {}

    t86, t86_url = fetch_first([rwd("fund/T86", date8, {"selectType": "ALL"})])
    margn, margn_url = fetch_first([f"{TWSE_API}/exchangeReport/MI_MARGN?date={date8}"])
    sbl, sbl_url = fetch_first([f"{TWSE_API}/SBL/TWT96U?date={date8}"])
    fmtqik, fmtqik_url = fetch_first([f"{TWSE_API}/exchangeReport/FMTQIK?date={date8}"])
    otc_quotes, otc_quotes_url = fetch_first([f"{TPEX_API}/tpex_mainboard_quotes?date={date8}", f"{TPEX_API}/tpex_mainboard_quotes"])
    otc_margin, otc_margin_url = fetch_first([f"{TPEX_API}/tpex_mainboard_margin_balance?date={date8}", f"{TPEX_API}/tpex_mainboard_margin_balance"])
    otc_sbl, otc_sbl_url = fetch_first([f"{TPEX_API}/tpex_margin_sbl?date={date8}", f"{TPEX_API}/tpex_margin_sbl"])
    otc_highlight, otc_highlight_url = fetch_first([f"{TPEX_API}/tpex_mainborad_highlight?date={date8}", f"{TPEX_API}/tpex_mainborad_highlight"])

    def breadth_from(payload):
        result = {k: None for k in ("up", "down", "unchanged", "limit_up", "limit_down")}
        for row in flatten(payload):
            text = " ".join(str(v) for v in row.values())
            if "上漲" in text:
                result["up"] = result["up"] or find_value(row, ("上漲", "up"))
                result["limit_up"] = result["limit_up"] or find_value(row, ("漲停", "limitup"))
            if "下跌" in text:
                result["down"] = result["down"] or find_value(row, ("下跌", "down"))
                result["limit_down"] = result["limit_down"] or find_value(row, ("跌停", "limitdown"))
            if "持平" in text or "平盤" in text:
                result["unchanged"] = result["unchanged"] or find_value(row, ("持平", "平盤", "unchanged"))
        return result

    def total_amount(payload):
        for row in flatten(payload):
            text = " ".join(str(v) for v in row.values())
            if "總計" in text or "合計" in text:
                value = find_value(row, ("成交金額", "amount", "turnover"))
                if value is not None:
                    return value
        return find_value(payload, ("成交金額", "amount", "turnover"))

    data = {
        "taiex": {
            "close": num(taiex.get("close")),
            "open": num(taiex.get("open")),
            "high": num(taiex.get("high")),
            "low": num(taiex.get("low")),
            "change_points": num(taiex.get("change", taiex.get("change_points"))),
            "change_percent": num(taiex.get("change_percent")),
            "turnover_value": total_amount(fmtqik) or total_amount(stats),
        },
        "listed_breadth": breadth_from(breadth),
        "otc_breadth": breadth_from(otc_quotes),
        "institutional": {
            "unit": "shares",
            "foreign": find_value(t86, ("外陸資買賣超", "外資及陸資買賣超", "foreign")),
            "investment_trust": find_value(t86, ("投信買賣超", "investmenttrust")),
            "dealer": find_value(t86, ("自營商買賣超", "dealer")),
            "total": find_value(t86, ("三大法人買賣超合計", "合計買賣超", "total")),
        },
        "margin": {
            "financing_balance": find_value(margn, ("融資餘額", "financingbalance")),
            "financing_change": find_value(margn, ("融資增減", "financingchange")),
            "short_balance": find_value(margn, ("融券餘額", "shortbalance")),
            "short_change": find_value(margn, ("融券增減", "shortchange")),
            "maintenance_ratio": find_value(margn, ("融資維持率", "maintenanceratio")),
        },
        "sbl": {
            "balance": find_value(sbl, ("借券餘額", "balance")),
            "short_sale_balance": find_value(sbl, ("借券賣出餘額", "shortsalebalance")),
            "short_sale_change": find_value(sbl, ("借券賣出增減", "shortsalechange")),
        },
        "turnover": {
            "listed": total_amount(fmtqik),
            "otc": total_amount(otc_highlight),
            "total": (total_amount(fmtqik) or 0) + (total_amount(otc_highlight) or 0) if total_amount(fmtqik) is not None or total_amount(otc_highlight) is not None else None,
        },
    }

    missing = [f"taiex.{k}" for k in ("close", "change_points", "change_percent") if data["taiex"][k] is None]
    unavailable = [f"{group}.{key}" for group, values in data.items() for key, value in values.items() if value is None]
    out = {
        "ok": not missing and not unavailable,
        "source": "SPOT",
        "date": d,
        "retrieved_at": datetime.now(timezone.utc).isoformat(),
        "timezone": "UTC",
        "data": data,
        "sources": {"twse_snapshot": str(twse_file), "twse_t86": t86_url, "twse_margin": margn_url, "twse_sbl": sbl_url, "twse_turnover": fmtqik_url, "tpex_breadth": otc_quotes_url, "tpex_margin": otc_margin_url, "tpex_sbl": otc_sbl_url, "tpex_turnover": otc_highlight_url},
        "missing_required": missing,
        "unavailable_fields": unavailable,
        "integrity_errors": [],
    }
    for path in (root / "snapshots" / d / "spot-snapshot.json", root / "spot" / f"{d}.json"):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"date": d, "ok": out["ok"], "missing_required": missing, "unavailable_fields": unavailable, "integrity_errors": []}, ensure_ascii=False))
    return 0 if out["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
