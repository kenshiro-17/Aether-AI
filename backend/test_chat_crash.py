import requests
import json
import sys

def test_crash():
    url = "http://localhost:8000/v1/chat/completions"
    payload = {
        "messages": [{"role": "user", "content": "What is the stock price of Apple?"}],
        "enable_search": True
    }
    
    print(f"Sending request to {url}...")
    try:
        with requests.post(url, json=payload, stream=True) as r:
            print(f"Status Code: {r.status_code}")
            if r.status_code != 200:
                print(f"Error: {r.text}")
                return

            print("--- Stream Start ---")
            for line in r.iter_lines():
                if line:
                    print(line.decode('utf-8'))
            print("--- Stream End ---")
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    test_crash()
