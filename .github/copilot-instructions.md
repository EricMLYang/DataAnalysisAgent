# Copilot Instructions

## Agent Trace Trigger

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

## Trace to Flow Trigger

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

## Flow Spec to LangChain Plan

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
