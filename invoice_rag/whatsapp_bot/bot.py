#!/usr/bin/env python3
"""
WhatsApp Bot Main Module
Integrates with n8n workflows for message processing
"""

import os
import sys
import asyncio
import json
from pathlib import Path
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import uvicorn
from dotenv import load_dotenv

# Add project root to path before imports
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from whatsapp_bot.message_handler import WhatsAppMessageHandler  # noqa: E402
from whatsapp_bot.waha_client import WahaClient  # noqa: E402
from whatsapp_bot.n8n_client import N8nClient  # noqa: E402
from whatsapp_bot.platform_database import init_platform_tables  # noqa: E402

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="WhatsApp Invoice Bot", version="1.0.0")

# Initialize components
message_handler = WhatsAppMessageHandler()
waha_client = WahaClient()
n8n_client = N8nClient()


@app.on_event("startup")
async def startup_event():
    """Initialize bot on startup."""
    print("🚀 Starting WhatsApp Invoice Bot...")
    
    # Initialize database tables
    init_platform_tables()
    
    # Check WAHA connection
    try:
        status = await waha_client.get_session_status()
        if status != "WORKING":
            print("⚠️ WAHA session not active, attempting to start...")
            success = await waha_client.start_session()
            if success:
                print("✅ WAHA session started successfully")
                
                # Show QR code if needed
                qr_code = await waha_client.get_qr_code()
                if qr_code:
                    print("📱 Scan this QR code with WhatsApp:")
                    print(qr_code)
            else:
                print("❌ Failed to start WAHA session")
        else:
            print("✅ WAHA session is already active")
            
    except Exception as e:
        print(f"❌ Error connecting to WAHA: {e}")
    
    print("🤖 WhatsApp Bot is ready!")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    print("🛑 Shutting down WhatsApp Bot...")


@app.get("/")
async def root():
    """Health check endpoint."""
    return {"message": "WhatsApp Invoice Bot is running", "status": "healthy"}


@app.get("/status")
async def get_status():
    """Get bot and WAHA status."""
    try:
        waha_status = await waha_client.get_session_status()
        session_info = await waha_client.get_session_info()
        
        return {
            "bot_status": "running",
            "waha_status": waha_status,
            "session_info": session_info,
            "n8n_configured": bool(os.getenv("N8N_WEBHOOK_URL"))
        }
    except Exception as e:
        return {
            "bot_status": "running",
            "waha_status": "error",
            "error": str(e)
        }


@app.post("/webhook/whatsapp")
async def handle_whatsapp_webhook(request: Request):
    """Handle incoming WhatsApp webhooks from n8n."""
    try:
        # Get request data
        webhook_data = await request.json()
        
        # Log incoming webhook (for debugging)
        print(f"📨 Received webhook: {json.dumps(webhook_data, indent=2)}")
        
        # Extract message data
        if 'event' in webhook_data and webhook_data['event'] == 'message':
            # Handle incoming message
            response = await message_handler.handle_webhook_message(webhook_data)
            
            if 'error' in response:
                return JSONResponse(
                    status_code=400,
                    content={"error": response['error']}
                )
            
            # Send response via WAHA
            if response.get('response_type') == 'text':
                success = await waha_client.send_text_message(
                    response['phone'],
                    response['content']
                )
            elif response.get('response_type') == 'image':
                image_path = response.get('image_path')
                if image_path:
                    success = await waha_client.send_image(
                        response['phone'],
                        image_path,
                        response.get('content', '')
                    )
                else:
                    success = False
            else:
                success = False
            
            if success:
                return {"status": "success", "message": "Response sent"}
            else:
                return JSONResponse(
                    status_code=500,
                    content={"error": "Failed to send response"}
                )
        
        # Handle other webhook events
        return {"status": "ignored", "message": "Event type not handled"}
        
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON")
    except Exception as e:
        print(f"❌ Webhook error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/webhook/n8n")
async def handle_n8n_webhook(request: Request):
    """Alternative endpoint for direct n8n integration."""
    try:
        webhook_data = await request.json()
        
        # Process the message
        response = await message_handler.handle_webhook_message(webhook_data)
        
        # Return response for n8n to process
        return {
            "status": "success",
            "response": response
        }
        
    except Exception as e:
        print(f"❌ n8n webhook error: {e}")
        return {
            "status": "error",
            "error": str(e)
        }


@app.post("/send/text")
async def send_text_message(request: Request):
    """Manual endpoint to send text messages (for testing)."""
    try:
        data = await request.json()
        phone = data.get('phone')
        text = data.get('text')
        
        if not phone or not text:
            raise HTTPException(status_code=400, detail="Phone and text are required")
        
        success = await waha_client.send_text_message(phone, text)
        
        if success:
            return {"status": "success", "message": "Text sent"}
        else:
            return JSONResponse(
                status_code=500,
                content={"error": "Failed to send text"}
            )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/send/image")
async def send_image_message(request: Request):
    """Manual endpoint to send image messages (for testing)."""
    try:
        data = await request.json()
        phone = data.get('phone')
        image_path = data.get('image_path')
        caption = data.get('caption', '')
        
        if not phone or not image_path:
            raise HTTPException(status_code=400, detail="Phone and image_path are required")
        
        success = await waha_client.send_image(phone, image_path, caption)
        
        if success:
            return {"status": "success", "message": "Image sent"}
        else:
            return JSONResponse(
                status_code=500,
                content={"error": "Failed to send image"}
            )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/qr")
async def get_qr_code():
    """Get QR code for WhatsApp pairing."""
    try:
        qr_code = await waha_client.get_qr_code()
        if qr_code:
            return {"qr_code": qr_code}
        else:
            return {"message": "No QR code available (session may be active)"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def main():
    """Main function to run the WhatsApp bot server."""
    # Get configuration
    host = os.getenv("WHATSAPP_BOT_HOST", "0.0.0.0")
    port = int(os.getenv("WHATSAPP_BOT_PORT", "8000"))
    
    print(f"🚀 Starting WhatsApp Bot server on {host}:{port}")
    
    # Configure uvicorn
    config = uvicorn.Config(
        app,
        host=host,
        port=port,
        log_level="info",
        reload=False
    )
    
    server = uvicorn.Server(config)
    await server.serve()


if __name__ == "__main__":
    asyncio.run(main())