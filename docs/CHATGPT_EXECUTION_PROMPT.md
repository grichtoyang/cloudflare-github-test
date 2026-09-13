# CHATGPT_EXECUTION_PROMPT.md

## 1. 文件定位

本文件是「每日盤前分析 V1.0」的 ChatGPT 實際執行控制文件。

- `docs/Daily_Starter_Prompt.md` 負責啟動本專案，不重複定義本文件內容。
- `docs/SYSTEM_ARCHITECTURE.md` 負責系統總體架構與責任邊界。
- `docs/AUTOMATION_ARCHITECTURE.md` 負責自動化、人工啟動與 GitHub Actions 邊界。
- GitHub 上的正式文件為唯一規格來源；不得以記憶、檔名或摘要代替實際讀取。

## 2. 執行前必讀文件

啟動後必須逐一確認並讀取實際內容：

1. `docs/Daily_Starter_Prompt.md`
2. `docs/PROJECT_OVERVIEW.md`
3. `docs/SYSTEM_ARCHITECTURE.md`
4. `docs/DATA_SCHEMA.md`
5. `docs/DATA_SOURCES.md`
6. `docs/ANALYSIS_RULES.md`
7. `docs/REPORT_TEMPLATE.md`
8. `docs/DASHBOARD_SPEC.md`
9. `docs/ERROR_AND_FALLBACK.md`
10. `docs/AUTOMATION_ARCHITECTURE.md`
11. 本文件 `docs/CHATGPT_EXECUTION_PROMPT.md`

每份文件都要記錄：路徑、是否存在、是否成功讀取、讀取結果、錯誤原因。

## 3. Gate 0

正式分析前必須確認：

- 可讀取 Repository 與文件實際內容。
- 可讀取最新資料包、標準化資料、Dashboard 資料及必要歷史資料。
- 可依正式規格執行分析。
- 可產出 Markdown 與 Dashboard JSON。
- 是否能寫回 GitHub。

Gate 0 未完成，不得宣稱完整分析已完成；但不得因此提前停止，仍須依第 8 節產出最低限度報告。

## 4. 日期與資料鎖定

- 時區固定為 `Asia/Taipei`。
- 明確記錄執行日期、資料日期、資料截止時間、資料來源及資料狀態。
- 不得把延遲資料標示為即時資料。
- 不得使用未讀取、過期或日期不符的資料而不揭露。
- 不得虛構、補 0、猜測或把估算值當成實際值。

## 5. 正式分析順序

依序執行：

1. 資料品質總覽
2. 現貨分析
3. 重要國際市場分析
4. 台指期分析
5. 選擇權分析
6. 綜合判斷
7. 交易情境、支撐壓力、失效條件與風險
8. Markdown 報告
9. Dashboard JSON

每個模組至少揭示：關鍵數據、前值、變化、日期／時間、來源、資料狀態、解讀、結論、信心與限制。

## 6. 資料來源與 Fallback

TWSE／TAIFEX 優先使用已驗證官方 Proxy／官方 API。TAIFEX Proxy：

`https://taifex.grichtoyang.workers.dev/`

所有資料集依適用性及驗證結果使用以下統一順序：

1. `primary_proxy`：已驗證的主要 Cloudflare Worker Proxy
2. `official_api`：官方 Open API
3. `backup_api_proxy`：官方備援 API／Proxy
4. `primary_web`：已驗證的主要金融資料來源
5. `backup_web`：已驗證的備援金融資料來源
6. `last_valid`：最近一次有效資料，僅限資料性質允許
7. `missing`：無法取得有效資料

任何 Fallback 都必須記錄來源、原因、時間、資料日期與影響。不得把 `last_valid` 當成當日最新資料。

## 7. Dashboard 與同源原則

Dashboard 是 V1.0 必要交付物，不是選配。必須產出單一 `dashboard_latest.json`，支援：

- `summary`
- `spot`
- `global_markets`
- `futures`
- `options`

預設頁面為 `summary`。Dashboard 只展示資料與結論，不自行抓資料、重算結論或解析 Markdown。Markdown 與 Dashboard JSON 必須由同一份分析結果產出。

## 8. 絕對不可提前停止

一旦開始執行，無論發生資料源失敗、解析錯誤、格式錯誤、權限問題或單一模組失敗，都必須繼續到流程結束。

至少必須產出：

- Markdown 正式或 partial 報告
- Dashboard JSON；若不完整則為結構化 partial JSON
- 資料品質總覽
- 錯誤清單
- Fallback 清單
- 未完成項目
- 最終狀態

可用 `report_status`：

`completed`、`completed_with_warnings`、`partial`、`insufficient_data`、`failed`、`blocked_by_access`、`blocked_by_rule_conflict`。

流程失敗但已產出報告時，使用 `report_status=failed`，不得使用 `failed_but_report_generated`。

## 9. GitHub 寫回

完成產出後，嘗試寫回 GitHub。成功或失敗都必須明確記錄：

- Repository
- 分支
- 檔案路徑
- Commit SHA（若有）
- 寫回結果
- 失敗原因（若有）

不得因無法寫回而否認已產出的本地結果，也不得宣稱寫回成功而未實際確認。

## 10. 最終回報

最終回報必須明確列出：

- 執行日期與資料日期
- Gate 0 結果
- 文件讀取清單
- 各模組完成狀態
- Markdown／Dashboard JSON 產出狀態
- 錯誤與 Fallback
- 未完成項目
- GitHub 寫回結果
- 最終狀態

禁止使用「應該完成」「大致完成」等模糊表述。
