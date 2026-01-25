from database import SessionLocal
from models import Conversation, Message
import os

def check_stats():
    print(f"CWD: {os.getcwd()}")
    db = SessionLocal()
    try:
        conv_count = db.query(Conversation).count()
        msg_count = db.query(Message).count()
        print(f"STATS_RESULT: Conversations={conv_count}, Messages={msg_count}")
    except Exception as e:
        print(f"ERROR: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_stats()
