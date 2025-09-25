import sqlite3
import os
from typing import Optional, Dict, Any
from src.analysis import analyze_invoices

def get_db_path():
    """Get the database path"""
    current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(current_dir, 'invoices.db')

def init_spending_limits_table():
    """Initialize the spending limits table in the database."""
    conn = sqlite3.connect(get_db_path())
    try:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS spending_limits (
                user_id INTEGER PRIMARY KEY,
                monthly_limit REAL NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
    finally:
        conn.close()

def set_monthly_limit(user_id: int, limit_amount: float) -> bool:
    """Set or update monthly spending limit for a user."""
    conn = sqlite3.connect(get_db_path())
    try:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO spending_limits (user_id, monthly_limit, updated_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(user_id) DO UPDATE SET
                monthly_limit = excluded.monthly_limit,
                updated_at = CURRENT_TIMESTAMP
        ''', (user_id, limit_amount))
        conn.commit()
        return True
    except Exception:
        return False
    finally:
        conn.close()

def get_monthly_limit(user_id: int) -> Optional[float]:
    """Get the monthly spending limit for a user."""
    conn = sqlite3.connect(get_db_path())
    try:
        cursor = conn.cursor()
        cursor.execute('SELECT monthly_limit FROM spending_limits WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        return result[0] if result else None
    finally:
        conn.close()

def get_current_month_spending(user_id: int) -> float:
    """Get the total spending using the same calculation as view_summary."""
    try:
        analysis = analyze_invoices()
        return float(analysis['total_spent'])
    except Exception:
        return 0.0

def check_spending_limit(user_id: int, new_amount: float = 0) -> Dict[str, Any]:
    """Check if a new transaction would exceed the monthly spending limit."""
    monthly_limit = get_monthly_limit(user_id)
    if not monthly_limit:
        return {
            'has_limit': False,
            'message': 'No spending limit set. Use /set_limit to set one.'
        }

    current_spending = get_current_month_spending(user_id)
    # For new invoices being processed, add the new amount
    # For checking current status, new_amount will be 0
    total_with_new = current_spending + new_amount if new_amount > 0 else current_spending
    
    remaining = monthly_limit - current_spending
    percentage_used = (current_spending / monthly_limit) * 100  # Calculate percentage based on current spending

    message = (
        f"💰 Monthly Spending Status:\n\n"
        f"Monthly Limit: Rp {monthly_limit:,.2f}\n"
        f"Total Spent: Rp {current_spending:,.2f}\n"
    )

    if new_amount > 0:
        message += (
            f"\nAfter this transaction:\n"
            f"New Total: Rp {total_with_new:,.2f}\n"
        )

    message += (
        f"\nRemaining: Rp {remaining:,.2f}\n"
        f"Usage: {percentage_used:.1f}%"
    )

    return {
        'has_limit': True,
        'limit': monthly_limit,
        'current_spending': current_spending,
        'new_total': total_with_new,
        'remaining': remaining,
        'exceeds_limit': total_with_new > monthly_limit,
        'percentage_used': percentage_used,
        'message': message
    }