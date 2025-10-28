# 🔧 Code Migration Guide: SQLite to Supabase

This guide shows how to update your code files to work with both SQLite and Supabase using the new unified `db_config.py` module.

---

## 📋 Overview

**New Module**: `src/db_config.py`
- ✅ Unified database abstraction
- ✅ Works with SQLite AND PostgreSQL/Supabase
- ✅ Switch using `USE_SUPABASE=true` in `.env`
- ✅ Zero downtime migration

---

## 🔄 Files Requiring Updates

### **Priority 1: Core Database Files (REQUIRED)**

1. ✅ `src/database.py` - Update `get_db_session()`
2. ✅ `src/analysis.py` - Replace `sqlite3.connect()`
3. ✅ `telegram_bot/spending_limits.py` - Replace `sqlite3.connect()`

### **Priority 2: Feature Files (IMPORTANT)**

4. ✅ `marimo_app/dashboard.py` - Replace `sqlite3.connect()`
5. ✅ `telegram_bot/visualizations.py` - Update if using raw SQL

### **Priority 3: Test/Utility Files (OPTIONAL)**

6. ⚠️ `check_database.py` - Update for testing
7. ⚠️ `testmarimo.py` - Update for testing
8. ⚠️ `test_marimo_setup.py` - Update for testing

---

## 📝 Migration Patterns

### **Pattern 1: SQLAlchemy ORM (database.py)**

**BEFORE:**
```python
from sqlalchemy import create_engine

def get_db_session(db_path=None):
    if db_path is None:
        db_path = get_default_db_path()
    engine = create_engine(f'sqlite:///{db_path}')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()
```

**AFTER:**
```python
from src.db_config import get_session, get_engine
from src.database import Base

def get_db_session(db_path=None):
    """
    Get database session (works with SQLite or Supabase).
    db_path parameter is ignored when USE_SUPABASE=true
    """
    if db_path is not None:
        # Legacy: specific db_path for SQLite
        engine = create_engine(f'sqlite:///{db_path}')
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        return Session()
    else:
        # Use unified config (supports both SQLite and Supabase)
        engine = get_engine()
        Base.metadata.create_all(engine)
        return get_session()
```

---

### **Pattern 2: Raw SQL with sqlite3 (analysis.py, spending_limits.py)**

**BEFORE:**
```python
import sqlite3

def get_db_path():
    current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(current_dir, 'invoices.db')

def get_db_connection():
    return sqlite3.connect(get_db_path())

def analyze_invoices(weeks_back: int | None = None):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        query = """
            SELECT COUNT(*) as total_invoices
            FROM invoices
            WHERE invoice_date >= ?
        """
        cursor.execute(query, (start_date,))
        result = cursor.fetchone()
        return result
    finally:
        conn.close()
```

**AFTER (Option A - Simple):**
```python
from src.db_config import get_raw_connection, get_placeholder

def analyze_invoices(weeks_back: int | None = None):
    conn = get_raw_connection()  # Auto-detects SQLite or PostgreSQL
    try:
        cursor = conn.cursor()
        placeholder = get_placeholder()  # '?' for SQLite, '%s' for PostgreSQL
        query = f"""
            SELECT COUNT(*) as total_invoices
            FROM invoices
            WHERE invoice_date >= {placeholder}
        """
        cursor.execute(query, (start_date,))
        result = cursor.fetchone()
        return result
    finally:
        conn.close()
```

**AFTER (Option B - Even Simpler):**
```python
from src.db_config import execute_query

def analyze_invoices(weeks_back: int | None = None):
    query = """
        SELECT COUNT(*) as total_invoices
        FROM invoices
        WHERE invoice_date >= ?
    """
    result = execute_query(query, params=(start_date,), fetch_one=True)
    return result
```

---

### **Pattern 3: Dashboard with pandas (marimo_app/dashboard.py)**

**BEFORE:**
```python
import sqlite3
import pandas as pd

def get_db_path():
    return 'invoices.db'

def load_invoice_data(weeks_back):
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    
    query = """SELECT * FROM invoices WHERE invoice_date >= ?"""
    df = pd.read_sql_query(query, conn, params=(start_date,))
    conn.close()
    return df
```

**AFTER:**
```python
import pandas as pd
from src.db_config import get_raw_connection, get_placeholder

def load_invoice_data(weeks_back):
    conn = get_raw_connection()  # Auto-detects database
    placeholder = get_placeholder()
    
    query = f"""SELECT * FROM invoices WHERE invoice_date >= {placeholder}"""
    df = pd.read_sql_query(query, conn, params=(start_date,))
    conn.close()
    return df
```

---

## 🚀 Step-by-Step Migration

### **Step 1: Add db_config.py** ✅ DONE
Already created at `src/db_config.py`

### **Step 2: Update .env file**
Add the control flag:
```env
# Database Selection (set to 'true' to use Supabase)
USE_SUPABASE=false

# Supabase credentials (for when USE_SUPABASE=true)
SUPABASE_DB_HOST=db.xxxxxxxxxxxxx.supabase.co
SUPABASE_DB_PORT=5432
SUPABASE_DB_NAME=postgres
SUPABASE_DB_USER=postgres
SUPABASE_DB_PASSWORD=your-password-here
```

### **Step 3: Update Core Files**

Run these updates in order:

```bash
# 1. Update database.py
# See detailed example below

# 2. Update analysis.py  
# See detailed example below

# 3. Update spending_limits.py
# See detailed example below

# 4. Test with SQLite first
USE_SUPABASE=false python test_bot_connection.py

# 5. Test with Supabase
USE_SUPABASE=true python test_bot_connection.py
```

### **Step 4: Gradual Rollout**

1. **Week 1**: Test with SQLite (USE_SUPABASE=false)
2. **Week 2**: Test with Supabase (USE_SUPABASE=true)
3. **Week 3**: Switch production to Supabase
4. **Week 4**: Remove SQLite fallback code (optional)

---

## 📄 Detailed File Updates

### **File 1: src/database.py**

**What to change:**
- Update `get_db_session()` to use `db_config`
- Keep existing models (Invoice, InvoiceItem) unchanged

**Changes needed:**
```python
# ADD at top:
from src.db_config import get_session, get_engine

# MODIFY get_db_session():
def get_db_session(db_path=None):
    """
    Creates a database session (SQLite or Supabase based on config).
    db_path parameter only used for SQLite legacy mode.
    """
    if db_path is not None:
        # Legacy mode: specific SQLite database
        engine = create_engine(f'sqlite:///{db_path}')
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        return Session()
    else:
        # Use unified config
        engine = get_engine()
        Base.metadata.create_all(engine)
        return get_session()
```

---

### **File 2: src/analysis.py**

**What to change:**
- Replace `get_db_connection()` with `db_config.get_raw_connection()`
- Update SQL placeholders using `get_placeholder()`

**Find and replace:**
```python
# OLD imports:
import sqlite3
def get_db_path():
    ...
def get_db_connection():
    return sqlite3.connect(get_db_path())

# NEW imports:
from src.db_config import get_raw_connection, get_placeholder

# DELETE get_db_path() and get_db_connection()

# UPDATE all functions:
def analyze_invoices(weeks_back: int | None = None):
    conn = get_raw_connection()  # <-- CHANGED
    try:
        cursor = conn.cursor()
        placeholder = get_placeholder()  # <-- NEW
        
        where_clause = ""
        if weeks_back is not None and weeks_back > 0:
            where_clause = f"WHERE invoice_date >= {placeholder}"  # <-- CHANGED
            # Rest of code unchanged
```

---

### **File 3: telegram_bot/spending_limits.py**

**What to change:**
- Replace `get_db_path()` and `sqlite3.connect()`
- Update all SQL queries with placeholders

**Find and replace:**
```python
# OLD:
import sqlite3
def get_db_path():
    current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(current_dir, 'invoices.db')

# NEW:
from src.db_config import get_raw_connection, get_placeholder

# UPDATE init_spending_limits_table():
def init_spending_limits_table():
    conn = get_raw_connection()  # <-- CHANGED
    try:
        cursor = conn.cursor()
        # SQL unchanged - works for both databases
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS spending_limits (...)
        ''')
        conn.commit()
    finally:
        conn.close()

# UPDATE set_monthly_limit():
def set_monthly_limit(user_id: int, limit_amount: float) -> bool:
    conn = get_raw_connection()  # <-- CHANGED
    try:
        cursor = conn.cursor()
        placeholder = get_placeholder()  # <-- NEW
        
        # Note: Need to update UPSERT syntax for PostgreSQL
        if get_db_type() == "postgresql":
            cursor.execute(f'''
                INSERT INTO spending_limits (user_id, monthly_limit, updated_at)
                VALUES ({placeholder}, {placeholder}, CURRENT_TIMESTAMP)
                ON CONFLICT(user_id) DO UPDATE SET
                    monthly_limit = EXCLUDED.monthly_limit,
                    updated_at = CURRENT_TIMESTAMP
            ''', (user_id, limit_amount))
        else:
            # SQLite version
            cursor.execute(f'''
                INSERT INTO spending_limits (user_id, monthly_limit, updated_at)
                VALUES ({placeholder}, {placeholder}, CURRENT_TIMESTAMP)
                ON CONFLICT(user_id) DO UPDATE SET
                    monthly_limit = excluded.monthly_limit,
                    updated_at = CURRENT_TIMESTAMP
            ''', (user_id, limit_amount))
        
        conn.commit()
        return True
    except Exception:
        return False
    finally:
        conn.close()
```

---

## ⚠️ SQL Dialect Differences

### **UPSERT Operations**

**SQLite:**
```sql
INSERT ... ON CONFLICT(user_id) DO UPDATE SET ...
```

**PostgreSQL (same syntax! ✅):**
```sql
INSERT ... ON CONFLICT(user_id) DO UPDATE SET ...
```
→ Both use same syntax, but watch for `excluded` vs `EXCLUDED`

### **Date Functions**

**SQLite:**
```sql
date('now')
datetime('now')
CURRENT_TIMESTAMP
```

**PostgreSQL:**
```sql
CURRENT_DATE
NOW()
CURRENT_TIMESTAMP
```

### **String Functions**

Most functions are compatible, but PostgreSQL is case-sensitive for function names.

---

## ✅ Testing Checklist

After updating each file:

- [ ] Test with SQLite: `USE_SUPABASE=false`
  - [ ] Upload invoice via Telegram
  - [ ] Check `/analysis` command
  - [ ] Set spending limit
  - [ ] View dashboard

- [ ] Test with Supabase: `USE_SUPABASE=true`
  - [ ] Upload invoice via Telegram
  - [ ] Check `/analysis` command
  - [ ] Set spending limit
  - [ ] View dashboard

- [ ] Compare results (should be identical)

---

## 🎯 Quick Start Commands

```bash
# 1. Test current SQLite setup
$env:USE_SUPABASE="false"
python telegram_bot/bot.py

# 2. Run migration to Supabase
python migration/migrate.py

# 3. Test with Supabase
$env:USE_SUPABASE="true"
python telegram_bot/bot.py

# 4. If all good, update .env permanently
# Edit .env: USE_SUPABASE=true
```

---

## 📞 Need Help?

If you encounter issues:

1. Check `.env` has all Supabase credentials
2. Run `python migration/test_connection.py`
3. Check database type: `python -c "from src.db_config import print_db_info; print_db_info()"`
4. Review error logs for SQL syntax issues

---

## 🎉 Benefits of This Approach

✅ **Zero Downtime**: Switch between databases instantly  
✅ **Easy Rollback**: Set `USE_SUPABASE=false` if issues occur  
✅ **Gradual Migration**: Test thoroughly before committing  
✅ **Future-Proof**: Easy to add other databases later  
✅ **Clean Code**: Single source of truth for DB connections  

---

**Next Steps**: See `USER_INVOICE_OWNERSHIP_GUIDE.md` for recommendation #2
