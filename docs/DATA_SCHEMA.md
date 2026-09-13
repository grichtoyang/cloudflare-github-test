# 每日盤前分析 V1.0 — 資料結構規格

**文件名稱：** `DATA_SCHEMA.md`  
**版本：** `V1.0`  
**狀態：** `APPROVED`  
**時區：** `Asia/Taipei`

## 1. 文件目的

定義每日盤前分析資料封包的統一格式，供資料收集、原始資料保存、正規化、驗證及後續分析使用。本文件只定義資料結構、來源追溯、資料狀態及完整性標記；不定義市場分析、交易訊號或風控規則。

## 2. Package 結構

```json
{
  "package_id": "PM-YYYY-MM-DD-HHMMSS",
  "schema_version": "1.0",
  "analysis_date": "YYYY-MM-DD",
  "generated_at": "ISO-8601",
  "package_status": "complete",
  "data_quality": {
    "overall_status": "fresh",
    "core_complete": true,
    "dataset_count": 0,
    "valid_dataset_count": 0,
    "partial_dataset_count": 0,
    "failed_dataset_count": 0,
    "missing_dataset_count": 0
  },
  "datasets": [],
  "errors": [],
  "incomplete_items": []
}
```

`package_status` 只允許：`complete`、`partial`、`failed`、`invalid`。

`overall_status` 只允許：`fresh`、`delayed`、`stale`、`missing`、`invalid`、`partial`、`estimated`、`insufficient_data`。

`package_status` 表示封包交付狀態；`overall_status` 表示資料品質，兩者不可混用。`fallback` 不屬於資料狀態，是否使用 fallback 由 `fallback.used` 表示。

## 3. Dataset 結構

```json
{
  "dataset_id": "taifex_futures_price",
  "dataset_name": "台指期近月價格",
  "dataset_category": "taiwan_futures",
  "priority": "core",
  "dataset_status": "available",
  "data_status": "fresh",
  "source": {
    "source_name": "TAIFEX Proxy",
    "source_role": "primary_proxy",
    "base_url": "https://taifex.grichtoyang.workers.dev",
    "endpoint": "/futures-price",
    "request_url": "https://taifex.grichtoyang.workers.dev/futures-price",
    "request_time": "ISO-8601",
    "response_time": "ISO-8601",
    "http_status": 200,
    "retrieved_at": "ISO-8601",
    "raw_payload": null
  },
  "data_date": "YYYY-MM-DD",
  "data_timestamp": "ISO-8601 or null",
  "records": [],
  "record_count": 0,
  "validation": {
    "schema_valid": true,
    "content_valid": true,
    "completeness": 1.0,
    "validation_errors": []
  },
  "fallback": {
    "used": false,
    "fallback_reason": null,
    "fallback_source": null,
    "fallback_retrieved_at": null
  },
  "errors": []
}
```

Dataset priority：`core`、`important`、`optional`。  
Dataset status：`available`、`partial`、`missing`、`failed`、`invalid`、`skipped`。

## 4. 固定 Dataset ID

```text
twse_taiex_price
twse_institutional_net
twse_margin_balance
taifex_futures_price
taifex_futures_institutional_oi
taifex_options_chain
taifex_options_market_structure
taifex_options_key_levels
us_equity_index_close
us_treasury_yield
fx_major_rates
market_news
industry_news
company_earnings
```

Dataset ID 必須固定，不因來源或 fallback 改變。

## 5. Source Role 與 Fallback

來源角色統一使用以下值：

```text
primary_proxy
official_api
backup_api_proxy
primary_web
backup_web
last_valid
```

所有資料集固定依下列順序嘗試：

```text
1. primary_proxy
2. official_api
3. backup_api_proxy
4. primary_web
5. backup_web
6. last_valid
7. missing
```

只有上一層來源發生連線、HTTP、格式、日期、欄位、空值、數值、單位、時間或完整性問題時，才可切換下一層；每次切換都必須記錄 `fallback_reason`。來源不適用時也必須記錄不適用原因。

最近一次有效資料只能在資料性質允許時使用，並標記：

```text
source_role=last_valid
data_status=stale
fallback.used=true
```

不得用舊資料冒充當日行情、成交量、法人流量、未平倉量或選擇權鏈。

## 6. 原始資料保存

每筆原始資料至少保存：

```text
source
source_role
base_url
endpoint
request_url
request_time
response_time
http_status
raw_payload
data_date
data_timestamp
data_status
fallback_reason
error_code
validation_errors
```

原始回傳內容不得被正規化資料覆寫。網站資料不得標示為官方即時資料。

## 7. Record 與 Field

```json
{
  "record_id": "TXF-near-month",
  "fields": {
    "close": {
      "value": 47200,
      "unit": "point",
      "field_status": "valid"
    }
  }
}
```

Field status：`valid`、`missing`、`invalid`、`estimated`、`stale`。`unit` 必須放在 Field 層級。

## 8. 選擇權關鍵位

以下欄位必須分開：

- `call_wall`
- `put_wall`
- `gamma_wall`
- `gamma_flip`
- `max_pain`

無法取得時使用 `null`，不可使用 `0` 代表缺失。必須區分近月、當週、到期月份、Call／Put、外資、造市商、OI、成交量、價格及 Gamma 資料。關鍵位僅為市場結構參考，不得單獨產生必然漲跌或交易結論。

## 9. Validation

```json
{
  "schema_valid": true,
  "content_valid": true,
  "completeness": 1.0,
  "validation_errors": []
}
```

`completeness` 範圍為 `0.0～1.0`，計算方式為有效必要欄位數除以必要欄位總數；選配欄位不計入核心完整度。驗證至少包括結構、欄位、日期與時間、數值與單位、非空內容、跨來源一致性及原始回應可解析性。

## 10. Error 與 Incomplete Item

```json
{
  "error_code": "SOURCE_UNAVAILABLE",
  "message": "Primary source unavailable",
  "dataset_id": "taifex_futures_price",
  "source": "TAIFEX Proxy",
  "severity": "high",
  "retryable": true
}
```

Severity：`low`、`medium`、`high`、`critical`。缺漏資料至少記錄 `dataset_id`、`missing_fields`、`reason`、`impact`。

## 11. 時間規則

`analysis_date` 為本次分析目標日期；`data_date` 為資料實際所屬日期；`data_timestamp` 為資料實際時間點；`request_time`、`response_time`、`retrieved_at` 及 `generated_at` 分別記錄請求、回應、取得完成及封包產生時間。所有時間使用 ISO-8601；台灣時間使用 `+08:00`。不可捏造不存在的時間。

## 12. 完整性原則

1. 不可自行補值。
2. 缺失值使用 `null`。
3. 不可把 `0` 當作缺失值。
4. 不可混淆資料日期與取得日期。
5. 不可隱藏 fallback。
6. 不可把估算值當成官方值。
7. 不可將錯誤訊息當成正常資料。
8. Dataset ID 不因來源切換而改變。
9. 所有核心資料都必須有來源、日期及狀態。
10. 本文件不包含市場分析與交易規則。

## 13. 文件狀態

- 文件名稱：`DATA_SCHEMA.md`
- 版本：`V1.0`
- 狀態：`APPROVED`
- 前置文件：`PROJECT_OVERVIEW.md`、`SYSTEM_ARCHITECTURE.md`、`DATA_SOURCES.md`
- 下一份文件：`ANALYSIS_RULES.md`
