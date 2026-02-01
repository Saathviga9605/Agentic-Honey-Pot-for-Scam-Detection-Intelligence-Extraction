"""
Router module
Handles request routing and orchestration logic
"""

import logging
import time
from typing import Dict, Any, Optional
from session_manager import session_manager, SessionState

logger = logging.getLogger(__name__)

# Latency threshold in seconds
AGENT_RESPONSE_TIMEOUT = 3.0
FALLBACK_REPLY = "Please wait, I'm checking this."


class RequestRouter:
    """Routes requests between internal modules"""
    
    def __init__(self, scam_detector, intelligence_engine, agent_interface=None):
        """
        Initialize router with module dependencies
        
        Args:
            scam_detector: Scam detection module
            intelligence_engine: Intelligence extraction module
            agent_interface: Optional agent for generating replies
        """
        self.scam_detector = scam_detector
        self.intelligence_engine = intelligence_engine
        self.agent_interface = agent_interface
        logger.info("RequestRouter initialized")
    
    def process_message(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main orchestration flow
        
        Args:
            payload: Incoming message payload
            
        Returns:
            Response with reply message
        """
        session_id = payload.get("sessionId")
        message = payload.get("message", {})
        conversation_history = payload.get("conversationHistory", [])
        metadata = payload.get("metadata", {})
        
        logger.info(f"[{session_id}] Processing message from {message.get('sender')}")
        
        # Get or create session
        session = session_manager.get_or_create_session(session_id)
        
        # Store incoming message
        session.add_message(message)
        session.metadata = metadata
        
        # Merge with existing history
        if conversation_history:
            session.conversation_history = conversation_history + [message]
        
        # Step 1: Scam Detection
        scam_result = self._detect_scam(message.get("text", ""), session)
        
        # Store signals in session for agent context
        session.scam_signals = scam_result.get("signals", [])
        
        # Step 2: State transition based on detection
        if scam_result["is_scam"] and session.state == SessionState.INIT:
            session.transition_to(SessionState.SUSPECTED)
            session.scam_detected = True
        
        if session.scam_detected and session.state == SessionState.SUSPECTED:
            session.transition_to(SessionState.ENGAGING)
        
        # Step 3: Generate reply (with timeout handling)
        reply = self._generate_reply(session, message)
        
        # Step 4: Extract intelligence
        if session.scam_detected:
            intel_result = self._extract_intelligence(session)
            
            # Check if intelligence collection is complete
            if intel_result.get("complete", False):
                session.transition_to(SessionState.INTEL_COMPLETE)
                session.intelligence_ready = True
                
                # Trigger final callback
                self._trigger_final_callback(session)
        
        return {
            "status": "success",
            "reply": reply
        }
    
    def _detect_scam(self, text: str, session) -> Dict[str, Any]:
        """
        Call scam detector module
        
        Args:
            text: Message text
            session: Current session
            
        Returns:
            Detection result
        """
        try:
            result = self.scam_detector.analyze_message(
                text,
                context={
                    "history": session.conversation_history,
                    "metadata": session.metadata
                }
            )
            logger.info(f"[{session.session_id}] Scam detection: {result}")
            return result
        except Exception as e:
            logger.error(f"Scam detection error: {e}")
            return {"is_scam": False, "confidence": 0}
    
    def _generate_reply(self, session, incoming_message: Dict) -> str:
        """
        Generate reply with timeout handling
        
        Args:
            session: Current session
            incoming_message: Incoming message
            
        Returns:
            Reply text
        """
        # If no agent interface, return neutral reply
        if not self.agent_interface:
            return self._get_default_reply(session)
        
        # Measure latency
        start_time = time.time()
        
        try:
            # Get scam detection signals from session
            signals = []
            if hasattr(session, 'scam_signals'):
                signals = session.scam_signals
            
            # Attempt to get agent reply with signals and session context
            reply = self.agent_interface.generate_reply(
                conversation_history=session.conversation_history,
                metadata=session.metadata,
                session_id=session.session_id,
                signals=signals,
                agent_state=session.state.name
            )
            
            elapsed = time.time() - start_time
            
            # Check if timeout exceeded
            if elapsed > AGENT_RESPONSE_TIMEOUT:
                logger.warning(f"[{session.session_id}] Agent response timeout ({elapsed:.2f}s)")
                return FALLBACK_REPLY
            
            return reply
            
        except Exception as e:
            logger.error(f"Agent reply error: {e}")
            return self._get_default_reply(session)
    
    def _get_default_reply(self, session) -> str:
        """Get default contextual reply"""
        if session.message_count == 1:
            return "Can you tell me more about this?"
        elif session.message_count < 5:
            return "I see. What should I do next?"
        else:
            return "Please provide more details."
    
    def _extract_intelligence(self, session) -> Dict[str, Any]:
        """
        Extract intelligence from conversation
        
        Args:
            session: Current session
            
        Returns:
            Intelligence extraction result
        """
        try:
            result = self.intelligence_engine.analyze_conversation(
                session.conversation_history,
                session.session_id
            )
            logger.info(f"[{session.session_id}] Intelligence extraction: {result.get('complete', False)}")
            return result
        except Exception as e:
            logger.error(f"Intelligence extraction error: {e}")
            return {"complete": False}
    
    def _trigger_final_callback(self, session):
        """
        Trigger final callback to evaluation server
        
        Args:
            session: Current session
        """
        if session.state != SessionState.INTEL_COMPLETE:
            logger.warning(f"[{session.session_id}] Cannot trigger callback - not in INTEL_COMPLETE state")
            return
        
        try:
            # Get final intelligence report
            report = self.intelligence_engine.generate_final_report(session.session_id)
            
            # Send callback
            success = self.intelligence_engine.send_callback(
                session.session_id,
                session.scam_detected,
                session.message_count,
                report
            )
            
            if success:
                session.transition_to(SessionState.REPORTED)
                logger.info(f"[{session.session_id}] Final callback sent successfully")
            else:
                logger.error(f"[{session.session_id}] Final callback failed")
                
        except Exception as e:
            logger.error(f"Callback error: {e}")


def create_router(scam_detector, intelligence_engine, agent_interface=None):
    """Factory function to create router"""
    return RequestRouter(scam_detector, intelligence_engine, agent_interface)
