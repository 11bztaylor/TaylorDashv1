# 🗄️ TaylorDash Database Layer

PostgreSQL database integration with asyncpg for the TaylorDash backend. Includes schema management, migrations, and query patterns.

## 📁 Current Files

- **`plugin_schema.sql`** - Plugin management database schema
- **Database migrations** - Version-controlled schema updates
- **Connection pooling** - Async PostgreSQL connection management

## 💻 Code Examples

### Common Patterns

#### Database Connection Pattern
```python
# Using the database connection in a router
from app.database import get_db_connection
import asyncpg

async def get_projects():
    """Get all projects from database"""
    async with get_db_connection() as conn:
        rows = await conn.fetch("""
            SELECT id, name, description, status, created_at, updated_at
            FROM projects
            ORDER BY created_at DESC
        """)
        return [dict(row) for row in rows]

# Alternative: using connection pool directly
from app.database import get_db_pool

async def get_project_by_id(project_id: str):
    """Get specific project by ID"""
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow("""
            SELECT * FROM projects WHERE id = $1
        """, project_id)

        if row:
            return dict(row)
        return None
```

#### Transaction Pattern
```python
async def create_project_with_tasks(project_data: dict, tasks: list):
    """Create project and associated tasks in a transaction"""
    async with get_db_connection() as conn:
        async with conn.transaction():
            # Insert project
            project_id = await conn.fetchval("""
                INSERT INTO projects (id, name, description, status)
                VALUES ($1, $2, $3, $4)
                RETURNING id
            """, project_data['id'], project_data['name'],
                project_data['description'], 'active')

            # Insert associated tasks
            for task in tasks:
                await conn.execute("""
                    INSERT INTO tasks (id, project_id, name, description, status)
                    VALUES ($1, $2, $3, $4, $5)
                """, task['id'], project_id, task['name'],
                    task['description'], 'pending')

            # Update project metadata
            await conn.execute("""
                UPDATE projects
                SET task_count = $2, updated_at = NOW()
                WHERE id = $1
            """, project_id, len(tasks))

            return project_id
```

#### JSONB Operations
```python
async def update_plugin_config(plugin_id: str, config_updates: dict):
    """Update plugin configuration using JSONB operations"""
    async with get_db_connection() as conn:
        # Update specific keys in JSONB config
        await conn.execute("""
            UPDATE plugins
            SET config = config || $2::jsonb,
                updated_at = NOW()
            WHERE id = $1
        """, plugin_id, config_updates)

        # Query with JSONB operations
        result = await conn.fetchrow("""
            SELECT
                id,
                name,
                config->>'enabled' as enabled,
                config->'settings'->>'theme' as theme,
                jsonb_array_length(permissions) as permission_count
            FROM plugins
            WHERE id = $1
        """, plugin_id)

        return dict(result) if result else None

async def search_plugins_by_config(search_criteria: dict):
    """Search plugins using JSONB operators"""
    async with get_db_connection() as conn:
        rows = await conn.fetch("""
            SELECT id, name, config
            FROM plugins
            WHERE config @> $1::jsonb
            AND config ? 'enabled'
            AND (config->>'enabled')::boolean = true
        """, search_criteria)

        return [dict(row) for row in rows]
```

### How to Extend

#### 1. Create New Migration
```sql
-- migrations/003_add_user_table.sql
CREATE TABLE IF NOT EXISTS users (
    id VARCHAR(255) PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'viewer',
    preferences JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_login TIMESTAMP WITH TIME ZONE
);

-- Add indexes for performance
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);
CREATE INDEX IF NOT EXISTS idx_users_created_at ON users(created_at);

-- Add constraints
ALTER TABLE users ADD CONSTRAINT check_role
    CHECK (role IN ('admin', 'maintainer', 'viewer'));
```

#### 2. Database Model Pattern
```python
# models/plugin.py
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any, List
import json

@dataclass
class Plugin:
    id: str
    name: str
    version: str
    description: Optional[str]
    author: str
    type: str
    repository_url: str
    install_path: str
    manifest: Dict[str, Any]
    permissions: List[str]
    config: Dict[str, Any]
    status: str
    installed_at: datetime
    last_updated: Optional[datetime]
    installation_id: Optional[str]
    security_violations: int
    last_violation: Optional[datetime]
    security_score: int
    created_at: datetime
    updated_at: datetime

    @classmethod
    async def find_by_id(cls, plugin_id: str) -> Optional['Plugin']:
        """Find plugin by ID"""
        async with get_db_connection() as conn:
            row = await conn.fetchrow("""
                SELECT * FROM plugins WHERE id = $1
            """, plugin_id)

            if row:
                return cls.from_db_row(row)
            return None

    @classmethod
    async def find_all(cls, status: Optional[str] = None) -> List['Plugin']:
        """Find all plugins, optionally filtered by status"""
        async with get_db_connection() as conn:
            if status:
                rows = await conn.fetch("""
                    SELECT * FROM plugins
                    WHERE status = $1
                    ORDER BY created_at DESC
                """, status)
            else:
                rows = await conn.fetch("""
                    SELECT * FROM plugins
                    ORDER BY created_at DESC
                """)

            return [cls.from_db_row(row) for row in rows]

    async def save(self) -> None:
        """Save plugin to database"""
        async with get_db_connection() as conn:
            await conn.execute("""
                INSERT INTO plugins (
                    id, name, version, description, author, type, kind,
                    repository_url, install_path, manifest, permissions, config,
                    status, installed_at, last_updated, installation_id,
                    security_violations, last_violation, security_score,
                    created_at, updated_at
                ) VALUES (
                    $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12,
                    $13, $14, $15, $16, $17, $18, $19, $20, $21
                )
                ON CONFLICT (id) DO UPDATE SET
                    name = EXCLUDED.name,
                    version = EXCLUDED.version,
                    description = EXCLUDED.description,
                    status = EXCLUDED.status,
                    config = EXCLUDED.config,
                    security_score = EXCLUDED.security_score,
                    updated_at = NOW()
            """,
                self.id, self.name, self.version, self.description,
                self.author, self.type, self.type,  # kind = type for compatibility
                self.repository_url, self.install_path,
                json.dumps(self.manifest), json.dumps(self.permissions),
                json.dumps(self.config), self.status, self.installed_at,
                self.last_updated, self.installation_id,
                self.security_violations, self.last_violation,
                self.security_score, self.created_at, self.updated_at
            )

    @classmethod
    def from_db_row(cls, row: asyncpg.Record) -> 'Plugin':
        """Create Plugin instance from database row"""
        return cls(
            id=row['id'],
            name=row['name'],
            version=row['version'],
            description=row['description'],
            author=row['author'],
            type=row['type'],
            repository_url=row['repository_url'],
            install_path=row['install_path'],
            manifest=row['manifest'],
            permissions=row['permissions'],
            config=row['config'],
            status=row['status'],
            installed_at=row['installed_at'],
            last_updated=row['last_updated'],
            installation_id=row['installation_id'],
            security_violations=row['security_violations'],
            last_violation=row['last_violation'],
            security_score=row['security_score'],
            created_at=row['created_at'],
            updated_at=row['updated_at']
        )
```

### Testing This Component

#### Database Test Setup
```python
# tests/conftest.py
import pytest
import asyncpg
import asyncio
from app.database import init_db_pool

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def test_db():
    """Setup test database"""
    # Use separate test database
    test_db_url = "postgresql://taylordash_test:password@localhost/taylordash_test"

    # Initialize test database pool
    pool = await init_db_pool(test_db_url)

    yield pool

    # Cleanup
    await pool.close()

@pytest.fixture
async def db_session(test_db):
    """Provide clean database session for each test"""
    async with test_db.acquire() as conn:
        # Start transaction
        async with conn.transaction():
            yield conn
            # Transaction is automatically rolled back
```

#### Database Test Examples
```python
# tests/test_database/test_plugin_operations.py
import pytest
from app.models.plugin import Plugin
from datetime import datetime

@pytest.mark.asyncio
async def test_plugin_crud_operations(db_session):
    """Test plugin CRUD operations"""
    # Test data
    plugin_data = {
        'id': 'test-plugin',
        'name': 'Test Plugin',
        'version': '1.0.0',
        'description': 'A test plugin',
        'author': 'Test Author',
        'type': 'ui',
        'repository_url': 'https://github.com/test/plugin',
        'install_path': '/plugins/test-plugin',
        'manifest': {'entry': 'index.js'},
        'permissions': ['read'],
        'config': {'enabled': True},
        'status': 'active',
        'installed_at': datetime.utcnow(),
        'last_updated': None,
        'installation_id': 'install-123',
        'security_violations': 0,
        'last_violation': None,
        'security_score': 100,
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow()
    }

    plugin = Plugin(**plugin_data)

    # Test save
    await plugin.save()

    # Test find by ID
    found_plugin = await Plugin.find_by_id('test-plugin')
    assert found_plugin is not None
    assert found_plugin.name == 'Test Plugin'
    assert found_plugin.status == 'active'

    # Test update
    plugin.status = 'disabled'
    plugin.security_score = 90
    await plugin.save()

    updated_plugin = await Plugin.find_by_id('test-plugin')
    assert updated_plugin.status == 'disabled'
    assert updated_plugin.security_score == 90

@pytest.mark.asyncio
async def test_jsonb_operations(db_session):
    """Test JSONB operations"""
    # Insert test plugin with complex config
    await db_session.execute("""
        INSERT INTO plugins (
            id, name, version, author, type, kind, repository_url,
            install_path, manifest, config, status
        ) VALUES (
            'jsonb-test', 'JSONB Test', '1.0.0', 'Test', 'ui', 'ui',
            'https://example.com', '/test', '{}', $1, 'active'
        )
    """, {
        'theme': 'dark',
        'features': ['feature1', 'feature2'],
        'settings': {
            'autoStart': True,
            'notifications': False
        }
    })

    # Test JSONB queries
    result = await db_session.fetchrow("""
        SELECT
            config->>'theme' as theme,
            config->'settings'->>'autoStart' as auto_start,
            jsonb_array_length(config->'features') as feature_count
        FROM plugins
        WHERE id = 'jsonb-test'
    """)

    assert result['theme'] == 'dark'
    assert result['auto_start'] == 'true'
    assert result['feature_count'] == 2
```

### Debugging Tips

#### Database Connection Debugging
```bash
# Check database connections
docker-compose exec postgres psql -U taylordash_app -d taylordash -c "
SELECT
    application_name,
    state,
    query_start,
    state_change,
    query
FROM pg_stat_activity
WHERE application_name LIKE '%taylordash%';"

# Monitor slow queries
docker-compose exec postgres psql -U taylordash_app -d taylordash -c "
SELECT
    query,
    calls,
    total_time,
    mean_time,
    stddev_time,
    rows
FROM pg_stat_statements
ORDER BY total_time DESC
LIMIT 10;"

# Check table sizes
docker-compose exec postgres psql -U taylordash_app -d taylordash -c "
SELECT
    schemaname,
    tablename,
    attname,
    n_distinct,
    correlation
FROM pg_stats
WHERE schemaname = 'public';"
```

### API Usage

#### Database Health Checks
```python
# Health check endpoint
@router.get("/health/database")
async def database_health():
    """Check database connectivity and performance"""
    try:
        pool = await get_db_pool()

        # Test basic connectivity
        start_time = time.time()
        async with pool.acquire() as conn:
            await conn.execute("SELECT 1")

        connection_time = (time.time() - start_time) * 1000

        # Get pool stats
        stats = {
            "status": "healthy",
            "connection_time_ms": round(connection_time, 2),
            "pool_size": pool.get_size(),
            "pool_min_size": pool.get_min_size(),
            "pool_max_size": pool.get_max_size(),
            "pool_free_connections": pool.get_idle_size()
        }

        return stats

    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }
```

#### MQTT Event Publishing
```python
# Example: Publishing database events to MQTT
async def publish_plugin_event(plugin_id: str, event_type: str, details: dict):
    """Publish plugin database events to MQTT"""
    from app.mqtt_client import get_mqtt_client
    import json

    event_data = {
        "event_type": event_type,
        "plugin_id": plugin_id,
        "timestamp": datetime.utcnow().isoformat(),
        "details": details
    }

    mqtt_client = get_mqtt_client()
    await mqtt_client.publish(
        topic=f"tracker/events/plugin/{event_type}",
        payload=json.dumps(event_data)
    )

# Usage in database operations
async def update_plugin_status(plugin_id: str, new_status: str):
    """Update plugin status and publish event"""
    async with get_db_connection() as conn:
        # Update database
        await conn.execute("""
            UPDATE plugins
            SET status = $2, updated_at = NOW()
            WHERE id = $1
        """, plugin_id, new_status)

        # Publish event
        await publish_plugin_event(
            plugin_id=plugin_id,
            event_type="status_changed",
            details={"new_status": new_status}
        )
```

## 🔧 Performance Optimization

- Use connection pooling for efficient resource management
- Add database indexes for frequently queried columns
- Use JSONB for flexible schema evolution
- Implement proper transaction management
- Monitor query performance with `pg_stat_statements`
- Use EXPLAIN ANALYZE for query optimization

## 🔐 Security Best Practices

- Use parameterized queries to prevent SQL injection
- Implement proper access controls and roles
- Encrypt sensitive data at rest
- Audit database access and modifications
- Regular backup and recovery testing
- Monitor for suspicious database activity