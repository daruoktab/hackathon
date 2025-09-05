#!/usr/bin/env python3
"""
View Database Contents - Shows all invoice data stored in the database
"""

import os
import sqlite3

def check_database_exists():
    """Check if database exists and show available databases."""
    
    print("CHECKING FOR DATABASES:")
    print("-" * 35)
    
    databases = []
    
    # Check common database locations - prioritize local database
    db_files = [
        'invoices.db',              # Current directory (priority)
        '../invoices.db',           # Root directory 
        'demo_invoices.db', 
        'invoice_rag/invoices.db'   # Old location
    ]
    
    for db_file in db_files:
        if os.path.exists(db_file):
            size = os.path.getsize(db_file)
            print(f"[FOUND] {db_file} ({size} bytes)")
            databases.append(db_file)
        else:
            print(f"[NOT FOUND] {db_file}")
    
    return databases

def view_database_contents(db_path):
    """View all contents of a database."""
    
    print(f"\nVIEWING DATABASE: {db_path}")
    print("=" * 60)
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        if not tables:
            print("[ERROR] No tables found in database")
            return
            
        table_names = [table[0] for table in tables]
        print(f"Tables found: {table_names}")
        
        # Show invoices
        if 'invoices' in table_names:
            show_invoices(cursor)
        
        # Show invoice items
        if 'invoice_items' in table_names:
            show_invoice_items(cursor)
            
        # Show summary
        show_summary(cursor)
            
        conn.close()
        
    except Exception as e:
        print(f"[ERROR] Failed to read database: {e}")

def show_invoices(cursor):
    """Show all invoices in a clean format."""
    
    print("\nINVOICES TABLE:")
    print("-" * 50)
    
    cursor.execute("SELECT COUNT(*) FROM invoices")
    count = cursor.fetchone()[0]
    print(f"Total invoices: {count}")
    
    if count == 0:
        print("[INFO] No invoices found")
        return
        
    cursor.execute("""
        SELECT id, shop_name, invoice_date, invoice_time, total_amount, 
               payment_method, processed_at, image_path
        FROM invoices 
        ORDER BY processed_at DESC
    """)
    
    invoices = cursor.fetchall()
    
    print("\nINVOICE DETAILS:")
    print("-" * 100)
    
    for invoice in invoices:
        id, shop_name, inv_date, inv_time, total, payment, processed, image = invoice
        
        print(f"\nInvoice ID: {id}")
        print(f"   Shop: {shop_name}")
        print(f"   Date: {inv_date or 'N/A'}")
        print(f"   Time: {inv_time or 'N/A'}")
        print(f"   Total: Rp {total:,.2f}")
        print(f"   Payment: {payment or 'N/A'}")
        print(f"   Processed: {processed}")
        print(f"   Image: {image}")
        
        # Show items for this invoice
        cursor.execute("""
            SELECT item_name, quantity, unit_price, total_price
            FROM invoice_items 
            WHERE invoice_id = ?
        """, (id,))
        
        items = cursor.fetchall()
        if items:
            print(f"   Items ({len(items)}):")
            for item_name, qty, unit_price, total_price in items:
                print(f"      • {item_name}")
                print(f"        Qty: {qty}")
                print(f"        Unit: Rp {unit_price:,.2f}")
                print(f"        Total: Rp {total_price:,.2f}")
        print("-" * 50)

def show_invoice_items(cursor):
    """Show all invoice items grouped by shop."""
    
    print("\nINVOICE ITEMS TABLE:")
    print("-" * 40)
    
    cursor.execute("SELECT COUNT(*) FROM invoice_items")
    count = cursor.fetchone()[0]
    print(f"Total items: {count}")
    
    if count == 0:
        print("[INFO] No items found")
        return
    
    cursor.execute("""
        SELECT i.shop_name, ii.item_name, ii.quantity, ii.unit_price, ii.total_price
        FROM invoice_items ii
        JOIN invoices i ON ii.invoice_id = i.id
        ORDER BY i.shop_name, ii.item_name
    """)
    
    items = cursor.fetchall()
    
    print("\nITEM DETAILS:")
    print("-" * 80)
    
    current_shop = None
    for shop_name, item_name, qty, unit_price, total_price in items:
        if shop_name != current_shop:
            print(f"\nShop: {shop_name}")
            current_shop = shop_name
        
        print(f"   • {item_name}")
        print(f"     Qty: {qty}")
        print(f"     Unit Price: Rp {unit_price:,.2f}")
        print(f"     Total: Rp {total_price:,.2f}")

def show_summary(cursor):
    """Show database summary statistics."""
    
    print("\nDATABASE SUMMARY:")
    print("-" * 50)
    
    # Total invoices
    cursor.execute("SELECT COUNT(*) FROM invoices")
    total_invoices = cursor.fetchone()[0]
    
    # Total items
    cursor.execute("SELECT COUNT(*) FROM invoice_items")
    total_items = cursor.fetchone()[0]
    
    # Total spending
    cursor.execute("SELECT SUM(total_amount) FROM invoices")
    total_spending = cursor.fetchone()[0] or 0
    
    # Unique shops
    cursor.execute("SELECT COUNT(DISTINCT shop_name) FROM invoices")
    unique_shops = cursor.fetchone()[0]
    
    # Date range
    cursor.execute("SELECT MIN(processed_at), MAX(processed_at) FROM invoices")
    date_range = cursor.fetchone()
    
    print(f"Total Invoices: {total_invoices}")
    print(f"Total Items: {total_items}")
    print(f"Total Spending: Rp {total_spending:,.2f}")
    print(f"Unique Shops: {unique_shops}")
    print(f"Date Range: {date_range[0]} to {date_range[1]}")
    
    if total_invoices > 0:
        avg_per_invoice = total_spending / total_invoices
        avg_items_per_invoice = total_items / total_invoices
        print(f"Average per Invoice: Rp {avg_per_invoice:,.2f}")
        print(f"Average Items per Invoice: {avg_items_per_invoice:.1f}")
    
    # Top shops by spending
    print("\nTOP SHOPS BY SPENDING:")
    cursor.execute("""
        SELECT shop_name, SUM(total_amount) as total_spent, COUNT(*) as transactions
        FROM invoices 
        GROUP BY shop_name 
        ORDER BY total_spent DESC
    """)
    
    top_shops = cursor.fetchall()
    for i, (shop, total, txns) in enumerate(top_shops, 1):
        print(f"   {i}. {shop}: Rp {total:,.2f} ({txns} transactions)")

def main():
    """Main function to view database contents."""
    
    print("DATABASE VIEWER")
    print("=" * 30)
    print("This script shows all invoice data stored in the database")
    
    # Check for available databases
    databases = check_database_exists()
    
    if not databases:
        print("\n[ERROR] No database files found!")
        print("Please run the invoice processing script first to create the database.")
        return
    
    # Use the first available database
    db_path = databases[0]
    view_database_contents(db_path)
    
    print("\n" + "=" * 60)
    print("[SUCCESS] DATABASE VIEWING COMPLETE!")
    print("This is where all your invoice data is stored and analyzed.")
    print("=" * 60)

if __name__ == "__main__":
    main()
