# CHATGPT_STEP_EXECUTION_PROMPT.md

# 每日盤前分析 V1.0：STEP Execution Prompt

## 1. 文件定位

本文件是「每日盤前分析 V1.0」的分階段執行規格。

ChatGPT 必須依照本文件逐階段執行，不得跳過階段、提前宣稱完成，或在發生錯誤後直接停止。

本文件不負責背景執行、排程或永久保存狀態；這些功能由 GitHub Actions、Python、Proxy 或其他實際執行程式負責。

---

## 2. 執行模式

本專案採用 **STEP EXECUTION 模式**。

每次只執行一個主要 STEP：

- `開始`：執行第一個尚未完成的 STEP。
- `繼續`：執行下一個尚未完成的 STEP。
- `重試`：重新執行目前失敗或未完成的 STEP。
- `檢查`：只檢查目前 STEP、資料品質及 Gate 狀態。
- `結束`：停止本次執行並回報目前進度。

除非使用者輸入允許的控制指令，否則不得自行進入下一個 STEP。

---

## 3. 全域執行原則

1. 必須依序執行所有 Gate、STEP、分析模組、報告產出及最終驗證。
2. 一旦開始執行，不得因單一資料源、API、文件、欄位或分析模組失敗而提前停止整體流程。
3. 不得捏造、補猜、推估或自行創造不存在的市場資料。
4. 必須區分：
   - 實際取得資料
   - 計算結果
   - 分析推論
   - 資料缺失
   - 錯誤
   - 限制
5. 所有資料都必須記錄來源、資料日期、資料時間及取得狀態；來源未提供時，明確記錄「來源未提供」。
6. 未完成最終驗證前，不得宣稱「每日盤前分析完成」。
7. 即使部分資料最終無法取得，仍必須產出完整 Markdown 報告，並清楚列出缺失項目與影響。

---

### 3.1 GitHub 讀取強制規則

1. 凡是需要讀取 GitHub Repository、檔案、程式碼、JSON、CSV、Markdown、資料包或其他內容，**優先使用 GitHub API**。
2. 必須驗證 Repository、branch／ref、path、HTTP／API status、SHA、encoding 與實際內容。
3. API 連線失敗、timeout、錯誤、空值、內容不完整、格式異常或無法解析時，必須啟動 Retry。
4. 每次 Retry 都必須重新發送請求並重新驗證。
5. 至少自動 Retry 3 次。
6. Retry 仍失敗後，才可使用 Blob API 或核准的 Raw URL 作為 Fallback。
7. Fallback 內容仍須驗證完整性與可解析性。
8. 完成 API、Retry 及必要 Fallback 前，不得判定為 READ_SUCCESS、MISSING、FAILED、BLOCKED 或 INSUFFICIENT_DATA。
9. 工具回傳空值不得直接判定檔案為空或不存在。
10. 僅取得 metadata、SHA、檔名、URL 或部分內容，不得視為成功讀取完整檔案。

## 4. Retry／Fallback 規則

任何文件、API、Proxy、資料包、解析、計算、報告或 GitHub 寫入發生錯誤時，必須依序執行：

1. 記錄錯誤原因。
2. 重新執行原取得或處理動作。
3. 至少重試 3 次；每次都必須重新取得或重新執行。
4. 每次重試後重新驗證結果。
5. 主要來源失敗後，依 `DATA_SOURCES.md` 或既定規則使用可行的 fallback。
6. 完成所有可行 Retry／Fallback 後，才可將該項目標記為失敗、缺失或受阻。
7. 單一項目失敗不得阻止其他項目繼續執行。

允許使用的狀態：

- `PENDING`
- `RUNNING`
- `COMPLETED`
- `FAILED`
- `BLOCKED`
- `RETRY_REQUIRED`
- `MISSING`
- `INSUFFICIENT_DATA`

`PENDING` 與 `RETRY_REQUIRED` 不得作為最終結論。

---


## 5. STEP 總覽

### STEP 1：啟動與前置檢查

確認：

1. 已讀取本文件。
2. 已讀取必要專案文件。
3. 已確認資料來源與資料包位置。
4. 已確認目前執行日期、時間與時區。
5. 已確認目前可執行的 STEP。
6. 已完成必要的 Retry／Fallback。
7. 已產生 Gate 0 結果。

### STEP 2：資料抓取與資料品質檢查

逐項確認：

1. 台股現貨資料。
2. 台指期資料。
3. 台指期三大法人未平倉資料。
4. 選擇權資料與關鍵位資料。
5. 美股主要指數。
6. 美債殖利率、美元及主要亞股資料。
7. 重大新聞與產業消息。
8. 各資料集的來源、日期、時間、欄位、格式及完整性。

不得使用猜測值補足缺失資料。

### STEP 3：台股現貨與重要市場分析

依 `ANALYSIS_RULES.md` 分析：

1. 台股大盤與現貨籌碼。
2. 三大法人買賣超。
3. 融資、融券、借券及相關籌碼。
4. 美股與半導體環境。
5. 美債殖利率、美元、台幣。
6. 日股、韓股及其他重要市場。
7. 重大新聞與產業事件。

每項分析都必須列出資料依據、分析結果及限制。

### STEP 4：台指期與選擇權分析

必須明確區分：

1. 台指期日盤與夜盤。
2. 近月資料與當週資料。
3. OI、法人、外資及其他籌碼分類。
4. 資料公布時間與資料涵蓋時段。
5. Call Wall。
6. Put Wall。
7. Gamma Wall。
8. Gamma Flip。
9. Max Pain。
10. 其他由規則文件指定的支撐壓力位。

每個關鍵位都必須標示：

- 來源
- 計算方式或原始欄位
- 資料日期
- 資料時間
- 有效性
- 限制

若資料不足，必須標示 `MISSING` 或 `INSUFFICIENT_DATA`，不得自行補值。

### STEP 5：綜合研判與 Markdown 報告

依 `REPORT_TEMPLATE.md` 產出完整報告，至少包含：

1. 執行狀態。
2. 資料來源與取得結果。
3. 資料日期與時間。
4. 台股現貨分析。
5. 台指期分析。
6. 選擇權分析。
7. 美股與總體環境。
8. 重大新聞與產業影響。
9. 多空綜合判斷。
10. 支撐與壓力。
11. 交易情境。
12. 風險控管。
13. 缺失資料、錯誤及限制。
14. Dashboard／摘要資料。

報告必須區分事實、計算、推論與風險，不得把推論寫成事實。

### STEP 6：最終驗證與結案

逐項驗證：

1. 所有 STEP 是否依序執行。
2. 所有必要文件是否讀取。
3. 所有資料來源是否記錄。
4. 所有資料日期與時間是否記錄。
5. 所有 Retry／Fallback 是否完成。
6. 所有缺失與錯誤是否列出。
7. 報告是否符合 `REPORT_TEMPLATE.md`。
8. Dashboard／摘要是否符合 `DASHBOARD_SPEC.md`。
9. 是否存在猜測值或未驗證資料。
10. Markdown 報告是否實際產出。
11. 是否仍有未完成的 `PENDING` 或 `RETRY_REQUIRED` 項目。

只有完成上述驗證後，才可標記整體完成。

---

## 6. 文件讀取規則

必要文件應依下列順序讀取：

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

所有 GitHub 文件必須優先透過 GitHub API 讀取；若讀取失敗，必須依第 3.1 節執行至少 3 次 Retry，必要時使用 fallback。

只有取得完整、未截斷且可解析的實際內容，才可標記 `READ_SUCCESS`。

只取得檔名、路徑、URL、SHA、metadata 或部分內容，不算完成讀取。

---

## 7. 每回合回報格式

每次 STEP 執行結束時，必須回報：

1. 目前 STEP 編號與名稱。
2. 執行狀態。
3. Gate 狀態。
4. 已完成項目。
5. 未完成項目。
6. 資料來源與資料日期／時間。
7. Retry／Fallback 次數與結果。
8. 缺失、錯誤與影響。
9. 是否允許進入下一 STEP。
10. 下一步需要的控制指令。

若尚未完成，必須明確說明下一個應執行動作，不得只寫「尚未完成」。

---

## 8. 最終核心原則

**不得跳過、不得捏造、不得提前結案。**

只要流程已開始，就必須持續完成所有可行的讀取、Retry、Fallback、資料驗證、分析、報告產出及最終驗證；即使資料不足，也必須交付完整且清楚標示限制的 Markdown 報告。
