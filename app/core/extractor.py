"""
Intelligence Extraction Engine
Extracts UPI IDs, phone numbers, bank accounts, links, and keywords using regex
"""
import logging
import re
from typing import Dict, List

logger = logging.getLogger(__name__)


class IntelligenceExtractor:
    """
    Regex-based extraction of scam-related intelligence
    Focuses on Indian financial identifiers
    """
    
    # Comprehensive regex patterns
    PATTERNS = {
        # UPI ID patterns (name@provider)
        "upiIds": re.compile(
            r'\b[a-zA-Z0-9.\-_]{2,256}@'
            r'(upi|paytm|ybl|oksbi|okhdfcbank|okicici|okaxis|'
            r'okbizaxis|ibl|axl|payzapp|ikwik|fam|apl|abf|pingpay|'
            r'olamoney|phonepe|googlepay|gpay|amazonpay)\b',
            re.IGNORECASE
        ),
        
        # Bank account numbers (9-18 digits, not part of longer number)
        "bankAccounts": re.compile(
            r'(?:account|a/c|acc|account number)[:\s]*(\d{9,18})\b',
            re.IGNORECASE
        ),
        
        # Indian phone numbers
        "phoneNumbers": re.compile(
            r'(?:\+91[\-\s]?)?[0]?(?:91)?[789]\d{9}\b'
        ),
        
        # URLs and links
        "phishingLinks": re.compile(
            r'http[s]?://(?:[a-zA-Z]|[0-9]|[$\-_@.&+]|[!*\\(\\),]|'
            r'(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        ),
        
        # Shortened URLs
        "shortenedLinks": re.compile(
            r'\b(bit\.ly|tinyurl\.com|goo\.gl|t\.co|ow\.ly|is\.gd|buff\.ly)/[a-zA-Z0-9]+\b',
            re.IGNORECASE
        )
    }
    
    # Suspicious keywords by category
    KEYWORD_CATEGORIES = {
        "urgency": ["urgent", "immediately", "now", "today", "expire", "last chance"],
        "authority": ["bank", "rbi", "government", "police", "official", "authorized"],
        "action": ["click", "verify", "update", "confirm", "share", "pay", "send"],
        "threat": ["blocked", "suspended", "terminated", "disconnected", "penalty", "legal action"],
        "financial": ["upi", "account", "payment", "transfer", "fee", "charge", "refund"]
    }
    
    def __init__(self):
        logger.info("🔬 IntelligenceExtractor initialized")
    
    def extract(self, text: str) -> Dict[str, List[str]]:
        """
        Extract all intelligence from text
        
        Returns dict with keys:
        - upiIds
        - bankAccounts
        - phoneNumbers
        - phishingLinks
        - suspiciousKeywords
        """
        results = {
            "upiIds": [],
            "bankAccounts": [],
            "phoneNumbers": [],
            "phishingLinks": [],
            "suspiciousKeywords": []
        }
        
        # Extract UPI IDs
        upi_matches = self.PATTERNS["upiIds"].findall(text)
        results["upiIds"] = self._deduplicate(upi_matches)
        
        # Extract bank accounts (capture group)
        account_matches = self.PATTERNS["bankAccounts"].findall(text)
        results["bankAccounts"] = self._deduplicate(account_matches)
        
        # Extract phone numbers
        phone_matches = self.PATTERNS["phoneNumbers"].findall(text)
        results["phoneNumbers"] = self._deduplicate(
            self._normalize_phones(phone_matches)
        )
        
        # Extract regular URLs
        link_matches = self.PATTERNS["phishingLinks"].findall(text)
        results["phishingLinks"].extend(link_matches)
        
        # Extract shortened URLs
        short_link_matches = self.PATTERNS["shortenedLinks"].findall(text)
        results["phishingLinks"].extend([f"http://{match}" for match in short_link_matches])
        results["phishingLinks"] = self._deduplicate(results["phishingLinks"])
        
        # Extract suspicious keywords
        results["suspiciousKeywords"] = self._extract_keywords(text)
        
        # Log extraction results
        if any(len(v) > 0 for v in results.values()):
            logger.info(
                f"📦 Extracted: "
                f"{len(results['upiIds'])} UPIs, "
                f"{len(results['bankAccounts'])} accounts, "
                f"{len(results['phoneNumbers'])} phones, "
                f"{len(results['phishingLinks'])} links"
            )
        
        return results
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract suspicious keywords from text"""
        text_lower = text.lower()
        found_keywords = []
        
        for category, keywords in self.KEYWORD_CATEGORIES.items():
            for keyword in keywords:
                if keyword in text_lower and keyword not in found_keywords:
                    found_keywords.append(keyword)
        
        return found_keywords
    
    def _deduplicate(self, items: List[str]) -> List[str]:
        """Remove duplicates while preserving order"""
        seen = set()
        result = []
        for item in items:
            item_lower = item.lower()
            if item_lower not in seen:
                seen.add(item_lower)
                result.append(item)
        return result
    
    def _normalize_phones(self, phones: List[str]) -> List[str]:
        """Normalize phone numbers to standard format"""
        normalized = []
        for phone in phones:
            # Remove all non-digits
            digits = re.sub(r'\D', '', phone)
            
            # Remove leading 0 or 91
            if digits.startswith('0'):
                digits = digits[1:]
            if digits.startswith('91') and len(digits) > 10:
                digits = digits[2:]
            
            # Should be exactly 10 digits now
            if len(digits) == 10 and digits[0] in '789':
                normalized.append(f"+91{digits}")
        
        return normalized
    
    def validate_upi(self, upi_id: str) -> bool:
        """Validate UPI ID format"""
        return bool(self.PATTERNS["upiIds"].match(upi_id))
    
    def validate_phone(self, phone: str) -> bool:
        """Validate phone number format"""
        digits = re.sub(r'\D', '', phone)
        return len(digits) == 10 and digits[0] in '789'
