# 每日盤前分析｜GitHub Actions Prompt V1.0

> 本文件為「每日盤前分析」GitHub Actions 執行規格。
> 它負責 L1 Data Acquisition、Validation、Snapshot、Canonical Package 與 AI-input；不取代 ChatGPT 的 Web / News 資料取得，也不取代 V1.1 的 L2～L5 分析、決策與報告規格。

---

# 1. SYSTEM ARCHITECTURE — LOCKED

本專案採三通道資料取得架構：

```text
                         AI-input
                            │
                            ▼
                         ChatGPT
                            │
          ┌─────────────────┼─────────────────┐
          ▼                 ▼                 ▼
       GitHub              Web              News
          │                 │                 │
          ▼                 ▼                 ▼
   台股／期貨／選擇權     美股／美債          Fed／產業
   法人／OI／GEX          FX／日韓            財報／事件
   TAIFEX／TWSE           全球市場            AI／半導體
          └─────────────────┼─────────────────┘
                            ▼
                     每日盤前綜合分析
```

**GitHub 不取代 Web / News。**

- GitHub：負責可自動化、結構化、可驗證、可保存的台灣市場資料。
- Web：由 ChatGPT 正式分析時補充最新全球市場、Rates、FX、Commodities、Macro 等資料。
- News：由 ChatGPT 正式分析時取得最新新聞、事件、產業與財報資訊。
- AI-input：GitHub 已驗證資料送入 ChatGPT 的標準入口。
- ChatGPT：負責完整分析、計算、情境、交易計畫與正式報告。

**正常 Production 流程禁止依賴 OpenAI API、`OPENAI_API_KEY` 或 `OPENAI_MODEL`。**

---

# 2. GITHUB ACTIONS ROLE — L1

GitHub Actions 僅負責：

```text
Data Acquisition
→ Validation
→ Immutable Snapshot
→ Canonical Package
→ AI-input
→ Commit / Push
```

不得在 GitHub Actions 中直接執行 OpenAI API 分析。

Production repository：

`grichtoyang/cloudflare-github-test`

Branch：`main`

正常排程：

`08:00 Asia/Taipei`（GitHub Actions cron：`0 0 * * 1-5`）

08:00 是流程啟動時間，不代表資料一定於 08:00:00 已完成。ChatGPT 正式分析前必須重新確認 AI-input Ready Gate。

---

# 3. DATE BASELINE — MANDATORY

GitHub Actions 每次執行必須先建立：

- Analysis Date：台灣當日曆日
- T0：Analysis Date 前最近一個已完成交易日
- T-1：T0 前最近一個已完成交易日

不得直接以 runner UTC 日期取代 Taiwan Analysis Date。

所有資料均必須帶有日期與來源識別，避免 Analysis Date、T0、T-1 混用。

---

# 4. TAIFEX PRODUCTION GATEWAY — LOCKED

Production Base URL 固定：

`https://taifex.grichtoyang.workers.dev/`

GitHub TAIFEX collector 必須以此 Production Gateway 為 Primary。

TAIFEX 所有資料必須依下列四項一致性驗證：

1. Date
2. Instrument / Contract
3. Session
4. Definition

並另外驗證：

- Completeness
- Provenance
- Data Quality
- HTTP / JSON validity
- `ready_for_analysis`

### 4.1 Date-required endpoints

以下 endpoint 必須使用 `?date=T0`：

- `/futures-institutional-oi`
- `/futures-institutional-oi-history`
- `/futures-options-chain`
- `/options-delta`
- `/options-key-levels`
- `/options-gamma-levels`
- `/options-market-structure`
- `/options-market-structure-compact`

### 4.2 Night-session endpoints

以下夜盤 endpoint 不任意附加 `?date=`：

- `/futures-price-after-hours`
- `/futures-institutional-after-hours`
- `/options-institutional-after-hours`
- `/options-after-hours`

夜盤日期規則：

```text
Night Session Trade Date = T0
Night Session Query Date = Analysis Date
```

完整夜盤窗口：

```text
T0 15:00 → Analysis Date 05:00
```

### 4.3 TAIFEX fallback

Primary Proxy 失效時，依序啟用合理 fallback：

1. TAIFEX 官方 OpenAPI：`https://openapi.taifex.com.tw/`
2. 其他官方 TAIFEX 資料路徑
3. 可靠第二來源
4. 自行計算／交叉驗證（僅在定義允許時）

Fallback 必須留下 provenance / audit information。

不得因 Primary Proxy 暫時失效而直接把資料標示為不存在。

---

# 5. TWSE — L1 DATA ACQUISITION

TWSE 為台灣現貨市場官方資料來源。

Production Proxy：

`https://twse-proxy.grichtoyang.workers.dev`

GitHub Actions 必須取得 T0 所對應的完整必要 TAIEX / market data，並驗證：

- Date
- Instrument
- Session
- Definition
- Completeness
- Provenance
- Data Quality

不得使用舊版或已停用的 `taiex-proxy.grichtoyang.workers.dev` 作為 Production TWSE collector。

---

# 6. IMMUTABLE SNAPSHOT — SOURCE OF TRUTH

原始資料必須保留為 immutable snapshots。

AI-input 不得取代 source of truth。

Production 結構：

```text
data/
├── snapshots/<T0>/
│   ├── snapshot.json
│   └── twse-snapshot.json
│
└── premarket/<Analysis Date>/
    ├── <Analysis Date>.json
    └── ai-input/
        ├── index.json
        ├── taifex-*.json
        └── twse.json
```

Canonical package：

`data/premarket/<analysis_date>.json`

AI-input：

`data/premarket/<analysis_date>/ai-input/`

AI-input index：

`data/premarket/<analysis_date>/ai-input/index.json`

所有重要 artifact 必須保留 SHA256。

---

# 7. CANONICAL PACKAGE

Canonical package 必須由已驗證的 TAIFEX / TWSE source manifests 建立。

必須包含並驗證：

- `analysis_date`
- `t0_trading_date`
- source manifests
- published snapshot references
- snapshot SHA256
- validation result
- `ready_for_analysis`
- `published`

只有完整通過 source validation 的 package 才可：

```text
ready_for_analysis = true
published = true
```

失敗資料不得覆蓋既有有效 immutable package。

---

# 8. AI-INPUT PACKAGE

`build_premarket_ai_inputs.py` 只可從已驗證 canonical package 建立 AI-input。

不得自行抓取未驗證資料。

每一個 TAIFEX endpoint 使用獨立 JSON 檔，避免大型 Options Chain 因 connector / transport 限制而無法讀取。

TWSE 使用 connector-friendly JSON。

Index 必須記錄：

- Analysis Date
- T0
- canonical package path
- canonical package SHA256
- source snapshot paths
- 每個 AI-input 檔案 path
- bytes
- SHA256
- source / endpoint
- creation timestamp

---

# 9. READY_FOR_ANALYSIS GATE

ChatGPT 正式分析前，必須確認至少：

1. Analysis Date 正確。
2. T0 正確。
3. T-1 可正確取得。
4. TAIFEX snapshot 存在且可讀。
5. TWSE snapshot 存在且可讀。
6. canonical package `ready_for_analysis=true`。
7. canonical package `published=true`。
8. AI-input index 存在。
9. AI-input SHA256 驗證通過。
10. TAIFEX / TWSE source identity 正確。
11. Date / Instrument / Contract / Session / Definition 通過。
12. Night Session Date Mapping 通過。
13. Chain / Delta 使用同一 T0。

任一必要條件 FAIL：

```text
不得直接判定資料不存在
→ 追查
→ fallback
→ 交叉驗證
→ 保留 Missing Data Investigation Log
→ 再進行最終判定
```

---

# 10. CHATGPT 的 WEB / NEWS 是獨立通道

GitHub Actions 不負責把所有全球資料塞入 GitHub。

ChatGPT 正式分析時，必須依完整分析規格使用 Web / News 補充 GitHub 尚未提供的資料。

### Web 至少涵蓋

- S&P 500
- Nasdaq
- Dow
- SOX
- VIX
- TSMC ADR
- Nikkei
- TOPIX
- KOSPI
- KOSDAQ
- Hang Seng
- Shanghai / Shenzhen
- BTC
- DXY
- USD/TWD
- USD/JPY（重要時）
- USD/KRW（重要時）
- U.S. 2Y / 10Y / 30Y
- U.S. 20Y（可靠時）
- WTI
- Brent（重要時）
- Gold

### News 至少涵蓋

- Fed
- 美國總體
- 地緣政治
- 中美
- 台灣
- AI
- 半導體
- 台積電
- 美股科技
- 原油
- 財報／重大事件

Web / News 取得資料後，同樣必須驗證 Date / Definition / Source / Relevance，不得把未驗證內容直接當作事實。

---

# 11. FAILURE ISOLATION

任何單一 endpoint、Proxy、網站或資料來源失效，不得直接中止整份盤前分析。

處理原則：

```text
自行追查
→ 自行換路
→ 自行計算
→ 自行交叉驗證
→ 自行修正
→ 繼續完成
→ 最終驗收
```

只有所有合理路徑均耗盡後，才可使用：

- `ESTIMATED`
- `DATA_MISSING`
- `UNRESOLVED`
- `FAILED`

缺失資料不得刪除 Mandatory Section。

`Report Status = COMPLETED` 不等於 `Data Coverage = 100%`，也不等於 `Zero-Defect Status = PASS`。

---

# 12. OPTIONS DATA RESPONSIBILITY

GitHub L1 的責任是保存完整、可驗證的 TAIFEX Options 原始資料。

至少必須保存：

- Options Chain
- Delta
- Key Levels
- Gamma Levels
- Market Structure
- Compact Market Structure
- Options Institutional
- Options Institutional After-Hours
- Options After-Hours

GitHub 不在 L1 重複建立另一套分析結果。

ChatGPT L3 才是統一 Calculation Orchestration Owner，負責：

- Strike Universe Audit
- Common Universe
- OI Migration
- Call Wall
- Put Wall
- Gamma Wall
- Gamma Flip
- Max Pain
- GEX
- Key Level Migration

Proxy-derived GEX / Gamma Wall / Gamma Flip 必須標示為 TAIFEX-derived / Proxy-derived model output，不得冒充 TAIFEX 官方公布 GEX 欄位。

---

# 13. INSTITUTIONAL / FUTURES DATA

GitHub L1 必須保存足以支援後續分析的：

- TX Futures Price
- TX Futures Institutional Flow
- TX Futures Institutional OI
- TX Futures Institutional OI History
- Night-session futures data
- Options institutional data
- Night-session options institutional data

不得在 L1 將：

- Volume 當成 OI
- OI 當成 OI Change
- 無法證實的開倉／平倉意圖當成事實

這些判讀由 ChatGPT L2～L5 完成。

---

# 14. HISTORICAL DATA

GitHub historical snapshots 與正式歷史 Markdown 報告分離。

GitHub Actions 不得覆寫歷史原始資料。

正式盤前分析時，ChatGPT 必須另外搜尋專案檔案庫最近五份有效交易日正式盤前報告，進行歷史比較與前次判斷驗證。

當日報告不得納入自己的歷史比較。

五份不足時使用實際存在數量，並揭露：

`Historical Comparison Dataset = N reports available`

---

# 15. GITHUB ACTIONS PRODUCTION FLOW

Production workflow 必須遵守以下順序：

```text
08:00 Asia/Taipei
      ↓
Resolve Analysis Date
      ↓
Resolve T0
      ↓
Build TAIFEX Snapshot
      ↓
Build TWSE Snapshot
      ↓
Validate Source Manifests
      ↓
Build Canonical Pre-Market Package
      ↓
Build ChatGPT-readable AI-input
      ↓
Validate AI-input Integrity
      ↓
READY_FOR_ANALYSIS
      ↓
Commit / Push GitHub
```

**READY_FOR_ANALYSIS 必須先於 Commit / Push。任何未通過 Ready Gate 的 artifact 不得被 commit / push。**

GitHub Actions 完成後，不產生 OpenAI API 報告。

ChatGPT 之後以：

```text
GitHub AI-input
+
Web
+
News
```

執行完整分析。

---

# 16. PRODUCTION SAFETY RULES

### 禁止

- 使用舊 TAIFEX Proxy URL。
- 使用舊 TWSE Proxy URL。
- 把 Analysis Date 當成所有資料的交易日期。
- 把 T0 與 Analysis Date 混用。
- 任意替夜盤 endpoint 加 `?date=`。
- 以空資料代表「市場沒有資料」。
- 以 Volume 代替 OI。
- 以 OI 代替 OI Change。
- 將推論寫成已證實事實。
- 因單一資料來源失敗而停止整份分析。
- 使用 OpenAI API 作為 Production 必要條件。
- 用 AI-input 取代 immutable source snapshots。

### 必須

- 保留 provenance。
- 保留 SHA256。
- 保留 immutable source snapshots。
- 使用 Ready Gate。
- 使用 fallback。
- 保留 failure / missing-data audit。
- 維持 GitHub / Web / News 三通道責任分離。
- 維持 L1 與 ChatGPT L2～L5 責任分離。

---

# 17. FINAL RESPONSIBILITY MATRIX

| Layer | Responsibility |
|---|---|
| GitHub Actions L1 | Data Acquisition / Validation / Snapshot / Package / AI-input |
| GitHub | TAIFEX / TWSE structured source data storage |
| Web | ChatGPT 正式分析時取得全球市場、Rates、FX、Commodities、Macro 等 |
| News | ChatGPT 正式分析時取得最新新聞、事件、產業、財報 |
| ChatGPT L2 | Data Validation |
| ChatGPT L3 | Calculation / Derived Data |
| ChatGPT L4 | Analysis Engine |
| ChatGPT L5 | Decision / Trading Plan / Final Report |

**唯一正式資料流：**

```text
GitHub Actions
→ GitHub AI-input
→ ChatGPT
→ Web + News 補足
→ L2 Validation
→ L3 Calculation
→ L4 Analysis
→ L5 Decision / Report
```

---

# 18. ACCEPTANCE CRITERIA

本 GitHub Actions V1.0 達成 Production Ready 的必要條件：

1. 08:00 Asia/Taipei 能正常啟動。
2. Analysis Date / T0 / T-1 正確。
3. TAIFEX Production Proxy 正確。
4. TAIFEX fallback 可用於合理失效情境。
5. TWSE Production Proxy 正確。
6. TAIFEX / TWSE snapshots 可驗證且不可被 AI-input 取代。
7. canonical package 可驗證。
8. AI-input 可驗證。
9. SHA256 完整。
10. Chain / Delta 日期一致。
11. 夜盤日期映射正確。
12. GitHub commit / push 正常。
13. 無 OpenAI API Production dependency。
14. GitHub / Web / News 三通道責任沒有混淆。
15. ChatGPT 可以在 Ready Gate 後接續完整盤前分析。

**本文件只規範 GitHub Actions L1；完整盤前分析的分析、計算、決策與報告規格，仍以目前正式核准的 V1.1 分析規格為上位規範，但本文件不以其檔名作為任何 Production dependency。**