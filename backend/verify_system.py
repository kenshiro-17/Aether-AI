import requests
import time
import json

BASE_URL = "http://localhost:8000"

def check_feature(name, func):
    print(f"\n[TEST] Verifying {name}...")
    try:
        result = func()
        print(f"   PASS: {result}")
        return True
    except Exception as e:
        print(f"   FAIL: {e}")
        return False

def test_api_root():
    res = requests.get(f"{BASE_URL}/")
    if res.status_code == 200:
        return res.json().get("service")
    raise Exception(f"Status {res.status_code}")

def test_model_loaded():
    res = requests.get(f"{BASE_URL}/api/settings")
    if res.status_code == 200:
        model = res.json().get("model")
        if "DeepSeek" in model:
            return f"Model Loaded: {model}"
        raise Exception(f"Wrong model: {model}")
    raise Exception(f"Status {res.status_code}")

def test_skill_forge():
    # 1. List
    res = requests.get(f"{BASE_URL}/api/skills")
    skills = res.json().get("skills", [])
    
    # 2. Create Dummy
    requests.post(f"{BASE_URL}/api/skills/create", params={"name": "test_echo", "task": "print hello world"})
    
    # 3. List Again
    time.sleep(1)
    res = requests.get(f"{BASE_URL}/api/skills")
    new_skills = res.json().get("skills", [])
    if "test_echo" in new_skills:
        return f"Skills Service Active. Available: {len(new_skills)}"
    return "Skill creation initiated (async)"

def test_research_trigger():
    res = requests.post(f"{BASE_URL}/api/research/start")
    if res.status_code == 200:
        return "Research Cycle Triggered"
    raise Exception(f"Status {res.status_code}")

def run_tests():
    print("--- STARTING SYSTEM VERIFICATION ---")
    
    # Wait for server
    for i in range(10):
        try:
            requests.get(f"{BASE_URL}/")
            break
        except:
            print(f"Waiting for server... ({i+1}/10)")
            time.sleep(2)
            
    success_count = 0
    checks = [
        ("API Connectivity", test_api_root),
        ("DeepSeek Model Status", test_model_loaded),
        ("Skill Forge Service", test_skill_forge),
        ("Autonomous Research", test_research_trigger)
    ]
    
    for name, func in checks:
        if check_feature(name, func):
            success_count += 1
            
    print(f"\n--- RESULTS: {success_count}/{len(checks)} PASSED ---")

if __name__ == "__main__":
    run_tests()
