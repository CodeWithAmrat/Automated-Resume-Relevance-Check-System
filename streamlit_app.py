#!/usr/bin/env python3
"""
Streamlit App for Resume Relevance Check System
Deployed on Streamlit Cloud
"""

import streamlit as st
import sqlite3
import pandas as pd
import re
import os
from datetime import datetime
from typing import Dict, List, Any
import tempfile

# Page configuration
st.set_page_config(
    page_title="🎯 Resume Relevance Check System",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

class ResumeProcessor:
    def __init__(self):
        self.skills_db = [
            'python', 'java', 'javascript', 'react', 'angular', 'vue', 'node.js',
            'sql', 'mysql', 'postgresql', 'mongodb', 'aws', 'azure', 'docker',
            'kubernetes', 'git', 'jenkins', 'tensorflow', 'machine learning',
            'data science', 'html', 'css', 'php', 'c++', 'c#', '.net', 'spring',
            'django', 'flask', 'express', 'bootstrap', 'jquery', 'typescript'
        ]
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database"""
        self.conn = sqlite3.connect('resume_system.db', check_same_thread=False)
        cursor = self.conn.cursor()
        
        # Create tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                company TEXT NOT NULL,
                location TEXT NOT NULL,
                description TEXT NOT NULL,
                requirements TEXT NOT NULL,
                skills_required TEXT,
                experience_min INTEGER DEFAULT 0,
                experience_max INTEGER DEFAULT 10,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS resumes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                candidate_name TEXT NOT NULL,
                email TEXT,
                phone TEXT,
                skills TEXT,
                experience_years INTEGER DEFAULT 0,
                summary TEXT,
                uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS evaluations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id INTEGER,
                resume_id INTEGER,
                candidate_name TEXT,
                relevance_score REAL,
                skills_match_score REAL,
                experience_match_score REAL,
                overall_fit TEXT,
                matched_skills TEXT,
                missing_skills TEXT,
                recommendations TEXT,
                evaluated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (job_id) REFERENCES jobs (id),
                FOREIGN KEY (resume_id) REFERENCES resumes (id)
            )
        ''')
        
        self.conn.commit()
        self.load_sample_data()
    
    def load_sample_data(self):
        """Load sample data if tables are empty"""
        cursor = self.conn.cursor()
        
        # Check if jobs exist
        cursor.execute('SELECT COUNT(*) FROM jobs')
        if cursor.fetchone()[0] == 0:
            # Insert sample jobs
            sample_jobs = [
                ("Senior Software Engineer", "Innomatics Research Labs", "Hyderabad", 
                 "We are looking for a Senior Software Engineer with expertise in Python, React, and cloud technologies.",
                 "5+ years experience, Python, React, AWS, SQL, Git", "Python,React,AWS,SQL,Git", 5, 8),
                ("Data Scientist", "Innomatics Research Labs", "Bangalore",
                 "Join our data science team to build ML models and analytics solutions.",
                 "3+ years experience, Python, Machine Learning, TensorFlow, SQL", "Python,Machine Learning,TensorFlow,SQL", 3, 6),
                ("Full Stack Developer", "Innomatics Research Labs", "Pune",
                 "Develop end-to-end web applications using modern technologies.",
                 "2+ years experience, JavaScript, Node.js, React, MongoDB", "JavaScript,Node.js,React,MongoDB", 2, 5)
            ]
            
            cursor.executemany('''
                INSERT INTO jobs (title, company, location, description, requirements, skills_required, experience_min, experience_max)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', sample_jobs)
        
        # Check if resumes exist
        cursor.execute('SELECT COUNT(*) FROM resumes')
        if cursor.fetchone()[0] == 0:
            # Insert sample resumes
            sample_resumes = [
                ("Rahul Sharma", "rahul.sharma@email.com", "+91-9876543210", "Python, React, AWS, SQL, Git", 6, "Experienced software engineer with full-stack development skills"),
                ("Priya Patel", "priya.patel@email.com", "+91-9876543211", "Python, Machine Learning, TensorFlow, Pandas", 4, "Data scientist with expertise in ML and analytics"),
                ("Amit Kumar", "amit.kumar@email.com", "+91-9876543212", "JavaScript, Node.js, React, MongoDB", 3, "Full-stack developer with modern web technologies"),
                ("Sneha Reddy", "sneha.reddy@email.com", "+91-9876543213", "Java, Spring, MySQL, Angular", 5, "Backend developer with enterprise application experience"),
                ("Vikram Singh", "vikram.singh@email.com", "+91-9876543214", "Python, Django, PostgreSQL, Docker", 2, "Junior developer with web development skills")
            ]
            
            cursor.executemany('''
                INSERT INTO resumes (candidate_name, email, phone, skills, experience_years, summary)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', sample_resumes)
        
        self.conn.commit()
    
    def extract_resume_info(self, text, filename):
        """Extract basic information from resume text"""
        # Extract email
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        email_match = re.search(email_pattern, text)
        email = email_match.group() if email_match else ''
        
        # Extract phone
        phone_pattern = r'[\+]?[1-9]?[\d\s\-\(\)]{8,15}'
        phone_match = re.search(phone_pattern, text)
        phone = phone_match.group().strip() if phone_match else ''
        
        # Extract name (first line or near email)
        lines = text.split('\n')
        candidate_name = ''
        for line in lines[:5]:  # Check first 5 lines
            line = line.strip()
            if line and len(line.split()) <= 4 and not '@' in line and not any(char.isdigit() for char in line):
                candidate_name = line
                break
        
        if not candidate_name:
            candidate_name = os.path.splitext(filename)[0].replace('_', ' ').replace('-', ' ').title()
        
        # Extract skills
        skills_found = []
        text_lower = text.lower()
        for skill in self.skills_db:
            if skill.lower() in text_lower:
                skills_found.append(skill)
        
        # Extract experience years
        exp_pattern = r'(\d+)[\+]?\s*(?:years?|yrs?)\s*(?:of\s*)?(?:experience|exp)'
        exp_match = re.search(exp_pattern, text.lower())
        experience_years = int(exp_match.group(1)) if exp_match else 0
        
        # Create summary
        summary = ' '.join(text.split()[:50])  # First 50 words
        
        return {
            'candidate_name': candidate_name or 'Unknown Candidate',
            'email': email,
            'phone': phone,
            'skills': ', '.join(skills_found[:10]),  # Limit to 10 skills
            'experience_years': experience_years,
            'summary': summary
        }
    
    def evaluate_resume(self, resume_data, job_data):
        """Evaluate resume against job requirements"""
        # Extract skills from job
        job_skills = [skill.strip().lower() for skill in job_data.get('skills_required', '').split(',')]
        resume_skills = [skill.strip().lower() for skill in resume_data.get('skills', '').split(',')]
        
        # Calculate skills match
        matched_skills = list(set(job_skills) & set(resume_skills))
        missing_skills = list(set(job_skills) - set(resume_skills))
        skills_score = (len(matched_skills) / len(job_skills)) * 100 if job_skills else 0
        
        # Calculate experience match
        exp_min = job_data.get('experience_min', 0)
        exp_max = job_data.get('experience_max', 10)
        candidate_exp = resume_data.get('experience_years', 0)
        
        if exp_min <= candidate_exp <= exp_max:
            experience_score = 100
        elif candidate_exp < exp_min:
            experience_score = max(0, (candidate_exp / exp_min) * 80)
        else:
            experience_score = max(60, 100 - ((candidate_exp - exp_max) * 5))
        
        # Overall relevance score
        relevance_score = (skills_score * 0.6 + experience_score * 0.4)
        
        # Determine fit level
        if relevance_score >= 75:
            overall_fit = "High"
        elif relevance_score >= 50:
            overall_fit = "Medium"
        else:
            overall_fit = "Low"
        
        # Generate recommendations
        recommendations = []
        if len(missing_skills) > 0:
            recommendations.append(f"Consider learning: {', '.join(missing_skills[:3])}")
        if candidate_exp < exp_min:
            recommendations.append(f"Gain {exp_min - candidate_exp} more years of experience")
        if skills_score < 50:
            recommendations.append("Focus on developing technical skills mentioned in job requirements")
        
        return {
            'relevance_score': round(relevance_score, 1),
            'skills_match_score': round(skills_score, 1),
            'experience_match_score': round(experience_score, 1),
            'overall_fit': overall_fit,
            'matched_skills': ', '.join(matched_skills),
            'missing_skills': ', '.join(missing_skills),
            'recommendations': '; '.join(recommendations) if recommendations else 'Great fit for the role!'
        }

# Initialize processor
@st.cache_resource
def get_processor():
    return ResumeProcessor()

processor = get_processor()

# Main app
def main():
    st.title("🎯 Resume Relevance Check System")
    st.markdown("**AI-Powered Recruitment for Innomatics Research Labs**")
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox("Choose a page", 
                               ["Dashboard", "Jobs", "Resumes", "Upload Resume", "Evaluate"])
    
    if page == "Dashboard":
        show_dashboard()
    elif page == "Jobs":
        show_jobs()
    elif page == "Resumes":
        show_resumes()
    elif page == "Upload Resume":
        show_upload()
    elif page == "Evaluate":
        show_evaluate()

def show_dashboard():
    st.header("📊 Dashboard")
    
    cursor = processor.conn.cursor()
    
    # Get statistics
    cursor.execute('SELECT COUNT(*) FROM jobs')
    total_jobs = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM resumes')
    total_resumes = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*), AVG(relevance_score) FROM evaluations')
    eval_stats = cursor.fetchone()
    total_evaluations = eval_stats[0] or 0
    avg_score = round(eval_stats[1] or 0, 1)
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Active Jobs", total_jobs)
    
    with col2:
        st.metric("Total Resumes", total_resumes)
    
    with col3:
        st.metric("Evaluations", total_evaluations)
    
    with col4:
        st.metric("Avg Score", f"{avg_score}%")
    
    # Recent evaluations
    if total_evaluations > 0:
        st.subheader("Recent Evaluations")
        cursor.execute('''
            SELECT candidate_name, relevance_score, overall_fit, evaluated_at 
            FROM evaluations 
            ORDER BY evaluated_at DESC 
            LIMIT 10
        ''')
        
        recent_data = cursor.fetchall()
        df = pd.DataFrame(recent_data, columns=['Candidate', 'Score', 'Fit', 'Date'])
        st.dataframe(df, use_container_width=True)

def show_jobs():
    st.header("💼 Job Postings")
    
    cursor = processor.conn.cursor()
    cursor.execute('SELECT * FROM jobs ORDER BY created_at DESC')
    jobs = cursor.fetchall()
    
    if jobs:
        for job in jobs:
            with st.expander(f"{job[1]} - {job[3]}"):
                st.write(f"**Company:** {job[2]}")
                st.write(f"**Description:** {job[4]}")
                st.write(f"**Requirements:** {job[5]}")
                st.write(f"**Experience:** {job[7]}-{job[8]} years")
                st.write(f"**Skills:** {job[6]}")
    else:
        st.info("No job postings available.")

def show_resumes():
    st.header("👥 Candidate Resumes")
    
    cursor = processor.conn.cursor()
    cursor.execute('SELECT * FROM resumes ORDER BY uploaded_at DESC')
    resumes = cursor.fetchall()
    
    if resumes:
        # Convert to DataFrame for better display
        df = pd.DataFrame(resumes, columns=[
            'ID', 'Name', 'Email', 'Phone', 'Skills', 'Experience', 'Summary', 'Uploaded'
        ])
        
        # Display as interactive table
        st.dataframe(df[['Name', 'Email', 'Skills', 'Experience', 'Uploaded']], use_container_width=True)
        
        # Resume details
        st.subheader("Resume Details")
        selected_resume = st.selectbox("Select a resume to view details:", 
                                     options=[(r[0], r[1]) for r in resumes],
                                     format_func=lambda x: x[1])
        
        if selected_resume:
            resume_id = selected_resume[0]
            cursor.execute('SELECT * FROM resumes WHERE id = ?', (resume_id,))
            resume = cursor.fetchone()
            
            if resume:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Name:** {resume[1]}")
                    st.write(f"**Email:** {resume[2] or 'Not provided'}")
                    st.write(f"**Phone:** {resume[3] or 'Not provided'}")
                    st.write(f"**Experience:** {resume[5]} years")
                
                with col2:
                    st.write(f"**Skills:** {resume[4]}")
                    st.write(f"**Uploaded:** {resume[7]}")
                
                st.write(f"**Summary:** {resume[6]}")
                
                # Delete button
                if st.button(f"🗑️ Delete {resume[1]}'s Resume", type="secondary"):
                    cursor.execute('DELETE FROM evaluations WHERE resume_id = ?', (resume_id,))
                    cursor.execute('DELETE FROM resumes WHERE id = ?', (resume_id,))
                    processor.conn.commit()
                    st.success(f"Resume for {resume[1]} deleted successfully!")
                    st.rerun()
    else:
        st.info("No resumes uploaded yet.")

def show_upload():
    st.header("📄 Upload Resume")
    
    uploaded_file = st.file_uploader("Choose a resume file", 
                                   type=['txt', 'pdf', 'doc', 'docx'],
                                   help="Upload PDF, DOC, DOCX, or TXT files")
    
    if uploaded_file is not None:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_path = tmp_file.name
        
        try:
            # Read file content
            if uploaded_file.type == "text/plain":
                text = uploaded_file.getvalue().decode("utf-8")
            else:
                # For other formats, read as text (simplified)
                with open(tmp_path, 'rb') as f:
                    text = f.read().decode('utf-8', errors='ignore')
            
            # Extract resume information
            resume_data = processor.extract_resume_info(text, uploaded_file.name)
            
            # Display extracted information
            st.subheader("Extracted Information")
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Name:** {resume_data['candidate_name']}")
                st.write(f"**Email:** {resume_data['email'] or 'Not found'}")
                st.write(f"**Phone:** {resume_data['phone'] or 'Not found'}")
            
            with col2:
                st.write(f"**Experience:** {resume_data['experience_years']} years")
                st.write(f"**Skills:** {resume_data['skills'] or 'None detected'}")
            
            st.write(f"**Summary:** {resume_data['summary']}")
            
            # Save to database
            if st.button("💾 Save Resume", type="primary"):
                cursor = processor.conn.cursor()
                cursor.execute('''
                    INSERT INTO resumes (candidate_name, email, phone, skills, experience_years, summary, uploaded_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    resume_data['candidate_name'],
                    resume_data['email'],
                    resume_data['phone'],
                    resume_data['skills'],
                    resume_data['experience_years'],
                    resume_data['summary'],
                    datetime.now().isoformat()
                ))
                processor.conn.commit()
                
                st.success(f"✅ Resume for {resume_data['candidate_name']} saved successfully!")
                
        except Exception as e:
            st.error(f"Error processing file: {str(e)}")
        
        finally:
            # Clean up temp file
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

def show_evaluate():
    st.header("🎯 Batch Evaluation")
    
    cursor = processor.conn.cursor()
    
    # Get jobs for selection
    cursor.execute('SELECT id, title, location FROM jobs')
    jobs = cursor.fetchall()
    
    if not jobs:
        st.warning("No jobs available. Please add jobs first.")
        return
    
    # Job selection
    selected_job = st.selectbox("Select a job for evaluation:",
                              options=jobs,
                              format_func=lambda x: f"{x[1]} - {x[2]}")
    
    if selected_job and st.button("🚀 Start Evaluation", type="primary"):
        job_id = selected_job[0]
        
        # Get job details
        cursor.execute('SELECT * FROM jobs WHERE id = ?', (job_id,))
        job_data = cursor.fetchone()
        
        if job_data:
            job_info = {
                'id': job_data[0],
                'title': job_data[1],
                'skills_required': job_data[6],
                'experience_min': job_data[7],
                'experience_max': job_data[8]
            }
            
            # Get all resumes
            cursor.execute('SELECT * FROM resumes')
            resumes = cursor.fetchall()
            
            if resumes:
                st.subheader("Evaluation Results")
                
                # Clear previous evaluations for this job
                cursor.execute('DELETE FROM evaluations WHERE job_id = ?', (job_id,))
                
                results = []
                progress_bar = st.progress(0)
                
                for i, resume in enumerate(resumes):
                    resume_data = {
                        'id': resume[0],
                        'candidate_name': resume[1],
                        'skills': resume[4],
                        'experience_years': resume[5]
                    }
                    
                    # Evaluate resume
                    evaluation = processor.evaluate_resume(resume_data, job_info)
                    
                    # Save evaluation
                    cursor.execute('''
                        INSERT INTO evaluations 
                        (job_id, resume_id, candidate_name, relevance_score, skills_match_score, 
                         experience_match_score, overall_fit, matched_skills, missing_skills, recommendations)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        job_id, resume_data['id'], resume_data['candidate_name'],
                        evaluation['relevance_score'], evaluation['skills_match_score'],
                        evaluation['experience_match_score'], evaluation['overall_fit'],
                        evaluation['matched_skills'], evaluation['missing_skills'],
                        evaluation['recommendations']
                    ))
                    
                    results.append({
                        'Candidate': resume_data['candidate_name'],
                        'Score': f"{evaluation['relevance_score']}%",
                        'Fit': evaluation['overall_fit'],
                        'Skills Match': f"{evaluation['skills_match_score']}%",
                        'Experience Match': f"{evaluation['experience_match_score']}%",
                        'Recommendations': evaluation['recommendations']
                    })
                    
                    progress_bar.progress((i + 1) / len(resumes))
                
                processor.conn.commit()
                
                # Display results
                df = pd.DataFrame(results)
                df = df.sort_values('Score', ascending=False, key=lambda x: x.str.rstrip('%').astype(float))
                
                st.dataframe(df, use_container_width=True)
                
                # Summary
                st.subheader("Summary")
                high_fit = len([r for r in results if r['Fit'] == 'High'])
                medium_fit = len([r for r in results if r['Fit'] == 'Medium'])
                low_fit = len([r for r in results if r['Fit'] == 'Low'])
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("High Fit", high_fit)
                with col2:
                    st.metric("Medium Fit", medium_fit)
                with col3:
                    st.metric("Low Fit", low_fit)
                
            else:
                st.warning("No resumes available for evaluation.")

if __name__ == "__main__":
    main()
