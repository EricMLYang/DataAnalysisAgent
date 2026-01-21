"""
Skill Loader - 自動載入 .github/skills/ 中的所有技能並轉換為 LangChain Tools
"""
import re
import sys
from pathlib import Path
from typing import List, Dict, Any, Callable
from langchain_core.tools import tool
import importlib.util


def parse_skill_metadata(skill_md_path: Path) -> Dict[str, str]:
    """
    解析 SKILL.md 的 YAML frontmatter
    
    Returns:
        {'name': '...', 'description': '...'}
    """
    content = skill_md_path.read_text(encoding='utf-8')
    
    # 提取 YAML frontmatter
    match = re.search(r'^---\s*\n(.*?)\n---', content, re.DOTALL | re.MULTILINE)
    if not match:
        return {}
    
    frontmatter = match.group(1)
    metadata = {}
    
    # 簡單解析 name 和 description
    name_match = re.search(r'^name:\s*(.+)$', frontmatter, re.MULTILINE)
    desc_match = re.search(r'^description:\s*(.+)$', frontmatter, re.MULTILINE)
    
    if name_match:
        metadata['name'] = name_match.group(1).strip()
    if desc_match:
        metadata['description'] = desc_match.group(1).strip()
    
    return metadata


def find_skill_main_function(skill_dir: Path) -> tuple[Path, str]:
    """
    尋找 skill 的主要執行函數
    
    Returns:
        (python_file_path, function_name)
    """
    scripts_dir = skill_dir / "scripts"
    if not scripts_dir.exists():
        return None, None
    
    # 尋找 Python 檔案
    py_files = list(scripts_dir.glob("*.py"))
    if not py_files:
        return None, None
    
    # 優先尋找特定命名的檔案
    preferred_names = ['fetch.py', 'main.py', 'run.py', 'execute.py']
    for preferred in preferred_names:
        for py_file in py_files:
            if py_file.name == preferred:
                return py_file, "load_and_profile"  # data-fetch 的主函數
    
    # 否則返回第一個
    return py_files[0], "load_and_profile"


def create_skill_wrapper(skill_name: str, skill_description: str, 
                         python_file: Path, func_name: str) -> Callable:
    """
    為 skill 創建 wrapper function 並用 @tool 裝飾
    """
    # 動態 import 模組
    spec = importlib.util.spec_from_file_location(f"skill_{skill_name}", python_file)
    if not spec or not spec.loader:
        return None
    
    module = importlib.util.module_from_spec(spec)
    sys.modules[f"skill_{skill_name}"] = module
    
    try:
        spec.loader.exec_module(module)
    except Exception as e:
        print(f"⚠️  Failed to load skill '{skill_name}': {e}", file=sys.stderr)
        return None
    
    # 取得主函數
    if not hasattr(module, func_name):
        print(f"⚠️  Skill '{skill_name}' has no function '{func_name}'", file=sys.stderr)
        return None
    
    main_func = getattr(module, func_name)
    
    # 創建 wrapper（根據不同 skill 調整參數）
    if skill_name == "data-fetch":
        def skill_tool(task_text: str) -> str:
            """Load mock CSV datasets from mock_data/ based on task text and output a JSON profile for downstream analysis."""
            try:
                result = main_func(task_text)
                import json
                return json.dumps(result, ensure_ascii=False, indent=2)
            except Exception as e:
                return f"Error executing {skill_name}: {str(e)}"
        
        # 使用 skill_description 覆蓋 docstring
        skill_tool.__doc__ = skill_description
        wrapped_tool = tool(skill_tool)
        wrapped_tool.name = skill_name.replace("-", "_")
        return wrapped_tool
    
    # 通用 wrapper（其他 skills）
    def generic_skill_tool(input_text: str) -> str:
        """Execute skill with input text."""
        try:
            # 嘗試調用主函數
            result = main_func(input_text)
            if isinstance(result, dict):
                import json
                return json.dumps(result, ensure_ascii=False, indent=2)
            return str(result)
        except Exception as e:
            return f"Error executing {skill_name}: {str(e)}"
    
    generic_skill_tool.__doc__ = skill_description
    wrapped_tool = tool(generic_skill_tool)
    wrapped_tool.name = skill_name.replace("-", "_")
    return wrapped_tool


def load_skills(skills_dir: str = ".github/skills", 
                include_skills: List[str] = None) -> List:
    """
    自動載入所有 skills 並轉換為 LangChain Tools
    
    Args:
        skills_dir: skills 目錄路徑（相對於專案根目錄）
        include_skills: 只載入指定的 skills（None 表示全部載入）
    
    Returns:
        LangChain tools 列表
    """
    # 取得專案根目錄
    root_dir = Path(__file__).parent
    skills_path = root_dir / skills_dir
    
    if not skills_path.exists():
        print(f"⚠️  Skills directory not found: {skills_path}", file=sys.stderr)
        return []
    
    tools = []
    skill_dirs = [d for d in skills_path.iterdir() if d.is_dir()]
    
    for skill_dir in skill_dirs:
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.exists():
            continue
        
        # 解析 metadata
        metadata = parse_skill_metadata(skill_md)
        if not metadata.get('name'):
            continue
        
        skill_name = metadata['name']
        
        # 過濾不需要的 skills
        if include_skills and skill_name not in include_skills:
            continue
        
        skill_description = metadata.get('description', f'Execute {skill_name} skill')
        
        # 尋找主函數
        python_file, func_name = find_skill_main_function(skill_dir)
        if not python_file:
            print(f"⚠️  No Python script found for skill: {skill_name}", file=sys.stderr)
            continue
        
        # 創建 wrapper tool
        skill_tool = create_skill_wrapper(skill_name, skill_description, python_file, func_name)
        if skill_tool:
            tools.append(skill_tool)
            print(f"✅ Loaded skill: {skill_name}", file=sys.stderr)
    
    return tools


def load_skills_simple(include_skills: List[str] = None) -> List:
    """
    簡化版：只載入指定的幾個 skills（推薦用於測試）
    
    Args:
        include_skills: 要載入的 skill 名稱列表，例如 ['data-fetch']
    
    Returns:
        LangChain tools 列表
    """
    if include_skills is None:
        include_skills = ['data-fetch']  # 預設只載入 data-fetch
    
    return load_skills(include_skills=include_skills)


# 測試用
if __name__ == "__main__":
    print("🔍 掃描並載入 Skills...\n")
    tools = load_skills_simple(['data-fetch'])
    
    print(f"\n📦 成功載入 {len(tools)} 個工具:")
    for t in tools:
        print(f"  - {t.name}: {t.description}")
