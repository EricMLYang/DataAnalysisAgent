# Skill: Agent Trace Logger

## Name
`agent-trace`

## Description
此技能用於在 `runs/` 目錄下建立結構化的執行紀錄 (NDJSON)。每當使用者要求「請記錄：ON」時，必須調用此技能來追蹤 Agent 的完整執行軌跡。

## Capabilities
- **Initialize:** 建立新的 run 目錄與 trace.ndjson 檔案
- **Logging:** 記錄任務的每一個原子動作
- **Reading:** 讀取已記錄的 trace 內容
- **Listing:** 列出所有歷史 run 紀錄

---

## Usage Guidelines

Agent 必須在執行具體動作的同時，同步調用以下命令：

### 1. 初始化 (init)

在開始追蹤任務前，必須先初始化：

```bash
python3 .github/skills/agent-trace/agent_trace.py init <run_name>
```

**輸出：** 會建立 `runs/<timestamp>-<run_name>/` 目錄並回傳路徑

### 2. 記錄事件 (log)

```bash
python3 .github/skills/agent-trace/agent_trace.py log <run_dir> <type> "<message>" '<data_json>'
```

**參數說明：**
- `run_dir`: init 回傳的目錄路徑
- `type`: 事件類型（見下方 Schema）
- `message`: 事件描述訊息
- `data_json`: JSON 格式的額外資料（可選）

### 3. 列出所有 runs (list)

```bash
python3 .github/skills/agent-trace/agent_trace.py list
```

### 4. 讀取 trace 內容 (read)

```bash
python3 .github/skills/agent-trace/agent_trace.py read <run_dir>
```

---

## Schema

### Event Types

| type | 說明 | 使用時機 | data 建議欄位 |
|------|------|----------|---------------|
| `plan` | 任務計劃 | 列出 3-8 個步驟 | `{"steps": ["step1", "step2", ...]}` |
| `tool_search` | 尋找工具 | 查找適合的工具或指令 | `{"query": "...", "found": [...]}` |
| `tool_use` | 使用工具 | 執行命令、編輯檔案、呼叫 function | `{"tool": "...", "args": {...}}` |
| `tool_result` | 工具結果 | 記錄工具回傳 | `{"success": true/false, "output": "..."}` |
| `prompt_search` | 查詢 prompt | 查詢 prompt 或 instruction | `{"query": "...", "source": "..."}` |
| `step_prepare` | 準備步驟 | 準備執行某步驟前 | `{"step": 1, "description": "..."}` |
| `step_execute` | 執行步驟 | 開始/完成執行步驟 | `{"step": 1, "status": "start/done"}` |
| `strategy_shift` | 策略改變 | 方法行不通需調整 | `{"from": "...", "to": "...", "reason": "..."}` |
| `error` | 錯誤 | 發生錯誤時 | `{"error": "...", "context": "..."}` |
| `summary` | 任務摘要 | 任務結束時 | `{"result": "success/failed", "notes": "..."}` |

---

## Constraints

1. **任務開始必須有 `plan`** - 列出要執行的步驟
2. **任務結束必須有 `summary`** - 總結執行結果
3. **策略改變必須記錄 `strategy_shift`** - 說明 from/to 與原因
4. **缺少 `plan` + `summary` 視為任務未完成**

---

## Example Workflow

```bash
# 1. 初始化
python3 .github/skills/agent-trace/agent_trace.py init "feature-login"
# Output: runs/20260116-143000-feature_login

# 2. 記錄計劃
python3 .github/skills/agent-trace/agent_trace.py log runs/20260116-143000-feature_login plan "規劃登入功能開發" '{"steps": ["分析需求", "建立 API", "實作前端", "測試"]}'

# 3. 記錄工具使用
python3 .github/skills/agent-trace/agent_trace.py log runs/20260116-143000-feature_login tool_use "建立 login.py" '{"tool": "create_file", "args": {"path": "src/login.py"}}'

# 4. 記錄結果
python3 .github/skills/agent-trace/agent_trace.py log runs/20260116-143000-feature_login tool_result "檔案建立成功" '{"success": true}'

# 5. 記錄摘要
python3 .github/skills/agent-trace/agent_trace.py log runs/20260116-143000-feature_login summary "登入功能開發完成" '{"result": "success", "files_created": 3}'
```

---

## Output Format

所有事件以 NDJSON (Newline Delimited JSON) 格式儲存在 `trace.ndjson`：

```json
{"ts": "2026-01-16T14:30:00.123456", "type": "plan", "message": "規劃登入功能開發", "data": {"steps": ["分析需求", "建立 API"]}}
{"ts": "2026-01-16T14:30:05.789012", "type": "tool_use", "message": "建立 login.py", "data": {"tool": "create_file"}}
```
