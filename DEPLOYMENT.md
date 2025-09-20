# Deployment Guide

## Quick Start with Docker

### Prerequisites
- Docker and Docker Compose installed
- At least 4GB RAM available
- 10GB free disk space

### 1. Clone and Setup
```bash
git clone <repository-url>
cd automated-resume-relevance-system
cp backend/.env.example backend/.env
```

### 2. Configure Environment
Edit `backend/.env` with your settings:
```env
DATABASE_URL=postgresql://postgres:password@postgres:5432/resume_system
SECRET_KEY=your-secure-secret-key-here
REDIS_URL=redis://redis:6379
```

### 3. Start Services
```bash
docker-compose up -d
```

### 4. Initialize Database
```bash
docker-compose exec backend python -c "from database.database import create_tables; create_tables()"
```

### 5. Access Application
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## Manual Installation

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm

# Setup database
createdb resume_system
python -c "from database.database import create_tables; create_tables()"

# Start server
uvicorn main:app --reload
```

### Frontend Setup
```bash
cd frontend
npm install
npm start
```

## Production Deployment

### Environment Variables
```env
DATABASE_URL=postgresql://user:pass@host:5432/dbname
SECRET_KEY=use-openssl-rand-hex-32-to-generate
REDIS_URL=redis://redis-host:6379
LOG_LEVEL=INFO
```

### Security Considerations
1. Change default passwords
2. Use HTTPS in production
3. Set up proper firewall rules
4. Regular security updates
5. Database backups

### Scaling
- Use load balancer for multiple backend instances
- Redis cluster for high availability
- PostgreSQL read replicas
- CDN for frontend assets

### Monitoring
- Application logs: `/var/log/resume-system/`
- Health checks: `/health` endpoint
- Metrics: Prometheus integration available
- Alerts: Configure for failed batches, high error rates

## Troubleshooting

### Common Issues
1. **Database connection failed**: Check PostgreSQL is running and credentials are correct
2. **spaCy model not found**: Run `python -m spacy download en_core_web_sm`
3. **File upload fails**: Check upload directory permissions
4. **Batch processing stuck**: Check Redis connection and worker processes

### Performance Tuning
- Increase `MAX_CONCURRENT_EVALUATIONS` for faster processing
- Adjust database connection pool size
- Use SSD storage for better I/O performance
- Monitor memory usage during batch processing
