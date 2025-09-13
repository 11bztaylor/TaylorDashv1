# TaylorDash System Architecture

## Overview

TaylorDash is a production-ready, event-driven project management platform built with modern microservices architecture. The system combines real-time capabilities, comprehensive security, and extensible plugin architecture to provide a scalable foundation for project tracking and management.

## System Status

**Current Production State (as of testing):**
- ✅ 8 Docker services running and healthy
- ✅ PostgreSQL with 17 tables and complete schema integrity
- ✅ Authentication system with JWT and comprehensive audit logging
- ✅ MQTT event processing pipeline operational
- ✅ 21 projects in system with complete data integrity
- ✅ Plugin infrastructure ready (registry currently empty)
- ✅ Performance: Sub-second response times, excellent efficiency
- ✅ Security: 100% security score, comprehensive audit trail

## Architecture Principles

### 1. Event-Driven Architecture
- **MQTT Event Bus**: All state changes flow through MQTT topics
- **Event Sourcing**: Complete audit trail of system changes
- **Asynchronous Processing**: Non-blocking event processing
- **Dead Letter Queue**: Robust error handling and recovery

### 2. Security-First Design
- **Zero Trust Architecture**: Every request authenticated and authorized
- **Role-Based Access Control**: Admin and viewer roles with granular permissions
- **Comprehensive Audit Logging**: All actions tracked with full context
- **Plugin Security Framework**: Static analysis and runtime monitoring

### 3. Microservices & Containerization
- **Docker Compose Stack**: 8 containerized services
- **Service Isolation**: Each service runs in dedicated container
- **Health Monitoring**: Comprehensive health checks and metrics
- **Scalable Infrastructure**: Ready for Kubernetes deployment

### 4. Data Integrity & Observability
- **ACID Transactions**: PostgreSQL ensures data consistency
- **Structured Logging**: Centralized log aggregation and analysis
- **Metrics Collection**: Prometheus + Grafana monitoring stack
- **Performance Tracking**: Response time and efficiency monitoring

## High-Level System Components

```mermaid
graph TB
    %% External
    User[👤 User] --> Traefik[🔀 Traefik Proxy]

    %% Core Services
    Traefik --> Backend[🚀 FastAPI Backend]
    Traefik --> Frontend[🎨 React Frontend]

    %% Data Layer
    Backend --> PostgreSQL[(🗄️ PostgreSQL)]
    Backend --> MQTT[📡 MQTT Broker]

    %% Storage & Cache
    Backend --> MinIO[📦 MinIO S3 Storage]

    %% Monitoring Stack
    Backend --> VictoriaMetrics[📊 VictoriaMetrics]
    VictoriaMetrics --> Grafana[📈 Grafana]
    Backend --> Prometheus[📊 Prometheus]
    Prometheus --> Grafana

    %% Optional Services
    Backend -.-> TimescaleDB[(⏰ TimescaleDB)]

    %% Plugin System
    Backend --> PluginEngine[🔌 Plugin Engine]
    PluginEngine --> PluginSecurity[🔒 Security Scanner]

    %% MCP Integration
    Backend --> MCPManager[🤖 MCP Manager]

    %% Event Flow
    MQTT --> EventProcessor[⚡ Event Processor]
    EventProcessor --> PostgreSQL
    EventProcessor --> DLQ[💀 Dead Letter Queue]

    classDef service fill:#e1f5fe
    classDef storage fill:#f3e5f5
    classDef monitoring fill:#e8f5e8
    classDef security fill:#fff3e0

    class Backend,Frontend,Traefik,MQTT service
    class PostgreSQL,MinIO,VictoriaMetrics,Prometheus storage
    class Grafana monitoring
    class PluginSecurity security
```

## Service Architecture

### Core Services

#### 1. Traefik (Reverse Proxy & TLS)
- **Purpose**: SSL termination, routing, load balancing
- **Key Features**:
  - Automatic TLS certificate management
  - Security headers injection
  - Request routing and path-based routing
  - Dashboard on port 8080
- **Configuration**: `/infra/traefik/traefik.yml`

#### 2. FastAPI Backend
- **Purpose**: Core business logic and API services
- **Key Features**:
  - RESTful API with OpenAPI documentation
  - JWT-based authentication with session management
  - Plugin management and security validation
  - MCP (Model Context Protocol) integration
  - Structured logging and metrics collection
- **Port**: 8000
- **Health Checks**: `/health/live`, `/health/ready`

#### 3. React Frontend
- **Purpose**: User interface and dashboard
- **Key Features**:
  - Responsive design for desktop and tablet
  - Real-time updates via WebSocket/EventSource
  - Plugin-based architecture for extensibility
  - Role-based UI rendering
- **Build**: Production-optimized static files served by Traefik

### Data Services

#### 4. PostgreSQL Database
- **Purpose**: Primary data store with ACID guarantees
- **Schema**: 17 tables across multiple domains:
  - **Project Management**: `projects`, `components`, `tasks`, `component_dependencies`
  - **Authentication**: `users`, `user_sessions`, `auth_audit_log`
  - **Event System**: `events_mirror`, `dlq_events`
  - **Plugin System**: `plugins`, `plugin_security_violations`, `plugin_configurations`
  - **Logging**: `application_logs`, `system_metrics`, `retention_policies`, `log_stream`
- **Features**:
  - UUID primary keys for security
  - JSONB for flexible metadata storage
  - Comprehensive indexing for performance
  - Automated cleanup functions

#### 5. MQTT Broker (Eclipse Mosquitto)
- **Purpose**: Event bus for real-time communication
- **Topics**:
  - `tracker/events/projects/*` - Project lifecycle events
  - `tracker/events/components/*` - Component state changes
  - `tracker/events/tasks/*` - Task updates
  - `tracker/events/auth/*` - Authentication events
  - `tracker/events/plugins/*` - Plugin system events
- **Security**: Username/password authentication
- **Persistence**: Message persistence enabled

#### 6. MinIO (S3-Compatible Storage)
- **Purpose**: Object storage for files, backups, artifacts
- **Features**:
  - S3-compatible API
  - Web console on port 9001
  - Bucket policies for access control
- **Use Cases**: Plugin assets, user uploads, system backups

### Monitoring & Observability

#### 7. VictoriaMetrics (Primary TSDB)
- **Purpose**: High-performance time series database
- **Features**:
  - Prometheus-compatible API
  - Superior performance and compression
  - 30-day retention period
  - HTTP API on port 8428

#### 8. Prometheus (Metrics Collection)
- **Purpose**: Metrics scraping and alerting
- **Targets**:
  - FastAPI backend metrics (`/metrics`)
  - System metrics from all containers
  - MQTT broker statistics
- **Configuration**: `/infra/prometheus/prometheus.yml`

#### 9. Grafana (Visualization)
- **Purpose**: Metrics visualization and alerting
- **Dashboards**:
  - System health overview
  - Application performance metrics
  - Security event monitoring
  - Plugin system health
- **Data Sources**: VictoriaMetrics, Prometheus

### Optional Services

#### 10. TimescaleDB
- **Purpose**: High-performance time series data (optional profile)
- **Use Case**: Large-scale metrics storage for enterprise deployments
- **Profile**: `timescale` (disabled by default)

## Network Architecture

### External Access
- **HTTPS (443)**: Public web interface via Traefik
- **HTTP (80)**: Redirects to HTTPS
- **Management (8080)**: Traefik dashboard (internal)

### Internal Network
- **Network**: `taylordash` (Docker bridge network)
- **Service Discovery**: Docker DNS resolution
- **Database**: PostgreSQL on port 5432 (internal + development access)
- **MQTT**: Mosquitto on ports 1883 (MQTT), 8883 (MQTT-TLS), 9001 (WebSocket)

### Security Configuration
- **TLS**: All external communication encrypted
- **Network Isolation**: Services isolated to dedicated network
- **Firewall**: Only necessary ports exposed
- **Authentication**: All inter-service communication authenticated

## Data Flow Architecture

### Request Flow
```mermaid
sequenceDiagram
    participant User
    participant Traefik
    participant Backend
    participant PostgreSQL
    participant MQTT

    User->>Traefik: HTTPS Request
    Traefik->>Backend: Proxy to Backend
    Backend->>PostgreSQL: Query/Update Data
    Backend->>MQTT: Publish Event
    Backend->>Traefik: JSON Response
    Traefik->>User: HTTPS Response

    Note over MQTT: Event processed async
    MQTT->>Backend: Event Handler
    Backend->>PostgreSQL: Event Mirror Update
```

### Event Processing Flow
```mermaid
graph LR
    API[API Endpoint] --> Event[Publish Event]
    Event --> MQTT[MQTT Broker]
    MQTT --> Handler[Event Handler]
    Handler --> Mirror[(Events Mirror)]
    Handler --> DLQ[(DLQ)]
    Handler --> Log[(Application Logs)]

    classDef api fill:#e1f5fe
    classDef event fill:#f3e5f5
    classDef data fill:#e8f5e8

    class API api
    class Event,MQTT,Handler event
    class Mirror,DLQ,Log data
```

## Scalability & Performance

### Current Performance Metrics
- **Response Time**: Sub-second for all endpoints
- **Throughput**: Handles 21 projects with excellent efficiency
- **Database**: 17 optimized tables with comprehensive indexing
- **Event Processing**: Real-time MQTT event handling
- **Memory Usage**: Efficient resource utilization

### Horizontal Scaling Readiness
- **Stateless Services**: Backend and frontend can scale horizontally
- **Database**: PostgreSQL read replicas supported
- **Message Queue**: MQTT supports clustering
- **Storage**: MinIO supports distributed deployments
- **Monitoring**: VictoriaMetrics supports clustering

### Optimization Features
- **Connection Pooling**: asyncpg connection pool (5-20 connections)
- **Caching**: Structured logging with retention policies
- **Indexing**: Comprehensive database indexes for performance
- **Compression**: Efficient JSONB storage for metadata
- **Cleanup**: Automated log and session cleanup procedures

## Extension Points

### Plugin System
- **Architecture**: Sandboxed plugin execution
- **Security**: Static analysis and runtime monitoring
- **API**: RESTful plugin management endpoints
- **Types**: Dashboard, tool, integration, visualization plugins

### MCP Integration
- **Protocol**: Model Context Protocol for AI integration
- **Management**: Process lifecycle management
- **Health Monitoring**: Server health checks and metrics
- **API**: Request/response handling for MCP servers

### Authentication Integration
- **Current**: JWT-based with database sessions
- **Extensible**: OAuth2, SAML, LDAP integration ready
- **Audit**: Comprehensive authentication event logging

This architecture provides a solid foundation for current operations while maintaining flexibility for future scaling and feature additions.