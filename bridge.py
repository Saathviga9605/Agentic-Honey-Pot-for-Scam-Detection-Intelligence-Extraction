"""
Integration Bridge
Connects API Gateway with existing scam-detector modules and agent engine
"""

import sys
from pathlib import Path
from typing import Dict, Any, List
import logging

# Add parent directory to path to import existing modules
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))
sys.path.insert(0, str(current_dir / 'agent-engine'))

# Import existing scam detector
from detector import detect_scam

# Import agent engine
from persona import generate_reply_safe, get_session_info

logger = logging.getLogger(__name__)


class ScamDetectorBridge:
    """
    Bridge between API Gateway and existing scam detector
    Adapts interface for orchestration layer
    """
    
    def __init__(self):
        logger.info("ScamDetectorBridge initialized")
    
    def analyze_message(self, text: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Analyze message for scam indicators
        
        Args:
            text: Message text to analyze
            context: Additional context (history, metadata)
            
        Returns:
            Detection result with is_scam and confidence
        """
        if context is None:
            context = {}
        
        # Prepare input for existing detector
        input_data = {
            "text": text,
            "conversationHistory": context.get("history", []),
            "metadata": context.get("metadata", {})
        }
        
        try:
            # Call existing detector
            result = detect_scam(input_data)
            
            # Adapt output format for orchestration
            return {
                "is_scam": result.get("scamDetected", False),
                "confidence": result.get("confidence", 0.0),
                "signals": result.get("signals", []),
                "explanation": result.get("explanation", {})
            }
            
        except Exception as e:
            logger.error(f"Scam detection error: {e}")
            # Return safe default
            return {
                "is_scam": False,
                "confidence": 0.0,
                "signals": [],
                "explanation": {"error": str(e)}
            }


class AgentInterface:
    """
    Real Agent Engine Interface
    Uses persona-based response generation for natural, human-like replies
    """
    
    def __init__(self):
        logger.info("AgentInterface initialized with persona-based agent engine")
    
    def generate_reply(
        self, 
        conversation_history: list, 
        metadata: Dict = None,
        session_id: str = "default",
        signals: List[str] = None,
        agent_state: str = "ENGAGING"
    ) -> str:
        """
        Generate natural, persona-based reply to scammer
        
        Args:
            conversation_history: Previous messages
            metadata: Additional context
            session_id: Unique session ID for persona consistency
            signals: Scam detection signals for context-aware responses
            agent_state: Current agent state (INIT, SUSPECTED, ENGAGING, etc.)
            
        Returns:
            Generated reply text
        """
        if not conversation_history:
            return "Hello, how can I help you?"
        
        # Get the latest message from scammer
        last_message = conversation_history[-1]
        latest_text = last_message.get("text", "")
        
        # Use signals if not provided
        if signals is None:
            signals = []
        
        # Generate reply using real agent engine
        try:
            result = generate_reply_safe(
                latest_message=latest_text,
                conversation_history=conversation_history,
                signals=signals,
                agent_state=agent_state,
                session_id=session_id
            )
            
            reply = result.get("reply", "I received your message. Can you provide more details?")
            
            logger.info(f"[{session_id}] Agent reply generated using persona: {get_session_info(session_id).get('persona', 'unknown')}")
            
            return reply
            
        except Exception as e:
            logger.error(f"Agent reply generation error: {e}")
            # Fallback to safe default
            return "Sorry, I didn't understand that. Can you explain again?"


# Factory functions for clean initialization
def create_scam_detector_bridge():
    """Create scam detector bridge instance"""
    return ScamDetectorBridge()


def create_agent_interface():
    """Create agent interface instance"""
    return AgentInterface()
