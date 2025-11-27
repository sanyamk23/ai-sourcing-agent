# Deployment Guide

## Production Deployment Options

### Option 1: Docker (Recommended)

#### Prerequisites
- Docker 20.10+
- Docker Compose 2.0+

#### Steps

1. **Clone repository**
```bash
git clone <your-repo>
cd linkedin
```

2. **Configure environment**
```bash
cp .env.production .env
# Edit .env with production values
```

3. **Build and run**
```bash
docker-compose up -d
```

4. **Verify**
```bash
curl http://localhost:8000/health
```

5. **View logs**
```bash
docker-compose logs -f
```

---

### Option 2: Direct Python Deployment

#### Prerequisites
- Python 3.12+
- Chrome browser
- System dependencies

#### Steps

1. **Install system dependencies**
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y python3.12 python3-pip google-chrome-stable

# macOS
brew install python@3.12
brew install --cask google-chrome
```

2. **Create virtual environment**
```bash
python3.12 -m venv venv
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate  # Windows
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment**
```bash
cp .env.production .env
# Edit .env
```

5. **Run with production settings**
```bash
export API_WORKERS=4
export LOG_LEVEL=INFO
python -m src
```

---

### Option 3: Cloud Deployment

#### AWS EC2

1. **Launch EC2 instance**
   - AMI: Ubuntu 22.04 LTS
   - Instance type: t3.medium or larger
   - Security group: Allow port 8000

2. **SSH into instance**
```bash
ssh -i your-key.pem ubuntu@your-instance-ip
```

3. **Install Docker**
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu
```

4. **Deploy application**
```bash
git clone <your-repo>
cd linkedin
cp .env.production .env
# Edit .env
docker-compose up -d
```

5. **Configure reverse proxy (optional)**
```bash
sudo apt-get install nginx
# Configure nginx to proxy to port 8000
```

#### Google Cloud Run

1. **Build container**
```bash
gcloud builds submit --tag gcr.io/PROJECT_ID/ai-candidate-sourcing
```

2. **Deploy**
```bash
gcloud run deploy ai-candidate-sourcing \
  --image gcr.io/PROJECT_ID/ai-candidate-sourcing \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GROQ_API_KEY=xxx,LINKEDIN_USERNAME=xxx
```

#### Heroku

1. **Create app**
```bash
heroku create your-app-name
```

2. **Set environment variables**
```bash
heroku config:set GROQ_API_KEY=xxx
heroku config:set LINKEDIN_USERNAME=xxx
heroku config:set LINKEDIN_PASSWORD=xxx
```

3. **Deploy**
```bash
git push heroku main
```

---

## Production Configuration

### Environment Variables

Required:
```env
GROQ_API_KEY=your_groq_api_key
LINKEDIN_USERNAME=your_email@example.com
LINKEDIN_PASSWORD=your_password
```

Recommended:
```env
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=4
LOG_LEVEL=INFO
SECRET_KEY=random_secret_key_here
ALLOWED_ORIGINS=https://yourdomain.com
DATABASE_URL=sqlite:///./data/candidates.db
```

### Security Checklist

- [ ] Change `SECRET_KEY` to random value
- [ ] Set `ALLOWED_ORIGINS` to your domain
- [ ] Use HTTPS in production
- [ ] Rotate API keys regularly
- [ ] Use strong LinkedIn password
- [ ] Enable firewall rules
- [ ] Set up monitoring
- [ ] Configure log rotation
- [ ] Use environment variables (never commit secrets)

### Performance Tuning

1. **API Workers**
```env
API_WORKERS=4  # Number of CPU cores
```

2. **Database**
```env
# For production, consider PostgreSQL
DATABASE_URL=postgresql://user:pass@host:5432/dbname
```

3. **Caching**
```env
REDIS_URL=redis://localhost:6379/0
```

4. **Rate Limiting**
```env
RATE_LIMIT_PER_MINUTE=60
```

---

## Monitoring

### Health Checks

```bash
# Basic health check
curl http://localhost:8000/health

# Docker health check
docker ps  # Check STATUS column
```

### Logs

```bash
# Docker logs
docker-compose logs -f

# File logs
tail -f logs/app.log
```

### Metrics

Consider adding:
- Prometheus for metrics
- Grafana for dashboards
- Sentry for error tracking
- DataDog for APM

---

## Backup and Recovery

### Database Backup

```bash
# Backup SQLite database
cp data/candidates.db data/candidates.db.backup

# Automated backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
cp data/candidates.db backups/candidates_$DATE.db
```

### Restore

```bash
# Restore from backup
cp backups/candidates_20240101_120000.db data/candidates.db
docker-compose restart
```

---

## Scaling

### Horizontal Scaling

1. **Load Balancer**
   - Use nginx or cloud load balancer
   - Distribute traffic across multiple instances

2. **Shared Database**
   - Use PostgreSQL instead of SQLite
   - Configure `DATABASE_URL`

3. **Shared Storage**
   - Use S3 or cloud storage for logs
   - Mount shared volumes

### Vertical Scaling

- Increase instance size
- Add more CPU cores
- Increase memory
- Use faster storage

---

## Troubleshooting

### Container won't start

```bash
# Check logs
docker-compose logs

# Check environment
docker-compose config

# Rebuild
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### High memory usage

- Reduce `API_WORKERS`
- Limit concurrent scrapers
- Increase instance memory

### Slow performance

- Check network latency
- Monitor CPU usage
- Review scraping timeouts
- Consider caching

---

## Maintenance

### Updates

```bash
# Pull latest code
git pull origin main

# Rebuild and restart
docker-compose down
docker-compose build
docker-compose up -d
```

### Log Rotation

Configure in `src/logging_config.py`:
```python
RotatingFileHandler(
    'logs/app.log',
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5
)
```

### Database Cleanup

```python
# Remove old jobs (older than 30 days)
from datetime import datetime, timedelta
from src.database import SessionLocal, JobDB

db = SessionLocal()
cutoff = datetime.now() - timedelta(days=30)
db.query(JobDB).filter(JobDB.created_at < cutoff).delete()
db.commit()
```

---

## Support

For deployment issues:
1. Check logs first
2. Review configuration
3. Test health endpoint
4. Open GitHub issue with details
