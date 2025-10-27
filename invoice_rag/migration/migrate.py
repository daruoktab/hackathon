#!/usr/bin/env python3
"""
Supabase Migration Helper Script
Interactive menu to guide through the migration process
"""
import os
import sys
import subprocess
from pathlib import Path

def print_header(text):
    """Print a formatted header"""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70 + "\n")

def print_step(number, text):
    """Print a formatted step"""
    print(f"\n{'='*70}")
    print(f"📍 Step {number}: {text}")
    print('='*70)

def check_env_file():
    """Check if .env file exists and has Supabase credentials"""
    env_path = Path(__file__).parent.parent / '.env'

    if not env_path.exists():
        print("❌ .env file not found!")
        print(f"   Expected location: {env_path}")
        return False

    with open(env_path, 'r') as f:
        content = f.read()
        has_supabase = 'SUPABASE_URL' in content and 'SUPABASE_DB_HOST' in content

    if not has_supabase:
        print("⚠️  .env file exists but missing Supabase credentials")
        return False

    print("✅ .env file found with Supabase credentials")
    return True

def check_dependencies():
    """Check if required packages are installed"""
    print("\n🔍 Checking dependencies...")

    missing = []
    packages = ['supabase', 'psycopg2', 'sqlalchemy', 'dotenv']

    for package in packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"   ✅ {package}")
        except ImportError:
            print(f"   ❌ {package}")
            missing.append(package)

    if missing:
        print(f"\n❌ Missing packages: {', '.join(missing)}")
        print("   Install with: pip install supabase psycopg2-binary python-dotenv")
        return False

    print("\n✅ All dependencies installed")
    return True

def run_command(command, description):
    """Run a shell command and return success status"""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            capture_output=True,
            text=True
        )
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e.stderr}")
        return False

def show_menu():
    """Display the main menu"""
    print_header("🚀 Supabase Migration Helper")
    print("Choose an option:")
    print()
    print("  1. Pre-flight Check (Check dependencies and configuration)")
    print("  2. Export SQLite Data")
    print("  3. Import to Supabase")
    print("  4. Run Full Migration (Steps 2 + 3)")
    print("  5. Verify Migration")
    print("  6. View Migration Guide")
    print("  7. Setup Environment (.env)")
    print()
    print("  0. Exit")
    print()

def pre_flight_check():
    """Run pre-flight checks"""
    print_step(1, "Pre-flight Check")

    all_good = True

    # Check SQLite database exists
    db_path = Path(__file__).parent.parent / 'invoices.db'
    if db_path.exists():
        print(f"✅ SQLite database found: {db_path}")

        # Get record count
        try:
            import sqlite3
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM invoices")
            count = cursor.fetchone()[0]
            print(f"   📊 Contains {count} invoices")
            conn.close()
        except Exception as e:
            print(f"   ⚠️  Could not read database: {e}")
    else:
        print(f"❌ SQLite database not found: {db_path}")
        all_good = False

    # Check dependencies
    if not check_dependencies():
        all_good = False

    # Check .env file
    if not check_env_file():
        all_good = False

    # Check migration scripts exist
    migration_dir = Path(__file__).parent
    scripts = ['export_sqlite_data.py', 'import_to_supabase.py', 'create_schema.sql']

    print("\n🔍 Checking migration scripts...")
    for script in scripts:
        script_path = migration_dir / script
        if script_path.exists():
            print(f"   ✅ {script}")
        else:
            print(f"   ❌ {script}")
            all_good = False

    print("\n" + "="*70)
    if all_good:
        print("✅ Pre-flight check passed! Ready for migration.")
    else:
        print("❌ Pre-flight check failed. Please fix the issues above.")
    print("="*70)

    return all_good

def export_sqlite():
    """Export SQLite data"""
    print_step(2, "Export SQLite Data")

    script_path = Path(__file__).parent / 'export_sqlite_data.py'

    if not script_path.exists():
        print(f"❌ Export script not found: {script_path}")
        return False

    print("📦 Starting SQLite data export...")
    print()

    success = run_command(
        f'python "{script_path}"',
        "Exporting data"
    )

    if success:
        # Find the most recent export file
        export_files = sorted(Path(__file__).parent.glob('sqlite_export_*.json'))
        if export_files:
            latest = export_files[-1]
            print(f"\n✅ Export completed: {latest.name}")
            return str(latest)

    return False

def import_to_supabase(export_file=None):
    """Import data to Supabase"""
    print_step(3, "Import to Supabase")

    script_path = Path(__file__).parent / 'import_to_supabase.py'

    if not script_path.exists():
        print(f"❌ Import script not found: {script_path}")
        return False

    # Find export file if not provided
    if not export_file:
        export_files = sorted(Path(__file__).parent.glob('sqlite_export_*.json'))
        if not export_files:
            print("❌ No export file found. Run export first.")
            return False
        export_file = str(export_files[-1])
        print(f"📁 Using export file: {Path(export_file).name}")

    print("\n⚠️  IMPORTANT: Before importing, make sure you have:")
    print("   1. Created the schema in Supabase (run create_schema.sql)")
    print("   2. Set up .env with Supabase credentials")
    print()

    response = input("Continue with import? (y/n): ")
    if response.lower() != 'y':
        print("❌ Import cancelled")
        return False

    print("\n📡 Starting Supabase import...")
    print()

    success = run_command(
        f'python "{script_path}" "{export_file}"',
        "Importing data"
    )

    return success

def verify_migration():
    """Verify migration was successful"""
    print_step(4, "Verify Migration")

    try:
        from dotenv import load_dotenv
        import psycopg2

        load_dotenv()

        # Connect to Supabase
        conn = psycopg2.connect(
            host=os.environ.get("SUPABASE_DB_HOST"),
            port=os.environ.get("SUPABASE_DB_PORT", "5432"),
            database=os.environ.get("SUPABASE_DB_NAME", "postgres"),
            user=os.environ.get("SUPABASE_DB_USER", "postgres"),
            password=os.environ.get("SUPABASE_DB_PASSWORD")
        )

        cursor = conn.cursor()

        print("📊 Checking record counts in Supabase:\n")

        tables = ['invoices', 'invoice_items', 'platform_users', 'spending_limits', 'spending_limits_v2']

        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"   • {table:25} {count:6} records")

        # Check for orphaned records
        cursor.execute("""
            SELECT COUNT(*)
            FROM invoice_items ii
            WHERE NOT EXISTS (
                SELECT 1 FROM invoices i WHERE i.id = ii.invoice_id
            )
        """)
        orphaned = cursor.fetchone()[0]

        print()
        if orphaned > 0:
            print(f"⚠️  Warning: Found {orphaned} orphaned invoice items")
        else:
            print("✅ No orphaned records found")

        # Check total amount
        cursor.execute("SELECT SUM(total_amount), COUNT(*) FROM invoices")
        result = cursor.fetchone()
        total_amount = result[0] if result[0] else 0
        invoice_count = result[1]

        print(f"\n💰 Data Summary:")
        print(f"   • Total invoices: {invoice_count}")
        print(f"   • Total amount: Rp {total_amount:,.2f}")

        cursor.close()
        conn.close()

        print("\n✅ Verification completed successfully!")
        return True

    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return False

def view_guide():
    """Open the migration guide"""
    print_step(5, "View Migration Guide")

    guide_path = Path(__file__).parent.parent.parent / 'SUPABASE_MIGRATION_GUIDE.md'

    if guide_path.exists():
        print(f"📖 Migration guide: {guide_path}")
        print("\nOpening guide in your default markdown viewer...")

        try:
            if sys.platform == 'win32':
                os.startfile(guide_path)
            elif sys.platform == 'darwin':
                subprocess.run(['open', guide_path])
            else:
                subprocess.run(['xdg-open', guide_path])
        except Exception as e:
            print(f"⚠️  Could not open guide: {e}")
            print(f"   Please open manually: {guide_path}")
    else:
        print(f"❌ Guide not found: {guide_path}")

def setup_environment():
    """Help setup .env file"""
    print_step(6, "Setup Environment")

    env_path = Path(__file__).parent.parent / '.env'
    example_path = Path(__file__).parent / '.env.supabase.example'

    print("🔧 Environment Setup")
    print()

    if env_path.exists():
        print(f"⚠️  .env file already exists: {env_path}")
        response = input("Do you want to view/edit it? (y/n): ")
        if response.lower() == 'y':
            try:
                if sys.platform == 'win32':
                    os.startfile(env_path)
                else:
                    print(f"\nPlease edit: {env_path}")
            except Exception as e:
                print(f"Error: {e}")
        return

    print("📝 Creating .env file from template...")

    if example_path.exists():
        import shutil
        shutil.copy(example_path, env_path)
        print(f"✅ Created: {env_path}")
        print()
        print("📋 Next steps:")
        print("   1. Get your Supabase credentials from:")
        print("      https://app.supabase.com/project/YOUR_PROJECT/settings/api")
        print("   2. Open and edit the .env file")
        print("   3. Add your SUPABASE_URL, SUPABASE_SERVICE_KEY, etc.")
        print()

        response = input("Open .env file now? (y/n): ")
        if response.lower() == 'y':
            try:
                if sys.platform == 'win32':
                    os.startfile(env_path)
                else:
                    print(f"\nPlease edit: {env_path}")
            except Exception as e:
                print(f"Error: {e}")
    else:
        print(f"❌ Template not found: {example_path}")

def full_migration():
    """Run full migration process"""
    print_header("🚀 Full Migration Process")

    print("This will:")
    print("  1. Export data from SQLite")
    print("  2. Import data to Supabase")
    print("  3. Verify the migration")
    print()

    response = input("Continue? (y/n): ")
    if response.lower() != 'y':
        print("❌ Migration cancelled")
        return

    # Pre-flight check
    if not pre_flight_check():
        print("\n❌ Pre-flight check failed. Please fix issues first.")
        return

    # Export
    export_file = export_sqlite()
    if not export_file:
        print("\n❌ Export failed. Migration stopped.")
        return

    # Import
    if not import_to_supabase(export_file):
        print("\n❌ Import failed. Migration stopped.")
        return

    # Verify
    verify_migration()

    print("\n" + "="*70)
    print("🎉 Migration completed!")
    print("="*70)
    print("\n📋 Next steps:")
    print("   1. Update your code to use database_supabase.py")
    print("   2. Test your application thoroughly")
    print("   3. Keep SQLite backup for rollback if needed")
    print()

def main():
    """Main function"""
    while True:
        show_menu()

        try:
            choice = input("Enter your choice (0-7): ").strip()

            if choice == '0':
                print("\n👋 Goodbye!")
                break
            elif choice == '1':
                pre_flight_check()
            elif choice == '2':
                export_sqlite()
            elif choice == '3':
                import_to_supabase()
            elif choice == '4':
                full_migration()
            elif choice == '5':
                verify_migration()
            elif choice == '6':
                view_guide()
            elif choice == '7':
                setup_environment()
            else:
                print("❌ Invalid choice. Please enter 0-7.")

            input("\nPress Enter to continue...")

        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
            input("\nPress Enter to continue...")

if __name__ == '__main__':
    main()
