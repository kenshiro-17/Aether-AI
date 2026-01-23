import requests
import sys
import time

# Configuration
API_URL = "http://localhost:8000"
SEARCH_TOPICS = [
    "Modern Python coding best practices 2025",
    "Advanced AI agent architecture patterns",
    "React TypeScript best practices for performance",
    "FastAPI production security guide"
]

def search_and_learn(topic):
    print(f"\n[LEADER] Researching topic: {topic}")
    
    # 1. Search (using our internal tool logic, but via a quick search API or just assuming we have a list)
    # Since we can't easily import the internal tools without env setup, let's use the API if we had a search endpoint, 
    # but we don't have a public search-and-list endpoint, only 'web_search' tool.
    # We will simulate this by asking the AI to search, or just hardcoding some high-value URLs for this demo.
    
    # Actually, let's use the `ingestion_service` if we can import it, OR just use DuckDuckGo here directly.
    try:
        from duckduckgo_search import DDGS
        results = list(DDGS().text(topic, max_results=3))
        
        for r in results:
            url = r['href']
            title = r['title']
            print(f"  > Found: {title}")
            print(f"    URL: {url}")
            
            # 2. Ingest
            try:
                res = requests.post(f"{API_URL}/ingest/url", json={"url": url}, timeout=30)
                if res.status_code == 200:
                    print(f"    [SUCCESS] Learned.")
                else:
                    print(f"    [FAILED] {res.status_code} - {res.text}")
            except Exception as e:
                print(f"    [ERROR] Could not ingest: {e}")
                
            time.sleep(1) # Be polite
            
    except ImportError:
        print("DuckDuckGo Search library not found. Please install `duckduckgo-search` or add URLs manually.")

def main():
    print("Initializing Autonomous Learning Session...")
    
    # Verify Backend is Reachable
    try:
        requests.get(f"{API_URL}/")
    except:
        print("ERROR: Personal AI Backend is NOT running. Please run `run_backend.bat` first.")
        return

    for topic in SEARCH_TOPICS:
        search_and_learn(topic)

if __name__ == "__main__":
    main()
