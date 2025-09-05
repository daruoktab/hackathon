#!/usr/bin/env python3
"""
Database Backup - Create backup of invoice database
"""

import os
import shutil
from datetime import datetime

def backup_database():
    """Create a timestamped backup of the database."""
    
    print("DATABASE BACKUP TOOL")
    print("=" * 50)
    
    # Check if database exists
    db_path = '../invoices.db'
    if not os.path.exists(db_path):
        print(f"Database not found: {db_path}")
        return
    
    # Get database size
    size = os.path.getsize(db_path)
    print(f"Found database: {db_path} ({size} bytes)")
    
    # Create backup filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"invoices_backup_{timestamp}.db"
    backup_path = f"../{backup_name}"
    
    try:
        # Create backup
        print(f"\nCreating backup...")
        shutil.copy2(db_path, backup_path)
        
        # Verify backup
        backup_size = os.path.getsize(backup_path)
        print(f"Backup created: {backup_path}")
        print(f"Backup size: {backup_size} bytes")
        
        if backup_size == size:
            print("✅ Backup created successfully!")
        else:
            print("⚠️ Warning: Backup size doesn't match original")
            
    except Exception as e:
        print(f"❌ Error creating backup: {e}")

def list_backups():
    """List all existing backups."""
    
    print("\nEXISTING BACKUPS:")
    print("-" * 30)
    
    backup_dir = ".."
    backups = []
    
    for file in os.listdir(backup_dir):
        if file.startswith("invoices_backup_") and file.endswith(".db"):
            path = os.path.join(backup_dir, file)
            size = os.path.getsize(path)
            modified = datetime.fromtimestamp(os.path.getmtime(path))
            backups.append((file, size, modified))
    
    if backups:
        backups.sort(key=lambda x: x[2], reverse=True)  # Sort by date, newest first
        for name, size, date in backups:
            print(f"- {name} ({size} bytes) - {date.strftime('%Y-%m-%d %H:%M:%S')}")
    else:
        print("No backups found")

def restore_backup():
    """Restore database from backup."""
    
    print("\nRESTORE FROM BACKUP")
    print("-" * 30)
    
    # List available backups
    backup_dir = ".."
    backups = []
    
    for file in os.listdir(backup_dir):
        if file.startswith("invoices_backup_") and file.endswith(".db"):
            backups.append(file)
    
    if not backups:
        print("No backups found to restore from")
        return
    
    backups.sort(reverse=True)  # Newest first
    
    print("Available backups:")
    for i, backup in enumerate(backups, 1):
        path = os.path.join(backup_dir, backup)
        size = os.path.getsize(path)
        modified = datetime.fromtimestamp(os.path.getmtime(path))
        print(f"{i}. {backup} ({size} bytes) - {modified.strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        choice = int(input(f"\nEnter backup number to restore (1-{len(backups)}): "))
        if 1 <= choice <= len(backups):
            selected_backup = backups[choice - 1]
            backup_path = os.path.join(backup_dir, selected_backup)
            
            # Confirm restore
            confirm = input(f"Restore from '{selected_backup}'? This will overwrite current database! (yes/no): ")
            if confirm.lower() == "yes":
                # Create backup of current database first
                current_db = "../invoices.db"
                if os.path.exists(current_db):
                    current_backup = f"../invoices_pre_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
                    shutil.copy2(current_db, current_backup)
                    print(f"Current database backed up to: {current_backup}")
                
                # Restore from backup
                shutil.copy2(backup_path, current_db)
                print(f"✅ Database restored from {selected_backup}")
            else:
                print("Restore cancelled")
        else:
            print("Invalid choice")
    except ValueError:
        print("Invalid input")

def main():
    """Main backup function."""
    
    print("Choose an option:")
    print("1. Create backup")
    print("2. List backups")
    print("3. Restore from backup")
    print("4. Exit")
    
    choice = input("\nEnter your choice (1-4): ").strip()
    
    if choice == "1":
        backup_database()
    elif choice == "2":
        list_backups()
    elif choice == "3":
        restore_backup()
    elif choice == "4":
        print("Exiting...")
    else:
        print("Invalid choice")

if __name__ == "__main__":
    main()
