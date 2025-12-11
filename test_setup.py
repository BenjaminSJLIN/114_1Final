"""
測試腳本 - 驗證所有模組是否正常運作
執行此腳本以確保環境設定正確
"""
import sys

def test_imports():
    """測試所有必要的套件是否可以正常匯入"""
    print("=" * 60)
    print("測試 1: 檢查套件安裝")
    print("=" * 60)
    
    required_packages = [
        ('pandas', 'Pandas'),
        ('numpy', 'NumPy'),
        ('requests', 'Requests'),
        ('sklearn', 'scikit-learn'),
        ('sentence_transformers', 'sentence-transformers'),
        ('plotly', 'Plotly'),
        ('streamlit', 'Streamlit'),
        ('dotenv', 'python-dotenv'),
    ]
    
    optional_packages = [
        ('google.generativeai', 'google-generativeai (Gemini API)'),
    ]
    
    all_ok = True
    
    for package, name in required_packages:
        try:
            __import__(package)
            print(f"✅ {name}")
        except ImportError:
            print(f"❌ {name} - 請執行: pip install {package}")
            all_ok = False
    
    print("\n可選套件：")
    for package, name in optional_packages:
        try:
            __import__(package)
            print(f"✅ {name}")
        except ImportError:
            print(f"⚠️  {name} - 如需使用 Gemini API 模式，請安裝")
    
    return all_ok


def test_config():
    """測試配置是否正確"""
    print("\n" + "=" * 60)
    print("測試 2: 檢查配置")
    print("=" * 60)
    
    try:
        from src.config import GITHUB_TOKEN, EMBEDDING_METHOD, validate_config
        
        print(f"GitHub Token: {'✅ 已設定' if GITHUB_TOKEN else '❌ 未設定'}")
        print(f"Embedding 模式: {EMBEDDING_METHOD}")
        
        errors = validate_config()
        if errors:
            print("\n⚠️  配置警告：")
            for error in errors:
                print(f"  {error}")
            return False
        else:
            print("\n✅ 配置檢查通過！")
            return True
    
    except Exception as e:
        print(f"❌ 配置測試失敗: {e}")
        return False


def test_github_api():
    """測試 GitHub API 連接"""
    print("\n" + "=" * 60)
    print("測試 3: GitHub API 連接")
    print("=" * 60)
    
    try:
        from src.github_api import fetch_repos_by_keyword
        
        # 搜尋少量資料進行測試
        print("正在搜尋 'python' 相關的前 3 個倉庫...")
        df = fetch_repos_by_keyword('python', max_results=3)
        
        if not df.empty:
            print(f"✅ API 測試成功！找到 {len(df)} 個倉庫：")
            print(df[['name', 'stars']].to_string(index=False))
            return True
        else:
            print("⚠️  未找到結果")
            return False
    
    except Exception as e:
        print(f"❌ GitHub API 測試失敗: {e}")
        return False


def test_embedding():
    """測試 Embedding 模型"""
    print("\n" + "=" * 60)
    print("測試 4: Embedding 模型")
    print("=" * 60)
    
    try:
        from src.embedding import create_embeddings, reduce_dimensions
        
        test_texts = [
            "A web framework",
            "Machine learning library",
            "Data visualization tool"
        ]
        
        print("正在測試向量化...")
        embeddings = create_embeddings(test_texts, method='local')
        print(f"✅ 向量化成功！形狀: {embeddings.shape}")
        
        print("\n正在測試降維...")
        coords = reduce_dimensions(embeddings)
        print(f"✅ 降維成功！形狀: {coords.shape}")
        
        return True
    
    except Exception as e:
        print(f"❌ Embedding 測試失敗: {e}")
        return False


def test_visualization():
    """測試視覺化模組"""
    print("\n" + "=" * 60)
    print("測試 5: 視覺化模組")
    print("=" * 60)
    
    try:
        import pandas as pd
        from src.visualization import create_scatter_plot
        
        # 建立測試資料
        test_df = pd.DataFrame({
            'name': ['repo1', 'repo2', 'repo3'],
            'description': ['desc1', 'desc2', 'desc3'],
            'stars': [100, 200, 300],
            'url': ['url1', 'url2', 'url3'],
            'language': ['Python', 'JavaScript', 'Go'],
            'x': [1.0, 2.0, 3.0],
            'y': [1.0, 2.0, 3.0]
        })
        
        fig = create_scatter_plot(test_df)
        print("✅ 視覺化測試成功！")
        return True
    
    except Exception as e:
        print(f"❌ 視覺化測試失敗: {e}")
        return False


def main():
    """執行所有測試"""
    print("\n🧪 GitHub Galaxy Explorer - 系統測試\n")
    
    results = {
        "套件安裝": test_imports(),
        "配置檢查": test_config(),
        "GitHub API": test_github_api(),
        "Embedding 模型": test_embedding(),
        "視覺化": test_visualization()
    }
    
    # 總結
    print("\n" + "=" * 60)
    print("測試總結")
    print("=" * 60)
    
    for test_name, result in results.items():
        status = "✅ 通過" if result else "❌ 失敗"
        print(f"{test_name}: {status}")
    
    all_passed = all(results.values())
    
    if all_passed:
        print("\n🎉 所有測試通過！您可以執行: streamlit run app.py")
        return 0
    else:
        print("\n⚠️  部分測試失敗，請檢查上述錯誤訊息")
        return 1


if __name__ == '__main__':
    sys.exit(main())
