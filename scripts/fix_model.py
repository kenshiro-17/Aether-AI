
import os
import sys

# Ensure backend module can be found
sys.path.append(os.path.join(os.getcwd(), 'backend'))

import backend.model_manager as mm

model_path = os.path.join("models", "Llama-3.2-3B-Instruct-Q4_K_M.gguf")

print(f"Target Model: {model_path}")

if os.path.exists(model_path):
    print(f"Found existing file ({os.path.getsize(model_path)} bytes). Deleting...")
    try:
        os.remove(model_path)
        print("File successfully deleted.")
    except Exception as e:
        print(f"Error deleting file: {e}")
        print("Attempting to rename it instead...")
        try:
            os.rename(model_path, model_path + ".corrupt")
            print("Renamed to .corrupt_backup")
        except:
            print("Could not delete or rename. File might be locked.")
            sys.exit(1)
            
print("Initiating fresh download...")
mm.download_model("llama_3_2_3b")
print("Process Complete.")
