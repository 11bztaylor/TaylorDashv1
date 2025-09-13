# Service Startup Guide

Proper service startup sequences and dependency management for TaylorDash infrastructure.

## Service Dependency Tree

```
Infrastructure Layer:
├── postgres (database)
├── mosquitto (MQTT broker)  
├── minio (object storage)
└── prometheus/grafana (monitoring)

Application Layer:
├── backend (depends on: postgres, mosquitto)
├── frontend (depends on: backend)
└── traefik (reverse proxy)
```

## Recommended Startup Sequence

### 1. Infrastructure Services
```bash
# Start core infrastructure first
docker compose up -d postgres mosquitto minio

# Wait for health checks to pass
docker compose ps | grep -E "(postgres|mosquitto|minio)"

# Verify services are healthy (retry if starting)
timeout 60s bash -c 'until docker compose ps | grep postgres | grep -q healthy; do sleep 2; done'
timeout 60s bash -c 'until docker compose ps | grep mosquitto | grep -q healthy; do sleep 2; done'
```

### 2. Backend Services  
```bash
# Start backend after dependencies are healthy
docker compose up -d backend

# Monitor backend startup logs
docker compose logs -f backend &

# Wait for backend readiness
timeout 120s bash -c 'until curl -sf http://localhost:8000/health/ready; do sleep 5; done'
```

### 3. Frontend & Proxy
```bash
# Start frontend and reverse proxy
docker compose up -d frontend traefik

# Verify full stack health
curl -H "X-API-Key: taylordash-dev-key" http://localhost:8000/api/v1/health/stack
```

## Health Check Validation

### Service Health Dependencies
Each service defines health checks in docker-compose.yml:

```yaml
postgres:
  healthcheck:
    test: ["CMD-SHELL", "pg_isready -U taylordash -d taylordash -h localhost"]
    interval: 30s
    timeout: 10s
    retries: 3

mosquitto:
  healthcheck:  
    test: ["CMD", "mosquitto_pub", "-h", "localhost", "-t", "test", "-m", "health", "-u", "taylordash", "-P", "taylordash"]
    interval: 30s
    timeout: 10s
    retries: 3

backend:
  depends_on:
    postgres:
      condition: service_healthy
    mosquitto:
      condition: service_healthy
```

### Manual Health Verification
```bash
# Check all service health status
docker compose ps --format "table {{.Names}}\t{{.Status}}"

# Individual service checks
docker exec taylordashv1-postgres-1 pg_isready -U taylordash -d taylordash
mosquitto_pub -h localhost -t test/health -m "ping" -u taylordash -P taylordash
curl http://localhost:8000/health/ready
```

## Startup Script Template

Create `/TaylorProjects/TaylorDashv1/scripts/startup.sh`:

```bash
#!/bin/bash
set -e

echo "Starting TaylorDash services..."

# Step 1: Infrastructure services
echo "Step 1: Starting infrastructure services..."
docker compose up -d postgres mosquitto minio victoriametrics

echo "Waiting for infrastructure services to be healthy..."
timeout 120s bash -c '
  while ! docker compose ps | grep postgres | grep -q healthy; do
    echo "Waiting for postgres..."
    sleep 5
  done
'

timeout 60s bash -c '
  while ! docker compose ps | grep mosquitto | grep -q healthy; do  
    echo "Waiting for mosquitto..."
    sleep 5
  done
'

# Step 2: Backend service
echo "Step 2: Starting backend service..."
docker compose up -d backend

echo "Waiting for backend to be ready..."
timeout 120s bash -c '
  while ! curl -sf http://localhost:8000/health/ready >/dev/null 2>&1; do
    echo "Waiting for backend..."
    sleep 5
  done
'

# Step 3: Frontend and monitoring
echo "Step 3: Starting frontend and monitoring..."
docker compose up -d frontend traefik prometheus grafana

# Verify full stack
echo "Verifying full stack health..."
sleep 10
if curl -sf -H "X-API-Key: taylordash-dev-key" http://localhost:8000/api/v1/health/stack >/dev/null; then
  echo "✅ TaylorDash startup completed successfully"
else
  echo "❌ Stack health check failed"
  exit 1
fi
```

## Development vs Production Startup

### Development (Quick Start)
```bash
# Fast startup for development (all services)
docker compose up -d

# Monitor critical services
docker compose logs -f postgres backend mosquitto
```

### Production (Staged Startup)
```bash
# Use staged startup script
chmod +x scripts/startup.sh
./scripts/startup.sh

# Enable monitoring
docker compose up -d prometheus grafana
```

## Graceful Shutdown

### Recommended Shutdown Order
```bash
# 1. Stop application layer first
docker compose stop frontend backend traefik

# 2. Stop monitoring (optional)  
docker compose stop prometheus grafana

# 3. Stop infrastructure last
docker compose stop postgres mosquitto minio victoriametrics

# 4. Clean shutdown
docker compose down
```

### Emergency Shutdown
```bash
# Force stop all services
docker compose kill
docker compose down --remove-orphans
```

## Common Startup Failures

### Database Not Ready
```bash
# Symptoms: Backend fails to connect to postgres
# Solution: Wait for postgres health check
timeout 60s bash -c 'until docker compose ps | grep postgres | grep -q healthy; do sleep 2; done'
```

### MQTT Broker Unavailable  
```bash
# Symptoms: Backend warns about MQTT connection failure
# Solution: Verify mosquitto is running and healthy
docker compose restart mosquitto
timeout 30s bash -c 'until docker compose ps | grep mosquitto | grep -q healthy; do sleep 2; done'
```

### Port Conflicts
```bash
# Symptoms: Service fails to bind to port
# Solution: Check for existing processes
lsof -i :8000 :5432 :1883 :3000
docker container prune -f
```

### Volume Permission Issues
```bash
# Symptoms: Container exits with permission errors
# Solution: Fix volume permissions
sudo chown -R 999:999 postgres_data/
sudo chown -R 1883:1883 mosquitto_data/
```

## Monitoring Startup Progress

### Real-time Status Dashboard
```bash
# Monitor all services
watch 'docker compose ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"'

# Monitor critical logs
docker compose logs -f postgres backend mosquitto | grep -E "(ready|error|failed|healthy)"
```

### Automated Health Monitoring
```bash
# Check every 30 seconds for 5 minutes
for i in {1..10}; do
  echo "Health check attempt $i:"
  docker compose ps | grep -E "(postgres|mosquitto|backend)" | grep healthy
  sleep 30
done
```

## Startup Performance Optimization

### Parallel Service Startup
```bash
# Start independent services in parallel
docker compose up -d postgres mosquitto minio &
docker compose up -d victoriametrics prometheus &
wait

# Start dependent services after infrastructure is ready
docker compose up -d backend frontend traefik
```

### Resource Allocation
```yaml
# Optimize for faster startup in docker-compose.yml
services:
  postgres:
    deploy:
      resources:
        limits:
          memory: 512M
        reservations:
          memory: 256M
```

## Troubleshooting Startup Issues

1. **Check service order**: Ensure dependencies start before dependents
2. **Verify health checks**: All health checks must pass before dependent services start
3. **Monitor resource usage**: Insufficient resources can cause startup failures
4. **Check configuration**: Validate .env and docker-compose.yml consistency
5. **Review logs**: Use `docker compose logs <service>` for detailed error information

## Emergency Recovery Procedures

If startup completely fails:
```bash
# Full system reset
docker compose down --volumes --remove-orphans
docker system prune -f
docker volume prune -f

# Restart with clean state
./scripts/startup.sh
```