---
name: spec-to-langchain
description: Generate LangGraph skeleton code from Flow Spec YAML files.
---

# Spec to LangChain Skill

## What This Skill Does

從 `specs/*.yaml` Flow Spec 檔案生成 LangGraph 骨架程式碼，包含：
- `graph.py` - LangGraph 主邏輯（State、Nodes、Graph）
- `run.py` - 測試執行入口
- `__init__.py` - 模組匯出

## When to Use

當你已經有 Flow Spec（透過 `trace-to-flow` skill 產生）並想要生成對應的 LangChain/LangGraph 程式碼時。

## Usage

### 列出可用的 Specs

```bash
python3 .github/skills/spec-to-langchain/scripts/generate.py list
```

### 生成 Flow 程式碼

```bash
# 從 spec 名稱生成
python3 .github/skills/spec-to-langchain/scripts/generate.py generate take-data-test

# 預覽（不寫入檔案）
python3 .github/skills/spec-to-langchain/scripts/generate.py generate take-data-test --dry-run

# 強制覆寫已存在的 flow
python3 .github/skills/spec-to-langchain/scripts/generate.py generate take-data-test --force
```

## Output Structure

```
flows/
└── <flow_name>/
    ├── __init__.py    # 模組匯出
    ├── graph.py       # LangGraph 定義
    └── run.py         # 測試入口
```

## Generated Code

### graph.py

- **FlowState**: 根據 spec 的 phases 和 outputs 生成的 TypedDict
- **Node Functions**: 每個 phase 對應一個 `<phase>_node()` 函數
- **Graph**: 線性連接所有 nodes 的 StateGraph

### run.py

- CLI 工具，可指定 `--task` 參數
- 支援 `--verbose` 顯示完整輸出

## Workflow

```
1. Agent 執行任務 → runs/<timestamp>-<name>/trace.ndjson
2. trace-to-flow   → specs/<name>.flow_spec.yaml
3. spec-to-langchain → flows/<name>/
4. 手動完善 graph.py 中的 TODO 邏輯
5. 測試：python flows/<name>/run.py
```

## Example

```bash
# 1. 列出 specs
python3 .github/skills/spec-to-langchain/scripts/generate.py list
# Output:
#   Available specs:
#     - take-data-test

# 2. 生成 flow（預覽）
python3 .github/skills/spec-to-langchain/scripts/generate.py generate take-data-test --dry-run
# Output:
#   [Dry Run] Would create: flows/take_data_test/
#     - __init__.py (67 bytes)
#     - graph.py (2048 bytes)
#     - run.py (1024 bytes)

# 3. 實際生成
python3 .github/skills/spec-to-langchain/scripts/generate.py generate take-data-test
# Output:
#   Created: flows/take_data_test/__init__.py
#   Created: flows/take_data_test/graph.py
#   Created: flows/take_data_test/run.py
```

## Dependencies

- Python 3.10+
- PyYAML (`pip install pyyaml`)
- LangGraph (`pip install langgraph`)
