# DATA_REPORT_TEMPLATE.md

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

| 項目 | 最新值 | 漲跌／變化 |
|---|---:|---:|
| USD/TWD | TBD | TBD |
| DXY 美元指數 | TBD | TBD |
| USD/JPY | TBD | TBD |
| USD/KRW | TBD | TBD |

### 6. 台灣相關 ADR

| 項目 | 收盤／最新值 | 漲跌幅 |
|---|---:|---:|
| 台積電 ADR | TBD | TBD |
| 聯電 ADR | TBD | TBD |
| 日月光 ADR | TBD | TBD |

### 7. 原油／黃金／Bitcoin

| 項目 | 收盤／最新值 | 漲跌幅 |
|---|---:|---:|
| WTI 原油 | TBD | TBD |
| 黃金 | TBD | TBD |
| Bitcoin BTC | TBD | TBD |

### 8. 重大經濟數據與央行事件

| 事件／數據 | 公布時間 | 市場預期 | 實際結果 | 備註 |
|---|---|---|---|---|
| TBD | TBD | TBD | TBD | TBD |

---

## 三、期貨

TBD

---

## 四、選擇權

TBD
