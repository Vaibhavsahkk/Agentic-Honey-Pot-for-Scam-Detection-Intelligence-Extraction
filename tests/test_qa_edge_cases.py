"""
QA Edge Cases & Adversarial Stress Testing Suite
Author: Principal QA Engineer
"""
import pytest
from app.core.extractor import IntelligenceExtractor

@pytest.fixture
def extractor():
    return IntelligenceExtractor()

def test_qa_empty_and_null_inputs(extractor):
    """Test 1: Empty and space-only inputs"""
    result = extractor.extract("")
    assert result["upiIds"] == []
    assert result["phishingLinks"] == []
    assert result["phoneNumbers"] == []

    result_spaces = extractor.extract("   \n\t   ")
    assert result_spaces["upiIds"] == []

def test_qa_massive_payload_stress(extractor):
    """Test 2: Extremely large text input (100,000 chars)"""
    large_text = "This is normal text. " * 5000 + "Contact upi@okaxis for refund. " + " Visit http://scam-site.com/fake "
    result = extractor.extract(large_text)
    assert "upi@okaxis" in result["upiIds"]
    assert "http://scam-site.com/fake" in result["phishingLinks"]

def test_qa_xss_sql_injection_payloads(extractor):
    """Test 3: XSS, SQLi, and script injection handling"""
    sqli_text = "' OR '1'='1'; DROP TABLE users; -- Send 5000 to hacker@ybl"
    xss_text = "<script>alert('XSS')</script> Visit http://malicious-xss.com/payload"
    
    res_sqli = extractor.extract(sqli_text)
    assert "hacker@ybl" in res_sqli["upiIds"]
    
    res_xss = extractor.extract(xss_text)
    assert "http://malicious-xss.com/payload" in res_xss["phishingLinks"]

def test_qa_unicode_emoji_payloads(extractor):
    """Test 4: Emojis and international unicode characters"""
    unicode_text = "Urgent alert! 🚨💸 Urgent transfer to target@okicici ⚡. Click https://verify-bank-id.org/kyc ✨"
    result = extractor.extract(unicode_text)
    assert "target@okicici" in result["upiIds"]
    assert "https://verify-bank-id.org/kyc" in result["phishingLinks"]

def test_qa_complex_upi_handles(extractor):
    """Test 5: Diverse UPI handle formats"""
    text = "Send to test.user123@icici or 9876543210@paytm or vendor@ybl"
    result = extractor.extract(text)
    assert "test.user123@icici" in result["upiIds"]
    assert "9876543210@paytm" in result["upiIds"]
    assert "vendor@ybl" in result["upiIds"]

def test_qa_ip_and_deep_urls(extractor):
    """Test 6: IP-based phishing URLs and deep link query parameters"""
    text = "Check http://192.168.1.1/login.php?user=admin&token=abc123xyz#sec or https://sub.domain.phish.co.in/path/to/page"
    result = extractor.extract(text)
    assert "http://192.168.1.1/login.php?user=admin&token=abc123xyz#sec" in result["phishingLinks"]
    assert "https://sub.domain.phish.co.in/path/to/page" in result["phishingLinks"]
