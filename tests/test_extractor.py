import pytest
import asyncio
from app.core.extractor import IntelligenceExtractor
from app.core.detector import ScamDetector

def test_upi_extraction():
    extractor = IntelligenceExtractor()
    text = "Please transfer money to rajesh123@paytm or scammer@okicici immediately"
    result = extractor.extract(text)
    
    assert "rajesh123@paytm" in result["upiIds"]
    assert "scammer@okicici" in result["upiIds"]
    assert len(result["upiIds"]) == 2

def test_phishing_link_extraction():
    extractor = IntelligenceExtractor()
    text = "Update your KYC at http://secure-bank-update.com/login or bit.ly/3xYz90"
    result = extractor.extract(text)
    
    assert "http://secure-bank-update.com/login" in result["phishingLinks"]
    assert "http://bit.ly/3xYz90" in result["phishingLinks"]

def test_phone_number_extraction():
    extractor = IntelligenceExtractor()
    text = "Call officer at +91 9876543210 or 9123456789"
    result = extractor.extract(text)
    
    assert "+919876543210" in result["phoneNumbers"]
    assert "+919123456789" in result["phoneNumbers"]

def test_scam_detection():
    detector = ScamDetector()
    
    async def run_detection():
        is_scam, confidence, scam_type = await detector.detect(
            "Your electricity bill is overdue. Pay immediately to avoid disconnection: send to bill@paytm",
            []
        )
        assert is_scam is True
        assert confidence > 0.2
        assert scam_type in ["ELECTRICITY_SCAM", "UPI_FRAUD"]

    asyncio.run(run_detection())
