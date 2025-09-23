#!/usr/bin/env python3
"""
Database Cleanup - Clean up invoice database
Merged from cleanup.py and quick_cleanup.py
"""

import os
import sqlite3
import sys
from datetime import datetime

def get_database_path():
    """Get the correct database path."""
    db_path = 'invoices.db'
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
        print("Database not found: invoices.db")
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

        print(f"\nCURRENT DATABASE STATS:")
        print(f"- Total Invoices: {invoice_count}")
        print(f"- Total Items: {item_count}")
        print(f"- Total Spending: Rp {total_spending:,.2f}")

        if invoice_count > 0:
            # Show date range
            cursor.execute("SELECT MIN(processed_at), MAX(processed_at) FROM invoices")
            date_range = cursor.fetchone()
            print(f"- Date Range: {date_range[0]} to {date_range[1]}")

            # Show recent invoices
            cursor.execute("""
                SELECT id, shop_name, total_amount, processed_at
                FROM invoices 
                ORDER BY processed_at DESC 
                LIMIT 5
            """)
            recent = cursor.fetchall()

            print(f"\nRECENT INVOICES:")
            for id, shop, amount, date in recent:
                print(f"- ID {id}: {shop} - Rp {amount:,.2f} ({date})")

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
            print("\nCLEANING ALL DATA...")
            cursor.execute("DELETE FROM invoice_items")
            cursor.execute("DELETE FROM invoices")
            cursor.execute("DELETE FROM sqlite_sequence WHERE name IN ('invoices', 'invoice_items')")
            print("- Deleted all invoices and items")

        elif clean_type == "items":
            print("\nCLEANING ITEMS ONLY...")
            cursor.execute("DELETE FROM invoice_items")
            print("- Deleted all invoice items")

        elif clean_type == "old":
            print("\nCLEANING OLD DATA (7+ days)...")
            cursor.execute("""
                DELETE FROM invoice_items 
                WHERE invoice_id IN (
                    SELECT id FROM invoices 
                    WHERE processed_at < datetime('now', '-7 days')
                )
            """)
            cursor.execute("DELETE FROM invoices WHERE processed_at < datetime('now', '-7 days')")
            deleted = cursor.rowcount
            print(f"- Deleted {deleted} old invoices")

        elif clean_type == "test":
            print("\nCLEANING TEST DATA...")
            cursor.execute("""
                DELETE FROM invoice_items 
                WHERE invoice_id IN (
                    SELECT id FROM invoices 
                    WHERE shop_name LIKE '%test%' OR shop_name LIKE '%Test%'
                )
            """)
            cursor.execute("DELETE FROM invoices WHERE shop_name LIKE '%test%' OR shop_name LIKE '%Test%'")
            deleted = cursor.rowcount
            print(f"- Deleted {deleted} test invoices")

        conn.commit()
        conn.close()
        print("✅ Database cleaned successfully!")

    except Exception as e:
        print(f"❌ Error cleaning database: {e}")

def vacuum_database(db_path):
    """Vacuum database to reclaim space."""
    try:
        print("\nVACUUMING DATABASE...")
        conn = sqlite3.connect(db_path)
        conn.execute("VACUUM")
        conn.close()
        print("✅ Database vacuumed successfully!")
    except Exception as e:
        print(f"❌ Error vacuuming database: {e}")

def main():
    """Main cleanup function."""
    print("DATABASE CLEANUP UTILITY")
    print("=" * 50)

    # Check if database exists
    db_path = check_database_exists()
    if not db_path:
        return

    # Show current stats
    invoice_count, item_count = show_database_stats(db_path)

    if invoice_count == 0:
        print("\n✅ Database is already empty!")
        return

    # Interactive mode if no arguments
    if len(sys.argv) == 1:
        print("\nCLEANUP OPTIONS:")
        print("1. Clean all data")
        print("2. Clean items only")
        print("3. Clean old data (7+ days)")
        print("4. Clean test data")
        print("5. Just vacuum database")
        print("0. Exit")

        choice = input("\nSelect option (0-5): ").strip()

        if choice == "1":
            confirm = input("⚠️  Delete ALL data? (yes/no/y/n): ").lower()
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
            vacuum_database(db_path)
        elif choice == "0":
            print("Exiting...")
        else:
            print("Invalid option!")

    # Command line arguments
    else:
        action = sys.argv[1].lower()
        if action in ["all", "items", "old", "test"]:
            if action == "all":
                confirm = input("⚠️  Delete ALL data? (yes/no/y/n): ").lower()
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
            print(f"Usage: {sys.argv[0]} [all|items|old|test|vacuum|stats]")

    # Show final stats
    print("\n" + "=" * 50)
    show_database_stats(db_path)

if __name__ == "__main__":
    main()
