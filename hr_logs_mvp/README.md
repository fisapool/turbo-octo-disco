# HR Logs System MVP

## Security Notice
**WARNING:** This project currently stores certain passwords in plain text. **Do not use this configuration in production.** Implement proper password hashing before deployment.

### Security Guidelines
- **Password Storage:** Always use bcrypt or Argon2 for password hashing in production
- **Secret Management:** Store SECRET_KEY in environment variables, never in code
- **Rate Limiting:** Configure to allow max 100 requests/minute per user
- **HTTPS:** Mandatory for production deployments
- **Security Audits:** Perform monthly vulnerability scans

## Features
- User authentication (with security warnings)
- Dashboard for viewing logs
- Create new HR logs
- Track log status (pending, approved, rejected)
- Different log types (attendance, leave, performance)
- Admin dashboard with management tools
- Real-time system health monitoring

## Requirements
- Python 3.9.7
- Flask 2.0.2
- SQLite3 3.35.5
- Modern web browser (Chrome 90+, Firefox 89+)
- See `requirements.txt` for complete list

## Performance Benchmarks
- API response time: < 200ms (p99)
- Concurrent users: 100+ (tested with Locust)
- Data processing: < 1 second for typical operations

## Setup Instructions
1. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment:
```bash
cp .env.example .env
nano .env  # Edit with your values
```

4. Run application:
```bash
python app.py
```

5. Access at `http://localhost:5000`

## Database
- SQLite by default (created automatically)
- For production: PostgreSQL recommended
- Migration tool: Alembic (`alembic upgrade head`)

### Backup Procedures
- Automated daily backups to `/backups`
- Retention: 30 days
- Manual backup: `python scripts/backup.py`

## API Documentation
[Full API docs available here](docs/api/endpoints.md)

## Monitoring & Alerts
- Prometheus metrics endpoint: `/metrics`
- Grafana dashboards included
- Alert rules defined in `alert_rules.yml`

## Deployment Options
### Docker Compose (Recommended)
```bash
docker-compose up -d --build
```

### Manual Production
```bash
gunicorn -w 4 -b 0.0.0.0:8000 app:create_app()
```

## Troubleshooting
**Issue:** Database connection failures  
**Fix:** Verify `DATABASE_URL` in `.env`

**Issue:** 429 Too Many Requests  
**Fix:** Adjust rate limiting in `config/rate_limiting.py`

**Issue:** Missing dependencies  
**Fix:** Run `pip install -r requirements.txt`

## Changelog
- v1.2: Added security enhancements
- v1.1: Initial MVP release

## Support
Contact: hr-logs-support@fisamy.work  
Slack: #hr-logs-support

## License
MIT License
