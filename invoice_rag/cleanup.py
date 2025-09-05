#!/usr/bin/env python3
"""
Database Cleanup - Clean up invoice database
"""

import os
import sqlite3
from datetime import datetime

def check_database_exists():
    """Check if database exists."""
    db_path = 'invoices.db'
    if os.path.exists(db_path):
        size = os.path.getsize(db_path)
        print(f"Found database: {db_path} ({size} bytes)")
        return db_path
    else:
        print(f"Database not found: {db_path}")
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
            cursor.execute("DELETE FROM sqlite_sequence")  # Reset auto-increment
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
                    WHERE image_path LIKE '%test%'
                )
            """)
            cursor.execute("DELETE FROM invoices WHERE image_path LIKE '%test%'")
            deleted = cursor.rowcount
            print(f"- Deleted {deleted} test invoices")
        
        conn.commit()
        conn.close()
        print("Database cleanup completed successfully!")
        
    except Exception as e:
        print(f"Error cleaning database: {e}")

def main():
    """Main cleanup function."""
    print("DATABASE CLEANUP TOOL")
    print("=" * 50)
    
    # Check database
    db_path = check_database_exists()
    if not db_path:
        print("No database found to clean!")
        return
    
    # Show current stats
    invoice_count, item_count = show_database_stats(db_path)
    
    if invoice_count == 0:
        print("\nDatabase is already empty!")
        return
    
    # Show cleanup options
    print(f"\nCLEANUP OPTIONS:")
    print(f"1. Clean ALL data (delete everything)")
    print(f"2. Clean items only (keep invoices)")
    print(f"3. Clean old data (7+ days old)")
    print(f"4. Clean test data (test images)")
    print(f"5. Show stats only (no cleanup)")
    print(f"6. Exit")
    
    while True:
        choice = input(f"\nEnter your choice (1-6): ").strip()
        
        if choice == "1":
            confirm = input(f"Are you sure you want to delete ALL {invoice_count} invoices? (yes/no): ")
            if confirm.lower() == "yes":
                clean_database(db_path, "all")
                break
            else:
                print("Cleanup cancelled.")
                
        elif choice == "2":
            confirm = input(f"Are you sure you want to delete ALL {item_count} items? (yes/no): ")
            if confirm.lower() == "yes":
                clean_database(db_path, "items")
                break
            else:
                print("Cleanup cancelled.")
                
        elif choice == "3":
            confirm = input(f"Delete invoices older than 7 days? (yes/no): ")
            if confirm.lower() == "yes":
                clean_database(db_path, "old")
                break
            else:
                print("Cleanup cancelled.")
                
        elif choice == "4":
            confirm = input(f"Delete test data (test images)? (yes/no): ")
            if confirm.lower() == "yes":
                clean_database(db_path, "test")
                break
            else:
                print("Cleanup cancelled.")
                
        elif choice == "5":
            print("Stats shown above. No cleanup performed.")
            break
            
        elif choice == "6":
            print("Exiting without cleanup.")
            break
            
        else:
            print("Invalid choice. Please enter 1-6.")
    
    # Show final stats if cleanup was performed
    if choice in ["1", "2", "3", "4"]:
        print(f"\nFINAL STATS AFTER CLEANUP:")
        show_database_stats(db_path)
    
    print(f"\nCLEANUP COMPLETE!")

if __name__ == "__main__":
    main()
