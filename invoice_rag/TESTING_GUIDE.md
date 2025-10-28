# 🧪 Testing Guide - Migration & Premium Feature

## ✅ Migration Status: COMPLETE

### What Was Done:
1. ✅ Executed `create_schema.sql` in Supabase - Created core tables
2. ✅ Executed `premium_schema.sql` in Supabase - Created premium tables
3. ✅ Ran data migration (0 records migrated - SQLite was empty)
4. ✅ Updated `.env` with `USE_SUPABASE=true`
5. ✅ Verified Supabase connection works
6. ✅ Updated `telegram_bot/bot.py` with all 7 premium feature changes
7. ✅ Bot imports successfully without errors

---

## 🧪 Test Premium Feature

### Step 1: Start the Bot

```powershell
cd "E:\Github Project\hackathon\invoice_rag"
conda activate Hackthon
python telegram_bot/bot.py
```

### Step 2: Test Token (7 Days Valid)

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NjIyNTU3NjAsImlhdCI6MTc2MTY1MDk2MCwiZHVyYXRpb24iOiI3IGRheXMiLCJwdXJwb3NlIjoicHJlbWl1bV9jbGFpbSJ9.lBiCAC5WHKmN7GF-R-FkxhRHH5BfZUYmwkowZoF4pLU
```

### Step 3: Test in Telegram

1. **Start Bot**: Send `/start`
   - Should see welcome message with `/premium` button
   - Should see user created in database

2. **Try Analysis (Without Premium)**: Send `/analysis`
   - Should get "Premium Feature" message with "Get Premium" button
   - Should be blocked from accessing analytics

3. **Claim Premium**: 
   - Send `/premium`
   - Click "🎫 Claim Token" button
   - Paste the test token above
   - Should see "✅ Premium activated successfully!"

4. **Try Analysis (With Premium)**: Send `/analysis`
   - Should now work and show analytics
   - Should generate visualization

5. **Test Token Reuse**: Try to claim the same token again
   - Should get error: "This token has already been used"

6. **Check Premium Persists**: 
   - Send `/start` - Should see "✨ Premium Active ✨"
   - Restart bot and test again - Premium should still be active

---

## 🔧 Generate More Test Tokens

```powershell
# 7 days token
python -c "from telegram_bot.premium import generate_test_token; print(generate_test_token(7))"

# 30 days token
python -c "from telegram_bot.premium import generate_test_token; print(generate_test_token(30))"

# 365 days token
python -c "from telegram_bot.premium import generate_test_token; print(generate_test_token(365))"
```

---

## 📊 Verify Database

### Check User Creation
```sql
SELECT * FROM "user" ORDER BY created_at DESC LIMIT 5;
```

### Check Premium Data
```sql
SELECT u.telegram_id, u.display_name, pd.is_premium, pd.premium_until
FROM "user" u
LEFT JOIN premium_data pd ON u.id = pd.user_id
WHERE u.telegram_id IS NOT NULL;
```

### Check Token Usage
```sql
SELECT * FROM token ORDER BY claimed_at DESC LIMIT 10;
```

---

## 🐛 Troubleshooting

### Issue: Bot won't start
**Solution**: Check `.env` has correct `USE_SUPABASE=true` and all credentials

### Issue: "Module not found" error
**Solution**: 
```powershell
pip install -r requirements.txt
```

### Issue: Database connection fails
**Solution**: 
```powershell
python -c "from src.db_config import get_engine; print(get_engine().url)"
```
Should show Supabase URL

### Issue: Token validation fails
**Solution**: Make sure `JWT_SECRET_KEY` in `.env` matches the one used to generate token

### Issue: Premium not persisting
**Solution**: Check that `activate_premium()` function ran successfully:
```sql
SELECT * FROM premium_data WHERE user_id = (SELECT id FROM "user" WHERE telegram_id = 'YOUR_TELEGRAM_ID');
```

---

## ✨ Next Steps

1. **Upload Invoice**: Test invoice upload flow with Supabase
2. **Check Spending Limits**: Verify limits work with new database
3. **Test Analytics**: Upload some test invoices and run full analysis
4. **Production Token**: Generate secure tokens with strong JWT_SECRET_KEY
5. **Deploy**: Consider hosting bot on cloud server

---

## 🎯 Success Criteria Checklist

- [ ] Bot starts without errors
- [ ] `/start` creates user in database
- [ ] `/analysis` blocked for non-premium users
- [ ] `/premium` shows claim interface
- [ ] Token claim activates premium successfully
- [ ] Token can't be reused
- [ ] Premium persists after restart
- [ ] `/analysis` works for premium users
- [ ] Premium status shows in `/start` message

---

## 📝 Important Notes

1. **JWT Secret**: The `JWT_SECRET_KEY` in `.env` is for testing only. Use a secure random string in production.

2. **Network Issue**: Direct PostgreSQL connection (port 5432) is blocked by firewall, but Supabase REST API works fine. All operations use the REST API.

3. **Empty Database**: Your SQLite database was empty, so 0 records were migrated. You can start fresh with Supabase.

4. **Token Expiry**: Test tokens expire after 7 days. Generate new ones as needed.

5. **Premium Duration**: Currently set to 7 days. Modify in `activate_premium()` function for different durations.

---

✅ **Migration Complete!**
✅ **Premium Feature Implemented!**

🚀 Ready to test!
