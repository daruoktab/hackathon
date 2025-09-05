#!/usr/bin/env python3
"""
Quick Database Cleanup - Non-interactive cleanup options
"""

import os
import sqlite3
import sys

def get_database_path():
    """Get the correct database path."""
    db_path = 'invoices.db'
    if os.path.exists(db_path):
        return db_path
    return None

def show_stats():
    """Show database statistics."""
    db_path = get_database_path()
    if not db_path:
        print("Database not found!")
        return
    
    print(f"Using database: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM invoices")
    invoice_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM invoice_items")
    item_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT SUM(total_amount) FROM invoices")
    total_spending = cursor.fetchone()[0] or 0
    
    print(f"Database Stats: {invoice_count} invoices, {item_count} items, Rp {total_spending:,.2f}")
    conn.close()

def clean_duplicates():
    """Remove duplicate invoices (keep newest)."""
    db_path = get_database_path()
    if not db_path:
        print("Database not found!")
        return
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Find duplicates based on shop_name, total_amount, and image_path
    cursor.execute("""
        DELETE FROM invoice_items 
        WHERE invoice_id IN (
            SELECT i1.id FROM invoices i1
            INNER JOIN invoices i2 ON 
                i1.shop_name = i2.shop_name AND 
                i1.total_amount = i2.total_amount AND
                i1.image_path = i2.image_path AND
                i1.id < i2.id
        )
    """)
    
    cursor.execute("""
        DELETE FROM invoices 
        WHERE id IN (
            SELECT i1.id FROM invoices i1
            INNER JOIN invoices i2 ON 
                i1.shop_name = i2.shop_name AND 
                i1.total_amount = i2.total_amount AND
                i1.image_path = i2.image_path AND
                i1.id < i2.id
        )
    """)
    
    deleted = cursor.rowcount
    conn.commit()
    conn.close()
    print(f"Removed {deleted} duplicate invoices")

def clean_test_data():
    """Remove test data."""
    db_path = get_database_path()
    if not db_path:
        print("Database not found!")
        return
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM invoice_items WHERE invoice_id IN (SELECT id FROM invoices WHERE image_path LIKE '%test%')")
    cursor.execute("DELETE FROM invoices WHERE image_path LIKE '%test%'")
    
    deleted = cursor.rowcount
    conn.commit()
    conn.close()
    print(f"Removed {deleted} test invoices")

def clean_all():
    """Remove all data."""
    db_path = get_database_path()
    if not db_path:
        print("Database not found!")
        return
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM invoice_items")
    cursor.execute("DELETE FROM invoices")
    cursor.execute("DELETE FROM sqlite_sequence")
    
    conn.commit()
    conn.close()
    print("Removed all data")

def main():
    """Main function with command line arguments."""
    
    if len(sys.argv) < 2:
        print("Quick Database Cleanup")
        print("Usage:")
        print("  python quick_cleanup.py stats           - Show database stats")
        print("  python quick_cleanup.py duplicates      - Remove duplicate invoices")
        print("  python quick_cleanup.py test           - Remove test data")
        print("  python quick_cleanup.py all            - Remove all data")
        return
    
    command = sys.argv[1].lower()
    
    print("QUICK DATABASE CLEANUP")
    print("=" * 30)
    
    if command == "stats":
        show_stats()
    elif command == "duplicates":
        print("Removing duplicate invoices...")
        show_stats()
        clean_duplicates()
        print("After cleanup:")
        show_stats()
    elif command == "test":
        print("Removing test data...")
        show_stats()
        clean_test_data()
        print("After cleanup:")
        show_stats()
    elif command == "all":
        print("Removing all data...")
        show_stats()
        clean_all()
        print("After cleanup:")
        show_stats()
    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    main()
