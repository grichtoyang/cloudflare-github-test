#!/usr/bin/env python3
"""Build an immutable daily TWSE snapshot from the TWSE production proxy.

The proxy remains the primary source.  If it returns HTTP 200/fetch_ok but
its normalized core fields are null, fall back to the official TWSE MI_INDEX
endpoint and normalize the required TAIEX / market-statistics / breadth data.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
from datetime import date, datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

DEFAULT_BASE = "https://twse-proxy.grichtoyang.workers.dev"
LEGACY_BASE = "https://taiex-proxy.grichtoyang.workers.dev"
OFFICIAL_BASE = "https://www.twse.com.tw/exchangeReport/MI_INDEX"
REQUIRED_ENDPOINTS = ("IND", "MS")
REQUIRED_DATA = ("taiex", "market_statistics", "advance_decline")


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def fetch_json(url: str, retries: int, timeout: int) -> tuple[dict, int, int]:
    last_error = None
    for attempt in range(1, retries + 1):
        try:
            request = Request(url, headers={"accept": "application/json", "user-agent": "daily-pre-market-analysis/1.1"})
            with urlopen(request, timeout=timeout) as response:
                payload = json.loads(response.read().decode("utf-8"))
                if not isinstance(payload, dict):
                    raise ValueError("response JSON root must be an object")
                return payload, response.status, attempt
        except (HTTPError, URLError, TimeoutError, ValueError, json.JSONDecodeError) as exc:
            last_error = str(exc)
            if attempt < retries:
                time.sleep(2 ** (attempt - 1))
    raise RuntimeError(last_error or "unknown fetch error")


def fetch_official(url: str, retries: int, timeout: int) -> tuple[object, int, int]:
    last_error = None
    for attempt in range(1, retries + 1):
        try:
            request = Request(url, headers={"accept": "application/json", "user-agent": "daily-pre-market-analysis/1.1"})
            with urlopen(request, timeout=timeout) as response:
                payload = json.loads(response.read().decode("utf-8"))
                return payload, response.status, attempt
        except (HTTPError, URLError, TimeoutError, ValueError, json.JSONDecodeError) as exc:
            last_error = str(exc)
            if attempt < retries:
                time.sleep(2 ** (attempt - 1))
    raise RuntimeError(last_error or "unknown official TWSE fetch error")


def numeric(value):
    if value is None:
        return None
    text = str(value).strip().replace(",", "")
    if text in {"", "--", "---", "N/A", "－", "—"}:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def parse_signed(row: list, sign_index: int, value_index: int):
    value = numeric(row[value_index]) if len(row) > value_index else None
    sign = str(row[sign_index]).strip() if len(row) > sign_index else ""
    if value is not None and sign == "-":
        value = -abs(value)
    return value


def official_ind_to_taiex(payload: dict, target_date: str) -> dict | None:
    if not isinstance(payload, dict) or payload.get("stat") != "OK":
        return None
    rows = payload.get("data1") or []
    fields = payload.get("fields1") or []
    if not rows or not fields:
        return None
    try:
        idx = {name: i for i, name in enumerate(fields)}
        name_i = idx.get("指數")
        close_i = idx.get("收盤指數")
        sign_i = idx.get("漲跌")
        points_i = idx.get("漲跌點數")
        pct_i = idx.get("漲跌百分比")
        if None in (name_i, close_i, sign_i, points_i, pct_i):
            return None
        for row in rows:
            if str(row[name_i]).strip() == "發行量加權股價指數":
                return {
                    "date": target_date,
                    "index": "TAIEX",
                    "close": numeric(row[close_i]),
                    "change": parse_signed(row, sign_i, points_i),
                    "change_percent": parse_signed(row, sign_i, pct_i),
                    "source": "TWSE_OFFICIAL_MI_INDEX_IND",
                }
    except (TypeError, IndexError):
        return None
    return None


def official_ms_to_stats(payload: dict, target_date: str) -> tuple[dict | None, dict | None]:
    if not isinstance(payload, dict) or payload.get("stat") != "OK":
        return None, None
    rows = payload.get("data8") or []
    fields = payload.get("fields8") or []
    if not rows or not fields:
        return None, None
    try:
        idx = {name: i for i, name in enumerate(fields)}
        stat_i = idx.get("成交統計")
        amount_i = idx.get("成交金額(元)")
        volume_i = idx.get("成交股數(股)")
        trades_i = idx.get("成交筆數")
        stats = None
        if None not in (stat_i, amount_i, volume_i, trades_i):
            for row in rows:
                if str(row[stat_i]).strip().startswith("總計"):
                    stats = {
                        "date": target_date,
                        "turnover_value": numeric(row[amount_i]),
                        "volume_shares": numeric(row[volume_i]),
                        "transaction_count": numeric(row[trades_i]),
                        "source": "TWSE_OFFICIAL_MI_INDEX_MS",
                    }
                    break

        breadth = None
        # The MS table contains a separate breadth block.  Match by semantic
        # column names rather than relying on a fixed table row number.
        overall_i = idx.get("整體市場")
        type_i = idx.get("類型")
        if type_i is not None and overall_i is not None:
            for row in rows:
                label = str(row[type_i]).strip()
                if label == "上漲(漲停)":
                    up_text = str(row[overall_i]).strip()
                    up = numeric(up_text.split("(", 1)[0])
                    limit_up = numeric(up_text.split("(", 1)[1].rstrip(")")) if "(" in up_text else None
                    breadth = breadth or {"date": target_date, "source": "TWSE_OFFICIAL_MI_INDEX_MS"}
                    breadth["up"] = up
                    breadth["limit_up"] = limit_up
                elif label == "下跌(跌停)":
                    down_text = str(row[overall_i]).strip()
                    down = numeric(down_text.split("(", 1)[0])
                    limit_down = numeric(down_text.split("(", 1)[1].rstrip(")")) if "(" in down_text else None
                    breadth = breadth or {"date": target_date, "source": "TWSE_OFFICIAL_MI_INDEX_MS"}
                    breadth["down"] = down
                    breadth["limit_down"] = limit_down
                elif label == "持平":
                    breadth = breadth or {"date": target_date, "source": "TWSE_OFFICIAL_MI_INDEX_MS"}
                    breadth["unchanged"] = numeric(row[overall_i])
        return stats, breadth
    except (TypeError, IndexError):
        return None, None


def official_fallback(target_date: str, retries: int, timeout: int) -> tuple[dict, dict]:
    date8 = target_date.replace("-", "")
    ind_url = f"{OFFICIAL_BASE}?{urlencode({'response': 'json', 'date': date8, 'type': 'IND'})}"
    ms_url = f"{OFFICIAL_BASE}?{urlencode({'response': 'json', 'date': date8, 'type': 'MS'})}"
    ind, ind_status, ind_attempts = fetch_official(ind_url, retries, timeout)
    ms, ms_status, ms_attempts = fetch_official(ms_url, retries, timeout)
    taiex = official_ind_to_taiex(ind, target_date)
    stats, breadth = official_ms_to_stats(ms, target_date)
    if taiex is None or stats is None or breadth is None:
        raise RuntimeError(
            f"official TWSE fallback incomplete: IND status={ind_status}, MS status={ms_status}, "
            f"taiex={taiex is not None}, market_statistics={stats is not None}, advance_decline={breadth is not None}"
        )
    return {
        "taiex": taiex,
        "market_statistics": stats,
        "advance_decline": breadth,
    }, {
        "IND": {"status": ind_status, "fetch_ok": True, "attempts": ind_attempts, "source": "TWSE_OFFICIAL"},
        "MS": {"status": ms_status, "fetch_ok": True, "attempts": ms_attempts, "source": "TWSE_OFFICIAL"},
    }


def core_data_complete(payload: dict) -> bool:
    data = payload.get("data") if isinstance(payload, dict) else None
    if not isinstance(data, dict):
        return False
    return all(data.get(key) is not None for key in REQUIRED_DATA)


def validate(payload: dict, target_date: str) -> list[str]:
    errors = []
    if payload.get("ok") is not True:
        errors.append("ok != true")
    if payload.get("source") != "TWSE":
        errors.append("source != TWSE")
    if payload.get("date") != target_date:
        errors.append(f"date={payload.get('date')}, expected={target_date}")

    endpoints = payload.get("endpoints")
    if not isinstance(endpoints, dict):
        errors.append("endpoints missing")
    else:
        for name in REQUIRED_ENDPOINTS:
            endpoint = endpoints.get(name)
            if not isinstance(endpoint, dict):
                errors.append(f"endpoint {name} missing")
            elif endpoint.get("status") != 200 or endpoint.get("fetch_ok") is not True:
                errors.append(f"endpoint {name} not OK")

    data = payload.get("data")
    if not isinstance(data, dict):
        errors.append("data missing")
    else:
        for key in REQUIRED_DATA:
            if key not in data:
                errors.append(f"data.{key} missing")
            elif data.get(key) is None:
                errors.append(f"data.{key} is null")
    return errors


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", default=date.today().isoformat())
    parser.add_argument("--base-url", default=os.getenv("TWSE_PROXY_BASE_URL", DEFAULT_BASE))
    parser.add_argument("--output-root", default="data")
    parser.add_argument("--retries", type=int, default=3)
    parser.add_argument("--timeout", type=int, default=30)
    args = parser.parse_args(argv)

    try:
        date.fromisoformat(args.date)
    except ValueError:
        print(f"Invalid date: {args.date}", file=sys.stderr)
        return 2

    root = Path(args.output_root)
    stable = root / "twse" / f"{args.date}.json"
    stable_snapshot = root / "snapshots" / args.date / "twse-snapshot.json"
    stable_manifest = root / "manifests" / f"{args.date}.twse.json"
    if any(path.exists() for path in (stable, stable_snapshot, stable_manifest)):
        print(json.dumps({"date": args.date, "ready_for_analysis": False, "immutable_publication": "blocked", "reason": "stable artifact already exists"}, ensure_ascii=False, indent=2))
        return 3

    started = now_utc()
    url = args.base_url.rstrip("/")
    if url == LEGACY_BASE:
        print(json.dumps({"date": args.date, "ready_for_analysis": False, "error": f"legacy TWSE proxy URL is forbidden: {LEGACY_BASE}; use {DEFAULT_BASE}"}, ensure_ascii=False, indent=2), file=sys.stderr)
        return 2

    fallback_used = False
    fallback_error = None
    try:
        payload, status, attempts = fetch_json(url, args.retries, args.timeout)
        if not core_data_complete(payload):
            fallback_used = True
            normalized, fallback_endpoints = official_fallback(args.date, args.retries, args.timeout)
            payload = {
                "ok": True,
                "source": "TWSE",
                "proxy": url,
                "version": payload.get("version", "1.0.0"),
                "date": args.date,
                "endpoints": {
                    **payload.get("endpoints", {}),
                    **fallback_endpoints,
                },
                "data": normalized,
                "source_lineage": {
                    "primary": "TWSE_PROXY",
                    "fallback": "TWSE_OFFICIAL_MI_INDEX",
                    "fallback_used": True,
                    "reason": "proxy returned HTTP 200/fetch_ok but one or more normalized core fields were null",
                },
            }
        errors = validate(payload, args.date)
    except RuntimeError as exc:
        fallback_error = str(exc)
        payload = {"ok": False, "source": "TWSE", "date": args.date, "error": str(exc)}
        status, attempts, errors = 0, args.retries, [str(exc)]

    completed = now_utc()
    ready = not errors
    attempt_dir = root / "snapshots" / args.date / f"attempt-twse-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
    attempt_snapshot = attempt_dir / "twse-snapshot.json"
    attempt_manifest = attempt_dir / "manifest.json"

    snapshot = {
        "date": args.date,
        "timestamp": completed,
        "source": "TWSE",
        "proxy": url,
        "collector": "twse_snapshot.py",
        "collector_version": "1.1.0",
        "data": payload,
        "validation": {
            "required_endpoint_count": 2,
            "successful_endpoint_count": 2 if ready else 0,
            "errors": errors,
            "ready_for_analysis": ready,
            "fallback_used": fallback_used,
            "fallback_error": fallback_error,
        },
    }
    write_json(attempt_snapshot, snapshot)
    digest = hashlib.sha256(attempt_snapshot.read_bytes()).hexdigest()
    manifest = {
        "manifest_version": "1.1.0",
        "analysis_date": args.date,
        "fetch_started_at": started,
        "fetch_completed_at": completed,
        "source": "TWSE",
        "primary_source": url,
        "required_endpoints": list(REQUIRED_ENDPOINTS),
        "required_endpoint_count": 2,
        "successful_endpoint_count": 2 if ready else 0,
        "endpoint_status": payload.get("endpoints", {}),
        "validation": {"validation_errors": errors, "all_required_endpoints_ok": ready},
        "attempt_artifacts": {"snapshot": str(attempt_snapshot), "manifest": str(attempt_manifest), "snapshot_sha256": digest},
        "ready_for_analysis": ready,
        "fallback_used": fallback_used,
        "fallback_error": fallback_error,
    }
    write_json(attempt_manifest, manifest)

    if not ready:
        print(json.dumps({"date": args.date, "ready_for_analysis": False, "attempt": str(attempt_dir), "errors": errors, "fallback_used": fallback_used, "fallback_error": fallback_error}, ensure_ascii=False, indent=2))
        return 1

    write_json(stable, payload)
    write_json(stable_snapshot, snapshot)
    manifest["published"] = True
    manifest["published_snapshot"] = str(stable_snapshot)
    write_json(stable_manifest, manifest)
    print(json.dumps({"date": args.date, "ready_for_analysis": True, "published": True, "fallback_used": fallback_used, "snapshot": str(stable_snapshot), "manifest": str(stable_manifest)}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
