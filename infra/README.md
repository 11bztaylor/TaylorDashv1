# 🐳 TaylorDash Infrastructure

Docker-based infrastructure for TaylorDash with Docker Compose orchestration, service monitoring, and operational tools.

## 📁 Infrastructure Components

- **`postgres/`** - PostgreSQL database configuration
- **`mosquitto/`** - MQTT broker setup
- **`grafana/`** - Monitoring dashboards
- **`prometheus/`** - Metrics collection
- **`traefik/`** - Reverse proxy and TLS termination
- **`minio/`** - Object storage for file management
- **`timescale/`** - Time-series database extension

## 💻 Code Examples

### Common Patterns

#### Docker Compose Operations
```bash
# Start all services
docker-compose up -d

# Start specific services
docker-compose up -d postgres mosquitto

# View logs
docker-compose logs -f backend
docker-compose logs --tail=100 postgres

# Check service status
docker-compose ps

# Stop services
docker-compose stop
docker-compose down

# Rebuild and restart
docker-compose up -d --build backend

# Scale services
docker-compose up -d --scale backend=3
```

#### Service Health Checks
```bash
# Check backend health
curl -f http://localhost:8000/health/ || echo "Backend unhealthy"

# Check database connectivity
docker-compose exec postgres pg_isready -U taylordash_app

# Check MQTT broker
docker-compose exec mosquitto mosquitto_pub -h localhost -t test/topic -m "health check"

# Check all services
docker-compose exec backend python -c "
import asyncio
import aiohttp
async def check():
    async with aiohttp.ClientSession() as session:
        async with session.get('http://localhost:8000/health/') as resp:
            print(f'Backend: {resp.status}')
asyncio.run(check())
"
```

#### Database Operations
```bash
# Connect to database
docker-compose exec postgres psql -U taylordash_app -d taylordash

# Backup database
docker-compose exec postgres pg_dump -U taylordash_app taylordash > backup.sql

# Restore database
docker-compose exec -T postgres psql -U taylordash_app -d taylordash < backup.sql

# Monitor database connections
docker-compose exec postgres psql -U taylordash_app -d taylordash -c "
SELECT state, count(*)
FROM pg_stat_activity
WHERE application_name LIKE '%taylordash%'
GROUP BY state;"

# Check database size
docker-compose exec postgres psql -U taylordash_app -d taylordash -c "
SELECT pg_size_pretty(pg_database_size('taylordash'));"
```

### How to Extend

#### 1. Add New Service
```yaml
# Add to docker-compose.yml
version: '3.8'
services:
  my-service:
    image: my-service:latest
    ports:
      - "3000:3000"
    environment:
      - API_URL=http://backend:8000
    depends_on:
      - backend
      - postgres
    networks:
      - taylordash
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    restart: unless-stopped
```

#### 2. Environment Configuration
```bash
# Create environment-specific compose file
# docker-compose.prod.yml
version: '3.8'
services:
  backend:
    image: taylordash/backend:v1.0.0
    environment:
      - DATABASE_URL=postgresql://prod_user:${DB_PASSWORD}@postgres:5432/taylordash_prod
      - MQTT_BROKER_HOST=mosquitto
      - LOG_LEVEL=INFO
    deploy:
      replicas: 3
      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 3
```

### Testing This Component

#### Infrastructure Testing
```bash
# Test script: test_infrastructure.sh
#!/bin/bash
set -e

echo "🚀 Testing TaylorDash Infrastructure"

# Start services
echo "Starting services..."
docker-compose up -d

# Wait for services to be ready
echo "Waiting for services to be ready..."
sleep 30

# Test backend health
echo "Testing backend health..."
curl -f http://localhost:8000/health/ || exit 1

# Test database connectivity
echo "Testing database..."
docker-compose exec -T postgres psql -U taylordash_app -d taylordash -c "SELECT 1;" || exit 1

# Test MQTT broker
echo "Testing MQTT broker..."
docker-compose exec mosquitto mosquitto_pub -h localhost -t test/health -m "test" || exit 1

# Test API endpoints
echo "Testing API endpoints..."
curl -f -H "X-API-Key: taylordash-dev-key" http://localhost:8000/api/v1/plugins/ || exit 1

echo "✅ All infrastructure tests passed!"
```

### Debugging Tips

#### Container Debugging
```bash
# Access container shell
docker-compose exec backend bash
docker-compose exec postgres bash

# Check container resources
docker stats $(docker-compose ps -q)

# View container logs with timestamps
docker-compose logs -t -f backend

# Check container health
docker inspect $(docker-compose ps -q backend) | jq '.[0].State.Health'

# Debug networking
docker-compose exec backend ping postgres
docker-compose exec backend nslookup mosquitto
```

### API Usage

#### Service Discovery
```python
# Service discovery helper
import docker
import json

def get_service_info():
    """Get information about running services"""
    client = docker.from_env()
    services = {}

    for container in client.containers.list():
        if 'taylordash' in container.name:
            services[container.name] = {
                'status': container.status,
                'ports': container.ports,
                'image': container.image.tags[0] if container.image.tags else 'unknown',
                'health': container.health if hasattr(container, 'health') else 'unknown'
            }

    return services

# Usage
services = get_service_info()
print(json.dumps(services, indent=2))
```

#### Backup Automation
```bash
#!/bin/bash
# backup.sh - Automated backup script

BACKUP_DIR="/backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

echo "📦 Starting TaylorDash backup..."

# Database backup
echo "Backing up database..."
docker-compose exec -T postgres pg_dump -U taylordash_app taylordash | gzip > "$BACKUP_DIR/database.sql.gz"

# Application data backup
echo "Backing up application data..."
docker-compose exec backend tar -czf - /app/data 2>/dev/null > "$BACKUP_DIR/app_data.tar.gz" || true

# Configuration backup
echo "Backing up configuration..."
cp docker-compose.yml "$BACKUP_DIR/"
cp -r .env* "$BACKUP_DIR/" 2>/dev/null || true

echo "✅ Backup completed: $BACKUP_DIR"
```

## 🚀 Operational Commands

```bash
# Common operations
docker-compose up -d                    # Start services
docker-compose down                     # Stop and remove
docker-compose restart backend          # Restart specific service
docker-compose logs -f --tail=100       # Follow logs
docker-compose exec backend bash        # Access container
docker-compose pull && docker-compose up -d  # Update services

# Maintenance
docker system prune -f                  # Clean up unused resources
docker volume prune -f                  # Clean up unused volumes
docker-compose down -v                  # Remove with volumes (destructive)
```