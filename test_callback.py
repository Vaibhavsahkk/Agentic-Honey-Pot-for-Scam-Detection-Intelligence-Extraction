"""
End-to-End Callback Test
Tests the complete flow including callback to mock GUVI server
"""
import requests
import json
import time
import subprocess
import sys
from pathlib import Path

API_URL = "http://localhost:8010"
MOCK_GUVI_URL = "http://localhost:9000"
API_KEY = "test-api-key-12345"


def check_server(url, name):
    """Check if server is running"""
    try:
        response = requests.get(url, timeout=2)
        print(f"✅ {name} is running")
        return True
    except:
        print(f"❌ {name} is NOT running")
        return False


def test_callback_flow():
    """Test complete flow with callback"""
    print("\n" + "="*60)
    print("🧪 END-TO-END CALLBACK TEST")
    print("="*60 + "\n")
    
    # Check servers
    print("1️⃣ Checking servers...")
    honeypot_running = check_server(f"{API_URL}/health", "Honeypot API")
    mock_guvi_running = check_server(f"{MOCK_GUVI_URL}", "Mock GUVI Server")
    
    if not honeypot_running:
        print("\n⚠️ Start honeypot server first:")
        print("   python -m app.main")
        return
    
    if not mock_guvi_running:
        print("\n⚠️ Start mock GUVI server first:")
        print("   python mock_guvi_server.py")
        return
    
    print("\n2️⃣ Starting conversation...")
    session_id = f"callback-test-{int(time.time())}"
    history = []
    
    # Send messages that will trigger callback
    messages = [
        "Your SBI KYC expired. Update immediately at bit.ly/fake-kyc",
        "Pay Rs 500 to verify@scam.paytm now or account blocked",
        "Call 9876543210 immediately to verify",
        "Last warning! Send payment or account suspended"
    ]
    
    for i, msg in enumerate(messages, 1):
        print(f"\n   Turn {i}: Sending scam message...")
        
        request_data = {
            "sessionId": session_id,
            "message": {
                "sender": "scammer",
                "text": msg,
                "timestamp": int(time.time() * 1000)
            },
            "conversationHistory": history,
            "metadata": {
                "channel": "SMS",
                "language": "English",
                "locale": "IN"
            }
        }
        
        response = requests.post(
            f"{API_URL}/detect",
            json=request_data,
            headers={"x-api-key": API_KEY},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Victim replied: {result['reply'][:60]}...")
            
            history.append({
                "sender": "scammer",
                "text": msg,
                "timestamp": int(time.time() * 1000)
            })
            history.append({
                "sender": "user",
                "text": result['reply'],
                "timestamp": int(time.time() * 1000)
            })
        else:
            print(f"   ❌ Error: {response.status_code}")
            return
        
        time.sleep(1)
    
    print("\n3️⃣ Checking if callback was sent...")
    time.sleep(2)  # Wait for callback to be processed
    
    # Check mock GUVI server for received callbacks
    response = requests.get(f"{MOCK_GUVI_URL}/api/listCallbacks")
    
    if response.status_code == 200:
        data = response.json()
        callbacks = data.get("callbacks", [])
        
        # Find our session
        our_callback = next(
            (cb for cb in callbacks if cb["payload"]["sessionId"] == session_id),
            None
        )
        
        if our_callback:
            print("\n" + "="*60)
            print("✅ CALLBACK SUCCESSFULLY RECEIVED!")
            print("="*60)
            payload = our_callback["payload"]
            print(f"🆔 Session: {payload['sessionId']}")
            print(f"💬 Messages: {payload['totalMessagesExchanged']}")
            print(f"📊 Intelligence:")
            intel = payload["extractedIntelligence"]
            print(f"   💳 UPI IDs: {intel['upiIds']}")
            print(f"   🔗 Links: {intel['phishingLinks']}")
            print(f"   📞 Phones: {intel['phoneNumbers']}")
            print(f"\n📝 Notes: {payload['agentNotes']}")
            print("="*60)
            print("\n🎉 TEST PASSED! Callback flow working correctly!\n")
        else:
            print(f"\n⚠️ Callback not found for session {session_id}")
            print(f"Total callbacks received: {len(callbacks)}")
            if callbacks:
                print("Sessions found:", [cb["payload"]["sessionId"] for cb in callbacks])
    else:
        print(f"\n❌ Failed to check callbacks: {response.status_code}")


def main():
    print("\n📋 SETUP INSTRUCTIONS:")
    print("="*60)
    print("1. Terminal 1: python -m app.main")
    print("2. Terminal 2: python mock_guvi_server.py")
    print("3. Terminal 3: python test_callback.py")
    print("="*60)
    
    input("\nPress Enter when both servers are running...")
    test_callback_flow()


if __name__ == "__main__":
    main()
