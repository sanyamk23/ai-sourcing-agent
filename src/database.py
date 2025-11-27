from sqlalchemy import create_engine, Column, String, Integer, Float, JSON, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import yaml

Base = declarative_base()

class CandidateDB(Base):
    __tablename__ = 'candidates'
    
    id = Column(String, primary_key=True)
    name = Column(String)
    email = Column(String)
    phone = Column(String)
    current_title = Column(String)
    skills = Column(JSON)
    experience_years = Column(Integer)
    education = Column(String)
    location = Column(String)
    profile_url = Column(String)
    source_portal = Column(String)
    summary = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

class JobDB(Base):
    __tablename__ = 'jobs'
    
    id = Column(String, primary_key=True)
    title = Column(String)
    description = Column(Text)
    required_skills = Column(JSON)
    experience_years = Column(Integer)
    location = Column(String)
    status = Column(String)
    candidates = Column(JSON)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

# Load config
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

# Create engine
engine = create_engine(config['database']['url'])
Base.metadata.create_all(engine)

# Create session factory
SessionLocal = sessionmaker(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
