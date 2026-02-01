"""
Session Manager
Handles session lifecycle, state transitions, and conversation history
"""

from datetime import datetime
from typing import Dict, List, Optional
from enum import Enum
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SessionState(Enum):
    """Session state machine states"""
    INIT = "INIT"
    SUSPECTED = "SUSPECTED"
    ENGAGING = "ENGAGING"
    INTEL_COMPLETE = "INTEL_COMPLETE"
    REPORTED = "REPORTED"


class Session:
    """Session data structure"""
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.state = SessionState.INIT
        self.conversation_history = []
        self.history = []  # Alias for conversation_history (used by forensics)
        self.message_count = 0
        self.scam_detected = False
        self.created_at = datetime.utcnow()
        self.start_time = datetime.utcnow()  # Alias for created_at
        self.metadata = {}
        self.intelligence_ready = False
        
        # Enhancement fields
        self.confidence_timeline = []  # Track confidence evolution
        self.scam_signals = []  # Accumulated scam signals
        self.scammer_profile = {}  # Behavior profile
        self.response_delays = []  # Track temporal realism
    
    def add_message(self, message: dict):
        """Add message to conversation history"""
        self.conversation_history.append({
            **message,
            "timestamp": message.get("timestamp", datetime.utcnow().isoformat())
        })
        self.history = self.conversation_history  # Keep alias in sync
        self.message_count += 1
    
    def add_confidence_snapshot(self, confidence: float, turn: int):
        """Track confidence evolution over time"""
        self.confidence_timeline.append({
            "turn": turn,
            "confidence": round(confidence, 2),
            "timestamp": datetime.utcnow().isoformat()
        })
    
    def add_response_delay(self, delay_ms: int):
        """Track response delays for temporal realism"""
        self.response_delays.append(delay_ms)
    
    def transition_to(self, new_state: SessionState):
        """Transition to new state with logging"""
        old_state = self.state
        self.state = new_state
        logger.info(f"[Session {self.session_id}] State transition: {old_state.value} -> {new_state.value}")
    
    def to_dict(self):
        """Convert session to dictionary"""
        return {
            "session_id": self.session_id,
            "state": self.state.value,
            "message_count": self.message_count,
            "scam_detected": self.scam_detected,
            "created_at": self.created_at.isoformat(),
            "intelligence_ready": self.intelligence_ready
        }


class SessionManager:
    """Manages all active sessions"""
    
    def __init__(self):
        self.sessions: Dict[str, Session] = {}
        logger.info("SessionManager initialized")
    
    def get_or_create_session(self, session_id: str) -> Session:
        """Get existing session or create new one"""
        if session_id not in self.sessions:
            logger.info(f"Creating new session: {session_id}")
            self.sessions[session_id] = Session(session_id)
        return self.sessions[session_id]
    
    def get_session(self, session_id: str) -> Optional[Session]:
        """Get existing session"""
        return self.sessions.get(session_id)
    
    def delete_session(self, session_id: str):
        """Delete session after completion"""
        if session_id in self.sessions:
            logger.info(f"Deleting session: {session_id}")
            del self.sessions[session_id]
    
    def get_active_sessions_count(self) -> int:
        """Get count of active sessions"""
        return len(self.sessions)
    
    def get_session_summary(self) -> List[dict]:
        """Get summary of all active sessions"""
        return [session.to_dict() for session in self.sessions.values()]


# Global session manager instance
session_manager = SessionManager()
