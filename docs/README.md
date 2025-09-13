# TaylorDash Documentation Hub

## Overview

This documentation provides comprehensive coverage of the TaylorDash system architecture, implementation, and operational procedures. The documentation is organized following the Diátaxis framework for optimal usability by developers, operators, and reviewers.

## System Status

**Production-Ready System:**
- ✅ 8 Docker services running and healthy
- ✅ PostgreSQL with 17 tables and complete schema integrity
- ✅ Authentication system with JWT and comprehensive audit logging
- ✅ MQTT event processing pipeline operational
- ✅ 21 projects in system with complete data integrity
- ✅ Plugin infrastructure ready (registry currently empty)
- ✅ Performance: Sub-second response times, excellent efficiency
- ✅ Security: 100% security score, comprehensive audit trail

## Documentation Structure

### 🏗️ Architecture Documentation (`reference/architecture/`)

#### [System Overview](reference/architecture/system-overview.md)
Complete system architecture with service interactions, high-level components, and scalability considerations.

**Key Topics:**
- Service architecture and interactions
- Network and security configuration
- Performance metrics and scalability
- Extension points and future considerations

#### [Database Schema](reference/architecture/database-schema.md)
Comprehensive documentation of all 17 database tables with relationships, indexing, and data integrity features.

**Key Topics:**
- Complete ERD with table relationships
- Schema organization across functional domains
- Indexing strategy and performance optimization
- Data integrity constraints and validation

#### [MQTT Event Architecture](reference/architecture/mqtt-event-architecture.md)
Event-driven architecture using MQTT for real-time communication, audit trails, and system integration.

**Key Topics:**
- Event sourcing and topic structure
- Dead Letter Queue (DLQ) error handling
- Real-time WebSocket integration
- Event correlation and tracing

#### [Monitoring & Observability](reference/architecture/monitoring-observability.md)
Comprehensive monitoring stack with structured logging, metrics collection, and real-time alerting.

**Key Topics:**
- Structured logging with database integration
- Prometheus metrics and VictoriaMetrics TSDB
- Grafana dashboards and alerting
- Performance monitoring and health checks

### 🔌 API Documentation (`reference/api/`)

#### [API Overview](reference/api/overview.md)
Complete API reference with authentication, error handling, and integration examples.

**Key Topics:**
- RESTful API design and standards
- Authentication methods and security
- Request/response formats and pagination
- Error handling and status codes

#### [Authentication API](reference/api/authentication.md)
Detailed authentication system documentation with session management and RBAC.

**Key Topics:**
- Session-based authentication flow
- Role-based access control (Admin/Viewer)
- User management endpoints
- Security features and audit logging

### 🔐 Security Documentation (`reference/security/`)

#### [Security Overview](reference/security/security-overview.md)
Comprehensive security architecture with defense-in-depth approach and 100% security score.

**Key Topics:**
- Multi-layer security architecture
- Authentication and authorization systems
- Plugin security framework
- Threat detection and incident response

### 🔌 Plugin System (`reference/plugins/`)

#### [Plugin Architecture](reference/plugins/plugin-architecture.md)
Complete plugin system with security validation, runtime monitoring, and development guide.

**Key Topics:**
- Plugin types and manifest structure
- Security framework and static analysis
- Runtime monitoring and violation tracking
- Development guide with best practices

### 🐳 Infrastructure Documentation (`infrastructure/`)

#### [Docker Compose Stack](infrastructure/docker-compose-stack.md)
Complete infrastructure documentation for the 8-service Docker Compose stack.

**Key Topics:**
- Service configurations and dependencies
- Network security and isolation
- Persistent storage and backup strategies
- Deployment and maintenance procedures

## Quick Navigation

### For Developers
- **Getting Started**: Start with [System Overview](reference/architecture/system-overview.md)
- **API Integration**: See [API Overview](reference/api/overview.md)
- **Database Work**: Check [Database Schema](reference/architecture/database-schema.md)
- **Plugin Development**: Review [Plugin Architecture](reference/plugins/plugin-architecture.md)

### For Operations Teams
- **Infrastructure**: Review [Docker Compose Stack](infrastructure/docker-compose-stack.md)
- **Monitoring**: See [Monitoring & Observability](reference/architecture/monitoring-observability.md)
- **Security**: Check [Security Overview](reference/security/security-overview.md)
- **Troubleshooting**: Reference health check procedures in infrastructure docs

### For Security Teams
- **Security Architecture**: Start with [Security Overview](reference/security/security-overview.md)
- **Authentication**: Review [Authentication API](reference/api/authentication.md)
- **Plugin Security**: Check [Plugin Architecture](reference/plugins/plugin-architecture.md)
- **Audit Trails**: See logging documentation in [Monitoring & Observability](reference/architecture/monitoring-observability.md)

### For Project Managers
- **System Status**: Current production metrics in [System Overview](reference/architecture/system-overview.md)
- **Feature Overview**: API capabilities in [API Overview](reference/api/overview.md)
- **Extension Capabilities**: Plugin system in [Plugin Architecture](reference/plugins/plugin-architecture.md)

## System Capabilities Summary

### Core Features
- **Project Management**: Complete CRUD operations with hierarchical structure
- **Real-time Updates**: MQTT-based event system with WebSocket integration
- **User Authentication**: JWT sessions with role-based access control
- **Plugin System**: Secure, sandboxed plugin architecture
- **Audit Logging**: Comprehensive audit trail for all operations

### Technical Highlights
- **Performance**: Sub-second response times across all endpoints
- **Security**: 100% security score with comprehensive protection
- **Reliability**: Automatic error recovery and health monitoring
- **Scalability**: Horizontal scaling ready with container architecture
- **Observability**: Complete monitoring and alerting stack

### Integration Points
- **RESTful API**: Complete OpenAPI 3.1 specification
- **WebSocket Events**: Real-time frontend updates
- **MQTT Events**: System-wide event publishing and consumption
- **Plugin API**: Secure plugin development framework
- **Monitoring API**: Health checks and metrics endpoints

## Documentation Standards

This documentation follows:
- **Diátaxis Framework**: Tutorials, how-tos, reference, and explanation
- **Clear Structure**: Hierarchical organization with cross-references
- **Code Examples**: Working examples for all integrations
- **Visual Diagrams**: Mermaid diagrams for complex systems
- **Practical Focus**: Immediately useful for developers and operators

## Maintenance

This documentation is:
- **Version Controlled**: Integrated with the codebase
- **Living Documentation**: Updated with system changes
- **Comprehensive**: Covers all system aspects
- **Practical**: Focused on real-world usage and maintenance

## Support & Resources

For additional support:
- **System Health**: Check `/health/stack` endpoint for real-time status
- **API Documentation**: Interactive docs at `/docs` (Swagger UI)
- **Metrics**: Grafana dashboards for system monitoring
- **Logs**: Structured logging API at `/api/v1/logs`

This documentation provides the foundation for understanding, maintaining, and extending the TaylorDash system effectively.