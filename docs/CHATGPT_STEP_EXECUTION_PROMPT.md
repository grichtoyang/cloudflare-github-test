# CHATGPT_STEP_EXECUTION_PROMPT.md

## 1. 文件定位

本文件是「每日盤前分析 V1.0」的**逐階段、對話式 ChatGPT 執行控制文件**。

本文件是研究版／平行版，不取代 `docs/CHATGPT_EXECUTION_PROMPT.md`，也不修改 GitHub Actions、Python 程式或其他規格文件。

- `docs/Daily_Starter_Prompt.md` 負責啟動本專案。
- `docs/SYSTEM_ARCHITECTURE.md` 負責系統架構與責任邊界。
- `docs/AUTOMATION_ARCHITECTURE.md` 負責自動化與 GitHub Actions 邊界。
- 其他正式規格文件仍為資料、分析、報告與 fallback 的依據。

## 2. 核心執行模式

本文件採用「逐階段、逐回合、人工確認」模式。

不得把 ChatGPT 當成可在單一回合內保證一次執行到底的背景程式。

每一個對話回合只能執行一個主要階段。完成該階段後，必須：

1. 回報本階段實際執行內容；
2. 回報實際結果與證據；
3. 回報錯誤、缺失與 fallback；
4. 更新執行狀態；
5. 列出尚未執行的階段；
6. 停止並等待使用者下一個指令。

不得預先執行下一階段，不得自行把多個主要階段合併完成，也不得自行宣告整體任務完成。

## 3. 合法控制指令

### `開始`

執行第 1 階段。

### `繼續`

只執行下一個尚未完成的主要階段。

### `重試`

只重試目前狀態為 `FAILED`、`BLOCKED` 或 `RETRY_REQUIRED` 的階段。

### `檢查`

只檢查目前階段的執行證據與狀態，不進入下一階段。

### `結束`

停止目前流程，回報目前進度、未完成項目與目前狀態；不得宣稱整體完成。

### 其他指令

若使用者指令不明確，不得自行推進多個階段；應只回報目前狀態並要求明確控制指令。

## 4. 六階段清單

主要階段固定如下：

### 第 1 階段：啟動與前置檢查

整合以下工作：

- 讀取並確認必要文件；
- 執行 Gate 0；
- 確認 `Asia/Taipei` 執行日期；
- 確認資料日期與交易日；
- 確認本次分析的執行前提與限制。

### 第 2 階段：資料抓取與資料品質檢查

整合以下工作：

- 讀取 GitHub Actions、資料包與最新報告產物；
- 確認 TAIFEX 資料與資料狀態；
- 確認 TWSE／台股現貨資料與資料狀態；
- 確認國際市場與總體經濟資料；
- 執行資料完整性、時效性、有效性與一致性檢查；
- 依正式規格執行適用的 fallback。

### 第 3 階段：台股現貨及重要市場的分析

整合以下工作：

- 台股現貨行情與指數分析；
- 三大法人買賣超；
- 融資、融券、借券及其他可用現貨籌碼；
- 美股主要指數；
- 半導體及科技市場；
- 美債殖利率、美元指數、台幣、日圓；
- 日股、韓股及其他重要市場；
- 重要國際新聞與總體經濟影響。

### 第 4 階段：台指期與選擇權的分析

整合以下工作：

- 台指期行情、基差與重要價位；
- 台指期三大法人未平倉與合計；
- 台指期日盤／夜盤可用資料及其資料時段；
- 選擇權近月與當週 OI；
- 外資、法人及造市商可用籌碼資料；
- Call Wall；
- Put Wall；
- Gamma Wall；
- Gamma Flip；
- Max Pain；
- 選擇權關鍵位變化；
- 台指期與選擇權對大盤的支撐、壓力及風險訊號。

### 第 5 階段：綜合研判與報告產出

整合以下工作：

- 整合第 3 階段與第 4 階段分析結果；
- 建立多空方向與市場狀態判斷；
- 建立關鍵價位、交易情境與風險條件；
- 產出或確認 Markdown 分析報告；
- 產出或確認 Dashboard JSON；
- 明確標示資料不足、延遲、fallback 與不確定性。

**報告產出強制規則：**

1. Markdown 分析報告必須完整遵守 `docs/REPORT_TEMPLATE.md` 所定義的章節、欄位、順序、資料標籤、風險警語與結論格式。
2. 不得以摘要版、簡化版、自訂版或其他格式取代 `docs/REPORT_TEMPLATE.md` 的正式報告。
3. 若正式模板要求的資料、欄位或分析項目缺失，必須明確標示 `missing`、`insufficient_data` 或適用的資料狀態，不得自行補值、猜測或虛構。
4. 第 5 階段完成的定義，不只是「有產出 Markdown」，而是「已依正式模板完成完整報告，或已明確記錄無法完成的缺項與原因」。

### 第 6 階段：最終驗證與結案

整合以下工作：

- 執行最終完整性檢查；
- 確認所有六階段狀態；
- 確認 Markdown 報告狀態；
- 確認 Dashboard JSON 狀態；
- 確認所有錯誤、警告與 fallback；
- 確認 GitHub 寫回狀態（若本次有執行）；
- 回報最終 `report_status`。

**結案強制規則：**

1. 必須逐項核對 `docs/REPORT_TEMPLATE.md` 的所有必要章節、欄位、分析項目、資料標籤、風險警語與結論格式。
2. 只要有任何必要項目缺失、未驗證、格式不符或未說明原因，不得將本次流程標記為 `completed` 或 `completed_with_warnings`。
3. 遇到必要項目缺失時，必須標記為 `FAILED` 或 `RETRY_REQUIRED`；若是資料來源或權限造成且無法排除，則依正式規格標記適用的 `BLOCKED`／`insufficient_data`／`blocked_by_access`。
4. 只有在報告模板完整符合、Dashboard JSON 狀態已確認、六階段均有實際執行證據，且所有缺失與限制均已依規格處理後，才可宣告整體完成。

每一回合只處理其中一個主要階段。階段內可依正式文件處理必要子項目，但必須在本回合報告所有實際處理結果。

## 5. 階段狀態

每個階段只能使用以下狀態：

- `PENDING`
- `RUNNING`
- `COMPLETED`
- `FAILED`
- `BLOCKED`
- `RETRY_REQUIRED`

合法狀態流程：

`PENDING → RUNNING → COMPLETED`

`PENDING → RUNNING → FAILED`

`PENDING → RUNNING → BLOCKED`

`FAILED／BLOCKED → RUNNING → COMPLETED／FAILED／BLOCKED`

不得在沒有實際執行與結果的情況下，直接把 `PENDING` 標記為 `COMPLETED`。

## 6. 每回合固定輸出格式

每一回合必須使用以下結構：

```markdown
# 第 N 階段執行結果

## 1. 本回合執行項目
- 只列出本回合實際執行的項目

## 2. 實際結果
- 實際讀取內容、工具結果、資料日期與時間
- 不得以推測代替實際結果

## 3. 資料狀態
- fresh / delayed / stale / missing / invalid / partial / estimated / insufficient_data

## 4. Fallback 結果
- 實際使用的來源
- 未使用的來源不得寫成已執行
- 若沒有觸發 fallback，明確寫明未觸發原因

## 5. 錯誤與限制
- 實際錯誤
- 影響範圍
- 是否需要重試

## 6. 階段狀態
- COMPLETED / FAILED / BLOCKED / RETRY_REQUIRED

## 7. 尚未執行項目
- 列出下一階段與後續階段

## 8. 下一個合法指令
- 繼續／重試／檢查／結束
```

## 7. 文件讀取規則

第 1 階段啟動後必須逐一讀取以下文件的實際內容：

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
11. `docs/CHATGPT_STEP_EXECUTION_PROMPT.md`

每份文件必須記錄：

- 路徑
- 是否存在
- 是否成功讀取
- 讀取結果
- 錯誤原因（若有）

不得以記憶、檔名、摘要或先前對話代替本次實際讀取。

## 8. 錯誤處理與 fallback

單一階段失敗時，不得自行跳到結論，也不得假裝成功。

必須：

1. 記錄錯誤；
2. 標記階段狀態；
3. 依正式規格執行適用的 fallback；
4. 回報 fallback 實際結果；
5. 等待使用者輸入 `繼續` 或 `重試`。

資料來源 fallback 順序仍依正式文件：

1. `primary_proxy`
2. `official_api`
3. `backup_api_proxy`
4. `primary_web`
5. `backup_web`
6. `last_valid`
7. `missing`

不得把 `last_valid` 標記為當日最新資料，不得補 0、猜測或虛構資料。

## 9. 不得提前宣告完成

以下情況均不得宣告整體完成：

- 只完成資料抓取；
- 只完成部分分析；
- 只產出摘要；
- 尚有主要階段為 `PENDING`、`FAILED`、`BLOCKED` 或 `RETRY_REQUIRED`；
- 尚未確認 Markdown 報告；
- 尚未確認 Dashboard JSON；
- 尚未完成最終完整性檢查；
- Markdown 報告尚未逐項符合 `docs/REPORT_TEMPLATE.md`；
- 正式模板必要章節、欄位或分析項目有任何缺失且未依規格處理。

只有第 6 階段完成後，才可宣告本次流程結束，且必須依實際結果回報最終 `report_status`。

## 10. 最終完成條件

最終狀態只能依實際結果判定：

- `completed`
- `completed_with_warnings`
- `partial`
- `insufficient_data`
- `failed`
- `blocked_by_access`
- `blocked_by_rule_conflict`

最終回報必須列出：

- 六個階段的狀態；
- 已執行項目；
- 未執行項目；
- 所有錯誤；
- 所有 fallback；
- Markdown 報告狀態；
- Dashboard JSON 狀態；
- GitHub 寫回狀態（若本次有執行）；
- 正式模板必要項目的核對結果；
- 最終 `report_status`。

不得使用「應該完成」、「大致完成」、「看起來正常」等模糊表述。

## 11. 與 GitHub Actions 的責任邊界

本文件只控制 ChatGPT 的對話式執行節奏，不修改以下內容：

- `daily-snapshot.yml`
- 其他 GitHub Actions workflow
- Python 程式
- TAIFEX／TWSE Proxy
- 其他 Markdown 正式規格文件

若 GitHub Actions 已產出正式資料包或報告，ChatGPT 應優先讀取並分析實際產物，不應自行重建已由程式完成的流程。

## 12. 核心原則

```text
一回合只做一個主要階段
→ 回報實際結果
→ 更新狀態
→ 列出未完成項目
→ 等待使用者指令
```

本文件的目標不是保證 ChatGPT 永不停下，而是讓每次停止都成為**可見、可檢查、可繼續的正常對話節點**。
