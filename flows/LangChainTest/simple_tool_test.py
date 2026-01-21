"""最簡單的 LangChain 工具選擇範例 - 整合 Skill Loader"""
import sys
from pathlib import Path

# 加入專案根目錄到 Python path
root_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_dir))

from langchain_core.tools import tool
from langchain_openai import AzureChatOpenAI
import yaml
from skill_loader import load_skills_simple

# 載入設定
with open(root_dir / "config" / "secret.yml") as f:
    config = yaml.safe_load(f)

# 定義簡單工具
@tool
def calculator(expression: str) -> str:
    """用於計算數學表達式，例如：2+2, 10*5"""
    try:
        result = eval(expression)
        return f"計算結果: {result}"
    except:
        return "計算錯誤"

@tool
def get_weather(city: str) -> str:
    """查詢指定城市的天氣"""
    return f"{city}的天氣是晴天，溫度25度"

@tool
def search_web(query: str) -> str:
    """在網路上搜尋資訊"""
    return f"搜尋 '{query}' 的結果..."

# 設定 LLM
llm = AzureChatOpenAI(
    azure_endpoint=config["API_BASE"],
    api_key=config["API_KEY"],
    api_version=config["API_VERSION"],
    deployment_name=config["DEPLOYMENT_NAME"],
    temperature=0
)

print("\n🔄 載入技能中...")
print("-" * 60)

# 載入手動定義的工具
manual_tools = [calculator, get_weather, search_web]

# 自動載入 skills（目前只載入 data-fetch）
skill_tools = load_skills_simple(['data-fetch'])

# 合併所有工具
all_tools = manual_tools + skill_tools

print(f"✅ 總共載入 {len(all_tools)} 個工具")
print("-" * 60)

# 綁定工具
llm_with_tools = llm.bind_tools(all_tools)

print("\n" + "=" * 60)
print("🤖 LangChain 工具選擇測試 - 互動模式（含 Skills）")
print("=" * 60)
print("可用工具:")
print("  📊 calculator - 計算數學表達式")
print("  🌤️  get_weather - 查詢城市天氣")
print("  🔍 search_web - 網路搜尋")
for tool in skill_tools:
    print(f"  🔧 {tool.name} - {tool.description[:50]}...")
print("\n輸入 'exit' 或 'quit' 結束程式\n")

# 互動迴圈
while True:
    question = input("👤 請輸入問題: ").strip()
    
    if question.lower() in ['exit', 'quit', '']:
        print("👋 再見！")
        break
    
    print("-" * 60)
    
    # 調用 LLM
    response = llm_with_tools.invoke(question)
    
    # 檢查是否選擇了工具
    if response.tool_calls:
        for tool_call in response.tool_calls:
            print(f"✅ 選擇的工具: {tool_call['name']}")
            print(f"   參數: {tool_call['args']}")
    else:
        print("❌ 沒有選擇工具")
        print(f"   回答: {response.content}")
    
    print()
