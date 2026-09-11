#!/usr/bin/env python3
"""Build an immutable daily TWSE snapshot from the TAIEX/TWSE proxy."""

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

DEFAULT_BASE = "https://twse-proxy.grichtoyang.workers.dev"
LEGACY_BASE = "https://taiex-proxy.grichtoyang.workers.dev"
REQUIRED_ENDPOINTS = ("IND", "MS")
REQUIRED_DATA = ("taiex", "market_statistics", "advance_decline")


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def fetch_json(url: str, retries: int, timeout: int) -> tuple[dict, int, int]:
    last_error = None
    for attempt in range(1, retries + 1):
        try:
            request = Request(url, headers={"accept": "application/json", "user-agent": "daily-pre-market-analysis/1.0"})
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

    try:
        payload, status, attempts = fetch_json(url, args.retries, args.timeout)
        errors = validate(payload, args.date)
    except RuntimeError as exc:
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
        "collector_version": "1.0.0",
        "data": payload,
        "validation": {
            "required_endpoint_count": 2,
            "successful_endpoint_count": 2 if ready else 0,
            "errors": errors,
            "ready_for_analysis": ready,
        },
    }
    write_json(attempt_snapshot, snapshot)
    digest = hashlib.sha256(attempt_snapshot.read_bytes()).hexdigest()
    manifest = {
        "manifest_version": "1.0.0",
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
    }
    write_json(attempt_manifest, manifest)

    if not ready:
        print(json.dumps({"date": args.date, "ready_for_analysis": False, "attempt": str(attempt_dir), "errors": errors}, ensure_ascii=False, indent=2))
        return 1

    write_json(stable, payload)
    write_json(stable_snapshot, snapshot)
    manifest["published"] = True
    manifest["published_snapshot"] = str(stable_snapshot)
    write_json(stable_manifest, manifest)
    print(json.dumps({"date": args.date, "ready_for_analysis": True, "published": True, "snapshot": str(stable_snapshot), "manifest": str(stable_manifest)}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
