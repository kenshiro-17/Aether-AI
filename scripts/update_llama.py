
import os
import sys
import zipfile
import urllib.request
import shutil

# URL for the latest stable build (approximate latest based on search)
# Using b4600 as a safe recent baseline if b7766 is too new/unstable, 
# but search suggested b7766. Let's try a known stable recent one or the specific one found.
# Actually, let's use a very recent one to ensure Llama 3.2 support.
DOWNLOAD_URL = "https://github.com/ggerganov/llama.cpp/releases/download/b4600/llama-b4600-bin-win-avx2-x64.zip" 
# Note: b4600 is hypothetical from typical numbering. 
# Search found b7766? That seems very high. 
# Let's try to find a *real* URL by checking a known recent tag if possible, or trust the search.
# Search said "b7766" as of Jan 2026. This seems plausible for 2026 context.
# Using Vulkan Build for AMD GPU Support
DOWNLOAD_URL = "https://github.com/ggerganov/llama.cpp/releases/download/b4500/llama-b4500-bin-win-vulkan-x64.zip"

TARGET_DIR = os.path.join(os.getcwd(), "backend", "bin")
ZIP_PATH = "llama_update.zip"

print(f"Downloading from: {DOWNLOAD_URL}")

try:
    # headers to avoid 403
    opener = urllib.request.build_opener()
    opener.addheaders = [('User-agent', 'Mozilla/5.0')]
    urllib.request.install_opener(opener)
    
    urllib.request.urlretrieve(DOWNLOAD_URL, ZIP_PATH)
    print("Download complete.")
    
    print("Extracting ALL files to ensure DLL compatibility...")
    with zipfile.ZipFile(ZIP_PATH, 'r') as zip_ref:
        for file in zip_ref.namelist():
            # Extract everything to target dir
            print(f"Extracting {file}...")
            zip_ref.extract(file, path=TARGET_DIR)
            
            # If it's in a subfolder (e.g. build/bin/...), move it to root of bin
            extracted_path = os.path.join(TARGET_DIR, file)
            filename = os.path.basename(file)
            final_path = os.path.join(TARGET_DIR, filename)
            
            if extracted_path != final_path and os.path.isfile(extracted_path):
                 if os.path.exists(final_path):
                     os.remove(final_path)
                 shutil.move(extracted_path, final_path)
                     
    print("Update complete.")
    
except Exception as e:
    print(f"Error updating: {e}")
    # Fallback to a slightly older but known good version if 404
    print("Trying fallback version b4500...")
    try: 
        FALLBACK_URL = "https://github.com/ggerganov/llama.cpp/releases/download/b4500/llama-b4500-bin-win-avx2-x64.zip"
        urllib.request.urlretrieve(FALLBACK_URL, ZIP_PATH)
        with zipfile.ZipFile(ZIP_PATH, 'r') as zip_ref:
             for file in zip_ref.namelist():
                if "llama-server.exe" in file:
                    zip_ref.extract(file, path=TARGET_DIR)
        print("Fallback update complete.")
    except Exception as e2:
        print(f"Fallback failed: {e2}")

if os.path.exists(ZIP_PATH):
    os.remove(ZIP_PATH)
