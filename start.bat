@echo off
echo Starting Automated Resume Relevance Check System...
echo.

REM Check if Docker is running
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Docker is not installed or not running
    echo Please install Docker Desktop and try again
    pause
    exit /b 1
)

echo Docker found. Setting up environment...

REM Copy environment file if it doesn't exist
if not exist "backend\.env" (
    echo Creating environment configuration...
    copy "backend\.env.example" "backend\.env"
)

echo.
echo Starting services with Docker Compose...
docker-compose up -d

echo.
echo Waiting for services to start...
timeout /t 30 /nobreak

echo.
echo Initializing database...
docker-compose exec -T backend python -c "from database.database import create_tables; create_tables()"

echo.
echo ========================================
echo System is ready!
echo ========================================
echo Frontend Dashboard: http://localhost:3000
echo Backend API: http://localhost:8000
echo API Documentation: http://localhost:8000/docs
echo.
echo Press any key to open the dashboard...
pause >nul
start http://localhost:3000
