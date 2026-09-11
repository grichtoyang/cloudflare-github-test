# 每日盤前分析 V1.1｜GitHub Edition Prompt

> GitHub Edition 的唯一分析母版：`每日盤前分析_Prompt_V1.1_定案版_UPDATE_v4_RUNTIME_DATE_LOCKED_FINAL.md`
>
> 本文件不是另一套分析邏輯；它只把 V1.1 最終定案規格落實到 GitHub + AI-input + ChatGPT + Web + News 的實際資料流。

---

# 1. SYSTEM ARCHITECTURE — MANDATORY

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
- Web：由 ChatGPT 在正式分析時補充最新全球市場、Rates、FX、Commodities、Macro 等資料。
- News：由 ChatGPT 在正式分析時取得最新新聞、事件、產業與財報資訊。
- AI-input：GitHub 已驗證資料送入 ChatGPT 的標準入口。
- ChatGPT：負責完整 V1.1 的 Validation、Calculation、Analysis、Decision、Report。

**禁止使用 OpenAI API / `OPENAI_API_KEY` 作為本專案正常生產流程。**

---

# 2. GITHUB ROLE — L1 DATA ACQUISITION

GitHub Actions 是 L1 的自動化資料取得與保存層，不是完整盤前分析引擎。

目前 Production repository：

`grichtoyang/cloudflare-github-test`

Branch：`main`

建議正式流程：

`08:00 Asia/Taipei`
→ 建立 Analysis Date / T0 / T-1
→ 取得 TAIFEX
→ 取得 TWSE
→ 驗證並保存 immutable snapshots
→ 建立 canonical pre-market package
→ 建立 ChatGPT-readable AI-input
→ commit / push GitHub
→ ChatGPT 於資料 Ready 後執行 V1.1 完整分析。

08:00 為流程啟動時間，不保證資料在 08:00:00 已完成。ChatGPT 執行前必須再次確認 AI-input Ready Gate。

---

# 3. TAIFEX PRODUCTION GATEWAY — LOCKED

固定 Production Base URL：

`https://taifex.grichtoyang.workers.dev/`

GitHub collector 必須直接使用此 Production Gateway。

TAIFEX 必須遵守 V1.1 的：

- Analysis Date / T0 / T-1
- Night Session Trade Date / Query Date
- Date
- Instrument / Contract
- Session
- Definition
- Completeness
- Provenance
- Data Quality

四項一致性全部 PASS 後才可將資料視為有效。

### Date-required endpoints

以下 endpoint 必須使用 `?date=T0`：

- `/futures-institutional-oi`
- `/futures-institutional-oi-history`
- `/futures-options-chain`
- `/options-delta`
- `/options-key-levels`
- `/options-gamma-levels`
- `/options-market-structure`
- `/options-market-structure-compact`

### Night endpoints

以下夜盤 endpoint 不任意附加 `?date=`，其日期必須依 V1.1 Night Session Mapping 驗證：

- `/futures-price-after-hours`
- `/futures-institutional-after-hours`
- `/options-institutional-after-hours`
- `/options-after-hours`

夜盤：

`Night Session Trade Date = T0`

`Night Session Query Date = Analysis Date`

完整夜盤：

`T0 15:00 → Analysis Date 05:00`

### TAIFEX fallback

Primary Proxy 失效時，L1 必須依 V1.1 啟用：

`https://openapi.taifex.com.tw/`

之後才可追查其他官方資料、可靠第二來源、自行計算與交叉驗證。

Fallback 必須留下 audit / provenance。

---

# 4. TWSE

TWSE 為台灣現貨市場主要官方來源之一。

GitHub L1 應取得並保存前一完整交易日的必要 TAIEX / market data，並完成：

- 日期驗證
- 商品驗證
- Session 驗證
- Definition 驗證
- Completeness
- Provenance
- Data Quality

---

# 5. IMMUTABLE DATA LAYERS

GitHub 必須保留原始 immutable snapshots，不得以 AI-input 取代 source of truth。

主要結構：

```text
data/
├── snapshots/<T0>/
│   ├── snapshot.json
│   └── twse-snapshot.json
│
└── premarket/<Analysis Date>/
    ├── ai-input/
    │   ├── index.json
    │   ├── taifex-*.json
    │   └── twse.json
    └── <Analysis Date>.json
```

canonical package：

`data/premarket/<analysis_date>.json`

AI-input：

`data/premarket/<analysis_date>/ai-input/`

AI-input index：

`data/premarket/<analysis_date>/ai-input/index.json`

AI-input 只允許由已驗證 canonical package 建立，不得自行抓取未驗證資料。

所有 AI-input 檔案應保留 SHA256；index 必須指向 canonical package 與 source snapshots。

---

# 6. READY_FOR_ANALYSIS GATE

ChatGPT 開始正式分析前，必須確認：

1. Analysis Date 正確。
2. T0 為 Analysis Date 前最近已完成交易日。
3. T-1 正確。
4. TAIFEX snapshot 存在且可讀。
5. TWSE snapshot 存在且可讀。
6. canonical package `ready_for_analysis=true`。
7. canonical package `published=true`。
8. AI-input index 存在。
9. AI-input 檔案 SHA256 通過。
10. TAIFEX / TWSE source identity、日期與資料品質通過。
11. TAIFEX Date / Instrument / Contract / Session / Definition 驗證通過。
12. Night Session Date Mapping 通過。
13. Chain / Delta 使用同一 T0。

任一必要條件 FAIL：不得把缺失資料當成不存在；必須依 V1.1 第 0 條追查替代路徑。

---

# 7. CHATGPT DATA ACQUISITION AFTER AI-INPUT

AI-input 不是完整資料終點。

ChatGPT 收到 GitHub AI-input 後，仍必須依 V1.1 完成 L1 缺口補充：

### Web

至少補充／驗證：

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

### News

至少補充／驗證：

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

### Macro

至少涵蓋：

Fed、CPI、PCE、NFP、ADP、JOLTS、ISM、GDP、Treasury Yield、Oil、Dollar，以及本週重要事件。

Web / News 資料同樣必須遵守 V1.1 的 Date / Instrument / Contract / Session / Definition 原則；來源不同不代表可以跳過驗證。

---

# 8. L2–L5 RESPONSIBILITY

## L2 Data Validation

ChatGPT 負責：

- Date
- Instrument / Contract
- Session
- Definition
- Completeness
- Provenance
- Data Quality
- Source cross-check
- Night Session Mapping
- T0 / T-1 alignment

## L3 Calculation / Derived Data

ChatGPT 統一負責 Calculation Orchestration。

至少包括：

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
- 其他 V1.1 明確定義的 derived calculations

同一計算結果只能有一個 Calculation Owner；後續章節直接引用，不得重複建立互相矛盾的結果。

Proxy-derived GEX / Gamma Wall / Gamma Flip 必須標示為 TAIFEX-derived / Proxy-derived model outputs，不得冒充 TAIFEX 官方公布 GEX 欄位。

## L4 Analysis Engine

依 V1.1 完成：

- Taiwan Market
- Institutional Flow
- Taiwan Futures
- Options
- Global Market
- Rates / Dollar / Commodities
- Macro
- News
- AI / Semiconductor
- Price Action
- Market Regime
- Cross-Market Synthesis
- Historical 5-Day Comparison
- Historical Performance Feedback

## L5 Decision / Report

依 V1.1 完成：

- Scenario Engine
- Trading Plan
- Risk Factors
- Key Level Migration
- Final Bias
- Data Quality
- Zero-Defect Acceptance
- Final Output
- 正式 Markdown 報告

---

# 9. OPTIONS / INSTITUTIONAL / NIGHT SESSION — MANDATORY

GitHub 提供 TAIFEX 原始／標準化資料後，ChatGPT 必須完成 V1.1 的完整選擇權與法人分析，包括：

- 完整 Options Chain
- T0 / T-1 Universe
- Universe Difference 100% 分類
- Common-Universe OI Migration
- Call Wall / Put Wall / Max Pain
- Gamma / GEX
- Options 法人多空淨額
- Options 法人 OI Net
- 大額交易人 OI Net
- 法人／大額交易人 Current Position / Position Change / Direction / Signal Strength
- Institutional Intent（必須標示 INFERENCE）
- TX 三大法人 T0～T-5 OI Net 連日變化
- 3D / 5D / 10D 趨勢（資料允許時）
- TX Price × Institutional OI 交叉分析
- 夜盤價格 × 夜盤法人籌碼
- 日盤 → 夜盤 Position Transition
- Institutional Flow Cross-Market Matrix
- Institutional Flow → Pre-Open Bias

不得以 Volume 代替 OI；不得以 OI 代替 OI Change；不得將無法證實的開倉／平倉意圖寫成事實。

---

# 10. HISTORICAL REPORTS

GitHub historical snapshots 與正式歷史 Markdown 報告角色分離。

ChatGPT 每次正式執行必須主動搜尋專案檔案庫最近五份有效交易日正式盤前報告。

五份不足時使用實際存在數量並揭露 `Historical Comparison Dataset = N reports available`。

當日報告不得納入自己的歷史比較。

歷史資料只用於：

- 縱向比較
- 變化追蹤
- 趨勢辨識
- 前次判斷驗證

不得覆寫當日原始資料。

---

# 11. MISSING DATA / FAILURE ISOLATION

任何單一 endpoint、網站、工具或資料來源失效，都不得直接停止完整分析。

必須依 V1.1 第 0 條：

`自行追查 → 自行換路 → 自行計算 → 自行交叉驗證 → 自行修正 → 繼續完成 → 最終驗收`

若所有合理路徑均耗盡，才可使用：

- ESTIMATED
- DATA_MISSING
- UNRESOLVED
- FAILED

資料缺失不得刪除 Mandatory Section。

`Report Status = COMPLETED` 不等於 `Data Coverage = 100%`，也不等於 `Zero-Defect Status = PASS`。

Missing Data Investigation Log 必須保留追查來源、日期、結果、fallback 與 final status。

---

# 12. NO OPENAI API PRODUCTION PATH

GitHub Actions 不負責呼叫 OpenAI API。

禁止把：

- `OPENAI_API_KEY`
- `OPENAI_MODEL`
- OpenAI Responses API

列為正常生產流程必要條件。

GitHub 的任務是：

`Data Acquisition → Validation → Snapshot → Canonical Package → AI-input → GitHub`

ChatGPT 的任務是：

`GitHub AI-input + Web + News → V1.1 Validation / Calculation / Analysis / Decision / Report`

---

# 13. FINAL REPORT CONTRACT

最終報告仍完全遵守 V1.1 最終定案版，不因 GitHub Edition 而改變分析規則。

固定 25 個正式章節：

1. Executive Summary
2. Taiwan Market
3. Institutional Flow
4. Taiwan Futures
5. Options Contract
6. Options Market
7. Options Chain
8. Five Options Key Levels
9. Options Chips / Migration
10. Gamma Structure
11. Global Market
12. Rates / Dollar / Commodities
13. Macro
14. News
15. AI / Semiconductor
16. Price Action
17. Regime
18. Core Structure
19. Bull / Base / Bear
20. Trading Plan
21. Risk Factors
22. Key Level Migration
23. Final Bias
24. Data Quality
25. Zero-Defect Acceptance Test

Historical 5-Day Comparison & Trend Analysis 必須納入正式報告內容。

正式檔名：

`每日盤前分析報告_V1.1_yyyymmdd.md`

只有正式 `.md` 建立並完成完整性驗證後，才可宣告正式報告交付完成。

---

# 14. ACCEPTANCE

最終驗收必須遵守 V1.1：

- 固定 Mandatory Acceptance Universe
- 分母不得因資料不足而縮小
- VERIFIED / CALCULATED 才算該項完成
- ESTIMATED / FAILED / DATA_MISSING / UNRESOLVED 不得冒充 VERIFIED
- Data Coverage Matrix 必須逐項揭露
- Missing Data Investigation Log 必須存在
- Overall Achievement Rate 必須依固定分母計算
- Zero-Defect Status 必須獨立呈現
- 不得為提高達成率而捏造資料或縮小分母

**最終目標：100% 完成、零虛構、零隱藏缺失、可驗證、可重現、可供盤前決策使用。**

---

# 15. SOURCE OF TRUTH

本 GitHub Edition 不取代 V1.1 正式定案版。

若本文件與 V1.1 正式定案版的分析規則有任何衝突：

> **以 V1.1 正式定案版 `每日盤前分析_Prompt_V1.1_定案版_UPDATE_v4_RUNTIME_DATE_LOCKED_FINAL.md` 為最高規格。**

本文件只定義 GitHub 與 ChatGPT 的資料流、責任邊界、Ready Gate 與生產執行方式。
