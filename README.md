# Agent Trace

極簡 AI Agent 動作記錄工具。

## 使用方式

```bash
# 初始化新的 run
python3 agent_trace.py init <run_name>

# 記錄事件
python3 agent_trace.py log <run_dir> <type> "<message>" '<data_json>'

# 列出所有 run
python3 agent_trace.py list

# 讀取 trace
python3 agent_trace.py read <run_dir>
```

## 事件類型

`plan` `tool_search` `tool_use` `tool_result` `prompt_search` `step_prepare` `step_execute` `strategy_shift` `error` `summary`

## Copilot 整合

在 Chat 中使用：

```
請記錄：ON
run_name: my-task
任務：<你的指令>
```

Copilot 會自動記錄每個動作到 `runs/<timestamp>-<run_name>/trace.ndjson`。
