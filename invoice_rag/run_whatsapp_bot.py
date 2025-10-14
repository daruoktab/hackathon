#!/usr/bin/env python3
"""
WhatsApp Bot Runner
Script to run the WhatsApp bot server
"""

import os
import sys
import asyncio
import nest_asyncio

# Allow nested event loops
nest_asyncio.apply()

# Add the project root directory to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from whatsapp_bot.bot import main

if __name__ == '__main__':
    try:
        print("🚀 Starting WhatsApp Invoice Bot...")
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 WhatsApp Bot stopped by user")
    except Exception as e:
        print(f"\n❌ Error occurred: {e}")
    finally:
        print("🧹 Cleanup complete. WhatsApp Bot stopped.")