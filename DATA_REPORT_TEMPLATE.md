# DATA_REPORT_yyyymmdd

- 報告日期：`YYYY-MM-DD`
- T0 交易日期：`YYYY-MM-DD`
- 資料產出時間：`YYYY-MM-DD HH:MM:SS`
- 時區：`Asia/Taipei`

---

## 一、現貨

### 1. 台股大盤行情

**資料來源：** `Cloudflare Worker：twse-proxy`

| 項目 | 數值 | 單位 |
|---|---:|---|
| 加權指數 | TBD | 點 |
| 開盤 | TBD | 點 |
| 最高 | TBD | 點 |
| 最低 | TBD | 點 |
| 收盤 | TBD | 點 |
| 漲跌點數 | TBD | 點 |
| 漲跌幅 | TBD | % |
| 成交金額 | TBD | 億元 |

---

### 2. 市場漲跌家數

#### 2.1 上市公司

**資料來源：** `Cloudflare Worker：twse-proxy`

| 項目 | 家數 |
|---|---:|
| 上漲家數 | TBD |
| 下跌家數 | TBD |
| 平盤家數 | TBD |
| 漲停家數 | TBD |
| 跌停家數 | TBD |

#### 2.2 上櫃公司

**資料來源：** `TPEX OpenAPI`  
`https://www.tpex.org.tw/openapi/`

| 項目 | 家數 |
|---|---:|
| 上漲家數 | TBD |
| 下跌家數 | TBD |
| 平盤家數 | TBD |
| 漲停家數 | TBD |
| 跌停家數 | TBD |

---

### 3. 三大法人現貨買賣超

**資料來源：** `Cloudflare Worker：twse-proxy`

| 法人別 | 買賣超金額 | 單位 |
|---|---:|---|
| 外資 | TBD | 億元 |
| 投信 | TBD | 億元 |
| 自營商 | TBD | 億元 |
| 三大法人合計 | TBD | 億元 |

---

### 4. 融資融券

**資料來源：**

- 上市：`TWSE OpenAPI` — `https://openapi.twse.com.tw/v1/exchangeReport/MI_MARGN`
- 上櫃：`TPEX OpenAPI` — `https://www.tpex.org.tw/openapi/v1/tpex_mainboard_margin_balance`

| 項目 | 數值 | 單位 |
|---|---:|---|
| 融資餘額 | TBD | 億元 |
| 融資增減 | TBD | 億元 |
| 融券餘額 | TBD | 張 |
| 融券增減 | TBD | 張 |
| 融資維持率 | TBD | % |

---

### 5. 借券資料

**資料來源：**

- 上市：`TWSE OpenAPI` — `https://openapi.twse.com.tw/v1/SBL/TWT96U`
- 上櫃：`TPEX OpenAPI` — `https://www.tpex.org.tw/openapi/v1/tpex_margin_sbl`

| 項目 | 數值 | 單位 |
|---|---:|---|
| 借券餘額 | TBD | 張 |
| 借券賣出餘額 | TBD | 張 |
| 借券賣出增減 | TBD | 張 |

---

### 6. 市場成交結構

**資料來源：**

- 上市：`TWSE OpenAPI` — `https://openapi.twse.com.tw/v1/exchangeReport/FMTQIK`
- 上櫃：`TPEX OpenAPI` — `https://www.tpex.org.tw/openapi/v1/tpex_mainborad_highlight`

| 項目 | 成交金額 | 單位 |
|---|---:|---|
| 上市成交金額 | TBD | 億元 |
| 上櫃成交金額 | TBD | 億元 |
| 上市櫃成交金額合計 | TBD | 億元 |

---

## 二、重要市場

### 1. 美股指數

**主要資料來源：** `Yahoo Finance Chart API`

**取得方式：** `Python requests／HTTP JSON`

**備援方式：** `Yahoo Finance 網頁爬蟲或其他公開金融資料網站`

**來源策略：** API 優先；API 失敗、資料缺漏或格式異常時，啟用爬蟲備援。

**目前狀態：** `技術上可行，待實際程式測試`

| 項目 | Yahoo Finance 代號 | 收盤／最新值 | 漲跌點 | 漲跌幅 |
|---|---|---:|---:|---:|
| S&P 500 | `^GSPC` | TBD | TBD | TBD |
| Nasdaq Composite | `^IXIC` | TBD | TBD | TBD |
| Nasdaq 100 | `^NDX` | TBD | TBD | TBD |
| Dow Jones | `^DJI` | TBD | TBD | TBD |
| 費城半導體指數 SOX | `^SOX` | TBD | TBD | TBD |
| VIX | `^VIX` | TBD | TBD | TBD |

**資料處理規則：**

- 取得前一交易日收盤價及漲跌資料。
- API 回傳成功且資料完整時，使用 API 資料。
- API 失敗或資料不完整時，啟用爬蟲備援。
- API 與爬蟲皆失敗時，標記為 `unavailable`，不得自行推估數值。
- 保留 `data_source`、`source_type`、`retrieved_at`、`timezone` 等欄位。
- Yahoo Finance 資料的長期穩定性、延遲及使用限制，於程式測試階段另行確認。

### 2. 亞洲主要指數

**主要資料來源：** `Yahoo Finance Chart API`

**取得方式：** `Python requests／HTTP JSON`

**備援方式：** `Yahoo Finance 網頁爬蟲或其他公開金融資料網站`

**來源策略：** API 優先；API 失敗、資料缺漏或格式異常時，啟用爬蟲備援。

**目前狀態：** `技術上可行，待實際程式測試`

| 項目 | Yahoo Finance 代號 | 收盤／最新值 | 漲跌點 | 漲跌幅 |
|---|---|---:|---:|---:|
| 日經 225 | `^N225` | TBD | TBD | TBD |
| 韓國 KOSPI | `^KS11` | TBD | TBD | TBD |
| 香港恆生指數 | `^HSI` | TBD | TBD | TBD |
| 上海綜合指數 | `000001.SS` | TBD | TBD | TBD |
| 深圳成分指數 | `399001.SZ` | TBD | TBD | TBD |

**資料處理規則：**

- 取得各市場最近一個可用交易日的收盤價及漲跌資料。
- 各市場交易日與交易時段不同，程式不得假設所有指數同日收盤。
- API 回傳成功且資料完整時，使用 API 資料。
- API 失敗或資料不完整時，啟用爬蟲備援。
- API 與爬蟲皆失敗時，標記為 `unavailable`，不得自行推估數值。
- 保留 `data_source`、`source_type`、`retrieved_at`、`timezone` 等欄位。
- 各指數代號與資料回傳狀況，於程式測試階段逐一確認。

### 3. 美股指數期貨

**主要資料來源：** `Yahoo Finance Chart API`

**取得方式：** `Python requests／HTTP JSON`

**備援方式：** `Yahoo Finance 網頁爬蟲或其他公開金融資料網站`

**來源策略：** API 優先；API 失敗、資料缺漏或格式異常時，啟用爬蟲備援。

**目前狀態：** `技術上可行，待實際程式測試`

| 項目 | Yahoo Finance 代號 | 最新值 | 漲跌點 | 漲跌幅 |
|---|---|---:|---:|---:|
| S&P 500 Futures | `ES=F` | TBD | TBD | TBD |
| Nasdaq 100 Futures | `NQ=F` | TBD | TBD | TBD |
| Dow Futures | `YM=F` | TBD | TBD | TBD |
| Russell 2000 Futures | `RTY=F` | TBD | TBD | TBD |

**資料處理規則：**

- 取得最新可用期貨報價、前次收盤、漲跌點與漲跌幅。
- 保留報價時間與時區；不得把期貨最新報價誤當成現貨指數收盤。
- API 回傳成功且資料完整時，使用 API 資料。
- API 失敗或資料不完整時，啟用爬蟲備援。
- API 與爬蟲皆失敗時，標記為 `unavailable`，不得自行推估數值。
- 保留 `data_source`、`source_type`、`retrieved_at`、`timezone` 等欄位。
- 期貨可能跨台灣日期，程式須依報價時間與交易時段處理。
- Yahoo Finance 資料的延遲、穩定性及使用限制，於程式測試階段另行確認。

### 4. 美國國債殖利率

**主要資料來源：** `U.S. Treasury Fiscal Data API`

**取得方式：** `Python requests／HTTP JSON`

**備援方式：** `U.S. Treasury 網頁資料或其他公開金融資料網站`

**來源策略：** API 優先；API 失敗、資料缺漏或格式異常時，啟用網頁資料備援。

**目前狀態：** `技術上可行，待實際程式測試`

| 項目 | API 資料欄位／識別 | 殖利率 | 日變化 |
|---|---|---:|---:|
| 美國 2 年期殖利率 | `2 Yr` | TBD | TBD |
| 美國 10 年期殖利率 | `10 Yr` | TBD | TBD |
| 美國 30 年期殖利率 | `30 Yr` | TBD | TBD |

**資料處理規則：**

- 取得最近一個可用交易日的殖利率資料。
- 殖利率以百分比表示，日變化以百分點表示。
- 保留資料日期、公布時間、資料來源與時區。
- API 失敗或資料不完整時，啟用備援來源。
- API 與備援皆失敗時，標記為 `unavailable`，不得自行推估數值。
- `2 Yr`、`10 Yr`、`30 Yr` 欄位名稱及實際回傳格式，於程式測試階段確認。

### 5. 主要匯率

**主要資料來源：** `Yahoo Finance Chart API`

**取得方式：** `Python requests／HTTP JSON`

**備援方式：** `Yahoo Finance 網頁爬蟲或其他公開金融資料網站`

**來源策略：** API 優先；API 失敗、資料缺漏或格式異常時，啟用爬蟲備援。

**目前狀態：** `技術上可行，待實際程式測試`

| 項目 | Yahoo Finance 代號 | 最新值 | 漲跌／變化 |
|---|---|---:|---:|
| USD/TWD | `TWD=X` | TBD | TBD |
| DXY 美元指數 | `DX-Y.NYB` | TBD | TBD |
| USD/JPY | `JPY=X` | TBD | TBD |
| USD/KRW | `KRW=X` | TBD | TBD |

**資料處理規則：**

- 取得最新可用匯率、前次收盤或前次可比較值，以及變化幅度。
- USD/TWD、USD/JPY、USD/KRW 以匯率報價表示；DXY 以指數點位表示。
- 明確記錄報價方向，不得將 `TWD=X` 等報價方向誤解為反向匯率。
- API 回傳成功且資料完整時，使用 API 資料。
- API 失敗或資料不完整時，啟用爬蟲備援。
- API 與爬蟲皆失敗時，標記為 `unavailable`，不得自行推估數值。
- 保留 `data_source`、`source_type`、`retrieved_at`、`timezone` 等欄位。
- 匯率為全球交易市場資料，需依報價時間判斷是否為最新值；不得一律套用台股收盤時間。
- Yahoo Finance 資料的延遲、穩定性及使用限制，於程式測試階段另行確認。

### 6. 台灣相關 ADR

**主要資料來源：** `Yahoo Finance Chart API`

**取得方式：** `Python requests／HTTP JSON`

**備援方式：** `Yahoo Finance 網頁爬蟲或其他公開金融資料網站`

**來源策略：** API 優先；API 失敗、資料缺漏或格式異常時，啟用爬蟲備援。

**目前狀態：** `技術上可行，待實際程式測試`

| 項目 | Yahoo Finance 代號 | 收盤／最新值 | 漲跌點 | 漲跌幅 |
|---|---|---:|---:|---:|
| 台積電 ADR | `TSM` | TBD | TBD | TBD |
| 聯電 ADR | `UMC` | TBD | TBD | TBD |
| 日月光投控 ADR | `ASX` | TBD | TBD | TBD |

**資料處理規則：**

- 取得美國市場最近一個可用交易日的 ADR 收盤價及漲跌資料。
- ADR 價格以美元表示。
- 保留美股交易日期、報價時間與時區。
- ADR 美股交易時段與台股現貨交易時段不同，程式不得將 ADR 收盤時間直接視為台股當日收盤。
- API 回傳成功且資料完整時，使用 API 資料。
- API 失敗或資料不完整時，啟用爬蟲備援。
- API 與爬蟲皆失敗時，標記為 `unavailable`，不得自行推估數值。
- 保留 `data_source`、`source_type`、`retrieved_at`、`timezone` 等欄位。
- ADR 與台股現貨之間的價差、匯率換算及溢價／折價，暫不於本項直接計算，後續另行定義。

### 7. 原油／黃金／Bitcoin

**主要資料來源：** `Yahoo Finance Chart API`

**取得方式：** `Python requests／HTTP JSON`

**備援方式：** `Yahoo Finance 網頁爬蟲或其他公開金融資料網站`

**來源策略：** API 優先；API 失敗、資料缺漏或格式異常時，啟用爬蟲備援。

**目前狀態：** `技術上可行，待實際程式測試`

| 項目 | Yahoo Finance 代號 | 收盤／最新值 | 漲跌點／變化 | 漲跌幅 |
|---|---|---:|---:|---:|
| WTI 原油期貨 | `CL=F` | TBD | TBD | TBD |
| 黃金期貨 | `GC=F` | TBD | TBD | TBD |
| Bitcoin BTC | `BTC-USD` | TBD | TBD | TBD |

**資料處理規則：**

- WTI 原油及黃金採用期貨報價，不得誤標示為現貨價格。
- Bitcoin 採用 `BTC-USD` 報價，屬於 24 小時交易市場。
- 原油與黃金需取得最近一個可用交易日的收盤價及漲跌資料。
- Bitcoin 需取得報告產出時間前的最新可用價格及變化資料。
- API 回傳成功且資料完整時，使用 API 資料。
- API 失敗或資料不完整時，啟用爬蟲備援。
- API 與爬蟲皆失敗時，標記為 `unavailable`，不得自行推估數值。
- 保留 `data_source`、`source_type`、`retrieved_at`、`timezone` 等欄位。
- 原油及黃金期貨可能跨越台灣日期，程式須依實際報價時間與交易時段處理。
- Bitcoin 不得直接套用傳統股票市場的收盤時間。
- Yahoo Finance 資料的延遲、穩定性及使用限制，於程式測試階段另行確認。

### 8. 重大經濟數據、央行事件與重大市場新聞

**資料來源：**

- 官方經濟數據與央行公告：官方 API、JSON、RSS 或固定公告頁面
- 重大市場新聞：固定 RSS 來源
- 新聞補充搜尋：GDELT DOC API

**取得方式：**

- 由 GitHub Actions 執行 Python 程式。
- 使用 `requests` 取得 JSON、RSS XML 或固定 HTML。
- 不使用需要登入的網站。
- 不抓取新聞全文，只保留標題、摘要、來源、時間與原文連結。
- GDELT 僅作為新聞搜尋與補充來源，不直接視為官方確認。

**處理規則：**

- 每日取得前一交易日收盤後至當日 08:00 的資料。
- 所有時間轉換為 `Asia/Taipei`，並保留原始時間。
- 依固定關鍵字篩選央行、利率、通膨、就業、GDP、關稅、制裁、地緣政治、AI 與半導體等重大事件。
- 相同事件進行基本去重與合併。
- 官方公告優先；媒體報導標示為新聞來源或市場解讀。
- 無法取得或解析失敗時標記為 `unavailable`，不得自行補寫。

| 事件／新聞 | 來源 | 發布時間 | 台北時間 | 摘要／實際結果 | 原文連結 |
|---|---|---|---|---|---|
| TBD | TBD | TBD | TBD | TBD | TBD |

**目前狀態：** `技術上可行，待實際程式測試`

---

## 三、期貨

TBD

---

## 四、選擇權

TBD
