# Rollback Procedures

**Last Updated:** 2025-09-12
**Version:** 1.0
**Status:** Production Ready Rollback Strategy

## Rollback Decision Matrix

### When to Rollback
- **Critical bugs** affecting core functionality
- **Security vulnerabilities** discovered post-deployment
- **Performance degradation** > 50% from baseline
- **High error rates** > 5% of total requests
- **Service unavailability** > 5 minutes
- **Data corruption** detected

### Rollback Types
1. **Immediate Rollback** - Critical issues, < 5 minutes
2. **Planned Rollback** - Scheduled, thorough validation
3. **Partial Rollback** - Single service/component
4. **Database Rollback** - Schema/data changes
5. **Configuration Rollback** - Settings and environment

## Immediate Rollback Procedures

### Emergency Service Rollback
```bash
# Quick service restart with previous image
docker-compose stop backend
docker tag taylordash_backend:previous taylordash_backend:latest
docker-compose up -d backend

# Verify service health
sleep 30
curl -sf http://localhost:3000/health/ready

# Full system validation
./ops/validate_p1.sh
```

### Complete System Rollback
```bash
# Stop all services
docker-compose down

# Restore previous images
docker tag taylordash_backend:previous taylordash_backend:latest
docker tag taylordash_frontend:previous taylordash_frontend:latest

# Restore configuration
cp .env.backup.$(ls -t .env.backup.* | head -1) .env
cp docker-compose.backup.$(ls -t docker-compose.backup.* | head -1) docker-compose.yml

# Start services
docker-compose up -d

# Validate rollback
sleep 60
./ops/validate_p1.sh
```

### Blue-Green Environment Switch
```bash
# Switch load balancer back to blue environment
cp nginx.blue.conf /etc/nginx/sites-available/taylordash
nginx -t
systemctl reload nginx

# Verify traffic switched
curl -H "Host: taylordash.local" http://localhost/api/v1/projects

# Stop green environment
docker-compose -f docker-compose.green.yml down
```

## Database Rollback Procedures

### Schema Migration Rollback
```bash
# Check current migration
docker-compose exec backend alembic current

# Rollback one migration
docker-compose exec backend alembic downgrade -1

# Rollback to specific revision
docker-compose exec backend alembic downgrade <revision_id>

# Verify schema
docker-compose exec postgres psql -U taylordash -d taylordash -c "\dt"
```

### Data Restoration Rollback
```bash
# Stop backend to prevent data modifications
docker-compose stop backend

# Create current database backup (safety)
docker-compose exec postgres pg_dump -U taylordash taylordash > current_state_backup.sql

# Restore from backup
BACKUP_FILE=$(ls -t backup_*.sql | head -1)
docker-compose exec postgres psql -U taylordash -d taylordash -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
docker-compose exec -T postgres psql -U taylordash -d taylordash < $BACKUP_FILE

# Restart backend
docker-compose start backend

# Validate data integrity
docker-compose exec postgres psql -U taylordash -d taylordash -c "SELECT COUNT(*) FROM users;"
docker-compose exec postgres psql -U taylordash -d taylordash -c "SELECT COUNT(*) FROM projects;"
```

### Backup Validation Before Rollback
```bash
# Verify backup integrity
BACKUP_FILE="backup_$(date -d '1 hour ago' +%Y%m%d_%H)*.sql"
if [ -f "$BACKUP_FILE" ]; then
    # Test restore to temporary database
    docker-compose exec postgres psql -U taylordash -c "CREATE DATABASE rollback_test;"
    docker-compose exec -T postgres psql -U taylordash -d rollback_test < $BACKUP_FILE

    # Verify table counts
    docker-compose exec postgres psql -U taylordash -d rollback_test -c "\dt"

    # Cleanup test database
    docker-compose exec postgres psql -U taylordash -c "DROP DATABASE rollback_test;"

    echo "Backup verified successfully"
else
    echo "ERROR: No recent backup found"
    exit 1
fi
```

## Configuration Rollback

### Environment Configuration Rollback
```bash
# Identify previous configuration
ls -la .env.backup.*

# Restore previous environment
PREV_ENV=$(ls -t .env.backup.* | head -1)
cp $PREV_ENV .env

# Verify configuration changes
diff .env $PREV_ENV

# Restart services with new configuration
docker-compose restart backend
docker-compose restart frontend
```

### Docker Compose Rollback
```bash
# Restore previous docker-compose configuration
PREV_COMPOSE=$(ls -t docker-compose.backup.* | head -1)
cp $PREV_COMPOSE docker-compose.yml

# Recreate services with previous configuration
docker-compose up -d --force-recreate

# Validate service configuration
docker-compose ps
docker-compose config
```

### SSL Certificate Rollback
```bash
# Backup current certificates
cp certs/taylordash.crt certs/taylordash.crt.current
cp certs/taylordash.key certs/taylordash.key.current

# Restore previous certificates
cp certs/taylordash.crt.backup certs/taylordash.crt
cp certs/taylordash.key.backup certs/taylordash.key

# Restart nginx
docker-compose restart nginx

# Verify certificate
openssl verify certs/taylordash.crt
```

## Partial Rollback Procedures

### Single Service Rollback
```bash
# Backend only rollback
docker-compose stop backend
docker tag taylordash_backend:previous taylordash_backend:latest
docker-compose up -d backend

# Verify backend health
curl -sf http://localhost:3000/health/ready

# Frontend only rollback
docker-compose stop frontend
docker tag taylordash_frontend:previous taylordash_frontend:latest
docker-compose up -d frontend

# Verify frontend
curl -I http://localhost:5174
```

### Plugin System Rollback
```bash
# Disable problematic plugins
curl -X DELETE -H "X-API-Key: taylordash-dev-key" \
  http://localhost:3000/api/v1/plugins/problematic-plugin

# Rollback plugin configuration
cp plugins_config.backup.json plugins_config.json

# Restart plugin system
docker-compose restart backend
```

### Authentication System Rollback
```bash
# If authentication changes are problematic
# Restore previous authentication configuration

# Check current auth config
docker-compose exec backend env | grep -E "(JWT|AUTH|SESSION)"

# Restore from backup
docker-compose exec backend cp /app/backup/auth_config.py /app/auth_config.py

# Restart authentication service
docker-compose restart backend

# Test authentication
curl -X POST http://localhost:3000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

## Rollback Validation

### Post-Rollback Health Check
```bash
# Comprehensive system validation
./ops/validate_p1.sh

# Expected results after rollback:
# - 89%+ pass rate maintained
# - All critical services healthy
# - Authentication working
# - Database connectivity confirmed
# - Performance restored to baseline

# Manual verification checklist
echo "Manual Rollback Verification:"
echo "1. Login functionality: $(curl -s -X POST http://localhost:3000/api/v1/auth/login -H 'Content-Type: application/json' -d '{\"username\":\"admin\",\"password\":\"admin123\"}' | jq -r '.session_token != null')"
echo "2. API endpoints: $(curl -s -H 'X-API-Key: taylordash-dev-key' http://localhost:3000/api/v1/projects | jq 'length')"
echo "3. Frontend accessible: $(curl -s -I http://localhost:5174 | head -1)"
echo "4. Database responsive: $(docker-compose exec postgres pg_isready -U taylordash -d taylordash)"
```

### Performance Validation
```bash
# Response time validation
echo "Validating response times post-rollback..."

# API performance test
RESPONSE_TIME=$(curl -w "%{time_total}" -o /dev/null -s -H "X-API-Key: taylordash-dev-key" http://localhost:3000/api/v1/projects)
echo "API response time: ${RESPONSE_TIME}s (target: <0.5s)"

# Authentication performance
AUTH_TIME=$(curl -w "%{time_total}" -o /dev/null -s -X POST http://localhost:3000/api/v1/auth/login -H "Content-Type: application/json" -d '{"username":"admin","password":"admin123"}')
echo "Auth response time: ${AUTH_TIME}s (target: <0.5s)"

# Frontend load time
FRONTEND_TIME=$(curl -w "%{time_total}" -o /dev/null -s http://localhost:5174)
echo "Frontend load time: ${FRONTEND_TIME}s (target: <1s)"
```

## Rollback Documentation

### Incident Documentation
```bash
# Create rollback incident report
cat > rollback_report_$(date +%Y%m%d_%H%M%S).md << EOF
# Rollback Incident Report

**Date:** $(date)
**Incident ID:** ROLL-$(date +%Y%m%d-%H%M)
**Severity:** [Critical/High/Medium/Low]

## Issue Description
[Describe the problem that triggered the rollback]

## Rollback Actions Taken
[List specific rollback steps performed]

## Services Affected
- [ ] Backend API
- [ ] Frontend Application
- [ ] Database
- [ ] Authentication System
- [ ] Plugin System
- [ ] External Integrations

## Validation Results
- [ ] System health check passed
- [ ] Performance restored
- [ ] Authentication functional
- [ ] User acceptance verified

## Root Cause Analysis
[Analysis of what caused the issue requiring rollback]

## Prevention Measures
[Steps to prevent similar issues in the future]
EOF
```

### Rollback Log Maintenance
```bash
# Maintain rollback history
echo "$(date): Rollback executed - $(cat rollback_report_*.md | head -5)" >> rollback_history.log

# Archive rollback artifacts
mkdir -p rollbacks/$(date +%Y%m%d_%H%M%S)
mv rollback_report_*.md rollbacks/$(date +%Y%m%d_%H%M%S)/
cp .env rollbacks/$(date +%Y%m%d_%H%M%S)/env_post_rollback
```

## Automated Rollback Triggers

### Health-Based Automatic Rollback
```bash
# Health check script with automatic rollback
#!/bin/bash
HEALTH_THRESHOLD=3
FAILED_CHECKS=0

while [ $FAILED_CHECKS -lt $HEALTH_THRESHOLD ]; do
    if ! curl -sf http://localhost:3000/health/ready > /dev/null; then
        ((FAILED_CHECKS++))
        echo "Health check failed ($FAILED_CHECKS/$HEALTH_THRESHOLD)"
        sleep 30
    else
        FAILED_CHECKS=0
        sleep 60
    fi
done

echo "CRITICAL: Health checks failed $HEALTH_THRESHOLD times. Initiating automatic rollback..."

# Execute rollback
docker-compose down
docker tag taylordash_backend:previous taylordash_backend:latest
docker tag taylordash_frontend:previous taylordash_frontend:latest
docker-compose up -d

# Send alert
echo "Automatic rollback executed at $(date)" | mail -s "TaylorDash Automatic Rollback" admin@yourdomain.com
```

### Performance-Based Rollback
```bash
# Monitor response times and trigger rollback if degraded
#!/bin/bash
RESPONSE_THRESHOLD=1.0  # 1 second threshold

# Test API response time
RESPONSE_TIME=$(curl -w "%{time_total}" -o /dev/null -s -H "X-API-Key: taylordash-dev-key" http://localhost:3000/api/v1/projects)

if (( $(echo "$RESPONSE_TIME > $RESPONSE_THRESHOLD" | bc -l) )); then
    echo "Performance degraded: ${RESPONSE_TIME}s > ${RESPONSE_THRESHOLD}s"
    echo "Initiating performance-based rollback..."

    # Execute rollback
    ./rollback_scripts/immediate_rollback.sh

    # Alert
    echo "Performance rollback executed: Response time ${RESPONSE_TIME}s exceeded ${RESPONSE_THRESHOLD}s threshold" | mail -s "Performance Rollback Alert" admin@yourdomain.com
fi
```

## Rollback Testing

### Rollback Drill Procedures
```bash
# Monthly rollback drill
#!/bin/bash
echo "=== TaylorDash Rollback Drill ==="

# 1. Create test backup
docker-compose exec postgres pg_dump -U taylordash taylordash > drill_backup.sql

# 2. Make a test change
echo "TEST_CHANGE=drill_$(date +%s)" >> .env

# 3. Restart services
docker-compose restart backend

# 4. Execute rollback procedure
cp .env.backup.$(ls -t .env.backup.* | head -1) .env
docker-compose restart backend

# 5. Validate rollback
if ./ops/validate_p1.sh > /dev/null; then
    echo "✅ Rollback drill successful"
else
    echo "❌ Rollback drill failed"
fi

# 6. Cleanup
rm drill_backup.sql
```

## Recovery After Failed Rollback

### Rollback Failure Recovery
```bash
# If rollback itself fails
echo "Rollback failed. Initiating emergency recovery..."

# 1. Stop all services
docker-compose down -v

# 2. Clean Docker state
docker system prune -f
docker volume prune -f

# 3. Restore from known good backup
# Database
docker-compose up -d postgres
sleep 30
docker-compose exec -T postgres psql -U taylordash -c "DROP DATABASE IF EXISTS taylordash; CREATE DATABASE taylordash OWNER taylordash;"
docker-compose exec -T postgres psql -U taylordash -d taylordash < emergency_backup.sql

# Configuration
cp .env.emergency .env
cp docker-compose.emergency.yml docker-compose.yml

# 4. Start services
docker-compose up -d

# 5. Extended validation
sleep 120
./ops/validate_p1.sh
```

### Emergency Contact Procedures
```bash
# Emergency escalation
if [ "$ROLLBACK_STATUS" = "FAILED" ]; then
    echo "EMERGENCY: Rollback failed. Manual intervention required."

    # Send emergency alerts
    echo "TaylorDash rollback failure requires immediate attention" | mail -s "EMERGENCY: Rollback Failed" emergency@yourdomain.com

    # Log emergency status
    echo "$(date): EMERGENCY - Rollback failed, system may be unstable" >> emergency.log

    # Activate incident response
    curl -X POST "https://your-incident-management-system.com/api/incidents" \
      -H "Content-Type: application/json" \
      -d '{"severity":"critical","title":"TaylorDash Rollback Failure","description":"Automated rollback failed, manual intervention required"}'
fi
```