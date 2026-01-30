"""
Confidence scoring logic with progressive escalation.
Handles multi-turn conversations and aggregates signal weights.
"""

from typing import List, Dict, Set
from signals import SignalType, SignalCategory, get_signal_weight, get_signal_category


class ConfidenceScorer:
    """
    Calculates progressive confidence scores based on detected signals.
    Implements the core rule: scamDetected = true if confidence >= 0.7
    """
    
    # Thresholds for scam detection
    SCAM_DETECTION_THRESHOLD = 0.7
    
    # Category multipliers (when multiple categories present)
    CATEGORY_DIVERSITY_BONUS = 0.15
    
    # Multi-turn multipliers
    MULTI_TURN_MULTIPLIER = 1.2  # 20% increase for signals across turns
    HIGH_SEVERITY_MULTIPLIER = 1.3  # 30% boost for critical signals
    
    def __init__(self):
        self.reset()
    
    def reset(self):
        """Reset scorer state"""
        self.seen_signals_history = []  # Track signals across conversation turns
        self.turn_count = 0
    
    def calculate_confidence(
        self,
        signals: List[SignalType],
        conversation_history: List[dict] = None,
        is_first_message: bool = True
    ) -> float:
        """
        Calculate confidence score with progressive escalation.
        
        Args:
            signals: List of detected signals in current message
            conversation_history: Optional conversation history
            is_first_message: Whether this is the first message in conversation
        
        Returns:
            Confidence score between 0.0 and 1.0
        """
        if not signals:
            return 0.0
        
        # Base score from signal weights
        base_score = self._calculate_base_score(signals)
        
        # Apply progressive multipliers
        score = base_score
        
        # 1. Check category diversity (multiple attack vectors)
        categories = self._get_unique_categories(signals)
        if len(categories) >= 2:
            score += self.CATEGORY_DIVERSITY_BONUS
        
        # 2. High severity signal boost
        if self._has_high_severity_signals(signals):
            score *= self.HIGH_SEVERITY_MULTIPLIER
        
        # 3. Check for classic scam combos (payment + threat)
        if self._is_classic_scam_combo(signals):
            score *= 1.25  # 25% boost for known scam patterns
        
        # 4. Multi-turn escalation
        if conversation_history and len(conversation_history) > 0:
            turn_multiplier = self._calculate_turn_multiplier(
                signals, conversation_history
            )
            score *= turn_multiplier
        
        # 5. First message cap (prevent aggressive flagging)
        if is_first_message:
            score = self._apply_first_message_cap(score, signals)
        
        # Ensure score is within [0.0, 1.0]
        return min(max(score, 0.0), 1.0)
    
    def _calculate_base_score(self, signals: List[SignalType]) -> float:
        """Calculate base score from signal weights"""
        # Use maximum weight among signals, not sum (to avoid score explosion)
        # But add partial credit for additional signals
        if not signals:
            return 0.0
        
        weights = sorted([get_signal_weight(sig) for sig in signals], reverse=True)
        
        # Primary signal weight
        score = weights[0]
        
        # Add diminishing returns for additional signals
        for i, weight in enumerate(weights[1:], start=1):
            decay_factor = 0.5 ** i  # Exponential decay
            score += weight * decay_factor
        
        return score
    
    def _get_unique_categories(self, signals: List[SignalType]) -> Set[SignalCategory]:
        """Get unique categories present in signals"""
        return set(get_signal_category(sig) for sig in signals)
    
    def _has_high_severity_signals(self, signals: List[SignalType]) -> bool:
        """Check if any high-severity signals are present"""
        high_severity = {
            SignalType.OTP_REQUEST,
            SignalType.PIN_REQUEST,
            SignalType.CARD_DETAILS_REQUEST,
            SignalType.ACCOUNT_NUMBER_REQUEST,
        }
        return any(sig in high_severity for sig in signals)
    
    def _is_classic_scam_combo(self, signals: List[SignalType]) -> bool:
        """
        Detect classic scam combinations:
        - Payment request + account threat
        - UPI/Account details + urgency + authority
        """
        has_payment = any(
            sig in {
                SignalType.UPI_REQUEST,
                SignalType.ACCOUNT_NUMBER_REQUEST,
                SignalType.OTP_REQUEST,
                SignalType.PIN_REQUEST,
                SignalType.CARD_DETAILS_REQUEST
            }
            for sig in signals
        )
        
        has_threat = any(
            sig in {
                SignalType.ACCOUNT_THREAT,
                SignalType.ACCOUNT_SUSPENSION,
                SignalType.KYC_FAILURE
            }
            for sig in signals
        )
        
        has_authority = any(
            sig in {
                SignalType.BANK_IMPERSONATION,
                SignalType.AUTHORITY_IMPERSONATION,
                SignalType.GOVERNMENT_IMPERSONATION
            }
            for sig in signals
        )
        
        # Classic combo: payment + threat, or payment + authority
        return (has_payment and has_threat) or (has_payment and has_authority)
    
    def _calculate_turn_multiplier(
        self,
        current_signals: List[SignalType],
        conversation_history: List[dict]
    ) -> float:
        """
        Calculate multiplier based on conversation progression.
        Increases confidence when scam signals persist/escalate across turns.
        """
        turn_count = len(conversation_history) + 1  # +1 for current message
        
        if turn_count == 1:
            return 1.0  # No multiplier for first message
        
        # Count how many previous turns had scam signals
        # (This is simplified; in real implementation, you'd track this)
        turns_with_signals = turn_count  # Assume all turns have signals if we're here
        
        # Progressive multiplier: 1.0 -> 1.1 -> 1.2 -> 1.3 (caps at 1.3)
        multiplier = 1.0 + min(0.1 * (turns_with_signals - 1), 0.3)
        
        # Additional boost if conversation patterns detected
        conversation_pattern_signals = {
            SignalType.REPETITION,
            SignalType.ESCALATION,
            SignalType.IGNORING_QUESTIONS,
            SignalType.COPY_PASTE,
        }
        
        if any(sig in conversation_pattern_signals for sig in current_signals):
            multiplier += 0.1
        
        return min(multiplier, 1.4)  # Cap at 1.4x
    
    def _apply_first_message_cap(self, score: float, signals: List[SignalType]) -> float:
        """
        Apply cap to first message to avoid false positives.
        Only very clear scams should exceed 0.6 on first message.
        """
        # If score is high AND contains critical signals, allow it
        critical_signals = {
            SignalType.OTP_REQUEST,
            SignalType.PIN_REQUEST,
            SignalType.CARD_DETAILS_REQUEST,
        }
        
        # Payment requests are also high severity
        payment_signals = {
            SignalType.UPI_REQUEST,
            SignalType.ACCOUNT_NUMBER_REQUEST,
        }
        
        has_critical = any(sig in critical_signals for sig in signals)
        has_payment = any(sig in payment_signals for sig in signals)
        
        # Check for pressure/threat signals
        has_pressure = any(
            get_signal_category(sig) in [
                SignalCategory.URGENCY_PRESSURE,
                SignalCategory.ACCOUNT_AUTHORITY
            ]
            for sig in signals
        )
        
        # Count different categories
        categories = self._get_unique_categories(signals)
        
        if has_critical and has_pressure:
            # OTP/PIN + urgency/threat = obvious scam
            return min(score, 0.95)
        elif has_critical:
            # OTP/PIN alone (requesting sensitive info) = high confidence
            # Ensure it meets detection threshold
            return max(min(score, 0.80), 0.70)  # Ensure >= 0.70 for detection
        elif has_payment and has_pressure:
            # UPI/Account + urgency/threat = high confidence
            return min(score, 0.85)
        elif len(categories) >= 3:
            # Multiple categories = higher confidence
            return min(score, 0.75)
        elif len(signals) >= 3:
            # Multiple signals but fewer categories -> moderate confidence
            return min(score, 0.65)
        else:
            # Single or double non-critical signals -> low confidence
            return min(score, 0.55)
    
    def is_scam_detected(self, confidence: float) -> bool:
        """
        Determine if scam is detected based on confidence threshold.
        
        STRICT RULE: scamDetected = true if confidence >= 0.7
        """
        return confidence >= self.SCAM_DETECTION_THRESHOLD
    
    def get_confidence_explanation(self, confidence: float, signals: List[SignalType]) -> str:
        """
        Generate human-readable explanation of confidence score.
        """
        if confidence < 0.4:
            level = "Very low suspicion"
        elif confidence < 0.6:
            level = "Low to moderate suspicion"
        elif confidence < 0.7:
            level = "Moderate suspicion (below detection threshold)"
        elif confidence < 0.85:
            level = "High confidence scam"
        else:
            level = "Very high confidence scam"
        
        categories = self._get_unique_categories(signals)
        category_names = [cat.value for cat in categories]
        
        return f"{level} - {len(signals)} signals across {len(categories)} categories: {', '.join(category_names)}"


def score_message(
    signals: List[SignalType],
    conversation_history: List[dict] = None
) -> Dict[str, any]:
    """
    Main scoring function. Returns confidence and scam detection decision.
    
    Args:
        signals: Detected signals in current message
        conversation_history: Optional conversation history
    
    Returns:
        Dictionary with:
        - confidence: float [0.0, 1.0]
        - scamDetected: bool
        - explanation: str
    """
    scorer = ConfidenceScorer()
    
    is_first_message = not conversation_history or len(conversation_history) == 0
    
    confidence = scorer.calculate_confidence(
        signals=signals,
        conversation_history=conversation_history,
        is_first_message=is_first_message
    )
    
    scam_detected = scorer.is_scam_detected(confidence)
    
    explanation = scorer.get_confidence_explanation(confidence, signals)
    
    return {
        "confidence": round(confidence, 2),
        "scamDetected": scam_detected,
        "scoreExplanation": explanation
    }


def validate_confidence_range(confidence: float) -> float:
    """Ensure confidence is in valid range [0.0, 1.0]"""
    return min(max(confidence, 0.0), 1.0)
