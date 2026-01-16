# Agent Trace
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


# Repo. Prupose
本 Repo. 是在進行 **「Agent 行為模式的逆向工程」**。

你的核心邏輯是：**利用 GitHub Copilot 作為一個靈活的「沙盒 (Sandbox)」來驗證數據分析的邏輯路徑，然後將這些經過驗證的「成功路徑」與「工具調用規律」，規格化地移植到 Databricks 企業級平台。**

為了幫你講得更清楚，我將你的構想整理為以下三個維度：**戰略價值**、**技術對照表**、以及**從實驗室到生產線的轉化路徑**。

---

### 1. 核心戰略：從「原型沙盒」到「企業級架構」

你的 Trace 動作本質上是在捕捉 LLM 的 **「思維鏈 (Chain of Thought)」** 與 **「工具互動模式」**。

* **在 Copilot (實驗室階段)：** Agent 的行為較不受限，適合探索「解決某個分析問題需要哪些步驟？」、「需要調用幾次 SQL？」、「中間是否需要 Python 進行數據加工？」。
* **在 Databricks (生產階段)：** 這些隨意的步驟必須轉化為 **可管控 (Governed)**、**可審核 (Audited)** 且 **高效** 的 Flow。透過 Trace，你就能精確定義在 Databricks 上需要開發哪些 UC Functions 以及 Orchestration 的邏輯。

---

### 2. 技術映射對照表 (Mapping)

這部分將你目前的「Trace 動作」與「未來 Databricks 元件」直接掛鉤：

| GitHub Copilot (實驗與原型) | 轉化邏輯 | Databricks Mosaic AI (部署與生產) |
| --- | --- | --- |
| **Agent Skills (Python 腳本)** |  | **Unity Catalog (UC) Functions** (受控工具) |
| **Agent Trace (log/plan)** |  | **Mosaic AI Agent Tracing (MLflow)** |
| **Instruction (System Prompt)** |  | **Mosaic AI Agent Framework (Configuration)** |
| **Local Mock Data / CSV** |  | **Delta Tables / Vector Search Index** |
| **Manual Shell Commands** |  | **Databricks Workflows / Serverless Jobs** |
| **MCP Tools** |  | **Mosaic AI MCP Managed Servers** |

---

### 3. 清楚的轉化流程 (Orchestration Flow)

當你有了 Copilot 的 Trace 紀錄，你在 Databricks 上的開發流程會變得很清晰：

#### 第一階段：行為分析 (From Copilot Trace)

* **分析 `plan`：** 確定數據分析的標準作業程序 (SOP)。例如：先檢查 Schema -> 執行 SQL -> 用 Python 繪圖 -> 生成摘要。
* **分析 `strategy_shift`：** 找出 Agent 容易卡關的地方，這就是你在 Databricks 上需要加強「系統提示詞」或預設「SOP 邏輯」的重點。

#### 第二階段：工具標準化 (To UC Functions)

* 將 Copilot 中 Agent 隨意寫出的 `cat` 或 `grep` 腳本，封裝成具備權限控管的 **UC Function**。
* 例如：Agent 在 Copilot 用 Python 算相關係數，你在 Databricks 就提供一個 `uc.analytics.calc_correlation()` 給它。

#### 第三階段：框架組裝 (Mosaic AI Agent Framework)

* **底座：** 使用 Mosaic AI Agent Framework 將這些 UC Functions 串起來。
* **檢索：** 如果 Trace 顯示 Agent 頻繁查詢數據字典，則將其規格書導入 **Vector Search** 作為 Retriever Tool。
* **監控：** 透過 Databricks 原生的 **Inference Table** 紀錄，來對標你當初在 Copilot 做的 `agent_trace.ndjson`。
---

### 4. 總結你的願景
> 「我正在利用 GitHub Copilot 作為 **Agent 行為的模擬器**。透過 Trace 記錄，我能提煉出 Agent 在處理複雜數據任務時的 **『最佳路徑 (Golden Path)』**。這些路徑最終會變成 **Databricks Mosaic AI** 上的定義，將 Agent Skills 轉化為受治理的 **UC Functions**，並將隨機的推理過程轉化為可預測、可規模化的 **企業級數據分析流 (Orchestration Flow)**。」