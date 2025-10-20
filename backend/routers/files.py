from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
import shutil
import os
import uuid
from pypdf import PdfReader
from PIL import Image
import io
from memory_service import memory_service
from ingestion_service import ingestion_service

router = APIRouter()

class IngestResponse(BaseModel):
    filename: str
    chunks_added: int
    message: str

TEMP_DIR = "temp_uploads"
os.makedirs(TEMP_DIR, exist_ok=True)

# File upload limits
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
ALLOWED_EXTENSIONS = {
    '.txt', '.md', '.pdf', '.py', '.js', '.jsx', '.ts', '.tsx', 
    '.json', '.xml', '.html', '.css', '.csv', '.log',
    '.jpg', '.jpeg', '.png', '.gif', '.bmp'
}

@router.post("/ingest/file", response_model=IngestResponse)
async def ingest_file(file: UploadFile = File(...)):
    # Sanitize filename (Path Traversal Protection)
    import werkzeug.utils
    filename = werkzeug.utils.secure_filename(file.filename or "unknown_file")
    
    # Validate file extension
    file_ext = os.path.splitext(filename)[1].lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400, 
            detail=f"File type {file_ext} not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    file_id = str(uuid.uuid4())
    file_path = os.path.join(TEMP_DIR, f"{file_id}_{filename}")
    
    # Save uploaded file with size validation
    try:
        file_size = 0
        with open(file_path, "wb") as buffer:
            while chunk := await file.read(8192):  # Read in 8KB chunks
                file_size += len(chunk)
                if file_size > MAX_FILE_SIZE:
                    # Cleanup partial file
                    buffer.close()
                    os.remove(file_path)
                    raise HTTPException(
                        status_code=413, 
                        detail=f"File too large. Maximum size: {MAX_FILE_SIZE // (1024*1024)}MB"
                    )
                buffer.write(chunk)
    except HTTPException:
        raise
    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Could not save file: {e}")
    finally:
        await file.close()

    extracted_text = ""
    
    # Process based on file type
    # Process using Ingestion Service for ALL types
    try:
        # Read the file back
        with open(file_path, "rb") as f:
            file_bytes = f.read()
            
        extracted_text = ingestion_service.parse_file(filename, file_bytes)
        
    except Exception as e:
        # If specific parsing fails, try to return generic error
        print(f"Parsing failed: {e}")
        extracted_text = f"Error interpreting file: {str(e)}"
    finally:
        # Cleanup
        if os.path.exists(file_path):
            os.remove(file_path)

    if not extracted_text.strip():
        return IngestResponse(filename=filename, chunks_added=0, message="No text content extracted")

    # Save to Memory
    try:
        # chunk_size=500 is default in memory_service
        # We prefix with filename for context
        full_text = f"File: {filename}\n\n{extracted_text}"
        memory_service.add_memory(full_text, metadata={"filename": filename})
    except Exception as e:
        print(f"ERROR: Failed to save memory: {e}")
        # We don't fail the upload if memory fails, but we should warn
        return IngestResponse(
            filename=filename,
            chunks_added=0,
            message=f"File processed but memory indexing failed: {str(e)}"
        )
    
    return IngestResponse(
        filename=filename, 
        chunks_added=1, # simplified, memory service splits it
        message="File processed and memory updated"
    )
