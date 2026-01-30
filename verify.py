"""
Quick verification script to ensure the Scam Detection Engine is working.
Run this to validate installation and basic functionality.
"""

import json
from detector import detect_scam, get_info


def verify():
    """Verify engine is working correctly"""
    
    print("\n" + "="*60)
    print("SCAM DETECTION ENGINE - VERIFICATION")
    print("="*60 + "\n")
    
    # Check 1: Engine info
    print("✓ Check 1: Engine Information")
    info = get_info()
    print(f"  Name: {info['name']}")
    print(f"  Version: {info['version']}")
    print(f"  Threshold: {info['detection_threshold']}\n")
    
    # Check 2: Basic detection
    print("✓ Check 2: Basic Detection")
    result1 = detect_scam({"text": "Share your OTP"})
    assert result1['scamDetected'] == True, "Failed: OTP request should be detected"
    assert result1['confidence'] >= 0.7, "Failed: Confidence should be >= 0.7"
    print(f"  OTP request detected: confidence = {result1['confidence']}\n")
    
    # Check 3: Legitimate message not flagged
    print("✓ Check 3: False Positive Control")
    result2 = detect_scam({"text": "Your statement is ready"})
    assert result2['scamDetected'] == False, "Failed: Legitimate message flagged"
    assert result2['confidence'] < 0.5, "Failed: Legitimate message has high confidence"
    print(f"  Legitimate message not flagged: confidence = {result2['confidence']}\n")
    
    # Check 4: Progressive confidence
    print("✓ Check 4: Progressive Confidence")
    result3_single = detect_scam({"text": "Update KYC"})
    result3_multi = detect_scam({
        "text": "Send OTP now",
        "conversationHistory": [
            {"sender": "scammer", "text": "Update KYC", "timestamp": "2026-01-31T10:00:00Z"}
        ]
    })
    assert result3_multi['confidence'] > result3_single['confidence'], "Failed: Multi-turn should have higher confidence"
    print(f"  Single turn: {result3_single['confidence']:.2f}")
    print(f"  Multi-turn: {result3_multi['confidence']:.2f}\n")
    
    # Check 5: Signal detection
    print("✓ Check 5: Signal Detection")
    result4 = detect_scam({"text": "Share UPI ID to avoid account suspension"})
    assert 'upi_request' in result4['signals'], "Failed: UPI signal not detected"
    assert 'account_suspension' in result4['signals'], "Failed: Account suspension not detected"
    assert len(result4['explanation']) > 0, "Failed: No explanations provided"
    print(f"  Detected {len(result4['signals'])} signals")
    print(f"  Signals: {', '.join(result4['signals'])}\n")
    
    # Check 6: Output contract
    print("✓ Check 6: Output Contract")
    result5 = detect_scam({"text": "Send money now"})
    required_keys = ['scamDetected', 'confidence', 'signals', 'explanation']
    for key in required_keys:
        assert key in result5, f"Failed: Missing key '{key}' in output"
    assert isinstance(result5['scamDetected'], bool), "Failed: scamDetected should be bool"
    assert isinstance(result5['confidence'], (int, float)), "Failed: confidence should be numeric"
    assert 0.0 <= result5['confidence'] <= 1.0, "Failed: confidence out of range"
    assert isinstance(result5['signals'], list), "Failed: signals should be list"
    assert isinstance(result5['explanation'], dict), "Failed: explanation should be dict"
    print(f"  All required keys present")
    print(f"  Types validated")
    print(f"  Confidence range: [{result5['confidence']:.2f}] ✓\n")
    
    # Final summary
    print("=" * 60)
    print("✓ ALL CHECKS PASSED - Engine is ready to use!")
    print("=" * 60 + "\n")
    
    # Example usage
    print("Example usage:")
    print("-" * 60)
    print("from detector import detect_scam")
    print()
    print("result = detect_scam({")
    print('    "text": "Share your UPI ID to avoid account suspension"')
    print("})")
    print()
    print("if result['scamDetected']:")
    print(f"    # Activate honeypot agent")
    print(f"    confidence = result['confidence']")
    print(f"    signals = result['signals']")
    print("-" * 60 + "\n")


if __name__ == "__main__":
    try:
        verify()
    except AssertionError as e:
        print(f"\n❌ VERIFICATION FAILED: {e}\n")
    except Exception as e:
        print(f"\n❌ ERROR: {e}\n")
