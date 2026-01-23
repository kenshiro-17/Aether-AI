import os
import sys
import json
from memory_service import memory_service

# Path setup
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
SKILLS_BASE = os.path.join(PROJECT_ROOT, "..", ".agent", "skills")

def ingest_documentation():
    print("Ingesting Skill System Documentation...")
    
    docs_to_ingest = [
        "README.md",
        "docs/SKILL_ANATOMY.md",
        "docs/VISUAL_GUIDE.md",
        "docs/EXAMPLES.md"
    ]
    
    for relative_path in docs_to_ingest:
        full_path = os.path.join(SKILLS_BASE, relative_path)
        if os.path.exists(full_path):
            try:
                with open(full_path, "r", encoding="utf-8") as f:
                    content = f.read()
                
                print(f"  + Ingesting {relative_path}...")
                memory_service.add_memory(
                    text=f"SKILL SYSTEM DOC: {relative_path}\n\n{content}",
                    metadata={
                        "source": "antigravity_skill_docs",
                        "type": "documentation",
                        "filename": relative_path
                    }
                )
            except Exception as e:
                print(f"  ! Failed to ingest {relative_path}: {e}")
        else:
            print(f"  - Skipped {relative_path} (not found)")

def ingest_index():
    print("\nIngesting Master Skill Index...")
    index_path = os.path.join(SKILLS_BASE, "skills_index.json")
    
    if os.path.exists(index_path):
        try:
            with open(index_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # Ingest the entire index as a single searchable artifact
            # This helps the model "list all skills" or "find skill for X"
            index_text = "MASTER SKILL INDEX:\n\n"
            for item in data:
                index_text += f"- {item.get('name')} ({item.get('id')}): {item.get('description')}\n"
            
            print(f"  + Ingesting Index ({len(data)} items)...")
            memory_service.add_memory(
                text=index_text,
                metadata={
                    "source": "antigravity_skill_index",
                    "type": "index",
                    "count": len(data)
                }
            )
            
            # Also ingest individual index entries for granular search
            print("  + Ingesting individual index entries...")
            for item in data:
                entry_text = f"SKILL META: {item.get('name')}\nID: {item.get('id')}\nPath: {item.get('path')}\nDescription: {item.get('description')}"
                memory_service.add_memory(
                    text=entry_text,
                    metadata={
                        "source": "antigravity_skill_entry",
                        "type": "skill_meta",
                        "skill_id": item.get('id')
                    }
                )
                
        except Exception as e:
            print(f"  ! Failed to ingest index: {e}")
    else:
        print("  - skills_index.json not found.")

if __name__ == "__main__":
    sys.path.append(PROJECT_ROOT)
    ingest_documentation()
    ingest_index()
    print("\n[COMPLETE] Skill System Knowledge Ingested.")
