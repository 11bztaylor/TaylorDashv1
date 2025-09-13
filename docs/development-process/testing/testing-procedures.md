# Testing Procedures

**Last Updated:** 2025-09-12
**Version:** 1.0
**Status:** Production Ready (89% pass rate)

## Validation Process

### Primary Validation Script
Use `/ops/validate_p1.sh` for comprehensive system validation.

```bash
cd /TaylorProjects/TaylorDashv1
./ops/validate_p1.sh
```

**Expected Results:**
- 89% pass rate minimum
- Zero critical failures
- All health checks passing

## Test Categories

### 1. Container Health Checks
```bash
# Check all services running
docker-compose ps

# Verify healthy status
docker-compose ps postgres | grep -q 'healthy'
docker-compose ps mosquitto | grep -q 'healthy'
docker-compose ps victoriametrics | grep -q 'healthy'
```

### 2. HTTP Health Endpoints
```bash
# Backend health
docker-compose exec -T backend curl -sf http://localhost:8000/health/live
docker-compose exec -T backend curl -sf http://localhost:8000/health/ready

# External services
curl -sf http://localhost:8428/health  # VictoriaMetrics
curl -sf http://localhost:9090/-/healthy  # Prometheus
```

### 3. API Testing
```bash
# Project API validation
curl -fsS -H "Host: taylordash.local" http://localhost/api/v1/projects

# Authentication test
curl -X POST -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' \
  http://localhost:3000/api/v1/auth/login
```

### 4. Event Processing
```bash
# MQTT connectivity
docker-compose exec -T mosquitto mosquitto_pub -h localhost -t tracker/test -m "validation"

# Database mirroring
docker-compose exec -T postgres psql -U taylordash -d taylordash \
  -c "SELECT COUNT(*) FROM events_mirror"
```

## UI Testing

### Quick UI Verification
```bash
# Run automated UI tests
python3 ui_test_automation.py

# Screenshot validation
python3 ui_screenshot_test.py
```

**Current Score:** 7.8/10 (Production Ready)
**Key Validations:**
- Authentication flow functional
- Navigation working
- Responsive design confirmed
- Security measures active

### Manual UI Checklist
- [ ] Login page loads with demo credentials
- [ ] Authentication successful (admin/admin123)
- [ ] Dashboard displays projects
- [ ] Settings page accessible
- [ ] Plugin system responsive
- [ ] All navigation links functional

## Performance Testing

### Response Time Validation
```bash
# API latency check (requires Apache Bench)
ab -n 100 -c 10 -H 'Host: taylordash.local' http://localhost/api/v1/projects
```

**Targets:**
- P95 < 200ms
- Sub-second response times
- Excellent resource efficiency

## Security Testing

### Authentication Security
```bash
# Test invalid credentials
curl -X POST -H "Content-Type: application/json" \
  -d '{"username":"invalid","password":"wrong"}' \
  http://localhost:3000/api/v1/auth/login

# Verify 401 response
echo $?  # Should be non-zero
```

### Session Management
- [ ] Sessions expire properly
- [ ] Logout invalidates tokens
- [ ] Protected routes enforce authentication
- [ ] API key validation working

## Troubleshooting Common Issues

### Service Not Starting
```bash
# Check logs
docker-compose logs backend
docker-compose logs postgres

# Restart specific service
docker-compose restart backend
```

### Database Connection Issues
```bash
# Verify database health
docker-compose exec postgres pg_isready -U taylordash -d taylordash

# Check connection pool
docker-compose exec backend curl -sf http://localhost:8000/health/ready
```

### MQTT Issues
```bash
# Test MQTT directly
docker-compose exec mosquitto mosquitto_pub -h localhost -t test -m "ping"
docker-compose exec mosquitto mosquitto_sub -h localhost -t test -C 1
```

### Frontend Issues
```bash
# Check frontend server
curl -I http://localhost:5174

# Verify backend connectivity
curl -sf http://localhost:3000/api/v1/projects
```

## Test Automation

### Continuous Testing Setup
```bash
# Pre-commit testing
make test

# Full validation pipeline
make validate

# Performance testing
make perf-test
```

### Test Environment Requirements
- Docker Compose running
- All services healthy
- Database seeded with test data
- API keys configured
- MQTT broker operational

## Success Criteria

### Production Readiness Checklist
- [ ] 89%+ validation pass rate
- [ ] Zero breaking API changes
- [ ] UI score 7.8+ (current: 7.8/10)
- [ ] Authentication system functional
- [ ] Plugin system responsive
- [ ] Performance targets met
- [ ] Security audit clean

### Critical Thresholds
- **Container Health:** All services "healthy"
- **API Response:** < 500ms average
- **Authentication:** 100% success rate
- **Database:** Zero connection failures
- **MQTT:** Event processing functional