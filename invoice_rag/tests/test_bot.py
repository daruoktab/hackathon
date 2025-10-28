"""
Test script to verify Telegram bot connection and network connectivity.
"""
import asyncio
import os
from dotenv import load_dotenv
from telegram import Bot
from telegram.error import TelegramError, NetworkError

# Load environment variables
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

async def test_connection():
    """Test the bot connection to Telegram servers."""
    print("=" * 60)
    print("Telegram Bot Connection Test")
    print("=" * 60)
    
    if not TOKEN:
        print("❌ ERROR: TELEGRAM_BOT_TOKEN not found in environment variables")
        print("Please check your .env file")
        return False
    
    print(f"✓ Token found: {TOKEN[:10]}...{TOKEN[-5:]}")
    print("\nTesting connection to Telegram servers...")
    
    try:
        # Create bot instance with custom timeout settings
        bot = Bot(
            token=TOKEN,
            request=None  # Use default request with custom timeout
        )
        
        # Try to get bot info
        print("Attempting to fetch bot information...")
        me = await bot.get_me()
        
        print("\n" + "=" * 60)
        print("✅ CONNECTION SUCCESSFUL!")
        print("=" * 60)
        print(f"Bot Name: {me.first_name}")
        print(f"Bot Username: @{me.username}")
        print(f"Bot ID: {me.id}")
        print(f"Can Join Groups: {me.can_join_groups}")
        print(f"Can Read All Group Messages: {me.can_read_all_group_messages}")
        print("=" * 60)
        
        # Close the bot
        await bot.close()
        return True
        
    except NetworkError as e:
        print("\n" + "=" * 60)
        print("❌ NETWORK ERROR")
        print("=" * 60)
        print(f"Error: {e}")
        print("\nPossible causes:")
        print("1. No internet connection")
        print("2. Firewall blocking Telegram API")
        print("3. Proxy configuration needed")
        print("4. Telegram API temporarily unavailable")
        print("\nSuggestions:")
        print("- Check your internet connection")
        print("- Try accessing https://api.telegram.org in your browser")
        print("- If behind a proxy, configure HTTP_PROXY and HTTPS_PROXY environment variables")
        return False
        
    except TelegramError as e:
        print("\n" + "=" * 60)
        print("❌ TELEGRAM API ERROR")
        print("=" * 60)
        print(f"Error: {e}")
        print("\nPossible causes:")
        print("1. Invalid bot token")
        print("2. Bot was deleted by @BotFather")
        print("3. Token has been revoked")
        print("\nSuggestions:")
        print("- Verify your token with @BotFather on Telegram")
        print("- Generate a new token if necessary")
        return False
        
    except Exception as e:
        print("\n" + "=" * 60)
        print("❌ UNEXPECTED ERROR")
        print("=" * 60)
        print(f"Error Type: {type(e).__name__}")
        print(f"Error Message: {e}")
        print("\nPlease check the error details above")
        return False

async def test_api_endpoint():
    """Test if we can reach Telegram API endpoint."""
    print("\nTesting API endpoint reachability...")
    
    try:
        import httpx
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get("https://api.telegram.org")
            print(f"✓ API endpoint reachable (Status: {response.status_code})")
            return True
    except Exception as e:
        print(f"❌ Cannot reach API endpoint: {e}")
        return False

async def main():
    """Run all connection tests."""
    # Test API endpoint first
    api_reachable = await test_api_endpoint()
    
    if not api_reachable:
        print("\n⚠️  WARNING: Cannot reach Telegram API endpoint")
        print("The bot will not work without internet connectivity to api.telegram.org")
        return
    
    # Test bot connection
    success = await test_connection()
    
    if success:
        print("\n🎉 All tests passed! Your bot is ready to run.")
        print("You can now start the bot with: python telegram_bot/bot.py")
    else:
        print("\n⚠️  Connection test failed. Please resolve the issues above.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    except Exception as e:
        print(f"\n❌ Test script error: {e}")
