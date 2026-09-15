#!/usr/bin/env python3
"""Generate a data-only daily market report from data/taifex/YYYY-MM-DD.json."""
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
    """Unwrap service containers whose data member is another dictionary."""
    while isinstance(value, dict) and isinstance(value.get("data"), dict):
        value = value["data"]
    return value


def rows_for(value: Any) -> list[dict[str, Any]]:
    """Read rows from either a direct list or a dataset wrapper with data=list."""
    if isinstance(value, dict) and isinstance(value.get("data"), list):
        value = value["data"]
    elif isinstance(value, dict):
        value = unwrap_dict(value)
        if isinstance(value, dict) and isinstance(value.get("data"), list):
            value = value["data"]
    if isinstance(value, list):
        return [row for row in value if isinstance(row, dict)]
    return []


def find_lists(obj: Any, key_terms: tuple[str, ...], found: list[list[dict[str, Any]]]) -> None:
    if isinstance(obj, dict):
        for key, value in obj.items():
            if isinstance(value, list) and any(term in key.lower() for term in key_terms):
                rows = [row for row in value if isinstance(row, dict)]
                if rows:
                    found.append(rows)
            find_lists(value, key_terms, found)
    elif isinstance(obj, list):
        for item in obj:
            find_lists(item, key_terms, found)


def first_list(data: dict[str, Any], names: tuple[str, ...]) -> list[dict[str, Any]]:
    found: list[list[dict[str, Any]]] = []
    find_lists(data, names, found)
    return found[0] if found else []


def row_table(rows: list[dict[str, Any]], columns: list[str]) -> str:
    if not rows:
        return "資料未取得。"
    header = "| " + " | ".join(columns) + " |\n"
    sep = "| " + " | ".join(["---"] * len(columns)) + " |\n"
    body = ""
    for row in rows[:100]:
        body += "| " + " | ".join(fmt(row.get(col)) for col in columns) + " |\n"
    return header + sep + body


def generate(data: dict[str, Any], source_file: str) -> str:
    meta = data if isinstance(data, dict) else {}
    payload = unwrap_dict(data)
    if not isinstance(payload, dict):
        payload = {}

    futures = rows_for(payload.get("futures_price"))
    institutional = rows_for(payload.get("futures_institutional"))
    institutional_oi = rows_for(payload.get("futures_institutional_oi"))
    options = first_list(payload, ("option", "options", "call", "put"))

    date = meta.get("date") or Path(source_file).stem
    timestamp = meta.get("timestamp", "未提供")
    lines = [
        f"# 每日市場資料報告｜{date}",
        "",
        f"> 資料來源：`{source_file}`  ",
        f"> 產生時間：{datetime.now(timezone.utc).isoformat()}  ",
        f"> 原始資料時間戳：`{timestamp}`  ",
        "> 本報告僅整理資料，不提供交易判斷。",
        "",
        "## 1. 台指期行情",
        "",
        row_table(futures, ["contract_month", "open", "high", "low", "close", "change", "change_percent", "total_volume", "open_interest"]),
        "",
        "## 2. 台指期法人交易",
        "",
        row_table(institutional, ["institution", "long_volume", "short_volume", "net_volume", "long_amount", "short_amount", "net_amount"]),
        "",
        "## 3. 台指期法人 OI",
        "",
        row_table(institutional_oi, ["institution", "long_open_interest", "short_open_interest", "net_open_interest"]),
        "",
        "## 4. 選擇權資料",
        "",
    ]
    if options:
        cols = list(options[0].keys())[:12]
        lines.append(row_table(options, cols))
    else:
        lines.append("選擇權資料未在目前 JSON 結構中辨識到可直接列示的資料。")
    lines += [
        "",
        "## 5. 資料完整性檢查",
        "",
        f"- 台指期行情筆數：{len(futures)}",
        f"- 法人交易筆數：{len(institutional)}",
        f"- 法人 OI 筆數：{len(institutional_oi)}",
        f"- 選擇權辨識筆數：{len(options)}",
        "",
        "## 6. 簡易圖表",
        "",
        "```text",
    ]
    if futures:
        for row in futures[:10]:
            label = str(row.get("contract_month", "unknown"))
            close = row.get("close", "—")
            volume = row.get("total_volume", 0)
            lines.append(f"{label:>12} | 收盤 {fmt(close):>10} | 成交量 {fmt(volume):>10}")
    else:
        lines.append("無台指期行情可繪製。")
    lines += ["```", ""]
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", default=None)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    data_dir = root / "data" / "taifex"
    report_dir = root / "reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    date = args.date or datetime.now().strftime("%Y-%m-%d")
    source = data_dir / f"{date}.json"
    if not source.exists():
        raise SystemExit(f"找不到資料檔：{source}")
    with source.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    report = generate(data, str(source.relative_to(root)))
    output = report_dir / f"{date}.md"
    output.write_text(report, encoding="utf-8")
    print(f"OK: {output.relative_to(root)}")


if __name__ == "__main__":
    main()
