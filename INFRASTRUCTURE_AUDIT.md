# TaylorDash Infrastructure Audit Report

## Executive Summary

The TaylorDash infrastructure is currently in a state of significant disorganization with multiple service conflicts, port duplication, and inefficient resource utilization. This audit identifies critical issues and provides actionable cleanup steps to establish a standardized, maintainable infrastructure.

## Critical Issues Identified

### 1. Service Duplication and Port Conflicts

#### Backend Services
- **3 Python/Uvicorn instances running simultaneously:**
  - Port 3000: `/TaylorProjects/TaylorDashv1/backend/venv/bin/python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 3000`
  - Port 8000: `/usr/local/bin/python3.11 /usr/local/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000`
  - Port 8000: `/TaylorProjects/TaylorDashv1/backend/venv/bin/python3 /TaylorProjects/TaylorDashv1/backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000`
- **Impact:** Resource waste, configuration conflicts, unclear service state

#### Frontend Services
- **6 Vite development servers running:**
  - Port 5173: Main frontend (IPv6) - `/TaylorProjects/TaylorDashv1/frontend/node_modules/.bin/vite`
  - Port 5176: Main frontend (IPv6) - `/TaylorProjects/TaylorDashv1/frontend/node_modules/.bin/vite`
  - Port 5178: Main frontend - `/TaylorProjects/TaylorDashv1/frontend/node_modules/.bin/vite --host 0.0.0.0 --port 5178`
  - Port 5174: MCP Manager - `/TaylorProjects/TaylorDashv1/examples/mcp-manager/node_modules/.bin/vite --port 5174 --host 0.0.0.0`
  - Port 5175: Projects Manager - `/TaylorProjects/TaylorDashv1/examples/projects-manager/node_modules/.bin/vite --port 5175 --host 0.0.0.0`
  - Port 5177: Midnight HUD - `/TaylorProjects/TaylorDashv1/examples/midnight-hud/node_modules/.bin/vite --host 0.0.0.0`

### 2. Docker vs Standalone Service Conflicts

#### Properly Containerized Services
- ✅ Traefik (Ports 80, 443, 8080)
- ✅ PostgreSQL (Port 5432)
- ✅ VictoriaMetrics (Port 8428)
- ✅ MinIO (Ports 9000, 9001)
- ✅ Mosquitto MQTT (Ports 1883, 8883, 9001)
- ✅ Prometheus (Internal only)
- ✅ Grafana (Internal only)

#### Services Running Outside Docker
- ❌ Backend API (3 instances on ports 3000, 8000, 8000)
- ❌ Frontend applications (6 instances on ports 5173-5178)
- ❌ Example applications (should be containerized for consistency)

### 3. Network Configuration Issues

- Docker network "taylordash" exists but standalone services bypass it
- Traefik routing configured but backend not properly integrated
- No consistent service discovery mechanism
- Port conflicts preventing proper load balancing

### 4. Environment Variable Management

#### Current State
- Docker Compose uses `.env` file properly
- Standalone services use inconsistent environment configuration
- Database credentials duplicated across configurations
- Some services hardcode configuration values

## Recommended Architecture

### Service Categorization

#### Core Infrastructure (Docker Compose)
- Traefik (Reverse Proxy)
- PostgreSQL (Database)
- VictoriaMetrics (TSDB)
- MinIO (Object Storage)
- Mosquitto (MQTT Broker)
- Prometheus (Metrics)
- Grafana (Visualization)

#### Application Services (Should be Containerized)
- TaylorDash Backend API
- TaylorDash Frontend
- Plugin Examples (Development only)

### Standardized Port Allocation

#### Production Ports (Docker Compose)
```yaml
# External facing
80/443: Traefik (HTTP/HTTPS)
8080: Traefik Dashboard

# Database & Storage
5432: PostgreSQL
8428: VictoriaMetrics
9000/9001: MinIO

# Message Broker
1883/8883/9001: Mosquitto MQTT

# Internal services (no external ports)
- Backend API (via Traefik)
- Frontend (via Traefik)
- Prometheus
- Grafana
```

#### Development Ports (Local override)
```yaml
3000: Backend API (local development)
5173: Frontend (local development)
5174-5179: Plugin examples (development only)
```

## Cleanup Procedures

### Phase 1: Service Inventory and Termination

#### Step 1: Stop All Duplicate Services
```bash
# Kill duplicate backend processes
pkill -f "uvicorn.*port.*3000"
pkill -f "uvicorn.*port.*8000"

# Kill duplicate frontend processes
pkill -f "vite.*5173"
pkill -f "vite.*5176"
pkill -f "vite.*5178"

# Keep only the intended development services
# Port 5174: MCP Manager
# Port 5175: Projects Manager
# Port 5177: Midnight HUD
```

#### Step 2: Clean Docker State
```bash
# Stop all containers
docker-compose down

# Remove orphaned containers
docker container prune -f

# Verify network state
docker network ls
docker network inspect taylordash
```

### Phase 2: Configuration Standardization

#### Step 1: Update Docker Compose Configuration
```yaml
# Add backend service to docker-compose.yml
backend:
  build:
    context: ./backend
    dockerfile: Dockerfile
  restart: unless-stopped
  environment:
    DATABASE_URL: postgresql://taylordash:${POSTGRES_PASSWORD}@postgres:5432/taylordash
    MQTT_HOST: mosquitto
    MQTT_PORT: 1883
    API_KEY: ${API_KEY:-taylordash-dev-key}
  depends_on:
    postgres:
      condition: service_healthy
    mosquitto:
      condition: service_healthy
  labels:
    - "traefik.enable=true"
    - "traefik.http.routers.backend.rule=Host(`taylordash.local`) && PathPrefix(`/api`)"
    - "traefik.http.services.backend.loadbalancer.server.port=8000"

# Add frontend service
frontend:
  build:
    context: ./frontend
    dockerfile: Dockerfile
  restart: unless-stopped
  depends_on:
    - backend
  labels:
    - "traefik.enable=true"
    - "traefik.http.routers.frontend.rule=Host(`taylordash.local`)"
    - "traefik.http.services.frontend.loadbalancer.server.port=80"
```

#### Step 2: Environment Variable Consolidation
```bash
# Update .env file
API_KEY=your-secure-api-key-here
DATABASE_URL=postgresql://taylordash:${POSTGRES_PASSWORD}@postgres:5432/taylordash
MQTT_HOST=mosquitto
MQTT_PORT=1883
MQTT_USERNAME=taylordash
MQTT_PASSWORD=${MQTT_PASSWORD}
```

### Phase 3: Service Management Scripts

#### Production Startup Script
```bash
#!/bin/bash
# scripts/start-production.sh

echo "Starting TaylorDash Production Environment..."

# Start core infrastructure
docker-compose up -d postgres mosquitto victoriametrics minio

# Wait for database
echo "Waiting for database..."
until docker-compose exec postgres pg_isready -U taylordash; do
  sleep 1
done

# Start application services
docker-compose up -d backend frontend

# Start monitoring
docker-compose up -d prometheus grafana

# Start reverse proxy
docker-compose up -d traefik

echo "Production environment started!"
echo "Access at: https://taylordash.local"
```

#### Development Startup Script
```bash
#!/bin/bash
# scripts/start-development.sh

echo "Starting TaylorDash Development Environment..."

# Start only infrastructure services
docker-compose up -d postgres mosquitto victoriametrics minio prometheus grafana

# Wait for services
echo "Waiting for services to be ready..."
sleep 10

# Start local development servers
echo "Starting backend (port 3000)..."
cd backend && source venv/bin/activate && uvicorn app.main:app --reload --host 0.0.0.0 --port 3000 &

echo "Starting frontend (port 5173)..."
cd ../frontend && npm run dev &

# Start traefik with development overrides
docker-compose up -d traefik

echo "Development environment started!"
echo "Backend API: http://localhost:3000"
echo "Frontend: http://localhost:5173"
echo "Traefik Dashboard: http://localhost:8080"
```

#### Cleanup Script
```bash
#!/bin/bash
# scripts/cleanup-infrastructure.sh

echo "Cleaning up TaylorDash infrastructure..."

# Stop all development servers
pkill -f "uvicorn.*app.main:app"
pkill -f "vite"

# Stop and remove all containers
docker-compose down -v

# Remove unused containers and networks
docker system prune -f

# Clean up orphaned processes
ps aux | grep -E "(node.*vite|python.*uvicorn)" | grep -v grep | awk '{print $2}' | xargs -r kill

echo "Infrastructure cleanup complete!"
```

### Phase 4: Service Health Monitoring

#### Health Check Script
```bash
#!/bin/bash
# scripts/health-check.sh

echo "TaylorDash Infrastructure Health Check"
echo "======================================"

# Check Docker services
echo "Docker Services:"
docker-compose ps

echo -e "\nPort Usage:"
netstat -tlnp | grep -E "(80|443|3000|5173|5432|8428|1883|8080|9000|9001)"

echo -e "\nProcess Status:"
ps aux | grep -E "(traefik|postgres|uvicorn|vite)" | grep -v grep

echo -e "\nService Endpoints:"
curl -s http://localhost:8080/ping && echo "✅ Traefik OK" || echo "❌ Traefik FAIL"
curl -s http://localhost:3000/health && echo "✅ Backend OK" || echo "❌ Backend FAIL"
curl -s http://localhost:5173 && echo "✅ Frontend OK" || echo "❌ Frontend FAIL"
```

## Implementation Steps

### Immediate Actions (Day 1)
1. Run cleanup script to stop duplicate services
2. Update docker-compose.yml with backend and frontend services
3. Create Dockerfiles for backend and frontend
4. Test production startup script

### Short Term (Week 1)
1. Implement service management scripts
2. Set up monitoring and alerting
3. Create development environment documentation
4. Establish deployment procedures

### Long Term (Month 1)
1. Implement CI/CD pipeline
2. Set up log aggregation
3. Implement backup procedures
4. Create disaster recovery plan

## Service Management Standards

### Development Workflow
1. Use `scripts/start-development.sh` for local development
2. Backend runs on port 3000 with hot reload
3. Frontend runs on port 5173 with hot reload
4. Infrastructure services run in Docker
5. Use `scripts/health-check.sh` to verify status

### Production Workflow
1. Use `scripts/start-production.sh` for production deployment
2. All services run in Docker containers
3. Traefik handles routing and SSL termination
4. Services communicate via Docker networks
5. Monitoring and logging centralized

### Plugin Development
1. Use dedicated ports 5174-5179 for plugin development
2. Each plugin should have its own dev script
3. Plugins should proxy API calls through Traefik
4. Consider containerizing plugins for consistency

## Security Considerations

### Network Security
- All external traffic routes through Traefik
- Internal services communicate via Docker networks
- Firewall rules restrict direct access to service ports
- SSL certificates managed by Traefik

### Access Control
- Database access restricted to application services
- MQTT broker requires authentication
- API endpoints protected with API keys
- Development endpoints not exposed in production

## Monitoring and Alerting

### Key Metrics
- Service uptime and response times
- Database connection health
- MQTT message throughput
- Container resource usage
- Network traffic patterns

### Alert Conditions
- Service failures or crashes
- High response times (>500ms)
- Database connection failures
- Storage space warnings (>80%)
- Memory usage warnings (>85%)

## Conclusion

This infrastructure audit reveals significant organizational issues that require immediate attention. The proposed cleanup procedures and standardized service management approach will:

1. Eliminate resource waste from duplicate services
2. Establish clear development vs production workflows
3. Improve service reliability and monitoring
4. Reduce configuration complexity
5. Enable proper scaling and deployment automation

Following these recommendations will transform the TaylorDash infrastructure from its current chaotic state into a well-organized, maintainable, and scalable system.

## Next Steps

1. **Immediate:** Execute cleanup procedures to stop duplicate services
2. **Priority:** Implement service management scripts and test thoroughly
3. **Critical:** Update documentation and train team on new procedures
4. **Ongoing:** Monitor service health and iterate on improvements

The success of this infrastructure reorganization depends on disciplined execution of these procedures and consistent adherence to the established standards.