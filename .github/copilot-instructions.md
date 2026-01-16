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
