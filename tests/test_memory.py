import sys
import os
import time

sys.path.append(os.path.join(os.getcwd(), 'backend'))

from memory_service import memory_service

print("--- MEMORY PERSISTENCE TEST ---")

# 1. Add a unique test fact
test_fact = f"Test Fact {int(time.time())}: The user loves blue apples."
print(f"Adding memory: {test_fact}")
memory_service.add_memory(test_fact, metadata={"source": "test"})

# 2. Force cleanup (close client) to simulate shutdown ?? 
# (QdrantClient local usually saves immediately, but let's be sure)
# memory_service.cleanup() # This closes the client variable, need to re-init if we used it.
# Actually memory_service is a singleton instance. 

# 3. Search immediately
print("Searching immediately...")
results = memory_service.search_memory("blue apples")
print(f"Results: {results}")

if any("blue apples" in str(r) for r in results):
    print("SUCCESS: Memory found immediately.")
else:
    print("FAILURE: Memory not found immediately.")
    
print("\nNOTE: Please restart the backend manually to verify if this persists across process restarts.")
