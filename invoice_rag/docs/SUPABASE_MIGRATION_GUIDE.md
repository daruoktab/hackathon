# 🚀 Supabase Migration Guide

Complete guide to migrate Invoice RAG from SQLite to Supabase PostgreSQL.

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Quick Start](#quick-start)
4. [Detailed Steps](#detailed-steps)
5. [Code Changes](#code-changes)
6. [Troubleshooting](#troubleshooting)

---

## Overview

### What This Migration Does

Migrates your Invoice RAG application from:
- **SQLite** (local file `invoices.db`) 
- **Supabase** (cloud PostgreSQL database)

### Benefits
- ☁️ Cloud-hosted, no local file management
- 🚀 Better concurrent access
- 🔒 Automatic backups
- 📊 Advanced PostgreSQL features
- 🌍 Access from anywhere

### Database Complexity
- **5 tables** with foreign key relationships
- **~15 Python files** need updates
- **Mixed queries**: SQLAlchemy ORM + raw SQL
- **Estimated time**: 4-8 hours (including testing)
- **Risk**: Low (SQLite backup remains intact)

---

## Prerequisites

### 1. Install Dependencies
```bash
pip install supabase>=2.22.2 psycopg2-binary>=2.9.11
```

### 2. Create Supabase Account
1. Go to https://supabase.com
2. Sign up (free tier is fine)
3. Create new project
4. Set a strong database password (save it!)
5. Choose region close to you
6. Wait 2-3 minutes for initialization

### 3. Get Credentials

You need **BOTH** API and Database credentials:

#### API Credentials (Settings > API)
```
SUPABASE_URL              → Project URL
SUPABASE_ANON_KEY         → anon public key
SUPABASE_SERVICE_KEY      → service_role key (click "reveal")
```

#### Database Credentials (Settings > Database)
```
SUPABASE_DB_HOST          → Host (db.xxxxx.supabase.co)
SUPABASE_DB_PORT          → Port (5432)
SUPABASE_DB_NAME          → Database name (postgres)
SUPABASE_DB_USER          → User (postgres)
SUPABASE_DB_PASSWORD      → Password from project creation
```

**Why both?** Your app uses direct database connection (faster, better for SQLAlchemy). API credentials are for optional Supabase features (Storage, Real-time, etc).

---

## Quick Start

### Step 1: Configure Environment (5 min)

Add to `invoice_rag/.env`:

```env
# Supabase API
SUPABASE_URL=https://xxxxxxxxxxxxx.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOi...
SUPABASE_SERVICE_KEY=eyJhbGciOi...

# Supabase Database
SUPABASE_DB_HOST=db.xxxxxxxxxxxxx.supabase.co
SUPABASE_DB_PORT=5432
SUPABASE_DB_NAME=postgres
SUPABASE_DB_USER=postgres
SUPABASE_DB_PASSWORD=your-password-here

# Keep existing settings
GROQ_API_KEY=...
TELEGRAM_BOT_TOKEN=...
```

### Step 2: Test Connection (2 min)
```bash
cd invoice_rag
python migration/test_connection.py
```

### Step 3: Create Schema (3 min)
1. Open Supabase Dashboard → SQL Editor
2. Click "New Query"
3. Copy content from `migration/create_schema.sql`
4. Paste and click "Run"
5. Should see "Success" message

### Step 4: Run Migration (5 min)
```bash
python migration/migrate.py
```
Choose option 4: "Run Full Migration"

This will:
- Export SQLite data
- Import to Supabase
- Verify migration

### Step 5: Update Code (10 min)
See [Code Changes](#code-changes) section below.

### Step 6: Test (10 min)
- Upload test invoice via Telegram
- Run `/analysis` command
- Check data in Supabase dashboard
- Verify everything works

---

## Detailed Steps

### Manual Migration (if not using migrate.py)

#### 1. Export SQLite Data
```bash
python migration/export_sqlite_data.py
```
Output: `migration/sqlite_export_YYYYMMDD_HHMMSS.json`

#### 2. Create Schema in Supabase
- Open Supabase Dashboard → SQL Editor
- Copy/paste `migration/create_schema.sql`
- Run it

#### 3. Import to Supabase
```bash
python migration/import_to_supabase.py migration/sqlite_export_*.json
```

#### 4. Verify
```bash
python migration/migrate.py
# Choose option 5: Verify Migration
```

---

## Code Changes

### 1. Create Supabase Database Adapter

Create `src/database_supabase.py`:

```python
"""Supabase database adapter"""
from sqlalchemy import create_engine, Column, BigInteger, String, Float, DateTime, ForeignKey, DECIMAL
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, timezone
from enum import Enum
import os
from dotenv import load_dotenv

load_dotenv()
Base = declarative_base()

class TransactionType(str, Enum):
    BANK = "bank"
    RETAIL = "retail"
    E_COMMERCE = "e-commerce"

def get_supabase_connection_string():
    """Get Supabase PostgreSQL connection string"""
    host = os.environ.get("SUPABASE_DB_HOST")
    port = os.environ.get("SUPABASE_DB_PORT", "5432")
    database = os.environ.get("SUPABASE_DB_NAME", "postgres")
    user = os.environ.get("SUPABASE_DB_USER", "postgres")
    password = os.environ.get("SUPABASE_DB_PASSWORD")
    
    if not all([host, password]):
        raise ValueError("SUPABASE_DB_HOST and SUPABASE_DB_PASSWORD must be set")
    
    return f"postgresql://{user}:{password}@{host}:{port}/{database}"

class Invoice(Base):
    __tablename__ = 'invoices'
    
    id = Column(BigInteger, primary_key=True)
    shop_name = Column(String(255), nullable=False)
    invoice_date = Column(String)
    total_amount = Column(DECIMAL(15, 2), nullable=False)
    transaction_type = Column(String(50))
    processed_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    image_path = Column(String)
    
    items = relationship("InvoiceItem", back_populates="invoice", cascade="all, delete-orphan")

class InvoiceItem(Base):
    __tablename__ = 'invoice_items'
    
    id = Column(BigInteger, primary_key=True)
    invoice_id = Column(BigInteger, ForeignKey('invoices.id', ondelete='CASCADE'), nullable=False)
    item_name = Column(String(500), nullable=False)
    quantity = Column(BigInteger)
    unit_price = Column(DECIMAL(15, 2))
    total_price = Column(DECIMAL(15, 2), nullable=False)
    
    invoice = relationship("Invoice", back_populates="items")

def get_db_session(connection_string=None):
    """Creates database session with Supabase PostgreSQL"""
    if connection_string is None:
        connection_string = get_supabase_connection_string()
    
    engine = create_engine(
        connection_string,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,
        echo=False
    )
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()

def insert_invoice_data(session, invoice_data, image_path):
    """Inserts extracted invoice data into database"""
    try:
        invoice = Invoice(
            shop_name=invoice_data.shop_name,
            invoice_date=invoice_data.invoice_date,
            total_amount=float(invoice_data.total_amount),
            transaction_type=invoice_data.transaction_type,
            image_path=image_path
        )
        session.add(invoice)
        session.flush()
        
        for item_data in invoice_data.items:
            item = InvoiceItem(
                invoice_id=invoice.id,
                item_name=item_data.name,
                quantity=item_data.quantity,
                unit_price=float(item_data.unit_price) if item_data.unit_price else None,
                total_price=float(item_data.total_price)
            )
            session.add(item)
        
        session.commit()
        print(f"Successfully inserted invoice from {invoice_data.shop_name}")
        return invoice.id
    except Exception as e:
        print(f"Error inserting invoice data: {e}")
        session.rollback()
        return None

def get_all_invoices(session):
    """Retrieves all invoices"""
    return session.query(Invoice).all()

def get_invoices_with_items(session):
    """Retrieves all invoices with items"""
    invoices = session.query(Invoice).all()
    return [{'invoice': invoice, 'items': invoice.items} for invoice in invoices]
```

### 2. Update All Database Imports

Change in these files:
- `src/processor.py`
- `src/chatbot.py`
- `telegram_bot/bot.py`
- Any file importing `src.database`

**Change from:**
```python
from src.database import get_db_session, Invoice, InvoiceItem
```

**Change to:**
```python
from src.database_supabase import get_db_session, Invoice, InvoiceItem
```

### 3. Update Analysis Queries

In `src/analysis.py`, update database connection:

```python
import os
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor

load_dotenv()

def get_db_connection():
    """Get PostgreSQL connection"""
    return psycopg2.connect(
        host=os.environ.get("SUPABASE_DB_HOST"),
        port=os.environ.get("SUPABASE_DB_PORT", "5432"),
        database=os.environ.get("SUPABASE_DB_NAME", "postgres"),
        user=os.environ.get("SUPABASE_DB_USER", "postgres"),
        password=os.environ.get("SUPABASE_DB_PASSWORD"),
        cursor_factory=RealDictCursor
    )
```

Update SQL queries to use PostgreSQL syntax:
- `DATETIME()` → `NOW()` or `CURRENT_TIMESTAMP`
- `CURRENT_TIMESTAMP` → `NOW()` (preferred in PostgreSQL)
- Date intervals: `datetime('now', '-7 days')` → `CURRENT_DATE - INTERVAL '7 days'`

### 4. Update Spending Limits Module

In `telegram_bot/spending_limits.py`, update connection:

```python
import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()

def get_db_connection():
    """Get PostgreSQL connection"""
    return psycopg2.connect(
        host=os.environ.get("SUPABASE_DB_HOST"),
        port=os.environ.get("SUPABASE_DB_PORT", "5432"),
        database=os.environ.get("SUPABASE_DB_NAME", "postgres"),
        user=os.environ.get("SUPABASE_DB_USER", "postgres"),
        password=os.environ.get("SUPABASE_DB_PASSWORD")
    )
```

---

## Key Differences: SQLite vs PostgreSQL

### Data Types
| SQLite | PostgreSQL |
|--------|------------|
| `INTEGER` | `BIGINT` or `BIGSERIAL` |
| `REAL` | `NUMERIC(15,2)` |
| `TEXT` | `VARCHAR(n)` or `TEXT` |
| `TIMESTAMP` | `TIMESTAMP WITH TIME ZONE` |

### Auto-increment
```sql
-- SQLite
id INTEGER PRIMARY KEY AUTOINCREMENT

-- PostgreSQL
id BIGSERIAL PRIMARY KEY
```

### Functions
```sql
-- SQLite
CURRENT_TIMESTAMP
datetime('now', '-7 days')

-- PostgreSQL
NOW()
CURRENT_DATE - INTERVAL '7 days'
```

### Foreign Keys
- SQLite: Not enforced by default
- PostgreSQL: Always enforced

---

## Troubleshooting

### Connection Issues

**"Connection refused" or "Connection timeout"**
- Check firewall allows port 5432
- Verify Supabase project is active (not paused)
- Confirm credentials in `.env` are correct
- Try connecting from Supabase dashboard first

### Import Issues

**"Table does not exist"**
- Run `create_schema.sql` in Supabase SQL Editor first

**"Foreign key violation"**
- Import scripts handle correct order automatically
- If manual: import users → invoices → items

**"Authentication failed"**
- Use `SUPABASE_SERVICE_KEY` for imports (not anon key)
- Verify database password is correct

**"Import failed"**
- Check all credentials in `.env`
- Ensure Supabase project has enough space
- Try using PostgreSQL direct method (faster)

### Data Issues

**Data mismatch after import**
- Re-export from SQLite (ensure latest data)
- Clear Supabase tables and re-import
- Check for concurrent modifications

**Missing records**
- Verify export included all tables
- Check for errors in import log
- Use verify tool to compare counts

### Application Issues

**"Can't connect to database"**
- Check `.env` file has all Supabase credentials
- Test with `python migration/test_connection.py`
- Verify imports use `database_supabase` not `database`

**Queries failing**
- Update SQL syntax to PostgreSQL
- Check for SQLite-specific functions
- Review query logs in Supabase dashboard

---

## Rollback Plan

If migration fails, you can easily rollback:

1. **Stop application**
2. **Revert code changes**: 
   ```bash
   git reset --hard HEAD
   # or restore from backup
   ```
3. **Use SQLite**: Change imports back to `src.database`
4. **Restart application**

**Your SQLite data remains untouched!** Migration is non-destructive.

---

## Testing Checklist

After migration, verify:

- [ ] Database connection works
- [ ] Upload new invoice via Telegram
- [ ] `/analysis` command works
- [ ] `/recent` command works
- [ ] `/visualizations` command works
- [ ] `/export_excel` works
- [ ] Check data in Supabase dashboard
- [ ] Record counts match SQLite
- [ ] No errors in logs
- [ ] Performance is acceptable

---

## Performance Tips

### Connection Pooling
Already configured in `get_db_session()`:
- Pool size: 10 connections
- Max overflow: 20 connections
- Pre-ping: Verifies connections

### Query Optimization
Add indexes for common queries (already in `create_schema.sql`):
```sql
CREATE INDEX idx_invoices_date ON invoices(invoice_date DESC);
CREATE INDEX idx_invoices_shop ON invoices(shop_name);
```

### Monitor Performance
- Check Supabase Dashboard → Database → Query Performance
- Review slow query logs
- Use `EXPLAIN ANALYZE` for complex queries

---

## Security Best Practices

### ✅ Do
- ✅ Use environment variables for credentials
- ✅ Add `.env` to `.gitignore`
- ✅ Use `SUPABASE_SERVICE_KEY` only on backend
- ✅ Enable SSL (Supabase uses SSL by default)
- ✅ Rotate keys if exposed

### ❌ Don't
- ❌ Commit credentials to Git
- ❌ Hardcode passwords in code
- ❌ Expose `SERVICE_KEY` to client-side
- ❌ Use weak database passwords

---

## What Gets Migrated

```
✅ invoices table
   - All transaction records
   - Shop names, dates, amounts
   
✅ invoice_items table
   - All line items
   - Linked to parent invoices
   
✅ platform_users table
   - Telegram/WhatsApp users
   
✅ spending_limits table
   - Budget tracking (legacy)
   
✅ spending_limits_v2 table
   - Enhanced budget tracking
   
✅ All relationships preserved
✅ Foreign key constraints enforced
✅ Data integrity maintained
```

---

## Migration Tools

| Tool | Purpose |
|------|---------|
| `migrate.py` | Interactive menu-driven migration |
| `export_sqlite_data.py` | Export SQLite to JSON |
| `import_to_supabase.py` | Import JSON to Supabase |
| `test_connection.py` | Test Supabase connection |
| `create_schema.sql` | PostgreSQL schema |

---

## Support Resources

- **Migration README**: `invoice_rag/migration/README.md`
- **Test Connection**: `python migration/test_connection.py`
- **Interactive Helper**: `python migration/migrate.py`
- **Supabase Docs**: https://supabase.com/docs
- **PostgreSQL Docs**: https://www.postgresql.org/docs/

---

## Summary

### What You Need:
1. Supabase account and project
2. API credentials (URL + keys)
3. Database credentials (host + password)
4. Updated dependencies installed
5. 30-60 minutes of time

### Migration Process:
1. Setup environment (`.env`)
2. Test connection
3. Create schema in Supabase
4. Export SQLite data
5. Import to Supabase
6. Update code
7. Test everything

### Key Points:
- ✅ Non-destructive (SQLite backup remains)
- ✅ Can rollback easily
- ✅ Automated scripts provided
- ✅ Interactive helper available
- ✅ ~30 minutes active work

---

**Good luck with your migration! 🚀**