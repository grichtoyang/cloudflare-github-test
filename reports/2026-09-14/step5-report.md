# 每日盤前分析 V1.0 — 2026-09-14

> 依 `docs/REPORT_TEMPLATE.md` 產出之完整報告。資料不足項目保留欄位並標註狀態，不以估算值、前一日數值或零值填補。

## 0. 執行與資料品質

| 項目 | 狀態 | 說明 |
|---|---|---|
| 報告日期 | OK | 2026-09-14；時區 Asia/Taipei |
| 單一資料源失敗即停止 | OK | 未因單一模組失敗而停止 |
| 缺失資料處理 | OK | 以 `Unavailable`、`Partial`、`Not Computable`、`Stale` 標註 |
| 日盤後 OI／夜盤交易流量分離 | OK | 未將兩者混用 |
| 數值來源與日期揭露 | Partial | 已取得數值附資料日期；缺失項目明確標註 |

---

# 一、現貨分析模組

## 1.1 大盤行情

| 項目 | 數值 | 判讀 |
|---|---:|---|
| 加權指數 | 45,862.52 | OK；偏空壓力 |
| 開盤／最高／最低／收盤 | Unavailable | 未取得完整 OHLC |
| 漲跌點／漲跌幅 | -322.33／-0.70% | OK；下跌 |
| 成交量／成交金額 | 成交金額約 630.917 億元 | Partial；原始單位與完整欄位需再核驗 |
| 上漲家數／下跌家數／平盤家數 | Unavailable | 必須是上市公司家數，未取得 |
| 5日／10日／20日均線 | Not Computable | 缺完整歷史序列 |
| RSI／ATR | Not Computable | 缺完整歷史序列 |
| 日線結構 | Partial | 以當日下跌判斷為偏空；無完整結構序列 |

## 1.2 現貨法人與籌碼

| 項目 | 狀態 | 判讀 |
|---|---|---|
| 外資買賣超 | Unavailable | 未取得可驗證數值 |
| 投信買賣超 | Unavailable | 未取得可驗證數值 |
| 自營商買賣超 | Unavailable | 未取得可驗證數值 |
| 三大法人合計 | Unavailable | 不以缺失值推估 |
| 融資餘額 | Unavailable | 未取得 |
| 融券餘額 | Unavailable | 未取得 |
| 融資維持率 | Unavailable | 未取得 |
| 借券餘額／借券賣出 | Unavailable | 未取得 |
| 法人籌碼連續性與趨勢 | Not Computable | 缺法人歷史資料 |
| 法人籌碼與指數是否一致 | Not Computable | 缺法人數據 |

## 1.3 類股與產業

| 項目 | 狀態 | 判讀 |
|---|---|---|
| 電子、半導體、AI、PCB、金融 | Unavailable | 未取得完整類股資料 |
| 領漲／領跌類股 | Unavailable | 未取得排行 |
| 類股輪動 | Not Computable | 缺類股時間序列 |
| 重要產業新聞 | Partial | 本報告未納入可驗證的完整新聞資料集 |

## 1.4 現貨圖表與結論

- 加權指數日線／成交量：Partial；目前只有指數與成交金額摘要，無完整歷史序列。
- 三大法人買賣超趨勢：Unavailable。
- 融資融券變化：Unavailable。
- 類股強弱排行：Unavailable。
- 現貨籌碼判斷：**中性偏空，但信心受籌碼資料缺失限制**。
- 現貨支撐／壓力：現貨本身完整技術位階 Not Computable；可參考選擇權 46,000、45,700、45,542 等外部關鍵位，但不得視為現貨技術指標。

---

# 二、重要市場分析模組

## 2.1 美股主要指數

| 項目 | 數值 | 狀態 | 判讀 |
|---|---:|---|---|
| NASDAQ | Unavailable | Unavailable | — |
| S&P 500 | Unavailable | Unavailable | — |
| 道瓊 | Unavailable | Unavailable | — |
| SOX | Unavailable | Unavailable | — |
| VIX | Unavailable | Unavailable | — |

## 2.2 利率、美元與匯率

| 項目 | 數值 | 狀態 | 判讀 |
|---|---:|---|---|
| 美國 2Y 殖利率 | Unavailable | Unavailable | — |
| 美國 10Y 殖利率 | Unavailable | Unavailable | — |
| 美國 20Y 殖利率 | Unavailable | Unavailable | — |
| 美國 30Y 殖利率 | Unavailable | Unavailable | — |
| DXY | Unavailable | Unavailable | — |
| USD/TWD | Unavailable | Unavailable | — |
| USD/JPY | Unavailable | Unavailable | — |

## 2.3 亞洲市場

| 市場 | 數值 | 狀態 |
|---|---:|---|
| 日經 | Unavailable | Unavailable |
| 韓國 | Unavailable | Unavailable |
| 香港 | Unavailable | Unavailable |
| 中國主要指數 | Unavailable | Unavailable |

## 2.4 產業與重大新聞

| 項目 | 狀態 | 判讀 |
|---|---|---|
| AI／半導體／HBM／PCB／CPO | Partial | 未取得完整且可核驗的當日新聞集合 |
| Fed／通膨／非農／ISM | Unavailable | 未取得本次報告所需資料 |
| 經濟／政策／地緣政治 | Unavailable | 未取得完整資料 |

## 2.5 重要市場圖表與結論

- 美股指數漲跌表：Unavailable。
- SOX／NASDAQ 對台股電子股影響：Not Computable。
- 美債殖利率、DXY、匯率：Unavailable。
- 亞洲市場方向：Unavailable。
- 外部市場判斷：**Unavailable，不做方向性假設**。
- 對台股開盤影響：**無法依模板完成定量判讀；需補齊外部市場資料**。

---

# 三、期貨分析模組

## 3.1 台指期日盤行情

| 項目 | 數值 | 判讀 |
|---|---:|---|
| 近月台指期收盤價 | Unavailable | 未取得可驗證數值 |
| 開盤／最高／最低／收盤 | Unavailable | 缺完整 OHLC |
| 漲跌點／漲跌幅 | Unavailable | 未取得 |
| 成交量 | Unavailable | 未取得 |
| 未平倉量 OI | Unavailable | 未取得 |
| OI 增減 | Unavailable | 未取得 |
| 期現貨基差 | Not Computable | 期貨與現貨收盤均不完整 |

## 3.2 每日日盤後法人未平倉

| 法人 | 多單未平倉 | 空單未平倉 | 淨未平倉 | 較前日變化 | 趨勢判斷 |
|---|---:|---:|---:|---:|---|
| 外資及陸資 | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable |
| 投信 | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable |
| 自營商 | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable |
| 三大法人合計 | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable |

### 日盤後期貨法人分析重點

- 外資期貨多單／空單／淨部位：Unavailable。
- 外資為主要觀察核心，但本次無可驗證部位。
- 三大法人合計：Unavailable。
- 與前一日比較：Unavailable。
- 期貨價格與法人部位一致／背離：Not Computable。
- 對隔日日盤影響：不可作方向性結論。

## 3.3 夜盤分析：法人佈局與價格反應

### A. 每日日盤後法人未平倉

| 項目 | 狀態 |
|---|---|
| 外資及陸資淨未平倉 | Unavailable |
| 投信淨未平倉 | Unavailable |
| 自營商淨未平倉 | Unavailable |
| 三大法人合計淨未平倉 | Unavailable |
| 與前一交易日比較 | Unavailable |

### B. 夜盤交易期間法人新增資訊

| 法人 | 夜盤多單交易量 | 夜盤空單交易量 | 夜盤多空淨交易量 | 與日盤後基準關係 | 趨勢判斷 |
|---|---:|---:|---:|---|---|
| 外資及陸資 | Unavailable | Unavailable | Unavailable | Not Computable | Unavailable |
| 投信 | Unavailable | Unavailable | Unavailable | Not Computable | Unavailable |
| 自營商 | Unavailable | Unavailable | Unavailable | Not Computable | Unavailable |
| 三大法人合計 | Unavailable | Unavailable | Unavailable | Not Computable | Unavailable |

> 夜盤交易量／交易金額屬新增交易流量，不等同盤中即時 OI。此次未取得可驗證數據，因此不推估夜盤 OI。

### C. 夜盤價格與成交量

| 項目 | 數值 | 判讀 |
|---|---:|---|
| 夜盤漲跌點 | Unavailable | — |
| 夜盤漲跌幅 | Unavailable | — |
| 夜盤收盤／最新價 | Unavailable | — |
| 夜盤成交量 | Unavailable | — |
| 相對日盤收盤 | Unavailable | — |
| 夜盤方向 | Unavailable | — |

### 夜盤核心分析問題

1. 夜盤法人佈局對隔日日盤：Unavailable。
2. 法人流向與價格一致／背離：Not Computable。
3. 外資夜盤流向是否延續日盤後部位：Not Computable。
4. 夜盤成交量是否支持方向：Not Computable。

## 3.4 期貨圖表與結論

- 台指期日盤價格／成交量／OI：Unavailable。
- 三大法人日盤後淨未平倉：Unavailable。
- 外資期貨淨部位：Unavailable。
- 夜盤漲跌與成交量：Unavailable。
- 夜盤法人多空交易流向：Unavailable。
- 日盤後基準與夜盤新增流向：Not Computable。
- 期貨日盤後法人部位：**Unavailable**。
- 夜盤法人流向：**資料不足**。
- 夜盤價格與法人流向：**Not Computable**。
- 對隔日日盤方向與風險：**僅能列為資料缺口，不作方向性結論**。

---

# 四、選擇權分析模組

## 4.1 原始資料

| 項目 | 狀態 | 說明 |
|---|---|---|
| 近月選擇權 | Partial | 已取得關鍵位資料，但完整鏈資料未在本報告中提供 |
| 當週選擇權 | Unavailable | 未取得可驗證完整資料 |
| Call／Put 成交量 | Unavailable | — |
| Call／Put OI 與 OI 增減 | Partial | 關鍵位模型可用；完整 OI 明細未取得 |
| 外資部位 | Unavailable | — |
| 自營商部位 | Unavailable | — |
| 造市商部位 | Unavailable | 資料源未實際提供，未推估 |
| 到期月份與履約價 | Partial | 關鍵履約價可用；完整到期結構未取得 |

## 4.2 日盤與夜盤資料規則

- 選擇權 OI 以日盤結束後公布資料為準。
- 本次未取得可驗證的選擇權夜盤獨立即時 OI，因此標註 `Unavailable`／`Not Computable`。
- 夜盤新增 Call／Put 交易口數與金額：Unavailable。
- 不將夜盤交易流量直接視為新增 OI。
- 本模組未重複假設或補造夜盤 OI。

## 4.3 選擇權部位：夜盤 Buy/Sell Call／Put 交易金額

### 夜盤法人交易金額表

| 法人 | Buy Call 金額 | Sell Call 金額 | Buy Put 金額 | Sell Put 金額 | 主要變化 | 方向／風險判斷 |
|---|---:|---:|---:|---:|---|---|
| 外資 | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | Not Computable |
| 自營商 | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | Not Computable |
| 三大法人合計 | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | Not Computable |

### 與前一交易日比較

| 法人 | Buy Call 變化 | Sell Call 變化 | Buy Put 變化 | Sell Put 變化 | 趨勢判斷 |
|---|---:|---:|---:|---:|---|
| 外資 | Unavailable | Unavailable | Unavailable | Unavailable | Not Computable |
| 自營商 | Unavailable | Unavailable | Unavailable | Unavailable | Not Computable |

### 必須觀察的重點

1. 外資 Buy Call：Unavailable。
2. 外資 Sell Call：Unavailable。
3. 外資 Buy Put：Unavailable，不能判定是否異常暴增。
4. 外資 Sell Put：Unavailable。
5. 自營商與外資同向／分歧：Not Computable。
6. 交易金額與夜盤價格、期貨流向一致性：Not Computable。
7. 單一 Buy/Sell 類別不作絕對方向解讀。

### 外資 Buy Put 異常暴增判定

- 當日與前一交易日：Unavailable。
- 近 5 個交易日平均：Unavailable。
- 判定：**資料不足**。
- 不得推論避險需求是否暴增。

## 4.4 選擇權關鍵價位

> 資料日期：2026-09-11；相對報告日期 2026-09-14 為 `Stale`。以下僅作為最近可取得的關鍵位參考，不視為 2026-09-14 即時盤後重算結果。

| 關鍵位 | 數值 | 狀態 | 交易解讀 |
|---|---:|---|---|
| Call Wall | 48,200 | Stale／Partial | 主要上方壓力 |
| Put Wall | 46,000 | Stale／Partial | 第一方向分界 |
| Max Pain | 46,250 | Stale／Partial | 反彈確認／價格吸引參考 |
| Gamma Wall | 45,700 | Stale／Partial | Gamma 反應／支撐區 |
| Gamma Flip | 約 45,542 | Stale／Partial | Gamma regime 風險門檻 |

### 選擇權圖表與結論

- 完整近月／當週 OI 分布圖：Unavailable。
- Call／Put OI 增減趨勢：Unavailable。
- 外資／自營商部位：Unavailable。
- 造市商部位：Unavailable，未捏造。
- 關鍵位結論：
  - 46,000：第一方向分界；站回並守穩才有利反彈延續。
  - 46,250：反彈確認位。
  - 45,700：Gamma 反應／支撐觀察區。
  - 約 45,542：Gamma regime 風險門檻。
  - 48,200：主要上方壓力。
- 選擇權籌碼總結：**中性偏空／資料日期偏舊，僅供情境規劃**。

---

# 五、綜合總結

## 5.1 跨模組整合

| 模組 | 狀態 | 綜合判斷 |
|---|---|---|
| 現貨 | Partial | 指數下跌，現貨方向偏空；籌碼與技術序列缺失 |
| 重要市場 | Unavailable／Partial | 無法完成外部市場方向判斷 |
| 期貨 | Unavailable | 期貨價格、OI、法人部位與夜盤流量缺失 |
| 選擇權 | Partial／Stale | 關鍵位可用但資料日期為 2026-09-11 |

## 5.2 隔日日盤情境

### 情境 A：站回 46,000 並進一步突破 46,250

- 代表價格重新取得第一方向分界，並開始確認反彈。
- 仍須搭配成交量、現貨與期貨法人資料確認。
- 未取得完整資料前，不得直接視為高勝率多單訊號。

### 情境 B：跌破 45,700

- 代表價格進入 Gamma 反應／支撐失守觀察區。
- 若再接近或跌破約 45,542，需提高波動與 regime 轉換風險警戒。
- 必須等待價格行為確認，不追價。

### 情境 C：46,000 下方震盪

- 偏空壓力仍在，但可能形成區間震盪。
- 不宜只憑單一關鍵位交易。
- 應等待真假突破、成交量效率與價格結構確認。

## 5.3 交易風險控管

1. 不以單一選擇權關鍵位直接進場。
2. 不將日盤後 OI 與夜盤新增交易流量混用。
3. 不以缺失資料補零、補前值或估算值。
4. 關鍵位資料為 2026-09-11，必須標註 `Stale`。
5. 在期貨與法人資料缺失下，降低方向性信心與部位曝險。
6. 以價格行為、成交量效率、真假突破與風險報酬比作為實際進場前提。

---

# 六、資料品質、成功／失敗／Fallback 與完成度

## 6.1 成功項目

- 加權指數 45,862.52。
- 指數漲跌 -322.33 點／-0.70%。
- 成交金額摘要。
- 選擇權 Call Wall、Put Wall、Max Pain。
- Gamma Wall、Gamma Flip。
- 關鍵位情境整合與風險說明。
- 日盤後 OI 與夜盤交易流量分離規則。

## 6.2 Partial 項目

- 現貨行情：僅取得部分欄位。
- 選擇權：關鍵位模型可用，但完整鏈資料與法人分類資料不足。
- 產業新聞：未完成完整資料集合。

## 6.3 Unavailable／Not Computable 項目

- 現貨完整 OHLC、上市公司漲跌家數。
- 5／10／20 日均線、RSI、ATR。
- 現貨法人、融資融券、借券。
- 美股、殖利率、美元、匯率、亞洲市場完整數據。
- 期貨行情、OI、法人部位、夜盤價格與流量。
- 選擇權夜盤 Buy/Sell Call／Put 金額。
- 外資 Buy Put 異常暴增判定。

## 6.4 Fallback 狀態

| 項目 | Fallback 狀態 |
|---|---|
| 選擇權關鍵位 | 使用最近可取得之 2026-09-11 資料；標註 `Stale` |
| 其他缺失數據 | 無可驗證備援可用；標註 `Unavailable` |
| 估算／前值／零值填補 | 未使用 |

## 6.5 整體完成度

> 本次未具備模板要求的完整必要項目計數器，因此**不宣稱虛構的百分比完成度**。依模板規則，完成度應由程式以「已成功取得並完成分析的必要項目數 ÷ 必要項目總數 × 100%」計算；本報告將狀態保留為：**Not Computable（缺少必要項目計數器）**。

## 最終狀態

**STEP 5：依模板完整報告已重新產出。**

**報告品質：Partial／Completed with warnings。**

**不可宣稱：完整資料已取得、所有模組均 OK、或整體完成度為 70%。**
