#!/usr/bin/env python3
"""
Spec to LangChain Code Generator

從 Flow Spec YAML 生成 LangGraph 骨架程式碼
"""

import argparse
import sys
from pathlib import Path
from textwrap import dedent

try:
    import yaml
except ImportError:
    print("Error: PyYAML not installed. Run: pip install pyyaml", file=sys.stderr)
    sys.exit(1)


# =============================================================================
# Templates
# =============================================================================

INIT_TEMPLATE = '''from .graph import graph, build_graph

__all__ = ["graph", "build_graph"]
'''


def generate_graph_template(spec: dict) -> str:
    """生成 graph.py 內容"""
    run_name = spec.get("run_name", "unknown")
    goal = spec.get("goal", "")
    phases = spec.get("phases", [])

    # 生成 phase 說明
    phase_docs = "\n".join([f"{i+1}. {p['name']} - {p['steps'][0] if p.get('steps') else ''}"
                           for i, p in enumerate(phases)])

    # 生成 State 欄位
    state_fields = [
        'task: str                          # 輸入：任務描述',
    ]
    for phase in phases:
        name_lower = phase["name"].lower()
        if phase.get("outputs"):
            for output in phase["outputs"]:
                field_name = output.replace(".json", "").replace("-", "_")
                state_fields.append(f'{field_name}: dict | None            # {phase["name"]} 輸出')
        else:
            state_fields.append(f'{name_lower}_result: dict | None      # {phase["name"]} 結果')
    state_fields.append('summary: str | None                # 最終摘要')
    state_fields.append('error: str | None                  # 錯誤訊息')

    # 生成 node 函數
    node_functions = []
    for phase in phases:
        name = phase["name"]
        name_lower = name.lower()
        steps = phase.get("steps", [""])
        tools = phase.get("tools", [])
        outputs = phase.get("outputs", [])

        tool_comment = f"    # Tools: {', '.join(tools)}" if tools else ""
        output_comment = f"    # Outputs: {', '.join(outputs)}" if outputs else ""

        node_func = f'''
def {name_lower}_node(state: FlowState) -> dict:
    """
    Phase: {name} - {steps[0] if steps else ''}
    """
{tool_comment}
{output_comment}
    print(f"[{name}] 執行中...")

    # TODO: 實作 {name} 邏輯
    return {{"{name_lower}_result": {{"status": "done"}}}}
'''
        node_functions.append(node_func.strip())

    # 生成 add_node 呼叫
    add_nodes = "\n    ".join([f'builder.add_node("{p["name"].lower()}", {p["name"].lower()}_node)'
                               for p in phases])

    # 生成 add_edge 呼叫
    edges = ["builder.add_edge(START, \"{}\")".format(phases[0]["name"].lower())]
    for i in range(len(phases) - 1):
        edges.append(f'builder.add_edge("{phases[i]["name"].lower()}", "{phases[i+1]["name"].lower()}")')
    edges.append(f'builder.add_edge("{phases[-1]["name"].lower()}", END)')
    add_edges = "\n    ".join(edges)

    template = f'''"""
{run_name.replace("-", " ").title()} Flow - LangGraph Implementation

基於 specs/{run_name}.flow_spec.yaml 生成
目標：{goal}

Phases:
{phase_docs}
"""

from typing import TypedDict
from langgraph.graph import StateGraph, START, END


# =============================================================================
# State Definition
# =============================================================================

class FlowState(TypedDict):
    """Flow 狀態"""
    {(chr(10) + "    ").join(state_fields)}


# =============================================================================
# Node Functions
# =============================================================================

{chr(10).join(node_functions)}


# =============================================================================
# Graph Construction
# =============================================================================

def build_graph() -> StateGraph:
    """建立 LangGraph 流程"""
    builder = StateGraph(FlowState)

    # 加入節點
    {add_nodes}

    # 加入邊
    {add_edges}

    return builder.compile()


# 匯出編譯後的 graph
graph = build_graph()
'''
    return template


def generate_run_template(spec: dict) -> str:
    """生成 run.py 內容"""
    run_name = spec.get("run_name", "unknown")
    flow_name = run_name.replace("-", "_")
    goal = spec.get("goal", "")

    template = f'''#!/usr/bin/env python3
"""
{run_name.replace("-", " ").title()} Flow - 測試執行入口

Usage:
    python flows/{flow_name}/run.py
    python flows/{flow_name}/run.py --task "your task"
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from flows.{flow_name}.graph import graph


def main():
    parser = argparse.ArgumentParser(description="Run {flow_name} flow")
    parser.add_argument(
        "--task",
        default="{goal}",
        help="任務描述文字"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="顯示完整輸出"
    )

    args = parser.parse_args()

    print("=" * 60)
    print("{run_name.replace("-", " ").title()} Flow")
    print("=" * 60)
    print(f"Task: {{args.task}}")
    print("-" * 60)

    # 初始 state
    initial_state = {{
        "task": args.task,
        "summary": None,
        "error": None,
    }}

    result = graph.invoke(initial_state)

    print("-" * 60)
    print("Result:")
    print("-" * 60)

    if args.verbose:
        print(json.dumps(result, ensure_ascii=False, indent=2, default=str))
    else:
        print(f"Summary: {{result.get('summary', 'N/A')}}")
        if result.get("error"):
            print(f"Error: {{result['error']}}")

    print("=" * 60)

    return 0 if not result.get("error") else 1


if __name__ == "__main__":
    sys.exit(main())
'''
    return template


# =============================================================================
# Main Logic
# =============================================================================

def find_spec(spec_identifier: str, specs_dir: Path) -> Path | None:
    """找到 spec 檔案"""
    # 直接路徑
    if Path(spec_identifier).exists():
        return Path(spec_identifier)

    # 在 specs/ 目錄搜尋
    for spec_file in specs_dir.glob("*.yaml"):
        if spec_identifier in spec_file.stem:
            return spec_file

    for spec_file in specs_dir.glob("*.yml"):
        if spec_identifier in spec_file.stem:
            return spec_file

    return None


def list_specs(specs_dir: Path) -> list[str]:
    """列出所有 specs"""
    specs = []
    for ext in ["*.yaml", "*.yml"]:
        for f in specs_dir.glob(ext):
            specs.append(f.stem)
    return sorted(specs)


def generate_flow(spec_path: Path, flows_dir: Path, dry_run: bool = False) -> Path:
    """從 spec 生成 flow 程式碼"""
    with open(spec_path, "r", encoding="utf-8") as f:
        spec = yaml.safe_load(f)

    run_name = spec.get("run_name", spec_path.stem.replace(".flow_spec", ""))
    flow_name = run_name.replace("-", "_")
    flow_dir = flows_dir / flow_name

    files = {
        "__init__.py": INIT_TEMPLATE,
        "graph.py": generate_graph_template(spec),
        "run.py": generate_run_template(spec),
    }

    if dry_run:
        print(f"[Dry Run] Would create: {flow_dir}/")
        for filename, content in files.items():
            print(f"  - {filename} ({len(content)} bytes)")
        return flow_dir

    # 建立目錄
    flow_dir.mkdir(parents=True, exist_ok=True)

    # 寫入檔案
    for filename, content in files.items():
        file_path = flow_dir / filename
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Created: {file_path}")

    return flow_dir


def main():
    parser = argparse.ArgumentParser(
        description="Generate LangGraph code from Flow Spec YAML"
    )
    parser.add_argument(
        "command",
        choices=["generate", "list"],
        help="Command: generate or list"
    )
    parser.add_argument(
        "spec",
        nargs="?",
        help="Spec name or path (for generate command)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview without writing files"
    )
    parser.add_argument(
        "--force", "-f",
        action="store_true",
        help="Overwrite existing flow"
    )

    args = parser.parse_args()

    # 專案路徑
    script_dir = Path(__file__).resolve().parent
    project_root = script_dir.parent.parent.parent.parent
    specs_dir = project_root / "specs"
    flows_dir = project_root / "flows"

    if args.command == "list":
        specs = list_specs(specs_dir)
        if specs:
            print("Available specs:")
            for spec in specs:
                print(f"  - {spec}")
        else:
            print("No specs found in specs/")
        return 0

    # Generate command
    if not args.spec:
        print("Error: spec name required for generate command", file=sys.stderr)
        return 1

    spec_path = find_spec(args.spec, specs_dir)
    if not spec_path:
        print(f"Error: Spec '{args.spec}' not found", file=sys.stderr)
        print("Available specs:", file=sys.stderr)
        for spec in list_specs(specs_dir):
            print(f"  - {spec}", file=sys.stderr)
        return 1

    # 檢查是否已存在
    with open(spec_path, "r", encoding="utf-8") as f:
        spec = yaml.safe_load(f)
    run_name = spec.get("run_name", spec_path.stem.replace(".flow_spec", ""))
    flow_name = run_name.replace("-", "_")
    flow_dir = flows_dir / flow_name

    if flow_dir.exists() and not args.force and not args.dry_run:
        print(f"Error: Flow '{flow_name}' already exists. Use --force to overwrite.", file=sys.stderr)
        return 1

    print(f"Generating flow from: {spec_path}")
    generate_flow(spec_path, flows_dir, dry_run=args.dry_run)

    if not args.dry_run:
        print(f"\nFlow generated at: {flow_dir}")
        print(f"Run with: python flows/{flow_name}/run.py")

    return 0


if __name__ == "__main__":
    sys.exit(main())
