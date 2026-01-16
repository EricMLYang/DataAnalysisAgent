# Flow Spec to LangChain/LangGraph Development Plan

## Input

You will receive a Flow Spec YAML file that describes an Agent's execution trace. Use this to generate a structured development plan for implementing the same workflow in LangChain/LangGraph.

## Output Format

Generate a development plan with the following sections:

---

## 1. Goal

**Objective:** [One sentence describing the workflow's purpose]

**Inputs:**
- [List of inputs the workflow expects]

**Outputs:**
- [List of outputs the workflow produces]

---

## 2. Architecture Overview

Describe the high-level architecture:
- State management approach
- Graph structure (nodes and edges)
- Tool integration pattern

---

## 3. Node Design (LangGraph)

For each phase in the flow spec, define a node:

### Node: `{phase_name}`

- **Purpose:** [What this node does]
- **Input State:** [Expected state fields]
- **Output State:** [State fields it produces/modifies]
- **Tools Required:** [List of tools]
- **Dependencies:** [Python packages needed]

---

## 4. Edge Definitions

Define the graph edges:

```
START → node1 → node2 → ... → END
         ↓
    [conditional edges for error handling]
```

---

## 5. Error Handling

Based on `failure_modes` in the flow spec:

| Error Type | Detection | Recovery Action |
|------------|-----------|-----------------|
| [error] | [how to detect] | [recovery strategy] |

---

## 6. Tool Definitions

For each tool mentioned in the flow spec:

### Tool: `{tool_name}`

```python
# Tool signature and description
@tool
def tool_name(args) -> ReturnType:
    """Description"""
    pass
```

---

## 7. Testing Strategy

### Unit Tests
- [Test cases for individual nodes]

### Integration Tests
- [End-to-end test scenarios]

### Mock Data
- [How to use mock data for testing]

---

## 8. MVP Implementation

Minimal viable version that can be built first:

1. [Step 1]
2. [Step 2]
3. [Step 3]

---

## Example

Given this flow spec:

```yaml
run_name: take-data-test
goal: 撈取 mock 數據並確認狀況
phases:
  - name: Fetch
    steps:
      - 執行 data-fetch 撈取數據
    tools:
      - python
    dependencies:
      - pandas
    failure_modes:
      - error: ModuleNotFoundError
    recovery_playbook:
      - install pandas
```

Generate:

```markdown
## 1. Goal

**Objective:** Fetch mock data and verify its quality

**Inputs:**
- Task description text
- Dataset identifier (sales/inventory)

**Outputs:**
- data_fetch_profile.json (data profile)

## 3. Node Design

### Node: `fetch_data`

- **Purpose:** Load CSV data and generate profile
- **Input State:** `{"task": str, "dataset_key": str}`
- **Output State:** `{"profile": dict, "success": bool}`
- **Tools Required:** data_fetch_tool
- **Dependencies:** pandas

## 5. Error Handling

| Error Type | Detection | Recovery Action |
|------------|-----------|-----------------|
| ModuleNotFoundError | Import fails | Install missing package |
```

---

## Instructions

1. Read the provided Flow Spec YAML
2. Generate a complete development plan following the format above
3. Ensure all phases map to LangGraph nodes
4. Include concrete error handling based on failure_modes
5. Provide runnable code snippets where appropriate
6. Focus on practical, implementable steps
