#!/usr/bin/env python3
"""
Fetch Data Test Flow - 測試執行入口

Usage:
    python flows/fetch_data_test/run.py
    python flows/fetch_data_test/run.py --task "your task"
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from flows.fetch_data_test.graph import graph


def main():
    parser = argparse.ArgumentParser(description="Run fetch_data_test flow")
    parser.add_argument(
        "--task",
        default="規劃數據撈取與檢查任務",
        help="任務描述文字"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="顯示完整輸出"
    )

    args = parser.parse_args()

    print("=" * 60)
    print("Fetch Data Test Flow")
    print("=" * 60)
    print(f"Task: {args.task}")
    print("-" * 60)

    # 初始 state
    initial_state = {
        "task": args.task,
        "summary": None,
        "error": None,
    }

    result = graph.invoke(initial_state)

    print("-" * 60)
    print("Result:")
    print("-" * 60)

    if args.verbose:
        print(json.dumps(result, ensure_ascii=False, indent=2, default=str))
    else:
        print(f"Summary: {result.get('summary', 'N/A')}")
        if result.get("error"):
            print(f"Error: {result['error']}")

    print("=" * 60)

    return 0 if not result.get("error") else 1


if __name__ == "__main__":
    sys.exit(main())
