#!/usr/bin/env python3
"""Publish connector-friendly, read-only AI input files from the canonical package.

No AI API is called here. The full immutable TAIFEX/TWSE snapshots remain the
source of truth; this script only splits their endpoint payloads into smaller
JSON files so a later ChatGPT prompt can read the GitHub data directly.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"{path} is not a JSON object")
    return value


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def compact_bytes(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, separators=(",", ":")) + "\n").encode("utf-8")


def write_compact(path: Path, value: object) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(compact_bytes(value))
    return file_sha256(path)


def safe_name(name: str) -> str:
    return "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in name)


def existing_is_valid(index_path: Path, canonical_sha: str, out_dir: Path) -> bool:
    if not index_path.exists():
        return False
    try:
        index = read_json(index_path)
    except Exception:
        return False
    if index.get("canonical_package_sha256") != canonical_sha:
        return False
    files = index.get("files")
    if not isinstance(files, list) or not files:
        return False
    for item in files:
        if not isinstance(item, dict):
            return False
        path = Path(str(item.get("path", "")))
        if not path.exists() or path.stat().st_size <= 2:
            return False
        if item.get("sha256") != file_sha256(path):
            return False
    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--analysis-date", required=True)
    parser.add_argument("--t0-date", required=True)
    parser.add_argument("--output-root", default="data/premarket")
    args = parser.parse_args()

    canonical_path = Path(args.output_root) / f"{args.analysis_date}.json"
    if not canonical_path.exists():
        print(f"canonical package missing: {canonical_path}", file=sys.stderr)
        return 1

    canonical = read_json(canonical_path)
    canonical_sha = file_sha256(canonical_path)
    if canonical.get("analysis_date") != args.analysis_date:
        print("canonical analysis_date mismatch", file=sys.stderr)
        return 1
    if canonical.get("t0_trading_date") != args.t0_date:
        print("canonical t0_trading_date mismatch", file=sys.stderr)
        return 1
    if canonical.get("ready_for_analysis") is not True or canonical.get("published") is not True:
        print("canonical package is not ready/published", file=sys.stderr)
        return 1

    sources = canonical.get("sources")
    if not isinstance(sources, dict):
        print("canonical sources missing", file=sys.stderr)
        return 1

    out_dir = Path(args.output_root) / args.analysis_date / "ai-input"
    out_dir.mkdir(parents=True, exist_ok=True)
    index_path = out_dir / "index.json"

    if existing_is_valid(index_path, canonical_sha, out_dir):
        print(json.dumps({
            "ok": True,
            "status": 3,
            "analysis_date": args.analysis_date,
            "t0_trading_date": args.t0_date,
            "output_dir": str(out_dir),
            "index": str(index_path),
            "reason": "AI input package already exists and passed integrity validation",
        }, ensure_ascii=False, indent=2))
        return 3

    files: list[dict[str, object]] = []

    # TAIFEX: one compact JSON per endpoint. This preserves every endpoint's
    # payload while avoiding one oversized connector response.
    taifex_ref = sources.get("TAIFEX", {}).get("snapshot")
    if not taifex_ref:
        print("TAIFEX snapshot reference missing", file=sys.stderr)
        return 1
    taifex_path = Path(taifex_ref)
    taifex = read_json(taifex_path)
    if taifex.get("source") != "TAIFEX" or taifex.get("date") != args.t0_date:
        print("TAIFEX snapshot identity mismatch", file=sys.stderr)
        return 1
    if taifex.get("validation", {}).get("ready_for_analysis") is not True:
        print("TAIFEX snapshot is not ready", file=sys.stderr)
        return 1
    taifex_data = taifex.get("data")
    if not isinstance(taifex_data, dict) or not taifex_data:
        print("TAIFEX endpoint data missing", file=sys.stderr)
        return 1

    for endpoint, payload in taifex_data.items():
        filename = f"taifex-{safe_name(str(endpoint))}.json"
        target = out_dir / filename
        digest = write_compact(target, payload)
        files.append({
            "source": "TAIFEX",
            "endpoint": endpoint,
            "path": str(target),
            "bytes": target.stat().st_size,
            "sha256": digest,
        })

    # TWSE is already small enough to remain one connector-friendly file.
    twse_ref = sources.get("TWSE", {}).get("snapshot")
    if not twse_ref:
        print("TWSE snapshot reference missing", file=sys.stderr)
        return 1
    twse_path = Path(twse_ref)
    twse = read_json(twse_path)
    if twse.get("source") != "TWSE" or twse.get("date") != args.t0_date:
        print("TWSE snapshot identity mismatch", file=sys.stderr)
        return 1
    if twse.get("validation", {}).get("ready_for_analysis") is not True:
        print("TWSE snapshot is not ready", file=sys.stderr)
        return 1
    target = out_dir / "twse.json"
    digest = write_compact(target, twse.get("data"))
    files.append({
        "source": "TWSE",
        "endpoint": "snapshot",
        "path": str(target),
        "bytes": target.stat().st_size,
        "sha256": digest,
    })

    index = {
        "version": "1.0.0",
        "type": "premarket-ai-input-index",
        "analysis_date": args.analysis_date,
        "t0_trading_date": args.t0_date,
        "created_at": now_utc(),
        "canonical_package": str(canonical_path),
        "canonical_package_sha256": canonical_sha,
        "source_of_truth": {
            "TAIFEX_snapshot": str(taifex_path),
            "TWSE_snapshot": str(twse_path),
        },
        "files": files,
    }
    write_compact(index_path, index)

    print(json.dumps({
        "ok": True,
        "status": 0,
        "analysis_date": args.analysis_date,
        "t0_trading_date": args.t0_date,
        "output_dir": str(out_dir),
        "file_count": len(files),
        "index": str(index_path),
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
