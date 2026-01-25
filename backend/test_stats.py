from database import SessionLocal
from models import Conversation, Message
from memory_service import memory_service

def check_stats():
    db = SessionLocal()
    try:
        conv_count = db.query(Conversation).count()
        msg_count = db.query(Message).count()
        print(f"DEBUG: Conversations in DB: {conv_count}")
        print(f"DEBUG: Messages in DB: {msg_count}")
        
        mem_stats = memory_service.get_memory_stats()
        print(f"DEBUG: Memory Stats: {mem_stats}")
    except Exception as e:
        print(f"ERROR: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_stats()
