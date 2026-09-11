#!/usr/bin/env python3
"""Resolve the latest completed TAIFEX trading date for a pre-market run.

The resolver must never silently fall back to an older trading day when the
immediately preceding calendar day was a trading day whose data is simply not
ready yet. It therefore uses a bounded weekday search and treats a failed
probe on the most recent weekday as a hard not-ready condition.
"""

from __future__ import annotations

import json
import sys
import time
from datetime import date, datetime, timedelta
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo

BASE = "https://taifex.grichtoyang.workers.dev"
PROBE_ENDPOINT = "futures-options-chain"
MAX_LOOKBACK_DAYS = 10


def taipei_today() -> date:
    return datetime.now(ZoneInfo("Asia/Taipei")).date()


def probe(target: date) -> tuple[bool, str]:
    """Return (ready, reason) for the target date."""
    url = f"{BASE}/{PROBE_ENDPOINT}?date={target.isoformat()}"
    last_reason = "unknown error"
    for attempt in range(3):
        try:
            req = Request(
                url,
                headers={
                    "accept": "application/json",
                    "user-agent": "daily-pre-market-analysis/1.0",
                },
            )
            with urlopen(req, timeout=30) as response:
                payload = json.loads(response.read().decode("utf-8"))
            if (
                isinstance(payload, dict)
                and payload.get("ok") is True
                and payload.get("date") == target.isoformat()
                and bool(payload.get("data"))
            ):
                return True, "ready"
            last_reason = "invalid or incomplete TAIFEX response"
        except (HTTPError, URLError, TimeoutError, ValueError, json.JSONDecodeError) as exc:
            last_reason = str(exc)
        if attempt < 2:
            time.sleep(2 ** attempt)
    return False, last_reason


def main() -> int:
    analysis_date = taipei_today()
    candidate = analysis_date - timedelta(days=1)

    # Weekend days are not trading days, so walk past them. For the first
    # weekday candidate, however, a failed probe means the expected previous
    # trading day's data is not ready; never silently use an older date.
    checked = 0
    while checked < MAX_LOOKBACK_DAYS:
        if candidate.weekday() >= 5:
            candidate -= timedelta(days=1)
            checked += 1
            continue

        ready, reason = probe(candidate)
        if ready:
            print(candidate.isoformat())
            return 0

        print(
            f"T0 candidate {candidate.isoformat()} is not ready: {reason}",
            file=sys.stderr,
        )
        print(
            "Refusing to fall back to an older trading day; previous trading-day data is not ready.",
            file=sys.stderr,
        )
        return 1

    print("Unable to resolve T0 within lookback window", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
