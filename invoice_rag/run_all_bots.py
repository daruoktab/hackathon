#!/usr/bin/env python3
"""
Unified Bot Runner
Script to run both Telegram and WhatsApp bots simultaneously
"""

import os
import sys
import asyncio
import nest_asyncio
from multiprocessing import Process

# Allow nested event loops
nest_asyncio.apply()

# Add the project root directory to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def run_telegram_bot():
    """Run the Telegram bot in a separate process."""
    try:
        from telegram_bot.bot import main as telegram_main
        print("🤖 Starting Telegram Bot...")
        asyncio.run(telegram_main())
    except Exception as e:
        print(f"❌ Telegram Bot error: {e}")


def run_whatsapp_bot():
    """Run the WhatsApp bot in a separate process."""
    try:
        from whatsapp_bot.bot import main as whatsapp_main
        print("📱 Starting WhatsApp Bot...")
        asyncio.run(whatsapp_main())
    except Exception as e:
        print(f"❌ WhatsApp Bot error: {e}")


def main():
    """Main function to coordinate both bots."""
    print("🚀 Starting Invoice Helper Bot System...")
    
    # Check which bots are enabled
    enable_telegram = os.getenv("ENABLE_TELEGRAM_BOT", "true").lower() == "true"
    enable_whatsapp = os.getenv("ENABLE_WHATSAPP_BOT", "true").lower() == "true"
    
    processes = []
    
    try:
        # Start Telegram bot if enabled
        if enable_telegram:
            telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
            if telegram_token:
                telegram_process = Process(target=run_telegram_bot, name="TelegramBot")
                telegram_process.start()
                processes.append(telegram_process)
                print("✅ Telegram Bot process started")
            else:
                print("⚠️ Telegram bot disabled: No TELEGRAM_BOT_TOKEN found")
        else:
            print("⚠️ Telegram bot disabled in configuration")
        
        # Start WhatsApp bot if enabled
        if enable_whatsapp:
            waha_url = os.getenv("WAHA_URL")
            if waha_url:
                whatsapp_process = Process(target=run_whatsapp_bot, name="WhatsAppBot")
                whatsapp_process.start()
                processes.append(whatsapp_process)
                print("✅ WhatsApp Bot process started")
            else:
                print("⚠️ WhatsApp bot disabled: No WAHA_URL found")
        else:
            print("⚠️ WhatsApp bot disabled in configuration")
        
        if not processes:
            print("❌ No bots enabled or configured. Please check your .env file.")
            return
        
        print(f"🎉 {len(processes)} bot(s) running successfully!")
        print("Press Ctrl+C to stop all bots")
        
        # Wait for all processes
        for process in processes:
            process.join()
            
    except KeyboardInterrupt:
        print("\n🛑 Stopping all bots...")
        
        # Terminate all processes
        for process in processes:
            if process.is_alive():
                process.terminate()
                process.join(timeout=5)
                if process.is_alive():
                    print(f"⚠️ Force killing {process.name}")
                    process.kill()
                else:
                    print(f"✅ {process.name} stopped gracefully")
        
        print("🧹 All bots stopped.")
        
    except Exception as e:
        print(f"❌ Error in main process: {e}")
        
        # Clean up processes on error
        for process in processes:
            if process.is_alive():
                process.terminate()


if __name__ == '__main__':
    main()