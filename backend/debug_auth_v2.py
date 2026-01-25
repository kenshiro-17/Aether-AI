import sys
import os

# Mimic main.py execution environment
sys.path.append(os.getcwd())

# Import exactly as main.py and routers do
from database import Base, DATABASE_URL, SessionLocal
import models
import auth_service

print("Testing Password Hashing...")
try:
    pwd = auth_service.get_password_hash("password123")
    print(f"Hash created: {pwd[:10]}...")
except Exception as e:
    print(f"Hashing failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\nTesting User Creation...")
db = SessionLocal()
try:
    user = models.User(
        username="debug_user_v2",
        email="debug_v2@test.com",
        hashed_password=pwd,
        full_name="Debug Local V2",
        avatar_url="http://test.com/avatar.svg"
    )
    # List all users
    print("\n--- Listing All Users ---")
    users = db.query(models.User).all()
    for u in users:
        print(f"User: '{u.username}' (Created: {u.created_at})")
        if u.username == "debug_user_v2":
            # Verify password for debug user
            is_valid = auth_service.verify_password("password123", u.hashed_password)
            print(f" -> Debug User Password Verify ('password123'): {is_valid}")
    
    print(f"Total Users: {len(users)}")

except Exception as e:
    print(f"Database Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()
