# Webhook Examples untuk WhatsApp Invoice Bot

## 📨 Incoming Webhooks (dari WAHA ke n8n)

### Text Message
```json
{
  "event": "message",
  "session": "invoice_bot_session",
  "data": {
    "id": "message_id_12345",
    "timestamp": "1697271600",
    "from": "6281234567890@c.us",
    "fromMe": false,
    "type": "text",
    "body": "start",
    "pushName": "John Doe"
  }
}
```

### Image Message
```json
{
  "event": "message",
  "session": "invoice_bot_session",
  "data": {
    "id": "message_id_12346",
    "timestamp": "1697271660",
    "from": "6281234567890@c.us",
    "fromMe": false,
    "type": "image",
    "mediaUrl": "http://localhost:3000/api/files/message_id_12346.jpg",
    "caption": "",
    "pushName": "John Doe"
  }
}
```

### Command Examples
```json
{
  "event": "message",
  "data": {
    "from": "6281234567890@c.us",
    "type": "text",
    "body": "analysis",
    "timestamp": "1697271600"
  }
}
```

```json
{
  "event": "message",
  "data": {
    "from": "6281234567890@c.us",
    "type": "text",
    "body": "setlimit 5000000",
    "timestamp": "1697271700"
  }
}
```

## 📤 Outgoing Responses (dari Python Bot ke n8n)

### Text Response
```json
{
  "response_type": "text",
  "phone": "+6281234567890",
  "content": "✅ Invoice berhasil diproses!\n\n📅 Tanggal: 2025-10-14\n🏢 Toko: Indomaret\n💰 Total: Rp 45,500.00\n📝 Items: 3 items"
}
```

### Error Response
```json
{
  "response_type": "text",
  "phone": "+6281234567890",
  "content": "❌ Gagal memproses invoice. Pastikan gambar jelas dan coba lagi."
}
```

### Analysis Response (Text + Image)
```json
{
  "response_type": "text",
  "phone": "+6281234567890",
  "content": "📊 Ringkasan Invoice\n\nTotal Invoice: 25\nTotal Pengeluaran: Rp 2,450,000.00\nRata-rata: Rp 98,000.00"
}
```

## 🔄 n8n ke WAHA API Calls

### Send Text Message
```json
POST http://localhost:3000/api/sessions/invoice_bot_session/chats/6281234567890@c.us/messages/text

Headers:
- Content-Type: application/json
- Authorization: Bearer YOUR_WAHA_API_KEY

Body:
{
  "text": "👋 Halo! Saya Invoice Helper Bot untuk WhatsApp!"
}
```

### Send Image Message
```json
POST http://localhost:3000/api/sessions/invoice_bot_session/chats/6281234567890@c.us/messages/image

Headers:
- Content-Type: application/json
- Authorization: Bearer YOUR_WAHA_API_KEY

Body:
{
  "file": {
    "mimetype": "image/png",
    "filename": "analysis.png",
    "data": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAA..."
  },
  "caption": "📊 Dashboard Analisis Pengeluaran Anda"
}
```

## 🧪 Test Payloads

### Test Start Command
```bash
curl -X POST http://localhost:5678/webhook/whatsapp-invoice-bot \
  -H "Content-Type: application/json" \
  -d '{
    "event": "message",
    "data": {
      "from": "6281234567890@c.us",
      "type": "text",
      "body": "start",
      "timestamp": "1697271600"
    }
  }'
```

### Test Analysis Command
```bash
curl -X POST http://localhost:5678/webhook/whatsapp-invoice-bot \
  -H "Content-Type: application/json" \
  -d '{
    "event": "message",
    "data": {
      "from": "6281234567890@c.us",
      "type": "text",
      "body": "analysis",
      "timestamp": "1697271600"
    }
  }'
```

### Test Image Upload
```bash
curl -X POST http://localhost:5678/webhook/whatsapp-invoice-bot \
  -H "Content-Type: application/json" \
  -d '{
    "event": "message",
    "data": {
      "from": "6281234567890@c.us",
      "type": "image",
      "id": "message_id_12345",
      "mediaUrl": "http://localhost:3000/api/files/test_invoice.jpg",
      "timestamp": "1697271600"
    }
  }'
```

### Test Set Limit Command
```bash
curl -X POST http://localhost:5678/webhook/whatsapp-invoice-bot \
  -H "Content-Type: application/json" \
  -d '{
    "event": "message",
    "data": {
      "from": "6281234567890@c.us",
      "type": "text",
      "body": "setlimit 5000000",
      "timestamp": "1697271600"
    }
  }'
```

## 📊 Expected Responses

### Start Command Response
```json
{
  "response_type": "text",
  "phone": "+6281234567890",
  "content": "👋 Halo! Saya Invoice Helper Bot untuk WhatsApp!\n\nSaya dapat membantu Anda:\n📸 Kirim foto struk/invoice untuk diproses\n📊 Lihat analisis pengeluaran dengan grafik\n💰 Set dan track budget bulanan\n📋 Cek riwayat pengeluaran\n\n💡 Perintah yang tersedia:\n• Kirim foto invoice langsung\n• 'analysis' - Lihat analisis & grafik\n• 'recent' - 5 invoice terbaru\n• 'setlimit 5000000' - Set budget\n• 'checklimit' - Cek status budget\n• 'help' - Bantuan lengkap\n\n📱 Mulai dengan mengirim foto struk Anda!"
}
```

### Analysis Command Response
```json
{
  "response_type": "text",
  "phone": "+6281234567890",
  "content": "📊 Ringkasan Invoice\n\nTotal Invoice: 25\nTotal Pengeluaran: Rp 2,450,000.00\nRata-rata: Rp 98,000.00\n\nTop Vendor:\n• Indomaret: Rp 650,000.00\n• Alfamart: Rp 480,000.00\n• Superindo: Rp 320,000.00"
}
```

### Error Response Examples
```json
{
  "response_type": "text",
  "phone": "+6281234567890", 
  "content": "❌ Tidak dapat mengunduh gambar. Silakan coba lagi."
}
```

```json
{
  "response_type": "text",
  "phone": "+6281234567890",
  "content": "❌ Mohon berikan angka yang valid untuk batas pengeluaran."
}
```

## 🔍 Debugging Payloads

### Check n8n Execution Log
Untuk melihat payload yang diterima n8n:

1. Buka n8n dashboard
2. Go to **Executions**
3. Click pada execution terbaru
4. Expand setiap node untuk melihat input/output data

### Check Python Bot Logs
```bash
# Jalankan WhatsApp bot dengan verbose logging
python run_whatsapp_bot.py

# Monitor logs untuk webhook data
tail -f whatsapp_bot.log
```

### Manual Testing
```bash
# Test Python Bot endpoint langsung
curl -X POST http://localhost:8000/webhook/whatsapp \
  -H "Content-Type: application/json" \
  -d '{
    "event": "message",
    "data": {
      "from": "6281234567890@c.us",
      "type": "text",
      "body": "test",
      "timestamp": "1697271600"
    }
  }'
```