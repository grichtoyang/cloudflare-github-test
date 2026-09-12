# GitHub V1.0 Formal Reports

This directory stores the formal Markdown reports produced after ChatGPT completes the GitHub V1.0 analysis.

## Naming

```text
每日盤前分析報告_GitHub_V1.0_yyyymmdd.md
```

## Writeback contract

A report is considered persisted only after all of the following succeed:

1. The complete Markdown report is created or updated in this directory.
2. `reports/HISTORY_INDEX.json` is updated for the same `analysis_date`.
3. The GitHub commit succeeds.
4. The report and index are read back and verified.

Creating an L1 snapshot, manifest, or AI-input package does **not** count as formal-report persistence.

Repeated execution for the same `analysis_date` must overwrite the same report path and update the corresponding history-index entry rather than creating duplicates.
