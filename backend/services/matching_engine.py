import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
import spacy
from typing import Dict, List, Tuple, Any
import re
import logging
from dataclasses import dataclass

@dataclass
class MatchingResult:
    relevance_score: float
    skills_match_score: float
    experience_match_score: float
    education_match_score: float
    matched_skills: List[str]
    missing_skills: List[str]
    strengths: List[str]
    weaknesses: List[str]

class ResumeJobMatcher:
    def __init__(self):
        # Initialize models
        try:
            self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
            self.nlp = spacy.load("en_core_web_sm")
        except Exception as e:
            logging.error(f"Error loading models: {e}")
            self.sentence_model = None
            self.nlp = None
        
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=5000,
            stop_words='english',
            ngram_range=(1, 2)
        )
        
        # Skill categories and weights
        self.skill_categories = {
            'programming_languages': 0.3,
            'frameworks': 0.25,
            'databases': 0.2,
            'tools': 0.15,
            'soft_skills': 0.1
        }
        
        # Experience level mapping
        self.experience_levels = {
            'entry': (0, 2),
            'junior': (1, 3),
            'mid': (3, 7),
            'senior': (7, 12),
            'lead': (10, float('inf'))
        }
    
    def preprocess_text(self, text: str) -> str:
        """Clean and preprocess text for analysis"""
        if not text:
            return ""
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep important ones
        text = re.sub(r'[^\w\s\-\+\#\.]', ' ', text)
        
        return text.strip()
    
    def extract_skills_from_jd(self, job_description: str, requirements: str) -> Dict[str, List[str]]:
        """Extract required and preferred skills from job description"""
        full_text = f"{job_description} {requirements}".lower()
        
        # Skill extraction patterns
        skill_patterns = {
            'required': [
                r'required[:\-]?\s*([^.]+)',
                r'must have[:\-]?\s*([^.]+)',
                r'essential[:\-]?\s*([^.]+)'
            ],
            'preferred': [
                r'preferred[:\-]?\s*([^.]+)',
                r'nice to have[:\-]?\s*([^.]+)',
                r'bonus[:\-]?\s*([^.]+)'
            ]
        }
        
        extracted_skills = {'required': [], 'preferred': []}
        
        for category, patterns in skill_patterns.items():
            for pattern in patterns:
                matches = re.findall(pattern, full_text)
                for match in matches:
                    # Split by common delimiters
                    skills = re.split(r'[,;|•\n]', match)
                    for skill in skills:
                        skill = skill.strip()
                        if skill and len(skill) < 50:
                            extracted_skills[category].append(skill)
        
        # If no explicit required/preferred found, extract all skills
        if not extracted_skills['required'] and not extracted_skills['preferred']:
            all_skills = self._extract_general_skills(full_text)
            extracted_skills['required'] = all_skills[:len(all_skills)//2]
            extracted_skills['preferred'] = all_skills[len(all_skills)//2:]
        
        return extracted_skills
    
    def _extract_general_skills(self, text: str) -> List[str]:
        """Extract general skills from text"""
        # Common technical skills database
        tech_skills = [
            'python', 'java', 'javascript', 'react', 'angular', 'node.js',
            'sql', 'mysql', 'postgresql', 'mongodb', 'aws', 'azure',
            'docker', 'kubernetes', 'git', 'jenkins', 'tensorflow',
            'machine learning', 'data analysis', 'html', 'css'
        ]
        
        found_skills = []
        for skill in tech_skills:
            if skill in text:
                found_skills.append(skill)
        
        return found_skills
    
    def calculate_skills_match(self, resume_skills: List[str], jd_skills: Dict[str, List[str]]) -> Tuple[float, List[str], List[str]]:
        """Calculate skill matching score between resume and job description"""
        if not resume_skills:
            return 0.0, [], jd_skills.get('required', []) + jd_skills.get('preferred', [])
        
        resume_skills_lower = [skill.lower().strip() for skill in resume_skills]
        required_skills = [skill.lower().strip() for skill in jd_skills.get('required', [])]
        preferred_skills = [skill.lower().strip() for skill in jd_skills.get('preferred', [])]
        
        # Calculate matches
        matched_required = []
        matched_preferred = []
        
        for skill in resume_skills_lower:
            # Check for exact matches and partial matches
            for req_skill in required_skills:
                if self._skills_similar(skill, req_skill):
                    matched_required.append(req_skill)
            
            for pref_skill in preferred_skills:
                if self._skills_similar(skill, pref_skill):
                    matched_preferred.append(pref_skill)
        
        # Remove duplicates
        matched_required = list(set(matched_required))
        matched_preferred = list(set(matched_preferred))
        
        # Calculate score
        required_score = len(matched_required) / max(len(required_skills), 1) if required_skills else 1.0
        preferred_score = len(matched_preferred) / max(len(preferred_skills), 1) if preferred_skills else 1.0
        
        # Weighted score (required skills are more important)
        overall_score = (required_score * 0.7 + preferred_score * 0.3) * 100
        
        # Find missing skills
        missing_required = [skill for skill in required_skills if skill not in matched_required]
        missing_preferred = [skill for skill in preferred_skills if skill not in matched_preferred]
        missing_skills = missing_required + missing_preferred
        
        matched_skills = matched_required + matched_preferred
        
        return min(overall_score, 100.0), matched_skills, missing_skills
    
    def _skills_similar(self, skill1: str, skill2: str) -> bool:
        """Check if two skills are similar"""
        # Exact match
        if skill1 == skill2:
            return True
        
        # Partial match
        if skill1 in skill2 or skill2 in skill1:
            return True
        
        # Handle common variations
        variations = {
            'javascript': ['js', 'node.js', 'nodejs'],
            'python': ['py'],
            'machine learning': ['ml', 'ai', 'artificial intelligence'],
            'database': ['db', 'sql'],
            'react': ['reactjs', 'react.js'],
            'angular': ['angularjs']
        }
        
        for base_skill, variants in variations.items():
            if (skill1 == base_skill and skill2 in variants) or \
               (skill2 == base_skill and skill1 in variants):
                return True
        
        return False
    
    def calculate_experience_match(self, resume_experience: float, jd_min_exp: int, jd_max_exp: int) -> float:
        """Calculate experience matching score"""
        if jd_min_exp == 0 and jd_max_exp == 0:
            return 100.0  # No experience requirement
        
        if resume_experience >= jd_min_exp and resume_experience <= jd_max_exp:
            return 100.0  # Perfect match
        elif resume_experience < jd_min_exp:
            # Underqualified
            gap = jd_min_exp - resume_experience
            score = max(0, 100 - (gap * 20))  # Penalize 20 points per year gap
            return score
        else:
            # Overqualified (less penalty)
            excess = resume_experience - jd_max_exp
            score = max(70, 100 - (excess * 5))  # Penalize 5 points per excess year
            return score
    
    def calculate_education_match(self, resume_education: List[Dict], jd_requirements: str) -> float:
        """Calculate education matching score"""
        if not resume_education:
            return 50.0  # Neutral score if no education info
        
        jd_lower = jd_requirements.lower()
        education_keywords = {
            'bachelor': 60,
            'master': 80,
            'phd': 100,
            'doctorate': 100,
            'engineering': 70,
            'computer science': 90,
            'mba': 75
        }
        
        max_score = 0
        for edu in resume_education:
            degree = edu.get('degree', '').lower()
            for keyword, score in education_keywords.items():
                if keyword in degree:
                    max_score = max(max_score, score)
        
        # Check if education matches JD requirements
        for keyword in education_keywords.keys():
            if keyword in jd_lower:
                # JD requires this education level
                for edu in resume_education:
                    if keyword in edu.get('degree', '').lower():
                        return min(100.0, max_score + 20)  # Bonus for matching requirement
        
        return max_score if max_score > 0 else 60.0  # Default score
    
    def calculate_semantic_similarity(self, resume_text: str, jd_text: str) -> float:
        """Calculate semantic similarity using sentence transformers"""
        if not self.sentence_model:
            return self._calculate_tfidf_similarity(resume_text, jd_text)
        
        try:
            # Preprocess texts
            resume_clean = self.preprocess_text(resume_text)
            jd_clean = self.preprocess_text(jd_text)
            
            if not resume_clean or not jd_clean:
                return 0.0
            
            # Generate embeddings
            embeddings = self.sentence_model.encode([resume_clean, jd_clean])
            
            # Calculate cosine similarity
            similarity = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
            
            return float(similarity * 100)
        
        except Exception as e:
            logging.error(f"Error calculating semantic similarity: {e}")
            return self._calculate_tfidf_similarity(resume_text, jd_text)
    
    def _calculate_tfidf_similarity(self, resume_text: str, jd_text: str) -> float:
        """Fallback TF-IDF similarity calculation"""
        try:
            texts = [self.preprocess_text(resume_text), self.preprocess_text(jd_text)]
            tfidf_matrix = self.tfidf_vectorizer.fit_transform(texts)
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            return float(similarity * 100)
        except Exception as e:
            logging.error(f"Error calculating TF-IDF similarity: {e}")
            return 0.0
    
    def generate_feedback(self, matching_result: MatchingResult, resume_data: Dict, jd_data: Dict) -> str:
        """Generate personalized feedback for the candidate"""
        feedback_parts = []
        
        # Overall assessment
        if matching_result.relevance_score >= 80:
            feedback_parts.append("Excellent match! Your profile aligns very well with the job requirements.")
        elif matching_result.relevance_score >= 60:
            feedback_parts.append("Good match! Your profile shows strong potential for this role.")
        else:
            feedback_parts.append("Your profile shows some relevant experience, but there are areas for improvement.")
        
        # Strengths
        if matching_result.strengths:
            feedback_parts.append(f"\nStrengths:\n• " + "\n• ".join(matching_result.strengths))
        
        # Areas for improvement
        if matching_result.weaknesses:
            feedback_parts.append(f"\nAreas for improvement:\n• " + "\n• ".join(matching_result.weaknesses))
        
        # Missing skills recommendations
        if matching_result.missing_skills:
            top_missing = matching_result.missing_skills[:5]  # Top 5 missing skills
            feedback_parts.append(f"\nRecommended skills to develop:\n• " + "\n• ".join(top_missing))
        
        return "\n".join(feedback_parts)
    
    def evaluate_resume(self, resume_data: Dict, job_data: Dict) -> MatchingResult:
        """Main method to evaluate resume against job description"""
        try:
            # Extract job requirements
            jd_skills = self.extract_skills_from_jd(
                job_data.get('description', ''),
                job_data.get('requirements', '')
            )
            
            # Calculate individual scores
            skills_score, matched_skills, missing_skills = self.calculate_skills_match(
                resume_data.get('skills', []),
                jd_skills
            )
            
            experience_score = self.calculate_experience_match(
                resume_data.get('experience_years', 0),
                job_data.get('experience_min', 0),
                job_data.get('experience_max', 10)
            )
            
            education_score = self.calculate_education_match(
                resume_data.get('education', []),
                job_data.get('requirements', '')
            )
            
            # Calculate semantic similarity
            resume_text = f"{resume_data.get('summary', '')} {' '.join(resume_data.get('skills', []))}"
            jd_text = f"{job_data.get('description', '')} {job_data.get('requirements', '')}"
            semantic_score = self.calculate_semantic_similarity(resume_text, jd_text)
            
            # Calculate overall relevance score (weighted average)
            relevance_score = (
                skills_score * 0.4 +
                experience_score * 0.3 +
                education_score * 0.2 +
                semantic_score * 0.1
            )
            
            # Generate strengths and weaknesses
            strengths = []
            weaknesses = []
            
            if skills_score >= 70:
                strengths.append("Strong technical skill match")
            else:
                weaknesses.append("Limited technical skill alignment")
            
            if experience_score >= 80:
                strengths.append("Appropriate experience level")
            elif experience_score < 50:
                weaknesses.append("Experience level mismatch")
            
            if education_score >= 70:
                strengths.append("Relevant educational background")
            
            if len(matched_skills) > 5:
                strengths.append("Diverse technical skill set")
            
            return MatchingResult(
                relevance_score=min(relevance_score, 100.0),
                skills_match_score=skills_score,
                experience_match_score=experience_score,
                education_match_score=education_score,
                matched_skills=matched_skills,
                missing_skills=missing_skills,
                strengths=strengths,
                weaknesses=weaknesses
            )
            
        except Exception as e:
            logging.error(f"Error evaluating resume: {e}")
            return MatchingResult(
                relevance_score=0.0,
                skills_match_score=0.0,
                experience_match_score=0.0,
                education_match_score=0.0,
                matched_skills=[],
                missing_skills=[],
                strengths=[],
                weaknesses=["Error in evaluation process"]
            )
