from database import engine, Base
from sqlalchemy import text

def reset_users():
    print("Dropping users table...")
    with engine.connect() as conn:
        conn.execute(text("DROP TABLE IF EXISTS users"))
        conn.commit()
    print("Users table dropped.")

if __name__ == "__main__":
    reset_users()
