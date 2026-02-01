"""
Conversational Response Module for Defensive Cybersecurity Honeypot
====================================================================

Generates natural replies to suspected scam messages in a controlled research environment.
This module ONLY generates reply text - does NOT detect, extract, or store data.

Usage:
    reply_text = generate_reply(latest_message, conversation_history, signals, agent_state)
"""

import random
import re
from typing import List, Dict, Optional
from datetime import datetime


# ============================================================================
# PERSONA DEFINITIONS
# ============================================================================

PERSONAS = {
    "cautious_bank_customer": {
        "traits": ["polite", "confused", "security-conscious"],
        "phrases": {
            "confusion": [
                "Sorry, which bank is this?",
                "I'm not sure what this is about",
                "Can you clarify which account?",
                "Which service is this regarding?",
                "I don't understand what account you mean"
            ],
            "verification": [
                "Can you give me a reference number?",
                "What's the official website for this?",
                "Which branch should I contact?",
                "Is there a customer service number I can call?",
                "Can you tell me the department name?"
            ],
            "concern": [
                "This seems urgent, what happened exactly?",
                "I'm worried, can you explain more?",
                "Should I be concerned about this?",
                "What exactly is the problem?"
            ],
            "link_issue": [
                "The link didn't open for me",
                "I tried clicking but nothing happened",
                "Can you send that link again?",
                "I can't seem to open it, is there another way?"
            ]
        }
    },
    "busy_employee": {
        "traits": ["hurried", "practical", "limited-time"],
        "phrases": {
            "confusion": [
                "Quick question - which company is this?",
                "Sorry I'm busy, what's this about?",
                "Can you be more specific?",
                "I'm at work, which account?",
                "Need more details, what service?"
            ],
            "verification": [
                "Send me the reference number please",
                "What's the official contact?",
                "Give me the ticket ID or something",
                "Which department exactly?",
                "Can you provide verification details?"
            ],
            "concern": [
                "Wait, what issue?",
                "Hold on, what happened?",
                "This is important, tell me more",
                "I need to know what went wrong"
            ],
            "link_issue": [
                "Link's not working",
                "Can't open it, send another?",
                "The link failed to load",
                "Not loading, can you resend?"
            ]
        }
    },
    "anxious_student": {
        "traits": ["worried", "inexperienced", "cooperative"],
        "phrases": {
            "confusion": [
                "I'm confused, what is this about?",
                "Which account do you mean?",
                "Sorry I don't know what this means",
                "Can you explain what happened?",
                "I'm not sure which service this is"
            ],
            "verification": [
                "How can I verify this is real?",
                "Can you give me a reference number or something?",
                "What's the official website?",
                "Should I call someone to confirm?",
                "Is there a way to check this officially?"
            ],
            "concern": [
                "I'm really worried now, what's wrong?",
                "This sounds serious, can you explain?",
                "I'm stressed, what should I do?",
                "Please tell me what the issue is"
            ],
            "link_issue": [
                "I clicked but it didn't work",
                "The link isn't opening for me",
                "Can you send it again? It failed",
                "I'm having trouble with the link"
            ]
        }
    }
}


# ============================================================================
# SESSION STATE (In-memory for demonstration)
# ============================================================================

class SessionState:
    """Manages session state including persona selection"""
    
    _sessions = {}  # In production, use proper session storage
    
    @classmethod
    def get_or_create_session(cls, session_id: str = "default") -> Dict:
        """Get or create a session with persistent persona"""
        if session_id not in cls._sessions:
            cls._sessions[session_id] = {
                "persona": random.choice(list(PERSONAS.keys())),
                "stage": "clarification",
                "questions_asked": [],
                "interaction_count": 0
            }
        return cls._sessions[session_id]
    
    @classmethod
    def update_session(cls, session_id: str, updates: Dict):
        """Update session state"""
        if session_id in cls._sessions:
            cls._sessions[session_id].update(updates)


# ============================================================================
# CONVERSATION STAGE DETECTION
# ============================================================================

def determine_stage(conversation_history: List[Dict], session_state: Dict) -> str:
    """
    Determine current conversation stage based on history and state
    
    Stages:
    - clarification: Initial questions about what/who/why
    - verification: Asking for official details, references, contacts
    - elicitation: Requesting specific indicators (links, IDs, numbers)
    """
    
    interaction_count = len([msg for msg in conversation_history if msg.get("sender") == "scammer"])
    
    # Stage progression
    if interaction_count <= 2:
        return "clarification"
    elif interaction_count <= 4:
        return "verification"
    else:
        return "elicitation"


# ============================================================================
# SIGNAL ANALYSIS
# ============================================================================

def analyze_signals(signals: List[str], latest_message: str) -> Dict:
    """
    Analyze signals to determine response characteristics
    
    Returns:
        {
            "urgency_level": "low" | "medium" | "high",
            "concern_tone": bool,
            "request_stronger_proof": bool,
            "mention_link_issue": bool
        }
    """
    
    urgency_signals = ["urgency", "account_threat", "deadline", "immediate", "account_suspension"]
    pressure_signals = ["repeated_pressure", "multiple_requests", "repetition"]
    link_signals = ["link", "url", "click_here", "website", "suspicious_url"]
    payment_signals = ["payment", "pay", "transfer", "upi", "bank_details", "upi_request"]
    
    urgency_count = sum(1 for s in signals if s in urgency_signals)
    
    # Check message content for additional clues
    message_lower = latest_message.lower()
    has_link = any(word in message_lower for word in ["http", "link", "click", "visit", "open"])
    has_payment_request = any(word in message_lower for word in ["pay", "transfer", "send", "confirm payment", "upi", "paytm"])
    
    return {
        "urgency_level": "high" if urgency_count >= 2 else ("medium" if urgency_count == 1 else "low"),
        "concern_tone": urgency_count > 0 or "account_threat" in signals,
        "request_stronger_proof": any(s in signals for s in pressure_signals) or has_payment_request,
        "mention_link_issue": has_link or any(s in signals for s in link_signals)
    }


# ============================================================================
# RESPONSE GENERATION
# ============================================================================

def generate_reply(
    latest_message: str,
    conversation_history: List[Dict],
    signals: List[str],
    agent_state: str,
    session_id: str = "default"
) -> str:
    """
    Generate a natural conversational reply
    
    Args:
        latest_message: The most recent message from the external sender
        conversation_history: List of previous messages with sender and text
        signals: List of behavioral signals (e.g., ["urgency", "account_threat"])
        agent_state: Current agent state (e.g., "ENGAGING")
        session_id: Unique session identifier for persona consistency
    
    Returns:
        str: The reply text to send
    """
    
    # Get or create session with consistent persona
    session_state = SessionState.get_or_create_session(session_id)
    persona_key = session_state["persona"]
    persona = PERSONAS[persona_key]
    
    # Determine conversation stage
    stage = determine_stage(conversation_history, session_state)
    
    # Analyze signals for response characteristics
    signal_analysis = analyze_signals(signals, latest_message)
    
    # Select appropriate phrase category
    if signal_analysis["mention_link_issue"]:
        category = "link_issue"
    elif signal_analysis["concern_tone"]:
        category = "concern"
    elif stage == "verification" or signal_analysis["request_stronger_proof"]:
        category = "verification"
    else:
        category = "confusion"
    
    # Get base phrases for this category
    phrases = persona["phrases"][category]
    
    # Select a phrase we haven't used recently
    recent_questions = session_state.get("questions_asked", [])[-3:]
    available_phrases = [p for p in phrases if p not in recent_questions]
    
    if not available_phrases:
        available_phrases = phrases  # Reset if all used
    
    base_reply = random.choice(available_phrases)
    
    # Add natural variations
    reply = add_natural_variations(base_reply, signal_analysis)
    
    # Update session state
    session_state["questions_asked"].append(base_reply)
    session_state["interaction_count"] += 1
    session_state["stage"] = stage
    SessionState.update_session(session_id, session_state)
    
    return reply


def add_natural_variations(base_reply: str, signal_analysis: Dict) -> str:
    """
    Add natural human-like variations to make replies less robotic
    
    - Occasional typos or casual language
    - Question marks sometimes omitted
    - Filler words
    - Contextual additions
    """
    
    # Add filler words occasionally (20% chance)
    fillers = ["Sorry, ", "Um, ", "Wait, ", "Ok, ", "Hmm, "]
    if random.random() < 0.20 and not base_reply.startswith(tuple(fillers)):
        base_reply = random.choice(fillers) + base_reply.lower()
    
    # Add concern markers for high urgency (30% chance)
    if signal_analysis["urgency_level"] == "high" and random.random() < 0.30:
        concern_additions = [
            " This sounds urgent.",
            " I'm worried about this.",
            " Should I be concerned?",
        ]
        base_reply = base_reply + random.choice(concern_additions)
    
    # Occasionally make it less formal (15% chance)
    if random.random() < 0.15:
        base_reply = base_reply.replace("I am", "I'm")
        base_reply = base_reply.replace("cannot", "can't")
        base_reply = base_reply.replace("do not", "don't")
    
    # Occasionally add a follow-up question (10% chance)
    if random.random() < 0.10 and signal_analysis["request_stronger_proof"]:
        follow_ups = [
            " Can you verify?",
            " How do I confirm this?",
            " Is this official?",
        ]
        base_reply = base_reply + random.choice(follow_ups)
    
    return base_reply


# ============================================================================
# SAFETY VALIDATION
# ============================================================================

def validate_reply_safety(reply: str) -> bool:
    """
    Ensure reply doesn't violate safety constraints
    
    Returns False if reply contains:
    - Real personal data patterns (OTP, passwords, account numbers)
    - Confirmation language
    - Accusatory language
    - Honeypot mentions
    """
    
    # Patterns that should NEVER appear
    forbidden_patterns = [
        r'\b\d{6}\b',  # OTP-like numbers
        r'\b\d{12,16}\b',  # Account numbers
        r'password\s*[:=]',  # Password sharing
        r'\bI confirm\b',  # Confirmations
        r'\bscam\b',  # Accusations
        r'\bfraud\b',
        r'\bhoneypot\b',
        r'\bdetect\b',
        r'\banalysis\b',
        r'\bgo away\b',  # Ending conversation
        r'\bleave me alone\b',
    ]
    
    reply_lower = reply.lower()
    
    for pattern in forbidden_patterns:
        if re.search(pattern, reply_lower):
            return False
    
    return True


# ============================================================================
# MAIN API FUNCTION
# ============================================================================

def generate_reply_safe(
    latest_message: str,
    conversation_history: List[Dict] = None,
    signals: List[str] = None,
    agent_state: str = "ENGAGING",
    session_id: str = "default"
) -> Dict:
    """
    Safe wrapper for generate_reply that returns structured output
    
    Returns:
        {"reply": "response text"}
    """
    
    if conversation_history is None:
        conversation_history = []
    
    if signals is None:
        signals = []
    
    # Generate reply
    reply = generate_reply(
        latest_message=latest_message,
        conversation_history=conversation_history,
        signals=signals,
        agent_state=agent_state,
        session_id=session_id
    )
    
    # Safety check
    if not validate_reply_safety(reply):
        # Fallback to safe generic response
        reply = "Sorry, I didn't understand that. Can you explain again?"
    
    # Self-check: ensure reply is short (1-2 sentences)
    sentences = reply.split('.')
    if len(sentences) > 3:
        reply = '. '.join(sentences[:2]) + '.'
    
    return {"reply": reply.strip()}


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def reset_session(session_id: str = "default"):
    """Reset session state (useful for testing)"""
    if session_id in SessionState._sessions:
        del SessionState._sessions[session_id]


def get_session_info(session_id: str = "default") -> Dict:
    """Get current session information (for debugging)"""
    return SessionState.get_or_create_session(session_id)
