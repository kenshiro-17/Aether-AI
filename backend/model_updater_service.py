"""
Model Updater Service
Periodically checks for new "Flagship" LLM releases and suggests upgrades.
"""
import threading
import time
import datetime
import random
from openai import OpenAI
from cortex import web_search

# Configuration
client = OpenAI(
    base_url="http://localhost:8081/v1",
    api_key="ollama"
)

CURRENT_MODEL_NAME = "DeepSeek R1 Distill Qwen 32B"

class ModelUpdaterService:
    def __init__(self):
        self.is_running = False
        self.check_interval_seconds = 30 * 24 * 3600  # Check once every 30 days
        self.updater_thread = None
        self.last_check_date = None

    def start_background_loop(self):
        """Start the background checking thread."""
        if self.updater_thread and self.updater_thread.is_alive():
            return
            
        self.is_running = True
        self.updater_thread = threading.Thread(target=self._update_loop, daemon=True)
        self.updater_thread.start()
        print("[UPDATER] Model Update Scout started.")

    def stop(self):
        self.is_running = False

    def _update_loop(self):
        print("[UPDATER] Waiting for next scheduled check...")
        
        # Initial check delay (don't check immediately on boot to save resources)
        time.sleep(60) 
        
        while self.is_running:
            try:
                self.check_for_updates()
            except Exception as e:
                print(f"[UPDATER ERROR] Check failed: {e}")
            
            # Sleep for 30 days
            time.sleep(self.check_interval_seconds)

    def check_for_updates(self):
        """Perform a web search for new state-of-the-art models."""
        print("\n=== [UPDATER] Checking for new AI Models ===")
        current_year = datetime.datetime.now().year
        current_month = datetime.datetime.now().strftime("%B")
        
        query = f"Best open source LLM model release {current_month} {current_year} benchmarks vs DeepSeek R1"
        print(f"[UPDATER] Searching: {query}...")
        
        try:
            results = web_search(query)
            
            # Use LLM to analyze search results
            prompt = f"""
            You are an AI Model Scout.
            Current Model: {CURRENT_MODEL_NAME}
            
            Search Results for New Models:
            {results[:5000]}
            
            Task:
            1. Identify if a NEW model has been released that is significantly BETTER than {CURRENT_MODEL_NAME}.
            2. Ignore models that are too large (>32GB VRAM) or closed source (GPT-5, Claude).
            3. Prioritize Llama 4, Gemma 3, and Mistral Large.
            4. Verify the release date is 2024, 2025 or 2026.
            
            If a better model exists, return a short JSON:
            {{
                "upgrade_available": true,
                "model_name": "Name of new model",
                "reason": "Why it is better (benchmarks)"
            }}
            
            If no better model found, return:
            {{ "upgrade_available": false }}
            """
            
            response = client.chat.completions.create(
                model="DeepSeek R1 Distill Qwen 32B",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            
            import json
            analysis = json.loads(response.choices[0].message.content)
            
            if analysis.get("upgrade_available"):
                new_model = analysis.get("model_name")
                reason = analysis.get("reason")
                print(f"[UPDATER] 🌟 UPGRADE FOUND: {new_model}")
                print(f"[UPDATER] Reason: {reason}")
                # In a GUI app, we would send a notification here.
                # For now, we log it to a file or special memory location.
                with open("UPGRADE_AVAILABLE.txt", "w") as f:
                    f.write(f"New Model Available: {new_model}\n{reason}")
            else:
                print("[UPDATER] No significantly better models found yet.")
                
        except Exception as e:
            error_msg = str(e)
            if "Connection error" in error_msg or "Connection refused" in error_msg or "503" in error_msg:
                print(f"[UPDATER ERROR] 🛑 Could not connect to Main Brain (Port 8081).")
                print(f"[UPDATER ERROR] Please ensure 'start_system.bat' (and start_llm.bat) is running.")
            else:
                print(f"[UPDATER] Update check failed: {e}")

# Global Instance
model_updater_service = ModelUpdaterService()
