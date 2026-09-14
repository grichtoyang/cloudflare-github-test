# CHATGPT_STEP_EXECUTION_PROMPT.md

## 1. 文件定位

本文件是「每日盤前分析 V1.0」的逐階段、逐回合 ChatGPT 執行控制文件。每回合只能執行一個主要階段；未完成前不得宣稱完成。

## 2. 合法控制指令

- `開始`：執行第 1 階段。
- `繼續`：執行下一個尚未完成的階段。
- `重試`：重試目前為 `FAILED`、`BLOCKED` 或 `RETRY_REQUIRED` 的階段。
- `檢查`：只檢查目前階段，不進入下一階段。
- `結束`：停止並回報進度，不得宣稱完成。

## 3. 六階段

1. 啟動與前置檢查
2. 資料抓取與資料品質檢查
3. 台股現貨及重要市場分析
4. 台指期與選擇權分析
5. 綜合研判與報告產出
6. 最終驗證與結案

## 4. 全域 Retry／Fallback 政策

本政策適用於所有 Gate、Stage、GitHub 文件、GitHub 程式碼、API、Proxy、外部資料、資料驗證、日期判定、分析計算、報告產出、Dashboard、GitHub 寫入及結果讀回，不僅限於 Gate 0。

凡發生逾時、連線失敗、空值、格式錯誤、欄位缺失、內容不完整、日期不明、資料無法核對或結果異常時，必須：

1. 重新執行該取得或處理動作；
2. 至少自動 Retry 3 次；
3. 每次 Retry 必須重新取得／重新執行，不得只重複使用失敗結果；
4. 每次 Retry 後必須重新驗證；
5. 主要來源 Retry 失敗後，依資料來源規則啟用可行 fallback；
6. 所有 Retry／Fallback 完成前，不得直接標記 `PARTIAL`、`BLOCKED` 或 `FAIL`，也不得直接終止整體流程。

**任何 `PENDING` 或 `RETRY_REQUIRED` 狀態都代表流程尚未完成，執行引擎必須自動繼續驗證、Retry 或 fallback，不得把它直接結案。**

只有在所有可行 Retry／Fallback 均完成後，才可依實際結果標記 `PARTIAL`、`BLOCKED` 或 `FAIL`。

不得只取得檔名、URL、SHA、metadata、HTTP 200 或部分回應就標記成功。只有完整實際內容／資料通過驗證，才能標記 `READ_SUCCESS`、`DATA_SUCCESS` 或 `VALIDATED`。

## 5. 第 1 階段與 Gate 0

第 1 階段必須依序完成：

1. 逐一讀取第 9 節列出的 11 份必要文件的實際內容；
2. 記錄每份文件的來源、路徑、實際內容取得狀態、關鍵規則與錯誤原因；
3. 鎖定 `Asia/Taipei` 執行日期與時間；
4. **自動實際驗證台灣交易日，不得只因日期已鎖定就判定 PASS；**
5. 確認資料日期、資料時間、公布時程、日盤／夜盤涵蓋狀態；
6. 確認資料前提條件；
7. 完成所有必要 Retry／Fallback；
8. 最後才回報 Gate 0 結果。

### 5.1 文件讀取協定

對每份文件依序執行：

1. 先檢查本次對話附件；
2. 附件存在時，讀取附件實際內容；
3. 附件不存在時，讀取 GitHub `main` 分支同一路徑；
4. 只有取得完整文件實際文字內容，才可標記 `READ_SUCCESS`；
5. 只看到檔名、目錄項目、URL、SHA 或 metadata，不算已讀取；
6. 讀取失敗時，執行全域 Retry／Fallback；
7. 文件已確認存在但所有讀取與 fallback 均失敗，標記 `READ_FAILED` 或 `BLOCKED`；
8. 只有確認路徑不存在，才標記 `MISSING`；
9. 只有所有 Retry／Fallback 後仍只取得部分內容，才標記 `PARTIAL`，並列出未取得範圍。

### 5.2 Gate 0 強制結案規則

**Gate 0 不得在交易日判定或資料前提仍為「尚未完成」時結案。**

執行控制必須遵守：

```text
鎖定執行日期
→ 自動查詢交易日
→ 失敗時 Retry 1／2／3
→ 必要時啟用 fallback
→ 重新驗證
→ 取得明確交易日結果
→ 驗證資料前提
→ 完成必要 Retry／Fallback
→ 才能判定 Gate 0
```

- `PASS`：11 份必要文件均取得完整實際內容，交易日已實際驗證，資料前提已完成驗證，且所有必要 Retry／Fallback 已完成。
- `BLOCKED`：所有必要讀取、Retry／Fallback、交易日驗證及資料前提驗證均已完成，但仍無法取得必要結果。
- `FAIL`：已完成必要嘗試，但發生非存取類的確定性規則或執行條件錯誤。
- `PENDING`／`RETRY_REQUIRED`：代表尚未完成，不得作為 Gate 0 最終結論；執行引擎必須繼續處理。

**「尚未完成」不得直接等同於 `BLOCKED`。**

單一文件、資料源或驗證項目失敗時，不得立即停止第 1 階段；必須繼續處理其餘項目，並完成所有可行 Retry／Fallback 後才可判定 Gate 0。

## 6. 交易日與資料日期有效性

### 6.1 交易日必須實際驗證

鎖定 `Asia/Taipei` 日期後，必須查詢台灣交易日曆、休市日或可靠官方資料，並記錄查詢結果、來源、時間與 Retry／Fallback 結果。

狀態定義：

- `PENDING`：尚未開始驗證；
- `RETRY_REQUIRED`：驗證失敗，尚未完成 Retry／Fallback；
- `VALID_TRADING_DAY`：已實際驗證為交易日；
- `VALID_NON_TRADING_DAY`：已實際驗證為非交易日；
- `MISSING`：來源不存在，或所有 Retry／Fallback 完成後仍無法取得任何可用判定資料；
- `BLOCKED`：來源已確認存在，但所有讀取、Retry／Fallback 後仍無法取得必要內容。

**尚未查詢、查詢中、讀取中斷或尚未完成 Retry 時，不得標記 `PASS` 或 `MISSING`。**

### 6.2 資料日期不得直接與執行日期比較

資料日期早於執行日期時，不得直接標記 `OLD_DATE`。必須先檢查：

1. 執行日期、星期與 `Asia/Taipei` 時區；
2. 該市場交易日、休市日與跨時區差異；
3. 資料屬於盤中、收盤、盤後、夜盤或延遲公布資料；
4. 資料來源正常公布時程；
5. 目前時點下來源可提供的最新合法資料日期；
6. 資料是否完整且通過驗證。

例如台灣時間星期一早上：

- 美股星期五收盤資料通常是合理的最新可用資料；
- 台股尚未開盤時，上一交易日資料可能是正確資料；
- 台指期、選擇權及法人資料，必須依 TAIFEX 實際公布時點與交易時段判定。

不得因資料日期早於執行日期，就直接標記 `OLD_DATE`。

### 6.3 日期狀態

- `VALID_LATEST_AVAILABLE`：目前時點下來源可提供的最新合法資料；
- `VALID_PREVIOUS_SESSION`：目前尚未完成當日交易／收盤，使用上一個合法交易時段資料；
- `INTRADAY_VALID`：當日盤中資料，且已標明資料時間；
- `OLD_DATE`：依正常公布時程應已更新，但實際資料仍停留在更早日期；
- `MISSING`：所有取得方式、Retry／Fallback 均完成後仍未取得資料；
- `INSUFFICIENT_DATA`：取得資料但不足以完成分析；
- `PENDING`：尚未完成日期有效性判定；
- `RETRY_REQUIRED`：日期或資料驗證失敗，尚未完成 Retry／Fallback。

只有在「依正常公布時程應已更新，但實際資料仍停留在更早日期」時，才可標記 `OLD_DATE`。

每項資料必須記錄：資料日期、資料時間、執行日期時間、判定狀態、判定理由、Retry／Fallback 結果及限制。

## 7. 其餘階段要求

### 第 2 階段

依 `DATA_SCHEMA.md`、`DATA_SOURCES.md` 逐項核對資料集、欄位、來源、日期、時間戳、交易時段、資料品質、Retry、fallback 與影響。不得補 0、猜測或虛構。

### 第 3 階段

依 `ANALYSIS_RULES.md` 分析台股現貨、三大法人、融資融券借券、美股、半導體、美債、美元、台幣、日圓、日韓股與重要新聞；每項均須有資料、日期有效性判定、規則、結果與限制。

### 第 4 階段

明確區分台指期日盤／夜盤、選擇權實際公布時點、近月／當週、OI、法人／外資／造市商資料。Call Wall、Put Wall、Gamma Wall、Gamma Flip、Max Pain 均須標記來源、計算方式、日期時間與有效性；無可靠資料時標記 `MISSING` 或 `INSUFFICIENT_DATA`。

### 第 5 階段

完整遵守 `REPORT_TEMPLATE.md` 與 `DASHBOARD_SPEC.md`。報告與 Dashboard 必須合法、完整、一致且可追溯；不得使用猜測值，也不得把合理的上一交易日資料誤標為 `OLD_DATE`。

### 第 6 階段

逐項驗證六階段證據、必要文件、報告模板、Dashboard JSON、錯誤、警告、資料缺失、日期有效性、延遲、Retry、fallback 與限制。未驗證項目不得宣稱完成。

## 8. 階段狀態與最終結案

允許狀態：`PENDING`、`RUNNING`、`COMPLETED`、`FAILED`、`BLOCKED`、`RETRY_REQUIRED`。

- 沒有實際執行證據，不得標記 `COMPLETED`。
- `PENDING` 或 `RETRY_REQUIRED` 不得作為最終結論。
- `BLOCKED` 只能在所有必要 Retry／Fallback 與驗證程序完成後使用。
- 單一文件、資料源或分析模組失敗，不得直接停止整個流程。
- 即使部分資料最終無法取得，也必須完成所有可行處理，並產出完整 Markdown 報告或明確的錯誤／限制報告。
- 第 6 階段完成前，不得宣稱每日盤前分析整體完成。

## 9. 11 份必要文件與固定順序

1. `docs/Daily_STEP_Starter_Prompt.md`
2. `docs/CHATGPT_STEP_EXECUTION_PROMPT.md`
3. `docs/PROJECT_OVERVIEW.md`
4. `docs/SYSTEM_ARCHITECTURE.md`
5. `docs/DATA_SCHEMA.md`
6. `docs/DATA_SOURCES.md`
7. `docs/ANALYSIS_RULES.md`
8. `docs/REPORT_TEMPLATE.md`
9. `docs/DASHBOARD_SPEC.md`
10. `docs/ERROR_AND_FALLBACK.md`
11. `docs/AUTOMATION_ARCHITECTURE.md`

每份文件都必須取得完整實際內容並記錄 `READ_SUCCESS`；若讀取中斷，必須自動 Retry／Fallback，直到成功或所有可行方法完成後才能標記最終失敗狀態。

## 10. 必要回報格式

每回合必須回報：

1. 目前階段與 Gate；
2. 執行日期、星期、時區；
3. 每份必要文件的讀取狀態；
4. 交易日驗證結果與來源；
5. 每項資料的資料日期、資料時間與日期有效性狀態；
6. Retry 次數、每次結果及 fallback 結果；
7. 缺失、延遲、限制與影響；
8. 是否允許進入下一階段；
9. 若未完成，必須明確寫出下一個自動處理動作，不得只寫「尚未完成」後停止。
