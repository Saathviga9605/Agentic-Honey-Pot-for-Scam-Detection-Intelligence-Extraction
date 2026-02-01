"""
Agent Strategy Selector
Determines agent behavior mode based on scammer profile and engagement context
"""

import logging
from enum import Enum
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class AgentStrategy(Enum):
    """Agent strategy modes for intelligent engagement"""
    PASSIVE_VERIFY = "PASSIVE_VERIFY"    # Slow clarification questions
    ANXIOUS_COMPLY = "ANXIOUS_COMPLY"    # Worried, cooperative tone
    STALL_AND_PROBE = "STALL_AND_PROBE"  # Deliberate delays + verification traps


class StrategySelector:
    """Selects optimal agent strategy based on scammer behavior"""
    
    @staticmethod
    def select_strategy(
        scammer_profile: Dict,
        confidence_score: float,
        message_count: int,
        signals: List[str]
    ) -> AgentStrategy:
        """
        Select agent strategy based on engagement context
        
        Args:
            scammer_profile: Scammer behavior profile
            confidence_score: Scam detection confidence
            message_count: Number of exchanges
            signals: Current detection signals
            
        Returns:
            Selected strategy mode
        """
        scammer_type = scammer_profile.get("type", "Unknown")
        
        # Early stage (1-2 messages): Use passive verification
        if message_count <= 2:
            return AgentStrategy.PASSIVE_VERIFY
        
        # High urgency scammer: Respond with anxious compliance to engage longer
        if scammer_type == "Urgency Enforcer" and confidence_score > 0.7:
            return AgentStrategy.ANXIOUS_COMPLY
        
        # Payment/Link pushers: Use stall and probe to elicit more info
        if scammer_type in ["Payment Redirector", "Link Pusher"] and message_count > 3:
            return AgentStrategy.STALL_AND_PROBE
        
        # Authority impersonator: Show anxious compliance
        if scammer_type == "Authority Impersonator":
            return AgentStrategy.ANXIOUS_COMPLY
        
        # Persistence attacker: Alternate between anxious and stalling
        if scammer_type == "Persistence Attacker":
            return AgentStrategy.STALL_AND_PROBE if message_count % 2 == 0 else AgentStrategy.ANXIOUS_COMPLY
        
        # Default: Passive verification
        return AgentStrategy.PASSIVE_VERIFY


class StrategyModifiers:
    """Modifies agent responses based on selected strategy"""
    
    STRATEGY_CHARACTERISTICS = {
        AgentStrategy.PASSIVE_VERIFY: {
            "delay_multiplier": 1.2,
            "question_probability": 0.8,
            "concern_level": "low",
            "compliance_level": "low",
            "probing_level": "medium"
        },
        AgentStrategy.ANXIOUS_COMPLY: {
            "delay_multiplier": 0.8,
            "question_probability": 0.5,
            "concern_level": "high",
            "compliance_level": "high",
            "probing_level": "low"
        },
        AgentStrategy.STALL_AND_PROBE: {
            "delay_multiplier": 1.8,
            "question_probability": 0.9,
            "concern_level": "medium",
            "compliance_level": "low",
            "probing_level": "high"
        }
    }
    
    @staticmethod
    def apply_strategy(base_reply: str, strategy: AgentStrategy) -> str:
        """
        Modify base reply according to strategy
        
        Args:
            base_reply: Original agent reply
            strategy: Selected strategy
            
        Returns:
            Modified reply with strategy-appropriate tone
        """
        characteristics = StrategyModifiers.STRATEGY_CHARACTERISTICS[strategy]
        
        # Strategy-specific modifications
        if strategy == AgentStrategy.ANXIOUS_COMPLY:
            # Add worried, cooperative phrases
            prefixes = [
                "Oh my! ",
                "I'm worried about this. ",
                "This sounds serious. ",
                "I want to help resolve this. "
            ]
            import random
            if random.random() < characteristics["concern_level"] == "high":
                base_reply = random.choice(prefixes) + base_reply
        
        elif strategy == AgentStrategy.STALL_AND_PROBE:
            # Add hesitation and verification requests
            suffixes = [
                " Can you verify your employee ID first?",
                " Let me just confirm something - which office are you calling from?",
                " I need to check with my bank first.",
                " Can you give me a reference number?"
            ]
            import random
            if random.random() < characteristics["probing_level"] == "high":
                base_reply = base_reply + random.choice(suffixes)
        
        elif strategy == AgentStrategy.PASSIVE_VERIFY:
            # Keep it simple, ask clarifying questions
            clarifiers = [
                " Could you please explain that again?",
                " I'm not sure I understand.",
                " Can you tell me more about this?",
                " What exactly do you need from me?"
            ]
            import random
            if random.random() < characteristics["question_probability"]:
                base_reply = base_reply + random.choice(clarifiers)
        
        return base_reply
    
    @staticmethod
    def calculate_response_delay(
        base_delay: float,
        strategy: AgentStrategy,
        message_length: int
    ) -> int:
        """
        Calculate response delay in milliseconds
        
        Args:
            base_delay: Base delay in ms
            strategy: Selected strategy
            message_length: Length of message to respond to
            
        Returns:
            Calculated delay in milliseconds
        """
        # Complexity factor based on message length
        complexity_factor = 1.0 + (message_length / 200.0)  # Longer messages = more thinking time
        
        # Strategy multiplier
        multiplier = StrategyModifiers.STRATEGY_CHARACTERISTICS[strategy]["delay_multiplier"]
        
        return int(base_delay * multiplier * complexity_factor)


# Global instance for easy access
strategy_selector = StrategySelector()
