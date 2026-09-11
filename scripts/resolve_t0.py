#!/usr/bin/env python3
"""Resolve the latest completed TAIFEX trading date for a pre-market run."""

from __future__ import annotations

import json
import sys
import time
from datetime import date, datetime, timedelta, timezone
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

BASE = "https://taifex.grichtoyang.workers.dev"
PROBE_ENDPOINT = "futures-institutional-oi"
MAX_LOOKBACK_DAYS = 10


def taipei_today() -> date:
    # GitHub Actions runners use UTC; obtain the Taiwan calendar date explicitly.
    from zoneinfo import ZoneInfo
    return datetime.now(ZoneInfo("Asia/Taipei")).date()


def probe(target: date) -> bool:
    url = f"{BASE}/{PROBE_ENDPOINT}?date={target.isoformat()}"
    for attempt in range(3):
        try:
            req = Request(url, headers={"accept": "application/json", "user-agent": "daily-pre-market-analysis/1.0"})
            with urlopen(req, timeout=30) as response:
                payload = json.loads(response.read().decode("utf-8"))
            return (
                isinstance(payload, dict)
                and payload.get("ok") is True
                and payload.get("date") == target.isoformat()
                and bool(payload.get("data"))
            )
        except (HTTPError, URLError, TimeoutError, ValueError, json.JSONDecodeError):
            if attempt < 2:
                time.sleep(2 ** attempt)
    return False


def main() -> int:
    analysis_date = taipei_today()
    candidate = analysis_date - timedelta(days=1)
    for _ in range(MAX_LOOKBACK_DAYS):
        if probe(candidate):
            print(candidate.isoformat())
            return 0
        candidate -= timedelta(days=1)
    print("Unable to resolve T0 within lookback window", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
