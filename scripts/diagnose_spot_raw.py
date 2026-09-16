#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

TWSE_API = "https://openapi.twse.com.tw/v1"
TWSE_RWD = "https://www.twse.com.tw/rwd/zh"
TPEX_API = "https://www.tpex.org.tw/openapi/v1"


def request_json(url: str):
    request = Request(url, headers={"accept": "application/json", "user-agent": "daily-pre-market-analysis-raw-diagnostic/1.0"})
    try:
        with urlopen(request, timeout=45) as response:
            body = response.read().decode("utf-8", errors="replace")
            try:
                payload = json.loads(body)
                return {"url": url, "ok": True, "http_status": getattr(response, "status", 200), "content_type": response.headers.get("content-type"), "json_type": type(payload).__name__, "payload": payload}
            except json.JSONDecodeError as exc:
                return {"url": url, "ok": False, "http_status": getattr(response, "status", 200), "content_type": response.headers.get("content-type"), "error": f"invalid_json: {exc}", "body_prefix": body[:1000]}
    except Exception as exc:
        return {"url": url, "ok": False, "error": f"request_error: {exc}"}


def twse_rwd(path: str, date8: str, extra: dict | None = None) -> str:
    query = {"date": date8, "response": "json"}
    if extra:
        query.update(extra)
    return f"{TWSE_RWD}/{path}?{urlencode(query)}"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", required=True)
    parser.add_argument("--output-root", default="data/raw")
    args = parser.parse_args()
    date8 = args.date.replace("-", "")
    output = Path(args.output_root)
    output.mkdir(parents=True, exist_ok=True)

    endpoints = {
        "twse_mi_index": f"{TWSE_API}/exchangeReport/MI_INDEX?date={date8}&type=IND",
        "twse_mi_index_ms": f"{TWSE_API}/exchangeReport/MI_INDEX?date={date8}&type=MS",
        "twse_listed_breadth": f"{TWSE_API}/exchangeReport/twtazu_od?date={date8}",
        "twse_t86": twse_rwd("fund/T86", date8, {"selectType": "ALL"}),
        "twse_margin": f"{TWSE_API}/exchangeReport/MI_MARGN?date={date8}",
        "twse_sbl": f"{TWSE_API}/SBL/TWT96U?date={date8}",
        "twse_turnover": f"{TWSE_API}/exchangeReport/FMTQIK?date={date8}",
        "tpex_quotes": f"{TPEX_API}/tpex_mainboard_quotes?date={date8}",
        "tpex_margin": f"{TPEX_API}/tpex_mainboard_margin_balance?date={date8}",
        "tpex_sbl": f"{TPEX_API}/tpex_margin_sbl?date={date8}",
        "tpex_highlight": f"{TPEX_API}/tpex_mainborad_highlight?date={date8}",
    }

    summary = {"source": "SPOT_RAW_DIAGNOSTIC", "date": args.date, "retrieved_at": datetime.now(timezone.utc).isoformat(), "timezone": "UTC", "endpoints": {}}
    for name, url in endpoints.items():
        result = request_json(url)
        target = output / f"{name}_{args.date}.json"
        target.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        payload = result.get("payload")
        summary["endpoints"][name] = {"url": url, "ok": result.get("ok", False), "http_status": result.get("http_status"), "content_type": result.get("content_type"), "json_type": result.get("json_type"), "top_level_keys": list(payload.keys()) if isinstance(payload, dict) else None, "list_length": len(payload) if isinstance(payload, list) else None, "file": str(target), "error": result.get("error")}
    (output / f"summary_{args.date}.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
