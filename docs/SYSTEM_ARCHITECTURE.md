# 每日盤前分析 V1.0 — 系統架構

**文件狀態：定案版**  
**適用專案：每日盤前分析 V1.0**  
**時區：Asia/Taipei**  
**主要儲存庫：`grichtoyang/cloudflare-github-test`**  
**主要分支：`main`**

## 1. 系統目標

每日自動取得台股、台指期、選擇權、全球市場及相關總體資料，完成資料驗證、盤前分析、Markdown 報告與 Dashboard JSON 產出。

系統只可根據實際取得並驗證的資料分析，不得虛構、補值或把推測當成事實。

## 2. 執行主線

```text
Gate 0
→ 讀取規格
→ 讀取最新資料與歷史資料
→ 資料正規化
→ 資料驗證
→ 五大分析模組
→ 綜合判斷
→ 產出 Markdown
→ 產出 Dashboard JSON
→ 紀錄錯誤與 Fallback
→ 最終驗收
→ GitHub 寫回
→ 產出最終狀態
```

任何階段發生錯誤，都不得提前停止；必須持續至至少產出報告、結構化資料、錯誤紀錄、Fallback 紀錄、未完成項目及最終狀態。

## 3. Gate 0

### 3.1 執行與讀取檢查

確認：

- GitHub 儲存庫及 `main` 分支可讀取。
- 所有必要規格檔案實際存在並已讀取。
- 最新資料、歷史比較資料及必要執行環境可取得。
- TAIFEX Proxy 可連線時，必須進行實際回應驗證。
- 不得只依檔名、摘要或推測宣稱已載入。

### 3.2 交付能力檢查

確認系統至少能產出：

- Markdown 報告
- Dashboard JSON 或 `partial` JSON
- 資料品質總覽
- 錯誤清單
- Fallback 清單
- 未完成項目
- 最終執行狀態

GitHub 寫回失敗不得阻止報告產出。

## 4. 規格讀取順序

1. `01_PROJECT_SPEC.md`
2. `02_DATA_SCHEMA.md`
3. `03_DATA_SOURCE_SPEC.md`
4. `04_ANALYSIS_RULES.md`
5. `06_REPORT_TEMPLATE.md`
6. `07_DASHBOARD_SPEC.md`
7. `08_ERROR_AND_FALLBACK.md`
8. `09_AUTOMATION_ARCHITECTURE.md`
9. `05_CHATGPT_EXECUTION_PROMPT.md`

只有實際讀取檔案內容，才可標示為「已載入」。

## 5. 資料來源與 Fallback

Fallback 順序固定為：

1. 官方 Open API
2. 已驗證官方 Proxy
3. 備援 API／Proxy
4. 主要網站資料擷取
5. 備援網站資料擷取
6. 最近一次有效資料，並標示 `fallback` 或 `stale`
7. `missing`

每筆資料均須保留：

- 來源
- 來源角色
- Endpoint 或網址
- 請求及回應時間
- HTTP 狀態
- 資料日期／時間
- 原始回應
- 驗證結果
- 錯誤碼
- Fallback 狀態

## 6. 資料狀態

允許使用的資料狀態包括：

- `fresh`
- `delayed`
- `stale`
- `missing`
- `invalid`
- `partial`
- `estimated`
- `insufficient_data`

規則：

- 缺失資料不得補成 `0`。
- 估算值不得標示為實際值。
- 延遲資料不得標示為即時。
- 日期不一致或欄位不完整時，必須標示並降低可信度。
- 資料不足時不得強行給出確定方向。

## 7. 五大分析模組

### 7.1 台股現貨

包含大盤指數、成交量、三大法人、融資融券、借券及其他已驗證現貨資料。

### 7.2 全球市場

包含美股主要指數、半導體指數、美元、主要美債殖利率、日韓市場及其他已取得的外部市場資料。

### 7.3 台指期

包含近月期貨價格、漲跌、成交量、未平倉量、三大法人部位及基差等資料。

### 7.4 選擇權

包含：

- Call Wall
- Put Wall
- Gamma Wall
- Gamma Flip
- Max Pain
- 外資部位
- 造市商部位
- 近月／當週變化
- 資料日期與可信度

單一選擇權關鍵位不得直接視為交易訊號，必須結合價格、成交量、未平倉量、波動及市場狀態判斷。

### 7.5 綜合判斷

輸出：

- 偏多情境
- 偏空情境
- 盤整情境
- 不確定情境

每個情境須列出：

- 觸發條件
- 支撐
- 壓力
- 失效條件
- 主要風險
- 資料限制
- 信心程度

## 8. 分析模組固定輸出格式

每一模組必須依序提供：

1. 關鍵資料
2. 資料日期／時間
3. 資料來源
4. 資料狀態
5. 與前次資料比較
6. 解讀
7. 模組結論
8. 信心程度
9. 風險與限制

## 9. Dashboard 規格

Dashboard 固定五頁：

- `summary`
- `spot`
- `global_markets`
- `futures`
- `options`

規則：

- 預設頁面為 `summary`。
- 五頁可切換。
- 目前頁面須有清楚的選取狀態及無障礙標記。
- 桌面與手機均須可使用。
- 所有頁面使用同一份 `dashboard_latest.json`。
- 頁面切換不得重新抓取資料。
- 頁面切換不得重新計算資料。
- Dashboard 只展示結果，不改寫分析結論。
- 資料不完整時仍須產出結構化 `partial` JSON。

## 10. 錯誤與錯誤碼

常見錯誤碼：

- `ACCESS_ERROR`
- `HTTP_ERROR`
- `TIMEOUT`
- `PARSE_ERROR`
- `SCHEMA_ERROR`
- `MISSING_FIELD`
- `EMPTY_RESPONSE`
- `DATE_MISMATCH`
- `STALE_DATA`
- `SOURCE_UNAVAILABLE`
- `VALIDATION_ERROR`
- `MODULE_ERROR`
- `REPORT_ERROR`
- `DASHBOARD_ERROR`
- `GITHUB_READ_ERROR`
- `GITHUB_WRITE_ERROR`
- `RULE_CONFLICT`

每個錯誤必須記錄：

- 發生階段
- 時間
- 來源或檔案
- 錯誤碼
- 錯誤描述
- 是否啟用 Fallback
- 對結果的影響
- 後續處理

## 11. Markdown 報告最低要求

報告至少包含：

- `run_id`
- 執行日期與時間
- 資料日期與時間
- Gate 0 結果
- GitHub 讀取結果
- 實際讀取的規格檔案清單
- 各資料來源狀態
- 五大模組狀態
- 關鍵資料與分析
- 已完成項目
- 未完成項目
- 錯誤清單
- Fallback 清單
- 資料品質總覽
- 風險與限制
- Markdown 產出狀態
- Dashboard 產出狀態
- GitHub 寫回狀態
- 最終執行狀態

## 12. 最終執行狀態

允許狀態：

- `completed`
- `completed_with_warnings`
- `partial`
- `failed_but_report_generated`
- `blocked_by_access`
- `blocked_by_rule_conflict`

狀態判定優先順序：

```text
blocked_by_rule_conflict
> blocked_by_access
> failed_but_report_generated
> partial
> completed_with_warnings
> completed
```

## 13. 硬性禁止事項

不得：

- 虛構任何資料
- 把缺失資料填為零
- 把估算當實際
- 把延遲資料當即時
- 把單一選擇權關鍵位當成交易訊號
- 在資料不足時強行預測確定方向
- 未讀取檔案內容卻宣稱已載入
- 因單一錯誤提前停止
- 自行修改已定案規則
- 自動下單或執行交易

## 14. 範圍外事項

本系統目前不包含：

- 自動交易
- 自動下單
- OCR 影像辨識
- 未核准資料來源
- 自行修改分析規則
- 未經驗證的即時行情宣稱

## 15. 定案原則

本文件只定義系統架構與執行約束。實際每日執行時，所有資料、狀態、錯誤、Fallback 及結論，均必須以當次實際執行結果為準。
