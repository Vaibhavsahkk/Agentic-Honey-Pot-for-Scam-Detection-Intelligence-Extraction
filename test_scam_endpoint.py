import requests
import json

url = "http://localhost:8015/detect"
headers = {"x-api-key": "test-api-key-12345"}
payload = {
    "sessionId": "test-session-1",
    "message": {
        "sender": "scammer",
        "text": "Hello, I am calling from your bank.",
        "timestamp": 1234567890
    },
    "conversationHistory": []
}

try:
    print(f"Testing {url}...")
    response = requests.post(url, json=payload, headers=headers)
    print(f"Status: {response.status_code}")
    print(response.json())
except Exception as e:
    print(f"Error: {e}")
