from memory_service import memory_service
import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.append(PROJECT_ROOT)

def test_search():
    print("Testing memory search...")
    # Search for something unique to the skills we just added
    results = memory_service.search_memory("voice ai development", limit=3)
    
    if results:
        print(f"Found {len(results)} results:")
        for r in results:
            print("-" * 20)
            print(f"Content: {r.get('content', '')[:100]}...")
            print(f"Metadata: {r.get('skill_name', 'N/A')}")
    else:
        print("No results found.")

if __name__ == "__main__":
    test_search()
