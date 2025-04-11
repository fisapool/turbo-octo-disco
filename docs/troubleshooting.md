# Troubleshooting Procedures

## Common Issues and Solutions

### 1. Service Startup Failures
**Symptoms**:
- Containers failing to start
- Port conflicts
- Dependency errors

**Resolution Steps**:
1. Check logs: `docker-compose logs [service]`
2. Verify port availability: `netstat -tuln`
3. Validate dependencies: `pip freeze | grep -E 'flask|sqlalchemy'`

### 2. Database Connection Issues
**Symptoms**:
- Connection timeouts
- Authentication failures
- Query timeouts

**Resolution Steps**:
1. Verify DB credentials in `app/config/config.json`
2. Check connection string format
3. Test direct connection: `psql -h [host] -U [user] -d [db]`

### 3. Performance Degradation
**Symptoms**:
- Slow API responses
- High CPU usage
- Memory leaks

**Resolution Steps**:
1. Generate profile: `python -m cProfile -o profile.stats app.py`
2. Analyze with: `snakeviz profile.stats`
3. Check for N+1 queries

### 4. Monitoring Alerts
**Response Protocol**:
1. Acknowledge alert
2. Check related dashboards
3. Consult runbooks
4. Escalate if unresolved after 15 minutes

## Diagnostic Tools
```bash
# Memory usage
docker stats

# Network inspection
tcpdump -i any -n port 5432

# Performance monitoring
htop
glances
```

## Emergency Procedures
1. **Service Rollback**:
   ```bash
   git checkout tags/<previous_version>
   docker-compose up -d --build
   ```

2. **Data Recovery**:
   ```bash
   pg_restore -U postgres -d hr_analytics latest_backup.dump
   ```

3. **Incident Documentation**:
   - Root cause analysis
   - Timeline of events
   - Remediation steps
