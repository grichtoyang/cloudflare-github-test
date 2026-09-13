# 每日盤前分析 V1.0 — 資料來源規格

**文件狀態：定案版**  
**時區：Asia/Taipei**

## 1. 固定資料來源優先級

1. GitHub Actions → 已驗證 Cloudflare Worker Proxy
2. 官方 Open API
3. 其他可合法擷取的財經／新聞網站
4. 最近一次有效資料（僅限資料性質允許）
5. `missing`

只有上一層來源發生連線、HTTP、格式、日期、欄位、空值、數值、單位、時間或完整性問題時，才可切換下一層；每次切換都必須記錄 `fallback_reason`。

## 2. 主要來源

- **TAIFEX Proxy**：`https://taifex.grichtoyang.workers.dev`
  - 台指期行情、期貨法人與未平倉量、選擇權鏈與法人籌碼、Call Wall、Put Wall、Gamma Wall、Gamma Flip、Max Pain。
- **TWSE／TAIEX Proxy**：`https://twse-proxy.grichtoyang.workers.dev/`
  - 加權指數、現貨、成交量、三大法人、融資融券、借券及其他 TWSE／TAIEX 資料。

每個 endpoint 使用前必須驗證 HTTP 狀態、格式、可解析性、日期、時間、必要欄位、非空、數值、單位與完整性；未通過不得進入分析。

## 3. 官方 API 備援

- TAIFEX：`https://openapi.taifex.com.tw/`
- TWSE：`https://openapi.twse.com.tw/`

官方 API 必須執行與 Proxy 相同的驗證，不得省略檢查。

## 4. 網站備援

僅在 Proxy 與官方 API 均無法取得有效資料時使用合法網站，例如 Yahoo Finance、MoneyDJ、Goodinfo!、財報狗、HiStock、鉅亨網、Reuters、CNBC、Trading Economics、MarketWatch。

網站資料必須記錄來源、`request_url`、擷取時間、資料日期、資料狀態與限制；不得標示為官方即時資料。

## 5. 最近一次有效資料與 missing

- 最近一次有效資料只能用於允許歷史延續的資料，並標示 `source_role=last_valid`、`data_status=stale`。
- 不得用舊資料冒充當日行情、成交量、法人流量、未平倉量或選擇權鏈。
- 資料性質不允許沿用時，直接標示 `missing`。
- `missing` 不得補成 `0`、虛構或無依據推算成實際資料。

## 6. 必要欄位

每筆原始資料不可覆寫，至少保存：

`source`、`source_role`、`base_url`、`endpoint`、`request_url`、`request_time`、`response_time`、`http_status`、`raw_payload`、`data_date`、`data_timestamp`、`data_status`、`fallback_reason`、`error_code`、`validation_errors`。

來源角色：`primary_proxy`、`official_api_fallback`、`web_scraping_fallback`、`last_valid`。

資料狀態：`fresh`、`delayed`、`stale`、`missing`、`invalid`、`partial`、`estimated`、`insufficient_data`。

`fallback` 不屬於 `data_status`；是否使用 fallback 由 `fallback.used` 表示，來源種類由 `source_role` 表示。

## 7. 歷史比較與選擇權

歷史比較前必須確認基準日期／時間、資料定義、單位、來源及缺值／延遲／過期狀態；無法有效比較時標示 `insufficient_data`，不得自行補算。

選擇權必須區分近月、當週、到期月份、Call／Put、外資、造市商、OI、成交量、價格及 Gamma 資料。Call Wall、Put Wall、Gamma Wall、Gamma Flip、Max Pain 僅為市場結構參考，不能單獨產生必然漲跌或交易結論。

## 8. Fallback 與交付規則

來源失敗時必須記錄來源、endpoint、錯誤、`fallback_reason`、切換後來源及資料狀態，並把資料品質、限制、缺失欄位與錯誤傳遞至分析、報告及 Dashboard。不得因單一來源失敗而停止整體流程；無法取得部分標示 `missing`，仍須產出報告。

## 9. 資料誠信禁止事項

不得虛構資料或來源、缺失補零、估算冒充實測、推測冒充事實、延遲冒充即時、隱藏來源切換、省略日期／時間、未驗證即分析、未記錄原因跳級，或以單一選擇權價位判定必然漲跌。

## 10. 最低交付要求

即使部分資料失敗，仍須產出：原始資料或失敗紀錄、正規化資料、驗證結果、來源／Fallback 狀態與原因、資料品質總覽、缺失欄位、錯誤清單及供分析模組使用的結構化資料；報告必須揭露資料限制。
