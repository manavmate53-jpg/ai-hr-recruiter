# 🚀 Deploy AI HR Recruiter to Web

## Why Deploy?
- ✅ Access from anywhere via a link
- ✅ No need to run locally every time
- ✅ Share with others
- ✅ Always online (no daily updates needed)

## Option 1: Netlify (Recommended - 100% Free)

### Step 1: Push to GitHub First
```bash
cd "/Users/manav/CascadeProjects/ai hr recruiter"
git add .
git commit -m "Add deployment config"
git push -u origin main
```

**Note**: You'll need to authenticate with GitHub. Use a Personal Access Token:
- Go to: https://github.com/settings/tokens
- Generate new token (classic)
- Select `repo` scope
- Copy token and use as password

### Step 2: Deploy to Netlify
1. Go to: https://app.netlify.com/
2. Sign up/Login (use GitHub account)
3. Click "Add new site" → "Import an existing project"
4. Choose "GitHub" and select `ai-hr-recruiter`
5. Click "Deploy site"

**Your app will be live at**: `https://your-app-name.netlify.app`

### Step 3: Custom Domain (Optional)
- In Netlify dashboard → Domain settings
- Add custom domain or use free `.netlify.app` subdomain

---

## Option 2: GitHub Pages (Free)

```bash
# Enable GitHub Pages
git checkout -b gh-pages
git push origin gh-pages
```

Then:
1. Go to: https://github.com/manavmate53-jpg/ai-hr-recruiter/settings/pages
2. Source: Deploy from branch `gh-pages`
3. Click Save

**Your app will be at**: `https://manavmate53-jpg.github.io/ai-hr-recruiter/ai-hr-recruiter-app.html`

---

## Option 3: Vercel (Free)

```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
cd "/Users/manav/CascadeProjects/ai hr recruiter"
vercel --prod
```

**Your app will be at**: `https://ai-hr-recruiter.vercel.app`

---

## Backend Deployment (For Full Features)

Your Flask backend needs separate hosting:

### Option A: Railway.app (Free Tier)
1. Go to: https://railway.app
2. Create new project
3. Upload `backend` folder
4. Add environment variables
5. Get backend URL: `https://your-app.railway.app`

### Option B: Render.com (Free)
1. Go to: https://render.com
2. New Web Service
3. Connect GitHub repo
4. Root directory: `backend`
5. Build command: `pip install -r requirements.txt`
6. Start command: `python app.py`

### Update Frontend to Use Deployed Backend
Edit `ai-hr-recruiter-app.html` line 31:
```javascript
const API_URL = 'https://your-backend.railway.app'; // Replace with your backend URL
```

---

## 🎯 Recommended Setup

**Best combination for zero cost**:
- **Frontend**: Netlify (free, fast, custom domain)
- **Backend**: Railway or Render (free tier)

**Result**: 
- Permanent link that works 24/7
- No need to run locally
- Share with anyone
- Auto-updates when you push to GitHub

---

## After Deployment

Your app will be accessible at a permanent URL like:
- `https://ai-hr-recruiter.netlify.app`
- `https://manavmate53-jpg.github.io/ai-hr-recruiter`

**No daily updates needed** - it stays online automatically!
