"""
Example usage of the Scam Detection Engine.
Demonstrates various integration patterns and use cases.
"""

import json
from detector import detect_scam, detect_scam_from_json, batch_detect, get_info


def example_1_basic_detection():
    """Example 1: Basic single-message detection"""
    print("\n" + "="*60)
    print("Example 1: Basic Detection")
    print("="*60)
    
    message = {
        "text": "Share your UPI ID to avoid account suspension"
    }
    
    result = detect_scam(message)
    
    print(f"Message: {message['text']}")
    print(f"\nScam Detected: {result['scamDetected']}")
    print(f"Confidence: {result['confidence']}")
    print(f"Signals: {', '.join(result['signals'])}")
    print(f"\nExplanations:")
    for signal, explanation in result['explanation'].items():
        print(f"  - {signal}: {explanation}")


def example_2_with_history():
    """Example 2: Detection with conversation history"""
    print("\n" + "="*60)
    print("Example 2: Multi-turn Conversation")
    print("="*60)
    
    conversation = {
        "text": "Send OTP now!",
        "conversationHistory": [
            {
                "sender": "scammer",
                "text": "Your KYC verification failed",
                "timestamp": "2026-01-31T10:00:00Z"
            },
            {
                "sender": "user",
                "text": "Why? What should I do?",
                "timestamp": "2026-01-31T10:01:00Z"
            },
            {
                "sender": "scammer",
                "text": "Update immediately or account blocked",
                "timestamp": "2026-01-31T10:02:00Z"
            },
            {
                "sender": "user",
                "text": "How?",
                "timestamp": "2026-01-31T10:03:00Z"
            }
        ],
        "metadata": {
            "channel": "WhatsApp",
            "language": "English"
        }
    }
    
    result = detect_scam(conversation)
    
    print(f"Conversation turn count: {len(conversation['conversationHistory']) + 1}")
    print(f"Current message: {conversation['text']}")
    print(f"\nScam Detected: {result['scamDetected']}")
    print(f"Confidence: {result['confidence']}")
    print(f"Signals: {', '.join(result['signals'])}")


def example_3_json_interface():
    """Example 3: Using JSON string interface"""
    print("\n" + "="*60)
    print("Example 3: JSON String Interface")
    print("="*60)
    
    json_input = json.dumps({
        "text": "Enter your ATM PIN to receive refund",
        "metadata": {"channel": "SMS"}
    })
    
    print(f"Input JSON:\n{json_input}\n")
    
    json_output = detect_scam_from_json(json_input)
    
    print(f"Output JSON:\n{json_output}")


def example_4_batch_processing():
    """Example 4: Batch detection"""
    print("\n" + "="*60)
    print("Example 4: Batch Processing")
    print("="*60)
    
    messages = [
        {"text": "Your package is out for delivery"},
        {"text": "Urgent: Share OTP to verify identity"},
        {"text": "Your bank account will be closed. Send UPI ID"},
        {"text": "Monthly statement attached"},
        {"text": "Click here to update KYC: http://bit.ly/kyc"},
    ]
    
    results = batch_detect(messages)
    
    print(f"Processed {len(results)} messages:\n")
    
    for i, (msg, result) in enumerate(zip(messages, results), 1):
        status = "🚨 SCAM" if result['scamDetected'] else "✓ Safe"
        print(f"{i}. [{status}] Confidence: {result['confidence']:.2f}")
        print(f"   Text: {msg['text'][:60]}...")
        if result['scamDetected']:
            print(f"   Signals: {', '.join(result['signals'][:3])}")
        print()


def example_5_progressive_confidence():
    """Example 5: Progressive confidence over conversation"""
    print("\n" + "="*60)
    print("Example 5: Progressive Confidence Escalation")
    print("="*60)
    
    conversation_turns = [
        "Your KYC verification is pending",
        "Complete it within 24 hours",
        "Your account will be blocked",
        "Share your UPI ID to verify"
    ]
    
    history = []
    
    for i, text in enumerate(conversation_turns, 1):
        result = detect_scam({
            "text": text,
            "conversationHistory": history
        })
        
        print(f"Turn {i}: \"{text}\"")
        print(f"  Confidence: {result['confidence']:.2f} | Detected: {result['scamDetected']}")
        print(f"  Signals: {result['signals']}\n")
        
        # Add to history for next turn
        history.append({
            "sender": "scammer" if i % 2 == 1 else "user",
            "text": text,
            "timestamp": f"2026-01-31T10:{i:02d}:00Z"
        })


def example_6_real_world_scenarios():
    """Example 6: Real-world scam scenarios"""
    print("\n" + "="*60)
    print("Example 6: Real-World Scam Scenarios")
    print("="*60)
    
    scenarios = [
        {
            "name": "Bank Impersonation",
            "text": "Dear customer, your State Bank account will be suspended. Share OTP immediately."
        },
        {
            "name": "Tax Scam",
            "text": "Income tax notice: Pay pending tax via UPI: taxdept@paytm urgently"
        },
        {
            "name": "KYC Scam",
            "text": "Your bank KYC expired. Update at http://bit.ly/kyc-update within 2 hours"
        },
        {
            "name": "Prize Scam",
            "text": "Congratulations! Share your account number to receive Rs 50,000 prize"
        },
        {
            "name": "Delivery Scam",
            "text": "COD payment failed. Re-verify card details: http://short.link/pay"
        }
    ]
    
    for scenario in scenarios:
        result = detect_scam({"text": scenario["text"]})
        
        print(f"\n📧 {scenario['name']}")
        print(f"Message: {scenario['text']}")
        print(f"Result: {'🚨 SCAM DETECTED' if result['scamDetected'] else '⚠️ Suspicious'}")
        print(f"Confidence: {result['confidence']:.2f}")
        print(f"Key signals: {', '.join(result['signals'][:3])}")


def example_7_integration_pattern():
    """Example 7: Integration with agent system"""
    print("\n" + "="*60)
    print("Example 7: Integration Pattern")
    print("="*60)
    
    def handle_incoming_message(message_text, conversation_history=None):
        """
        Example integration function for honeypot agent system.
        """
        # Run detection
        result = detect_scam({
            "text": message_text,
            "conversationHistory": conversation_history or []
        })
        
        # Decision logic
        if result["scamDetected"]:
            confidence = result["confidence"]
            
            if confidence >= 0.9:
                action = "ENGAGE_AGGRESSIVE"
                print(f"✓ High confidence scam (>= 0.9)")
            elif confidence >= 0.7:
                action = "ENGAGE_CAUTIOUS"
                print(f"✓ Confirmed scam (>= 0.7)")
            else:
                action = "MONITOR"
                print(f"⚠ Below threshold but suspicious")
            
            print(f"  Action: {action}")
            print(f"  Confidence: {confidence:.2f}")
            print(f"  Signals: {', '.join(result['signals'][:3])}")
            
            return {
                "action": action,
                "confidence": confidence,
                "signals": result["signals"],
                "explanation": result["explanation"]
            }
        else:
            print(f"✗ Not a scam (confidence: {result['confidence']:.2f})")
            return {"action": "IGNORE", "confidence": result["confidence"]}
    
    # Test messages
    messages = [
        "Your statement is ready",
        "Update KYC today",
        "Share OTP to avoid suspension"
    ]
    
    print("\nProcessing incoming messages:\n")
    for msg in messages:
        print(f"Message: \"{msg}\"")
        handle_incoming_message(msg)
        print()


def show_engine_info():
    """Display engine information"""
    print("\n" + "="*60)
    print("Engine Information")
    print("="*60)
    
    info = get_info()
    print(json.dumps(info, indent=2))


if __name__ == "__main__":
    print("\n" + "="*60)
    print("SCAM DETECTION ENGINE - USAGE EXAMPLES")
    print("="*60)
    
    show_engine_info()
    
    example_1_basic_detection()
    example_2_with_history()
    example_3_json_interface()
    example_4_batch_processing()
    example_5_progressive_confidence()
    example_6_real_world_scenarios()
    example_7_integration_pattern()
    
    print("\n" + "="*60)
    print("All examples completed!")
    print("="*60 + "\n")
