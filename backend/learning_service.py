"""
Self-Learning Service for Personal AI
Automatically extracts and stores knowledge from conversations using LLM analysis.
"""

import re
import datetime
import json
from typing import List, Dict, Optional

from openai import AsyncOpenAI
from memory_service import memory_service


class LearningService:
    """
    Extracts knowledge from conversations and stores it for future reference.
    The AI learns from every interaction automatically using a dedicated LLM call.
    """
    
    def _get_client(self):
        return AsyncOpenAI(
            base_url="http://127.0.0.1:8081/v1",
            api_key="ollama",
            timeout=300.0
        )

    def __init__(self):
        self.learning_enabled = True
        self.min_content_length = 5
        self.learned_count = 0
        self.curriculum_index = 0
        self.dynamic_queue = []
        self.learned_topics = set()
        
        # Self-Improvement Curriculum (Prioritized Coding & Architecture)
        self.curriculum = [
            # 1. CORE ARCHITECTURE & SYSTEM DESIGN
            "Python Memory Management Optimization for AI Systems",
            "FastAPI Performance Tuning for High Concurrency",
            "Effective RAG Strategies for Long-Context LLMs",
            "Event-Driven Architecture Patterns in Python",
            "Microservices vs Monoliths for AI Backends",
            "Database Sharding and Partitioning Strategies",
            
            # 2. MACHINE LEARNING & AI OPTIMIZATION
            "Quantization Techniques for LLMs (GGUF, GPTQ, AWQ)",
            "Mechanistic Interpretability in Transformers",
            "Chain of Thought Reasoning Improvements",
            "Parameter Efficient Fine-Tuning (PEFT) and LoRA",
            "Optimizing Vector Search with HNSW",
            "Agentic AI Patterns (ReAct, Plan-and-Solve)",
            
            # 3. MODERN WEB DEVELOPMENT (REACT/TS)
            "React 19 Server Components and Suspense Architecture",
            "Advanced TypeScript Generic Patterns",
            "WebAssembly for Client-Side AI Inference",
            "Modern CSS Layouts: Subgrid and Container Queries",
            "WebSockets vs Server-Sent Events for Realtime Apps",
            "Progressive Web App (PWA) Offline Capabilities",
            "State Management Patterns: Zustand vs Redux Toolkit",
            
            # 4. DEVOPS & INFRASTRUCTURE
            "Docker Multi-Stage Builds for Python AI Apps",
            "Kubernetes Scaling Strategies for Inference Services",
            "CI/CD Pipelines for Machine Learning Models",
            
            # 5. CORE PROGRAMMING & ALGORITHMS
            "Data Structures: Trees, Graphs, and Hash Maps",
            "Algorithm Design: Dynamic Programming Techniques",
            "Big O Notation and Time Complexity Analysis",
            "Recursion vs Iteration: When to Use Each",
            "Sorting Algorithms: QuickSort, MergeSort, HeapSort",
            "Graph Algorithms: BFS, DFS, Dijkstra, A*",
            
            # 6. LANGUAGE-SPECIFIC MASTERY
            "Python Advanced: Decorators, Metaclasses, Generators",
            "Python Asyncio: Concurrent Programming Patterns",
            "JavaScript ES2024: New Features and Best Practices",
            "TypeScript 5.x: Advanced Type System Patterns",
            "Rust for Python Developers: Memory Safety Concepts",
            "Go Concurrency: Goroutines and Channels",
            
            # 7. SOFTWARE ENGINEERING BEST PRACTICES
            "SOLID Principles in Practice",
            "Clean Code: Naming, Functions, and Comments",
            "Design Patterns: Factory, Singleton, Observer, Strategy",
            "Test-Driven Development (TDD) with Python",
            "Code Review Best Practices",
            "Refactoring: Improving Existing Code Safety",
            
            # 8. DATABASE & DATA ENGINEERING
            "SQL Query Optimization and Indexing",
            "NoSQL Design Patterns: MongoDB, Redis, Cassandra",
            "PostgreSQL Advanced Features: CTEs, Window Functions",
            "Data Pipelines with Apache Airflow",
            "Real-time Data Processing with Apache Kafka",
            
            # 9. STUDENT LIFE & STUDY TECHNIQUES
            "Evidence-Based Study Techniques: Spaced Repetition, Active Recall",
            "Note-Taking Systems: Cornell Method, Zettelkasten",
            "Speed Reading and Comprehension Improvement",
            "Time Management for Students: Pomodoro, Time Blocking",
            "Exam Preparation Strategies for Technical Subjects",
            "Academic Writing: Research Papers and Citations",
            
            # 10. CAREER DEVELOPMENT
            "Resume Writing for Software Engineers",
            "Technical Interview Preparation: Coding Challenges",
            "Behavioral Interview Questions: STAR Method",
            "LinkedIn Optimization for Job Seekers",
            "Building a Portfolio: GitHub and Personal Projects",
            "Salary Negotiation Strategies",
            "Networking Skills for Introverts",
            
            # 11. PERSONAL FINANCE & LIFE SKILLS
            "Budgeting for Students: 50/30/20 Rule",
            "Introduction to Investing: Stocks, ETFs, Index Funds",
            "Understanding Taxes for Freelancers",
            "Building Credit Score and Financial Health",
            "Meal Planning and Healthy Eating on a Budget",
            
            # 12. HEALTH & PRODUCTIVITY
            "Sleep Optimization for Peak Performance",
            "Managing Stress and Avoiding Burnout",
            "Exercise Routines for Desk Workers",
            "Mindfulness and Meditation for Focus",
            "Building Consistent Habits: Atomic Habits Principles",
        ]
        
    async def learn_from_conversation(self, user_query: str, ai_response: str):
        """
        Background Task: Analyze conversation turn for new knowledge.
        """
        if not self.learning_enabled:
            return

        # Simple heuristic: Only learn if there's substantial content
        if len(user_query) < 5: # Reduced from 10 to capture short commands
            return

        try:
            # Combine relevant context
            conversation_text = f"User: {user_query}\nAI: {ai_response}"
            
            # Extract facts
            knowledge = await self.extract_knowledge(conversation_text)
            
            if knowledge:
                print(f"[LEARNING] Learned: {knowledge[:50]}...")
                # Store in Memory
                memory_service.add_memory(knowledge, metadata={
                    "type": "conversation_fact",
                    "source": "chat",
                    "timestamp": datetime.datetime.now().isoformat()
                })
                self.learned_count += 1
                
        except Exception as e:
            print(f"[LEARNING] Error during learning: {e}")

    async def extract_knowledge(self, text: str) -> Optional[str]:
        """
        Ask LLM to extract highly relevant, long-term facts from the text.
        """
        prompt = f"""
        Analyze the following conversation snippet.
        Extract any NEW, PERMANENT facts about the User, the Project, or the World that should be remembered long-term.
        
        Rules:
        1. Capture explicit USER INSTRUCTIONS or PREFERENCES (e.g. "Use EST timezone", "My name is X", "Don't use emojis").
        2. Focus on: Project requirements, Technical decisions, Personal details.
        3. Ignore generic greetings.
        4. Output the extracted fact as a single concise statement.
        5. If nothing worth learning is found, return "NO_FACTS".
        
        Conversation:
        {text}
        
        Fact:
        """
        
        try:
            client = self._get_client()
            response = await client.chat.completions.create(
                model="Mistral-Nemo-Instruct-2407",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=200
            )
            
            # Robust Check
            if not response or not hasattr(response, 'choices') or not response.choices:
                return None
                
            fact = response.choices[0].message.content.strip()
            
            # Filter output
            if "NO_FACTS" in fact or len(fact) < 5:
                return None
            
            # Reject if it looks like a generic refusal or hallucination
            if "<|im_end|>" in fact: 
                fact = fact.replace("<|im_end|>", "").strip()
                
            return fact
            
        except Exception as e:
            print(f"[LEARNING] Extraction failed: {e}")
            return None

    async def generate_curriculum(self, subject: str) -> list:
        """
        Generates a structured learning path (Curriculum) for a subject.
        Returns a list of sub-topics.
        """
        prompt = f"""
        Act as a Professor.
        Create a comprehensive curriculum to MASTER the subject: "{subject}".
        Break it down into 5-10 specific, searchable sub-topics, ordered from beginner to advanced.
        
        RETURN ONLY A VALID JSON LIST OF STRINGS. NO PREAMBLE. NO MARKDOWN.
        
        Example Output:
        ["Python Variables", "Python Loops", "Python Classes", "Python AsyncIO"]
        """
        
        try:
            # Use internal client
            client = self._get_client()
            response = await client.chat.completions.create(
                model="Llama-3.2-3B-Instruct",
                messages=[
                    {"role": "system", "content": "You are a curriculum generator. output valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=600,
                temperature=0.3
            )
            content = response.choices[0].message.content.strip()
            # Extract JSON list
            import re
            json_match = re.search(r'\[.*\]', content, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group(0))
                except:
                    pass
            
            # Fallback: Try splitting lines if it looks like a list
            if "[" not in content:
                lines = [l.strip("- *").strip() for l in content.split('\n') if l.strip()]
                return lines[:10]
                
            return []
        except Exception as e:
            print(f"[LEARNING] Curriculum generation error: {e}")
            return [f"{subject} Fundamentals", f"{subject} Advanced Concepts"]

    async def generate_phd_syllabus(self, subject: str) -> dict:
        """
        Generates a PhD-level syllabus (Modules -> Topics) for deep automation.
        """
        prompt = f"""
        Act as a Distinguished Professor.
        Create a PHD-LEVEL syllabus to master: "{subject}".
        
        Structure:
        1. Foundations (Undergraduate level)
        2. Advanced Theory (Graduate level)
        3. Expert Specialization (PhD level)
        4. State-of-the-Art Research
        
        For EACH module, provide 3-5 specific, dense, searchable topics.
        
        RETURN JSON ONLY:
        {{
            "foundations": ["Topic 1", "Topic 2"],
            "advanced": ["Topic 3", "Topic 4"],
            "expert": ["Topic 5", "Topic 6"],
            "research": ["Topic 7", "Topic 8"]
        }}
        """
        
        try:
            client = self._get_client()
            response = await client.chat.completions.create(
                model="Mistral-Nemo-Instruct-2407",
                messages=[
                    {"role": "system", "content": "You are a syllabus generator. Output strictly valid JSON only. Do not wrap in markdown blocks."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                temperature=0.3
            )
            content = response.choices[0].message.content.strip()
            print(f"[LEARNING] Raw LLM Syllabus Response: {content[:100]}...")

            # Clean Markdown Code Blocks
            content = content.replace("```json", "").replace("```", "").strip()
            
            # Extract JSON
            import re
            # look for the outermost braces
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                try:
                    data = json.loads(json_match.group(0))
                    print(f"[LEARNING] Syllabus Generated Successfully: {list(data.keys())}")
                    return data
                except json.JSONDecodeError as je:
                    print(f"[LEARNING] JSON Decode Error: {je}")
            
            print(f"[LEARNING] ERROR: Valid JSON not found in response.")
            return {}
        except Exception as e:
            print(f"[LEARNING] PhD Syllabus generation failed: {e}")
            return {}

    def _create_log_callback(self, parent_callback):
        """Helper to create a callback that respects the parent context."""
        async def wrapper(msg):
            # If we have a parent callback (from websocket), use it
            if parent_callback:
                # Need to handle if parent_callback is async or not?
                # Usually log_callback in start_automation_task comes from lambda in router which is likely just a function wrapping queue.put
                # Wait, in start_automation_task scope, I don't have access to the 'log' function defined inside?
                # No, I define 'log' inside start_automation_task but I need to pass something to active_research
                await parent_callback(msg)
            else:
                print(f"[AUTO] {msg}")
        return wrapper

    async def start_automation_task(self, subject: str, level: str = "PHD", log_callback=None):
        """
        Starts a long-running, autonomous learning task for a subject at a specific level.
        Iterates through the PhD syllabus chapters sequentially.
        """
        async def log(msg):
            print(f"[AUTO] {msg}")
            if log_callback:
                await log_callback(f"[AUTO] {msg}")

        await log(f"=== INITIALIZING AUTONOMOUS LEARNING ENGINE: {subject} ({level}) ===")
        await log("Consulting expert professors for curriculum generation...")
        
        # 1. Generate Full Syllabus
        syllabus = await self.generate_phd_syllabus(subject)
        
        if not syllabus:
             await log("Error: Failed to generate syllabus. Aborting.")
             return

        # 2. Iterate through Modules
        chapters = ["foundations", "advanced", "expert", "research"]
        
        # DEBUG: Log the keys we got
        await log(f"DEBUG: Syllabus Keys Received: {list(syllabus.keys())}")
        
        total_topics = sum(len(syllabus.get(c, [])) for c in chapters)
        
        await log(f"Syllabus Generated. {total_topics} Core Topics identified across {len(chapters)} Modules.")
        await log("Beginning Sequential Deep Dive...")
        
        processed = 0
        for module in chapters:
            topics = syllabus.get(module, [])
            if not topics:
                await log(f"DEBUG: Skipping empty module: {module}")
                continue
                
            await log(f"\n>> ENTERING MODULE: {module.upper()} <<")
            
            for topic in topics:
                processed += 1
                await log(f"--- Processing Topic {processed}/{total_topics}: {topic} ---")
                
                # Perform Deep Research on this topic
                try:
                    # Pass the SAME log wrapper to active_research
                    # Note: active_research expects log_callback(msg)
                    await self.active_research(topic, log_callback=log_callback)
                except Exception as ex:
                    await log(f"Error researching {topic}: {ex}")
                
                # Small cool-down
                import asyncio
                await asyncio.sleep(2)
        
        await log(f"=== AUTOMATION TASK COMPLETE: {subject}. Mastered {processed} topics. ===")

    async def start_mastery_mode(self, subject: str, log_callback=None):
        """
        Executes the Mastery Learning Loop.
        """
        import asyncio
        async def log(msg):
            if log_callback:
                print(f"[MASTERY] {msg}")
                await log_callback(f"[MASTERY] {msg}")
                await asyncio.sleep(0.02)  # Fast mode

        await log(f"Generating Curriculum for: {subject}...")
        curriculum = await self.generate_curriculum(subject)
        
        await log(f"Curriculum Developed ({len(curriculum)} Modules):")
        for i, item in enumerate(curriculum):
            await log(f"  {i+1}. {item}")
            
        await log("Beginning Intensive Study Session...")
        
        for i, topic in enumerate(curriculum):
            await log(f"--- Module {i+1}/{len(curriculum)}: {topic} ---")
            # Reuse existing active_research logic
            await self.active_research(topic, log_callback=log_callback)
            await log(f"Module '{topic}' Complete.")
            
        # Recursive Phase (The Rabbit Hole) - Extended for Deep Learning
        if self.dynamic_queue:
            max_depth = 100  # Extended for hours-long learning sessions
            await log(f"=== CURRICULUM COMPLETE. ENTERING EXTENDED DEEP DIVE ({len(self.dynamic_queue)} Related Topics, Max: {max_depth}) ===")
            
            rabbit_hole_depth = 0
            while self.dynamic_queue and rabbit_hole_depth < max_depth:
                topic = self.dynamic_queue.pop(0)
                if topic in self.learned_topics:
                    continue
                    
                rabbit_hole_depth += 1
                await log(f"--- Deep Dive {rabbit_hole_depth}/{max_depth}: {topic} ---")
                await self.active_research(topic, log_callback=log_callback)
                
                # Progress update every 10 topics
                if rabbit_hole_depth % 10 == 0:
                    await log(f">>> PROGRESS: {rabbit_hole_depth} topics explored. {len(self.dynamic_queue)} in queue. <<<")
                    
            if rabbit_hole_depth >= max_depth:
                await log(f">>> DEPTH LIMIT REACHED. Explored {rabbit_hole_depth} topics. {len(self.dynamic_queue)} remaining in queue. <<<")
            
        await log(f"=== EXTENDED MASTERY SESSION COMPLETE: {subject} ({self.learned_count} total facts stored) ===")



    async def active_research_auto(self, log_callback=None):
        """
        Autonomous Mode: PRIORITIZES Dynamic Queue (Recursive), then Curriculum, then Random.
        """
        import random
        import asyncio
        
        prefix = "[DEFAULT]"
        topic = "Future of AI"

        # 1. Check Dynamic Queue (Recursive Depth)
        if self.dynamic_queue:
            topic = self.dynamic_queue.pop(0)
            prefix = f"[DEEP DIVE ({len(self.dynamic_queue)} remaining)]"
        
        # 2. Check Curriculum
        elif self.curriculum and self.curriculum_index < len(self.curriculum):
            topic = self.curriculum[self.curriculum_index]
            self.curriculum_index += 1
            prefix = f"[CURRICULUM {self.curriculum_index}/{len(self.curriculum)}]"
            
        # 3. Random Discovery
        else:
            try:
                client = self._get_client()
                topic_resp = await client.chat.completions.create(
                    model="DeepSeek R1 Distill Qwen 32B",
                    messages=[{"role": "user", "content": "Generate ONE advanced and specific computer science topic to research right now. Return ONLY the topic name."}],
                    temperature=0.8
                )
                topic = topic_resp.choices[0].message.content.strip()
                prefix = "[AUTONOMOUS DISCOVERY]"
            except:
                topic = "Artificial General Intelligence Safety"
                prefix = "[DEFAULT]"
        
        # Avoid cycles
        if topic in self.learned_topics:
            if self.dynamic_queue:
                # Try next
                await self.active_research_auto(log_callback)
                return
            else:
                topic += " (Advanced)"

        if log_callback:
            await log_callback(f"\n>> AUTO-PILOT ENGAGED. ANALYZING KNOWLEDGE GAPS...\n")
            await asyncio.sleep(0.5)
            await log_callback(f">> OBJECTIVE SET: {prefix} {topic}\n")
            await log_callback(f">> AUTOMATICALLY ESTABLISHING SECURE CONNECTION...\n")
            
        # 2. Execute Research
        await self.active_research(topic, log_callback)
        
    async def active_research(self, topic: str, log_callback=None):
        # ... (Existing logic) ...
        import asyncio
        # 2. Execute Research
        # -----------------------------------------------------
        # NEW: Using Motor Cortex for Web Interaction
        import asyncio
        from cortex import web_search, read_url
        
        self.learned_topics.add(topic)
        
        async def log(message):
            if log_callback:
                # Sanitize message
                clean_msg = message.replace('\n', ' ')
                await log_callback(clean_msg)
                await asyncio.sleep(0.02)  # Fast mode
        
        # Initial log
        if log_callback:
             await log(f"\n>> ANALYZING: {topic}")

        await log(f"INITIATING RESEARCH PROTOCOL: '{topic}'")
        await log("Scanning neural pathways for existing knowledge...")
        
        # 1. Search Web (Non-blocking)
        await log("Connecting to global information grid...")
        # OFF-LOAD SYNCHRONOUS CALL TO THREAD
        search_results = await asyncio.to_thread(web_search, topic)
        
        if "No results" in search_results:
            await log("ERROR: No data streams found. Aborting.")
            return

        # DEEP RESEARCH: Read multiple URLs for comprehensive coverage
        await log("Analyzing search vectors...")
        
        # Extract ALL URLs from search results
        import re
        url_matches = re.findall(r'https?://[^\s\)]+', search_results)
        
        context_data = search_results
        pages_read = 0
        max_pages = 3  # Read up to 3 pages for depth
        
        for target_url in url_matches[:max_pages]:
            await log(f"Deep diving into node {pages_read+1}/{min(len(url_matches), max_pages)}: {target_url[:40]}...")
            
            try:
                page_content = await asyncio.to_thread(read_url, target_url)
                if "Error" not in page_content and len(page_content) > 100:
                    context_data += f"\n\n=== SOURCE {pages_read+1} ({target_url}) ===\n{page_content[:3000]}"
                    pages_read += 1
                    await log(f"Downloaded knowledge packet ({len(page_content)} chars).")
            except Exception as e:
                await log(f"Node access failed: {str(e)[:30]}")
                
        if pages_read == 0:
            await log("No deep sources accessible. Using search summary only.")
        else:
            await log(f"Acquired {pages_read} knowledge sources. Total context: {len(context_data)} chars.")
            
        await log("Data streams acquired. Analyzing content...")
        
        # 2. Extract Knowledge via LLM (Enhanced for Deep Learning)
        prompt = f"""
        Research Topic: "{topic}"
        
        Context Data (Search Results & Content):
        {context_data[:8000]} 
        
        Task: Extract COMPREHENSIVE knowledge for mastery-level understanding.
        
        Requirements:
        1. Extract 15-20 HIGH-VALUE FACTS covering:
           - Core concepts & definitions
           - Key principles & mechanisms
           - Real-world applications
           - Common misconceptions
           - Best practices
        2. Identify 5-8 RELATED CONCEPTS for deeper exploration.
        3. Extract 3-5 KEY TERMS with brief definitions.
        
        RETURN ONLY VALID JSON. NO MARKDOWN. NO CONVERSATION.
        Format:
        {{
            "facts": ["Fact 1", "Fact 2", ...],
            "related": ["Concept A", "Concept B", ...],
            "key_terms": {{"term1": "definition1", "term2": "definition2"}}
        }}
        """
        
        await log("Engaging cognitive processors...")
        try:
            client = self._get_client()
            response = await client.chat.completions.create(
                model="Mistral-Nemo-Instruct-2407",
                messages=[
                    {"role": "system", "content": "You are a research assistant. Output valid JSON only. Do not wrap in markdown."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=4000
            )
            
            # Robust Response Handling
            if not response:
                await log("ERROR: Received empty response from brain.")
                return
                
            content = ""
            if isinstance(response, dict):
                 choices = response.get('choices')
                 if not choices:
                     if "expoClient" in str(response):
                         await log(">> CRITICAL ERROR: PORT 8081 IS HIJACKED BY EXPO.")
                         return
                     await log(f"ERROR: No choices in response.")
                     return
                 content = choices[0].get('message', {}).get('content')
            else:
                if not hasattr(response, 'choices') or not response.choices:
                    if "expoClient" in str(response):
                         await log(">> CRITICAL ERROR: PORT 8081 IS HIJACKED BY EXPO.")
                         return
                    await log(f"ERROR: Invalid response structure.")
                    return
                content = response.choices[0].message.content

            if not content:
                await log("ERROR: Empty content received.")
                return
            
            # Clean JSON with Regex (Most Robust)
            import re
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
            else:
                json_str = content
                
            try:
                data = json.loads(json_str)
                facts = data.get("facts", [])
                related = data.get("related", [])
                key_terms = data.get("key_terms", {})
                
                # Convert key_terms dict to facts for storage
                if isinstance(key_terms, dict):
                    for term, definition in key_terms.items():
                        facts.append(f"DEFINITION: {term} - {definition}")
                
                # Fallback if list returned
                if isinstance(data, list):
                    facts = data
                    related = []
                    
            except json.JSONDecodeError:
                await log("WARNING: JSON Parsing failed. Attempting Fallback...")
                
                # Fallback: Treat entire content as one summary fact if it looks useful
                if len(content) > 50:
                    facts = [content.strip()]
                    related = ["Related Topic (Auto-Detected)"]
                    await log("Fallback successful: Saved raw summary as fact.")
                else:
                    await log("ERROR: Content too short for fallback.")
                    return

            if not facts:
                await log("No significant facts extracted.")
                return

            await log(f"Extraction complete. Found {len(facts)} knowledge items.")
            
            # Handle Related Topics (Deep Dive)
            if related:
                new_topics = [t for t in related if t not in self.learned_topics and t not in self.dynamic_queue]
                self.dynamic_queue.extend(new_topics)
                await log(f">> BRAIN EXPANSION: Discovered {len(new_topics)} new research vectors:")
                for t in new_topics[:3]:
                     await log(f"   > {t}")
                if len(new_topics) > 3: await log(f"   > ...and {len(new_topics)-3} more.")
            
            # 3. Store in Memory (Thread-safe, with duplicate detection)
            await log(f"Encoding {len(facts)} facts to long-term memory...")
            stored = 0
            skipped = 0
            for i, fact in enumerate(facts):
                was_new = await asyncio.to_thread(memory_service.add_memory, fact, {"source": "active_research", "topic": topic})
                if was_new:
                    self.learned_count += 1
                    stored += 1
                    await log(f"++ LEARNED: {fact[:80]}...")
                else:
                    skipped += 1
            
            if skipped > 0:
                await log(f"Stored {stored} new facts. Skipped {skipped} duplicates (already known).")
            else:
                await log(f"All {stored} facts stored successfully.")
                
            await log("RESEARCH PROTOCOL COMPLETE. Knowledge integrated.")
            
        except Exception as e:
            await log(f"CRITICAL ERROR during processing: {e}")
            import traceback
            traceback.print_exc()


    def get_learning_stats(self) -> dict:
        """
        Returns current learning statistics.
        """
        return {
            "learned_count": self.learned_count,
            "curriculum_progress": f"{self.curriculum_index}/{len(self.curriculum)}",
            "current_topics": list(self.learned_topics)[-5:] if self.learned_topics else [],
            "queue_size": len(self.dynamic_queue)
        }

learning_service = LearningService()
