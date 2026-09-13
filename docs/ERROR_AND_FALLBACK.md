# 每日盤前分析 V1.0 — 錯誤與 Fallback 規範

**文件狀態：定案版**  
**適用專案：每日盤前分析 V1.0**  
**時區：Asia/Taipei**  
**主要儲存庫：`grichtoyang/cloudflare-github-test`**  
**主要分支：`main`**

## 1. 文件目的

本文件定義每日盤前分析系統的錯誤處理、資料驗證失敗處理、Fallback 順序、模組降級、報告產出及最終狀態判定規則。

本文件必須與 `SYSTEM_ARCHITECTURE.md`、`DATA_SOURCES.md`、`DATA_SCHEMA.md`、`ANALYSIS_RULES.md`、`REPORT_TEMPLATE.md` 及 `CHATGPT_EXECUTION_PROMPT.md` 一致。

## 2. 核心硬性原則

一旦開始執行每日盤前分析，無論中間發生任何錯誤，都不得提前停止；必須持續執行至盡可能產出以下項目後才能結束：

- Markdown 報告
- Dashboard JSON 或 `partial` JSON
- 資料品質總覽
- 錯誤紀錄
- Fallback 紀錄
- 未完成項目
- 風險與限制
- 最終執行狀態

單一資料來源、單一分析模組、Markdown 產出或 GitHub 寫回失敗，不得直接中止整體流程。

唯一的規則級例外是 `RULE_CONFLICT`：系統不得在無法判定應遵守哪一項規則時自行猜測或繼續產生受影響的結論；但仍須完成錯誤紀錄、降級處理及最終狀態輸出。

## 3. Fallback 固定順序

資料來源的 Fallback 順序固定如下，不得任意跳過可用且已驗證的前順位來源：

1. 已驗證 Cloudflare Worker Proxy
2. 官方 Open API
3. 備援 API／Proxy
4. 主要網站資料擷取
5. 備援網站資料擷取
6. 最近一次有效資料
7. `missing`

### 3.1 使用最近一次有效資料的限制

最近一次有效資料僅可在資料性質允許時使用，且必須同時標記：

```text
source_role=last_valid
data_status=stale
fallback.used=true
```

不得將歷史資料描述為當日實際資料，不得用於需要當日即時狀態的判斷，除非規格明確允許。

### 3.2 Fallback 禁止事項

不得：

- 將缺失資料補成 `0`
- 將估算值標記為實際值
- 將延遲資料標記為即時資料
- 將未驗證來源視為已驗證來源
- 因為某一來源失敗而直接跳到 `missing`，卻未嘗試規定中的可用備援
- 使用沒有記錄來源、時間及驗證結果的資料

## 4. 資料狀態與來源狀態分離

`fallback` 不是 `data_status`。三者必須分開記錄：

### 4.1 `data_status`

允許值：

- `fresh`
- `delayed`
- `stale`
- `missing`
- `invalid`
- `partial`
- `estimated`
- `insufficient_data`

### 4.2 `source_role`

用於表示資料來源角色，例如：

- `cloudflare_proxy`
- `official_api`
- `backup_api`
- `primary_website`
- `backup_website`
- `last_valid`

### 4.3 `fallback.used`

```text
true  = 實際使用了備援來源
false = 未使用備援來源
```

## 5. 錯誤碼標準

| 錯誤碼 | 定義 |
|---|---|
| `ACCESS_ERROR` | 權限、拒絕存取或連線被阻擋 |
| `HTTP_ERROR` | HTTP 回應為非成功狀態碼 |
| `TIMEOUT` | 請求逾時 |
| `PARSE_ERROR` | JSON、CSV 或文字解析失敗 |
| `SCHEMA_ERROR` | 回傳結構不符合預期 |
| `MISSING_FIELD` | 必要欄位缺失 |
| `EMPTY_RESPONSE` | 回應為空或無有效資料 |
| `DATE_MISMATCH` | 資料日期與要求日期不一致 |
| `STALE_DATA` | 資料超過允許時效 |
| `SOURCE_UNAVAILABLE` | 來源暫時不可用 |
| `VALIDATION_ERROR` | 資料驗證失敗 |
| `MODULE_ERROR` | 單一分析模組執行失敗 |
| `REPORT_ERROR` | Markdown 報告產出失敗 |
| `DASHBOARD_ERROR` | Dashboard JSON 產出失敗 |
| `GITHUB_READ_ERROR` | GitHub 讀取失敗 |
| `GITHUB_WRITE_ERROR` | GitHub 寫回失敗 |
| `RULE_CONFLICT` | 規格或規則互相衝突 |

## 6. 每筆錯誤的必要紀錄

每筆錯誤至少必須包含：

```json
{
  "error_id": "ERR-001",
  "stage": "data_fetch",
  "timestamp": "2026-01-01T08:00:00+08:00",
  "source": "TAIFEX",
  "endpoint": "/futures-price",
  "error_code": "HTTP_ERROR",
  "error_message": "HTTP 503",
  "fallback_attempted": true,
  "fallback_used": true,
  "fallback_source": "official_api",
  "impact": "台指期價格資料不可用",
  "next_action": "改用官方 Open API",
  "status": "warning"
}
```

實際執行時不得使用範例值冒充實際結果；時間、來源、錯誤內容及處理結果必須填入當次執行資訊。

## 7. 各類錯誤處理規則

### 7.1 存取、HTTP、逾時及來源不可用

1. 記錄原始錯誤與時間。
2. 確認是否可使用下一順位 Fallback。
3. 依固定順序嘗試備援。
4. 若所有來源失敗，標記 `missing` 或 `insufficient_data`。
5. 將影響寫入錯誤清單、Fallback 清單及報告限制。

### 7.2 解析、Schema、欄位及驗證錯誤

1. 保留原始回應。
2. 記錄失敗欄位或結構。
3. 不得將不完整資料直接視為有效資料。
4. 嘗試下一順位來源。
5. 若只有部分欄位有效，標記 `partial`，並明確列出缺失欄位。

### 7.3 日期不一致或資料過期

1. 比對資料日期、時間及要求日期。
2. 標記 `DATE_MISMATCH` 或 `STALE_DATA`。
3. 不得把日期不符資料標記為 `fresh`。
4. 只有在規格允許時才使用最近一次有效資料。
5. 在分析結論中降低可信度並揭露限制。

### 7.4 單一分析模組失敗

單一模組失敗時：

- 其他模組必須繼續執行
- 該模組標記為 `failed`、`partial` 或 `insufficient_data`
- 報告列出失敗原因、缺少資料及對結論的影響
- 不得用猜測補出結論
- 綜合判斷必須反映資料不足及信心下降

### 7.5 Markdown 報告產出失敗

若完整 Markdown 產出失敗，仍須盡可能產出最小錯誤報告，至少包含：

- `run_id`
- 執行時間
- 已完成階段
- 錯誤碼 `REPORT_ERROR`
- 錯誤描述
- 已產出資料位置
- 未完成項目
- 最終狀態

### 7.6 Dashboard 產出失敗

若完整 Dashboard JSON 產出失敗：

- 優先產出結構化 `partial` JSON
- 保留可用模組資料
- 標記 `DASHBOARD_ERROR`
- 不得讓 Dashboard 失敗抹除 Markdown 報告

### 7.7 GitHub 讀取或寫回失敗

GitHub 讀取失敗時：

- 記錄 `GITHUB_READ_ERROR`
- 不得宣稱檔案已載入
- 若無法取得必要規格，標記 `blocked_by_access` 或 `blocked_by_rule_conflict`
- 仍須產出可產出的錯誤報告

GitHub 寫回失敗時：

- 記錄 `GITHUB_WRITE_ERROR`
- 報告及 Dashboard 必須先在執行環境產出
- 不得因寫回失敗而刪除或覆蓋已產出的結果
- 最終狀態不得標示為完整寫回成功

## 8. Fallback 紀錄格式

每次啟用 Fallback 至少記錄：

```json
{
  "fallback_id": "FB-001",
  "data_item": "taifex_futures_price",
  "failed_source": "cloudflare_proxy",
  "failed_error_code": "TIMEOUT",
  "fallback_source": "official_api",
  "attempt_time": "2026-01-01T08:00:00+08:00",
  "result": "success",
  "data_status": "delayed",
  "reason": "Proxy timeout"
}
```

## 9. 最終狀態判定

狀態優先順序固定為：

```text
blocked_by_rule_conflict
> blocked_by_access
> failed_but_report_generated
> partial
> completed_with_warnings
> completed
```

### 9.1 狀態定義

- `completed`：必要資料、分析、Markdown、Dashboard 及必要寫回均完成。
- `completed_with_warnings`：主要流程完成，但存在不影響核心結果的警告。
- `partial`：部分資料、模組或交付項目未完成，但仍有可用結果。
- `failed_but_report_generated`：主要流程失敗，但仍成功產出報告。
- `blocked_by_access`：關鍵規格、資料或必要資源因存取問題無法取得。
- `blocked_by_rule_conflict`：規格衝突導致無法安全判定或執行。

## 10. 最終交付最低要求

無論執行結果為何，最終輸出必須盡可能包含：

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

- 虛構任何資料或錯誤結果
- 把缺失資料填為零
- 把估算值當成實際值
- 把延遲或過期資料當成即時資料
- 未嘗試規定中的 Fallback 就直接宣告資料缺失
- 未讀取檔案內容卻宣稱已載入
- 因單一錯誤提前停止
- 自行修改已定案規則
- 在規則衝突時自行選擇一方並繼續推論
- 自動下單或執行交易

## 12. 定案原則

本文件定義錯誤、Fallback、降級及最終狀態處理方式。實際執行時，所有錯誤、來源、時間、資料狀態、Fallback 結果及最終狀態，均必須以當次實際執行紀錄為準。
