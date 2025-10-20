from fastapi import APIRouter, HTTPException, Body, Depends, UploadFile, File
from pydantic import BaseModel
from memory_service import memory_service
from ingestion_service import ingestion_service
from database import get_db

router = APIRouter(prefix="/memory", tags=["memory"])

class MemoryItem(BaseModel):
    text: str
    metadata: dict = {}

@router.post("/add")
def add_memory(item: MemoryItem):
    """Ingest new knowledge into the AI's long-term memory."""
    try:
        memory_service.add_memory(item.text, item.metadata)
        return {"status": "success", "message": "Memory ingested."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Parse and ingest a file (PDF, Docx, Text, Code) into memory."""
    try:
        content = await file.read()
        text = ingestion_service.parse_file(file.filename, content)
        
        # Smart Chunking
        chunks = ingestion_service.chunk_text(text, chunk_size=1000, overlap=200)
        
        print(f"Ingesting {len(chunks)} chunks from {file.filename}...")
        for i, chunk in enumerate(chunks):
            memory_service.add_memory(chunk, {
                "source": "file", 
                "filename": file.filename, 
                "chunk_index": i,
                "total_chunks": len(chunks)
            })
        
        return {"status": "success", "message": f"File '{file.filename}' ingested as {len(chunks)} chunks.", "chars_read": len(text)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/list")
def list_memories(limit: int = 100):
    """Retrieve all stored memories."""
    return {"memories": memory_service.get_all_memories(limit=limit)}

@router.post("/query")
def query_memory(query: str = Body(..., embed=True)):
    """Debug endpoint to search memory directly."""
    results = memory_service.search_memory(query)
    return {"results": results}
