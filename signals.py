"""
Signal definitions and enums for scam detection.
Each signal represents a specific scam indicator.
"""

from enum import Enum


class SignalType(Enum):
    """Machine-readable signal identifiers"""
    
    # Urgency / Pressure signals
    URGENCY = "urgency"
    TIME_PRESSURE = "time_pressure"
    DEADLINE = "deadline"
    IMMEDIATE_ACTION = "immediate_action"
    
    # Account / Authority Threats
    ACCOUNT_THREAT = "account_threat"
    ACCOUNT_SUSPENSION = "account_suspension"
    KYC_FAILURE = "kyc_failure"
    AUTHORITY_IMPERSONATION = "authority_impersonation"
    BANK_IMPERSONATION = "bank_impersonation"
    GOVERNMENT_IMPERSONATION = "government_impersonation"
    
    # Payment Requests
    PAYMENT_REQUEST = "payment_request"
    UPI_REQUEST = "upi_request"
    OTP_REQUEST = "otp_request"
    ACCOUNT_NUMBER_REQUEST = "account_number_request"
    CARD_DETAILS_REQUEST = "card_details_request"
    PIN_REQUEST = "pin_request"
    
    # Phishing / Redirection
    PHISHING = "phishing"
    SUSPICIOUS_LINK = "suspicious_link"
    SHORTENED_URL = "shortened_url"
    LOGIN_REQUEST = "login_request"
    VERIFY_LINK = "verify_link"
    MISSPELLED_DOMAIN = "misspelled_domain"
    
    # Conversation Patterns
    REPETITION = "repetition"
    ESCALATION = "escalation"
    IGNORING_QUESTIONS = "ignoring_questions"
    COPY_PASTE = "copy_paste"
    DEFLECTION = "deflection"


class SignalCategory(Enum):
    """Grouping of signals into broader categories"""
    URGENCY_PRESSURE = "urgency_pressure"
    ACCOUNT_AUTHORITY = "account_authority"
    PAYMENT = "payment"
    PHISHING = "phishing"
    CONVERSATION = "conversation"


# Map signals to categories for scoring
SIGNAL_TO_CATEGORY = {
    # Urgency/Pressure
    SignalType.URGENCY: SignalCategory.URGENCY_PRESSURE,
    SignalType.TIME_PRESSURE: SignalCategory.URGENCY_PRESSURE,
    SignalType.DEADLINE: SignalCategory.URGENCY_PRESSURE,
    SignalType.IMMEDIATE_ACTION: SignalCategory.URGENCY_PRESSURE,
    
    # Account/Authority
    SignalType.ACCOUNT_THREAT: SignalCategory.ACCOUNT_AUTHORITY,
    SignalType.ACCOUNT_SUSPENSION: SignalCategory.ACCOUNT_AUTHORITY,
    SignalType.KYC_FAILURE: SignalCategory.ACCOUNT_AUTHORITY,
    SignalType.AUTHORITY_IMPERSONATION: SignalCategory.ACCOUNT_AUTHORITY,
    SignalType.BANK_IMPERSONATION: SignalCategory.ACCOUNT_AUTHORITY,
    SignalType.GOVERNMENT_IMPERSONATION: SignalCategory.ACCOUNT_AUTHORITY,
    
    # Payment
    SignalType.PAYMENT_REQUEST: SignalCategory.PAYMENT,
    SignalType.UPI_REQUEST: SignalCategory.PAYMENT,
    SignalType.OTP_REQUEST: SignalCategory.PAYMENT,
    SignalType.ACCOUNT_NUMBER_REQUEST: SignalCategory.PAYMENT,
    SignalType.CARD_DETAILS_REQUEST: SignalCategory.PAYMENT,
    SignalType.PIN_REQUEST: SignalCategory.PAYMENT,
    
    # Phishing
    SignalType.PHISHING: SignalCategory.PHISHING,
    SignalType.SUSPICIOUS_LINK: SignalCategory.PHISHING,
    SignalType.SHORTENED_URL: SignalCategory.PHISHING,
    SignalType.LOGIN_REQUEST: SignalCategory.PHISHING,
    SignalType.VERIFY_LINK: SignalCategory.PHISHING,
    SignalType.MISSPELLED_DOMAIN: SignalCategory.PHISHING,
    
    # Conversation
    SignalType.REPETITION: SignalCategory.CONVERSATION,
    SignalType.ESCALATION: SignalCategory.CONVERSATION,
    SignalType.IGNORING_QUESTIONS: SignalCategory.CONVERSATION,
    SignalType.COPY_PASTE: SignalCategory.CONVERSATION,
    SignalType.DEFLECTION: SignalCategory.CONVERSATION,
}


# Base weights for each signal (used in scoring)
SIGNAL_WEIGHTS = {
    # High severity signals
    SignalType.OTP_REQUEST: 0.40,
    SignalType.PIN_REQUEST: 0.40,
    SignalType.CARD_DETAILS_REQUEST: 0.35,
    SignalType.ACCOUNT_NUMBER_REQUEST: 0.30,
    SignalType.UPI_REQUEST: 0.30,
    
    # Medium-high severity
    SignalType.ACCOUNT_SUSPENSION: 0.25,
    SignalType.SUSPICIOUS_LINK: 0.22,
    SignalType.VERIFY_LINK: 0.20,
    SignalType.SHORTENED_URL: 0.20,
    
    # Medium severity
    SignalType.AUTHORITY_IMPERSONATION: 0.18,
    SignalType.BANK_IMPERSONATION: 0.18,
    SignalType.GOVERNMENT_IMPERSONATION: 0.18,
    SignalType.KYC_FAILURE: 0.18,
    SignalType.ACCOUNT_THREAT: 0.18,
    SignalType.PAYMENT_REQUEST: 0.18,
    
    # Lower severity (more context needed)
    SignalType.URGENCY: 0.12,
    SignalType.TIME_PRESSURE: 0.12,
    SignalType.DEADLINE: 0.12,
    SignalType.IMMEDIATE_ACTION: 0.12,
    SignalType.LOGIN_REQUEST: 0.12,
    SignalType.PHISHING: 0.12,
    
    # Conversation patterns (need multiple turns)
    SignalType.REPETITION: 0.10,
    SignalType.ESCALATION: 0.15,
    SignalType.IGNORING_QUESTIONS: 0.12,
    SignalType.COPY_PASTE: 0.10,
    SignalType.DEFLECTION: 0.10,
    SignalType.MISSPELLED_DOMAIN: 0.18,
}


def get_signal_weight(signal: SignalType) -> float:
    """Get the base weight for a signal"""
    return SIGNAL_WEIGHTS.get(signal, 0.10)


def get_signal_category(signal: SignalType) -> SignalCategory:
    """Get the category for a signal"""
    return SIGNAL_TO_CATEGORY.get(signal, SignalCategory.CONVERSATION)
