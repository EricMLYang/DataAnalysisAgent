任務描述 (Prompt)** 以及**檔案結構規範**。



> **任務：將「記錄規則」封裝為 GitHub Copilot Agent Skill**
> 我想將現有的 Trace 記錄邏輯從 .github/copilot-instructions.md 遷移為專屬 Skill。請執行以下步驟：
> 1. **建立目錄：** 在 `.github/copilot/skills/agent-trace/` 建立技能資料夾。
> 2. **遷移腳本：** 將現有的 `agent_trace.py` 移動到該目錄下。
> 3. **編寫 SKILL.md：** 這是最重要的部分。請參考以下格式撰寫，讓 Agent 知道這是個可呼叫的工具：
> * **Name:** agent-trace
> * **Description:** 用於記錄 Agent 的執行軌跡（Planning, Tool use, Strategy shift 等）。
> * **Usage:** 說明如何使用 `python3 agent_trace.py init` 與 `log` 指令。
> * **Schema:** 明確定義 `type` 的枚舉值（plan, tool_use, strategy_shift 等）。
> 
> 
> 4. **精簡 Instructions：** 修改根目錄或 `.github/` 下的指令檔，刪除所有技術細節，僅保留觸發邏輯。
> 
> 
> **備註：** Agent Skill 是一種將特定功能封裝成 API 的方式，當你看到 `SKILL.md` 時，你應該將其視為你具備的一項「原生能力」。

---

## 3. 轉換後的 SKILL.md 範例

這是 Agent 讀取的核心文件，它將原本的 Markdown 規則轉化為「API 規格」：

```markdown
# Skill: Agent Trace Logger

## Description
此技能用於在 `runs/` 目錄下建立結構化的執行紀錄 (NDJSON)。每當使用者要求「請記錄：ON」時，必須調用此技能。

## Capabilities
- **Initialize:** 建立新的 run 目錄與 trace 檔案。
- **Logging:** 記錄任務的每一個原子動作。

## Usage Guidelines
Agent 必須在執行具體動作的同時，同步調用以下命令：

### 1. 初始化
```bash
python3 .github/copilot/skills/agent-trace/agent_trace.py init <run_name>

```

### 2. 記錄事件 (Log types)

支援的 type 包含：`plan`, `tool_search`, `tool_use`, `tool_result`, `prompt_search`, `step_prepare`, `step_execute`, `strategy_shift`, `error`, `summary`。

```bash
python3 .github/copilot/skills/agent-trace/agent_trace.py log <run_dir> <type> "<message>" '<data_json>'

```

## Constraints

* 任務開始必須有 `plan`。
* 任務結束必須有 `summary`。
* 策略改變（例如原本的方法行不通）必須記錄 `strategy_shift`。

```

---

## 4. 精簡後的 Copilot Instructions

原本長達幾十行的指令，現在只需保留這一小段在 `.github/copilot-instructions.md` 中：

```markdown
# Agent Trace Trigger

當使用者訊息包含「請記錄：ON」與「run_name」時：
1. **啟用技能：** 使用位於 `.github/copilot/skills/agent-trace/` 的 `agent-trace` 技能。
2. **全程追蹤：** 根據該技能的 `SKILL.md` 規範，在執行任務的過程中自動進行初始化與日誌記錄。

```
