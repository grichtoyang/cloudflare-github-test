#!/usr/bin/env python3
"""Validate the immutable ChatGPT AI-input handoff package.

This is a final L1 handoff gate. It verifies the canonical package identity,
the AI-input index, every referenced file, and every recorded SHA256 before
GitHub publishes the package as ready for ChatGPT consumption.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import date
from pathlib import Path

TAIFEX_ENDPOINTS = {
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
}


def read_json(path: Path) -> dict:
    if not path.exists() or path.stat().st_size <= 2:
        raise ValueError(f"missing or empty JSON file: {path}")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON root is not an object: {path}")
    return value


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    # Fail closed on CLI typos: do not silently accept abbreviated long options.
    parser = argparse.ArgumentParser(allow_abbrev=False)
    parser.add_argument("--analysis-date", required=True)
    parser.add_argument("--t0-date", required=True)
    parser.add_argument("--output-root", default="data/premarket")
    args = parser.parse_args()

    try:
        date.fromisoformat(args.analysis_date)
        date.fromisoformat(args.t0_date)
    except ValueError:
        print("invalid analysis/T0 date", file=sys.stderr)
        return 2

    root = Path(args.output_root)
    canonical_path = root / f"{args.analysis_date}.json"
    ai_root = root / args.analysis_date / "ai-input"
    index_path = ai_root / "index.json"
    errors: list[str] = []

    try:
        canonical = read_json(canonical_path)
        index = read_json(index_path)
    except Exception as exc:
        print(f"AI-input gate FAILED: {exc}", file=sys.stderr)
        return 1

    if canonical.get("analysis_date") != args.analysis_date:
        errors.append("canonical analysis_date mismatch")
    if canonical.get("t0_trading_date") != args.t0_date:
        errors.append("canonical t0_trading_date mismatch")
    if canonical.get("ready_for_analysis") is not True:
        errors.append("canonical ready_for_analysis != true")
    if canonical.get("published") is not True:
        errors.append("canonical published != true")

    actual_canonical_sha = sha256(canonical_path)
    if index.get("canonical_package") != str(canonical_path):
        errors.append("index canonical_package mismatch")
    if index.get("canonical_package_sha256") != actual_canonical_sha:
        errors.append("index canonical_package_sha256 mismatch")
    if index.get("analysis_date") != args.analysis_date:
        errors.append("index analysis_date mismatch")
    if index.get("t0_trading_date") != args.t0_date:
        errors.append("index t0_trading_date mismatch")

    files = index.get("files")
    if not isinstance(files, list):
        errors.append("index files is missing/not a list")
        files = []

    expected_names = {f"taifex-{name}.json" for name in TAIFEX_ENDPOINTS} | {"twse.json"}
    actual_names = {Path(str(item.get("path", ""))).name for item in files if isinstance(item, dict)}
    if actual_names != expected_names:
        missing = sorted(expected_names - actual_names)
        unexpected = sorted(actual_names - expected_names)
        if missing:
            errors.append(f"missing AI-input files: {missing}")
        if unexpected:
            errors.append(f"unexpected AI-input files: {unexpected}")

    if len(files) != len(expected_names):
        errors.append(f"AI-input file count={len(files)}, expected={len(expected_names)}")

    seen: set[str] = set()
    resolved_ai_root = ai_root.resolve()
    for item in files:
        if not isinstance(item, dict):
            errors.append("index contains non-object file entry")
            continue

        raw_path = str(item.get("path", ""))
        path = Path(raw_path)
        name = path.name
        if name in seen:
            errors.append(f"duplicate AI-input file: {name}")
        seen.add(name)

        # Index paths must resolve inside this analysis-date AI-input directory.
        # This prevents an otherwise valid SHA256 entry from escaping the
        # published package and pointing at an arbitrary repository file.
        resolved_path = path.resolve()
        try:
            resolved_path.relative_to(resolved_ai_root)
        except ValueError:
            errors.append(f"AI-input path outside package: {raw_path}")
            continue

        if not path.exists() or path.stat().st_size <= 2:
            errors.append(f"AI-input missing/empty: {path}")
            continue
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            errors.append(f"invalid JSON: {path}: {exc}")
            continue

        expected_sha = item.get("sha256")
        actual_sha = sha256(path)
        if expected_sha != actual_sha:
            errors.append(f"SHA256 mismatch: {path}")
        if item.get("bytes") != path.stat().st_size:
            errors.append(f"byte count mismatch: {path}")

        if name == "twse.json":
            if item.get("source") != "TWSE":
                errors.append("twse.json source mismatch")
            if item.get("endpoint") != "snapshot":
                errors.append("twse.json endpoint mismatch")
        elif name.startswith("taifex-"):
            if item.get("source") != "TAIFEX":
                errors.append(f"TAIFEX source mismatch: {name}")
            endpoint = str(item.get("endpoint", ""))
            expected_endpoint = name[len("taifex-") : -len(".json")]
            if endpoint not in TAIFEX_ENDPOINTS:
                errors.append(f"unknown TAIFEX endpoint: {endpoint}")
            elif endpoint != expected_endpoint:
                errors.append(f"TAIFEX filename/endpoint mismatch: {name} -> {endpoint}")

    result = {
        "ok": not errors,
        "analysis_date": args.analysis_date,
        "t0_trading_date": args.t0_date,
        "canonical_package": str(canonical_path),
        "ai_input_index": str(index_path),
        "expected_file_count": len(expected_names),
        "actual_file_count": len(files),
        "errors": errors,
        "ready_for_analysis": not errors,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
