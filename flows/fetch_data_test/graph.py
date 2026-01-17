"""
Fetch Data Test Flow - LangGraph Implementation

基於 specs/fetch-data-test.flow_spec.yaml 生成
目標：規劃數據撈取與檢查任務

Phases:
1. Understand - 檢查現有數據文件
2. Fetch - 讀取 data_fetch_profile.json 配置
3. Profile - 載入並檢查 CSV 數據
4. QualityCheck - 驗證數據完整性
5. Summarize - 生成數據摘要報告
"""

from typing import TypedDict
from langgraph.graph import StateGraph, START, END


# =============================================================================
# State Definition
# =============================================================================

class FlowState(TypedDict):
    """Flow 狀態"""
    task: str                          # 輸入：任務描述
    understand_result: dict | None      # Understand 結果
    fetch_result: dict | None      # Fetch 結果
    profile_result: dict | None      # Profile 結果
    qualitycheck_result: dict | None      # QualityCheck 結果
    summarize_result: dict | None      # Summarize 結果
    summary: str | None                # 最終摘要
    error: str | None                  # 錯誤訊息


# =============================================================================
# Node Functions
# =============================================================================

def understand_node(state: FlowState) -> dict:
    """
    Phase: Understand - 檢查現有數據文件
    """


    print(f"[Understand] 執行中...")

    # TODO: 實作 Understand 邏輯
    return {"understand_result": {"status": "done"}}
def fetch_node(state: FlowState) -> dict:
    """
    Phase: Fetch - 讀取 data_fetch_profile.json 配置
    """


    print(f"[Fetch] 執行中...")

    # TODO: 實作 Fetch 邏輯
    return {"fetch_result": {"status": "done"}}
def profile_node(state: FlowState) -> dict:
    """
    Phase: Profile - 載入並檢查 CSV 數據
    """


    print(f"[Profile] 執行中...")

    # TODO: 實作 Profile 邏輯
    return {"profile_result": {"status": "done"}}
def qualitycheck_node(state: FlowState) -> dict:
    """
    Phase: QualityCheck - 驗證數據完整性
    """


    print(f"[QualityCheck] 執行中...")

    # TODO: 實作 QualityCheck 邏輯
    return {"qualitycheck_result": {"status": "done"}}
def summarize_node(state: FlowState) -> dict:
    """
    Phase: Summarize - 生成數據摘要報告
    """


    print(f"[Summarize] 執行中...")

    # TODO: 實作 Summarize 邏輯
    return {"summarize_result": {"status": "done"}}


# =============================================================================
# Graph Construction
# =============================================================================

def build_graph() -> StateGraph:
    """建立 LangGraph 流程"""
    builder = StateGraph(FlowState)

    # 加入節點
    builder.add_node("understand", understand_node)
    builder.add_node("fetch", fetch_node)
    builder.add_node("profile", profile_node)
    builder.add_node("qualitycheck", qualitycheck_node)
    builder.add_node("summarize", summarize_node)

    # 加入邊
    builder.add_edge(START, "understand")
    builder.add_edge("understand", "fetch")
    builder.add_edge("fetch", "profile")
    builder.add_edge("profile", "qualitycheck")
    builder.add_edge("qualitycheck", "summarize")
    builder.add_edge("summarize", END)

    return builder.compile()


# 匯出編譯後的 graph
graph = build_graph()
