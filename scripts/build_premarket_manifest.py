#!/usr/bin/env python3
"""Build the canonical immutable daily pre-market manifest.

Only a fully validated package is published to data/premarket/YYYY-MM-DD.json.
Failed validation is retained under data/snapshots/YYYY-MM-DD/attempt-premarket-*/
and never blocks a later retry.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import date, datetime, timezone
from pathlib import Path


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"{path} is not a JSON object")
    return value


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_source_manifest(path: Path, source: str, target_date: str) -> tuple[bool, list[str], dict]:
    errors: list[str] = []
    if not path.exists():
        return False, [f"missing manifest: {path}"], {}
    try:
        manifest = read_json(path)
    except Exception as exc:
        return False, [f"cannot read {path}: {exc}"], {}

    if manifest.get("analysis_date") != target_date:
        errors.append(f"{source} analysis_date mismatch")
    if manifest.get("source") != source:
        errors.append(f"{source} source mismatch")
    if manifest.get("ready_for_analysis") is not True:
        errors.append(f"{source} ready_for_analysis != true")
    if manifest.get("published") is not True:
        errors.append(f"{source} published != true")
    snapshot = manifest.get("published_snapshot")
    if not snapshot:
        errors.append(f"{source} published_snapshot missing")
    elif not Path(snapshot).exists():
        errors.append(f"{source} published snapshot missing: {snapshot}")
    return not errors, errors, manifest


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", default=date.today().isoformat())
    parser.add_argument("--output-root", default="data")
    args = parser.parse_args()

    try:
        date.fromisoformat(args.date)
    except ValueError:
        print(f"Invalid date: {args.date}", file=sys.stderr)
        return 2

    root = Path(args.output_root)
    output = root / "premarket" / f"{args.date}.json"
    taifex_path = root / "manifests" / f"{args.date}.json"
    twse_path = root / "manifests" / f"{args.date}.twse.json"

    # A published package is immutable. A failed attempt is never written to
    # this canonical path, so failed runs can always be retried.
    if output.exists():
        try:
            existing = read_json(output)
        except Exception:
            existing = {}
        if existing.get("ready_for_analysis") is True and existing.get("published") is True:
            print(json.dumps({"date": args.date, "ready_for_analysis": False, "immutable_publication": "blocked", "reason": "canonical pre-market package already exists"}, ensure_ascii=False, indent=2))
            return 3
        print(json.dumps({"date": args.date, "ready_for_analysis": False, "immutable_publication": "blocked", "reason": "invalid canonical pre-market package already exists"}, ensure_ascii=False, indent=2))
        return 3

    started = now_utc()
    taifex_ok, taifex_errors, taifex = validate_source_manifest(taifex_path, "TAIFEX", args.date)
    twse_ok, twse_errors, twse = validate_source_manifest(twse_path, "TWSE", args.date)
    errors = taifex_errors + twse_errors
    ready = taifex_ok and twse_ok
    completed = now_utc()

    manifest = {
        "manifest_version": "1.1.0",
        "manifest_type": "pre-market",
        "analysis_date": args.date,
        "created_at": completed,
        "fetch_started_at": started,
        "fetch_completed_at": completed,
        "sources": {
            "TAIFEX": {
                "ready_for_analysis": taifex_ok,
                "manifest": str(taifex_path),
                "snapshot": taifex.get("published_snapshot"),
                "snapshot_sha256": sha256(Path(taifex["published_snapshot"])) if taifex_ok else None,
            },
            "TWSE": {
                "ready_for_analysis": twse_ok,
                "manifest": str(twse_path),
                "snapshot": twse.get("published_snapshot"),
                "snapshot_sha256": sha256(Path(twse["published_snapshot"])) if twse_ok else None,
            },
        },
        "validation": {
            "required_sources": ["TAIFEX", "TWSE"],
            "successful_sources": [source for source, ok in (("TAIFEX", taifex_ok), ("TWSE", twse_ok)) if ok],
            "validation_errors": errors,
        },
        "ready_for_analysis": ready,
        "published": False,
    }

    if not ready:
        attempt_dir = root / "snapshots" / args.date / f"attempt-premarket-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
        attempt_manifest = attempt_dir / "manifest.json"
        attempt_dir.mkdir(parents=True, exist_ok=True)
        attempt_manifest.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        manifest["attempt_artifacts"] = {"manifest": str(attempt_manifest), "manifest_sha256": sha256(attempt_manifest)}
        attempt_manifest.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(manifest, ensure_ascii=False, indent=2))
        return 1

    manifest["published"] = True
    manifest["ready_for_analysis"] = True
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
