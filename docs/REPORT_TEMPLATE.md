# 每日盤前分析 V1.0 — Markdown 報告模板

**文件狀態：定案版**  
**時區：Asia/Taipei**

## 1. 強制執行規則

1. 讀取全部規格後才開始分析。
2. 單一來源、endpoint、模組或圖表失敗，不得提前停止。
3. 必須記錄錯誤、執行既定 fallback，並繼續不受影響的模組。
4. 即使資料不完整，也必須盡可能產出 Markdown 報告；若最低限度報告無法產出，才使用 `report_status=failed`。
5. 不得捏造數據，不得以 `0`、前一日數值或未驗證估算值填補缺漏。
6. 必須區分事實、解讀、推測與交易風險。
7. 必須區分日盤後 OI 存量與夜盤新增交易流量。
8. 報告最後必須列出成功、失敗、Fallback、未完成項目與限制。

## 2. 固定 Fallback 順序

```text
1. primary_proxy
2. official_api
3. backup_api_proxy
4. primary_web
5. backup_web
6. last_valid
7. missing
```

Retry 可以在同一來源內進行，但不得任意改變上述來源層級順序。

## 3. 報告標頭

| 欄位 | 內容 |
|---|---|
| 報告日期 | `YYYY-MM-DD`，以台北時區判定 |
| 產出時間 | ISO 8601，含 `+08:00` |
| 時區 | `Asia/Taipei` |
| `report_status` | 見正式狀態表 |
| `package_status` | `complete`／`partial`／`failed`／`invalid` |
| 整體完成度 | 成功完成必要項目 ÷ 必要項目總數 × 100% |
| 資料品質 | 依各資料集 `data_status` 彙整 |

## 4. 正式狀態碼

### `report_status`

- `completed`
- `completed_with_warnings`
- `partial`
- `insufficient_data`
- `failed`
- `blocked_by_access`
- `blocked_by_rule_conflict`

### `data_status`

- `fresh`
- `delayed`
- `stale`
- `missing`
- `invalid`
- `partial`
- `estimated`
- `insufficient_data`

### `source_role`

- `primary_proxy`
- `official_api`
- `backup_api_proxy`
- `primary_web`
- `backup_web`
- `last_valid`

## 5. 固定五大分析模組

### 一、現貨

- 加權指數行情與技術結構
- 三大法人買賣超
- 融資、融券、借券與維持率（若取得）
- 類股與產業強弱
- 支撐、壓力、方向與限制

### 二、重要市場

- NASDAQ、S&P 500、Dow Jones、SOX、VIX（若取得）
- 美國 2Y／10Y／20Y／30Y 殖利率
- DXY、USD/TWD、USD/JPY
- 日韓等亞洲市場
- Bitcoin、財經／產業／公司新聞
- 對台股與台指期的可能影響

### 三、期貨

- 台指期日盤行情、OI、期現貨基差
- 日盤後法人多空未平倉與變化
- 夜盤價格、成交量與法人新增交易流量
- 嚴禁把夜盤交易流量稱為盤中即時法人 OI

### 四、選擇權

- 近月與當週 Call／Put OI、成交量與變化
- Call Wall、Put Wall、Gamma Wall、Gamma Flip、Max Pain
- 外資、自營商及實際提供的造市商資料
- 選擇權 OI 以可驗證的日盤後資料為準
- 未取得可驗證夜盤 OI 時，標示 `missing`、`insufficient_data` 或 `Not Computable`

### 五、綜合總結

- 市場 Regime：Trend／Range／Transition
- 台股與台指期方向：偏多／偏空／中性／資料不足
- 主要支撐與壓力
- 多空情境與觸發條件
- 風險、失效條件與不可判定項目
- 交易計畫只能建立在已驗證資料上

## 6. 每個模組固定結構

1. 資料摘要
2. 已知事實
3. 數據解讀
4. 推測與可能影響
5. 關鍵價位或指標
6. 風險與限制
7. 模組結論

## 7. 錯誤與完成度

報告結尾必須包含：

- 成功取得與完成分析項目
- 失敗或缺失項目
- 各項 `data_status`
- 實際使用的 `source_role`
- Fallback 使用原因
- `last_valid` 使用時的原始資料日期與 `stale` 標記
- 未完成項目
- 影響分析可信度的限制
- `report_status`
- 整體完成度百分比

## 8. 禁止事項

- 不得使用 `SUCCESS`、`SUCCESS_WITH_FALLBACK`、`PARTIAL_SUCCESS`、`FAILED_WITH_REPORT`、`FAILED_FATAL` 作為 `report_status`。
- 不得使用 `failed_but_report_generated` 作為狀態。
- 不得把 `fallback`、`unknown` 當成正式報告狀態。
- 不得把缺失資料填成零。
- 不得把舊資料當成目前資料而不標註 `stale`。
- 不得隱藏錯誤、資料缺失、來源切換或規則衝突。
