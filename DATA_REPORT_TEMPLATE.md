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

**資料來源：**
1. Cloudflare Workers：TAIFEX Proxy — https://taifex.grichtoyang.workers.dev/
2. TAIFEX Open API — https://openapi.taifex.com.tw/

# 期貨核心數據 7 項

## 1．台指期近月日盤行情
- 開盤價
- 最高價
- 最低價
- 收盤價
- 漲跌點數
- 漲跌幅
- 成交量
- 日盤高點及低點

## 2．台指期近月夜盤行情
- 開盤價
- 最高價
- 最低價
- 收盤價
- 漲跌點數
- 漲跌幅
- 成交量
- 夜盤高點及低點

## 3．法人台指期多空未平倉部位
- 外資多方 OI
- 外資空方 OI
- 外資多空淨 OI
- 投信多方 OI
- 投信空方 OI
- 投信多空淨 OI
- 自營商多方 OI
- 自營商空方 OI
- 自營商多空淨 OI
- 三大法人合計多方 OI
- 三大法人合計空方 OI
- 三大法人合計多空淨 OI
- 各法人多方、空方及多空淨 OI 變化

## 4．前十大交易人多空未平倉部位
- 前十大交易人多方 OI
- 前十大交易人空方 OI
- 前十大交易人多空淨 OI
- 多方 OI 變化
- 空方 OI 變化
- 多空淨 OI 變化

## 5．日盤、夜盤法人交易資料
- 外資日盤多單交易量
- 外資日盤空單交易量
- 外資日盤多空淨交易量
- 外資夜盤多單交易量
- 外資夜盤空單交易量
- 外資夜盤多空淨交易量
- 外資日盤／夜盤交易量變化
- 投信日盤多單交易量
- 投信日盤空單交易量
- 投信日盤多空淨交易量
- 投信夜盤多單交易量
- 投信夜盤空單交易量
- 投信夜盤多空淨交易量
- 投信日盤／夜盤交易量變化
- 自營商日盤多單交易量
- 自營商日盤空單交易量
- 自營商日盤多空淨交易量
- 自營商夜盤多單交易量
- 自營商夜盤空單交易量
- 自營商夜盤多空淨交易量
- 自營商日盤／夜盤交易量變化
- 三大法人日盤多空淨交易量
- 三大法人夜盤多空淨交易量
- 三大法人日盤／夜盤交易量變化
- 法人日盤、夜盤交易口數
- 法人日盤、夜盤交易金額

## 6．期貨與現貨關係
- 台指期近月價格
- 加權指數價格
- 台指期與加權指數價差
- 價差百分比
- 日盤基差
- 夜盤價格相對日盤收盤的變化

## 7．日盤、夜盤與籌碼變化對照
- 價格變化
- 成交量變化
- 台指期總 OI 變化
- 法人多方、空方及多空淨 OI 變化
- 前十大交易人多空淨 OI 變化

---

## 四、選擇權

## 資料來源

- 主要資料來源：TAIFEX 臺灣期貨交易所
- 資料範圍：
  - 選擇權成交量、未平倉量 OI、OI 增減
  - 外資與自營商 Call／Put 部位
  - 各履約價 Call／Put OI 分布
  - 選擇權衍生關鍵點位計算所需資料
- 資料取得方式：TAIFEX 官方資料 API／CSV
- API 轉接：TAIFEX Cloudflare Worker Proxy
- 時區：Asia/Taipei

# 選擇權核心數據與資料 16 項

## 1．選擇權交易日期、到期日與資料時間
- 交易日期
- 到期月份／到期日
- 資料更新時間
- 日盤／夜盤或盤後資料標記

## 2．Call 總成交量、OI、OI 增減
- Call 總成交量
- Call 總未平倉量 OI
- Call OI 增減

## 3．Put 總成交量、OI、OI 增減
- Put 總成交量
- Put 總未平倉量 OI
- Put OI 增減

## 4．Call／Put 比例與變化
- Call／Put 成交量比例
- Call／Put 未平倉量比例
- Put／Call Ratio
- Call／Put 比例變化
- 與前一交易日比較

## 5．外資 Call／Put 部位
- 外資 Call 部位
- 外資 Put 部位
- 外資 Call／Put 淨部位
- 外資部位增減

## 6．自營商 Call／Put 部位
- 自營商 Call 部位
- 自營商 Put 部位
- 自營商 Call／Put 淨部位
- 自營商部位增減

## 7．主要 Call OI 集中區
- 主要 Call OI 集中履約價
- Call OI 最大履約價
- 主要 Call OI 集中區

## 8．主要 Put OI 集中區
- 主要 Put OI 集中履約價
- Put OI 最大履約價
- 主要 Put OI 集中區

## 9．Call OI 增減集中區
- Call OI 增加最多的履約價
- Call OI 減少最多的履約價
- Call OI 增減集中區

## 10．Put OI 增減集中區
- Put OI 增加最多的履約價
- Put OI 減少最多的履約價
- Put OI 增減集中區

## 11．Call Wall
- Call Wall 價位
- 對應到期月份／到期日
- 與前一交易日的變化

## 12．Put Wall
- Put Wall 價位
- 對應到期月份／到期日
- 與前一交易日的變化

## 13．Gamma Wall
- Gamma Wall 價位
- 對應到期月份／到期日
- 與前一交易日的變化

## 14．Gamma Flip
- Gamma Flip 價位
- 對應到期月份／到期日
- 與前一交易日的變化

## 15．Max Pain
- Max Pain 價位
- 對應到期月份／到期日
- 與前一交易日的變化

## 16．資料來源、時間、時區與狀態
- 資料來源
- API／Worker 來源
- 資料日期
- 資料時間
- 時區：`Asia/Taipei`
- 日盤／夜盤／盤後標記
- 資料完整性
- 缺資料或延遲說明

