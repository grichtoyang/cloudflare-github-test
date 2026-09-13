# 每日盤前分析 V1.0 — 錯誤與 Fallback 規範

**文件狀態：Review Draft（已修正版，待最終跨文件驗證）**  
**適用專案：每日盤前分析 V1.0**  
**時區：Asia/Taipei**  
**主要儲存庫：`grichtoyang/cloudflare-github-test`**  
**主要分支：`main`**

## 1. 文件目的

本文件定義錯誤處理、資料驗證失敗、Fallback、模組降級、報告產出及最終狀態判定規則。

本文件必須與 `SYSTEM_ARCHITECTURE.md`、`DATA_SOURCES.md`、`DATA_SCHEMA.md`、`ANALYSIS_RULES.md`、`REPORT_TEMPLATE.md` 及 `CHATGPT_EXECUTION_PROMPT.md` 一致。

## 2. 核心硬性原則

一旦開始執行，無論中間發生任何一般錯誤，都不得提前停止；必須盡可能完成：

- Markdown 報告或最小錯誤報告
- Dashboard JSON 或 `partial` JSON
- 資料品質總覽
- 錯誤紀錄
- Fallback 紀錄
- 未完成項目
- 風險與限制
- 最終執行狀態

單一來源、單一模組、報告產出或 GitHub 寫回失敗，不得直接中止整體流程。

唯一規則級例外為 `RULE_CONFLICT`：不得自行猜測衝突規則的優先順序，也不得產生受衝突影響的結論；但仍須產出錯誤紀錄、可產出的降級結果及最終狀態。

## 3. Fallback 固定順序

Fallback 順序依 `DATA_SOURCES.md` 及 `DATA_SCHEMA.md` 統一為：

1. `primary_proxy`：已驗證的主要 Cloudflare Worker Proxy
2. `official_api_fallback`：官方 Open API
3. `web_scraping_fallback`：已允許且通過驗證的網站資料
4. `last_valid`：最近一次有效資料，僅限資料性質允許
5. `missing`：無法取得有效資料

同一層內的實際來源、endpoint 及適用資料項目，依 `DATA_SOURCES.md` 或資料項目設定定義；本文件不得自行擴張來源角色。

不得任意跳過可用且已驗證的前順位來源。若來源不適用於該資料項目，必須記錄不適用原因，不得視為未嘗試。

### 3.1 最近一次有效資料限制

只有資料性質允許時才可使用 `last_valid`，且必須同時標記：

```text
source_role=last_valid
data_status=stale
fallback.used=true
```

不得將舊資料描述為當日實際資料；不得用於當日行情、成交量、法人流量、未平倉量、選擇權鏈或其他要求當日狀態的判斷，除非正式規格明確允許。

## 4. 資料狀態、來源角色與 Fallback 分離

### 4.1 `data_status`

允許值：

```text
fresh
delayed
stale
missing
invalid
partial
estimated
insufficient_data
```

### 4.2 `source_role`

只能使用正式 Schema 定義值：

```text
primary_proxy
official_api_fallback
web_scraping_fallback
last_valid
```

實際來源名稱、網址及 endpoint 放在 `source.source_name`、`base_url`、`endpoint`、`request_url`，不得自行創造新的 `source_role` 值。

### 4.3 `fallback`

Dataset 內使用正式結構：

```json
{
  "used": true,
  "fallback_reason": "Primary proxy timeout",
  "fallback_source": "official_api_fallback",
  "fallback_retrieved_at": "ISO-8601"
}
```

## 5. 錯誤碼標準

```text
ACCESS_ERROR
HTTP_ERROR
TIMEOUT
PARSE_ERROR
SCHEMA_ERROR
MISSING_FIELD
EMPTY_RESPONSE
DATE_MISMATCH
STALE_DATA
SOURCE_UNAVAILABLE
VALIDATION_ERROR
MODULE_ERROR
REPORT_ERROR
DASHBOARD_ERROR
GITHUB_READ_ERROR
GITHUB_WRITE_ERROR
RULE_CONFLICT
```

## 6. 錯誤紀錄格式

### 6.1 Dataset／Package 錯誤

必須符合 `DATA_SCHEMA.md` 的欄位：

```json
{
  "error_code": "HTTP_ERROR",
  "message": "HTTP 503",
  "dataset_id": "taifex_futures_price",
  "source": "TAIFEX Proxy",
  "severity": "high",
  "retryable": true
}
```

### 6.2 Execution log 錯誤

執行追蹤可額外保存：

```json
{
  "error_id": "ERR-001",
  "stage": "data_fetch",
  "timestamp": "ISO-8601",
  "dataset_id": "taifex_futures_price",
  "source": "TAIFEX Proxy",
  "endpoint": "/futures-price",
  "error_code": "HTTP_ERROR",
  "message": "HTTP 503",
  "fallback_attempted": true,
  "fallback_used": true,
  "fallback_source": "official_api_fallback",
  "impact": "台指期價格資料不可用",
  "next_action": "依規定嘗試官方 Open API"
}
```

範例中的時間、來源、錯誤內容及處理結果不得冒充實際執行結果。

## 7. 各類錯誤處理

### 7.1 存取、HTTP、逾時及來源不可用

1. 保存錯誤及時間。
2. 判定下一個適用且已定義的 Fallback。
3. 依固定順序嘗試。
4. 全部失敗時標記 `missing` 或 `insufficient_data`。
5. 將影響傳遞至資料品質、分析、報告及 Dashboard。

### 7.2 解析、Schema、欄位及驗證錯誤

1. 保留原始回應。
2. 記錄失敗欄位或結構。
3. 不得將不完整資料視為有效資料。
4. 嘗試下一個適用 Fallback。
5. 僅部分欄位有效時標記 `partial` 並列出缺失欄位。

### 7.3 日期不一致或資料過期

1. 比對 `analysis_date`、`data_date`、`data_timestamp`。
2. 標記 `DATE_MISMATCH` 或 `STALE_DATA`。
3. 不得標記為 `fresh`。
4. 僅在正式規格允許時使用 `last_valid`。
5. 在報告中揭露限制並降低結論可信度。

### 7.4 單一分析模組失敗

- 其他模組繼續執行。
- 該模組標記 `failed`、`partial` 或 `insufficient_data`。
- 報告列出原因、缺少資料及影響。
- 不得以猜測補出結論。
- 綜合判斷必須反映資料不足及信心下降。

### 7.5 Markdown 報告失敗

盡可能產出最小錯誤報告，至少包含：

- `run_id` 或 `package_id`
- 執行時間
- 已完成階段
- `REPORT_ERROR`
- 錯誤描述
- 已產出資料位置
- 未完成項目
- 最終狀態

若連最小 Markdown 也無法寫入，必須保留可用的結構化錯誤輸出及執行環境產物，並標記 `REPORT_ERROR`。

### 7.6 Dashboard 失敗

- 優先產出保留核心欄位的 `partial` JSON。
- 保留可用模組資料。
- 記錄 `DASHBOARD_ERROR`。
- 不得讓 Dashboard 失敗抹除 Markdown 報告。
- `partial` JSON 應盡可能保留 `package_id`、`data_quality`、`modules` 或 `datasets`、`errors`、`fallbacks`、`incomplete_items`、`risks_and_limits` 及 `final_status`。

### 7.7 GitHub 讀取或寫回失敗

GitHub 讀取失敗：

- 記錄 `GITHUB_READ_ERROR`。
- 不得宣稱檔案已載入。
- 必要規格無法取得時標記 `blocked_by_access`；若同時存在規則衝突，依狀態優先順序判定。
- 仍須產出可產出的錯誤報告。

GitHub 寫回失敗：

- 記錄 `GITHUB_WRITE_ERROR`。
- 報告與 Dashboard 必須先在執行環境產出。
- 不得刪除或覆蓋已產出的結果。
- 必須保留執行環境產物或 workflow artifact（若執行環境支援）。
- 最終狀態不得標示為完整寫回成功。

## 8. Fallback 紀錄格式

```json
{
  "fallback_id": "FB-001",
  "dataset_id": "taifex_futures_price",
  "failed_source": "primary_proxy",
  "failed_error_code": "TIMEOUT",
  "fallback_source": "official_api_fallback",
  "attempt_time": "ISO-8601",
  "result": "success",
  "data_status": "delayed",
  "reason": "Primary proxy timeout"
}
```

## 9. 最終狀態判定

優先順序固定為：

```text
blocked_by_rule_conflict
> blocked_by_access
> failed_but_report_generated
> partial
> completed_with_warnings
> completed
```

- `completed`：必要資料、分析、Markdown、Dashboard 及必要寫回均完成。
- `completed_with_warnings`：主要流程完成，僅有不影響核心結果的警告。
- `partial`：部分資料、模組或交付項目未完成，但仍有可用結果。
- `failed_but_report_generated`：主要流程失敗，但仍成功產出報告。
- `blocked_by_access`：關鍵規格、資料或必要資源因存取問題無法取得。
- `blocked_by_rule_conflict`：規格衝突導致無法安全判定或執行。

## 10. 最低交付要求

無論結果為何，必須盡可能產出：

- Markdown 報告或最小錯誤報告
- Dashboard JSON 或 `partial` JSON
- 資料品質總覽
- 錯誤清單
- Fallback 清單
- 未完成項目
- 風險與限制
- 最終執行狀態

## 11. 硬性禁止事項

不得：

- 虛構資料、來源、時間或錯誤結果
- 把缺失資料填為零
- 把估算值當成實際值
- 把延遲或過期資料當成即時資料
- 未嘗試適用的 Fallback 就直接宣告資料缺失
- 未讀取檔案內容卻宣稱已載入
- 因單一一般錯誤提前停止
- 自行修改已定案規則
- 在規則衝突時自行選擇一方並繼續推論
- 自動下單或執行交易

## 12. 定案條件

本文件只有在完成以下項目後，才可將狀態改為 `定案版`：

1. 與 `SYSTEM_ARCHITECTURE.md` 一致。
2. 與 `DATA_SOURCES.md` 的來源角色及 Fallback 順序一致。
3. 與 `DATA_SCHEMA.md` 的 Package、Dataset、Error、Fallback 及狀態欄位一致。
4. 與 `ANALYSIS_RULES.md`、`REPORT_TEMPLATE.md` 及 `CHATGPT_EXECUTION_PROMPT.md` 完成交叉驗證。
5. 完成實際執行測試，確認一般錯誤不會提前停止。
6. 完成第二輪 Review 且無未解決衝突。
