"""
Embedding 與降維模組
支援兩種 Embedding 方式：
1. 本地模型 (sentence-transformers)
2. Gemini API (google-generativeai)
"""
import numpy as np
from typing import List, Literal
from sklearn.manifold import TSNE
import warnings

from src.config import (
    EMBEDDING_METHOD,
    LOCAL_EMBEDDING_MODEL,
    GEMINI_API_KEY,
    TSNE_PERPLEXITY,
    TSNE_RANDOM_STATE
)

# 全域變數用於快取模型
_local_model = None
_gemini_configured = False


def get_local_embedding_model():
    """
    取得本地 Embedding 模型（單例模式，避免重複載入）
    
    Returns:
        SentenceTransformer 模型實例
    """
    global _local_model
    
    if _local_model is None:
        try:
            from sentence_transformers import SentenceTransformer
            print(f"📥 正在載入本地 Embedding 模型: {LOCAL_EMBEDDING_MODEL}...")
            _local_model = SentenceTransformer(LOCAL_EMBEDDING_MODEL)
            print("✅ 模型載入完成！")
        except ImportError:
            raise ImportError(
                "請安裝 sentence-transformers:\n"
                "pip install sentence-transformers"
            )
    
    return _local_model


def configure_gemini_api():
    """配置 Gemini API"""
    global _gemini_configured
    
    if not _gemini_configured:
        if not GEMINI_API_KEY:
            raise ValueError(
                "使用 Gemini API 模式需要設定 GEMINI_API_KEY！\n"
                "請在 .env 檔案中新增：GEMINI_API_KEY=your_api_key"
            )
        
        try:
            import google.generativeai as genai
            genai.configure(api_key=GEMINI_API_KEY)
            _gemini_configured = True
            print("✅ Gemini API 配置完成！")
        except ImportError:
            raise ImportError(
                "請安裝 google-generativeai:\n"
                "pip install google-generativeai"
            )


def create_embeddings_local(texts: List[str]) -> np.ndarray:
    """
    使用本地模型建立 Embeddings
    
    Args:
        texts: 文字列表
        
    Returns:
        Embedding 向量矩陣 (shape: [len(texts), embedding_dim])
    """
    model = get_local_embedding_model()
    
    print(f"🧠 正在使用本地模型對 {len(texts)} 段文字進行向量化...")
    embeddings = model.encode(texts, show_progress_bar=True)
    print(f"✅ 向量化完成！維度: {embeddings.shape}")
    
    return embeddings


def create_embeddings_gemini(texts: List[str]) -> np.ndarray:
    """
    使用 Gemini API 建立 Embeddings
    
    Args:
        texts: 文字列表
        
    Returns:
        Embedding 向量矩陣
    """
    import google.generativeai as genai
    
    configure_gemini_api()
    
    print(f"🌐 正在使用 Gemini API 對 {len(texts)} 段文字進行向量化...")
    
    embeddings = []
    for i, text in enumerate(texts):
        try:
            # 使用 Gemini 的 Embedding 模型
            result = genai.embed_content(
                model="models/text-embedding-004",
                content=text,
                task_type="semantic_similarity"
            )
            embeddings.append(result['embedding'])
            
            if (i + 1) % 10 == 0:
                print(f"  進度: {i + 1}/{len(texts)}")
        
        except Exception as e:
            print(f"⚠️ 警告：文字 {i} 向量化失敗，使用零向量替代。錯誤: {e}")
            # 使用零向量作為後備方案
            embeddings.append([0.0] * 768)
    
    embeddings_array = np.array(embeddings)
    print(f"✅ 向量化完成！維度: {embeddings_array.shape}")
    
    return embeddings_array


def create_embeddings(
    texts: List[str],
    method: Literal['local', 'gemini'] = None
) -> np.ndarray:
    """
    建立文字 Embeddings（自動根據配置選擇方法）
    
    Args:
        texts: 文字列表
        method: 強制指定方法 ('local' 或 'gemini')，若為 None 則使用配置檔設定
        
    Returns:
        Embedding 向量矩陣
    """
    # 決定使用哪種方法
    selected_method = method or EMBEDDING_METHOD
    
    if selected_method == 'local':
        return create_embeddings_local(texts)
    elif selected_method == 'gemini':
        return create_embeddings_gemini(texts)
    else:
        raise ValueError(
            f"不支援的 Embedding 方法: {selected_method}\n"
            f"請使用 'local' 或 'gemini'"
        )


def reduce_dimensions(
    embeddings: np.ndarray,
    n_components: int = 2,
    perplexity: int = None,
    method: Literal['tsne', 'umap'] = 'tsne'
) -> np.ndarray:
    """
    將高維向量降維至 2D（用於可視化）
    
    Args:
        embeddings: 高維向量矩陣
        n_components: 目標維度（預設 2D）
        perplexity: t-SNE 的 perplexity 參數（推薦值：樣本數的 5-10%）
        method: 降維方法 ('tsne' 或 'umap')
        
    Returns:
        降維後的座標矩陣 (shape: [n_samples, n_components])
    """
    n_samples = embeddings.shape[0]
    
    # 自動調整 perplexity
    if perplexity is None:
        perplexity = min(TSNE_PERPLEXITY, max(2, n_samples // 10))
    
    # 確保 perplexity 合法
    perplexity = min(perplexity, n_samples - 1)
    
    print(f"📉 正在使用 {method.upper()} 將 {n_samples} 個向量降維至 {n_components}D...")
    print(f"   參數: perplexity={perplexity}")
    
    if method == 'tsne':
        # 使用 t-SNE
        with warnings.catch_warnings():
            warnings.filterwarnings('ignore')
            
            # scikit-learn 1.0+ 使用 max_iter，舊版使用 n_iter
            # 為了相容性，我們使用 max_iter（新版本的參數名稱）
            tsne = TSNE(
                n_components=n_components,
                perplexity=perplexity,
                random_state=TSNE_RANDOM_STATE,
                init='random',
                max_iter=1000  # 修改：從 n_iter 改為 max_iter
            )
            reduced = tsne.fit_transform(embeddings)
    
    elif method == 'umap':
        # UMAP (需要額外安裝)
        try:
            from umap import UMAP
            reducer = UMAP(
                n_components=n_components,
                random_state=TSNE_RANDOM_STATE
            )
            reduced = reducer.fit_transform(embeddings)
        except ImportError:
            raise ImportError(
                "使用 UMAP 需要安裝 umap-learn:\n"
                "pip install umap-learn"
            )
    else:
        raise ValueError(f"不支援的降維方法: {method}")
    
    print(f"✅ 降維完成！輸出維度: {reduced.shape}")
    return reduced


if __name__ == '__main__':
    # 測試 Embedding 模組
    print("🧪 測試 Embedding 模組...\n")
    
    # 測試資料
    test_texts = [
        "A lightweight WSGI web application framework in Python.",
        "The Web framework for perfectionists with deadlines.",
        "Tensors and Dynamic neural networks in Python.",
        "An Open Source Machine Learning Framework for Everyone.",
    ]
    
    # 測試本地模型
    print("=" * 50)
    print("測試 1: 本地 Embedding 模型")
    print("=" * 50)
    try:
        embeddings_local = create_embeddings(test_texts, method='local')
        print(f"✅ 本地模型測試成功！向量維度: {embeddings_local.shape}\n")
        
        # 測試降維
        coords = reduce_dimensions(embeddings_local)
        print(f"✅ 降維測試成功！座標:\n{coords}\n")
    except Exception as e:
        print(f"❌ 本地模型測試失敗: {e}\n")
    
    # 測試 Gemini API（僅在配置時）
    if GEMINI_API_KEY:
        print("=" * 50)
        print("測試 2: Gemini API Embedding")
        print("=" * 50)
        try:
            embeddings_gemini = create_embeddings(test_texts[:2], method='gemini')  # 只測試 2 個節省配額
            print(f"✅ Gemini API 測試成功！向量維度: {embeddings_gemini.shape}\n")
        except Exception as e:
            print(f"❌ Gemini API 測試失敗: {e}\n")
    else:
        print("⏭️  跳過 Gemini API 測試（未設定 GEMINI_API_KEY）\n")
