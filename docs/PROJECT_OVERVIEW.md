# 每日盤前分析 V1.0｜專案總覽

**文件狀態：正式定案版**

## 1. 專案目的

建立可每日執行、可追溯、可驗證，並具備錯誤隔離與固定 Fallback 機制的盤前分析系統。系統彙整台股、台指期、選擇權、國際市場、總體經濟與新聞資料，產出 Markdown 報告及 Dashboard JSON。

完整流程：

1. 取得並保存原始資料與 metadata。
2. 正規化、驗證及標記資料品質。
3. 執行市場分析。
4. 產出 Markdown 與 Dashboard JSON。
5. 揭露錯誤、缺失、Fallback、未完成項目與限制。
6. 驗證輸出並嘗試寫回 GitHub。

## 2. 分析範圍

- 台股現貨、加權指數與三大法人。
- 台指期近月、日盤、夜盤與法人部位。
- 融資、融券、借券等籌碼。
- 台指選擇權近月與當週。
- Call Wall、Put Wall、Gamma Wall、Gamma Flip、Max Pain。
- 美股、SOX、美債、美元、匯率、日韓市場與 BTC。
- Fed、經濟數據、金融新聞、產業新聞及公司事件。

## 3. 核心原則

1. Data First：先取得與驗證資料，再分析。
2. Traceability：重要結論必須可追溯。
3. Facts vs. Inference：事實、推論與預測分開。
4. No False Completeness：缺失資料不得假裝完整。
5. Risk-Control Priority：風險控管優先於方向預測。
6. No OCR Core：OCR 不作為核心依賴。
7. Failure Isolation：單一模組失敗不得拖垮全系統。
8. No Unauthorized Changes：未經確認不得任意修改規則。

## 4. 日期與時間

以 `Asia/Taipei` 判定排程與市場日期，並分開記錄：

- `runtime_date`
- `market_date`
- `data_date`
- `generated_at`

不得因 UTC 轉換、跨日或休市日誤用資料；不得把前一交易日資料標示為當日資料。

## 5. 錯誤與 Fallback

單一來源、Endpoint、模組或輸出失敗，不得直接停止整體流程。必須記錄錯誤、執行既定 Fallback、標記影響並繼續其他模組；在可行時仍須產出報告與 Dashboard。

固定順序：

```text
primary_proxy
official_api
backup_api_proxy
primary_web
backup_web
last_valid
missing
```

`last_valid` 必須標示為 `stale`，不得當作即時資料。缺失資料不得補成 `0`。

## 6. 正式狀態

`report_status` 僅可使用：

- `completed`
- `completed_with_warnings`
- `partial`
- `insufficient_data`
- `failed`
- `blocked_by_access`
- `blocked_by_rule_conflict`

`data_status` 僅可使用：

- `fresh`
- `delayed`
- `stale`
- `missing`
- `invalid`
- `partial`
- `estimated`
- `insufficient_data`

GitHub 寫回狀態使用：`success`、`partial`、`failed`。

不得使用舊式大寫狀態或 `failed_but_report_generated` 作為正式 `report_status`。

## 7. 系統邊界

V1.0 不包含自動下單、自動交易、獲利保證、預測準確保證或未核准的資料來源與規則變更。資料抓取完成不等於 ChatGPT 分析完成；報告產出不等於 GitHub 寫回成功。

## 8. 成功標準

- 資料可取得、保存、驗證與追溯。
- 部分失敗時仍可繼續執行。
- Markdown 與 Dashboard JSON 使用同一份分析結果。
- 錯誤、缺失、Fallback、未完成項目與限制均揭露。
- 輸出與 GitHub 寫回狀態均可驗證。
- 未經端到端測試不得宣稱整體系統完成。

## 9. 文件關係

本文件為專案總覽；其他文件定義系統架構、資料來源、資料 schema、分析規則、報告、Dashboard、錯誤與 Fallback、執行 Prompt、檔案結構及版本控制。所有文件必須使用一致的狀態碼、Fallback 順序與日期規則。
