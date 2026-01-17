#!/usr/bin/env python3
"""
Fetch Data Test Flow - Test Runner

執行數據撈取與檢查任務的測試流程
"""

import argparse
from graph import graph

def main():
    parser = argparse.ArgumentParser(description='Run fetch-data-test flow')
    parser.add_argument('--task', type=str, required=True, help='任務描述')
    parser.add_argument('--verbose', action='store_true', help='顯示詳細輸出')
    args = parser.parse_args()
    
    # 準備初始狀態
    initial_state = {
        "task": args.task,
        "available_files": None,
        "config": None,
        "profile": None,
        "quality_report": None,
        "summary": None,
        "error": None
    }
    
    print(f"\n{'='*60}")
    print(f"執行 Fetch Data Test Flow")
    print(f"任務: {args.task}")
    print(f"{'='*60}\n")
    
    # 執行 graph
    result = graph.invoke(initial_state)
    
    print(f"\n{'='*60}")
    print("執行結果：")
    print(f"{'='*60}")
    
    if args.verbose:
        print("\n完整狀態：")
        for key, value in result.items():
            if value is not None:
                print(f"\n{key}:")
                print(f"  {value}")
    else:
        # 只顯示關鍵資訊
        if result.get("error"):
            print(f"\n❌ 錯誤: {result['error']}")
        else:
            print(f"\n✅ 執行成功\n")
            
            # 顯示摘要
            if result.get("summary"):
                print(result["summary"])
            
            # 顯示品質狀態
            if result.get("quality_report"):
                qr = result["quality_report"]
                status_emoji = "✅" if qr.get("status") == "pass" else "⚠️" if qr.get("status") == "warning" else "❌"
                print(f"\n品質檢查: {status_emoji} {qr.get('status', 'unknown').upper()}")

if __name__ == "__main__":
    main()
