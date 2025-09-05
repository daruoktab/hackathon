#!/usr/bin/env python3
"""
View Database Contents - Shows all invoice data stored in the database
"""

import os
import sqlite3

def check_database_exists():
    """Check if database exists and show available databases."""
    
    print("🔍 CHECKING FOR DATABASES:")
    print("-" * 35)
    
    databases = []
    
    # Check common database locations
    db_files = [
        'invoices.db',
        'demo_invoices.db', 
        '../invoices.db',
        'invoice_rag/invoices.db'
    ]
    
    for db_file in db_files:
        if os.path.exists(db_file):
            size = os.path.getsize(db_file)
            print(f"✅ Found: {db_file} ({size} bytes)")
            databases.append(db_file)
        else:
            print(f"❌ Not found: {db_file}")
    
    return databases

def view_database_contents(db_path):
    """View all contents of a database."""
    
    print(f"\n💾 VIEWING DATABASE: {db_path}")
    print("=" * 60)
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        if not tables:
            print("❌ No tables found in database")
            return
        
        print(f"📋 Tables found: {[table[0] for table in tables]}")
        
        # Show invoices table
        if ('invoices',) in tables:
            show_invoices_table(cursor)
        
        # Show invoice_items table  
        if ('invoice_items',) in tables:
            show_items_table(cursor)
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error reading database: {e}")

def show_invoices_table(cursor):
    """Show all data from invoices table."""
    
    print("\n📋 INVOICES TABLE:")
    print("-" * 50)
    
    try:
        cursor.execute("SELECT COUNT(*) FROM invoices")
        count = cursor.fetchone()[0]
        
        if count == 0:
            print("❌ No invoices found in database")
            return
        
        print(f"📊 Total invoices: {count}")
        
        # Get all invoices
        cursor.execute("""
            SELECT id, shop_name, invoice_date, total_amount, 
                   payment_method, processed_at, image_path
            FROM invoices 
            ORDER BY processed_at DESC
        """)
        
        invoices = cursor.fetchall()
        
        print("\n🧾 INVOICE DETAILS:")
        print("-" * 100)
        
        for invoice in invoices:
            id, shop_name, inv_date, total, payment, processed, image = invoice
            
            print(f"\n🧾 Invoice ID: {id}")
            print(f"   🏪 Shop: {shop_name}")
            print(f"   📅 Date: {inv_date or 'N/A'}")
            print(f"   💰 Total: Rp {total:,.2f}")
            print(f"   💳 Payment: {payment or 'N/A'}")
            print(f"   🕒 Processed: {processed}")
            print(f"   📸 Image: {image}")
            
            # Show items for this invoice
            cursor.execute("""
                SELECT name, quantity, unit_price, total_price 
                FROM invoice_items 
                WHERE invoice_id = ?
            """, (id,))
            
            items = cursor.fetchall()
            if items:
                print(f"   🛒 Items ({len(items)}):")
                for item in items:
                    name, qty, unit_price, item_total = item
                    print(f"      • {name}")
                    if qty:
                        print(f"        Qty: {qty}")
                    if unit_price:
                        print(f"        Unit: Rp {unit_price:,.2f}")
                    print(f"        Total: Rp {item_total:,.2f}")
            
            print("-" * 50)
        
    except Exception as e:
        print(f"❌ Error reading invoices: {e}")

def show_items_table(cursor):
    """Show all data from invoice_items table."""
    
    print("\n🛒 INVOICE ITEMS TABLE:")
    print("-" * 40)
    
    try:
        cursor.execute("SELECT COUNT(*) FROM invoice_items")
        count = cursor.fetchone()[0]
        
        if count == 0:
            print("❌ No items found in database")
            return
        
        print(f"📊 Total items: {count}")
        
        # Get all items with invoice info
        cursor.execute("""
            SELECT i.shop_name, it.name, it.quantity, it.unit_price, it.total_price
            FROM invoice_items it
            JOIN invoices i ON it.invoice_id = i.id
            ORDER BY i.processed_at DESC, it.id
        """)
        
        items = cursor.fetchall()
        
        print("\n📦 ITEM DETAILS:")
        print("-" * 80)
        
        current_shop = None
        for item in items:
            shop, name, qty, unit_price, total = item
            
            if shop != current_shop:
                print(f"\n🏪 {shop}:")
                current_shop = shop
            
            print(f"   • {name}")
            if qty:
                print(f"     Qty: {qty}")
            if unit_price:
                print(f"     Unit Price: Rp {unit_price:,.2f}")
            print(f"     Total: Rp {total:,.2f}")
        
    except Exception as e:
        print(f"❌ Error reading items: {e}")

def show_database_summary(db_path):
    """Show database summary statistics."""
    
    print(f"\n📊 DATABASE SUMMARY: {db_path}")
    print("-" * 50)
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Invoice count
        cursor.execute("SELECT COUNT(*) FROM invoices")
        invoice_count = cursor.fetchone()[0]
        
        # Item count
        cursor.execute("SELECT COUNT(*) FROM invoice_items")
        item_count = cursor.fetchone()[0]
        
        # Total spending
        cursor.execute("SELECT SUM(total_amount) FROM invoices")
        total_spending = cursor.fetchone()[0] or 0
        
        # Unique shops
        cursor.execute("SELECT COUNT(DISTINCT shop_name) FROM invoices")
        unique_shops = cursor.fetchone()[0]
        
        # Date range
        cursor.execute("SELECT MIN(processed_at), MAX(processed_at) FROM invoices")
        date_range = cursor.fetchone()
        
        print(f"📋 Total Invoices: {invoice_count}")
        print(f"🛒 Total Items: {item_count}")
        print(f"💰 Total Spending: Rp {total_spending:,.2f}")
        print(f"🏪 Unique Shops: {unique_shops}")
        
        if date_range[0] and date_range[1]:
            print(f"📅 Date Range: {date_range[0]} to {date_range[1]}")
        
        if invoice_count > 0:
            avg_per_invoice = total_spending / invoice_count
            avg_items_per_invoice = item_count / invoice_count
            print(f"📊 Average per Invoice: Rp {avg_per_invoice:,.2f}")
            print(f"🛒 Average Items per Invoice: {avg_items_per_invoice:.1f}")
        
        # Top shops
        cursor.execute("""
            SELECT shop_name, COUNT(*), SUM(total_amount)
            FROM invoices 
            GROUP BY shop_name 
            ORDER BY SUM(total_amount) DESC 
            LIMIT 5
        """)
        
        top_shops = cursor.fetchall()
        if top_shops:
            print("\n🏆 TOP SHOPS BY SPENDING:")
            for i, (shop, count, total) in enumerate(top_shops, 1):
                print(f"   {i}. {shop}: Rp {total:,.2f} ({count} transactions)")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error generating summary: {e}")

def main():
    """Main function to view database contents."""
    
    print("👀 DATABASE VIEWER")
    print("=" * 30)
    print("This script shows all invoice data stored in the database")
    
    # Check for existing databases
    databases = check_database_exists()
    
    if not databases:
        print("\n❌ No databases found!")
        print("\n💡 To create data:")
        print("1. Run: python -m src.main")
        print("2. Or process images with the main system")
        print("3. Then run this script again to view the data")
        return
    
    # View each database
    for db_path in databases:
        view_database_contents(db_path)
        show_database_summary(db_path)
    
    print("\n" + "=" * 60)
    print("✅ DATABASE VIEWING COMPLETE!")
    print("💡 This is where all your invoice data is stored and analyzed.")
    print("=" * 60)

if __name__ == "__main__":
    main()
