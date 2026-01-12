import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.database import Base, DATABASE_URL
from backend import models
from backend import auth_service

# Setup Test DB (Memory) to avoid messing with real one, or use real one?
# Let's use real one to ensure environment matches
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

print("Testing Password Hashing...")
try:
    pwd = auth_service.get_password_hash("password123")
    print(f"Hash created: {pwd[:10]}...")
except Exception as e:
    print(f"Hashing failed: {e}")
    import traceback
    traceback.print_exc()

print("\nTesting User Creation...")
try:
    user = models.User(
        username="debug_user_local",
        email="debug_local@test.com",
        hashed_password=pwd,
        full_name="Debug Local",
        avatar_url="http://test.com/avatar.svg"
    )
    # Check if user exists first to avoid unique constraint error
    existing = db.query(models.User).filter(models.User.username == "debug_user_local").first()
    if existing:
        print("User already exists, skipping insert.")
    else:
        db.add(user)
        db.commit()
        print("User created successfully!")
except Exception as e:
    print(f"User creation failed: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()
