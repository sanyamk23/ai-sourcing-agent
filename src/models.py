from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime
from enum import Enum

class JobStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class JobDescription(BaseModel):
    title: str
    description: str
    required_skills: List[str] = []
    experience_years: Optional[int] = None
    location: Optional[str] = None
    salary_range: Optional[Dict[str, float]] = None

class Candidate(BaseModel):
    id: str
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    current_title: Optional[str] = None
    skills: List[str] = []
    experience_years: Optional[int] = None
    education: Optional[str] = None
    location: Optional[str] = None
    profile_url: str
    source_portal: str
    summary: Optional[str] = None
    
class RankedCandidate(BaseModel):
    candidate: Candidate
    match_score: float = Field(ge=0.0, le=1.0)
    match_breakdown: Dict[str, float]
    reasoning: str

class Job(BaseModel):
    id: str
    description: JobDescription
    status: JobStatus
    created_at: datetime
    candidates: List[RankedCandidate] = []
