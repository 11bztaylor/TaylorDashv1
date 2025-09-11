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

# Metrics
http_requests_total = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
http_request_duration = Histogram('http_request_duration_seconds', 'HTTP request duration')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
    
    # Initialize MQTT processor
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
    
    yield
    
    # Shutdown
    logger.info("Shutting down TaylorDash Backend")
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

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
async def get_events(topic: str = None, kind: str = None, limit: int = 100):
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
async def get_dlq_events(limit: int = 50):
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
async def health_stack():
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
async def get_projects():
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
async def get_project(project_id: str):
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
async def create_project(project: ProjectCreate):
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
async def update_project(project_id: str, project_update: ProjectUpdate):
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
async def delete_project(project_id: str):
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
async def get_project_components(project_id: str):
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
async def get_component_tasks(component_id: str):
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
async def test_mqtt_event():
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