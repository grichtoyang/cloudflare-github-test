# 每日盤前分析 V1.0
# DATA_SCHEMA.md

## 1. 目的

定義每日盤前分析資料封包的統一格式，供資料收集、驗證及後續分析使用。本文件不定義市場分析、交易訊號或風控規則。

## 2. 資料層級

```text
Package
└── Dataset
    └── Record
        └── Field
```

- Package：一次完整的盤前資料封包。
- Dataset：一組同類型資料。
- Record：Dataset 中的一筆紀錄。
- Field：Record 中的單一欄位。

## 3. Package

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

`package_status`：`complete`、`partial`、`failed`、`invalid`。

`overall_status`：`fresh`、`delayed`、`stale`、`partial`、`invalid`、`missing`、`estimated`、`insufficient_data`。

狀態優先順序：

```text
invalid > failed > missing > insufficient_data > partial > stale > delayed > fresh
```

## 4. Dataset

```json
{
  "dataset_id": "taifex_futures_price",
  "dataset_name": "台指期近月價格",
  "dataset_category": "taiwan_futures",
  "priority": "core",
  "dataset_status": "available",
  "data_status": "fresh",
  "source": {
    "source_name": "TAIFEX Cloudflare Proxy",
    "source_role": "primary_proxy",
    "endpoint": "/futures-price",
    "retrieved_at": "ISO-8601"
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
    "reason": null,
    "fallback_source": null,
    "fallback_retrieved_at": null
  },
  "errors": []
}
```

`priority`：`core`、`important`、`optional`。

`dataset_status`：`available`、`partial`、`missing`、`failed`、`invalid`、`skipped`。

## 5. Dataset ID

Dataset ID 必須固定，不因來源或 fallback 改變。

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

## 6. Source 與 fallback

`source_role`：`primary_proxy`、`official_api`、`official_api_fallback`、`backup_api`、`web_source`、`last_valid`。

規則：

1. 優先使用主要 Proxy。
2. 主要來源失敗時才使用 fallback。
3. fallback 必須記錄原因、來源及取得時間。
4. 不可將 fallback 偽裝成主要來源。
5. 舊資料須標記 `stale` 或 `last_valid`。
6. 網頁資料不可直接視為官方即時資料。

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

`field_status`：`valid`、`missing`、`invalid`、`estimated`、`stale`。

`unit` 必須放在 Field 層級。常見單位：`point`、`contracts`、`shares`、`currency`、`percent`、`percentage_point`、`yield_percent`、`index`、`date`、`datetime`、`text`、`boolean`、`null`。

## 8. 選擇權關鍵位

以下欄位必須分開：

- `call_wall`
- `put_wall`
- `gamma_wall`
- `gamma_flip`
- `max_pain`

無法取得時使用 `null`，不可使用 `0` 代表缺失；每個欄位可個別標記狀態。

## 9. Validation

```text
completeness = 有效必要欄位數 ÷ 必要欄位總數
```

範圍為 `0.0～1.0`；選配欄位不計入核心完整度。

## 10. Error / Incomplete Item

```json
{
  "error_code": "SOURCE_UNAVAILABLE",
  "message": "Primary source unavailable",
  "dataset_id": "taifex_futures_price",
  "source": "TAIFEX Cloudflare Proxy",
  "severity": "high",
  "retryable": true
}
```

Severity：`low`、`medium`、`high`、`critical`。

缺漏資料至少記錄：`dataset_id`、`missing_fields`、`reason`、`impact`。

## 11. 時間規則

- `analysis_date`：本次分析目標日期。
- `data_date`：資料實際所屬日期。
- `data_timestamp`：資料實際時間點。
- `retrieved_at`：系統取得資料時間。
- `generated_at`：封包產生時間。

所有時間使用 ISO-8601；台灣時間使用 `+08:00`；不可自行捏造不存在的時間。

## 12. 完整性原則

1. 不可自行補值。
2. 缺失值使用 `null`。
3. 不可把 `0` 當作缺失值。
4. 不可混淆資料日期與取得日期。
5. 不可隱藏 fallback。
6. 不可把估算值當成官方值。
7. 不可將錯誤訊息當成正常資料。
8. Dataset ID 不因來源切換而改變。
9. 所有核心資料都必須有來源與狀態。

## 13. 文件狀態

- 文件名稱：`DATA_SCHEMA.md`
- 版本：`V1.0`
- 狀態：正式定案
- 前置文件：`PROJECT_OVERVIEW.md`、`SYSTEM_ARCHITECTURE.md`、`DATA_SOURCES.md`
- 下一份文件：`ANALYSIS_RULES.md`
