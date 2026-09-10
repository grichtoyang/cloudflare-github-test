#!/usr/bin/env python3
"""Build the daily TAIFEX snapshot used by the pre-market analysis pipeline.

Primary source: the production TAIFEX Cloudflare Proxy. The proxy itself owns
TAIFEX/OpenAPI fallback logic, so this collector does not duplicate upstream
parsers. The collector is intentionally dependency-free and writes a stable
snapshot plus a machine-readable manifest.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import date, datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

DEFAULT_BASE = "https://taifex.grichtoyang.workers.dev"
REQUIRED_ENDPOINTS = [
    "futures-institutional-after-hours",
    "futures-institutional",
    "futures-price",
    "futures-price-after-hours",
    "futures-institutional-oi",
    "futures-institutional-oi-history",
    "futures-options-chain",
    "options-delta",
    "options-key-levels",
    "options-gamma-levels",
    "options-market-structure",
    "options-market-structure-compact",
    "options-institutional",
    "options-institutional-after-hours",
    "options-after-hours",
]

DATE_ENDPOINTS = {
    "futures-institutional-oi",
    "futures-institutional-oi-history",
    "futures-options-chain",
    "options-delta",
    "options-key-levels",
    "options-gamma-levels",
    "options-market-structure",
    "options-market-structure-compact",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", default=date.today().isoformat())
    parser.add_argument("--base-url", default=os.getenv("TAIFEX_PROXY_BASE_URL", DEFAULT_BASE))
    parser.add_argument("--output-root", default="data")
    parser.add_argument("--retries", type=int, default=3)
    parser.add_argument("--timeout", type=int, default=30)
    return parser.parse_args()


def valid_date(value: str) -> bool:
    try:
        date.fromisoformat(value)
        return len(value) == 10
    except ValueError:
        return False


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def endpoint_url(base: str, endpoint: str, target_date: str) -> str:
    separator = "&" if "?" in endpoint else "?"
    if endpoint in DATE_ENDPOINTS:
        return f"{base.rstrip('/')}/{endpoint}{separator}date={target_date}"
    return f"{base.rstrip('/')}/{endpoint}"


def fetch_json(url: str, retries: int, timeout: int) -> tuple[dict, int, int]:
    last_error = None
    for attempt in range(1, retries + 1):
        try:
            request = Request(
                url,
                headers={
                    "accept": "application/json",
                    "user-agent": "daily-pre-market-analysis/1.0",
                },
            )
            with urlopen(request, timeout=timeout) as response:
                status = response.status
                payload = json.loads(response.read().decode("utf-8"))
                if not isinstance(payload, dict):
                    raise ValueError("response JSON root must be an object")
                return payload, status, attempt
        except (HTTPError, URLError, TimeoutError, ValueError, json.JSONDecodeError) as exc:
            last_error = str(exc)
            if attempt < retries:
                time.sleep(2 ** (attempt - 1))
    raise RuntimeError(last_error or "unknown fetch error")


def validate_response(name: str, payload: dict, target_date: str) -> list[str]:
    errors: list[str] = []
    if payload.get("ok") is not True:
        errors.append(f"{name}: ok != true")
    response_date = payload.get("date")
    if response_date and response_date != target_date:
        errors.append(f"{name}: date={response_date}, expected={target_date}")
    if "data" not in payload:
        errors.append(f"{name}: missing data")
    return errors


def main() -> int:
    args = parse_args()
    if not valid_date(args.date):
        print(f"Invalid date: {args.date}", file=sys.stderr)
        return 2

    root = Path(args.output_root)
    taifex_dir = root / "taifex"
    snapshot_dir = root / "snapshots"
    manifest_dir = root / "manifests"
    for directory in (taifex_dir, snapshot_dir, manifest_dir):
        directory.mkdir(parents=True, exist_ok=True)

    started = now_utc()
    results: dict[str, object] = {}
    endpoint_status: dict[str, object] = {}
    validation_errors: list[str] = []

    # Health is checked separately so a healthy proxy cannot be mistaken for
    # complete market data.
    health_url = f"{args.base_url.rstrip('/')}/health"
    try:
        health, status, attempts = fetch_json(health_url, args.retries, args.timeout)
        endpoint_status["health"] = {"ok": health.get("ok") is True, "status": status, "attempts": attempts}
    except RuntimeError as exc:
        endpoint_status["health"] = {"ok": False, "error": str(exc)}
        validation_errors.append(f"health: {exc}")

    for name in REQUIRED_ENDPOINTS:
        url = endpoint_url(args.base_url, name, args.date)
        try:
            payload, status, attempts = fetch_json(url, args.retries, args.timeout)
            errors = validate_response(name, payload, args.date)
            validation_errors.extend(errors)
            results[name] = payload
            endpoint_status[name] = {
                "ok": not errors,
                "status": status,
                "attempts": attempts,
                "url": url,
                "source": payload.get("source"),
                "dataset": payload.get("dataset"),
            }
        except RuntimeError as exc:
            endpoint_status[name] = {"ok": False, "url": url, "error": str(exc)}
            validation_errors.append(f"{name}: {exc}")

    completed = now_utc()
    all_ok = not validation_errors and len(results) == len(REQUIRED_ENDPOINTS)

    snapshot = {
        "date": args.date,
        "timestamp": completed,
        "source": "TAIFEX",
        "proxy": "taifex.grichtoyang.workers.dev",
        "collector": "daily_snapshot.py",
        "collector_version": "1.0.0",
        "data": results,
        "validation": {
            "health": endpoint_status.get("health", {}).get("ok", False),
            "required_endpoint_count": len(REQUIRED_ENDPOINTS),
            "successful_endpoint_count": len(results),
            "errors": validation_errors,
            "ready_for_analysis": all_ok,
        },
    }

    manifest = {
        "analysis_date": args.date,
        "fetch_started_at": started,
        "fetch_completed_at": completed,
        "source": "TAIFEX",
        "primary_source": args.base_url,
        "required_endpoints": REQUIRED_ENDPOINTS,
        "endpoint_status": endpoint_status,
        "fallback": {
            "handled_by": "TAIFEX Cloudflare Proxy",
            "status": "delegated_to_proxy",
        },
        "validation_errors": validation_errors,
        "ready_for_analysis": all_ok,
    }

    (taifex_dir / f"{args.date}.json").write_text(json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (snapshot_dir / f"{args.date}.json").write_text(json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (manifest_dir / f"{args.date}.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(json.dumps({
        "date": args.date,
        "ready_for_analysis": all_ok,
        "successful_endpoint_count": len(results),
        "required_endpoint_count": len(REQUIRED_ENDPOINTS),
        "errors": validation_errors,
    }, ensure_ascii=False, indent=2))
    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
