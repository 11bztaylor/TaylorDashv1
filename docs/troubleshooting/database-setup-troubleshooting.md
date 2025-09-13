# Database Setup Troubleshooting Guide

Comprehensive guide for resolving PostgreSQL connection, permission, and authentication issues in TaylorDash.

## Database Architecture

TaylorDash uses PostgreSQL with multiple user roles:
- **postgres**: Superuser for administration
- **taylordash**: Main application database user
- **taylordash_app**: Application-specific user for plugin operations

## Common Authentication Issues

### 1. Password Authentication Failures

**Symptoms:**
```
FATAL: password authentication failed for user "taylordash"
psql: FATAL: password authentication failed
Backend fails to connect to database
```

**Root Cause Analysis:**
```bash
# Check environment variable consistency
echo "DATABASE_URL from .env:"
grep DATABASE_URL .env

echo "Docker compose environment:"
docker compose config | grep -A 5 -B 5 POSTGRES

echo "Container environment:"
docker exec taylordashv1-postgres-1 env | grep POSTGRES
```

**Resolution Steps:**

1. **Verify Configuration Consistency:**
```bash
# .env file should match docker-compose.yml
cat .env | grep -E "POSTGRES_PASSWORD|DATABASE_URL"
cat docker-compose.yml | grep -A 3 -B 3 POSTGRES_PASSWORD
```

2. **Reset Database with Correct Credentials:**
```bash
# Stop database and remove data
docker compose stop postgres
docker volume rm taylordashv1_postgres_data

# Restart with fresh configuration
docker compose up -d postgres

# Wait for initialization
timeout 60s bash -c 'until docker exec taylordashv1-postgres-1 pg_isready -U taylordash -d taylordash; do sleep 2; done'
```

3. **Test Authentication:**
```bash
# Test connection
docker exec -it taylordashv1-postgres-1 psql -U taylordash -d taylordash -c "SELECT version();"

# Test from backend container
docker exec taylordashv1-backend-1 python -c "
import asyncpg
import asyncio
async def test():
    conn = await asyncpg.connect('postgresql://taylordash:taylordash_secure_password@postgres:5432/taylordash')
    print('Connection successful')
    await conn.close()
asyncio.run(test())
"
```

### 2. Connection Pool Exhaustion

**Symptoms:**
```
asyncpg.exceptions.TooManyConnectionsError
Connection pool exhausted
```

**Diagnosis:**
```sql
-- Check active connections
SELECT count(*) as active_connections, state 
FROM pg_stat_activity 
WHERE datname = 'taylordash' 
GROUP BY state;

-- Check connection limits
SELECT setting as max_connections 
FROM pg_settings 
WHERE name = 'max_connections';
```

**Resolution:**
```bash
# Restart backend to reset connection pool
docker compose restart backend

# Monitor connection usage
docker exec -it taylordashv1-postgres-1 psql -U taylordash -d taylordash -c "
SELECT client_addr, state, count(*) 
FROM pg_stat_activity 
WHERE datname = 'taylordash' 
GROUP BY client_addr, state;
"
```

## Permission and Ownership Issues

### 1. Plugin Table Permission Errors

**Symptoms:**
```
ERROR: must be owner of table plugins
Permission denied for table plugin_permissions
```

**Diagnosis:**
```sql
-- Check table ownership
SELECT schemaname, tablename, tableowner 
FROM pg_tables 
WHERE tablename LIKE '%plugin%';

-- Check user permissions
SELECT grantee, privilege_type, table_name 
FROM information_schema.table_privileges 
WHERE table_name LIKE '%plugin%' AND grantee IN ('taylordash', 'taylordash_app');
```

**Resolution:**
```sql
-- Fix table ownership
ALTER TABLE plugins OWNER TO taylordash_app;
ALTER TABLE plugin_permissions OWNER TO taylordash_app;
ALTER TABLE plugin_sessions OWNER TO taylordash_app;

-- Grant proper permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO taylordash_app;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO taylordash_app;

-- Verify permissions
SELECT schemaname, tablename, tableowner 
FROM pg_tables 
WHERE tablename LIKE '%plugin%';
```

### 2. Schema Permission Issues

**Symptoms:**
```
ERROR: permission denied for schema logging
Cannot create table in schema
```

**Resolution:**
```sql
-- Create and configure logging schema
CREATE SCHEMA IF NOT EXISTS logging;
ALTER SCHEMA logging OWNER TO taylordash;

-- Grant usage permissions
GRANT USAGE ON SCHEMA logging TO taylordash_app;
GRANT CREATE ON SCHEMA logging TO taylordash_app;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA logging TO taylordash_app;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA logging TO taylordash_app;

-- Set default privileges for future objects
ALTER DEFAULT PRIVILEGES IN SCHEMA logging GRANT ALL ON TABLES TO taylordash_app;
ALTER DEFAULT PRIVILEGES IN SCHEMA logging GRANT ALL ON SEQUENCES TO taylordash_app;
```

## Database Initialization Issues

### 1. Init Script Failures

**Symptoms:**
```
Init script failed to execute
Database not properly initialized
Missing tables or schemas
```

**Diagnosis:**
```bash
# Check init script
cat infra/postgres/init.sql

# Check container logs for init errors
docker compose logs postgres | grep -i "error\|failed\|fatal"

# Verify init script is mounted
docker exec taylordashv1-postgres-1 ls -la /docker-entrypoint-initdb.d/
```

**Resolution:**
```bash
# Fix init script permissions
chmod 644 infra/postgres/init.sql

# Recreate database with init script
docker compose down postgres
docker volume rm taylordashv1_postgres_data
docker compose up -d postgres

# Monitor initialization
docker compose logs -f postgres
```

### 2. Missing Database Objects

**Common Missing Objects:**
```sql
-- Check for required tables
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public' 
ORDER BY table_name;

-- Check for required schemas
SELECT schema_name FROM information_schema.schemata 
WHERE schema_name IN ('public', 'logging');

-- Verify required functions/procedures exist
SELECT routine_name, routine_type 
FROM information_schema.routines 
WHERE routine_schema = 'public';
```

**Create Missing Objects:**
```sql
-- Projects tables
CREATE TABLE IF NOT EXISTS projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(50) DEFAULT 'planning',
    owner_id UUID,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Events mirror table
CREATE TABLE IF NOT EXISTS events_mirror (
    id SERIAL PRIMARY KEY,
    topic VARCHAR(255) NOT NULL,
    payload JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- DLQ events table
CREATE TABLE IF NOT EXISTS dlq_events (
    id SERIAL PRIMARY KEY,
    original_topic VARCHAR(255) NOT NULL,
    failure_reason TEXT NOT NULL,
    payload JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

## Connection Troubleshooting

### 1. Network Connectivity Issues

**Symptoms:**
```
Connection refused to postgres:5432
Name resolution failure
```

**Diagnosis:**
```bash
# Test network connectivity from backend
docker exec taylordashv1-backend-1 nc -zv postgres 5432

# Check Docker network
docker network inspect taylordash | jq '.[] | .Containers'

# Verify service discovery
docker exec taylordashv1-backend-1 nslookup postgres
```

**Resolution:**
```bash
# Restart network stack
docker compose down
docker network prune -f
docker compose up -d

# Verify container networking
docker compose ps
docker network ls | grep taylordash
```

### 2. SSL/TLS Connection Issues

**Symptoms:**
```
SSL connection failed
Certificate verification failed
```

**Configuration:**
```bash
# Check PostgreSQL SSL settings
docker exec -it taylordashv1-postgres-1 psql -U postgres -c "SHOW ssl;"

# Test connection without SSL
docker exec taylordashv1-backend-1 python -c "
import asyncpg
import asyncio
async def test():
    conn = await asyncpg.connect(
        'postgresql://taylordash:taylordash_secure_password@postgres:5432/taylordash?ssl=false'
    )
    print('Connection successful')
    await conn.close()
asyncio.run(test())
"
```

## Performance and Monitoring

### 1. Connection Pool Monitoring

**Monitor Pool Health:**
```python
# Add to backend health check
async def check_db_pool_health():
    pool = await get_db_pool()
    return {
        "size": pool.get_size(),
        "idle": pool.get_idle_size(), 
        "max_size": pool.get_max_size(),
        "min_size": pool.get_min_size()
    }
```

**Optimal Pool Configuration:**
```python
# In database.py
await asyncpg.create_pool(
    database_url,
    min_size=5,      # Minimum connections
    max_size=20,     # Maximum connections  
    max_queries=50000,  # Max queries per connection
    max_inactive_connection_lifetime=300  # 5 minutes
)
```

### 2. Query Performance Monitoring

**Enable Query Logging:**
```sql
-- Enable slow query logging
ALTER SYSTEM SET log_min_duration_statement = 1000;  -- Log queries > 1s
ALTER SYSTEM SET log_statement = 'all';  -- Log all statements
SELECT pg_reload_conf();
```

**Monitor Query Performance:**
```sql
-- Top slow queries
SELECT query, calls, mean_exec_time, total_exec_time
FROM pg_stat_statements 
ORDER BY mean_exec_time DESC 
LIMIT 10;

-- Lock analysis
SELECT waiting.pid AS waiting_pid,
       waiting.query AS waiting_query,
       blocking.pid AS blocking_pid,
       blocking.query AS blocking_query
FROM pg_stat_activity waiting
JOIN pg_stat_activity blocking ON blocking.pid = ANY(pg_blocking_pids(waiting.pid))
WHERE waiting.state = 'active';
```

## Backup and Recovery

### 1. Database Backup

**Create Backup:**
```bash
# Full database backup
docker exec taylordashv1-postgres-1 pg_dump -U taylordash -d taylordash > backup_$(date +%Y%m%d_%H%M%S).sql

# Schema-only backup
docker exec taylordashv1-postgres-1 pg_dump -U taylordash -d taylordash --schema-only > schema_backup.sql

# Data-only backup
docker exec taylordashv1-postgres-1 pg_dump -U taylordash -d taylordash --data-only > data_backup.sql
```

### 2. Database Recovery

**Restore from Backup:**
```bash
# Stop services
docker compose stop backend

# Recreate database
docker compose down postgres
docker volume rm taylordashv1_postgres_data
docker compose up -d postgres

# Wait for startup
sleep 30

# Restore backup
cat backup_20240912_143000.sql | docker exec -i taylordashv1-postgres-1 psql -U taylordash -d taylordash

# Restart services
docker compose up -d backend
```

## Emergency Database Recovery

### Complete Database Reset

```bash
#!/bin/bash
echo "WARNING: This will destroy all database data!"
read -p "Continue? (y/N): " confirm

if [[ $confirm == [yY] ]]; then
    # Stop all services
    docker compose down
    
    # Remove database volume
    docker volume rm taylordashv1_postgres_data
    
    # Start fresh
    docker compose up -d postgres
    
    # Wait for initialization
    timeout 120s bash -c 'until docker exec taylordashv1-postgres-1 pg_isready -U taylordash -d taylordash; do sleep 5; done'
    
    # Start backend
    docker compose up -d backend
    
    echo "Database reset completed"
else
    echo "Reset cancelled"
fi
```

### Database Health Check Script

```bash
#!/bin/bash
# database_health_check.sh

echo "=== TaylorDash Database Health Check ==="

# 1. Connection test
echo "Testing database connection..."
if docker exec taylordashv1-postgres-1 pg_isready -U taylordash -d taylordash; then
    echo "✅ Database connection: OK"
else
    echo "❌ Database connection: FAILED"
    exit 1
fi

# 2. Table existence check
echo "Checking required tables..."
TABLES=("projects" "events_mirror" "dlq_events" "logging.application_logs")
for table in "${TABLES[@]}"; do
    if docker exec taylordashv1-postgres-1 psql -U taylordash -d taylordash -c "\dt $table" &>/dev/null; then
        echo "✅ Table $table: EXISTS"
    else
        echo "❌ Table $table: MISSING"
    fi
done

# 3. Permission check
echo "Checking permissions..."
if docker exec taylordashv1-postgres-1 psql -U taylordash_app -d taylordash -c "SELECT 1 FROM plugins LIMIT 1;" &>/dev/null; then
    echo "✅ Plugin permissions: OK"
else
    echo "⚠️  Plugin permissions: CHECK REQUIRED"
fi

# 4. Connection pool test
echo "Testing connection pool..."
if curl -sf -H "X-API-Key: taylordash-dev-key" http://localhost:8000/health/ready &>/dev/null; then
    echo "✅ Backend database connection: OK"
else
    echo "❌ Backend database connection: FAILED"
fi

echo "=== Health check completed ==="
```