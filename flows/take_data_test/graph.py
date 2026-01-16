"""
Take Data Test Flow - LangGraph Implementation

基於 specs/take-data-test.flow_spec.yaml 生成的 LangGraph 流程
目標：撈取 mock 數據並確認狀況

Phases:
1. Understand - 解析任務需求
2. Fetch - 執行 data-fetch 撈取數據
3. Profile - 分析數據 profile
4. QualityCheck - 檢視數據品質
5. Summarize - 總結數據狀況
"""

import sys
from pathlib import Path
from typing import TypedDict, Annotated

from langgraph.graph import StateGraph, START, END

# 加入專案根目錄到 path，以便 import skills
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / ".github" / "skills" / "data-fetch" / "scripts"))

from fetch import load_and_profile, parse_dataset_key


# =============================================================================
# State Definition
# =============================================================================

class FlowState(TypedDict):
    """Flow 狀態"""
    task: str                          # 輸入：任務描述
    dataset_key: str | None            # Understand 階段解析出的 dataset
    profile: dict | None               # Fetch 階段產生的 data profile
    quality_report: dict | None        # QualityCheck 階段產生的品質報告
    summary: str | None                # Summarize 階段產生的摘要
    error: str | None                  # 錯誤訊息（如有）


# =============================================================================
# Node Functions
# =============================================================================

def understand_node(state: FlowState) -> dict:
    """
    Phase: Understand - 解析任務需求

    從 task 文字中解析出要載入的 dataset key
    """
    task = state["task"]
    dataset_key = parse_dataset_key(task)

    print(f"[Understand] 任務: {task}")
    print(f"[Understand] 解析出 dataset_key: {dataset_key}")

    return {"dataset_key": dataset_key}


def fetch_node(state: FlowState) -> dict:
    """
    Phase: Fetch - 執行 data-fetch 撈取數據

    使用現有的 data-fetch skill 載入數據並生成 profile
    """
    task = state["task"]

    print(f"[Fetch] 開始載入數據...")

    try:
        profile = load_and_profile(task)
        print(f"[Fetch] 成功載入 {profile['rows']} 筆資料，{profile['cols']} 個欄位")
        return {"profile": profile, "error": None}
    except Exception as e:
        error_msg = f"載入數據失敗: {e}"
        print(f"[Fetch] {error_msg}")
        return {"profile": None, "error": error_msg}


def quality_check_node(state: FlowState) -> dict:
    """
    Phase: QualityCheck - 檢視數據品質

    分析 profile 中的 null counts 和資料品質
    """
    profile = state.get("profile")

    if not profile:
        return {"quality_report": {"status": "skipped", "reason": "no profile"}}

    null_counts = profile.get("null_counts", {})
    total_nulls = sum(null_counts.values())
    rows = profile.get("rows", 0)
    cols = profile.get("cols", 0)

    # 計算品質指標
    total_cells = rows * cols
    null_ratio = total_nulls / total_cells if total_cells > 0 else 0

    quality_report = {
        "status": "良好" if null_ratio == 0 else ("acceptable" if null_ratio < 0.05 else "需注意"),
        "total_nulls": total_nulls,
        "null_ratio": round(null_ratio * 100, 2),
        "null_by_column": null_counts,
        "has_timestamp": "min_ts" in profile
    }

    print(f"[QualityCheck] 品質狀態: {quality_report['status']}")
    print(f"[QualityCheck] 缺失值比例: {quality_report['null_ratio']}%")

    return {"quality_report": quality_report}


def summarize_node(state: FlowState) -> dict:
    """
    Phase: Summarize - 總結數據狀況

    整合所有資訊產生最終摘要
    """
    profile = state.get("profile")
    quality = state.get("quality_report")
    error = state.get("error")

    if error:
        summary = f"任務失敗: {error}"
    elif not profile:
        summary = "無法生成摘要：缺少數據 profile"
    else:
        # 建立摘要
        parts = [
            f"數據集: {profile.get('dataset_key', 'unknown')}",
            f"資料量: {profile.get('rows', 0)} 筆 x {profile.get('cols', 0)} 欄位",
        ]

        if quality:
            parts.append(f"品質狀態: {quality.get('status', 'unknown')}")

        if profile.get("min_ts") and profile.get("max_ts"):
            parts.append(f"時間範圍: {profile['min_ts'][:10]} 至 {profile['max_ts'][:10]}")

        summary = " | ".join(parts)

    print(f"[Summarize] {summary}")

    return {"summary": summary}


# =============================================================================
# Graph Construction
# =============================================================================

def build_graph() -> StateGraph:
    """
    建立 LangGraph 流程

    流程: START -> understand -> fetch -> quality_check -> summarize -> END
    """
    builder = StateGraph(FlowState)

    # 加入節點
    builder.add_node("understand", understand_node)
    builder.add_node("fetch", fetch_node)
    builder.add_node("quality_check", quality_check_node)
    builder.add_node("summarize", summarize_node)

    # 加入邊（線性流程）
    builder.add_edge(START, "understand")
    builder.add_edge("understand", "fetch")
    builder.add_edge("fetch", "quality_check")
    builder.add_edge("quality_check", "summarize")
    builder.add_edge("summarize", END)

    return builder.compile()


# 匯出編譯後的 graph
graph = build_graph()
