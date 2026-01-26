import requests
import json

try:
    print("Testing /api/chat on port 8005...")
    response = requests.post(
        "http://127.0.0.1:8005/api/chat",
        json={"message": "Hello", "history": []},
        headers={"Content-Type": "application/json"}
    )
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
