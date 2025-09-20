import PyPDF2
import docx
import re
import spacy
from typing import Dict, List, Optional, Any
import json
from datetime import datetime
import logging

# Load spaCy model
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("Please install spaCy English model: python -m spacy download en_core_web_sm")
    nlp = None

class ResumeParser:
    def __init__(self):
        self.skills_database = self._load_skills_database()
        self.education_keywords = [
            'bachelor', 'master', 'phd', 'doctorate', 'diploma', 'certificate',
            'b.tech', 'm.tech', 'bca', 'mca', 'bba', 'mba', 'b.sc', 'm.sc',
            'engineering', 'computer science', 'information technology', 'software',
            'university', 'college', 'institute', 'school'
        ]
        
    def _load_skills_database(self) -> Dict[str, List[str]]:
        """Load comprehensive skills database categorized by domain"""
        return {
            'programming_languages': [
                'python', 'java', 'javascript', 'c++', 'c#', 'php', 'ruby', 'go',
                'rust', 'kotlin', 'swift', 'typescript', 'scala', 'r', 'matlab'
            ],
            'web_technologies': [
                'html', 'css', 'react', 'angular', 'vue', 'node.js', 'express',
                'django', 'flask', 'spring', 'laravel', 'bootstrap', 'jquery'
            ],
            'databases': [
                'mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch',
                'oracle', 'sql server', 'sqlite', 'cassandra', 'dynamodb'
            ],
            'cloud_platforms': [
                'aws', 'azure', 'google cloud', 'gcp', 'docker', 'kubernetes',
                'jenkins', 'terraform', 'ansible', 'heroku', 'netlify'
            ],
            'data_science': [
                'machine learning', 'deep learning', 'tensorflow', 'pytorch',
                'pandas', 'numpy', 'scikit-learn', 'data analysis', 'statistics'
            ],
            'tools': [
                'git', 'github', 'gitlab', 'jira', 'confluence', 'slack',
                'visual studio', 'intellij', 'eclipse', 'postman'
            ]
        }
    
    def extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF file"""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                return text
        except Exception as e:
            logging.error(f"Error extracting PDF text: {e}")
            return ""
    
    def extract_text_from_docx(self, file_path: str) -> str:
        """Extract text from DOCX file"""
        try:
            doc = docx.Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except Exception as e:
            logging.error(f"Error extracting DOCX text: {e}")
            return ""
    
    def extract_text_from_doc(self, file_path: str) -> str:
        """Extract text from DOC file (basic implementation)"""
        # Note: For production, consider using python-docx2txt or antiword
        try:
            # This is a simplified approach - in production use proper DOC parser
            with open(file_path, 'rb') as file:
                content = file.read()
                # Basic text extraction (not reliable for all DOC files)
                text = content.decode('utf-8', errors='ignore')
                return text
        except Exception as e:
            logging.error(f"Error extracting DOC text: {e}")
            return ""
    
    def extract_contact_info(self, text: str) -> Dict[str, Optional[str]]:
        """Extract contact information from resume text"""
        contact_info = {
            'email': None,
            'phone': None,
            'name': None
        }
        
        # Extract email
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        if emails:
            contact_info['email'] = emails[0]
        
        # Extract phone number
        phone_patterns = [
            r'\+?1?[-.\s]?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}',
            r'\+?91[-.\s]?[0-9]{10}',
            r'[0-9]{10}'
        ]
        for pattern in phone_patterns:
            phones = re.findall(pattern, text)
            if phones:
                contact_info['phone'] = phones[0]
                break
        
        # Extract name (first few words, excluding common resume headers)
        lines = text.split('\n')
        for line in lines[:5]:
            line = line.strip()
            if line and len(line.split()) <= 4 and not any(keyword in line.lower() for keyword in ['resume', 'cv', 'curriculum']):
                # Simple name detection
                if re.match(r'^[A-Za-z\s]+$', line):
                    contact_info['name'] = line
                    break
        
        return contact_info
    
    def extract_skills(self, text: str) -> List[str]:
        """Extract skills from resume text"""
        text_lower = text.lower()
        found_skills = []
        
        # Check all skill categories
        for category, skills in self.skills_database.items():
            for skill in skills:
                if skill.lower() in text_lower:
                    found_skills.append(skill)
        
        # Additional pattern-based skill extraction
        skill_patterns = [
            r'skills?[:\-]?\s*([^.\n]+)',
            r'technologies?[:\-]?\s*([^.\n]+)',
            r'programming languages?[:\-]?\s*([^.\n]+)'
        ]
        
        for pattern in skill_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                # Split by common delimiters
                skills_in_match = re.split(r'[,;|•\n]', match)
                for skill in skills_in_match:
                    skill = skill.strip()
                    if skill and len(skill) < 30:  # Reasonable skill name length
                        found_skills.append(skill)
        
        return list(set(found_skills))  # Remove duplicates
    
    def extract_experience(self, text: str) -> float:
        """Extract years of experience from resume text"""
        experience_patterns = [
            r'(\d+)\+?\s*years?\s*(?:of\s*)?experience',
            r'experience[:\-]?\s*(\d+)\+?\s*years?',
            r'(\d+)\+?\s*years?\s*in\s*(?:the\s*)?(?:field|industry)',
        ]
        
        for pattern in experience_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                try:
                    return float(matches[0])
                except ValueError:
                    continue
        
        # Calculate experience from work history dates
        date_patterns = [
            r'(\d{4})\s*[-–]\s*(\d{4}|present|current)',
            r'(\d{1,2})/(\d{4})\s*[-–]\s*(\d{1,2})/(\d{4})',
        ]
        
        total_experience = 0
        for pattern in date_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                try:
                    if len(match) == 2:  # Year format
                        start_year = int(match[0])
                        end_year = datetime.now().year if match[1].lower() in ['present', 'current'] else int(match[1])
                        total_experience += max(0, end_year - start_year)
                except ValueError:
                    continue
        
        return min(total_experience, 50)  # Cap at 50 years
    
    def extract_education(self, text: str) -> List[Dict[str, str]]:
        """Extract education information from resume text"""
        education = []
        text_lower = text.lower()
        
        # Find education section
        education_section = ""
        education_start = -1
        
        for keyword in ['education', 'academic', 'qualification']:
            if keyword in text_lower:
                education_start = text_lower.find(keyword)
                break
        
        if education_start != -1:
            # Extract text after education keyword
            education_section = text[education_start:education_start + 1000]
        else:
            education_section = text  # Use full text if no education section found
        
        # Extract degree information
        degree_patterns = [
            r'(bachelor|master|phd|doctorate|diploma|certificate|b\.tech|m\.tech|bca|mca|bba|mba|b\.sc|m\.sc)[^.\n]*',
            r'(engineering|computer science|information technology|software)[^.\n]*'
        ]
        
        for pattern in degree_patterns:
            matches = re.findall(pattern, education_section, re.IGNORECASE)
            for match in matches:
                education.append({
                    'degree': match.strip(),
                    'field': 'Not specified',
                    'year': 'Not specified'
                })
        
        return education
    
    def extract_certifications(self, text: str) -> List[str]:
        """Extract certifications from resume text"""
        certifications = []
        
        # Common certification patterns
        cert_patterns = [
            r'certified?\s+([^.\n]+)',
            r'certification[:\-]?\s*([^.\n]+)',
            r'(aws|azure|google|microsoft|oracle|cisco|comptia)[^.\n]*certified?[^.\n]*',
        ]
        
        for pattern in cert_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                cert = match.strip()
                if cert and len(cert) < 100:  # Reasonable certification name length
                    certifications.append(cert)
        
        return list(set(certifications))
    
    def extract_projects(self, text: str) -> List[Dict[str, str]]:
        """Extract project information from resume text"""
        projects = []
        
        # Find projects section
        project_keywords = ['project', 'work', 'portfolio', 'github']
        project_section = ""
        
        for keyword in project_keywords:
            if keyword in text.lower():
                start_idx = text.lower().find(keyword)
                project_section = text[start_idx:start_idx + 2000]
                break
        
        if not project_section:
            project_section = text
        
        # Extract project titles (simple heuristic)
        lines = project_section.split('\n')
        for i, line in enumerate(lines):
            line = line.strip()
            if line and len(line.split()) <= 8 and not line.startswith(('•', '-', '*')):
                # Potential project title
                description = ""
                if i + 1 < len(lines):
                    description = lines[i + 1].strip()
                
                projects.append({
                    'title': line,
                    'description': description[:200]  # Limit description length
                })
        
        return projects[:10]  # Limit to 10 projects
    
    def parse_resume(self, file_path: str, file_type: str) -> Dict[str, Any]:
        """Main method to parse resume and extract all information"""
        try:
            # Extract text based on file type
            if file_type.lower() == 'pdf':
                text = self.extract_text_from_pdf(file_path)
            elif file_type.lower() in ['docx']:
                text = self.extract_text_from_docx(file_path)
            elif file_type.lower() in ['doc']:
                text = self.extract_text_from_doc(file_path)
            else:
                raise ValueError(f"Unsupported file type: {file_type}")
            
            if not text.strip():
                raise ValueError("No text could be extracted from the file")
            
            # Extract all information
            contact_info = self.extract_contact_info(text)
            skills = self.extract_skills(text)
            experience_years = self.extract_experience(text)
            education = self.extract_education(text)
            certifications = self.extract_certifications(text)
            projects = self.extract_projects(text)
            
            # Create summary (first 500 characters of cleaned text)
            summary = re.sub(r'\s+', ' ', text[:500]).strip()
            
            return {
                'candidate_name': contact_info['name'] or 'Unknown',
                'email': contact_info['email'],
                'phone': contact_info['phone'],
                'experience_years': experience_years,
                'skills': skills,
                'education': education,
                'certifications': certifications,
                'projects': projects,
                'summary': summary,
                'work_experience': [],  # To be enhanced with more sophisticated parsing
                'is_parsed': True,
                'parsing_error': None
            }
            
        except Exception as e:
            logging.error(f"Error parsing resume {file_path}: {e}")
            return {
                'candidate_name': 'Unknown',
                'email': None,
                'phone': None,
                'experience_years': 0,
                'skills': [],
                'education': [],
                'certifications': [],
                'projects': [],
                'summary': '',
                'work_experience': [],
                'is_parsed': False,
                'parsing_error': str(e)
            }
