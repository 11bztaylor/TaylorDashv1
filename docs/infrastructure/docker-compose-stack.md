# Docker Compose Infrastructure Documentation

## Overview

TaylorDash uses a Docker Compose stack with 8 core services plus optional components, providing a complete containerized infrastructure for production deployment. The stack includes reverse proxy, application services, databases, message queuing, and comprehensive monitoring.

## Infrastructure Status

**Current Production State:**
- ✅ 8 services running and healthy
- ✅ All health checks passing
- ✅ Service discovery operational
- ✅ Persistent storage configured
- ✅ Network isolation implemented
- ✅ Monitoring stack active

## Service Architecture

```mermaid
graph TB
    subgraph "External Access"
        Internet[🌐 Internet]
    end

    subgraph "Traefik Layer"
        Traefik[🔀 Traefik Proxy<br/>Port 80/443/8080]
    end

    subgraph "Application Layer"
        Backend[🚀 FastAPI Backend<br/>Port 8000]
        Frontend[🎨 React Frontend<br/>Static Files]
    end

    subgraph "Data Layer"
        PostgreSQL[(🗄️ PostgreSQL<br/>Port 5432)]
        MQTT[📡 MQTT Broker<br/>Ports 1883/8883/9001]
        MinIO[📦 MinIO S3<br/>Port 9000/9001]
    end

    subgraph "Monitoring Layer"
        VictoriaMetrics[📊 VictoriaMetrics<br/>Port 8428]
        Prometheus[📊 Prometheus<br/>Port 9090]
        Grafana[📈 Grafana<br/>Port 3000]
    end

    subgraph "Optional Services"
        TimescaleDB[(⏰ TimescaleDB<br/>Profile: timescale)]
    end

    Internet --> Traefik
    Traefik --> Backend
    Traefik --> Frontend
    Backend --> PostgreSQL
    Backend --> MQTT
    Backend --> MinIO
    Backend --> VictoriaMetrics
    Prometheus --> Backend
    Prometheus --> VictoriaMetrics
    Grafana --> VictoriaMetrics
    Grafana --> Prometheus

    classDef proxy fill:#e1f5fe
    classDef app fill:#f3e5f5
    classDef data fill:#e8f5e8
    classDef monitor fill:#fff3e0
    classDef optional fill:#fce4ec

    class Traefik proxy
    class Backend,Frontend app
    class PostgreSQL,MQTT,MinIO data
    class VictoriaMetrics,Prometheus,Grafana monitor
    class TimescaleDB optional
```

## Network Configuration

### Docker Network
- **Network Name**: `taylordash`
- **Driver**: bridge
- **Isolation**: Services isolated from host and other networks
- **DNS**: Automatic service discovery via Docker DNS

### External Ports
| Service | Port | Protocol | Purpose |
|---------|------|----------|---------|
| Traefik | 80 | HTTP | Web traffic (redirects to HTTPS) |
| Traefik | 443 | HTTPS | Secure web traffic |
| Traefik | 8080 | HTTP | Dashboard (development) |
| PostgreSQL | 5432 | TCP | Database access (development) |
| MQTT | 1883 | MQTT | MQTT protocol |
| MQTT | 8883 | MQTT-TLS | Secure MQTT |
| MQTT | 9001 | WebSocket | Browser MQTT clients |

### Internal Communication
All services communicate via Docker network using service names:
- `backend:8000` - FastAPI application
- `postgres:5432` - PostgreSQL database
- `mosquitto:1883` - MQTT broker
- `minio:9000` - MinIO storage
- `victoriametrics:8428` - Time series database
- `prometheus:9090` - Metrics collection
- `grafana:3000` - Visualization dashboard

## Service Configurations

### 1. Traefik (Reverse Proxy)

**Image**: `traefik:2.10`

**Purpose**: SSL termination, routing, load balancing, security headers

**Configuration**: `/infra/traefik/traefik.yml`

```yaml
# Key Features
api:
  dashboard: true        # Management dashboard
  insecure: true        # Development mode

entryPoints:
  web:
    address: ":80"      # HTTP entry point
  websecure:
    address: ":443"     # HTTPS entry point

providers:
  docker:
    exposedByDefault: false  # Explicit service exposure
    network: taylordash      # Single network
```

**Security Features**:
- Automatic HTTPS redirect (configurable)
- Let's Encrypt certificate management
- Security headers injection
- Request routing with path-based rules

**Health Check**:
```bash
wget --quiet --tries=1 --spider http://localhost:8080/ping
```

**Labels**:
```yaml
labels:
  - "traefik.enable=true"
```

### 2. FastAPI Backend

**Image**: Custom build from `/backend/Dockerfile`

**Purpose**: Core business logic, API services, authentication

**Environment Variables**:
```yaml
API_KEY: ${API_KEY:-taylordash-dev-key}
DATABASE_URL: postgresql://taylordash_app:password@postgres:5432/taylordash
MQTT_HOST: mosquitto
MQTT_PORT: 1883
MQTT_USERNAME: taylordash
MQTT_PASSWORD: taylordash
OTEL_EXPORTER_OTLP_ENDPOINT: http://jaeger:4317
```

**Volume Mounts**:
```yaml
volumes:
  - ./backend:/app  # Development hot reload
```

**Health Check**:
```bash
curl -f http://localhost:8000/health/ready
```

**Traefik Labels**:
```yaml
labels:
  - "traefik.enable=true"
  - "traefik.http.routers.backend.rule=Host(`taylordash.local`) && PathPrefix(`/api`)"
  - "traefik.http.services.backend.loadbalancer.server.port=8000"
```

**Dependencies**:
- PostgreSQL (service_healthy)
- MQTT (service_healthy)

### 3. PostgreSQL Database

**Image**: `postgres:15`

**Purpose**: Primary data store with ACID guarantees

**Environment Variables**:
```yaml
POSTGRES_DB: taylordash
POSTGRES_USER: taylordash
POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-taylordash}
POSTGRES_INITDB_ARGS: "--auth-host=md5 --auth-local=trust"
```

**Volume Mounts**:
```yaml
volumes:
  - postgres_data:/var/lib/postgresql/data           # Persistent data
  - ./infra/postgres/init.sql:/docker-entrypoint-initdb.d/init.sql:ro  # Schema
```

**Health Check**:
```bash
pg_isready -U taylordash -d taylordash -h localhost
```

**Configuration Features**:
- Application user with restricted permissions
- Automatic schema initialization
- Development port exposure (5432)
- Data persistence across restarts

### 4. Eclipse Mosquitto (MQTT Broker)

**Image**: `eclipse-mosquitto:2`

**Purpose**: Event bus for real-time communication

**Configuration**: `/infra/mosquitto/mosquitto.conf`

```properties
# Security
allow_anonymous false
password_file /mosquitto/config/password_file

# Listeners
listener 1883          # Standard MQTT
listener 9001          # WebSocket for browsers

# Performance
max_connections 1000
max_inflight_messages 20
max_queued_messages 100

# Persistence
persistence true
persistence_location /mosquitto/data/
```

**Volume Mounts**:
```yaml
volumes:
  - ./infra/mosquitto/mosquitto.conf:/mosquitto/config/mosquitto.conf:ro
  - ./infra/mosquitto/password_file:/mosquitto/config/password_file:ro
  - ./certs:/mosquitto/certs:ro
  - mosquitto_data:/mosquitto/data
  - mosquitto_logs:/mosquitto/log
```

**Health Check**:
```bash
mosquitto_pub -h localhost -t test -m health -u taylordash -P taylordash
```

**Authentication**:
- Username/password authentication required
- Credentials: `taylordash:taylordash`
- Password file managed separately

### 5. MinIO (S3-Compatible Storage)

**Image**: `minio/minio:latest`

**Purpose**: Object storage for files, backups, artifacts

**Environment Variables**:
```yaml
MINIO_ROOT_USER: ${MINIO_ROOT_USER:-taylordash}
MINIO_ROOT_PASSWORD: ${MINIO_ROOT_PASSWORD:-taylordash123}
```

**Command**:
```bash
server /data --console-address ":9001"
```

**Volume Mounts**:
```yaml
volumes:
  - minio_data:/data  # Persistent object storage
```

**Health Check**:
```bash
curl -f http://localhost:9000/minio/health/live
```

**Features**:
- S3-compatible API
- Web console on port 9001
- Bucket policies for access control
- Data persistence across restarts

### 6. VictoriaMetrics (Time Series Database)

**Image**: `victoriametrics/victoria-metrics:latest`

**Purpose**: High-performance metrics storage

**Configuration**:
```bash
command:
  - '--storageDataPath=/victoria-metrics-data'
  - '--httpListenAddr=:8428'
  - '--retentionPeriod=30d'
  - '--maxConcurrentInserts=4'
```

**Volume Mounts**:
```yaml
volumes:
  - victoria_data:/victoria-metrics-data  # Persistent metrics
```

**Health Check**:
```bash
wget --quiet --tries=1 --spider http://0.0.0.0:8428/health
```

**Features**:
- Prometheus-compatible API
- 30-day retention period
- Superior compression and performance
- HTTP API on port 8428

### 7. Prometheus (Metrics Collection)

**Image**: `prom/prometheus:latest`

**Purpose**: Metrics scraping and alerting

**Configuration**: `/infra/prometheus/prometheus.yml`

```yaml
scrape_configs:
  - job_name: 'taylordash-backend'
    static_configs:
      - targets: ['backend:8000']
    metrics_path: '/metrics'
    scrape_interval: 15s
```

**Volume Mounts**:
```yaml
volumes:
  - ./infra/prometheus/prometheus.yml:/etc/prometheus/prometheus.yml:ro
  - prometheus_data:/prometheus
```

**Command**:
```bash
command:
  - '--config.file=/etc/prometheus/prometheus.yml'
  - '--storage.tsdb.path=/prometheus'
  - '--storage.tsdb.retention.time=30d'
  - '--web.enable-lifecycle'
```

**Health Check**:
```bash
wget --quiet --tries=1 --spider http://localhost:9090/-/healthy
```

### 8. Grafana (Visualization)

**Image**: `grafana/grafana:latest`

**Purpose**: Metrics visualization and dashboards

**Environment Variables**:
```yaml
GF_SECURITY_ADMIN_PASSWORD: ${GRAFANA_PASSWORD:-admin}
GF_INSTALL_PLUGINS: grafana-piechart-panel
```

**Volume Mounts**:
```yaml
volumes:
  - grafana_data:/var/lib/grafana
  - ./infra/grafana/provisioning:/etc/grafana/provisioning:ro
```

**Health Check**:
```bash
curl -f http://localhost:3000/api/health
```

**Features**:
- Pre-configured data sources (VictoriaMetrics, Prometheus)
- Dashboard provisioning
- Plugin support
- Persistent configuration

### 9. TimescaleDB (Optional)

**Image**: `timescale/timescaledb:latest-pg15`

**Profile**: `timescale` (disabled by default)

**Purpose**: High-performance time series data for enterprise

**Environment Variables**:
```yaml
POSTGRES_DB: taylordash_ts
POSTGRES_USER: taylordash
POSTGRES_PASSWORD: ${TIMESCALE_PASSWORD:-taylordash}
```

**Activation**:
```bash
docker-compose --profile timescale up -d
```

## Persistent Storage

### Named Volumes

| Volume | Purpose | Backup Priority |
|--------|---------|----------------|
| `postgres_data` | Database files | Critical |
| `mosquitto_data` | MQTT persistence | High |
| `mosquitto_logs` | MQTT logs | Medium |
| `minio_data` | Object storage | High |
| `prometheus_data` | Metrics storage | Medium |
| `grafana_data` | Dashboards/config | Medium |
| `victoria_data` | Time series data | Medium |

### Backup Strategy

```bash
# Database backup
docker exec taylordash-postgres pg_dump -U taylordash taylordash > backup.sql

# Volume backup
docker run --rm -v taylordash_postgres_data:/data -v $(pwd):/backup alpine tar czf /backup/postgres_backup.tar.gz /data

# MinIO backup
mc mirror taylordash/ backup-bucket/
```

## Health Monitoring

### Service Health Checks

All services include comprehensive health checks:

```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/health/ready"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s
```

### Health Check Endpoints

| Service | Endpoint | Check Type |
|---------|----------|------------|
| Backend | `/health/ready` | Database connectivity |
| Backend | `/health/live` | Service liveness |
| Traefik | `/ping` | Proxy health |
| PostgreSQL | `pg_isready` | Database readiness |
| MQTT | Message publish test | Broker connectivity |
| MinIO | `/minio/health/live` | Storage health |
| VictoriaMetrics | `/health` | TSDB health |
| Prometheus | `/-/healthy` | Metrics collection |
| Grafana | `/api/health` | Dashboard service |

### Dependency Management

Services start in proper order with dependency checks:

```yaml
depends_on:
  postgres:
    condition: service_healthy
  mosquitto:
    condition: service_healthy
```

## Environment Configuration

### Environment Variables

**Required Variables**:
```bash
# Security
API_KEY=your-secure-api-key
POSTGRES_PASSWORD=secure-database-password

# Optional with defaults
MINIO_ROOT_USER=taylordash
MINIO_ROOT_PASSWORD=taylordash123
GRAFANA_PASSWORD=admin
TIMESCALE_PASSWORD=taylordash
```

### Configuration Files

```
infra/
├── traefik/
│   └── traefik.yml           # Reverse proxy config
├── mosquitto/
│   ├── mosquitto.conf        # MQTT broker config
│   └── password_file         # MQTT credentials
├── prometheus/
│   └── prometheus.yml        # Metrics collection config
├── grafana/
│   └── provisioning/         # Dashboard provisioning
├── postgres/
│   ├── init.sql             # Database initialization
│   ├── logging_schema.sql   # Logging tables
│   └── user_auth_schema.sql # Authentication tables
└── timescale/
    └── init.sql             # TimescaleDB initialization
```

## Security Configuration

### Network Security
- Services isolated to dedicated network
- Only necessary ports exposed to host
- Internal communication via service names
- No direct database access from external

### Authentication
- MQTT broker requires username/password
- PostgreSQL uses application-specific user
- MinIO requires root credentials
- Grafana admin password configurable

### SSL/TLS
- Traefik handles SSL termination
- Let's Encrypt automatic certificate management
- Internal communication can use TLS
- MQTT supports TLS on port 8883

## Performance Tuning

### Resource Limits

```yaml
# Example resource constraints
deploy:
  resources:
    limits:
      cpus: '0.50'
      memory: 512M
    reservations:
      cpus: '0.25'
      memory: 256M
```

### Connection Pooling
- PostgreSQL: Connection pooling in application
- MQTT: Connection limits configured
- MinIO: S3 connection pooling

### Monitoring Resources
- CPU and memory usage tracked
- Disk I/O monitoring
- Network traffic analysis
- Health check response times

## Scaling Considerations

### Horizontal Scaling Ready
- **Backend**: Stateless, can scale horizontally
- **PostgreSQL**: Read replicas supported
- **MQTT**: Clustering capabilities
- **MinIO**: Distributed deployment support

### Vertical Scaling
- Resource limits easily adjustable
- Memory and CPU can be increased
- Storage volumes expandable

### Load Balancing
- Traefik provides load balancing
- Multiple backend instances supported
- Health check integration
- Automatic service discovery

## Deployment Commands

### Standard Deployment
```bash
# Start all services
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Development Mode
```bash
# Start with development overrides
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# Hot reload backend
docker-compose up -d --build backend
```

### Production Deployment
```bash
# Production environment
export API_KEY="production-api-key"
export POSTGRES_PASSWORD="secure-password"

# Start with production profile
docker-compose --profile production up -d

# Enable TimescaleDB
docker-compose --profile timescale up -d
```

### Maintenance Operations
```bash
# Update services
docker-compose pull
docker-compose up -d

# Restart specific service
docker-compose restart backend

# Scale service
docker-compose up -d --scale backend=3

# View resource usage
docker stats
```

## Troubleshooting

### Common Issues

#### Service Won't Start
```bash
# Check logs
docker-compose logs service-name

# Check health
docker-compose ps

# Restart service
docker-compose restart service-name
```

#### Database Connection Issues
```bash
# Check PostgreSQL logs
docker-compose logs postgres

# Test connection
docker-compose exec backend psql -h postgres -U taylordash -d taylordash

# Reset database
docker-compose down -v
docker-compose up -d
```

#### MQTT Connection Issues
```bash
# Test MQTT
docker-compose exec mosquitto mosquitto_pub -h localhost -t test -m "hello"

# Check authentication
docker-compose exec mosquitto cat /mosquitto/config/password_file
```

### Log Locations
- **Traefik**: Docker logs via `docker-compose logs traefik`
- **Backend**: Application logs in database + Docker logs
- **PostgreSQL**: Docker logs + database logs
- **MQTT**: `/mosquitto/log/` volume + Docker logs
- **MinIO**: Docker logs
- **Prometheus**: Docker logs + `/prometheus` volume
- **Grafana**: Docker logs + `/var/lib/grafana` volume

This infrastructure provides a robust, scalable foundation for the TaylorDash application with comprehensive monitoring, security, and maintenance capabilities.