# CHATGPT_STEP_EXECUTION_PROMPT.md

## 1. 文件定位

本文件是「每日盤前分析 V1.0」的逐階段、對話式 ChatGPT 執行控制文件。

本文件是研究版／平行版，不取代 `docs/CHATGPT_EXECUTION_PROMPT.md`，也不修改 GitHub Actions、Python 程式、Proxy 或其他正式規格文件。

- `docs/Daily_Starter_Prompt.md`：啟動規則。
- `docs/PROJECT_OVERVIEW.md`：專案目標與範圍。
- `docs/SYSTEM_ARCHITECTURE.md`：系統架構與責任邊界。
- `docs/DATA_SCHEMA.md`：資料結構與欄位定義。
- `docs/DATA_SOURCES.md`：資料來源與來源優先級。
- `docs/ANALYSIS_RULES.md`：分析規則，必須逐項套用。
- `docs/REPORT_TEMPLATE.md`：正式報告格式，必須完整遵守。
- `docs/DASHBOARD_SPEC.md`：Dashboard JSON 規格。
- `docs/ERROR_AND_FALLBACK.md`：錯誤與 fallback 規則。
- `docs/AUTOMATION_ARCHITECTURE.md`：自動化與 GitHub Actions 邊界。

## 2. 核心執行模式

本文件採用「逐階段、逐回合、人工確認」模式。每一回合只能執行一個主要階段。

完成該階段後，必須：

1. 回報本回合實際執行項目；
2. 回報實際結果與證據；
3. 回報資料日期、時段、來源與資料狀態；
4. 回報錯誤、缺失、限制與 fallback；
5. 更新階段狀態；
6. 列出尚未執行項目；
7. 停止並等待下一個合法指令。

不得預先執行下一階段，不得把多個主要階段合併，不得在未完成第 6 階段前宣告整體完成。

## 3. 合法控制指令

- `開始`：執行第 1 階段。
- `繼續`：只執行下一個尚未完成的主要階段。
- `重試`：只重試目前為 `FAILED`、`BLOCKED` 或 `RETRY_REQUIRED` 的階段。
- `檢查`：只檢查目前階段的證據與狀態，不進入下一階段。
- `結束`：停止流程並回報進度，不得宣稱完成。
- 其他或不明確指令：只回報目前狀態並要求合法控制指令。

## 4. 六階段清單與強制驗證

### 第 1 階段：啟動與前置檢查

必須完成：

1. 逐一實際讀取第 7 節列出的所有文件；
2. 對每份文件記錄：路徑、存在性、讀取是否成功、關鍵規則、錯誤原因；
3. 執行 Gate 0；
4. 確認 `Asia/Taipei` 的實際執行日期與時間；
5. 確認當日是否為台灣交易日；
6. 確認資料日期、資料截止時間、日盤／夜盤時段；
7. 確認本次可用資料、不可用資料、權限限制與前置阻塞。

**Gate 0 必須明確回報 PASS／FAIL／BLOCKED。** 不得只寫「已檢查」或「正常」。Gate 0 至少檢查：必要文件可讀、執行日期已鎖定、交易日判定已完成、資料前提已確認、規則衝突已揭露。

### 第 2 階段：資料抓取與資料品質檢查

必須按 `DATA_SCHEMA.md`、`DATA_SOURCES.md` 逐項核對所需資料欄位，並對每個資料集記錄：

- 資料集名稱與必要欄位；
- 實際來源、來源層級與請求結果；
- 資料日期、時間戳、交易時段；
- `fresh / delayed / stale / missing / invalid / partial / estimated / insufficient_data`；
- 欄位完整性、型別、數值合理性、重複、日期一致性；
- 是否觸發 fallback、使用哪一層、未使用層級及原因；
- 對後續分析的影響。

資料品質判定：

- 必要欄位缺失、格式錯誤或來源資料無法驗證：不得當作完整資料；
- `last_valid` 只能標記為歷史有效資料，不得標記為當日最新；
- 不得補 0、猜測、虛構或將缺失值改寫成正常值；
- 若資料只涵蓋日盤或夜盤，必須明確標示涵蓋時段，不得推論另一時段；
- 若資料不足以支持後續分析，必須標記 `insufficient_data`，並列出受影響分析項目。

### 第 3 階段：台股現貨及重要市場的分析

必須依 `docs/ANALYSIS_RULES.md` 逐項套用，不得只做概略敘述。至少核對：

- 台股現貨行情與指數；
- 三大法人買賣超；
- 融資、融券、借券及其他可用現貨籌碼；
- 美股主要指數、半導體與科技市場；
- 美債殖利率、美元指數、台幣、日圓；
- 日股、韓股及其他必要市場；
- 重要新聞與總體經濟影響。

每一分析項目必須記錄：使用資料、套用規則、分析結果、證據、限制。未有資料或未能套用規則時，必須標示原因，不得以一般性市場敘述代替。

### 第 4 階段：台指期與選擇權的分析

必須依 `DATA_SCHEMA.md`、`ANALYSIS_RULES.md` 逐項執行，並明確區分：

- 台指期日盤與夜盤；
- 選擇權資料的實際公布時點與涵蓋時段；
- 近月與當週契約；
- OI、成交量、法人／外資／造市商資料的實際可用性。

至少核對：

- 台指期行情、基差與重要價位；
- 台指期三大法人未平倉與合計；
- 選擇權近月與當週 OI；
- 可取得的外資、法人及造市商籌碼；
- Call Wall、Put Wall、Gamma Wall、Gamma Flip、Max Pain；
- 關鍵位變化、支撐壓力、風險訊號。

每個關鍵位必須標記：實際資料來源、計算／推導方式、資料日期時間、是否為當日有效值。若 Gamma、造市商或其他欄位沒有可靠資料，必須標記 `missing` 或 `insufficient_data`，不得自行推導成已確認結果。

### 第 5 階段：綜合研判與報告產出

必須整合第 3、4 階段，建立市場狀態、多空方向、關鍵價位、交易情境與風險條件。

**Markdown 報告強制規則：**

1. 完整遵守 `docs/REPORT_TEMPLATE.md` 的所有章節、欄位、順序、標籤、警語與結論格式；
2. 不得使用摘要版、簡化版、自訂版取代正式模板；
3. 必須建立逐項核對表，至少使用 `PASS / MISSING / INVALID / NOT_APPLICABLE`；
4. `MISSING`、`INVALID` 必須記錄原因、影響與是否需要重試；
5. 不得補值、猜測或虛構；
6. 報告中的數值、日期、資料狀態與分析結論必須能追溯到第 2～4 階段證據。

**Dashboard JSON 強制規則：**

1. 必須遵守 `docs/DASHBOARD_SPEC.md` 的欄位、型別、必要性與命名；
2. 必須驗證為合法 JSON；
3. 必要欄位缺失、型別錯誤、非法值或報告與 Dashboard 不一致時，不得標記完成；
4. 缺失資料必須使用正式規格允許的 `null`／狀態標籤，不得補 0 或虛構；
5. 必須確認 Dashboard JSON 與 Markdown 報告的日期、關鍵位、方向、資料狀態一致。

### 第 6 階段：最終驗證與結案

必須逐項驗證：

1. 六階段均有實際執行證據；
2. 所有必要文件均已讀取或已明確記錄阻塞原因；
3. `REPORT_TEMPLATE.md` 所有必要章節、欄位、分析項目、標籤、警語、結論格式均已核對；
4. Dashboard JSON 合法、欄位完整、型別正確且與 Markdown 一致；
5. 所有錯誤、警告、資料缺失、延遲、fallback 與限制均已揭露；
6. GitHub 寫回狀態已確認（若本次有執行）；
7. 沒有任何未說明的 `MISSING`、`INVALID`、`BLOCKED` 或未驗證項目。

只要任何必要項目缺失、未驗證、格式不符、報告與 Dashboard 不一致，便不得使用 `completed` 或 `completed_with_warnings`。應依實際情況使用 `failed`、`partial`、`insufficient_data`、`blocked_by_access` 或 `blocked_by_rule_conflict`。

## 5. 階段狀態

每個階段只能使用：

- `PENDING`
- `RUNNING`
- `COMPLETED`
- `FAILED`
- `BLOCKED`
- `RETRY_REQUIRED`

合法流程：

- `PENDING → RUNNING → COMPLETED`
- `PENDING → RUNNING → FAILED`
- `PENDING → RUNNING → BLOCKED`
- `FAILED／BLOCKED／RETRY_REQUIRED → RUNNING → COMPLETED／FAILED／BLOCKED／RETRY_REQUIRED`

不得在沒有實際執行與證據時，把 `PENDING` 改為 `COMPLETED`。

## 6. 每回合固定輸出格式

```markdown
# 第 N 階段執行結果

## 1. 本回合執行項目
- 只列實際執行項目

## 2. 實際結果與證據
- 實際讀取內容、工具結果、資料日期、時間戳、來源

## 3. 規則核對結果
- 依適用正式文件逐項列出 PASS / MISSING / INVALID / NOT_APPLICABLE

## 4. 資料狀態
- fresh / delayed / stale / missing / invalid / partial / estimated / insufficient_data

## 5. Fallback 結果
- 實際使用來源、未使用來源及原因

## 6. 錯誤與限制
- 錯誤、影響範圍、是否需要重試

## 7. 階段狀態
- COMPLETED / FAILED / BLOCKED / RETRY_REQUIRED

## 8. 尚未執行項目
- 下一階段及後續階段

## 9. 下一個合法指令
- 繼續／重試／檢查／結束
```

## 7. 必要文件讀取清單

第 1 階段必須逐一讀取以下文件的實際內容：

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

每份文件必須記錄：路徑、是否存在、是否成功讀取、關鍵規則／限制、讀取結果、錯誤原因（若有）。不得以記憶、檔名、摘要或先前對話代替本次讀取。

## 8. 錯誤處理與 fallback

單一階段失敗時，不得跳到結論或假裝成功。必須記錄錯誤、標記狀態、依正式規格執行 fallback、回報實際結果，並等待 `繼續` 或 `重試`。

資料來源 fallback 順序：

1. `primary_proxy`
2. `official_api`
3. `backup_api_proxy`
4. `primary_web`
5. `backup_web`
6. `last_valid`
7. `missing`

不得把 `last_valid` 標記為當日最新資料，不得補 0、猜測或虛構資料。

## 9. 最終 report_status 判定矩陣

- `completed`：六階段全部完成；模板逐項 PASS；Dashboard 合法且一致；無未處理必要缺項。
- `completed_with_warnings`：六階段全部完成；只有已揭露且不影響必要結論的警告；模板與 Dashboard 仍完整有效。
- `partial`：部分階段完成，或部分非必要分析未完成，但流程尚未完全結案。
- `insufficient_data`：必要資料不足，無法支持一項或多項必要分析。
- `failed`：執行、格式、驗證或寫回發生未排除的失敗。
- `blocked_by_access`：因權限、網路、來源封鎖或服務不可用而無法完成必要工作。
- `blocked_by_rule_conflict`：正式規格之間存在未解決衝突，無法安全判定或產出。

不得使用「應該完成」、「大致完成」、「看起來正常」等模糊表述。

## 10. 不得提前宣告完成

以下任一情況均不得宣告整體完成：

- 只完成資料抓取或部分分析；
- 只產出摘要；
- 尚有階段為 `PENDING`、`FAILED`、`BLOCKED` 或 `RETRY_REQUIRED`；
- 尚未逐項驗證正式報告模板；
- 尚未驗證 Dashboard JSON；
- Markdown 與 Dashboard 不一致；
- 尚有必要缺項、未驗證項目或未說明限制；
- 尚未完成第 6 階段。

## 11. 與 GitHub Actions 的責任邊界

本文件只控制 ChatGPT 的對話式執行節奏，不修改：

- `daily-snapshot.yml` 或其他 GitHub Actions workflow；
- Python 程式；
- TAIFEX／TWSE Proxy；
- 其他正式 Markdown／YAML／JSON 規格文件。

若 GitHub Actions 已產出正式資料包或報告，ChatGPT 應優先讀取並分析實際產物，不應自行重建已由程式完成的流程。

## 12. 核心原則

```text
一回合只做一個主要階段
→ 實際讀取與執行
→ 逐項核對正式規格
→ 回報證據、資料狀態、錯誤與 fallback
→ 更新狀態
→ 列出未完成項目
→ 等待使用者指令
```

本文件的目標不是保證 ChatGPT 永不停下，而是讓每次停止都成為可見、可檢查、可繼續的正常對話節點。
