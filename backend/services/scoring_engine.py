from typing import Dict, List, Tuple, Any
from dataclasses import dataclass
import logging
from .matching_engine import ResumeJobMatcher, MatchingResult

@dataclass
class ScoringResult:
    relevance_score: float
    skills_match_score: float
    experience_match_score: float
    education_match_score: float
    overall_fit: str  # High, Medium, Low
    matched_skills: List[str]
    missing_skills: List[str]
    missing_certifications: List[str]
    missing_projects: List[str]
    strengths: List[str]
    weaknesses: List[str]
    recommendations: str

class ResumeScorer:
    def __init__(self):
        self.matcher = ResumeJobMatcher()
        
        # Scoring thresholds
        self.fit_thresholds = {
            'high': 75,
            'medium': 50,
            'low': 0
        }
        
        # Certification importance mapping
        self.certification_categories = {
            'cloud': ['aws', 'azure', 'gcp', 'google cloud'],
            'project_management': ['pmp', 'scrum', 'agile'],
            'security': ['cissp', 'ceh', 'security+'],
            'data': ['tableau', 'power bi', 'databricks'],
            'programming': ['oracle', 'microsoft', 'java', 'python']
        }
    
    def determine_fit_level(self, relevance_score: float) -> str:
        """Determine fit level based on relevance score"""
        if relevance_score >= self.fit_thresholds['high']:
            return 'High'
        elif relevance_score >= self.fit_thresholds['medium']:
            return 'Medium'
        else:
            return 'Low'
    
    def identify_missing_certifications(self, resume_certs: List[str], jd_requirements: str) -> List[str]:
        """Identify missing certifications based on job requirements"""
        jd_lower = jd_requirements.lower()
        resume_certs_lower = [cert.lower() for cert in resume_certs]
        
        missing_certs = []
        
        # Check for specific certification mentions in JD
        for category, certs in self.certification_categories.items():
            for cert in certs:
                if cert in jd_lower:
                    # Check if candidate has this certification
                    has_cert = any(cert in resume_cert for resume_cert in resume_certs_lower)
                    if not has_cert:
                        missing_certs.append(cert.upper())
        
        # Common certifications for different roles
        role_certs = {
            'cloud': ['AWS Solutions Architect', 'Azure Fundamentals'],
            'data': ['Google Analytics', 'Tableau Desktop'],
            'security': ['CompTIA Security+', 'CISSP'],
            'project': ['PMP', 'Scrum Master']
        }
        
        for role_type, certs in role_certs.items():
            if role_type in jd_lower:
                for cert in certs:
                    has_cert = any(cert.lower() in resume_cert for resume_cert in resume_certs_lower)
                    if not has_cert and cert not in missing_certs:
                        missing_certs.append(cert)
        
        return missing_certs[:5]  # Limit to top 5
    
    def identify_missing_projects(self, resume_projects: List[Dict], jd_requirements: str, matched_skills: List[str]) -> List[str]:
        """Identify types of projects candidate should have based on JD"""
        jd_lower = jd_requirements.lower()
        
        # Extract project types from resume
        resume_project_types = set()
        for project in resume_projects:
            title = project.get('title', '').lower()
            description = project.get('description', '').lower()
            project_text = f"{title} {description}"
            
            # Categorize projects
            if any(keyword in project_text for keyword in ['web', 'website', 'frontend', 'backend']):
                resume_project_types.add('web development')
            if any(keyword in project_text for keyword in ['mobile', 'android', 'ios', 'app']):
                resume_project_types.add('mobile development')
            if any(keyword in project_text for keyword in ['data', 'analytics', 'ml', 'ai']):
                resume_project_types.add('data science')
            if any(keyword in project_text for keyword in ['cloud', 'aws', 'azure']):
                resume_project_types.add('cloud computing')
        
        # Determine expected project types from JD
        expected_projects = []
        
        if any(keyword in jd_lower for keyword in ['web development', 'frontend', 'backend', 'full stack']):
            if 'web development' not in resume_project_types:
                expected_projects.append('Web Development Project')
        
        if any(keyword in jd_lower for keyword in ['mobile', 'android', 'ios', 'app development']):
            if 'mobile development' not in resume_project_types:
                expected_projects.append('Mobile Application Project')
        
        if any(keyword in jd_lower for keyword in ['data science', 'machine learning', 'analytics']):
            if 'data science' not in resume_project_types:
                expected_projects.append('Data Science/ML Project')
        
        if any(keyword in jd_lower for keyword in ['cloud', 'aws', 'azure', 'devops']):
            if 'cloud computing' not in resume_project_types:
                expected_projects.append('Cloud Computing Project')
        
        return expected_projects[:3]  # Limit to top 3
    
    def generate_detailed_strengths(self, matching_result: MatchingResult, resume_data: Dict) -> List[str]:
        """Generate detailed list of candidate strengths"""
        strengths = []
        
        # Skill-based strengths
        if matching_result.skills_match_score >= 80:
            strengths.append("Excellent technical skill alignment with job requirements")
        elif matching_result.skills_match_score >= 60:
            strengths.append("Good technical skill match")
        
        # Experience-based strengths
        if matching_result.experience_match_score >= 90:
            strengths.append("Perfect experience level for the role")
        elif matching_result.experience_match_score >= 70:
            strengths.append("Appropriate experience level")
        
        # Education strengths
        if matching_result.education_match_score >= 80:
            strengths.append("Strong educational background")
        
        # Specific skill strengths
        high_value_skills = ['python', 'java', 'react', 'aws', 'machine learning', 'sql']
        matched_high_value = [skill for skill in matching_result.matched_skills 
                             if any(hvs in skill.lower() for hvs in high_value_skills)]
        
        if matched_high_value:
            strengths.append(f"Proficiency in high-demand skills: {', '.join(matched_high_value[:3])}")
        
        # Project diversity
        projects = resume_data.get('projects', [])
        if len(projects) >= 3:
            strengths.append("Diverse project portfolio demonstrating practical experience")
        
        # Certification strengths
        certifications = resume_data.get('certifications', [])
        if certifications:
            strengths.append("Professional certifications demonstrate commitment to continuous learning")
        
        return strengths
    
    def generate_detailed_weaknesses(self, matching_result: MatchingResult, resume_data: Dict, missing_certs: List[str], missing_projects: List[str]) -> List[str]:
        """Generate detailed list of areas for improvement"""
        weaknesses = []
        
        # Skill gaps
        if matching_result.skills_match_score < 50:
            weaknesses.append("Significant gaps in required technical skills")
        elif matching_result.skills_match_score < 70:
            weaknesses.append("Some important technical skills are missing")
        
        # Experience gaps
        if matching_result.experience_match_score < 50:
            weaknesses.append("Experience level doesn't align well with job requirements")
        
        # Missing critical skills
        critical_missing = [skill for skill in matching_result.missing_skills[:3]]
        if critical_missing:
            weaknesses.append(f"Missing key skills: {', '.join(critical_missing)}")
        
        # Certification gaps
        if missing_certs:
            weaknesses.append(f"Lack of relevant certifications: {', '.join(missing_certs[:2])}")
        
        # Project gaps
        if missing_projects:
            weaknesses.append(f"Limited project experience in: {', '.join(missing_projects[:2])}")
        
        # Portfolio gaps
        projects = resume_data.get('projects', [])
        if len(projects) < 2:
            weaknesses.append("Limited project portfolio to demonstrate practical skills")
        
        return weaknesses
    
    def generate_comprehensive_recommendations(self, scoring_result: ScoringResult, resume_data: Dict) -> str:
        """Generate comprehensive, actionable recommendations"""
        recommendations = []
        
        # Overall assessment
        if scoring_result.overall_fit == 'High':
            recommendations.append("🎉 Excellent match! You're well-qualified for this position.")
        elif scoring_result.overall_fit == 'Medium':
            recommendations.append("👍 Good potential! With some improvements, you could be a strong candidate.")
        else:
            recommendations.append("📈 There's room for growth. Focus on developing key skills to improve your candidacy.")
        
        # Skill development recommendations
        if scoring_result.missing_skills:
            top_missing = scoring_result.missing_skills[:3]
            recommendations.append(f"\n🔧 Priority Skills to Develop:")
            for i, skill in enumerate(top_missing, 1):
                recommendations.append(f"   {i}. {skill}")
        
        # Certification recommendations
        if scoring_result.missing_certifications:
            recommendations.append(f"\n📜 Recommended Certifications:")
            for i, cert in enumerate(scoring_result.missing_certifications[:2], 1):
                recommendations.append(f"   {i}. {cert}")
        
        # Project recommendations
        if scoring_result.missing_projects:
            recommendations.append(f"\n💼 Suggested Project Types:")
            for i, project in enumerate(scoring_result.missing_projects, 1):
                recommendations.append(f"   {i}. {project}")
        
        # Experience recommendations
        experience_years = resume_data.get('experience_years', 0)
        if scoring_result.experience_match_score < 70:
            if experience_years < 2:
                recommendations.append("\n⏰ Focus on gaining more hands-on experience through internships or entry-level positions.")
            else:
                recommendations.append("\n⏰ Consider highlighting more relevant work experience or taking on projects that align with the job requirements.")
        
        # Portfolio recommendations
        projects = resume_data.get('projects', [])
        if len(projects) < 3:
            recommendations.append("\n🚀 Build a stronger portfolio with 3-5 diverse projects showcasing different skills.")
        
        # Next steps
        recommendations.append(f"\n📋 Immediate Action Items:")
        if scoring_result.overall_fit == 'Low':
            recommendations.append("   • Focus on developing 2-3 key missing skills")
            recommendations.append("   • Complete at least one relevant project")
            recommendations.append("   • Consider taking online courses or bootcamps")
        elif scoring_result.overall_fit == 'Medium':
            recommendations.append("   • Address 1-2 critical skill gaps")
            recommendations.append("   • Enhance your project portfolio")
            recommendations.append("   • Consider relevant certifications")
        else:
            recommendations.append("   • Polish your resume to highlight relevant experience")
            recommendations.append("   • Prepare for technical interviews")
            recommendations.append("   • Research the company and role thoroughly")
        
        return "\n".join(recommendations)
    
    def score_resume(self, resume_data: Dict, job_data: Dict) -> ScoringResult:
        """Main method to score resume against job description"""
        try:
            # Get matching results from the matching engine
            matching_result = self.matcher.evaluate_resume(resume_data, job_data)
            
            # Determine overall fit
            overall_fit = self.determine_fit_level(matching_result.relevance_score)
            
            # Identify missing elements
            missing_certifications = self.identify_missing_certifications(
                resume_data.get('certifications', []),
                job_data.get('requirements', '')
            )
            
            missing_projects = self.identify_missing_projects(
                resume_data.get('projects', []),
                job_data.get('requirements', ''),
                matching_result.matched_skills
            )
            
            # Generate detailed strengths and weaknesses
            strengths = self.generate_detailed_strengths(matching_result, resume_data)
            weaknesses = self.generate_detailed_weaknesses(
                matching_result, resume_data, missing_certifications, missing_projects
            )
            
            # Create scoring result
            scoring_result = ScoringResult(
                relevance_score=matching_result.relevance_score,
                skills_match_score=matching_result.skills_match_score,
                experience_match_score=matching_result.experience_match_score,
                education_match_score=matching_result.education_match_score,
                overall_fit=overall_fit,
                matched_skills=matching_result.matched_skills,
                missing_skills=matching_result.missing_skills,
                missing_certifications=missing_certifications,
                missing_projects=missing_projects,
                strengths=strengths,
                weaknesses=weaknesses,
                recommendations=""  # Will be filled next
            )
            
            # Generate comprehensive recommendations
            scoring_result.recommendations = self.generate_comprehensive_recommendations(
                scoring_result, resume_data
            )
            
            return scoring_result
            
        except Exception as e:
            logging.error(f"Error scoring resume: {e}")
            return ScoringResult(
                relevance_score=0.0,
                skills_match_score=0.0,
                experience_match_score=0.0,
                education_match_score=0.0,
                overall_fit='Low',
                matched_skills=[],
                missing_skills=[],
                missing_certifications=[],
                missing_projects=[],
                strengths=[],
                weaknesses=["Error in scoring process"],
                recommendations="Unable to generate recommendations due to processing error."
            )
