#!/usr/bin/env python3
"""
Startup script for running both the Marimo dashboard server and Telegram bot.
"""

import subprocess
import sys
import time
import os
import signal
from pathlib import Path

def start_marimo_server():
    """Start the Marimo dashboard server."""
    print("🎨 Starting Marimo Dashboard Server...")
    marimo_process = subprocess.Popen(
        [sys.executable, "marimo_server.py"],
        cwd=Path(__file__).parent
    )
    
    # Wait for server to start
    print("⏳ Waiting for Marimo server to initialize...")
    time.sleep(3)
    
    # Check if server is running
    if marimo_process.poll() is not None:
        print("❌ Failed to start Marimo server")
        return None
    
    print("✅ Marimo Dashboard Server started successfully")
    return marimo_process

def start_telegram_bot():
    """Start the Telegram bot."""
    print("🤖 Starting Telegram Bot...")
    bot_process = subprocess.Popen(
        [sys.executable, "run_bot.py"],
        cwd=Path(__file__).parent
    )
    
    # Wait for bot to start
    time.sleep(2)
    
    if bot_process.poll() is not None:
        print("❌ Failed to start Telegram bot")
        return None
    
    print("✅ Telegram Bot started successfully")
    return bot_process

def main():
    """Main function to start all services."""
    print("=" * 60)
    print("  Invoice RAG - Complete System Startup")
    print("=" * 60)
    print()
    
    processes = []
    
    try:
        # Start Marimo server
        marimo_proc = start_marimo_server()
        if marimo_proc:
            processes.append(("Marimo Server", marimo_proc))
        else:
            print("⚠️  Marimo server failed to start, but continuing...")
        
        print()
        
        # Start Telegram bot
        bot_proc = start_telegram_bot()
        if bot_proc:
            processes.append(("Telegram Bot", bot_proc))
        else:
            print("❌ Critical: Telegram bot failed to start")
            # Cleanup and exit
            for name, proc in processes:
                proc.terminate()
            return 1
        
        print()
        print("=" * 60)
        print("✨ All services started successfully!")
        print("=" * 60)
        print()
        print("Services running:")
        for name, _ in processes:
            print(f"  • {name}")
        print()
        print("📊 Marimo Dashboard API: http://127.0.0.1:5001")
        print("🤖 Telegram Bot: Active")
        print()
        print("Press Ctrl+C to stop all services")
        print("=" * 60)
        
        # Wait for interrupt
        while True:
            time.sleep(1)
            # Check if any process died
            for name, proc in processes:
                if proc.poll() is not None:
                    print(f"\n⚠️  {name} stopped unexpectedly!")
                    raise KeyboardInterrupt
    
    except KeyboardInterrupt:
        print("\n")
        print("=" * 60)
        print("🛑 Shutting down all services...")
        print("=" * 60)
        
        for name, proc in processes:
            print(f"  Stopping {name}...")
            proc.terminate()
            try:
                proc.wait(timeout=5)
                print(f"  ✓ {name} stopped")
            except subprocess.TimeoutExpired:
                print(f"  ! Force killing {name}...")
                proc.kill()
                proc.wait()
        
        print()
        print("✅ All services stopped successfully")
        return 0

if __name__ == "__main__":
    sys.exit(main())
