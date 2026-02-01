"""
Integration Test Suite
Tests the complete flow from API Gateway to Intelligence Extraction
"""

import json
import sys
import os
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, os.path.join(str(Path(__file__).parent), 'intelligence-engine'))
sys.path.insert(0, os.path.join(str(Path(__file__).parent), 'api-gateway'))

from bridge import create_scam_detector_bridge, create_agent_interface
from reporter import intelligence_reporter
from main import create_api_gateway


def test_scam_detector_bridge():
    """Test scam detector bridge integration"""
    print("[TEST] Testing Scam Detector Bridge...")
    
    bridge = create_scam_detector_bridge()
    
    # Test case 1: Obvious scam message
    result = bridge.analyze_message(
        "Your account will be blocked! Pay immediately to 9876543210@paytm",
        context={"history": [], "metadata": {}}
    )
    
    assert result["is_scam"] == True, "Should detect scam"
    assert result["confidence"] > 0, "Should have confidence score"
    print(f"  [OK] Scam detected: {result['confidence']:.2f} confidence")
    
    # Test case 2: Normal message
    result = bridge.analyze_message(
        "Hello, how are you today?",
        context={"history": [], "metadata": {}}
    )
    
    assert result["is_scam"] == False, "Should not detect scam in normal message"
    print(f"  [OK] Normal message: {result['confidence']:.2f} confidence")
    
    print("[PASS] Scam Detector Bridge tests passed!\n")


def test_intelligence_extraction():
    """Test intelligence extraction"""
    print("[TEST] Testing Intelligence Extraction...")
    
    # Simulate conversation with scammer
    conversation = [
        {"sender": "scammer", "text": "Your account will be blocked urgently!", "timestamp": "2026-01-31T10:00:00Z"},
        {"sender": "honeypot", "text": "Why is my account blocked?", "timestamp": "2026-01-31T10:01:00Z"},
        {"sender": "scammer", "text": "Pay immediately to 9876543210@paytm to unblock", "timestamp": "2026-01-31T10:02:00Z"},
        {"sender": "honeypot", "text": "How much should I pay?", "timestamp": "2026-01-31T10:03:00Z"},
        {"sender": "scammer", "text": "Send 5000 rupees to 9876543210@paytm now", "timestamp": "2026-01-31T10:04:00Z"},
        {"sender": "honeypot", "text": "OK, sending to 9876543210@paytm", "timestamp": "2026-01-31T10:05:00Z"}
    ]
    
    # Analyze conversation
    result = intelligence_reporter.analyze_conversation(conversation, "test-session-001")
    
    print(f"  [OK] Entities found: {result['entities_found']}")
    print(f"  [OK] Keywords found: {result['keywords_found']}")
    print(f"  [OK] Complete: {result['complete']}")
    
    # Generate report
    report = intelligence_reporter.generate_final_report("test-session-001")
    
    print(f"  [OK] UPI IDs: {len(report['upi_ids'])}")
    print(f"  [OK] Keywords: {len(report['keywords'])}")
    print(f"  [OK] Summary: {report['behavior_summary'][:50]}...")
    
    assert len(report['upi_ids']) > 0, "Should extract UPI ID"
    assert len(report['keywords']) > 0, "Should extract keywords"
    
    print("[PASS] Intelligence Extraction tests passed!\n")


def test_api_gateway():
    """Test API Gateway integration"""
    print("[TEST] Testing API Gateway...")
    
    # Initialize components
    scam_detector = create_scam_detector_bridge()
    agent = create_agent_interface()
    
    gateway = create_api_gateway(
        scam_detector=scam_detector,
        intelligence_engine=intelligence_reporter,
        agent_interface=agent
    )
    
    app = gateway.get_app()
    
    # Create test client
    with app.test_client() as client:
        # Test 1: Health check
        response = client.get('/health')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        print("  [OK] Health check passed")
        
        # Test 2: Invalid authentication
        response = client.post('/ingest-message', json={})
        assert response.status_code == 401
        print("  [OK] Authentication validation passed")
        
        # Test 3: Valid message ingestion
        payload = {
            "sessionId": "test-session-002",
            "message": {
                "sender": "scammer",
                "text": "Your account is blocked! Pay to 9999888877@paytm",
                "timestamp": "2026-01-31T10:00:00Z"
            },
            "conversationHistory": [],
            "metadata": {
                "channel": "SMS",
                "language": "English",
                "locale": "IN"
            }
        }
        
        response = client.post(
            '/ingest-message',
            json=payload,
            headers={'x-api-key': 'test-key-123'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert 'reply' in data
        print(f"  [OK] Message ingestion passed: '{data['reply']}'")
        
        # Test 4: Session listing
        response = client.get(
            '/sessions',
            headers={'x-api-key': 'test-key-123'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'sessions' in data
        print(f"  [OK] Session listing passed: {len(data['sessions'])} sessions")
    
    print("[PASS] API Gateway tests passed!\n")


def test_agent_interface():
    """Test agent interface"""
    print("[TEST] Testing Agent Interface...")
    
    agent = create_agent_interface()
    
    # Test contextual replies
    conversation = [
        {"sender": "scammer", "text": "Your account will be blocked!"}
    ]
    
    reply = agent.generate_reply(conversation)
    assert len(reply) > 0, "Should generate reply"
    print(f"  [OK] Generated reply: '{reply}'")
    
    # Test with payment context
    conversation.append({"sender": "scammer", "text": "Pay 5000 rupees immediately"})
    reply = agent.generate_reply(conversation)
    assert "payment" in reply.lower() or "pay" in reply.lower() or "details" in reply.lower()
    print(f"  [OK] Contextual reply: '{reply}'")
    
    print("[PASS] Agent Interface tests passed!\n")


def run_all_tests():
    """Run all integration tests"""
    print("=" * 60)
    print("INTEGRATION TEST SUITE")
    print("=" * 60)
    print()
    
    try:
        test_scam_detector_bridge()
        test_intelligence_extraction()
        test_agent_interface()
        test_api_gateway()
        
        print("=" * 60)
        print("[SUCCESS] ALL TESTS PASSED!")
        print("=" * 60)
        print()
        print("System is ready for deployment!")
        print()
        return True
        
    except AssertionError as e:
        print()
        print("=" * 60)
        print("❌ TEST FAILED!")
        print("=" * 60)
        print(f"Error: {e}")
        return False
        
    except Exception as e:
        print()
        print("=" * 60)
        print("❌ UNEXPECTED ERROR!")
        print("=" * 60)
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
