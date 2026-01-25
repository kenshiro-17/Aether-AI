import os
from huggingface_hub import hf_hub_download

# Qwen2.5-Coder-7B-Instruct (GGUF Quantization for speed/memory balance)
MODEL_REPO = "Qwen/Qwen2.5-Coder-7B-Instruct-GGUF"
MODEL_FILE = "qwen2.5-coder-7b-instruct-q4_k_m.gguf"
OUTPUT_DIR = "../models"

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

print(f"Downloading {MODEL_FILE} from {MODEL_REPO}...")
hf_hub_download(repo_id=MODEL_REPO, filename=MODEL_FILE, local_dir=OUTPUT_DIR, local_dir_use_symlinks=False)
print("Download complete.")
