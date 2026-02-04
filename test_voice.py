import base64
import requests
import json

# Create a small dummy mp3 file (1k of silence/noise) just to have valid base64
dummy_data = b'\xFF\xFB\x90\xC4\x00\x00' * 100 
base64_audio = base64.b64encode(dummy_data).decode('utf-8')

url = "http://localhost:8012/detect-voice"
headers = {"x-api-key": "test-api-key-12345"}
payload = {
    "language": "en",
    "audioFormat": "mp3",
    "audioBase64": base64_audio
}

print(f"Sending request to {url}...")
try:
    response = requests.post(url, json=payload, headers=headers)
    print(f"Status Code: {response.status_code}")
    print("Response:")
    print(json.dumps(response.json(), indent=2))
except Exception as e:
    print(f"Error: {e}")
