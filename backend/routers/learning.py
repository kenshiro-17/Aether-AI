from fastapi import APIRouter, BackgroundTasks, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import asyncio
import json
from learning_service import learning_service

router = APIRouter()

class ResearchRequest(BaseModel):
    topic: str

@router.post("/learn/start")
async def start_learning(request: ResearchRequest, background_tasks: BackgroundTasks):
    """Start a background research task."""
    # In a real app, we'd use a queue. For now, we'll trigger it via the stream/generator pattern
    # Actually, with SSE, the client connects to the stream, and THEN we start the logic inside the stream generator
    return {"status": "ready", "message": "Connect to /learn/stream to start"}


async def _stream_research(task_coro):
    """Helper to stream logs from a research task."""
    queue = asyncio.Queue()
    
    async def log_callback(msg):
        await queue.put(msg)
        
    task = asyncio.create_task(task_coro(log_callback))
    
    yield "data: Connected to Research Module...\n\n"
    
    while not task.done() or not queue.empty():
        try:
            msg = await asyncio.wait_for(queue.get(), timeout=0.1)
            yield f"data: {msg}\n\n"
        except asyncio.TimeoutError:
            continue
            
    yield "data: [DONE]\n\n"

@router.get("/learn/stream")
async def stream_learning(topic: str):
    """Streams manual research logs."""
    return StreamingResponse(
        _stream_research(lambda cb: learning_service.active_research(topic, cb)), 
        media_type="text/event-stream"
    )

@router.get("/learn/auto/stream")
async def stream_auto_learning():
    """Streams autonomous research logs."""
    return StreamingResponse(
        _stream_research(lambda cb: learning_service.active_research_auto(cb)), 
        media_type="text/event-stream"
    )

@router.get("/learn/automate/stream")
async def stream_automation_task(topic: str, level: str = "PHD"):
    """
    Streams a goal-oriented Deep Automation Task (e.g. Master Rust - PhD Level).
    Iterates through a generated syllabus.
    """
    return StreamingResponse(
        _stream_research(lambda cb: learning_service.start_automation_task(topic, level, log_callback=cb)), 
        media_type="text/event-stream"
    )
