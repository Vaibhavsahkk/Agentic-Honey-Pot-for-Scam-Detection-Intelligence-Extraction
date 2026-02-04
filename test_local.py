import subprocess
import time
import requests
import sys
import os

# Start server
print("Starting server...")
server = subprocess.Popen(
    [r"d:\HACKATHON\venv\Scripts\uvicorn.exe", "app.main:app", "--host", "127.0.0.1", "--port", "8030"],
    cwd=r"d:\HACKATHON"
)

time.sleep(3)

# Test
print("Testing /detect endpoint...")
try:
    r = requests.post(
        "http://127.0.0.1:8030/detect",
        json={},
        headers={"x-api-key": "test-api-key-12345"}
    )
    print(f"Status: {r.status_code}")
    print(f"Response: {r.json()}")
except Exception as e:
    print(f"Error: {e}")

# Cleanup
print("Stopping server...")
server.terminate()
server.wait()
print("Done")
