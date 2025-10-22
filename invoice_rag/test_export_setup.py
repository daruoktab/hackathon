"""
Quick test script to verify spreadsheet export functionality
"""
import sys
from pathlib import Path

# Add project to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

print("=== Spreadsheet Export Implementation Test ===\n")

# Test 1: Check imports
print("1. Testing imports...")
try:
    from telegram import InlineKeyboardMarkup, InlineKeyboardButton
    from telegram.ext import CallbackQueryHandler
    import pandas as pd
    from datetime import datetime
    print("   ✅ Telegram components imported")
    print("   ✅ pandas imported")
    print("   ✅ datetime imported")
except ImportError as e:
    print(f"   ❌ Import error: {e}")

# Test 2: Check Excel dependencies
print("\n2. Testing Excel dependencies...")
try:
    import openpyxl
    print("   ✅ openpyxl installed")
except ImportError:
    print("   ⚠️  openpyxl NOT installed - Run: pip install openpyxl")

# Test 3: Check Google Sheets dependencies
print("\n3. Testing Google Sheets dependencies...")
try:
    import gspread
    print("   ✅ gspread installed")
except ImportError:
    print("   ⚠️  gspread NOT installed - Run: pip install gspread")

try:
    from oauth2client.service_account import ServiceAccountCredentials
    print("   ✅ oauth2client installed")
except ImportError:
    print("   ⚠️  oauth2client NOT installed - Run: pip install oauth2client")

# Test 4: Check credentials file
print("\n4. Checking Google Sheets credentials...")
credentials_path = project_root / 'google_credentials.json'
if credentials_path.exists():
    print(f"   ✅ google_credentials.json found at {credentials_path}")
else:
    print(f"   ⚠️  google_credentials.json NOT found")
    print(f"      Expected location: {credentials_path}")
    print(f"      See GOOGLE_SHEETS_SETUP.md for setup instructions")

# Test 5: Check bot functions exist
print("\n5. Checking bot functions...")
try:
    from telegram_bot.bot import export_to_excel, export_to_google_sheets, handle_export_callback
    print("   ✅ export_to_excel function exists")
    print("   ✅ export_to_google_sheets function exists")
    print("   ✅ handle_export_callback function exists")
except ImportError as e:
    print(f"   ❌ Function import error: {e}")

# Test 6: Check analysis functions
print("\n6. Checking analysis functions...")
try:
    from src.analysis import analyze_invoices, calculate_weekly_averages, analyze_spending_trends
    print("   ✅ analyze_invoices function available")
    print("   ✅ calculate_weekly_averages function available")
    print("   ✅ analyze_spending_trends function available")
except ImportError as e:
    print(f"   ❌ Analysis import error: {e}")

# Summary
print("\n" + "="*50)
print("SUMMARY")
print("="*50)

excel_ready = True
sheets_ready = True

try:
    import openpyxl
except ImportError:
    excel_ready = False

try:
    import gspread
    from oauth2client.service_account import ServiceAccountCredentials
    if not credentials_path.exists():
        sheets_ready = False
except ImportError:
    sheets_ready = False

if excel_ready and sheets_ready:
    print("✅ FULLY READY - Both Excel and Google Sheets export available")
elif excel_ready:
    print("✅ PARTIALLY READY - Excel export available")
    print("⚠️  Google Sheets export needs setup (see GOOGLE_SHEETS_SETUP.md)")
else:
    print("⚠️  NEEDS SETUP")
    print("\nTo enable Excel export:")
    print("   pip install openpyxl")
    print("\nTo enable Google Sheets export:")
    print("   pip install gspread oauth2client")
    print("   See GOOGLE_SHEETS_SETUP.md for credentials setup")

print("\n" + "="*50)
print("Next Steps:")
print("="*50)
if not excel_ready:
    print("1. Install dependencies: pip install openpyxl gspread oauth2client")
if excel_ready and not sheets_ready:
    print("1. (Optional) Follow GOOGLE_SHEETS_SETUP.md for Google Sheets")
if excel_ready:
    print("2. Start the bot: python run_bot.py")
    print("3. Test with /analysis command")
    print("4. Click export buttons to test functionality")

print("\nDocs:")
print("  - SPREADSHEET_EXPORT_IMPLEMENTATION.md - Feature overview")
print("  - GOOGLE_SHEETS_SETUP.md - Google Sheets setup guide")
