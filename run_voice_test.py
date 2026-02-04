import base64
import requests
import json
import subprocess
import time
import sys
import os
import signal

def wait_for_server(url, retries=20, delay=1):
    for i in range(retries):
        try:
            requests.get(url) 
            return True
        except requests.ConnectionError:
            time.sleep(delay)
    return False

def main():
    # 1. Start the server
    print("Starting server...")
    # Using python -m uvicorn instead of exe directly to ensure path correctness
    server_process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8013"],
        cwd=os.getcwd(),
        # stdout=subprocess.PIPE,
        # stderr=subprocess.PIPE
    ) # Using port 8013

    try:
        # 2. Wait for server to be ready
        base_url = "http://127.0.0.1:8013"
        print("Waiting for server to be ready...")
        if not wait_for_server(f"{base_url}/health"):
             print("Server failed to start.")
             return

        # 3. Prepare data
        dummy_data = b'\xFF\xFB\x90\xC4\x00\x00' * 100 
        base64_audio = base64.b64encode(dummy_data).decode('utf-8')

        url = f"{base_url}/detect-voice"
        headers = {"x-api-key": "test-api-key-12345"}
        payload = {
            "language": "en",
            "audioFormat": "mp3",
            "audioBase64": base64_audio
        }

        # 4. Send Request
        print(f"Sending request to {url}...")
        response = requests.post(url, json=payload, headers=headers)
        
        # 5. Output Result
        print(f"Status Code: {response.status_code}")
        print("Response Body:")
        print(json.dumps(response.json(), indent=2))

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # 6. Cleanup
        print("Stopping server...")
        server_process.terminate()
        server_process.wait()

if __name__ == "__main__":
    main()
