#!/usr/bin/env python3
"""
Supabase Connection Diagnostic Tool
Tests all aspects of Supabase connectivity
"""
import os
import socket
import sys
from dotenv import load_dotenv

def print_header(text):
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)

def test_dns_resolution(host):
    """Test DNS resolution"""
    print(f"\n🔍 Testing DNS resolution for {host}...")
    try:
        ip = socket.gethostbyname(host)
        print(f"   ✅ DNS Resolution successful: {host} → {ip}")
        return True, ip
    except socket.gaierror as e:
        print(f"   ❌ DNS Resolution FAILED: {e}")
        print("\n   💡 Try these fixes:")
        print("      1. Run: ipconfig /flushdns")
        print("      2. Change DNS to Google (8.8.8.8) or Cloudflare (1.1.1.1)")
        print("      3. Check if domain is accessible: ping db.ahcplakbhnyddyhyecep.supabase.co")
        return False, None

def test_port_connectivity(host, port):
    """Test if port is accessible"""
    print(f"\n🔌 Testing port connectivity to {host}:{port}...")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((host, port))
        sock.close()
        
        if result == 0:
            print(f"   ✅ Port {port} is OPEN and accessible")
            return True
        else:
            print(f"   ❌ Port {port} is BLOCKED (error code: {result})")
            print("\n   💡 Try these fixes:")
            print("      1. Check Windows Firewall:")
            print("         - Open 'wf.msc'")
            print("         - Create Outbound Rule for TCP port 5432")
            print("      2. Check antivirus (temporarily disable and test)")
            print("      3. Check corporate firewall/proxy")
            print("      4. Try VPN")
            print("      5. Try connection pooler port 6543 instead")
            return False
    except Exception as e:
        print(f"   ❌ Port test FAILED: {e}")
        return False

def test_alternate_port(host):
    """Test connection pooler port"""
    print(f"\n🔄 Testing alternate port (Connection Pooler - 6543)...")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((host, 6543))
        sock.close()
        
        if result == 0:
            print(f"   ✅ Port 6543 is OPEN!")
            print("\n   💡 Solution: Use connection pooler")
            print("      Update .env:")
            print("      SUPABASE_DB_PORT=6543")
            return True
        else:
            print(f"   ❌ Port 6543 is also blocked")
            return False
    except Exception as e:
        print(f"   ❌ Alternate port test failed: {e}")
        return False

def test_postgresql_connection(host, port, database, user, password):
    """Test actual PostgreSQL connection"""
    print(f"\n🐘 Testing PostgreSQL connection...")
    try:
        import psycopg2
        conn = psycopg2.connect(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password,
            connect_timeout=5
        )
        print("   ✅ PostgreSQL connection SUCCESSFUL!")
        
        # Test a simple query
        cursor = conn.cursor()
        cursor.execute("SELECT 1;")
        result = cursor.fetchone()
        print(f"   ✅ Query test successful: {result}")
        
        cursor.close()
        conn.close()
        return True
    except ImportError:
        print("   ❌ psycopg2 not installed")
        print("      Install with: pip install psycopg2-binary")
        return False
    except Exception as e:
        print(f"   ❌ PostgreSQL connection FAILED: {e}")
        return False

def test_supabase_rest_api():
    """Test Supabase REST API (alternative)"""
    print(f"\n🌐 Testing Supabase REST API...")
    try:
        from supabase import create_client
        
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_SERVICE_KEY")
        
        if not supabase_url or not supabase_key:
            print("   ⚠️  Supabase URL or Service Key not found in .env")
            return False
        
        client = create_client(supabase_url, supabase_key)
        
        # Try a simple query
        result = client.table('user').select('count').execute()
        print("   ✅ Supabase REST API works!")
        print("      This is a good alternative if direct connection fails")
        return True
    except ImportError:
        print("   ⚠️  supabase-py not installed")
        print("      Install with: pip install supabase")
        return False
    except Exception as e:
        print(f"   ❌ REST API test failed: {e}")
        return False

def main():
    print_header("🚀 SUPABASE CONNECTION DIAGNOSTIC TOOL")
    
    # Load environment variables
    load_dotenv()
    
    host = os.getenv("SUPABASE_DB_HOST")
    port = int(os.getenv("SUPABASE_DB_PORT", 5432))
    database = os.getenv("SUPABASE_DB_NAME", "postgres")
    user = os.getenv("SUPABASE_DB_USER", "postgres")
    password = os.getenv("SUPABASE_DB_PASSWORD")
    
    if not host or not password:
        print("\n❌ ERROR: Supabase credentials not found in .env file")
        print("   Make sure these are set:")
        print("   - SUPABASE_DB_HOST")
        print("   - SUPABASE_DB_PASSWORD")
        sys.exit(1)
    
    print(f"\nTesting connection to:")
    print(f"   Host: {host}")
    print(f"   Port: {port}")
    print(f"   Database: {database}")
    print(f"   User: {user}")
    
    # Run all tests
    tests_passed = []
    
    # Test 1: DNS
    dns_ok, ip = test_dns_resolution(host)
    tests_passed.append(("DNS Resolution", dns_ok))
    
    if not dns_ok:
        print("\n" + "="*70)
        print("❌ DIAGNOSIS: DNS resolution failed")
        print("   Cannot proceed with further tests")
        print("="*70)
        sys.exit(1)
    
    # Test 2: Port 5432
    port_ok = test_port_connectivity(host, port)
    tests_passed.append((f"Port {port} Connectivity", port_ok))
    
    # Test 3: Alternate port (if main port fails)
    if not port_ok:
        alt_port_ok = test_alternate_port(host)
        tests_passed.append(("Alternate Port 6543", alt_port_ok))
    
    # Test 4: PostgreSQL connection
    if port_ok:
        pg_ok = test_postgresql_connection(host, port, database, user, password)
        tests_passed.append(("PostgreSQL Connection", pg_ok))
    else:
        print("\n⏭️  Skipping PostgreSQL test (port blocked)")
        tests_passed.append(("PostgreSQL Connection", False))
    
    # Test 5: REST API
    rest_ok = test_supabase_rest_api()
    tests_passed.append(("Supabase REST API", rest_ok))
    
    # Summary
    print_header("📊 TEST SUMMARY")
    
    for test_name, passed in tests_passed:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"   {status}  {test_name}")
    
    passed_count = sum(1 for _, passed in tests_passed if passed)
    total_count = len(tests_passed)
    
    print(f"\n   Results: {passed_count}/{total_count} tests passed")
    
    # Recommendations
    print_header("💡 RECOMMENDATIONS")
    
    if tests_passed[2][1]:  # PostgreSQL connection passed
        print("\n   🎉 GREAT NEWS! Direct PostgreSQL connection works!")
        print("\n   ✅ You can use Supabase with full features:")
        print("      1. Set USE_SUPABASE=true in .env")
        print("      2. Restart your bot")
        print("      3. Enjoy Supabase! 🚀")
        
    elif tests_passed[1][1] == False and tests_passed[3][1]:  # Port blocked but REST API works
        print("\n   ⚠️  Port 5432 is blocked, but REST API works!")
        print("\n   🔄 WORKAROUND OPTIONS:")
        print("\n      Option 1: Fix the firewall (RECOMMENDED)")
        print("         1. Open Windows Firewall (wf.msc)")
        print("         2. Create Outbound Rule for TCP port 5432")
        print("         3. Allow connections to db.ahcplakbhnyddyhyecep.supabase.co")
        print("         4. Run this diagnostic again")
        print("\n      Option 2: Use Connection Pooler")
        if tests_passed[2][1]:  # If alternate port works
            print("         ✅ Port 6543 is open!")
            print("         Update .env: SUPABASE_DB_PORT=6543")
        else:
            print("         ❌ Port 6543 is also blocked")
        print("\n      Option 3: Continue with SQLite")
        print("         Keep USE_SUPABASE=false")
        print("         All features work with SQLite!")
    
    else:
        print("\n   ❌ Multiple connection issues detected")
        print("\n   🔧 TROUBLESHOOTING STEPS:")
        print("      1. Check Windows Firewall settings")
        print("      2. Temporarily disable antivirus and test")
        print("      3. Flush DNS cache: ipconfig /flushdns")
        print("      4. Try using a VPN")
        print("      5. Check if on corporate network with restrictions")
        print("\n   📝 For now, continue using SQLite (USE_SUPABASE=false)")
    
    print("\n" + "="*70)
    
    if tests_passed[2][1]:
        sys.exit(0)  # Success
    else:
        sys.exit(1)  # Failure

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Diagnostic cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
