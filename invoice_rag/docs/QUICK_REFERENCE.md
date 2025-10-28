# 🎯 QUICK REFERENCE - Invoice Bot

## Start Bot
```powershell
cd "E:\Github Project\hackathon\invoice_rag"
conda activate Hackthon
python run_bot.py
```

## Generate Premium Token
```powershell
# 7 days
python -c "from telegram_bot.premium import generate_test_token; print(generate_test_token(7))"

# 30 days
python -c "from telegram_bot.premium import generate_test_token; print(generate_test_token(30))"
```

## Backup Database
```powershell
python backup_database.py
```

## Test Supabase Connection (Future)
```powershell
python test_supabase_connection.py
```

## Telegram Commands
```
/start        - Initialize bot & create user
/help         - Show help message
/premium      - View & claim premium
/analysis     - Advanced analytics (premium)
/set_limit    - Set monthly spending limit
/check_limit  - Check current limit
/upload_invoice - Upload receipt
/recent_invoices - View recent uploads
/chatmode     - Toggle AI chat mode
/clear        - Clear chat history
```

## Configuration
```env
# Current (Working)
USE_SUPABASE=false

# Database Location
invoices.db

# Backups Location
backups/invoices_YYYYMMDD_HHMMSS.db
```

## Troubleshooting
| Issue | Solution |
|-------|----------|
| Bot won't start | Check .env file exists |
| Premium not working | Check JWT_SECRET_KEY in .env |
| Database error | Run backup_database.py |
| Network error | Keep USE_SUPABASE=false |

## Important Files
- `run_bot.py` - Start bot
- `backup_database.py` - Backup DB
- `test_supabase_connection.py` - Test network
- `.env` - Configuration
- `invoices.db` - Database

## Status
✅ All features working
✅ Premium system operational  
✅ SQLite recommended
✅ Production-ready

## Support Docs
- `PROJECT_COMPLETE.md` - Full project summary
- `FINAL_SUPABASE_SOLUTION.md` - IPv6 solution
- `TESTING_GUIDE.md` - Premium testing
- `DNS_FIX_GUIDE.md` - Network fixes
