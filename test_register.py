import requests
import json

url = "http://127.0.0.1:8000/api/auth/register"
payload = {
    "username": "debug_user_1",
    "password": "password123",
    "email": "debug@test.com",
    "full_name": "Debug User"
}
headers = {
    "Content-Type": "application/json"
}

try:
    print(f"Sending POST to {url}...")
    response = requests.post(url, json=payload, headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Request failed: {e}")
