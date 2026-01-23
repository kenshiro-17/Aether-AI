import os
import sys
from memory_service import memory_service

# Path to the skills directory
# Root is one level up from backend
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
SKILLS_ROOT = os.path.join(PROJECT_ROOT, "..", ".agent", "skills", "skills")

def ingest_all_skills():
    print(f"Scanning for skills in: {SKILLS_ROOT}")
    
    if not os.path.exists(SKILLS_ROOT):
        print(f"Error: Skills directory not found at {SKILLS_ROOT}")
        return

    count = 0
    errors = 0
    
    for root, dirs, files in os.walk(SKILLS_ROOT):
        for file in files:
            if file == "SKILL.md":
                skill_path = os.path.join(root, file)
                skill_name = os.path.basename(root)
                
                try:
                    with open(skill_path, "r", encoding="utf-8") as f:
                        content = f.read()
                    
                    # Create a rich context for the memory
                    # We prepend headers to help the RAG retriever find it by title/topic
                    full_content = f"SKILL: {skill_name}\n\n{content}"
                    
                    # Add to memory
                    print(f"Ingesting skill: {skill_name}...")
                    memory_service.add_memory(
                        text=full_content,
                        metadata={
                            "source": "antigravity_skill_library",
                            "type": "skill",
                            "skill_name": skill_name,
                            "path": skill_path
                        }
                    )
                    count += 1
                    
                except Exception as e:
                    print(f"Failed to ingest {skill_name}: {e}")
                    errors += 1

    print(f"\n[COMPLETE] Ingested {count} skills with {errors} errors.")
    print("The model now possesses this knowledge in its long-term memory.")

if __name__ == "__main__":
    # Ensure we can import backend modules
    sys.path.append(PROJECT_ROOT)
    ingest_all_skills()
