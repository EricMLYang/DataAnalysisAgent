## Path1: Mosaic AI Agent Framework + LangChain + UC Function Toolkit
### 適合情境：
追求靈活性、高度流程控制，利用 Mosaic AI Agent Framework + LangChain，並以 Unity Catalog (UC) 中的 SQL 或 Python 函數作為工具調用基礎，是目前最受推崇的架構模式。
* 繼承了 LangChain 豐富的生態組件，也發揮 Databricks 在數據治理優勢 

### 關鍵庫的角色：databricks-langchain 與 UCFunctionToolkit
* databricks-langchain 庫將 Databricks 特定資源（如模型服務終點、向量搜索索引與 UC 函數）抽象化為 LangChain 可識別的標準組件。
傳統的 LangChain 工具定義往往需要在代碼中硬編碼邏輯與憑證，而 databricks-langchain 提供的 UCFunctionToolkit 則實現了工具的動態發現與自動封裝 。   

* UCFunctionToolkit 的技術核心在於其對 Unity Catalog 元數據的深度解析。當開發者在 UC 中定義了一個函數並為其撰寫了詳盡的註釋（COMMENT）後，該工具包會自動提取函數的簽名（Signature）與文檔說明，並將其轉化為 LLM 所需的工具描述語法。這使得 LLM 能夠精確理解每個工具的用途、所需參數類型及其業務含義，從而大幅降低了工具誤用的機率 。   


### 實作流程與代碼範例分析

1.在 Unity Catalog 中定義一個 Python UDF。  

```Python
# 在 Databricks 筆記本中定義 Python 函數
def extract_enterprise_keywords(text: str) -> list[str]:
    """
    從輸入文本中提取與企業業務相關的關鍵字，並過濾通用停用詞。
    
    參數:
        text: 需要進行分析的原始文本內容。
        
    返回:
        提取到的業務關鍵字列表。
    """
    from sklearn.feature_extraction.text import TfidfVectorizer
    import re
    # 函數體內部的依賴導入與邏輯處理...
    return ["keyword1", "keyword2"]
```
2. 用 DatabricksFunctionClient 將此 Python 定義註冊到 Unity Catalog。這一點至關重要，因為一旦註冊，該函數便受到 UC 的統一治理，包括權限控管與審計追蹤 

3. 開發者使用 UCFunctionToolkit 將其封裝為 LangChain 兼容的工具：   

```Python
from databricks_langchain.uc_ai import DatabricksFunctionClient, UCFunctionToolkit

# 初始化客戶端
client = DatabricksFunctionClient()

# 指定 UC 中的函數路徑
tool_names = ["main.default.extract_enterprise_keywords"]
toolkit = UCFunctionToolkit(function_names=tool_names)


## 將工具集成到 LangChain Agent 中
from langchain.agents import create_tool_calling_agent
from databricks_langchain import ChatDatabricks

llm = ChatDatabricks(endpoint="databricks-meta-llama-3-3-70b-instruct")
agent = create_tool_calling_agent(llm, toolkit.tools, prompt)
```

注意:
* [Create AI agent tools using Unity Catalog functions (legacy)](Create AI agent tools using Unity Catalog functions (legacy))



## Path2:
第三方框架多層抽象會帶來額外的延遲與版本維護的複雜度。
優勢是可快速產品化，劣勢是靈活度上或略有不足。預製模板雖省時，但若要實現非常定制化的交互邏輯，可能需要等待 Databricks 官方支持或繼續通過客製 MCP 服務擴展
Databricks 推出原生的 Mosaic AI 開發路徑，主要圍繞 AI Playground 與 Agent Bricks 展開 。   

### AI Playground：從快速原型到生產代碼的無縫橋樑
 * Low-Code 快速測試不同模型（如 Claude 3.5、Llama 3）對 UC 函數或向量索引的調用能力
 *  一鍵生成標準 Python 筆記本。該筆記本會自動封裝為 ResponsesAgent 接口，這是 Databricks 推薦的生產級代理簽名，支持 Token Streaming 與 Signature Inference，極大縮短構思到部署的週期 。   

### Agent Bricks：聲明式代理構建的「自動化工程師」
* 常見的 AI 應用（如文檔摘要、信息提），Agent Bricks這種聲明式開發模式，只需指定任務目標與數據來源，系統便會自動完成模型選擇、Prompt Optimization、超參數掃描 。   

* Agent Bricks 集成 Mosaic Research 的多項前沿技術，例如「測試時自適應優化」（Test-time Adaptive Optimization, TAO）與基於合成數據的微調技術。這使得構建出的 Agent 在處理特定領域（如法律文檔或醫療報告）時，其準確性與成本效益往往優於通用的 LangChain 實現 。

* 原生路徑利用 Mosaic AI Gateway 作為統一的控制平面（Control Plane）。所有的模型調用請求都會經過 Gateway 的治理，這不僅支持速率限制（Rate Limiting）以防止成本失控，還能配置自動備援（Fallback）機制。當高階模型（如 GPT-4）發生延遲或超時時，Gateway 能自動切換至低延遲的本地部署模型，確保業務連續性 。


## Path: 專業化與多代理協同架構案例
集成 LlamaIndex 的高級檢索能力，以及利用 AI/BI Genie 構建的多代理協作系統。

### LlamaIndex 的集成：極致的檢索精度
任務核心在於從海量、複雜的非結構數據取信息時，LlamaIndex 是許多架構師的首選。在 Databricks 上，常見的模式是利用 LlamaIndex 構建專門的「檢索代理」，然後將其作為一個工具集成到 Mosaic AI 的總控環境中 。   
LlamaIndex 的優勢在於對層次化文檔（如 PDF 中的複雜表格與巢狀結構）的處理能力。

### 多代理架構：AI/BI Genie 與 Supervisor 模式
將 AI/BI Genie 作為結構化數據查詢的子代理（Sub-agent）。

* 在一個典型的企業銷售助理案例中，系統架構如下：
  * 總控代理（Supervisor Agent）：利用 LangGraph 構建，負責解析用戶意圖。
  * Genie 代理：當問題涉及「上個季度的銷售額是多少？」時，總控將任務轉發給 Genie 。   
  * RAG 代理：當問題涉及「市場部對該產品的推廣策略是什麼？」時，總控轉發給基於向量搜索的 RAG 代理。
  * 結果整合：Genie 從 Delta Table 獲取數據，RAG 代理從 PDF 獲取策略，總控代理將兩者合成一份完整的市場表現與建議報告 。      



## references

* [Build an Autonomous AI Assistant with Mosaic AI Agent Framework](https://www.databricks.com/blog/build-autonomous-ai-assistant-mosaic-ai-agent-framework#:~:text=Code%20snippet%3A%20)