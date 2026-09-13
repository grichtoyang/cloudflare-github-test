# 每日盤前分析 V1.0 — 新對話啟動 Prompt

## 1. 執行環境

- Repository：`grichtoyang/cloudflare-github-test`
- 分支：`main`
- 時區：`Asia/Taipei`
- 分析引擎：ChatGPT
- OpenAI API Key：不使用
- TAIFEX Proxy：`https://taifex.grichtoyang.workers.dev/`

每次啟動後，必須先驗證 GitHub 存取能力，再讀取規格與資料，最後產出報告。不得只依檔名、摘要或過往對話宣稱已完成。

## 2. Gate 0：執行能力

開始分析前，必須確認並回報：

1. GitHub Repository 是否可讀取。
2. GitHub 檔案內容是否可實際開啟。
3. 規格文件是否可讀取。
4. 最新資料包與歷史資料是否可讀取。
5. 是否可執行分析。
6. 是否可產出 Markdown 報告。
7. 是否可產出 Dashboard JSON。
8. 是否可寫回 GitHub。

任何項目失敗，都必須說明原因、記錄影響，並繼續完成其他可完成工作。不得假裝完成。

## 3. 規格文件讀取順序

依 GitHub `docs/` 的實際檔名讀取：

1. `docs/PROJECT_OVERVIEW.md`
2. `docs/DATA_SCHEMA.md`
3. `docs/DATA_SOURCES.md`
4. `docs/SYSTEM_ARCHITECTURE.md`
5. `docs/每日盤前分析_新對話啟動_Prompt_V1.0.md`（最後讀取）

目前尚未確認存在的規格文件，不得自行假設或以相近檔名代替：

- `04_ANALYSIS_RULES.md`
- `05_CHATGPT_EXECUTION_PROMPT.md`
- `06_REPORT_TEMPLATE.md`
- `07_DASHBOARD_SPEC.md`
- `08_ERROR_AND_FALLBACK.md`
- `09_AUTOMATION_ARCHITECTURE.md`

每份文件都要記錄：實際路徑、是否存在、是否成功讀取、文件狀態及讀取失敗原因（如有）。

## 4. 資料讀取

規格讀取完成後，確認：

- 最新資料包
- 最新標準化資料
- 最新 Dashboard 資料
- 必要歷史比較資料
- 錯誤與 fallback 紀錄

資料目錄以 GitHub 實際路徑為準：

- `data/manifests/`
- `data/premarket/`
- `data/snapshots/`
- `data/taifex/`
- `data/twse/`

所有資料都必須檢查日期、時間、來源、單位與狀態。缺失資料不得補成 0，也不得當成已取得。

## 5. 分析與交付順序

1. 確認執行日期與資料日期。
2. 執行資料品質檢查。
3. 揭示關鍵數據。
4. 分析現貨。
5. 分析重要市場。
6. 分析台指期。
7. 分析選擇權。
8. 產出綜合市場判斷。
9. 產出交易情境、支撐、壓力、失效條件與風險控管。
10. 產出圖表資料。
11. 產出 Markdown 報告。
12. 產出 Dashboard JSON；規格不足時產出 partial JSON。
13. 記錄錯誤、fallback 與未完成項目。
14. 執行最終驗收。

每個模組都必須揭示：

- 關鍵數據
- 前值與變化
- 資料日期／時間
- 來源
- 資料狀態
- 數據解讀
- 模組結論
- 分析信心
- 風險與限制

## 6. Dashboard 基本規則

Dashboard 使用同一份 `dashboard_latest.json`，只展示分析結果，不自行改寫結論。

必須支援五個頁面：

- `spot`：現貨
- `global_markets`：重要市場
- `futures`：期貨
- `options`：選擇權
- `summary`：總結

預設頁面為 `summary`。五頁可切換，且不得因切換而重新抓取資料或重新計算結論。桌面與手機皆須可使用。

## 7. 錯誤與 Fallback

### 7.1 不得提前停止

開始執行後，無論發生資料源失敗、HTTP 錯誤、解析錯誤、日期不一致、單一模組失敗、GitHub 錯誤或格式錯誤，都不得只回覆錯誤後停止。

至少要完成：

- Markdown 報告
- Dashboard JSON 或 partial JSON
- 資料品質總覽
- 錯誤紀錄
- fallback 紀錄
- 未完成項目
- 最終狀態

### 7.2 Fallback 順序

1. 官方 Open API
2. 已驗證官方 Proxy
3. 備援 API／Proxy
4. 主要網站
5. 備援網站
6. 最近一次有效資料（標示 `fallback` 或 `stale`）
7. `missing`

每個錯誤需記錄：模組、來源、時間、錯誤類型、影響、處理方式及 fallback。

### 7.3 資料誠信

禁止：

- 虛構資料
- 缺失值補 0
- 將估算值當實際值
- 將推測當事實
- 將延遲資料標示為即時
- 將單一選擇權關鍵位直接當交易訊號
- 資料不足時強行給出確定方向

可使用狀態：`missing`、`invalid`、`delayed`、`partial`、`fallback`、`estimated`、`insufficient_data`。

## 8. 最終驗收

最終回報必須列出：

- 執行日期
- 資料日期
- Gate 0 結果
- GitHub 讀取與寫回結果
- 每份規格文件的實際讀取狀態
- 各分析模組完成狀態
- Markdown 報告狀態
- Dashboard JSON 狀態
- 錯誤與 fallback
- 未完成項目
- 最終執行狀態

可用狀態：

`completed`、`completed_with_warnings`、`partial`、`failed_but_report_generated`、`blocked_by_access`、`blocked_by_rule_conflict`

**硬性規則：開始執行後不得提前停止；必須完成最低交付物、錯誤與 fallback 紀錄、未完成項目及最終狀態後才能結束。**

**只有實際開啟並讀取檔案內容，才可以宣稱文件已載入。**

**文件名稱與路徑一律以 GitHub `docs/` 的實際檔名為準。**

**只有實際完成並驗收後，才可以宣稱每日盤前分析已完成。**
