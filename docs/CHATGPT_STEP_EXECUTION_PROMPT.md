# CHATGPT_STEP_EXECUTION_PROMPT.md

## 1. 文件定位

本文件是「每日盤前分析 V1.0」的逐階段、對話式 ChatGPT 執行控制文件。採用逐階段、逐回合、人工確認模式；每回合只能執行一個主要階段。

本文件不取代 `docs/CHATGPT_EXECUTION_PROMPT.md`，也不修改 GitHub Actions、Python、Proxy 或其他正式規格文件。

## 2. 合法控制指令

- `開始`：執行第 1 階段。
- `繼續`：執行下一個尚未完成的階段。
- `重試`：重試目前為 `FAILED`、`BLOCKED` 或 `RETRY_REQUIRED` 的階段。
- `檢查`：只檢查目前階段，不進入下一階段。
- `結束`：停止並回報進度，不得宣稱完成。

不得預先執行後續階段，也不得在第 6 階段完成前宣稱整體完成。

## 3. 六階段

1. 啟動與前置檢查
2. 資料抓取與資料品質檢查
3. 台股現貨及重要市場分析
4. 台指期與選擇權分析
5. 綜合研判與報告產出
6. 最終驗證與結案

## 4. 全域 Retry／Fallback 政策

本政策適用於所有 Gate、Stage、資料來源、API、Proxy、GitHub 文件、程式碼、資料驗證、分析計算、報告產出、Dashboard、GitHub 寫入及結果讀回，不僅限於 Gate 0。

凡發生逾時、連線失敗、空值、格式錯誤、欄位缺失、內容不完整、日期不明、資料無法核對或結果異常時，必須：

1. 重新執行該取得或處理動作；
2. 至少自動 Retry 3 次；
3. 每次 Retry 都必須重新取得／重新執行並重新驗證；
4. 主要來源 Retry 失敗後，依規則啟用可行 fallback；
5. 所有 Retry／Fallback 完成前，不得直接標記 `PARTIAL`、`BLOCKED` 或 `FAIL`，也不得直接終止整體流程。

只有在所有可行 Retry／Fallback 完成後，才可依實際結果標記 `PARTIAL`、`BLOCKED` 或 `FAIL`。

不得只取得檔名、URL、SHA、metadata、HTTP 200 或部分回應就標記成功。只有完整實際內容／資料通過驗證，才能標記 `READ_SUCCESS`、`DATA_SUCCESS` 或 `VALIDATED`。

## 5. 第 1 階段與 Gate 0

第 1 階段必須：

1. 逐一讀取第 9 節列出的 11 份必要文件的實際內容；
2. 記錄每份文件的來源、路徑、實際內容取得狀態、關鍵規則與錯誤原因；
3. 鎖定 `Asia/Taipei` 執行日期與時間；
4. 判定台灣交易日；
5. 確認資料日期、截止時間、日盤／夜盤涵蓋狀態；
6. 回報 Gate 0：`PASS`、`FAIL` 或 `BLOCKED`。

### 5.1 文件讀取協定

對每份文件依序執行：

1. 先檢查本次對話附件；
2. 附件存在時，讀取附件實際內容；
3. 附件不存在時，讀取 GitHub `main` 分支的同一路徑；
4. 只有取得文件實際文字內容，才可標記 `READ_SUCCESS`；
5. 只看到檔名、目錄項目、URL 或 SHA，不算已讀取；
6. 讀取失敗時，依全域 Retry／Fallback 政策重試；
7. 文件已確認存在但所有讀取與 fallback 均失敗，標記 `READ_FAILED` 或 `BLOCKED`；
8. 只有確認路徑不存在，才標記 `MISSING`；
9. 只有所有 Retry／Fallback 後仍只取得部分內容，才標記 `PARTIAL` 並列出未取得範圍。

### 5.2 Gate 0 判定

- `PASS`：11 份必要文件均已取得實際內容，且日期、交易日與資料前提均已確認。
- `BLOCKED`：必要文件已確認存在，但至少一份實際內容無法取得，且已完成可行的讀取、重試與 fallback。
- `FAIL`：必要條件未完成，原因不是文件存取阻擋，例如日期未鎖定、交易日未判定或規則衝突未揭露。

單一文件讀取失敗時，不得立即停止第 1 階段。必須繼續檢查其餘文件，完成所有可行讀取、Retry 與 fallback 後，才可判定 Gate 0。

`BLOCKED` 不等於 `MISSING`，不得互相替換，也不得把 `BLOCKED` 改寫成 `PASS` 或 `COMPLETED`。

## 6. 市場資料日期與交易日有效性判定

### 6.1 執行日期與交易日必須實際驗證

鎖定 `Asia/Taipei` 執行日期後，必須實際查詢並驗證該日是否為台灣交易日，不得只因日期已鎖定就將交易日判定標記為 `PASS`。

交易日驗證必須檢查：

1. 執行日期、星期與台灣時區 `Asia/Taipei`；
2. 台灣交易日曆、休市日或可靠官方交易日資料；
3. 查詢是否成功取得實際結果；
4. Retry／Fallback 是否已完成；
5. 最終判定是否有可追溯證據。

交易日狀態不得混用：

- `PENDING`：尚未開始驗證；
- `RETRY_REQUIRED`：驗證失敗，尚未完成必要 Retry／Fallback；
- `VALID_TRADING_DAY`：已實際驗證為台灣交易日；
- `VALID_NON_TRADING_DAY`：已實際驗證為非交易日；
- `MISSING`：交易日資料來源不存在，或所有 Retry／Fallback 均完成後仍無法取得任何可用判定資料；
- `BLOCKED`：來源已確認存在，但所有讀取、Retry／Fallback 後仍無法取得必要內容。

**「尚未實際驗證」不得標記為 `MISSING`。**

若交易日查詢尚未執行、正在執行、讀取中斷或尚未完成 Retry，狀態只能是 `PENDING`、`RETRY_REQUIRED` 或 `BLOCKED`，不得是 `MISSING`，更不得是 `PASS`。

### 6.2 市場資料日期不得直接以執行日期比較

資料日期早於執行日期時，不得直接標記為 `OLD_DATE`。必須先判斷該市場在目前執行時間下，是否已完成當日交易、收盤或資料公布。

日期判定必須同時檢查：

1. 執行日期、星期與台灣時區 `Asia/Taipei`；
2. 該市場的交易日、休市日及跨時區差異；
3. 該資料屬於盤中、收盤、盤後、夜盤或延遲公布資料；
4. 該資料來源正常公布時程；
5. 目前時點下該來源可提供的最新合法資料日期；
6. 資料是否完整、欄位是否齊全及是否通過驗證。

### 6.3 合法上一交易日資料

例如台灣時間星期一早上，前一個完整交易日為星期五：

- 美股主要指數星期五收盤資料，應視為合理的最新可用資料；
- 美債、美元、匯率及其他跨時區市場資料，應依其實際公布時間判定；
- 台股現貨若尚未開盤，使用上一交易日資料可能是正確的；
- 台指期、選擇權及法人資料，應依 TAIFEX 實際公布時點與交易時段判定。

此類資料不得僅因日期早於執行日期，就標記為 `OLD_DATE`。

### 6.4 日期狀態

可使用下列狀態：

- `VALID_LATEST_AVAILABLE`：目前時點下來源可提供的最新合法資料；
- `VALID_PREVIOUS_SESSION`：目前尚未完成當日交易／收盤，使用上一個合法交易時段資料；
- `INTRADAY_VALID`：當日盤中資料，且已標明資料時間；
- `OLD_DATE`：依正常公布時程，應已取得更新資料，但實際資料仍停留在更早日期；
- `MISSING`：來源不存在，或所有取得方式、Retry／Fallback 均完成後仍未取得資料；
- `INSUFFICIENT_DATA`：取得資料但不足以完成該項分析；
- `PENDING`：尚未完成資料日期有效性判定；
- `RETRY_REQUIRED`：日期或資料驗證失敗，尚未完成必要 Retry／Fallback。

只有在「依正常公布時程應已更新，但實際資料仍停留在更早日期」時，才可標記 `OLD_DATE`。

每項資料都必須記錄：資料日期、資料時間、執行日期時間、判定狀態、判定理由、Retry／Fallback 結果及限制。

## 7. 其餘階段要求

### 第 2 階段

依 `DATA_SCHEMA.md`、`DATA_SOURCES.md` 逐項核對資料集、欄位、來源、日期、時間戳、交易時段、資料品質、Retry、fallback 與影響。不得補 0、猜測或虛構。

### 第 3 階段

依 `ANALYSIS_RULES.md` 分析台股現貨、三大法人、融資融券借券、美股、半導體、美債、美元、台幣、日圓、日韓股與重要新聞；每項均須有資料、日期有效性判定、規則、結果與限制。

### 第 4 階段

明確區分台指期日盤／夜盤、選擇權實際公布時點、近月／當週、OI、法人／外資／造市商資料。Call Wall、Put Wall、Gamma Wall、Gamma Flip、Max Pain 均須標記來源、計算方式、日期時間與有效性；無可靠資料時標記 `MISSING` 或 `INSUFFICIENT_DATA`。

### 第 5 階段

完整遵守 `REPORT_TEMPLATE.md` 與 `DASHBOARD_SPEC.md`。報告與 Dashboard 必須合法、完整、一致且可追溯；不得使用猜測值，且不得把合理的上一交易日資料誤標為 `OLD_DATE`。

### 第 6 階段

逐項驗證六階段證據、必要文件、報告模板、Dashboard JSON、錯誤、警告、資料缺失、日期有效性、延遲、Retry、fallback 與限制。未驗證項目不得宣稱完成。

## 8. 階段狀態與結案

允許狀態：`PENDING`、`RUNNING`、`COMPLETED`、`FAILED`、`BLOCKED`、`RETRY_REQUIRED`。

沒有實際執行證據，不得將階段標記為 `COMPLETED`。

單一文件、資料源或分析模組失敗，不得直接停止整個流程。必須記錄錯誤並執行可行 fallback 或 Retry。

流程最終必須產出完整 Markdown 分析報告，或明確列出已完成項目、失敗項目、資料缺漏、錯誤原因與限制的 Markdown 錯誤報告後，才可結束。

## 9. 必要文件讀取清單

第 1 階段必須逐一讀取以下 11 份文件的實際內容：

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

## 10. 每回合固定回報

每回合必須回報：

1. 本回合實際執行項目
2. 實際結果與證據
3. 文件／資料讀取狀態
4. 規則核對結果
5. 資料日期有效性判定
6. Retry 次數與結果
7. Fallback 結果
8. 錯誤與限制
9. Gate 結果
10. 階段狀態
11. 尚未執行項目
12. 下一個合法指令
