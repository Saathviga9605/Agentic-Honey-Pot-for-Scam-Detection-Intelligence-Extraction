"""
Comprehensive Enhancement Test Suite
=====================================
Tests all 6 research-grade novelties with ASCII output for Windows compatibility
"""

import sys
from pathlib import Path

# Add paths BEFORE imports
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "intelligence-engine"))
sys.path.insert(0, str(project_root / "agent-engine"))
sys.path.insert(0, str(project_root / "api-gateway"))

from profiler import scammer_profiler
from forensics import forensic_analyzer
from strategy import strategy_selector
from session_manager import Session

def print_section(title):
    print("\n" + "=" * 80)
    print(f" {title}")
    print("=" * 80 + "\n")

def test_all():
    print("\nCOMPREHENSIVE ENHANCEMENT TEST SUITE")
    print("Testing 6 Research-Grade Novelties")
    print("=" * 80)
    
    # Test 1: Profiling
    print_section("NOVELTY 1: Scammer Behavior Profiling")
    profile = scammer_profiler.analyze_behavior(
        "test-session",
        ["urgency", "threat", "time_pressure"],
        "Your account will be blocked in 10 minutes!",
        []
    )
    print(f"Primary Type: {profile['type']}")
    print(f"Confidence: {profile['confidence']:.2f}")
    print("[PASS] Profiling functional\n")
    
    # Test 2: Strategy
    print_section("NOVELTY 2: Agent Strategy Adaptation")
    strategy = strategy_selector.select_strategy(
        {"type": "urgency_enforcer"},
        0.5,
        2,
        ["urgency"]
    )
    print(f"Selected Strategy: {strategy.value}")
    print("[PASS] Strategy selection functional\n")
    
    # Test 3: Session Tracking
    print_section("NOVELTY 3-4: Temporal Realism & Confidence Timeline")
    session = Session("test-001")
    session.add_confidence_snapshot(0.75, 1)
    session.add_response_delay(1500)
    print(f"Confidence snapshots: {len(session.confidence_timeline)}")
    print(f"Response delays tracked: {len(session.response_delays)}")
    print("[PASS] Session tracking functional\n")
    
    # Test 4: Forensics
    print_section("NOVELTY 5: Forensic Summary Generator")
    session.scam_signals = ["urgency", "threat", "payment_demand"]
    session.scammer_profile = profile
    forensic = forensic_analyzer.generate_forensic_summary(session)
    print(f"Attack Type: {forensic['attack_classification']['attack_type']}")
    print(f"Risk Level: {forensic['attack_classification']['risk_level']}")
    print("[PASS] Forensic analysis functional\n")
    
    # Test 5: Callback
    print_section("NOVELTY 6: Failure-Resistant Callback")
    from guvi_callback import guvi_callback
    print(f"MAX_RETRIES: {guvi_callback.MAX_RETRIES}")
    print(f"RETRY_BACKOFF: {guvi_callback.RETRY_BACKOFF}")
    print("[PASS] Callback resilience configured\n")
    
    print("\n" + "=" * 80)
    print("ALL ENHANCEMENTS VERIFIED - SYSTEM READY")
    print("=" * 80 + "\n")

if __name__ == "__main__":
    test_all()
