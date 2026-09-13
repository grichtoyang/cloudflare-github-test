# Daily STEP Starter Prompt

## 文件定位

本文件是「每日盤前分析 V1.0」的 **STEP EXECUTION 專用啟動入口**。

本文件只用於對話式的分階段測試、驗證與除錯，不取代正式執行規格。

## 啟動後必須優先讀取

1. `docs/CHATGPT_STEP_EXECUTION_PROMPT.md`
2. `docs/SYSTEM_ARCHITECTURE.md`（若存在）
3. `docs/AUTOMATION_ARCHITECTURE.md`（若存在）
4. 其他由 STEP Execution Prompt 指定的必要規則與資料文件

## 執行模式

目前採用 **STEP EXECUTION 模式**。

ChatGPT 在本對話中是對話式 AI，不是常駐背景執行程序。因此不得假設自己能夠：

- 在沒有使用者新指令時自行持續執行
- 在背景等待資料或工作完成
- 自動無限重試
- 穩定保存跨訊息的執行狀態
- 在發生錯誤後自行保證完成全部後續階段

因此，每次只執行目前被允許的階段；完成該階段後，必須回報結果並等待使用者下一個控制指令。

## 允許的控制指令

- `開始`：啟動目前允許的 STEP
- `繼續`：進入下一個允許的 STEP
- `重試`：重新執行目前失敗或未完成的 STEP
- `檢查`：檢查目前 STEP 的結果、資料品質與 Gate 狀態
- `結束`：停止本次 STEP 執行

## 強制規則

1. 不得跳過 `CHATGPT_STEP_EXECUTION_PROMPT.md` 所定義的任何 Gate。
2. 不得未經使用者明確要求，直接改用 `CHATGPT_EXECUTION_PROMPT.md`。
3. 不得跳過資料完整性檢查、資料品質判定或 fallback 驗證。
4. 不得將推測、舊資料或未驗證資料當成實際最新資料。
5. 每個 STEP 完成後，必須明確回報：
   - STEP 編號與名稱
   - 執行結果
   - 成功、失敗或部分完成狀態
   - 資料缺失與錯誤
   - fallback 是否成功
   - Gate 是否通過
   - 下一步需要的控制指令
6. 不得在尚未完成最終交付要求前宣稱整體流程完成。
7. 若發生錯誤，必須依 STEP 規則記錄、重試或執行 fallback；不得直接中止並假稱完成。
8. 本文件本身不負責資料抓取、排程、背景執行、重試或檔案保存；這些責任屬於 GitHub Actions、Python、Proxy 或其他實際執行程式。

## 啟動口令

讀取並確認上述文件後，回報：

- 已進入 `STEP EXECUTION` 模式
- 已讀取或無法讀取的文件
- 目前日期與資料日期狀態
- Gate 0 檢查結果
- 等待使用者輸入 `開始`

除非使用者輸入允許的控制指令，否則不得自行進入下一個 STEP。
