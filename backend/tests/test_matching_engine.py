import unittest
from unittest.mock import patch, MagicMock
from services.matching_engine import ResumeJobMatcher, MatchingResult

class TestMatchingEngine(unittest.TestCase):
    def setUp(self):
        self.matcher = ResumeJobMatcher()
    
    def test_extract_skills_from_jd(self):
        """Test skill extraction from job description"""
        jd_text = """
        We are looking for a software engineer with the following required skills:
        Python, React, AWS, Docker, SQL
        
        Preferred skills include:
        Kubernetes, GraphQL, TypeScript
        """
        
        requirements = "Bachelor's degree required. 3+ years experience preferred."
        
        skills = self.matcher.extract_skills_from_jd(jd_text, requirements)
        
        self.assertIn('required', skills)
        self.assertIn('preferred', skills)
        self.assertTrue(len(skills['required']) > 0)
    
    def test_calculate_skills_match(self):
        """Test skills matching calculation"""
        resume_skills = ['Python', 'React', 'JavaScript', 'SQL', 'Git']
        jd_skills = {
            'required': ['Python', 'React', 'SQL'],
            'preferred': ['JavaScript', 'Docker', 'AWS']
        }
        
        score, matched, missing = self.matcher.calculate_skills_match(resume_skills, jd_skills)
        
        self.assertGreater(score, 50)  # Should have decent match
        self.assertIn('python', [s.lower() for s in matched])
        self.assertIn('react', [s.lower() for s in matched])
        self.assertIn('docker', [s.lower() for s in missing])
    
    def test_calculate_experience_match(self):
        """Test experience matching"""
        # Perfect match
        score = self.matcher.calculate_experience_match(5, 3, 7)
        self.assertEqual(score, 100.0)
        
        # Underqualified
        score = self.matcher.calculate_experience_match(2, 5, 10)
        self.assertLess(score, 100.0)
        
        # Overqualified
        score = self.matcher.calculate_experience_match(12, 3, 7)
        self.assertLess(score, 100.0)
        self.assertGreaterEqual(score, 70.0)  # Less penalty for overqualification
    
    def test_calculate_education_match(self):
        """Test education matching"""
        resume_education = [
            {'degree': 'Bachelor of Technology in Computer Science', 'field': 'CS', 'year': '2020'},
            {'degree': 'Master of Science in Software Engineering', 'field': 'SE', 'year': '2022'}
        ]
        
        jd_requirements = "Bachelor's degree in Computer Science or related field required"
        
        score = self.matcher.calculate_education_match(resume_education, jd_requirements)
        
        self.assertGreater(score, 80)  # Should match well
    
    def test_skills_similarity(self):
        """Test skill similarity matching"""
        # Exact match
        self.assertTrue(self.matcher._skills_similar('python', 'python'))
        
        # Partial match
        self.assertTrue(self.matcher._skills_similar('javascript', 'js'))
        self.assertTrue(self.matcher._skills_similar('react', 'reactjs'))
        
        # No match
        self.assertFalse(self.matcher._skills_similar('python', 'java'))
    
    @patch('sentence_transformers.SentenceTransformer')
    def test_calculate_semantic_similarity(self, mock_transformer):
        """Test semantic similarity calculation"""
        # Mock sentence transformer
        mock_model = MagicMock()
        mock_model.encode.return_value = [[0.1, 0.2, 0.3], [0.15, 0.25, 0.35]]
        mock_transformer.return_value = mock_model
        
        self.matcher.sentence_model = mock_model
        
        resume_text = "Software engineer with Python and React experience"
        jd_text = "Looking for developer with Python and JavaScript skills"
        
        similarity = self.matcher.calculate_semantic_similarity(resume_text, jd_text)
        
        self.assertIsInstance(similarity, float)
        self.assertGreaterEqual(similarity, 0)
        self.assertLessEqual(similarity, 100)
    
    def test_evaluate_resume_complete(self):
        """Test complete resume evaluation"""
        resume_data = {
            'candidate_name': 'John Doe',
            'experience_years': 5,
            'skills': ['Python', 'React', 'SQL', 'Git'],
            'education': [{'degree': 'Bachelor of Computer Science', 'field': 'CS', 'year': '2018'}],
            'summary': 'Experienced software developer with full-stack skills'
        }
        
        job_data = {
            'title': 'Senior Software Engineer',
            'description': 'We need a senior developer with Python and React experience',
            'requirements': 'Bachelor degree required, 3-7 years experience',
            'experience_min': 3,
            'experience_max': 7
        }
        
        result = self.matcher.evaluate_resume(resume_data, job_data)
        
        self.assertIsInstance(result, MatchingResult)
        self.assertGreaterEqual(result.relevance_score, 0)
        self.assertLessEqual(result.relevance_score, 100)
        self.assertIsInstance(result.matched_skills, list)
        self.assertIsInstance(result.missing_skills, list)
        self.assertIsInstance(result.strengths, list)
        self.assertIsInstance(result.weaknesses, list)

if __name__ == '__main__':
    unittest.main()
