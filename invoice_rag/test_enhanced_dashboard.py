"""
Test script for the enhanced dashboard visualization.
This script tests the refactored create_comprehensive_dashboard function.
"""
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from telegram_bot.visualizations import create_comprehensive_dashboard, format_rp

def test_format_rp():
    """Test the format_rp helper function."""
    print("Testing format_rp function...")
    
    test_cases = [
        (0, 'Rp 0'),
        (500, 'Rp 500'),
        (1500, 'Rp 2K'),
        (50000, 'Rp 50K'),
        (1000000, 'Rp 1.0M'),
        (2500000, 'Rp 2.5M'),
        (None, 'Rp 0')
    ]
    
    for value, expected in test_cases:
        result = format_rp(value)
        status = "✓" if result == expected else "✗"
        print(f"  {status} format_rp({value}) = {result} (expected: {expected})")

def test_dashboard_without_user():
    """Test dashboard generation without user_id."""
    print("\nTesting dashboard without user_id...")
    try:
        buf = create_comprehensive_dashboard(weeks_back=8, user_id=None)
        print("  ✓ Dashboard created successfully without user_id")
        print(f"  ✓ Image size: {len(buf.getvalue())} bytes")
        
        # Save to file for inspection
        output_path = project_root / 'dashboard_output' / 'test_dashboard_no_user.png'
        output_path.parent.mkdir(exist_ok=True)
        with open(output_path, 'wb') as f:
            f.write(buf.getvalue())
        print(f"  ✓ Dashboard saved to: {output_path}")
        
    except Exception as e:
        print(f"  ✗ Error: {e}")
        import traceback
        traceback.print_exc()

def test_dashboard_with_user():
    """Test dashboard generation with user_id."""
    print("\nTesting dashboard with user_id...")
    try:
        # Use a test user_id (this user may or may not have a budget set)
        test_user_id = 12345
        buf = create_comprehensive_dashboard(weeks_back=8, user_id=test_user_id)
        print(f"  ✓ Dashboard created successfully with user_id={test_user_id}")
        print(f"  ✓ Image size: {len(buf.getvalue())} bytes")
        
        # Save to file for inspection
        output_path = project_root / 'dashboard_output' / f'test_dashboard_user_{test_user_id}.png'
        output_path.parent.mkdir(exist_ok=True)
        with open(output_path, 'wb') as f:
            f.write(buf.getvalue())
        print(f"  ✓ Dashboard saved to: {output_path}")
        
    except Exception as e:
        print(f"  ✗ Error: {e}")
        import traceback
        traceback.print_exc()

def test_dashboard_insufficient_data():
    """Test dashboard with very limited data (weeks_back=1)."""
    print("\nTesting dashboard with insufficient data (weeks_back=1)...")
    try:
        buf = create_comprehensive_dashboard(weeks_back=1, user_id=None)
        print("  ✓ Dashboard created successfully with limited data")
        print(f"  ✓ Image size: {len(buf.getvalue())} bytes")
        
        # Save to file for inspection
        output_path = project_root / 'dashboard_output' / 'test_dashboard_limited_data.png'
        output_path.parent.mkdir(exist_ok=True)
        with open(output_path, 'wb') as f:
            f.write(buf.getvalue())
        print(f"  ✓ Dashboard saved to: {output_path}")
        
    except Exception as e:
        print(f"  ✗ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("=" * 60)
    print("Enhanced Dashboard Test Suite")
    print("=" * 60)
    
    test_format_rp()
    test_dashboard_without_user()
    test_dashboard_with_user()
    test_dashboard_insufficient_data()
    
    print("\n" + "=" * 60)
    print("Test suite completed!")
    print("=" * 60)
