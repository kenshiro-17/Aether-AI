import os
import gc
import threading
import time
from pypdf import PdfReader
from docx import Document
from io import BytesIO
import requests
from bs4 import BeautifulSoup
from PIL import Image
import numpy as np

class IngestionService:
    """
    Document ingestion service with lazy-loaded OCR to minimize RAM usage.
    EasyOCR is only loaded when needed and auto-unloads after inactivity.
    """
    
    def __init__(self):
        self._ocr_reader = None
        self._ocr_lock = threading.Lock()
        self._last_ocr_use = 0
        self._ocr_unload_timeout = 120  # Unload OCR after 2 minutes of inactivity
        self._unload_timer = None
        print("[INGESTION] Service initialized (OCR will load on demand)")

    def _get_ocr_reader(self):
        """Lazy-load EasyOCR reader on first use."""
        with self._ocr_lock:
            if self._ocr_reader is None:
                print("[INGESTION] Loading OCR Model (this may take a moment)...")
                import easyocr
                # Use CPU to avoid VRAM conflicts with LLM
                self._ocr_reader = easyocr.Reader(['en'], gpu=False)
                print("[INGESTION] OCR Model loaded.")
            
            self._last_ocr_use = time.time()
            self._schedule_ocr_unload()
            return self._ocr_reader
    
    def _schedule_ocr_unload(self):
        """Schedule OCR unload after timeout."""
        if self._unload_timer:
            self._unload_timer.cancel()
        
        self._unload_timer = threading.Timer(self._ocr_unload_timeout, self._auto_unload_ocr)
        self._unload_timer.daemon = True
        self._unload_timer.start()
    
    def _auto_unload_ocr(self):
        """Auto-unload OCR after inactivity to free RAM (~1-2GB)."""
        with self._ocr_lock:
            if self._ocr_reader is not None:
                elapsed = time.time() - self._last_ocr_use
                if elapsed >= self._ocr_unload_timeout:
                    print(f"[INGESTION] Auto-unloading OCR after {elapsed:.0f}s of inactivity...")
                    self._unload_ocr_internal()
    
    def _unload_ocr_internal(self):
        """Internal method to unload OCR (must hold lock)."""
        if self._ocr_reader is not None:
            try:
                del self._ocr_reader
                self._ocr_reader = None
                gc.collect()
                
                # Also try to clear any PyTorch cache
                try:
                    import torch
                    if torch.cuda.is_available():
                        torch.cuda.empty_cache()
                except:
                    pass
                
                print("[INGESTION] OCR unloaded - RAM freed (~1-2GB).")
            except Exception as e:
                print(f"[INGESTION] Error unloading OCR: {e}")
    
    def unload_ocr(self):
        """Manually unload OCR to free RAM."""
        with self._ocr_lock:
            self._unload_ocr_internal()

    def parse_file(self, filename: str, content: bytes) -> str:
        # Secure filename check (double check just in case called directly)
        import werkzeug.utils
        filename = werkzeug.utils.secure_filename(filename)
        
        ext = filename.split('.')[-1].lower()
        
        if ext == 'pdf':
            return self._parse_pdf(content)
        elif ext == 'docx':
            return self._parse_docx(content)
        elif ext in ['txt', 'md', 'py', 'js', 'ts', 'tsx', 'java', 'c', 'cpp', 'rs', 'go', 'json', 'yml', 'yaml', 'html', 'htm']:
            return content.decode('utf-8', errors='ignore')
        elif ext in ['jpg', 'jpeg', 'png', 'bmp', 'webp']:
            return self._parse_image(content)
        else:
            raise ValueError(f"Unsupported file type: {ext}")

    def parse_url(self, url: str) -> str:
        """Extract main content from a URL."""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove clutter
            for tag in soup(['script', 'style', 'nav', 'footer', 'header', 'aside', 'iframe', 'ads', 'noscript']):
                tag.decompose()
            
            # Extract meaningful text blocks
            lines = []
            
            # Title
            if soup.title:
                lines.append(f"# {soup.title.get_text(strip=True)}")
                
            # Content - prioritize article bodies
            content_area = soup.find('article') or soup.find('main') or soup.body
            
            if content_area:
                for element in content_area.find_all(['h1', 'h2', 'h3', 'p', 'li', 'pre', 'code']):
                    text = element.get_text(strip=True)
                    if len(text) > 10:
                        if element.name.startswith('h'):
                            lines.append(f"\n## {text}")
                        elif element.name == 'li':
                            lines.append(f"- {text}")
                        elif element.name in ['pre', 'code']:
                            lines.append(f"```\n{text}\n```")
                        else:
                            lines.append(text)
                            
            return "\n".join(lines)
            
        except Exception as e:
            raise ValueError(f"Failed to fetch URL: {str(e)}")

    def _parse_pdf(self, content: bytes) -> str:
        reader = PdfReader(BytesIO(content))
        full_text = []
        
        for i, page in enumerate(reader.pages):
            text = page.extract_text()
            if text and len(text.strip()) > 50:
                full_text.append(text)
            else:
                # Fallback: Try to extract images for OCR (Scanned PDF)
                print(f"[INGESTION] Page {i} seems scanned/empty. Attempting OCR...")
                page_text = ""
                try:
                    for img in page.images:
                        ocr_data = self._parse_image(img.data)
                        page_text += ocr_data + "\n"
                except Exception as e:
                    print(f"[INGESTION] PDF OCR failed for page {i}: {e}")
                
                if page_text:
                    full_text.append(f"[OCR Page {i+1}]\n{page_text}")
                else:
                    full_text.append(text or "")

        return "\n\n".join(full_text)

    def _parse_docx(self, content: bytes) -> str:
        doc = Document(BytesIO(content))
        return "\n".join([para.text for para in doc.paragraphs])

    def _parse_image(self, content: bytes) -> str:
        try:
            image = Image.open(BytesIO(content))
            image_np = np.array(image)
            
            print("[INGESTION] Starting OCR processing...")
            reader = self._get_ocr_reader()
            result = reader.readtext(image_np)
            print(f"[INGESTION] OCR found {len(result)} text regions.")
            
            # Format results: (bbox, text, prob)
            text_lines = []
            for (bbox, text, prob) in result:
                if prob > 0.3:  # Confidence threshold
                    text_lines.append(text)
            
            full_text = "\n".join(text_lines)
            print(f"[INGESTION] OCR extracted: {full_text[:100]}...")
            return f"[IMAGE CONTENT START]\n{full_text}\n[IMAGE CONTENT END]"
            
        except Exception as e:
            print(f"[INGESTION] OCR Error: {e}")
            return f"[Error processing image: {str(e)}]"

    def chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> list[str]:
        """Split text into overlapping chunks for better RAG retrieval."""
        chunks = []
        start = 0
        while start < len(text):
            end = start + chunk_size
            # Try to find a sentence break
            if end < len(text):
                last_period = text.rfind('.', start, end)
                if last_period != -1 and last_period > start + chunk_size // 2:
                    end = last_period + 1
            
            chunks.append(text[start:end])
            start = end - overlap
        return chunks

    def cleanup(self):
        """Clean up resources."""
        print("[INGESTION] Cleaning up...")
        if self._unload_timer:
            self._unload_timer.cancel()
        self.unload_ocr()
        print("[INGESTION] Cleanup complete.")

ingestion_service = IngestionService()
