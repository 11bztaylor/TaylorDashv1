# TaylorDash Centralized Logging & Error Handling - Technical Specification

## Overview

This document provides a comprehensive technical specification for the centralized logging and error handling system implemented in TaylorDash. The system provides structured logging, error boundaries, real-time log viewing, and comprehensive error recovery mechanisms.

## Architecture Components

### 1. Backend Logging Infrastructure

#### 1.1 Structured Logger (`logging_utils.py`)
- **StructuredLogger Class**: Main logging interface with database integration
- **Custom Exception Hierarchy**: Categorized errors (TaylorDashError, ValidationError, etc.)
- **JSON Formatter**: Consistent structured log output
- **Database Integration**: Automatic log storage with context preservation

**Key Features:**
- Async logging with database persistence
- Automatic trace ID correlation
- Context-aware error categorization
- Performance monitoring integration

#### 1.2 Logging Middleware (`logging_middleware.py`)
- **LoggingMiddleware**: Request/response logging with timing
- **ErrorHandlingMiddleware**: Global exception handling
- **PerformanceMiddleware**: Slow query detection
- **SecurityMiddleware**: Suspicious activity monitoring

**Middleware Stack Order:**
1. SecurityMiddleware (outermost)
2. PerformanceMiddleware
3. LoggingMiddleware
4. ErrorHandlingMiddleware (innermost)

#### 1.3 Database Schema (`logging_schema.sql`)

**Tables:**
- `logging.application_logs`: Primary log storage with full context
- `logging.log_stream`: Real-time log streaming (short-lived)
- `logging.system_metrics`: Performance metrics storage
- `logging.retention_policies`: Log retention configuration

**Key Indexes:**
- Timestamp-based for chronological queries
- Service/level/category for filtering
- GIN index on JSONB context for flexible searching

### 2. Frontend Error Handling

#### 2.1 Error Utilities (`utils/errorHandling.ts`)
- **ErrorLogger**: Client-side error collection and batching
- **API Helper**: Structured API error handling with retries
- **NotificationManager**: User-facing error notifications
- **Performance Monitoring**: Client-side performance tracking

#### 2.2 Error Boundaries (`components/ErrorBoundary.tsx`)
- **ErrorBoundary**: React component error containment
- **AsyncErrorBoundary**: Promise rejection handling
- **NotificationContainer**: Toast-style error notifications
- **Recovery Mechanisms**: Retry and fallback strategies

### 3. MQTT Error Integration

#### 3.1 Enhanced MQTT Client (`mqtt_client.py`)
- **Retry Logic**: Exponential backoff for connection failures
- **Structured Logging**: Full context logging for MQTT operations
- **DLQ Integration**: Failed message handling
- **Connection Health**: Monitoring and alerting

### 4. Log Viewing Interface

#### 4.1 Settings Page Integration
- **Real-time Log Viewer**: Live log streaming with filters
- **Advanced Filtering**: By level, service, category, search terms
- **Log Detail Modal**: Full context view with JSON formatting
- **Export Capabilities**: Log data export for analysis

#### 4.2 API Endpoints
- `GET /api/v1/logs` - Filtered log retrieval
- `GET /api/v1/logs/{id}` - Individual log details
- `GET /api/v1/logs/stats` - Log statistics and analytics
- `POST /api/v1/logs/test` - Test log generation

## Implementation Details

### Error Classification System

```
Categories:
- API: REST API related errors
- DATABASE: Data persistence errors
- MQTT: Message broker errors
- VALIDATION: Input validation failures
- SYSTEM: Internal system errors
- COMPONENT: Frontend component errors
- NETWORK: Connectivity issues

Severities:
- CRITICAL: System unavailable
- HIGH: Service degraded
- MEDIUM: Feature impacted
- LOW: Minor issues
- INFO: Informational events
```

### Structured Log Format

```json
{
  "timestamp": "2025-01-10T12:00:00.000Z",
  "level": "ERROR",
  "service": "taylordash-backend",
  "category": "DATABASE",
  "severity": "HIGH",
  "message": "Connection pool exhausted",
  "details": "All 20 connections in use",
  "trace_id": "uuid-v4",
  "request_id": "uuid-v4",
  "user_id": "uuid-v4",
  "endpoint": "/api/v1/projects",
  "method": "POST",
  "status_code": 500,
  "duration_ms": 1500,
  "error_code": "DATABASE_ERROR",
  "stack_trace": "...",
  "context": {
    "pool_size": 20,
    "active_connections": 20,
    "query": "SELECT * FROM projects"
  },
  "environment": "production"
}
```

### Recovery Strategies

#### 1. Automatic Retry
- **API Calls**: 3 attempts with exponential backoff
- **MQTT Publishing**: 3 attempts with 2^n second delays
- **Database Operations**: Connection pool retry logic

#### 2. Circuit Breaker Pattern
- **Failure Threshold**: 5 failures trigger circuit open
- **Timeout Period**: 60 seconds before half-open state
- **Health Recovery**: Automatic circuit closure on success

#### 3. Graceful Degradation
- **Database Down**: Use cached data, queue writes
- **MQTT Down**: Store events locally, retry publishing
- **Service Unavailable**: Show user-friendly messages

### Performance Considerations

#### Database Optimization
- **Partitioning**: Planned by date for large log tables
- **Retention Policies**: Automatic cleanup based on service/level
- **Index Strategy**: Optimized for common query patterns
- **Connection Pooling**: Efficient database resource usage

#### Frontend Performance
- **Error Batching**: Collect and send errors in batches
- **Local Storage**: Fallback when API unavailable
- **Component Isolation**: Error boundaries prevent cascade failures
- **Performance Monitoring**: Track slow operations

### Security Measures

#### Data Protection
- **Sensitive Data Sanitization**: Remove passwords, tokens, etc.
- **Access Control**: API key required for log endpoints
- **Audit Trail**: Track log access and modifications

#### Monitoring Integration
- **Suspicious Pattern Detection**: SQL injection, XSS attempts
- **Rate Limiting**: Protection against log flooding
- **Security Event Logging**: 401/403 responses tracked

## Monitoring & Alerting

### Metrics Collection
- **Error Rate**: Errors per minute by category
- **Response Time**: P95/P99 latencies by endpoint
- **Service Health**: Connection status, queue depths
- **User Impact**: Affected user counts, session failures

### Alert Conditions
- **CRITICAL**: >10 errors/minute system-wide
- **HIGH**: >5 database errors/minute
- **MEDIUM**: >20% error rate on any endpoint
- **Circuit Breaker**: State changes to OPEN

### Dashboard Integration
- **Grafana Dashboards**: Real-time metrics visualization
- **Prometheus Rules**: Automated alert generation
- **Log Analytics**: Trend analysis and pattern detection

## Configuration

### Environment Variables
```bash
# Logging Configuration
LOG_LEVEL=INFO
LOG_RETENTION_DAYS=30
LOG_DATABASE_BATCH_SIZE=100

# Error Handling
ERROR_RETRY_MAX_ATTEMPTS=3
ERROR_RETRY_BASE_DELAY=1000
CIRCUIT_BREAKER_THRESHOLD=5

# MQTT Configuration
MQTT_RETRY_MAX_ATTEMPTS=3
MQTT_RETRY_BASE_DELAY=1000
MQTT_DLQ_ENABLED=true

# Performance Monitoring
SLOW_QUERY_THRESHOLD_MS=1000
PERFORMANCE_SAMPLING_RATE=0.1
```

### Retention Policies
```sql
-- Default retention by service and level
taylordash-backend.ERROR: 90 days
taylordash-backend.WARN: 60 days
taylordash-backend.INFO: 30 days
taylordash-backend.DEBUG: 7 days

taylordash-mqtt.ERROR: 90 days
taylordash-mqtt.WARN: 60 days
taylordash-mqtt.INFO: 30 days
taylordash-mqtt.DEBUG: 7 days

taylordash-frontend.ERROR: 60 days
taylordash-frontend.WARN: 30 days
taylordash-frontend.INFO: 14 days
taylordash-frontend.DEBUG: 3 days
```

## Testing Strategy

### Unit Tests
- **Error Handler Coverage**: All error types and categories
- **Logger Functionality**: Format validation, database integration
- **Retry Logic**: Backoff algorithms, max attempts
- **Circuit Breaker**: State transitions, recovery

### Integration Tests
- **End-to-End Logging**: Request to database storage
- **Error Propagation**: Frontend to backend correlation
- **MQTT Integration**: Event publishing, DLQ handling
- **Log Viewer**: Real-time updates, filtering accuracy

### Load Testing
- **High Error Volume**: System behavior under stress
- **Database Performance**: Query optimization validation
- **Memory Usage**: Error buffer management
- **Recovery Time**: System restoration after failures

## Maintenance Procedures

### Daily Operations
- **Log Cleanup**: Automated retention policy execution
- **Health Checks**: Service connectivity validation
- **Error Analysis**: Pattern identification, trending
- **Performance Review**: Slow query identification

### Weekly Reviews
- **Error Pattern Analysis**: Recurring issues identification
- **Performance Trending**: System degradation detection
- **Retention Policy Review**: Storage optimization
- **Alert Tuning**: False positive reduction

### Monthly Maintenance
- **Schema Optimization**: Index analysis, partition review
- **Configuration Updates**: Threshold adjustments
- **Documentation Updates**: Process refinement
- **Disaster Recovery**: Backup validation, restore testing

## Deployment Checklist

### Database Setup
- [ ] Execute `logging_schema.sql`
- [ ] Verify table creation and indexes
- [ ] Test retention policy functions
- [ ] Validate permissions for app user

### Backend Deployment
- [ ] Update environment variables
- [ ] Deploy logging utilities and middleware
- [ ] Test structured logger initialization
- [ ] Verify API endpoint functionality

### Frontend Deployment
- [ ] Deploy error handling utilities
- [ ] Integrate error boundaries
- [ ] Test notification system
- [ ] Validate log viewer interface

### Infrastructure
- [ ] Configure Prometheus alerts
- [ ] Set up Grafana dashboards
- [ ] Test MQTT DLQ functionality
- [ ] Verify log retention automation

## Troubleshooting Guide

### Common Issues

#### High Error Volume
1. Check error patterns in log viewer
2. Identify root cause from context
3. Implement specific error handling
4. Adjust alert thresholds if needed

#### Log Storage Issues
1. Monitor database disk usage
2. Verify retention policy execution
3. Check index performance
4. Consider partition strategy

#### Frontend Error Boundaries
1. Review component error logs
2. Check error boundary coverage
3. Validate fallback UI behavior
4. Test error recovery mechanisms

#### MQTT Connection Issues
1. Check broker connectivity
2. Review retry logic execution
3. Monitor DLQ event volume
4. Validate credential configuration

This comprehensive logging and error handling system provides robust observability and error recovery capabilities for the TaylorDash application, enabling proactive issue detection and resolution.