"""
FastAPI backend with health checks, metrics, and MQTT integration
"""
import asyncio
import json
import logging
import os
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST, Counter, Histogram
from starlette.responses import Response
import uvicorn

from .otel import init_telemetry
from .database import init_db_pool, close_db_pool, get_db_pool
from .mqtt_client import init_mqtt_processor, get_mqtt_processor
from .security import verify_api_key, SecurityHeadersMiddleware
from .logging_middleware import add_logging_middleware
from .logging_utils import get_logger, init_logger
from .routers import auth
try:
    from .routers import plugins
    PLUGINS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Plugin router unavailable: {e}")
    PLUGINS_AVAILABLE = False

try:
    from .routers import mcp
    MCP_AVAILABLE = True
except ImportError as e:
    print(f"Warning: MCP router unavailable: {e}")
    MCP_AVAILABLE = False

# Metrics - use try/except to handle potential registration conflicts
try:
    http_requests_total = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
    http_request_duration = Histogram('http_request_duration_seconds', 'HTTP request duration')
except ValueError as e:
    # Handle duplicate metric registration during reload
    if "Duplicated timeseries" in str(e):
        from prometheus_client import CollectorRegistry, REGISTRY
        # Create new registry for this instance
        REGISTRY._collector_to_names.clear()
        REGISTRY._names_to_collectors.clear()
        http_requests_total = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
        http_request_duration = Histogram('http_request_duration_seconds', 'HTTP request duration')
    else:
        raise

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
struct_logger = None  # Will be initialized with db pool

async def init_plugin_schema():
    """Initialize plugin database schema"""
    try:
        db_pool = await get_db_pool()
        schema_path = Path(__file__).parent / "database" / "plugin_schema.sql"
        
        if not schema_path.exists():
            logger.warning(f"Plugin schema file not found at {schema_path}")
            return
        
        with open(schema_path, 'r') as f:
            schema_sql = f.read()
        
        async with db_pool.acquire() as conn:
            # Execute schema in a transaction
            async with conn.transaction():
                await conn.execute(schema_sql)
            
        logger.info("Plugin database schema initialized successfully")
    except FileNotFoundError as e:
        logger.warning(f"Plugin schema file not found: {e}")
    except Exception as e:
        logger.error(f"Failed to initialize plugin schema: {e}")
        # Check if this is a permissions issue and provide helpful error message
        if "must be owner" in str(e):
            logger.error("Database user permissions issue. Plugin features may be limited.")
        # Don't raise here as we want the app to continue running

# Pydantic Models for Projects CRUD
class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Project name")
    description: Optional[str] = Field(None, max_length=1000, description="Project description")
    status: str = Field("planning", description="Project status")
    owner_id: Optional[str] = Field(None, description="Owner ID")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")

class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Project name")
    description: Optional[str] = Field(None, max_length=1000, description="Project description")
    status: Optional[str] = Field(None, description="Project status")
    owner_id: Optional[str] = Field(None, description="Owner ID")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")

class ProjectResponse(BaseModel):
    id: str = Field(..., description="Project ID")
    name: str = Field(..., description="Project name")
    description: Optional[str] = Field(None, description="Project description")
    status: str = Field(..., description="Project status")
    owner_id: Optional[str] = Field(None, description="Owner ID")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan"""
    # Startup
    logger.info("Starting TaylorDash Backend")
    # init_telemetry()  # Disabled for now
    
    # Initialize database
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL environment variable is required")
    logger.info(f"Connecting to database with URL: {database_url[:database_url.find('@')+1]}***")
    await init_db_pool(database_url)
    
    # Initialize plugin database schema
    await init_plugin_schema()
    
    # Initialize structured logging with database pool
    global struct_logger
    db_pool = await get_db_pool()
    struct_logger = init_logger(db_pool)
    logger.info("Structured logging initialized with database integration")
    
    # Log system startup
    await struct_logger.info(
        "TaylorDash Backend starting up",
        context={"database_url": database_url[:database_url.find('@')+1]+"***"}
    )
    
    # Initialize MQTT processor
    mqtt_processor = None
    mqtt_task = None
    try:
        mqtt_host = os.getenv("MQTT_HOST", "localhost")
        mqtt_port = int(os.getenv("MQTT_PORT", "1883"))
        mqtt_username = os.getenv("MQTT_USERNAME", "")
        mqtt_password = os.getenv("MQTT_PASSWORD", "")
        
        db_pool = await get_db_pool()
        mqtt_processor = await init_mqtt_processor(
            mqtt_host, mqtt_port, mqtt_username, mqtt_password, db_pool
        )
        
        # Start MQTT processor in background
        mqtt_task = asyncio.create_task(mqtt_processor.start())
        logger.info(f"Started MQTT processor connecting to {mqtt_host}:{mqtt_port}")
        
        # Log successful MQTT initialization
        await struct_logger.info(
            "MQTT processor initialized successfully",
            context={"mqtt_host": mqtt_host, "mqtt_port": mqtt_port}
        )
    except Exception as e:
        logger.warning(f"MQTT processor initialization failed: {e}")
        await struct_logger.warn(
            "MQTT processor initialization failed - continuing without MQTT",
            category="MQTT",
            severity="MEDIUM",
            details=str(e)
        )
    
    yield
    
    # Shutdown
    logger.info("Shutting down TaylorDash Backend")
    
    # Clean up MCP processes
    if MCP_AVAILABLE:
        await mcp.cleanup_mcp_processes()
    
    if mqtt_processor:
        await mqtt_processor.stop()
    if mqtt_task:
        mqtt_task.cancel()
        try:
            await mqtt_task
        except asyncio.CancelledError:
            pass
    await close_db_pool()

app = FastAPI(
    title="TaylorDash API",
    description="Event-driven project management API",
    version="1.0.0",
    lifespan=lifespan
)

# Security headers middleware
app.add_middleware(SecurityHeadersMiddleware)

# Add logging middleware (will be initialized with db pool in lifespan)
add_logging_middleware(app)

# CORS middleware - restrict origins for security
allowed_origins = [
    "http://localhost:3000",  # Frontend dev server
    "http://localhost:5173",  # Vite dev server
    "https://taylordash.local",  # Production domain
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Include plugin management router
if PLUGINS_AVAILABLE:
    app.include_router(plugins.router)
    print("Plugin management router enabled")
else:
    print("Plugin management router disabled due to import errors")

# Include MCP router
if MCP_AVAILABLE:
    app.include_router(mcp.router, prefix="/api/v1")
    print("MCP router enabled")
else:
    print("MCP router disabled due to import errors")

# Include auth router
app.include_router(auth.router)

@app.get("/health/live")
async def health_live():
    """Liveness probe"""
    return {"status": "alive", "service": "taylordash-backend"}

@app.get("/health/ready") 
async def health_ready():
    """Readiness probe"""
    try:
        # Check database connection
        pool = await get_db_pool()
        async with pool.acquire() as conn:
            await conn.execute("SELECT 1")
        return {"status": "ready", "service": "taylordash-backend", "database": "healthy"}
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        raise HTTPException(status_code=503, detail="Database not ready")

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


# Events query endpoint
@app.get("/api/v1/events")
async def get_events(topic: str = None, kind: str = None, limit: int = 100, api_key: str = Depends(verify_api_key)):
    """Get events from mirror"""
    try:
        pool = await get_db_pool()
        async with pool.acquire() as conn:
            # Build query based on filters
            query = "SELECT topic, payload, created_at FROM events_mirror"
            conditions = []
            params = []
            
            if topic:
                conditions.append(f"topic = ${len(params) + 1}")
                params.append(topic)
            
            if kind:
                conditions.append(f"payload->>'kind' = ${len(params) + 1}")
                params.append(kind)
                
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
                
            query += f" ORDER BY created_at DESC LIMIT ${len(params) + 1}"
            params.append(limit)
            
            rows = await conn.fetch(query, *params)
            events = [dict(row) for row in rows]
            
            # Convert datetime objects to ISO format
            for event in events:
                if event.get('created_at'):
                    event['created_at'] = event['created_at'].isoformat()
            
            return {"events": events, "count": len(events)}
    except Exception as e:
        logger.error(f"Failed to fetch events: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch events")

# DLQ monitoring endpoint
@app.get("/api/v1/dlq")
async def get_dlq_events(limit: int = 50, api_key: str = Depends(verify_api_key)):
    """Get DLQ events"""
    try:
        pool = await get_db_pool()
        async with pool.acquire() as conn:
            rows = await conn.fetch(
                "SELECT original_topic, failure_reason, payload, created_at FROM dlq_events ORDER BY created_at DESC LIMIT $1",
                limit
            )
            dlq_events = [dict(row) for row in rows]
            
            # Convert datetime objects to ISO format
            for event in dlq_events:
                if event.get('created_at'):
                    event['created_at'] = event['created_at'].isoformat()
            
            return {"dlq_events": dlq_events, "count": len(dlq_events)}
    except Exception as e:
        logger.error(f"Failed to fetch DLQ events: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch DLQ events")

@app.get("/api/v1/health/stack")
async def health_stack(api_key: str = Depends(verify_api_key)):
    """Comprehensive stack health check"""
    services = {}
    overall_healthy = True
    
    # Database health check
    try:
        pool = await get_db_pool()
        async with pool.acquire() as conn:
            await conn.execute("SELECT 1")
        services["database"] = {
            "status": "healthy",
            "type": "postgresql",
            "message": "Database is connected and responsive"
        }
    except Exception as e:
        services["database"] = {
            "status": "unhealthy",
            "type": "postgresql",
            "message": f"Database connection failed: {str(e)}"
        }
        overall_healthy = False
    
    # MQTT health check
    try:
        mqtt_processor = await get_mqtt_processor()
        if mqtt_processor and mqtt_processor.running:
            services["mqtt"] = {
                "status": "healthy",
                "type": "mqtt",
                "message": "MQTT processor is running and connected"
            }
        else:
            services["mqtt"] = {
                "status": "unhealthy", 
                "type": "mqtt",
                "message": "MQTT processor is not running"
            }
            overall_healthy = False
    except Exception as e:
        services["mqtt"] = {
            "status": "unhealthy",
            "type": "mqtt", 
            "message": f"MQTT processor error: {str(e)}"
        }
        overall_healthy = False
    
    # API health check
    services["api"] = {
        "status": "healthy",
        "type": "fastapi",
        "message": "API server is running"
    }
    
    status_code = 200 if overall_healthy else 503
    return Response(
        content=json.dumps({
            "overall_status": "healthy" if overall_healthy else "unhealthy",
            "services": services,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }),
        status_code=status_code,
        media_type="application/json"
    )

# Project Management API Endpoints
@app.get("/api/v1/projects")
async def get_projects(api_key: str = Depends(verify_api_key)):
    """Get all projects"""
    try:
        pool = await get_db_pool()
        async with pool.acquire() as conn:
            rows = await conn.fetch(
                "SELECT id, name, description, status, owner_id, metadata, created_at, updated_at FROM projects ORDER BY created_at DESC"
            )
            projects = [dict(row) for row in rows]
            
            # Convert datetime and UUID objects to ISO format and strings
            for project in projects:
                if project.get('created_at'):
                    project['created_at'] = project['created_at'].isoformat()
                if project.get('updated_at'):
                    project['updated_at'] = project['updated_at'].isoformat()
                if project.get('id'):
                    project['id'] = str(project['id'])
                if project.get('owner_id'):
                    project['owner_id'] = str(project['owner_id'])
                # Parse metadata JSON string back to dict
                if project.get('metadata'):
                    if isinstance(project['metadata'], str):
                        project['metadata'] = json.loads(project['metadata'])
                else:
                    project['metadata'] = {}
            
            return {"projects": projects, "count": len(projects)}
    except Exception as e:
        logger.error(f"Failed to fetch projects: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch projects")

@app.get("/api/v1/projects/{project_id}")
async def get_project(project_id: str, api_key: str = Depends(verify_api_key)):
    """Get project by ID"""
    try:
        pool = await get_db_pool()
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT id, name, description, status, owner_id, metadata, created_at, updated_at FROM projects WHERE id = $1",
                project_id
            )
            
            if not row:
                raise HTTPException(status_code=404, detail="Project not found")
            
            project = dict(row)
            
            # Convert datetime and UUID objects to ISO format and strings
            if project.get('created_at'):
                project['created_at'] = project['created_at'].isoformat()
            if project.get('updated_at'):
                project['updated_at'] = project['updated_at'].isoformat()
            if project.get('id'):
                project['id'] = str(project['id'])
            if project.get('owner_id'):
                project['owner_id'] = str(project['owner_id'])
            # Parse metadata JSON string back to dict
            if project.get('metadata'):
                if isinstance(project['metadata'], str):
                    project['metadata'] = json.loads(project['metadata'])
            else:
                project['metadata'] = {}
            
            return project
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid project ID format")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch project {project_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch project")

@app.post("/api/v1/projects", status_code=status.HTTP_201_CREATED, response_model=ProjectResponse)
async def create_project(project: ProjectCreate, api_key: str = Depends(verify_api_key)):
    """Create a new project"""
    try:
        pool = await get_db_pool()
        new_project_id = str(uuid.uuid4())
        current_time = datetime.now(timezone.utc)
        
        async with pool.acquire() as conn:
            # Insert the new project
            row = await conn.fetchrow("""
                INSERT INTO projects (id, name, description, status, owner_id, metadata, created_at, updated_at)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $7)
                RETURNING id, name, description, status, owner_id, metadata, created_at, updated_at
            """, 
                new_project_id,
                project.name,
                project.description,
                project.status,
                project.owner_id,
                json.dumps(project.metadata),
                current_time
            )
            
            # Convert row to dict and format for response
            created_project = dict(row)
            created_project['id'] = str(created_project['id'])
            if created_project.get('owner_id'):
                created_project['owner_id'] = str(created_project['owner_id'])
            # Parse metadata JSON string back to dict
            if created_project.get('metadata'):
                if isinstance(created_project['metadata'], str):
                    created_project['metadata'] = json.loads(created_project['metadata'])
            else:
                created_project['metadata'] = {}
            
            # Publish MQTT event for project creation
            try:
                mqtt_processor = await get_mqtt_processor()
                await mqtt_processor.publish_event(
                    topic="tracker/events/projects/created",
                    kind="project_created",
                    payload={
                        "project_id": created_project['id'],
                        "name": created_project['name'],
                        "status": created_project['status'],
                        "created_by": created_project.get('owner_id'),
                        "timestamp": current_time.isoformat()
                    }
                )
            except Exception as mqtt_error:
                logger.warning(f"Failed to publish project creation event: {mqtt_error}")
            
            return created_project
            
    except Exception as e:
        logger.error(f"Failed to create project: {e}")
        raise HTTPException(status_code=500, detail="Failed to create project")

@app.put("/api/v1/projects/{project_id}", response_model=ProjectResponse)
async def update_project(project_id: str, project_update: ProjectUpdate, api_key: str = Depends(verify_api_key)):
    """Update an existing project"""
    try:
        pool = await get_db_pool()
        current_time = datetime.now(timezone.utc)
        
        async with pool.acquire() as conn:
            # First check if project exists
            existing = await conn.fetchrow("SELECT id FROM projects WHERE id = $1", project_id)
            if not existing:
                raise HTTPException(status_code=404, detail="Project not found")
            
            # Build dynamic update query based on provided fields
            update_fields = []
            params = [project_id]
            param_count = 1
            
            if project_update.name is not None:
                param_count += 1
                update_fields.append(f"name = ${param_count}")
                params.append(project_update.name)
            
            if project_update.description is not None:
                param_count += 1
                update_fields.append(f"description = ${param_count}")
                params.append(project_update.description)
                
            if project_update.status is not None:
                param_count += 1
                update_fields.append(f"status = ${param_count}")
                params.append(project_update.status)
                
            if project_update.owner_id is not None:
                param_count += 1
                update_fields.append(f"owner_id = ${param_count}")
                params.append(project_update.owner_id)
                
            if project_update.metadata is not None:
                param_count += 1
                update_fields.append(f"metadata = ${param_count}")
                params.append(json.dumps(project_update.metadata))
            
            # Always update the updated_at timestamp
            param_count += 1
            update_fields.append(f"updated_at = ${param_count}")
            params.append(current_time)
            
            if not update_fields:
                raise HTTPException(status_code=400, detail="No fields to update")
            
            query = f"""
                UPDATE projects 
                SET {', '.join(update_fields)}
                WHERE id = $1
                RETURNING id, name, description, status, owner_id, metadata, created_at, updated_at
            """
            
            row = await conn.fetchrow(query, *params)
            
            # Convert row to dict and format for response
            updated_project = dict(row)
            updated_project['id'] = str(updated_project['id'])
            if updated_project.get('owner_id'):
                updated_project['owner_id'] = str(updated_project['owner_id'])
            # Parse metadata JSON string back to dict
            if updated_project.get('metadata'):
                if isinstance(updated_project['metadata'], str):
                    updated_project['metadata'] = json.loads(updated_project['metadata'])
            else:
                updated_project['metadata'] = {}
                
            # Publish MQTT event for project update
            try:
                mqtt_processor = await get_mqtt_processor()
                await mqtt_processor.publish_event(
                    topic="tracker/events/projects/updated",
                    kind="project_updated",
                    payload={
                        "project_id": updated_project['id'],
                        "name": updated_project['name'],
                        "status": updated_project['status'],
                        "updated_by": updated_project.get('owner_id'),
                        "timestamp": current_time.isoformat(),
                        "updated_fields": [field.split(' = ')[0] for field in update_fields if 'updated_at' not in field]
                    }
                )
            except Exception as mqtt_error:
                logger.warning(f"Failed to publish project update event: {mqtt_error}")
            
            return updated_project
            
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid project ID format")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update project {project_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to update project")

@app.delete("/api/v1/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(project_id: str, api_key: str = Depends(verify_api_key)):
    """Delete a project"""
    try:
        pool = await get_db_pool()
        
        async with pool.acquire() as conn:
            # First check if project exists and get its info for the event
            existing_project = await conn.fetchrow(
                "SELECT id, name, status, owner_id FROM projects WHERE id = $1", 
                project_id
            )
            if not existing_project:
                raise HTTPException(status_code=404, detail="Project not found")
            
            # Delete the project (this will cascade to components and tasks due to foreign key constraints)
            result = await conn.execute("DELETE FROM projects WHERE id = $1", project_id)
            
            if result == "DELETE 0":
                raise HTTPException(status_code=404, detail="Project not found")
            
            # Publish MQTT event for project deletion
            try:
                mqtt_processor = await get_mqtt_processor()
                await mqtt_processor.publish_event(
                    topic="tracker/events/projects/deleted",
                    kind="project_deleted",
                    payload={
                        "project_id": str(existing_project['id']),
                        "name": existing_project['name'],
                        "status": existing_project['status'],
                        "deleted_by": str(existing_project['owner_id']) if existing_project['owner_id'] else None,
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    }
                )
            except Exception as mqtt_error:
                logger.warning(f"Failed to publish project deletion event: {mqtt_error}")
            
            return  # 204 No Content
            
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid project ID format")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete project {project_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete project")

@app.get("/api/v1/projects/{project_id}/components")
async def get_project_components(project_id: str, api_key: str = Depends(verify_api_key)):
    """Get components for a project"""
    try:
        pool = await get_db_pool()
        async with pool.acquire() as conn:
            rows = await conn.fetch(
                "SELECT id, project_id, name, type, status, progress, position, metadata, created_at, updated_at FROM components WHERE project_id = $1 ORDER BY created_at DESC",
                project_id
            )
            components = [dict(row) for row in rows]
            
            # Convert datetime and UUID objects to ISO format and strings
            for component in components:
                if component.get('created_at'):
                    component['created_at'] = component['created_at'].isoformat()
                if component.get('updated_at'):
                    component['updated_at'] = component['updated_at'].isoformat()
                if component.get('id'):
                    component['id'] = str(component['id'])
                if component.get('project_id'):
                    component['project_id'] = str(component['project_id'])
            
            return {"components": components, "count": len(components)}
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid project ID format")
    except Exception as e:
        logger.error(f"Failed to fetch components for project {project_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch components")

@app.get("/api/v1/components/{component_id}/tasks")
async def get_component_tasks(component_id: str, api_key: str = Depends(verify_api_key)):
    """Get tasks for a component"""
    try:
        pool = await get_db_pool()
        async with pool.acquire() as conn:
            rows = await conn.fetch(
                "SELECT id, component_id, name, description, status, assignee_id, due_date, completed_at, created_at, updated_at FROM tasks WHERE component_id = $1 ORDER BY created_at DESC",
                component_id
            )
            tasks = [dict(row) for row in rows]
            
            # Convert datetime and UUID objects to ISO format and strings
            for task in tasks:
                if task.get('created_at'):
                    task['created_at'] = task['created_at'].isoformat()
                if task.get('updated_at'):
                    task['updated_at'] = task['updated_at'].isoformat()
                if task.get('due_date'):
                    task['due_date'] = task['due_date'].isoformat()
                if task.get('completed_at'):
                    task['completed_at'] = task['completed_at'].isoformat()
                if task.get('id'):
                    task['id'] = str(task['id'])
                if task.get('component_id'):
                    task['component_id'] = str(task['component_id'])
                if task.get('assignee_id'):
                    task['assignee_id'] = str(task['assignee_id'])
            
            return {"tasks": tasks, "count": len(tasks)}
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid component ID format")
    except Exception as e:
        logger.error(f"Failed to fetch tasks for component {component_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch tasks")

@app.post("/api/v1/events/test")
async def test_mqtt_event(api_key: str = Depends(verify_api_key)):
    """Test MQTT event publishing"""
    try:
        mqtt_processor = await get_mqtt_processor()
        trace_id = await mqtt_processor.publish_event(
            topic="tracker/events/test/api",
            kind="test_event",
            payload={"message": "Test event from API", "timestamp": datetime.now(timezone.utc).isoformat()}
        )
        return {"status": "success", "trace_id": trace_id, "message": "Test event published"}
    except Exception as e:
        logger.error(f"Failed to publish test event: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to publish test event: {e}")

# Log viewing endpoints
@app.get("/api/v1/logs")
async def get_logs(
    level: Optional[str] = None,
    service: Optional[str] = None,
    category: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    api_key: str = Depends(verify_api_key)
):
    """Get application logs with filtering"""
    try:
        pool = await get_db_pool()
        async with pool.acquire() as conn:
            # Build query based on filters
            where_conditions = []
            params = []
            param_count = 0
            
            if level and level != 'ALL':
                param_count += 1
                where_conditions.append(f"level = ${param_count}")
                params.append(level)
            
            if service and service != 'ALL':
                param_count += 1
                where_conditions.append(f"service = ${param_count}")
                params.append(service)
            
            if category and category != 'ALL':
                param_count += 1
                where_conditions.append(f"category = ${param_count}")
                params.append(category)
            
            if search:
                param_count += 1
                where_conditions.append(f"(message ILIKE ${param_count} OR details ILIKE ${param_count})")
                params.append(f"%{search}%")
            
            where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"
            
            query = f"""
                SELECT id, timestamp, level, service, category, severity, message, details,
                       trace_id, request_id, user_id, endpoint, method, status_code,
                       duration_ms, error_code, context, environment
                FROM logging.application_logs 
                WHERE {where_clause}
                ORDER BY timestamp DESC 
                LIMIT ${param_count + 1} OFFSET ${param_count + 2}
            """
            
            params.extend([limit, offset])
            rows = await conn.fetch(query, *params)
            
            # Convert to dict and format timestamps
            logs = []
            for row in rows:
                log_dict = dict(row)
                log_dict['timestamp'] = log_dict['timestamp'].isoformat()
                # Parse context JSON if it exists
                if log_dict.get('context'):
                    try:
                        if isinstance(log_dict['context'], str):
                            log_dict['context'] = json.loads(log_dict['context'])
                    except json.JSONDecodeError:
                        pass  # Keep as string if invalid JSON
                logs.append(log_dict)
            
            # Get total count for pagination
            count_query = f"SELECT COUNT(*) FROM logging.application_logs WHERE {where_clause}"
            count_params = params[:-2]  # Remove limit and offset
            total_count = await conn.fetchval(count_query, *count_params)
            
            return {
                "logs": logs,
                "total": total_count,
                "limit": limit,
                "offset": offset,
                "has_more": total_count > offset + len(logs)
            }
    except Exception as e:
        logger.error(f"Failed to fetch logs: {e}")
        if struct_logger:
            await struct_logger.error("Failed to fetch logs", exc=e, category="API")
        raise HTTPException(status_code=500, detail="Failed to fetch logs")

@app.get("/api/v1/logs/{log_id}")
async def get_log_detail(log_id: int, api_key: str = Depends(verify_api_key)):
    """Get detailed log entry by ID"""
    try:
        pool = await get_db_pool()
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM logging.application_logs WHERE id = $1",
                log_id
            )
            
            if not row:
                raise HTTPException(status_code=404, detail="Log entry not found")
            
            log_dict = dict(row)
            log_dict['timestamp'] = log_dict['timestamp'].isoformat()
            
            # Parse context JSON
            if log_dict.get('context'):
                try:
                    if isinstance(log_dict['context'], str):
                        log_dict['context'] = json.loads(log_dict['context'])
                except json.JSONDecodeError:
                    pass
            
            return log_dict
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch log detail: {e}")
        if struct_logger:
            await struct_logger.error("Failed to fetch log detail", exc=e, category="API")
        raise HTTPException(status_code=500, detail="Failed to fetch log detail")

@app.get("/api/v1/logs/stats")
async def get_log_stats(
    hours: int = 24,
    api_key: str = Depends(verify_api_key)
):
    """Get log statistics for dashboard"""
    try:
        pool = await get_db_pool()
        async with pool.acquire() as conn:
            # Get stats for the last N hours
            stats_query = """
                SELECT 
                    level,
                    category,
                    service,
                    COUNT(*) as count,
                    AVG(duration_ms) as avg_duration,
                    MAX(duration_ms) as max_duration
                FROM logging.application_logs 
                WHERE timestamp >= NOW() - INTERVAL '%s hours'
                GROUP BY level, category, service
                ORDER BY count DESC
            """
            
            stats = await conn.fetch(stats_query, hours)
            
            # Get error rate by hour
            error_rate_query = """
                SELECT 
                    DATE_TRUNC('hour', timestamp) as hour,
                    COUNT(*) FILTER (WHERE level = 'ERROR') as error_count,
                    COUNT(*) as total_count
                FROM logging.application_logs 
                WHERE timestamp >= NOW() - INTERVAL '%s hours'
                GROUP BY DATE_TRUNC('hour', timestamp)
                ORDER BY hour DESC
            """
            
            error_rates = await conn.fetch(error_rate_query, hours)
            
            # Format results
            stats_formatted = []
            for row in stats:
                stat_dict = dict(row)
                if stat_dict['avg_duration']:
                    stat_dict['avg_duration'] = float(stat_dict['avg_duration'])
                stats_formatted.append(stat_dict)
            
            error_rates_formatted = []
            for row in error_rates:
                rate_dict = dict(row)
                rate_dict['hour'] = rate_dict['hour'].isoformat()
                rate_dict['error_rate'] = (
                    rate_dict['error_count'] / rate_dict['total_count'] 
                    if rate_dict['total_count'] > 0 else 0
                )
                error_rates_formatted.append(rate_dict)
            
            return {
                "timeframe_hours": hours,
                "stats": stats_formatted,
                "error_rates": error_rates_formatted,
                "generated_at": datetime.now(timezone.utc).isoformat()
            }
    except Exception as e:
        logger.error(f"Failed to fetch log stats: {e}")
        if struct_logger:
            await struct_logger.error("Failed to fetch log stats", exc=e, category="API")
        raise HTTPException(status_code=500, detail="Failed to fetch log stats")

@app.post("/api/v1/logs/test")
async def test_logging(api_key: str = Depends(verify_api_key)):
    """Test endpoint to generate various log entries"""
    try:
        if not struct_logger:
            raise HTTPException(status_code=500, detail="Structured logging not initialized")
        
        # Generate test logs
        await struct_logger.info(
            "Test INFO log entry",
            category="API",
            severity="INFO",
            context={"test": True, "endpoint": "/api/v1/logs/test"}
        )
        
        await struct_logger.warn(
            "Test WARNING log entry",
            category="API", 
            severity="MEDIUM",
            context={"test": True, "warning_type": "test_warning"}
        )
        
        await struct_logger.error(
            "Test ERROR log entry",
            category="API",
            severity="HIGH",
            error_code="TEST_ERROR",
            details="This is a test error for demonstration",
            context={"test": True, "error_type": "test_error"}
        )
        
        return {
            "message": "Test log entries created successfully",
            "logs_created": 3,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to create test logs: {e}")
        raise HTTPException(status_code=500, detail="Failed to create test logs")

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "TaylorDash Backend API", "version": "1.0.0"}

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )