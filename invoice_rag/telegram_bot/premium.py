"""
Premium Feature Management Module
Handles JWT validation, token claims, and premium subscription management
"""
import os
import jwt
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any, Tuple
from dotenv import load_dotenv

load_dotenv()

# JWT Configuration
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "change-this-secret-key")
JWT_ALGORITHM = "HS256"

def validate_jwt_token(token: str) -> Tuple[bool, Optional[Dict[str, Any]], str]:
    """
    Validate JWT token signature and expiry.
    
    Args:
        token: JWT token string
    
    Returns:
        Tuple of (is_valid, decoded_payload, error_message)
    """
    try:
        # Decode and verify JWT
        payload = jwt.decode(
            token,
            JWT_SECRET_KEY,
            algorithms=[JWT_ALGORITHM]
        )
        
        # Check expiry (exp claim)
        if 'exp' in payload:
            exp_timestamp = payload['exp']
            exp_datetime = datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)
            
            if datetime.now(timezone.utc) > exp_datetime:
                return False, None, "Token has expired"
        
        return True, payload, ""
    
    except jwt.ExpiredSignatureError:
        return False, None, "Token has expired"
    except jwt.InvalidSignatureError:
        return False, None, "Invalid token signature"
    except jwt.DecodeError:
        return False, None, "Invalid token format"
    except Exception as e:
        return False, None, f"Token validation error: {str(e)}"

def parse_duration_from_jwt(payload: Dict[str, Any]) -> int:
    """
    Parse duration from JWT payload.
    Expected format: payload['duration'] = '7 days' or '30 days'
    
    Args:
        payload: Decoded JWT payload
    
    Returns:
        Number of days for premium access
    """
    duration_str = payload.get('duration', '7 days')
    
    # Parse duration string (e.g., '7 days', '30 days')
    parts = duration_str.lower().split()
    
    if len(parts) >= 2:
        try:
            number = int(parts[0])
            unit = parts[1]
            
            if 'day' in unit:
                return number
            elif 'week' in unit:
                return number * 7
            elif 'month' in unit:
                return number * 30
        except ValueError:
            pass
    
    # Default to 7 days if parsing fails
    return 7

def check_premium_access(session, telegram_user_id: str) -> Dict[str, Any]:
    """
    Check if user has active premium access and provide status info.
    
    Args:
        session: Database session
        telegram_user_id: Telegram user ID
    
    Returns:
        Dict with premium status information
    """
    from src.database import get_or_create_user, User, PremiumData, AccountStatus
    
    # Get or create user
    user = get_or_create_user(session, telegram_user_id)
    
    # Check if user is premium
    if user.status_account != AccountStatus.PREMIUM:
        return {
            'is_premium': False,
            'status': 'Free',
            'message': '🆓 You are on the Free plan.\n\n💎 Upgrade to Premium to unlock advanced features!'
        }
    
    # Get premium data
    premium_data = session.query(PremiumData).filter_by(user_id=user.id).first()
    
    if not premium_data:
        # User marked as premium but no data -> downgrade
        user.status_account = AccountStatus.FREE
        session.commit()
        return {
            'is_premium': False,
            'status': 'Free',
            'message': '🆓 Your premium access has expired.\n\n💎 Upgrade again to continue using premium features!'
        }
    
    # Check expiry
    now = datetime.now(timezone.utc)
    
    # Ensure expired_at has timezone info for comparison
    expired_at = premium_data.expired_at
    if expired_at.tzinfo is None:
        # If stored without timezone, assume UTC
        expired_at = expired_at.replace(tzinfo=timezone.utc)
    
    if now > expired_at:
        # Expired -> downgrade
        user.status_account = AccountStatus.FREE
        session.commit()
        return {
            'is_premium': False,
            'status': 'Free',
            'message': '⏰ Your premium subscription expired.\n\n💎 Renew to continue using premium features!'
        }
    
    # Calculate remaining days
    remaining = expired_at - now
    remaining_days = remaining.days
    
    return {
        'is_premium': True,
        'status': 'Premium',
        'expires_at': expired_at,
        'remaining_days': remaining_days,
        'method': premium_data.premium_for,
        'message': (
            f'💎 Premium Account Active\n\n'
            f'⏰ Expires: {expired_at.strftime("%Y-%m-%d %H:%M UTC")}\n'
            f'📅 Days remaining: {remaining_days}\n'
            f'🎫 Activated via: {premium_data.premium_for}'
        )
    }

def claim_token(session, telegram_user_id: str, jwt_token: str) -> Dict[str, Any]:
    """
    Process token claim request.
    
    Args:
        session: Database session
        telegram_user_id: Telegram user ID
        jwt_token: JWT token string from user
    
    Returns:
        Dict with claim result
    """
    from src.database import is_token_used, mark_token_used, activate_premium
    
    # Step 1: Validate JWT
    is_valid, payload, error_msg = validate_jwt_token(jwt_token)
    
    if not is_valid:
        return {
            'success': False,
            'message': f'❌ Token validation failed:\n{error_msg}'
        }
    
    # Step 2: Check if token already used
    if is_token_used(session, jwt_token):
        return {
            'success': False,
            'message': '❌ This token has already been claimed.\n\n🎫 Each token can only be used once.'
        }
    
    # Step 3: Parse duration from JWT
    duration_days = parse_duration_from_jwt(payload)
    
    # Step 4: Activate premium
    try:
        activate_premium(session, telegram_user_id, 'claim token', duration_days)
        
        # Mark token as used
        mark_token_used(session, jwt_token)
        
        return {
            'success': True,
            'duration_days': duration_days,
            'message': (
                f'✅ Token claimed successfully!\n\n'
                f'💎 Your account is now Premium\n'
                f'⏰ Duration: {duration_days} days\n\n'
                f'🎉 Enjoy your premium features!'
            )
        }
    except Exception as e:
        return {
            'success': False,
            'message': f'❌ Error activating premium:\n{str(e)}'
        }

def require_premium(session, telegram_user_id: str) -> Tuple[bool, str]:
    """
    Decorator-style function to check premium access.
    
    Args:
        session: Database session
        telegram_user_id: Telegram user ID
    
    Returns:
        Tuple of (has_access, message)
    """
    from src.database import is_user_premium
    
    if is_user_premium(session, telegram_user_id):
        return True, ""
    else:
        return False, (
            '🔒 This is a Premium Feature\n\n'
            '💎 Upgrade to Premium to access:\n'
            '  • Advanced analytics\n'
            '  • Detailed reports\n'
            '  • Export capabilities\n'
            '  • Priority support\n\n'
            '📱 Use /premium to upgrade!'
        )

# Generate JWT token (for testing/admin purposes)
def generate_test_token(duration_days: int = 7) -> str:
    """
    Generate a test JWT token with specified duration.
    FOR TESTING ONLY - Should be generated by payment/admin system in production.
    
    Args:
        duration_days: Number of days for premium access
    
    Returns:
        JWT token string
    """
    now = datetime.now(timezone.utc)
    expiry = now + timedelta(days=duration_days)
    
    payload = {
        'exp': int(expiry.timestamp()),
        'iat': int(now.timestamp()),
        'duration': f'{duration_days} days',
        'purpose': 'premium_claim'
    }
    
    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return token

if __name__ == "__main__":
    # Test token generation
    print("Generating test tokens...")
    print("\n7-day token:")
    print(generate_test_token(7))
    print("\n30-day token:")
    print(generate_test_token(30))
