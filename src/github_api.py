"""
GitHub API 資料獲取模組
負責從 GitHub 搜尋並獲取倉庫資訊
"""
import time
from typing import List, Optional
import pandas as pd
import requests
from src.config import GITHUB_TOKEN, GITHUB_API_URL, MAX_REPOS_PER_SEARCH


class GitHubAPIError(Exception):
    """GitHub API 錯誤"""
    pass


def fetch_repos_by_keyword(
    keyword: str,
    max_results: int = MAX_REPOS_PER_SEARCH,
    sort_by: str = 'stars',
    language: Optional[str] = None
) -> pd.DataFrame:
    """
    根據關鍵字搜尋 GitHub 倉庫並回傳 DataFrame
    
    Args:
        keyword: 搜尋關鍵字 (例如: "machine learning", "web framework")
        max_results: 最大結果數量 (預設 50，避免速率限制和 t-SNE 計算過慢)
        sort_by: 排序方式 ('stars', 'forks', 'updated')
        language: 篩選程式語言 (可選，例如: "Python", "JavaScript")
        
    Returns:
        包含以下欄位的 DataFrame:
        - name: 倉庫名稱
        - description: 倉庫描述
        - stars: 星星數量
        - url: 倉庫 URL
        - topics: 主題標籤 (列表)
        - language: 主要程式語言
        
    Raises:
        GitHubAPIError: API 請求失敗時拋出
    """
    if not GITHUB_TOKEN:
        raise GitHubAPIError(
            "缺少 GitHub Token！請在 .env 檔案中設定 GITHUB_TOKEN。\n"
            "取得方式：GitHub Settings > Developer settings > Personal access tokens"
        )
    
    # 構建搜尋查詢
    query = keyword
    if language:
        query += f" language:{language}"
    
    # API 參數
    headers = {
        'Authorization': f'token {GITHUB_TOKEN}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    params = {
        'q': query,
        'sort': sort_by,
        'order': 'desc',
        'per_page': min(max_results, 100)  # GitHub API 單頁最多 100 筆
    }
    
    try:
        # 發送 API 請求
        response = requests.get(
            f'{GITHUB_API_URL}/search/repositories',
            headers=headers,
            params=params,
            timeout=30
        )
        
        # 檢查速率限制
        remaining = int(response.headers.get('X-RateLimit-Remaining', 0))
        if remaining < 10:
            print(f"⚠️ 警告：GitHub API 剩餘請求次數僅剩 {remaining}")
        
        # 檢查回應狀態
        if response.status_code == 403:
            reset_time = int(response.headers.get('X-RateLimit-Reset', 0))
            wait_seconds = max(0, reset_time - time.time())
            raise GitHubAPIError(
                f"GitHub API 速率限制已達上限！\n"
                f"請等待 {int(wait_seconds / 60)} 分鐘後再試。"
            )
        
        response.raise_for_status()
        data = response.json()
        
        # 解析結果
        repos = []
        for item in data.get('items', [])[:max_results]:
            repos.append({
                'name': item.get('full_name', 'Unknown'),
                'description': item.get('description') or 'No description available',  # 處理空描述
                'stars': item.get('stargazers_count', 0),
                'url': item.get('html_url', ''),
                'topics': item.get('topics', []),
                'language': item.get('language', 'Unknown')
            })
        
        if not repos:
            print(f"⚠️ 未找到符合 '{keyword}' 的倉庫")
        
        return pd.DataFrame(repos)
    
    except requests.exceptions.Timeout:
        raise GitHubAPIError("請求超時！請檢查網路連接。")
    except requests.exceptions.RequestException as e:
        raise GitHubAPIError(f"API 請求失敗：{str(e)}")


def get_repo_details(owner: str, repo: str) -> dict:
    """
    取得單一倉庫的詳細資訊（未來擴展用）
    
    Args:
        owner: 倉庫擁有者
        repo: 倉庫名稱
        
    Returns:
        倉庫詳細資訊字典
    """
    headers = {
        'Authorization': f'token {GITHUB_TOKEN}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    response = requests.get(
        f'{GITHUB_API_URL}/repos/{owner}/{repo}',
        headers=headers,
        timeout=30
    )
    
    response.raise_for_status()
    return response.json()


if __name__ == '__main__':
    # 測試 API 功能
    print("🧪 測試 GitHub API 模組...")
    
    try:
        # 測試搜尋
        df = fetch_repos_by_keyword('machine learning', max_results=5)
        print(f"\n✅ 成功搜尋到 {len(df)} 個倉庫：")
        print(df[['name', 'stars', 'language']].to_string(index=False))
        
        # 檢查是否有空描述
        empty_desc = df[df['description'] == 'No description available']
        if not empty_desc.empty:
            print(f"\n📝 發現 {len(empty_desc)} 個倉庫沒有描述（已自動填充）")
        
    except GitHubAPIError as e:
        print(f"\n❌ 錯誤：{e}")
