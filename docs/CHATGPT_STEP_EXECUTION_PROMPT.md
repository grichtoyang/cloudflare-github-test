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

## 4. 第 1 階段與 Gate 0

第 1 階段必須：

1. 逐一讀取第 8 節列出的 11 份必要文件的實際內容；
2. 記錄每份文件的來源、路徑、實際內容取得狀態、關鍵規則與錯誤原因；
3. 鎖定 `Asia/Taipei` 執行日期與時間；
4. 判定台灣交易日；
5. 確認資料日期、截止時間、日盤／夜盤涵蓋狀態；
6. 回報 Gate 0：`PASS`、`FAIL` 或 `BLOCKED`。

### 4.1 文件讀取協定

對每份文件依序執行：

1. 先檢查本次對話附件；
2. 附件存在時，讀取附件實際內容；
3. 附件不存在時，讀取 GitHub `main` 分支的同一路徑；
4. 只有取得文件實際文字內容，才可標記 `READ_SUCCESS`；
5. 只看到檔名、目錄項目、URL 或 SHA，不算已讀取；
6. 文件已確認存在但內容無法取得，標記 `READ_FAILED` 或 `BLOCKED`；
7. 只有確認路徑不存在，才標記 `MISSING`；
8. 只取得部分內容，標記 `PARTIAL` 並列出未取得範圍。

### 4.2 Gate 0 判定

- `PASS`：11 份必要文件均已取得實際內容，且日期、交易日與資料前提均已確認。
- `BLOCKED`：必要文件已確認存在，但至少一份實際內容無法取得，且已完成可行的讀取、重試與 fallback。
- `FAIL`：必要條件未完成，原因不是文件存取阻擋，例如日期未鎖定、交易日未判定或規則衝突未揭露。

單一文件讀取失敗時，不得立即停止第 1 階段。必須繼續檢查其餘文件，完成所有可行讀取與 fallback 後，才可判定 Gate 0。

`BLOCKED` 不等於 `MISSING`，不得互相替換，也不得把 `BLOCKED` 改寫成 `PASS` 或 `COMPLETED`。

## 5. 其餘階段要求

### 第 2 階段

依 `DATA_SCHEMA.md`、`DATA_SOURCES.md` 逐項核對資料集、欄位、來源、日期、時間戳、交易時段、資料品質、fallback 與影響。不得補 0、猜測或虛構。

### 第 3 階段

依 `ANALYSIS_RULES.md` 分析台股現貨、三大法人、融資融券借券、美股、半導體、美債、美元、台幣、日圓、日韓股與重要新聞；每項均須有資料、規則、結果與限制。

### 第 4 階段

明確區分台指期日盤／夜盤、選擇權實際公布時點、近月／當週、OI、法人／外資／造市商資料。Call Wall、Put Wall、Gamma Wall、Gamma Flip、Max Pain 均須標記來源、計算方式、日期時間與有效性；無可靠資料時標記 `missing` 或 `insufficient_data`。

### 第 5 階段

完整遵守 `REPORT_TEMPLATE.md` 與 `DASHBOARD_SPEC.md`。報告與 Dashboard 必須合法、完整、一致且可追溯；不得使用猜測值。

### 第 6 階段

逐項驗證六階段證據、必要文件、報告模板、Dashboard JSON、錯誤、警告、資料缺失、延遲、fallback 與限制。未驗證項目不得宣稱完成。

## 6. 階段狀態

允許狀態：`PENDING`、`RUNNING`、`COMPLETED`、`FAILED`、`BLOCKED`、`RETRY_REQUIRED`。

沒有實際執行證據，不得將階段標記為 `COMPLETED`。

## 7. 每回合固定回報

每回合必須回報：

1. 本回合實際執行項目
2. 實際結果與證據
3. 文件／資料讀取狀態
4. 規則核對結果
5. 資料狀態
6. Fallback 結果
7. 錯誤與限制
8. Gate 結果
9. 階段狀態
10. 尚未執行項目
11. 下一個合法指令

## 8. 必要文件讀取清單

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

## 9. 錯誤與結案規則

單一文件、資料源或分析模組失敗，不得直接停止整個流程。必須記錄錯誤並執行可行 fallback 或重試。

流程最終必須產出完整 Markdown 分析報告，或明確列出已完成項目、失敗項目、資料缺漏、錯誤原因與限制的 Markdown 錯誤報告後，才可結束。
