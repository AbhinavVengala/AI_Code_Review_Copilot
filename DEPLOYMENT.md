# Production Deployment Guide

## Prerequisites

- Python 3.9+
- Git
- SMTP server (for email reports)
- API keys (Gemini or OpenAI)

## Environment Configuration

Create `.env` file:

```bash
# Required: AI Provider Configuration
AI_PROVIDER=gemini  # or "openai"
GEMINI_API_KEY=your_gemini_key_here
# OPENAI_API_KEY=your_openai_key_here

# Optional: Email Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Optional: Dashboard Integration
DASHBOARD_API_ENDPOINT=https://your-dashboard.com/api/results
DASHBOARD_API_KEY=your_dashboard_key

# Production Settings
ENVIRONMENT=production  # "development" or "production"
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR
```

## Production Environment Settings

### Logging

**Development:**
- Colored console output
- DEBUG level logs
- Pretty formatting

**Production:**
- JSON structured output
- INFO level logs (WARNING/ERROR recommended)
- Machine-parseable for log aggregation

```bash
# Development
ENVIRONMENT=development
LOG_LEVEL=DEBUG

# Production
ENVIRONMENT=production
LOG_LEVEL=WARNING
```

### Log Rotation

Configure log rotation using system tools:

**Linux (logrotate):**
Create `/etc/logrotate.d/ai-code-review`:
```
/var/log/ai-code-review/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0644 appuser appuser
    sharedscripts
    postrotate
        systemctl reload ai-code-review
    endscript
}
```

**Docker:**
```yaml
services:
  app:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

## Deployment Options

### Option 1: Direct Deployment

```bash
# 1. Clone repository
git clone https://github.com/your-repo/AI_Code_Review_Copilot.git
cd AI_Code_Review_Copilot

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env with your keys

# 4. Run tests
pytest

# 5. Start FastAPI server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Option 2: Docker Deployment

```bash
# 1. Build image
docker build -t ai-code-review .

# 2. Run container
docker run -d \
  -p 8000:8000 \
  -e ENVIRONMENT=production \
  -e LOG_LEVEL=WARNING \
  -e GEMINI_API_KEY=your_key \
  --name ai-code-review \
  ai-code-review
```

### Option 3: Docker Compose

Create `docker-compose.yml`:
```yaml
version: '3.8'
services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=production
      - LOG_LEVEL=INFO
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - SMTP_SERVER=${SMTP_SERVER}
      - SMTP_USER=${SMTP_USER}
      - SMTP_PASSWORD=${SMTP_PASSWORD}
    restart: unless-stopped
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

Run:
```bash
docker-compose up -d
```

## Monitoring & Observability

### Log Aggregation

**For JSON logs (production):**

Stream to log aggregation service:
```bash
# Example: Ship to ELK/Splunk/Datadog
tail -f /var/log/ai-code-review/app.log | your-log-shipper
```

### Key Log Events

Monitor these events:

| Event | Level | Description |
|-------|-------|-------------|
| `request_started` | INFO | API request received |
| `request_completed` | INFO | Request finished (includes duration) |
| `llm_init_failed` | WARNING | LLM initialization failed |
| `ai_review_failed` | ERROR | AI review encountered error |
| `email_send_failed` | ERROR | Email delivery failed |
| `github_pr_comment_failed` | ERROR | GitHub PR comment failed |

### Request Correlation

All API requests include `X-Request-ID` header:
```bash
curl -i https://your-api.com/health
# Response includes: X-Request-ID: a1b2c3d4-e5f6-7890-abcd-ef1234567890
```

Use `request_id` to trace requests across logs:
```json
{"event": "request_started", "request_id": "a1b2c3d4-...", "method": "POST", "path": "/analyze"}
{"event": "llm_initialized", "request_id": "a1b2c3d4-...", "provider": "gemini"}
{"event": "request_completed", "request_id": "a1b2c3d4- ...", "duration_seconds": 2.345}
```

## Health Checks

```bash
# API health check
curl https://your-api.com/health
# Should return: {"status": "ok"}

# Full system check with logging
LOG_LEVEL=INFO python -c "from core.logging_config import get_logger; logger = get_logger('healthcheck'); logger.info('system_healthy'); print('✓ All systems operational')"
```

## Performance Tuning

### FastAPI Workers

```bash
# Development
uvicorn app.main:app --reload

# Production (4 workers)
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

# High traffic (use gunicorn)
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Resource Limits

Recommended minimum:
- CPU: 2 cores
- RAM: 2GB
- Disk: 10GB

For high traffic:
- CPU: 4+ cores
- RAM: 4GB+
- Disk: 20GB+

## Security Checklist

- [ ] Environment variables secured (not in code)
- [ ] API keys rotated regularly
- [ ] HTTPS enabled in production
- [ ] Rate limiting configured  
- [ ] CORS properly restricted
- [ ] Regular dependency updates
- [ ] Log sensitive data scrubbed
- [ ] Database backups automated

## Troubleshooting

### Logs not appearing

```bash
# Check log level
echo $LOG_LEVEL  # Should be INFO or DEBUG

# Test logging manually
python -c "from core.logging_config import get_logger; logger = get_logger('test'); logger.info('test')"
```

### LLM errors

```bash
# Check API key
python -c "import os; print('Key set:', bool(os.getenv('GEMINI_API_KEY')))"

# Test LLM initialization
python -c "from core.llm_factory import get_llm; llm = get_llm(); print('LLM:', llm)"
```

### Email not sending

Check SMTP logs:
```json
{"event": "email_send_skipped", "reason": "missing_smtp_credentials"}
{"event": "email_send_failed", "error": "..."}
```

## Support & Maintenance

### Log Retention

- Development: Keep 7 days
- Staging: Keep 30 days  
- Production: Keep 90 days

### Updates

```bash
# Pull latest code
git pull

# Update dependencies
pip install -r requirements.txt --upgrade

# Run tests
pytest

# Restart service
systemctl restart ai-code-review  # or docker-compose restart
```

---

For questions or issues, check logs first:
```bash
# View recent logs (development)  
tail -f logs/app.log

# View recent logs (production - JSON)
tail -f logs/app.log | jq '.'
```
