# Copilot Instructions

## 🚀 一鍵端到端流程 (Full Pipeline)

當使用者訊息包含「**/full-pipeline**」或「**端到端執行**」時：

1. **步驟 1：執行任務並記錄 Trace**
   - 自動啟用 Agent Trace 記錄模式
   - 執行使用者指定的數據分析任務
   - 產生 `runs/<timestamp>-<name>/trace.ndjson`

2. **步驟 2：轉換 Trace 為 Flow Spec**
   - 自動執行 `trace-to-flow` 轉換
   - 產生 `specs/<name>.flow_spec.yaml`

3. **步驟 3：生成 LangGraph 程式碼**
   - 自動執行 `spec-to-langchain` 生成
   - 產生 `flows/<name>/{graph.py, run.py, __init__.py}`

4. **步驟 4：測試執行**
   - 執行生成的 flow 測試
   - 驗證是否正常運作

### 觸發格式範例

```
/full-pipeline
run_name: analyze-sales-data
任務：分析 sales.csv 的銷售趨勢並生成報告
```

或

```
端到端執行: customer-segmentation
請分析客戶數據並進行分群分析
```

### 完整流程圖

```
用戶需求 (Chat)
    ↓
Agent 執行任務 (自動記錄)
    ↓
runs/<timestamp>-<name>/trace.ndjson
    ↓ [trace-to-flow]
specs/<name>.flow_spec.yaml
    ↓ [spec-to-langchain]
flows/<name>/{graph.py, run.py}
    ↓ [test]
驗證成功 ✓
    ↓ [future]
Databricks 部署
```

---

## 📝 單步執行模式

### 1. Agent Trace Trigger

當使用者訊息包含「**請記錄：ON**」與「**run_name**」時：

1. **啟用技能：** 使用位於 `.github/skills/agent-trace/` 的 `agent-trace` 技能。
2. **全程追蹤：** 根據該技能的 `SKILL.md` 規範，在執行任務的過程中自動進行初始化與日誌記錄。

### 觸發格式範例

```
請記錄：ON
run_name: <任務名>
任務：<指令內容>
```

看到此格式就啟動記錄模式，參考 `.github/skills/agent-trace/SKILL.md` 執行追蹤。

---

### 2. Trace to Flow Trigger

當使用者訊息包含「**/trace-to-flow**」或「**轉換 trace**」時：

1. **啟用技能：** 使用位於 `.github/skills/trace-to-flow/` 的 `trace-to-flow` 技能。
2. **執行轉換：** 根據該技能的 `skill.md` 規範，將指定的 run trace 轉換為 Flow Spec YAML。

### 使用方式

**列出可用的 runs：**
```bash
python3 .github/skills/trace-to-flow/scripts/trace_to_flow.py list
```

**轉換指定的 run（支援部分名稱匹配）：**
```bash
python3 .github/skills/trace-to-flow/scripts/trace_to_flow.py convert <run_name>
```

### 觸發格式範例

```
/trace-to-flow take-data-test
```

或

```
轉換 trace: take-data-test
```

執行後會產生 `specs/<run_name>.flow_spec.yaml`，可進一步使用 `.github/prompts/trace_to_langchain_plan.prompt.md` 生成 LangChain 開發計畫。

---

### 3. Flow Spec to LangChain Plan

當使用者想要從 Flow Spec 生成 LangChain/LangGraph 開發計畫時：

1. 先確保已經執行 `trace-to-flow` 生成 Flow Spec
2. 讀取 `specs/<run_name>.flow_spec.yaml`
3. 參考 `.github/prompts/trace_to_langchain_plan.prompt.md` 的格式生成開發計畫
4. 輸出到 `plans/<run_name>.langchain-plan.md`

### 完整流程

```
runs/<timestamp>-<name>/trace.ndjson
    ↓ trace-to-flow
specs/<name>.flow_spec.yaml
    ↓ trace_to_langchain_plan.prompt.md
plans/<name>.langchain-plan.md
```

---

### 4. Spec to LangChain Code Trigger

當使用者訊息包含「**/spec-to-langchain**」或「**生成 flow**」時：

1. **啟用技能：** 使用位於 `.github/skills/spec-to-langchain/` 的 `spec-to-langchain` 技能。
2. **直接生成程式碼：** 根據該技能的 `skill.md` 規範，**Agent 直接手工撰寫** LangGraph 程式碼（不使用腳本生成）。

### Agent 執行步驟

1. **列出 specs：** 使用 `list_dir` 查看 `specs/` 目錄
2. **讀取 spec：** 使用 `read_file` 讀取 `specs/<name>.flow_spec.yaml`
3. **分析結構：** 解析 YAML 中的 `phases`、`outputs`、`dependencies`
4. **生成程式碼：** 使用 `create_file` 直接創建三個檔案：
   - `flows/<flow_name>/__init__.py`
   - `flows/<flow_name>/graph.py`（完整的 LangGraph 實作）
   - `flows/<flow_name>/run.py`（測試入口）
5. **加入移植提示：** 在 `graph.py` 中為每個 node 加入 Databricks 移植註解

### 觸發格式範例

```
/spec-to-langchain take-data-test
```

或

```
生成 flow: take-data-test
```

### 輸出說明

Agent 會在 `flows/<flow_name>/` 直接創建：
- `__init__.py` - 模組匯出
- `graph.py` - LangGraph 主邏輯（包含 Databricks 移植註解）
- `run.py` - 測試入口

**關鍵：** `graph.py` 中每個 node function 都應包含 `# 🏢 Databricks Migration Notes` 註解，標註如何轉換為 UC Functions。

---

## 🎯 使用情境對照表

| 情境 | 指令格式 | 輸出結果 |
|------|---------|---------|
| **完整流程（推薦）** | `/full-pipeline` <br> `run_name: my-task` <br> `任務：...` | `flows/<name>/` 完整可執行程式碼 |
| **只記錄執行** | `請記錄：ON` <br> `run_name: my-task` <br> `任務：...` | `runs/<timestamp>-<name>/trace.ndjson` |
| **只轉 Spec** | `/trace-to-flow my-task` | `specs/<name>.flow_spec.yaml` |
| **只生成程式碼** | `/spec-to-langchain my-task` | `flows/<name>/{graph.py, run.py}` |

---

## 🔧 Agent 執行原則

### 自動化行為
當識別到觸發關鍵字時，Copilot 應該：
1. ✅ **主動執行** - 不要只描述步驟，直接執行對應的操作
   - `trace-to-flow`: 執行 Python 腳本轉換
   - `spec-to-langchain`: Agent 直接生成程式碼（不執行腳本）
2. ✅ **連續執行** - 在 `/full-pipeline` 模式下，自動完成所有步驟
3. ✅ **錯誤處理** - 若某步驟失敗，記錄錯誤並提供除錯建議
4. ✅ **進度回報** - 每完成一個階段，簡短報告當前狀態
5. ✅ **移植意識** - 在生成 LangGraph 程式碼時，加入 Databricks 移植提示

### 檔案路徑規範
- Trace 輸出：`runs/<timestamp>-<run_name>/trace.ndjson`
- Spec 輸出：`specs/<run_name>.flow_spec.yaml`
- Flow 輸出：`flows/<run_name>/{graph.py, run.py, __init__.py}`
- Plan 輸出：`plans/<run_name>.langchain-plan.md` (可選)

### 命名規範
- `run_name` 應使用 kebab-case (例如：`analyze-sales-data`)
- 自動將空格轉換為連字號
- 避免使用特殊字元

---

## 📦 技能依賴關係

```
agent-trace (基礎記錄)
    ↓
trace-to-flow (分析轉換)
    ↓
spec-to-langchain (程式碼生成)
    ↓
[未來] databricks-deploy (企業部署)
```

每個技能都有獨立的 `SKILL.md` 與 `scripts/` 目錄，位於 `.github/skills/<skill-name>/`。
