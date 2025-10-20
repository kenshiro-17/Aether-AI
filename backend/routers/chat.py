from fastapi import APIRouter, Depends, HTTPException, Request, BackgroundTasks
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from database import get_db
from pydantic import BaseModel
from typing import List, Optional, Any
import uuid
import datetime
import json
import os
import asyncio
from openai import AsyncOpenAI

# Service Imports
from memory_service import memory_service
from learning_service import learning_service
from personality_service import personality_service
from cortex import web_search, run_python, read_url, TOOLS_SCHEMA
from cortex.visual import visual_cortex 

# Models imported from backend.models
from models import Conversation, Message

# API Router
router = APIRouter()

# --- Pydantic Models ---

class ChatMessage(BaseModel):
    role: str
    content: str
    created_at: Optional[datetime.datetime] = None

class ChatRequest(BaseModel):
    messages: list[ChatMessage]
    conversation_id: Optional[str] = None
    enable_search: bool = False
    enable_thinking: bool = False

class ConversationResponse(BaseModel):
    id: str
    title: str
    updated_at: datetime.datetime
    messages: Optional[List[ChatMessage]] = []

# --- OpenAI Client ---
client = AsyncOpenAI(
    base_url="http://127.0.0.1:8081/v1",
    api_key="ollama"
)

# --- History Endpoints ---

@router.get("/history/conversations", response_model=List[ConversationResponse])
def get_conversations(db: Session = Depends(get_db)):
    return db.query(Conversation).order_by(Conversation.updated_at.desc()).limit(20).all()

@router.get("/history/conversation/{conversation_id}", response_model=List[ChatMessage])
def get_messages(conversation_id: str, db: Session = Depends(get_db)):
    msgs = db.query(Message).filter(Message.conversation_id == conversation_id).order_by(Message.created_at.asc()).all()
    # Convert DB model to Pydantic
    return [ChatMessage(role=m.role, content=m.content, created_at=m.created_at) for m in msgs]

@router.post("/history/conversation", response_model=ConversationResponse)
def create_conversation(title: str, db: Session = Depends(get_db)):
    conv = Conversation(title=title)
    db.add(conv)
    db.commit()
    db.refresh(conv)
    return ConversationResponse(id=conv.id, title=conv.title, updated_at=conv.updated_at)

@router.delete("/history/conversation/{conversation_id}")
def delete_conversation(conversation_id: str, db: Session = Depends(get_db)):
    conv = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    db.query(Message).filter(Message.conversation_id == conversation_id).delete()
    db.delete(conv)
    db.commit()
    return {"status": "success", "id": conversation_id}

# --- Chat Completion Endpoint (Streaming) ---

@router.post("/v1/chat/completions")
async def chat_completions(request: ChatRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):

    # 0. Conversation Init
    if request.conversation_id:
        conversation = db.query(Conversation).filter(Conversation.id == request.conversation_id).first()
        if not conversation:
            conversation = Conversation(id=request.conversation_id, title="New Chat")
            db.add(conversation)
            db.commit()
            db.refresh(conversation)
    else:
        # Create new conversation with title based on first query
        initial_title = request.messages[-1].content[:30] + "..." if request.messages else "New Chat"
        conversation = Conversation(title=initial_title)
        db.add(conversation)
        db.commit()
        db.refresh(conversation)

    # Store conversation ID immediately
    conversation_id = conversation.id
    user_query = request.messages[-1].content
    
    # Save User Message
    db.add(Message(conversation_id=conversation_id, role="user", content=user_query))
    db.commit()

    # 1. RAG Search - Include both documents and learned knowledge
    print(f"Searching memory for: {user_query}")
    context_str = ""
    try:
        # Retrieve top 5 items
        relevant_context = memory_service.search_memory(user_query, limit=5)
        
        if relevant_context:
            print(f"[MEMORY] Found {len(relevant_context)} relevant items.")
            documents = [item for item in relevant_context if item.get('type') not in ['fact', 'conversation_fact', 'code_example', 'definition', 'user_preference']]
            learned_items = [item for item in relevant_context if item.get('type') in ['fact', 'conversation_fact', 'code_example', 'definition', 'user_preference']]
            
            context_parts = []
            
            # Add learned knowledge first (prioritized)
            if learned_items:
                context_parts.append("=== LEARNED KNOWLEDGE ===")
                for item in learned_items[:3]:
                    item_type = item.get('type', 'knowledge').upper()
                    context_parts.append(f"[{item_type}] {item['content']}")
                context_parts.append("")
            
            # Add document chunks
            if documents:
                context_parts.append("=== DOCUMENT KNOWLEDGE ===")
                for item in documents[:3]:
                    filename = item.get('filename', 'unknown')
                    context_parts.append(f"[{filename}] {item['content']}")
            
            context_str = "\n".join(context_parts)
            
    except Exception as e:
        print(f"Warning: Memory search failed: {e}")

    # 2. Get Dynamic System Prompt
    system_prompt = personality_service.get_system_prompt(db, user_query)
    current_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    async def generate_stream():
        try:
            full_response = ""
            context_block = ""
            
            # 1. Yield Conversation ID
            yield f'data: {{"conversation_id": "{conversation_id}"}}\n\n'
            
            # 2. Perform Web Search / Thinking (Inside Generator)
            if request.enable_search:
                try:
                    # 0. Smart Decision: Do we actually need to search?
                    # We ask the model quickly (non-streaming)
                    decision_messages = [
                        {"role": "system", "content": "You are a Search Router. Analyze the user query. Does it require external real-time information, news, or specific facts? Respond 'YES' if search is needed, 'NO' if you can answer from general knowledge. \n\nCRITICAL: Respond 'NO' for creative requests (e.g., 'write a story', 'poem', 'code', 'draft'). Respond 'NO' for greetings. Respond with ONLY 'YES' or 'NO'."},
                        {"role": "user", "content": user_query}
                    ]
                    
                    decision_msg = json.dumps({"status": "Thinking..."})
                    yield f'data: {decision_msg}\n\n'
                    
                    decision = await client.chat.completions.create(
                        model="local-model",
                        messages=decision_messages,
                        max_tokens=10,
                        temperature=0.0
                    )
                    decision_text = decision.choices[0].message.content.strip().upper()
                    print(f"DEBUG: Search Decision: {decision_text}")
                    
                    if "YES" in decision_text:
                        # Proceed with Search
                        search_query = user_query
                        # Follow-up detection
                        follow_up_patterns = ["tell me more", "explain", "detail", "continue", "why", "how"]
                        query_lower = user_query.lower().strip()
                        if len(query_lower.split()) < 6 and any(query_lower.startswith(p) for p in follow_up_patterns) and len(request.messages) > 1:
                             prev_messages = [m for m in request.messages[:-1] if m.role == "user"]
                             if prev_messages:
                                 search_query = f"{prev_messages[-1].content} {user_query}"
                        
                        status_msg = json.dumps({"status": f"Searching: {search_query}..."})
                        yield f'data: {status_msg}\n\n'
                        
                        # Run sync search in thread pool
                        search_results = await asyncio.to_thread(web_search, search_query)
                        
                        search_context = f"\n\n--- REAL-TIME WEB SEARCH RESULTS ---\n{search_results}\n------------------------------------\n"
                        context_block += search_context
                        
                        done_msg = json.dumps({"status": "Analyzing results..."})
                        yield f'data: {done_msg}\n\n'
                    else:
                        skip_msg = json.dumps({"status": "Thinking..."})
                        yield f'data: {skip_msg}\n\n'
                         
                except Exception as e:
                    import traceback
                    traceback.print_exc()
                    print(f"Web Search Failed: {e}")
                    err_msg = json.dumps({"status": "Search failed (continuing)"})
                    yield f'data: {err_msg}\n\n'
    
            # 3. Add Memory Context (Pre-calculated)
            if context_str:
                context_block += f"\n{context_str}"
                
            # 4. Construct Final Prompt with Dynamic Context
            final_system_prompt_str = system_prompt
            
            if context_block:
                 final_user_overlay = (
                    f"User Query: {request.messages[-1].content}\n\n"
                    f"### REFERENCE DATA (INTEL)\n[SYSTEM_CLOCK]: {current_date}\n{context_block}\n### END INTEL\n\n"
                    "INSTRUCTIONS:\n"
                    "1. Use the REFERENCE DATA above if relevant.\n"
                    "2. If search results are incomplete, admit it or suggest reading a URL.\n"
                )
            else:
                final_user_overlay = request.messages[-1].content
    
            # Re-assemble messages for LLM
            llm_messages = [{"role": "system", "content": final_system_prompt_str}]
            if len(request.messages) > 1:
                llm_messages.extend([{"role": m.role, "content": m.content} for m in request.messages[:-1]])
            llm_messages.append({"role": "user", "content": final_user_overlay})
    
            try:
                # LLM Generation
                stream = await client.chat.completions.create(
                    model="local-model",
                    messages=llm_messages,
                    max_tokens=16384,
                    temperature=0.3,
                    stream=True
                )
                
                async for chunk in stream:
                    if chunk.choices[0].delta.content:
                        content = chunk.choices[0].delta.content
                        full_response += content
                        # Sanitize ChatML
                        if "<|im_start|>" not in content and "<|im_end|>" not in content:
                            yield f'data: {json.dumps({"content": content})}\n\n'
                        
                yield "data: [DONE]\n\n"
                
                # Background tasks after stream finishes
                if full_response.strip():
                    await save_message_async(conversation_id, "assistant", full_response)
                    asyncio.create_task(learning_service.learn_from_conversation(user_query, full_response))
                    asyncio.create_task(personality_service.evolve_personality_async(conversation_id, user_query, full_response))
    
            except Exception as e:
                import traceback
                traceback.print_exc()
                yield f'data: {{"error": "LLM Error: {str(e)}"}}\n\n'
                
        except Exception as e:
            import traceback
            traceback.print_exc()
            yield f'data: {{"error": "Generator Crash: {str(e)}"}}\n\n'

    return StreamingResponse(generate_stream(), media_type="text/event-stream")

# Helper for async DB save (since we can't easily reuse the dependency session in the generator)
async def save_message_async(conversation_id, role, content):
    # This is a bit hacky, better to use the specific service or a fresh session
    # For now, we will trust that the session logic in services is robust or just skip implicit saving 
    # if it complicates things. But we need to save.
    
    # We'll use a functional approach with a new session
    # Re-import to avoid circular issues or scope problems
    from database import SessionLocal
    db = SessionLocal()
    try:
        db.add(Message(conversation_id=conversation_id, role=role, content=content))
        db.commit()
    except Exception as e:
        print(f"Error saving message: {e}")
    finally:
        db.close()
