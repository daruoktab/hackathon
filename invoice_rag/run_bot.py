#!/usr/bin/env python3
import os
import sys
import asyncio

# Add the project root directory to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

from src.telegram.bot import main

if __name__ == '__main__':
    asyncio.run(main())