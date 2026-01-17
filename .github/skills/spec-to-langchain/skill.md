---
name: spec-to-langchain
description: Generate LangGraph skeleton code from Flow Spec YAML files.
---

# Spec to LangChain Skill

## What This Skill Does

**Agent 直接閱讀** `specs/*.yaml` Flow Spec 檔案，**手工撰寫**完整的 LangGraph 程式碼，包含：
- `graph.py` - LangGraph 主邏輯（State、Nodes、Graph）
- `run.py` - 測試執行入口
- `__init__.py` - 模組匯出

⚠️ **重要：** 這個 Skill 要求 Agent 根據 Spec **直接生成程式碼**，而非執行腳本產生。

## Strategic Purpose（戰略目的）

這個步驟是「**Copilot 實驗室 → Databricks 生產環境**」轉化流程中的關鍵橋樑：

```
Agent 隨機行為 (Copilot Trace)
    ↓ 結構化
Flow Spec (標準作業程序)
    ↓ 程式化（此 Skill）
LangGraph Code (可測試、可驗證的流程)
    ↓ 企業化
Databricks Mosaic AI (UC Functions + Workflows)
```

### 為什麼需要 LangGraph 這一層？

1. **驗證邏輯正確性** - 在移植到 Databricks 前先本地測試
2. **識別可重用元件** - Node functions → UC Functions 的候選清單
3. **定義狀態流轉** - FlowState → Databricks Job Parameters 的設計基礎
4. **捕捉錯誤處理** - recovery_playbook → 企業級 SLA 的需求來源

## When to Use

當你已經有 Flow Spec（透過 `trace-to-flow` skill 產生）並想要生成對應的 LangChain/LangGraph 程式碼時。

## How Agent Should Work

### Step 1: 列出並選擇 Spec

Agent 應該列出 `specs/` 目錄中的所有 `.flow_spec.yaml` 檔案，並讓使用者選擇或自動匹配。

### Step 2: 讀取並理解 Spec

```python
# Agent 讀取 specs/<name>.flow_spec.yaml
import yaml
with open(f'specs/{spec_name}.flow_spec.yaml') as f:
    spec = yaml.safe_load(f)
```

### Step 3: 生成程式碼檔案

Agent 應該直接使用 `create_file` 工具創建以下三個檔案：

1. `flows/<flow_name>/__init__.py`
2. `flows/<flow_name>/graph.py`
3. `flows/<flow_name>/run.py`

## Code Generation Rules

### 1. File: `__init__.py`

簡單的模組匯出：

```python
from .graph import graph, build_graph

__all__ = ["graph", "build_graph"]
```

### 2. File: `graph.py`

**結構要求：**

```python
"""
<Flow Name> - LangGraph Implementation

基於 specs/<spec-name>.flow_spec.yaml 生成的 LangGraph 流程
目標：<goal from spec>

Phases:
<list all phases with steps>
"""

import sys
from pathlib import Path
from typing import TypedDict

from langgraph.graph import StateGraph, START, END

# 如果需要使用其他 skills，加入到 path
PROJECT_ROOT = Path(__file__).parent.parent.parent
# sys.path.insert(0, str(PROJECT_ROOT / ".github" / "skills" / "<skill-name>" / "scripts"))

# =============================================================================
# State Definition
# =============================================================================

class FlowState(TypedDict):
    """Flow 狀態"""
    task: str                          # 輸入：任務描述
    # 根據 spec.phases[].outputs 生成狀態欄位
    # 根據需要加入中間結果欄位
    error: str | None                  # 錯誤訊息（如有）


# =============================================================================
# Node Functions
# =============================================================================

def <phase_name_lower>_node(state: FlowState) -> dict:
    """
    Phase: <PhaseName> - <phase description>
    
    Steps:
    <list phase steps>
    
    Tools: <list tools if any>
    Dependencies: <list dependencies if any>
    """
    # 實作邏輯：
    # 1. 從 state 中取得必要資訊
    # 2. 執行該 phase 的核心邏輯
    # 3. 處理 failure_modes（如果 spec 有記錄）
    # 4. 回傳更新的狀態
    
    print(f"[{<PhaseName>}] <描述動作>")
    
    # TODO: 實作該 phase 的邏輯
    
    return {<updated_fields>}


# 為每個 phase 生成一個 node function


# =============================================================================
# Graph Construction
# =============================================================================

def build_graph() -> StateGraph:
    """構建 LangGraph 流程圖"""
    graph = StateGraph(FlowState)
    
    # 加入所有 phase nodes
    graph.add_node("<phase1>", <phase1>_node)
    graph.add_node("<phase2>", <phase2>_node)
    # ... 為每個 phase 加入 node
    
    # 線性連接（可根據實際需求調整）
    graph.add_edge(START, "<phase1>")
    graph.add_edge("<phase1>", "<phase2>")
    # ...
    graph.add_edge("<last_phase>", END)
    
    return graph.compile()


# 建立可匯出的 graph instance
graph = build_graph()
```

**關鍵設計原則：**

- **FlowState 欄位命名：** 根據 `spec.phases[].outputs` 中的檔案名轉換（如 `data_fetch_profile.json` → `profile: dict | None`）
- **Node Function 命名：** `<phase.name.lower()>_node`（如 `Fetch` → `fetch_node`）
- **實作參考 trace：** 如果 spec 有 `recovery_playbook`，應在 node 中實作錯誤處理
- **Skills 整合：** 檢查是否有已存在的 skills 可重用（如 `data-fetch`）

**💡 Databricks 移植提示（在程式碼註解中標註）：**

在生成的 `graph.py` 中，對於每個 node function，Agent 應該加入註解標註：

```python
def fetch_node(state: FlowState) -> dict:
    """
    Phase: Fetch - 執行 data-fetch 撈取數據
    
    # 🏢 Databricks Migration Notes:
    # - 此 node 可封裝為 UC Function: `uc.data.fetch_profile(dataset_key: str) -> dict`
    # - Dependencies: pandas, yaml → 需在 UC Function 環境中預裝
    # - Data Source: 將從 Delta Tables 讀取而非 CSV
    # - Trace: 使用 MLflow logging 取代 print statements
    """
    # ... implementation
```

這些註解將作為未來 Databricks 部署時的重要參考。

### 3. File: `run.py`

測試入口程式：

```python
#!/usr/bin/env python3
"""
<Flow Name> - Test Runner
"""

import argparse
from graph import graph

def main():
    parser = argparse.ArgumentParser(description='Run <flow_name> flow')
    parser.add_argument('--task', type=str, required=True, help='任務描述')
    parser.add_argument('--verbose', action='store_true', help='顯示詳細輸出')
    args = parser.parse_args()
    
    # 準備初始狀態
    initial_state = {
        "task": args.task,
        # 根據 FlowState 初始化其他欄位為 None
    }
    
    print(f"\n{'='*60}")
    print(f"執行 <Flow Name>")
    print(f"任務: {args.task}")
    print(f"{'='*60}\n")
    
    # 執行 graph
    result = graph.invoke(initial_state)
    
    print(f"\n{'='*60}")
    print("執行結果：")
    print(f"{'='*60}")
    
    if args.verbose:
        for key, value in result.items():
            print(f"{key}: {value}")
    else:
        # 只顯示重要欄位
        if result.get("error"):
            print(f"❌ 錯誤: {result['error']}")
        else:
            print("✅ 執行成功")
            # 根據 flow 特性顯示關鍵結果

if __name__ == "__main__":
    main()
```

## Agent Execution Example

當使用者說：`/spec-to-langchain take-data-test`

Agent 應該：

1. **列出 specs**：使用 `list_dir` 查看 `specs/` 目錄
2. **匹配名稱**：找到 `specs/take-data-test.flow_spec.yaml`
3. **讀取 spec**：使用 `read_file` 讀取完整 YAML
4. **分析結構**：
   - `run_name`: take-data-test
   - `goal`（完整流程）

```
1. Agent 執行任務 (Copilot Sandbox)
   → runs/<timestamp>-<name>/trace.ndjson
   
2. trace-to-flow (結構化)
   → specs/<name>.flow_spec.yaml
   
3. spec-to-langchain (程式化) ← 當前 Skill
   → flows/<name>/{__init__.py, graph.py, run.py}
   
4. 本地測試與驗證
   → python flows/<name>/run.py --task "..."
   → 確認邏輯正確性、識別可重用元件
   
5. [Future] Databricks 移植
   → Node Functions → UC Functions
   → FlowState → Job Parameters
   → Error Handling → Workflow Retry Logic
   → Local Data → Delta Tables
```

## Databricks Migration Mapping（移植對照）

當生成 LangGraph 程式碼時，Agent 應該思考以下對應關係：

| LangGraph Component | Databricks Component | Migration Action |
|---------------------|---------------------|------------------|
| `FlowState` (TypedDict) | Job Parameters / Delta Table Schema | 定義數據流轉結構 |
| `<phase>_node()` | UC Function | 封裝為可治理的工具 |
| `skills/` imports | UC Functions Library | 標準化工具集 |
| `print()` logging | MLflow Logging | 企業級追蹤 |
| Local CSV | Delta Tables | 生產數據源 |
| `graph.compile()` | Databricks Workflows | 編排邏輯 |
| Error handling | Retry Policies + Alerts | SLA 保證 |

## Dependencies

Flow 程式碼需要：
- Python 3.10+
- LangGraph (`pip install langgraph`)
- 其他依賴視 spec 中的 `dependencies` 而定

**🔍 移植檢查清單：**
- [ ] 所有 dependencies 是否在 Databricks Runtime 中可用？
- [ ] 是否有使用本地檔案路徑？（需改為 DBFS/Unity Catalog）
- [ ] 是否有 print() 需改為 MLflow logging？
- [ ] 哪些 node functions 可以共用？（抽取為 UC Functions）
- 實作錯誤處理
- 定義清晰的 State 結構
- 串接多個 phases

## Workflow

```
1. Agent 執行任務 → runs/<timestamp>-<name>/trace.ndjson
2. trace-to-flow   → specs/<name>.flow_spec.yaml
3. Agent 讀取 spec → 直接生成 flows/<name>/{__init__.py, graph.py, run.py}
4. 測試：python flows/<name>/run.py --task "..."
5. 完善：根據測試結果調整程式碼
```

## Dependencies

Flow 程式碼需要：
- Python 3.10+
- LangGraph (`pip install langgraph`)
- 其他依賴視 spec 中的 `dependencies` 而定
