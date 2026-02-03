"""
Reporter Module
Generates final intelligence reports and coordinates callback
"""

import logging
from typing import Dict, Any
from extractor import intelligence_extractor
from guvi_callback import guvi_callback

logger = logging.getLogger(__name__)


class IntelligenceReporter:
    """Generates reports and sends callbacks"""
    
    def __init__(self):
        self.extractor = intelligence_extractor
        self.callback = guvi_callback
        logger.info("IntelligenceReporter initialized")
    
    def analyze_conversation(self, conversation_history: list, session_id: str) -> Dict[str, Any]:
        """
        Analyze conversation and extract intelligence
        
        Args:
            conversation_history: List of messages
            session_id: Session identifier
            
        Returns:
            Analysis result with completion status
        """
        return self.extractor.analyze_conversation(conversation_history, session_id)
    
    def get_session_intelligence(self, session_id: str) -> Dict[str, Any]:
        """
        Get stored intelligence for a session
        
        Args:
            session_id: Session identifier
            
        Returns:
            Intelligence data or empty dict
        """
        return self.extractor.get_session_intelligence(session_id)
    
    def generate_final_report(self, session_id: str) -> Dict[str, Any]:
        """
        Generate final intelligence report for session
        
        Args:
            session_id: Session identifier
            
        Returns:
            Complete intelligence report
        """
        intel = self.extractor.get_session_intelligence(session_id)
        
        if not intel:
            logger.warning(f"[{session_id}] No intelligence data found")
            return {
                "entities": {},
                "keywords": [],
                "behavior_summary": "No intelligence collected"
            }
        
        report = {
            "bank_accounts": intel.get("entities", {}).get("bank_accounts", []),
            "upi_ids": intel.get("entities", {}).get("upi_ids", []),
            "urls": intel.get("entities", {}).get("urls", []),
            "phone_numbers": intel.get("entities", {}).get("phone_numbers", []),
            "ifsc_codes": intel.get("entities", {}).get("ifsc_codes", []),
            "keywords": intel.get("keywords", []),
            "behavior_summary": intel.get("behavior_summary", "No summary available")
        }
        
        logger.info(f"[{session_id}] Final report generated")
        return report
    
    def send_callback(
        self,
        session_id: str,
        scam_detected: bool,
        total_messages: int,
        report: Dict[str, Any]
    ) -> bool:
        """
        Send final callback to evaluation server
        
        Args:
            session_id: Session identifier
            scam_detected: Whether scam was detected
            total_messages: Total messages exchanged
            report: Intelligence report
            
        Returns:
            True if successful, False otherwise
        """
        # Extract intelligence in callback format
        extracted_intelligence = {
            "bank_accounts": report.get("bank_accounts", []),
            "upi_ids": report.get("upi_ids", []),
            "urls": report.get("urls", []),
            "phone_numbers": report.get("phone_numbers", []),
            "keywords": report.get("keywords", [])
        }
        
        agent_notes = report.get("behavior_summary", "Scam conversation analyzed")
        
        # Send callback
        success = self.callback.send_final_result(
            session_id=session_id,
            scam_detected=scam_detected,
            total_messages=total_messages,
            extracted_intelligence=extracted_intelligence,
            agent_notes=agent_notes
        )
        
        # Clean up session intelligence after callback
        if success:
            self.extractor.clear_session(session_id)
        
        return success
    
    def get_statistics(self, session_id: str) -> Dict[str, Any]:
        """
        Get intelligence statistics for a session
        
        Args:
            session_id: Session identifier
            
        Returns:
            Statistics dictionary
        """
        intel = self.extractor.get_session_intelligence(session_id)
        
        if not intel:
            return {
                "entities_count": 0,
                "keywords_count": 0,
                "message_count": 0
            }
        
        entities = intel.get("entities", {})
        total_entities = sum(len(v) for v in entities.values())
        
        return {
            "entities_count": total_entities,
            "keywords_count": len(intel.get("keywords", [])),
            "message_count": intel.get("message_count", 0),
            "has_upi": len(entities.get("upi_ids", [])) > 0,
            "has_bank_accounts": len(entities.get("bank_accounts", [])) > 0,
            "has_urls": len(entities.get("urls", [])) > 0
        }


# Global instance
intelligence_reporter = IntelligenceReporter()