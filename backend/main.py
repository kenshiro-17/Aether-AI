from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks, Request, Depends
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
import os
import sys
import gc
import json
import asyncio
import datetime
import signal
import atexit
from typing import Optional
from database import engine, Base
import models # Import logic models to ensure they are registered with Base
from openai import OpenAI
from routers import sync, memory, chat, files, stt, auth
from memory_service import memory_service
from learning_service import learning_service
from research_service import research_service
from model_updater_service import model_updater_service
from skill_forge_service import skill_forge
from ingestion_service import ingestion_service
import shutil
from database import get_db
from routers.chat import Message as DBMessage, Conversation as DBConversation
from cortex import web_search, run_python, TOOLS_SCHEMA
from cortex.visual import visual_cortex

# Create tables
Base.metadata.create_all(bind=engine)

# OpenAI Client moved to routers/chat.py

app = FastAPI(title="Aether-AI")

app.include_router(sync.router)
app.include_router(memory.router)
app.include_router(chat.router)
app.include_router(files.router)
app.include_router(stt.router)
app.include_router(auth.router)

# Dynamic Routers
from routers import learning
app.include_router(learning.router, prefix="/v1", tags=["learning"])

from starlette.middleware.base import BaseHTTPMiddleware

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response

app.add_middleware(SecurityHeadersMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Chat Models moved to routers/chat.py

class UrlIngestRequest(BaseModel):
    url: str

def cleanup_resources():
    """Clean up RAM and VRAM resources on shutdown."""
    print("\n[SHUTDOWN] Cleaning up resources...")
    
    # 1. Stop background services
    try:
        research_service.stop()
        print("[SHUTDOWN] Research service stopped.")
    except Exception as e:
        print(f"[SHUTDOWN] Error stopping research service: {e}")
    
    try:
        model_updater_service.stop()
        print("[SHUTDOWN] Model updater service stopped.")
    except Exception as e:
        print(f"[SHUTDOWN] Error stopping model updater: {e}")
    
    # 2. Close memory service (Qdrant client)
    try:
        memory_service.cleanup()
        print("[SHUTDOWN] Memory service cleaned up.")
    except Exception as e:
        print(f"[SHUTDOWN] Error cleaning up memory service: {e}")
    
    # 2b. Clean up ingestion service (OCR)
    try:
        ingestion_service.cleanup()
        print("[SHUTDOWN] Ingestion service cleaned up.")
    except Exception as e:
        print(f"[SHUTDOWN] Error cleaning up ingestion service: {e}")
    
    # 3. Clear PyTorch GPU cache if available (for SentenceTransformer/EasyOCR)
    try:
        import torch
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            torch.cuda.synchronize()
            print("[SHUTDOWN] PyTorch GPU cache cleared.")
    except ImportError:
        pass  # PyTorch not installed
    except Exception as e:
        print(f"[SHUTDOWN] Error clearing GPU cache: {e}")
    
    # 4. Force garbage collection
    gc.collect()
    print("[SHUTDOWN] Garbage collection completed.")
    print("[SHUTDOWN] Cleanup complete.")

# Register cleanup for various shutdown scenarios
atexit.register(cleanup_resources)

def signal_handler(signum, frame):
    """Handle termination signals."""
    print(f"\n[SHUTDOWN] Received signal {signum}, initiating cleanup...")
    cleanup_resources()
    sys.exit(0)

# Register signal handlers (Windows compatible)
try:
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    # SIGBREAK is Windows-specific for Ctrl+Break
    if hasattr(signal, 'SIGBREAK'):
        signal.signal(signal.SIGBREAK, signal_handler)
except Exception as e:
    print(f"[STARTUP] Could not register some signal handlers: {e}")

@app.on_event("startup")
async def startup_event():
    print("Starting Learning & Research Services...")
    research_service.start_background_loop()
    model_updater_service.start_background_loop()

@app.on_event("shutdown")
async def shutdown_event():
    """FastAPI shutdown event - clean up all resources."""
    cleanup_resources()

@app.get("/")
def read_root():
    return {"status": "online", "service": "Aether-AI // Systems Operational"}

@app.post("/ingest/url")
def ingest_url(request: UrlIngestRequest):
    """Ingest content from a URL into long-term memory."""
    try:
        print(f"Ingesting URL: {request.url}")
        content = ingestion_service.parse_url(request.url)
        
        if not content:
            raise HTTPException(status_code=400, detail="Could not extract content from URL")
            
        # Store in memory
        memory_service.add_memory(content, metadata={
            "source": request.url,
            "type": "web_article",
            "timestamp": datetime.datetime.now().isoformat()
        })
        
        return {"status": "success", "message": f"Ingested content from {request.url}", "length": len(content)}
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"URL Ingestion Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/check-internet")
def check_internet():
    """Check if internet connectivity is available (Robust Socket + HTTP)."""
    import requests
    import socket
    
    # 1. Quickest Check: DNS Socket (Bypasses SSL/HTTP issues)
    try:
        # Try connecting to Google DNS (8.8.8.8) on port 53
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return {"connected": True, "status": "Online (Socket)", "latency_ms": 10}
    except:
        pass

    # 2. HTTP Fallback
    test_urls = [
        "http://www.google.com", # HTTP first (faster/no handshake)
        "https://www.google.com",
        "https://www.cloudflare.com"
    ]
    
    errors = []
    
    for url in test_urls:
        try:
            response = requests.get(url, timeout=3, headers={'User-Agent': 'Mozilla/5.0'})
            if response.status_code < 400:
                return {"connected": True, "status": f"Online ({url})", "latency_ms": int(response.elapsed.total_seconds() * 1000)}
        except Exception as e:
            errors.append(str(e)[:50])
            
    return {"connected": False, "status": "Offline", "error": "; ".join(errors)}

@app.get("/api/settings")
def get_settings():
    """Get current AI settings - reads real values from config files."""
    import re
    import os
    
    # Get model name dynamically
    from model_manager import get_current_model
    model_key, model_info = get_current_model()
    model_name = model_info["name"] if model_info else "Unknown Model"
    
    # Read context size from start_system.bat
    context_size = 8192  # Default fallback
    max_tokens = 4096    # Default fallback
    
    try:
        bat_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "start_system.bat")
        with open(bat_path, "r") as f:
            content = f.read()
        
        # Parse -c parameter from llama-server command
        context_match = re.search(r'-c\s+(\d+)', content)
        if context_match:
            context_size = int(context_match.group(1))
            max_tokens = context_size // 2  # Max tokens typically half of context
    except Exception as e:
        print(f"[SETTINGS] Could not read start_system.bat: {e}")
    
    return {
        "model": model_name,
        "temperature": 0.7,
        "max_tokens": max_tokens,
        "context_size": context_size,
        "persona": "Personal Assistant",
        "llm_endpoint": "http://localhost:8081/v1",
        "features": {
            "web_search": True,
            "deep_thinking": True,
            "code_execution": True,
            "memory": True
        }
    }

@app.post("/api/settings")
def update_settings(settings: dict):
    """Update AI settings (placeholder for future implementation)."""
    # For now, just acknowledge - actual implementation would save to config file
    return {"status": "success", "message": "Settings updated", "settings": settings}

@app.get("/api/profile")
def get_profile(db: Session = Depends(get_db)):
    """Get user profile information with real stats."""
    try:
        total_convs = db.query(DBConversation).count()
        total_msgs = db.query(DBMessage).count()
        
        mem_stats = memory_service.get_memory_stats()
        total_docs = mem_stats.get('total_memories', 0)
        
        return {
            "name": "Operator",
            "role": "System Administrator",
            "avatar": "OP",
            "stats": {
                "total_conversations": total_convs,
                "total_messages": total_msgs,
                "documents_indexed": total_docs
            },
            "preferences": {
                "theme": "system",
                "language": "en"
            }
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Profile Error: {str(e)}")

@app.get("/v1/learn/mastery/stream")
async def stream_mastery_learning(topic: str):
    """
    Stream the Mastery Learning process (Curriculum -> Research Loop).
    """
    async def event_generator():
        # Capture logs via callback
        queue = asyncio.Queue()
        
        async def log_callback(msg):
            # Sanitize newlines to prevent SSE corruption
            clean_msg = msg.replace('\n', ' ')
            await queue.put(clean_msg)
            
        # Start learning in background
        task = asyncio.create_task(learning_service.start_mastery_mode(topic, log_callback))
        
        last_yield_time = datetime.datetime.now()
        
        try:
            while not task.done() or not queue.empty():
                try:
                    # Check queue with non-blocking call
                    if not queue.empty():
                        msg = queue.get_nowait()
                        yield f"data: {msg}\n\n"
                        last_yield_time = datetime.datetime.now()
                    else:
                        # If queue empty, check task status
                        if task.done():
                             # Task finished, but check if it had an error
                             err = task.exception()
                             if err:
                                 print(f"DEBUG: Task Exception: {err}")
                                 yield f"data: ERROR: {str(err)}\n\n"
                             break
                        
                        # KEEP-ALIVE: Send comment every 2 seconds to prevent timeout
                        now = datetime.datetime.now()
                        if (now - last_yield_time).total_seconds() > 2.0:
                            yield ": keep-alive\n\n"
                            last_yield_time = now
                            
                        await asyncio.sleep(0.1)
                        
                except Exception as e:
                    print(f"DEBUG: Loop Error: {e}")
                    yield f"data: ERROR: Loop Error {e}\n\n"
                    break
        except Exception as e:
            print(f"DEBUG: Generator Error: {e}")
            yield f"data: ERROR: Gen Error {str(e)}\n\n"
            
        print("DEBUG: Stream Finished")
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.get("/api/learning/stats")
def get_learning_stats():
    """Get statistics about the self-learning system."""
    return learning_service.get_learning_stats()

@app.get("/v1/learn/auto/stream")
async def stream_auto_learning():
    """
    Stream the Autonomous Learning process.
    """
    async def event_generator():
        # Capture logs via callback
        queue = asyncio.Queue()
        
        async def log_callback(msg):
            await queue.put(msg)
            
        # Start learning in background
        task = asyncio.create_task(learning_service.active_research_auto(log_callback))
        
        try:
            while not task.done() or not queue.empty():
                try:
                    # Wait for new log or task completion
                    msg = await asyncio.wait_for(queue.get(), timeout=1.0)
                    yield f"data: {msg}\n\n"
                except asyncio.TimeoutError:
                    continue
            
            # Final check
            if task.exception():
                yield f"data: ERROR: {str(task.exception())}\n\n"
                
        except Exception as e:
            yield f"data: ERROR: {str(e)}\n\n"
            
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.get("/api/system/memory")
def get_memory_usage():
    """Get current RAM usage statistics for monitoring."""
    import psutil
    
    process = psutil.Process()
    mem_info = process.memory_info()
    
    # Get system-wide memory
    system_mem = psutil.virtual_memory()
    
    # Check if encoder/OCR are loaded
    encoder_loaded = memory_service._encoder is not None
    ocr_loaded = ingestion_service._ocr_reader is not None
    
    return {
        "process": {
            "rss_mb": round(mem_info.rss / 1024 / 1024, 2),
            "vms_mb": round(mem_info.vms / 1024 / 1024, 2),
        },
        "system": {
            "total_gb": round(system_mem.total / 1024 / 1024 / 1024, 2),
            "available_gb": round(system_mem.available / 1024 / 1024 / 1024, 2),
            "used_percent": system_mem.percent,
        },
        "models_loaded": {
            "sentence_transformer": encoder_loaded,
            "easyocr": ocr_loaded,
        },
        "tips": [] if not encoder_loaded and not ocr_loaded else [
            "Models auto-unload after inactivity to free RAM",
            "Call /api/system/unload to manually free RAM now"
        ]
    }

@app.post("/api/system/unload")
def unload_models():
    """Manually unload heavy models to free RAM immediately."""
    freed = []
    
    try:
        if memory_service._encoder is not None:
            memory_service.unload_encoder()
            freed.append("SentenceTransformer (~500MB)")
    except Exception as e:
        print(f"Error unloading encoder: {e}")
    
    try:
        if ingestion_service._ocr_reader is not None:
            ingestion_service.unload_ocr()
            freed.append("EasyOCR (~1-2GB)")
    except Exception as e:
        print(f"Error unloading OCR: {e}")
    
    # Force garbage collection
    import gc
    gc.collect()
    
    try:
        import torch
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            freed.append("PyTorch GPU cache")
    except:
        pass
    
    if freed:
        return {"status": "success", "freed": freed, "message": f"Freed: {', '.join(freed)}"}
    else:
        return {"status": "ok", "message": "No models were loaded to unload"}

@app.post("/api/research/start")
def trigger_research():
    """Manually trigger a curiosity research cycle."""
    import threading
    # Run in thread to not block API
    threading.Thread(target=research_service.perform_research_cycle).start()
    return {"status": "success", "message": "Research cycle initiated"}

@app.get("/api/skills")
def list_skills():
    """List all available dynamic skills."""
    return {"skills": skill_forge.get_skills_list()}

@app.post("/api/skills/create")
def create_skill(name: str, task: str):
    """Forge a new skill."""
    return {"result": skill_forge.create_skill(name, task)}

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload an image for visual analysis."""
    try:
        # Save to temp
        temp_dir = "temp"
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
        
        # Ensure filename is not None and safe
        import werkzeug.utils
        filename = werkzeug.utils.secure_filename(file.filename or "uploaded_file")
        file_path = os.path.join(temp_dir, filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # Analyze with Vision Service
        print(f"[UPLOAD] Analyzing {filename} with Vision Cortex...")
        description = visual_cortex.analyze_image(file_path)
        
        return {
            "filename": filename,
            "description": description,
            "path": file_path
        }
    except Exception as e:
        print(f"[UPLOAD ERROR] {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Chat Completions moved to routers/chat.py

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
