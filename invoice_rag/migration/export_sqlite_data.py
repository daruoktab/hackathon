#!/usr/bin/env python3
"""
SQLite Data Export Script
Exports all data from SQLite database to JSON for Supabase migration
"""
import sqlite3
import json
from datetime import datetime
import os
import sys

def get_db_path():
    """Get the absolute path to the SQLite database"""
    current_file = os.path.abspath(__file__)
    migration_dir = os.path.dirname(current_file)
    invoice_rag_dir = os.path.dirname(migration_dir)
    return os.path.join(invoice_rag_dir, 'invoices.db')

def export_table(cursor, table_name):
    """Export a single table to a list of dictionaries"""
    try:
        cursor.execute(f"SELECT * FROM {table_name}")
        columns = [description[0] for description in cursor.description]
        rows = cursor.fetchall()

        data = []
        for row in rows:
            record = {}
            for i, column in enumerate(columns):
                record[column] = row[i]
            data.append(record)

        return data
    except sqlite3.OperationalError as e:
        print(f"⚠️  Warning: Could not export table '{table_name}': {e}")
        return []

def export_data():
    """Export all data from SQLite database"""
    db_path = get_db_path()

    if not os.path.exists(db_path):
        print(f"❌ Error: Database file not found at {db_path}")
        sys.exit(1)

    print("=" * 70)
    print("🚀 SQLite Data Export Tool")
    print("=" * 70)
    print(f"📁 Database: {db_path}")
    print()

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get list of all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
    all_tables = [row[0] for row in cursor.fetchall()]
    print(f"📊 Found {len(all_tables)} tables: {', '.join(all_tables)}")
    print()

    data = {}
    total_records = 0

    # Export core tables in order (to maintain foreign key relationships)
    tables_to_export = [
        'invoices',
        'invoice_items',
        'platform_users',
        'spending_limits',
        'spending_limits_v2'
    ]

    for table_name in tables_to_export:
        if table_name in all_tables:
            print(f"📦 Exporting table: {table_name}")
            table_data = export_table(cursor, table_name)
            data[table_name] = table_data
            record_count = len(table_data)
            total_records += record_count
            print(f"   ✅ Exported {record_count} records")
        else:
            print(f"   ⚠️  Table '{table_name}' not found, skipping")
            data[table_name] = []

    # Export any additional tables not in the main list
    additional_tables = [t for t in all_tables if t not in tables_to_export]
    if additional_tables:
        print()
        print("📦 Exporting additional tables:")
        for table_name in additional_tables:
            print(f"   {table_name}")
            table_data = export_table(cursor, table_name)
            data[table_name] = table_data
            record_count = len(table_data)
            total_records += record_count
            print(f"   ✅ Exported {record_count} records")

    conn.close()

    # Create export directory if it doesn't exist
    export_dir = os.path.dirname(os.path.abspath(__file__))

    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    export_filename = f'sqlite_export_{timestamp}.json'
    export_path = os.path.join(export_dir, export_filename)

    # Save to JSON file
    print()
    print("💾 Saving data to JSON file...")
    with open(export_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False, default=str)

    file_size = os.path.getsize(export_path)
    file_size_mb = file_size / (1024 * 1024)

    print()
    print("=" * 70)
    print("✅ Export completed successfully!")
    print("=" * 70)
    print(f"📄 File: {export_path}")
    print(f"📊 Total records: {total_records}")
    print(f"💾 File size: {file_size_mb:.2f} MB")
    print()
    print("📋 Export summary:")
    for table_name, table_data in data.items():
        if table_data:
            print(f"   • {table_name}: {len(table_data)} records")
    print()
    print("🚀 Next step: Run import_to_supabase.py with this export file")
    print(f"   python migration/import_to_supabase.py migration/{export_filename}")
    print("=" * 70)

    return export_path

def verify_export(export_path):
    """Verify the exported data"""
    print()
    print("🔍 Verifying export...")

    with open(export_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Check for data integrity
    issues = []

    # Check if invoices have corresponding items
    if data.get('invoices') and data.get('invoice_items'):
        invoice_ids = set(inv['id'] for inv in data['invoices'])
        item_invoice_ids = set(item['invoice_id'] for item in data['invoice_items'])
        orphaned_items = item_invoice_ids - invoice_ids

        if orphaned_items:
            issues.append(f"⚠️  Found {len(orphaned_items)} orphaned invoice items")

    # Check if spending_limits_v2 references valid platform_users
    if data.get('spending_limits_v2') and data.get('platform_users'):
        user_ids = set(user['id'] for user in data['platform_users'])
        limit_user_ids = set(limit['user_id'] for limit in data['spending_limits_v2'])
        invalid_refs = limit_user_ids - user_ids

        if invalid_refs:
            issues.append(f"⚠️  Found {len(invalid_refs)} spending limits with invalid user references")

    if issues:
        print("⚠️  Verification warnings:")
        for issue in issues:
            print(f"   {issue}")
    else:
        print("✅ Verification passed: No data integrity issues found")

if __name__ == '__main__':
    try:
        export_path = export_data()
        verify_export(export_path)
    except Exception as e:
        print(f"❌ Error during export: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
