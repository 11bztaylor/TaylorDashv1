# TaylorDash Error Handling Strategy

## Overview
This document outlines the comprehensive error handling strategy for TaylorDash, including standardized error responses, logging architecture, and recovery mechanisms.

## 1. Error Classification

### Error Categories
- **VALIDATION**: Input validation failures, schema violations
- **AUTHENTICATION**: API key, authorization failures  
- **AUTHORIZATION**: Permission denied, access control
- **DATABASE**: Connection, query, transaction failures
- **MQTT**: Connection, publishing, subscription failures
- **EXTERNAL**: Third-party service failures
- **SYSTEM**: Internal server errors, unexpected failures
- **BUSINESS**: Domain-specific logic errors

### Severity Levels
- **CRITICAL**: System unavailable, data corruption risk
- **HIGH**: Service degraded, user operations failing
- **MEDIUM**: Non-critical features affected
- **LOW**: Minor issues, warnings
- **INFO**: Informational events

## 2. Standardized Error Response Format

### API Error Response Schema
```json
{
  "error": {
    "code": "VALIDATION_FAILED",
    "message": "User-friendly error message",
    "details": "Technical details for debugging",
    "timestamp": "2025-01-10T12:00:00Z",
    "trace_id": "uuid-v4",
    "category": "VALIDATION",
    "severity": "MEDIUM",
    "context": {
      "endpoint": "/api/v1/projects",
      "method": "POST",
      "user_id": "uuid",
      "request_id": "uuid"
    },
    "suggestions": [
      "Check required fields",
      "Validate input format"
    ]
  }
}
```

### Error Codes Registry
- `VALIDATION_FAILED`: Input validation errors
- `RESOURCE_NOT_FOUND`: Requested resource doesn't exist
- `DUPLICATE_RESOURCE`: Resource already exists
- `DATABASE_ERROR`: Database operation failed
- `MQTT_UNAVAILABLE`: MQTT broker connection lost
- `RATE_LIMIT_EXCEEDED`: Too many requests
- `UNAUTHORIZED`: Invalid API key
- `FORBIDDEN`: Insufficient permissions
- `INTERNAL_ERROR`: Unexpected server error

## 3. Logging Architecture

### Structured Log Format (JSON)
```json
{
  "timestamp": "2025-01-10T12:00:00.000Z",
  "level": "ERROR",
  "service": "taylordash-backend",
  "category": "DATABASE",
  "severity": "HIGH",
  "message": "Database connection failed",
  "details": "Connection timeout after 30s",
  "trace_id": "uuid-v4",
  "request_id": "uuid-v4",
  "user_id": "uuid-v4",
  "endpoint": "/api/v1/projects",
  "method": "GET",
  "error_code": "DATABASE_ERROR",
  "context": {
    "database_host": "postgres",
    "connection_pool": "exhausted",
    "retry_count": 3
  },
  "stack_trace": "...",
  "duration_ms": 1500
}
```

### Log Levels
- **ERROR**: Error conditions requiring attention
- **WARN**: Warning conditions, degraded performance
- **INFO**: Informational messages, normal operations
- **DEBUG**: Detailed debugging information

### Service-Specific Context
- **Backend API**: endpoint, method, user_id, request_id
- **MQTT Processor**: topic, qos, broker_host, message_size
- **Database**: query, connection_pool, transaction_id
- **Frontend**: component, user_action, browser_info

## 4. Error Handling Patterns

### Backend (FastAPI)
```python
# Custom exception hierarchy
class TaylorDashError(Exception):
    def __init__(self, code: str, message: str, details: str = None, 
                 category: str = "SYSTEM", severity: str = "MEDIUM"):
        self.code = code
        self.message = message
        self.details = details
        self.category = category
        self.severity = severity

class ValidationError(TaylorDashError):
    def __init__(self, message: str, field: str = None):
        super().__init__("VALIDATION_FAILED", message, f"Field: {field}", 
                        "VALIDATION", "MEDIUM")

# Global error handler middleware
@app.exception_handler(TaylorDashError)
async def taylordash_error_handler(request: Request, exc: TaylorDashError):
    error_response = {
        "error": {
            "code": exc.code,
            "message": exc.message,
            "details": exc.details,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "trace_id": get_trace_id(),
            "category": exc.category,
            "severity": exc.severity,
            "context": {
                "endpoint": str(request.url.path),
                "method": request.method,
                "request_id": get_request_id(request)
            }
        }
    }
    
    # Log the error
    logger.error("API Error", extra={
        "error_code": exc.code,
        "category": exc.category,
        "severity": exc.severity,
        "endpoint": str(request.url.path),
        "method": request.method
    })
    
    return JSONResponse(content=error_response, status_code=400)
```

### Frontend (React)
```typescript
// Error Boundary Component
class ErrorBoundary extends React.Component {
  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    logError({
      category: 'FRONTEND',
      severity: 'HIGH',
      message: error.message,
      stack_trace: error.stack,
      component: errorInfo.componentStack
    });
  }
}

// API Error Handler
const handleApiError = (error: any, context: ApiContext) => {
  const errorData = {
    category: 'API',
    severity: 'MEDIUM',
    endpoint: context.endpoint,
    method: context.method,
    status_code: error.status,
    message: error.message || 'Unknown API error'
  };
  
  logError(errorData);
  showUserNotification(errorData);
};
```

### MQTT Error Handling
```python
# Retry with exponential backoff
async def publish_with_retry(self, topic: str, payload: dict, max_retries: int = 3):
    for attempt in range(max_retries):
        try:
            await self.client.publish(topic, json.dumps(payload))
            return
        except Exception as e:
            if attempt == max_retries - 1:
                await self._send_to_dlq(topic, payload, f"Max retries exceeded: {e}")
                raise
            
            delay = min(2 ** attempt, 30)  # Max 30s delay
            logger.warning(f"MQTT publish failed, retrying in {delay}s", extra={
                "category": "MQTT",
                "topic": topic,
                "attempt": attempt + 1,
                "error": str(e)
            })
            await asyncio.sleep(delay)
```

## 5. Database Error Recovery

### Connection Pool Management
- **Connection Timeout**: 30 seconds
- **Max Retries**: 3 attempts with exponential backoff
- **Pool Size**: 10 connections min, 20 max
- **Health Check**: Every 30 seconds

### Transaction Error Handling
```python
async def safe_database_operation(operation_func, *args, **kwargs):
    max_retries = 3
    for attempt in range(max_retries):
        try:
            async with db_pool.acquire() as conn:
                async with conn.transaction():
                    return await operation_func(conn, *args, **kwargs)
        except asyncpg.PostgresError as e:
            if attempt == max_retries - 1:
                logger.error("Database operation failed after retries", extra={
                    "category": "DATABASE",
                    "severity": "HIGH",
                    "operation": operation_func.__name__,
                    "error_code": e.sqlstate,
                    "error_message": str(e)
                })
                raise DatabaseError("Operation failed", str(e))
            
            delay = 2 ** attempt
            await asyncio.sleep(delay)
```

## 6. Graceful Degradation Patterns

### Service Unavailability Handling
- **Database Down**: Return cached data, queue writes
- **MQTT Down**: Store events locally, retry publishing
- **External APIs Down**: Use fallback data, show warnings

### Circuit Breaker Pattern
```python
class CircuitBreaker:
    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
    
    async def call(self, func, *args, **kwargs):
        if self.state == "OPEN":
            if time.time() - self.last_failure_time > self.timeout:
                self.state = "HALF_OPEN"
            else:
                raise ServiceUnavailableError("Circuit breaker OPEN")
        
        try:
            result = await func(*args, **kwargs)
            if self.state == "HALF_OPEN":
                self.state = "CLOSED"
                self.failure_count = 0
            return result
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()
            
            if self.failure_count >= self.failure_threshold:
                self.state = "OPEN"
            
            raise
```

## 7. Monitoring and Alerting

### Error Rate Metrics
- Errors per minute by category
- Error rate by endpoint  
- P95/P99 error response times
- Circuit breaker state changes

### Alert Conditions
- **CRITICAL**: >10 errors/minute
- **HIGH**: >5 database errors/minute  
- **MEDIUM**: >20% error rate on any endpoint
- **Circuit Breaker**: State changes to OPEN

### Health Check Integration
```python
@app.get("/health/detailed")
async def detailed_health():
    checks = {
        "database": await check_database_health(),
        "mqtt": await check_mqtt_health(),
        "error_rate": await check_error_rate()
    }
    
    overall_health = all(check["status"] == "healthy" for check in checks.values())
    
    return {
        "status": "healthy" if overall_health else "degraded",
        "checks": checks,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
```

## 8. Implementation Checklist

### Backend Implementation
- [ ] Custom exception hierarchy
- [ ] Global error handler middleware  
- [ ] Structured logging configuration
- [ ] Database error recovery
- [ ] MQTT retry mechanisms
- [ ] Circuit breaker implementation
- [ ] Health check enhancements

### Frontend Implementation
- [ ] Error boundary components
- [ ] API error handling utilities
- [ ] User notification system
- [ ] Log aggregation client
- [ ] Error recovery UX patterns

### Infrastructure
- [ ] Log storage schema
- [ ] Log retention policies
- [ ] Error monitoring dashboards
- [ ] Alert rule configuration
- [ ] Log viewing interface

### Testing
- [ ] Error scenario test cases
- [ ] Recovery mechanism tests
- [ ] Load testing with failures
- [ ] Alert system validation

## 9. Operational Runbooks

### Common Error Scenarios
1. **Database Connection Loss**: Check connection pool, restart service
2. **MQTT Broker Down**: Check broker health, process DLQ events
3. **High Error Rate**: Check recent deployments, scale services
4. **Memory Leaks**: Monitor heap usage, restart affected services
5. **Disk Space**: Clean up old logs, extend storage

### Recovery Procedures
1. **Service Restart**: Graceful shutdown, health check validation
2. **Database Recovery**: Connection pool reset, transaction replay
3. **MQTT Recovery**: Reconnect, process queued messages
4. **Log Analysis**: Query error patterns, identify root causes

This strategy ensures comprehensive error handling across all TaylorDash components with proper observability and recovery mechanisms.