#!/usr/bin/env python3
"""
SQLite Database Backup Script
Creates timestamped backups of invoices.db
"""
import shutil
import os
from datetime import datetime
from pathlib import Path

def backup_database():
    """Create a timestamped backup of the database"""
    
    # Database file
    db_file = Path('database') / 'invoices.db'
    
    if not db_file.exists():
        print("❌ Database file 'database/invoices.db' not found")
        return False
    
    # Create backups directory
    backup_dir = Path('backups')
    backup_dir.mkdir(exist_ok=True)
    
    # Create timestamped backup filename
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = backup_dir / f'invoices_{timestamp}.db'
    
    try:
        # Copy database
        shutil.copy2(db_file, backup_file)
        
        # Get file sizes
        original_size = db_file.stat().st_size / 1024  # KB
        backup_size = backup_file.stat().st_size / 1024  # KB
        
        print("=" * 70)
        print("✅ DATABASE BACKUP SUCCESSFUL!")
        print("=" * 70)
        print(f"📁 Original: {db_file}")
        print(f"   Size: {original_size:.2f} KB")
        print(f"\n💾 Backup: {backup_file}")
        print(f"   Size: {backup_size:.2f} KB")
        print(f"   Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)
        
        # List all backups
        backups = sorted(backup_dir.glob('invoices_*.db'))
        if len(backups) > 1:
            print(f"\n📚 Total backups: {len(backups)}")
            print("   Recent backups:")
            for backup in backups[-5:]:  # Show last 5
                size = backup.stat().st_size / 1024
                print(f"   - {backup.name} ({size:.2f} KB)")
        
        return True
    
    except Exception as e:
        print(f"❌ Backup failed: {e}")
        return False

if __name__ == "__main__":
    print("\n🔄 Starting database backup...")
    success = backup_database()
    
    if success:
        print("\n💡 Tip: Run this script regularly to keep backups!")
        print("   Schedule it: Task Scheduler (Windows) or cron (Linux)")
    else:
        print("\n❌ Backup failed. Check error message above.")
