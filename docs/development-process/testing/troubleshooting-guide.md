# Testing Troubleshooting Guide

**Last Updated:** 2025-09-12
**Version:** 1.0

## Common Test Failures

### Container Health Check Failures

#### Postgres Not Healthy
```bash
# Check logs
docker-compose logs postgres

# Common fix - restart service
docker-compose restart postgres

# Verify health
docker-compose exec postgres pg_isready -U taylordash -d taylordash
```

#### Backend Health Check Failing
```bash
# Check backend logs
docker-compose logs backend

# Test health endpoint directly
docker-compose exec backend curl -sf http://localhost:8000/health/ready

# Common fixes
docker-compose restart backend
docker-compose up -d --force-recreate backend
```

#### VictoriaMetrics Issues
```bash
# Check metrics service
curl -sf http://localhost:8428/health

# Restart if needed
docker-compose restart victoriametrics

# Verify data directory permissions
docker-compose exec victoriametrics ls -la /victoria-metrics-data
```

### Authentication Test Failures

#### Login Endpoint Not Responding
```bash
# Test backend directly
curl -X POST http://localhost:3000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# Check backend configuration
docker-compose exec backend env | grep -E "(DATABASE|API)"

# Verify database connection
docker-compose exec backend python -c "from app.database import engine; print(engine.url)"
```

#### Session Token Issues
```bash
# Test token generation
TOKEN=$(curl -s -X POST http://localhost:3000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' | jq -r '.session_token')

# Test token usage
curl -H "Authorization: Bearer $TOKEN" http://localhost:3000/api/v1/auth/me
```

#### Database Authentication Problems
```bash
# Check user table
docker-compose exec postgres psql -U taylordash -d taylordash \
  -c "SELECT username, role FROM users;"

# Reset admin password if needed
docker-compose exec postgres psql -U taylordash -d taylordash \
  -c "UPDATE users SET password_hash = '\$2b\$12\$hashed_password_here' WHERE username = 'admin';"
```

### API Test Failures

#### Project API Not Accessible
```bash
# Test with proper headers
curl -H "Host: taylordash.local" -H "X-API-Key: taylordash-dev-key" \
  http://localhost/api/v1/projects

# Check nginx configuration
docker-compose exec nginx nginx -t

# Verify routing
curl -I -H "Host: taylordash.local" http://localhost/api/v1/projects
```

#### API Key Validation Failing
```bash
# Verify API key in environment
docker-compose exec backend env | grep API_KEY

# Test without API key (should fail)
curl -v http://localhost:3000/api/v1/projects

# Test with correct key
curl -H "X-API-Key: taylordash-dev-key" http://localhost:3000/api/v1/projects
```

### MQTT Test Failures

#### Mosquitto Connection Issues
```bash
# Check mosquitto service
docker-compose logs mosquitto

# Test connection directly
docker-compose exec mosquitto mosquitto_pub -h localhost -t test -m "ping"

# Check port binding
docker-compose ps mosquitto

# Verify configuration
docker-compose exec mosquitto cat /mosquitto/config/mosquitto.conf
```

#### Event Processing Failures
```bash
# Check events mirror table
docker-compose exec postgres psql -U taylordash -d taylordash \
  -c "SELECT COUNT(*) FROM events_mirror ORDER BY created_at DESC LIMIT 5;"

# Check DLQ for failed events
docker-compose exec postgres psql -U taylordash -d taylordash \
  -c "SELECT * FROM dlq_events ORDER BY created_at DESC LIMIT 5;"

# Test event publishing
curl -X POST -H "X-API-Key: taylordash-dev-key" \
  http://localhost:3000/api/v1/events/test
```

### UI Test Failures

#### Frontend Not Accessible
```bash
# Check frontend service
curl -I http://localhost:5174

# Check Vite dev server
docker-compose logs frontend

# Restart frontend
docker-compose restart frontend
```

#### Authentication Flow Issues
```bash
# Test backend auth from frontend perspective
curl -X POST http://localhost:3000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -H "Origin: http://localhost:5174" \
  -d '{"username":"admin","password":"admin123"}'

# Check CORS configuration
curl -I -H "Origin: http://localhost:5174" http://localhost:3000/api/v1/auth/login
```

#### Plugin System Issues
```bash
# Check plugin registry
curl -H "X-API-Key: taylordash-dev-key" \
  http://localhost:3000/api/v1/plugins/list

# Verify plugin ports
netstat -tlnp | grep -E "(5173|5175)"

# Check plugin health
curl -H "X-API-Key: taylordash-dev-key" \
  http://localhost:3000/api/v1/plugins/midnight-hud/health
```

## Performance Issues

### Slow API Responses
```bash
# Check database connection pool
docker-compose exec backend python -c "
from app.database import SessionLocal
session = SessionLocal()
print('Database connection OK')
session.close()
"

# Monitor query performance
docker-compose exec postgres psql -U taylordash -d taylordash \
  -c "SELECT query, mean_time, calls FROM pg_stat_statements ORDER BY mean_time DESC LIMIT 5;"
```

### High Memory Usage
```bash
# Check container memory usage
docker stats --no-stream

# Check for memory leaks
docker-compose exec backend python -c "
import psutil
process = psutil.Process()
print(f'Memory: {process.memory_info().rss / 1024 / 1024:.2f} MB')
"
```

### Database Performance
```bash
# Check active connections
docker-compose exec postgres psql -U taylordash -d taylordash \
  -c "SELECT count(*) FROM pg_stat_activity WHERE state = 'active';"

# Analyze slow queries
docker-compose exec postgres psql -U taylordash -d taylordash \
  -c "SELECT query, mean_time FROM pg_stat_statements WHERE mean_time > 100 ORDER BY mean_time DESC;"
```

## Environment Issues

### Docker Compose Problems
```bash
# Check service status
docker-compose ps

# View all logs
docker-compose logs

# Restart all services
docker-compose restart

# Force recreate if needed
docker-compose down && docker-compose up -d
```

### Network Connectivity
```bash
# Test internal networking
docker-compose exec backend ping postgres
docker-compose exec backend ping mosquitto

# Check port bindings
docker-compose port backend 8000
docker-compose port frontend 5174
```

### Volume Mount Issues
```bash
# Check volume mounts
docker-compose exec backend ls -la /app
docker-compose exec postgres ls -la /var/lib/postgresql/data

# Verify permissions
docker-compose exec backend id
docker-compose exec postgres id
```

## Quick Fixes

### Reset Development Environment
```bash
# Complete reset
docker-compose down -v
docker-compose up -d
sleep 30
./ops/validate_p1.sh
```

### Database Reset
```bash
# Reset database only
docker-compose stop backend
docker-compose exec postgres psql -U taylordash -d taylordash -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
docker-compose restart backend
```

### Cache Clear
```bash
# Clear browser cache for frontend testing
# Clear Docker build cache
docker system prune -f

# Clear Python cache
docker-compose exec backend find . -name "*.pyc" -delete
docker-compose exec backend find . -name "__pycache__" -exec rm -rf {} +
```

## Test Environment Recovery

### Service Recovery Order
1. Stop all services: `docker-compose down`
2. Check disk space: `df -h`
3. Clean up: `docker system prune -f`
4. Start database: `docker-compose up -d postgres`
5. Wait for health: `sleep 10`
6. Start remaining services: `docker-compose up -d`
7. Validate: `./ops/validate_p1.sh`

### Data Recovery
```bash
# Backup before recovery
docker-compose exec postgres pg_dump -U taylordash taylordash > backup.sql

# Restore if needed
docker-compose exec -T postgres psql -U taylordash taylordash < backup.sql
```