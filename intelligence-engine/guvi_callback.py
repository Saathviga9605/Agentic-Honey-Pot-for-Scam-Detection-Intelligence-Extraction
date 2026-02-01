"""
GUVI Callback Module
Handles final callback to evaluation server with retry and persistence
"""

import requests
import logging
import time
import json
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

# Evaluation endpoint
GUVI_CALLBACK_URL = "https://hackathon.guvi.in/api/updateHoneyPotFinalResult"
CALLBACK_TIMEOUT = 5  # seconds

# Retry configuration
MAX_RETRIES = 3
RETRY_BACKOFF = [1, 3, 5]  # seconds between retries


class GUVICallback:
    """Handles callbacks to GUVI evaluation server with retry and persistence"""
    
    def __init__(self, callback_url: str = GUVI_CALLBACK_URL):
        self.callback_url = callback_url
        self.sent_callbacks = set()  # Track sent callbacks to prevent duplicates
        self.pending_reports = {}  # Track reports waiting for retry
        self.failed_reports_dir = Path(__file__).parent / "failed_reports"
        self.failed_reports_dir.mkdir(exist_ok=True)
        
        # For test access
        self.MAX_RETRIES = MAX_RETRIES
        self.RETRY_BACKOFF = RETRY_BACKOFF
        
        logger.info(f"GUVICallback initialized with URL: {callback_url}")
    
    def send_final_result(
        self,
        session_id: str,
        scam_detected: bool,
        total_messages: int,
        extracted_intelligence: Dict[str, Any],
        agent_notes: str
    ) -> bool:
        """
        Send final result to GUVI evaluation server with retry logic
        
        Args:
            session_id: Session identifier
            scam_detected: Whether scam was detected
            total_messages: Total messages exchanged
            extracted_intelligence: Extracted intelligence data
            agent_notes: Behavior summary notes
            
        Returns:
            True if successful, False otherwise
        """
        # Prevent duplicate callbacks
        if session_id in self.sent_callbacks:
            logger.warning(f"[{session_id}] Callback already sent, skipping")
            return True
        
        # Prepare payload
        payload = {
            "sessionId": session_id,
            "scamDetected": scam_detected,
            "totalMessagesExchanged": total_messages,
            "extractedIntelligence": {
                "bankAccounts": extracted_intelligence.get("bank_accounts", []),
                "upiIds": extracted_intelligence.get("upi_ids", []),
                "phishingLinks": extracted_intelligence.get("urls", []),
                "phoneNumbers": extracted_intelligence.get("phone_numbers", []),
                "suspiciousKeywords": extracted_intelligence.get("keywords", [])
            },
            "agentNotes": agent_notes
        }
        
        logger.info(f"[{session_id}] Sending final callback to {self.callback_url}")
        
        # Retry loop with exponential backoff
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                response = requests.post(
                    self.callback_url,
                    json=payload,
                    timeout=CALLBACK_TIMEOUT,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code in [200, 201, 202]:
                    logger.info(f"[{session_id}] Callback successful on attempt {attempt}")
                    self.sent_callbacks.add(session_id)
                    
                    # Remove from pending if it was there
                    if session_id in self.pending_reports:
                        del self.pending_reports[session_id]
                    
                    return True
                else:
                    logger.warning(f"[{session_id}] Callback failed with status {response.status_code} on attempt {attempt}")
                    
            except requests.exceptions.RequestException as e:
                logger.error(f"[{session_id}] Callback error on attempt {attempt}: {e}")
            
            # If not last attempt, wait before retry
            if attempt < MAX_RETRIES:
                backoff_time = RETRY_BACKOFF[attempt - 1]
                logger.info(f"[{session_id}] Retrying in {backoff_time} seconds...")
                time.sleep(backoff_time)
        
        # All retries failed - persist locally
        logger.error(f"[{session_id}] All {MAX_RETRIES} callback attempts failed, persisting locally")
        self._persist_failed_report(session_id, payload)
        self.pending_reports[session_id] = payload
        
        return False
    
    def _persist_failed_report(self, session_id: str, payload: Dict):
        """Persist failed report to local storage"""
        report_file = self.failed_reports_dir / f"{session_id}.json"
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(payload, f, indent=2)
            logger.info(f"[{session_id}] Report persisted to {report_file}")
        except Exception as e:
            logger.error(f"[{session_id}] Failed to persist report: {e}")
    
    def retry_pending_reports(self) -> int:
        """Retry all pending reports. Returns number of successful retries."""
        if not self.pending_reports:
            return 0
        
        logger.info(f"Retrying {len(self.pending_reports)} pending reports...")
        successful = 0
        
        for session_id, payload in list(self.pending_reports.items()):
            try:
                response = requests.post(
                    self.callback_url,
                    json=payload,
                    timeout=CALLBACK_TIMEOUT,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code in [200, 201, 202]:
                    logger.info(f"[{session_id}] Retry successful")
                    self.sent_callbacks.add(session_id)
                    del self.pending_reports[session_id]
                    successful += 1
            except Exception as e:
                logger.error(f"[{session_id}] Retry failed: {e}")
        
        return successful
    
    def has_sent_callback(self, session_id: str) -> bool:
        """Check if callback has already been sent for session"""
        return session_id in self.sent_callbacks
    
    def reset_callback_tracker(self, session_id: Optional[str] = None):
        """Reset callback tracker for testing purposes"""
        if session_id:
            self.sent_callbacks.discard(session_id)
        else:
            self.sent_callbacks.clear()
        logger.info(f"Callback tracker reset: {session_id or 'all'}")


# Global instance
guvi_callback = GUVICallback()
