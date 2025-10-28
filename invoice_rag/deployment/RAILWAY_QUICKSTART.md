# 🚀 Railway Deployment - Quick Start

## ⚡ 5-Minute Setup

### 1️⃣ Prepare Repository
```powershell
# Run the deployment preparation script
.\deploy.ps1

# Commit and push
git commit -m "feat: add Railway deployment configuration"
git push origin main
```

### 2️⃣ Create Railway Project
1. Go to [railway.app](https://railway.app)
2. Login with GitHub
3. Click **"New Project"** → **"Deploy from GitHub repo"**
4. Select repository: `hackathon`
5. Set root directory: `invoice_rag` (if needed)

### 3️⃣ Add Environment Variables
Click **"Variables"** tab and add:

| Variable | Value | Get From |
|----------|-------|----------|
| `TELEGRAM_BOT_TOKEN` | Your bot token | [@BotFather](https://t.me/botfather) |
| `GROQ_API_KEY` | Your API key | [console.groq.com](https://console.groq.com/keys) |
| `PYTHONUNBUFFERED` | `1` | (Required for Railway) |

**Optional:**
| Variable | Default Value |
|----------|---------------|
| `OCR_MODEL` | `meta-llama/llama-4-scout-17b-16e-instruct` |
| `CHAT_MODEL` | `llama-3.3-70b-versatile` |

### 4️⃣ Add Persistent Storage
1. Click **"+ New"** → **"Volume"**
2. Name: `invoice-database`
3. Mount path: `/app/database`
4. Size: 1 GB

### 5️⃣ Deploy
- Railway will automatically deploy
- Wait for status: **"Active"** ✅
- Check logs for: `"Bot started successfully!"`

### 6️⃣ Test
1. Open Telegram
2. Search for your bot
3. Send `/start`
4. Upload a receipt photo
5. Send `/analysis`

---

## 📋 Deployment Checklist

- [ ] ✅ `railway.json` file created
- [ ] ✅ `Procfile` file created
- [ ] ✅ `runtime.txt` file created
- [ ] ✅ `.railwayignore` file created
- [ ] ✅ `.env` is in `.gitignore` (NOT committed)
- [ ] ✅ Code pushed to GitHub
- [ ] ✅ Railway project created
- [ ] ✅ Environment variables added
- [ ] ✅ Volume added for database
- [ ] ✅ Deployment successful
- [ ] ✅ Bot responding on Telegram

---

## 🔗 Important Links

- **Railway Dashboard:** [railway.app/dashboard](https://railway.app/dashboard)
- **Telegram BotFather:** [t.me/botfather](https://t.me/botfather)
- **Groq Console:** [console.groq.com](https://console.groq.com)
- **Full Guide:** See `RAILWAY_DEPLOYMENT.md`

---

## 🆘 Troubleshooting

### Bot Not Starting
```
Railway Dashboard → Your Service → Logs
```
Check for errors and verify environment variables

### Database Not Persisting
- Verify volume is mounted at `/app/database`
- Check volume status in Railway dashboard

### Out of Memory
- Check usage in Railway dashboard
- Default 512MB should be enough
- Upgrade to Developer plan if needed

---

## 💰 Free Tier Limits

- ✅ $5 free credits per month
- ✅ ~500 hours runtime (~20 days)
- ✅ 1 GB database storage
- ✅ Good for personal use!

---

## 🎉 That's It!

Your bot is now deployed and running 24/7 on Railway!

**Next Steps:**
- Monitor logs for first 24 hours
- Test all bot features
- Set up automatic cleanup: `/cleanup`
- Share your bot with friends!

---

**Need Help?** Check `RAILWAY_DEPLOYMENT.md` for detailed guide.
