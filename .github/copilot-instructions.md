# Copilot Instructions

## Agent Trace 記錄規則

當使用者訊息中包含 **「請記錄：ON」** 時，必須遵守以下規則：

### 1. 初始化
在 `runs/` 下建立新的 run：
```bash
python3 agent_trace.py init <run_name>
```
這會建立 `runs/<timestamp>-<run_name>/trace.ndjson`

### 2. 記錄每個動作
從初始化開始，**每做一個動作都要記錄**：
```bash
python3 agent_trace.py log <run_dir> <type> "<message>" '<data_json>'
```

### 3. 事件類型
| type | 何時使用 |
|------|----------|
| `plan` | 列出計劃步驟（3-8 步） |
| `tool_search` | 尋找工具或指令 |
| `tool_use` | 使用工具（命令、檔案、function） |
| `tool_result` | 工具回傳結果（成功/失敗） |
| `prompt_search` | 查詢 prompt 或 instruction |
| `step_prepare` | 準備執行某步驟 |
| `step_execute` | 開始/結束執行步驟 |
| `strategy_shift` | 改變策略（記錄 from/to + 原因） |
| `error` | 發生錯誤 |
| `summary` | 任務結束摘要（**必須**） |

### 4. 完成條件
任務結束**必須**寫 `summary` 事件。缺少 `plan` + `summary` 視為任務未完成。

---

## 觸發格式

```
請記錄：ON
run_name: <任務名>
任務：<指令內容>
```

看到此格式就啟動記錄模式。
