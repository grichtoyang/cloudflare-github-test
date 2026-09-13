# 每日盤前分析 V1.0
## 資料自動化與 ChatGPT 分析自動化邊界修訂版

**版本狀態：定案規則**

---

## 1. 核心結論

本專案目前必須明確區分：

1. **資料自動化**
2. **ChatGPT 分析自動化**
3. **ChatGPT 寫回 GitHub**

目前 V1.0 的正確定位為：

> **資料自動化 + ChatGPT 人工啟動分析 + ChatGPT 嘗試自動寫回 GitHub 的半自動化系統。**

本系統目前不是完整無人值守自動化系統。

---

## 2. 資料自動化

資料自動化由 GitHub Actions 負責，包含：

- 依排程啟動，例如每日台灣時間 08:00。
- 抓取 TWSE、TAIFEX、Cloudflare Proxy 及其他資料來源。
- 執行資料標準化。
- 執行日期、格式、欄位、數值與完整性檢查。
- 執行官方 API、已驗證 Proxy、備援來源及歷史資料 Fallback。
- 建立每日資料包。
- 保存 Raw Data、Normalized Data、Data Package。
- 保存資料品質、錯誤、Fallback 及未完成項目。

### 重要限制

> GitHub Actions 完成資料抓取，不代表 ChatGPT 分析已完成。

---

## 3. ChatGPT 分析啟動方式

### 3.1 已確認結論

> **無 API Key 自動呼叫 ChatGPT 已證實不可行。**

因此：

- GitHub Actions 不得被描述為能在無 API Key 情況下自動啟動 ChatGPT。
- GitHub Actions 不得被描述為能自行完成 ChatGPT 盤前分析。
- 每日 ChatGPT 分析目前必須由使用者人工啟動。
- 任何流程圖、Prompt、Notice、Workflow 與驗收文件，都必須遵守此限制。

### 3.2 正確流程

```text
GitHub Actions 自動抓取資料
        ↓
資料標準化、品質檢查、Fallback
        ↓
建立並保存每日資料包
        ↓
使用者人工啟動 ChatGPT
        ↓
ChatGPT 讀取規格與每日資料包
        ↓
ChatGPT 執行盤前分析
        ↓
產出 Markdown 報告
        ↓
產出 Dashboard JSON
        ↓
嘗試寫回 GitHub
```

---

## 4. ChatGPT 寫回 GitHub

### 4.1 功能狀態

> **ChatGPT 自動寫回 GitHub 可以完成，但有可能失敗。**

因此應使用「嘗試寫回」或「可執行寫回」等精確描述，不得宣稱每次必定成功。

### 4.2 可能失敗原因

包括但不限於：

- GitHub 授權或權限問題。
- Repository、Branch 或檔案路徑錯誤。
- GitHub API 暫時性錯誤。
- Commit 或 Push 失敗。
- 網路或連線問題。
- 檔案內容或格式驗證失敗。
- ChatGPT 工具執行中斷。
- 寫入逾時或部分完成。

### 4.3 寫回成功時

應確認：

- Markdown 報告已成功保存。
- Dashboard JSON 已成功保存。
- 目標 Repository 正確。
- 目標 Branch 正確。
- 目標檔案路徑正確。
- Commit 或更新結果可確認。

只有在上述結果獲得確認後，才可標示：

```text
github_writeback_status: success
```

### 4.4 寫回失敗時

必須：

- 明確標示 GitHub 寫回失敗。
- 保留已產出的 Markdown 報告。
- 保留已產出的 Dashboard JSON 或 partial JSON。
- 記錄失敗原因。
- 記錄尚未寫回的檔案。
- 不得宣稱 GitHub 已成功更新。
- 不得因寫回失敗而抹除已完成的分析結果。

建議狀態：

```text
github_writeback_status: failed
```

或：

```text
github_writeback_status: partial
```

---

## 5. 系統狀態定義

| 狀態 | 定義 |
|---|---|
| `data_collection_completed` | 資料抓取、標準化及保存完成 |
| `data_collection_partial` | 部分資料完成，仍有缺失或 Fallback |
| `analysis_not_started` | 尚未人工啟動 ChatGPT |
| `analysis_completed` | ChatGPT 已完成分析與報告產出 |
| `github_writeback_success` | 報告與 Dashboard 已確認寫回 GitHub |
| `github_writeback_partial` | 部分檔案已寫回，部分失敗 |
| `github_writeback_failed` | 寫回 GitHub 失敗，但分析結果仍保留 |
| `completed_with_warnings` | 分析完成，但存在資料、Fallback 或寫回警告 |
| `partial` | 僅部分流程完成 |
| `failed_but_report_generated` | 流程有失敗，但仍產出報告 |

---

## 6. V1.0 功能狀態

| 功能 | 狀態 |
|---|---|
| GitHub Actions 定時抓取資料 | 可行 |
| 資料標準化與品質檢查 | 可行 |
| Fallback 機制 | 可行 |
| 建立每日資料包 | 可行 |
| 無 API Key 自動呼叫 ChatGPT | **已證實不可行** |
| 人工啟動 ChatGPT 分析 | 可行 |
| ChatGPT 產出 Markdown | 可行 |
| ChatGPT 產出 Dashboard JSON | 可行 |
| ChatGPT 自動寫回 GitHub | **可行，但可能失敗** |
| 完整無人值守分析流程 | **目前不可行／未達成** |

---

## 7. 文件與實作上的強制要求

所有相關文件必須遵守：

1. 不得將資料自動化寫成分析自動化。
2. 不得宣稱 GitHub Actions 能無 API Key 自動呼叫 ChatGPT。
3. 必須明確寫出 ChatGPT 分析需要使用者人工啟動。
4. ChatGPT 寫回 GitHub 必須使用「嘗試寫回」的描述。
5. 寫回成功必須有結果確認。
6. 寫回失敗必須保留分析結果並記錄失敗。
7. 不得把「報告已產出」等同於「GitHub 已成功更新」。
8. 不得把「資料包已建立」等同於「每日盤前分析已完成」。
9. 完整無人值守流程列為後續版本或獨立驗證項目。
10. 未經實際端到端測試，不得宣稱流程已完成。

---

## 8. 最終定義

本專案目前的正確描述為：

> **GitHub Actions 負責資料自動化；使用者人工啟動 ChatGPT 進行分析；ChatGPT 可嘗試將 Markdown 報告與 Dashboard JSON 寫回 GitHub，但寫回可能失敗，且必須明確回報成功、部分成功或失敗狀態。**

