"""
Pattern matching rules for scam signal detection.
Supports multiple languages and handles spelling variations.
"""

import re
from typing import List, Tuple
from signals import SignalType


class PatternRule:
    """A detection rule with patterns and associated signal"""
    
    def __init__(self, signal: SignalType, patterns: List[str], description: str, is_regex: bool = False):
        self.signal = signal
        self.patterns = patterns
        self.description = description
        self.is_regex = is_regex
        
        # Compile regex patterns for efficiency
        if is_regex:
            self.compiled_patterns = [re.compile(p, re.IGNORECASE) for p in patterns]
        else:
            # For simple keyword matching, normalize patterns
            self.normalized_patterns = [p.lower() for p in patterns]
    
    def matches(self, text: str) -> bool:
        """Check if the text matches any pattern in this rule"""
        text_normalized = text.lower()
        
        if self.is_regex:
            return any(pattern.search(text) for pattern in self.compiled_patterns)
        else:
            return any(pattern in text_normalized for pattern in self.normalized_patterns)


# =============================================================================
# URGENCY / PRESSURE PATTERNS
# =============================================================================

URGENCY_RULES = [
    PatternRule(
        signal=SignalType.URGENCY,
        patterns=[
            "urgent", "urgently", "immediate", "immediately", "asap", "right now",
            "hurry", "quick", "quickly", "fast", "tez", "jaldi", "turant"
        ],
        description="General urgency keywords"
    ),
    PatternRule(
        signal=SignalType.TIME_PRESSURE,
        patterns=[
            r"\b(within|in)\s+\d+\s+(hour|hours|minute|minutes|min|mins|hr|hrs)\b",
            r"\btoday\b", r"\btonite\b", r"\btonight\b",
            r"\b(by|before)\s+(today|tonight|tomorrow|end of day)\b",
            "expire", "expiring", "expiry", "limited time", "last chance"
        ],
        description="Time-based pressure",
        is_regex=True
    ),
    PatternRule(
        signal=SignalType.DEADLINE,
        patterns=[
            "deadline", "time limit", "countdown", "last day", "final notice",
            "before midnight", "by end of", "must complete by"
        ],
        description="Deadline-based threats"
    ),
    PatternRule(
        signal=SignalType.IMMEDIATE_ACTION,
        patterns=[
            "act now", "take action", "respond now", "reply immediately",
            "do it now", "submit now", "verify now", "update now", "confirm now"
        ],
        description="Demands for immediate action"
    ),
]


# =============================================================================
# ACCOUNT / AUTHORITY THREAT PATTERNS
# =============================================================================

ACCOUNT_THREAT_RULES = [
    PatternRule(
        signal=SignalType.ACCOUNT_THREAT,
        patterns=[
            "account blocked", "account suspended", "account locked", "account closed",
            "account deactivated", "account will be", "will block", "will suspend",
            "avoid suspension", "avoid blocking", "avoid closure", "prevent suspension",
            "खाता ब्लॉक", "खाता बंद", "account band", "block ho jayega"
        ],
        description="Account threat keywords"
    ),
    PatternRule(
        signal=SignalType.ACCOUNT_SUSPENSION,
        patterns=[
            r"(account|card|service).{0,20}(suspend|block|lock|close|deactivat|disable)",
            r"(suspend|block|lock|close|deactivat|disable).{0,20}(account|card|service)",
            r"(avoid|prevent|stop).{0,15}(suspension|blocking|closure|deactivation)",
            "avoid suspension", "prevent blocking", "stop deactivation", "account suspension"
        ],
        description="Account suspension patterns",
        is_regex=True
    ),
    PatternRule(
        signal=SignalType.KYC_FAILURE,
        patterns=[
            "kyc", "kyc failed", "kyc pending", "kyc expired", "kyc incomplete",
            "kyc verification", "update kyc", "complete kyc", "kyc update required",
            "know your customer", "customer verification failed"
        ],
        description="KYC-related threats"
    ),
    PatternRule(
        signal=SignalType.BANK_IMPERSONATION,
        patterns=[
            r"\b(state bank|sbi|hdfc|icici|axis bank|pnb|bank of|canara bank|union bank)\b",
            r"\byour bank\b", r"\bour bank\b", r"\bbanking (system|service|team)\b",
            "reserve bank", "rbi", "central bank", "federal bank"
        ],
        description="Bank impersonation",
        is_regex=True
    ),
    PatternRule(
        signal=SignalType.GOVERNMENT_IMPERSONATION,
        patterns=[
            "income tax", "tax department", "tax notice", "government", "govt",
            "ministry", "police", "cybercrime", "enforcement directorate",
            "uidai", "aadhaar", "pan card", "passport office"
        ],
        description="Government authority impersonation"
    ),
    PatternRule(
        signal=SignalType.AUTHORITY_IMPERSONATION,
        patterns=[
            "official", "authorized", "verified sender", "department",
            "customer care", "customer support", "technical support", "helpdesk",
            r"\b(from|this is).{0,15}(bank|government|police|tax|official)\b"
        ],
        description="General authority impersonation",
        is_regex=False
    ),
]


# =============================================================================
# PAYMENT REQUEST PATTERNS
# =============================================================================

PAYMENT_REQUEST_RULES = [
    PatternRule(
        signal=SignalType.UPI_REQUEST,
        patterns=[
            "upi", "upi id", "upi pin", "google pay", "gpay", "phonepe", "paytm",
            "bhim", "payment id", "vpa", "virtual payment",
            r"[a-zA-Z0-9._-]+@[a-zA-Z]+",  # UPI ID pattern
            "send payment", "make payment", "pay via upi"
        ],
        description="UPI and payment ID requests",
        is_regex=False
    ),
    PatternRule(
        signal=SignalType.OTP_REQUEST,
        patterns=[
            r"\botp\b", "one time password", "one-time password", "verification code",
            "security code", "authentication code", "sms code", "text code",
            r"\b\d{4}\b.*code", r"\b\d{6}\b.*code", "share otp", "send otp", "enter otp"
        ],
        description="OTP/verification code requests",
        is_regex=True
    ),
    PatternRule(
        signal=SignalType.ACCOUNT_NUMBER_REQUEST,
        patterns=[
            "account number", "bank account", "account no", "acct no", "a/c number",
            "ifsc", "ifsc code", "routing number", "sort code",
            r"\baccount\s*#", "provide account", "share account"
        ],
        description="Bank account number requests",
        is_regex=True
    ),
    PatternRule(
        signal=SignalType.CARD_DETAILS_REQUEST,
        patterns=[
            "card number", "debit card", "credit card", "card details", "cvv", "cvc",
            "card expiry", "expiry date", "card pin", "atm pin",
            r"\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}",  # Card number pattern
            "16 digit", "card info"
        ],
        description="Card details requests",
        is_regex=True
    ),
    PatternRule(
        signal=SignalType.PIN_REQUEST,
        patterns=[
            r"\bpin\b", "atm pin", "card pin", "security pin", "personal identification",
            "enter pin", "share pin", "provide pin", "send pin", "what is your pin"
        ],
        description="PIN requests",
        is_regex=True
    ),
    PatternRule(
        signal=SignalType.PAYMENT_REQUEST,
        patterns=[
            "send money", "transfer money", "make payment", "pay now", "payment required",
            "deposit", "remit", "wire transfer", "send funds", "transfer funds",
            r"pay\s+(rs|inr|₹)?\s*\d+", "paisa bhejo", "paise send"
        ],
        description="General payment requests",
        is_regex=True
    ),
]


# =============================================================================
# PHISHING / REDIRECTION PATTERNS
# =============================================================================

PHISHING_RULES = [
    PatternRule(
        signal=SignalType.SUSPICIOUS_LINK,
        patterns=[
            r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+",
            r"www\.[a-zA-Z0-9-]+\.[a-z]{2,}",
            "click here", "click link", "visit link", "open link", "tap link"
        ],
        description="URLs and link requests",
        is_regex=True
    ),
    PatternRule(
        signal=SignalType.SHORTENED_URL,
        patterns=[
            r"\b(bit\.ly|goo\.gl|tinyurl|short\.link|t\.co|ow\.ly|is\.gd|buff\.ly)/\S+",
            r"\bhttps?://[a-z0-9-]{1,10}\.[a-z]{2,3}/[a-zA-Z0-9]+\b"
        ],
        description="Shortened URL patterns",
        is_regex=True
    ),
    PatternRule(
        signal=SignalType.LOGIN_REQUEST,
        patterns=[
            "login", "log in", "sign in", "signin", "log into",
            "enter credentials", "username and password", "login details"
        ],
        description="Login credential requests"
    ),
    PatternRule(
        signal=SignalType.VERIFY_LINK,
        patterns=[
            "verify your", "verify account", "verify identity", "verification link",
            "confirm your", "validate your", "authenticate your",
            r"verify.{0,20}(click|link|here)", r"(click|link).{0,20}verify"
        ],
        description="Verification link patterns",
        is_regex=True
    ),
    PatternRule(
        signal=SignalType.MISSPELLED_DOMAIN,
        patterns=[
            r"\b(gooogle|yaahoo|amazzon|paypai|microosft|bankofindia|statebank)\b",
            r"\b[a-z]+-secure\.(com|net|org)\b",
            r"\bverify-[a-z]+\.(com|net)\b"
        ],
        description="Common domain misspellings",
        is_regex=True
    ),
]


# =============================================================================
# CONVERSATION PATTERN DETECTION (Multi-turn analysis)
# =============================================================================

def detect_repetition(messages: List[str]) -> bool:
    """Detect if scammer is repeating the same message"""
    if len(messages) < 2:
        return False
    
    # Check if last 2-3 messages are very similar
    recent_messages = messages[-3:]
    for i in range(len(recent_messages) - 1):
        similarity = _text_similarity(recent_messages[i], recent_messages[i + 1])
        if similarity > 0.8:  # 80% similar
            return True
    return False


def detect_escalation(messages: List[str]) -> bool:
    """Detect escalating threats across conversation"""
    if len(messages) < 2:
        return False
    
    threat_keywords = [
        "block", "suspend", "close", "deactivate", "legal", "action",
        "police", "arrest", "fine", "penalty", "last chance", "final"
    ]
    
    threat_counts = []
    for msg in messages:
        count = sum(1 for keyword in threat_keywords if keyword in msg.lower())
        threat_counts.append(count)
    
    # Check if threats are increasing
    if len(threat_counts) >= 2:
        return threat_counts[-1] > threat_counts[-2]
    
    return False


def detect_ignoring_questions(conversation_history: List[dict]) -> bool:
    """Detect if scammer ignores user questions and repeats demands"""
    if len(conversation_history) < 3:
        return False
    
    # Look for pattern: user asks question, scammer ignores and makes demand
    question_indicators = ["?", "why", "what", "how", "who", "when", "which"]
    demand_indicators = ["send", "provide", "share", "give", "submit", "enter"]
    
    for i in range(len(conversation_history) - 2):
        if conversation_history[i].get("sender") == "user":
            user_text = conversation_history[i].get("text", "").lower()
            has_question = any(ind in user_text for ind in question_indicators)
            
            if has_question and i + 1 < len(conversation_history):
                next_msg = conversation_history[i + 1].get("text", "").lower()
                scammer_ignores = not any(
                    word in next_msg for word in user_text.split()[:5]
                )
                makes_demand = any(ind in next_msg for ind in demand_indicators)
                
                if scammer_ignores and makes_demand:
                    return True
    
    return False


def detect_copy_paste(messages: List[str]) -> bool:
    """Detect exact copy-paste of messages"""
    if len(messages) < 2:
        return False
    
    # Check for exact duplicates
    seen = set()
    for msg in messages:
        normalized = msg.strip().lower()
        if normalized in seen:
            return True
        seen.add(normalized)
    
    return False


def _text_similarity(text1: str, text2: str) -> float:
    """Calculate simple similarity between two texts"""
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())
    
    if not words1 or not words2:
        return 0.0
    
    intersection = words1.intersection(words2)
    union = words1.union(words2)
    
    return len(intersection) / len(union) if union else 0.0


# =============================================================================
# MAIN RULE MATCHER
# =============================================================================

def detect_signals(text: str, conversation_history: List[dict] = None) -> Tuple[List[SignalType], dict]:
    """
    Detect all scam signals in the given text and conversation history.
    
    Args:
        text: The current message to analyze
        conversation_history: Optional list of previous messages
    
    Returns:
        Tuple of (detected_signals, explanations)
    """
    detected_signals = []
    explanations = {}
    
    # Combine all rule sets
    all_rules = URGENCY_RULES + ACCOUNT_THREAT_RULES + PAYMENT_REQUEST_RULES + PHISHING_RULES
    
    # Check each rule against the text
    for rule in all_rules:
        if rule.matches(text):
            if rule.signal not in detected_signals:
                detected_signals.append(rule.signal)
                explanations[rule.signal.value] = rule.description
    
    # Conversation pattern detection (requires history)
    if conversation_history:
        scammer_messages = [
            msg.get("text", "") for msg in conversation_history 
            if msg.get("sender") == "scammer"
        ]
        scammer_messages.append(text)  # Add current message
        
        if detect_repetition(scammer_messages):
            detected_signals.append(SignalType.REPETITION)
            explanations[SignalType.REPETITION.value] = "Scammer is repeating similar messages"
        
        if detect_escalation(scammer_messages):
            detected_signals.append(SignalType.ESCALATION)
            explanations[SignalType.ESCALATION.value] = "Threat level escalating across conversation"
        
        if detect_copy_paste(scammer_messages):
            detected_signals.append(SignalType.COPY_PASTE)
            explanations[SignalType.COPY_PASTE.value] = "Exact message repetition detected"
        
        if detect_ignoring_questions(conversation_history):
            detected_signals.append(SignalType.IGNORING_QUESTIONS)
            explanations[SignalType.IGNORING_QUESTIONS.value] = "Scammer ignores questions and repeats demands"
    
    return detected_signals, explanations
