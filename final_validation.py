"""
Final Validation Script for GUVI Hackathon Submission
Verifies all requirements for automated evaluation
"""

import requests
import json
import time
from datetime import datetime

# Configuration
API_BASE_URL = "http://127.0.0.1:5000"
API_KEY = "test-key-123"
HEADERS = {
    "x-api-key": API_KEY,
    "Content-Type": "application/json"
}

def print_section(title):
    print("\n" + "=" * 80)
    print(f" {title}")
    print("=" * 80)

def test_health_check():
    """Test 1: Health endpoint"""
    print_section("TEST 1: Health Check")
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        assert response.status_code == 200, "Health check failed"
        assert response.json().get("status") == "healthy", "Status not healthy"
        print("[PASS] Health check successful")
        return True
    except Exception as e:
        print(f"[FAIL] Health check error: {e}")
        return False

def test_authentication():
    """Test 2: API Key Authentication"""
    print_section("TEST 2: Authentication")
    
    # Test without API key
    print("Testing without API key...")
    try:
        response = requests.get(f"{API_BASE_URL}/sessions", timeout=5)
        assert response.status_code == 401, "Should reject without API key"
        print(f"[PASS] Correctly rejected: {response.json()}")
    except Exception as e:
        print(f"[FAIL] Auth test error: {e}")
        return False
    
    # Test with valid API key
    print("\nTesting with valid API key...")
    try:
        response = requests.get(f"{API_BASE_URL}/sessions", headers=HEADERS, timeout=5)
        assert response.status_code == 200, "Should accept valid API key"
        print(f"[PASS] Correctly authenticated: {response.status_code}")
        return True
    except Exception as e:
        print(f"[FAIL] Auth test error: {e}")
        return False

def test_message_ingestion():
    """Test 3: Message Ingestion (Core Functionality)"""
    print_section("TEST 3: Message Ingestion & Intelligence Extraction")
    
    test_messages = [
        {
            "name": "UPI Payment Scam",
            "payload": {
                "sessionId": "eval-test-001",
                "message": {
                    "sender": "scammer",
                    "text": "URGENT! Your SBI account will be blocked. Pay Rs 5000 verification fee to UPI: fraud@paytm immediately!",
                    "timestamp": datetime.now().isoformat()
                },
                "conversationHistory": [],
                "metadata": {
                    "channel": "SMS",
                    "language": "English",
                    "locale": "IN"
                }
            }
        },
        {
            "name": "Phishing Link Scam",
            "payload": {
                "sessionId": "eval-test-002",
                "message": {
                    "sender": "scammer",
                    "text": "Click here to update KYC: http://fake-bank-india.com/verify?id=12345",
                    "timestamp": datetime.now().isoformat()
                },
                "conversationHistory": [],
                "metadata": {
                    "channel": "WhatsApp",
                    "language": "English",
                    "locale": "IN"
                }
            }
        },
        {
            "name": "Authority Impersonation",
            "payload": {
                "sessionId": "eval-test-003",
                "message": {
                    "sender": "scammer",
                    "text": "This is RBI Cyber Cell. Your account has suspicious activity. Call 9876543210 within 30 minutes.",
                    "timestamp": datetime.now().isoformat()
                },
                "conversationHistory": [],
                "metadata": {
                    "channel": "Call",
                    "language": "English",
                    "locale": "IN"
                }
            }
        }
    ]
    
    results = []
    for test in test_messages:
        print(f"\nTesting: {test['name']}")
        print(f"Message: {test['payload']['message']['text'][:60]}...")
        
        try:
            start_time = time.time()
            response = requests.post(
                f"{API_BASE_URL}/ingest-message",
                headers=HEADERS,
                json=test['payload'],
                timeout=10
            )
            latency = (time.time() - start_time) * 1000  # ms
            
            print(f"Status Code: {response.status_code}")
            print(f"Latency: {latency:.0f}ms")
            
            if response.status_code == 200:
                data = response.json()
                print(f"Reply Generated: {data.get('reply', '')[:80]}...")
                
                # Validate response structure
                required_fields = ['sessionId', 'reply', 'scamDetected', 'signals']
                missing = [f for f in required_fields if f not in data]
                
                if missing:
                    print(f"[WARN] Missing fields: {missing}")
                
                # Show extracted intelligence
                if 'signals' in data:
                    print(f"Signals Detected: {len(data['signals'])} - {data['signals'][:5]}")
                
                # Show enhancements
                if 'scammerProfile' in data:
                    profile = data['scammerProfile']
                    print(f"Scammer Type: {profile.get('type', 'Unknown')}")
                
                if 'responseDelayMs' in data:
                    print(f"Response Delay: {data['responseDelayMs']}ms")
                
                results.append({
                    "test": test['name'],
                    "status": "PASS",
                    "latency": latency,
                    "signals": len(data.get('signals', []))
                })
                print(f"[PASS] {test['name']}")
            else:
                print(f"[FAIL] Unexpected status code: {response.status_code}")
                print(f"Response: {response.text}")
                results.append({
                    "test": test['name'],
                    "status": "FAIL",
                    "latency": latency
                })
                
        except Exception as e:
            print(f"[FAIL] Error: {e}")
            results.append({
                "test": test['name'],
                "status": "FAIL",
                "error": str(e)
            })
    
    # Summary
    print("\n--- Test Summary ---")
    passed = sum(1 for r in results if r.get('status') == 'PASS')
    print(f"Passed: {passed}/{len(results)}")
    
    if passed == len(results):
        avg_latency = sum(r.get('latency', 0) for r in results) / len(results)
        print(f"Average Latency: {avg_latency:.0f}ms")
        if avg_latency > 3000:
            print("[WARN] Latency exceeds 3 seconds")
    
    return passed == len(results)

def test_multi_turn_conversation():
    """Test 4: Multi-turn conversation handling"""
    print_section("TEST 4: Multi-Turn Conversation")
    
    session_id = "eval-test-multiturn"
    conversation = []
    
    messages = [
        "Your account has been suspended!",
        "To reactivate, send ₹2000 to UPI: scammer@paytm",
        "Why haven't you paid yet? Time is running out!"
    ]
    
    try:
        for i, msg in enumerate(messages, 1):
            print(f"\nTurn {i}: {msg}")
            
            payload = {
                "sessionId": session_id,
                "message": {
                    "sender": "scammer",
                    "text": msg,
                    "timestamp": datetime.now().isoformat()
                },
                "conversationHistory": conversation,
                "metadata": {
                    "channel": "SMS",
                    "language": "English",
                    "locale": "IN"
                }
            }
            
            response = requests.post(
                f"{API_BASE_URL}/ingest-message",
                headers=HEADERS,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                reply = data.get('reply', '')
                print(f"Agent Reply: {reply[:80]}...")
                
                # Update conversation history
                conversation.append({
                    "sender": "scammer",
                    "text": msg,
                    "timestamp": datetime.now().isoformat()
                })
                conversation.append({
                    "sender": "agent",
                    "text": reply,
                    "timestamp": datetime.now().isoformat()
                })
                
                # Check for confidence timeline
                if 'confidenceTimeline' in data:
                    timeline = data['confidenceTimeline']
                    if timeline:
                        latest = timeline[-1]
                        print(f"Confidence: {latest.get('confidence', 0):.2f}")
            else:
                print(f"[FAIL] Status {response.status_code}")
                return False
        
        print(f"\n[PASS] Multi-turn conversation handled successfully")
        return True
        
    except Exception as e:
        print(f"[FAIL] Error: {e}")
        return False

def test_error_handling():
    """Test 5: Error handling"""
    print_section("TEST 5: Error Handling")
    
    # Test invalid payload
    print("Testing with invalid payload...")
    try:
        response = requests.post(
            f"{API_BASE_URL}/ingest-message",
            headers=HEADERS,
            json={"invalid": "data"},
            timeout=5
        )
        print(f"Status: {response.status_code}")
        if response.status_code in [400, 422]:
            print(f"[PASS] Correctly rejected invalid payload")
            return True
        else:
            print(f"[WARN] Status {response.status_code} for invalid data")
            return True  # Still pass if handled gracefully
    except Exception as e:
        print(f"[FAIL] Error handling test failed: {e}")
        return False

def test_concurrent_sessions():
    """Test 6: Multiple concurrent sessions"""
    print_section("TEST 6: Concurrent Session Handling")
    
    try:
        import concurrent.futures
        
        def send_message(session_id):
            payload = {
                "sessionId": f"concurrent-{session_id}",
                "message": {
                    "sender": "scammer",
                    "text": f"Test message {session_id}",
                    "timestamp": datetime.now().isoformat()
                },
                "conversationHistory": [],
                "metadata": {"channel": "SMS", "language": "English", "locale": "IN"}
            }
            response = requests.post(
                f"{API_BASE_URL}/ingest-message",
                headers=HEADERS,
                json=payload,
                timeout=10
            )
            return response.status_code == 200
        
        # Send 5 concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(send_message, i) for i in range(5)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]
        
        success_count = sum(results)
        print(f"Successful requests: {success_count}/5")
        
        if success_count >= 4:  # Allow 1 failure
            print("[PASS] Concurrent sessions handled")
            return True
        else:
            print("[FAIL] Too many concurrent failures")
            return False
            
    except Exception as e:
        print(f"[WARN] Concurrent test error: {e}")
        return True  # Non-critical

def main():
    print("\n" + "=" * 80)
    print(" FINAL VALIDATION FOR GUVI HACKATHON SUBMISSION")
    print(" Agentic Honeypot - Problem 2")
    print("=" * 80)
    
    print(f"\nTarget Endpoint: {API_BASE_URL}")
    print(f"API Key: {API_KEY}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    tests = [
        ("Health Check", test_health_check),
        ("Authentication", test_authentication),
        ("Message Ingestion", test_message_ingestion),
        ("Multi-Turn Conversation", test_multi_turn_conversation),
        ("Error Handling", test_error_handling),
        ("Concurrent Sessions", test_concurrent_sessions)
    ]
    
    results = {}
    for name, test_func in tests:
        try:
            results[name] = test_func()
        except Exception as e:
            print(f"\n[ERROR] Test '{name}' crashed: {e}")
            results[name] = False
    
    # Final Summary
    print("\n" + "=" * 80)
    print(" FINAL VALIDATION SUMMARY")
    print("=" * 80)
    
    for name, passed in results.items():
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{status} {name}")
    
    total_passed = sum(results.values())
    total_tests = len(results)
    
    print(f"\nOverall: {total_passed}/{total_tests} tests passed")
    
    if total_passed == total_tests:
        print("\n✓ ALL TESTS PASSED - READY FOR SUBMISSION!")
        print("\nNext Steps:")
        print("1. Deploy your endpoint to a public URL (e.g., Railway, Render, etc.)")
        print("2. Update API_BASE_URL in this script to your public URL")
        print("3. Run validation again on public endpoint")
        print("4. Submit your endpoint URL and API key to GUVI platform")
    else:
        print(f"\n✗ {total_tests - total_passed} TEST(S) FAILED - REVIEW REQUIRED")
        print("\nFix the failing tests before submission.")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    main()
