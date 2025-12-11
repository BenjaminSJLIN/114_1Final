# 部署指南 - GitHub Galaxy Explorer 🚀

本文件說明如何將 GitHub Galaxy Explorer 部署到雲端，讓任何人都能透過網址存取。

## 🌐 部署平台選擇

### 推薦：Streamlit Community Cloud（完全免費）

**優勢**：
- ✅ 完全免費（公開應用）
- ✅ 部署超級簡單（5 分鐘內完成）
- ✅ 自動 HTTPS 加密
- ✅ GitHub 整合（推送即部署）
- ✅ 提供免費網址（`yourapp.streamlit.app`）

---

## 📋 部署步驟（Streamlit Cloud）

### 步驟 1: 準備 GitHub Repository

1. **初始化 Git**（如果尚未初始化）

```bash
git init
git add .
git commit -m "Initial commit: GitHub Galaxy Explorer"
```

2. **建立 GitHub Repository**
   - 前往 [GitHub](https://github.com/new)
   - 建立新 repository（例如：`github-galaxy-explorer`）
   - 設為 **Public**（免費部署）

3. **推送程式碼**

```bash
git remote add origin https://github.com/你的用戶名/github-galaxy-explorer.git
git branch -M main
git push -u origin main
```

---

### 步驟 2: 部署到 Streamlit Cloud

1. **前往 [Streamlit Cloud](https://share.streamlit.io/)**
   - 使用 GitHub 帳號登入
   - 點擊 "New app"

2. **選擇 Repository**
   - Repository: `你的用戶名/github-galaxy-explorer`
   - Branch: `main`
   - Main file path: `app.py`

3. **設定 Secrets**（重要！）
   - 點擊 "Advanced settings"
   - 在 "Secrets" 區域貼上以下內容：

```toml
# 複製 .streamlit/secrets.toml.example 的內容
GITHUB_TOKEN = "ghp_your_actual_token_here"
GEMINI_API_KEY = "your_actual_gemini_key_here"
EMBEDDING_METHOD = "gemini"
```

> [!IMPORTANT]
> **雲端部署時強烈建議使用 `EMBEDDING_METHOD = "gemini"`**
> 
> **原因**：
> - 本地模型 (`sentence-transformers`) 需要下載 80MB
> - Streamlit Cloud 每次重啟都會重新下載
> - Gemini API 啟動更快、更穩定
> - Gemini 免費配額對學生專案完全足夠

4. **點擊 "Deploy"**
   - 等待 2-3 分鐘
   - 完成後會獲得公開網址！

---

### 步驟 3: 取得 Gemini API Key（雲端部署必需）

1. 前往 [Google AI Studio](https://aistudio.google.com/app/apikey)
2. 點擊 "Create API Key"
3. 複製 API Key
4. 在 Streamlit Cloud 的 Secrets 中填入

---

## 🔄 更新部署的應用程式

當您修改程式碼後：

```bash
git add .
git commit -m "Update: 描述您的修改"
git push
```

Streamlit Cloud 會**自動偵測**並重新部署！

---

## ⚙️ 環境變數對照表

| 本地開發 | 雲端部署 |
|---------|---------|
| `.env` 檔案 | Streamlit Secrets |
| `EMBEDDING_METHOD=local` | `EMBEDDING_METHOD=gemini`（推薦） |
| GitHub Token | 必需（兩者都需要） |
| Gemini API Key | 雲端部署時必需 |

---

## 🐛 常見問題排解

### 問題 1: 應用啟動失敗

**可能原因**：缺少 Secrets

**解決方案**：
1. 前往 Streamlit Cloud > App settings > Secrets
2. 確認已填入 `GITHUB_TOKEN` 和 `GEMINI_API_KEY`

---

### 問題 2: 模組找不到

**可能原因**：`requirements.txt` 不完整

**解決方案**：
確認 `requirements.txt` 包含所有依賴：

```txt
streamlit>=1.28.0
pandas>=2.0.0
google-generativeai>=0.3.0
# ... 其他套件
```

---

### 問題 3: API 速率限制

**可能原因**：多人同時使用導致 GitHub API 超過限制

**解決方案**：
1. 確認使用了 GitHub Token（提升至 5000/小時）
2. 限制搜尋結果數量（預設 30-50 個）
3. 考慮實作快取機制

---

## 🎓 其他部署選項

### Hugging Face Spaces（免費）

適合 AI/ML 專案展示

1. 註冊 [Hugging Face](https://huggingface.co/)
2. 建立 Space，選擇 Streamlit
3. 上傳程式碼
4. 設定 Secrets

### 自架伺服器

適合進階用戶，可使用：
- AWS EC2
- Google Cloud Run
- DigitalOcean
- Azure App Service

---

## 📊 部署檢查清單

在部署前，請確認：

- [ ] 程式碼已推送到 GitHub
- [ ] `.gitignore` 已排除 `.env` 和 `secrets.toml`
- [ ] `requirements.txt` 完整且正確
- [ ] 已取得 GitHub Personal Access Token
- [ ] 已取得 Gemini API Key（雲端部署）
- [ ] 在 Streamlit Cloud 設定 Secrets
- [ ] `EMBEDDING_METHOD` 設為 `gemini`（雲端部署）

---

## 🎉 部署完成後

您會獲得一個公開網址，例如：

```
https://your-github-galaxy.streamlit.app
```

可以分享給：
- 👨‍🏫 教授（展示期末專案）
- 👥 同學（協作使用）
- 🌍 全世界（Portfolio 作品）

---

## 💡 效能優化建議

### 1. 快取搜尋結果

在 `app.py` 中使用：

```python
@st.cache_data(ttl=3600)  # 快取 1 小時
def cached_search(keyword, max_results):
    return fetch_repos_by_keyword(keyword, max_results)
```

### 2. 限制並發請求

使用 Streamlit 的 session state 避免重複請求

### 3. 監控 API 使用量

定期檢查 Gemini API 和 GitHub API 的配額使用情況

---

## 📞 支援資源

- [Streamlit 部署文檔](https://docs.streamlit.io/streamlit-community-cloud/get-started)
- [GitHub Token 說明](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token)
- [Gemini API 文檔](https://ai.google.dev/docs)

---

**祝部署順利！🚀**
