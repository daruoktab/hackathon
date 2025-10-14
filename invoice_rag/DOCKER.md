# 🐳 Docker Quick Start Guide

## 🚀 Option 1: Full Stack dengan Docker Compose

### Prerequisites
- Docker dan Docker Compose terinstall
- File `.env` sudah dikonfigurasi

### Jalankan Semua Services
```bash
# Clone repository
git clone <your-repo-url>
cd hackathon/invoice_rag

# Copy dan edit environment variables
cp .env.example .env
# Edit .env dengan API keys Anda

# Jalankan WhatsApp Bot + WAHA + n8n
docker-compose up -d

# Atau jalankan dengan Telegram Bot juga
docker-compose --profile telegram up -d

# Atau jalankan dengan Web App juga  
docker-compose --profile web --profile telegram up -d
```

### Setup WhatsApp (Setelah containers running)
1. **Import n8n workflow**:
   - Buka http://localhost:5678
   - Import `n8n_workflows/whatsapp-message-processor.json`

2. **Scan QR Code**:
   - Buka http://localhost:8000/qr
   - Scan QR code dengan WhatsApp

3. **Test**:
   - Kirim pesan `start` ke nomor WhatsApp Anda

## 🛠️ Option 2: Development Setup

### 1. Setup Individual Services
```bash
# Start WAHA
docker run -d --name waha -p 3000:3000 devlikeapro/waha

# Start n8n
docker run -d --name n8n -p 5678:5678 n8nio/n8n

# Install Python dependencies
pip install -r requirements.txt

# Run WhatsApp bot
python run_whatsapp_bot.py

# Run Telegram bot (separate terminal)
python run_bot.py
```

## 📊 Service URLs

| Service | URL | Description |
|---------|-----|-------------|
| WhatsApp Bot API | http://localhost:8000 | FastAPI server |
| WAHA Dashboard | http://localhost:3000 | WhatsApp HTTP API |
| n8n Workflows | http://localhost:5678 | Workflow automation |
| Streamlit Web App | http://localhost:8501 | Web interface |

## 🧪 Testing

### Test WhatsApp Bot
```bash
# Check bot status
curl http://localhost:8000/status

# Get QR code
curl http://localhost:8000/qr

# Test webhook
curl -X POST http://localhost:8000/webhook/whatsapp \
  -H "Content-Type: application/json" \
  -d '{"event": "message", "data": {"from": "test", "type": "text", "body": "start"}}'
```

### Test n8n Workflow
```bash
# Test n8n webhook
curl -X POST http://localhost:5678/webhook/whatsapp-invoice-bot \
  -H "Content-Type: application/json" \
  -d '{"event": "message", "data": {"from": "6281234567890@c.us", "type": "text", "body": "start"}}'
```

## 🔧 Troubleshooting

### Common Issues

1. **WAHA tidak connect**:
   ```bash
   docker logs waha
   # Check QR code scan status
   ```

2. **n8n workflow error**:
   ```bash
   docker logs n8n
   # Check workflow import dan configuration
   ```

3. **WhatsApp bot error**:
   ```bash
   docker logs invoice-whatsapp-bot
   # Check environment variables
   ```

### Restart Services
```bash
# Restart semua services
docker-compose restart

# Restart individual service
docker-compose restart whatsapp-bot
docker-compose restart waha
docker-compose restart n8n
```

## 📝 Logs

```bash
# View logs untuk semua services
docker-compose logs -f

# View logs untuk specific service
docker-compose logs -f whatsapp-bot
docker-compose logs -f waha
docker-compose logs -f n8n
```

## 🗄️ Data Persistence

Data disimpan dalam Docker volumes:
- `waha_data`: WhatsApp session data
- `n8n_data`: n8n workflows dan settings
- `./invoices.db`: SQLite database (bind mount)

## 🔒 Production Notes

Untuk production deployment:
1. Set proper environment variables
2. Use HTTPS dengan reverse proxy (nginx)
3. Configure proper networking
4. Set up monitoring dan logging
5. Regular backup untuk volumes