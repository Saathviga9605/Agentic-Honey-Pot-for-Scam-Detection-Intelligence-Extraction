"""
Intelligence Extractor
Analyzes conversation history and extracts scam indicators
"""

import logging
from typing import Dict, List, Set, Any
from collections import Counter
from patterns import COMPILED_PATTERNS, get_keyword_categories

logger = logging.getLogger(__name__)

# Minimum occurrences for confidence-weighted intelligence
# Set to 1 so entities are captured on first occurrence
MIN_OCCURRENCE_THRESHOLD = 1


class IntelligenceExtractor:
    """Extracts and aggregates intelligence from conversations"""
    
    def __init__(self):
        self.patterns = COMPILED_PATTERNS
        self.keyword_categories = get_keyword_categories()
        # Store extracted intelligence per session
        self.session_intelligence = {}
        logger.info("IntelligenceExtractor initialized")
    
    def analyze_conversation(self, conversation_history: List[Dict], session_id: str) -> Dict[str, Any]:
        """
        Analyze conversation and extract intelligence
        
        Args:
            conversation_history: List of messages
            session_id: Session identifier
            
        Returns:
            Intelligence analysis result with completion status
        """
        # Extract all text from conversation
        full_text = self._extract_text(conversation_history)
        
        # Extract entities
        entities = self._extract_entities(full_text)
        
        # Extract keywords
        keywords = self._extract_keywords(full_text)
        
        # Generate behavior summary
        behavior_summary = self._generate_behavior_summary(keywords, len(conversation_history))
        
        # Store intelligence for this session
        self.session_intelligence[session_id] = {
            "entities": entities,
            "keywords": keywords,
            "behavior_summary": behavior_summary,
            "message_count": len(conversation_history)
        }
        
        # Determine if intelligence collection is complete
        is_complete = self._is_intelligence_complete(entities, keywords, len(conversation_history))
        
        logger.info(f"[{session_id}] Intelligence extraction complete: {is_complete}")
        
        return {
            "complete": is_complete,
            "entities_found": sum(len(v) for v in entities.values()),
            "keywords_found": len(keywords)
        }
    
    def _extract_text(self, conversation_history: List[Dict]) -> str:
        """
        Extract all text from conversation history
        
        Args:
            conversation_history: List of messages
            
        Returns:
            Combined text
        """
        texts = []
        for message in conversation_history:
            if isinstance(message, dict) and "text" in message:
                texts.append(message["text"])
        return " ".join(texts)
    
    def _extract_entities(self, text: str) -> Dict[str, List[str]]:
        """
        Extract entities using regex patterns
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary of extracted entities (always includes all entity types)
        """
        # Initialize with all entity types to ensure consistent structure
        entities = {
            "bank_accounts": [],
            "ifsc_codes": [],
            "phone_numbers": [],
            "upi_ids": [],
            "phishing_links": []  # Changed from "urls" to match expected schema
        }
        
        # Extract UPI IDs
        for pattern in self.patterns.get("upi_id", []):
            matches = pattern.findall(text)
            entities["upi_ids"].extend(matches)
        
        # Extract bank accounts
        for pattern in self.patterns.get("bank_account", []):
            matches = pattern.findall(text)
            if isinstance(matches[0] if matches else None, tuple):
                # Extract from capture groups
                matches = [m[0] if isinstance(m, tuple) else m for m in matches]
            entities["bank_accounts"].extend(matches)
        
        # Extract phone numbers
        for pattern in self.patterns.get("phone_number", []):
            matches = pattern.findall(text)
            entities["phone_numbers"].extend(matches)
        
        # Extract URLs/Phishing Links
        for pattern in self.patterns.get("url", []):
            matches = pattern.findall(text)
            entities["phishing_links"].extend(matches)
        
        # Extract IFSC codes
        for pattern in self.patterns.get("ifsc_code", []):
            matches = pattern.findall(text)
            entities["ifsc_codes"].extend(matches)
        
        # Deduplicate and ensure all keys exist (even if empty)
        filtered_entities = {
            "bank_accounts": list(set(entities["bank_accounts"])),
            "ifsc_codes": list(set(entities["ifsc_codes"])),
            "phone_numbers": list(set(entities["phone_numbers"])),
            "upi_ids": list(set(entities["upi_ids"])),
            "phishing_links": list(set(entities["phishing_links"]))
        }
        
        return filtered_entities
    
    def _extract_keywords(self, text: str) -> List[str]:
        """
        Extract suspicious keywords from text
        
        Args:
            text: Text to analyze
            
        Returns:
            List of detected keywords
        """
        text_lower = text.lower()
        detected_keywords = []
        
        for category, keyword_list in self.keyword_categories.items():
            for keyword in keyword_list:
                if keyword.lower() in text_lower:
                    detected_keywords.append(keyword)
        
        # Deduplicate
        return list(set(detected_keywords))
    
    def _generate_behavior_summary(self, keywords: List[str], message_count: int) -> str:
        """
        Generate behavior summary from keywords
        
        Args:
            keywords: Detected keywords
            message_count: Number of messages
            
        Returns:
            Behavior summary text
        """
        tactics = []
        
        # Categorize tactics
        urgency_keywords = [k for k in keywords if k in self.keyword_categories["urgency"]]
        threat_keywords = [k for k in keywords if k in self.keyword_categories["threats"]]
        payment_keywords = [k for k in keywords if k in self.keyword_categories["payment"]]
        impersonation_keywords = [k for k in keywords if k in self.keyword_categories["impersonation"]]
        credential_keywords = [k for k in keywords if k in self.keyword_categories["credential_request"]]
        
        if urgency_keywords:
            tactics.append("urgency pressure")
        
        if threat_keywords:
            tactics.append("threat-based coercion")
        
        if payment_keywords:
            tactics.append("payment redirection")
        
        if impersonation_keywords:
            tactics.append("authority impersonation")
        
        if credential_keywords:
            tactics.append("credential harvesting")
        
        if not tactics:
            return ""  # Return empty string for non-scam messages
        
        tactics_str = ", ".join(tactics)
        return f"Scammer used {tactics_str} across {message_count} messages"
    
    def _is_intelligence_complete(self, entities: Dict, keywords: List[str], message_count: int) -> bool:
        """
        Determine if intelligence collection is complete
        
        Args:
            entities: Extracted entities
            keywords: Detected keywords
            message_count: Number of messages
            
        Returns:
            True if complete, False otherwise
        """
        # Intelligence is complete if:
        # 1. UPI ID or Bank Account + IFSC extracted (payment details), OR
        # 2. Multiple phishing links found (2+), OR
        # 3. At least 10 messages exchanged with some entities
        
        # Check for complete payment details
        has_upi = len(entities.get("upi_ids", [])) > 0
        has_bank_details = (
            len(entities.get("bank_accounts", [])) > 0 and 
            len(entities.get("ifsc_codes", [])) > 0
        )
        
        if has_upi or has_bank_details:
            logger.info(f"Intelligence complete: Payment details extracted (UPI: {has_upi}, Bank: {has_bank_details})")
            return True
        
        # Check for multiple phishing links (strong indicator)
        phishing_links = len(entities.get("phishing_links", []))
        if phishing_links >= 2:
            logger.info(f"Intelligence complete: {phishing_links} phishing links detected")
            return True
        
        # Long conversation with some entities
        total_entities = sum(len(v) for v in entities.values())
        if message_count >= 10 and total_entities > 0:
            logger.info(f"Intelligence complete: {message_count} messages with {total_entities} entities")
            return True
        
        # Check for repeated credential harvesting attempts
        credential_keywords = [
            k for k in keywords 
            if k in self.keyword_categories.get("credential_request", [])
        ]
        
        if len(credential_keywords) >= 3:
            logger.info(f"Intelligence complete: {len(credential_keywords)} credential requests detected")
            return True
        
        return False
    
    def get_session_intelligence(self, session_id: str) -> Dict[str, Any]:
        """
        Get stored intelligence for a session
        
        Args:
            session_id: Session identifier
            
        Returns:
            Intelligence data or empty dict
        """
        return self.session_intelligence.get(session_id, {})
    
    def clear_session(self, session_id: str):
        """Clear intelligence data for a session"""
        if session_id in self.session_intelligence:
            del self.session_intelligence[session_id]
            logger.info(f"[{session_id}] Intelligence data cleared")


# Global instance
intelligence_extractor = IntelligenceExtractor()
print("")