from fastapi import FastAPI, File, UploadFile, Depends, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import shutil
from datetime import datetime
import logging

from database.database import get_db, create_tables
from database.models import JobDescription, Resume, ResumeEvaluation, ProcessingBatch
from services.resume_parser import ResumeParser
from services.scoring_engine import ResumeScorer
from api.schemas import (
    JobDescriptionCreate, JobDescriptionResponse,
    ResumeResponse, EvaluationResponse,
    BatchProcessRequest, BatchProcessResponse
)
from api.auth import get_current_user_dev as get_current_user
from core.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Automated Resume Relevance Check System",
    description="AI-powered resume evaluation system for Innomatics Research Labs",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
resume_parser = ResumeParser()
resume_scorer = ResumeScorer()

# Create upload directory
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.on_event("startup")
async def startup_event():
    """Initialize database tables on startup"""
    create_tables()
    logger.info("Application started successfully")

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Automated Resume Relevance Check System API",
        "status": "active",
        "version": "1.0.0"
    }

@app.post("/api/jobs", response_model=JobDescriptionResponse)
async def create_job(
    job: JobDescriptionCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create a new job description"""
    try:
        db_job = JobDescription(
            title=job.title,
            company=job.company,
            location=job.location,
            description=job.description,
            requirements=job.requirements,
            skills_required=job.skills_required,
            experience_min=job.experience_min,
            experience_max=job.experience_max,
            salary_min=job.salary_min,
            salary_max=job.salary_max,
            department=job.department,
            employment_type=job.employment_type
        )
        
        db.add(db_job)
        db.commit()
        db.refresh(db_job)
        
        logger.info(f"Created job posting: {db_job.title} (ID: {db_job.id})")
        return db_job
        
    except Exception as e:
        logger.error(f"Error creating job: {e}")
        raise HTTPException(status_code=500, detail="Failed to create job posting")

@app.get("/api/jobs", response_model=List[JobDescriptionResponse])
async def get_jobs(
    skip: int = 0,
    limit: int = 100,
    location: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get list of job descriptions"""
    try:
        query = db.query(JobDescription).filter(JobDescription.is_active == True)
        
        if location:
            query = query.filter(JobDescription.location == location)
        
        jobs = query.offset(skip).limit(limit).all()
        return jobs
        
    except Exception as e:
        logger.error(f"Error fetching jobs: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch job postings")

@app.post("/api/resumes/upload")
async def upload_resumes(
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Upload multiple resume files"""
    try:
        uploaded_resumes = []
        
        for file in files:
            # Validate file type
            if not file.filename.lower().endswith(('.pdf', '.doc', '.docx')):
                continue
            
            # Save file
            file_path = os.path.join(UPLOAD_DIR, f"{datetime.now().timestamp()}_{file.filename}")
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            # Create resume record
            db_resume = Resume(
                candidate_name="Unknown",  # Will be updated after parsing
                file_path=file_path,
                file_name=file.filename,
                file_type=file.filename.split('.')[-1].lower()
            )
            
            db.add(db_resume)
            db.commit()
            db.refresh(db_resume)
            
            uploaded_resumes.append({
                "id": db_resume.id,
                "filename": file.filename,
                "status": "uploaded"
            })
        
        logger.info(f"Uploaded {len(uploaded_resumes)} resumes")
        return {"uploaded_resumes": uploaded_resumes, "count": len(uploaded_resumes)}
        
    except Exception as e:
        logger.error(f"Error uploading resumes: {e}")
        raise HTTPException(status_code=500, detail="Failed to upload resumes")

@app.post("/api/resumes/{resume_id}/parse")
async def parse_resume(
    resume_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Parse a specific resume"""
    try:
        resume = db.query(Resume).filter(Resume.id == resume_id).first()
        if not resume:
            raise HTTPException(status_code=404, detail="Resume not found")
        
        # Add parsing task to background
        background_tasks.add_task(parse_resume_task, resume_id, db)
        
        return {"message": "Resume parsing started", "resume_id": resume_id}
        
    except Exception as e:
        logger.error(f"Error starting resume parsing: {e}")
        raise HTTPException(status_code=500, detail="Failed to start resume parsing")

@app.post("/api/evaluate", response_model=BatchProcessResponse)
async def evaluate_resumes(
    request: BatchProcessRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Start batch evaluation of resumes against a job description"""
    try:
        # Validate job exists
        job = db.query(JobDescription).filter(JobDescription.id == request.job_id).first()
        if not job:
            raise HTTPException(status_code=404, detail="Job description not found")
        
        # Validate resumes exist
        resumes = db.query(Resume).filter(Resume.id.in_(request.resume_ids)).all()
        if len(resumes) != len(request.resume_ids):
            raise HTTPException(status_code=404, detail="Some resumes not found")
        
        # Create processing batch
        batch = ProcessingBatch(
            job_id=request.job_id,
            batch_name=request.batch_name or f"Batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            total_resumes=len(request.resume_ids),
            status="pending"
        )
        
        db.add(batch)
        db.commit()
        db.refresh(batch)
        
        # Add evaluation task to background
        background_tasks.add_task(evaluate_batch_task, batch.id, request.resume_ids, db)
        
        logger.info(f"Started batch evaluation: {batch.batch_name} (ID: {batch.id})")
        return BatchProcessResponse(
            batch_id=batch.id,
            batch_name=batch.batch_name,
            status=batch.status,
            total_resumes=batch.total_resumes,
            message="Batch evaluation started successfully"
        )
        
    except Exception as e:
        logger.error(f"Error starting batch evaluation: {e}")
        raise HTTPException(status_code=500, detail="Failed to start batch evaluation")

@app.get("/api/results/{job_id}", response_model=List[EvaluationResponse])
async def get_evaluation_results(
    job_id: int,
    skip: int = 0,
    limit: int = 100,
    min_score: Optional[float] = None,
    fit_level: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get evaluation results for a job"""
    try:
        query = db.query(ResumeEvaluation).filter(ResumeEvaluation.job_id == job_id)
        
        if min_score is not None:
            query = query.filter(ResumeEvaluation.relevance_score >= min_score)
        
        if fit_level:
            query = query.filter(ResumeEvaluation.overall_fit == fit_level)
        
        evaluations = query.offset(skip).limit(limit).all()
        
        # Format response
        results = []
        for eval in evaluations:
            results.append(EvaluationResponse(
                id=eval.id,
                resume_id=eval.resume_id,
                job_id=eval.job_id,
                candidate_name=eval.resume.candidate_name,
                relevance_score=eval.relevance_score,
                skills_match_score=eval.skills_match_score,
                experience_match_score=eval.experience_match_score,
                education_match_score=eval.education_match_score,
                overall_fit=eval.overall_fit,
                matched_skills=eval.matched_skills,
                missing_skills=eval.missing_skills,
                recommendations=eval.recommendations,
                evaluation_date=eval.evaluation_date
            ))
        
        return results
        
    except Exception as e:
        logger.error(f"Error fetching evaluation results: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch evaluation results")

@app.get("/api/batch/{batch_id}/status")
async def get_batch_status(
    batch_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get status of a processing batch"""
    try:
        batch = db.query(ProcessingBatch).filter(ProcessingBatch.id == batch_id).first()
        if not batch:
            raise HTTPException(status_code=404, detail="Batch not found")
        
        return {
            "batch_id": batch.id,
            "batch_name": batch.batch_name,
            "status": batch.status,
            "total_resumes": batch.total_resumes,
            "processed_resumes": batch.processed_resumes,
            "failed_resumes": batch.failed_resumes,
            "high_fit_count": batch.high_fit_count,
            "medium_fit_count": batch.medium_fit_count,
            "low_fit_count": batch.low_fit_count,
            "average_score": batch.average_score,
            "started_at": batch.started_at,
            "completed_at": batch.completed_at
        }
        
    except Exception as e:
        logger.error(f"Error fetching batch status: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch batch status")

# Background task functions
async def parse_resume_task(resume_id: int, db: Session):
    """Background task to parse a resume"""
    try:
        resume = db.query(Resume).filter(Resume.id == resume_id).first()
        if not resume:
            return
        
        # Parse resume
        parsed_data = resume_parser.parse_resume(resume.file_path, resume.file_type)
        
        # Update resume record
        resume.candidate_name = parsed_data['candidate_name']
        resume.email = parsed_data['email']
        resume.phone = parsed_data['phone']
        resume.experience_years = parsed_data['experience_years']
        resume.skills = parsed_data['skills']
        resume.education = parsed_data['education']
        resume.certifications = parsed_data['certifications']
        resume.projects = parsed_data['projects']
        resume.summary = parsed_data['summary']
        resume.work_experience = parsed_data['work_experience']
        resume.is_parsed = parsed_data['is_parsed']
        resume.parsing_error = parsed_data['parsing_error']
        resume.processed_at = datetime.utcnow()
        
        db.commit()
        logger.info(f"Parsed resume {resume_id}: {resume.candidate_name}")
        
    except Exception as e:
        logger.error(f"Error parsing resume {resume_id}: {e}")

async def evaluate_batch_task(batch_id: int, resume_ids: List[int], db: Session):
    """Background task to evaluate a batch of resumes"""
    try:
        batch = db.query(ProcessingBatch).filter(ProcessingBatch.id == batch_id).first()
        if not batch:
            return
        
        # Update batch status
        batch.status = "processing"
        batch.started_at = datetime.utcnow()
        db.commit()
        
        job = db.query(JobDescription).filter(JobDescription.id == batch.job_id).first()
        
        total_score = 0
        fit_counts = {"High": 0, "Medium": 0, "Low": 0}
        
        for resume_id in resume_ids:
            try:
                resume = db.query(Resume).filter(Resume.id == resume_id).first()
                if not resume or not resume.is_parsed:
                    # Parse resume if not already parsed
                    await parse_resume_task(resume_id, db)
                    db.refresh(resume)
                
                # Prepare data for scoring
                resume_data = {
                    'candidate_name': resume.candidate_name,
                    'email': resume.email,
                    'phone': resume.phone,
                    'experience_years': resume.experience_years or 0,
                    'skills': resume.skills or [],
                    'education': resume.education or [],
                    'certifications': resume.certifications or [],
                    'projects': resume.projects or [],
                    'summary': resume.summary or '',
                    'work_experience': resume.work_experience or []
                }
                
                job_data = {
                    'title': job.title,
                    'description': job.description,
                    'requirements': job.requirements,
                    'skills_required': job.skills_required or [],
                    'experience_min': job.experience_min or 0,
                    'experience_max': job.experience_max or 10
                }
                
                # Score resume
                scoring_result = resume_scorer.score_resume(resume_data, job_data)
                
                # Create evaluation record
                evaluation = ResumeEvaluation(
                    resume_id=resume_id,
                    job_id=batch.job_id,
                    relevance_score=scoring_result.relevance_score,
                    skills_match_score=scoring_result.skills_match_score,
                    experience_match_score=scoring_result.experience_match_score,
                    education_match_score=scoring_result.education_match_score,
                    overall_fit=scoring_result.overall_fit,
                    matched_skills=scoring_result.matched_skills,
                    missing_skills=scoring_result.missing_skills,
                    missing_certifications=scoring_result.missing_certifications,
                    missing_projects=scoring_result.missing_projects,
                    strengths=scoring_result.strengths,
                    weaknesses=scoring_result.weaknesses,
                    recommendations=scoring_result.recommendations
                )
                
                db.add(evaluation)
                
                # Update statistics
                total_score += scoring_result.relevance_score
                fit_counts[scoring_result.overall_fit] += 1
                batch.processed_resumes += 1
                
            except Exception as e:
                logger.error(f"Error evaluating resume {resume_id}: {e}")
                batch.failed_resumes += 1
        
        # Update batch completion
        batch.status = "completed"
        batch.completed_at = datetime.utcnow()
        batch.high_fit_count = fit_counts["High"]
        batch.medium_fit_count = fit_counts["Medium"]
        batch.low_fit_count = fit_counts["Low"]
        batch.average_score = total_score / max(batch.processed_resumes, 1)
        
        db.commit()
        logger.info(f"Completed batch evaluation {batch_id}")
        
    except Exception as e:
        logger.error(f"Error in batch evaluation {batch_id}: {e}")
        batch.status = "failed"
        db.commit()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
