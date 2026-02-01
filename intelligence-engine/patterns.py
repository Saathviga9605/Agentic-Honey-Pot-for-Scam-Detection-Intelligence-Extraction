"""
Pattern definitions for intelligence extraction
Contains regex patterns and keywords for detecting scam indicators
"""

import re
from typing import Dict, List

# Regex patterns for extracting entities
PATTERNS = {
    "upi_id": [
        r'\b[a-zA-Z0-9._-]+@[a-zA-Z]+\b',  # username@bank
        r'\b\d{10}@[a-zA-Z]+\b'  # phone@bank
    ],
    
    "bank_account": [
        r'\b\d{9,18}\b',  # 9-18 digit account numbers
        r'\b[Aa]c+ount\s*[:#]?\s*(\d{9,18})\b'
    ],
    
    "phone_number": [
        r'\b\+?91[-\s]?\d{10}\b',  # Indian format
        r'\b\d{10}\b',  # 10 digit numbers
        r'\b\+\d{1,3}[-\s]?\d{8,15}\b'  # International
    ],
    
    "url": [
        r'https?://[^\s]+',
        r'www\.[^\s]+',
        r'\b[a-zA-Z0-9-]+\.(com|net|org|in|co\.in)[^\s]*\b'
    ],
    
    "ifsc_code": [
        r'\b[A-Z]{4}0[A-Z0-9]{6}\b'
    ]
}

# Suspicious keywords indicating scam tactics
SUSPICIOUS_KEYWORDS = {
    "urgency": [
        "urgent", "immediately", "now", "quick", "fast", "hurry",
        "expire", "expiring", "limited time", "today only", "last chance"
    ],
    
    "threats": [
        "block", "blocked", "suspend", "suspended", "close", "closed",
        "deactivate", "deactivated", "terminate", "terminated", "freeze",
        "legal action", "police", "arrest", "fine", "penalty"
    ],
    
    "verification": [
        "verify", "verification", "confirm", "confirmation", "update",
        "authenticate", "validation", "check", "review", "validate"
    ],
    
    "payment": [
        "pay", "payment", "transfer", "send money", "refund", "credit",
        "debit", "transaction", "amount", "rupees", "rs", "inr"
    ],
    
    "impersonation": [
        "bank", "official", "customer care", "support team", "security team",
        "government", "tax department", "income tax", "rbi", "sebi",
        "authorized", "representative"
    ],
    
    "credential_request": [
        "password", "pin", "otp", "cvv", "card number", "atm pin",
        "account number", "login", "username", "credentials"
    ]
}


def compile_patterns() -> Dict[str, List[re.Pattern]]:
    """
    Compile all regex patterns for efficiency
    
    Returns:
        Dictionary of compiled patterns
    """
    compiled = {}
    for key, pattern_list in PATTERNS.items():
        compiled[key] = [re.compile(pattern, re.IGNORECASE) for pattern in pattern_list]
    return compiled


def get_keyword_categories() -> Dict[str, List[str]]:
    """Get all keyword categories"""
    return SUSPICIOUS_KEYWORDS


# Precompile patterns on module load
COMPILED_PATTERNS = compile_patterns()
