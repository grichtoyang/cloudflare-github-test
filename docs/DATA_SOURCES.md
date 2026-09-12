# 每日盤前分析 V1.0 — 資料來源規格

**文件狀態：定案版**  
**時區：Asia/Taipei**

## 1. 固定資料來源優先級

所有資料必須依下列順序取得，不得任意跳級：

1. GitHub Actions → 已驗證 Cloudflare Worker Proxy
2. 官方 Open API
3. 其他可合法擷取的財經／新聞網站
4. 最近一次有效資料（僅限資料性質允許）
5. `missing`

只有在上一層來源發生連線失敗、HTTP 錯誤、格式錯誤、日期不符、必要欄位缺失、資料為空、數值或單位異常、資料延遲／過期、或驗證失敗時，才可切換下一層；每次切換都必須記錄 `fallback_reason`。

## 2. 主要來源：Cloudflare Worker Proxy

### 2.1 TAIFEX

Base URL：`https://taifex.grichtoyang.workers.dev`

用途：台指期行情、期貨三大法人、未平倉量、選擇權鏈、選擇權法人籌碼、Call Wall、Put Wall、Gamma Wall、Gamma Flip、Max Pain，以及期貨／選擇權歷史比較。

### 2.2 TWSE／TAIEX

Base URL：`https://twse-proxy.grichtoyang.workers.dev/`

用途：加權指數、現貨行情、成交量、三大法人買賣超、融資融券、借券及其他 TWSE／TAIEX 資料。

### 2.3 Proxy 使用前驗證

每個 endpoint 必須驗證：HTTP 狀態、回應格式、可解析性、資料日期、資料時間、必要欄位、非空、數值、單位及完整性。未通過驗證不得進入分析。

## 3. 第一層備援：官方 Open API

- TAIFEX：`https://openapi.taifex.com.tw/`
- TWSE：`https://openapi.twse.com.tw/`

官方 API 仍須執行與 Proxy 相同的完整驗證，不得因為是官方來源而省略檢查。

## 4. 第二層備援：合法網站

僅在 Proxy 與官方 API 均無法取得有效資料時使用。可依資料類型選用 Yahoo 股市／Yahoo Finance、MoneyDJ、Goodinfo!、財報狗、HiStock、鉅亨網、經濟日報、工商時報、Reuters、CNBC、Trading Economics、MarketWatch 等。

每筆網站資料必須記錄來源、`request_url`、擷取時間、資料日期、資料狀態及限制；不得標示為官方即時資料，也不得把網站推估值當成官方實際值。

## 5. 最近一次有效資料與 missing

- 最近一次有效資料只能用於允許歷史延續的資料，並標示 `source_role=last_valid`、`data_status=stale`。
- 不得用舊資料冒充當日即時行情、當日成交量、當日法人流量、當日未平倉量或當日選擇權鏈。
- 若資料性質不允許沿用，直接標示 `missing`。
- `missing` 不得補成 `0`、不得虛構、不得無依據推算成實際資料。

## 6. 來源角色與資料狀態

`source_role`：

- `primary_proxy`
- `official_api_fallback`
- `web_scraping_fallback`
- `last_valid`

`data_status`：`fresh`、`delayed`、`stale`、`missing`、`invalid`、`partial`、`estimated`、`fallback`、`insufficient_data`。

`source_role` 與 `data_status` 必須分開記錄。例如官方 API 取得但已過期：`official_api_fallback` + `stale`。

## 7. 原始資料與欄位要求

原始資料不可覆寫；正規化資料與分析結果必須另存。至少保存：

- `source`
- `source_role`
- `base_url`
- `endpoint`
- `request_url`
- `request_time`
- `response_time`
- `http_status`
- `raw_payload`
- `data_date`
- `data_timestamp`
- `data_status`
- `fallback_reason`
- `error_code`
- `validation_errors`

## 8. 歷史比較

比較前次資料前，必須確認基準日期、基準時間、資料定義、單位、來源可追溯性，以及缺值／延遲／過期狀態。無法有效比較時標示 `insufficient_data`，不得自行補算。

## 9. 選擇權資料規則

必須明確區分近月、當週、到期月份、Call／Put、外資、造市商、OI、成交量、價格及 Gamma 資料。Call Wall、Put Wall、Gamma Wall、Gamma Flip、Max Pain 只能作為市場結構參考，不能單獨產生必然漲跌或交易結論，必須結合價格行為、成交量、未平倉量與市場狀態。

## 10. Fallback 執行規則

來源失敗時必須：

1. 記錄來源、endpoint、HTTP 狀態或錯誤。
2. 記錄具體 `fallback_reason`。
3. 依固定順序切換來源。
4. 記錄切換後來源及資料狀態。
5. 將資料品質、限制、缺失欄位及錯誤傳遞至分析、報告與 Dashboard。
6. 不得因單一來源失敗而停止整體流程；應繼續至產出報告，無法取得部分則標示 `missing`。

## 11. 資料誠信禁止事項

不得虛構資料或來源、把缺失補成零、把估算當實測、把推測當事實、把延遲當即時、隱藏來源切換、省略日期／時間、未驗證即分析、未記錄原因跳級，或用單一選擇權價位判定必然漲跌。

## 12. 最低交付要求

即使部分資料失敗，仍須產出：原始資料或失敗紀錄、正規化資料、驗證結果、來源狀態、Fallback 狀態與原因、資料品質總覽、缺失欄位、錯誤清單，以及可供分析模組使用的結構化資料。報告必須明確揭露資料限制。
