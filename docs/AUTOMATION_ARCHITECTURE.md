# 每日盤前分析 V1.0 — 自動化架構規範

**版本：** V1.0  
**文件狀態：** 定案版  
**時區：** Asia/Taipei

## 1. 系統定位

V1.0 採以下責任分工：

- GitHub Actions：資料抓取、標準化、驗證、Retry、Fallback、每日資料包及執行紀錄。
- 使用者：人工啟動 ChatGPT 分析流程。
- ChatGPT：讀取規格與資料包、產出 Markdown 報告、Dashboard JSON、錯誤與未完成紀錄，並嘗試寫回 GitHub。

資料抓取完成不等於盤前分析完成；報告產出不等於 GitHub 寫回成功；不得宣稱 GitHub Actions 在無 API Key 下自動呼叫 ChatGPT。

## 2. 執行流程

```text
初始化
→ 判定 runtime_date / market_date
→ 載入規格與設定
→ 抓取資料
→ 標準化
→ 品質驗證
→ Retry / Fallback
→ 建立每日資料包
→ 保存資料與紀錄
→ 使用者人工啟動 ChatGPT
→ 產出 Markdown
→ 產出 Dashboard JSON
→ 驗證輸出
→ 嘗試寫回 GitHub
→ 回報最終狀態
```

## 3. 日期與時區

所有排程與市場日期以 `Asia/Taipei` 判定，並分開記錄：

- `runtime_date`
- `market_date`
- `data_date`
- `generated_at`

週末或休市日不得假造當日資料，也不得把前一交易日資料標示為當日資料。

## 4. 強制不中斷規則

分析開始後，無論發生一般錯誤，都必須盡可能完成：

- Markdown 報告或最小錯誤報告
- Dashboard JSON 或 `partial` JSON
- 資料品質總覽
- 錯誤紀錄
- Fallback 紀錄
- 未完成項目
- 風險與限制
- 最終報告狀態

單一資料集、模組、Dashboard 或 GitHub 寫回失敗，不得直接停止整體流程。規則衝突時不得猜測，但仍須產出錯誤與降級結果。

## 5. 資料層

```text
raw/
normalized/
validated/
analysis_input/
output/
logs/
```

- `raw`：保存原始回傳，不覆寫。
- `normalized`：統一欄位、日期、時間、單位與型別。
- `validated`：完成結構、欄位、日期、型別、數值、盤別、時間戳及完整性驗證。
- `analysis_input`：供 ChatGPT 使用，必須附來源、時間、品質、Fallback、缺失及未完成項目。

## 6. Retry 與 Fallback

同一來源內的 Retry／替代 Endpoint 是技術重試層；跨來源 Fallback 必須遵守下列固定順序：

```text
1. primary_proxy
2. official_api
3. backup_api_proxy
4. primary_web
5. backup_web
6. last_valid
7. missing
```

每次切換必須記錄：原始來源、Endpoint、失敗原因、時間、Retry 次數、實際採用來源、資料日期、資料狀態及對分析的影響。不得跳過可用且已驗證的前順位來源。

`last_valid` 只有在資料性質允許時可使用，且必須標記：

```text
source_role=last_valid
data_status=stale
fallback.used=true
```

不得以舊資料冒充當日行情、成交量、法人流量、未平倉量或選擇權鏈。

## 7. 資料硬性規則

1. 缺失資料使用 `null`，不得補成 `0`。
2. OI 是部位存量；成交量及夜盤新增流向是期間流量，不得混用。
3. 近月與當週選擇權必須分開。
4. 所有資料必須標示日期、時間、來源、單位及狀態。
5. Call Wall、Put Wall、Gamma Wall、Gamma Flip、Max Pain 不得單獨直接產生交易訊號。
6. 資料不足、矛盾或規則衝突時，不得強行產生多空結論。

## 8. Markdown 與 Dashboard

Markdown 與 Dashboard 必須使用同一份已確認的分析結果。

Dashboard 不得重新抓資料、重新計算結論，或自行推導未經分析引擎確認的訊號。

最低 Dashboard 結構：

```json
{
  "schema_version": "1.0",
  "report_date": "YYYY-MM-DD",
  "generated_at": "ISO-8601",
  "runtime_date": "YYYY-MM-DD",
  "report_status": "completed",
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

`report_status` 只允許：

```text
completed
completed_with_warnings
partial
insufficient_data
failed
blocked_by_access
blocked_by_rule_conflict
```

## 9. 錯誤與寫回

錯誤至少記錄：

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

GitHub 寫回狀態獨立記錄，不得與 `report_status` 混用：

```text
github_writeback_success
github_writeback_partial
github_writeback_failed
```

只有重新讀取並確認 Repository、Branch、路徑、Commit 及檔案內容後，才可宣稱寫回成功。

## 10. 完成判定

### 資料自動化完成

- 資料抓取、標準化及驗證完成。
- Retry／Fallback 已執行。
- 每日資料包已建立。
- 錯誤、Fallback 及未完成項目已保存。

### 盤前分析完成

- ChatGPT 已人工啟動。
- 規格與資料包已讀取。
- Markdown 與 Dashboard JSON 已產出。
- 資料限制、Fallback 及未完成項目已揭露。
- 輸出格式已驗證。

### GitHub 寫回完成

- 必要檔案已成功寫回。
- Repository、Branch、路徑及 Commit 已確認。
- 檔案已重新讀取驗證。

## 11. 禁止事項

- 不得虛構資料、來源、時間或錯誤結果。
- 不得把延遲、過期或估算資料標示為即時資料。
- 不得把缺失資料補零。
- 不得隱藏 Fallback 或資料限制。
- 不得把報告產出等同於 GitHub 寫回成功。
- 不得把資料自動化等同於 ChatGPT 分析自動化。
- 未經端到端測試不得宣稱整個系統完成。
