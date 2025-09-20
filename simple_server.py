#!/usr/bin/env python3
"""
Simple HTTP Server for Resume Relevance Check System
Uses only built-in Python libraries - no external dependencies required
"""

import http.server
import socketserver
import json
import urllib.parse
import os
import re
from typing import Dict, List, Any
import sqlite3
from datetime import datetime
import tempfile
import shutil

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
                evaluation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (job_id) REFERENCES jobs (id),
                FOREIGN KEY (resume_id) REFERENCES resumes (id)
            )
        ''')
        
        self.conn.commit()
        
        # Insert sample data if empty
        cursor.execute('SELECT COUNT(*) FROM jobs')
        if cursor.fetchone()[0] == 0:
            self.insert_sample_data()
    
    def insert_sample_data(self):
        """Insert sample jobs and resumes"""
        cursor = self.conn.cursor()
        
        # Sample jobs
        jobs = [
            ('Senior Software Engineer', 'Innomatics Research Labs', 'Hyderabad', 
             'Looking for experienced software engineer with full-stack skills', 
             'Bachelor degree in CS/IT, 3+ years experience in Python and React', 
             'python,react,aws,sql,docker', 3, 7),
            ('Data Scientist', 'Innomatics Research Labs', 'Bangalore',
             'Join our data science team to build ML models and analytics',
             'Masters in Data Science, 2+ years experience in ML and Python',
             'python,machine learning,sql,tensorflow,pandas', 2, 6),
            ('Full Stack Developer', 'Innomatics Research Labs', 'Pune',
             'Develop modern web applications using latest technologies',
             'Experience in JavaScript, React, Node.js and databases',
             'javascript,react,node.js,mongodb,html,css', 1, 5)
        ]
        
        for job in jobs:
            cursor.execute('''
                INSERT INTO jobs (title, company, location, description, requirements, skills_required, experience_min, experience_max)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', job)
        
        # Sample resumes
        resumes = [
            ('John Smith', 'john@email.com', '+91-9876543210', 'python,react,aws,sql,git', 5, 
             'Experienced software engineer with 5 years in Python and React development'),
            ('Sarah Johnson', 'sarah@email.com', '+91-9876543211', 'java,angular,mysql,spring', 3,
             'Full-stack developer with expertise in Java and Angular frameworks'),
            ('Mike Chen', 'mike@email.com', '+91-9876543212', 'python,machine learning,tensorflow,pandas', 4,
             'Data scientist with strong background in ML and statistical analysis'),
            ('Emily Davis', 'emily@email.com', '+91-9876543213', 'javascript,react,node.js,mongodb', 2,
             'Frontend developer specializing in modern JavaScript frameworks'),
            ('Alex Wilson', 'alex@email.com', '+91-9876543214', 'php,mysql,html,css,wordpress', 6,
             'Web developer with extensive experience in PHP and content management')
        ]
        
        for resume in resumes:
            cursor.execute('''
                INSERT INTO resumes (candidate_name, email, phone, skills, experience_years, summary)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', resume)
        
        self.conn.commit()
    
    def calculate_match_score(self, resume_skills: str, job_skills: str, resume_exp: int, job_min_exp: int, job_max_exp: int):
        """Calculate matching score between resume and job"""
        resume_skill_list = [s.strip().lower() for s in resume_skills.split(',') if s.strip()]
        job_skill_list = [s.strip().lower() for s in job_skills.split(',') if s.strip()]
        
        # Skills matching
        matched_skills = set(resume_skill_list).intersection(set(job_skill_list))
        missing_skills = set(job_skill_list) - set(resume_skill_list)
        
        skills_score = (len(matched_skills) / max(len(job_skill_list), 1)) * 100
        
        # Experience matching
        if job_min_exp <= resume_exp <= job_max_exp:
            exp_score = 100
        elif resume_exp < job_min_exp:
            exp_score = max(0, 100 - (job_min_exp - resume_exp) * 20)
        else:
            exp_score = max(70, 100 - (resume_exp - job_max_exp) * 5)
        
        # Overall score
        overall_score = (skills_score * 0.6) + (exp_score * 0.4)
        
        # Fit level
        if overall_score >= 75:
            fit_level = "High"
        elif overall_score >= 50:
            fit_level = "Medium"
        else:
            fit_level = "Low"
        
        # Recommendations
        recommendations = f"Score: {overall_score:.1f}%. "
        if matched_skills:
            recommendations += f"Strong in: {', '.join(list(matched_skills)[:3])}. "
        if missing_skills:
            recommendations += f"Develop: {', '.join(list(missing_skills)[:3])}."
        
        return {
            'relevance_score': round(overall_score, 1),
            'skills_match_score': round(skills_score, 1),
            'experience_match_score': round(exp_score, 1),
            'overall_fit': fit_level,
            'matched_skills': ','.join(matched_skills),
            'missing_skills': ','.join(missing_skills),
            'recommendations': recommendations
        }

class RequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.processor = ResumeProcessor()
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """Handle GET requests"""
        if self.path == '/':
            self.serve_dashboard()
        elif self.path == '/api/jobs':
            self.get_jobs()
        elif self.path == '/api/resumes':
            self.get_resumes()
        elif self.path.startswith('/api/resume/') and not self.path.endswith('/'):
            resume_id = self.path.split('/')[-1]
            self.get_resume_details(resume_id)
        elif self.path.startswith('/api/results/'):
            job_id = self.path.split('/')[-1]
            self.get_results(job_id)
        elif self.path == '/api/stats':
            self.get_stats()
        else:
            self.send_error(404)
    
    def do_POST(self):
        """Handle POST requests"""
        if self.path == '/api/evaluate':
            self.evaluate_batch()
        elif self.path == '/api/upload':
            self.upload_resume()
        else:
            self.send_error(404)
    
    def do_DELETE(self):
        """Handle DELETE requests"""
        if self.path.startswith('/api/resume/'):
            resume_id = self.path.split('/')[-1]
            self.delete_resume(resume_id)
        else:
            self.send_error(404)
    
    def serve_dashboard(self):
        """Serve the main dashboard HTML"""
        html = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Resume Relevance Check System</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f5f5; }
        .header { background: #1976d2; color: white; padding: 1rem; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .container { max-width: 1200px; margin: 2rem auto; padding: 0 1rem; }
        .card { background: white; border-radius: 8px; padding: 1.5rem; margin-bottom: 1.5rem; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1.5rem; }
        .stat-card { text-align: center; padding: 1rem; }
        .stat-number { font-size: 2rem; font-weight: bold; color: #1976d2; }
        .stat-label { color: #666; margin-top: 0.5rem; }
        .btn { background: #1976d2; color: white; border: none; padding: 0.75rem 1.5rem; border-radius: 4px; cursor: pointer; font-size: 1rem; }
        .btn:hover { background: #1565c0; }
        .btn-secondary { background: #666; }
        .btn-secondary:hover { background: #555; }
        .btn-danger { background: #dc3545; }
        .btn-danger:hover { background: #c82333; }
        .btn-small { padding: 0.4rem 0.8rem; font-size: 0.875rem; }
        table { width: 100%; border-collapse: collapse; margin-top: 1rem; }
        th, td { padding: 0.75rem; text-align: left; border-bottom: 1px solid #ddd; }
        th { background: #f8f9fa; font-weight: 600; }
        .fit-high { color: #4caf50; font-weight: bold; }
        .fit-medium { color: #ff9800; font-weight: bold; }
        .fit-low { color: #f44336; font-weight: bold; }
        .loading { text-align: center; padding: 2rem; }
        .success { background: #d4edda; color: #155724; padding: 1rem; border-radius: 4px; margin: 1rem 0; }
        .error { background: #f8d7da; color: #721c24; padding: 1rem; border-radius: 4px; margin: 1rem 0; }
        .tabs { display: flex; border-bottom: 2px solid #ddd; margin-bottom: 1rem; }
        .tab { padding: 1rem 2rem; cursor: pointer; border-bottom: 2px solid transparent; }
        .tab.active { border-bottom-color: #1976d2; color: #1976d2; font-weight: bold; }
        .tab-content { display: none; }
        .tab-content.active { display: block; }
        .modal { display: none; position: fixed; z-index: 1000; left: 0; top: 0; width: 100%; height: 100%; background-color: rgba(0,0,0,0.5); }
        .modal-content { background-color: white; margin: 5% auto; padding: 2rem; border-radius: 8px; width: 80%; max-width: 600px; max-height: 80%; overflow-y: auto; }
        .modal-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; border-bottom: 1px solid #ddd; padding-bottom: 1rem; }
        .modal-title { margin: 0; color: #1976d2; }
        .close { font-size: 2rem; cursor: pointer; color: #666; }
        .close:hover { color: #000; }
        .resume-detail { margin-bottom: 1rem; }
        .resume-detail h4 { margin: 0 0 0.5rem 0; color: #333; }
        .resume-detail p { margin: 0; color: #666; line-height: 1.5; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🎯 Resume Relevance Check System</h1>
        <p>AI-Powered Recruitment for Innomatics Research Labs</p>
    </div>
    
    <div class="container">
        <div class="tabs">
            <div class="tab active" onclick="showTab('dashboard')">Dashboard</div>
            <div class="tab" onclick="showTab('jobs')">Jobs</div>
            <div class="tab" onclick="showTab('resumes')">Resumes</div>
            <div class="tab" onclick="showTab('evaluate')">Evaluate</div>
        </div>
        
        <!-- Dashboard Tab -->
        <div id="dashboard" class="tab-content active">
            <div class="grid">
                <div class="card stat-card">
                    <div class="stat-number" id="totalJobs">-</div>
                    <div class="stat-label">Active Jobs</div>
                </div>
                <div class="card stat-card">
                    <div class="stat-number" id="totalResumes">-</div>
                    <div class="stat-label">Total Resumes</div>
                </div>
                <div class="card stat-card">
                    <div class="stat-number" id="totalEvaluations">-</div>
                    <div class="stat-label">Evaluations</div>
                </div>
                <div class="card stat-card">
                    <div class="stat-number" id="avgScore">-</div>
                    <div class="stat-label">Avg Score</div>
                </div>
            </div>
            
            <div class="card">
                <h3>Recent Evaluations</h3>
                <div id="recentEvaluations">Loading...</div>
            </div>
        </div>
        
        <!-- Jobs Tab -->
        <div id="jobs" class="tab-content">
            <div class="card">
                <h3>Job Postings</h3>
                <div id="jobsList">Loading...</div>
            </div>
        </div>
        
        <!-- Resumes Tab -->
        <div id="resumes" class="tab-content">
            <div class="card">
                <h3>Upload New Resume</h3>
                <div style="border: 2px dashed #ddd; padding: 2rem; text-align: center; margin-bottom: 1rem; border-radius: 8px;" id="uploadArea">
                    <input type="file" id="resumeFile" accept=".pdf,.doc,.docx,.txt" style="display: none;" onchange="handleFileSelect(event)">
                    <div onclick="document.getElementById('resumeFile').click()" style="cursor: pointer;">
                        <div style="font-size: 3rem; color: #1976d2; margin-bottom: 1rem;">📄</div>
                        <p><strong>Click to select resume file</strong></p>
                        <p style="color: #666; margin-top: 0.5rem;">Supports PDF, DOC, DOCX, TXT files</p>
                    </div>
                </div>
                <div id="uploadStatus"></div>
            </div>
            
            <div class="card">
                <h3>Candidate Resumes</h3>
                <div id="resumesList">Loading...</div>
            </div>
        </div>
        
        <!-- Evaluate Tab -->
        <div id="evaluate" class="tab-content">
            <div class="card">
                <h3>Batch Evaluation</h3>
                <p>Select a job and evaluate all candidates:</p>
                <div style="margin: 1rem 0;">
                    <select id="jobSelect" style="padding: 0.5rem; margin-right: 1rem; width: 300px;">
                        <option value="">Select a job...</option>
                    </select>
                    <button class="btn" onclick="runEvaluation()">Start Evaluation</button>
                </div>
                <div id="evaluationResults"></div>
            </div>
        </div>
    </div>
    
    <!-- Resume Detail Modal -->
    <div id="resumeModal" class="modal">
        <div class="modal-content">
            <div class="modal-header">
                <h2 class="modal-title" id="modalTitle">Resume Details</h2>
                <span class="close" onclick="closeResumeModal()">&times;</span>
            </div>
            <div id="resumeDetails">
                <!-- Resume details will be loaded here -->
            </div>
        </div>
    </div>
    
    <script>
        // Tab functionality
        function showTab(tabName) {
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
            event.target.classList.add('active');
            document.getElementById(tabName).classList.add('active');
            
            if (tabName === 'dashboard') loadDashboard();
            if (tabName === 'jobs') loadJobs();
            if (tabName === 'resumes') loadResumes();
            if (tabName === 'evaluate') loadEvaluateTab();
        }
        
        // Load dashboard data
        async function loadDashboard() {
            try {
                const stats = await fetch('/api/stats').then(r => r.json());
                document.getElementById('totalJobs').textContent = stats.total_jobs;
                document.getElementById('totalResumes').textContent = stats.total_resumes;
                document.getElementById('totalEvaluations').textContent = stats.total_evaluations;
                document.getElementById('avgScore').textContent = stats.avg_score + '%';
                
                const evaluations = await fetch('/api/results/1').then(r => r.json());
                const html = evaluations.slice(0, 5).map(e => 
                    `<div style="padding: 0.5rem; border-left: 3px solid ${getFitColor(e.overall_fit)};">
                        <strong>${e.candidate_name}</strong> - ${e.relevance_score}% (${e.overall_fit} Fit)
                    </div>`
                ).join('');
                document.getElementById('recentEvaluations').innerHTML = html || 'No evaluations yet';
            } catch (e) {
                console.error('Error loading dashboard:', e);
            }
        }
        
        // Load jobs
        async function loadJobs() {
            try {
                const jobs = await fetch('/api/jobs').then(r => r.json());
                const html = `<table>
                    <thead><tr><th>Title</th><th>Location</th><th>Required Skills</th><th>Experience</th></tr></thead>
                    <tbody>${jobs.map(j => 
                        `<tr>
                            <td><strong>${j.title}</strong><br><small>${j.company}</small></td>
                            <td>${j.location}</td>
                            <td>${j.skills_required}</td>
                            <td>${j.experience_min}-${j.experience_max} years</td>
                        </tr>`
                    ).join('')}</tbody>
                </table>`;
                document.getElementById('jobsList').innerHTML = html;
            } catch (e) {
                document.getElementById('jobsList').innerHTML = 'Error loading jobs';
            }
        }
        
        // Handle file selection
        function handleFileSelect(event) {
            const file = event.target.files[0];
            if (!file) return;
            
            const statusDiv = document.getElementById('uploadStatus');
            statusDiv.innerHTML = '<div class="loading">Uploading and processing resume...</div>';
            
            const formData = new FormData();
            formData.append('resume', file);
            
            fetch('/api/upload', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    statusDiv.innerHTML = `<div class="success">✅ Resume uploaded successfully! Candidate: ${data.candidate_name}</div>`;
                    loadResumes(); // Refresh the resume list
                } else {
                    statusDiv.innerHTML = `<div class="error">❌ Upload failed: ${data.error}</div>`;
                }
            })
            .catch(error => {
                statusDiv.innerHTML = `<div class="error">❌ Upload failed: ${error.message}</div>`;
            });
        }
        
        // Delete resume function
        async function deleteResume(resumeId, candidateName) {
            if (!confirm(`Are you sure you want to delete ${candidateName}'s resume? This action cannot be undone.`)) {
                return;
            }
            
            try {
                const response = await fetch(`/api/resume/${resumeId}`, {
                    method: 'DELETE'
                });
                
                const result = await response.json();
                if (result.success) {
                    loadResumes(); // Refresh the list
                    document.getElementById('uploadStatus').innerHTML = `<div class="success">✅ Resume for ${candidateName} deleted successfully</div>`;
                } else {
                    document.getElementById('uploadStatus').innerHTML = `<div class="error">❌ Failed to delete resume: ${result.error}</div>`;
                }
            } catch (error) {
                document.getElementById('uploadStatus').innerHTML = `<div class="error">❌ Error deleting resume: ${error.message}</div>`;
            }
        }
        
        // View resume details
        async function viewResume(resumeId) {
            try {
                const response = await fetch(`/api/resume/${resumeId}`);
                const resume = await response.json();
                
                if (resume.success === false) {
                    alert('Error loading resume details');
                    return;
                }
                
                document.getElementById('modalTitle').textContent = `${resume.candidate_name} - Resume Details`;
                
                const detailsHtml = `
                    <div class="resume-detail">
                        <h4>👤 Personal Information</h4>
                        <p><strong>Name:</strong> ${resume.candidate_name}</p>
                        <p><strong>Email:</strong> ${resume.email || 'Not provided'}</p>
                        <p><strong>Phone:</strong> ${resume.phone || 'Not provided'}</p>
                        <p><strong>Experience:</strong> ${resume.experience_years} years</p>
                    </div>
                    
                    <div class="resume-detail">
                        <h4>🛠️ Skills</h4>
                        <p>${resume.skills || 'No skills listed'}</p>
                    </div>
                    
                    <div class="resume-detail">
                        <h4>📄 Resume Summary</h4>
                        <p>${resume.summary || 'No summary available'}</p>
                    </div>
                    
                    <div class="resume-detail">
                        <h4>📅 Upload Information</h4>
                        <p><strong>Uploaded:</strong> ${new Date(resume.uploaded_at).toLocaleString()}</p>
                        <p><strong>Status:</strong> Processed and ready for evaluation</p>
                    </div>
                `;
                
                document.getElementById('resumeDetails').innerHTML = detailsHtml;
                document.getElementById('resumeModal').style.display = 'block';
                
            } catch (error) {
                alert('Error loading resume details: ' + error.message);
            }
        }
        
        // Close resume modal
        function closeResumeModal() {
            document.getElementById('resumeModal').style.display = 'none';
        }
        
        // Close modal when clicking outside
        window.onclick = function(event) {
            const modal = document.getElementById('resumeModal');
            if (event.target === modal) {
                modal.style.display = 'none';
            }
        }
        
        // Load resumes
        async function loadResumes() {
            try {
                const resumes = await fetch('/api/resumes').then(r => r.json());
                const html = `<table>
                    <thead><tr><th>Candidate</th><th>Skills</th><th>Experience</th><th>Contact</th><th>Actions</th></tr></thead>
                    <tbody>${resumes.map(r => 
                        `<tr>
                            <td><strong>${r.candidate_name}</strong></td>
                            <td>${r.skills}</td>
                            <td>${r.experience_years} years</td>
                            <td>${r.email}<br>${r.phone}</td>
                            <td>
                                <button class="btn btn-small" onclick="viewResume(${r.id})" style="margin-right: 0.5rem;">
                                    👁️ View
                                </button>
                                <button class="btn btn-danger btn-small" onclick="deleteResume(${r.id}, '${r.candidate_name}')">
                                    🗑️ Delete
                                </button>
                            </td>
                        </tr>`
                    ).join('')}</tbody>
                </table>`;
                document.getElementById('resumesList').innerHTML = html;
            } catch (e) {
                document.getElementById('resumesList').innerHTML = 'Error loading resumes';
            }
        }
        
        // Load evaluate tab
        async function loadEvaluateTab() {
            try {
                const jobs = await fetch('/api/jobs').then(r => r.json());
                const select = document.getElementById('jobSelect');
                select.innerHTML = '<option value="">Select a job...</option>' + 
                    jobs.map(j => `<option value="${j.id}">${j.title} - ${j.location}</option>`).join('');
            } catch (e) {
                console.error('Error loading jobs for evaluation:', e);
            }
        }
        
        // Run evaluation
        async function runEvaluation() {
            const jobId = document.getElementById('jobSelect').value;
            if (!jobId) {
                alert('Please select a job first');
                return;
            }
            
            const resultsDiv = document.getElementById('evaluationResults');
            resultsDiv.innerHTML = '<div class="loading">Running evaluation...</div>';
            
            try {
                const response = await fetch('/api/evaluate', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({job_id: parseInt(jobId)})
                });
                
                if (response.ok) {
                    const results = await fetch(`/api/results/${jobId}`).then(r => r.json());
                    displayResults(results);
                } else {
                    resultsDiv.innerHTML = '<div class="error">Evaluation failed</div>';
                }
            } catch (e) {
                resultsDiv.innerHTML = '<div class="error">Error running evaluation</div>';
            }
        }
        
        // Display results
        function displayResults(results) {
            const html = `
                <div class="success">Evaluation completed! ${results.length} candidates processed.</div>
                <table>
                    <thead>
                        <tr>
                            <th>Rank</th>
                            <th>Candidate</th>
                            <th>Score</th>
                            <th>Fit</th>
                            <th>Skills Match</th>
                            <th>Recommendations</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${results.sort((a,b) => b.relevance_score - a.relevance_score).map((r, i) => 
                            `<tr>
                                <td>${i + 1}</td>
                                <td><strong>${r.candidate_name}</strong></td>
                                <td>${r.relevance_score}%</td>
                                <td class="fit-${r.overall_fit.toLowerCase()}">${r.overall_fit}</td>
                                <td>${r.skills_match_score}%</td>
                                <td>${r.recommendations}</td>
                            </tr>`
                        ).join('')}
                    </tbody>
                </table>
            `;
            document.getElementById('evaluationResults').innerHTML = html;
        }
        
        // Helper functions
        function getFitColor(fit) {
            return fit === 'High' ? '#4caf50' : fit === 'Medium' ? '#ff9800' : '#f44336';
        }
        
        // Load dashboard on page load
        loadDashboard();
    </script>
</body>
</html>
        '''
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())
    
    def get_jobs(self):
        """Get all jobs"""
        cursor = self.processor.conn.cursor()
        cursor.execute('SELECT * FROM jobs ORDER BY created_at DESC')
        jobs = []
        for row in cursor.fetchall():
            jobs.append({
                'id': row[0], 'title': row[1], 'company': row[2], 'location': row[3],
                'description': row[4], 'requirements': row[5], 'skills_required': row[6],
                'experience_min': row[7], 'experience_max': row[8]
            })
        
        self.send_json_response(jobs)
    
    def get_resumes(self):
        """Get all resumes"""
        cursor = self.processor.conn.cursor()
        cursor.execute('SELECT * FROM resumes ORDER BY uploaded_at DESC')
        resumes = []
        for row in cursor.fetchall():
            resumes.append({
                'id': row[0], 'candidate_name': row[1], 'email': row[2], 'phone': row[3],
                'skills': row[4], 'experience_years': row[5], 'summary': row[6]
            })
        
        self.send_json_response(resumes)
    
    def get_resume_details(self, resume_id):
        """Get detailed information for a specific resume"""
        try:
            cursor = self.processor.conn.cursor()
            cursor.execute('SELECT * FROM resumes WHERE id = ?', (resume_id,))
            row = cursor.fetchone()
            
            if not row:
                self.send_json_response({'success': False, 'error': 'Resume not found'})
                return
            
            resume_details = {
                'id': row[0],
                'candidate_name': row[1],
                'email': row[2],
                'phone': row[3],
                'skills': row[4],
                'experience_years': row[5],
                'summary': row[6],
                'uploaded_at': row[7]
            }
            
            self.send_json_response(resume_details)
            
        except Exception as e:
            self.send_json_response({'success': False, 'error': str(e)})
    
    def get_results(self, job_id):
        """Get evaluation results for a job"""
        cursor = self.processor.conn.cursor()
        cursor.execute('SELECT * FROM evaluations WHERE job_id = ? ORDER BY relevance_score DESC', (job_id,))
        results = []
        for row in cursor.fetchall():
            results.append({
                'id': row[0], 'job_id': row[1], 'resume_id': row[2], 'candidate_name': row[3],
                'relevance_score': row[4], 'skills_match_score': row[5], 'experience_match_score': row[6],
                'overall_fit': row[7], 'matched_skills': row[8], 'missing_skills': row[9],
                'recommendations': row[10]
            })
        
        self.send_json_response(results)
    
    def get_stats(self):
        """Get dashboard statistics"""
        cursor = self.processor.conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM jobs')
        total_jobs = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM resumes')
        total_resumes = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*), AVG(relevance_score) FROM evaluations')
        eval_stats = cursor.fetchone()
        total_evaluations = eval_stats[0] or 0
        avg_score = round(eval_stats[1] or 0, 1)
        
        stats = {
            'total_jobs': total_jobs,
            'total_resumes': total_resumes,
            'total_evaluations': total_evaluations,
            'avg_score': avg_score
        }
        
        self.send_json_response(stats)
    
    def delete_resume(self, resume_id):
        """Delete a resume and its associated evaluations"""
        try:
            cursor = self.processor.conn.cursor()
            
            # First, get the candidate name for confirmation
            cursor.execute('SELECT candidate_name FROM resumes WHERE id = ?', (resume_id,))
            result = cursor.fetchone()
            
            if not result:
                self.send_json_response({'success': False, 'error': 'Resume not found'})
                return
            
            candidate_name = result[0]
            
            # Delete associated evaluations first (foreign key constraint)
            cursor.execute('DELETE FROM evaluations WHERE resume_id = ?', (resume_id,))
            
            # Delete the resume
            cursor.execute('DELETE FROM resumes WHERE id = ?', (resume_id,))
            
            self.processor.conn.commit()
            
            self.send_json_response({
                'success': True,
                'message': f'Resume for {candidate_name} deleted successfully'
            })
            
        except Exception as e:
            self.send_json_response({'success': False, 'error': str(e)})
    
    def upload_resume(self):
        """Handle resume file upload"""
        try:
            # Parse multipart form data
            content_type = self.headers.get('Content-Type', '')
            if not content_type.startswith('multipart/form-data'):
                self.send_json_response({'success': False, 'error': 'Invalid content type'})
                return
            
            # Get content length
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length == 0:
                self.send_json_response({'success': False, 'error': 'No file data'})
                return
            
            # Read the uploaded data
            post_data = self.rfile.read(content_length)
            
            # Parse the multipart data
            boundary = content_type.split('boundary=')[1].encode()
            parts = post_data.split(b'--' + boundary)
            
            file_data = None
            filename = None
            
            for part in parts:
                if b'Content-Disposition: form-data' in part and b'filename=' in part:
                    # Extract filename
                    lines = part.split(b'\r\n')
                    for line in lines:
                        if b'filename=' in line:
                            filename = line.decode().split('filename="')[1].split('"')[0]
                            break
                    
                    # Extract file content (after double CRLF)
                    content_start = part.find(b'\r\n\r\n')
                    if content_start != -1:
                        file_data = part[content_start + 4:]
                        # Remove trailing CRLF
                        if file_data.endswith(b'\r\n'):
                            file_data = file_data[:-2]
                    break
            
            if not file_data or not filename:
                self.send_json_response({'success': False, 'error': 'No file found in upload'})
                return
            
            # Save file temporarily and process
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1]) as temp_file:
                temp_file.write(file_data)
                temp_path = temp_file.name
            
            try:
                # Process the resume (simplified text extraction)
                file_ext = os.path.splitext(filename)[1].lower()
                if file_ext == '.txt':
                    with open(temp_path, 'r', encoding='utf-8', errors='ignore') as f:
                        text = f.read()
                else:
                    # For other formats, treat as text for now
                    with open(temp_path, 'rb') as f:
                        text = f.read().decode('utf-8', errors='ignore')
                
                # Extract basic information using regex
                resume_data = self.extract_resume_info(text, filename)
                
                # Save to database
                cursor = self.processor.conn.cursor()
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
                self.processor.conn.commit()
                
                self.send_json_response({
                    'success': True,
                    'candidate_name': resume_data['candidate_name'],
                    'message': 'Resume uploaded and processed successfully'
                })
                
            finally:
                # Clean up temp file
                os.unlink(temp_path)
                
        except Exception as e:
            self.send_json_response({'success': False, 'error': str(e)})
    
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
        for skill in self.processor.skills_db:
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
    
    def evaluate_batch(self):
        """Run batch evaluation"""
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data.decode())
        
        job_id = data.get('job_id')
        
        # Get job details
        cursor = self.processor.conn.cursor()
        cursor.execute('SELECT * FROM jobs WHERE id = ?', (job_id,))
        job = cursor.fetchone()
        
        if not job:
            self.send_error(404, "Job not found")
            return
        
        # Get all resumes
        cursor.execute('SELECT * FROM resumes')
        resumes = cursor.fetchall()
        
        # Clear previous evaluations for this job
        cursor.execute('DELETE FROM evaluations WHERE job_id = ?', (job_id,))
        
        # Evaluate each resume
        for resume in resumes:
            result = self.processor.calculate_match_score(
                resume[4],  # skills
                job[6],     # job skills_required
                resume[5],  # experience_years
                job[7],     # experience_min
                job[8]      # experience_max
            )
            
            cursor.execute('''
                INSERT INTO evaluations 
                (job_id, resume_id, candidate_name, relevance_score, skills_match_score, 
                 experience_match_score, overall_fit, matched_skills, missing_skills, recommendations)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                job_id, resume[0], resume[1], result['relevance_score'],
                result['skills_match_score'], result['experience_match_score'],
                result['overall_fit'], result['matched_skills'], result['missing_skills'],
                result['recommendations']
            ))
        
        self.processor.conn.commit()
        
        self.send_json_response({'status': 'success', 'message': f'Evaluated {len(resumes)} resumes'})
    
    def send_json_response(self, data):
        """Send JSON response"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

def start_server(port=8000):
    """Start the HTTP server"""
    handler = RequestHandler
    
    with socketserver.TCPServer(("", port), handler) as httpd:
        print(f"🚀 Resume Relevance Check System")
        print(f"📊 Dashboard: http://localhost:{port}")
        print(f"🔧 Server running on port {port}")
        print(f"📋 Sample data loaded with 3 jobs and 5 resumes")
        print(f"💡 Click 'Evaluate' tab to test the AI matching!")
        print(f"\nPress Ctrl+C to stop the server")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 Server stopped")

if __name__ == "__main__":
    start_server()
