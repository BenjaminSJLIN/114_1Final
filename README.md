# GitHub Galaxy Explorer 🌌

一個基於語義搜索的 GitHub 專案探索工具，使用 AI 技術將相似的開源專案聚集在 2D 語義地圖上。

## 🎯 專案目標

解決開源專案搜尋時的「資訊過載」問題。傳統的列表檢視難以快速理解專案之間的關係，而語義地圖能讓您一眼看出哪些專案相似、哪些專案獨特。

## ✨ 功能特色

- 🔍 **智慧搜尋**：使用 GitHub API 搜尋開源專案
- 🧠 **語義分析**：使用 AI Embeddings 理解專案描述的語義
- 📉 **降維視覺化**：使用 t-SNE 將高維向量降至 2D
- 🎨 **互動式地圖**：Plotly 提供美觀的互動式散點圖
- 🔄 **雙模式支援**：支援本地模型與 Gemini API

## 🛠️ 技術堆疊

- **前端框架**：Streamlit
- **資料處理**：Pandas, NumPy
- **API**：PyGithub, requests
- **AI/ML**：sentence-transformers, scikit-learn, google-generativeai
- **視覺化**：Plotly Express

## 📦 安裝步驟

### 1. 克隆專案（或解壓縮）

```bash
cd 114_1Final
```

### 2. 安裝依賴套件

```bash
pip install -r requirements.txt
```

### 3. 配置環境變數

複製 `.env.example` 為 `.env`：

```bash
copy .env.example .env  # Windows
# 或
cp .env.example .env    # macOS/Linux
```

然後編輯 `.env` 檔案，填入您的 API Keys：

```env
# GitHub Personal Access Token (必需)
GITHUB_TOKEN=ghp_your_token_here

# Google Gemini API Key (可選 - 僅在使用 API 模式時需要)
GEMINI_API_KEY=your_gemini_key_here

# Embedding 模式選擇
EMBEDDING_METHOD=local  # 或 gemini
```

#### 如何取得 API Keys？

**GitHub Token**：
1. 前往 [GitHub Settings > Developer settings > Personal access tokens](https://github.com/settings/tokens)
2. 點擊 "Generate new token (classic)"
3. 選擇權限：`public_repo`（如果只搜尋公開倉庫）
4. 複製 token

**Gemini API Key**（可選）：
1. 前往 [Google AI Studio](https://aistudio.google.com/app/apikey)
2. 建立 API Key
3. 複製 key

## 🚀 使用方式

### 運行應用程式

```bash
streamlit run app.py
```

應用程式將在瀏覽器中自動開啟（預設：http://localhost:8501）

### 基本流程

1. 在側邊欄輸入搜尋關鍵字（例如："machine learning"）
2. 調整搜尋參數（結果數量、程式語言篩選等）
3. 選擇 Embedding 方法（本地模型或 Gemini API）
4. 點擊「🚀 開始探索」按鈕
5. 查看語義地圖並探索相似專案

### 測試個別模組

```bash
# 測試配置
python -m src.config

# 測試 GitHub API
python -m src.github_api

# 測試 Embedding
python -m src.embedding

# 測試視覺化
python -m src.visualization
```

## 📁 專案結構

```
114_1Final/
├── app.py                    # Streamlit 主應用程式
├── .env                      # 環境變數（請自行建立）
├── .env.example              # 環境變數範本
├── requirements.txt          # Python 依賴套件
├── README.md                 # 本檔案
│
├── src/                      # 核心程式碼
│   ├── __init__.py
│   ├── config.py             # 配置管理
│   ├── github_api.py         # GitHub API 資料獲取
│   ├── embedding.py          # 向量化與降維
│   └── visualization.py      # Plotly 視覺化
│
└── utils/                    # 輔助工具
    └── __init__.py
```

## 🧪 範例搜尋

試試以下關鍵字：

- `machine learning` - 探索機器學習專案
- `web framework` - 比較網頁框架
- `data visualization` - 發現視覺化工具
- `blockchain` - 了解區塊鏈生態系統

## ⚙️ Embedding 方法比較

### 本地模型（sentence-transformers）

- ✅ 完全免費
- ✅ 離線可用
- ✅ 無調用次數限制
- ❌ 首次下載模型（~80MB）
- ❌ 首次載入需 2-3 秒

### Gemini API

- ✅ 無需下載模型
- ✅ 瞬間啟動
- ✅ 更高質量的 embeddings
- ❌ 需要 API Key
- ❌ 免費配額有限（每分鐘 1500 次）

**建議**：開發時使用本地模型，部署時切換至 Gemini API

## 📊 效能考量

- **GitHub API 速率限制**：
  - 未認證：60 次/小時
  - 已認證：5000 次/小時
  - 搜索 API：30 次/分鐘

- **t-SNE 計算時間**：
  - 30 個倉庫：~2 秒
  - 50 個倉庫：~5 秒
  - 100 個倉庫：~15 秒

建議將搜尋結果限制在 30-50 個以獲得最佳體驗。

## 🔮 未來功能

- [ ] LLM 摘要：點擊聚類時自動生成摘要
- [ ] 聚類分析：使用 K-means 或 DBSCAN 自動識別聚類
- [ ] 歷史記錄：儲存過去的搜尋結果
- [ ] 多維度篩選：支援 stars 範圍、更新時間等篩選

## 📝 授權

本專案為教育用途，使用 MIT License。

## 👨‍💻 作者

大學期末專案 - GitHub Galaxy Explorer

---

**Enjoy exploring the GitHub galaxy! 🌌✨**
