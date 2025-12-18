
import sys
import os

# quick hack to add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

try:
    from cortex import web_search
    print("Importing web_search successful.")
    
    print("Running search...")
    results = web_search("Rust Programming Language")
    print(f"Search Results Length: {len(results)}")
    print("Search successful.")
except Exception as e:
    print(f"Search traceback: {e}")
    import traceback
    traceback.print_exc()
