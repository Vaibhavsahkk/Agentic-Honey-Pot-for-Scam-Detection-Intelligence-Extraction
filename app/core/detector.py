"""
Scam Detection Engine
Combines rule-based patterns with optional LLM classification
"""
import logging
import re
from typing import Tuple, List
from app.models import Message

logger = logging.getLogger(__name__)


class ScamDetector:
    """
    Multi-layered scam detection:
    1. Rule-based pattern matching (fast, reliable)
    2. LLM classification (optional, if API available)
    """
    
    # Scam patterns organized by category
    SCAM_PATTERNS = {
        "UPI_FRAUD": [
            r"upi\s*id", r"upi\s*payment", r"@(paytm|ybl|oksbi|okhdfcbank|okicici)",
            r"send\s*money", r"transfer\s*to", r"verification\s*fee", r"activate\s*upi"
        ],
        "KYC_FRAUD": [
            r"kyc\s*(expired|update|verify|pending|blocked)",
            r"(update|verify)\s*your\s*(kyc|account|details)",
            r"account\s*will\s*be\s*(blocked|suspended|closed)",
            r"account\s*(blocked|suspended|closed|expiry)",
            r"rbi\s*mandate", r"regulatory\s*compliance"
        ],
        "ELECTRICITY_SCAM": [
            r"electricity\s*bill", r"power\s*supply\s*(cut|disconnect)",
            r"pay\s*your\s*bill", r"overdue\s*(bill|payment)",
            r"connection\s*will\s*be\s*(cut|terminated)"
        ],
        "COURIER_SCAM": [
            r"(fedex|dhl|aramex|bluedart)\s*parcel",
            r"customs?\s*(duty|clearance|fee)", r"package\s*held",
            r"delivery\s*(pending|failed)", r"customs?\s*office"
        ],
        "JOB_SCAM": [
            r"(job|work)\s*(offer|opportunity|opening)",
            r"amazon\s*(hiring|recruitment)", r"part[\s-]?time\s*(job|work)",
            r"earn\s*(\₹|\d+)", r"registration\s*fee"
        ],
        "LOTTERY_PRIZE": [
            r"(won|winner|congratulations)", r"lottery\s*prize",
            r"claim\s*your\s*(prize|reward)", r"lucky\s*draw",
            r"₹\s*\d+\s*(lakh|crore)"
        ]
    }
    
    # Urgency indicators
    URGENCY_KEYWORDS = [
        "urgent", "immediate", "today", "now", "quickly", "hurry",
        "expire", "last chance", "limited time", "within 24 hours",
        "blocked", "suspended", "terminated", "disconnected"
    ]
    
    # Authority impersonation
    AUTHORITY_KEYWORDS = [
        "bank", "rbi", "government", "police", "cyber cell", "income tax",
        "customs", "courier company", "official", "authorized"
    ]
    
    # Suspicious actions
    SUSPICIOUS_ACTIONS = [
        "click", "link", "verify", "update", "confirm", "share",
        "send", "pay", "transfer", "deposit", "fee", "charge"
    ]
    
    def __init__(self):
        logger.info("🔍 ScamDetector initialized")
        self._compile_patterns()
    
    def _compile_patterns(self):
        """Pre-compile regex patterns for performance"""
        self.compiled_patterns = {}
        for category, patterns in self.SCAM_PATTERNS.items():
            self.compiled_patterns[category] = [
                re.compile(pattern, re.IGNORECASE) 
                for pattern in patterns
            ]
    
    async def detect(
        self, 
        message: str, 
        conversation_history: List[Message]
    ) -> Tuple[bool, float, str]:
        """
        Detect if message is a scam
        
        Returns:
            (is_scam, confidence, scam_type)
        """
        # Rule-based detection
        rule_result = self._rule_based_detection(message)
        
        # Very aggressive detection - catch everything suspicious
        # First message: trigger at 0.3+ confidence
        # With history: trigger at 0.2+ confidence
        # This ensures we engage and collect intelligence
        
        if rule_result["confidence"] > 0.2:
            return (
                True,
                rule_result["confidence"],
                rule_result["scam_type"]
            )
        
        # If we have conversation context, be even more generous
        if conversation_history and rule_result["confidence"] > 0.1:
            return (
                True,
                rule_result["confidence"],
                rule_result["scam_type"]
            )
        
        # Not a scam
        return (False, rule_result["confidence"], "NONE")
    
    def _rule_based_detection(self, message: str) -> dict:
        """
        Fast pattern-based detection
        Returns dict with confidence and scam_type
        """
        message_lower = message.lower()
        scores = {}
        
        # Check each scam category
        for category, patterns in self.compiled_patterns.items():
            matches = sum(1 for pattern in patterns if pattern.search(message))
            if matches > 0:
                scores[category] = matches / len(patterns)
        
        # Calculate additional signals
        urgency_score = sum(
            1 for keyword in self.URGENCY_KEYWORDS 
            if keyword in message_lower
        ) / len(self.URGENCY_KEYWORDS)
        
        authority_score = sum(
            1 for keyword in self.AUTHORITY_KEYWORDS 
            if keyword in message_lower
        ) / len(self.AUTHORITY_KEYWORDS)
        
        action_score = sum(
            1 for keyword in self.SUSPICIOUS_ACTIONS 
            if keyword in message_lower
        ) / len(self.SUSPICIOUS_ACTIONS)
        
        # Determine primary scam type
        if scores:
            scam_type = max(scores, key=scores.get)
            category_confidence = scores[scam_type]
            # Boost category confidence - if ANY patterns match, give at least 0.5
            if category_confidence > 0:
                category_confidence = max(0.6, category_confidence * 3)
        else:
            scam_type = "GENERIC_FRAUD"
            category_confidence = 0.0
        
        # Combined confidence calculation
        # Category match: 70% weight (more important)
        # Urgency/Authority/Action signals: 30% weight
        signal_score = (urgency_score + authority_score + action_score) / 3
        final_confidence = (category_confidence * 0.7) + (signal_score * 0.3)
        
        # Boost confidence if multiple signals present
        if urgency_score > 0.1 and authority_score > 0.05:
            final_confidence = min(1.0, final_confidence + 0.15)
        
        # Additional boost for specific high-risk keywords
        high_risk_keywords = ["kyc", "upi", "blocked", "suspended", "verify", "urgent"]
        high_risk_count = sum(1 for kw in high_risk_keywords if kw in message_lower)
        if high_risk_count >= 2:
            final_confidence = min(1.0, final_confidence + 0.1)
        
        logger.debug(
            f"Rule detection: {scam_type} "
            f"(category: {category_confidence:.2f}, "
            f"signals: {signal_score:.2f}, "
            f"final: {final_confidence:.2f})"
        )
        
        return {
            "confidence": final_confidence,
            "scam_type": scam_type,
            "signals": {
                "urgency": urgency_score,
                "authority": authority_score,
                "action": action_score
            }
        }
