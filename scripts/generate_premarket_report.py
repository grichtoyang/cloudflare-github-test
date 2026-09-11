#!/usr/bin/env python3
"""Generate the daily AI pre-market report from the canonical data package.

This report generator is intentionally independent of the separate V1.1 prompt.
It consumes only the immutable canonical pre-market package and its referenced
TAIFEX/TWSE snapshots, then sends that data to the OpenAI Responses API.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import date, datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

DEFAULT_MODEL = "gpt-5.6-luna"

SYSTEM_INSTRUCTIONS = """You are the automated analyst for a Taiwan pre-market report.
Use only the supplied canonical package and source snapshots. Do not invent
missing values. Clearly label missing, stale, inconsistent, or unavailable data.
Separate observed facts from interpretation and from scenario/risk assessment.
Focus on Taiwan equities, TAIEX, Taiwan index futures, institutional futures
positioning, options positioning, and the key option-derived levels contained
in the source data. Treat the report as market analysis, not personalized
financial advice.

Produce a concise but decision-useful Markdown report with these sections:
1. Executive Summary
2. Data Integrity / Session Context
3. Taiwan Market & Futures Positioning
4. Options Structure and Key Levels
5. Bullish / Bearish Evidence Matrix
6. Base Case, Bull Case, Bear Case
7. Key Levels and Invalidation Conditions
8. Risk Controls / What Would Change the View

When numerical values are available, preserve their units and identify the
source dataset. Never fabricate a value merely to complete a section.
"""


def read_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"{path} is not a JSON object")
    return value


def extract_text(response: dict) -> str:
    direct = response.get("output_text")
    if isinstance(direct, str) and direct.strip():
        return direct.strip()
    chunks: list[str] = []
    for item in response.get("output", []):
        if not isinstance(item, dict):
            continue
        for content in item.get("content", []):
            if isinstance(content, dict) and isinstance(content.get("text"), str) and content["text"].strip():
                chunks.append(content["text"].strip())
    if not chunks:
        raise RuntimeError("OpenAI response contained no text output")
    return "\n\n".join(chunks)


def call_openai(api_key: str, model: str, input_text: str, timeout: int) -> tuple[str, dict]:
    body = {"model": model, "instructions": SYSTEM_INSTRUCTIONS, "input": input_text}
    request = Request(
        "https://api.openai.com/v1/responses",
        data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json", "Accept": "application/json"},
        method="POST",
    )
    try:
        with urlopen(request, timeout=timeout) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"OpenAI API HTTP {exc.code}: {detail[:1000]}") from exc
    except (URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"OpenAI API request failed: {exc}") from exc
    return extract_text(payload), payload


def _existing_report_is_valid(report_path: Path, audit_path: Path, analysis_date: str) -> bool:
    """Return True only when both idempotent report artifacts are structurally valid."""
    try:
        if not report_path.is_file() or not audit_path.is_file():
            return False
        report_text = report_path.read_text(encoding="utf-8").strip()
        audit = read_json(audit_path)
        if not report_text.startswith(f"# 每日盤前分析 — {analysis_date}"):
            return False
        if audit.get("analysis_date") != analysis_date:
            return False
        if not audit.get("response_id") or not audit.get("model"):
            return False
        return True
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError):
        return False


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--analysis-date", default=date.today().isoformat())
    parser.add_argument("--output-root", default="data")
    parser.add_argument("--report-root", default="reports")
    parser.add_argument("--model", default=os.getenv("OPENAI_MODEL", DEFAULT_MODEL))
    parser.add_argument("--timeout", type=int, default=180)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    report_dir = Path(args.report_root)
    report_path = report_dir / f"premarket-{args.analysis_date}.md"
    audit_path = report_dir / f"premarket-{args.analysis_date}.meta.json"

    # Idempotency is accepted only after validating the existing artifacts.
    # A corrupt/partial pair must fall through to canonical-data validation and
    # regeneration rather than being treated as a successful prior run.
    if not args.force and _existing_report_is_valid(report_path, audit_path, args.analysis_date):
        print(json.dumps({"ok": True, "published": True, "status": "already_exists", "report": str(report_path), "audit": str(audit_path)}, ensure_ascii=False, indent=2))
        return 3

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("OPENAI_API_KEY is not configured", file=sys.stderr)
        return 2

    root = Path(args.output_root)
    package_path = root / "premarket" / f"{args.analysis_date}.json"
    if not package_path.exists():
        print(f"Canonical pre-market package not found: {package_path}", file=sys.stderr)
        return 1

    package = read_json(package_path)
    if package.get("ready_for_analysis") is not True or package.get("published") is not True:
        print("Canonical pre-market package is not ready/published", file=sys.stderr)
        return 1

    sources = package.get("sources", {})
    source_payloads: dict[str, dict] = {}
    for source_name in ("TAIFEX", "TWSE"):
        source = sources.get(source_name, {})
        snapshot_path = source.get("snapshot")
        if not snapshot_path:
            print(f"{source_name} snapshot reference missing", file=sys.stderr)
            return 1
        path = Path(snapshot_path)
        if not path.exists():
            print(f"{source_name} snapshot missing: {path}", file=sys.stderr)
            return 1
        snapshot = read_json(path)
        if snapshot.get("source") != source_name:
            print(f"{source_name} snapshot source mismatch: {path}", file=sys.stderr)
            return 1
        source_payloads[source_name] = snapshot

    input_package = {"analysis_date": args.analysis_date, "t0_trading_date": package.get("t0_trading_date"), "canonical_manifest": package, "sources": source_payloads}
    input_text = "Canonical pre-market data package follows as JSON. Analyze it exactly as supplied.\n\n" + json.dumps(input_package, ensure_ascii=False, separators=(",", ":"))
    report_text, response = call_openai(api_key, args.model, input_text, args.timeout)

    generated_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    report = (
        f"# 每日盤前分析 — {args.analysis_date}\n\n"
        f"> Generated automatically by GitHub Actions at {generated_at}.\n\n"
        f"**Model:** `{args.model}`  \n**T0:** `{package.get('t0_trading_date')}`  \n**Canonical package:** `{package_path}`\n\n---\n\n"
        f"{report_text.strip()}\n"
    )

    report_dir.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report, encoding="utf-8")
    audit = {"analysis_date": args.analysis_date, "t0_trading_date": package.get("t0_trading_date"), "generated_at": generated_at, "model": args.model, "report": str(report_path), "response_id": response.get("id"), "status": response.get("status")}
    audit_path.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"ok": True, "report": str(report_path), "audit": str(audit_path), "model": args.model, "response_id": response.get("id")}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
