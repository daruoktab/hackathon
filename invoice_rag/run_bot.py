#!/usr/bin/env python3
import os
import sys
import asyncio
import nest_asyncio

# Allow nested event loops
nest_asyncio.apply()

# Add the project root directory to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from telegram_bot.bot import main

if __name__ == '__main__':
    asyncio.run(main())