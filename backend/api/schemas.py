from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict, Any
from datetime import datetime

# Job Description Schemas
class JobDescriptionBase(BaseModel):
    title: str
    company: str
    location: str
    description: str
    requirements: str
    skills_required: Optional[List[str]] = []
    experience_min: Optional[int] = 0
    experience_max: Optional[int] = 10
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    department: Optional[str] = None
    employment_type: Optional[str] = "Full-time"

class JobDescriptionCreate(JobDescriptionBase):
    pass

class JobDescriptionResponse(JobDescriptionBase):
    id: int
    created_at: datetime
    updated_at: datetime
    is_active: bool

    class Config:
        from_attributes = True

# Resume Schemas
class ResumeBase(BaseModel):
    candidate_name: str
    email: Optional[str] = None
    phone: Optional[str] = None

class ResumeResponse(ResumeBase):
    id: int
    file_name: str
    file_type: str
    experience_years: Optional[float] = None
    skills: Optional[List[str]] = []
    education: Optional[List[Dict[str, Any]]] = []
    certifications: Optional[List[str]] = []
    projects: Optional[List[Dict[str, Any]]] = []
    summary: Optional[str] = None
    is_parsed: bool
    uploaded_at: datetime
    processed_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Evaluation Schemas
class EvaluationResponse(BaseModel):
    id: int
    resume_id: int
    job_id: int
    candidate_name: str
    relevance_score: float
    skills_match_score: float
    experience_match_score: float
    education_match_score: float
    overall_fit: str
    matched_skills: List[str]
    missing_skills: List[str]
    recommendations: str
    evaluation_date: datetime

    class Config:
        from_attributes = True

# Batch Processing Schemas
class BatchProcessRequest(BaseModel):
    job_id: int
    resume_ids: List[int]
    batch_name: Optional[str] = None

class BatchProcessResponse(BaseModel):
    batch_id: int
    batch_name: str
    status: str
    total_resumes: int
    message: str

# User Schemas
class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: str
    role: Optional[str] = "recruiter"
    location: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True

# Authentication Schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
