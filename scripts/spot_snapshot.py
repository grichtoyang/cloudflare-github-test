#!/usr/bin/env python3
"""Collect only spot-market data required by DATA_REPORT_TEMPLATE."""
from __future__ import annotations
import argparse, json, re, sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

TWSE_PROXY = "https://twse-proxy.grichtoyang.workers.dev"
TPEX_BASE = "https://www.tpex.org.tw/openapi/v1"


def fetch(url: str, timeout: int = 30):
    req = Request(url, headers={"accept": "application/json", "user-agent": "daily-pre-market-analysis/1.0"})
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
        for k, v in obj.items():
            if str(k).strip() in aliases:
                n = num(v)
                if n is not None: return n
        for v in obj.values():
            got = find(v, aliases)
            if got is not None: return got
    elif isinstance(obj, list):
        for v in obj:
            got = find(v, aliases)
            if got is not None: return got
    return None


def collect(date: str):
    sources = {}
    def get(name, url):
        try:
            payload, status = fetch(url)
            sources[name] = {"url": url, "status": status, "ok": True, "payload": payload}
            return payload
        except Exception as e:
            sources[name] = {"url": url, "status": None, "ok": False, "error": str(e)}
            return None

    twse = get("twse_proxy", f"{TWSE_PROXY}?date={date.replace('-', '')}")
    tpex_urls = {
        "tpex_breadth": f"{TPEX_BASE}/tpex_mainboard_daily_close_quotes",
        "tpex_margin": f"{TPEX_BASE}/tpex_mainboard_margin_balance",
        "tpex_sbl": f"{TPEX_BASE}/tpex_margin_sbl",
        "tpex_turnover": f"{TPEX_BASE}/tpex_mainboard_highlight",
    }
    tpex = {name: get(name, url) for name, url in tpex_urls.items()}
    d = twse.get("data", {}) if isinstance(twse, dict) else {}
    taiex = d.get("taiex") or {}
    stats = d.get("market_statistics") or {}
    breadth = d.get("advance_decline") or {}
    spot = {
        "taiex": {
            "close": find(taiex, {"close", "收盤指數", "收盤"}),
            "open": find(taiex, {"open", "開盤指數", "開盤"}),
            "high": find(taiex, {"high", "最高指數", "最高"}),
            "low": find(taiex, {"low", "最低指數", "最低"}),
            "change_points": find(taiex, {"change_points", "漲跌點數", "change"}),
            "change_percent": find(taiex, {"change_percent", "漲跌百分比", "change_pct"}),
            "turnover_value": find(stats, {"turnover_value", "成交金額(元)", "成交金額", "turnover"}),
        },
        "listed_breadth": {
            "up": find(breadth, {"up", "advance", "上漲家數"}),
            "down": find(breadth, {"down", "decline", "下跌家數"}),
            "unchanged": find(breadth, {"unchanged", "持平", "平盤家數"}),
            "limit_up": find(breadth, {"limit_up", "漲停家數"}),
            "limit_down": find(breadth, {"limit_down", "跌停家數"}),
        },
        "otc_breadth": {
            "up": find(tpex.get("tpex_breadth"), {"上漲家數", "上漲", "up"}),
            "down": find(tpex.get("tpex_breadth"), {"下跌家數", "下跌", "down"}),
            "unchanged": find(tpex.get("tpex_breadth"), {"平盤家數", "平盤", "unchanged"}),
            "limit_up": find(tpex.get("tpex_breadth"), {"漲停家數", "漲停", "limit_up"}),
            "limit_down": find(tpex.get("tpex_breadth"), {"跌停家數", "跌停", "limit_down"}),
        },
        "margin": {}, "sbl": {}, "turnover": {}
    }
    return {"ok": True, "source": "SPOT", "date": date, "retrieved_at": datetime.now(timezone.utc).isoformat(), "timezone": "UTC", "data": spot, "sources": sources}


def main():
    p = argparse.ArgumentParser(); p.add_argument("--date", required=True); p.add_argument("--output-root", default="data"); a = p.parse_args()
    payload = collect(a.date)
    out = Path(a.output_root) / "snapshots" / a.date / "spot-snapshot.json"
    out.parent.mkdir(parents=True, exist_ok=True); out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    stable = Path(a.output_root) / "spot" / f"{a.date}.json"; stable.parent.mkdir(parents=True, exist_ok=True); stable.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"date": a.date, "output": str(out), "ok": payload["ok"]}, ensure_ascii=False))

if __name__ == "__main__": sys.exit(main())
