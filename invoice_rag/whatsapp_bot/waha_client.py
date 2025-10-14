#!/usr/bin/env python3
"""
WAHA Client for WhatsApp Bot
Wrapper for WAHA (WhatsApp HTTP API) interactions
"""

import os
import aiohttp
from typing import Dict, Any, Optional
from dotenv import load_dotenv
import base64

# Load environment variables
load_dotenv()


class WahaClient:
    """Client for communicating with WAHA WhatsApp API."""
    
    def __init__(self):
        self.base_url = os.getenv("WAHA_URL", "http://localhost:3000")
        self.api_key = os.getenv("WAHA_API_KEY")
        self.session_name = os.getenv("WHATSAPP_SESSION_NAME", "invoice_bot_session")
        
    async def _make_request(self, method: str, endpoint: str, data: Dict[str, Any] | None = None) -> Optional[Dict[str, Any]]:
        """Make HTTP request to WAHA API."""
        url = f"{self.base_url}{endpoint}"
        headers = {
            "Content-Type": "application/json"
        }
        
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
            
        try:
            async with aiohttp.ClientSession() as session:
                if method.upper() == "GET":
                    async with session.get(url, headers=headers) as response:
                        return await self._handle_response(response)
                elif method.upper() == "POST":
                    async with session.post(url, json=data, headers=headers) as response:
                        return await self._handle_response(response)
                elif method.upper() == "DELETE":
                    async with session.delete(url, headers=headers) as response:
                        return await self._handle_response(response)
                        
        except Exception as e:
            print(f"WAHA API error: {e}")
            return None
    
    async def _handle_response(self, response: aiohttp.ClientResponse) -> Optional[Dict[str, Any]]:
        """Handle HTTP response from WAHA API."""
        try:
            if response.status == 200:
                return await response.json()
            else:
                error_text = await response.text()
                print(f"WAHA API error {response.status}: {error_text}")
                return None
        except Exception as e:
            print(f"Error parsing WAHA response: {e}")
            return None

    async def start_session(self) -> bool:
        """Start WhatsApp session."""
        result = await self._make_request("POST", f"/api/sessions/{self.session_name}/start", {
            "config": {
                "webhooks": [
                    {
                        "url": os.getenv("N8N_WEBHOOK_URL"),
                        "events": ["message", "message.any"],
                        "hmac": None
                    }
                ]
            }
        })
        return result is not None

    async def get_session_status(self) -> Optional[str]:
        """Get current session status."""
        result = await self._make_request("GET", f"/api/sessions/{self.session_name}")
        return result.get("status") if result else None

    async def get_qr_code(self) -> Optional[str]:
        """Get QR code for WhatsApp pairing."""
        result = await self._make_request("GET", f"/api/sessions/{self.session_name}/auth/qr")
        return result.get("qr") if result else None

    async def stop_session(self) -> bool:
        """Stop WhatsApp session."""
        result = await self._make_request("DELETE", f"/api/sessions/{self.session_name}/stop")
        return result is not None

    async def send_text_message(self, phone: str, text: str) -> bool:
        """Send text message via WhatsApp."""
        # Ensure phone number format (include country code)
        if not phone.startswith("+"):
            phone = f"+{phone}"
        
        data = {
            "chatId": f"{phone.replace('+', '')}@c.us",
            "text": text
        }
        
        result = await self._make_request("POST", f"/api/sessions/{self.session_name}/chats/{data['chatId']}/messages/text", data)
        return result is not None

    async def send_image(self, phone: str, image_path: str, caption: str | None = None) -> bool:
        """Send image with optional caption via WhatsApp."""
        # Ensure phone number format
        if not phone.startswith("+"):
            phone = f"+{phone}"
            
        # Convert image to base64
        try:
            with open(image_path, "rb") as image_file:
                base64_image = base64.b64encode(image_file.read()).decode()
        except Exception as e:
            print(f"Error reading image file: {e}")
            return False
        
        data = {
            "chatId": f"{phone.replace('+', '')}@c.us",
            "file": {
                "mimetype": "image/jpeg",
                "filename": os.path.basename(image_path),
                "data": f"data:image/jpeg;base64,{base64_image}"
            }
        }
        
        if caption:
            data["caption"] = caption
        
        result = await self._make_request("POST", f"/api/sessions/{self.session_name}/chats/{data['chatId']}/messages/image", data)
        return result is not None

    async def download_media(self, media_id: str, save_path: str) -> bool:
        """Download media file from WhatsApp."""
        result = await self._make_request("GET", f"/api/sessions/{self.session_name}/chats/messages/{media_id}/media")
        
        if result and "data" in result:
            try:
                # Decode base64 data and save to file
                media_data = base64.b64decode(result["data"])
                with open(save_path, "wb") as f:
                    f.write(media_data)
                return True
            except Exception as e:
                print(f"Error saving media file: {e}")
                return False
        
        return False

    async def get_session_info(self) -> Optional[Dict[str, Any]]:
        """Get detailed session information."""
        return await self._make_request("GET", f"/api/sessions/{self.session_name}")