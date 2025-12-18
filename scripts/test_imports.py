import sys
import os

# Add backend to path (simulating running from backend dir)
sys.path.append(os.path.join(os.getcwd(), 'backend'))

try:
    from cortex import web_search, read_url
    print("SUCCESS: Imported web_search and read_url from cortex")
except ImportError as e:
    print(f"FAILURE: {e}")
except Exception as e:
    print(f"FAILURE: {e}")
