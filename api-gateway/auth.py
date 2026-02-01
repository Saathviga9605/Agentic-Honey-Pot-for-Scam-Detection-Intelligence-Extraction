"""
Authentication module for API Gateway
Handles API key validation for incoming requests
"""

import os
from typing import Optional

# Valid API keys (in production, use environment variables or secure vault)
VALID_API_KEYS = {
    "test-key-123",
    "guvi-honeypot-key",
    os.getenv("API_KEY", "default-dev-key")
}


def validate_api_key(api_key: Optional[str]) -> bool:
    """
    Validate incoming API key
    
    Args:
        api_key: API key from request header
        
    Returns:
        True if valid, False otherwise
    """
    if not api_key:
        return False
    
    return api_key in VALID_API_KEYS


def get_authentication_error():
    """Return authentication error response"""
    return {
        "status": "error",
        "message": "Invalid or missing API key",
        "code": 401
    }
