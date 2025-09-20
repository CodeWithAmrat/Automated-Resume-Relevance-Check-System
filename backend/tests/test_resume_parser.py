import unittest
import os
import tempfile
from unittest.mock import patch, MagicMock
from services.resume_parser import ResumeParser

class TestResumeParser(unittest.TestCase):
    def setUp(self):
        self.parser = ResumeParser()
    
    def test_extract_contact_info(self):
        """Test contact information extraction"""
        sample_text = """
        John Smith
        Email: john.smith@email.com
        Phone: +1-555-123-4567
        Software Engineer with 5 years experience
        """
        
        contact_info = self.parser.extract_contact_info(sample_text)
        
        self.assertEqual(contact_info['name'], 'John Smith')
        self.assertEqual(contact_info['email'], 'john.smith@email.com')
        self.assertIn('555-123-4567', contact_info['phone'])
    
    def test_extract_skills(self):
        """Test skill extraction"""
        sample_text = """
        Technical Skills: Python, Java, React, Node.js, AWS, Docker
        Programming Languages: JavaScript, C++, SQL
        """
        
        skills = self.parser.extract_skills(sample_text)
        
        self.assertIn('python', [skill.lower() for skill in skills])
        self.assertIn('java', [skill.lower() for skill in skills])
        self.assertIn('react', [skill.lower() for skill in skills])
        self.assertIn('aws', [skill.lower() for skill in skills])
    
    def test_extract_experience(self):
        """Test experience extraction"""
        sample_text = """
        I have 5 years of experience in software development.
        Working in the industry since 2019.
        """
        
        experience = self.parser.extract_experience(sample_text)
        
        self.assertGreaterEqual(experience, 4)
        self.assertLessEqual(experience, 6)
    
    def test_extract_education(self):
        """Test education extraction"""
        sample_text = """
        Education:
        Bachelor of Technology in Computer Science
        XYZ University, 2018
        Master of Science in Software Engineering
        ABC University, 2020
        """
        
        education = self.parser.extract_education(sample_text)
        
        self.assertGreater(len(education), 0)
        self.assertTrue(any('bachelor' in edu['degree'].lower() for edu in education))
    
    def test_extract_certifications(self):
        """Test certification extraction"""
        sample_text = """
        Certifications:
        - AWS Certified Solutions Architect
        - Google Cloud Professional
        - Microsoft Azure Fundamentals
        """
        
        certifications = self.parser.extract_certifications(sample_text)
        
        self.assertGreater(len(certifications), 0)
        self.assertTrue(any('aws' in cert.lower() for cert in certifications))
    
    @patch('PyPDF2.PdfReader')
    def test_extract_text_from_pdf(self, mock_pdf_reader):
        """Test PDF text extraction"""
        # Mock PDF reader
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "Sample PDF text content"
        mock_pdf_reader.return_value.pages = [mock_page]
        
        # Create temporary PDF file
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
            temp_file.write(b"dummy pdf content")
            temp_path = temp_file.name
        
        try:
            text = self.parser.extract_text_from_pdf(temp_path)
            self.assertEqual(text.strip(), "Sample PDF text content")
        finally:
            os.unlink(temp_path)
    
    def test_parse_resume_error_handling(self):
        """Test error handling in resume parsing"""
        # Test with non-existent file
        result = self.parser.parse_resume("non_existent_file.pdf", "pdf")
        
        self.assertFalse(result['is_parsed'])
        self.assertIsNotNone(result['parsing_error'])
        self.assertEqual(result['candidate_name'], 'Unknown')

if __name__ == '__main__':
    unittest.main()
