這個需求本質上是：**把「Copilot/Agent 的執行軌跡（trace）」變成「可實作的 LangChain/LangGraph 開發規劃」**。
`.github/prompts` 可以放「提示詞模板」，但**單靠 prompt 不夠穩**：因為你還需要把 JSON trace 先整理成「可讀、可映射」的結構（不然模型每次自己解讀，格式容易飄）。

我會建議用 **Prompt + 一個小型 trace 轉換器（script/skill）** 的組合。

---

## 最推薦做法：Trace →（轉換器）→ Flow Spec →（prompt）→ LangChain 規劃

### 1) Repo 放什麼

**A. `.github/prompts/trace_to_langchain_plan.prompt.md`**
放「把 Flow Spec 變成 LangChain 規劃」的 prompt（固定格式輸出）。

**B. `./github/skills/trace-to-flow/`（或你現有的 skills 結構）**
放一個最小工具：把 trace JSONL 轉成「Flow Spec」（例如 YAML/JSON/Markdown）。

> 重點：**模型吃 Flow Spec，不要直接吃原始 trace**。

---

## Flow Spec 長什麼樣（建議你固定一個 schema）

例如輸出成 `flow_spec.yaml`：

```yaml
run_name: take-data-test
goal: 撈取 mock 數據並確認狀況
phases:
  - name: Understand
    steps:
      - 解析任務需求
  - name: Fetch
    steps:
      - 執行 data-fetch 撈取數據
    tools:
      - python
    outputs:
      - data_fetch_profile.json
    dependencies:
      - pandas
    failure_modes:
      - module_missing: pandas
      - wrong_python_env: pandas installed in venv
    recovery_playbook:
      - install_dependency: pip install pandas (in the right env)
      - select_python: /Users/ericmlyang/Coding/Projects/Venvs/pyspark/bin/python
  - name: Profile
    steps:
      - 分析數據 profile
    outputs:
      - data_fetch_profile.json
  - name: QualityCheck
    steps:
      - 檢視數據品質
final_summary:
  dataset: sales.csv
  rows: 50
  cols: 6
  data_quality: 無缺失值
  time_range: 2026-01-01 至 2026-01-10
artifacts:
  - data_fetch_profile.json
```

這份 spec 會非常容易被轉成：

* LangChain 的 chain/agent steps
* LangGraph 的 nodes/edges
* 工具（tool）與 error handling 的設計

---

## `.github/prompts` 裡的 prompt 應該怎麼寫？

你可以把 prompt 寫成「**輸入 = Flow Spec，輸出 = LangChain 開發計畫**」，並強制格式，例如：

* **目標**
* **Inputs/Outputs**
* **Tools（Python、Shell、DB、HTTP…）**
* **Node 設計（LangGraph 節點）**
* **錯誤處理（對應 failure_modes）**
* **測試策略（unit/integration、mock data）**
* **最小可跑版本（MVP）」**

這樣 Copilot 每次都會產出一致的工程規劃。

---

## 你問的核心：「通常會是在 `.github/prompts` 放對應的 prompt 嗎？」

可以放，但我會這樣拆：

* `.github/prompts/…`：**只放「轉換規劃」的提示詞（穩定輸出格式）**
* `skills/trace-to-flow/…`：**把 trace 先變成 Flow Spec（穩定輸入）**
* `plans/…`：產出結果（例如 `plans/take-data-test.langchain-plan.md`）

原因很直白：
**prompt 擅長把「結構化輸入」寫成「可讀可實作文件」；但不擅長每次都把雜訊很多的 log 自己整理乾淨。**

---

## 最小落地流程（你可以直接用在 repo）

1. Agent 跑完任務 → 產生 `traces/take-data-test.jsonl`
2. 執行 `trace-to-flow` → 產生 `specs/take-data-test.flow_spec.yaml`
3. Copilot 套用 `.github/prompts/trace_to_langchain_plan.prompt.md`
   讀 `flow_spec.yaml` → 生成 `plans/take-data-test.langchain-plan.md`

> 你之後要更進一步：
> 同一份 `flow_spec.yaml` 還可以再加一個 prompt 直接生成 **LangGraph skeleton code**（nodes/edges/tool wrappers）。

---

## 針對你這份 trace，我會怎麼映射到 LangChain（概念對照）

* `plan.steps[]` → LangGraph nodes 的主幹（Understand → Fetch → Profile → QualityCheck → Summarize）
* `error + strategy_shift` → 專門做一個 **Recovery node**（依賴安裝、選 python env、重跑 fetch）
* `tool_result.output_file` → artifact contract（節點輸出是文件/JSON，而不是只在記憶體裡）
