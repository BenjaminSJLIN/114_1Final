"""
GitHub Galaxy Explorer - Streamlit 主應用程式
探索 GitHub 倉庫的語義地圖
"""
import streamlit as st
import pandas as pd
from src.config import validate_config, EMBEDDING_METHOD
from src.github_api import fetch_repos_by_keyword, GitHubAPIError
from src.embedding import create_embeddings, reduce_dimensions
from src.visualization import create_scatter_plot


# 頁面配置
st.set_page_config(
    page_title="GitHub Galaxy Explorer",
    page_icon="🌌",
    layout="wide",
    initial_sidebar_state="expanded"
)


def main():
    """主應用程式邏輯"""
    
    # 標題與說明
    st.title("🌌 GitHub Galaxy Explorer")
    st.markdown("""
    探索 GitHub 開源專案的語義宇宙！輸入關鍵字，我們將為您繪製一張 **2D 語義地圖**，
    相似的專案會自動聚集在一起。
    """)
    
    # 側邊欄 - 配置與設定
    with st.sidebar:
        st.header("⚙️ 設定")
        
        # 檢查配置
        config_errors = validate_config()
        if config_errors:
            st.error("配置錯誤：")
            for error in config_errors:
                st.write(error)
            st.info("💡 請在專案根目錄建立 `.env` 檔案，參考 `.env.example`")
            st.stop()
        else:
            st.success("✅ 配置正常")
        
        st.markdown("---")
        
        # 搜尋參數
        st.subheader("🔍 搜尋參數")
        
        keyword = st.text_input(
            "關鍵字",
            value="machine learning",
            help="輸入您想搜尋的主題，例如：web framework, data science, blockchain"
        )
        
        max_results = st.slider(
            "結果數量",
            min_value=10,
            max_value=100,
            value=30,
            step=5,
            help="⚠️ 數量越多，計算時間越長（推薦 30-50 個）"
        )
        
        language = st.selectbox(
            "程式語言篩選（可選）",
            options=["All", "Python", "JavaScript", "TypeScript", "Go", "Rust", "Java", "C++"],
            index=0
        )
        language_filter = None if language == "All" else language
        
        st.markdown("---")
        
        # Embedding 方法選擇
        st.subheader("🧠 Embedding 方法")
        
        embedding_options = {
            "本地模型 (sentence-transformers)": "local",
            "Gemini API (google-generativeai)": "gemini"
        }
        
        selected_method_display = st.radio(
            "選擇方法：",
            options=list(embedding_options.keys()),
            index=0 if EMBEDDING_METHOD == 'local' else 1,
            help="本地模型：免費、離線可用\nGemini API：更快啟動、更高質量"
        )
        
        selected_method = embedding_options[selected_method_display]
        
        st.markdown("---")
        
        # 視覺化選項
        st.subheader("🎨 視覺化選項")
        
        color_by = st.selectbox(
            "顏色編碼",
            options=["language", "stars"],
            index=0,
            help="依據什麼欄位上色"
        )
        
        show_labels = st.checkbox(
            "顯示標籤",
            value=False,
            help="在圖表上顯示倉庫名稱（只在結果少於 30 個時有效）"
        )
        
        st.markdown("---")
        
        # 執行按鈕
        search_button = st.button("🚀 開始探索", type="primary", use_container_width=True)
    
    # 主要內容區域
    if search_button:
        if not keyword.strip():
            st.warning("⚠️ 請輸入關鍵字！")
            return
        
        try:
            # 步驟 1: 獲取資料
            with st.spinner(f"🔍 正在搜尋 '{keyword}' 相關的倉庫..."):
                df = fetch_repos_by_keyword(
                    keyword=keyword,
                    max_results=max_results,
                    language=language_filter
                )
            
            if df.empty:
                st.warning("未找到符合條件的倉庫，請嘗試其他關鍵字。")
                return
            
            st.success(f"✅ 找到 {len(df)} 個倉庫！")
            
            # 顯示資料預覽
            with st.expander("📊 資料預覽", expanded=False):
                st.dataframe(
                    df[['name', 'stars', 'language', 'description']],
                    use_container_width=True,
                    height=400  # 設定高度避免太長
                )
            
            # 步驟 2: 向量化
            with st.spinner(f"🧠 正在使用 {selected_method_display} 進行向量化..."):
                embeddings = create_embeddings(
                    df['description'].tolist(),
                    method=selected_method
                )
            
            st.success(f"✅ 向量化完成！維度: {embeddings.shape}")
            
            # 步驟 3: 降維
            with st.spinner("📉 正在使用 t-SNE 降維至 2D..."):
                coords = reduce_dimensions(embeddings)
                df['x'] = coords[:, 0]
                df['y'] = coords[:, 1]
            
            st.success("✅ 降維完成！")
            
            # 步驟 4: 視覺化
            st.markdown("---")
            st.header("🗺️ 語義地圖")
            st.markdown("""
            **如何解讀**：相近的點代表語義相似的專案。
            將滑鼠懸停在點上可查看詳細資訊。
            """)
            
            fig = create_scatter_plot(
                df,
                title=f"'{keyword}' 的語義地圖",
                color_by=color_by,
                show_labels=show_labels
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # 統計資訊
            st.markdown("---")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("倉庫總數", len(df))
            
            with col2:
                st.metric("總星星數", f"{df['stars'].sum():,}")
            
            with col3:
                top_lang = df['language'].mode()[0] if not df['language'].mode().empty else "Unknown"
                st.metric("最常見語言", top_lang)
            
            with col4:
                avg_stars = int(df['stars'].mean())
                st.metric("平均星星數", f"{avg_stars:,}")
            
            # 下載資料
            st.markdown("---")
            st.subheader("💾 下載資料")
            
            csv = df.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label="📥 下載 CSV",
                data=csv,
                file_name=f"github_galaxy_{keyword.replace(' ', '_')}.csv",
                mime="text/csv"
            )
        
        except GitHubAPIError as e:
            st.error(f"GitHub API 錯誤：{e}")
        
        except Exception as e:
            st.error(f"發生錯誤：{e}")
            st.exception(e)
    
    else:
        # 未搜尋時顯示說明
        st.info("👈 請在左側設定搜尋參數，然後點擊「開始探索」按鈕！")
        
        # 功能介紹
        st.markdown("---")
        st.header("✨ 功能特色")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            ### 🔍 智慧搜尋
            - 關鍵字搜尋 GitHub 倉庫
            - 支援程式語言篩選
            - 可自訂結果數量
            """)
        
        with col2:
            st.markdown("""
            ### 🧠 語義分析
            - 使用 AI 模型理解專案描述
            - 支援本地與 API 兩種模式
            - 自動聚類相似專案
            """)
        
        with col3:
            st.markdown("""
            ### 🎨 視覺化
            - 2D 互動式地圖
            - 懸停顯示詳細資訊
            - 可依語言/星星數上色
            """)
        
        # 使用範例
        st.markdown("---")
        st.header("💡 使用範例")
        
        examples = [
            {"keyword": "machine learning", "desc": "探索機器學習相關專案"},
            {"keyword": "web framework", "desc": "比較不同的網頁框架"},
            {"keyword": "data visualization", "desc": "發現數據視覺化工具"},
            {"keyword": "blockchain", "desc": "了解區塊鏈生態系統"}
        ]
        
        for example in examples:
            st.markdown(f"- **{example['keyword']}** - {example['desc']}")


if __name__ == '__main__':
    main()
