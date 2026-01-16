# 計畫：Spec to LangChain Code Generator

## 目標

讓 Coding Agent 能夠：
1. 讀取一個或多個 `specs/*.yaml` Flow Spec
2. 生成可本地測試的 LangChain/LangGraph 程式碼
3. 程式碼結構可輕鬆移植到 Databricks Mosaic AI

---

## 一、資料夾結構設計

```
DataAnalysisAgent/
├── specs/                          # Flow Spec YAML (已存在)
│   └── take-data-test.flow_spec.yaml
│
├── flows/                          # 【新增】LangChain/LangGraph 程式碼
│   ├── __init__.py
│   ├── common/                     # 共用模組
│   │   ├── __init__.py
│   │   ├── state.py                # 共用 State 定義
│   │   ├── tools.py                # Tool 基類與工廠
│   │   └── config.py               # 環境配置 (local vs databricks)
│   │
│   └── take_data_test/             # 每個 Flow 一個子資料夾
│       ├── __init__.py
│       ├── graph.py                # LangGraph 主邏輯
│       ├── nodes.py                # Node 函數定義
│       ├── tools.py                # Flow 專屬 Tools
│       ├── state.py                # Flow 專屬 State
│       └── tests/
│           ├── __init__.py
│           ├── test_nodes.py       # 單元測試
│           └── test_graph.py       # 整合測試
│
├── databricks/                     # 【新增】Databricks 部署相關
│   ├── uc_functions/               # Unity Catalog Functions 定義
│   │   └── README.md
│   └── deployment/                 # 部署腳本與配置
│       └── README.md
│
└── tests/                          # 【新增】全域測試
    ├── conftest.py                 # pytest fixtures
    └── test_flows.py               # 跨 flow 測試
```

### 資料夾命名邏輯

- `flows/` - 代表可執行的「流程」，對應 LangGraph 的 Graph
- 子資料夾名稱 = `flow_spec.yaml` 的 `run_name`（底線取代連字號）
- `databricks/` - 未來移植時的目標位置

---

## 二、生成的程式碼結構

### 2.1 `flows/<flow_name>/state.py`

```python
from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages

class FlowState(TypedDict):
    """Flow 狀態定義 - 從 flow_spec.yaml 的 phases 推導"""
    messages: Annotated[list, add_messages]
    task: str
    dataset_key: str | None
    profile: dict | None
    quality_report: dict | None
    summary: str | None
    error: str | None
```

### 2.2 `flows/<flow_name>/tools.py`

```python
from langchain_core.tools import tool

@tool
def fetch_data(task: str, dataset_key: str) -> dict:
    """從 mock_data 載入數據並生成 profile

    對應 Databricks: uc.data_ops.fetch_profile()
    """
    # 本地實作：呼叫現有的 data-fetch skill
    pass

@tool
def check_quality(profile: dict) -> dict:
    """檢查數據品質

    對應 Databricks: uc.data_ops.quality_check()
    """
    pass
```

### 2.3 `flows/<flow_name>/nodes.py`

```python
from .state import FlowState
from .tools import fetch_data, check_quality

def understand_node(state: FlowState) -> FlowState:
    """Phase: Understand - 解析任務需求"""
    # 從 state["task"] 解析意圖
    return {"dataset_key": parsed_key}

def fetch_node(state: FlowState) -> FlowState:
    """Phase: Fetch - 撈取數據"""
    result = fetch_data.invoke({
        "task": state["task"],
        "dataset_key": state["dataset_key"]
    })
    return {"profile": result}

def quality_check_node(state: FlowState) -> FlowState:
    """Phase: QualityCheck - 檢視數據品質"""
    report = check_quality.invoke({"profile": state["profile"]})
    return {"quality_report": report}

def summarize_node(state: FlowState) -> FlowState:
    """Phase: Summarize - 總結"""
    return {"summary": "..."}
```

### 2.4 `flows/<flow_name>/graph.py`

```python
from langgraph.graph import StateGraph, START, END
from .state import FlowState
from .nodes import understand_node, fetch_node, quality_check_node, summarize_node

def build_graph() -> StateGraph:
    """建立 LangGraph - 從 flow_spec.yaml 的 phases 生成"""

    builder = StateGraph(FlowState)

    # 加入節點 (對應 phases)
    builder.add_node("understand", understand_node)
    builder.add_node("fetch", fetch_node)
    builder.add_node("quality_check", quality_check_node)
    builder.add_node("summarize", summarize_node)

    # 加入邊 (線性流程)
    builder.add_edge(START, "understand")
    builder.add_edge("understand", "fetch")
    builder.add_edge("fetch", "quality_check")
    builder.add_edge("quality_check", "summarize")
    builder.add_edge("summarize", END)

    return builder.compile()

# 匯出可執行的 graph
graph = build_graph()
```

---

## 三、Spec → Code 映射規則

| Flow Spec 欄位 | LangChain/LangGraph 對應 |
|----------------|--------------------------|
| `phases[].name` | Node 名稱 |
| `phases[].steps` | Node docstring / 實作邏輯 |
| `phases[].tools` | `@tool` 裝飾的函數 |
| `phases[].outputs` | State 欄位 |
| `phases[].dependencies` | `requirements.txt` |
| `phases[].failure_modes` | 條件邊 / try-except |
| `phases[].recovery_playbook` | 錯誤處理節點 |
| `final_summary` | 最終 State 驗證 |
| `artifacts` | 輸出檔案路徑 |

---

## 四、Copilot 觸發方式設計

### 方式一：單一 Spec

```
/spec-to-langchain take-data-test
```

### 方式二：多個 Specs（合併成一個 Graph）

```
/spec-to-langchain take-data-test,fetch-inventory --merge
```

### 方式三：所有 Specs

```
/spec-to-langchain --all
```

---

## 五、本地測試策略

### 5.1 單元測試 (`test_nodes.py`)

```python
def test_fetch_node_success():
    """測試 fetch_node 正常情況"""
    state = {"task": "撈 sales 資料", "dataset_key": "sales"}
    result = fetch_node(state)
    assert "profile" in result
    assert result["profile"]["rows"] > 0

def test_fetch_node_missing_dependency():
    """測試缺少 pandas 的錯誤處理"""
    # 模擬 ModuleNotFoundError
    pass
```

### 5.2 整合測試 (`test_graph.py`)

```python
def test_full_flow():
    """端到端測試"""
    from flows.take_data_test.graph import graph

    result = graph.invoke({
        "task": "撈取 sales 資料並確認品質",
        "messages": []
    })

    assert result["summary"] is not None
    assert "error" not in result or result["error"] is None
```

### 5.3 Mock 數據

- 使用現有的 `mock_data/` 資料夾
- 測試時透過 `flows/common/config.py` 切換本地/Databricks 模式

---

## 六、Databricks 移植路徑

### 6.1 Tool → UC Function 對照

| Local Tool | Databricks UC Function |
|------------|------------------------|
| `fetch_data()` | `catalog.data_ops.fetch_profile` |
| `check_quality()` | `catalog.data_ops.quality_check` |

### 6.2 移植步驟

1. **本地驗證通過** → `flows/<name>/` 測試全綠
2. **提取 Tool 邏輯** → 放入 `databricks/uc_functions/`
3. **建立 UC Function** → 在 Databricks 註冊
4. **替換 Tool 實作** → 從本地呼叫改為 UC Function 呼叫
5. **部署 Agent** → 使用 Mosaic AI Agent Framework

---

## 七、需要建立的新 Skill

### `.github/skills/spec-to-langchain/`

```
spec-to-langchain/
├── skill.md              # Skill 說明
└── scripts/
    └── generate.py       # 程式碼生成器
```

### 生成器功能

1. 讀取 `specs/<name>.flow_spec.yaml`
2. 根據映射規則生成 `flows/<name>/` 目錄結構
3. 生成骨架程式碼（state, nodes, tools, graph, tests）
4. 支援 `--dry-run` 預覽不寫入

---

## 八、實作優先順序

1. **建立 `flows/common/`** - 共用模組（State 基類、Config）
2. **建立生成器骨架** - `spec-to-langchain` skill
3. **手動實作一個範例** - `flows/take_data_test/` 作為模板
4. **完善生成器** - 根據範例調整生成邏輯
5. **加入測試框架** - pytest + fixtures
6. **撰寫 Databricks 移植指南** - `databricks/README.md`

---

## 九、開放問題（待確認）

1. **LLM 選擇**：本地測試用哪個 LLM？（OpenAI / Azure / Ollama）
2. **State 持久化**：是否需要 checkpointing？
3. **多 Spec 合併**：合併時的節點命名衝突如何處理？
4. **Databricks 認證**：本地測試時如何模擬 UC Function？
