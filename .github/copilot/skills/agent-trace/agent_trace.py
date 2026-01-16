#!/usr/bin/env python3
"""
Agent Trace - 極簡 AI Agent 動作記錄工具
支援事件類型：plan, tool_search, tool_use, tool_result, prompt_search, 
              step_prepare, step_execute, strategy_shift, error, summary
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

# 找到專案根目錄（向上尋找 .github 目錄的父層）
def _find_project_root() -> Path:
    """找到專案根目錄"""
    current = Path(__file__).resolve()
    while current != current.parent:
        if (current / ".github").is_dir():
            return current
        current = current.parent
    # 如果找不到，預設為腳本上四層目錄
    return Path(__file__).resolve().parent.parent.parent.parent

RUNS_DIR = _find_project_root() / "runs"

# 支援的事件類型
EVENT_TYPES = {
    "plan",           # 計劃（列 3-8 步）
    "tool_search",    # 尋找工具/指令
    "tool_use",       # 使用工具
    "tool_result",    # 工具結果
    "prompt_search",  # 查詢 prompt/instruction
    "step_prepare",   # 準備執行步驟
    "step_execute",   # 執行步驟
    "strategy_shift", # 改變策略
    "error",          # 錯誤
    "summary",        # 任務摘要
}


def init(run_name: str) -> Path:
    """
    建立新的 run 資料夾與 trace.ndjson
    
    Args:
        run_name: 任務名稱
        
    Returns:
        run_dir: 新建立的 run 資料夾路徑
    """
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    # 清理 run_name 中的特殊字元
    safe_name = "".join(c if c.isalnum() or c in "-_" else "_" for c in run_name)
    run_dir = RUNS_DIR / f"{timestamp}-{safe_name}"
    run_dir.mkdir(parents=True, exist_ok=True)
    
    trace_file = run_dir / "trace.ndjson"
    trace_file.touch()
    
    # 寫入初始化事件
    log(run_dir, "init", f"Run '{run_name}' initialized", {"run_name": run_name})
    
    print(f"✓ Run initialized: {run_dir}")
    return run_dir


def log(run_dir: str | Path, event_type: str, message: str, data: dict | None = None) -> None:
    """
    追加一行事件到 trace.ndjson
    
    Args:
        run_dir: run 資料夾路徑
        event_type: 事件類型
        message: 事件訊息
        data: 額外資料（可選）
    """
    run_dir = Path(run_dir)
    trace_file = run_dir / "trace.ndjson"
    
    if not trace_file.exists():
        raise FileNotFoundError(f"trace.ndjson not found in {run_dir}")
    
    event = {
        "ts": datetime.now().isoformat(),
        "type": event_type,
        "message": message,
        "data": data or {},
    }
    
    with open(trace_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")
    
    # 簡潔輸出
    icon = _get_icon(event_type)
    print(f"{icon} [{event_type}] {message}")


def _get_icon(event_type: str) -> str:
    """取得事件類型對應的圖示"""
    icons = {
        "init": "🚀",
        "plan": "📋",
        "tool_search": "🔍",
        "tool_use": "🔧",
        "tool_result": "📤",
        "prompt_search": "📖",
        "step_prepare": "📝",
        "step_execute": "▶️",
        "strategy_shift": "🔄",
        "error": "❌",
        "summary": "✅",
    }
    return icons.get(event_type, "•")


def read_trace(run_dir: str | Path) -> list[dict]:
    """
    讀取 trace.ndjson 內容
    
    Args:
        run_dir: run 資料夾路徑
        
    Returns:
        事件列表
    """
    run_dir = Path(run_dir)
    trace_file = run_dir / "trace.ndjson"
    
    if not trace_file.exists():
        return []
    
    events = []
    with open(trace_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                events.append(json.loads(line))
    return events


def list_runs() -> list[Path]:
    """列出所有 run 資料夾"""
    if not RUNS_DIR.exists():
        return []
    return sorted(RUNS_DIR.iterdir(), reverse=True)


# CLI 介面
def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  agent_trace.py init <run_name>")
        print("  agent_trace.py log <run_dir> <type> <message> [data_json]")
        print("  agent_trace.py list")
        print("  agent_trace.py read <run_dir>")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == "init":
        if len(sys.argv) < 3:
            print("Error: run_name required")
            sys.exit(1)
        run_dir = init(sys.argv[2])
        print(run_dir)
        
    elif cmd == "log":
        if len(sys.argv) < 5:
            print("Error: run_dir, type, message required")
            sys.exit(1)
        run_dir = sys.argv[2]
        event_type = sys.argv[3]
        message = sys.argv[4]
        data = json.loads(sys.argv[5]) if len(sys.argv) > 5 else None
        log(run_dir, event_type, message, data)
        
    elif cmd == "list":
        runs = list_runs()
        if runs:
            for r in runs:
                print(r.name)
        else:
            print("No runs found")
            
    elif cmd == "read":
        if len(sys.argv) < 3:
            print("Error: run_dir required")
            sys.exit(1)
        events = read_trace(sys.argv[2])
        for e in events:
            print(json.dumps(e, ensure_ascii=False, indent=2))
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)


if __name__ == "__main__":
    main()
