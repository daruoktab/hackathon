#!/usr/bin/env python3
"""
n8n Integration Module for WhatsApp Bot
Handles communication with n8n workflows
"""

import os
import aiohttp
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class N8nClient:
    """Client for communicating with n8n workflows."""
    
    def __init__(self):
        self.n8n_url = os.getenv("N8N_URL", "http://localhost:5678")
        self.webhook_url = os.getenv("N8N_WEBHOOK_URL")
        self.api_key = os.getenv("N8N_API_KEY")
        
    async def send_to_webhook(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Send data to n8n webhook endpoint."""
        if not self.webhook_url:
            print("Warning: N8N_WEBHOOK_URL not configured")
            return None
            
        headers = {
            "Content-Type": "application/json"
        }
        
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
            
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.webhook_url,
                    json=data,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        print(f"n8n webhook error: {response.status}")
                        return None
                        
        except Exception as e:
            print(f"Error sending to n8n webhook: {e}")
            return None
    
    async def trigger_workflow(self, workflow_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Trigger specific n8n workflow by ID."""
        if not self.api_key:
            print("Warning: N8N_API_KEY not configured")
            return None
            
        url = f"{self.n8n_url}/api/v1/workflows/{workflow_id}/execute"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url,
                    json={"data": data},
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        print(f"n8n workflow trigger error: {response.status}")
                        return None
                        
        except Exception as e:
            print(f"Error triggering n8n workflow: {e}")
            return None

    def format_whatsapp_message_for_n8n(self, phone: str, message_type: str, content: str, 
                                       media_url: str | None = None) -> Dict[str, Any]:
        """Format WhatsApp message data for n8n processing."""
        return {
            "platform": "whatsapp",
            "phone": phone,
            "message_type": message_type,  # "text", "image", "document"
            "content": content,
            "media_url": media_url,
            "timestamp": "",  # Will be added by n8n
            "action": "process_message"
        }

    def format_bot_response_for_n8n(self, phone: str, response_type: str, 
                                   content: str, image_path: str | None = None) -> Dict[str, Any]:
        """Format bot response for n8n to send via WAHA."""
        return {
            "platform": "whatsapp", 
            "phone": phone,
            "response_type": response_type,  # "text", "image", "document"
            "content": content,
            "image_path": image_path,
            "action": "send_response"
        }