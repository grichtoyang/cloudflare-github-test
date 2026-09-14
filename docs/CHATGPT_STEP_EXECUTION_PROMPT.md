# CHATGPT_STEP_EXECUTION_PROMPT.md — 日期檢查移除修正版

## 修改目的

本版本移除 ChatGPT 執行引擎自行判定「交易日」及「資料日期有效性」的機制。

資料日期、交易日、資料版本與資料是否為最新，均由 GitHub Actions／GitHub 所提供的資料流程負責把關。ChatGPT 不得自行推論、改寫或否定 GitHub 已提供的日期資訊。

## 一、移除項目

請從原版 `CHATGPT_STEP_EXECUTION_PROMPT.md` 移除：

- 台灣交易日驗證要求
- Gate 0 對交易日驗證的必要條件
- Gate 0 對資料日期、資料時間、公布時程、日盤／夜盤涵蓋狀態的必要判定
- ChatGPT 自行判定資料是否過期的規則
- `VALID_TRADING_DAY`
- `VALID_NON_TRADING_DAY`
- `VALID_LATEST_AVAILABLE`
- `VALID_PREVIOUS_SESSION`
- `INTRADAY_VALID`
- `OLD_DATE`
- 所有因日期未驗證而阻擋 Gate 0 的規則

## 二、日期資料權威原則

1. ChatGPT 只使用 GitHub Actions／GitHub 提供的資料。
2. GitHub 資料中的日期、時間、版本與來源資訊，視為上游資料流程提供的結果。
3. ChatGPT 不得因資料日期早於本次執行日期，就自行標記 `OLD_DATE`。
4. ChatGPT 不得因資料日期不是當日，就自行判定資料錯誤。
5. ChatGPT 不得自行推論市場是否已開盤、收盤、休市或完成資料公布。
6. 若 GitHub 資料已附帶資料狀態，ChatGPT 必須原樣保留並引用。
7. 若 GitHub 資料沒有提供日期或狀態，應標記為「上游資料未提供」，不得自行補判。
8. 日期與交易日的正確性由 GitHub Actions／上游資料流程負責把關。

## 三、Gate 0 修正版

Gate 0 只檢查：

- 必要文件是否實際讀取
- GitHub／資料來源是否可存取
- 資料包是否存在
- 資料格式與必要欄位是否存在
- Retry／Fallback 是否依規則執行
- 是否具備後續分析所需的必要輸入

Gate 0 不再自行檢查：

- 台灣是否為交易日
- 執行日期是否與資料日期相同
- 資料是否為上一交易日
- 資料是否因市場休市而延遲
- 資料是否為最新合法交易時段

## 四、保留的全域 Retry／Fallback

全域 Retry／Fallback 規則完整保留，適用於所有 Gate、Stage、GitHub 文件、GitHub 程式碼、GitHub 資料包、API、Proxy、外部資料、資料解析、資料驗證、分析計算、報告產出、Dashboard、GitHub 寫入及寫入後讀回驗證。

任何讀取或處理失敗，必須先完成 Retry／Fallback，再依實際結果標記錯誤狀態。

## 五、報告呈現

報告中的日期、時間、來源與狀態，必須直接引用 GitHub 提供的內容。

不得自行增加或改寫：

- `OLD_DATE`
- `VALID_LATEST_AVAILABLE`
- `VALID_PREVIOUS_SESSION`
- `VALID_TRADING_DAY`
- `VALID_NON_TRADING_DAY`

## 六、保留項目

不得移除：

- 資料存在性檢查
- 欄位完整性檢查
- JSON／格式檢查
- 資料來源檢查
- Retry／Fallback
- 缺失資料記錄
- 錯誤記錄
- 報告產出
- Dashboard 產出
- 最終驗證

**核心原則：ChatGPT 不判日期；GitHub／GitHub Actions 負責日期把關；ChatGPT 忠實使用並呈現 GitHub 提供的結果。**
