# n8n Setup Guide untuk WhatsApp Invoice Bot

## 🎯 Prerequisites

1. **n8n** installed dan running pada `http://localhost:5678`
2. **WAHA** running pada `http://localhost:3000`
3. **Python Bot** akan running pada `http://localhost:8000`

## 📦 Installation n8n

### Option 1: Docker (Recommended)
```bash
docker run -it --rm --name n8n -p 5678:5678 n8nio/n8n
```

### Option 2: npm
```bash
npm install n8n -g
n8n start
```

## 🔧 Workflow Setup

### Step 1: Import Workflows

1. Buka n8n di `http://localhost:5678`
2. Klik **"Import from URL"** atau **"Import from file"**
3. Import file `whatsapp-message-processor.json`
4. Import file `response-sender.json`

### Step 2: Configure Main Workflow

**Workflow: "WhatsApp Message Processor"**

#### Node 1: Webhook Trigger
- **Type**: Webhook
- **Path**: `/webhook/whatsapp-invoice-bot`
- **Method**: POST
- **Response Mode**: Last Node

#### Node 2: Check Message Type
- **Type**: Switch
- **Property**: `{{ $json.data.type }}`
- **Rules**:
  - `text` → Route to Text Processor
  - `image` → Route to Image Processor
  - Default → Route to Unsupported Handler

#### Node 3: Text Message Processor
- **Type**: HTTP Request
- **Method**: POST
- **URL**: `http://localhost:8000/webhook/whatsapp`
- **Body**:
```json
{
  "event": "message",
  "data": {
    "from": "{{ $json.data.from }}",
    "type": "text",
    "body": "{{ $json.data.body }}",
    "timestamp": "{{ $json.data.timestamp }}"
  }
}
```

#### Node 4: Image Message Processor
- **Type**: HTTP Request
- **Method**: POST
- **URL**: `http://localhost:8000/webhook/whatsapp`
- **Body**:
```json
{
  "event": "message",
  "data": {
    "from": "{{ $json.data.from }}",
    "type": "image",
    "id": "{{ $json.data.id }}",
    "mediaUrl": "{{ $json.data.mediaUrl }}",
    "timestamp": "{{ $json.data.timestamp }}"
  }
}
```

#### Node 5: Send Response to WAHA
- **Type**: HTTP Request
- **Method**: POST
- **URL**: `http://localhost:3000/api/sessions/invoice_bot_session/chats/{{ $json.response.phone.replace('+', '') }}@c.us/messages/text`
- **Headers**:
  - `Content-Type`: `application/json`
  - `Authorization`: `Bearer {{ $env.WAHA_API_KEY }}`
- **Body**:
```json
{
  "text": "{{ $json.response.content }}"
}
```

### Step 3: Configure WAHA Webhook

Konfigurasi WAHA untuk mengirim webhook ke n8n:

```bash
# Start WAHA session dengan webhook
curl -X POST http://localhost:3000/api/sessions/invoice_bot_session/start \
  -H "Content-Type: application/json" \
  -d '{
    "config": {
      "webhooks": [
        {
          "url": "http://localhost:5678/webhook/whatsapp-invoice-bot",
          "events": ["message", "message.any"]
        }
      ]
    }
  }'
```

## 🔗 Environment Variables untuk n8n

Set di n8n Settings → Environment Variables:

```env
WAHA_URL=http://localhost:3000
WAHA_API_KEY=your_waha_api_key
PYTHON_BOT_URL=http://localhost:8000
WHATSAPP_SESSION_NAME=invoice_bot_session
```

## 🧪 Testing Setup

### Test 1: Basic Webhook
```bash
curl -X POST http://localhost:5678/webhook/whatsapp-invoice-bot \
  -H "Content-Type: application/json" \
  -d '{
    "event": "message",
    "data": {
      "from": "6281234567890@c.us",
      "type": "text",
      "body": "start",
      "timestamp": "2025-10-14T12:00:00Z"
    }
  }'
```

### Test 2: Image Message
```bash
curl -X POST http://localhost:5678/webhook/whatsapp-invoice-bot \
  -H "Content-Type: application/json" \
  -d '{
    "event": "message",
    "data": {
      "from": "6281234567890@c.us",
      "type": "image",
      "id": "message_id_123",
      "mediaUrl": "https://example.com/image.jpg",
      "timestamp": "2025-10-14T12:00:00Z"
    }
  }'
```

## 🔄 Workflow Flow

1. **WhatsApp User** mengirim pesan
2. **WAHA** menerima pesan dari WhatsApp
3. **WAHA** kirim webhook ke **n8n**
4. **n8n** memproses dan forward ke **Python Bot**
5. **Python Bot** memproses pesan dan return response
6. **n8n** menerima response dari Python Bot
7. **n8n** kirim response ke **WAHA**
8. **WAHA** kirim response ke **WhatsApp User**

## 🛠️ Troubleshooting

### Common Issues

1. **Webhook tidak received**
   - Check n8n logs
   - Verify webhook URL accessible
   - Check WAHA webhook configuration

2. **Python Bot error**
   - Check Python Bot logs
   - Verify bot running on correct port
   - Check database connectivity

3. **WAHA connection issues**
   - Check WAHA session status
   - Verify WhatsApp QR code scanned
   - Check WAHA API key

### Debug Commands

```bash
# Check n8n workflows
curl http://localhost:5678/rest/workflows

# Check WAHA session status
curl http://localhost:3000/api/sessions/invoice_bot_session

# Check Python Bot status
curl http://localhost:8000/status

# Test webhook manually
curl -X POST http://localhost:8000/webhook/whatsapp \
  -H "Content-Type: application/json" \
  -d '{"event": "message", "data": {"from": "test", "type": "text", "body": "test"}}'
```

## 📊 Monitoring

Monitor workflow execution dalam n8n:
1. Buka n8n dashboard
2. Go to **Executions**
3. Filter by workflow name
4. Check execution logs untuk debugging

## 🔒 Security Considerations

1. **API Keys**: Store WAHA API key dengan aman
2. **Webhook Security**: Implementasi HMAC validation jika diperlukan
3. **Rate Limiting**: Set rate limits pada webhook endpoints
4. **Network Security**: Restrict access ke internal network saja

## 📱 Production Deployment

Untuk production:

1. **Use HTTPS** untuk semua webhook URLs
2. **Reverse Proxy** (nginx) untuk routing
3. **Process Managers** (PM2, systemd) untuk auto-restart
4. **Monitoring** (Prometheus, Grafana) untuk observability
5. **Backup Strategy** untuk n8n workflows dan database