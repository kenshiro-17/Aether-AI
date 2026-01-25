from openai import OpenAI
import time
import sys

# Configure OpenAI Client
client = OpenAI(
    base_url="http://localhost:8081/v1",
    api_key="ollama"
)

print(f"Testing connection to http://localhost:8081/v1...")

try:
    start = time.time()
    response = client.chat.completions.create(
        model="DeepSeek R1 Distill Qwen 32B",
        messages=[{"role": "user", "content": "Hello, are you online? Reply with 'Yes'."}],
        max_tokens=10,
        temperature=0.7
    )
    end = time.time()
    print(f"Success! Response: {response.choices[0].message.content}")
    print(f"Time taken: {end - start:.2f}s")
except Exception as e:
    print(f"FAILED. Error: {e}")
    import traceback
    traceback.print_exc()
