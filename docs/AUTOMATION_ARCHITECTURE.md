# 每日盤前分析 V1.0
# AUTOMATION_ARCHITECTURE.md

**版本：V1.0**  
**文件狀態：正式架構基準**

## 1. 文件定位

本文件定義每日盤前分析 V1.0 的自動化執行架構、資料流程、錯誤處理、Fallback、報告產出、Dashboard JSON 產出、GitHub Actions 執行責任與完成判定。

本文件不取代：
- `ANALYSIS_RULES.md`
- `REPORT_TEMPLATE.md`
- `DASHBOARD_SPEC.md`
- `CHATGPT_EXECUTION_PROMPT.md`
- `NOTICE.md`

## 2. V1.0 系統定位

V1.0 是：

> GitHub Actions 自動抓取與整理資料；使用者人工啟動 ChatGPT 進行分析；ChatGPT 產出 Markdown 報告與 Dashboard JSON，並嘗試寫回 GitHub。

目前不是完整無人值守的 ChatGPT 分析系統。

GitHub Actions 負責資料抓取、標準化、品質檢查、Retry、Fallback、每日資料包與執行紀錄。ChatGPT 負責讀取規格與資料包、執行分析、產出報告與 Dashboard JSON，並嘗試寫回 GitHub。

不得宣稱 GitHub Actions 在無 API Key 下可自動呼叫 ChatGPT；不得把資料抓取完成等同於盤前分析完成；不得把報告產出等同於 GitHub 寫回成功。

## 3. 系統架構

```text
GitHub Actions
  → 日期與設定初始化
  → 資料抓取
  → 資料標準化
  → 品質驗證
  → Retry／Fallback
  → 建立每日資料包
  → 保存資料與紀錄
  → 使用者人工啟動 ChatGPT
  → ChatGPT 分析
  → Markdown 報告
  → Dashboard JSON
  → 驗證輸出
  → 嘗試寫回 GitHub
```

## 4. 時區與日期

所有排程與市場日期判定以 `Asia/Taipei` 為基準。

必須分開記錄：
- `runtime_date`
- `market_date`
- `data_date`
- `generated_at`

週末或台灣休市日不得假造當日資料，不得將前一交易日資料標示為當日資料；可產出非交易日或未執行狀態。

## 5. 執行方式

必須支援：
- GitHub Actions `schedule`
- GitHub Actions `workflow_dispatch`
- 手動重跑
- 指定日期重建
- Fallback 測試
- 輸出驗證

應使用 `concurrency` 避免同一日期重複執行。重跑時必須保留執行 ID、重跑原因與時間。

## 6. 執行階段

```text
Stage 0   初始化
Stage 1   判定 runtime_date／market_date
Stage 2   載入設定與規格
Stage 3   抓取資料
Stage 4   資料標準化
Stage 5   資料品質驗證
Stage 6   Retry 與 Fallback
Stage 7   建立每日資料包
Stage 8   保存資料與執行紀錄
Stage 9   回報資料自動化狀態
Stage 10  使用者人工啟動 ChatGPT
Stage 11  產出 Markdown
Stage 12  產出 Dashboard JSON
Stage 13  驗證輸出
Stage 14  嘗試寫回 GitHub
Stage 15  回報最終狀態
```

### 強制不中斷規則

一旦分析流程開始，無論中間發生任何錯誤，都必須盡可能完成：
- Markdown 報告
- Dashboard JSON
- 未完成項目
- 錯誤紀錄
- Fallback 紀錄
- 最終執行狀態

單一模組失敗不得直接使整體流程停止。只有執行環境完全無法運作，或必要輸出完全無法建立時，才可標示 `FAILED_FATAL`。

## 7. 資料來源

### TAIFEX／Cloudflare Proxy
- 台指期行情
- 日盤與夜盤資料
- 三大法人期貨 OI
- 選擇權鏈與 OI
- 法人資料
- Call Wall、Put Wall、Gamma Wall、Gamma Flip、Max Pain

### TWSE／TAIEX Proxy
- 台股現貨
- 加權指數
- 成交量
- 三大法人現貨資料
- 融資融券等可取得資料

### FinMind
作為補充、歷史與備援來源。使用前必須驗證日期、欄位與定義。

### 外部市場與新聞
可包含美股指數、SOX、美債殖利率、美元、匯率、日韓市場、BTC、金融與產業新聞。每筆資料必須記錄來源、時間與狀態。

## 8. 資料處理層

```text
raw/
normalized/
validated/
analysis_input/
output/
logs/
```

- Raw Data：保存原始回傳，不任意修改。
- Normalized Data：統一欄位、日期、時間、單位與型別。
- Validated Data：完成日期、欄位、型別、數值、盤別、時間戳與完整性檢查。
- Analysis Package：提供 ChatGPT 使用，並包含來源、時間、品質、Fallback、缺失與未完成項目。

## 9. Retry 與 Fallback

```text
Level 1：同一 Endpoint 重試
Level 2：同一來源替代 Endpoint
Level 3：Cloudflare Proxy 內部備援
Level 4：第二資料來源
Level 5：Unavailable／Not Computable
```

每次必須記錄：
- 原始來源與 Endpoint
- 失敗時間與原因
- Retry 次數
- 實際使用來源與 Endpoint
- 資料時間
- 是否影響分析結論

## 10. 錯誤處理

錯誤至少包括：
- 網路、DNS、HTTP
- 空值、JSON、欄位與型別
- 日期、盤別、延遲與來源不一致
- 分析、Markdown、Dashboard JSON
- GitHub 寫回

每個錯誤至少包含：

```text
error_code
error_stage
source
endpoint
timestamp
message
retry_count
fallback_used
impact
resolution
```

## 11. 強制資料規則

1. 缺失資料不得補成 `0`，應使用 `null`、`Unavailable`、`Partial` 或 `Not Computable`。
2. OI 是部位存量；成交量與夜盤新增流向是期間流量，不得混用。
3. 近月與當週選擇權必須分開標示。
4. 所有資料必須標示資料日期、時間、來源、單位與狀態。
5. Call Wall、Put Wall、Gamma Wall、Gamma Flip、Max Pain 不得單獨直接作為交易訊號。
6. 資料不足或矛盾時不得強行產生多空方向。

## 12. Markdown 報告

報告至少包含：
- 報告日期與產出時間
- 執行狀態與資料品質
- 台股現貨、台指期、選擇權
- 美股與總體環境
- 重要新聞
- 綜合判斷、支撐壓力與風險情境
- Fallback、缺失資料與未完成項目
- 資料限制與免責

資料不完整時仍必須產出，並明確揭露原因。

## 13. Dashboard JSON

Dashboard 必須與 Markdown 使用同一份分析結果。

不得重新抓資料、重新計算結論，或在前端自行推導未經分析引擎確認的結論。

最低結構：

```json
{
  "schema_version": "1.0",
  "report_date": "YYYY-MM-DD",
  "generated_at": "ISO-8601",
  "runtime_date": "YYYY-MM-DD",
  "overall_status": "SUCCESS",
  "data_quality": {},
  "sources": {},
  "market": {},
  "futures": {},
  "options": {},
  "macro": {},
  "news": {},
  "summary": {},
  "warnings": [],
  "incomplete_items": [],
  "fallbacks": []
}
```

## 14. GitHub 寫回

ChatGPT 可以嘗試寫回 Markdown、Dashboard JSON 與狀態紀錄，但不得保證每次成功。

只有在 Repository、Branch、路徑、Commit 與檔案內容重新讀取均確認後，才可標示成功。

狀態至少區分：
- `github_writeback_success`
- `github_writeback_partial`
- `github_writeback_failed`

寫回失敗時必須保留已產出的分析結果並記錄原因。

## 15. 最終狀態

| 狀態 | 定義 |
|---|---|
| `SUCCESS` | 所有必要流程與輸出完成 |
| `SUCCESS_WITH_FALLBACK` | 完成但使用備援來源 |
| `PARTIAL_SUCCESS` | 部分資料或模組未完成但輸出已產出 |
| `INCOMPLETE` | 必要流程仍未完成 |
| `FAILED_OUTPUT` | 必要輸出失敗 |
| `FAILED_FATAL` | 執行環境或必要流程完全無法運作 |
| `ANALYSIS_NOT_STARTED` | 資料包完成但 ChatGPT 尚未人工啟動 |
| `GITHUB_WRITEBACK_PARTIAL` | 部分檔案已寫回 |
| `GITHUB_WRITEBACK_FAILED` | GitHub 寫回失敗 |

## 16. 完成判定

### 資料自動化完成
- 資料抓取、標準化與驗證完成
- Retry／Fallback 已執行
- 每日資料包已建立
- 錯誤與未完成項目已保存
- 執行狀態已寫入

### 盤前分析完成
- ChatGPT 已人工啟動
- 規格與資料包已讀取
- Markdown 與 Dashboard JSON 已產出
- 未完成項目與 Fallback 已揭露
- 輸出格式已驗證
- 最終狀態已回報

### GitHub 寫回完成
- Markdown 與 Dashboard JSON 已成功寫回
- Repository、Branch、路徑正確
- Commit 已確認
- 檔案可重新讀取驗證

## 17. 驗收標準

- [ ] 排程與時區正確
- [ ] 手動執行可用
- [ ] 日期與休市日判定正確
- [ ] 可重跑且保留歷史紀錄
- [ ] Retry／Fallback 可用
- [ ] 缺失資料不補零
- [ ] OI 與交易流量未混用
- [ ] 每日資料包可建立
- [ ] Markdown 可產出
- [ ] Dashboard JSON 可產出
- [ ] 兩者使用同一份分析結果
- [ ] 錯誤與未完成項目可追蹤
- [ ] GitHub 寫回成功、部分成功與失敗可區分
- [ ] 未經端到端測試不得宣稱完成

## 18. 最終強制規則

1. 資料自動化不等於 ChatGPT 分析自動化。
2. 無 API Key 不得宣稱 GitHub Actions 可自動呼叫 ChatGPT。
3. ChatGPT 分析目前必須由使用者人工啟動。
4. 分析開始後必須盡可能完成所有最終輸出與狀態。
5. 缺失資料不得補零。
6. 不得把延遲資料標示為即時。
7. 不得混用 OI 與交易流量。
8. 不得混用近月與當週選擇權。
9. 不得把單一關鍵價位直接當成交易訊號。
10. Fallback 必須可追蹤。
11. Markdown 與 Dashboard 必須來自同一份分析結果。
12. 報告已產出不等於 GitHub 已成功更新。
13. 未經端到端測試不得宣稱系統完成。
