# TaylorDash Clean Architecture Design

## Executive Summary

This document defines the canonical port assignments, service organization, and architectural standards for TaylorDash to eliminate the current chaos in port management and service startup sequences. The design establishes clear boundaries between development and production environments while maintaining security and scalability.

## Current State Analysis

### Identified Issues
- **Port Conflicts**: Multiple services competing for same ports (5173, 5174, etc.)
- **Inconsistent Port Assignment**: Random port usage across plugins without coordination
- **Service Dependency Chaos**: No clear startup sequence or dependency mapping
- **Environment Variable Sprawl**: Inconsistent environment configuration across services
- **Development vs Production Confusion**: Same ports used in different contexts

### Architecture Violations
- Multiple frontend instances instead of single unified frontend
- Plugins running as separate Vite servers instead of integrated components
- No centralized service registry or discovery mechanism
- Backend API hardcoded to single port without load balancing capability

## 1. Canonical Port Assignments

### Production Environment (Docker Compose)

#### Core Infrastructure Ports
```
80      - Traefik HTTP (public)
443     - Traefik HTTPS (public)
8080    - Traefik Dashboard (internal)
5432    - PostgreSQL (internal + dev access)
1883    - MQTT Plain (internal)
8883    - MQTT TLS (internal)
9001    - MQTT WebSocket (internal)
```

#### Application Services
```
8000    - Backend API (internal)
3000    - Frontend Application (internal)
```

#### Monitoring & Observability
```
9000    - MinIO API (internal)
9001    - MinIO Console (internal)
8428    - VictoriaMetrics (internal)
9090    - Prometheus (internal)
3000    - Grafana (internal) [Note: Shared with frontend via Traefik routing]
```

### Development Environment

#### Core Development Ports
```
8000    - Backend API (direct access)
5173    - Frontend Development Server (Vite)
```

#### Plugin Development Ports (Reserved Range: 5174-5179)
```
5174    - MCP Manager Plugin
5175    - Projects Manager Plugin
5176    - Midnight HUD Plugin
5177-5179 - Reserved for future plugins
```

#### Development Support Services
```
5432    - PostgreSQL (direct access)
1883    - MQTT (direct access)
8428    - VictoriaMetrics (direct access)
9090    - Prometheus (direct access)
```

### Port Assignment Rules

1. **Production**: All external access via Traefik (80/443)
2. **Development**: Direct port access for debugging
3. **Plugin Range**: 5174-5179 reserved exclusively for plugin development
4. **Service Discovery**: All services must register their ports in environment variables
5. **Port Conflicts**: Use `netstat -tulpn` validation before startup

## 2. Service Dependency Mapping

### Dependency Hierarchy

```mermaid
graph TB
    A[PostgreSQL] --> B[Backend API]
    A --> C[MQTT Broker]
    B --> D[Frontend App]
    C --> B
    E[Traefik] --> D
    E --> F[Monitoring Stack]
    G[Plugin Development] --> B
    G --> D
```

### Critical Dependencies

#### Tier 1 - Foundation Services
- **PostgreSQL**: Database layer - MUST start first
- **MQTT Broker**: Event bus - MUST be available before backend

#### Tier 2 - Core Application
- **Backend API**: Depends on PostgreSQL + MQTT
- **Frontend Application**: Depends on Backend API for initial routing

#### Tier 3 - Infrastructure Services
- **Traefik**: Reverse proxy - can start independently
- **Monitoring Stack**: Observability - can start independently

#### Tier 4 - Development Services
- **Plugin Development Servers**: Independent Vite instances for development only

## 3. Service Startup Sequence

### Production Startup (Docker Compose)

```bash
# Phase 1: Foundation (30s timeout each)
docker-compose up -d postgres mosquitto

# Phase 2: Core Application (60s timeout)
docker-compose up -d backend

# Phase 3: Frontend & Routing (30s timeout)
docker-compose up -d frontend traefik

# Phase 4: Monitoring (Independent)
docker-compose up -d victoriametrics prometheus grafana minio
```

### Development Startup

```bash
# Phase 1: Foundation Services
docker-compose up -d postgres mosquitto

# Phase 2: Backend Development
cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Phase 3: Frontend Development
cd frontend && npm run dev  # Port 5173

# Phase 4: Plugin Development (as needed)
cd examples/mcp-manager && npm run dev      # Port 5174
cd examples/projects-manager && npm run dev # Port 5175
cd examples/midnight-hud && npm run dev     # Port 5176
```

### Health Check Sequence

Each service must pass health checks before dependents start:

1. **PostgreSQL**: `pg_isready -U taylordash -d taylordash`
2. **MQTT**: `mosquitto_pub -h localhost -t test -m health`
3. **Backend**: `curl -f http://localhost:8000/health/ready`
4. **Frontend**: `curl -f http://localhost:5173/` (dev) or via Traefik (prod)

## 4. Service Management Procedures

### Development Environment

#### Single Service Management
```bash
# Backend only
make dev-backend

# Frontend only
make dev-frontend

# Full development stack
make dev-full
```

#### Plugin Development
```bash
# Start plugin development environment
make dev-plugin PLUGIN=mcp-manager    # Port 5174
make dev-plugin PLUGIN=projects-manager # Port 5175
make dev-plugin PLUGIN=midnight-hud   # Port 5176
```

### Production Environment

#### Full Stack Management
```bash
# Production startup
make prod-up

# Production health check
make prod-health

# Production shutdown
make prod-down
```

#### Service Scaling
```bash
# Scale backend instances
docker-compose up -d --scale backend=3

# Scale monitoring
docker-compose up -d --scale prometheus=2
```

### Emergency Procedures

#### Port Conflict Resolution
```bash
# Check port usage
netstat -tulpn | grep :5173

# Kill conflicting processes
sudo lsof -ti:5173 | xargs kill -9

# Restart with alternative port
PORT=5180 npm run dev
```

#### Service Recovery
```bash
# Individual service restart
docker-compose restart backend

# Full system restart
make prod-restart

# Reset all data (DANGEROUS)
make prod-reset
```

## 5. Environment Variable Standards

### Backend Configuration

#### Required Variables
```bash
# Database
DATABASE_URL=postgresql://taylordash_app:password@postgres:5432/taylordash
POSTGRES_PASSWORD=<secure_password>

# MQTT
MQTT_HOST=mosquitto
MQTT_PORT=1883
MQTT_USERNAME=taylordash
MQTT_PASSWORD=<secure_password>

# API Security
API_KEY=<random_64_char_key>
JWT_SECRET=<random_256_bit_key>

# Service Discovery
BACKEND_PORT=8000
BACKEND_HOST=0.0.0.0
```

#### Optional Variables
```bash
# Observability
OTEL_EXPORTER_OTLP_ENDPOINT=http://jaeger:4317
PROMETHEUS_ENDPOINT=http://prometheus:9090

# Feature Flags
ENABLE_PLUGIN_SYSTEM=true
ENABLE_AUTHENTICATION=true
ENABLE_METRICS=true
```

### Frontend Configuration

#### Build-time Variables
```bash
# API Configuration
VITE_API_BASE_URL=http://localhost:8000/api
VITE_FRONTEND_PORT=5173

# Feature Flags
VITE_ENABLE_PLUGINS=true
VITE_ENABLE_AUTH=true
VITE_ENABLE_DEBUG=false
```

#### Runtime Variables (via .env.local)
```bash
# Development specific
VITE_DEV_MODE=true
VITE_HOT_RELOAD=true

# Production specific
VITE_PROD_MODE=true
VITE_ENABLE_ANALYTICS=true
```

### Plugin Configuration

#### Standard Plugin Variables
```bash
# Plugin Identity
PLUGIN_NAME=<plugin-name>
PLUGIN_VERSION=1.0.0
PLUGIN_PORT=<assigned-port>

# API Integration
TAYLORDASH_API_URL=http://localhost:8000/api
TAYLORDASH_FRONTEND_URL=http://localhost:5173

# Security
PLUGIN_API_KEY=<plugin-specific-key>
PLUGIN_SANDBOX_MODE=true
```

### Environment File Structure

```
/TaylorProjects/TaylorDashv1/
├── .env                    # Global production configuration
├── .env.example           # Template with safe defaults
├── .env.development       # Development overrides
├── .env.test             # Test environment
├── backend/
│   ├── .env              # Backend-specific production
│   ├── .env.development  # Backend development
│   └── .env.test         # Backend testing
├── frontend/
│   ├── .env.local        # Frontend development (gitignored)
│   └── .env.production   # Frontend production build
└── examples/
    ├── mcp-manager/.env
    ├── projects-manager/.env
    └── midnight-hud/.env
```

## 6. Architectural Decision Record (ADR)

### ADR: TaylorDash Port Management & Service Organization Cleanup

#### Status
Approved - 2025-09-13

#### Context
TaylorDash has grown organically with inconsistent port assignments, unclear service dependencies, and chaotic startup procedures. This creates developer friction, deployment complexity, and operational instability. Multiple services compete for the same ports, and there's no clear distinction between development and production environments.

#### Decision
We will implement a **canonical port assignment system** with **strict service dependency management** and **environment-specific configuration standards**.

#### Consequences

**Benefits:**
- **Elimination of Port Conflicts**: Reserved ranges prevent collision
- **Predictable Service Startup**: Clear dependency hierarchy ensures reliable boot
- **Environment Separation**: Development and production use different port strategies
- **Operational Clarity**: Standardized procedures for all service management tasks
- **Plugin Isolation**: Dedicated port range for plugin development prevents interference

**Tradeoffs:**
- **Migration Effort**: All existing configurations must be updated
- **Documentation Overhead**: New standards require comprehensive documentation
- **Developer Onboarding**: Additional complexity in understanding port assignments
- **Port Range Limitations**: Fixed ranges may require expansion for large plugin ecosystems

#### Implementation

1. **Phase 1: Foundation** (Week 1)
   - Update docker-compose.yml with canonical port assignments
   - Create environment variable templates (.env.example files)
   - Implement health check sequences

2. **Phase 2: Application Layer** (Week 2)
   - Update backend configuration to use standard ports
   - Modify frontend development server configuration
   - Create Makefile with standardized commands

3. **Phase 3: Plugin Migration** (Week 3)
   - Migrate all existing plugins to assigned port range
   - Update plugin documentation with new standards
   - Implement plugin service discovery

4. **Phase 4: Production Deployment** (Week 4)
   - Deploy production environment with new architecture
   - Create monitoring dashboards for service health
   - Document operational procedures

5. **Phase 5: Documentation & Training** (Week 5)
   - Complete architecture documentation
   - Create developer onboarding guides
   - Conduct team training on new procedures

## Implementation Checklist

### Immediate Actions (Day 1)
- [ ] Update docker-compose.yml port mappings
- [ ] Create .env.example templates
- [ ] Update frontend/backend Vite/FastAPI configurations
- [ ] Test basic service startup sequence

### Short Term (Week 1)
- [ ] Migrate all plugin configurations
- [ ] Create Makefile with service management commands
- [ ] Implement health check endpoints
- [ ] Update all documentation references

### Medium Term (Month 1)
- [ ] Deploy production environment
- [ ] Create monitoring dashboards
- [ ] Implement automated service discovery
- [ ] Performance test the new architecture

### Long Term (Quarter 1)
- [ ] Plugin marketplace with automatic port assignment
- [ ] Service mesh implementation for advanced routing
- [ ] Automated scaling based on port utilization
- [ ] Advanced monitoring and alerting

## Validation Criteria

### Technical Validation
- [ ] All services start without port conflicts
- [ ] Health checks pass in correct dependency order
- [ ] Environment variables load correctly in all contexts
- [ ] Plugin development servers work in isolation

### Operational Validation
- [ ] Developers can start any service independently
- [ ] Production deployment completes without manual intervention
- [ ] Service restart procedures work reliably
- [ ] Monitoring provides clear service status

### Security Validation
- [ ] No services expose unnecessary ports
- [ ] All communication uses appropriate encryption
- [ ] Plugin isolation prevents cross-contamination
- [ ] Environment variables don't leak sensitive data

## Conclusion

This clean architecture design establishes TaylorDash as a professionally managed system with clear service boundaries, predictable behavior, and operational excellence. The canonical port assignments eliminate conflicts while the structured dependency management ensures reliable service startup.

The implementation plan provides a clear path from the current chaotic state to a well-organized system that scales effectively and supports ongoing development without operational friction.

**Success Metrics:**
- Zero port conflicts across all environments
- 100% reliable service startup sequence
- < 2 minute full system startup time
- Developer productivity increase of 30%
- Production deployment reliability > 99.9%

---
*Architecture Design Version: 1.0*
*Document Created: 2025-09-13*
*Next Review: 2025-12-13*