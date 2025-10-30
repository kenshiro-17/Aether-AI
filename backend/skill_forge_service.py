"""
Skill Forge Service (Dynamic Tool Creation)
Allows the AI to write its own Python tools (Skills) and use them.
"""
import os
import importlib.util
import inspect
from typing import Dict, List, Callable, Any
from openai import OpenAI

# Configuration
client = OpenAI(
    base_url="http://localhost:8081/v1",
    api_key="ollama"
)

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILLS_DIR = os.path.join(PROJECT_ROOT, "backend", "skills")

# Ensure skills directory exists
os.makedirs(SKILLS_DIR, exist_ok=True)

class SkillForgeService:
    def __init__(self):
        self.loaded_skills: Dict[str, Callable] = {}
        self.load_all_skills() # Load on startup

    def load_all_skills(self):
        """Dynamically load all python scripts in the skills directory."""
        print("[SKILL FORGE] Loading skills...")
        self.loaded_skills = {}
        
        for filename in os.listdir(SKILLS_DIR):
            if filename.endswith(".py") and not filename.startswith("_"):
                self._load_skill_file(filename)
                
        print(f"[SKILL FORGE] Loaded {len(self.loaded_skills)} skills.")

    def _load_skill_file(self, filename: str):
        """Load a single skill file."""
        module_name = filename[:-3]
        file_path = os.path.join(SKILLS_DIR, filename)
        
        try:
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Find the main function in the module (convention: must match filename or be decorated)
            # For simplicity, we assume the module has a function named 'execute' or same as module
            if hasattr(module, "execute"):
                self.loaded_skills[module_name] = module.execute
                print(f"  + Loaded Skill: {module_name}")
            else:
                print(f"  - Skipped {filename}: No 'execute' function found.")
                
        except Exception as e:
            print(f"  ! Error loading {filename}: {e}")

    def create_skill(self, tool_name: str, problem_description: str) -> str:
        """
        Ask LLM to write a new Python skill to solve a problem.
        Saves the file and loads it.
        """
        print(f"[SKILL FORGE] Forging new skill: {tool_name}...")
        
        prompt = f"""
        You are a Python Tool Developer.
        Goal: Create a standalone Python script to solve a specific problem.
        
        Tool Name: {tool_name}
        Problem: {problem_description}
        
        Requirements:
        1. Must have a function named `execute(**kwargs)` as the entry point.
        2. Must be pure Python (standard library preferred, or common libs like requests/pandas).
        3. Include docstrings explaining usage.
        4. Return the result (str or dict), do not just print.
        
        Output ONLY the Python code.
        """
        
        try:
            response = client.chat.completions.create(
                model="DeepSeek R1 Distill Qwen 32B", 
                messages=[{"role": "user", "content": prompt}]
            )
            code = response.choices[0].message.content.strip()
            # Clean markdown
            if "```python" in code:
                code = code.split("```python")[1].split("```")[0].strip()
            elif "```" in code:
                code = code.split("```")[1].split("```")[0].strip()
                
            # Save to file
            filename = f"{tool_name}.py"
            file_path = os.path.join(SKILLS_DIR, filename)
            
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(code)
                
            print(f"[SKILL FORGE] Skill saved to {file_path}")
            
            # Reload
            self._load_skill_file(filename)
            return f"Skill '{tool_name}' created and loaded successfully."
            
        except Exception as e:
            return f"Failed to forge skill: {e}"

    def run_skill(self, tool_name: str, **kwargs) -> Any:
        """Run a specific skill."""
        if tool_name not in self.loaded_skills:
            return f"Error: Skill '{tool_name}' not found."
            
        try:
            print(f"[SKILL FORGE] Executing {tool_name}...")
            return self.loaded_skills[tool_name](**kwargs)
        except Exception as e:
            return f"Skill Execution Error: {e}"

    def get_skills_list(self) -> List[str]:
        return list(self.loaded_skills.keys())

# Global Instance
skill_forge = SkillForgeService()
