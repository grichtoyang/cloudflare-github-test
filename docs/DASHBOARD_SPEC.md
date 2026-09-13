# 每日盤前分析 V1.0 — Dashboard Specification

**文件狀態：正式定案版**

## 1. 文件定位

Dashboard 是視覺化展示層，不是獨立分析引擎。

- Markdown 報告與 Dashboard JSON 必須來自同一份分析結果。
- Dashboard 不重新抓資料、不重新計算結論、不自行推導交易方向。
- 所有頁面共用同一份 `dashboard_latest.json`。
- 單一資料源、模組或圖表失敗，不得使整個 Dashboard 崩潰。
- 必須揭露資料品質、延遲、缺失、Fallback、錯誤與未完成項目。

## 2. 技術與檔案結構

```text
dashboard/
├── index.html
├── style.css
├── app.js
└── data/
    └── dashboard_latest.json
```

| 檔案 | 責任 |
|---|---|
| `index.html` | 頁面骨架與頁面切換 |
| `style.css` | RWD、卡片、狀態與無障礙樣式 |
| `app.js` | 讀取 JSON、資料綁定、頁面切換、錯誤處理 |
| `dashboard_latest.json` | 最新結構化分析結果 |

## 3. 固定頁面

Page Selection 是必要核心功能，固定五頁：

| Page ID | 名稱 | 內容 |
|---|---|---|
| `summary` | 總結 | 綜合方向、Regime、燈號、支撐壓力、情境與風險 |
| `spot` | 現貨 | TAIEX、現貨籌碼、融資融券、借券、技術結構 |
| `futures` | 期貨 | 台指期、日盤、夜盤、基差、法人 OI、夜盤流向 |
| `options` | 選擇權 | 近月／當週、OI、GEX、Call Wall、Put Wall、Gamma Wall、Gamma Flip、Max Pain |
| `global_markets` | 重要市場 | 美股、SOX、美債、美元、匯率、亞洲、BTC、新聞 |

行為要求：

- 預設開啟 `summary`。
- 目前頁面須高亮並提供 `aria-selected` 等無障礙標記。
- 桌面使用頁籤；手機支援橫向滑動或下拉選單。
- 頁面切換不得重新抓資料或重新計算結論。
- 必須支援鍵盤操作且不得造成整頁水平溢出。

## 4. 共通資料顯示

每個頁面至少顯示：

- `report_date`
- `generated_at`
- `runtime_date`
- 時區 `Asia/Taipei`
- `report_status`
- `data_status`
- 分析信心
- 來源與更新時間
- 延遲、Fallback、錯誤與未完成提示

每張數據卡至少顯示：

1. 名稱與最新值
2. 單位
3. 漲跌或變化
4. 前值（如有）
5. 資料日期／時間
6. 來源
7. 狀態

## 5. 正式狀態契約

### `report_status`

只允許：

```text
completed
completed_with_warnings
partial
insufficient_data
failed
blocked_by_access
blocked_by_rule_conflict
```

### `data_status`

只允許：

```text
fresh
delayed
stale
missing
invalid
partial
estimated
insufficient_data
```

### `source_role`

只允許：

```text
primary_proxy
official_api
backup_api_proxy
primary_web
backup_web
last_valid
```

### `github_writeback_status`

只允許：

```text
success
partial
failed
```

不得把 `SUCCESS`、`SUCCESS_WITH_FALLBACK`、`FAILED_FATAL`、`failed_but_report_generated` 或 `fallback` 當作 `report_status`。

## 6. 資料揭露規則

- 缺失資料不得補成 `0`，使用 `null` 或明確缺失狀態。
- 沒有前值不得製造變化。
- 沒有單位不得猜測。
- 延遲資料不得標示為即時。
- 估算資料必須標示 `estimated` 與計算版本。
- Fallback 必須標示原始來源、實際來源、原因與時間。
- 不同交易日期、盤別或時間戳不得無說明混合。
- OI 為部位存量；交易量與夜盤流向為期間流量，不得混用。
- 近月與當週選擇權必須分開展示。
- Call Wall、Put Wall、Gamma Wall、Gamma Flip、Max Pain 不得單獨直接作為交易訊號。

## 7. 各頁面最低展示要求

### 現貨

TAIEX 行情、成交量、三大法人、融資融券、借券、技術結構、支撐壓力與資料限制。

### 期貨

台指期日盤行情、期現基差、日盤後法人 OI、夜盤價格、夜盤成交量、夜盤法人新增交易流向，以及存量／流量的明確區分。

夜盤交易量或多空淨交易量不得宣稱為盤中即時法人 OI。

### 選擇權

近月與當週分開展示；至少包含 Call Wall、Put Wall、Gamma Wall、Gamma Flip、Max Pain、OI、GEX、變化、來源、時間與狀態。

### 重要市場

NASDAQ、S&P 500、Dow Jones、SOX、美債殖利率、DXY、匯率、日韓市場、BTC、金融與產業新聞；必須區分事實、解讀與推測。

### 總結

綜合方向、Regime、主要證據、支撐壓力、情境分析、風險、資料品質、Fallback、缺失與未完成項目。

## 8. 最低 JSON 結構

```json
{
  "schema_version": "1.0",
  "report_date": "YYYY-MM-DD",
  "generated_at": "ISO-8601",
  "runtime_date": "YYYY-MM-DD",
  "report_status": "completed",
  "data_status": "fresh",
  "data_quality": {},
  "sources": {},
  "market": {},
  "futures": {},
  "options": {},
  "macro": {},
  "news": {},
  "summary": {},
  "warnings": [],
  "incomplete_items": [],
  "fallbacks": []
}
```

## 9. 驗收標準

- [ ] 五頁可切換且不重新抓資料
- [ ] Dashboard 與 Markdown 使用同一份分析結果
- [ ] 所有數據卡有來源、時間、單位與狀態
- [ ] 缺失資料不補零
- [ ] 延遲、估算、Fallback 與錯誤清楚揭露
- [ ] OI 與交易流量未混用
- [ ] 近月與當週選擇權分開
- [ ] 單一模組失敗不造成整頁崩潰
- [ ] JSON 結構與狀態值符合本文件
- [ ] 未經端到端測試不得宣稱完成
