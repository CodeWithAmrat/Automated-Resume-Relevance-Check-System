# Setup Options for Resume Relevance Check System

## Option 1: Install Docker (Recommended)

### Download Docker Desktop:
1. Visit: https://www.docker.com/products/docker-desktop/
2. Download Docker Desktop for Windows
3. Install and restart your computer
4. Run `start.bat` to launch the system automatically

### Benefits:
- One-click setup with all dependencies
- Isolated environment
- Production-ready deployment
- Easy scaling and management

## Option 2: Manual Installation (Development)

### Prerequisites:
- Python 3.9+ 
- Node.js 16+
- PostgreSQL 13+
- Redis (optional but recommended)

### Backend Setup:
```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm

# Setup PostgreSQL database
# Create database: resume_system
# Update DATABASE_URL in .env

python -c "from database.database import create_tables; create_tables()"
uvicorn main:app --reload
```

### Frontend Setup:
```bash
cd frontend
npm install
npm start
```

## Option 3: Cloud Deployment

### Deploy to Heroku:
```bash
# Install Heroku CLI
heroku create resume-relevance-system
heroku addons:create heroku-postgresql:hobby-dev
heroku addons:create heroku-redis:hobby-dev
git push heroku main
```

### Deploy to Railway:
1. Connect GitHub repository to Railway
2. Add PostgreSQL and Redis services
3. Set environment variables
4. Deploy automatically

## Option 4: Local Development (Simplified)

### Quick Python Setup:
```bash
cd backend
pip install fastapi uvicorn sqlalchemy psycopg2-binary
pip install spacy transformers sentence-transformers
python -m spacy download en_core_web_sm

# Use SQLite for testing (modify database.py)
DATABASE_URL = "sqlite:///./resume_system.db"

python main.py
```

### Access API Documentation:
- Open: http://localhost:8000/docs
- Test endpoints directly from the browser

## Recommended Next Steps:

### For Quick Testing:
1. **Install Docker Desktop** (easiest option)
2. Run the automated setup script
3. Test with sample data

### For Development:
1. Use Option 2 (Manual Installation)
2. Set up development environment
3. Customize and extend features

### For Production:
1. Use Docker deployment
2. Set up proper database and Redis
3. Configure SSL and security settings

## Sample Data for Testing:

### Create Test Job:
```json
{
  "title": "Senior Software Engineer",
  "company": "Innomatics Research Labs",
  "location": "Hyderabad",
  "description": "Looking for experienced developer",
  "requirements": "Python, React, 3+ years experience",
  "skills_required": ["Python", "React", "AWS", "SQL"]
}
```

### Test Resume Content:
- Create sample PDF resumes with different skill sets
- Include candidates with Python/React (high match)
- Include candidates with Java/Angular (medium match)
- Include candidates with PHP/WordPress (low match)

Would you like me to help you with any specific setup option?
