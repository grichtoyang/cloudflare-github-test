#!/usr/bin/env python3
"""Runtime date policy for TAIFEX snapshot validation."""

DATE_REQUIRED_ENDPOINTS = {
    "futures-institutional-oi",
    "futures-institutional-oi-history",
    "futures-options-chain",
    "options-delta",
    "options-key-levels",
    "options-gamma-levels",
    "options-market-structure",
    "options-market-structure-compact",
}

NIGHT_SESSION_ENDPOINTS = {
    "futures-price-after-hours",
    "futures-institutional-after-hours",
    "options-institutional-after-hours",
    "options-after-hours",
}


def expected_response_date(endpoint: str, *, t0: str, analysis_date: str) -> str | None:
    """Return the response date expected by the V1.1 runtime contract.

    Historical date-required endpoints use T0. Night-session endpoints use
    Analysis Date as their query/label date. Date-less regular endpoints are
    intentionally not compared with T0 because their worker response date is
    current-date metadata rather than a historical-date query contract.
    """
    if endpoint in DATE_REQUIRED_ENDPOINTS:
        return t0
    if endpoint in NIGHT_SESSION_ENDPOINTS:
        return analysis_date
    return None
