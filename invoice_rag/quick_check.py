#!/usr/bin/env python3
"""Quick database check"""

import sqlite3

conn = sqlite3.connect('invoices.db')
cursor = conn.cursor()

# Count invoices
cursor.execute('SELECT COUNT(*) FROM invoices')
count = cursor.fetchone()[0]
print(f'Total invoices: {count}')

if count > 0:
    # Show recent invoices
    cursor.execute('SELECT id, shop_name, total_amount, invoice_date FROM invoices ORDER BY id DESC LIMIT 5')
    print('\nRecent invoices:')
    for row in cursor.fetchall():
        print(f'  ID {row[0]}: {row[1]} - Rp {row[2]:,.2f} ({row[3]})')
    
    # Total spending
    cursor.execute('SELECT SUM(total_amount) FROM invoices')
    total = cursor.fetchone()[0]
    print(f'\nTotal spending: Rp {total:,.2f}')

conn.close()
