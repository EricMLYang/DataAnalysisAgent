# Databricks Agent 技術工具清單精簡版，
---

## Mosaic AI（3 個核心組件）

### 1) Mosaic AI Agent Framework（Agent 組裝底座）

* **是什麼**：一套在 Databricks 上建置「tool-calling + RAG」Agent 的框架與規範。
* **目的**：把 LLM、工具、檢索串起來，並走 Databricks 的治理/部署方式。
* **Agent 怎麼用**：你定義「有哪些 tools + 哪個 retriever + 系統提示詞」，Agent 就能在對話中自動決定要不要呼叫工具或查文件。([docs.databricks.com][1])

### 2) Mosaic AI Model Serving / Foundation Model APIs（LLM 服務層）

* **是什麼**：在 Databricks 上呼叫/部署模型的 API 與 Serving Endpoints（OpenAI-compatible）。
* **目的**：讓 Agent 的「大腦」有穩定的 API 可呼叫、可部署成服務。
* **Agent 怎麼用**：Agent 的每次推理都打到這個 API；也常用它來啟用 function calling / structured outputs。([docs.databricks.com][2])

### 3) Mosaic AI Vector Search（RAG 向量檢索層）

* **是什麼**：Databricks 原生向量索引與相似度搜尋服務（通常從 Delta table 建 index）。
* **目的**：讓 Agent 能查「文件/SOP/規格/知識庫」這類非結構化資料，做 RAG。
* **Agent 怎麼用**：把 Vector Search index 做成 retriever tool，Agent 需要補知識時先檢索再回答。([docs.databricks.com][3])

---

## Databricks Agent 技術工具清單（平台面向）

### A) Tools（讓 Agent “能做事”）

> Databricks 官方把 agent tools 分三種路徑：([docs.databricks.com][1])

1. **Unity Catalog Function Tools（UC Functions）**

* **是什麼**：把查數據/算指標/呼叫外部 API 封裝成 UC function。
* **目的**：治理（權限/稽核）+ 可控（只讓 Agent 做你允許的事）。
* **Agent 怎麼用**：Agent 透過 tool-calling 呼叫 `uc.some_function(...)` 取得結果再整理。([docs.databricks.com][3])

2. **Agent Code Tools**

* **是什麼**：工具直接寫在 agent 的 Python code 裡。
* **目的**：最快 PoC、彈性最高。
* **Agent 怎麼用**：把 Python function 當 tool 註冊，讓 Agent 直接呼叫（但治理比 UC 弱）。([docs.databricks.com][1])

3. **MCP Tools（Model Context Protocol）**

* **是什麼**：用 MCP 標準把工具/資源掛給 Agent（可用 Databricks managed MCP 或外部 MCP）。
* **目的**：標準化接入各種工具與資源，減少客製整合成本。
* **Agent 怎麼用**：在 Playground 或程式裡指定 MCP servers，Agent 就能用它提供的工具。([docs.databricks.com][4])

---

### B) Function Calling（讓模型“自己決定何時叫工具”）

* **是什麼**：Databricks 的 OpenAI-compatible function calling（在 model serving 時提供）。
* **目的**：讓 Agent 更自然地「先規劃 → 再選工具 → 再呼叫參數」。
* **Agent 怎麼用**：你給工具 schema（名稱/參數），模型在對話中輸出 tool call，系統執行後回傳結果。([docs.databricks.com][5])

---

### C) RAG / Retrieval Tools（讓 Agent 查文件）

* **是什麼**：把 Vector Search（或其他索引）包成 retriever tool，並支援 trace。
* **目的**：讓 Agent 在回答前先取回「可引用來源」。
* **Agent 怎麼用**：Agent 認為需要背景/條款/規格時，先呼叫 retriever tool 取回片段再回答。([docs.databricks.com][6])

---

### D) AI Playground（Agent 原型化工作台）

* **是什麼**：UI 介面快速做 tool-calling agent。
* **目的**：不用先寫很多 code，就能測：提示詞、工具、Vector Search、MCP 的行為。
* **Agent 怎麼用**：在 UI 選 **UC Function / Vector Search / MCP** → 直接 chat 看它怎麼呼叫工具 → 可匯出 Python。([docs.databricks.com][3])

---

### E) Databricks AI Functions（SQL 內建 AI 能力）

* **是什麼**：在 Databricks SQL / Notebook / Workflows 直接用 `ai_query`, `ai_classify` 等函數對資料做 AI 處理。
* **目的**：把資料先「結構化/標註/摘要」成可用欄位，降低 Agent 即時推理負擔。
* **Agent 怎麼用**：常見做法是 **先用 AI Functions 做離線加工**（生成標籤/欄位/摘要），Agent 查詢時直接撈加工後結果。([docs.databricks.com][7])

---

如果你下一步要落地「最簡單：**規劃 > 撈數據**」，我建議你先只用這 3 個：
**(1) Foundation Model APIs + (2) UC Function Tool + (3)（可選）Function Calling**。
你回我一句：你要撈的是「某張 Delta 表的彙總」還是「跨多表 join 的指標」，我就用最小範例幫你把 UC Function 的形狀（參數/回傳/權限邊界）定出來。
