#!/usr/bin/env python3
"""
Supabase Data Import Script
Imports data from JSON export to Supabase PostgreSQL database
"""
import json
import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Try importing Supabase client
try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    print("⚠️  Warning: supabase-py not installed. Install with: pip install supabase")

# Try importing psycopg2 for direct database access
try:
    import psycopg2
    from psycopg2.extras import execute_batch
    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False
    print("⚠️  Warning: psycopg2 not installed. Install with: pip install psycopg2-binary")


def get_supabase_client():
    """Initialize Supabase client"""
    if not SUPABASE_AVAILABLE:
        raise ImportError("supabase-py is not installed. Run: pip install supabase")

    supabase_url = os.environ.get("SUPABASE_URL")
    supabase_key = os.environ.get("SUPABASE_SERVICE_KEY")

    if not supabase_url or not supabase_key:
        raise ValueError(
            "SUPABASE_URL and SUPABASE_SERVICE_KEY must be set in .env file\n"
            "Get these from: Supabase Dashboard > Settings > API"
        )

    return create_client(supabase_url, supabase_key)


def get_postgres_connection():
    """Get direct PostgreSQL connection"""
    if not PSYCOPG2_AVAILABLE:
        raise ImportError("psycopg2 is not installed. Run: pip install psycopg2-binary")

    host = os.environ.get("SUPABASE_DB_HOST")
    port = os.environ.get("SUPABASE_DB_PORT", "5432")
    database = os.environ.get("SUPABASE_DB_NAME", "postgres")
    user = os.environ.get("SUPABASE_DB_USER", "postgres")
    password = os.environ.get("SUPABASE_DB_PASSWORD")

    if not host or not password:
        raise ValueError(
            "SUPABASE_DB_HOST and SUPABASE_DB_PASSWORD must be set in .env file\n"
            "Get these from: Supabase Dashboard > Settings > Database"
        )

    return psycopg2.connect(
        host=host,
        port=port,
        database=database,
        user=user,
        password=password
    )


def import_with_supabase_client(data):
    """Import data using Supabase Python client (slower but easier)"""
    print("\n📡 Using Supabase Client API method...")

    supabase = get_supabase_client()
    stats = {
        'success': 0,
        'errors': 0,
        'skipped': 0
    }

    # Import order matters due to foreign keys
    import_order = [
        'platform_users',
        'invoices',
        'invoice_items',
        'spending_limits',
        'spending_limits_v2'
    ]

    for table_name in import_order:
        if table_name not in data or not data[table_name]:
            print(f"⏭️  Skipping {table_name} (no data)")
            continue

        records = data[table_name]
        print(f"\n📦 Importing {len(records)} records to {table_name}...")

        # Import in batches to avoid rate limits
        batch_size = 100
        for i in range(0, len(records), batch_size):
            batch = records[i:i + batch_size]

            try:
                response = supabase.table(table_name).insert(batch).execute()
                stats['success'] += len(batch)
                print(f"   ✅ Batch {i//batch_size + 1}: {len(batch)} records")
            except Exception as e:
                print(f"   ❌ Error in batch {i//batch_size + 1}: {e}")

                # Try inserting records one by one
                for record in batch:
                    try:
                        supabase.table(table_name).insert(record).execute()
                        stats['success'] += 1
                    except Exception as e2:
                        print(f"   ⚠️  Failed to import record ID {record.get('id', 'unknown')}: {e2}")
                        stats['errors'] += 1

        print(f"   ✅ Completed {table_name}")

    return stats


def import_with_postgres_direct(data):
    """Import data using direct PostgreSQL connection (faster)"""
    print("\n🔌 Using Direct PostgreSQL method...")

    conn = get_postgres_connection()
    cursor = conn.cursor()

    stats = {
        'success': 0,
        'errors': 0,
        'skipped': 0
    }

    try:
        # Import order matters due to foreign keys
        tables_config = {
            'platform_users': {
                'columns': ['id', 'platform', 'platform_user_id', 'display_name', 'phone_number', 'created_at', 'last_active'],
                'insert_sql': """
                    INSERT INTO platform_users (id, platform, platform_user_id, display_name, phone_number, created_at, last_active)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (platform, platform_user_id) DO NOTHING
                """
            },
            'invoices': {
                'columns': ['id', 'shop_name', 'invoice_date', 'total_amount', 'transaction_type', 'processed_at', 'image_path'],
                'insert_sql': """
                    INSERT INTO invoices (id, shop_name, invoice_date, total_amount, transaction_type, processed_at, image_path)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
            },
            'invoice_items': {
                'columns': ['id', 'invoice_id', 'item_name', 'quantity', 'unit_price', 'total_price'],
                'insert_sql': """
                    INSERT INTO invoice_items (id, invoice_id, item_name, quantity, unit_price, total_price)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """
            },
            'spending_limits': {
                'columns': ['user_id', 'monthly_limit', 'created_at', 'updated_at'],
                'insert_sql': """
                    INSERT INTO spending_limits (user_id, monthly_limit, created_at, updated_at)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (user_id) DO UPDATE SET
                        monthly_limit = EXCLUDED.monthly_limit,
                        updated_at = EXCLUDED.updated_at
                """
            },
            'spending_limits_v2': {
                'columns': ['id', 'user_id', 'monthly_limit', 'created_at', 'updated_at'],
                'insert_sql': """
                    INSERT INTO spending_limits_v2 (id, user_id, monthly_limit, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s)
                """
            }
        }

        for table_name, config in tables_config.items():
            if table_name not in data or not data[table_name]:
                print(f"⏭️  Skipping {table_name} (no data)")
                continue

            records = data[table_name]
            print(f"\n📦 Importing {len(records)} records to {table_name}...")

            # Prepare data tuples
            values = []
            for record in records:
                row = tuple(record.get(col) for col in config['columns'])
                values.append(row)

            try:
                # Use execute_batch for better performance
                execute_batch(cursor, config['insert_sql'], values, page_size=1000)
                conn.commit()
                stats['success'] += len(values)
                print(f"   ✅ Imported {len(values)} records")
            except Exception as e:
                print(f"   ❌ Error: {e}")
                conn.rollback()

                # Try one by one
                print(f"   🔄 Retrying with individual inserts...")
                for i, row in enumerate(values):
                    try:
                        cursor.execute(config['insert_sql'], row)
                        conn.commit()
                        stats['success'] += 1
                    except Exception as e2:
                        print(f"   ⚠️  Failed record {i+1}: {e2}")
                        stats['errors'] += 1
                        conn.rollback()

        # Update sequences to continue from the last imported ID
        print("\n🔧 Updating sequences...")
        sequence_updates = [
            ("SELECT setval('invoices_id_seq', (SELECT MAX(id) FROM invoices))", "invoices"),
            ("SELECT setval('invoice_items_id_seq', (SELECT MAX(id) FROM invoice_items))", "invoice_items"),
            ("SELECT setval('platform_users_id_seq', (SELECT MAX(id) FROM platform_users))", "platform_users"),
            ("SELECT setval('spending_limits_v2_id_seq', (SELECT MAX(id) FROM spending_limits_v2))", "spending_limits_v2"),
        ]

        for sql, name in sequence_updates:
            try:
                cursor.execute(sql)
                conn.commit()
                print(f"   ✅ Updated sequence for {name}")
            except Exception as e:
                print(f"   ⚠️  Could not update sequence for {name}: {e}")

    finally:
        cursor.close()
        conn.close()

    return stats


def verify_import():
    """Verify the imported data"""
    print("\n🔍 Verifying imported data...")

    try:
        conn = get_postgres_connection()
        cursor = conn.cursor()

        # Check record counts
        tables = ['invoices', 'invoice_items', 'platform_users', 'spending_limits', 'spending_limits_v2']

        print("\n📊 Record counts in Supabase:")
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"   • {table}: {count}")

        # Check for orphaned records
        cursor.execute("""
            SELECT COUNT(*)
            FROM invoice_items ii
            WHERE NOT EXISTS (
                SELECT 1 FROM invoices i WHERE i.id = ii.invoice_id
            )
        """)
        orphaned = cursor.fetchone()[0]
        if orphaned > 0:
            print(f"\n⚠️  Warning: Found {orphaned} orphaned invoice items")
        else:
            print("\n✅ No orphaned records found")

        # Check data integrity
        cursor.execute("""
            SELECT
                SUM(total_amount) as total_spent,
                COUNT(*) as invoice_count
            FROM invoices
        """)
        result = cursor.fetchone()
        total_spent = result[0] if result[0] else 0
        invoice_count = result[1]

        print(f"\n💰 Data summary:")
        print(f"   • Total invoices: {invoice_count}")
        print(f"   • Total amount: Rp {total_spent:,.2f}")

        cursor.close()
        conn.close()

        return True

    except Exception as e:
        print(f"❌ Verification error: {e}")
        return False


def main(export_file, method='auto'):
    """Main import function"""
    print("=" * 70)
    print("🚀 Supabase Data Import Tool")
    print("=" * 70)

    # Check if export file exists
    if not os.path.exists(export_file):
        print(f"❌ Error: Export file not found: {export_file}")
        sys.exit(1)

    print(f"📁 Import file: {export_file}")

    # Load export data
    print("📂 Loading export data...")
    with open(export_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    total_records = sum(len(records) for records in data.values() if isinstance(records, list))
    print(f"✅ Loaded {total_records} total records from {len(data)} tables")

    # Choose import method
    if method == 'auto':
        method = 'postgres' if PSYCOPG2_AVAILABLE else 'supabase'

    print(f"🔧 Import method: {method}")

    # Perform import
    start_time = datetime.now()

    try:
        if method == 'postgres':
            stats = import_with_postgres_direct(data)
        else:
            stats = import_with_supabase_client(data)

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        print("\n" + "=" * 70)
        print("✅ Import completed!")
        print("=" * 70)
        print(f"⏱️  Duration: {duration:.2f} seconds")
        print(f"✅ Success: {stats['success']} records")
        if stats['errors'] > 0:
            print(f"❌ Errors: {stats['errors']} records")
        print("=" * 70)

        # Verify import
        verify_import()

        print("\n🎉 Migration completed successfully!")
        print("📋 Next steps:")
        print("   1. Update your .env file with Supabase credentials")
        print("   2. Update imports in your code to use database_supabase.py")
        print("   3. Test your application thoroughly")
        print("   4. Keep the SQLite backup for rollback if needed")

    except Exception as e:
        print(f"\n❌ Import failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python import_to_supabase.py <export_file.json> [method]")
        print("Methods: auto (default), postgres, supabase")
        print("\nExample:")
        print("  python import_to_supabase.py migration/sqlite_export_20240101_120000.json")
        sys.exit(1)

    export_file = sys.argv[1]
    method = sys.argv[2] if len(sys.argv) > 2 else 'auto'

    main(export_file, method)
