# ScrollCorner Automated News Pipeline 🚀

Fully automated news aggregator pipeline that:
1. **Fetches** latest headlines from NewsAPI
2. **Rewrites** them into original articles using Groq AI
3. **Publishes** automatically to ScrollCorner Blogger site
4. **Runs** every 6 hours via GitHub Actions — completely hands-off!

---

## 📋 Setup Guide

### Step 1 — Clone This Repository
```bash
git clone https://github.com/YOUR_USERNAME/scrollcorner-pipeline.git
cd scrollcorner-pipeline
```

### Step 2 — Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3 — Generate Blogger OAuth Token (ONE TIME ONLY)
1. Download your `credentials.json` from Google Cloud Console
2. Place it in this folder
3. Run:
```bash
python generate_token.py
```
4. A browser window will open — log in with your Blogger Google account
5. Copy the tokens shown in the terminal

### Step 4 — Add GitHub Secrets
Go to your GitHub repo → Settings → Secrets → New Secret

Add these secrets:
| Secret Name | Value |
|---|---|
| `GROQ_API_KEY` | Your Groq API key |
| `NEWSAPI_KEY` | Your NewsAPI key |
| `BLOG_ID` | `863166249650115658` |
| `BLOGGER_TOKEN` | From generate_token.py output |
| `BLOGGER_REFRESH_TOKEN` | From generate_token.py output |
| `BLOGGER_CLIENT_ID` | From credentials.json |
| `BLOGGER_CLIENT_SECRET` | From credentials.json |

### Step 5 — Push to GitHub
```bash
git add .
git commit -m "Initial ScrollCorner pipeline setup"
git push origin main
```

### Step 6 — Enable GitHub Actions
1. Go to your repo on GitHub
2. Click **Actions** tab
3. Click **"I understand my workflows, go ahead and enable them"**
4. Done! Pipeline runs automatically every 6 hours ✅

---

## 🔧 Manual Run
To trigger the pipeline manually:
1. Go to GitHub repo → Actions
2. Click **"ScrollCorner Auto Publisher"**
3. Click **"Run workflow"** → **"Run workflow"**

---

## ⚙️ Configuration
Edit `news_fetcher.py` to change:
- `ARTICLES_PER_CATEGORY` — how many articles per category per run
- `CATEGORIES` — add/remove categories

---

## 📊 Monitoring
After each run GitHub saves a `last_run.json` log showing:
- How many articles were fetched, written and published
- Timestamp of the run
- Any failures

View logs: GitHub repo → Actions → Latest run → Artifacts

---

## 💰 Cost
| Service | Cost |
|---|---|
| GitHub Actions | Free (2,000 min/month) |
| Groq API | Free (14,400 req/day) |
| NewsAPI | Free (100 req/day) |
| Blogger | Free |
| **Total** | **$0/month** |
