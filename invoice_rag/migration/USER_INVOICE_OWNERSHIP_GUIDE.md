# 👤 User-Invoice Ownership Recommendation

This guide addresses the **lack of direct user-invoice ownership** in your current database schema.

---

## 🔍 Current Situation

### **Problem**
Your invoices table has **NO user_id column**, meaning:
- ❌ Can't identify which user uploaded which invoice
- ❌ Multi-user budgets don't work properly (all users see same total)
- ❌ Can't have per-user analytics
- ❌ No user-specific data isolation

### **Current Workaround**
- `spending_limits` uses Telegram `user_id` directly
- Budget checks query **ALL invoices** (not user-specific)
- Works for single-user, breaks for multi-user

---

## 🎯 Recommended Solution

Add user tracking to invoices with **backward compatibility**.

### **Option A: Full User Integration (RECOMMENDED)**

Add `user_id` foreign key to invoices table.

#### **Benefits:**
- ✅ Proper multi-user support
- ✅ User-specific analytics
- ✅ Data isolation/privacy
- ✅ Accurate budget tracking per user
- ✅ Future-proof for scaling

#### **Migration Complexity:** Medium
- Add column to existing table
- Update 8-10 files
- Migrate existing data (assign to default user)

---

### **Option B: Keep Current (NOT RECOMMENDED)**

Keep invoices shared across all users.

#### **When to use:**
- ✅ Single-user application only
- ✅ Family shared budget
- ✅ Quick prototype/demo

#### **Limitations:**
- ❌ Can't scale to multiple users
- ❌ Privacy issues
- ❌ Inaccurate per-user budgets

---

## 📋 Implementation Plan: Option A (User Integration)

### **Phase 1: Database Schema Update**

#### **Step 1.1: Add user_id to invoices table**

**For PostgreSQL/Supabase** (add to `create_schema.sql`):

```sql
-- ADD COLUMN to invoices table (after line 28)
ALTER TABLE invoices 
ADD COLUMN user_id BIGINT REFERENCES platform_users(id) ON DELETE SET NULL;

-- ADD INDEX for performance
CREATE INDEX idx_invoices_user_id ON invoices(user_id);

-- ADD COMMENT
COMMENT ON COLUMN invoices.user_id IS 'User who uploaded this invoice (FK to platform_users)';
```

**For SQLite** (for local testing):
```sql
-- SQLite doesn't support ALTER TABLE ADD FOREIGN KEY easily
-- Easier to recreate table with new schema

-- 1. Create new table with user_id
CREATE TABLE invoices_new (
    id INTEGER PRIMARY KEY,
    shop_name TEXT NOT NULL,
    invoice_date TEXT,
    total_amount REAL NOT NULL,
    transaction_type TEXT,
    processed_at TEXT,
    image_path TEXT,
    user_id INTEGER,  -- NEW COLUMN
    FOREIGN KEY (user_id) REFERENCES platform_users(id) ON DELETE SET NULL
);

-- 2. Copy existing data (user_id will be NULL)
INSERT INTO invoices_new 
SELECT id, shop_name, invoice_date, total_amount, transaction_type, 
       processed_at, image_path, NULL as user_id
FROM invoices;

-- 3. Drop old table and rename
DROP TABLE invoices;
ALTER TABLE invoices_new RENAME TO invoices;

-- 4. Recreate indexes
CREATE INDEX idx_invoices_date ON invoices(invoice_date);
CREATE INDEX idx_invoices_user_id ON invoices(user_id);
```

#### **Step 1.2: Update SQLAlchemy Model**

Edit `src/database.py`:

```python
class Invoice(Base):
    __tablename__ = 'invoices'

    id = Column(Integer, primary_key=True)
    shop_name = Column(String, nullable=False)
    invoice_date = Column(String)
    total_amount = Column(Float, nullable=False)
    transaction_type = Column(String)
    processed_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    image_path = Column(String)
    user_id = Column(Integer, ForeignKey('platform_users.id'))  # NEW

    # Relationships
    items = relationship("InvoiceItem", back_populates="invoice", cascade="all, delete-orphan")
    user = relationship("PlatformUser", back_populates="invoices")  # NEW

    def __repr__(self):
        return f"<Invoice(shop_name='{self.shop_name}', total_amount='{self.total_amount}', user_id={self.user_id})>"


# NEW MODEL for platform_users (if not exists)
class PlatformUser(Base):
    __tablename__ = 'platform_users'
    
    id = Column(Integer, primary_key=True)
    platform = Column(String, nullable=False)  # 'telegram', 'whatsapp'
    platform_user_id = Column(String, nullable=False)
    display_name = Column(String)
    phone_number = Column(String)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    last_active = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    invoices = relationship("Invoice", back_populates="user")  # NEW
    spending_limits = relationship("SpendingLimitV2", back_populates="user")
    
    __table_args__ = (
        UniqueConstraint('platform', 'platform_user_id', name='unique_platform_user'),
    )
```

---

### **Phase 2: Code Updates**

#### **Step 2.1: Update Invoice Processing**

Edit `src/database.py` - `insert_invoice_data()`:

```python
def insert_invoice_data(session, invoice_data, image_path, user_id=None):
    """
    Inserts extracted invoice data into the database.
    
    Args:
        session: Database session
        invoice_data: Pydantic invoice model
        image_path: Path to invoice image
        user_id: ID of user who uploaded (from platform_users table)
    """
    try:
        invoice = Invoice(
            shop_name=invoice_data.shop_name,
            invoice_date=invoice_data.invoice_date,
            total_amount=float(invoice_data.total_amount),
            transaction_type=invoice_data.transaction_type,
            image_path=image_path,
            user_id=user_id  # NEW
        )
        session.add(invoice)
        session.flush()
        
        # Create invoice items (unchanged)
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
        print(f"Successfully inserted invoice from {invoice_data.shop_name} for user {user_id}")
        return invoice.id
    except Exception as e:
        print(f"Error inserting invoice data: {e}")
        session.rollback()
        return None
```

#### **Step 2.2: Update Telegram Bot**

Edit `telegram_bot/bot.py` - `handle_photo()`:

```python
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle invoice photos sent by users."""
    if not update.message or not update.effective_user:
        return
    
    telegram_user_id = update.effective_user.id  # Get Telegram user ID
    
    # Get the largest photo
    photo = update.message.photo[-1]
    file = await context.bot.get_file(photo.file_id)
    temp_path = f"temp_{telegram_user_id}.jpg"
    await file.download_to_drive(temp_path)
    
    try:
        await update.message.reply_text("Processing your invoice... Please wait.")
        invoice_data = process_invoice(temp_path)
        
        if invoice_data:
            # NEW: Get or create platform user
            session = get_db_session()
            platform_user = get_or_create_platform_user(
                session=session,
                platform='telegram',
                platform_user_id=str(telegram_user_id),
                display_name=update.effective_user.full_name
            )
            
            # Save invoice with user_id
            from src.processor import save_to_database_robust
            invoice_id = save_to_database_robust(
                invoice_data, 
                temp_path,
                user_id=platform_user.id  # NEW
            )
            
            # Check spending limit (now user-specific)
            amount = invoice_data.get('total_amount', 0)
            limit_check = check_spending_limit(platform_user.id, amount)  # NEW: use platform_user.id
            
            # ... rest of code
```

#### **Step 2.3: Add User Management Functions**

Add to `src/database.py`:

```python
def get_or_create_platform_user(session, platform, platform_user_id, display_name=None, phone_number=None):
    """
    Get existing platform user or create new one.
    
    Args:
        session: Database session
        platform: Platform name ('telegram', 'whatsapp')
        platform_user_id: User ID from platform
        display_name: User's display name (optional)
        phone_number: User's phone number (optional)
    
    Returns:
        PlatformUser object
    """
    # Try to find existing user
    user = session.query(PlatformUser).filter_by(
        platform=platform,
        platform_user_id=str(platform_user_id)
    ).first()
    
    if user:
        # Update last_active
        user.last_active = datetime.now(timezone.utc)
        if display_name:
            user.display_name = display_name
        session.commit()
        return user
    
    # Create new user
    user = PlatformUser(
        platform=platform,
        platform_user_id=str(platform_user_id),
        display_name=display_name,
        phone_number=phone_number
    )
    session.add(user)
    session.commit()
    return user
```

#### **Step 2.4: Update Analysis Functions**

Edit `src/analysis.py` - add user filtering:

```python
def analyze_invoices(weeks_back: int | None = None, user_id: int | None = None):
    """
    Analyze invoices with optional user filtering.
    
    Args:
        weeks_back: Number of weeks to analyze
        user_id: Filter by specific user (platform_users.id)
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        params = []
        where_clauses = []
        
        if weeks_back is not None and weeks_back > 0:
            end_date = datetime.now()
            start_date = end_date - timedelta(weeks=weeks_back)
            where_clauses.append("invoice_date >= ?")
            params.append(start_date.strftime('%Y-%m-%d'))
        
        if user_id is not None:
            where_clauses.append("user_id = ?")
            params.append(user_id)
        
        where_clause = ""
        if where_clauses:
            where_clause = "WHERE " + " AND ".join(where_clauses)
        
        query = f"""
            SELECT 
                COUNT(*) as total_invoices,
                SUM(total_amount) as total_spent,
                AVG(total_amount) as average_amount
            FROM invoices
            {where_clause}
        """
        cursor.execute(query, params)
        
        # ... rest of code
```

#### **Step 2.5: Update Spending Limits**

Edit `telegram_bot/spending_limits.py`:

```python
def get_current_month_spending(user_id: int) -> float:
    """
    Get total spending for current month for specific user.
    
    Args:
        user_id: platform_users.id (NOT Telegram user_id!)
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        # Get current month start date
        today = datetime.now()
        month_start = today.replace(day=1).strftime('%Y-%m-%d')
        
        # Query user-specific invoices
        cursor.execute('''
            SELECT SUM(total_amount)
            FROM invoices
            WHERE user_id = ? AND invoice_date >= ?
        ''', (user_id, month_start))
        
        result = cursor.fetchone()
        return float(result[0]) if result and result[0] else 0.0
    finally:
        conn.close()

def check_spending_limit(user_id: int, new_amount: float = 0) -> Dict[str, Any]:
    """
    Check spending limit for specific user.
    
    Args:
        user_id: platform_users.id (NOT Telegram user_id!)
    """
    # Get limit from spending_limits_v2 (linked to platform_users)
    monthly_limit = get_monthly_limit(user_id)
    if not monthly_limit:
        return {
            'has_limit': False,
            'message': 'No spending limit set. Use /set_limit to set one.'
        }
    
    current_spending = get_current_month_spending(user_id)
    total_with_new = current_spending + new_amount
    remaining = monthly_limit - current_spending
    percentage_used = (current_spending / monthly_limit) * 100
    
    # ... rest unchanged
```

---

### **Phase 3: Data Migration**

#### **Step 3.1: Migrate Existing Invoices**

For existing invoices with `user_id = NULL`, assign to default user:

```sql
-- PostgreSQL
-- Create a default "system" user if needed
INSERT INTO platform_users (platform, platform_user_id, display_name)
VALUES ('system', 'legacy', 'Legacy Data User')
ON CONFLICT (platform, platform_user_id) DO NOTHING;

-- Assign all NULL invoices to this user
UPDATE invoices
SET user_id = (
    SELECT id FROM platform_users 
    WHERE platform = 'system' AND platform_user_id = 'legacy'
)
WHERE user_id IS NULL;
```

Or assign to first Telegram user:
```sql
-- Assign to first telegram user
UPDATE invoices
SET user_id = (
    SELECT id FROM platform_users 
    WHERE platform = 'telegram'
    ORDER BY created_at ASC
    LIMIT 1
)
WHERE user_id IS NULL;
```

---

## 📊 Updated Schema Diagram

```
platform_users (1) ──────── (M) invoices
    │                       [user_id FK → platform_users.id]
    │                       
    └─────────────────────── (M) spending_limits_v2
                            [user_id FK → platform_users.id]

invoices (1) ──────────────── (M) invoice_items
                              [invoice_id FK → invoices.id]
```

---

## ✅ Benefits After Migration

### **Before (Current):**
- ❌ All users see combined spending
- ❌ Budget applies to ALL invoices
- ❌ No privacy/data isolation
- ❌ Can't do per-user analytics

### **After (With user_id):**
- ✅ Each user sees only their invoices
- ✅ Budget tracks per-user spending
- ✅ Data privacy maintained
- ✅ Per-user analytics possible
- ✅ Can scale to thousands of users

---

## 🚀 Migration Checklist

- [ ] **Phase 1: Schema**
  - [ ] Add `user_id` column to invoices table (SQL)
  - [ ] Update SQLAlchemy models (Invoice, PlatformUser)
  - [ ] Add database indexes

- [ ] **Phase 2: Code**
  - [ ] Update `insert_invoice_data()` to accept user_id
  - [ ] Add `get_or_create_platform_user()` function
  - [ ] Update Telegram bot `handle_photo()` to track user
  - [ ] Update all analysis functions with user filtering
  - [ ] Update spending_limits with user-specific queries

- [ ] **Phase 3: Data**
  - [ ] Migrate existing NULL invoices to default user
  - [ ] Test with multiple test users
  - [ ] Verify budget calculations per user

- [ ] **Phase 4: Testing**
  - [ ] Test invoice upload from User A
  - [ ] Test invoice upload from User B
  - [ ] Verify User A only sees their invoices
  - [ ] Verify User B only sees their invoices
  - [ ] Test spending limits per user
  - [ ] Test analytics per user

---

## 📝 Files Requiring Updates

1. ✅ `migration/create_schema.sql` - Add user_id column
2. ✅ `src/database.py` - Update models, add user functions
3. ✅ `src/processor.py` - Update save functions
4. ✅ `telegram_bot/bot.py` - Track user on upload
5. ✅ `telegram_bot/spending_limits.py` - User-specific queries
6. ✅ `src/analysis.py` - Add user filtering
7. ✅ `src/chatbot.py` - Pass user_id to analysis
8. ⚠️ `marimo_app/dashboard.py` - Add user filter (optional)

---

## 🎯 Quick Start Commands

```bash
# 1. Update schema in Supabase
# Run the ALTER TABLE commands in Supabase SQL Editor

# 2. Update SQLAlchemy models
# Edit src/database.py

# 3. Create migration script
python migration/add_user_column.py

# 4. Test with SQLite first
python test_bot_connection.py

# 5. Deploy to Supabase
USE_SUPABASE=true python telegram_bot/bot.py
```

---

## ⚖️ Decision Matrix

| Factor | Keep Current | Add user_id |
|--------|--------------|-------------|
| **Effort** | Low (0 hours) | Medium (4-6 hours) |
| **Multi-user Support** | ❌ No | ✅ Yes |
| **Privacy** | ❌ None | ✅ Full |
| **Scaling** | ❌ Limited | ✅ Unlimited |
| **Budget Accuracy** | ❌ Combined | ✅ Per-user |
| **Production Ready** | ❌ No | ✅ Yes |

---

## 💡 Recommendation Summary

**Choose Option A (Add user_id)** if:
- ✅ You want multiple users
- ✅ You need accurate per-user budgets
- ✅ You want production-ready system
- ✅ You're already doing migration anyway

**Choose Option B (Keep current)** if:
- ✅ Strictly single-user forever
- ✅ Quick prototype only
- ✅ Family shared budget desired

**My Recommendation: Option A** - Since you're already migrating to Supabase, now is the PERFECT time to add proper user tracking. It's a small additional effort that makes your system production-ready and scalable.

---

## 📞 Implementation Support

I can help you:
1. ✅ Generate the exact SQL migration scripts
2. ✅ Update each Python file with proper code
3. ✅ Create test scripts to verify multi-user functionality
4. ✅ Write data migration scripts for existing invoices

Just let me know which option you'd like to proceed with!
