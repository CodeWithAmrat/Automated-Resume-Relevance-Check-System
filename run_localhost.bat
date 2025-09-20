@echo off
echo Starting Resume Relevance Check System on Localhost...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed
    echo Please install Python 3.9+ from https://python.org
    pause
    exit /b 1
)

echo Setting up backend...
cd backend

REM Install minimal dependencies
echo Installing dependencies...
pip install fastapi uvicorn sqlalchemy python-multipart
pip install PyPDF2 python-docx pandas numpy

REM Create environment file
if not exist ".env" (
    echo DATABASE_URL=sqlite:///./resume_system.db > .env
    echo SECRET_KEY=dev-secret-key >> .env
)

REM Initialize database
echo Initializing database...
python -c "from database.database import create_tables; create_tables()" 2>nul

echo.
echo Starting backend server...
echo Backend API: http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo.

start /B uvicorn main:app --reload --host 0.0.0.0 --port 8000

echo Waiting for backend to start...
timeout /t 5 /nobreak >nul

REM Check if Node.js is available for frontend
cd ..\frontend
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo Node.js not found. Opening API documentation instead...
    start http://localhost:8000/docs
) else (
    echo.
    echo Setting up frontend...
    if not exist "node_modules" (
        echo Installing frontend dependencies...
        npm install --silent
    )
    
    echo Starting frontend server...
    echo Frontend: http://localhost:3000
    start /B npm start
    
    echo Waiting for frontend to start...
    timeout /t 10 /nobreak >nul
    
    echo Opening dashboard...
    start http://localhost:3000
)

echo.
echo ========================================
echo System is running on localhost!
echo ========================================
echo Backend API: http://localhost:8000
echo Frontend Dashboard: http://localhost:3000
echo API Documentation: http://localhost:8000/docs
echo.
echo Press any key to stop the servers...
pause >nul

REM Kill the processes
taskkill /F /IM "uvicorn.exe" 2>nul
taskkill /F /IM "node.exe" 2>nul
echo Servers stopped.
