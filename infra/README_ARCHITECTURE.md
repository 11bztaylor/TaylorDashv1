# TaylorDash Infrastructure Architecture

## 🎯 Purpose
Docker Compose-based infrastructure implementing **container orchestration patterns** for single-node deployment with production-grade security, monitoring, and data persistence.

## 🏗️ Infrastructure Architecture & Design

### Core Design Patterns

#### **1. Reverse Proxy Pattern**
- **Implementation**: Traefik as edge proxy with automatic TLS termination
- **Benefits**: Single entry point, SSL/TLS handling, request routing
- **Security**: HSTS enforcement, security headers, rate limiting
- **Service Discovery**: Automatic backend discovery via Docker labels

#### **2. Microservices Pattern**
- **Implementation**: Service decomposition with clear boundaries
- **Communication**: HTTP API + MQTT message bus
- **Benefits**: Independent scaling, technology diversity, fault isolation
- **Service Mesh**: Internal communication through container network

#### **3. Data Persistence Pattern**
- **Implementation**: Docker volumes with persistent storage
- **Strategy**: Separate volumes per service for data isolation
- **Backup**: Volume-based backup and restore procedures
- **Migration**: Schema versioning and data migration support

#### **4. Observability Pattern**
- **Implementation**: Prometheus metrics + Grafana dashboards
- **Monitoring**: Health checks, resource metrics, application metrics
- **Alerting**: Rule-based alerting with notification channels
- **Tracing**: OpenTelemetry integration for distributed tracing

#### **5. Security Defense in Depth**
- **Implementation**: Multiple security layers with different functions
- **Network Security**: Internal network isolation + TLS everywhere
- **Authentication**: OIDC with Keycloak + service-to-service auth
- **Secrets Management**: Environment variables + Docker secrets

### Key Architectural Decisions

#### **Docker Compose over Kubernetes**
- **Rationale**: Simpler single-node deployment + lower resource overhead
- **Trade-offs**: Less orchestration features but easier management
- **Impact**: Faster setup and maintenance for development environments

#### **Traefik over NGINX**
- **Rationale**: Automatic service discovery + modern reverse proxy features
- **Trade-offs**: Less mature but better container integration
- **Impact**: Simplified configuration and dynamic routing

#### **PostgreSQL over NoSQL**
- **Rationale**: ACID compliance + mature ecosystem + JSON support
- **Trade-offs**: Less horizontal scaling but better consistency guarantees
- **Impact**: Reliable data persistence with flexible schema evolution

#### **Mosquitto over RabbitMQ**
- **Rationale**: Lightweight MQTT broker perfect for single-node
- **Trade-offs**: Fewer features but lower resource usage
- **Impact**: Efficient pub/sub messaging with minimal overhead

### Service Architecture

#### **Edge Layer - Traefik**
```yaml
# Configuration Pattern
traefik:
  image: traefik:2.10
  command:
    - --api.dashboard=true
    - --entrypoints.web.address=:80
    - --entrypoints.websecure.address=:443
    - --providers.docker=true
    - --certificatesresolvers.letsencrypt.acme.email=admin@example.com
  labels:
    - "traefik.enable=true"
    - "traefik.http.routers.api.rule=Host(`traefik.local`)"
```

**Responsibilities:**
- TLS termination and certificate management
- Request routing to backend services
- Security headers injection (HSTS, CSP, etc.)
- Load balancing and health checking

**Security Features:**
- Automatic HTTPS redirection
- Security headers middleware
- Rate limiting configuration
- Access logging and monitoring

#### **Application Layer - FastAPI**
```yaml
# Configuration Pattern
backend:
  build: ./backend
  environment:
    - DATABASE_URL=postgresql://user:pass@postgres:5432/db
    - MQTT_BROKER_URL=mqtt://mosquitto:1883
  labels:
    - "traefik.enable=true"
    - "traefik.http.routers.api.rule=PathPrefix(`/api`)"
  depends_on:
    - postgres
    - mosquitto
```

**Responsibilities:**
- API request handling and business logic
- Database connection management
- MQTT event publishing and subscribing
- Authentication and authorization

**Integration Points:**
- Database connection pooling
- MQTT client with reconnection
- OpenTelemetry instrumentation
- Health check endpoints

#### **Data Layer - PostgreSQL**
```yaml
# Configuration Pattern
postgres:
  image: postgres:15
  environment:
    POSTGRES_DB: taylordash
    POSTGRES_USER: taylordash
    POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
  volumes:
    - postgres_data:/var/lib/postgresql/data
    - ./infra/postgres/init.sql:/docker-entrypoint-initdb.d/init.sql
```

**Responsibilities:**
- Primary data storage with ACID guarantees
- Schema management and migrations
- Connection pooling and query optimization
- Backup and restore procedures

**Performance Features:**
- Connection pooling configuration
- Query performance monitoring
- Index optimization
- Automated backups

#### **Message Layer - Mosquitto MQTT**
```yaml
# Configuration Pattern
mosquitto:
  image: eclipse-mosquitto:2.0
  ports:
    - "1883:1883"
    - "9001:9001"
  volumes:
    - ./infra/mosquitto/mosquitto.conf:/mosquitto/config/mosquitto.conf
    - mosquitto_data:/mosquitto/data
    - mosquitto_logs:/mosquitto/log
```

**Responsibilities:**
- Event message brokering
- Topic management and routing
- Client authentication and authorization
- Message persistence and QoS

**Configuration Features:**
- Authentication via password file
- Topic access control lists
- Message retention policies
- WebSocket support for browsers

### Storage Architecture

#### **Volume Management Strategy**
```yaml
volumes:
  postgres_data:
    driver: local
  mosquitto_data:
    driver: local
  mosquitto_logs:
    driver: local
  minio_data:
    driver: local
  prometheus_data:
    driver: local
  grafana_data:
    driver: local
```

**Storage Patterns:**
- **Database Storage**: PostgreSQL data directory persistence
- **Message Storage**: MQTT message and log persistence
- **Object Storage**: MinIO for file and artifact storage
- **Metrics Storage**: Prometheus time-series data
- **Dashboard Storage**: Grafana configuration and dashboards

#### **Backup and Recovery**
```bash
# Backup Strategy
docker-compose exec postgres pg_dump -U taylordash taylordash > backup.sql
docker run --rm -v taylordash_postgres_data:/data -v $(pwd):/backup alpine tar czf /backup/postgres_backup.tar.gz /data

# Recovery Strategy
docker-compose down
docker volume rm taylordash_postgres_data
docker-compose up -d postgres
docker-compose exec postgres psql -U taylordash -d taylordash < backup.sql
```

### Network Architecture

#### **Container Network Topology**
```yaml
networks:
  taylordash:
    name: taylordash
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16
```

**Network Segmentation:**
- **Frontend Network**: React app served via Traefik
- **Backend Network**: API services communication
- **Database Network**: Data layer isolation
- **Message Network**: MQTT broker communication

**Security Features:**
- Internal network isolation
- No direct external access to internal services
- Encrypted inter-service communication
- Network-level access controls

### Monitoring and Observability

#### **Prometheus Metrics Collection**
```yaml
prometheus:
  image: prom/prometheus:latest
  command:
    - '--config.file=/etc/prometheus/prometheus.yml'
    - '--storage.tsdb.path=/prometheus'
    - '--storage.tsdb.retention.time=30d'
  volumes:
    - ./infra/prometheus/prometheus.yml:/etc/prometheus/prometheus.yml
    - prometheus_data:/prometheus
```

**Metrics Sources:**
- Application metrics from FastAPI
- Container metrics from Docker
- System metrics from node_exporter
- Custom business metrics

#### **Grafana Dashboards**
```yaml
grafana:
  image: grafana/grafana:latest
  environment:
    - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD}
    - GF_USERS_ALLOW_SIGN_UP=false
  volumes:
    - grafana_data:/var/lib/grafana
    - ./infra/grafana/dashboards:/etc/grafana/provisioning/dashboards
```

**Dashboard Categories:**
- System overview and health
- Application performance metrics
- Database query performance
- MQTT message throughput
- User activity and errors

### Security Architecture

#### **Authentication and Authorization**
```yaml
keycloak:
  image: quay.io/keycloak/keycloak:22.0
  environment:
    KC_DB: postgres
    KC_DB_URL: jdbc:postgresql://postgres:5432/keycloak
    KC_DB_USERNAME: keycloak
    KC_DB_PASSWORD: ${KEYCLOAK_DB_PASSWORD}
    KEYCLOAK_ADMIN: ${KEYCLOAK_ADMIN}
    KEYCLOAK_ADMIN_PASSWORD: ${KEYCLOAK_ADMIN_PASSWORD}
```

**Security Features:**
- OIDC/OAuth2 authentication
- Role-based access control
- Multi-factor authentication support
- Session management and SSO

#### **TLS and Certificate Management**
```yaml
# Traefik TLS Configuration
- --certificatesresolvers.letsencrypt.acme.tlschallenge=true
- --certificatesresolvers.letsencrypt.acme.email=${ACME_EMAIL}
- --certificatesresolvers.letsencrypt.acme.storage=/letsencrypt/acme.json
```

**Certificate Features:**
- Automatic TLS certificate generation
- Certificate renewal automation
- Wildcard certificate support
- Custom CA integration

### Performance Optimization

#### **Resource Management**
```yaml
# Service Resource Limits
backend:
  deploy:
    resources:
      limits:
        cpus: '1.0'
        memory: 1G
      reservations:
        cpus: '0.5'
        memory: 512M
```

**Optimization Strategies:**
- Container resource limits
- Database connection pooling
- HTTP response caching
- Static asset optimization

#### **Scaling Patterns**
```yaml
# Horizontal Scaling Configuration
backend:
  deploy:
    replicas: 3
    update_config:
      parallelism: 1
      delay: 10s
    restart_policy:
      condition: on-failure
```

**Scaling Considerations:**
- Stateless application design
- Database connection management
- Session state externalization
- Load balancer configuration

## 🔧 Deployment and Operations

### Environment Configuration
```bash
# Environment Variables
POSTGRES_PASSWORD=secure_postgres_password
KEYCLOAK_DB_PASSWORD=secure_keycloak_db_password
KEYCLOAK_ADMIN=admin
KEYCLOAK_ADMIN_PASSWORD=secure_admin_password
GRAFANA_PASSWORD=secure_grafana_password
ACME_EMAIL=admin@yourdomain.com
```

### Service Health Monitoring
```yaml
# Health Check Configuration
backend:
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
    interval: 30s
    timeout: 10s
    retries: 3
    start_period: 40s
```

### Backup and Maintenance
```bash
# Automated Backup Script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
docker-compose exec -T postgres pg_dump -U taylordash taylordash > "backup_${DATE}.sql"
docker run --rm -v taylordash_prometheus_data:/data -v $(pwd):/backup alpine tar czf "/backup/prometheus_${DATE}.tar.gz" /data
```

## 💡 Infrastructure Extension Guidelines

### Adding New Services
1. **Define Service**: Add service to docker-compose.yml
2. **Configure Networking**: Add to taylordash network
3. **Setup Monitoring**: Add Prometheus scrape config
4. **Configure Proxy**: Add Traefik routing labels
5. **Add Health Checks**: Implement health check endpoints

### Scaling Considerations
1. **Stateless Design**: Ensure services are stateless
2. **Database Connections**: Use connection pooling
3. **Session Management**: Externalize session state
4. **File Storage**: Use shared storage for file assets

### Security Hardening
1. **Container Security**: Use minimal base images
2. **Network Isolation**: Implement network segmentation
3. **Secrets Management**: Use Docker secrets or external vaults
4. **Regular Updates**: Automate security updates

## ⚠️ Operational Considerations

### Monitoring and Alerting
- **System Metrics**: CPU, memory, disk, network usage
- **Application Metrics**: Response times, error rates, throughput
- **Business Metrics**: User activity, plugin usage, system health
- **Alert Thresholds**: Set appropriate alerting thresholds

### Backup and Recovery
- **Regular Backups**: Automated daily backups
- **Recovery Testing**: Regular restore procedure testing
- **Point-in-Time Recovery**: Database PITR capability
- **Disaster Recovery**: Off-site backup storage

### Performance Tuning
- **Database Optimization**: Query optimization, indexing
- **Caching Strategy**: Redis or in-memory caching
- **CDN Integration**: Static asset delivery optimization
- **Resource Monitoring**: Continuous performance monitoring

### Security Maintenance
- **Regular Updates**: Keep all components updated
- **Vulnerability Scanning**: Regular security scans
- **Access Auditing**: Regular access review
- **Incident Response**: Security incident procedures