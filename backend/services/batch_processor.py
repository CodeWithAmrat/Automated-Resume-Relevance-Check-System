import asyncio
import logging
from typing import List, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

from database.models import ProcessingBatch, Resume, JobDescription, ResumeEvaluation
from services.resume_parser import ResumeParser
from services.scoring_engine import ResumeScorer

logger = logging.getLogger(__name__)

class BatchProcessor:
    def __init__(self, max_workers: int = 5):
        self.max_workers = max_workers
        self.resume_parser = ResumeParser()
        self.resume_scorer = ResumeScorer()
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
    
    async def process_batch(self, batch_id: int, db: Session) -> bool:
        """Process a batch of resumes asynchronously"""
        try:
            # Get batch details
            batch = db.query(ProcessingBatch).filter(ProcessingBatch.id == batch_id).first()
            if not batch:
                logger.error(f"Batch {batch_id} not found")
                return False
            
            # Update batch status
            batch.status = "processing"
            batch.started_at = datetime.utcnow()
            db.commit()
            
            # Get job description
            job = db.query(JobDescription).filter(JobDescription.id == batch.job_id).first()
            if not job:
                logger.error(f"Job {batch.job_id} not found")
                batch.status = "failed"
                db.commit()
                return False
            
            # Get resumes to process
            resumes = db.query(Resume).join(ResumeEvaluation, Resume.id == ResumeEvaluation.resume_id, isouter=True)\
                .filter(ResumeEvaluation.job_id == batch.job_id)\
                .limit(batch.total_resumes).all()
            
            if not resumes:
                logger.error(f"No resumes found for batch {batch_id}")
                batch.status = "failed"
                db.commit()
                return False
            
            logger.info(f"Starting batch processing for {len(resumes)} resumes")
            
            # Process resumes in parallel
            results = await self._process_resumes_parallel(resumes, job, batch, db)
            
            # Update batch completion status
            successful_count = sum(1 for result in results if result['success'])
            failed_count = len(results) - successful_count
            
            batch.processed_resumes = successful_count
            batch.failed_resumes = failed_count
            batch.status = "completed" if failed_count == 0 else "completed_with_errors"
            batch.completed_at = datetime.utcnow()
            
            # Calculate summary statistics
            if successful_count > 0:
                evaluations = db.query(ResumeEvaluation).filter(
                    ResumeEvaluation.job_id == batch.job_id
                ).all()
                
                total_score = sum(eval.relevance_score for eval in evaluations)
                batch.average_score = total_score / len(evaluations)
                
                batch.high_fit_count = sum(1 for eval in evaluations if eval.overall_fit == "High")
                batch.medium_fit_count = sum(1 for eval in evaluations if eval.overall_fit == "Medium")
                batch.low_fit_count = sum(1 for eval in evaluations if eval.overall_fit == "Low")
            
            db.commit()
            logger.info(f"Batch {batch_id} completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error processing batch {batch_id}: {e}")
            if batch:
                batch.status = "failed"
                batch.completed_at = datetime.utcnow()
                db.commit()
            return False
    
    async def _process_resumes_parallel(self, resumes: List[Resume], job: JobDescription, 
                                      batch: ProcessingBatch, db: Session) -> List[Dict[str, Any]]:
        """Process multiple resumes in parallel"""
        loop = asyncio.get_event_loop()
        
        # Create tasks for parallel processing
        tasks = []
        for resume in resumes:
            task = loop.run_in_executor(
                self.executor,
                self._process_single_resume,
                resume, job, batch.id, db
            )
            tasks.append(task)
        
        # Wait for all tasks to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results and handle exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Error processing resume {resumes[i].id}: {result}")
                processed_results.append({
                    'resume_id': resumes[i].id,
                    'success': False,
                    'error': str(result)
                })
            else:
                processed_results.append(result)
        
        return processed_results
    
    def _process_single_resume(self, resume: Resume, job: JobDescription, 
                             batch_id: int, db: Session) -> Dict[str, Any]:
        """Process a single resume"""
        start_time = time.time()
        
        try:
            # Parse resume if not already parsed
            if not resume.is_parsed:
                parsed_data = self.resume_parser.parse_resume(resume.file_path, resume.file_type)
                
                # Update resume with parsed data
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
            scoring_result = self.resume_scorer.score_resume(resume_data, job_data)
            
            # Create evaluation record
            evaluation = ResumeEvaluation(
                resume_id=resume.id,
                job_id=job.id,
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
                recommendations=scoring_result.recommendations,
                processing_time_seconds=time.time() - start_time
            )
            
            db.add(evaluation)
            db.commit()
            
            logger.info(f"Successfully processed resume {resume.id} for job {job.id}")
            
            return {
                'resume_id': resume.id,
                'success': True,
                'score': scoring_result.relevance_score,
                'fit': scoring_result.overall_fit,
                'processing_time': time.time() - start_time
            }
            
        except Exception as e:
            logger.error(f"Error processing resume {resume.id}: {e}")
            db.rollback()
            return {
                'resume_id': resume.id,
                'success': False,
                'error': str(e),
                'processing_time': time.time() - start_time
            }
    
    def get_batch_status(self, batch_id: int, db: Session) -> Dict[str, Any]:
        """Get current status of a batch"""
        batch = db.query(ProcessingBatch).filter(ProcessingBatch.id == batch_id).first()
        if not batch:
            return None
        
        return {
            'id': batch.id,
            'batch_name': batch.batch_name,
            'status': batch.status,
            'total_resumes': batch.total_resumes,
            'processed_resumes': batch.processed_resumes,
            'failed_resumes': batch.failed_resumes,
            'high_fit_count': batch.high_fit_count,
            'medium_fit_count': batch.medium_fit_count,
            'low_fit_count': batch.low_fit_count,
            'average_score': batch.average_score,
            'started_at': batch.started_at,
            'completed_at': batch.completed_at,
            'created_at': batch.created_at
        }
    
    def cancel_batch(self, batch_id: int, db: Session) -> bool:
        """Cancel a running batch"""
        try:
            batch = db.query(ProcessingBatch).filter(ProcessingBatch.id == batch_id).first()
            if not batch:
                return False
            
            if batch.status == "processing":
                batch.status = "cancelled"
                batch.completed_at = datetime.utcnow()
                db.commit()
                logger.info(f"Batch {batch_id} cancelled")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error cancelling batch {batch_id}: {e}")
            return False
    
    def cleanup_old_batches(self, db: Session, days_old: int = 30) -> int:
        """Clean up old completed batches"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_old)
            
            old_batches = db.query(ProcessingBatch).filter(
                ProcessingBatch.completed_at < cutoff_date,
                ProcessingBatch.status.in_(["completed", "failed", "cancelled"])
            ).all()
            
            count = len(old_batches)
            for batch in old_batches:
                db.delete(batch)
            
            db.commit()
            logger.info(f"Cleaned up {count} old batches")
            return count
            
        except Exception as e:
            logger.error(f"Error cleaning up old batches: {e}")
            return 0
    
    def get_processing_statistics(self, db: Session) -> Dict[str, Any]:
        """Get overall processing statistics"""
        try:
            total_batches = db.query(ProcessingBatch).count()
            completed_batches = db.query(ProcessingBatch).filter(
                ProcessingBatch.status == "completed"
            ).count()
            
            processing_batches = db.query(ProcessingBatch).filter(
                ProcessingBatch.status == "processing"
            ).count()
            
            failed_batches = db.query(ProcessingBatch).filter(
                ProcessingBatch.status == "failed"
            ).count()
            
            # Average processing time
            completed = db.query(ProcessingBatch).filter(
                ProcessingBatch.status == "completed",
                ProcessingBatch.started_at.isnot(None),
                ProcessingBatch.completed_at.isnot(None)
            ).all()
            
            avg_processing_time = 0
            if completed:
                total_time = sum(
                    (batch.completed_at - batch.started_at).total_seconds()
                    for batch in completed
                )
                avg_processing_time = total_time / len(completed)
            
            return {
                'total_batches': total_batches,
                'completed_batches': completed_batches,
                'processing_batches': processing_batches,
                'failed_batches': failed_batches,
                'success_rate': (completed_batches / max(total_batches, 1)) * 100,
                'average_processing_time_seconds': avg_processing_time
            }
            
        except Exception as e:
            logger.error(f"Error getting processing statistics: {e}")
            return {}

# Global batch processor instance
batch_processor = BatchProcessor()
