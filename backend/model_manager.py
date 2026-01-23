import os
import sys
import shutil
from huggingface_hub import hf_hub_download

# Define Best-in-Class Models (Optimized for 8GB-16GB RAM Systems)
MODELS = {
    "llama_4_scout_17b": {
        "name": "Llama 4 Scout 17B (Instruct)",
        "repo_id": "lmstudio-community/Llama-4-Scout-17B-16E-Instruct-GGUF",
        "filenames": [
            "Llama-4-Scout-17B-16E-Instruct-Q4_K_M-00001-of-00002.gguf",
            "Llama-4-Scout-17B-16E-Instruct-Q4_K_M-00002-of-00002.gguf"
        ],
        "type": "flagship",
        "priority": 0
    },
    "llama_3_3_8b": {
        "name": "Llama 3.3 8B Instruct",
        "repo_id": "Mungert/Llama-3.3-8B-Instruct-GGUF",
        "filenames": ["Llama-3.3-8B-Instruct-q4_k_m.gguf"],
        "type": "general",
        "priority": 1
    },
    "deepseek_r1_8b": {
        "name": "DeepSeek R1 Distill Llama 8B",
        "repo_id": "unsloth/DeepSeek-R1-Distill-Llama-8B-GGUF",
        "filenames": ["DeepSeek-R1-Distill-Llama-8B-Q4_K_M.gguf"],
        "type": "general",
        "priority": 2
    },
    "qwen_coder_7b": {
        "name": "Qwen 2.5 Coder 7B",
        "repo_id": "Qwen/Qwen2.5-Coder-7B-Instruct-GGUF", 
        "filenames": ["qwen2.5-coder-7b-instruct-q4_k_m.gguf"],
        "type": "coding",
        "priority": 2
    },
    "mistral_nemo_12b": {
        "name": "Mistral Nemo 12B",
        "repo_id": "bartowski/Mistral-Nemo-Instruct-2407-GGUF",
        "filenames": ["Mistral-Nemo-Instruct-2407-Q4_K_M.gguf"],
        "type": "general",
        "priority": 3
    },
    "llama_3_2_3b": {
        "name": "Llama 3.2 3B Instruct",
        "repo_id": "unsloth/Llama-3.2-3B-Instruct-GGUF",
        "filenames": ["Llama-3.2-3B-Instruct-Q4_K_M.gguf"],
        "type": "efficient",
        "priority": 4
    },
    "phi_3_5_mini": {
        "name": "Phi-3.5 Mini Instruct",
        "repo_id": "Bartowski/Phi-3.5-mini-instruct-GGUF",
        "filenames": ["Phi-3.5-mini-instruct-Q4_K_M.gguf"],
        "type": "efficient",
        "priority": 5
    }
}

MODELS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models")

def get_current_model():
    """Reads start_system.bat to find the active model."""
    bat_path = os.path.join(os.path.dirname(MODELS_DIR), "start_system.bat")
    with open(bat_path, "r") as f:
        content = f.read()
    
    for key, model in MODELS.items():
        # Check first filename
        if model["filenames"][0] in content:
            return key, model
    return "unknown", None

def download_model(model_key):
    """Downloads the specified model from Hugging Face."""
    if model_key not in MODELS:
        print(f"Error: Unknown model key {model_key}")
        return False
        
    model = MODELS[model_key]
    print(f"Inititating download for {model['name']}...")
    
    success = True
    for fname in model["filenames"]:
        try:
            print(f"Downloading part: {fname}...")
            file_path = hf_hub_download(
                repo_id=model["repo_id"],
                filename=fname,
                local_dir=MODELS_DIR
            )
            print(f"Successfully downloaded to: {file_path}")
        except Exception as e:
            print(f"Download failed for {fname}: {e}")
            success = False
            break
            
    return success

def switch_model(model_key):
    """Updates start_system.bat to use the new model."""
    if model_key not in MODELS:
        print(f"Error: Unknown model key {model_key}")
        return False

    model = MODELS[model_key]
    # Use the first file as the target (llama.cpp auto-detects the rest)
    main_filename = model["filenames"][0]
    target_path = os.path.join(MODELS_DIR, main_filename)
    
    # 1. Ensure it exists (check all parts)
    missing = False
    for fname in model["filenames"]:
        if not os.path.exists(os.path.join(MODELS_DIR, fname)):
            missing = True
            break
            
    if missing:
        print(f"Model files incomplete. Downloading {model['name']}...")
        success = download_model(model_key)
        if not success:
            return False
            
    # 2. Update start_system.bat
    bat_path = os.path.join(os.path.dirname(MODELS_DIR), "start_system.bat")
    
    with open(bat_path, "r") as f:
        lines = f.readlines()
        
    new_lines = []
    for line in lines:
        if line.strip().startswith("set \"MODEL_PATH="):
            new_lines.append(f'set "MODEL_PATH=%PROJECT_ROOT%models\\{main_filename}"\n')
        else:
            new_lines.append(line)
            
    with open(bat_path, "w") as f:
        f.writelines(new_lines)
        
    print(f"System configuration updated to use: {model['name']}")
    print("Please restart the backend (start_system.bat) to apply changes.")
    print("(You can run force_restart.bat)")
    return True

if __name__ == "__main__":
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "download" and len(sys.argv) > 2:
            download_model(sys.argv[2])
        elif cmd == "switch" and len(sys.argv) > 2:
            switch_model(sys.argv[2])
        elif cmd == "list":
            for k, v in MODELS.items():
                print(f"{k}: {v['name']} ({v['filename']})")
    else:
        print("Usage: python model_manager.py [download|switch|list] [model_key]")
