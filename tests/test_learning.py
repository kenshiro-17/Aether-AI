
import requests
import asyncio
import json
import sys

# Test the detailed research flow
def test_learning():
    print("Triggering Active Research on 'Quantum Computing'...")
    try:
        # Start the process
        # We need to find the correct endpoint name. 
        # Based on previous context, it should be POST /v1/learn/mastery/start or similar.
        # Let's try /v1/learn/auto which was mentioned in the code or previous tasks.
        # Actually, looking at learning_service.py, `active_research_auto` is the method.
        # The router likely exposes this.
        # Let's assume there is a POST endpoint. I will guess /v1/learn/start or /v1/learn/auto.
        
        # Checking routers/learning.py (I can't see it but I can infer).
        # I'll try to hit the auto endpoint.
        url = "http://127.0.0.1:8000/v1/learn/auto" 
        resp = requests.post(url, json={"mode": "auto"})
        print(f"Start Response: {resp.status_code} - {resp.text}")
        
    except Exception as e:
        print(f"Failed to start: {e}")

if __name__ == "__main__":
    test_learning()
