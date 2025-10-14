# 🚀 WhatsApp Bot Execution Guide

## Urutan Eksekusi Step-by-Step untuk WhatsApp Invoice Bot

### **PHASE 1: Environment Setup** ✅

#### Step 1: Install Dependencies
```bash
# Navigate to project directory
cd e:\Github Project\hackathon\invoice_rag

# Install Python dependencies
pip install -r requirements.txt
# atau menggunakan uv (faster)
uv pip install -r requirements.txt -U
```

#### Step 2: Environment Configuration
```bash
# Check current .env file
Get-Content .env
```

**Verify Environment Variables:**
- ✅ `GROQ_API_KEY` - AI processing
- ✅ `TELEGRAM_BOT_TOKEN` - Telegram bot (optional)
- 🔧 `WAHA_URL=http://localhost:3000` - WhatsApp API
- 🔧 `N8N_URL=http://localhost:5678` - Workflow automation
- 🔧 `WHATSAPP_SESSION_NAME=invoice_bot_session`

---

### **PHASE 2: Start Infrastructure Services** 🏗️

#### Step 3: Start WAHA Server
```powershell
# Terminal 1 - Start WAHA WhatsApp HTTP API server
docker run -it --rm --name waha -p 3000:3000/tcp devlikeapro/waha
```

> **⚠️ Action Required**: 
> - Jalankan command ini di **terminal terpisah**
> - Biarkan terminal ini **tetap running**
> - WAHA akan accessible di `http://localhost:3000`

#### Step 4: Start n8n Server  
```powershell
# Terminal 2 - Start n8n workflow automation server
docker run -it --rm --name n8n -p 5678:5678 n8nio/n8n
```

> **⚠️ Action Required**: 
> - Jalankan command ini di **terminal kedua**
> - Biarkan terminal ini **tetap running**
> - n8n akan accessible di `http://localhost:5678`

**Verification Commands:**
```powershell
# Check if services are running
docker ps
netstat -an | Select-String ":3000"  # WAHA
netstat -an | Select-String ":5678"  # n8n
```

---

### **PHASE 3: Configure n8n Workflow** 🔄

#### Step 5: Setup n8n Workflow
1. **Open n8n Dashboard**: http://localhost:5678
   - Wait for n8n to fully load (may take 1-2 minutes)

2. **Import Workflow**:
   - Click **"Import from URL"** atau **"Import from file"**
   - Select file: `n8n_workflows/whatsapp-message-processor.json`
   - Click **"Import"**

3. **Configure Environment Variables** (dalam n8n):
   - Go to **Settings** → **Environment Variables**
   - Add:
     ```
     WAHA_URL=http://host.docker.internal:3000
     WHATSAPP_SESSION_NAME=invoice_bot_session
     PYTHON_BOT_URL=http://host.docker.internal:8000
     ```

4. **Activate Workflow**:
   - Set workflow status menjadi **"Active"**
   - Verify webhook URL: `http://localhost:5678/webhook/whatsapp-invoice-bot`

---

### **PHASE 4: Start Python WhatsApp Bot** 🐍

#### Step 6: Initialize Database
```powershell
# Test database initialization
python -c "from whatsapp_bot.platform_database import init_platform_tables; init_platform_tables(); print('✅ Database initialized successfully!')"
```

**Expected Output:**
```
Platform tables initialized successfully
✅ Database initialized successfully!
```

#### Step 7: Start WhatsApp Bot Server
```powershell
# Terminal 3 - Start WhatsApp bot server
python run_whatsapp_bot.py
```

**Expected Output:**
```
🚀 Starting WhatsApp Invoice Bot...
✅ WAHA session started successfully
🤖 WhatsApp Bot is ready!
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

> **⚠️ Action Required**: 
> - Jalankan command ini di **terminal ketiga**
> - Bot akan running di `http://localhost:8000`
> - Tunggu sampai muncul "WhatsApp Bot is ready!"

---

### **PHASE 5: WhatsApp Pairing & Setup** 📱

#### Step 8: Get QR Code untuk WhatsApp Pairing

**Option 1: Via Browser**
```
http://localhost:8000/qr
```

**Option 2: Via PowerShell**
```powershell
# Get QR code (terminal 4)
Invoke-RestMethod -Uri "http://localhost:8000/qr" -Method GET
```

**Expected Response:**
```json
{
  "qr_code": "2@BjgX8vxg9mKAlbHr..."
}
```

#### Step 9: Scan QR Code
1. **Buka WhatsApp** di smartphone
2. Go to **Settings** → **Linked Devices** → **Link a Device**
3. **Scan QR code** yang muncul di browser/terminal
4. **Wait for confirmation** message

**Verification:**
```powershell
# Check WAHA session status
Invoke-RestMethod -Uri "http://localhost:3000/api/sessions/invoice_bot_session" -Method GET
```

**Expected Response:**
```json
{
  "name": "invoice_bot_session",
  "status": "WORKING"
}
```

---

### **PHASE 6: Testing & Verification** 🧪

#### Step 10: Test Bot Status
```powershell
# Check WhatsApp bot status
Invoke-RestMethod -Uri "http://localhost:8000/status" -Method GET
```

**Expected Response:**
```json
{
  "bot_status": "running",
  "waha_status": "WORKING",
  "n8n_configured": true
}
```

#### Step 11: Test n8n Webhook
```powershell
# Test n8n webhook endpoint
$body = @{
    event = "message"
    data = @{
        from = "6281234567890@c.us"
        type = "text"
        body = "start"
        timestamp = "2025-10-14T12:00:00Z"
    }
} | ConvertTo-Json -Depth 3

Invoke-RestMethod -Uri "http://localhost:5678/webhook/whatsapp-invoice-bot" -Method POST -Body $body -ContentType "application/json"
```

#### Step 12: Test Python Bot Direct
```powershell
# Test Python bot webhook endpoint
$body = @{
    event = "message"
    data = @{
        from = "6281234567890@c.us"
        type = "text"
        body = "start"
        timestamp = "2025-10-14T12:00:00Z"
    }
} | ConvertTo-Json -Depth 3

Invoke-RestMethod -Uri "http://localhost:8000/webhook/whatsapp" -Method POST -Body $body -ContentType "application/json"
```

---

### **PHASE 7: WhatsApp Bot Testing** 📱

#### Step 13: Test Basic Commands
Kirim pesan WhatsApp ke nomor yang sudah di-pair:

| Command | Description | Expected Response |
|---------|-------------|-------------------|
| `start` | Mulai bot | Welcome message dengan menu |
| `help` | Bantuan lengkap | Panduan penggunaan bot |
| `analysis` | Analisis pengeluaran | Text summary + grafik |

**Testing Sequence:**
1. **Send**: `start`
   - **Expect**: Welcome message dalam Bahasa Indonesia
2. **Send**: `help`  
   - **Expect**: Complete help guide
3. **Send**: `analysis`
   - **Expect**: Financial summary + dashboard image

#### Step 14: Test Advanced Features
| Command | Description | Expected Response |
|---------|-------------|-------------------|
| `setlimit 1000000` | Set budget Rp 1 juta | Confirmation message |
| `checklimit` | Check budget status | Current spending vs limit |
| `recent` | 5 invoice terbaru | List of recent transactions |

#### Step 15: Test Image Processing
1. **Upload Invoice**: 
   - Ambil foto struk/invoice
   - Kirim via WhatsApp ke bot
   
2. **Expected Response**:
   ```
   📄 Memproses invoice... Mohon tunggu.
   ✅ Invoice berhasil diproses!
   
   📅 Tanggal: 2025-10-14
   🏢 Toko: [Shop Name]
   💰 Total: Rp XX,XXX.00
   📝 Items: X items
   ```

---

### **PHASE 8: Monitoring & Debugging** 📊

#### Step 16: Monitor Logs

**WhatsApp Bot Logs:**
```powershell
# Monitor bot console output (Terminal 3)
# Check for error messages or successful processing logs
```

**n8n Execution Logs:**
1. Open http://localhost:5678
2. Go to **Executions** tab
3. Check recent workflow executions
4. Click on executions to see detailed logs

**WAHA Logs:**
```powershell
# Check WAHA container logs
docker logs waha
```

#### Step 17: Database Verification
```powershell
# Check if data is being saved
python -c "
from src.database import get_db_session
from src.database import Invoice
session = get_db_session()
count = session.query(Invoice).count()
print(f'Total invoices in database: {count}')
session.close()
"
```

---

## 🎯 **Checkpoint Verification**

### ✅ **Phase 1-2 Success Indicators**:
- [ ] `uv pip install` completed successfully
- [ ] WAHA container running on port 3000
- [ ] n8n container running on port 5678
- [ ] Both services accessible via browser

### ✅ **Phase 3-4 Success Indicators**:
- [ ] n8n workflow imported successfully
- [ ] Workflow status is "Active" 
- [ ] Database tables initialized
- [ ] WhatsApp bot server running on port 8000
- [ ] "WhatsApp Bot is ready!" message appears

### ✅ **Phase 5-6 Success Indicators**:
- [ ] QR code generated successfully
- [ ] WhatsApp successfully paired (phone shows "Connected")
- [ ] WAHA session status = "WORKING"
- [ ] Bot status API returns healthy response

### ✅ **Phase 7-8 Success Indicators**:
- [ ] `start` command returns Indonesian welcome message
- [ ] `analysis` command generates and sends chart
- [ ] Image upload processes invoice correctly
- [ ] Data saved to database successfully
- [ ] n8n executions show successful workflow runs

---

## 🔧 **Troubleshooting Commands**

### Common Issues & Solutions

#### **Services Not Starting:**
```powershell
# Check running containers
docker ps

# Check port usage
netstat -an | Select-String ":3000|:5678|:8000"

# Kill existing processes if needed
Stop-Process -Name "docker" -Force
docker container prune -f
```

#### **WhatsApp Connection Issues:**
```powershell
# Reset WAHA session
Invoke-RestMethod -Uri "http://localhost:3000/api/sessions/invoice_bot_session/stop" -Method DELETE
Invoke-RestMethod -Uri "http://localhost:3000/api/sessions/invoice_bot_session/start" -Method POST

# Get new QR code
Invoke-RestMethod -Uri "http://localhost:8000/qr" -Method GET
```

#### **Database Issues:**
```powershell
# Reinitialize database
python -c "
from whatsapp_bot.platform_database import init_platform_tables
init_platform_tables()
print('Database reinitialized')
"
```

#### **n8n Workflow Issues:**
1. Check **Environment Variables** in n8n settings
2. Verify **webhook URL** is accessible
3. Re-import workflow if needed
4. Check **Executions** tab for error details

---

## 🚀 **Quick Start Summary**

```powershell
# Terminal 1: WAHA
docker run -it --rm --name waha -p 3000:3000/tcp devlikeapro/waha

# Terminal 2: n8n  
docker run -it --rm --name n8n -p 5678:5678 n8nio/n8n

# Terminal 3: WhatsApp Bot
cd e:\Github Project\hackathon\invoice_rag
python run_whatsapp_bot.py

# Terminal 4: Testing
Invoke-RestMethod -Uri "http://localhost:8000/qr" -Method GET
```

**Ready to start? Begin with Step 1!** 🎯