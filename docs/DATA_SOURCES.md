# 每日盤前分析 V1.0 — 資料來源規格

**文件狀態：審閱版（待確認）**  
**時區：Asia/Taipei**

## 1. 資料來源優先級

所有資料依下列順序取得：

1. GitHub Actions 透過已驗證的 Cloudflare Worker Proxy
2. 官方 Open API
3. 其他可合法擷取的財經網站／新聞網站
4. 最近一次有效資料
5. `missing`

只有在較高優先級來源無法取得、格式錯誤、日期不符、資料過期、資料不完整或驗證失敗時，才可使用下一層來源。每次跳級都必須記錄原因。

## 2. 主要資料來源：Cloudflare Worker Proxy

GitHub Actions 為每日盤前分析的執行端，主要透過以下兩個 Cloudflare Worker Proxy 取得資料。

### 2.1 TAIFEX Proxy

Base URL：

`https://taifex.grichtoyang.workers.dev`

用途包括：

- 台指期行情
- 台指期三大法人資料
- 台指期未平倉量
- 選擇權鏈
- 選擇權法人籌碼
- Call Wall
- Put Wall
- Gamma Wall
- Gamma Flip
- Max Pain
- 期貨與選擇權歷史比較

### 2.2 TWSE Proxy

Base URL：

`https://twse-proxy.grichtoyang.workers.dev/`

用途包括：

- 加權指數
- 現貨行情
- 成交量
- 三大法人買賣超
- 融資融券
- 借券資料
- 其他 TWSE／TAIEX 相關資料

### 2.3 Proxy 使用前驗證

每個 Proxy endpoint 使用前必須確認：

- HTTP 回應正常
- 回應格式可解析
- 資料日期正確
- 必要欄位存在
- 資料非空
- 數值與單位正確
- 資料時間合理

## 3. 第一層備援：官方 Open API

當主要 Proxy 無法取得有效資料時，依下列官方 Open API 進行備援。

### 3.1 TAIFEX 官方 Open API

`https://openapi.taifex.com.tw/`

### 3.2 TWSE 官方 Open API

`https://openapi.twse.com.tw/`

官方 Open API 仍須執行完整的 HTTP、格式、日期、欄位、數值、時間及資料完整性驗證。

## 4. 第二層備援：其他可爬蟲擷取的網站

當 Cloudflare Proxy 與官方 Open API 都無法取得有效資料時，才可使用其他可合法擷取的財經網站或新聞網站。

可納入的網站類型包括：

- Yahoo 股市／Yahoo Finance
- MoneyDJ
- Goodinfo!
- 財報狗
- HiStock 嗨投資
- 鉅亨網
- 經濟日報
- 工商時報
- Reuters
- CNBC
- Trading Economics
- MarketWatch

實際使用的網站必須記錄來源、網址、擷取時間、資料日期、資料狀態及擷取限制。網站資料不得標示為官方即時資料。

## 5. 最後備援

若上述來源皆無法取得有效資料，依序使用：

1. 最近一次有效資料，並標示 `last_valid`／`stale`
2. `missing`

`missing` 不得補成 `0`，也不得自行虛構或推算成實際資料。

## 6. 來源角色與資料狀態

來源角色 `source_role`：

- `primary`：主要 Proxy 來源
- `official_api_fallback`：官方 Open API 備援
- `web_scraping_fallback`：網站爬蟲備援
- `last_valid`：最近一次有效資料

資料狀態 `data_status`：

- `fresh`
- `delayed`
- `stale`
- `missing`
- `invalid`
- `partial`
- `estimated`
- `fallback`
- `insufficient_data`

`source_role` 與 `data_status` 是不同欄位。使用備援來源時，必須同時記錄來源角色與實際資料狀態；例如官方 API 備援取得的過期資料，可標示為 `official_api_fallback` + `stale`。

## 7. 資料驗證

每次取得資料後，必須檢查：

1. HTTP 狀態
2. 預期回應格式
3. JSON／CSV／文字是否可解析
4. 必要欄位是否存在
5. 是否為空
6. 資料日期是否符合執行日期
7. 資料時間是否合理
8. 數值是否為有效數字
9. 單位與欄位意義是否正確
10. 是否延遲、過期或部分資料

驗證失敗時不得直接進入分析，必須記錄錯誤並啟用下一層來源。

## 8. 原始資料保存

原始資料不可覆寫。每筆原始資料至少保存：

- `source`
- `source_role`
- `endpoint`
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

正規化資料及分析結果須另行保存，不得取代原始資料。

## 9. 歷史比較

比較前次資料時，必須確認：

- 比較基準日期
- 比較基準時間
- 資料定義一致
- 單位一致
- 來源可追溯
- 是否存在缺值、延遲或過期資料

若無法建立有效比較，必須標示 `insufficient_data`，不得自行推算。

## 10. 選擇權資料規則

選擇權資料必須區分：

- 近月
- 當週
- 到期月份
- Call／Put
- 外資
- 造市商
- OI
- 成交量
- 價格
- Gamma 相關資料

Call Wall、Put Wall、Gamma Wall、Gamma Flip、Max Pain 僅是市場結構參考，不能單獨產生交易訊號，必須結合價格行為、成交量、未平倉量及市場狀態。

## 11. 來源失敗與 Fallback 處理

來源失敗時必須：

1. 記錄失敗來源。
2. 記錄 HTTP 狀態或錯誤訊息。
3. 記錄具體失敗原因。
4. 依固定 Fallback 順序繼續。
5. 記錄切換後的來源。
6. 標示資料狀態。
7. 將資料品質與限制傳遞至分析、報告及 Dashboard。
8. 不得因單一來源失敗而停止整體流程。

## 12. 資料誠信與禁止事項

不得：

- 虛構來源或資料。
- 將缺失資料補成 `0`。
- 將估算值當成實際值。
- 將推測當成事實。
- 將延遲資料標示為即時。
- 隱藏來源切換或 Fallback。
- 省略資料日期與時間。
- 以單一選擇權價位判定必然漲跌。
- 使用未驗證資料作為確定結論。
- 未記錄原因就跳過較高優先級來源。

## 13. 最低交付要求

資料層至少提供：

- 原始資料或失敗紀錄
- 正規化資料
- 資料驗證結果
- 來源狀態
- Fallback 狀態
- Fallback 原因
- 資料品質總覽
- 缺失欄位
- 錯誤清單
- 可供分析模組使用的結構化資料

資料不足時仍須產出部分結果，並明確標示限制。
