#!/usr/bin/env python3
"""
Take Data Test Flow - 測試執行入口

Usage:
    python flows/take_data_test/run.py
    python flows/take_data_test/run.py --task "撈 inventory 資料"
    python flows/take_data_test/run.py --task "load sales data"
"""

import argparse
import json
import sys
from pathlib import Path

# 確保可以 import graph
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from flows.take_data_test.graph import graph


def main():
    parser = argparse.ArgumentParser(description="Run take_data_test flow")
    parser.add_argument(
        "--task",
        default="撈取 sales 資料並確認品質",
        help="任務描述文字"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="顯示完整輸出"
    )

    args = parser.parse_args()

    print("=" * 60)
    print("Take Data Test Flow")
    print("=" * 60)
    print(f"Task: {args.task}")
    print("-" * 60)

    # 執行 flow
    initial_state = {
        "task": args.task,
        "dataset_key": None,
        "profile": None,
        "quality_report": None,
        "summary": None,
        "error": None,
    }

    result = graph.invoke(initial_state)

    print("-" * 60)
    print("Result:")
    print("-" * 60)

    if args.verbose:
        # 顯示完整結果
        print(json.dumps(result, ensure_ascii=False, indent=2, default=str))
    else:
        # 只顯示摘要
        print(f"Summary: {result.get('summary', 'N/A')}")
        if result.get("error"):
            print(f"Error: {result['error']}")

    print("=" * 60)

    return 0 if not result.get("error") else 1


if __name__ == "__main__":
    sys.exit(main())
