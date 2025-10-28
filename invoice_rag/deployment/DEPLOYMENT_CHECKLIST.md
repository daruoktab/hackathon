# ✅ Railway Deployment Checklist

Use this checklist to ensure everything is ready for deployment.

---

## 📦 Pre-Deployment Checklist

### Local Development
- [ ] Bot works locally (`python run_bot.py`)
- [ ] All features tested (upload, analysis, chat)
- [ ] Database located at `database/invoices.db`
- [ ] No errors in local testing
- [ ] `.env` file contains working credentials

### Repository Preparation
- [ ] Code committed to Git
- [ ] `.env` file is in `.gitignore` (NOT committed)
- [ ] `google_credentials.json` is in `.gitignore` (if used)
- [ ] All changes pushed to GitHub
- [ ] Repository is public or Railway has access

### Railway Configuration Files
- [ ] `railway.json` exists
- [ ] `Procfile` exists
- [ ] `runtime.txt` exists (specifies Python 3.11.7)
- [ ] `requirements.txt` is up to date
- [ ] `.railwayignore` exists

---

## 🚂 Railway Setup Checklist

### Project Creation
- [ ] Logged into Railway.app
- [ ] GitHub account connected
- [ ] New project created
- [ ] Repository selected: `hackathon`
- [ ] Root directory set (if needed): `invoice_rag`
- [ ] Railway detected as Python project

### Environment Variables
Required:
- [ ] `TELEGRAM_BOT_TOKEN` = `[your_bot_token]`
- [ ] `GROQ_API_KEY` = `[your_groq_key]`
- [ ] `PYTHONUNBUFFERED` = `1`

Optional:
- [ ] `OCR_MODEL` = `meta-llama/llama-4-scout-17b-16e-instruct`
- [ ] `CHAT_MODEL` = `llama-3.3-70b-versatile`

### Storage Configuration
- [ ] Volume created: `invoice-database`
- [ ] Mount path: `/app/database`
- [ ] Size: 1 GB
- [ ] Volume linked to service

---

## 🚀 Deployment Checklist

### Initial Deployment
- [ ] Deployment triggered (automatic or manual)
- [ ] Build completed successfully
- [ ] No build errors in logs
- [ ] Service status: "Active" ✅
- [ ] Logs show: "Bot started successfully!"

### Post-Deployment Testing
- [ ] Bot is online in Telegram
- [ ] `/start` command works
- [ ] Can upload photo of receipt
- [ ] Photo processing works
- [ ] Invoice saved to database
- [ ] `/analysis` shows dashboard
- [ ] `/recent_invoices` displays data
- [ ] `/chat` responds correctly
- [ ] Budget features work (`/set_limit`, `/check_limit`)

---

## 🔍 Verification Checklist

### Telegram Bot
- [ ] Bot responds immediately
- [ ] All commands work
- [ ] Image upload works
- [ ] Dashboard generates correctly
- [ ] No error messages

### Database
- [ ] Data persists after restart
- [ ] Multiple invoices can be added
- [ ] Analysis includes all data
- [ ] No "database locked" errors

### Railway Dashboard
- [ ] CPU usage: < 50%
- [ ] Memory usage: < 400 MB
- [ ] No error logs
- [ ] Service uptime: 100%
- [ ] Volume usage tracking

---

## 📊 Monitoring Checklist (First 24 Hours)

### Hour 1
- [ ] Bot still responding
- [ ] No errors in Railway logs
- [ ] Memory stable
- [ ] CPU normal

### Hour 6
- [ ] Service still active
- [ ] Database writes working
- [ ] No crashes or restarts
- [ ] Response time normal

### Hour 24
- [ ] Continuous uptime
- [ ] All features working
- [ ] No memory leaks
- [ ] Database healthy

---

## 🆘 Troubleshooting Checklist

### If Bot Not Starting
- [ ] Check Railway logs for errors
- [ ] Verify environment variables are set
- [ ] Check `TELEGRAM_BOT_TOKEN` is correct
- [ ] Check `GROQ_API_KEY` is valid
- [ ] Verify Python version in `runtime.txt`

### If Database Issues
- [ ] Volume is mounted at `/app/database`
- [ ] Volume has enough space
- [ ] Check file permissions
- [ ] Verify database path in code

### If Memory Issues
- [ ] Check memory usage in Railway
- [ ] Look for memory leaks in logs
- [ ] Consider upgrading plan
- [ ] Optimize code if needed

---

## 💰 Cost Monitoring Checklist

### Free Tier Tracking
- [ ] Current usage: $_____ / $5.00
- [ ] Estimated monthly cost: $_____
- [ ] Days remaining on free tier: ___
- [ ] Alerts set for 80% usage

### Usage Optimization
- [ ] Cleanup old database entries
- [ ] Monitor API call frequency
- [ ] Check for infinite loops
- [ ] Optimize image processing

---

## 🎉 Success Criteria

All of these should be ✅ for successful deployment:

- [ ] ✅ Bot is live 24/7
- [ ] ✅ All Telegram commands work
- [ ] ✅ Photo upload and processing works
- [ ] ✅ Database persists data
- [ ] ✅ Dashboard generates correctly
- [ ] ✅ No errors in logs
- [ ] ✅ Within free tier limits
- [ ] ✅ Response time < 3 seconds
- [ ] ✅ Uptime > 99%

---

## 📝 Notes

**Deployment Date:** __________________

**Railway Project URL:** __________________

**Bot Username:** @__________________

**Free Tier Expiry:** __________________

**Issues Encountered:**
- 
- 
- 

**Solutions Applied:**
- 
- 
- 

---

**Next Steps After Successful Deployment:**

1. [ ] Share bot with friends/family
2. [ ] Monitor usage for 7 days
3. [ ] Set up automatic database cleanup
4. [ ] Create backup strategy
5. [ ] Document any custom configurations
6. [ ] Consider premium features

---

**Congratulations on your deployment! 🎊**

Keep this checklist for future reference and maintenance.
