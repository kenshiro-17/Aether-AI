
import urllib.request
import json
import socket

def check_llm():
    url = "http://127.0.0.1:8081/v1/models"
    print(f"Checking LLM Server at {url}...")
    
    # 1. Check TCP Port first
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex(('127.0.0.1', 8081))
        if result == 0:
            print("Port 8081 is OPEN (Socket Connected).")
        else:
            print(f"Port 8081 is CLOSED (Error {result}). Server not running?")
            return False
        sock.close()
    except Exception as e:
        print(f"Socket Check Failed: {e}")
        
    # 2. Check HTTP Response
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=5) as response:
            if response.status == 200:
                data = json.loads(response.read().decode())
                print("SUCCESS: HTTP Connection established.")
                print(f"Models: {len(data.get('data', []))} available.")
                return True
            else:
                print(f"HTTP ERROR: {response.status}")
                return False
    except urllib.error.URLError as e:
        print(f"HTTP Connection Failed: {e}")
        return False
    except Exception as e:
        print(f"General Error: {e}")
        return False

if __name__ == "__main__":
    check_llm()
