#!/usr/bin/env python3
"""
Test script to generate the comprehensive dashboard visualization.
This generates the exact same image that users receive in Telegram.
"""

import os
import sys
from datetime import datetime

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from telegram_bot.visualizations import create_comprehensive_dashboard

def test_dashboard():
    """Generate the comprehensive dashboard visualization that users get in Telegram."""
    
    print("🎨 Generating Invoice Dashboard (Same as Telegram users receive)...")
    
    # Create output directory
    output_dir = "dashboard_output"
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    try:
        # Generate the dashboard
        dashboard_buf = create_comprehensive_dashboard()
        
        # Save the image
        filepath = f"{output_dir}/invoice_dashboard_{timestamp}.png"
        with open(filepath, "wb") as f:
            f.write(dashboard_buf.getvalue())
        
        print("✅ Dashboard generated successfully!")
        print(f"📁 Saved as: {filepath}")
        print(f"📍 Full path: {os.path.abspath(filepath)}")
        print("\n📊 This is the exact dashboard image that Telegram users receive")
        print("   when they request invoice analysis visualization.")
        
        # Try to open the file (Windows)
        try:
            if os.name == 'nt':
                os.startfile(filepath)
                print("\n🖼️  Opening image...")
        except Exception:
            pass
            
        return filepath
        
    except Exception as e:
        print(f"❌ Error generating dashboard: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    test_dashboard()