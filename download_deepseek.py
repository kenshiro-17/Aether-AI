
import os
import requests
from tqdm import tqdm

MODEL_URL = "https://huggingface.co/bartowski/DeepSeek-R1-Distill-Llama-8B-GGUF/resolve/main/DeepSeek-R1-Distill-Llama-8B-Q4_K_M.gguf"
OUTPUT_DIR = "models"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "DeepSeek-R1-Distill-Llama-8B-Q4_K_M.gguf")

def download_file(url, filename):
    print(f"Starting download: {filename}")
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    block_size = 1024 * 1024  # 1MB

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    with open(filename, 'wb') as file, tqdm(
        desc=filename,
        total=total_size,
        unit='iB',
        unit_scale=True,
        unit_divisor=1024,
    ) as bar:
        for data in response.iter_content(block_size):
            size = file.write(data)
            bar.update(size)
    print("Download complete.")

if __name__ == "__main__":
    if os.path.exists(OUTPUT_FILE):
        print(f"File already exists: {OUTPUT_FILE}")
    else:
        try:
            download_file(MODEL_URL, OUTPUT_FILE)
        except KeyboardInterrupt:
            print("\nDownload cancelled.")
            if os.path.exists(OUTPUT_FILE):
                os.remove(OUTPUT_FILE)
        except Exception as e:
            print(f"Error: {e}")
