#!/usr/bin/env python3
"""Generate a data-only report from the official premarket snapshot."""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def fmt(value: Any) -> str:
    if value is None or value == "":
        return "—"
    if isinstance(value, float):
        return f"{value:,.2f}"
    if isinstance(value, int):
        return f"{value:,}"
    return str(value)


def rows_for(value: Any) -> list[dict[str, Any]]:
    if isinstance(value, dict):
        for key in ("records", "data"):
            if isinstance(value.get(key), list):
                value = value[key]
                break
    return [row for row in value if isinstance(row, dict)] if isinstance(value, list) else []


def walk(obj: Any):
    if isinstance(obj, dict):
        yield obj
        for value in obj.values():
            yield from walk(value)
    elif isinstance(obj, list):
        for value in obj:
            yield from walk(value)


def schema_dataset(data: dict[str, Any], dataset_id: str) -> list[dict[str, Any]]:
    for obj in walk(data):
        if obj.get("dataset_id") == dataset_id:
            return rows_for(obj)
    return []


def find_endpoint(data: dict[str, Any], names: tuple[str, ...]) -> list[dict[str, Any]]:
    for obj in walk(data):
        for key, value in obj.items():
            normalized = key.lower().replace("_", "-")
            if normalized in names:
                rows = rows_for(value)
                if rows:
                    return rows
    return []


def load_source(root: Path, report_date: str) -> tuple[dict[str, Any], Path]:
    # Official chain: premarket manifest -> snapshot path.
    manifest = root / "data" / "premarket" / f"{report_date}.json"
    if manifest.exists():
        manifest_data = json.loads(manifest.read_text(encoding="utf-8"))
        for obj in walk(manifest_data):
            for key, value in obj.items():
                if key in ("snapshot", "snapshot_path", "published_snapshot") and isinstance(value, str):
                    candidate = root / value if not Path(value).is_absolute() else Path(value)
                    if candidate.exists():
                        return json.loads(candidate.read_text(encoding="utf-8")), candidate
    # Direct official snapshot fallback.
    for candidate in sorted((root / "data" / "snapshots").glob("*/snapshot.json"), reverse=True):
        if candidate.exists():
            return json.loads(candidate.read_text(encoding="utf-8")), candidate
    # Legacy fallback retained only for compatibility.
    legacy = root / "data" / "taifex" / f"{report_date}.json"
    if legacy.exists():
        return json.loads(legacy.read_text(encoding="utf-8")), legacy
    raise SystemExit(f"找不到正式 snapshot 或 legacy 資料：{report_date}")


def row_table(rows: list[dict[str, Any]], columns: list[str] | None = None) -> str:
    if not rows:
        return "資料未取得。"
    columns = columns or list(rows[0].keys())[:12]
    text = "| " + " | ".join(columns) + " |\n| " + " | ".join(["---"] * len(columns)) + " |\n"
    for row in rows[:100]:
        text += "| " + " | ".join(fmt(row.get(col)) for col in columns) + " |\n"
    return text


def generate(data: dict[str, Any], source_file: str, report_date: str) -> str:
    futures = schema_dataset(data, "taifex_futures_price") or find_endpoint(data, ("futures-price", "futures_price"))
    institutional = schema_dataset(data, "taifex_futures_institutional") or find_endpoint(data, ("futures-institutional", "futures_institutional"))
    institutional_oi = schema_dataset(data, "taifex_futures_institutional_oi") or find_endpoint(data, ("futures-institutional-oi", "futures_institutional_oi"))
    options = schema_dataset(data, "taifex_options_chain") or find_endpoint(data, ("futures-options-chain", "options-chain", "options_chain"))
    if not options:
        options = find_endpoint(data, ("options-delta", "options-key-levels", "options-gamma-levels", "options-market-structure", "options_market_structure"))
    timestamp = data.get("timestamp") or data.get("generated_at") or "未提供"
    lines = [f"# 每日市場資料報告｜{report_date}", "", f"> 資料來源：`{source_file}`  ", f"> 產生時間：{datetime.now(timezone.utc).isoformat()}  ", f"> 原始資料時間戳：`{timestamp}`  ", "> 本報告僅整理資料，不提供交易判斷。", "", "## 1. 台指期行情", "", row_table(futures, ["contract_month", "open", "high", "low", "close", "change", "change_percent", "total_volume", "open_interest"]), "", "## 2. 台指期法人交易", "", row_table(institutional), "", "## 3. 台指期法人 OI", "", row_table(institutional_oi), "", "## 4. 選擇權資料", "", row_table(options), "", "## 5. 資料完整性檢查", f"- 台指期行情筆數：{len(futures)}", f"- 法人交易筆數：{len(institutional)}", f"- 法人 OI 筆數：{len(institutional_oi)}", f"- 選擇權辨識筆數：{len(options)}", "", "## 6. 簡易圖表", "", "```text"]
    lines += [f"{str(row.get('contract_month', 'unknown')):>12} | 收盤 {fmt(row.get('close')):>10} | 成交量 {fmt(row.get('total_volume')):>10}" for row in futures[:10]] or ["無台指期行情可繪製。"]
    lines += ["```", ""]
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    data, source = load_source(root, args.date)
    output = root / "reports" / f"{args.date}.md"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(generate(data, str(source.relative_to(root)), args.date), encoding="utf-8")
    print(f"OK: {output.relative_to(root)}; source={source.relative_to(root)}")


if __name__ == "__main__":
    main()
