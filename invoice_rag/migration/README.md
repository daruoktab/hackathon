# 🚀 SQLite to Supabase Migration

Quick guide to migrate your Invoice RAG database from SQLite to Supabase PostgreSQL.

---

## ⚡ Quick Start (30 minutes)

### 1. Install Dependencies
```bash
pip install supabase>=2.22.2 psycopg2-binary>=2.9.11
```

### 2. Setup Supabase Project
1. Go to https://supabase.com and create a project
2. Wait 2-3 minutes for initialization
3. Get credentials from dashboard

### 3. Configure Environment
Add to your `.env` file (in `invoice_rag` directory):

```env
# API Credentials (from Settings > API)
SUPABASE_URL=https://xxxxxxxxxxxxx.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOi...
SUPABASE_SERVICE_KEY=eyJhbGciOi...

# Database Credentials (from Settings > Database)
SUPABASE_DB_HOST=db.xxxxxxxxxxxxx.supabase.co
SUPABASE_DB_PORT=5432
SUPABASE_DB_NAME=postgres
SUPABASE_DB_USER=postgres
SUPABASE_DB_PASSWORD=your-password-here
```

**Note**: You need BOTH API and Database credentials. Database credentials are used for actual migration and app queries (faster, direct access). API credentials are for optional Supabase features.

### 4. Test Connection
```bash
python migration/test_connection.py
```

### 5. Run Migration

**Option A: Interactive (Recommended)**
```bash
python migration/migrate.py
```
Choose from menu:
- Option 1: Pre-flight check
- Option 4: Full migration (auto export + import + verify)

**Option B: Manual Steps**
```bash
# Step 1: Create schema in Supabase
# - Go to Supabase Dashboard > SQL Editor
# - Copy/paste create_schema.sql and run it

# Step 2: Export SQLite data
python migration/export_sqlite_data.py

# Step 3: Import to Supabase
python migration/import_to_supabase.py migration/sqlite_export_*.json

# Step 4: Verify
python migration/migrate.py  # Choose option 5
```

---

## 📁 Files in This Directory

| File | Purpose |
|------|---------|
| `README.md` | This file - quick start guide |
| `create_schema.sql` | PostgreSQL schema (run in Supabase SQL Editor) |
| `export_sqlite_data.py` | Export SQLite data to JSON |
| `import_to_supabase.py` | Import JSON to Supabase |
| `migrate.py` | Interactive migration helper (menu-driven) |
| `test_connection.py` | Test Supabase connection before migration |

---

## 🔑 Getting Supabase Credentials

### API Credentials
**From**: Supabase Dashboard → Settings → API
- `SUPABASE_URL` = Project URL
- `SUPABASE_ANON_KEY` = anon public key
- `SUPABASE_SERVICE_KEY` = service_role key (click "reveal")

### Database Credentials
**From**: Supabase Dashboard → Settings → Database → "Connection Info"
- `SUPABASE_DB_HOST` = Host
- `SUPABASE_DB_PORT` = Port (usually 5432)
- `SUPABASE_DB_NAME` = Database name (usually postgres)
- `SUPABASE_DB_USER` = User (usually postgres)
- `SUPABASE_DB_PASSWORD` = Password you set during project creation

**Forgot password?** Click "Reset Database Password" on the same page.

---

## ✅ What Gets Migrated

```
✅ invoices table (with all records)
✅ invoice_items table (with all line items)
✅ platform_users table (Telegram/WhatsApp users)
✅ spending_limits table (budget tracking)
✅ spending_limits_v2 table (enhanced limits)
✅ All foreign key relationships
✅ Data integrity preserved
```

---

## 🧪 Testing After Migration

1. **Upload a test invoice** via Telegram bot
2. **Run analysis commands**: `/analysis`, `/recent`, `/visualizations`
3. **Check Supabase dashboard**: Table Editor → invoices
4. **Verify data**: Compare record counts with SQLite

---

## 🐛 Troubleshooting

### "Connection failed"
- Check credentials in `.env`
- Verify Supabase project is active (not paused)
- Check firewall allows port 5432

### "Table does not exist"
- Run `create_schema.sql` in Supabase SQL Editor first

### "Foreign key violation"
- Export/import runs tables in correct order automatically
- If manual import, ensure: users → invoices → items

### "Import failed"
- Ensure you're using `SUPABASE_SERVICE_KEY` (not anon key)
- Check database password is correct

---

## 🔄 Rollback Plan

If something goes wrong:
1. Stop your application
2. Revert code changes: `git reset --hard` or restore backup
3. Your SQLite data is untouched - just switch back to it
4. Update `.env` to use SQLite again

**Migration is non-destructive** - your original `invoices.db` remains intact!

---

## 📊 Migration Time

| Database Size | Export | Import | Total |
|--------------|--------|--------|-------|
| Small (<1K records) | 5s | 3s | ~10s |
| Medium (1K-10K) | 15s | 10s | ~30s |
| Large (>10K) | 60s | 30s | ~90s |

Plus setup time: ~20 minutes first time

---

## 📚 More Help

- **Detailed guide**: `../../SUPABASE_MIGRATION_GUIDE.md`
- **Test connection**: `python test_connection.py`
- **Interactive helper**: `python migrate.py`
- **Supabase docs**: https://supabase.com/docs

---

## 🎯 Success Checklist

- [ ] Supabase project created
- [ ] All credentials added to `.env`
- [ ] Connection test passed
- [ ] Schema created in Supabase
- [ ] Data exported from SQLite
- [ ] Data imported to Supabase
- [ ] Record counts match
- [ ] Test invoice upload works
- [ ] Bot commands work
- [ ] No errors in logs

---

**Made with ❤️ for easy migrations**