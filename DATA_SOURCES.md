# DATA_SOURCES.md

## 1. 文件目的

本文件列出「每日盤前分析 V1.0」預定使用的資料來源，以及各資料來源主要提供的市場資訊。

本文件作為後續 ChatGPT 查找資料、驗證資料來源，以及撰寫 Python 資料收集程式時的參考依據。

---

## 2. 資料來源使用原則

1. 優先使用官方資料來源。
2. 優先使用已建立並確認可運作的 Cloudflare Proxy。
3. 各資料項目應依實際需求，確認可使用的資料來源與取得方式。
4. 資料取得方式可能包含：
   - API
   - OpenAPI
   - CSV
   - JSON
   - HTML
   - 網頁資料
   - Cloudflare Proxy
5. 本文件所列網址為資料來源入口或參考網址，實際使用時仍須確認可取得的資料內容與路徑。

---

## 3. Cloudflare Proxy

### 3.1 TWSE Proxy

網址：

https://twse-proxy.grichtoyang.workers.dev/

用途：

- 取得臺灣證券交易所相關資料。
- 提供台股現貨、三大法人、融資融券及其他 TWSE 資料。
- 作為 Python 程式連接 TWSE 資料的中介來源。

### 3.2 TAIFEX Proxy

網址：

https://taifex.grichtoyang.workers.dev/

用途：

- 取得臺灣期貨交易所相關資料。
- 提供台指期、期貨法人部位、選擇權及其他 TAIFEX 資料。
- 作為 Python 程式連接 TAIFEX 資料的中介來源。

---

## 4. 台股現貨資料來源

### 4.1 臺灣證券交易所 TWSE

網址：

https://www.twse.com.tw/

用途：

- 加權指數
- 台股大盤資料
- 三大法人買賣超
- 融資融券
- 個股及市場交易資料
- 其他臺灣證券交易所公開資料

### 4.2 臺灣證券交易所 OpenAPI／公開資料

網址：

https://www.twse.com.tw/

用途：

- 取得 TWSE 公開資料。
- 依實際資料項目確認 API、CSV、JSON 或其他可用格式。

### 4.3 櫃買中心 TPEX

網址：

https://www.tpex.org.tw/

用途：

- 櫃買指數
- 上櫃市場資料
- 上櫃股票交易資料
- 其他櫃買中心公開資訊

### 4.4 FinMind

網址：

https://finmindtrade.com/

用途：

- 台股歷史資料
- 三大法人資料
- 融資融券資料
- 個股交易資料
- 其他可取得的金融市場資料

### 4.5 Yahoo 股市

網址：

https://tw.finance.yahoo.com/

用途：

- 台股行情
- 加權指數
- 個股價格與成交量
- 市場相關資訊
- 作為市場資料交叉比對來源

### 4.6 Goodinfo! 台灣股市資訊網

網址：

https://goodinfo.tw/

用途：

- 個股基本資料
- 籌碼資料
- 法人資料
- 融資融券
- 財務與市場資訊
- 個股及產業查詢

### 4.7 MoneyDJ 理財網

網址：

https://www.moneydj.com/

用途：

- 台股市場資訊
- 個股資料
- 法人與籌碼資訊
- 產業與財經資訊

### 4.8 HiStock 嗨投資

網址：

https://histock.tw/

用途：

- 台股行情
- 技術分析資料
- 個股資訊
- 市場與籌碼資料

### 4.9 財報狗

網址：

https://statementdog.com/

用途：

- 公司財務資料
- 財報資訊
- 營收與獲利資料
- 公司基本面資訊

### 4.10 公開資訊觀測站 MOPS

網址：

https://mops.twse.com.tw/

用途：

- 公司重大訊息
- 財務報告
- 營收資料
- 法說會及公司公告
- 其他上市櫃公司公開資訊

---

## 5. 期貨與選擇權資料來源

### 5.1 臺灣期貨交易所 TAIFEX

網址：

https://www.taifex.com.tw/

用途：

- 台指期行情
- 期貨交易資料
- 期貨未平倉量
- 三大法人期貨部位
- 選擇權交易資料
- 選擇權未平倉量
- 買權與賣權資料
- 其他期貨交易所公開資料

### 5.2 TAIFEX OpenAPI

網址：

https://openapi.taifex.com.tw/

用途：

- 取得 TAIFEX 公開 API 資料。
- 查找期貨、選擇權、法人部位及其他公開資料。
- 依實際資料項目確認可用 endpoint、資料格式與更新時間。

---

## 6. 財經新聞與產業資訊來源

### 6.1 鉅亨網

網址：

https://news.cnyes.com/

用途：

- 台股新聞
- 財經新聞
- 產業新聞
- 公司新聞
- 國際市場新聞

### 6.2 工商時報

網址：

https://www.ctee.com.tw/

用途：

- 財經新聞
- 產業趨勢
- 公司與市場消息
- 台灣產業資訊

### 6.3 經濟日報

網址：

https://money.udn.com/

用途：

- 財經新聞
- 產業新聞
- 公司動態
- 台股及國際市場資訊

### 6.4 聯合新聞網財經

網址：

https://udn.com/news/cate/2/6644

用途：

- 財經新聞
- 市場消息
- 產業與公司資訊

### 6.5 公開資訊觀測站 MOPS

網址：

https://mops.twse.com.tw/

用途：

- 公司重大訊息
- 公司公告
- 財報與營收
- 法說會資料
- 上市櫃公司正式揭露資訊

---

## 7. 國際市場資料來源

### 7.1 Yahoo Finance

網址：

https://finance.yahoo.com/

用途：

- 美國主要股價指數
- Nasdaq
- Dow Jones
- S&P 500
- 費城半導體指數
- 國際股票與市場資料
- 其他國際金融市場資訊

### 7.2 Investing.com

網址：

https://www.investing.com/

用途：

- 國際股市指數
- 美國公債殖利率
- 美元指數
- 匯率
- 國際商品
- 其他全球市場資料

### 7.3 TradingView

網址：

https://www.tradingview.com/

用途：

- 國際市場行情
- 技術分析資料
- 指數與金融商品走勢
- 市場價格交叉比對

### 7.4 新浪財經

網址：

https://finance.sina.com.cn/stock/

用途：

- 中國及亞洲市場資訊
- 國際市場新聞
- 股票與指數資料
- 市場消息交叉參考

---

## 8. 資料來源優先順序

### 第一優先：官方資料

- TWSE
- TAIFEX
- TPEX
- MOPS
- 其他官方公開資料來源

### 第二優先：已確認可運作的 Proxy 或 API

- TWSE Proxy
- TAIFEX Proxy
- TWSE API
- TAIFEX OpenAPI
- FinMind API

### 第三優先：財經資訊網站

- Yahoo 股市
- Yahoo Finance
- Goodinfo!
- MoneyDJ
- HiStock
- 財報狗
- Investing.com
- TradingView

### 第四優先：財經新聞與產業資訊網站

- 鉅亨網
- 工商時報
- 經濟日報
- 聯合新聞網財經
- 新浪財經

---

## 9. Python 程式使用規範

後續撰寫 Python 程式時，應依照本文件所列資料來源進行查找與實作。

實際程式應使用經確認可取得的資料來源與資料路徑，例如：

- API endpoint
- OpenAPI endpoint
- CSV 下載路徑
- JSON 資料路徑
- HTML 網頁
- Cloudflare Proxy endpoint
- 其他已確認可使用的資料取得方式

Python 程式應依實際確認結果撰寫，不預設所有網站都具有相同的資料格式或取得方式。

---

## 10. 文件目前範圍

本文件目前只定義：

- 預定使用的資料來源
- 各資料來源的用途
- 資料來源的優先順序
- 後續 Python 實作時的查找依據

本文件不定義：

- Python 程式架構
- 資料庫結構
- API 詳細欄位格式
- 報告內容與分析邏輯
- 自動化執行流程
- 交易策略或交易訊號

上述內容由其他專案文件另行定義。
