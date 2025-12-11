"""
Plotly 視覺化模組
建立互動式的 GitHub 倉庫語義地圖
"""
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Optional


def create_scatter_plot(
    df: pd.DataFrame,
    title: str = "GitHub Repository Galaxy 🌌",
    color_by: str = 'language',
    size_by: str = 'stars',
    show_labels: bool = True
) -> go.Figure:
    """
    建立互動式散點圖，展示倉庫的語義分布
    
    Args:
        df: 包含 x, y, name, description, stars, url 等欄位的 DataFrame
        title: 圖表標題
        color_by: 用於顏色編碼的欄位 (預設依程式語言)
        size_by: 用於大小編碼的欄位 (預設依星星數)
        show_labels: 是否顯示標籤
        
    Returns:
        Plotly Figure 物件
    """
    # 確保必要欄位存在
    required_cols = ['x', 'y', 'name']
    for col in required_cols:
        if col not in df.columns:
            raise ValueError(f"DataFrame 缺少必要欄位: {col}")
    
    # 準備 hover 資訊
    hover_data = {
        'name': True,
        'description': True,
        'stars': ':,',  # 千分位格式
        'url': False,  # 不在 hover 中顯示（會在 customdata 中）
        'x': False,  # 隱藏座標
        'y': False
    }
    
    # 如果有 language 欄位，加入 hover
    if 'language' in df.columns:
        hover_data['language'] = True
    
    # 建立散點圖
    fig = px.scatter(
        df,
        x='x',
        y='y',
        color=color_by if color_by in df.columns else None,
        size=size_by if size_by in df.columns else None,
        hover_name='name',
        hover_data=hover_data,
        title=title,
        labels={
            'x': '',
            'y': '',
            'stars': '⭐ Stars',
            'language': '💻 Language',
            'description': '📝 Description'
        },
        size_max=30
    )
    
    # 自訂 hover 模板
    fig.update_traces(
        hovertemplate='<b>%{hovertext}</b><br>' +
                      '⭐ %{customdata[0]:,} stars<br>' +
                      '💻 %{customdata[1]}<br>' +
                      '📝 %{customdata[2]}<br>' +
                      '<extra></extra>',
        customdata=df[['stars', 'language', 'description']].values if 'language' in df.columns 
                   else df[['stars', 'description']].values,
        marker=dict(
            line=dict(width=1, color='white'),  # 邊框
            opacity=0.8
        )
    )
    
    # 如果需要顯示標籤
    if show_labels and len(df) <= 30:  # 只在倉庫數量少時顯示標籤
        fig.add_trace(
            go.Scatter(
                x=df['x'],
                y=df['y'],
                mode='text',
                text=df['name'].str.split('/').str[-1],  # 只顯示倉庫名稱（去掉 owner）
                textposition='top center',
                textfont=dict(size=8, color='gray'),
                showlegend=False,
                hoverinfo='skip'
            )
        )
    
    # 美化圖表
    fig.update_layout(
        showlegend=True,
        hovermode='closest',
        plot_bgcolor='rgba(240, 240, 250, 0.5)',
        paper_bgcolor='white',
        font=dict(family='Arial, sans-serif', size=12),
        title=dict(
            font=dict(size=20, color='#2c3e50'),
            x=0.5,
            xanchor='center'
        ),
        xaxis=dict(
            showgrid=False,
            showticklabels=False,
            zeroline=False
        ),
        yaxis=dict(
            showgrid=False,
            showticklabels=False,
            zeroline=False
        ),
        height=700,
        margin=dict(l=50, r=50, t=80, b=50)
    )
    
    return fig


def create_cluster_summary_plot(
    df: pd.DataFrame,
    cluster_labels: list,
    title: str = "Repository Clusters"
) -> go.Figure:
    """
    建立帶聚類標籤的散點圖（未來功能：與 LLM 整合時使用）
    
    Args:
        df: 倉庫資料 DataFrame
        cluster_labels: 聚類標籤列表
        title: 圖表標題
        
    Returns:
        Plotly Figure 物件
    """
    df_with_clusters = df.copy()
    df_with_clusters['cluster'] = cluster_labels
    
    fig = px.scatter(
        df_with_clusters,
        x='x',
        y='y',
        color='cluster',
        hover_name='name',
        title=title,
        color_continuous_scale='Viridis'
    )
    
    fig.update_layout(
        showlegend=True,
        hovermode='closest',
        height=700
    )
    
    return fig


if __name__ == '__main__':
    # 測試視覺化模組
    print("🧪 測試視覺化模組...")
    
    # 建立測試資料
    test_data = pd.DataFrame({
        'name': ['owner/repo1', 'owner/repo2', 'owner/repo3', 'owner/repo4'],
        'description': ['A web framework', 'Machine learning library', 'Data visualization tool', 'API framework'],
        'stars': [1000, 5000, 2000, 3000],
        'url': ['https://github.com/1', 'https://github.com/2', 'https://github.com/3', 'https://github.com/4'],
        'language': ['Python', 'Python', 'JavaScript', 'Go'],
        'x': [1.2, 3.5, 1.8, 3.2],
        'y': [2.1, 1.5, 2.8, 1.9]
    })
    
    try:
        fig = create_scatter_plot(test_data)
        print("✅ 視覺化測試成功！")
        print("💡 提示: 在 Streamlit 中使用 st.plotly_chart(fig) 顯示圖表")
        
        # 儲存為 HTML（可選）
        # fig.write_html('test_plot.html')
        # print("📊 測試圖表已儲存為 test_plot.html")
        
    except Exception as e:
        print(f"❌ 視覺化測試失敗: {e}")
