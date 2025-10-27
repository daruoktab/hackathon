#!/usr/bin/env python3
"""
Supabase Connection Test Script
Tests database connection and basic operations before migration
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Load environment variables
load_dotenv()

def print_header(text):
    """Print formatted header"""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70 + "\n")

def check_environment():
    """Check if required environment variables are set"""
    print_header("🔧 Checking Environment Variables")

    required_vars = [
        "SUPABASE_URL",
        "SUPABASE_SERVICE_KEY",
        "SUPABASE_DB_HOST",
        "SUPABASE_DB_PORT",
        "SUPABASE_DB_NAME",
        "SUPABASE_DB_USER",
        "SUPABASE_DB_PASSWORD"
    ]

    missing = []
    for var in required_vars:
        value = os.environ.get(var)
        if value:
            # Mask sensitive values
            if "KEY" in var or "PASSWORD" in var:
                display = value[:10] + "..." + value[-5:] if len(value) > 15 else "***"
            else:
                display = value
            print(f"✅ {var:25} = {display}")
        else:
            print(f"❌ {var:25} = NOT SET")
            missing.append(var)

    if missing:
        print(f"\n❌ Missing environment variables: {', '.join(missing)}")
        print("   Please set them in your .env file")
        return False

    print("\n✅ All environment variables are set!")
    return True

def test_supabase_client():
    """Test Supabase Python client connection"""
    print_header("📡 Testing Supabase Client Connection")

    try:
        from supabase import create_client, Client

        supabase_url = os.environ.get("SUPABASE_URL")
        supabase_key = os.environ.get("SUPABASE_SERVICE_KEY")

        print("Initializing Supabase client...")
        supabase: Client = create_client(supabase_url, supabase_key)

        print("✅ Supabase client initialized successfully!")

        # Try to query a table (if it exists)
        try:
            print("\nTesting table query...")
            response = supabase.table('invoices').select("id").limit(1).execute()
            print(f"✅ Successfully queried 'invoices' table")
            if response.data:
                print(f"   Sample record ID: {response.data[0]['id']}")
            else:
                print("   ⚠️  Table exists but is empty")
        except Exception as e:
            if "relation" in str(e).lower() or "does not exist" in str(e).lower():
                print("⚠️  'invoices' table doesn't exist yet (run create_schema.sql)")
            else:
                print(f"⚠️  Query failed: {e}")

        return True

    except ImportError:
        print("❌ Supabase client not installed")
        print("   Install with: pip install supabase")
        return False
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

def test_postgres_connection():
    """Test direct PostgreSQL connection"""
    print_header("🐘 Testing PostgreSQL Direct Connection")

    try:
        import psycopg2

        connection_params = {
            'host': os.environ.get("SUPABASE_DB_HOST"),
            'port': os.environ.get("SUPABASE_DB_PORT", "5432"),
            'database': os.environ.get("SUPABASE_DB_NAME", "postgres"),
            'user': os.environ.get("SUPABASE_DB_USER", "postgres"),
            'password': os.environ.get("SUPABASE_DB_PASSWORD")
        }

        print("Connecting to PostgreSQL...")
        conn = psycopg2.connect(**connection_params)
        print("✅ Connection established!")

        # Test query
        cursor = conn.cursor()

        # Get PostgreSQL version
        print("\nGetting database info...")
        cursor.execute("SELECT version()")
        version = cursor.fetchone()[0]
        print(f"✅ PostgreSQL Version: {version.split(',')[0]}")

        # List tables
        cursor.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        tables = cursor.fetchall()

        if tables:
            print(f"\n✅ Found {len(tables)} tables:")
            for table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
                count = cursor.fetchone()[0]
                print(f"   • {table[0]:25} {count:6} records")
        else:
            print("\n⚠️  No tables found (run create_schema.sql first)")

        cursor.close()
        conn.close()

        return True

    except ImportError:
        print("❌ psycopg2 not installed")
        print("   Install with: pip install psycopg2-binary")
        return False
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print("\nPossible issues:")
        print("  • Wrong credentials in .env")
        print("  • Firewall blocking port 5432")
        print("  • Supabase project is paused")
        print("  • Network connection issues")
        return False

def test_sqlalchemy_connection():
    """Test SQLAlchemy ORM connection"""
    print_header("🔗 Testing SQLAlchemy Connection")

    try:
        from sqlalchemy import create_engine, text

        # Build connection string
        user = os.environ.get("SUPABASE_DB_USER", "postgres")
        password = os.environ.get("SUPABASE_DB_PASSWORD")
        host = os.environ.get("SUPABASE_DB_HOST")
        port = os.environ.get("SUPABASE_DB_PORT", "5432")
        database = os.environ.get("SUPABASE_DB_NAME", "postgres")

        connection_string = f"postgresql://{user}:{password}@{host}:{port}/{database}"

        print("Creating SQLAlchemy engine...")
        engine = create_engine(
            connection_string,
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True,
            echo=False
        )

        # Test connection
        print("Testing connection...")
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ SQLAlchemy connection successful!")

            # Test connection pool
            print("\nTesting connection pool...")
            result = conn.execute(text("SELECT current_database(), current_user"))
            row = result.fetchone()
            print(f"✅ Connected to database: {row[0]}")
            print(f"✅ Connected as user: {row[1]}")

            # Check pool status
            print(f"\n📊 Connection Pool Status:")
            print(f"   • Pool size: {engine.pool.size()}")
            print(f"   • Checked out: {engine.pool.checkedout()}")
            print(f"   • Overflow: {engine.pool.overflow()}")

        engine.dispose()
        return True

    except ImportError:
        print("❌ SQLAlchemy not installed")
        print("   Install with: pip install sqlalchemy")
        return False
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

def test_data_operations():
    """Test basic CRUD operations"""
    print_header("🧪 Testing Basic Operations")

    try:
        import psycopg2

        connection_params = {
            'host': os.environ.get("SUPABASE_DB_HOST"),
            'port': os.environ.get("SUPABASE_DB_PORT", "5432"),
            'database': os.environ.get("SUPABASE_DB_NAME", "postgres"),
            'user': os.environ.get("SUPABASE_DB_USER", "postgres"),
            'password': os.environ.get("SUPABASE_DB_PASSWORD")
        }

        conn = psycopg2.connect(**connection_params)
        cursor = conn.cursor()

        # Check if invoices table exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_name = 'invoices'
            )
        """)

        if not cursor.fetchone()[0]:
            print("⚠️  'invoices' table doesn't exist")
            print("   Run create_schema.sql first before testing operations")
            cursor.close()
            conn.close()
            return False

        # Test SELECT
        print("Testing SELECT query...")
        cursor.execute("SELECT COUNT(*) FROM invoices")
        count = cursor.fetchone()[0]
        print(f"✅ SELECT successful: {count} invoices found")

        # Test INSERT (with rollback to not pollute data)
        print("\nTesting INSERT operation (will rollback)...")
        try:
            cursor.execute("""
                INSERT INTO invoices (shop_name, total_amount, invoice_date, transaction_type)
                VALUES ('Test Shop', 100000.00, '2024-01-01', 'retail')
                RETURNING id
            """)
            test_id = cursor.fetchone()[0]
            print(f"✅ INSERT successful: Created test record with ID {test_id}")

            # Rollback to not save the test data
            conn.rollback()
            print("✅ ROLLBACK successful: Test data removed")
        except Exception as e:
            print(f"⚠️  INSERT test failed: {e}")
            conn.rollback()

        cursor.close()
        conn.close()

        print("\n✅ All basic operations working!")
        return True

    except Exception as e:
        print(f"❌ Operations test failed: {e}")
        return False

def main():
    """Run all connection tests"""
    print("\n" + "="*70)
    print("  🚀 SUPABASE CONNECTION TEST SUITE")
    print("="*70)
    print("\nThis script will test your Supabase connection")
    print("before you start the migration process.\n")

    results = {
        'environment': False,
        'supabase_client': False,
        'postgres': False,
        'sqlalchemy': False,
        'operations': False
    }

    # Run tests
    results['environment'] = check_environment()

    if results['environment']:
        results['supabase_client'] = test_supabase_client()
        results['postgres'] = test_postgres_connection()
        results['sqlalchemy'] = test_sqlalchemy_connection()

        # Only test operations if basic connection works
        if results['postgres']:
            results['operations'] = test_data_operations()

    # Summary
    print_header("📊 Test Summary")

    passed = sum(results.values())
    total = len(results)

    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}  {test_name.replace('_', ' ').title()}")

    print(f"\n{'='*70}")
    print(f"Results: {passed}/{total} tests passed")
    print('='*70)

    if passed == total:
        print("\n🎉 All tests passed! You're ready to migrate!")
        print("\nNext steps:")
        print("  1. Run create_schema.sql in Supabase SQL Editor")
        print("  2. Run: python migration/export_sqlite_data.py")
        print("  3. Run: python migration/import_to_supabase.py export.json")
    elif results['environment'] and (results['postgres'] or results['supabase_client']):
        print("\n⚠️  Connection working but some tests failed")
        print("   This is OK if you haven't created the schema yet")
        print("\nNext steps:")
        print("  1. Run create_schema.sql in Supabase SQL Editor")
        print("  2. Run this test again")
    else:
        print("\n❌ Connection tests failed")
        print("   Please check your .env configuration")
        print("\nTroubleshooting:")
        print("  • Verify credentials in Supabase Dashboard")
        print("  • Check if Supabase project is active")
        print("  • Ensure firewall allows port 5432")
        print("  • Review the error messages above")

    print()
    return passed == total

if __name__ == '__main__':
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
