# 每日盤前分析 V1.0 — ANALYSIS_RULES.md

```text
文件名稱：ANALYSIS_RULES.md
文件版本：V1.0
文件狀態：定案版
適用時區：Asia/Taipei
```

## 1. 目的與模組

本文件定義資料有效性、分析、Fallback、方向、信心、風險及最低交付要求。固定模組：`spot`、`global_markets`、`futures`、`options`、`summary`。報告版面由 `REPORT_TEMPLATE.md` 定義；Dashboard 由 `DASHBOARD_SPEC.md` 定義；執行流程由 `CHATGPT_EXECUTION_PROMPT.md` 定義。

## 2. 資料分層

```text
raw
proxy_raw
fallback_raw
calculated
derived
interpretation
```

不得把計算值、推導值或解讀標示為官方原始資料。

## 3. 日期與時段

所有時間使用 `Asia/Taipei`。必須區分 `analysis_date`、`market_date`、`data_timestamp`、`generated_at`。美股、海外市場與台股可有不同交易日；夜盤與日盤必須分開標示；日期不明資料不得作為核心方向依據。

## 4. 狀態碼

`source_status`：`success`、`failed`、`timeout`、`blocked`、`invalid`、`empty`、`not_available`。

`data_quality_status`：`complete`、`partial`、`stale`、`invalid`、`missing`。

`fallback_status`：`not_used`、`used`、`failed`。

`module_status`：`completed`、`completed_with_warnings`、`partial`、`insufficient_data`、`failed`。

`report_status`：`completed`、`completed_with_warnings`、`partial`、`insufficient_data`、`failed`、`blocked_by_access`、`blocked_by_rule_conflict`。

禁止使用 `failed_but_report_generated`、`fallback`、`success`、`unknown` 作為 `report_status`。流程失敗但已產出報告時使用 `failed`。

## 5. Fallback 固定順序

1. `primary_proxy`：已驗證的主要 Cloudflare Worker Proxy
2. `official_api`：官方 Open API
3. `backup_api_proxy`：官方備援 API／Proxy
4. `primary_web`：已驗證的主要金融資料來源
5. `backup_web`：已驗證的備援金融資料來源
6. `last_valid`：最近一次有效資料，僅限資料性質允許
7. `missing`

`source_role` 只允許上述六種值。Fallback 必須記錄原始來源、失敗原因、採用來源、資料日期、取得時間、資料狀態及信心影響。`last_valid` 必須標示 `data_status=stale`，不得用於當日即時行情、成交量、法人流量、OI 或選擇權鏈，除非正式規格明確允許。

## 6. 最低交付

一旦開始執行，無論一般錯誤、來源失敗、模組失敗或 GitHub 寫回失敗，都不得在產出 Markdown 報告或最小錯誤報告前停止。必須盡可能產出已取得資料、模組狀態、來源與 Fallback、錯誤、缺失資料、未完成項目、風險限制、Dashboard JSON 或 `partial` JSON 及最終狀態。不得以猜測、補零或空白掩蓋失敗。

## 7. 方向與信心

偏多或偏空至少需要兩項獨立證據，且不得有同等強度反向證據。證據接近、現貨與期貨不一致或價格位於支撐壓力間時判定震盪。核心衝突、日期無法校正、證據單一或資料不足時判定方向不明／資料不足。`觀望` 是行動建議，不等同市場方向。

`high` 僅限核心資料完整有效、至少兩個主要模組一致且無重大衝突；`medium` 可有部分缺失或有限 Fallback；`low` 用於歷史值、核心缺失、明顯衝突或單一證據；不足時使用 `insufficient_data`。`high` 不得與核心 `stale`、`missing` 或重大 `invalid` 並存。

## 8. 模組規則

`spot`：分析指數、漲跌、成交量、三大法人、融資、融券、借券、維持率及變化；不得只因單日法人買超判定必然上漲。

`global_markets`：檢查 NASDAQ、Dow、S&P 500、SOX、主要美債殖利率、美元、台幣、日圓、日經、韓國指數、BTC 及重要新聞；不得單獨決定台股方向。

`futures`：區分近月、日／夜盤、價格、成交量、OI、法人部位及現貨／期貨關係；不得重複計權同一法人資料。

`options`：區分近月、當週、到期日、外資、造市商、Call、Put、原始 OI、淨部位、計算值及資料日期。Call Wall、Put Wall、Gamma Wall、Gamma Flip、Max Pain 必須標示來源／公式、日期、到期結構、資料類型及 Fallback 狀態，不得視為絕對支撐壓力。

Opening Range 固定為 `08:45–09:15` 的 1-minute bars，輸出 `OR_High`、`OR_Low`、日期及完整性。OR 獨立於手動 Key Level／Zone，不合併且不受 50 點限制。盤前不得把尚未發生的突破、BOS、VSA 或真／假突破寫成已確認。

### 8.1 TWSE 市場廣度資料判讀

TWSE Proxy 回傳的 `advance_decline` 資料可能同時包含「整體市場」與「股票」兩個欄位。

每日盤前分析的市場廣度只採用「股票」欄位，並遵守以下規則：

1. 只讀取「股票」欄位的上漲、下跌、持平、未成交、無比價及漲停／跌停數據。
2. 「整體市場」欄位一律忽略。
3. 「整體市場」不得納入上漲家數、下跌家數、漲跌比、漲停／跌停統計或市場廣度判讀。
4. 不得將「整體市場」數據誤認為上市股票漲跌家數。
5. 不需要在每日盤前分析報告中呈現「整體市場」數據。
6. 若需分析上櫃股票，必須另行使用 TPEX 官方上櫃股票資料；不得以 TWSE「整體市場」代替上櫃資料。

## 9. 整合與風險

不得以模組數量簡單投票。必須說明支持證據、反向證據、資料重複、權重限制及失效條件。支撐／壓力必須標示價位、類型、來源、日期、距離現價、重要性、失效條件及 Fallback 狀態。

所有錯誤須記錄模組、時間、來源、錯誤類型、重試、Fallback、影響及未完成項目。不得虛構資料、來源或時間；不得把缺失填零；不得把舊資料當最新；不得因單一錯誤提前停止；不得在規則衝突時猜測；不得自動下單。

## 10. 最終狀態優先順序

```text
blocked_by_rule_conflict
> blocked_by_access
> failed
> insufficient_data
> partial
> completed_with_warnings
> completed
```

不得因已產出檔案就標示 `completed`。
