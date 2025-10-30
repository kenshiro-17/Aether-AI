"""
Self-Evolution Service (Architect Mode)
Enables the AI to analyze its own source code and propose improvements.
Safety Level: ARCHITECT (Can modify backend code with approval).
"""
import os
import glob
from typing import List, Dict, Optional
from openai import OpenAI
import difflib

# Configuration
# Point to local LLM (will be DeepSeek R1 32B)
client = OpenAI(
    base_url="http://localhost:8081/v1",
    api_key="ollama"
)

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKEND_DIR = os.path.join(PROJECT_ROOT, "backend")

class SelfEvolutionService:
    def __init__(self):
        self.enabled = True
        
    def analyze_module(self, module_name: str) -> Dict:
        """
        Reads a backend file and asks the LLM for optimization proposals.
        """
        file_path = os.path.join(BACKEND_DIR, module_name)
        if not os.path.exists(file_path):
            return {"error": f"File {module_name} not found."}
            
        with open(file_path, "r", encoding="utf-8") as f:
            code_content = f.read()
            
        print(f"[ARCHITECT] Analyzing {module_name}...")
        
        prompt = f"""
        Act as a Senior Python Architect.
        Analyze the following source code from the file '{module_name}'.
        
        Goal: Identify potential bugs, performance bottlenecks, or messy code.
        Focus: Security, Speed, and PEP8 Compliance.
        
        Source Code:
        ```python
        {code_content}
        ```
        
        Return a JSON object with:
        - "issues": List of strings describing problems.
        - "score": 1-10 rating of code quality.
        - "proposal": A suggested refactoring description (High Level).
        """
        
        try:
            response = client.chat.completions.create(
                model="Mistral-Nemo-Instruct-2407", 
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                temperature=0.2
            )
            return response.choices[0].message.content
        except Exception as e:
            return {"error": str(e)}

    def generate_patch(self, module_name: str, proposal_text: str) -> str:
        """
        Generates the actual new code based on a proposal.
        Returns the new code content.
        """
        file_path = os.path.join(BACKEND_DIR, module_name)
        with open(file_path, "r", encoding="utf-8") as f:
            code_content = f.read()

        prompt = f"""
        You are a Code Refactoring Engine.
        Original File: {module_name}
        
        Proposal: {proposal_text}
        
        Task: Rewrite the ENTIRE file content to implement the proposal.
        Maintain all existing functionality. Only improve.
        
        Original Code:
        ```python
        {code_content}
        ```
        
        Output ONLY the raw Python code. No markdown.
        """
        
        try:
            response = client.chat.completions.create(
                model="Mistral-Nemo-Instruct-2407",
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content.strip().replace("```python", "").replace("```", "")
        except Exception as e:
            return f"# Error generating patch: {e}"

    def list_backend_files(self) -> List[str]:
        """List all Python files in backend."""
        files = glob.glob(os.path.join(BACKEND_DIR, "*.py"))
        return [os.path.basename(f) for f in files]

# Global Instance
self_evolution_service = SelfEvolutionService()
