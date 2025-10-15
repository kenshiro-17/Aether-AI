
from sqlalchemy import Column, String, DateTime, Text, ForeignKey, Float, Integer
from database import Base
import uuid
import datetime

def generate_uuid():
    return str(uuid.uuid4())

def get_utc_now():
    return datetime.datetime.now(datetime.timezone.utc)

class Conversation(Base):
    __tablename__ = "conversations"
    id = Column(String, primary_key=True, default=generate_uuid)
    title = Column(String)
    created_at = Column(DateTime, default=get_utc_now)
    updated_at = Column(DateTime, default=get_utc_now)

class Message(Base):
    __tablename__ = "messages"
    id = Column(String, primary_key=True, default=generate_uuid)
    conversation_id = Column(String, ForeignKey("conversations.id"))
    role = Column(String)
    content = Column(Text)
    created_at = Column(DateTime, default=get_utc_now)

class PersonalityProfile(Base):
    __tablename__ = "personality_profile"
    id = Column(Integer, primary_key=True, autoincrement=True)
    # The Big Five Traits (0.0 to 1.0)
    openness = Column(Float, default=0.5)
    conscientiousness = Column(Float, default=0.5)
    extraversion = Column(Float, default=0.5)
    agreeableness = Column(Float, default=0.5)
    neuroticism = Column(Float, default=0.5)
    
    # Emotional State
    current_mood = Column(String, default="Neutral")
    empathy_coefficient = Column(Float, default=0.5)
    
    updated_at = Column(DateTime, default=get_utc_now)

class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, default=generate_uuid)
    email = Column(String, unique=True, index=True, nullable=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String, nullable=True)
    full_name = Column(String, nullable=True)
    avatar_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=get_utc_now)
    last_login = Column(DateTime, nullable=True)
