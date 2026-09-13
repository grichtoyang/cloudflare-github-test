# 每日盤前分析 V1.0 — 錯誤與 Fallback 規範

**文件狀態：定案版**  
**文件版本：V1.0**  
**適用專案：每日盤前分析 V1.0**  
**時區：Asia/Taipei**  
**主要儲存庫：`grichtoyang/cloudflare-github-test`**  
**主要分支：`main`**

## 1. 文件目的

本文件定義錯誤處理、資料驗證失敗、Fallback、模組降級、報告產出及最終狀態判定規則。內容必須與 `SYSTEM_ARCHITECTURE.md`、`DATA_SOURCES.md`、`DATA_SCHEMA.md`、`ANALYSIS_RULES.md`、`REPORT_TEMPLATE.md` 及 `CHATGPT_EXECUTION_PROMPT.md` 一致。

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

單一來源、單一模組、報告產出或 GitHub 寫回失敗，不得直接中止整體流程。規則衝突時不得猜測或產出受衝突影響的結論，但仍須產出錯誤紀錄、降級結果及最終狀態。

## 3. Fallback 固定順序

所有資料集統一依下列順序，並只使用適用且已驗證的來源：

1. `primary_proxy`：已驗證的主要 Cloudflare Worker Proxy
2. `official_api`：官方 Open API
3. `backup_api_proxy`：官方備援 API／Proxy
4. `primary_web`：已驗證的主要金融資料來源
5. `backup_web`：已驗證的備援金融資料來源
6. `last_valid`：最近一次有效資料，僅限資料性質允許
7. `missing`：無法取得有效資料

不得任意跳過可用且已驗證的前順位來源。來源不適用時，必須記錄不適用原因。

### 3.1 最近一次有效資料限制

只有資料性質允許時才可使用 `last_valid`，且必須同時標記：

```text
source_role=last_valid
data_status=stale
fallback.used=true
```

不得將舊資料描述為當日實際資料；不得用於當日行情、成交量、法人流量、未平倉量、選擇權鏈或其他要求當日狀態的判斷，除非正式規格明確允許。

## 4. 狀態欄位標準

### 4.1 `data_status`

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

```text
primary_proxy
official_api
backup_api_proxy
primary_web
backup_web
last_valid
```

### 4.3 `fallback_status`

```text
not_used
used
failed
```

Fallback 使用紀錄至少包含：原始來源、失敗原因、實際採用來源、資料日期、取得時間、資料狀態及對分析信心的影響。

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

## 6. 錯誤處理規則

1. 保存錯誤、時間、資料集、來源及影響。
2. 依固定順序嘗試下一個適用 Fallback。
3. 解析、Schema 或驗證失敗時，不得將資料視為有效。
4. 單一模組失敗時，其他模組繼續執行。
5. 全部來源失敗時，標記 `missing` 或 `insufficient_data`，不得猜測或補零。
6. 日期不一致或過期資料不得標記為 `fresh`。
7. GitHub 讀取或寫回失敗時，必須保留錯誤與執行環境產物；不得宣稱已成功寫回。
8. Dashboard 失敗不得抹除 Markdown 報告，應盡可能產出 `partial` JSON。

## 7. 最終報告狀態

只允許：

```text
completed
completed_with_warnings
partial
insufficient_data
failed
blocked_by_access
blocked_by_rule_conflict
```

優先順序固定為：

```text
blocked_by_rule_conflict
> blocked_by_access
> failed
> insufficient_data
> partial
> completed_with_warnings
> completed
```

- `completed`：核心資料、分析及必要交付均完成。
- `completed_with_warnings`：核心結果完成，僅有非核心警告。
- `partial`：部分模組或交付項目未完成，但仍有可用結果。
- `insufficient_data`：核心資料不足，無法形成可靠方向判斷，但仍產出報告。
- `failed`：流程或分析失敗，但仍記錄錯誤並產出可產出的報告內容。
- `blocked_by_access`：必要資料或規格因存取限制無法取得。
- `blocked_by_rule_conflict`：規則衝突導致無法安全判定或執行。

不得使用 `failed_but_report_generated`、`fallback` 或 `unknown` 作為報告狀態。

## 8. 最低交付要求

無論結果為何，必須盡可能產出：

- Markdown 報告或最小錯誤報告
- Dashboard JSON 或 `partial` JSON
- 資料品質總覽
- 錯誤清單
- Fallback 清單
- 未完成項目
- 風險與限制
- 最終執行狀態

## 9. 硬性禁止事項

不得虛構資料、來源、時間或錯誤結果；不得把缺失資料填為零；不得把估算、延遲或過期資料當成即時資料；不得未嘗試適用 Fallback 就宣告缺失；不得因單一一般錯誤提前停止；不得在規則衝突時自行選擇一方；不得自動下單或執行交易。

## 10. 定案條件

本文件與其他專案 Markdown 文件的狀態碼、來源角色、Fallback 順序、最低交付要求及規則衝突處理必須一致。完成交叉驗證後，本文件維持 `定案版` 狀態。
