# GitHub Explorer

一個基於語義搜索的 GitHub 專案探索工具，使用 AI 技術將相似的開源專案在 2D 語義地圖上視覺化。

## 系統需求

- Python 3.10 或以上版本
- pip (Python 套件管理工具)
- Git (用於克隆專案)

## 安裝步驟

### 1. 解壓縮專案

將 ZIP 檔案解壓縮到您的電腦。

### 2. 進入專案目錄

```bash
cd {folder_name}
```

### 3. 建立虛擬環境（建議）

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 4. 安裝依賴套件

```bash
pip install -r requirements.txt
```

### 5. 配置環境變數

複製 `.env.example` 為 `.env`：

```bash
# Windows
copy .env.example .env

# macOS/Linux
cp .env.example .env
```

編輯 `.env` 檔案，填入您的 API Keys：

```env
# GitHub Personal Access Token (必需)
GITHUB_TOKEN=ghp_your_token_here

# Google Gemini API Key (可選)
GEMINI_API_KEY=your_gemini_key_here

# Embedding 模式選擇
EMBEDDING_METHOD=local
```

### 6. 取得 GitHub Token

1. 前往 https://github.com/settings/tokens
2. 點擊 "Generate new token (classic)"
3. 選擇權限：`public_repo`
4. 複製 token 並貼到 `.env` 檔案中

### 7. 取得 Gemini API Key

如果要使用 Gemini API 模式：
1. 前往 https://aistudio.google.com/app/apikey
2. 建立 API Key
3. 複製 key 並貼到 `.env` 檔案中
4. 將 `EMBEDDING_METHOD` 改為 `gemini`

## 運行應用程式

```bash
streamlit run app.py
```

應用程式將在瀏覽器中自動開啟（預設：http://localhost:8501）

## 使用說明

1. 在側邊欄輸入搜尋關鍵字（例如："machine learning"）
2. 調整搜尋參數（結果數量、程式語言篩選）
3. 點擊「開始探索」按鈕
4. 查看語義地圖並與相似專案互動

## 測試環境設定

執行測試腳本以驗證環境配置：

```bash
python test_setup.py
```

