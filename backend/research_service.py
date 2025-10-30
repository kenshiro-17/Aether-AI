"""
Autonomous Research Service
Implements a "Curiosity Loop" that periodically researches topics on the web
and expands the AI's knowledge base.
"""
import threading
import time
import random
import datetime
import json
from typing import List, Dict
from openai import OpenAI

import re
# Internal Services
from ingestion_service import ingestion_service
from memory_service import memory_service
from cortex import web_search

# Configure OpenAI Client
client = OpenAI(
    base_url="http://localhost:8081/v1",
    api_key="ollama"
)

class ResearchService:
    def __init__(self):
        self.is_running = False
        self.interval_seconds = 3600  # Default: Research every hour
        self.research_thread = None
        self.curiosity_enabled = True # Default to True
        
    def start_background_loop(self):
        """Start the background research thread."""
        if self.research_thread and self.research_thread.is_alive():
            return # Already running
            
        self.is_running = True
        self.research_thread = threading.Thread(target=self._research_loop, daemon=True)
        self.research_thread.start()
        print("[RESEARCH] Background service started.")

    def _wait_for_model(self):
        """Block until the LLM server is responding."""
        print("[RESEARCH] Waiting for Brain to come online...")
        retries = 0
        while self.is_running:
            try:
                # simple health check
                client.models.list()
                print("[RESEARCH] Brain is ONLINE. Starting Curiosity.")
                return True
            except:
                time.sleep(5)
                retries += 1
                if retries % 6 == 0: print("[RESEARCH] Still waiting for Brain...")
        return False

    def stop(self):
        """Stop the background loop."""
        self.is_running = False
        print("[RESEARCH] Background service stopping...")

    def _research_loop(self):
        """Main loop that runs in the background."""
        if not self._wait_for_model():
            return

        print("[RESEARCH] Curiosity Loop Initialized.")
        
        while self.is_running:
            failure = False # Initialize failure flag for the current cycle
            if self.curiosity_enabled:
                try:
                    self.perform_research_cycle()
                    failure = False
                except Exception as e:
                    print(f"[RESEARCH ERROR] Cycle failed: {e}")
                    failure = True
            
            # Smart Sleep Logic
            if failure:
                wait_time = 60 # Retry fast on error
                print(f"[RESEARCH] Cycle failed. Retrying in {wait_time} seconds...")
            else:
                # Normal sleep (1 hour +/- 10 mins)
                wait_time = self.interval_seconds + random.randint(-600, 600)
                if wait_time < 300: wait_time = 3600 # Enforce minimum 1 hour if not failure
                print(f"[RESEARCH] Cycle complete. Sleeping for {wait_time/60:.1f} minutes...")
            
            time.sleep(wait_time)

    def perform_research_cycle(self):
        """Execute one full research cycle - DEEP MODE: 3 topics, multiple sources each."""
        print("\n=== [RESEARCH] STARTING DEEP CURIOSITY CYCLE ===")
        
        topics_to_research = 3  # Research 3 different topics per cycle
        sources_per_topic = 2   # Read 2 sources per topic
        total_learned = 0
        
        for i in range(topics_to_research):
            print(f"\n--- [RESEARCH] Topic {i+1}/{topics_to_research} ---")
            
            # 1. Generate Topic
            topic = self._generate_curiosity_topic()
            if not topic:
                print("[RESEARCH] No topic generated. Skipping.")
                continue

            print(f"[RESEARCH] Decided to learn about: '{topic}'")
            
            # 2. Search Web
            try:
                print(f"[RESEARCH] Searching web for '{topic}'...")
                search_results_str = web_search(topic)
                
                # 3. Get multiple URLs from search results
                urls = self._extract_multiple_urls(topic, search_results_str, limit=sources_per_topic)
                
                if not urls:
                    print("[RESEARCH] No suitable URLs found.")
                    continue
                
                # 4. Read each source
                for j, url in enumerate(urls):
                    print(f"[RESEARCH] Source {j+1}/{len(urls)}: {url}")
                    success = self._ingest_and_learn(url, topic)
                    if success:
                        total_learned += 1
                    time.sleep(2)  # Be polite to servers
                    
            except Exception as e:
                print(f"[RESEARCH] Search failed for '{topic}': {e}")
                continue
            
            time.sleep(3)  # Pause between topics
        
        print(f"\n=== [RESEARCH] CYCLE COMPLETE: Learned {total_learned} new facts ===\n")

    def _generate_curiosity_topic(self) -> str:
        """Ask LLM what it wants to learn about."""
        try:
            # Get recent context from memory to see what user is interested in? 
            # Or just purely random/general knowledge.
            # Let's verify what the user likes.
            
            prompt = """
            You are an autonomous AI with curiosity.
            Based on your internal goal to be a "Helpful, Intelligent Assistant", 
            generate ONE specific topic you would like to research right now to expand your knowledge.
            
            Criteria:
            - Relevant to technology, science, coding, or productivity (User's broad interests).
            - Specific enough to be searchable (e.g. "Latest features in React 19" instead of "React").
            - NOT something you already know basics of.
            
            Return ONLY the topic as a string. No quotes.
            """
            
            response = client.chat.completions.create(
                model="Mistral-Nemo-Instruct-2407", 
                messages=[{"role": "user", "content": prompt}],
                max_tokens=50,
                temperature=0.8
            )
            
            # Robust Checking
            if not response or not hasattr(response, 'choices') or not response.choices:
                return None
                
            content = response.choices[0].message.content.strip().strip('"')
            # Fallback: if model is chatty, take last line or regex
            if "\n" in content:
                content = content.splitlines()[-1] 
            return content
        except Exception as e:
            print(f"[RESEARCH] Topic generation failed: {e}")
            return None

    def _extract_multiple_urls(self, topic: str, search_results: str, limit: int = 2) -> list:
        """Extract multiple URLs from search results for deeper research."""
        try:
            # First try direct regex extraction (faster, no LLM call needed)
            urls = re.findall(r'(https?://[^\s\)]+)', search_results)
            
            # Filter out bad URLs
            good_urls = []
            bad_patterns = ['google.com/search', 'bing.com/search', 'duckduckgo.com', 'facebook.com', 'twitter.com', 'x.com']
            
            for url in urls:
                url = url.strip('.,)"\'')
                if any(bad in url for bad in bad_patterns):
                    continue
                if url not in good_urls:
                    good_urls.append(url)
                if len(good_urls) >= limit:
                    break
            
            if good_urls:
                return good_urls[:limit]
            
            # Fallback: Use LLM to extract URLs
            prompt = f"""
            Search results for: "{topic}"
            {search_results}
            
            List the {limit} best URLs to read for learning about this topic.
            Prefer documentation, encyclopedias, or reputable sites.
            Return ONLY the URLs, one per line.
            """
            
            response = client.chat.completions.create(
                model="Mistral-Nemo-Instruct-2407",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300,
                temperature=0.1
            )
            text = response.choices[0].message.content.strip()
            urls = re.findall(r'(https?://\S+)', text)
            return [u.strip(')"\',') for u in urls[:limit]]
        except Exception as e:
            print(f"[RESEARCH] URL extraction failed: {e}")
            return []

    def _ingest_and_learn(self, url: str, topic: str) -> bool:
        """Ingest the URL and verify facts. Returns True if successful."""
        try:
            print(f"[RESEARCH] Reading {url}...")
            content = ingestion_service.parse_url(url)
            
            if not content:
                print("[RESEARCH] Failed to extract content.")
                return False

            # Verification / Summarization Step (Deep Reasoning)
            print("[RESEARCH] Verifying and condensing knowledge...")
            verified_content = self._verify_knowledge(topic, content)
            
            if verified_content:
                # Store
                memory_service.add_memory(verified_content, metadata={
                    "type": "research_knowledge",
                    "topic": topic,
                    "source": url,
                    "verified": True,
                    "timestamp": datetime.datetime.now().isoformat()
                })
                print(f"[RESEARCH] SUCCESS. Stored knowledge about '{topic}'.")
                return True
            else:
                print("[RESEARCH] Content deemed not useful by verification.")
                return False
                
        except Exception as e:
            print(f"[RESEARCH] Ingestion failed: {e}")
            return False

    def _verify_knowledge(self, topic: str, content: str) -> str:
        """Use DeepSeek R1 to summarize and extract facts."""
        try:
            prompt = f"""
            Analyze the following scraped text about "{topic}".
            
            Task:
            1. Extract the key FACTS and technical details.
            2. Verify they seem logical (discard marketing fluff or obvious spam).
            3. Condense into a clear, informative summary for your long-term memory.
            
            Text:
            {content[:10000]} # Limit context
            
            Output ONLY the condensed, verified knowledge.
            """
            
            response = client.chat.completions.create(
                model="Mistral-Nemo-Instruct-2407",
                messages=[
                    {"role": "system", "content": "You are a Fact Verification Engine."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.3
            )
            
            # Robust Response Handling
            if not response:
                print("[RESEARCH ERROR] Verification failed: Empty response from brain.")
                return None
                
            if hasattr(response, 'choices') and response.choices:
                text = response.choices[0].message.content.strip()
            # Handle dict-like response just in case
            elif isinstance(response, dict) and 'choices' in response and response['choices']:
                text = response['choices'][0]['message']['content'].strip()
            else:
                print(f"[RESEARCH ERROR] Verification failed: Invalid response structure: {response}")
                return None
                
            # Filter out hallucinations/bad tokens
            if "<|im_end|>" in text:
                text = text.replace("<|im_end|>", "").strip()
            if not text:
                return None
                
            return text
            
        except Exception as e:
            print(f"[RESEARCH] Verification failed: {e}")
            return None

# Global Instance
research_service = ResearchService()
