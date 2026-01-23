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

#### 1. 意圖理解 (Intent Understanding)
剛接收到問題，應該會有一段撈取 Context 去釐清問題的動作

- **`context_search`** - 搜尋相關 Context
  - **使用時機**: 收到問題後，搜尋相關檔案、文件、歷史記錄
  - **data 欄位**: `{"query": "...", "sources": [...], "findings": "..."}`

- **`intent_clarify`** - 釐清意圖
  - **使用時機**: 分析問題、確認需求、理解目標
  - **data 欄位**: `{"question": "...", "understanding": "...", "assumptions": [...]}`

#### 2. 計畫 (Planning)
把問題變成步驟

- **`plan`** - 任務計劃
  - **使用時機**: 列出 3-8 個執行步驟
  - **data 欄位**: `{"steps": ["step1", "step2", ...], "rationale": "..."}`

#### 3. 發現資源 (Resource Discovery)
包含 prompt、工具、技能等資源

- **`prompt_search`** - 查詢 prompt
  - **使用時機**: 查詢 prompt 或 instruction
  - **data 欄位**: `{"query": "...", "source": "...", "result": "..."}`

- **`tool_search`** - 尋找工具
  - **使用時機**: 查找適合的工具、指令或技能
  - **data 欄位**: `{"query": "...", "found": [...], "selected": "..."}`

- **`step_prepare`** - 準備步驟
  - **使用時機**: 準備執行某步驟前，收集所需資源
  - **data 欄位**: `{"step": 1, "description": "...", "resources": [...]}`

#### 4. 執行 (Execution)
執行發現的資源

- **`step_execute`** - 執行步驟
  - **使用時機**: 開始/完成執行步驟
  - **data 欄位**: `{"step": 1, "status": "start/done", "action": "..."}`

- **`tool_use`** - 使用工具
  - **使用時機**: 執行命令、編輯檔案、呼叫 function
  - **data 欄位**: `{"tool": "...", "args": {...}, "purpose": "..."}`

- **`tool_result`** - 工具結果
  - **使用時機**: 記錄工具回傳結果
  - **data 欄位**: `{"success": true/false, "output": "...", "error": "..."}`

#### 5. 觀察檢視 (Observation)
針對結果作評論

- **`observation`** - 觀察結果
  - **使用時機**: 檢視執行結果、分析輸出、發現問題
  - **data 欄位**: `{"observation": "...", "findings": [...], "concerns": [...]}`

- **`error`** - 錯誤記錄
  - **使用時機**: 發生錯誤時
  - **data 欄位**: `{"error": "...", "context": "...", "severity": "..."}`

#### 6. 驗證反思 (Validation & Reflection)
針對目前狀態決定要不要有其他計畫循環

- **`validation`** - 驗證結果
  - **使用時機**: 檢查結果是否符合預期、驗證輸出正確性
  - **data 欄位**: `{"status": "pass/fail", "checks": [...], "issues": [...]}`

- **`reflection`** - 反思與評估
  - **使用時機**: 評估當前進度、判斷是否需要調整
  - **data 欄位**: `{"current_state": "...", "next_action": "...", "confidence": 0.0-1.0}`

- **`strategy_shift`** - 策略改變
  - **使用時機**: 方法行不通需調整策略
  - **data 欄位**: `{"from": "...", "to": "...", "reason": "..."}`

#### 7. 總結與提交 (Summary & Delivery)
交出最終結果

- **`summary`** - 任務摘要
  - **使用時機**: 任務結束時，總結執行結果
  - **data 欄位**: `{"result": "success/failed", "notes": "...", "deliverables": [...]}`

- **`delivery`** - 交付成果
  - **使用時機**: 提交最終結果給使用者
  - **data 欄位**: `{"output": "...", "files": [...], "next_steps": [...]}`

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
