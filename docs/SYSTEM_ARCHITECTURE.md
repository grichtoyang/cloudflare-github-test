# 每日盤前分析 V1.0 — 系統架構

**文件狀態：定案版**  
**時區：Asia/Taipei**

## 1. 目標

每日取得台股現貨、台指期、選擇權、全球市場、總體經濟與新聞資料，完成驗證、分析、Markdown 報告及 Dashboard JSON。不得虛構、補零或把推測當成事實。

## 2. 執行主線

```text
讀取規格
→ 鎖定台北時區與目標交易日
→ 取得並保存原始資料
→ 正規化與驗證
→ 執行固定 fallback
→ 分析五大模組
→ 產出 Markdown 與 Dashboard JSON
→ 寫回 GitHub
→ 重新讀取驗證
→ 回報最終狀態
```

## 3. 固定 Fallback 順序

```text
1. primary_proxy
2. official_api
3. backup_api_proxy
4. primary_web
5. backup_web
6. last_valid
7. missing
```

Retry 可在同一來源內進行，但不得任意改變來源層級。使用 `last_valid` 時，必須標示原始資料日期並將 `data_status` 設為 `stale`。

## 4. 正式狀態

### `data_status`

`fresh`、`delayed`、`stale`、`missing`、`invalid`、`partial`、`estimated`、`insufficient_data`

### `report_status`

`completed`、`completed_with_warnings`、`partial`、`insufficient_data`、`failed`、`blocked_by_access`、`blocked_by_rule_conflict`

### `package_status`

`complete`、`partial`、`failed`、`invalid`

### 寫回狀態

`success`、`partial`、`failed`

## 5. 強制不中斷

單一資料源、endpoint、分析模組、報告區塊、Dashboard 或寫回失敗時，必須：

1. 記錄錯誤。
2. 執行可用 fallback。
3. 標記受影響資料與模組。
4. 繼續其他不受影響部分。
5. 在可行時產出報告與 Dashboard JSON。
6. 揭露失敗、缺失、未完成與限制。

只有最低限度輸出無法產出，或環境／規則衝突阻止執行時，才可使用 `failed` 或阻塞狀態。

## 6. 資料一致性

- Markdown 與 Dashboard JSON 必須來自同一份資料快照。
- 每個資料集必須保留來源、取得時間、目標交易日期、狀態與錯誤資訊。
- 不同交易日期、盤別或時間戳不得無說明混合。
- 缺失值不得填 `0`。
- 延遲資料不得標示為即時。
- 估算值必須標示 `estimated`。
- 事實、解讀、推測與交易建議必須分開。

## 7. 期貨與選擇權限制

- 日盤後法人 OI 是部位存量。
- 夜盤法人交易口數／金額是新增交易流量。
- 夜盤流量不得稱為即時法人 OI。
- 選擇權 OI 以可驗證的日盤後資料為準。
- 未取得可驗證夜盤選擇權 OI 時，必須標示資料不足。
- 造市商資料只有在來源實際提供且可驗證時才可揭露。

## 8. 系統邊界

本 V1.0 不包含自動下單、自動交易執行、獲利保證、OCR 核心依賴或未經核准的規則／資料來源變更。

## 9. 驗收

規格、日期、來源、fallback、資料狀態、報告、Dashboard、錯誤揭露及寫回驗證均須完成；不得使用已淘汰的大寫或模糊狀態碼。
