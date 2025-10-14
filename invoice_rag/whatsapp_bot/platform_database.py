#!/usr/bin/env python3
"""
Multi-Platform Database Adapter
Handles database operations for both Telegram and WhatsApp platforms
"""

import sqlite3
import os
from typing import Optional, Dict, Any
from src.analysis import analyze_invoices


def get_db_path():
    """Get the database path"""
    current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(current_dir, 'invoices.db')


def init_platform_tables():
    """Initialize platform-specific tables in the database."""
    conn = sqlite3.connect(get_db_path())
    try:
        cursor = conn.cursor()
        
        # Create platform_users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS platform_users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                platform TEXT NOT NULL,
                platform_user_id TEXT NOT NULL,
                display_name TEXT,
                phone_number TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(platform, platform_user_id)
            )
        ''')
        
        # Create enhanced spending_limits table if not exists
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS spending_limits_v2 (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                monthly_limit REAL NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES platform_users(id)
            )
        ''')
        
        # Migration: Check if old spending_limits table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='spending_limits'")
        old_table_exists = cursor.fetchone() is not None
        
        if old_table_exists:
            # Migrate old Telegram data to new structure
            cursor.execute("SELECT user_id, monthly_limit, created_at, updated_at FROM spending_limits")
            old_limits = cursor.fetchall()
            
            for old_limit in old_limits:
                telegram_user_id, limit, created, updated = old_limit
                
                # Insert into platform_users if not exists
                cursor.execute('''
                    INSERT OR IGNORE INTO platform_users (platform, platform_user_id, display_name)
                    VALUES (?, ?, ?)
                ''', ('telegram', str(telegram_user_id), f'Telegram User {telegram_user_id}'))
                
                # Get the platform user ID
                cursor.execute('''
                    SELECT id FROM platform_users 
                    WHERE platform = ? AND platform_user_id = ?
                ''', ('telegram', str(telegram_user_id)))
                
                platform_user_result = cursor.fetchone()
                if platform_user_result:
                    platform_user_id = platform_user_result[0]
                    
                    # Insert into new spending_limits table
                    cursor.execute('''
                        INSERT OR IGNORE INTO spending_limits_v2 (user_id, monthly_limit, created_at, updated_at)
                        VALUES (?, ?, ?, ?)
                    ''', (platform_user_id, limit, created, updated))
        
        conn.commit()
        print("Platform tables initialized successfully")
        
    except Exception as e:
        print(f"Error initializing platform tables: {e}")
    finally:
        conn.close()


def get_or_create_platform_user(platform: str, platform_user_id: str, 
                               display_name: str | None = None, phone_number: str | None = None) -> Optional[int]:
    """Get or create a platform user and return their internal user ID."""
    conn = sqlite3.connect(get_db_path())
    try:
        cursor = conn.cursor()
        
        # Try to get existing user
        cursor.execute('''
            SELECT id FROM platform_users 
            WHERE platform = ? AND platform_user_id = ?
        ''', (platform, platform_user_id))
        
        result = cursor.fetchone()
        if result:
            # Update last_active
            cursor.execute('''
                UPDATE platform_users 
                SET last_active = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (result[0],))
            conn.commit()
            return result[0]
        
        # Create new user
        cursor.execute('''
            INSERT INTO platform_users (platform, platform_user_id, display_name, phone_number)
            VALUES (?, ?, ?, ?)
        ''', (platform, platform_user_id, display_name, phone_number))
        
        conn.commit()
        return cursor.lastrowid
        
    except Exception as e:
        print(f"Error getting/creating platform user: {e}")
        return None
    finally:
        conn.close()


def set_monthly_limit_platform(platform: str, platform_user_id: str, limit_amount: float) -> bool:
    """Set or update monthly spending limit for a platform user."""
    user_id = get_or_create_platform_user(platform, platform_user_id)
    if not user_id:
        return False
    
    conn = sqlite3.connect(get_db_path())
    try:
        cursor = conn.cursor()
        
        # Check if limit already exists
        cursor.execute('''
            SELECT id FROM spending_limits_v2 WHERE user_id = ?
        ''', (user_id,))
        
        if cursor.fetchone():
            # Update existing limit
            cursor.execute('''
                UPDATE spending_limits_v2 
                SET monthly_limit = ?, updated_at = CURRENT_TIMESTAMP
                WHERE user_id = ?
            ''', (limit_amount, user_id))
        else:
            # Insert new limit
            cursor.execute('''
                INSERT INTO spending_limits_v2 (user_id, monthly_limit)
                VALUES (?, ?)
            ''', (user_id, limit_amount))
        
        conn.commit()
        return True
        
    except Exception as e:
        print(f"Error setting monthly limit: {e}")
        return False
    finally:
        conn.close()


def get_monthly_limit_platform(platform: str, platform_user_id: str) -> Optional[float]:
    """Get the monthly spending limit for a platform user."""
    user_id = get_or_create_platform_user(platform, platform_user_id)
    if not user_id:
        return None
    
    conn = sqlite3.connect(get_db_path())
    try:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT monthly_limit FROM spending_limits_v2 WHERE user_id = ?
        ''', (user_id,))
        
        result = cursor.fetchone()
        return result[0] if result else None
        
    except Exception as e:
        print(f"Error getting monthly limit: {e}")
        return None
    finally:
        conn.close()


def check_spending_limit_platform(platform: str, platform_user_id: str, new_amount: float = 0) -> Dict[str, Any]:
    """Check if a new transaction would exceed the monthly spending limit."""
    monthly_limit = get_monthly_limit_platform(platform, platform_user_id)
    
    if not monthly_limit:
        return {
            'has_limit': False,
            'exceeds_limit': False,
            'message': 'No spending limit set',
            'percentage_used': 0,
            'remaining': 0
        }
    
    # Get current spending using existing analysis function
    try:
        analysis = analyze_invoices()
        current_spending = analysis['total_spent']
        total_with_new = current_spending + new_amount
        
        exceeds_limit = total_with_new > monthly_limit
        percentage_used = (total_with_new / monthly_limit) * 100
        remaining = monthly_limit - total_with_new
        
        if exceeds_limit:
            message = f"⚠️ OVER LIMIT!\nSpent: Rp {total_with_new:,.2f}\nLimit: Rp {monthly_limit:,.2f}\nOver by: Rp {total_with_new - monthly_limit:,.2f}"
        else:
            message = f"💰 Spending Status\nSpent: Rp {total_with_new:,.2f}\nLimit: Rp {monthly_limit:,.2f}\nRemaining: Rp {remaining:,.2f} ({100 - percentage_used:.1f}%)"
        
        return {
            'has_limit': True,
            'exceeds_limit': exceeds_limit,
            'message': message,
            'percentage_used': percentage_used,
            'remaining': remaining,
            'current_spending': current_spending,
            'new_total': total_with_new
        }
        
    except Exception as e:
        print(f"Error checking spending limit: {e}")
        return {
            'has_limit': True,
            'exceeds_limit': False,
            'message': 'Error calculating spending',
            'percentage_used': 0,
            'remaining': monthly_limit
        }


def get_platform_user_info(platform: str, platform_user_id: str) -> Optional[Dict[str, Any]]:
    """Get platform user information."""
    conn = sqlite3.connect(get_db_path())
    try:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, platform, platform_user_id, display_name, phone_number, created_at, last_active
            FROM platform_users 
            WHERE platform = ? AND platform_user_id = ?
        ''', (platform, platform_user_id))
        
        result = cursor.fetchone()
        if result:
            return {
                'id': result[0],
                'platform': result[1],
                'platform_user_id': result[2],
                'display_name': result[3],
                'phone_number': result[4],
                'created_at': result[5],
                'last_active': result[6]
            }
        return None
        
    except Exception as e:
        print(f"Error getting platform user info: {e}")
        return None
    finally:
        conn.close()


# Legacy functions for backwards compatibility with Telegram bot
def set_monthly_limit(user_id: int, limit_amount: float) -> bool:
    """Legacy function for Telegram bot compatibility."""
    return set_monthly_limit_platform('telegram', str(user_id), limit_amount)


def get_monthly_limit(user_id: int) -> Optional[float]:
    """Legacy function for Telegram bot compatibility."""
    return get_monthly_limit_platform('telegram', str(user_id))


def check_spending_limit(user_id: int, new_amount: float = 0) -> Dict[str, Any]:
    """Legacy function for Telegram bot compatibility."""
    return check_spending_limit_platform('telegram', str(user_id), new_amount)