"""
Quick bot startup script with pre-flight checks
"""
import os
import sys
import subprocess
from pathlib import Path

def check_environment():
    """Check if environment is properly set up."""
    print("🔍 Checking environment...")
    
    # Check if .env file exists
    if not Path(".env").exists():
        print("❌ .env file not found!")
        print("Please create a .env file with your TELEGRAM_BOT_TOKEN")
        return False
    
    # Load and check token
    from dotenv import load_dotenv
    load_dotenv()
    
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        print("❌ TELEGRAM_BOT_TOKEN not found in .env file!")
        return False
    
    print(f"✓ Bot token found: {token[:10]}...{token[-5:]}")
    return True

def run_connection_test():
    """Run the connection test."""
    print("\n🔌 Testing connection to Telegram...")
    
    try:
        result = subprocess.run(
            [sys.executable, "test_bot_connection.py"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            print("✅ Connection test passed!")
            return True
        else:
            print("❌ Connection test failed!")
            print(result.stdout)
            print(result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        print("⏱️ Connection test timed out")
        return False
    except Exception as e:
        print(f"❌ Error running connection test: {e}")
        return False

def start_bot():
    """Start the bot."""
    print("\n🚀 Starting Telegram bot...")
    print("Press Ctrl+C to stop the bot\n")
    print("=" * 60)
    
    try:
        subprocess.run([sys.executable, "telegram_bot/bot.py"])
    except KeyboardInterrupt:
        print("\n\n👋 Bot stopped by user")
    except Exception as e:
        print(f"\n❌ Error starting bot: {e}")

def main():
    """Main function."""
    print("=" * 60)
    print("Telegram Invoice Bot - Startup Script")
    print("=" * 60)
    print()
    
    # Step 1: Check environment
    if not check_environment():
        print("\n❌ Environment check failed. Please fix the issues above.")
        input("Press Enter to exit...")
        return
    
    # Step 2: Run connection test
    print()
    response = input("Run connection test? (Y/n): ").strip().lower()
    if response != 'n':
        if not run_connection_test():
            response = input("\nConnection test failed. Continue anyway? (y/N): ").strip().lower()
            if response != 'y':
                print("Startup cancelled.")
                return
    
    # Step 3: Start the bot
    start_bot()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        input("Press Enter to exit...")
