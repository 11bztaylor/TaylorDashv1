"""
FastAPI backend with health checks, metrics, and MQTT integration
"""
import asyncio
import logging
import os
from contextlib import asynccontextmanager
from typing import Dict, Any, List

from fastapi import FastAPI, Depends, HTTPException, status
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST, Counter, Histogram
from starlette.responses import Response
import uvicorn

from .otel import init_telemetry
from .database import init_db_pool, close_db_pool, get_db_pool
from .mqtt_client import init_mqtt_processor, get_mqtt_processor
from .health_stack import get_stack_health
from .routers import projects
from .core.cors import configure_cors

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
    init_telemetry()
    
    # Initialize database
    database_url = os.getenv("DATABASE_URL", "postgresql://taylordash:taylordash@postgres:5432/taylordash")
    await init_db_pool(database_url)
    
    # Initialize MQTT processor
    mqtt_host = os.getenv("MQTT_HOST", "mosquitto")
    mqtt_port = int(os.getenv("MQTT_PORT", "1883"))
    mqtt_username = os.getenv("MQTT_USERNAME", "taylordash")
    mqtt_password = os.getenv("MQTT_PASSWORD", "taylordash")
    
    db_pool = await get_db_pool()
    mqtt_processor = await init_mqtt_processor(mqtt_host, mqtt_port, mqtt_username, mqtt_password, db_pool)
    
    # Start MQTT processor in background
    mqtt_task = asyncio.create_task(mqtt_processor.start())
    
    yield
    
    # Shutdown
    logger.info("Shutting down TaylorDash Backend")
    await mqtt_processor.stop()
    mqtt_task.cancel()
    await close_db_pool()

app = FastAPI(
    title="TaylorDash API",
    description="Event-driven project management API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
configure_cors(app)

# Include routers
app.include_router(projects.router)

@app.get("/health/live")
async def health_live():
    """Liveness probe"""
    return {"status": "alive", "service": "taylordash-backend"}

@app.get("/health/ready") 
async def health_ready():
    """Readiness probe"""
    try:
        # Check database connectivity
        db_pool = await get_db_pool()
        async with db_pool.acquire() as conn:
            await conn.fetchval("SELECT 1")
        
        # Check MQTT processor
        mqtt_processor = await get_mqtt_processor()
        if not mqtt_processor.running:
            raise HTTPException(status_code=503, detail="MQTT processor not running")
            
        return {"status": "ready", "service": "taylordash-backend"}
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        raise HTTPException(status_code=503, detail="Service not ready")

@app.get("/api/v1/health/stack")
async def health_stack():
    """Stack health check - probe all services"""
    try:
        result = await get_stack_health()
        return result
    except Exception as e:
        logger.error(f"Stack health check failed: {e}")
        raise HTTPException(status_code=500, detail="Stack health check failed")

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

# Event publishing endpoint for testing
@app.post("/api/v1/events/publish")
async def publish_event(topic: str, kind: str, payload: Dict[str, Any]):
    """Publish event to MQTT (testing endpoint)"""
    try:
        mqtt_processor = await get_mqtt_processor()
        trace_id = await mqtt_processor.publish_event(topic, kind, payload)
        return {"trace_id": trace_id, "status": "published"}
    except Exception as e:
        logger.error(f"Failed to publish event: {e}")
        raise HTTPException(status_code=500, detail="Failed to publish event")

# Events query endpoint
@app.get("/api/v1/events")
async def get_events(topic: str = None, kind: str = None, limit: int = 100):
    """Get events from mirror"""
    try:
        db_pool = await get_db_pool()
        async with db_pool.acquire() as conn:
            query = "SELECT topic, payload, created_at FROM events_mirror"
            params = []
            conditions = []
            
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
            
            events = []
            for row in rows:
                events.append({
                    "topic": row["topic"],
                    "payload": row["payload"],
                    "created_at": row["created_at"].isoformat()
                })
                
            return {"events": events, "count": len(events)}
    except Exception as e:
        logger.error(f"Failed to get events: {e}")
        raise HTTPException(status_code=500, detail="Failed to get events")

# DLQ monitoring endpoint
@app.get("/api/v1/dlq")
async def get_dlq_events(limit: int = 50):
    """Get DLQ events"""
    try:
        db_pool = await get_db_pool()
        async with db_pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT original_topic, failure_reason, payload, created_at 
                FROM dlq_events 
                ORDER BY created_at DESC 
                LIMIT $1
            """, limit)
            
            events = []
            for row in rows:
                events.append({
                    "original_topic": row["original_topic"],
                    "failure_reason": row["failure_reason"],
                    "payload": row["payload"],
                    "created_at": row["created_at"].isoformat()
                })
                
            return {"dlq_events": events, "count": len(events)}
    except Exception as e:
        logger.error(f"Failed to get DLQ events: {e}")
        raise HTTPException(status_code=500, detail="Failed to get DLQ events")

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