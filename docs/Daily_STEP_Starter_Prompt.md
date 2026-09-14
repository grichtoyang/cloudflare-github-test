# 每日盤前分析 V1.0
# Daily STEP Starter Prompt

## 1. 文件定位

本文件是「每日盤前分析 V1.0」的 **STEP EXECUTION 啟動入口**。

本文件只負責：

- 指定正式執行規格與必要文件的讀取順序
- 指定 GitHub Repository 來源
- 要求完成 Gate 0 前置條件確認
- 定義啟動時的控制指令與回報方式

本文件**不是完整的 STEP EXECUTION 執行規格**，不取代：

- `docs/CHATGPT_STEP_EXECUTION_PROMPT.md`
- `docs/SYSTEM_ARCHITECTURE.md`
- `docs/AUTOMATION_ARCHITECTURE.md`
- 其他由正式 STEP Execution Prompt 指定的必要文件

---

## 2. 指定 GitHub Repository

目前指定的 GitHub Repository：

- **Repository URL**  
  `https://github.com/grichtoyang/cloudflare-github-test`
- **Repository owner**  
  `grichtoyang`
- **Repository name**  
  `cloudflare-github-test`

執行時必須以此 Repository 作為優先讀取來源。

正式讀取前，仍必須確認：

- branch／ref
- 必要文件 path
- 必要資料文件 path
- 實際回傳內容
- 文件及資料完整性

不得自行猜測或使用未確認的 Repository、branch、ref 或 path。

---

## 3. 啟動時必須讀取的文件

啟動後，必須依下列順序讀取：

### 3.1 正式 STEP Execution 規格

```text
docs/CHATGPT_STEP_EXECUTION_PROMPT.md
```

### 3.2 系統架構文件

```text
docs/SYSTEM_ARCHITECTURE.md
```

若檔案存在，必須讀取並驗證。

### 3.3 自動化架構文件

```text
docs/AUTOMATION_ARCHITECTURE.md
```

若檔案存在，必須讀取並驗證。

### 3.4 其他必要文件與資料

依正式 `CHATGPT_STEP_EXECUTION_PROMPT.md` 的要求，讀取所有必要：

- 架構文件
- 程式碼文件
- 設定文件
- JSON／CSV／Markdown 資料文件
- 資料包
- API／Proxy 相關文件
- 其他必要輸入

---

## 4. Gate 0 前置條件

在完成 Gate 0 前，必須先取得並確認：

1. 必要架構文件的位置
2. 必要資料文件的位置
3. GitHub Repository 位置
4. Repository owner／name
5. branch／ref
6. 每一份必要文件及資料的 path

本文件已指定 Repository：

```text
https://github.com/grichtoyang/cloudflare-github-test
```

但若必要文件的 path、branch／ref 或資料文件位置仍無法確認，則不得宣稱已完成 Gate 0。

### 4.1 位置資訊不足時

若任何必要位置資訊：

- 尚未提供
- 無法確認
- 不完整
- 與實際 Repository 結構不一致

則必須：

- 將 Gate 0 標示為 `BLOCKED` 或 `INSUFFICIENT_DATA`
- 列出缺少或無法確認的具體項目
- 等待使用者補充或確認
- 取得完整資訊後，才可繼續 Gate 0

不得自行猜測、補寫或假設文件位置。

---

## 5. GitHub 讀取要求

所有 GitHub Repository、文件、程式碼及資料讀取，必須依正式 STEP Execution Prompt 的規則執行。

至少必須確認：

- Repository
- branch／ref
- path
- HTTP／API status
- 實際內容
- SHA（若 API 提供）
- encoding
- 格式
- 內容完整性
- 可解析性

若發生連線錯誤、timeout、HTTP／API 錯誤、空值、截斷、格式異常或解析失敗，必須依正式規格執行 Retry／Fallback。

不得只因取得：

- 檔名
- URL
- SHA
- metadata
- 部分內容

就判定為完整讀取成功。

---

## 6. 執行模式與控制指令

本專案採用 **STEP EXECUTION 模式**。

允許的控制指令：

- `開始`：執行目前允許的 STEP
- `繼續`：進入下一個允許的 STEP
- `重試`：重新執行目前失敗或未完成的 STEP
- `檢查`：檢查目前 STEP、資料品質及 Gate 狀態
- `結束`：停止本次執行

除非使用者輸入允許的控制指令，否則不得自行進入下一個 STEP。

---

## 7. 啟動後的必要回報

啟動後，必須回報：

1. 是否已進入 `STEP EXECUTION` 模式
2. 指定 GitHub Repository
3. 實際確認的 branch／ref
4. 已讀取的文件
5. 尚未讀取、缺失或無法確認的文件
6. 必要架構文件、資料文件及 path 的確認結果
7. GitHub API／Retry／Fallback 狀態
8. Gate 0 結果：
   - `PASS`
   - `PASS_WITH_MISSING_DATA`
   - `BLOCKED`
   - `FAIL`
   - `INSUFFICIENT_DATA`
9. 目前允許執行的 STEP
10. 等待使用者輸入 `開始`

---

## 8. 強制停止條件

符合以下任一情況時，不得進入後續 STEP：

- 正式 STEP Execution Prompt 無法取得
- 必要架構文件無法取得或無法確認
- 必要資料文件位置不明
- Repository、branch／ref 或 path 無法確認
- GitHub 讀取尚未完成必要 Retry／Fallback
- 內容完整性或格式驗證未通過
- Gate 0 尚未通過

此時必須清楚回報阻塞原因，不得假稱流程完成。
