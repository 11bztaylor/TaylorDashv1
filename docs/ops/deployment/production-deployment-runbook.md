# Production Deployment Runbook

**Last Updated:** 2025-09-12
**Version:** 1.0
**Status:** Production Ready (Based on 89% test validation)

## Pre-Deployment Checklist

### Validation Requirements
- [ ] `./ops/validate_p1.sh` passes with 89%+ success rate
- [ ] All automated tests passing
- [ ] Security scan completed with no critical issues
- [ ] Performance benchmarks met
- [ ] Database migrations tested
- [ ] Backup procedures verified

### Environment Preparation
```bash
# Verify production environment
./ops/validate_p1.sh

# Check system resources
df -h
free -h
docker system df

# Verify certificates
openssl x509 -in certs/taylordash.crt -text -noout
```

## Deployment Procedure

### 1. Pre-Deployment Backup
```bash
# Database backup
docker-compose exec postgres pg_dump -U taylordash taylordash > "backup_$(date +%Y%m%d_%H%M%S).sql"

# Configuration backup
cp .env ".env.backup.$(date +%Y%m%d_%H%M%S)"
cp docker-compose.yml "docker-compose.backup.$(date +%Y%m%d_%H%M%S).yml"

# Verify backup integrity
psql -U taylordash -d taylordash_test < backup_*.sql
```

### 2. Service Health Check
```bash
# Pre-deployment health verification
docker-compose ps
curl -sf http://localhost:3000/health/ready
curl -sf http://localhost:5174
./ops/validate_p1.sh | tee pre_deployment_validation.log
```

### 3. Rolling Deployment
```bash
# Pull latest images
docker-compose pull

# Deploy backend first (zero downtime)
docker-compose up -d --no-deps backend

# Wait for backend health
sleep 30
curl -sf http://localhost:3000/health/ready

# Deploy frontend
docker-compose up -d --no-deps frontend

# Deploy remaining services
docker-compose up -d
```

### 4. Post-Deployment Validation
```bash
# Full system validation
./ops/validate_p1.sh

# Smoke tests
curl -sf -H "Host: taylordash.local" http://localhost/api/v1/projects
curl -sf http://localhost:5174

# Performance check
ab -n 50 -c 5 -H 'Host: taylordash.local' http://localhost/api/v1/projects
```

## Production Environment Configuration

### Environment Variables
```bash
# Production .env template
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO

# Database
DATABASE_URL=postgresql://user:pass@host:5432/taylordash
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=30

# Authentication
JWT_SECRET_KEY=<strong-production-secret>
API_KEY=<production-api-key>
SESSION_EXPIRE_HOURS=8

# Security
CORS_ORIGINS=["https://yourdomain.com"]
SECURE_COOKIES=true
HTTPS_ONLY=true

# External Services
MQTT_BROKER_URL=mqtt://production-broker:1883
VICTORIA_METRICS_URL=http://vm:8428
PROMETHEUS_URL=http://prometheus:9090
```

### SSL/TLS Configuration
```bash
# Generate production certificates
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout certs/taylordash.key \
  -out certs/taylordash.crt \
  -subj "/CN=yourdomain.com"

# Verify certificate
openssl verify certs/taylordash.crt
```

### Database Configuration
```bash
# Production database setup
createdb -U postgres taylordash_prod
psql -U postgres -d taylordash_prod -c "CREATE USER taylordash WITH PASSWORD 'secure_password';"
psql -U postgres -d taylordash_prod -c "GRANT ALL PRIVILEGES ON DATABASE taylordash_prod TO taylordash;"

# Run migrations
alembic upgrade head
```

## Security Hardening

### Container Security
```bash
# Run containers as non-root
# Set in docker-compose.yml:
user: "1000:1000"

# Read-only root filesystem where possible
read_only: true
tmpfs:
  - /tmp

# Security scanning
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
  aquasec/trivy:latest image taylordash_backend:latest
```

### Network Security
```bash
# Firewall configuration (example for UFW)
ufw default deny incoming
ufw default allow outgoing
ufw allow 22/tcp    # SSH
ufw allow 80/tcp    # HTTP
ufw allow 443/tcp   # HTTPS
ufw enable

# Internal network isolation
docker network create --driver bridge taylordash_internal
```

### Application Security
- [ ] Security headers configured
- [ ] HTTPS enforced
- [ ] API rate limiting enabled
- [ ] Input validation comprehensive
- [ ] Secrets management secure
- [ ] Audit logging enabled

## Monitoring and Alerting

### Health Monitoring
```bash
# Health check endpoints
/health/live    # Container liveness
/health/ready   # Service readiness
/metrics        # Prometheus metrics

# Service discovery for monitoring
curl -sf http://localhost:3000/health/stack
```

### Performance Monitoring
```bash
# Key metrics to monitor
# - Response times (P50, P95, P99)
# - Error rates
# - Database connection pool
# - Memory usage
# - CPU utilization
# - Disk space

# Prometheus queries
http_request_duration_seconds{quantile="0.95"}
http_requests_total
database_connections_active
```

### Alerting Rules
```yaml
# Example Prometheus alerting rules
groups:
  - name: taylordash_alerts
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.1
        for: 5m
        annotations:
          summary: "High error rate detected"

      - alert: DatabaseConnectionHigh
        expr: database_connections_active > 80
        for: 2m
        annotations:
          summary: "Database connection pool usage high"
```

## Rollback Procedures

### Immediate Rollback
```bash
# Quick rollback to previous version
docker-compose down
docker-compose up -d --force-recreate

# Or specific service rollback
docker-compose stop backend
docker tag taylordash_backend:previous taylordash_backend:latest
docker-compose up -d backend
```

### Database Rollback
```bash
# Database migration rollback
alembic downgrade -1

# Full database restore
docker-compose stop backend
psql -U postgres -c "DROP DATABASE taylordash;"
psql -U postgres -c "CREATE DATABASE taylordash OWNER taylordash;"
psql -U taylordash -d taylordash < backup_YYYYMMDD_HHMMSS.sql
docker-compose start backend
```

### Configuration Rollback
```bash
# Restore previous configuration
cp .env.backup.YYYYMMDD_HHMMSS .env
cp docker-compose.backup.YYYYMMDD_HHMMSS.yml docker-compose.yml
docker-compose up -d --force-recreate
```

## Disaster Recovery

### Backup Strategy
```bash
# Automated backup script
#!/bin/bash
BACKUP_DIR="/backups/taylordash"
DATE=$(date +%Y%m%d_%H%M%S)

# Database backup
docker-compose exec postgres pg_dump -U taylordash taylordash > "$BACKUP_DIR/db_$DATE.sql"

# Configuration backup
cp .env "$BACKUP_DIR/env_$DATE"
cp docker-compose.yml "$BACKUP_DIR/compose_$DATE.yml"

# Cleanup old backups (keep 30 days)
find $BACKUP_DIR -name "*.sql" -mtime +30 -delete
```

### Recovery Procedures
```bash
# Full system recovery
# 1. Restore infrastructure
# 2. Restore database
# 3. Restore configuration
# 4. Restart services
# 5. Validate system health

# Infrastructure restore
docker-compose down -v
docker volume prune -f

# Database restore
createdb -U postgres taylordash
psql -U taylordash -d taylordash < latest_backup.sql

# Service restart
docker-compose up -d
sleep 60
./ops/validate_p1.sh
```

## Blue-Green Deployment

### Blue-Green Setup
```bash
# Blue environment (current production)
docker-compose -f docker-compose.blue.yml up -d

# Green environment (new version)
docker-compose -f docker-compose.green.yml up -d

# Health check green environment
curl -sf http://localhost:8001/health/ready  # Green backend
./ops/validate_p1.sh  # Full validation

# Switch traffic (update load balancer)
# nginx upstream configuration change
```

### Traffic Switching
```bash
# Update nginx configuration
cp nginx.green.conf /etc/nginx/sites-available/taylordash
nginx -t
systemctl reload nginx

# Verify traffic switch
curl -H "Host: taylordash.local" http://localhost/api/v1/projects

# Monitor new version
tail -f /var/log/nginx/access.log
docker-compose -f docker-compose.green.yml logs -f
```

## Scaling Procedures

### Horizontal Scaling
```bash
# Scale backend services
docker-compose up -d --scale backend=3

# Verify load balancing
for i in {1..10}; do
  curl -H "Host: taylordash.local" http://localhost/api/v1/projects
done

# Scale database (read replicas)
# Configure PostgreSQL streaming replication
```

### Vertical Scaling
```yaml
# docker-compose.yml resource limits
services:
  backend:
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: '0.5'
        reservations:
          memory: 512M
          cpus: '0.25'
```

## Maintenance Procedures

### Scheduled Maintenance
```bash
# Maintenance window checklist
# 1. Notify users
# 2. Enable maintenance mode
# 3. Stop services gracefully
# 4. Perform maintenance
# 5. Restart services
# 6. Validate system
# 7. Disable maintenance mode

# Maintenance mode
echo "System under maintenance" > /var/www/maintenance.html
# Configure nginx to serve maintenance page
```

### Security Updates
```bash
# Update containers
docker-compose pull
docker-compose up -d

# Update system packages
apt update && apt upgrade -y

# Security scanning post-update
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
  aquasec/trivy:latest image --severity HIGH,CRITICAL taylordash_backend:latest
```

## Troubleshooting Production Issues

### Common Issues

#### High Response Times
```bash
# Check system resources
top
iotop
docker stats

# Database performance
docker-compose exec postgres psql -U taylordash -d taylordash -c "
SELECT query, mean_time, calls FROM pg_stat_statements
WHERE mean_time > 100 ORDER BY mean_time DESC LIMIT 5;
"
```

#### Service Unavailability
```bash
# Check service health
docker-compose ps
docker-compose logs backend
docker-compose logs postgres

# Restart unhealthy services
docker-compose restart backend
```

#### Database Issues
```bash
# Check database connections
docker-compose exec postgres psql -U taylordash -d taylordash -c "
SELECT count(*) FROM pg_stat_activity WHERE state = 'active';
"

# Check database locks
docker-compose exec postgres psql -U taylordash -d taylordash -c "
SELECT * FROM pg_locks WHERE NOT granted;
"
```

## Post-Deployment Validation

### System Health Verification
- [ ] All services running and healthy
- [ ] API endpoints responding correctly
- [ ] Authentication system functional
- [ ] Database connectivity verified
- [ ] Performance metrics within targets
- [ ] Error rates normal
- [ ] Monitoring and alerting active

### User Acceptance Testing
- [ ] Login functionality working
- [ ] Core features accessible
- [ ] Data integrity maintained
- [ ] Performance acceptable
- [ ] No critical bugs reported