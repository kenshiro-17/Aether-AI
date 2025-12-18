
import requests
import sys

def test_stream():
    url = "http://127.0.0.1:8000/v1/learn/stream?topic=Python"
    print(f"Connecting to Manual Learning Stream: {url}")
    
    try:
        with requests.get(url, stream=True, timeout=60) as response:
            if response.status_code == 200:
                print("Connected! Listening for events...")
                for line in response.iter_lines():
                    if line:
                        decoded_line = line.decode('utf-8')
                        print(f"Received: {decoded_line}")
                        if "DONE" in decoded_line:
                            print("Stream finished.")
                            break
            else:
                print(f"Failed to connect: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Stream Error: {e}")

if __name__ == "__main__":
    test_stream()
