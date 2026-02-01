"""
Forensic Analysis Generator
Produces comprehensive session analysis reports for law enforcement and research
"""

import logging
from typing import Dict, List, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class ForensicAnalyzer:
    """Generates forensic-grade session analysis reports"""
    
    def __init__(self):
        logger.info("ForensicAnalyzer initialized")
    
    def generate_forensic_summary(self, session) -> Dict[str, Any]:
        """
        Generate comprehensive forensic analysis for a session
        
        Args:
            session: Session object with conversation history
            
        Returns:
            Detailed forensic analysis dict
        """
        # Classify attack type
        attack_classification = self._classify_attack(session)
        
        # Analyze tactics
        tactical_analysis = self._analyze_tactics(session)
        
        # Assess intelligence quality
        intelligence_quality = self._assess_intelligence_quality(session)
        
        # Extract key artifacts
        extracted_artifacts = self._extract_artifacts(session)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(session, attack_classification)
        
        return {
            "session_id": session.session_id,
            "timestamp": datetime.now().isoformat(),
            "attack_classification": attack_classification,
            "tactical_analysis": tactical_analysis,
            "intelligence_quality": intelligence_quality,
            "extracted_artifacts": extracted_artifacts,
            "recommendations": recommendations,
            "engagement_summary": {
                "total_turns": len(session.history),
                "duration_seconds": (datetime.now() - session.start_time).total_seconds(),
                "final_state": session.state.value if hasattr(session, 'state') else "unknown"
            }
        }
    
    def _classify_attack(self, session) -> Dict[str, str]:
        """Classify the attack type and risk level"""
        signals = getattr(session, 'scam_signals', [])
        profile = getattr(session, 'scammer_profile', {})
        
        # Determine primary attack type
        if "payment_demand" in signals or "upi" in signals:
            attack_type = "Payment Fraud / UPI Scam"
            risk_level = "high"
        elif "suspicious_link" in signals or "phishing" in signals:
            attack_type = "Phishing Attack"
            risk_level = "high"
        elif "authority_claim" in signals or "impersonation" in signals:
            attack_type = "Authority Impersonation"
            risk_level = "high"
        elif "urgency" in signals and "threat" in signals:
            attack_type = "Urgency-Based Social Engineering"
            risk_level = "medium"
        else:
            attack_type = "Generic Social Engineering"
            risk_level = "medium"
        
        # Adjust risk based on profile confidence
        if profile.get("confidence", 0) > 0.9:
            risk_level = "critical"
        
        return {
            "attack_type": attack_type,
            "risk_level": risk_level,
            "scammer_archetype": profile.get("type", "Unknown"),
            "confidence": profile.get("confidence", 0.0)
        }
    
    def _analyze_tactics(self, session) -> Dict[str, Any]:
        """Analyze scammer tactics and behavior patterns"""
        signals = getattr(session, 'scam_signals', [])
        history = session.history
        profile = getattr(session, 'scammer_profile', {})
        
        # Count different tactical categories
        urgency_count = sum(1 for s in signals if s in ["urgency", "threat", "time_pressure", "deadline"])
        payment_count = sum(1 for s in signals if s in ["payment_demand", "upi", "fee"])
        authority_count = sum(1 for s in signals if s in ["authority_claim", "impersonation", "official"])
        technical_count = sum(1 for s in signals if s in ["suspicious_link", "phishing", "download"])
        
        # Determine behavior consistency
        scammer_messages = [msg for msg in history if msg.get("role") == "scammer"]
        message_count = len(scammer_messages)
        
        # Calculate persistence
        persistence_level = "low"
        if message_count > 5:
            persistence_level = "high"
        elif message_count > 3:
            persistence_level = "medium"
        
        # Analyze adaptability
        adaptability = "rigid"
        if profile.get("secondaryType"):
            adaptability = "adaptive"
        
        return {
            "behavior_consistency": profile.get("type", "Unknown"),
            "scammer_adaptability": adaptability,
            "persistence_level": persistence_level,
            "message_count": message_count,
            "sophistication": self._assess_sophistication(signals, message_count),
            "tactical_breakdown": {
                "urgency_tactics": urgency_count,
                "payment_tactics": payment_count,
                "authority_tactics": authority_count,
                "technical_tactics": technical_count
            }
        }
    
    def _assess_sophistication(self, signals: List[str], message_count: int) -> str:
        """Assess scammer sophistication level"""
        unique_signals = len(set(signals))
        
        if unique_signals > 8 and message_count > 4:
            return "high"
        elif unique_signals > 5 or message_count > 3:
            return "medium"
        else:
            return "low"
    
    def _assess_intelligence_quality(self, session) -> Dict[str, Any]:
        """Assess the quality of intelligence gathered"""
        signals = getattr(session, 'scam_signals', [])
        history = session.history
        confidence_timeline = getattr(session, 'confidence_timeline', [])
        
        # Calculate metrics
        total_signals = len(signals)
        unique_signals = len(set(signals))
        conversation_depth = len(history)
        
        # Engagement quality
        engagement_depth = "shallow"
        if conversation_depth > 10:
            engagement_depth = "deep"
        elif conversation_depth > 5:
            engagement_depth = "moderate"
        
        # Intelligence value
        intelligence_value = "low"
        if unique_signals > 6 and conversation_depth > 5:
            intelligence_value = "high"
        elif unique_signals > 3 or conversation_depth > 3:
            intelligence_value = "medium"
        
        # Confidence progression
        confidence_trend = "unknown"
        if len(confidence_timeline) > 1:
            start_conf = confidence_timeline[0].get("confidence", 0)
            end_conf = confidence_timeline[-1].get("confidence", 0)
            if end_conf > start_conf + 0.2:
                confidence_trend = "increasing"
            elif end_conf < start_conf - 0.2:
                confidence_trend = "decreasing"
            else:
                confidence_trend = "stable"
        
        return {
            "total_signals": total_signals,
            "unique_signals": unique_signals,
            "engagement_depth": engagement_depth,
            "intelligence_value": intelligence_value,
            "confidence_progression": confidence_trend,
            "data_completeness": self._calculate_completeness(session)
        }
    
    def _calculate_completeness(self, session) -> float:
        """Calculate how complete the intelligence data is"""
        score = 0.0
        max_score = 5.0
        
        # Check for various data points
        if hasattr(session, 'scam_signals') and session.scam_signals:
            score += 1.0
        if hasattr(session, 'scammer_profile') and session.scammer_profile:
            score += 1.0
        if hasattr(session, 'confidence_timeline') and len(session.confidence_timeline) > 2:
            score += 1.0
        if len(session.history) > 5:
            score += 1.0
        if hasattr(session, 'response_delays') and session.response_delays:
            score += 1.0
        
        return round(score / max_score, 2)
    
    def _extract_artifacts(self, session) -> Dict[str, List[str]]:
        """Extract key artifacts from conversation"""
        artifacts = {
            "phone_numbers": [],
            "upi_ids": [],
            "urls": [],
            "claimed_organizations": [],
            "keywords": []
        }
        
        # Extract from conversation history
        for msg in session.history:
            if msg.get("role") == "scammer":
                text = msg.get("message", "")
                text_lower = text.lower()
                
                # Extract phone numbers (simple pattern)
                import re
                phones = re.findall(r'\b\d{10}\b', text)
                artifacts["phone_numbers"].extend(phones)
                
                # Extract UPI IDs
                upi_matches = re.findall(r'[\w\.-]+@[\w\.-]+', text)
                artifacts["upi_ids"].extend([u for u in upi_matches if any(
                    provider in u.lower() for provider in ['paytm', 'gpay', 'phonepe', 'upi']
                )])
                
                # Extract URLs
                url_matches = re.findall(r'https?://[^\s]+|bit\.ly/[^\s]+', text)
                artifacts["urls"].extend(url_matches)
                
                # Extract claimed organizations
                orgs = ["rbi", "sbi", "hdfc", "icici", "police", "income tax", "cyber cell"]
                for org in orgs:
                    if org in text_lower:
                        artifacts["claimed_organizations"].append(org.upper())
        
        # Deduplicate
        for key in artifacts:
            artifacts[key] = list(set(artifacts[key]))
        
        # Extract keywords from signals
        signals = getattr(session, 'scam_signals', [])
        artifacts["keywords"] = list(set(signals))[:15]
        
        return artifacts
    
    def _generate_recommendations(self, session, attack_classification: Dict) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        risk_level = attack_classification.get("risk_level", "medium")
        attack_type = attack_classification.get("attack_type", "")
        
        # Risk-based recommendations
        if risk_level in ["high", "critical"]:
            recommendations.append("IMMEDIATE ACTION: Report to cybercrime authorities")
            recommendations.append("Block all extracted phone numbers and UPI IDs")
        
        # Attack-specific recommendations
        if "payment" in attack_type.lower() or "upi" in attack_type.lower():
            recommendations.append("Alert payment gateway providers about extracted UPI IDs")
            recommendations.append("Add UPI IDs to fraud database")
        
        if "phishing" in attack_type.lower():
            recommendations.append("Report URLs to domain registrars and hosting providers")
            recommendations.append("Submit URLs to phishing databases (PhishTank, etc.)")
        
        if "impersonation" in attack_type.lower():
            recommendations.append("Notify impersonated organization of fraud campaign")
            recommendations.append("Share attack patterns with organization's fraud prevention team")
        
        # General recommendations
        recommendations.append("Archive session data for legal proceedings")
        recommendations.append("Update scam detection patterns based on observed tactics")
        recommendations.append("Share intelligence with law enforcement and financial institutions")
        
        return recommendations
    
    def generate_markdown_report(self, forensic_data: Dict) -> str:
        """Generate markdown-formatted forensic report"""
        report = []
        
        # Header
        report.append("# FORENSIC SESSION ANALYSIS REPORT")
        report.append(f"\n**Session ID:** {forensic_data['session_id']}")
        report.append(f"**Timestamp:** {forensic_data['timestamp']}")
        report.append(f"**Analysis Status:** Complete\n")
        
        # Attack Classification
        report.append("## Attack Classification")
        attack = forensic_data['attack_classification']
        report.append(f"- **Attack Type:** {attack['attack_type']}")
        report.append(f"- **Risk Level:** {attack['risk_level'].upper()}")
        report.append(f"- **Scammer Archetype:** {attack['scammer_archetype']}")
        report.append(f"- **Detection Confidence:** {attack['confidence']:.2%}\n")
        
        # Tactical Analysis
        report.append("## Tactical Analysis")
        tactics = forensic_data['tactical_analysis']
        report.append(f"- **Behavior Pattern:** {tactics['behavior_consistency']}")
        report.append(f"- **Scammer Adaptability:** {tactics['scammer_adaptability']}")
        report.append(f"- **Persistence Level:** {tactics['persistence_level']}")
        report.append(f"- **Message Count:** {tactics['message_count']}")
        report.append(f"- **Sophistication:** {tactics['sophistication']}\n")
        
        report.append("### Tactical Breakdown")
        breakdown = tactics['tactical_breakdown']
        report.append(f"- Urgency Tactics: {breakdown['urgency_tactics']}")
        report.append(f"- Payment Tactics: {breakdown['payment_tactics']}")
        report.append(f"- Authority Tactics: {breakdown['authority_tactics']}")
        report.append(f"- Technical Tactics: {breakdown['technical_tactics']}\n")
        
        # Intelligence Quality
        report.append("## Intelligence Quality Assessment")
        intel = forensic_data['intelligence_quality']
        report.append(f"- **Total Signals Detected:** {intel['total_signals']}")
        report.append(f"- **Unique Signals:** {intel['unique_signals']}")
        report.append(f"- **Engagement Depth:** {intel['engagement_depth']}")
        report.append(f"- **Intelligence Value:** {intel['intelligence_value']}")
        report.append(f"- **Confidence Progression:** {intel['confidence_progression']}")
        report.append(f"- **Data Completeness:** {intel['data_completeness']:.0%}\n")
        
        # Extracted Artifacts
        report.append("## Extracted Artifacts")
        artifacts = forensic_data['extracted_artifacts']
        
        if artifacts['phone_numbers']:
            report.append(f"**Phone Numbers:** {', '.join(artifacts['phone_numbers'])}")
        if artifacts['upi_ids']:
            report.append(f"**UPI IDs:** {', '.join(artifacts['upi_ids'])}")
        if artifacts['urls']:
            report.append(f"**URLs:** {', '.join(artifacts['urls'])}")
        if artifacts['claimed_organizations']:
            report.append(f"**Claimed Organizations:** {', '.join(artifacts['claimed_organizations'])}")
        if artifacts['keywords']:
            report.append(f"**Detection Keywords:** {', '.join(artifacts['keywords'][:10])}")
        
        report.append("")
        
        # Recommendations
        report.append("## Recommended Actions")
        for i, rec in enumerate(forensic_data['recommendations'], 1):
            report.append(f"{i}. {rec}")
        
        report.append("")
        
        # Engagement Summary
        report.append("## Engagement Summary")
        summary = forensic_data['engagement_summary']
        report.append(f"- **Total Conversation Turns:** {summary['total_turns']}")
        report.append(f"- **Session Duration:** {summary['duration_seconds']:.1f} seconds")
        report.append(f"- **Final State:** {summary['final_state']}")
        
        report.append("\n---")
        report.append("*This report was auto-generated by the Agentic Honeypot Forensic Analyzer*")
        
        return "\n".join(report)


# Global instance for easy access
forensic_analyzer = ForensicAnalyzer()
