@echo off
echo Setting up Resume Relevance Check System (Local Development)...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed
    echo Please install Python 3.9+ from https://python.org
    pause
    exit /b 1
)

echo Python found. Setting up backend...
cd backend

REM Create virtual environment
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate

REM Install basic dependencies
echo Installing core dependencies...
pip install fastapi uvicorn sqlalchemy python-multipart
pip install PyPDF2 python-docx spacy scikit-learn pandas numpy
pip install sentence-transformers transformers

REM Download spaCy model
echo Downloading language model...
python -m spacy download en_core_web_sm

REM Create SQLite version for testing
echo Creating local database configuration...
if not exist ".env" (
    echo DATABASE_URL=sqlite:///./resume_system.db > .env
    echo SECRET_KEY=dev-secret-key-change-in-production >> .env
    echo LOG_LEVEL=INFO >> .env
)

REM Initialize database
echo Initializing database...
python -c "from database.database import create_tables; create_tables()"

echo.
echo ========================================
echo Backend setup complete!
echo ========================================
echo Starting FastAPI server...
echo API will be available at: http://localhost:8000
echo API Documentation: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo.

uvicorn main:app --reload --host 0.0.0.0 --port 8000
