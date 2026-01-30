"""
Main entry point for Scam Detection Engine.
Exposes clean interface for external modules to consume.
"""

import json
from typing import Dict, List, Optional, Any
from signals import SignalType
from rules import detect_signals
from scorer import score_message


def detect_scam(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main detection function. Analyzes a message for scam indicators.
    
    INPUT CONTRACT:
    {
        "text": str (required),
        "conversationHistory": List[Dict] (optional),
        "metadata": Dict (optional)
    }
    
    OUTPUT CONTRACT:
    {
        "scamDetected": bool,
        "confidence": float,
        "signals": List[str],
        "explanation": Dict[str, str]
    }
    
    Args:
        input_data: Dictionary matching input contract
    
    Returns:
        Dictionary matching output contract
    
    Raises:
        ValueError: If input doesn't match contract
    """
    # Input validation
    if not isinstance(input_data, dict):
        raise ValueError("Input must be a dictionary")
    
    if "text" not in input_data:
        raise ValueError("Input must contain 'text' field")
    
    text = input_data.get("text", "")
    if not isinstance(text, str) or not text.strip():
        raise ValueError("'text' must be a non-empty string")
    
    # Extract optional fields
    conversation_history = input_data.get("conversationHistory", [])
    metadata = input_data.get("metadata", {})
    
    # Validate conversation history format
    if conversation_history and not isinstance(conversation_history, list):
        conversation_history = []
    
    # Detect signals in the text
    detected_signal_types, signal_explanations = detect_signals(
        text=text,
        conversation_history=conversation_history
    )
    
    # Calculate confidence score
    scoring_result = score_message(
        signals=detected_signal_types,
        conversation_history=conversation_history
    )
    
    confidence = scoring_result["confidence"]
    scam_detected = scoring_result["scamDetected"]
    
    # Convert signal types to machine-readable strings
    signal_strings = [sig.value for sig in detected_signal_types]
    
    # Build output
    output = {
        "scamDetected": scam_detected,
        "confidence": confidence,
        "signals": signal_strings,
        "explanation": signal_explanations
    }
    
    return output


def detect_scam_from_json(json_string: str) -> str:
    """
    Convenience function that accepts and returns JSON strings.
    
    Args:
        json_string: JSON string matching input contract
    
    Returns:
        JSON string matching output contract
    """
    try:
        input_data = json.loads(json_string)
        output_data = detect_scam(input_data)
        return json.dumps(output_data, indent=2)
    except json.JSONDecodeError as e:
        return json.dumps({
            "error": f"Invalid JSON input: {str(e)}",
            "scamDetected": False,
            "confidence": 0.0,
            "signals": [],
            "explanation": {}
        }, indent=2)
    except Exception as e:
        return json.dumps({
            "error": f"Detection error: {str(e)}",
            "scamDetected": False,
            "confidence": 0.0,
            "signals": [],
            "explanation": {}
        }, indent=2)


def batch_detect(messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Detect scams in multiple messages.
    
    Args:
        messages: List of input dictionaries
    
    Returns:
        List of output dictionaries
    """
    results = []
    for msg in messages:
        try:
            result = detect_scam(msg)
            results.append(result)
        except Exception as e:
            results.append({
                "error": str(e),
                "scamDetected": False,
                "confidence": 0.0,
                "signals": [],
                "explanation": {}
            })
    return results


def validate_input(input_data: Dict[str, Any]) -> tuple[bool, Optional[str]]:
    """
    Validate input against contract.
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(input_data, dict):
        return False, "Input must be a dictionary"
    
    if "text" not in input_data:
        return False, "Missing required field: 'text'"
    
    text = input_data.get("text")
    if not isinstance(text, str):
        return False, "'text' must be a string"
    
    if not text.strip():
        return False, "'text' cannot be empty"
    
    # Validate optional fields if present
    if "conversationHistory" in input_data:
        history = input_data["conversationHistory"]
        if not isinstance(history, list):
            return False, "'conversationHistory' must be a list"
        
        for i, msg in enumerate(history):
            if not isinstance(msg, dict):
                return False, f"conversationHistory[{i}] must be a dictionary"
            if "text" not in msg:
                return False, f"conversationHistory[{i}] missing 'text' field"
    
    if "metadata" in input_data:
        if not isinstance(input_data["metadata"], dict):
            return False, "'metadata' must be a dictionary"
    
    return True, None


def get_version() -> str:
    """Return version information"""
    return "1.0.0"


def get_info() -> Dict[str, Any]:
    """Return engine information"""
    return {
        "name": "Scam Detection Engine",
        "version": get_version(),
        "description": "Rule-based scam detection with progressive confidence scoring",
        "detection_threshold": 0.7,
        "signal_categories": [
            "urgency_pressure",
            "account_authority",
            "payment",
            "phishing",
            "conversation"
        ]
    }


# Example usage and testing
if __name__ == "__main__":
    # Test case 1: Simple threat
    test1 = {
        "text": "Your bank account will be blocked today",
        "conversationHistory": [],
        "metadata": {"channel": "SMS"}
    }
    
    print("Test 1: Simple Threat")
    print(json.dumps(detect_scam(test1), indent=2))
    print("\n" + "="*60 + "\n")
    
    # Test case 2: UPI request with urgency
    test2 = {
        "text": "Share your UPI ID to avoid account suspension",
        "conversationHistory": [],
        "metadata": {"channel": "SMS", "language": "English"}
    }
    
    print("Test 2: UPI Request + Urgency")
    print(json.dumps(detect_scam(test2), indent=2))
    print("\n" + "="*60 + "\n")
    
    # Test case 3: Multi-turn escalation
    test3 = {
        "text": "Send your OTP now or account will be permanently closed",
        "conversationHistory": [
            {
                "sender": "scammer",
                "text": "Your KYC has failed",
                "timestamp": "2026-01-31T10:00:00Z"
            },
            {
                "sender": "user",
                "text": "Why?",
                "timestamp": "2026-01-31T10:01:00Z"
            },
            {
                "sender": "scammer",
                "text": "Update KYC within 1 hour",
                "timestamp": "2026-01-31T10:02:00Z"
            }
        ],
        "metadata": {"channel": "WhatsApp"}
    }
    
    print("Test 3: Multi-turn Escalation")
    print(json.dumps(detect_scam(test3), indent=2))
    print("\n" + "="*60 + "\n")
    
    # Test case 4: Legitimate message (should not flag)
    test4 = {
        "text": "Your account statement for January is ready",
        "conversationHistory": [],
        "metadata": {"channel": "Email"}
    }
    
    print("Test 4: Legitimate Message")
    print(json.dumps(detect_scam(test4), indent=2))
    print("\n" + "="*60 + "\n")
    
    # Test case 5: Phishing link
    test5 = {
        "text": "Verify your account immediately: http://bit.ly/verify123 Click here now",
        "conversationHistory": [],
        "metadata": {}
    }
    
    print("Test 5: Phishing Link")
    print(json.dumps(detect_scam(test5), indent=2))
    print("\n" + "="*60 + "\n")
    
    # Display engine info
    print("Engine Info:")
    print(json.dumps(get_info(), indent=2))
