# 每日盤前分析 V1.0 — Dashboard Specification

本文件依據 `dashboard的架構討論.md` 與 `REPORT_TEMPLATE.md` 制定。

核心規格：

- Dashboard 是視覺化展示層，不是分析引擎。
- 固定五頁：`spot`、`global_markets`、`futures`、`options`、`summary`。
- `summary` 為預設首頁。
- 所有頁面共用 `dashboard/data/dashboard_latest.json`。
- Markdown 報告與 Dashboard JSON 必須同源。
- 切換頁面不得重新抓資料或重新計算結論。
- 所有數據必須顯示日期／時間、來源、單位與狀態。
- 缺失資料不得補 0；延遲、Fallback、估算與錯誤必須明示。
- 日盤後法人 OI 與夜盤新增交易流量必須分開。
- 選擇權近月與當週必須分開。
- Call Wall、Put Wall、Gamma Wall、Gamma Flip、Max Pain 必須依資料狀況展示。
- 選擇權關鍵位不得單獨作為交易訊號。
- 單一資料源或模組失敗不得拖垮整體 Dashboard。
- 總結頁必須展示方向、Regime、燈號、支撐壓力、三種情境、失效條件、風險、信心與未完成項目。
- 只有實測驗收通過後，才能宣稱 Dashboard 完成。

完整規格請以同一專案中的 `docs/DASHBOARD_SPEC.md` 為主文件。