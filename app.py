"""GitHub Explorer"""
import streamlit as st
import pandas as pd
from src.config import validate_config, EMBEDDING_METHOD
from src.github_api import fetch_repos_by_keyword, GitHubAPIError
from src.embedding import create_embeddings, reduce_dimensions
from src.visualization import create_scatter_plot


# 頁面配置
st.set_page_config(
    page_title="GitHub Explorer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)


def main():
    """主程式"""
    
    # 標題與說明
    st.title("GitHub Explorer")
    st.markdown("""
    探索 GitHub 開源專案
    """)
    
    # 側邊欄
    with st.sidebar:
        st.header("設定")
        
        # 檢查配置
        config_errors = validate_config()
        if config_errors:
            st.error("配置錯誤：")
            for error in config_errors:
                st.write(error)
            st.info("請在專案根目錄建立 `.env` 檔案，參考 `.env.example`")
            st.stop()
        else:
            st.success("配置正常")
        
        st.markdown("---")
        
        # 搜尋參數
        st.subheader("搜尋參數")
        
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
            help="數量越多，計算時間越長（推薦 30-50 個）"
        )
        
        language = st.selectbox(
            "程式語言篩選（可選）",
            options=["All", "Python", "JavaScript", "TypeScript", "Go", "Rust", "Java", "C++"],
            index=0
        )
        language_filter = None if language == "All" else language
        
        st.markdown("---")
        
        # 視覺化選項
        st.subheader("視覺化選項")
        
        color_by = st.selectbox(
            "顏色編碼",
            options=["language", "stars"],
            index=0,
            help="依據什麼欄位上色"
        )
        
        show_labels = st.checkbox(
            "顯示標籤",
            value=False,
            help="在圖表上顯示倉庫名稱（數量多時字體會自動縮小）"
        )
        
        st.markdown("---")
        
        # 進階探索功能
        st.subheader("進階探索")
        
        enable_advanced = st.checkbox(
            "啟用進階篩選",
            value=False,
            help="在搜尋結果中進一步篩選語義相近的倉庫"
        )
        
        advanced_keyword = ""
        advanced_count = 10
        
        if enable_advanced:
            advanced_keyword = st.text_input(
                "進階關鍵字",
                value="",
                help="輸入更具體的關鍵字，系統會找出與此關鍵字語義最相近的倉庫"
            )
            
            advanced_count = st.slider(
                "篩選數量",
                min_value=5,
                max_value=50,
                value=10,
                step=5,
                help="從搜尋結果中保留最相近的幾個倉庫"
            )
        
        st.markdown("---")
        
        # 執行按鈕
        search_button = st.button("開始探索", type="primary", use_container_width=True)
    
    # 主要內容
    if search_button:
        if not keyword.strip():
            st.warning("請輸入關鍵字！")
            return
        
        try:
            # 步驟 1: 獲取資料
            with st.spinner(f"正在搜尋 '{keyword}' 相關的倉庫..."):
                df = fetch_repos_by_keyword(
                    keyword=keyword,
                    max_results=max_results,
                    language=language_filter
                )
            
            if df.empty:
                st.warning("未找到符合條件的倉庫，請嘗試其他關鍵字。")
                return
            
            st.success(f"找到 {len(df)} 個倉庫！")
            
            # 資料預覽
            with st.expander("資料預覽（點擊專案名稱可開啟 GitHub 頁面）", expanded=False):
                df_display = df[['name', 'stars', 'language', 'description', 'url']].copy()
                
                # 組合 Markdown 連結
                df_display['專案連結'] = df_display.apply(
                    lambda row: f"[{row['name']}]({row['url']})", 
                    axis=1
                )
                
                # 顯示表格
                st.dataframe(
                    df_display[['專案連結', 'stars', 'language', 'description']],
                    use_container_width=True,
                    height=400,
                    column_config={
                        "專案連結": st.column_config.LinkColumn(
                            "專案名稱",
                            help="點擊開啟 GitHub 頁面",
                            max_chars=100
                        ),
                        "stars": st.column_config.NumberColumn(
                            "Stars",
                            format="%d"
                        ),
                        "language": st.column_config.TextColumn(
                            "語言"
                        ),
                        "description": st.column_config.TextColumn(
                            "描述"
                        )
                    }
                )
            
            # 步驟 2: 向量化
            with st.spinner(f"正在使用 Embedding 進行向量化..."):
                embeddings = create_embeddings(
                    df['description'].tolist(),
                    method=EMBEDDING_METHOD  # 直接使用 .env 中的設定
                )
            
            st.success(f"向量化完成！維度: {embeddings.shape}")
            
            # 保存原始數據
            df_original = df.copy()
            embeddings_original = embeddings.copy()
            
            # 步驟 3: 降維
            with st.spinner("正在使用 t-SNE 降維至 2D..."):
                coords_original = reduce_dimensions(embeddings_original)
                df_original['x'] = coords_original[:, 0]
                df_original['y'] = coords_original[:, 1]
            
            st.success("降維完成！")
            
            # 步驟 4: 視覺化
            st.markdown("---")
            st.header("語義地圖 - 完整結果")
            st.markdown(f"""
            **如何解讀**：相近的點代表語義相似的專案。
            共找到 **{len(df_original)}** 個倉庫。
            """)
            
            fig_original = create_scatter_plot(
                df_original,
                title=f"'{keyword}' 的語義地圖（完整結果）",
                color_by=color_by,
                show_labels=show_labels
            )
            
            st.plotly_chart(fig_original, use_container_width=True)
            
            # 進階篩選
            if enable_advanced and advanced_keyword.strip():
                st.markdown("---")
                st.header("語義地圖 - 進階篩選結果")
                
                with st.spinner(f"正在使用進階關鍵字 '{advanced_keyword}' 進行語義篩選..."):
                    # 將進階關鍵字也進行向量化
                    keyword_embedding = create_embeddings(
                        [advanced_keyword],
                        method=EMBEDDING_METHOD
                    )
                    
                    # 計算餘弦相似度
                    import numpy as np
                    from sklearn.metrics.pairwise import cosine_similarity
                    
                    similarities = cosine_similarity(embeddings, keyword_embedding).flatten()
                    
                    # 將相似度添加到 DataFrame
                    df['similarity'] = similarities
                    
                    # 排序取前 N 個
                    df_filtered = df.nlargest(min(advanced_count, len(df)), 'similarity').copy()
                    
                    # 更新 embeddings 以匹配篩選後的結果
                    filtered_indices = df_filtered.index.tolist()
                    embeddings_filtered = embeddings[filtered_indices]
                    
                    # 重置索引
                    df_filtered = df_filtered.reset_index(drop=True)
                
                st.success(f"進階篩選完成！從 {len(df)} 個倉庫中篩選出 {len(df_filtered)} 個最相近的倉庫")
                
                # 對篩選後的結果進行降維
                with st.spinner("正在對篩選結果降維..."):
                    coords_filtered = reduce_dimensions(embeddings_filtered)
                    df_filtered['x'] = coords_filtered[:, 0]
                    df_filtered['y'] = coords_filtered[:, 1]
                
                st.markdown(f"""
                **篩選條件**：與 "{advanced_keyword}" 語義最相近的 **{len(df_filtered)}** 個倉庫。
                相似度範圍：{df_filtered['similarity'].min():.3f} - {df_filtered['similarity'].max():.3f}
                """)
                
                # 繪製篩選後的圖表
                fig_filtered = create_scatter_plot(
                    df_filtered,
                    title=f"進階篩選：'{advanced_keyword}'",
                    color_by=color_by,
                    show_labels=show_labels
                )
                
                st.plotly_chart(fig_filtered, use_container_width=True)
                
                # 使用篩選後的數據進行後續統計
                df_for_stats = df_filtered
            else:
                # 使用原始數據進行統計
                df_for_stats = df_original
            
            # 統計資訊
            st.markdown("---")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("倉庫總數", len(df_for_stats))
            
            with col2:
                st.metric("總星星數", f"{df_for_stats['stars'].sum():,}")
            
            with col3:
                top_lang = df_for_stats['language'].mode()[0] if not df_for_stats['language'].mode().empty else "Unknown"
                st.metric("最常見語言", top_lang)
            
            with col4:
                avg_stars = int(df_for_stats['stars'].mean())
                st.metric("平均星星數", f"{avg_stars:,}")
            
            # 下載資料
            st.markdown("---")
            st.subheader("下載資料")
            
            csv = df_for_stats.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label="下載 CSV",
                data=csv,
                file_name=f"github_explorer_{keyword.replace(' ', '_')}.csv",
                mime="text/csv"
            )
        
        except GitHubAPIError as e:
            st.error(f"GitHub API 錯誤：{e}")
        
        except Exception as e:
            st.error(f"發生錯誤：{e}")
            st.exception(e)
    
    else:
        # 初始說明
        st.info("請在左側設定搜尋參數，然後點擊「開始探索」按鈕！")

if __name__ == '__main__':
    main()
