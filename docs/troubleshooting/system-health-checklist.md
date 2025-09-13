# TaylorDash System Health Checklist

Quick diagnostic procedures for validating TaylorDash system health across all components.

## Quick Health Check

```bash
# Overall system status
curl -H "X-API-Key: taylordash-dev-key" http://localhost:8000/api/v1/health/stack

# Individual service checks
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
docker compose logs --tail=50 backend postgres mosquitto
```

## Component Health Verification

### Database (PostgreSQL)
```bash
# Connection test
docker exec taylordashv1-postgres-1 pg_isready -U taylordash -d taylordash

# Permission check
docker exec -it taylordashv1-postgres-1 psql -U taylordash -d taylordash -c "\dt"

# Plugin table ownership
docker exec -it taylordashv1-postgres-1 psql -U taylordash -d taylordash -c "SELECT schemaname, tablename, tableowner FROM pg_tables WHERE tablename LIKE '%plugin%';"
```

**Healthy Output:**
- `pg_isready` returns `accepting connections`
- Plugin tables owned by `taylordash_app` user
- No permission denied errors

### Backend API
```bash
# Health endpoints
curl http://localhost:8000/health/live
curl http://localhost:8000/health/ready

# Process check
docker exec taylordashv1-backend-1 ps aux | grep uvicorn
```

**Healthy Output:**
- `/health/live` returns `{"status": "alive"}`
- `/health/ready` returns `{"status": "ready", "database": "healthy"}`
- Single uvicorn process running

### MQTT Broker
```bash
# Connection test
mosquitto_pub -h localhost -t test/health -m "ping" -u taylordash -P taylordash

# Subscription test  
timeout 5 mosquitto_sub -h localhost -t test/health -u taylordash -P taylordash
```

**Healthy Output:**
- No connection refused errors
- Messages publish/subscribe successfully

### Frontend (React)
```bash
# Development server
curl -s -o /dev/null -w "%{http_code}" http://localhost:3000

# Build verification
docker exec taylordashv1-frontend-1 ls -la /app/dist
```

### Logging System
```bash
# Database logging table
docker exec -it taylordashv1-postgres-1 psql -U taylordash -d taylordash -c "SELECT COUNT(*) FROM logging.application_logs WHERE timestamp > NOW() - INTERVAL '1 hour';"

# Test log creation
curl -X POST -H "X-API-Key: taylordash-dev-key" http://localhost:8000/api/v1/logs/test
```

## Service Dependencies Check

### Startup Order Verification
```bash
# Check service health dependencies
docker compose ps | grep -E "(postgres|mosquitto|backend)"

# Verify backend waits for dependencies
docker compose logs backend | grep -i "waiting\|ready\|connecting"
```

### Network Connectivity
```bash
# Internal network connectivity
docker exec taylordashv1-backend-1 nc -zv postgres 5432
docker exec taylordashv1-backend-1 nc -zv mosquitto 1883

# Service discovery
docker network inspect taylordash | jq '.[] | .Containers'
```

## Configuration Validation

### Environment Variables
```bash
# Backend environment check
docker exec taylordashv1-backend-1 env | grep -E "(DATABASE_URL|MQTT_|POSTGRES_)"

# Configuration consistency
diff <(grep -E "^(POSTGRES_|MQTT_)" .env) <(docker compose config | grep -E "(POSTGRES_|MQTT_)")
```

### Critical Files
```bash
# Required configuration files
ls -la infra/postgres/init.sql
ls -la infra/mosquitto/mosquitto.conf
ls -la backend/app/database/plugin_schema.sql

# File permissions
docker exec taylordashv1-postgres-1 ls -la /docker-entrypoint-initdb.d/
```

## Performance Metrics

### Resource Usage
```bash
# Container resource consumption
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}"

# Database connections
docker exec -it taylordashv1-postgres-1 psql -U taylordash -d taylordash -c "SELECT count(*) FROM pg_stat_activity WHERE state = 'active';"
```

### Event Processing
```bash
# MQTT event statistics
curl -H "X-API-Key: taylordash-dev-key" http://localhost:8000/api/v1/events?limit=10

# DLQ monitoring
curl -H "X-API-Key: taylordash-dev-key" http://localhost:8000/api/v1/dlq?limit=10
```

## Severity Levels

- **CRITICAL**: System completely unavailable
- **HIGH**: Core functionality impaired
- **MEDIUM**: Degraded performance or minor feature issues
- **LOW**: Cosmetic issues or non-essential features

## Escalation Path

1. **Level 1**: Run health checklist, review recent logs
2. **Level 2**: Contact backend_dev agent for API issues
3. **Level 3**: Contact infra_compose agent for infrastructure
4. **Level 4**: Contact architect agent for design decisions

## Common Red Flags

- Multiple uvicorn processes running simultaneously
- Database connection timeouts
- MQTT broker connection refused
- Plugin permission errors (`must be owner`)
- Logging type errors (`dict + string`)
- Service startup race conditions