# n8n Workflows untuk WhatsApp Invoice Bot

Folder ini berisi konfigurasi n8n workflows untuk menghubungkan WAHA WhatsApp API dengan Python bot.

## 📋 Overview

n8n bertindak sebagai middleware antara:
- **WAHA** (WhatsApp HTTP API) → **n8n** → **Python Bot** → **n8n** → **WAHA**

## 🔄 Workflow Architecture

```
WhatsApp Message → WAHA → n8n Webhook → Python Bot API → Response → n8n → WAHA → WhatsApp
```

## 📁 Files dalam Folder Ini

1. `whatsapp-message-processor.json` - Main workflow untuk memproses pesan WhatsApp
2. `response-sender.json` - Workflow untuk mengirim response kembali ke WhatsApp  
3. `setup-guide.md` - Panduan lengkap setup n8n
4. `webhook-examples.md` - Contoh webhook payloads

## 🚀 Quick Setup

1. Import workflow JSON files ke n8n
2. Konfigurasi webhook URLs
3. Set environment variables
4. Jalankan Python bot
5. Test dengan WhatsApp message

Lihat `setup-guide.md` untuk instruksi detail.