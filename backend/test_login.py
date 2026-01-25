import requests

API_URL = "http://localhost:8000/token"

def test_login():
    print("Testing Login Endpoint with different formats...")
    
    # 1. Test Multipart (FormData) - What Frontend currently uses
    print("\n1. Testing Multipart/Form-Data...")
    try:
        # requests.post(files=...) sends multipart
        resp = requests.post(API_URL, files={
            'username': (None, 'debug_user_v2'),
            'password': (None, 'password123')
        })
        print(f"Status: {resp.status_code}")
        print(f"Response: {resp.text}")
    except Exception as e:
        print(f"Error: {e}")

    # 2. Test URL Encoded (Standard OAuth2)
    print("\n2. Testing x-www-form-urlencoded...")
    try:
        # requests.post(data=...) sends urlencoded
        resp = requests.post(API_URL, data={
            'username': 'debug_user_v2',
            'password': 'password123'
        })
        print(f"Status: {resp.status_code}")
        print(f"Response: {resp.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_login()
