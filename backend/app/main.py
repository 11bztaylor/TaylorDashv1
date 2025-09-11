"""
FastAPI backend with health checks, metrics, and MQTT integration
"""
import asyncio
import json
import logging
import os
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Dict, Any, List

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
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
            
            return project
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid project ID format")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch project {project_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch project")

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