#!/usr/bin/env python3
"""Build an immutable daily TAIFEX snapshot for the pre-market pipeline.

The Cloudflare Proxy owns upstream TAIFEX/OpenAPI fallback logic. This collector
owns collection retries, validation, immutable publication, and the
READY_FOR_ANALYSIS gate.

Date contract:
- Date-required historical endpoints are queried/validated against T0.
- Night-session endpoints are date-less and their response date is validated
  against Analysis Date, not T0.
- Date-less regular endpoints are not globally date-compared because the
  production Worker emits current-date metadata for those endpoints.
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
from urllib.request import Request, urlopen

from endpoint_date_policy import expected_response_date

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
    parser.add_argument("--date", default=date.today().isoformat(), help="T0 trading date")
    parser.add_argument(
        "--analysis-date",
        default=date.today().isoformat(),
        help="Taiwan analysis calendar date (D)",
    )
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


def run_id() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def endpoint_url(base: str, endpoint: str, target_date: str) -> str:
    if endpoint in DATE_ENDPOINTS:
        return f"{base.rstrip('/')}/{endpoint}?date={target_date}"
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


def validate_response(name: str, payload: dict, *, t0: str, analysis_date: str) -> list[str]:
    errors: list[str] = []
    if payload.get("ok") is not True:
        errors.append(f"{name}: ok != true")

    response_date = payload.get("date")
    expected_date = expected_response_date(name, t0=t0, analysis_date=analysis_date)
    if expected_date is not None and response_date and response_date != expected_date:
        errors.append(f"{name}: date={response_date}, expected={expected_date}")

    if "data" not in payload:
        errors.append(f"{name}: missing data")
    return errors


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def stable_paths(root: Path, target_date: str) -> tuple[Path, Path, Path]:
    return (
        root / "taifex" / f"{target_date}.json",
        root / "snapshots" / target_date / "snapshot.json",
        root / "manifests" / f"{target_date}.json",
    )


def main() -> int:
    args = parse_args()
    if not valid_date(args.date):
        print(f"Invalid T0 date: {args.date}", file=sys.stderr)
        return 2
    if not valid_date(args.analysis_date):
        print(f"Invalid analysis date: {args.analysis_date}", file=sys.stderr)
        return 2
    if args.retries < 1:
        print("--retries must be >= 1", file=sys.stderr)
        return 2

    root = Path(args.output_root)
    target_snapshot_dir = root / "snapshots" / args.date
    target_attempt_dir = target_snapshot_dir / f"attempt-{run_id()}"
    stable_taifex, stable_snapshot, stable_manifest = stable_paths(root, args.date)

    existing_stable = [p for p in (stable_taifex, stable_snapshot, stable_manifest) if p.exists()]
    if existing_stable:
        print(
            json.dumps(
                {
                    "date": args.date,
                    "analysis_date": args.analysis_date,
                    "ready_for_analysis": False,
                    "immutable_publication": "blocked",
                    "reason": "stable artifact already exists",
                    "existing": [str(p) for p in existing_stable],
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 3

    started = now_utc()
    results: dict[str, object] = {}
    endpoint_status: dict[str, object] = {}
    validation_errors: list[str] = []

    health_url = f"{args.base_url.rstrip('/')}/health"
    try:
        health, status, attempts = fetch_json(health_url, args.retries, args.timeout)
        health_ok = health.get("ok") is True
        endpoint_status["health"] = {"ok": health_ok, "status": status, "attempts": attempts, "url": health_url}
        if not health_ok:
            validation_errors.append("health: ok != true")
    except RuntimeError as exc:
        endpoint_status["health"] = {"ok": False, "url": health_url, "error": str(exc)}
        validation_errors.append(f"health: {exc}")

    for name in REQUIRED_ENDPOINTS:
        url = endpoint_url(args.base_url, name, args.date)
        try:
            payload, status, attempts = fetch_json(url, args.retries, args.timeout)
            errors = validate_response(name, payload, t0=args.date, analysis_date=args.analysis_date)
            validation_errors.extend(errors)
            results[name] = payload
            endpoint_status[name] = {
                "ok": not errors,
                "status": status,
                "attempts": attempts,
                "url": url,
                "source": payload.get("source"),
                "dataset": payload.get("dataset"),
                "response_date": payload.get("date"),
                "expected_response_date": expected_response_date(
                    name, t0=args.date, analysis_date=args.analysis_date
                ),
            }
        except RuntimeError as exc:
            endpoint_status[name] = {"ok": False, "url": url, "error": str(exc)}
            validation_errors.append(f"{name}: {exc}")

    completed = now_utc()
    all_ok = (
        endpoint_status.get("health", {}).get("ok", False)
        and not validation_errors
        and len(results) == len(REQUIRED_ENDPOINTS)
    )

    snapshot = {
        "date": args.date,
        "analysis_date": args.analysis_date,
        "timestamp": completed,
        "source": "TAIFEX",
        "proxy": args.base_url.rstrip("/"),
        "collector": "daily_snapshot.py",
        "collector_version": "1.2.0",
        "run_id": target_attempt_dir.name,
        "data": results,
        "validation": {
            "health": endpoint_status.get("health", {}).get("ok", False),
            "required_endpoint_count": len(REQUIRED_ENDPOINTS),
            "successful_endpoint_count": len(results),
            "errors": validation_errors,
            "ready_for_analysis": all_ok,
        },
    }

    attempt_snapshot = target_attempt_dir / "snapshot.json"
    attempt_manifest = target_attempt_dir / "manifest.json"
    write_json(attempt_snapshot, snapshot)

    snapshot_hash = sha256_file(attempt_snapshot)
    manifest = {
        "manifest_version": "1.2.0",
        "analysis_date": args.analysis_date,
        "t0_trading_date": args.date,
        "run_id": target_attempt_dir.name,
        "fetch_started_at": started,
        "fetch_completed_at": completed,
        "source": "TAIFEX",
        "primary_source": args.base_url.rstrip("/"),
        "required_endpoint_count": len(REQUIRED_ENDPOINTS),
        "successful_endpoint_count": len(results),
        "required_endpoints": REQUIRED_ENDPOINTS,
        "endpoint_status": endpoint_status,
        "validation": {
            "health_ok": endpoint_status.get("health", {}).get("ok", False),
            "all_required_endpoints_ok": len(results) == len(REQUIRED_ENDPOINTS) and not validation_errors,
            "validation_errors": validation_errors,
        },
        "freshness": {
            "collector_completed_at": completed,
            "response_dates": {
                name: status.get("response_date")
                for name, status in endpoint_status.items()
                if name != "health" and isinstance(status, dict)
            },
        },
        "fallback": {
            "handled_by": "TAIFEX Cloudflare Proxy",
            "status": "delegated_to_proxy",
        },
        "attempt_artifacts": {
            "snapshot": str(attempt_snapshot),
            "manifest": str(attempt_manifest),
            "snapshot_sha256": snapshot_hash,
        },
        "ready_for_analysis": all_ok,
    }
    write_json(attempt_manifest, manifest)

    if not all_ok:
        print(
            json.dumps(
                {
                    "date": args.date,
                    "analysis_date": args.analysis_date,
                    "ready_for_analysis": False,
                    "attempt": str(target_attempt_dir),
                    "successful_endpoint_count": len(results),
                    "required_endpoint_count": len(REQUIRED_ENDPOINTS),
                    "errors": validation_errors,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 1

    collisions = [p for p in (stable_taifex, stable_snapshot, stable_manifest) if p.exists()]
    if collisions:
        print(f"Immutable publication collision: {[str(p) for p in collisions]}", file=sys.stderr)
        return 3

    write_json(stable_taifex, snapshot)
    write_json(stable_snapshot, snapshot)

    stable_manifest_payload = dict(manifest)
    stable_manifest_payload["published"] = True
    stable_manifest_payload["published_snapshot"] = str(stable_snapshot)
    stable_manifest_payload["ready_for_analysis"] = True
    write_json(stable_manifest, stable_manifest_payload)

    print(
        json.dumps(
            {
                "date": args.date,
                "analysis_date": args.analysis_date,
                "ready_for_analysis": True,
                "published": True,
                "snapshot": str(stable_snapshot),
                "manifest": str(stable_manifest),
                "snapshot_sha256": snapshot_hash,
                "successful_endpoint_count": len(results),
                "required_endpoint_count": len(REQUIRED_ENDPOINTS),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
