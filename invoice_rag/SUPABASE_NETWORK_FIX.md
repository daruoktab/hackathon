# Supabase Connection Fix Guide

## Problem
Direct PostgreSQL connections (port 5432) to Supabase are being blocked, causing this error:
```
psycopg2.OperationalError: could not translate host name "db.ahcplakbhnyddyhyecep.supabase.co" to address: Name or service not known
```

## Root Cause
Your network/firewall is blocking outbound connections to PostgreSQL (port 5432).

---

## Permanent Solutions

### Solution 1: Windows Firewall Configuration (RECOMMENDED)

#### Step 1: Open Windows Firewall
```powershell
# Run as Administrator
Start-Process "wf.msc"
```

#### Step 2: Create Outbound Rule
1. Click **"Outbound Rules"** in left panel
2. Click **"New Rule..."** in right panel
3. Select **"Port"** → Click Next
4. Select **"TCP"** → Specific remote ports: **5432** → Click Next
5. Select **"Allow the connection"** → Click Next
6. Check all profiles (Domain, Private, Public) → Click Next
7. Name: **"Supabase PostgreSQL"** → Click Finish

#### Step 3: Test Connection
```powershell
# Test if port 5432 is accessible
Test-NetConnection -ComputerName db.ahcplakbhnyddyhyecep.supabase.co -Port 5432
```

Should see: `TcpTestSucceeded : True`

#### Step 4: Enable Supabase in .env
```env
USE_SUPABASE=true
```

#### Step 5: Restart Bot
```powershell
python run_bot.py
```

---

### Solution 2: Check DNS Resolution

Sometimes the issue is DNS, not firewall:

```powershell
# Test DNS resolution
nslookup db.ahcplakbhnyddyhyecep.supabase.co

# Try with Google DNS
nslookup db.ahcplakbhnyddyhyecep.supabase.co 8.8.8.8

# Flush DNS cache
ipconfig /flushdns

# Test again
Test-NetConnection -ComputerName db.ahcplakbhnyddyhyecep.supabase.co -Port 5432
```

---

### Solution 3: Check Antivirus/Security Software

Some antivirus software blocks database connections:

1. **Temporarily disable** your antivirus
2. **Test** the connection again
3. If it works, **add an exception** for:
   - Python executable: `D:\anaconda3\envs\Hackthon\python.exe`
   - Port: `5432`
   - Host: `db.ahcplakbhnyddyhyecep.supabase.co`

---

### Solution 4: Check Corporate/Network Proxy

If you're on a corporate network:

```powershell
# Check proxy settings
netsh winhttp show proxy

# If proxy is set, you may need to configure psycopg2 to use it
# Or ask your IT department to whitelist:
# - db.ahcplakbhnyddyhyecep.supabase.co:5432
```

---

### Solution 5: Use VPN (If All Else Fails)

If your ISP or organization blocks port 5432:

1. Install a VPN (e.g., ProtonVPN, Windscribe, Cloudflare WARP)
2. Connect to VPN
3. Test connection again

---

## Alternative: Connection Pooling Service

If you can't modify firewall settings, use **Supabase Connection Pooler**:

### Update .env:
```env
# Instead of direct connection
# SUPABASE_DB_HOST=db.ahcplakbhnyddyhyecep.supabase.co

# Use connection pooler (port 6543 - often not blocked)
SUPABASE_DB_HOST=db.ahcplakbhnyddyhyecep.supabase.co
SUPABASE_DB_PORT=6543
```

Then test:
```powershell
Test-NetConnection -ComputerName db.ahcplakbhnyddyhyecep.supabase.co -Port 6543
```

---

## Verification Steps

After applying any solution:

### 1. Test Network Connection
```powershell
Test-NetConnection -ComputerName db.ahcplakbhnyddyhyecep.supabase.co -Port 5432
```

### 2. Test Python Connection
```powershell
cd "E:\Github Project\hackathon\invoice_rag"
conda activate Hackthon
python -c "import psycopg2; conn = psycopg2.connect(host='db.ahcplakbhnyddyhyecep.supabase.co', port=5432, database='postgres', user='postgres', password='gmx3nAXlydwNgbUR'); print('✅ Connection successful!'); conn.close()"
```

### 3. Test Bot with Supabase
```powershell
# Enable Supabase in .env
# USE_SUPABASE=true

python run_bot.py
```

Should see:
```
ℹ️  Using Supabase - spending_limits table already exists
Bot is ready to serve!
```

### 4. Test Premium Feature
- Send `/start` in Telegram
- Bot should create user in Supabase
- Generate new token and claim it
- `/analysis` should work

---

## Quick Diagnostic Script

Save as `test_supabase_connection.py`:

```python
import os
import socket
from dotenv import load_dotenv

load_dotenv()

host = os.getenv("SUPABASE_DB_HOST")
port = int(os.getenv("SUPABASE_DB_PORT", 5432))

print(f"Testing connection to {host}:{port}...")

try:
    # Test DNS resolution
    ip = socket.gethostbyname(host)
    print(f"✅ DNS Resolution: {host} → {ip}")
except socket.gaierror as e:
    print(f"❌ DNS Resolution failed: {e}")
    print("   Try: ipconfig /flushdns")
    exit(1)

try:
    # Test port connectivity
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5)
    result = sock.connect_ex((host, port))
    sock.close()
    
    if result == 0:
        print(f"✅ Port {port} is OPEN")
    else:
        print(f"❌ Port {port} is BLOCKED")
        print("   → Check firewall settings")
        print("   → Check antivirus")
        print("   → Try VPN")
        exit(1)
except Exception as e:
    print(f"❌ Connection test failed: {e}")
    exit(1)

try:
    # Test PostgreSQL connection
    import psycopg2
    conn = psycopg2.connect(
        host=host,
        port=port,
        database=os.getenv("SUPABASE_DB_NAME"),
        user=os.getenv("SUPABASE_DB_USER"),
        password=os.getenv("SUPABASE_DB_PASSWORD")
    )
    print("✅ PostgreSQL connection successful!")
    conn.close()
except Exception as e:
    print(f"❌ PostgreSQL connection failed: {e}")
    exit(1)

print("\n🎉 All tests passed! Supabase is ready to use.")
print("   Set USE_SUPABASE=true in .env")
```

Run it:
```powershell
python test_supabase_connection.py
```

---

## Current Workaround (Temporary)

While you fix the network issue, continue using SQLite:
```env
USE_SUPABASE=false
```

All features work perfectly with SQLite for development and testing.

---

## Support

If none of these solutions work:

1. **Check Supabase Status**: https://status.supabase.com/
2. **Supabase Support**: https://supabase.com/support
3. **Your Network Admin**: If on corporate network

---

## Summary

**Most Common Fixes:**
1. ✅ Add Windows Firewall rule for port 5432
2. ✅ Flush DNS cache (`ipconfig /flushdns`)
3. ✅ Disable antivirus temporarily and add exception
4. ✅ Try connection pooler port 6543
5. ✅ Use VPN if ISP blocks port 5432

**After fixing:**
- Set `USE_SUPABASE=true`
- Restart bot
- Test premium features
- Enjoy Supabase! 🚀
