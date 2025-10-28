"""
Test script to verify Marimo dashboard integration works correctly.
"""

import sys
import time
import requests
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

def test_marimo_installation():
    """Test if Marimo is installed."""
    print("🧪 Testing Marimo installation...")
    try:
        import marimo
        print(f"   ✅ Marimo version {marimo.__version__} found")
        return True
    except ImportError:
        print("   ❌ Marimo not installed. Run: pip install marimo")
        return False

def test_flask_installation():
    """Test if Flask is installed."""
    print("🧪 Testing Flask installation...")
    try:
        import flask
        print(f"   ✅ Flask version {flask.__version__} found")
        return True
    except ImportError:
        print("   ❌ Flask not installed. Run: pip install flask")
        return False

def test_dashboard_file():
    """Test if dashboard.py exists."""
    print("🧪 Testing dashboard file...")
    dashboard_path = Path(__file__).parent / "marimo_app" / "dashboard.py"
    if dashboard_path.exists():
        print(f"   ✅ Dashboard found at {dashboard_path}")
        return True
    else:
        print(f"   ❌ Dashboard not found at {dashboard_path}")
        return False

def test_database_exists():
    """Test if database exists."""
    print("🧪 Testing database...")
    db_path = Path(__file__).parent / "database" / "invoices.db"
    if db_path.exists():
        print(f"   ✅ Database found at {db_path}")
        return True
    else:
        print(f"   ⚠️  No database found (will be created on first invoice)")
        return True  # Not critical for testing

def test_marimo_integration():
    """Test marimo integration module."""
    print("🧪 Testing Marimo integration...")
    try:
        from telegram_bot.marimo_integration import check_server_health
        print("   ✅ Marimo integration module loaded")
        return True
    except ImportError as e:
        print(f"   ❌ Failed to import integration: {e}")
        return False

def test_server_running():
    """Test if Marimo server is running."""
    print("🧪 Testing Marimo server connection...")
    try:
        response = requests.get("http://127.0.0.1:5001/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Server is running")
            print(f"      Active sessions: {data['active_sessions']}/{data['max_sessions']}")
            return True
        else:
            print(f"   ❌ Server responded with status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("   ⚠️  Server not running (start with: python marimo_server.py)")
        return False
    except Exception as e:
        print(f"   ❌ Error connecting to server: {e}")
        return False

def test_create_dashboard():
    """Test creating a dashboard session."""
    print("🧪 Testing dashboard creation...")
    try:
        response = requests.post(
            "http://127.0.0.1:5001/api/dashboard/create",
            json={"user_id": "test_user"},
            timeout=10
        )
        
        if response.status_code == 201:
            data = response.json()
            session_id = data['session_id']
            url = data['url']
            print(f"   ✅ Dashboard created successfully")
            print(f"      Session ID: {session_id}")
            print(f"      URL: {url}")
            
            # Test if dashboard is accessible
            print("   Testing dashboard accessibility...")
            time.sleep(3)  # Wait for Marimo to start
            try:
                dash_response = requests.get(url, timeout=5)
                if dash_response.status_code == 200:
                    print("   ✅ Dashboard is accessible")
                else:
                    print(f"   ⚠️  Dashboard returned status {dash_response.status_code}")
            except:
                print("   ⚠️  Dashboard not yet accessible (may need more time)")
            
            # Cleanup
            print("   Cleaning up test session...")
            requests.delete(f"http://127.0.0.1:5001/api/dashboard/{session_id}/terminate")
            
            return True
        else:
            error = response.json().get('error', 'Unknown error')
            print(f"   ❌ Failed to create dashboard: {error}")
            return False
    except requests.exceptions.ConnectionError:
        print("   ⚠️  Cannot connect to server")
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("  Marimo Dashboard Integration - Test Suite")
    print("=" * 60)
    print()
    
    tests = [
        ("Marimo Installation", test_marimo_installation),
        ("Flask Installation", test_flask_installation),
        ("Dashboard File", test_dashboard_file),
        ("Database", test_database_exists),
        ("Integration Module", test_marimo_integration),
        ("Server Running", test_server_running),
    ]
    
    results = []
    for name, test_func in tests:
        result = test_func()
        results.append((name, result))
        print()
    
    # Only test dashboard creation if server is running
    if results[5][1]:  # Server Running test
        result = test_create_dashboard()
        results.append(("Dashboard Creation", result))
        print()
    
    # Summary
    print("=" * 60)
    print("  Test Summary")
    print("=" * 60)
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} - {name}")
    
    print()
    print(f"  Total: {passed}/{total} tests passed")
    print("=" * 60)
    
    if passed == total:
        print()
        print("🎉 All tests passed! Your dashboard integration is ready to use.")
        print()
        print("Next steps:")
        print("  1. If server isn't running: python marimo_server.py")
        print("  2. Start your bot: python run_bot.py")
        print("  3. Try /dashboard command in Telegram")
        return 0
    else:
        print()
        print("⚠️  Some tests failed. Please fix the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
