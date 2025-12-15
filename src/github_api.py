"""GitHub API 資料獲取"""
import time
from typing import List, Optional
import pandas as pd
import requests
from src.config import GITHUB_TOKEN, GITHUB_API_URL, MAX_REPOS_PER_SEARCH


class GitHubAPIError(Exception):
    """錯誤類別"""
    pass


def fetch_repos_by_keyword(
    keyword: str,
    max_results: int = MAX_REPOS_PER_SEARCH,
    sort_by: str = 'stars',
    language: Optional[str] = None
) -> pd.DataFrame:
    """搜尋 GitHub 倉庫
    
    Args:
        keyword: 搜尋關鍵字
        max_results: 最大結果數
        sort_by: 排序方式
        language: 篩選語言
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
        'per_page': min(max_results, 100)
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
            print(f"警告：GitHub API 剩餘請求次數僅剩 {remaining}")
        
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
                'description': item.get('description') or 'No description available',
                'stars': item.get('stargazers_count', 0),
                'url': item.get('html_url', ''),
                'topics': item.get('topics', []),
                'language': item.get('language', 'Unknown')
            })
        
        if not repos:
            print(f"未找到符合 '{keyword}' 的倉庫")
        
        return pd.DataFrame(repos)
    
    except requests.exceptions.Timeout:
        raise GitHubAPIError("請求超時！請檢查網路連接。")
    except requests.exceptions.RequestException as e:
        raise GitHubAPIError(f"API 請求失敗：{str(e)}")


def get_repo_details(owner: str, repo: str) -> dict:
    """取得倉庫詳細資訊"""
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
    # 測試
    print("測試 GitHub API 模組...")
    
    try:
        # 測試搜尋
        df = fetch_repos_by_keyword('machine learning', max_results=5)
        print(f"\n成功搜尋到 {len(df)} 個倉庫：")
        print(df[['name', 'stars', 'language']].to_string(index=False))
        
        # 檢查是否有空描述
        empty_desc = df[df['description'] == 'No description available']
        if not empty_desc.empty:
            print(f"\n發現 {len(empty_desc)} 個倉庫沒有描述（已自動填充）")
        
    except GitHubAPIError as e:
        print(f"\n錯誤：{e}")
