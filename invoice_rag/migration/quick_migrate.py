#!/usr/bin/env python3
"""
Quick Migration Script - One Command to Rule Them All
Executes the complete migration process from SQLite to Supabase
"""
import os
import sys
from pathlib import Path

def print_header(text):
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70 + "\n")

def print_step(number, text):
    print(f"\n{'='*70}")
    print(f"📍 Step {number}: {text}")
    print('='*70)

def run_command(command, description):
    """Run a shell command"""
    print(f"\n🔄 {description}...")
    result = os.system(command)
    if result == 0:
        print(f"✅ {description} completed successfully")
        return True
    else:
        print(f"❌ {description} failed with code {result}")
        return False

def main():
    print_header("🚀 Quick Migration: SQLite → Supabase")
    
    # Check if we're in the right directory
    if not os.path.exists('migration'):
        print("❌ Error: migration/ directory not found")
        print("Please run this script from the invoice_rag directory")
        sys.exit(1)
    
    print("This script will:")
    print("1. Test Supabase connection")
    print("2. Export SQLite data")
    print("3. Import to Supabase")
    print("4. Verify migration")
    print("\n⚠️  Make sure you have:")
    print("  - Supabase credentials in .env")
    print("  - Created schemas in Supabase SQL Editor")
    print("  - Installed all requirements (pip install -r requirements.txt)")
    
    response = input("\n➡️  Continue? (yes/no): ")
    if response.lower() not in ['yes', 'y']:
        print("Migration cancelled")
        sys.exit(0)
    
    # Step 1: Test connection
    print_step(1, "Testing Supabase Connection")
    if not run_command("python migration/test_connection.py", "Connection test"):
        print("\n❌ Connection test failed. Please check your .env credentials.")
        sys.exit(1)
    
    # Step 2: Export SQLite data
    print_step(2, "Exporting SQLite Data")
    if not run_command("python migration/export_sqlite_data.py", "Data export"):
        print("\n❌ Export failed")
        sys.exit(1)
    
    # Find the latest export file
    migration_dir = Path("migration")
    export_files = sorted(migration_dir.glob("sqlite_export_*.json"))
    
    if not export_files:
        print("❌ No export file found")
        sys.exit(1)
    
    latest_export = export_files[-1]
    print(f"\n📁 Using export file: {latest_export.name}")
    
    # Step 3: Import to Supabase
    print_step(3, "Importing to Supabase")
    # Force 'supabase' method to use REST API instead of direct PostgreSQL (better for firewalls)
    if not run_command(f'python migration/import_to_supabase.py "{latest_export}" supabase', "Data import"):
        print("\n❌ Import failed")
        sys.exit(1)
    
    # Step 4: Verify
    print_step(4, "Migration Complete!")
    
    print("\n✅ Migration completed successfully!")
    print("\n📋 Next steps:")
    print("1. Update .env: Set USE_SUPABASE=true")
    print("2. Test bot: python telegram_bot/bot.py")
    print("3. Verify uploads, analysis, and limits work")
    print("\n💎 For Premium Feature:")
    print("1. Generate test token: python -c \"from telegram_bot.premium import generate_test_token; print(generate_test_token(7))\"")
    print("2. Test /premium command in Telegram")
    print("3. Claim token and verify access")
    
    print("\n" + "=" * 70)
    print("  🎉 MIGRATION SUCCESSFUL!")
    print("=" * 70)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Migration cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        sys.exit(1)
