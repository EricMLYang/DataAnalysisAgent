"""
Fetch Data Test Flow - LangGraph Implementation

基於 specs/fetch-data-test.flow_spec.yaml 生成的 LangGraph 流程
目標：規劃數據撈取與檢查任務

Phases:
1. Understand - 檢查現有數據文件
2. Fetch - 讀取 data_fetch_profile.json 配置
3. Profile - 載入並檢查 CSV 數據
4. QualityCheck - 驗證數據完整性
5. Summarize - 生成數據摘要報告
"""

import sys
import json
from pathlib import Path
from typing import TypedDict

from langgraph.graph import StateGraph, START, END

# 加入專案根目錄到 path，以便 import skills
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / ".github" / "skills" / "data-fetch" / "scripts"))

try:
    from fetch import load_and_profile, parse_dataset_key
    FETCH_SKILL_AVAILABLE = True
except ImportError:
    FETCH_SKILL_AVAILABLE = False


# =============================================================================
# State Definition
# =============================================================================

class FlowState(TypedDict):
    """Flow 狀態"""
    task: str                          # 輸入：任務描述
    available_files: list[str] | None  # Understand 階段發現的檔案
    config: dict | None                # Fetch 階段讀取的配置
    profile: dict | None               # Profile 階段產生的數據 profile
    quality_report: dict | None        # QualityCheck 階段產生的品質報告
    summary: str | None                # Summarize 階段產生的摘要
    error: str | None                  # 錯誤訊息（如有）


# =============================================================================
# Node Functions
# =============================================================================

def understand_node(state: FlowState) -> dict:
    """
    Phase: Understand - 檢查現有數據文件
    
    Steps:
    - 檢查現有數據文件
    
    # 🏢 Databricks Migration Notes:
    # - 此 node 可封裝為 UC Function: `uc.data.list_available_datasets() -> list[str]`
    # - Data Source: 將從 Unity Catalog 查詢 Delta Tables 而非本地檔案系統
    # - Permissions: 需要 USAGE 權限在 catalog/schema
    # - Trace: 使用 MLflow logging 取代 print statements
    """
    task = state["task"]
    
    print(f"[Understand] 任務: {task}")
    print(f"[Understand] 檢查可用的數據文件...")
    
    # 檢查 mock_data 目錄
    mock_data_dir = PROJECT_ROOT / "mock_data"
    available_files = []
    
    if mock_data_dir.exists():
        available_files = [f.name for f in mock_data_dir.glob("*.csv")]
        print(f"[Understand] 發現 {len(available_files)} 個 CSV 檔案: {available_files}")
    else:
        print(f"[Understand] mock_data 目錄不存在")
    
    # 檢查是否有 data_fetch_profile.json
    profile_path = PROJECT_ROOT / "data_fetch_profile.json"
    if profile_path.exists():
        print(f"[Understand] 發現現有 profile 檔案")
    
    return {
        "available_files": available_files,
        "error": None
    }


def fetch_node(state: FlowState) -> dict:
    """
    Phase: Fetch - 讀取 data_fetch_profile.json 配置
    
    Steps:
    - 讀取 data_fetch_profile.json 配置
    
    Failure Modes:
    - ModuleNotFoundError: 嘗試載入 pandas 分析數據失敗
    
    Recovery:
    - 從 pandas 數據分析改為基於檔案的基本檢查（pandas 未安裝時）
    
    # 🏢 Databricks Migration Notes:
    # - 此 node 可封裝為 UC Function: `uc.data.load_config(config_path: str) -> dict`
    # - Data Source: 將從 DBFS 或 Unity Catalog Volumes 讀取配置檔
    # - Dependencies: json (標準庫，無需特別處理)
    # - Error Handling: 使用 Databricks Workflows 的 retry policy
    # - Trace: MLflow 記錄配置內容和載入時間
    """
    print(f"[Fetch] 讀取數據配置...")
    
    profile_path = PROJECT_ROOT / "data_fetch_profile.json"
    
    if not profile_path.exists():
        print(f"[Fetch] 未找到 data_fetch_profile.json，嘗試生成...")
        
        # Recovery: 如果 pandas 不可用，使用基本檔案檢查
        if not FETCH_SKILL_AVAILABLE:
            error_msg = "data-fetch skill 不可用，且無現有配置"
            print(f"[Fetch] ❌ {error_msg}")
            return {
                "config": None,
                "error": error_msg
            }
        
        # 嘗試使用 data-fetch skill
        try:
            task = state["task"]
            profile = load_and_profile(task)
            config = {"profile": profile, "source": "generated"}
            print(f"[Fetch] ✅ 生成新的 profile")
        except Exception as e:
            error_msg = f"生成 profile 失敗: {e}"
            print(f"[Fetch] ❌ {error_msg}")
            return {
                "config": None,
                "error": error_msg
            }
    else:
        # 讀取現有配置
        try:
            with open(profile_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            print(f"[Fetch] ✅ 讀取現有配置成功")
        except Exception as e:
            error_msg = f"讀取配置失敗: {e}"
            print(f"[Fetch] ❌ {error_msg}")
            return {
                "config": None,
                "error": error_msg
            }
    
    return {
        "config": config,
        "error": None
    }


def profile_node(state: FlowState) -> dict:
    """
    Phase: Profile - 載入並檢查 CSV 數據
    
    Steps:
    - 載入並檢查 CSV 數據
    
    # 🏢 Databricks Migration Notes:
    # - 此 node 可封裝為 UC Function: `uc.data.profile_dataset(dataset_name: str) -> dict`
    # - Data Source: 使用 Spark DataFrames 讀取 Delta Tables
    # - Statistics: 使用 Spark SQL 的 DESCRIBE、ANALYZE TABLE 指令
    # - Performance: 對大數據集使用取樣分析 (TABLESAMPLE)
    # - Trace: MLflow 記錄 profile 統計資訊和執行時間
    """
    config = state.get("config")
    
    print(f"[Profile] 分析數據 profile...")
    
    if not config:
        print(f"[Profile] ⚠️  無配置可分析，跳過")
        return {"profile": None}
    
    # 從配置中提取 profile 資訊
    if "profile" in config:
        profile = config["profile"]
    elif "dataset" in config:
        profile = config
    else:
        profile = config
    
    print(f"[Profile] ✅ Profile 資訊:")
    if isinstance(profile, dict):
        for key in ["dataset", "rows", "cols", "columns"]:
            if key in profile:
                print(f"  - {key}: {profile[key]}")
    
    return {
        "profile": profile,
        "error": None
    }


def quality_check_node(state: FlowState) -> dict:
    """
    Phase: QualityCheck - 驗證數據完整性
    
    Steps:
    - 驗證數據完整性
    
    # 🏢 Databricks Migration Notes:
    # - 此 node 可封裝為 UC Function: `uc.data.quality_check(profile: dict) -> dict`
    # - Integration: 整合 Databricks Lakehouse Monitoring 進行自動品質監控
    # - Metrics: 定義品質 SLA (null_ratio < 5%, completeness > 95%)
    # - Alerts: 品質不達標時透過 Databricks Alerts 通知
    # - Trace: MLflow 記錄品質指標和閾值比較結果
    """
    profile = state.get("profile")
    
    print(f"[QualityCheck] 檢查數據品質...")
    
    if not profile:
        return {
            "quality_report": {
                "status": "skipped",
                "reason": "no profile available"
            }
        }
    
    # 執行品質檢查
    quality_report = {
        "status": "unknown",
        "checks": []
    }
    
    # 檢查 1: 數據列數
    if isinstance(profile, dict) and "rows" in profile:
        rows = profile["rows"]
        if rows > 0:
            quality_report["checks"].append({
                "name": "row_count",
                "status": "pass",
                "value": rows
            })
        else:
            quality_report["checks"].append({
                "name": "row_count",
                "status": "fail",
                "value": rows,
                "message": "數據為空"
            })
    
    # 檢查 2: Null 值比例
    if isinstance(profile, dict) and "null_counts" in profile:
        null_counts = profile["null_counts"]
        total_nulls = sum(null_counts.values())
        rows = profile.get("rows", 0)
        cols = profile.get("cols", 0)
        
        if rows > 0 and cols > 0:
            null_ratio = total_nulls / (rows * cols)
            quality_report["checks"].append({
                "name": "null_ratio",
                "status": "pass" if null_ratio < 0.05 else "warning",
                "value": f"{null_ratio:.2%}",
                "threshold": "< 5%"
            })
    
    # 判斷整體狀態
    if all(check["status"] == "pass" for check in quality_report["checks"]):
        quality_report["status"] = "pass"
    elif any(check["status"] == "fail" for check in quality_report["checks"]):
        quality_report["status"] = "fail"
    else:
        quality_report["status"] = "warning"
    
    print(f"[QualityCheck] ✅ 品質檢查完成: {quality_report['status']}")
    for check in quality_report["checks"]:
        print(f"  - {check['name']}: {check['status']} ({check.get('value', 'N/A')})")
    
    return {
        "quality_report": quality_report,
        "error": None
    }


def summarize_node(state: FlowState) -> dict:
    """
    Phase: Summarize - 生成數據摘要報告
    
    Steps:
    - 生成數據摘要報告
    
    # 🏢 Databricks Migration Notes:
    # - 此 node 可封裝為 UC Function: `uc.reporting.generate_summary(state: dict) -> str`
    # - Output: 將摘要寫入 Delta Table 或 DBFS 而非本地檔案
    # - Template: 使用 Databricks SQL 的 Dashboard 或 Markdown widgets
    # - Distribution: 透過 Databricks Jobs 的 email notification 發送報告
    # - Trace: MLflow 記錄摘要生成時間和內容長度
    """
    profile = state.get("profile")
    quality_report = state.get("quality_report")
    
    print(f"[Summarize] 生成數據摘要...")
    
    summary_lines = ["## 數據分析摘要\n"]
    
    # 任務資訊
    summary_lines.append(f"**任務:** {state['task']}\n")
    
    # Profile 摘要
    if profile and isinstance(profile, dict):
        summary_lines.append("### 數據概覽")
        if "dataset" in profile:
            summary_lines.append(f"- 數據集: {profile['dataset']}")
        if "rows" in profile:
            summary_lines.append(f"- 總列數: {profile['rows']:,}")
        if "cols" in profile:
            summary_lines.append(f"- 總欄位數: {profile['cols']}")
        if "columns" in profile:
            summary_lines.append(f"- 欄位名稱: {', '.join(profile['columns'])}")
        summary_lines.append("")
    
    # 品質報告摘要
    if quality_report and isinstance(quality_report, dict):
        summary_lines.append("### 品質檢查")
        summary_lines.append(f"- 整體狀態: {quality_report.get('status', 'unknown').upper()}")
        
        if "checks" in quality_report:
            for check in quality_report["checks"]:
                status_emoji = "✅" if check["status"] == "pass" else "⚠️" if check["status"] == "warning" else "❌"
                summary_lines.append(f"- {check['name']}: {status_emoji} {check.get('value', 'N/A')}")
        summary_lines.append("")
    
    # 錯誤資訊
    if state.get("error"):
        summary_lines.append("### ⚠️ 錯誤")
        summary_lines.append(f"```\n{state['error']}\n```\n")
    
    summary = "\n".join(summary_lines)
    
    print(f"[Summarize] ✅ 摘要生成完成 ({len(summary)} 字元)")
    
    return {
        "summary": summary,
        "error": None
    }


# =============================================================================
# Graph Construction
# =============================================================================

def build_graph() -> StateGraph:
    """
    構建 LangGraph 流程圖
    
    # 🏢 Databricks Migration Notes:
    # - Graph Structure: 可轉換為 Databricks Workflows 的 Task Dependencies
    # - Parallel Execution: 識別可平行執行的 nodes（目前為線性流程）
    # - Conditional Routing: 根據 error 狀態決定是否跳過後續 nodes
    # - Retry Logic: 每個 node 對應一個 Databricks Task 的 retry policy
    # - Monitoring: 使用 Databricks Job Runs 追蹤整體 workflow 執行狀態
    """
    graph = StateGraph(FlowState)
    
    # 加入所有 phase nodes
    graph.add_node("understand", understand_node)
    graph.add_node("fetch", fetch_node)
    graph.add_node("profile", profile_node)
    graph.add_node("quality_check", quality_check_node)
    graph.add_node("summarize", summarize_node)
    
    # 線性連接所有 phases
    graph.add_edge(START, "understand")
    graph.add_edge("understand", "fetch")
    graph.add_edge("fetch", "profile")
    graph.add_edge("profile", "quality_check")
    graph.add_edge("quality_check", "summarize")
    graph.add_edge("summarize", END)
    
    return graph.compile()


# 建立可匯出的 graph instance
graph = build_graph()
