"""
Scammer Behavior Profiler
Classifies scammers into behavioral archetypes based on conversation patterns
"""

import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

# Scammer behavior archetypes with their characteristic signals
SCAMMER_ARCHETYPES = {
    "Urgency Enforcer": {
        "description": "Uses threats and time pressure to force immediate action",
        "primary_signals": ["urgency", "threat", "time_pressure", "deadline"],
        "secondary_signals": ["account_threat", "suspension", "blocked"],
        "typical_phrases": ["immediate", "urgent", "act now", "last warning", "within", "minutes"]
    },
    "Payment Redirector": {
        "description": "Focuses on extracting payments through UPI or fees",
        "primary_signals": ["payment_demand", "upi", "fee", "refund"],
        "secondary_signals": ["payment_method", "transfer", "wallet"],
        "typical_phrases": ["pay", "₹", "rupees", "send", "transfer", "upi", "paytm", "gpay"]
    },
    "Authority Impersonator": {
        "description": "Pretends to be from legitimate organizations",
        "primary_signals": ["authority_claim", "impersonation", "official"],
        "secondary_signals": ["verification", "bank", "government"],
        "typical_phrases": ["rbi", "bank", "police", "income tax", "cyber cell", "official", "department"]
    },
    "Link Pusher": {
        "description": "Prioritizes getting victim to click malicious links",
        "primary_signals": ["suspicious_link", "phishing", "url"],
        "secondary_signals": ["download", "install", "click"],
        "typical_phrases": ["click", "link", "http", "bit.ly", "download", "install", "update"]
    },
    "Persistence Attacker": {
        "description": "Repeatedly follows up with same demands",
        "primary_signals": ["persistence", "follow_up", "repetition"],
        "secondary_signals": ["reminder", "waiting"],
        "typical_phrases": ["still waiting", "have you", "why haven't", "again", "reminder", "calling again"]
    }
}


class ScammerProfiler:
    """Profiles scammer behavior based on conversation patterns"""
    
    def __init__(self):
        self.profiles = {}  # session_id -> profile data
        logger.info("ScammerProfiler initialized")
    
    def analyze_behavior(
        self, 
        session_id: str, 
        signals: List[str], 
        message_text: str,
        conversation_history: List[Dict] = None
    ) -> Dict[str, Any]:
        """
        Analyze scammer behavior and update profile
        
        Args:
            session_id: Session identifier
            signals: Detected scam signals
            message_text: Latest message text
            conversation_history: Full conversation history
            
        Returns:
            Updated behavior profile
        """
        if conversation_history is None:
            conversation_history = []
        
        # Get or create profile
        if session_id not in self.profiles:
            self.profiles[session_id] = {
                "observed_signals": [],
                "observed_tactics": [],
                "message_count": 0,
                "archetype_scores": {archetype: 0.0 for archetype in SCAMMER_ARCHETYPES.keys()}
            }
        
        profile = self.profiles[session_id]
        
        # Update observed data
        profile["observed_signals"].extend(signals)
        profile["message_count"] += 1
        
        # Analyze message for tactics
        message_lower = message_text.lower()
        
        # Score each archetype
        for archetype, characteristics in SCAMMER_ARCHETYPES.items():
            score = 0.0
            
            # Check primary signals (high weight)
            for signal in characteristics["primary_signals"]:
                if signal in signals:
                    score += 3.0
            
            # Check secondary signals (medium weight)
            for signal in characteristics["secondary_signals"]:
                if signal in signals:
                    score += 1.5
            
            # Check typical phrases (low weight but adds nuance)
            for phrase in characteristics["typical_phrases"]:
                if phrase in message_lower:
                    score += 0.5
            
            # Update archetype score
            profile["archetype_scores"][archetype] += score
        
        # Determine dominant archetype
        dominant_archetype = max(
            profile["archetype_scores"].items(), 
            key=lambda x: x[1]
        )
        
        # Calculate confidence (normalized)
        total_score = sum(profile["archetype_scores"].values())
        confidence = dominant_archetype[1] / total_score if total_score > 0 else 0.0
        
        # Extract observed tactics (unique signals)
        unique_signals = list(set(profile["observed_signals"]))
        
        # Build profile result
        result = {
            "type": dominant_archetype[0],
            "confidence": round(min(confidence, 1.0), 2),
            "observedTactics": unique_signals[:10],  # Top 10 tactics
            "messageCount": profile["message_count"],
            "secondaryType": self._get_secondary_archetype(profile["archetype_scores"], dominant_archetype[0]),
            "description": SCAMMER_ARCHETYPES[dominant_archetype[0]]["description"]
        }
        
        logger.info(f"[{session_id}] Scammer profiled as '{result['type']}' (confidence: {result['confidence']})")
        
        return result
    
    def _get_secondary_archetype(self, scores: Dict[str, float], primary: str) -> str:
        """Get the second most likely archetype"""
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        # Find first archetype that's not the primary
        for archetype, score in sorted_scores:
            if archetype != primary and score > 0:
                return archetype
        
        return None
    
    def get_profile(self, session_id: str) -> Dict[str, Any]:
        """Get current profile for session"""
        if session_id not in self.profiles:
            return {
                "type": "Unknown",
                "confidence": 0.0,
                "observedTactics": [],
                "messageCount": 0,
                "secondaryType": None,
                "description": "Insufficient data for profiling"
            }
        
        profile = self.profiles[session_id]
        dominant_archetype = max(
            profile["archetype_scores"].items(), 
            key=lambda x: x[1]
        )
        
        total_score = sum(profile["archetype_scores"].values())
        confidence = dominant_archetype[1] / total_score if total_score > 0 else 0.0
        
        return {
            "type": dominant_archetype[0],
            "confidence": round(min(confidence, 1.0), 2),
            "observedTactics": list(set(profile["observed_signals"]))[:10],
            "messageCount": profile["message_count"],
            "secondaryType": self._get_secondary_archetype(profile["archetype_scores"], dominant_archetype[0]),
            "description": SCAMMER_ARCHETYPES[dominant_archetype[0]]["description"]
        }
    
    def clear_profile(self, session_id: str):
        """Clear profile data for session"""
        if session_id in self.profiles:
            del self.profiles[session_id]
            logger.info(f"[{session_id}] Profile data cleared")


# Global instance for easy access
scammer_profiler = ScammerProfiler()