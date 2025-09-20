#!/usr/bin/env python3
"""
Quick Demo of Resume Relevance Check System
Run this to test core functionality without full setup
"""

import json
import re
from typing import Dict, List, Any

class SimpleResumeParser:
    def __init__(self):
        self.skills_db = [
            'python', 'java', 'javascript', 'react', 'angular', 'vue', 'node.js',
            'sql', 'mysql', 'postgresql', 'mongodb', 'aws', 'azure', 'docker',
            'kubernetes', 'git', 'jenkins', 'tensorflow', 'machine learning',
            'data science', 'html', 'css', 'php', 'c++', 'c#', '.net'
        ]
    
    def parse_text(self, text: str) -> Dict[str, Any]:
        """Parse resume text and extract key information"""
        text_lower = text.lower()
        
        # Extract skills
        found_skills = []
        for skill in self.skills_db:
            if skill in text_lower:
                found_skills.append(skill)
        
        # Extract experience (simple pattern matching)
        experience = 0
        exp_patterns = [
            r'(\d+)\+?\s*years?\s*(?:of\s*)?experience',
            r'experience[:\-]?\s*(\d+)\+?\s*years?'
        ]
        for pattern in exp_patterns:
            matches = re.findall(pattern, text_lower)
            if matches:
                experience = int(matches[0])
                break
        
        return {
            'skills': found_skills,
            'experience_years': experience,
            'text': text[:200] + "..." if len(text) > 200 else text
        }

class SimpleJobMatcher:
    def calculate_relevance_score(self, resume_data: Dict, job_data: Dict) -> Dict[str, Any]:
        """Calculate relevance score between resume and job"""
        resume_skills = set(skill.lower() for skill in resume_data.get('skills', []))
        job_skills = set(skill.lower() for skill in job_data.get('required_skills', []))
        
        # Skills match
        matched_skills = resume_skills.intersection(job_skills)
        missing_skills = job_skills - resume_skills
        skills_score = (len(matched_skills) / max(len(job_skills), 1)) * 100
        
        # Experience match
        resume_exp = resume_data.get('experience_years', 0)
        job_min_exp = job_data.get('min_experience', 0)
        job_max_exp = job_data.get('max_experience', 10)
        
        if job_min_exp <= resume_exp <= job_max_exp:
            exp_score = 100
        elif resume_exp < job_min_exp:
            exp_score = max(0, 100 - (job_min_exp - resume_exp) * 20)
        else:
            exp_score = max(70, 100 - (resume_exp - job_max_exp) * 5)
        
        # Overall score (weighted)
        overall_score = (skills_score * 0.6) + (exp_score * 0.4)
        
        # Determine fit level
        if overall_score >= 75:
            fit_level = "High"
        elif overall_score >= 50:
            fit_level = "Medium"
        else:
            fit_level = "Low"
        
        return {
            'relevance_score': round(overall_score, 1),
            'skills_match_score': round(skills_score, 1),
            'experience_match_score': round(exp_score, 1),
            'overall_fit': fit_level,
            'matched_skills': list(matched_skills),
            'missing_skills': list(missing_skills),
            'recommendations': self.generate_feedback(overall_score, matched_skills, missing_skills)
        }
    
    def generate_feedback(self, score: float, matched: set, missing: set) -> str:
        """Generate personalized feedback"""
        feedback = []
        
        if score >= 75:
            feedback.append("🎉 Excellent match! Strong candidate for this position.")
        elif score >= 50:
            feedback.append("👍 Good potential with some areas for improvement.")
        else:
            feedback.append("📈 Significant skill development needed for this role.")
        
        if matched:
            feedback.append(f"✅ Strong skills: {', '.join(list(matched)[:3])}")
        
        if missing:
            feedback.append(f"📚 Skills to develop: {', '.join(list(missing)[:3])}")
        
        return " ".join(feedback)

def run_demo():
    """Run the demo with sample data"""
    print("🚀 Resume Relevance Check System - Demo")
    print("=" * 50)
    
    # Sample job description
    job_posting = {
        'title': 'Senior Software Engineer',
        'company': 'Innomatics Research Labs',
        'location': 'Hyderabad',
        'required_skills': ['python', 'react', 'aws', 'sql', 'docker'],
        'min_experience': 3,
        'max_experience': 7
    }
    
    # Sample resumes
    sample_resumes = [
        {
            'name': 'John Smith',
            'text': '''John Smith
            Email: john@email.com
            
            Experienced software engineer with 5 years of experience in Python, React, and AWS.
            Built scalable web applications using Docker and PostgreSQL.
            Strong background in machine learning and data science.
            '''
        },
        {
            'name': 'Sarah Johnson',
            'text': '''Sarah Johnson
            sarah.j@email.com
            
            Software developer with 2 years experience in Java, Angular, and MySQL.
            Worked on enterprise applications and REST APIs.
            Knowledge of Git, Jenkins, and Agile methodologies.
            '''
        },
        {
            'name': 'Mike Chen',
            'text': '''Mike Chen
            mike.chen@email.com
            
            Full-stack developer with 6 years experience in Python, React, Node.js, and MongoDB.
            Expert in AWS cloud services, Docker, and Kubernetes.
            Led multiple projects and mentored junior developers.
            '''
        }
    ]
    
    # Initialize components
    parser = SimpleResumeParser()
    matcher = SimpleJobMatcher()
    
    print(f"📋 Job Posting: {job_posting['title']} - {job_posting['location']}")
    print(f"🎯 Required Skills: {', '.join(job_posting['required_skills'])}")
    print(f"👔 Experience: {job_posting['min_experience']}-{job_posting['max_experience']} years")
    print("\n" + "=" * 50)
    
    results = []
    
    # Process each resume
    for i, resume in enumerate(sample_resumes, 1):
        print(f"\n📄 Candidate {i}: {resume['name']}")
        print("-" * 30)
        
        # Parse resume
        parsed_data = parser.parse_text(resume['text'])
        
        # Calculate match
        evaluation = matcher.calculate_relevance_score(parsed_data, job_posting)
        
        # Display results
        print(f"🎯 Relevance Score: {evaluation['relevance_score']}%")
        print(f"🔧 Skills Match: {evaluation['skills_match_score']}%")
        print(f"👔 Experience Match: {evaluation['experience_match_score']}%")
        print(f"📊 Overall Fit: {evaluation['overall_fit']}")
        print(f"✅ Matched Skills: {', '.join(evaluation['matched_skills']) if evaluation['matched_skills'] else 'None'}")
        print(f"❌ Missing Skills: {', '.join(evaluation['missing_skills']) if evaluation['missing_skills'] else 'None'}")
        print(f"💡 Feedback: {evaluation['recommendations']}")
        
        results.append({
            'candidate': resume['name'],
            'score': evaluation['relevance_score'],
            'fit': evaluation['overall_fit']
        })
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 SUMMARY RESULTS")
    print("=" * 50)
    
    results.sort(key=lambda x: x['score'], reverse=True)
    
    for i, result in enumerate(results, 1):
        fit_emoji = "🟢" if result['fit'] == "High" else "🟡" if result['fit'] == "Medium" else "🔴"
        print(f"{i}. {result['candidate']}: {result['score']}% {fit_emoji} {result['fit']} Fit")
    
    high_fit = sum(1 for r in results if r['fit'] == 'High')
    medium_fit = sum(1 for r in results if r['fit'] == 'Medium')
    low_fit = sum(1 for r in results if r['fit'] == 'Low')
    avg_score = sum(r['score'] for r in results) / len(results)
    
    print(f"\n📈 Statistics:")
    print(f"   • High Fit: {high_fit} candidates")
    print(f"   • Medium Fit: {medium_fit} candidates")
    print(f"   • Low Fit: {low_fit} candidates")
    print(f"   • Average Score: {avg_score:.1f}%")
    
    print("\n🎉 Demo completed! This shows the core functionality of the full system.")
    print("For the complete web interface and advanced features, set up the full system.")

if __name__ == "__main__":
    run_demo()
