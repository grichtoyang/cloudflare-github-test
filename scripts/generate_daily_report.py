#!/usr/bin/env python3
"""Generate a data-only report from either DATA_SCHEMA.md packages or legacy TAIFEX JSON."""
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


def unwrap_dict(value: Any) -> Any:
    while isinstance(value, dict) and isinstance(value.get("data"), dict):
        value = value["data"]
    return value


def rows_for(value: Any) -> list[dict[str, Any]]:
    if isinstance(value, dict) and isinstance(value.get("records"), list):
        value = value["records"]
    elif isinstance(value, dict) and isinstance(value.get("data"), list):
        value = value["data"]
    if isinstance(value, list):
        return [row for row in value if isinstance(row, dict)]
    return []


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


def legacy_dataset(data: dict[str, Any], key: str) -> list[dict[str, Any]]:
    payload = unwrap_dict(data)
    if isinstance(payload, dict):
        return rows_for(payload.get(key))
    return []


def option_rows(data: dict[str, Any]) -> list[dict[str, Any]]:
    for dataset_id in (
        "taifex_options_chain",
        "taifex_options_market_structure",
        "taifex_options_key_levels",
    ):
        rows = schema_dataset(data, dataset_id)
        if rows:
            return rows

    found: list[list[dict[str, Any]]] = []
    for obj in walk(data):
        for key, value in obj.items():
            if any(term in key.lower() for term in ("option", "call", "put")):
                rows = rows_for(value)
                if rows:
                    found.append(rows)
    return found[0] if found else []


def row_table(rows: list[dict[str, Any]], columns: list[str] | None = None) -> str:
    if not rows:
        return "資料未取得。"
    if columns is None:
        columns = list(rows[0].keys())[:12]
    header = "| " + " | ".join(columns) + " |\n"
    sep = "| " + " | ".join(["---"] * len(columns)) + " |\n"
    body = ""
    for row in rows[:100]:
        body += "| " + " | ".join(fmt(row.get(col)) for col in columns) + " |\n"
    return header + sep + body


def generate(data: dict[str, Any], source_file: str) -> str:
    meta = data if isinstance(data, dict) else {}
    futures = schema_dataset(data, "taifex_futures_price") or legacy_dataset(data, "futures_price")
    institutional = legacy_dataset(data, "futures_institutional")
    institutional_oi = schema_dataset(data, "taifex_futures_institutional_oi") or legacy_dataset(data, "futures_institutional_oi")
    options = option_rows(data)

    date = meta.get("analysis_date") or meta.get("date") or Path(source_file).stem
    timestamp = meta.get("generated_at") or meta.get("timestamp") or "未提供"
    lines = [
        f"# 每日市場資料報告｜{date}",
        "",
        f"> 資料來源：`{source_file}`  ",
        f"> 產生時間：{datetime.now(timezone.utc).isoformat()}  ",
        f"> 原始資料時間戳：`{timestamp}`  ",
        "> 本報告僅整理資料，不提供交易判斷。",
        "",
        "## 1. 台指期行情", "", 
        row_table(futures, ["contract_month", "open", "high", "low", "close", "change", "change_percent", "total_volume", "open_interest"]),
        "",
        "## 2. 台指期法人交易", "",
        row_table(institutional, ["institution", "long_volume", "short_volume", "net_volume", "long_amount", "short_amount", "net_amount"]),
        "",
        "## 3. 台指期法人 OI", "",
        row_table(institutional_oi, ["institution", "long_open_interest", "short_open_interest", "net_open_interest"]),
        "",
        "## 4. 選擇權資料", "",
        row_table(options),
        "",
        "## 5. 資料完整性檢查", "",
        f"- 台指期行情筆數：{len(futures)}",
        f"- 法人交易筆數：{len(institutional)}",
        f"- 法人 OI 筆數：{len(institutional_oi)}",
        f"- 選擇權辨識筆數：{len(options)}",
        "",
        "## 6. 簡易圖表", "", "```text",
    ]
    if futures:
        for row in futures[:10]:
            lines.append(f"{str(row.get('contract_month', 'unknown')):>12} | 收盤 {fmt(row.get('close')):>10} | 成交量 {fmt(row.get('total_volume')):>10}")
    else:
        lines.append("無台指期行情可繪製。")
    lines += ["```", ""]
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", default=None)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    date = args.date or datetime.now().strftime("%Y-%m-%d")
    source = root / "data" / "taifex" / f"{date}.json"
    if not source.exists():
        raise SystemExit(f"找不到資料檔：{source}")
    with source.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    report_dir = root / "reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    output = report_dir / f"{date}.md"
    output.write_text(generate(data, str(source.relative_to(root))), encoding="utf-8")
    print(f"OK: {output.relative_to(root)}")


if __name__ == "__main__":
    main()
