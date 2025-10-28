#!/usr/bin/env python3
"""
Database Cleanup - Clean up invoice database
Merged cleanup for invoices, spending limits, and premium tables

Usage:
    python cleanup.py premium users        # Delete all users
    python cleanup.py premium tokens       # Delete all tokens
    python cleanup.py premium used_tokens  # Delete used tokens only
    python cleanup.py premium expired      # Delete expired subscriptions
    python cleanup.py premium all          # Delete everything (requires confirmation)
    python cleanup.py premium stats        # Show premium statistics
"""

import os
import sqlite3
import sys
from datetime import datetime

def get_database_path():
    """Get the correct database path."""
    db_path = os.path.join('database', 'invoices.db')
    if os.path.exists(db_path):
        return db_path
    return None

def check_database_exists():
    """Check if database exists."""
    db_path = get_database_path()
    if db_path:
        size = os.path.getsize(db_path)
        print(f"Found database: {db_path} ({size} bytes)")
        return db_path
    else:
        print("Database not found: database/invoices.db")
        return None

def show_database_stats(db_path):
    """Show current database statistics."""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Count invoices
        cursor.execute("SELECT COUNT(*) FROM invoices")
        invoice_count = cursor.fetchone()[0]

        # Count items
        cursor.execute("SELECT COUNT(*) FROM invoice_items")
        item_count = cursor.fetchone()[0]

        # Total spending
        cursor.execute("SELECT SUM(total_amount) FROM invoices")
        total_spending = cursor.fetchone()[0] or 0

        # Count spending limits
        try:
            cursor.execute("SELECT COUNT(*) FROM spending_limits")
            spending_limits_count = cursor.fetchone()[0]
        except sqlite3.OperationalError:
            spending_limits_count = 0

        # Count premium users
        try:
            cursor.execute("SELECT COUNT(*) FROM \"user\"")
            user_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM premium_data")
            premium_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM token")
            token_count = cursor.fetchone()[0]
        except sqlite3.OperationalError:
            user_count = premium_count = token_count = 0

        print(f"\nCURRENT DATABASE STATS:")
        print(f"📊 INVOICES:")
        print(f"   - Total Invoices: {invoice_count}")
        print(f"   - Total Items: {item_count}")
        print(f"   - Total Spending: Rp {total_spending:,.2f}")
        
        print(f"\n💰 SPENDING LIMITS:")
        print(f"   - Users with limits: {spending_limits_count}")
        
        print(f"\n💎 PREMIUM:")
        print(f"   - Total Users: {user_count}")
        print(f"   - Premium Users: {premium_count}")
        print(f"   - Tokens: {token_count}")

        if invoice_count > 0:
            # Show date range
            cursor.execute("SELECT MIN(processed_at), MAX(processed_at) FROM invoices")
            date_range = cursor.fetchone()
            print(f"\n📅 Date Range: {date_range[0]} to {date_range[1]}")

            # Show recent invoices
            cursor.execute("""
                SELECT id, shop_name, total_amount, processed_at
                FROM invoices 
                ORDER BY processed_at DESC 
                LIMIT 5
            """)
            recent = cursor.fetchall()

            print(f"\n📝 RECENT INVOICES:")
            for id, shop, amount, date in recent:
                print(f"   - ID {id}: {shop} - Rp {amount:,.2f} ({date})")

        conn.close()
        return invoice_count, item_count

    except Exception as e:
        print(f"Error reading database: {e}")
        return 0, 0

def clean_database(db_path, clean_type):
    """Clean database based on type."""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        if clean_type == "all":
            print("\n🧹 CLEANING ALL DATA...")
            cursor.execute("DELETE FROM invoice_items")
            cursor.execute("DELETE FROM invoices")
            cursor.execute("DELETE FROM sqlite_sequence WHERE name IN ('invoices', 'invoice_items')")
            print("   ✅ Deleted all invoices and items")

        elif clean_type == "items":
            print("\n🧹 CLEANING ITEMS ONLY...")
            cursor.execute("DELETE FROM invoice_items")
            print("   ✅ Deleted all invoice items")

        elif clean_type == "limits":
            print("\n🧹 CLEANING SPENDING LIMITS...")
            try:
                cursor.execute("DELETE FROM spending_limits")
                print("   ✅ Deleted all spending limits")
            except sqlite3.OperationalError:
                print("   ⚠️  spending_limits table doesn't exist")

        elif clean_type == "everything":
            print("\n🧹 CLEANING EVERYTHING (invoices + limits, NOT premium)...")
            # Invoices
            cursor.execute("DELETE FROM invoice_items")
            cursor.execute("DELETE FROM invoices")
            print("   ✅ Deleted all invoices")
            
            # Spending limits
            try:
                cursor.execute("DELETE FROM spending_limits")
                print("   ✅ Deleted spending limits")
            except sqlite3.OperationalError:
                pass
            
            # Reset sequences
            cursor.execute("DELETE FROM sqlite_sequence WHERE name IN ('invoices', 'invoice_items', 'spending_limits')")
            print("   ✅ Reset auto-increment counters")
            print("\n💡 Note: Premium tables not affected. Use cleanup_premium.py for that.")

        elif clean_type == "old":
            print("\n🧹 CLEANING OLD DATA (7+ days)...")
            cursor.execute("""
                DELETE FROM invoice_items 
                WHERE invoice_id IN (
                    SELECT id FROM invoices 
                    WHERE processed_at < datetime('now', '-7 days')
                )
            """)
            cursor.execute("DELETE FROM invoices WHERE processed_at < datetime('now', '-7 days')")
            deleted = cursor.rowcount
            print(f"   ✅ Deleted {deleted} old invoices")

        elif clean_type == "test":
            print("\n🧹 CLEANING TEST DATA...")
            cursor.execute("""
                DELETE FROM invoice_items 
                WHERE invoice_id IN (
                    SELECT id FROM invoices 
                    WHERE shop_name LIKE '%test%' OR shop_name LIKE '%Test%'
                )
            """)
            cursor.execute("DELETE FROM invoices WHERE shop_name LIKE '%test%' OR shop_name LIKE '%Test%'")
            deleted = cursor.rowcount
            print(f"   ✅ Deleted {deleted} test invoices")

        conn.commit()
        conn.close()
        print("\n✅ Database cleaned successfully!")

    except Exception as e:
        print(f"\n❌ Error cleaning database: {e}")

def vacuum_database(db_path):
    """Vacuum database to reclaim space."""
    try:
        print("\n🔄 VACUUMING DATABASE...")
        conn = sqlite3.connect(db_path)
        conn.execute("VACUUM")
        conn.close()
        print("✅ Database vacuumed successfully!")
    except Exception as e:
        print(f"❌ Error vacuuming database: {e}")

def show_premium_stats(db_path):
    """Show premium-related statistics."""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        print("\n" + "="*70)
        print("💎 PREMIUM DATA STATISTICS")
        print("="*70)

        # Check if tables exist
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name IN ('user', 'premium_data', 'token')
        """)
        existing_tables = [row[0] for row in cursor.fetchall()]

        if not existing_tables:
            print("\n⚠️  No premium tables found in database")
            print("   Premium tables may not have been created yet")
            conn.close()
            return False

        print(f"\n📊 Found tables: {', '.join(existing_tables)}")

        # Count users
        if 'user' in existing_tables:
            cursor.execute('SELECT COUNT(*) FROM "user"')
            user_count = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM "user" WHERE status_account = ?', ('Premium',))
            premium_count = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM "user" WHERE status_account = ?', ('Free',))
            free_count = cursor.fetchone()[0]
            
            print(f"\n👥 USERS:")
            print(f"   Total Users: {user_count}")
            print(f"   💎 Premium Users: {premium_count}")
            print(f"   🆓 Free Users: {free_count}")

            if user_count > 0 and user_count <= 5:
                cursor.execute('SELECT user_id, status_account, created_at FROM "user" ORDER BY created_at DESC LIMIT 5')
                recent_users = cursor.fetchall()
                print(f"\n   Recent Users:")
                for user_id, status, created in recent_users:
                    status_icon = "💎" if status == "Premium" else "🆓"
                    print(f"   {status_icon} {user_id} - {status} (joined: {created})")

        # Count premium data
        if 'premium_data' in existing_tables:
            cursor.execute('SELECT COUNT(*) FROM premium_data')
            premium_data_count = cursor.fetchone()[0]
            
            print(f"\n📝 PREMIUM SUBSCRIPTIONS:")
            print(f"   Active Premium Data: {premium_data_count}")

            if premium_data_count > 0 and premium_data_count <= 5:
                cursor.execute("""
                    SELECT u.user_id, pd.premium_for, pd.expired_at, pd.created_at
                    FROM premium_data pd
                    JOIN "user" u ON pd.user_id = u.id
                    ORDER BY pd.created_at DESC
                    LIMIT 5
                """)
                recent_premium = cursor.fetchall()
                print(f"\n   Recent Premium Subscriptions:")
                for user_id, method, expired_at, created in recent_premium:
                    now = datetime.now()
                    expired_dt = datetime.fromisoformat(expired_at.replace('Z', '+00:00')) if expired_at else None
                    status = "⏰ Expired" if expired_dt and expired_dt < now else "✅ Active"
                    print(f"   {status} User {user_id} - {method}")
                    print(f"      Expires: {expired_at}")

        # Count tokens
        if 'token' in existing_tables:
            cursor.execute('SELECT COUNT(*) FROM token')
            total_tokens = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM token WHERE is_used = 1')
            used_tokens = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM token WHERE is_used = 0')
            unused_tokens = cursor.fetchone()[0]
            
            print(f"\n🎫 TOKENS:")
            print(f"   Total Tokens: {total_tokens}")
            print(f"   ✅ Used Tokens: {used_tokens}")
            print(f"   🔖 Unused Tokens: {unused_tokens}")

            if unused_tokens > 0 and unused_tokens <= 3:
                cursor.execute('SELECT token FROM token WHERE is_used = 0 LIMIT 3')
                unused = cursor.fetchall()
                print(f"\n   Sample Unused Tokens:")
                for (token,) in unused:
                    short_token = token[:50] + "..." if len(token) > 50 else token
                    print(f"   - {short_token}")

        conn.close()
        print("\n" + "="*70)
        return True

    except Exception as e:
        print(f"\n❌ Error reading database: {e}")
        import traceback
        traceback.print_exc()
        return False

def clean_premium_tables(db_path, table_type):
    """Clean premium tables based on type."""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Check if tables exist
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name IN ('user', 'premium_data', 'token')
        """)
        existing_tables = [row[0] for row in cursor.fetchall()]

        if not existing_tables:
            print("\n⚠️  No premium tables found in database")
            conn.close()
            return

        deleted_count = 0

        if table_type == "all":
            print("\n🧹 CLEANING ALL PREMIUM DATA...")
            
            # Delete in correct order (foreign key constraints)
            if 'premium_data' in existing_tables:
                cursor.execute("SELECT COUNT(*) FROM premium_data")
                count = cursor.fetchone()[0]
                cursor.execute("DELETE FROM premium_data")
                print(f"   ✅ Deleted {count} premium_data records")
                deleted_count += count
            
            if 'token' in existing_tables:
                cursor.execute("SELECT COUNT(*) FROM token")
                count = cursor.fetchone()[0]
                cursor.execute("DELETE FROM token")
                print(f"   ✅ Deleted {count} tokens")
                deleted_count += count
            
            if 'user' in existing_tables:
                cursor.execute('SELECT COUNT(*) FROM "user"')
                count = cursor.fetchone()[0]
                cursor.execute('DELETE FROM "user"')
                print(f"   ✅ Deleted {count} users")
                deleted_count += count
            
            # Reset auto-increment
            cursor.execute("DELETE FROM sqlite_sequence WHERE name IN ('user', 'premium_data')")
            print("   ✅ Reset auto-increment counters")

        elif table_type == "users":
            print("\n🧹 CLEANING USERS ONLY...")
            if 'user' in existing_tables:
                # First delete related premium_data
                if 'premium_data' in existing_tables:
                    cursor.execute("DELETE FROM premium_data")
                    print("   ✅ Deleted related premium_data")
                
                cursor.execute('SELECT COUNT(*) FROM "user"')
                count = cursor.fetchone()[0]
                cursor.execute('DELETE FROM "user"')
                print(f"   ✅ Deleted {count} users")
                deleted_count = count
                
                cursor.execute("DELETE FROM sqlite_sequence WHERE name = 'user'")

        elif table_type == "tokens":
            print("\n🧹 CLEANING TOKENS ONLY...")
            if 'token' in existing_tables:
                cursor.execute("SELECT COUNT(*) FROM token")
                count = cursor.fetchone()[0]
                cursor.execute("DELETE FROM token")
                print(f"   ✅ Deleted {count} tokens")
                deleted_count = count

        elif table_type == "used_tokens":
            print("\n🧹 CLEANING USED TOKENS ONLY...")
            if 'token' in existing_tables:
                cursor.execute("SELECT COUNT(*) FROM token WHERE is_used = 1")
                count = cursor.fetchone()[0]
                cursor.execute("DELETE FROM token WHERE is_used = 1")
                print(f"   ✅ Deleted {count} used tokens")
                deleted_count = count

        elif table_type == "expired":
            print("\n🧹 CLEANING EXPIRED PREMIUM SUBSCRIPTIONS...")
            if 'premium_data' in existing_tables:
                cursor.execute("""
                    SELECT COUNT(*) FROM premium_data 
                    WHERE expired_at < datetime('now')
                """)
                count = cursor.fetchone()[0]
                
                cursor.execute("""
                    DELETE FROM premium_data 
                    WHERE expired_at < datetime('now')
                """)
                print(f"   ✅ Deleted {count} expired premium subscriptions")
                deleted_count = count
                
                # Update user status to Free
                if 'user' in existing_tables:
                    cursor.execute("""
                        UPDATE "user" 
                        SET status_account = 'Free'
                        WHERE id NOT IN (SELECT user_id FROM premium_data)
                        AND status_account = 'Premium'
                    """)
                    updated = cursor.rowcount
                    print(f"   ✅ Updated {updated} users to Free status")

        conn.commit()
        conn.close()
        
        if deleted_count > 0:
            print(f"\n✅ Successfully deleted {deleted_count} records!")
        else:
            print("\n✅ Cleanup completed!")

    except Exception as e:
        print(f"\n❌ Error cleaning database: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Main cleanup function."""
    print("="*70)
    print("DATABASE CLEANUP UTILITY")
    print("="*70)

    # Check if database exists
    db_path = check_database_exists()
    if not db_path:
        return

    # Handle premium subcommands first
    if len(sys.argv) >= 2 and sys.argv[1].lower() == "premium":
        if len(sys.argv) == 2:
            # Show premium stats only
            show_premium_stats(db_path)
            return
        
        # Premium cleanup subcommand
        premium_action = sys.argv[2].lower() if len(sys.argv) >= 3 else ""
        
        if premium_action == "stats":
            show_premium_stats(db_path)
            return
        
        # Show stats before cleanup
        has_premium_tables = show_premium_stats(db_path)
        if not has_premium_tables:
            print("\n✅ No premium data to clean!")
            return
        
        # Handle premium cleanup actions
        if premium_action == "all":
            confirm = input("\n⚠️⚠️⚠️  Delete ALL premium data? This cannot be undone! (yes/no): ").lower()
            if confirm in ["yes", "y"]:
                confirm2 = input("Type 'DELETE' to confirm: ")
                if confirm2 == "DELETE":
                    clean_premium_tables(db_path, "all")
                    vacuum_database(db_path)
                    show_premium_stats(db_path)
                else:
                    print("Cancelled.")
            else:
                print("Cancelled.")
        elif premium_action == "users":
            confirm = input("\n⚠️  Delete all users? This will also delete related premium_data. (yes/no): ").lower()
            if confirm in ["yes", "y"]:
                clean_premium_tables(db_path, "users")
                vacuum_database(db_path)
                show_premium_stats(db_path)
            else:
                print("Cancelled.")
        elif premium_action == "tokens":
            confirm = input("\n⚠️  Delete all tokens? (yes/no): ").lower()
            if confirm in ["yes", "y"]:
                clean_premium_tables(db_path, "tokens")
                vacuum_database(db_path)
                show_premium_stats(db_path)
            else:
                print("Cancelled.")
        elif premium_action == "used_tokens":
            confirm = input("\n⚠️  Delete all used tokens? (yes/no): ").lower()
            if confirm in ["yes", "y"]:
                clean_premium_tables(db_path, "used_tokens")
                vacuum_database(db_path)
                show_premium_stats(db_path)
            else:
                print("Cancelled.")
        elif premium_action == "expired":
            confirm = input("\n⚠️  Delete expired premium subscriptions? (yes/no): ").lower()
            if confirm in ["yes", "y"]:
                clean_premium_tables(db_path, "expired")
                vacuum_database(db_path)
                show_premium_stats(db_path)
            else:
                print("Cancelled.")
        elif premium_action == "vacuum":
            vacuum_database(db_path)
        else:
            print("\nUsage: python cleanup.py premium [all|users|tokens|used_tokens|expired|vacuum|stats]")
            print("\nOptions:")
            print("  all         - Delete ALL premium data (users + premium_data + tokens)")
            print("  users       - Delete users only (+ related premium_data)")
            print("  tokens      - Delete all tokens")
            print("  used_tokens - Delete used tokens only")
            print("  expired     - Delete expired premium subscriptions")
            print("  vacuum      - Vacuum database to reclaim space")
            print("  stats       - Show premium statistics only")
        return

    # Show current stats
    invoice_count, item_count = show_database_stats(db_path)

    # Interactive mode if no arguments
    if len(sys.argv) == 1:
        print("\n🧹 CLEANUP OPTIONS:")
        print("1. Clean all invoices data")
        print("2. Clean items only")
        print("3. Clean old data (7+ days)")
        print("4. Clean test data")
        print("5. Clean spending limits")
        print("6. Clean EVERYTHING (invoices + limits)")
        print("7. Premium data cleanup (interactive)")
        print("8. Just vacuum database")
        print("0. Exit")

        choice = input("\nSelect option (0-8): ").strip()

        if choice == "1":
            confirm = input("⚠️  Delete ALL invoices? (yes/no): ").lower()
            if confirm in ["yes", "y"]:
                clean_database(db_path, "all")
                vacuum_database(db_path)
        elif choice == "2":
            clean_database(db_path, "items")
            vacuum_database(db_path)
        elif choice == "3":
            clean_database(db_path, "old")
            vacuum_database(db_path)
        elif choice == "4":
            clean_database(db_path, "test")
            vacuum_database(db_path)
        elif choice == "5":
            confirm = input("⚠️  Delete ALL spending limits? (yes/no): ").lower()
            if confirm in ["yes", "y"]:
                clean_database(db_path, "limits")
                vacuum_database(db_path)
        elif choice == "6":
            confirm = input("⚠️⚠️⚠️  DELETE EVERYTHING? This cannot be undone! (yes/no): ").lower()
            if confirm in ["yes", "y"]:
                confirm2 = input("Type 'DELETE' to confirm: ")
                if confirm2 == "DELETE":
                    clean_database(db_path, "everything")
                    vacuum_database(db_path)
                else:
                    print("Cancelled.")
            else:
                print("Cancelled.")
        elif choice == "7":
            # Premium cleanup submenu
            has_premium_tables = show_premium_stats(db_path)
            if not has_premium_tables:
                print("\n✅ No premium data to clean!")
            else:
                print("\n💎 PREMIUM CLEANUP OPTIONS:")
                print("1. Clean ALL premium data (users + premium_data + tokens)")
                print("2. Clean users only (+ related premium_data)")
                print("3. Clean tokens only")
                print("4. Clean used tokens only")
                print("5. Clean expired premium subscriptions")
                print("0. Back")
                
                premium_choice = input("\nSelect option (0-5): ").strip()
                
                if premium_choice == "1":
                    confirm = input("⚠️⚠️⚠️  Delete ALL premium data? (yes/no): ").lower()
                    if confirm in ["yes", "y"]:
                        confirm2 = input("Type 'DELETE' to confirm: ")
                        if confirm2 == "DELETE":
                            clean_premium_tables(db_path, "all")
                            vacuum_database(db_path)
                elif premium_choice == "2":
                    clean_premium_tables(db_path, "users")
                    vacuum_database(db_path)
                elif premium_choice == "3":
                    clean_premium_tables(db_path, "tokens")
                    vacuum_database(db_path)
                elif premium_choice == "4":
                    clean_premium_tables(db_path, "used_tokens")
                    vacuum_database(db_path)
                elif premium_choice == "5":
                    clean_premium_tables(db_path, "expired")
                    vacuum_database(db_path)
        elif choice == "8":
            vacuum_database(db_path)
        elif choice == "0":
            print("Exiting...")
        else:
            print("Invalid option!")

    # Command line arguments
    else:
        action = sys.argv[1].lower()
        if action in ["all", "items", "old", "test", "limits", "everything"]:
            if action in ["all", "limits", "everything"]:
                confirm = input(f"⚠️  Delete {action.upper()} data? (yes/no): ").lower()
                if confirm not in ["yes", "y"]:
                    print("Cancelled.")
                    return
            clean_database(db_path, action)
            vacuum_database(db_path)
        elif action == "vacuum":
            vacuum_database(db_path)
        elif action == "stats":
            pass  # Already shown above
        else:
            print(f"\nUsage: {sys.argv[0]} [command] [options]")
            print("\nInvoice Commands:")
            print("  all        - Delete all invoices and items")
            print("  items      - Delete invoice items only")
            print("  old        - Delete invoices older than 7 days")
            print("  test       - Delete test invoices")
            print("  limits     - Delete spending limits")
            print("  everything - Delete invoices + limits (not premium)")
            print("  vacuum     - Vacuum database to reclaim space")
            print("  stats      - Show database statistics only")
            print("\nPremium Commands:")
            print("  premium [action]  - Manage premium data")
            print("    Actions: all, users, tokens, used_tokens, expired, vacuum, stats")
            print("\nExamples:")
            print("  python cleanup.py all")
            print("  python cleanup.py premium users")
            print("  python cleanup.py premium tokens")
            print("  python cleanup.py premium expired")

    # Show final stats
    if len(sys.argv) == 1 or (len(sys.argv) >= 2 and sys.argv[1] not in ["stats", "vacuum", "premium"]):
        print("\n" + "=" * 70)
        print("FINAL STATISTICS")
        show_database_stats(db_path)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Cleanup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
