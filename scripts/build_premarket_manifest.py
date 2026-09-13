#!/usr/bin/env python3
"""Build the canonical immutable daily pre-market manifest."""
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

def validate_published_snapshot(path: Path, source: str, t0_date: str) -> list[str]:
    if not path.exists():
        return [f"{source} published snapshot missing: {path}"]
    if path.stat().st_size <= 2:
        return [f"{source} published snapshot is empty: {path}"]
    try:
        snapshot = read_json(path)
    except Exception as exc:
        return [f"{source} published snapshot invalid JSON: {exc}"]
    errors: list[str] = []
    if snapshot.get("source") != source:
        errors.append(f"{source} snapshot source mismatch")
    if snapshot.get("date") != t0_date:
        errors.append(f"{source} snapshot date mismatch")
    if snapshot.get("validation", {}).get("ready_for_analysis") is not True:
        errors.append(f"{source} snapshot ready_for_analysis != true")
    if not isinstance(snapshot.get("data"), dict) or not snapshot.get("data"):
        errors.append(f"{source} snapshot data is empty")
    return errors

def validate_source_manifest(path: Path, source: str, expected_data_date: str) -> tuple[bool, list[str], dict]:
    errors: list[str] = []
    if not path.exists():
        return False, [f"missing manifest: {path}"], {}
    try:
        manifest = read_json(path)
    except Exception as exc:
        return False, [f"cannot read {path}: {exc}"], {}
    if manifest.get("t0_trading_date") != expected_data_date:
        errors.append(f"{source} data_date mismatch")
    if manifest.get("source") != source:
        errors.append(f"{source} source mismatch")
    if manifest.get("ready_for_analysis") is not True:
        errors.append(f"{source} ready_for_analysis != true")
    if manifest.get("published") is not True:
        errors.append(f"{source} published != true")
    snapshot = manifest.get("published_snapshot")
    if not snapshot:
        errors.append(f"{source} published_snapshot missing")
    else:
        errors.extend(validate_published_snapshot(Path(snapshot), source, expected_data_date))
        expected_hash = manifest.get("snapshot_sha256")
        if expected_hash:
            actual_hash = sha256(Path(snapshot))
            if actual_hash != expected_hash:
                errors.append(f"{source} snapshot SHA256 mismatch")
    return not errors, errors, manifest

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", default=date.today().isoformat(), help="T0 trading date")
    parser.add_argument("--analysis-date", default=None, help="Taiwan calendar date for the pre-market analysis")
    parser.add_argument("--output-root", default="data")
    args = parser.parse_args(argv)
    try:
        date.fromisoformat(args.date)
        analysis_date = args.analysis_date or args.date
        date.fromisoformat(analysis_date)
    except ValueError:
        print(f"Invalid date: {args.date} / analysis date: {args.analysis_date}", file=sys.stderr)
        return 2
    t0_date = args.date
    root = Path(args.output_root)
    output = root / "premarket" / f"{analysis_date}.json"
    taifex_path = root / "manifests" / f"{t0_date}.json"
    twse_path = root / "manifests" / f"{t0_date}.twse.json"
    if output.exists():
        try:
            existing = read_json(output)
        except Exception:
            existing = {}
        if existing.get("ready_for_analysis") is True and existing.get("published") is True:
            print(json.dumps({"date": t0_date, "analysis_date": analysis_date, "ready_for_analysis": True, "immutable_publication": "blocked", "reason": "canonical pre-market package already exists"}, ensure_ascii=False, indent=2))
            return 3
        print(json.dumps({"date": t0_date, "analysis_date": analysis_date, "ready_for_analysis": False, "immutable_publication": "invalid", "reason": "invalid canonical pre-market package already exists"}, ensure_ascii=False, indent=2))
        return 1
    started = now_utc()
    taifex_ok, taifex_errors, taifex = validate_source_manifest(taifex_path, "TAIFEX", t0_date)
    twse_ok, twse_errors, twse = validate_source_manifest(twse_path, "TWSE", t0_date)
    errors = taifex_errors + twse_errors
    ready = taifex_ok and twse_ok
    completed = now_utc()
    manifest = {"manifest_version": "1.3.0", "manifest_type": "pre-market", "analysis_date": analysis_date, "t0_trading_date": t0_date, "created_at": completed, "fetch_started_at": started, "fetch_completed_at": completed, "sources": {"TAIFEX": {"ready_for_analysis": taifex_ok, "manifest": str(taifex_path), "snapshot": taifex.get("published_snapshot"), "snapshot_sha256": sha256(Path(taifex["published_snapshot"])) if taifex_ok else None}, "TWSE": {"ready_for_analysis": twse_ok, "manifest": str(twse_path), "snapshot": twse.get("published_snapshot"), "snapshot_sha256": sha256(Path(twse["published_snapshot"])) if twse_ok else None}}, "validation": {"required_sources": ["TAIFEX", "TWSE"], "successful_sources": [source for source, ok in (("TAIFEX", taifex_ok), ("TWSE", twse_ok)) if ok], "validation_errors": errors}, "ready_for_analysis": ready, "published": False}
    if not ready:
        attempt_dir = root / "snapshots" / t0_date / f"attempt-premarket-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
        attempt_manifest = attempt_dir / "manifest.json"
        attempt_dir.mkdir(parents=True, exist_ok=True)
        manifest["attempt_artifacts"] = {"manifest": str(attempt_manifest)}
        attempt_manifest.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        manifest["attempt_artifacts"]["manifest_sha256"] = sha256(attempt_manifest)
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
