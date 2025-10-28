# 🚂 Deployment Configuration

This folder contains all files needed to deploy the Invoice RAG bot to Railway.app.

---

## 📁 Files Overview

### Configuration Files (Required by Railway)
- **`railway.json`** - Railway platform configuration
- **`Procfile`** - Process definition (tells Railway what to run)
- **`runtime.txt`** - Python version specification
- **`.railwayignore`** - Files to exclude from deployment

### Environment Configuration
- **`.env.railway`** - Template for Railway environment variables

### Deployment Scripts
- **`deploy.ps1`** - PowerShell deployment preparation script
- **`deploy.sh`** - Bash deployment preparation script

### Documentation
- **`RAILWAY_QUICKSTART.md`** - ⚡ 5-minute quick start guide
- **`RAILWAY_DEPLOYMENT.md`** - 📖 Complete deployment documentation
- **`DEPLOYMENT_CHECKLIST.md`** - ✅ Step-by-step checklist

---

## 🚀 Quick Start

1. **Run deployment preparation:**
   ```powershell
   cd deployment
   .\deploy.ps1
   ```

2. **Follow the guide:**
   - Read [`RAILWAY_QUICKSTART.md`](RAILWAY_QUICKSTART.md) for 5-minute setup
   - Or [`RAILWAY_DEPLOYMENT.md`](RAILWAY_DEPLOYMENT.md) for detailed instructions

3. **Deploy to Railway:**
   - Push to GitHub
   - Connect Railway to your repo
   - Add environment variables
   - Deploy! ✅

---

## 📋 What You Need

Before deploying, make sure you have:

- ✅ GitHub account with your code pushed
- ✅ Railway.app account (free tier available)
- ✅ Telegram Bot Token (from @BotFather)
- ✅ Groq API Key (from console.groq.com)

---

## 📖 Documentation

1. **[RAILWAY_QUICKSTART.md](RAILWAY_QUICKSTART.md)** - Start here for quick deployment
2. **[RAILWAY_DEPLOYMENT.md](RAILWAY_DEPLOYMENT.md)** - Detailed guide with troubleshooting
3. **[DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)** - Verify your deployment

---

## 🔗 Important Links

- **Railway Dashboard:** [railway.app/dashboard](https://railway.app/dashboard)
- **Railway Docs:** [docs.railway.app](https://docs.railway.app)
- **Telegram BotFather:** [t.me/botfather](https://t.me/botfather)
- **Groq Console:** [console.groq.com](https://console.groq.com)

---

## 💡 Pro Tips

1. **Use the deployment script** - It checks everything before you deploy
2. **Start with QUICKSTART** - Don't skip the 5-minute guide
3. **Use the checklist** - Ensures nothing is missed
4. **Monitor first 24h** - Check Railway logs regularly

---

## 🆘 Need Help?

- Check [`RAILWAY_DEPLOYMENT.md`](RAILWAY_DEPLOYMENT.md) troubleshooting section
- Review [`DEPLOYMENT_CHECKLIST.md`](DEPLOYMENT_CHECKLIST.md) for common issues
- Check Railway logs in the dashboard

---

**Ready to deploy? Start with `RAILWAY_QUICKSTART.md`! 🚀**
