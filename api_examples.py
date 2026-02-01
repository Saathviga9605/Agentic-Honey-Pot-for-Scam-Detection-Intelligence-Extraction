"""
Example Usage Demonstrations
Shows how to use the API Gateway and Intelligence System
"""

import requests
import json
import time

# Configuration
API_URL = "http://localhost:5000"
API_KEY = "test-key-123"

def print_section(title):
    """Print section header"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)


def example_1_simple_scam():
    """Example 1: Simple scam detection"""
    print_section("Example 1: Simple Scam Detection")
    
    payload = {
        "sessionId": "example-001",
        "message": {
            "sender": "scammer",
            "text": "Your account will be blocked! Verify immediately at http://fake-bank.com",
            "timestamp": "2026-01-31T10:00:00Z"
        },
        "conversationHistory": [],
        "metadata": {
            "channel": "SMS",
            "language": "English",
            "locale": "IN"
        }
    }
    
    print("\n📤 Request:")
    print(json.dumps(payload, indent=2))
    
    response = requests.post(
        f"{API_URL}/ingest-message",
        json=payload,
        headers={"x-api-key": API_KEY}
    )
    
    print("\n📥 Response:")
    print(json.dumps(response.json(), indent=2))
    print(f"Status Code: {response.status_code}")


def example_2_payment_scam():
    """Example 2: Payment scam with UPI"""
    print_section("Example 2: Payment Scam with UPI")
    
    payload = {
        "sessionId": "example-002",
        "message": {
            "sender": "scammer",
            "text": "Dear customer, your account is suspended. Pay Rs 5000 to 9876543210@paytm urgently!",
            "timestamp": "2026-01-31T10:05:00Z"
        },
        "conversationHistory": [],
        "metadata": {
            "channel": "WhatsApp",
            "language": "English",
            "locale": "IN"
        }
    }
    
    print("\n📤 Request:")
    print(json.dumps(payload, indent=2))
    
    response = requests.post(
        f"{API_URL}/ingest-message",
        json=payload,
        headers={"x-api-key": API_KEY}
    )
    
    print("\n📥 Response:")
    print(json.dumps(response.json(), indent=2))


def example_3_multi_turn_conversation():
    """Example 3: Multi-turn conversation"""
    print_section("Example 3: Multi-Turn Conversation")
    
    session_id = "example-003"
    
    messages = [
        {
            "sender": "scammer",
            "text": "Hello, this is from State Bank customer care.",
            "timestamp": "2026-01-31T10:00:00Z"
        },
        {
            "sender": "scammer",
            "text": "Your account has suspicious activity. We need to verify immediately.",
            "timestamp": "2026-01-31T10:02:00Z"
        },
        {
            "sender": "scammer",
            "text": "Please send OTP and account number to verify your identity.",
            "timestamp": "2026-01-31T10:05:00Z"
        },
        {
            "sender": "scammer",
            "text": "Also transfer Rs 1000 to 9999888877@paytm as security deposit.",
            "timestamp": "2026-01-31T10:07:00Z"
        },
        {
            "sender": "scammer",
            "text": "Do it now or account will be blocked permanently!",
            "timestamp": "2026-01-31T10:08:00Z"
        }
    ]
    
    conversation_history = []
    
    for i, message in enumerate(messages, 1):
        print(f"\n--- Turn {i} ---")
        
        payload = {
            "sessionId": session_id,
            "message": message,
            "conversationHistory": conversation_history,
            "metadata": {
                "channel": "Call",
                "language": "English",
                "locale": "IN"
            }
        }
        
        print(f"Scammer: {message['text']}")
        
        response = requests.post(
            f"{API_URL}/ingest-message",
            json=payload,
            headers={"x-api-key": API_KEY}
        )
        
        result = response.json()
        print(f"Honeypot: {result.get('reply', 'No reply')}")
        
        # Add to conversation history
        conversation_history.append(message)
        if result.get('reply'):
            conversation_history.append({
                "sender": "honeypot",
                "text": result['reply'],
                "timestamp": message['timestamp']
            })
        
        time.sleep(0.5)  # Small delay between messages


def example_4_check_sessions():
    """Example 4: Check active sessions"""
    print_section("Example 4: Check Active Sessions")
    
    response = requests.get(
        f"{API_URL}/sessions",
        headers={"x-api-key": API_KEY}
    )
    
    print("\n📊 Active Sessions:")
    data = response.json()
    
    if data.get('sessions'):
        for session in data['sessions']:
            print(f"\n  Session: {session['session_id']}")
            print(f"    State: {session['state']}")
            print(f"    Messages: {session['message_count']}")
            print(f"    Scam Detected: {session['scam_detected']}")
            print(f"    Intelligence Ready: {session['intelligence_ready']}")
    else:
        print("  No active sessions")


def example_5_health_check():
    """Example 5: Health check"""
    print_section("Example 5: Health Check")
    
    response = requests.get(f"{API_URL}/health")
    
    print("\n🏥 System Health:")
    print(json.dumps(response.json(), indent=2))


def example_6_invalid_auth():
    """Example 6: Invalid authentication"""
    print_section("Example 6: Invalid Authentication")
    
    payload = {
        "sessionId": "example-006",
        "message": {
            "sender": "scammer",
            "text": "Test message"
        }
    }
    
    print("\n❌ Attempting request without API key...")
    response = requests.post(
        f"{API_URL}/ingest-message",
        json=payload
    )
    
    print(f"Status Code: {response.status_code}")
    print("Response:", response.json())


def run_all_examples():
    """Run all examples"""
    print("\n" + "="*60)
    print("  AGENTIC HONEYPOT - API USAGE EXAMPLES")
    print("="*60)
    print("\nMake sure the server is running: python app.py")
    print(f"API URL: {API_URL}")
    
    input("\nPress Enter to start examples...")
    
    try:
        # Check if server is running
        response = requests.get(f"{API_URL}/health", timeout=2)
        if response.status_code != 200:
            print("\n❌ Server is not responding correctly!")
            return
    except:
        print("\n❌ Cannot connect to server!")
        print("Please start the server first: python app.py")
        return
    
    try:
        example_5_health_check()
        time.sleep(1)
        
        example_1_simple_scam()
        time.sleep(1)
        
        example_2_payment_scam()
        time.sleep(1)
        
        example_3_multi_turn_conversation()
        time.sleep(1)
        
        example_4_check_sessions()
        time.sleep(1)
        
        example_6_invalid_auth()
        
        print("\n" + "="*60)
        print("  ✅ ALL EXAMPLES COMPLETED!")
        print("="*60)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Examples interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")


if __name__ == "__main__":
    run_all_examples()
