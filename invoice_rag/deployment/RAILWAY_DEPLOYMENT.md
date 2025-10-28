# 🚂 Railway.app Deployment Guide

Complete guide to deploy the Invoice RAG Telegram Bot on Railway.app.

---

## 📋 Prerequisites

Before you begin, make sure you have:

1. ✅ **GitHub Account** - Your code needs to be in a GitHub repository
2. ✅ **Railway.app Account** - Sign up at [railway.app](https://railway.app) (free)
3. ✅ **Telegram Bot Token** - Get from [@BotFather](https://t.me/botfather)
4. ✅ **Groq API Key** - Get from [console.groq.com](https://console.groq.com)
5. ✅ **Google Credentials** (Optional) - For Google Sheets integration

---

## 🚀 Step-by-Step Deployment

### Step 1: Prepare Your Repository

1. **Push your code to GitHub:**
   ```powershell
   cd "e:\Github Project\hackathon\invoice_rag"
   git add .
   git commit -m "feat: add Railway deployment configuration"
   git push origin main
   ```

2. **Verify these files exist in your repo:**
   - ✅ `railway.json` - Railway configuration
   - ✅ `Procfile` - Process definition
   - ✅ `runtime.txt` - Python version
   - ✅ `requirements.txt` - Python dependencies
   - ✅ `.railwayignore` - Files to exclude from deployment

---

### Step 2: Create Railway Project

1. **Go to Railway.app:**
   - Visit [railway.app](https://railway.app)
   - Click **"Login"** or **"Start a New Project"**
   - Login with your **GitHub account**

2. **Create New Project:**
   - Click **"New Project"**
   - Select **"Deploy from GitHub repo"**
   - Choose your repository: **`hackathon`**
   - Railway will detect it as a Python project

3. **Select Root Directory:**
   - If prompted, set root directory to: `invoice_rag`
   - Railway should auto-detect the configuration

---

### Step 3: Configure Environment Variables

In your Railway project dashboard:

1. Click on your service
2. Go to **"Variables"** tab
3. Add these environment variables:

#### Required Variables:

```env
# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here

# AI API Configuration
GROQ_API_KEY=your_groq_api_key_here

# Optional: Model Configuration
OCR_MODEL=meta-llama/llama-4-scout-17b-16e-instruct
CHAT_MODEL=llama-3.3-70b-versatile

# Python Environment
PYTHONUNBUFFERED=1
```

#### How to Add Variables:

1. Click **"+ New Variable"**
2. Enter **Variable Name** (e.g., `TELEGRAM_BOT_TOKEN`)
3. Enter **Variable Value** (your actual token)
4. Click **"Add"**
5. Repeat for all required variables

---

### Step 4: Add Persistent Storage (Database)

Railway doesn't persist files by default. We need to add a volume for SQLite database:

1. In your Railway project, click **"+ New"**
2. Select **"Volume"**
3. Configure the volume:
   - **Name:** `invoice-database`
   - **Mount Path:** `/app/database`
   - **Size:** 1 GB (free tier)

4. **Link to your service:**
   - The volume should automatically link
   - Verify in **"Settings"** → **"Volumes"**

---

### Step 5: Deploy

1. **Trigger Deployment:**
   - Railway will automatically deploy when you push to GitHub
   - Or click **"Deploy"** button in Railway dashboard

2. **Monitor Deployment:**
   - Go to **"Deployments"** tab
   - Watch the build logs
   - Wait for status: **"Active"** ✅

3. **Check Logs:**
   - Click **"View Logs"**
   - Look for: `"Bot started successfully!"`
   - Verify no errors

---

### Step 6: Verify Bot is Working

1. **Open Telegram:**
   - Search for your bot: `@YourBotName`
   - Send `/start` command
   - You should get a welcome message ✅

2. **Test Upload:**
   - Send a photo of a receipt
   - Bot should process it
   - Send `/analysis` to see dashboard

3. **Check Railway Logs:**
   - Any errors will appear in Railway logs
   - Go to **"Logs"** tab in Railway dashboard

---

## 📊 Database Management on Railway

### Accessing Your Database

Since SQLite runs on the Railway server, you can't directly access it. Here are options:

#### Option 1: Use Bot Commands (Recommended)
```
/recent_invoices - View recent data
/analysis - See all analytics
/chat Show me all my invoices - Query via AI
```

#### Option 2: Add Database Export Feature

Add this to your bot for periodic exports:
- Export to Google Sheets
- Download backup via `/export` command
- Automatic daily backups

#### Option 3: Railway CLI

```powershell
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Connect to your project
railway link

# Access shell
railway run bash

# View database
cd /app/database
sqlite3 invoices.db
```

---

## 🔄 Continuous Deployment

Railway automatically deploys when you push to GitHub:

```powershell
# Make changes to your code
git add .
git commit -m "feat: add new feature"
git push origin main

# Railway will automatically:
# 1. Detect the push
# 2. Build the new version
# 3. Deploy with zero downtime
# 4. Keep database intact
```

---

## 💰 Pricing & Limits

### Free Tier (Hobby Plan):
- ✅ $5 free credits per month
- ✅ 500 hours of usage (~20 days)
- ✅ 1 GB database storage
- ✅ Unlimited projects
- ✅ Automatic scaling

### Tips to Stay Within Free Tier:
- ✅ One bot uses ~0.5 GB RAM (~$2.50/month)
- ✅ Monitor usage in Railway dashboard
- ✅ Optimize database size with cleanup commands

---

## 🛠️ Troubleshooting

### Bot Not Starting

**Check Logs:**
```
Railway Dashboard → Your Service → Logs
```

**Common Issues:**

1. **Missing Environment Variables**
   - Verify all variables are set
   - Check for typos in variable names

2. **Database Permission Error**
   ```
   Error: Unable to write to database
   ```
   **Fix:** Verify volume is mounted at `/app/database`

3. **Import Error**
   ```
   ModuleNotFoundError: No module named 'xxx'
   ```
   **Fix:** Add missing package to `requirements.txt`

### Bot Stops After Some Time

**Issue:** Railway free tier has usage limits

**Solution:**
- Check usage in Railway dashboard
- Upgrade to Developer plan if needed ($5/month)
- Optimize code to reduce resource usage

### Database Gets Too Large

**Solution:**
```python
# Use cleanup commands regularly
python cleanup.py premium expired
python cleanup.py old 180

# Or via Telegram bot
/cleanup - Set up automatic cleanup
```

---

## 📈 Monitoring & Maintenance

### Check Bot Health

1. **Railway Dashboard:**
   - Memory usage
   - CPU usage
   - Request count
   - Error rate

2. **Telegram Bot:**
   ```
   /status - Check bot status
   /stats - Database statistics
   ```

### Database Backup Strategy

**Automatic Backups:**
- Railway takes daily snapshots (paid plans)
- Free tier: Manual backups recommended

**Manual Backup:**
1. Use bot export feature: `/export`
2. Download to Google Sheets
3. Use Railway CLI to download database

---

## 🔒 Security Best Practices

1. **Never Commit Secrets:**
   - ✅ Use Railway environment variables
   - ✅ Keep `.env` in `.gitignore`
   - ❌ Never commit API keys to GitHub

2. **Rotate Keys Regularly:**
   - Change bot token every 6 months
   - Update in Railway variables

3. **Monitor Access:**
   - Check Railway logs for suspicious activity
   - Enable GitHub notifications

---

## 🚀 Advanced Configuration

### Custom Domain (Optional)

1. Go to **"Settings"** → **"Domains"**
2. Add custom domain
3. Update DNS records
4. (Note: Not needed for Telegram bots)

### Multiple Environments

Create separate Railway projects for:
- **Production** - Main bot
- **Staging** - Testing new features
- **Development** - Local testing

### Scaling

Railway automatically scales, but you can configure:
- **Memory:** 512MB - 8GB
- **CPU:** Shared or dedicated
- **Replicas:** Run multiple instances

---

## 📞 Support

### Railway Support:
- [Railway Docs](https://docs.railway.app)
- [Railway Discord](https://discord.gg/railway)
- [Railway Status](https://status.railway.app)

### Project Issues:
- Check bot logs first
- Test locally with `python run_bot.py`
- Verify environment variables
- Check database connectivity

---

## ✅ Deployment Checklist

- [ ] Code pushed to GitHub
- [ ] Railway project created
- [ ] Environment variables configured
- [ ] Volume added for database
- [ ] Deployment successful
- [ ] Bot responding on Telegram
- [ ] Photo upload working
- [ ] `/analysis` command working
- [ ] Database persisting data
- [ ] Logs showing no errors

---

**Congratulations! Your bot is now deployed! 🎉**

Test it thoroughly and monitor the Railway dashboard for the first 24 hours.
