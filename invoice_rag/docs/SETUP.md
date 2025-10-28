# 🚀 Complete Implementation Guide: Database Migration + Premium Feature

This guide provides step-by-step instructions for implementing the database migration to Supabase and adding the premium feature to your Telegram bot.

---

## ✅ What's Been Done

### 1. Core Files Created/Updated:
- ✅ `.env` - Added `USE_SUPABASE`, `JWT_SECRET_KEY`, and correct Supabase credentials
- ✅ `src/database.py` - Enhanced with Supabase support + Premium models (User, PremiumData, Token)
- ✅ `src/db_config.py` - Unified database abstraction (already exists)
- ✅ `src/analysis.py` - Updated to support both SQLite and Supabase
- ✅ `telegram_bot/spending_limits.py` - Updated for Supabase compatibility
- ✅ `telegram_bot/premium.py` - NEW: Premium feature module with JWT validation
- ✅ `migration/premium_schema.sql` - NEW: SQL schema for premium tables
- ✅ `requirements.txt` - Added PyJWT for JWT token validation

---

## 📋 Step-by-Step Implementation

### PHASE 1: Database Migration to Supabase

#### Step 1: Create Schema in Supabase

1. Open Supabase Dashboard: https://supabase.com/dashboard
2. Select your project (`urfinance`)
3. Go to **SQL Editor**
4. Click **"New Query"**
5. Copy the content from `migration/create_schema.sql`
6. Paste and click **"Run"**
7. Wait for success message: "✅ Schema created successfully!"

#### Step 2: Create Premium Schema

1. Still in SQL Editor, click **"New Query"**
2. Copy the content from `migration/premium_schema.sql`
3. Paste and click **"Run"**
4. Wait for success message: "✅ Premium feature schema created successfully!"

#### Step 3: Test Connection

```bash
cd e:\Github Project\hackathon\invoice_rag
python migration/test_connection.py
```

Expected output:
```
✅ Supabase connection successful!
✅ Can query database
✅ All systems ready!
```

#### Step 4: Export SQLite Data

```bash
python migration/export_sqlite_data.py
```

This creates: `migration/sqlite_export_YYYYMMDD_HHMMSS.json`

#### Step 5: Import to Supabase

```bash
python migration/import_to_supabase.py migration/sqlite_export_YYYYMMDD_HHMMSS.json
```

Replace `YYYYMMDD_HHMMSS` with actual filename from Step 4.

#### Step 6: Switch to Supabase

Edit `.env`:
```properties
USE_SUPABASE=true
```

#### Step 7: Test with Supabase

```bash
python telegram_bot/bot.py
```

Test in Telegram:
- Upload an invoice
- Run `/analysis`
- Set spending limit with `/set_limit`

---

### PHASE 2: Premium Feature Implementation

#### Step 8: Install PyJWT

```bash
pip install PyJWT>=2.8.0
```

Or install all updated requirements:
```bash
pip install -r requirements.txt
```

#### Step 9: Update JWT Secret Key

Edit `.env` and replace the JWT secret:
```properties
JWT_SECRET_KEY=<YOUR_SUPER_SECRET_64_CHARACTER_RANDOM_STRING_HERE>
```

Generate a secure random string:
```bash
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

#### Step 10: Add Premium Commands to Bot

Add these imports to `telegram_bot/bot.py` (after existing imports around line 30):

```python
from telegram_bot.premium import (
    check_premium_access,
    claim_token,
    require_premium,
    validate_jwt_token
)
from src.database import get_or_create_user
```

#### Step 11: Update /start Command

Replace the `start()` function in `telegram_bot/bot.py` (around line 65) with:

```python
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a welcome message when the command /start is issued."""
    if not update.message or not update.effective_user:
        return

    # Get or create user in database
    session = get_db_session()
    try:
        user = get_or_create_user(session, str(update.effective_user.id))
        logger.info(f"User {update.effective_user.id} started bot (Status: {user.status_account})")
    finally:
        session.close()

    keyboard = [
        ['/set_limit', '/check_limit'],
        ['/upload_invoice', '/analysis', '/recent_invoices'],
        ['/premium', '/chatmode', '/clear', '/help']  # Added /premium
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    welcome_text = (
        "👋 Hello! I'm your friendly Invoice Helper Bot!\n\n"
        "Let me help you keep track of your spending the easy way:\n"
        "📸 Send me a photo of your receipt or invoice\n"
        "📊 See where your money goes with simple charts\n"
        "💰 Set and track your monthly budget\n"
        "📋 Check your spending history\n\n"
        "💡 Just tap any button below to get started!\n"
        "🤖 Chat with AI for deep dive and quick summary\n\n"
        "💎 NEW: Premium features available! Use /premium to learn more.\n\n"
        "Need help? Type /help for more details."
    )
    await update.message.reply_text(welcome_text, reply_markup=reply_markup)
```

#### Step 12: Add /premium Command

Add this new function to `telegram_bot/bot.py` (before the `main()` function):

```python
async def premium_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show premium options with inline buttons."""
    if not update.message or not update.effective_user:
        return
    
    # Check current premium status
    session = get_db_session()
    try:
        status_info = check_premium_access(session, str(update.effective_user.id))
        
        # Create inline keyboard with two buttons
        keyboard = [
            [
                InlineKeyboardButton("💳 Make Payment", callback_data="premium_payment"),
                InlineKeyboardButton("🎫 Claim Token", callback_data="premium_claim")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        message = (
            "💎 **Premium Features**\n\n"
            f"**Current Status:** {status_info['status']}\n\n"
            f"{status_info['message']}\n\n"
            "**Premium Benefits:**\n"
            "• 📊 Advanced Analytics\n"
            "• 📈 Detailed Spending Reports\n"
            "• 📤 Export to Google Sheets\n"
            "• 🎨 Interactive Dashboards\n"
            "• 🚀 Priority Support\n\n"
            "**Choose an option below:**"
        )
        
        await update.message.reply_text(message, reply_markup=reply_markup, parse_mode='Markdown')
    finally:
        session.close()
```

#### Step 13: Add Callback Query Handler

Add this new function to `telegram_bot/bot.py`:

```python
async def premium_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle premium button callbacks."""
    query = update.callback_query
    if not query or not query.from_user:
        return
    
    await query.answer()
    
    if query.data == "premium_payment":
        # Dummy payment flow
        message = (
            "💳 **Payment Feature (Coming Soon)**\n\n"
            "The payment feature is currently under development.\n\n"
            "🎫 For now, please use the **Claim Token** option instead.\n\n"
            "💡 Contact support to get a premium token!"
        )
        await query.edit_message_text(message, parse_mode='Markdown')
    
    elif query.data == "premium_claim":
        # Start token claim flow
        context.user_data['awaiting_token'] = True
        message = (
            "🎫 **Claim Premium Token**\n\n"
            "Please send me your JWT token to activate premium access.\n\n"
            "📝 Example format:\n"
            "`eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`\n\n"
            "💡 Get your token from the administrator or purchase page.\n\n"
            "❌ Send /cancel to cancel this operation."
        )
        await query.edit_message_text(message, parse_mode='Markdown')
```

#### Step 14: Add Token Claim Handler

Add this new function to `telegram_bot/bot.py`:

```python
async def handle_token_claim(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle JWT token input from user."""
    if not update.message or not update.effective_user:
        return
    
    # Check if user is in token claim flow
    if not context.user_data.get('awaiting_token', False):
        return
    
    jwt_token = update.message.text.strip()
    
    # Handle cancel
    if jwt_token.lower() == '/cancel':
        context.user_data['awaiting_token'] = False
        await update.message.reply_text("❌ Token claim cancelled.")
        return
    
    # Process token claim
    await update.message.reply_text("⏳ Validating token... Please wait.")
    
    session = get_db_session()
    try:
        result = claim_token(session, str(update.effective_user.id), jwt_token)
        
        context.user_data['awaiting_token'] = False
        await update.message.reply_text(result['message'])
        
        if result['success']:
            # Send premium welcome message
            welcome = (
                "🎉 **Welcome to Premium!**\n\n"
                "You now have access to all premium features:\n\n"
                "📊 /analysis - Now includes advanced insights\n"
                "📈 Enhanced spending reports\n"
                "📤 Export capabilities\n"
                "🎨 Interactive dashboards\n\n"
                "💡 Start exploring your premium benefits now!"
            )
            await update.message.reply_text(welcome, parse_mode='Markdown')
    finally:
        session.close()
```

#### Step 15: Add Premium Gate to /analysis Command

Find the `analysis_command()` function (around line 240) and add premium check at the beginning:

```python
async def analysis_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show invoice summary and analysis, then send visualization."""
    if not update.message or not update.effective_user:
        return
    
    # Premium feature gate
    session = get_db_session()
    try:
        has_access, message = require_premium(session, str(update.effective_user.id))
        
        if not has_access:
            await update.message.reply_text(message)
            return
    finally:
        session.close()
    
    # Rest of existing analysis code...
    try:
        from telegram_bot.marimo_integration import create_interactive_dashboard, check_server_health
        
        # Send text summary first
        analysis = analyze_invoices()
        # ... rest of existing code
```

#### Step 16: Register New Handlers

Find the `main()` function at the bottom of `telegram_bot/bot.py` and add these handlers:

```python
def main() -> None:
    """Start the bot."""
    # Create application
    application = Application.builder().token(TOKEN).build()

    # Initialize spending limits table
    init_spending_limits_table()

    # Register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("premium", premium_command))  # NEW
    
    # ... existing handlers ...
    
    # NEW: Callback query handler for premium buttons
    application.add_handler(CallbackQueryHandler(premium_callback_handler, pattern="^premium_"))
    
    # NEW: Message handler for token claim (must be before general message handler)
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND, 
        handle_token_claim
    ))
    
    # Existing photo handler
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    
    # ... rest of existing code
```

---

### PHASE 3: Testing

#### Test 1: Generate Test Token

```bash
cd e:\Github Project\hackathon\invoice_rag
python -c "from telegram_bot.premium import generate_test_token; print(generate_test_token(7))"
```

This generates a 7-day test token. Copy the output.

#### Test 2: Test Premium Flow in Telegram

1. Start bot: `/start`
2. Click `/premium` button
3. Click `🎫 Claim Token` button
4. Paste the test token from Test 1
5. Should receive: "✅ Token claimed successfully!"
6. Try `/analysis` - should now work (premium feature)

#### Test 3: Test Token Reuse Prevention

1. Click `/premium` again
2. Click `🎫 Claim Token` again
3. Paste the SAME token
4. Should receive: "❌ This token has already been claimed."

#### Test 4: Test Premium Expiry

For testing expiry, generate a 0-day token:
```bash
python -c "from telegram_bot.premium import generate_test_token; print(generate_test_token(0))"
```

This token expires immediately, allowing you to test expiry logic.

---

## 🎯 Complete Checklist

### Migration Checklist:
- [ ] Schema created in Supabase (`create_schema.sql`)
- [ ] Premium schema created (`premium_schema.sql`)
- [ ] Connection tested (`test_connection.py`)
- [ ] Data exported (`export_sqlite_data.py`)
- [ ] Data imported (`import_to_supabase.py`)
- [ ] `USE_SUPABASE=true` in `.env`
- [ ] Bot works with Supabase

### Premium Feature Checklist:
- [ ] PyJWT installed
- [ ] JWT_SECRET_KEY set in `.env`
- [ ] Premium imports added to `bot.py`
- [ ] `/start` command updated
- [ ] `/premium` command added
- [ ] Callback handler added
- [ ] Token claim handler added
- [ ] Premium gate added to `/analysis`
- [ ] Handlers registered in `main()`
- [ ] Test token generated
- [ ] Token claim tested
- [ ] Token reuse prevention tested
- [ ] Premium expiry tested

---

## 🚨 Common Issues & Solutions

### Issue 1: "Module not found: psycopg2"
**Solution:**
```bash
pip install psycopg2-binary
```

### Issue 2: "Invalid JWT signature"
**Solution:** Make sure `JWT_SECRET_KEY` in `.env` matches the key used to generate tokens.

### Issue 3: "Table does not exist"
**Solution:** Run both SQL files in Supabase SQL Editor:
1. `create_schema.sql`
2. `premium_schema.sql`

### Issue 4: Bot doesn't respond to /premium
**Solution:** Make sure handlers are registered in correct order in `main()` function.

### Issue 5: "User table not found"
**Solution:** Run `premium_schema.sql` in Supabase SQL Editor.

---

## 📞 Need Help?

### Generate Test Tokens:
```bash
# 7-day token
python -c "from telegram_bot.premium import generate_test_token; print('7-day:', generate_test_token(7))"

# 30-day token
python -c "from telegram_bot.premium import generate_test_token; print('30-day:', generate_test_token(30))"
```

### Check Database Connection:
```bash
python migration/test_connection.py
```

### Verify Premium Models:
```bash
python -c "from src.database import User, PremiumData, Token; print('✅ Models loaded successfully')"
```

---

## 🎉 Success Criteria

Your implementation is complete when:

1. ✅ Bot connects to Supabase (not SQLite)
2. ✅ Upload invoice works
3. ✅ `/analysis` requires premium
4. ✅ `/premium` command shows options
5. ✅ Can claim token successfully
6. ✅ Token can't be reused
7. ✅ Premium status persists across restarts
8. ✅ Expired premium auto-downgrades to Free

---

**Ready to go live! 🚀**
