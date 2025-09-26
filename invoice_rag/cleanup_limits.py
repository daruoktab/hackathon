import sqlite3
import os

def get_db_path():
    """Get the database path"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(current_dir, 'invoices.db')

def cleanup_spending_limits():
    """Clean up spending limits table"""
    conn = sqlite3.connect(get_db_path())
    try:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM spending_limits')
        conn.commit()
        print("✅ Successfully cleaned up spending limits table")
    except Exception as e:
        print(f"❌ Error cleaning up spending limits: {str(e)}")
    finally:
        conn.close()

if __name__ == "__main__":
    cleanup_spending_limits()