import requests
import sys

try:
    print("Sending request...")
    r = requests.post("http://localhost:8000/api/chat", json={"message": "Describe PMJAY in 10 words", "history": []})
    print(f"Status: {r.status_code}")
    print(f"Response: {r.text}")
except Exception as e:
    print(f"Error: {e}")
