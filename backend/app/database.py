"""
Database connection and migration utilities
"""
import asyncpg
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Global connection pool
db_pool: Optional[asyncpg.Pool] = None

async def init_db_pool(database_url: str, retries: int = 5, delay: float = 2.0) -> asyncpg.Pool:
    """Initialize database connection pool with retry logic"""
    import asyncio
    
    global db_pool
    
    for attempt in range(retries):
        try:
            logger.info(f"Attempting to connect to database (attempt {attempt + 1}/{retries})")
            db_pool = await asyncpg.create_pool(database_url, min_size=5, max_size=20)
            
            # Test the connection
            async with db_pool.acquire() as conn:
                await conn.execute("SELECT 1")
            
            # Run migrations
            await run_migrations()
            
            logger.info("Database pool initialized successfully")
            return db_pool
        except Exception as e:
            logger.warning(f"Database connection attempt {attempt + 1} failed: {e}")
            if attempt < retries - 1:
                logger.info(f"Retrying in {delay} seconds...")
                await asyncio.sleep(delay)
            else:
                logger.error("All database connection attempts failed")
                raise

async def get_db_pool() -> asyncpg.Pool:
    """Get global database pool"""
    if db_pool is None:
        raise RuntimeError("Database pool not initialized")
    return db_pool

async def run_migrations():
    """Run database migrations"""
    if db_pool is None:
        raise RuntimeError("Database pool not initialized")
        
    async with db_pool.acquire() as conn:
        # Events mirror table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS events_mirror (
                id BIGSERIAL PRIMARY KEY,
                topic VARCHAR(255) NOT NULL,
                payload JSONB NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                trace_id UUID GENERATED ALWAYS AS ((payload->>'trace_id')::UUID) STORED
            )
        """)
        
        # Index for performance
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_events_mirror_topic ON events_mirror(topic)
        """)
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_events_mirror_trace_id ON events_mirror(trace_id)
        """)
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_events_mirror_created_at ON events_mirror(created_at)
        """)
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_events_mirror_kind ON events_mirror((payload->>'kind'))
        """)
        
        # DLQ events table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS dlq_events (
                id BIGSERIAL PRIMARY KEY,
                original_topic VARCHAR(255) NOT NULL,
                failure_reason TEXT NOT NULL,
                payload JSONB NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            )
        """)
        
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_dlq_events_topic ON dlq_events(original_topic)
        """)
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_dlq_events_created_at ON dlq_events(created_at)
        """)
        
        # Projects table (metadata)
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                name VARCHAR(255) NOT NULL,
                description TEXT,
                status VARCHAR(50) DEFAULT 'active',
                owner_id UUID,
                metadata JSONB DEFAULT '{}',
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            )
        """)
        
        # Components table (metadata)
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS components (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
                name VARCHAR(255) NOT NULL,
                type VARCHAR(100),
                status VARCHAR(50) DEFAULT 'pending',
                progress INTEGER DEFAULT 0,
                position JSONB,
                metadata JSONB DEFAULT '{}',
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            )
        """)
        
        # Component dependencies
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS component_dependencies (
                component_id UUID REFERENCES components(id) ON DELETE CASCADE,
                depends_on_id UUID REFERENCES components(id) ON DELETE CASCADE,
                PRIMARY KEY (component_id, depends_on_id)
            )
        """)
        
        # Tasks table (metadata)
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
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
            )
        """)
        
        logger.info("Database migrations completed")

async def close_db_pool():
    """Close database connection pool"""
    global db_pool
    if db_pool:
        await db_pool.close()
        db_pool = None
        logger.info("Database pool closed")