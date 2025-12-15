"""
配置管理模組
負責從 .env 檔案或 Streamlit secrets 載入環境變數
"""
import os
from pathlib import Path
from typing import Optional

try:
    import streamlit as st
    STREAMLIT_AVAILABLE = True
except ImportError:
    STREAMLIT_AVAILABLE = False

# 嘗試載入 .env 檔案
try:
    from dotenv import load_dotenv
    # 載入專案根目錄的 .env 檔案
    env_path = Path(__file__).parent.parent / '.env'
    load_dotenv(dotenv_path=env_path)
except ImportError:
    pass


def get_config(key: str, default: Optional[str] = None) -> Optional[str]:
    """
    取得配置值，優先順序：
    1. Streamlit secrets (適合部署)
    2. 環境變數 (適合本地開發)
    3. 預設值
    
    Args:
        key: 配置鍵名
        default: 預設值
        
    Returns:
        配置值或 None
    """
    # 1. 嘗試從 Streamlit secrets 讀取
    if STREAMLIT_AVAILABLE and hasattr(st, 'secrets'):
        try:
            return st.secrets.get(key, None)
        except:
            pass
    
    # 2. 從環境變數讀取
    value = os.getenv(key)
    if value:
        return value
    
    # 3. 回傳預設值
    return default


# GitHub API 配置
GITHUB_TOKEN = get_config('GITHUB_TOKEN')
GITHUB_API_URL = 'https://api.github.com'
MAX_REPOS_PER_SEARCH = 50  # 限制搜尋結果數量，避免速率限制

# Embedding 配置
EMBEDDING_METHOD = get_config('EMBEDDING_METHOD', 'local')  # 'local' 或 'gemini'
GEMINI_API_KEY = get_config('GEMINI_API_KEY')

# 本地 Embedding 模型配置
LOCAL_EMBEDDING_MODEL = 'all-MiniLM-L6-v2'

# t-SNE 配置
TSNE_PERPLEXITY = 5  # 推薦值：樣本數的 1/10
TSNE_RANDOM_STATE = 42


def validate_config():
    """驗證必要的配置是否存在"""
    errors = []
    
    if not GITHUB_TOKEN:
        errors.append("缺少 GITHUB_TOKEN。請在 .env 檔案中設定或使用 Streamlit secrets。")
    
    if EMBEDDING_METHOD == 'gemini' and not GEMINI_API_KEY:
        errors.append("EMBEDDING_METHOD 設為 'gemini'，但缺少 GEMINI_API_KEY。")
    
    return errors


if __name__ == '__main__':
    # 測試配置載入
    print("配置檢查：")
    print(f"GitHub Token: {'已設定' if GITHUB_TOKEN else '未設定'}")
    print(f"Gemini API Key: {'已設定' if GEMINI_API_KEY else '未設定'}")
    print(f"Embedding 模式: {EMBEDDING_METHOD}")
    
    errors = validate_config()
    if errors:
        print("\n配置錯誤：")
        for error in errors:
            print(f"  {error}")
    else:
        print("\n配置正常！")
