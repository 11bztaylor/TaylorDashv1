# Backend Quick Reference

## 🚀 Start Backend

```bash
cd /TaylorProjects/TaylorDashv1/backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or via Docker
docker compose up backend -d
```

## 📍 Key Files

- **`app/main.py`** - FastAPI entry point, health checks, CRUD APIs
- **`app/routers/`** - API endpoint modules
  - `auth.py` - Authentication routes
  - `plugins.py` - Plugin management API
  - `mcp.py` - Model Context Protocol integration
- **`app/database.py`** - PostgreSQL connection pool management
- **`app/mqtt_client.py`** - MQTT event publisher/subscriber
- **`app/security.py`** - API key authentication, security headers
- **`app/models/`** - Database models and schemas
- **`app/services/`** - Business logic services
  - `plugin_security.py` - Plugin validation and security
  - `plugin_installer.py` - Plugin installation logic

## 🔑 Environment Variables

```bash
# Required
DATABASE_URL=postgresql://taylordash_app:password@postgres:5432/taylordash
API_KEY=taylordash-dev-key

# Optional
MQTT_HOST=mosquitto
MQTT_PORT=1883
MQTT_USERNAME=taylordash
MQTT_PASSWORD=taylordash
OTEL_EXPORTER_OTLP_ENDPOINT=http://jaeger:4317
```

## 🛠 API Endpoints

### Core APIs
```bash
GET  /health/live          # Liveness probe
GET  /health/ready         # Readiness probe
GET  /metrics              # Prometheus metrics
GET  /api/v1/health/stack  # Comprehensive health check
```

### Project Management
```bash
GET    /api/v1/projects              # List all projects
GET    /api/v1/projects/{id}         # Get project by ID
POST   /api/v1/projects              # Create new project
PUT    /api/v1/projects/{id}         # Update project
DELETE /api/v1/projects/{id}         # Delete project
GET    /api/v1/projects/{id}/components  # Get project components
GET    /api/v1/components/{id}/tasks     # Get component tasks
```

### Events & Monitoring
```bash
GET  /api/v1/events        # Query event mirror
GET  /api/v1/dlq           # Dead letter queue events
POST /api/v1/events/test   # Test MQTT publishing
GET  /api/v1/logs          # Application logs with filtering
GET  /api/v1/logs/stats    # Log statistics
POST /api/v1/logs/test     # Generate test log entries
```

### Plugin System
```bash
GET    /api/v1/plugins              # List installed plugins
POST   /api/v1/plugins/install     # Install plugin
DELETE /api/v1/plugins/{id}        # Uninstall plugin
GET    /api/v1/plugins/{id}/status # Plugin status
POST   /api/v1/plugins/validate    # Validate plugin security
```

## 🔐 Authentication

All API endpoints require `X-API-Key` header:

```bash
curl -H "X-API-Key: taylordash-dev-key" http://localhost:8000/api/v1/projects
```

## 📊 Database Schema

### Core Tables
```sql
-- Projects
CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(50) DEFAULT 'planning',
    owner_id UUID,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Components (project parts)
CREATE TABLE components (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    type VARCHAR(100),
    status VARCHAR(50) DEFAULT 'pending',
    progress INTEGER DEFAULT 0,
    position JSONB, -- React Flow position
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tasks (component work items)
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    component_id UUID REFERENCES components(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(50) DEFAULT 'todo',
    assignee_id UUID,
    due_date TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Event mirror (MQTT events stored in DB)
CREATE TABLE events_mirror (
    id SERIAL PRIMARY KEY,
    topic VARCHAR(255) NOT NULL,
    payload JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Plugin management
CREATE TABLE plugins (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL UNIQUE,
    version VARCHAR(50) NOT NULL,
    status VARCHAR(50) DEFAULT 'installed',
    metadata JSONB DEFAULT '{}',
    installed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

## 📡 MQTT Integration

### Event Publishing
```python
mqtt_processor = await get_mqtt_processor()
await mqtt_processor.publish_event(
    topic="tracker/events/projects/created",
    kind="project_created",
    payload={
        "project_id": project_id,
        "name": project_name,
        "timestamp": datetime.now().isoformat()
    }
)
```

### Event Topics
```
tracker/events/projects/created    # Project lifecycle
tracker/events/projects/updated
tracker/events/projects/deleted
tracker/events/plugins/installed   # Plugin lifecycle
tracker/events/plugins/uninstalled
tracker/events/test/api           # Testing
```

## 🔍 Debugging & Development

### Development Server
```bash
# Hot reload development
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# With debug logging
uvicorn app.main:app --reload --log-level debug
```

### Database Connection Test
```bash
# Test PostgreSQL connection
python -c "
import asyncio
import asyncpg
async def test():
    conn = await asyncpg.connect('postgresql://taylordash_app:password@localhost:5432/taylordash')
    result = await conn.fetchval('SELECT 1')
    print(f'DB connection: {result}')
    await conn.close()
asyncio.run(test())
"
```

### MQTT Connection Test
```bash
# Test MQTT publishing
mosquitto_pub -h localhost -t "test/topic" -m "hello" -u taylordash -P taylordash

# Test MQTT subscription
mosquitto_sub -h localhost -t "tracker/events/#" -u taylordash -P taylordash
```

## 🤖 For AI Agents

### Quick Context
FastAPI backend with PostgreSQL database, MQTT messaging, plugin system, and comprehensive observability. Handles authentication, project management, and event-driven architecture.

### Your Tools
- **Command**: `uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`
- **File**: `/TaylorProjects/TaylorDashv1/backend/app/main.py`
- **Pattern**: Add new routes using FastAPI decorators and dependency injection
- **Auth**: Always use `api_key: str = Depends(verify_api_key)` parameter

### Common Pitfalls
- ⚠️ Missing API key authentication in new endpoints
- ⚠️ Not handling database connection pool properly (use `await get_db_pool()`)
- ⚠️ Forgetting to convert UUIDs to strings in API responses
- ⚠️ Not publishing MQTT events for state changes
- ⚠️ Missing error handling and proper HTTP status codes

### Success Criteria
- ✅ `/health/ready` returns 200 with database healthy
- ✅ All endpoints require and validate API key
- ✅ Database operations use connection pool correctly
- ✅ MQTT events published for state changes
- ✅ Proper error handling with meaningful HTTP status codes
- ✅ OpenAPI documentation generated at `/docs`

## 📚 Dependencies

### Key Python Packages
```
fastapi         # Web framework
uvicorn        # ASGI server
asyncpg        # PostgreSQL driver
pydantic       # Data validation
prometheus-client  # Metrics
paho-mqtt      # MQTT client
```

### Development Tools
```bash
# Install dependencies
pip install -r requirements.txt

# Run tests
pytest

# Code formatting
black .
isort .

# Linting
flake8
```