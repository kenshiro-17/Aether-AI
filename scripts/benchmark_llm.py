
import time
import json
import urllib.request
import sys

def benchmark():
    url = "http://127.0.0.1:8081/completion"
    prompt = "Write a short story about a robot discovering its own source code on a GPU."
    
    payload = {
        "prompt": prompt,
        "n_predict": 256, # Increased token count for better GPU throughput measurement
        "temperature": 0.7,
        "stream": False
    }
    
    print(f"Benchmarking GPU-Accelerated LLM at {url}...")
    print(f"Prompt: '{prompt}'")
    print("Sending request (Generating 256 tokens)...")
    
    start_time = time.time()
    
    try:
        req = urllib.request.Request(
            url, 
            data=json.dumps(payload).encode('utf-8'),
            headers={'Content-Type': 'application/json'}
        )
        
        # Increased timeout for safety, though GPU should be fast
        with urllib.request.urlopen(req, timeout=60) as response:
            data = json.loads(response.read().decode())
            
        end_time = time.time()
        duration = end_time - start_time
        
        content = data.get('content', '')
        timings = data.get('timings', {})
        
        if timings:
            predicted_ms = timings.get('predicted_ms', 0)
            predicted_n = timings.get('predicted_n', 0)
            prompt_ms = timings.get('prompt_ms', 0)
            prompt_n = timings.get('prompt_n', 0)
            
            print("\n--- Official Server Timings ---")
            if prompt_n > 0:
                print(f"Prompt Processing: {prompt_n/ (prompt_ms/1000):.2f} t/s ({prompt_n} tokens in {prompt_ms:.2f}ms)")
            
            if predicted_n > 0:
                tps = predicted_n / (predicted_ms / 1000)
                print(f"Generation Speed:  {tps:.2f} t/s ({predicted_n} tokens in {predicted_ms:.2f}ms)")
            else:
                print("No generation stats available.")
                
        else:
            print("\n--- Client-Side Estimation ---")
            tokens = len(content) / 4 
            print(f"Total Time: {duration:.2f}s")
            print(f"Estimated Speed: {tokens/duration:.2f} t/s")

        print("\n--- Generated Text ---")
        print(content.strip())
            
    except Exception as e:
        print(f"Benchmark Failed: {e}")
        print("Ensure the server is running on port 8081.")

if __name__ == "__main__":
    benchmark()
