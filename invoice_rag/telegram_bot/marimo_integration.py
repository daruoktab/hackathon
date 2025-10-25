"""
Integration module for Telegram bot to generate interactive Marimo dashboard links.
"""

import requests
import logging
from typing import Optional, Dict

logger = logging.getLogger(__name__)

MARIMO_SERVER_URL = "http://127.0.0.1:5001"


def create_interactive_dashboard(user_id: Optional[int] = None) -> Dict:
    """
    Create an interactive Marimo dashboard session for a user.
    
    Args:
        user_id: Telegram user ID (optional)
    
    Returns:
        Dictionary with:
        - success: bool
        - url: str (dashboard URL)
        - session_id: str
        - expires_at: str (ISO timestamp)
        - error: str (if failed)
    """
    try:
        payload = {}
        if user_id:
            payload['user_id'] = user_id
        
        response = requests.post(
            f"{MARIMO_SERVER_URL}/api/dashboard/create",
            json=payload,
            timeout=60  # Increased timeout for Marimo startup (was 30)
        )
        
        if response.status_code == 201:
            data = response.json()
            return {
                'success': True,
                'url': data['url'],
                'session_id': data['session_id'],
                'expires_at': data['expires_at'],
                'timeout_minutes': data['timeout_minutes']
            }
        else:
            error_msg = response.json().get('error', 'Unknown error')
            logger.error(f"Failed to create dashboard: {error_msg}")
            return {
                'success': False,
                'error': error_msg
            }
    
    except requests.exceptions.ConnectionError:
        logger.error("Cannot connect to Marimo server. Is it running?")
        return {
            'success': False,
            'error': "Dashboard server is not available. Please contact admin."
        }
    except Exception as e:
        logger.error(f"Error creating dashboard: {e}")
        return {
            'success': False,
            'error': str(e)
        }


def get_dashboard_info(session_id: str) -> Dict:
    """
    Get information about an existing dashboard session.
    
    Args:
        session_id: The session ID
    
    Returns:
        Dictionary with dashboard info or error
    """
    try:
        response = requests.get(
            f"{MARIMO_SERVER_URL}/api/dashboard/{session_id}",
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            return {
                'success': True,
                **data
            }
        else:
            return {
                'success': False,
                'error': 'Session not found or expired'
            }
    
    except Exception as e:
        logger.error(f"Error getting dashboard info: {e}")
        return {
            'success': False,
            'error': str(e)
        }


def terminate_dashboard(session_id: str) -> bool:
    """
    Terminate a dashboard session.
    
    Args:
        session_id: The session ID to terminate
    
    Returns:
        True if successful, False otherwise
    """
    try:
        response = requests.delete(
            f"{MARIMO_SERVER_URL}/api/dashboard/{session_id}/terminate",
            timeout=5
        )
        
        return response.status_code == 200
    
    except Exception as e:
        logger.error(f"Error terminating dashboard: {e}")
        return False


def check_server_health() -> bool:
    """
    Check if the Marimo server is running and healthy.
    
    Returns:
        True if server is healthy, False otherwise
    """
    try:
        response = requests.get(
            f"{MARIMO_SERVER_URL}/health",
            timeout=5
        )
        
        return response.status_code == 200
    
    except Exception:
        return False


def get_user_friendly_url(session_id: str, base_url: str = "http://127.0.0.1:5001") -> str:
    """
    Get a user-friendly redirect URL for a dashboard session.
    
    Args:
        session_id: The session ID
        base_url: Base URL of the Marimo server
    
    Returns:
        User-friendly URL that redirects to the dashboard
    """
    return f"{base_url}/d/{session_id}"
