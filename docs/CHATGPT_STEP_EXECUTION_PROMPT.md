# CHATGPT_STEP_EXECUTION_PROMPT.md

# 每日盤前分析：ChatGPT STEP 執行提示詞

## 1. 執行總則

1. 必須依序執行所有 Gate、Stage、分析模組、報告產出及最終驗證。
2. 一旦開始執行，不得因任何單一資料缺失、日期欄位缺失、來源欄位缺失、API 錯誤或驗證失敗而提前停止。
3. 任何失敗都必須先執行全域 Retry／Fallback；完成後仍失敗，才記錄錯誤並繼續後續流程。
4. 最終必須產出 Markdown 分析報告；若資料不足，報告仍須產出，並清楚標示缺失項目與影響範圍。
5. ChatGPT 必須忠實使用 GitHub／GitHub Actions 提供的資料，不得自行捏造資料。
6. **所有 GitHub 文件、程式碼、資料包、JSON、CSV、報告及其他 repository 內容，均必須優先透過 GitHub API 讀取；不得把一般頁面顯示、工具包裝層的空值或截斷內容直接視為檔案實際內容。**

## 2. 日期與交易日規則

1. ChatGPT 不負責判定台灣是否為交易日。
2. ChatGPT 不負責判定資料是否為最新、上一交易日或合法交易時段資料。
3. ChatGPT 不得因 `runtime_date`、`market_date`、`data_date` 或資料截止時間缺失而阻擋流程。
4. ChatGPT 不得自行建立或套用 `OLD_DATE`、`VALID_TRADING_DAY`、`VALID_NON_TRADING_DAY`、`VALID_LATEST_AVAILABLE`、`VALID_PREVIOUS_SESSION` 或其他日期阻擋狀態。
5. 若上游資料有提供日期、時間、交易日或資料狀態，直接引用原值。
6. 若上游沒有提供上述欄位，僅記錄「上游未提供」，不得自行推論或判定錯誤。

## 3. Gate 0：資料與環境可用性

### 3.1 Gate 0 只檢查

- 必要 Prompt／規則文件是否成功讀取
- GitHub／資料來源是否可以存取
- 必要資料包是否存在
- 資料是否能被解析
- JSON、CSV 或其他格式是否有效
- 後續分析所需的必要欄位是否存在
- Retry／Fallback 是否已依規則執行
- **GitHub API 回傳的 HTTP 狀態、檔案 metadata、檔案大小、SHA、encoding 與實際內容是否一致**

### 3.2 GitHub API 讀取規則

1. 所有 repository 內容必須使用 GitHub API 讀取，優先使用 GitHub Contents API。
2. 讀取時必須記錄至少：repository、branch／ref、path、HTTP 狀態、檔案大小、SHA、encoding 及讀取時間。
3. Contents API 回傳內容若為空、截斷、格式異常或與檔案 metadata 不符，不得直接判定檔案空白或資料缺失。
4. 發生上述情況時，必須依序使用 Git Blob API 或 Raw GitHub URL 交叉驗證；必要時再使用其他已核准的 GitHub API fallback。
5. 至少完成一次交叉驗證，並確認 JSON／CSV／文字內容可解析後，才可判定檔案是否真的空白、損壞或缺失。
6. **「GitHub 工具回傳空值」不得直接等同於「GitHub 檔案內容為空」。**
7. 若 API 讀取失敗，必須記錄為 `github_read_failed`；若第二讀取方式成功，記錄實際成功方式，不得把前一次讀取異常列為資料缺失。
8. 只有在 GitHub API、Blob／Raw 交叉驗證及既定 fallback 均失敗後，才可將檔案標記為 `missing` 或 `unavailable`。

### 3.3 NOTICE.md 讀取規則

1. `NOTICE.md` 的標準路徑為 repository 根目錄：`NOTICE.md`。
2. 執行開始時，必須先嘗試透過 GitHub API 讀取根目錄 `NOTICE.md`。
3. 若根目錄沒有 `NOTICE.md`，不得直接將整個流程標記為 `BLOCKED`；必須記錄 `notice_missing`，並繼續執行後續流程。
4. 若讀取回傳 HTTP 404，必須確認根目錄與 `docs/NOTICE.md` 是否存在；若兩者皆不存在，記錄「NOTICE.md 未部署」，不得反覆重試造成流程停滯。
5. 若 `NOTICE.md` 存在但讀取失敗，依全域 Retry／Fallback 規則處理；完成後仍失敗時，記錄 `notice_read_failed`，但不得阻擋報告產出。
6. `NOTICE.md` 僅屬於執行注意事項文件，不是市場資料必要輸入；其缺失不得阻擋 Gate 0、Stage 2 或最終 Markdown 報告。
7. 只有在實際成功讀取 `NOTICE.md` 後，才可在報告中列為 `READ_SUCCESS`；不可將預期存在、檔名出現於 Prompt 或 HTTP 404 說成已讀取成功。

### 3.4 Gate 0 禁止檢查並阻擋的項目

以下項目不得作為 Gate 0 的 BLOCKED 條件：

- `runtime_date` 是否存在
- `market_date` 是否存在
- `data_date` 是否存在
- 執行日期是否等於資料日期
- 資料是否為當日或上一交易日
- 是否為台灣交易日
- 是否已開盤、收盤或休市
- 日盤／夜盤涵蓋狀態
- 資料截止時間是否存在
- 資料品質欄位是否存在
- 錯誤及 Fallback 紀錄欄位是否存在
- `NOTICE.md` 是否存在或是否成功讀取

### 3.5 Gate 0 結果

- 若資料可讀取且具備分析所需輸入：`PASS`
- 若部分資料缺失但仍可進行部分分析：`PASS_WITH_MISSING_DATA`
- 只有在必要資料完全無法取得、無法解析，且 Retry／Fallback 均完成後，才可標記：`BLOCKED`
- 即使標記 `BLOCKED`，仍不得停止；必須繼續執行錯誤報告、可用資料分析、Markdown 報告及最終驗證。

## 4. 全域 Retry／Fallback

全域 Retry／Fallback 適用於：

- GitHub 文件
- GitHub 程式碼
- GitHub 資料包
- TAIFEX API／Proxy
- TWSE API／Proxy
- 外部資料來源
- JSON／CSV 解析
- 資料欄位驗證
- 分析計算
- Markdown 報告產出
- Dashboard 產出
- GitHub 寫入
- 寫入後讀回驗證

每次失敗必須：

1. 記錄失敗原因
2. 依既定次數重試
3. 改用既定 Fallback
4. 再次驗證結果
5. 將最終結果記錄於報告
6. 繼續後續流程，不得無故中止

## 5. 分析執行要求

在 Gate 0 完成後，依序執行：

1. 台股大盤現貨籌碼分析
2. 台指期價格與三大法人未平倉分析
3. 選擇權籌碼與關鍵位分析
4. 美股、利率、美元、亞股及總體環境分析
5. 重大新聞與產業消息分析
6. 台股／台指期盤前綜合判斷
7. 支撐、壓力、情境與風險控管
8. Dashboard／摘要資料整理
9. Markdown 報告產出
10. 最終完整性驗證

## 6. 缺失資料處理

1. 缺失資料必須逐項列出。
2. 必須說明缺失資料對分析的影響。
3. 不得用猜測值補足缺失資料。
4. 不得因單一模組缺失而阻擋其他可執行模組。
5. 報告必須明確區分：實際資料、計算結果、推論、風險與缺失項目。

## 7. 最終交付條件

執行不得在 Gate 0、Retry、Fallback、資料驗證或單一分析模組失敗時提前結束。

最終交付至少包含：

- 執行狀態
- 資料來源與實際取得結果
- 各模組分析結果
- 缺失資料與錯誤紀錄
- 台股／台指期綜合判斷
- 關鍵支撐壓力位
- 交易情境與風險控管
- Markdown 完整報告
- 最終驗證結果

**核心原則：GitHub／GitHub Actions 負責資料日期與上游資料流程；ChatGPT 負責透過 GitHub API 讀取、分析、記錄並完成報告。ChatGPT 不得自行判日期，也不得因日期欄位缺失或 NOTICE.md 缺失而阻擋整個執行流程。**