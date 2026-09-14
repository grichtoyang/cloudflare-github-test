# Daily STEP Starter Prompt

## 1. Project Information

- Repository: `grichtoyang/cloudflare-github-test`
- Branch: `main`
- STEP execution prompt（GitHub API）:
  `https://api.github.com/repos/grichtoyang/cloudflare-github-test/contents/docs/CHATGPT_STEP_EXECUTION_PROMPT.md?ref=main`
- This starter prompt（GitHub API）:
  `https://api.github.com/repos/grichtoyang/cloudflare-github-test/contents/docs/Daily_STEP_Starter_Prompt.md?ref=main`

## 2. Execution Objective

本文件是「每日盤前分析 V1.0」的啟動入口。

收到本 Prompt 後，ChatGPT 必須：

1. 先讀取並理解 `CHATGPT_STEP_EXECUTION_PROMPT.md`。
2. 再依照該執行規則，逐步執行每日盤前分析流程。
3. 不得跳過 Gate 0。
4. 不得因中途錯誤而直接停止。
5. 無論中間發生什麼錯誤，都必須持續執行到產出最終 Markdown 分析報告，或明確產出「無法完成報告」的錯誤報告後，才可以結束。

## 3. Source Priority

請依下列順序尋找必要文件：

### Priority 1 — 本次對話附件

優先讀取本次對話中實際上傳的檔案。

### Priority 2 — GitHub Repository（必須使用 GitHub API）

若附件不存在，改由 GitHub REST API 讀取下列 Repository：

- Owner: `grichtoyang`
- Repository: `cloudflare-github-test`
- Branch: `main`

GitHub API 根網址：

`https://api.github.com`

Repository Contents API 格式：

`https://api.github.com/repos/grichtoyang/cloudflare-github-test/contents/{path}?ref=main`

主要文件的 API 讀取位置：

- `https://api.github.com/repos/grichtoyang/cloudflare-github-test/contents/docs/CHATGPT_STEP_EXECUTION_PROMPT.md?ref=main`
- `https://api.github.com/repos/grichtoyang/cloudflare-github-test/contents/docs/ANALYSIS_RULES.md?ref=main`
- `https://api.github.com/repos/grichtoyang/cloudflare-github-test/contents/docs/DATA_SOURCES.md?ref=main`
- `https://api.github.com/repos/grichtoyang/cloudflare-github-test/contents/docs/NOTICE.md?ref=main`
- 其他由 STEP 執行 Prompt 指定的必要文件，均須依相同 API 格式讀取。

#### GitHub API 讀取規則

1. 不得使用 GitHub 網頁版 `github.com/.../blob/...` 頁面作為檔案讀取方式。
2. 必須使用 GitHub REST API 的 Repository Contents endpoint 取得檔案內容。
3. API 回傳的 `content` 欄位通常為 Base64 編碼，必須先 Base64 解碼後，才能讀取文字檔案。
4. 必須確認 API 回傳的 `type` 為 `file`，並檢查 HTTP 狀態碼及回傳內容。
5. 若檔案位於子目錄，必須使用完整的 repository-relative path。
6. 若需要列出目錄內容，使用：
   `https://api.github.com/repos/grichtoyang/cloudflare-github-test/contents/{directory}?ref=main`
7. API 回傳 404 且明確表示資源不存在時，才可標示 `MISSING`；其他連線、權限、限流、格式或解析問題，必須標示 `READ_FAILED` 或 `BLOCKED`。
8. GitHub API 讀取失敗時，必須依本 Prompt 的 fallback 與錯誤處理規則繼續執行，不得直接停止。
9. 每次讀取 GitHub 文件時，必須記錄 API endpoint、Repository、Branch、File path、HTTP 狀態、讀取狀態，以及是否成功解碼與解析。

### Priority 3 — 明確錯誤狀態

若文件無法取得，必須明確標示狀態，不得假設文件內容不存在。

允許的狀態：

- `READ_SUCCESS`：成功讀取
- `MISSING`：確認不存在
- `READ_FAILED`：讀取失敗
- `BLOCKED`：存取被阻擋
- `PARTIAL`：僅取得部分內容

## 4. Important Distinction

不得將以下兩種情況混為一談：

1. 本次對話沒有附件。
2. GitHub Repository 中沒有該文件。

正確流程：

- 先確認附件是否存在。
- 若附件不存在，才查詢 GitHub。
- 若 GitHub 讀取失敗，只能標示 `READ_FAILED` 或 `BLOCKED`。
- 不得直接推論為 `MISSING`。

## 5. STEP Execution Mode

本專案採用嚴格 STEP 模式。

### Allowed commands

- `開始`：從 STEP 0 開始
- `繼續`：繼續下一個尚未完成的 STEP
- `重試`：重試目前失敗的 STEP
- `檢查`：檢查目前執行狀態
- `結束`：只有在最終報告或最終錯誤報告產出後才能結束

### Execution requirements

- 每次只執行目前允許的 STEP。
- 不得自行跳到後續 STEP。
- 每個 STEP 完成後，必須回報：
  - STEP 編號
  - STEP 名稱
  - 執行結果
  - 資料來源
  - 缺漏與錯誤
  - 下一步
- 若遇到錯誤，先記錄錯誤，再依規則進行 fallback、重試或繼續。
- 不得因單一資料源失敗而停止整個流程。

## 6. Gate 0

開始執行任何分析前，必須完成 Gate 0：

1. 讀取 `CHATGPT_STEP_EXECUTION_PROMPT.md`。
2. 讀取所有目前可取得的必要規則文件。
3. 確認資料來源與 fallback 順序。
4. 確認執行日期與市場交易日期。
5. 確認本次執行模式為 STEP 模式。
6. 回報 Gate 0 結果。

若 Gate 0 尚未完成，不得直接進入後續分析。

## 7. Startup Response

收到本文件後，若使用者尚未輸入 `開始`，請先回覆：

> 已載入 Daily STEP Starter Prompt。
>
> 請輸入「開始」，以依照 `CHATGPT_STEP_EXECUTION_PROMPT.md` 的規則執行 Gate 0 與後續 STEP 流程。

收到 `開始` 後，才正式執行。

## 8. Finalization Rule

本流程不可在中途因錯誤、資料缺漏、來源無法連線或單一模組失敗而直接停止。

最終必須產出以下其中一項：

1. 完整的每日盤前分析 Markdown 報告。
2. 明確列出已完成項目、失敗項目、資料缺漏、錯誤原因與限制的 Markdown 錯誤報告。

只有在上述報告產出後，流程才算結束。
