# Logging System Troubleshooting Guide

Comprehensive guide for diagnosing and maintaining TaylorDash's structured logging system.

## Architecture Overview

TaylorDash uses a multi-tier logging system:
- **Console Output**: JSON structured logs via StructuredFormatter
- **Database Storage**: PostgreSQL logging.application_logs table  
- **Log Aggregation**: Centralized via logging_utils.py
- **API Access**: REST endpoints for log querying

## Common Logging Issues

### 1. JSON Serialization Failures

**Symptoms:**
```
TypeError: Object of type 'dict' is not JSON serializable
TypeError: can only concatenate str (not "dict") to str
```

**Diagnosis:**
```bash
# Check for serialization errors
docker compose logs backend | grep -i "json\|serialize\|typeerror"

# Test logging endpoint
curl -X POST -H "X-API-Key: taylordash-dev-key" http://localhost:8000/api/v1/logs/test
```

**Resolution:**
```python
# Ensure proper context handling in logging calls
context = context or {}
if isinstance(context, dict):
    context_str = json.dumps(context, default=str)
else:
    context_str = str(context)
```

### 2. Database Logging Connection Issues

**Symptoms:**
```
Failed to store log in database
Connection to database lost during logging
```

**Diagnosis:**
```bash
# Verify logging table exists
docker exec -it taylordashv1-postgres-1 psql -U taylordash -d taylordash -c "
SELECT schemaname, tablename FROM pg_tables WHERE tablename = 'application_logs';"

# Check table structure
docker exec -it taylordashv1-postgres-1 psql -U taylordash -d taylordash -c "\d logging.application_logs"
```

**Resolution:**
```sql
-- Create logging schema if missing
CREATE SCHEMA IF NOT EXISTS logging;

-- Create application_logs table
CREATE TABLE IF NOT EXISTS logging.application_logs (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    level VARCHAR(10) NOT NULL,
    service VARCHAR(50),
    category VARCHAR(50),
    severity VARCHAR(10),
    message TEXT NOT NULL,
    details TEXT,
    trace_id VARCHAR(32),
    request_id VARCHAR(36),
    user_id VARCHAR(36),
    endpoint VARCHAR(255),
    method VARCHAR(10),
    status_code INTEGER,
    duration_ms INTEGER,
    error_code VARCHAR(50),
    stack_trace TEXT,
    context JSONB,
    environment VARCHAR(20) DEFAULT 'production',
    version VARCHAR(20),
    host_name VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_logs_timestamp ON logging.application_logs(timestamp);
CREATE INDEX IF NOT EXISTS idx_logs_level ON logging.application_logs(level);
CREATE INDEX IF NOT EXISTS idx_logs_service_category ON logging.application_logs(service, category);
CREATE INDEX IF NOT EXISTS idx_logs_trace_id ON logging.application_logs(trace_id);
```

### 3. Log Level Configuration Issues

**Symptoms:**
```
Debug logs not appearing
Too much verbose output
Incorrect log filtering
```

**Diagnosis:**
```bash
# Check current log level
docker exec taylordashv1-backend-1 python -c "
import logging
logger = logging.getLogger('app.main')
print(f'Logger level: {logger.level}')
print(f'Effective level: {logger.getEffectiveLevel()}')
"

# Test different log levels
curl -X POST -H "X-API-Key: taylordash-dev-key" http://localhost:8000/api/v1/logs/test
```

**Configuration:**
```python
# In logging_utils.py or main.py
logging.basicConfig(level=logging.INFO)  # Adjust as needed

# For development
logging.basicConfig(level=logging.DEBUG)

# For production  
logging.basicConfig(level=logging.WARNING)
```

## Log Analysis Techniques

### Query Patterns
```bash
# Recent error logs
curl -H "X-API-Key: taylordash-dev-key" "http://localhost:8000/api/v1/logs?level=ERROR&limit=20"

# Specific service logs
curl -H "X-API-Key: taylordash-dev-key" "http://localhost:8000/api/v1/logs?service=taylordash-backend&category=MQTT"

# Search logs by content
curl -H "X-API-Key: taylordash-dev-key" "http://localhost:8000/api/v1/logs?search=authentication"

# Log statistics
curl -H "X-API-Key: taylordash-dev-key" "http://localhost:8000/api/v1/logs/stats?hours=24"
```

### Database Queries
```sql
-- Top error categories
SELECT category, COUNT(*) as error_count 
FROM logging.application_logs 
WHERE level = 'ERROR' AND timestamp > NOW() - INTERVAL '24 hours'
GROUP BY category 
ORDER BY error_count DESC;

-- Request performance analysis
SELECT endpoint, AVG(duration_ms) as avg_duration, COUNT(*) as request_count
FROM logging.application_logs 
WHERE duration_ms IS NOT NULL AND timestamp > NOW() - INTERVAL '1 hour'
GROUP BY endpoint
ORDER BY avg_duration DESC;

-- Error trends by hour
SELECT 
    DATE_TRUNC('hour', timestamp) as hour,
    COUNT(*) FILTER (WHERE level = 'ERROR') as error_count,
    COUNT(*) as total_count
FROM logging.application_logs 
WHERE timestamp > NOW() - INTERVAL '24 hours'
GROUP BY hour
ORDER BY hour;
```

## Structured Logging Best Practices

### Proper Context Usage
```python
# Good: Structured context
await logger.info(
    "User authentication successful",
    category="AUTHENTICATION",
    severity="INFO", 
    context={
        "user_id": user_id,
        "endpoint": request.url.path,
        "duration_ms": duration
    }
)

# Bad: Unstructured context
logger.info(f"User {user_id} authenticated via {endpoint}")
```

### Error Handling
```python
try:
    # Operation that might fail
    result = await risky_operation()
except Exception as e:
    await logger.error(
        "Operation failed",
        exc=e,
        category="OPERATION",
        severity="HIGH",
        context={
            "operation": "risky_operation",
            "parameters": sanitize_sensitive_data(params)
        }
    )
    raise
```

### Sensitive Data Handling
```python
# Use sanitization for sensitive data
from logging_utils import sanitize_sensitive_data

context = {
    "user_credentials": {"username": "john", "password": "secret"},
    "api_key": "sensitive_key"
}

sanitized = sanitize_sensitive_data(context)
# Result: {"user_credentials": {"username": "john", "password": "[REDACTED]"}, "api_key": "[REDACTED]"}
```

## Log Monitoring and Alerting

### Critical Error Detection
```bash
# Monitor for critical errors
docker compose logs -f backend | grep -E "CRITICAL|ERROR.*HIGH" --line-buffered

# Database connection monitoring
docker compose logs -f backend | grep -i "database.*error\|connection.*failed" --line-buffered
```

### Performance Monitoring
```sql
-- Slow requests (>1000ms)
SELECT timestamp, endpoint, method, duration_ms, status_code
FROM logging.application_logs 
WHERE duration_ms > 1000 AND timestamp > NOW() - INTERVAL '1 hour'
ORDER BY duration_ms DESC;

-- Error rate by endpoint
SELECT 
    endpoint,
    COUNT(*) FILTER (WHERE status_code >= 400) as error_count,
    COUNT(*) as total_count,
    ROUND(100.0 * COUNT(*) FILTER (WHERE status_code >= 400) / COUNT(*), 2) as error_rate
FROM logging.application_logs 
WHERE endpoint IS NOT NULL AND timestamp > NOW() - INTERVAL '1 hour'
GROUP BY endpoint
HAVING COUNT(*) > 10
ORDER BY error_rate DESC;
```

## Log Retention and Cleanup

### Automatic Cleanup
```sql
-- Clean up old logs (older than 30 days)
DELETE FROM logging.application_logs 
WHERE timestamp < NOW() - INTERVAL '30 days';

-- Archive old logs before deletion
CREATE TABLE logging.application_logs_archive AS 
SELECT * FROM logging.application_logs 
WHERE timestamp < NOW() - INTERVAL '30 days';
```

### Partition Management
```sql
-- Create monthly partitions for better performance
CREATE TABLE logging.application_logs_202409 
PARTITION OF logging.application_logs 
FOR VALUES FROM ('2024-09-01') TO ('2024-10-01');
```

## Debugging Logging Issues

### Enable Debug Logging
```bash
# Temporarily enable debug logging
docker exec taylordashv1-backend-1 python -c "
import logging
logging.getLogger('app').setLevel(logging.DEBUG)
logging.getLogger('app.logging_utils').setLevel(logging.DEBUG)
"

# Monitor debug output
docker compose logs -f backend | grep DEBUG
```

### Test Logging Components
```python
# Test structured logger directly
from app.logging_utils import get_logger
logger = get_logger()

# Test different log types
await logger.info("Test info message", category="TEST")
await logger.warn("Test warning", category="TEST", severity="MEDIUM")  
await logger.error("Test error", category="TEST", exc=Exception("Test exception"))
```

### Validate Log Storage
```sql
-- Check recent log entries
SELECT timestamp, level, category, message, context 
FROM logging.application_logs 
ORDER BY timestamp DESC 
LIMIT 10;

-- Verify log structure
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_schema = 'logging' AND table_name = 'application_logs'
ORDER BY ordinal_position;
```

## Emergency Log Recovery

### When Logging Completely Fails
```bash
# 1. Fall back to container logs
docker compose logs --tail=1000 backend > emergency_logs.txt

# 2. Check filesystem for log files
docker exec taylordashv1-backend-1 find /app -name "*.log" -type f

# 3. Restart logging subsystem
docker compose restart backend

# 4. Verify logging recovery
curl -X POST -H "X-API-Key: taylordash-dev-key" http://localhost:8000/api/v1/logs/test
```

### Logging Performance Issues
```bash
# Monitor logging performance
docker exec taylordashv1-postgres-1 psql -U taylordash -d taylordash -c "
SELECT schemaname, tablename, n_tup_ins, n_tup_upd, n_tup_del
FROM pg_stat_user_tables 
WHERE tablename = 'application_logs';
"

# Check for blocking queries
docker exec taylordashv1-postgres-1 psql -U taylordash -d taylordash -c "
SELECT query, state, wait_event_type, wait_event 
FROM pg_stat_activity 
WHERE query LIKE '%application_logs%';
"
```