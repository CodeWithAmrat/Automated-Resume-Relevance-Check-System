from sqlalchemy import Column, Integer, String, Text, Float, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class JobDescription(Base):
    __tablename__ = "job_descriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    company = Column(String(255), nullable=False)
    location = Column(String(100), nullable=False)  # Hyderabad, Bangalore, Pune, Delhi NCR
    description = Column(Text, nullable=False)
    requirements = Column(Text, nullable=False)
    skills_required = Column(JSON)  # List of required skills
    experience_min = Column(Integer, default=0)
    experience_max = Column(Integer, default=10)
    salary_min = Column(Float, nullable=True)
    salary_max = Column(Float, nullable=True)
    department = Column(String(100), nullable=True)
    employment_type = Column(String(50), default="Full-time")  # Full-time, Part-time, Contract
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    evaluations = relationship("ResumeEvaluation", back_populates="job_description")

class Resume(Base):
    __tablename__ = "resumes"
    
    id = Column(Integer, primary_key=True, index=True)
    candidate_name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=True)
    phone = Column(String(20), nullable=True)
    file_path = Column(String(500), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_type = Column(String(10), nullable=False)  # pdf, doc, docx
    
    # Extracted Information
    experience_years = Column(Float, nullable=True)
    education = Column(JSON)  # List of education details
    skills = Column(JSON)  # List of extracted skills
    certifications = Column(JSON)  # List of certifications
    projects = Column(JSON)  # List of projects
    work_experience = Column(JSON)  # List of work experiences
    summary = Column(Text, nullable=True)
    
    # Processing Status
    is_parsed = Column(Boolean, default=False)
    parsing_error = Column(Text, nullable=True)
    
    # Metadata
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime, nullable=True)
    
    # Relationships
    evaluations = relationship("ResumeEvaluation", back_populates="resume")

class ResumeEvaluation(Base):
    __tablename__ = "resume_evaluations"
    
    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=False)
    job_id = Column(Integer, ForeignKey("job_descriptions.id"), nullable=False)
    
    # Scoring Results
    relevance_score = Column(Float, nullable=False)  # 0-100
    skills_match_score = Column(Float, nullable=False)  # 0-100
    experience_match_score = Column(Float, nullable=False)  # 0-100
    education_match_score = Column(Float, nullable=False)  # 0-100
    overall_fit = Column(String(20), nullable=False)  # High, Medium, Low
    
    # Analysis Results
    matched_skills = Column(JSON)  # Skills that match
    missing_skills = Column(JSON)  # Skills candidate lacks
    missing_certifications = Column(JSON)  # Certifications candidate lacks
    missing_projects = Column(JSON)  # Project types candidate lacks
    
    # Feedback
    strengths = Column(JSON)  # List of candidate strengths
    weaknesses = Column(JSON)  # List of areas for improvement
    recommendations = Column(Text)  # Personalized feedback
    
    # Processing Info
    evaluation_date = Column(DateTime, default=datetime.utcnow)
    processing_time_seconds = Column(Float, nullable=True)
    
    # Relationships
    resume = relationship("Resume", back_populates="evaluations")
    job_description = relationship("JobDescription", back_populates="evaluations")

class ProcessingBatch(Base):
    __tablename__ = "processing_batches"
    
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("job_descriptions.id"), nullable=False)
    batch_name = Column(String(255), nullable=False)
    total_resumes = Column(Integer, nullable=False)
    processed_resumes = Column(Integer, default=0)
    failed_resumes = Column(Integer, default=0)
    status = Column(String(20), default="pending")  # pending, processing, completed, failed
    
    # Results Summary
    high_fit_count = Column(Integer, default=0)
    medium_fit_count = Column(Integer, default=0)
    low_fit_count = Column(Integer, default=0)
    average_score = Column(Float, nullable=True)
    
    # Timing
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(String(50), default="recruiter")  # admin, recruiter, hr
    location = Column(String(100), nullable=True)  # Hyderabad, Bangalore, Pune, Delhi NCR
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)

class SystemMetrics(Base):
    __tablename__ = "system_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, default=datetime.utcnow)
    total_resumes_processed = Column(Integer, default=0)
    total_jobs_posted = Column(Integer, default=0)
    average_processing_time = Column(Float, nullable=True)
    system_accuracy = Column(Float, nullable=True)
    active_users = Column(Integer, default=0)
    location = Column(String(100), nullable=True)
