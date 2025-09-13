# Common Issues Resolution Guide

Solutions for frequently encountered TaylorDash failure patterns based on production incidents.

## 1. Logging System Type Errors

### Symptoms
```
TypeError: dict + string
JSON serialization failed in structured logging
```

### Root Cause
String concatenation with dict objects in logging_utils.py

### Quick Fix
```bash
# Check logging middleware for type errors
docker compose logs backend | grep -i "typeerror\|json"

# Restart backend to clear corrupted state
docker compose restart backend
```

### Permanent Solution
```python
# Ensure proper JSON serialization in logging
context = context or {}
log_entry["context"] = json.dumps(context) if isinstance(context, dict) else str(context)
```

### Prevention
- Validate context data types before logging
- Use structured logger methods consistently
- Test logging with various data types

## 2. Database Authentication Failures

### Symptoms
```
FATAL: password authentication failed for user "taylordash"
Connection refused to postgres:5432
```

### Root Cause
Mismatch between .env DATABASE_URL and docker-compose.yml postgres credentials

### Resolution Steps
```bash
# 1. Check environment consistency
grep DATABASE_URL .env
grep POSTGRES_PASSWORD docker-compose.yml

# 2. Verify container environment
docker exec taylordashv1-postgres-1 env | grep POSTGRES

# 3. Reset database with correct credentials
docker compose down postgres
docker volume rm taylordashv1_postgres_data
docker compose up -d postgres

# 4. Wait for initialization and test
sleep 30
docker exec taylordashv1-postgres-1 pg_isready -U taylordash -d taylordash
```

### Configuration Fix
Ensure .env and docker-compose.yml match:
```env
# .env
DATABASE_URL=postgresql://taylordash:taylordash_secure_password@postgres:5432/taylordash
POSTGRES_PASSWORD=taylordash_secure_password
```

## 3. Plugin Table Permission Issues

### Symptoms
```
ERROR: must be owner of table plugins
Permission denied for table plugins
```

### Root Cause
Plugin tables created with wrong ownership during migrations

### Resolution
```bash
# Fix table ownership
docker exec -it taylordashv1-postgres-1 psql -U postgres -d taylordash -c "
ALTER TABLE plugins OWNER TO taylordash_app;
ALTER TABLE plugin_permissions OWNER TO taylordash_app;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO taylordash_app;
"

# Verify ownership
docker exec -it taylordashv1-postgres-1 psql -U taylordash -d taylordash -c "
SELECT schemaname, tablename, tableowner 
FROM pg_tables 
WHERE tablename LIKE '%plugin%';
"
```

### Prevention
- Run migrations with app user, not postgres superuser
- Use proper database initialization scripts
- Validate permissions after schema changes

## 4. MQTT Connection Failures with Graceful Degradation

### Symptoms
```
MQTT connection refused
Failed to connect to mosquitto:1883
Backend continues running without MQTT
```

### Diagnostic Steps
```bash
# Check MQTT broker status
docker compose ps mosquitto
docker compose logs mosquitto | tail -20

# Test broker connectivity
docker exec taylordashv1-backend-1 nc -zv mosquitto 1883

# Verify authentication
mosquitto_pub -h localhost -t test -m "auth_test" -u taylordash -P taylordash
```

### Resolution
```bash
# 1. Restart MQTT broker
docker compose restart mosquitto

# 2. Check broker configuration
docker exec taylordashv1-mosquitto-1 cat /mosquitto/config/mosquitto.conf

# 3. Verify password file
docker exec taylordashv1-mosquitto-1 cat /mosquitto/config/password_file

# 4. If credentials corrupted, regenerate
mosquitto_passwd -c infra/mosquitto/password_file taylordash
docker compose restart mosquitto
```

### Expected Behavior
Backend should:
- Log MQTT connection failure as WARNING
- Continue operating without MQTT functionality
- Retry connection with exponential backoff
- Gracefully handle MQTT publish failures

## 5. Multiple Backend Process Conflicts

### Symptoms
```
Port 8000 already in use
Multiple uvicorn processes detected
Prometheus metrics conflicts
```

### Detection
```bash
# Check for duplicate processes
docker exec taylordashv1-backend-1 ps aux | grep uvicorn
docker exec taylordashv1-backend-1 netstat -tlnp | grep :8000

# Check for orphaned containers
docker ps -a | grep backend
```

### Resolution
```bash
# 1. Stop all backend containers
docker compose stop backend
docker container prune -f

# 2. Check for port conflicts
lsof -i :8000 || netstat -tlnp | grep :8000

# 3. Clean restart
docker compose up -d backend

# 4. Verify single process
docker exec taylordashv1-backend-1 ps aux | grep -c uvicorn
```

### Prevention
- Use `docker compose stop` instead of `docker stop`
- Implement proper process cleanup in Dockerfile
- Monitor for duplicate containers in health checks

## 6. Service Dependency Startup Race Conditions

### Symptoms
```
Database connection failed during startup
MQTT processor initialization failed
Backend exits with dependency errors
```

### Solution Pattern
Use proper health checks and depends_on:
```yaml
backend:
  depends_on:
    postgres:
      condition: service_healthy
    mosquitto:
      condition: service_healthy
```

### Manual Recovery
```bash
# 1. Start dependencies first
docker compose up -d postgres mosquitto

# 2. Wait for health checks
docker compose ps | grep -E "(healthy|starting)"

# 3. Start backend
docker compose up -d backend

# 4. Monitor startup logs
docker compose logs -f backend
```

### Verification
```bash
# Check dependency order
docker compose config | grep -A 10 depends_on

# Verify health check functionality
docker compose ps | grep healthy
```

## Error Patterns and Quick Actions

| Error Pattern | Quick Action | Agent Contact |
|---------------|--------------|---------------|
| `TypeError.*dict.*string` | Restart backend | backend_dev |
| `password authentication failed` | Check .env vs compose | infra_compose |
| `must be owner of table` | Fix table ownership | backend_dev |
| `MQTT connection refused` | Restart mosquitto | infra_compose |
| `Port.*already in use` | Stop duplicate containers | infra_compose |
| `Database.*not ready` | Wait for postgres health | infra_compose |

## Critical Configuration Files

Verify these files for common misconfigurations:
- `/TaylorProjects/TaylorDashv1/.env` - Environment variables
- `/TaylorProjects/TaylorDashv1/docker-compose.yml` - Service definitions
- `/TaylorProjects/TaylorDashv1/infra/postgres/init.sql` - Database initialization
- `/TaylorProjects/TaylorDashv1/infra/mosquitto/mosquitto.conf` - MQTT configuration
- `/TaylorProjects/TaylorDashv1/backend/app/database/plugin_schema.sql` - Plugin schema