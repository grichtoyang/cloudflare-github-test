# 每日盤前分析 V1.0 — ANALYSIS_RULES.md

```text
文件名稱：ANALYSIS_RULES.md
文件版本：V1.0
文件狀態：定案版
適用時區：Asia/Taipei
備註：本文件為每日盤前分析 V1.0 的正式分析規則；跨文件一致性以本版及其他定案文件為準
```

> 本文件原有分析規則內容維持不變；本次定案統一規範如下：

## 跨文件統一規範

### 報告狀態 `report_status`

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

不得使用：

```text
failed_but_report_generated
fallback
success
unknown
```

流程失敗但已產出報告時，使用 `report_status=failed`，並在錯誤紀錄或 `unfinished_items` 說明報告已產出但流程未完整成功。

### Fallback 固定順序

所有資料集依適用性及驗證結果使用下列順序：

1. `primary_proxy`：已驗證的主要 Cloudflare Worker Proxy
2. `official_api`：官方 Open API
3. `backup_api_proxy`：官方備援 API／Proxy
4. `primary_web`：已驗證的主要金融資料來源
5. `backup_web`：已驗證的備援金融資料來源
6. `last_valid`：最近一次有效資料，僅限資料性質允許
7. `missing`：無法取得有效資料

### `source_role`

只允許：

```text
primary_proxy
official_api
backup_api_proxy
primary_web
backup_web
last_valid
```

### 錯誤後續執行

一旦開始執行，無論中間發生何種一般錯誤，都必須持續至產出 Markdown 報告或最小錯誤報告；不得以空白、猜測值或自行補值掩蓋失敗。規則衝突時不得猜測，但仍須產出錯誤紀錄、降級結果及最終狀態。

### 定案要求

其他 Markdown 文件不得重新定義與本文件衝突的狀態碼、來源角色、Fallback 順序或最低交付要求。