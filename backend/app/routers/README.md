# 🚀 TaylorDash API Routers

FastAPI routers for the TaylorDash backend. This directory contains modular API endpoints organized by domain.

## 📁 Current Routers

- **`auth.py`** - Authentication and user management
- **`mcp.py`** - MCP (Model Context Protocol) integration
- **`plugins.py`** - Plugin management and execution

## 💻 Code Examples

### Common Patterns

#### Creating a New API Router
```python
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID

from ..database import get_db_connection
from ..security import verify_api_key

# Create router with prefix and tags
router = APIRouter(prefix="/api/v1/example", tags=["example"])

# Request/Response models
class ExampleRequest(BaseModel):
    name: str
    description: Optional[str] = None

class ExampleResponse(BaseModel):
    id: str
    name: str
    status: str

@router.get("/", response_model=List[ExampleResponse])
async def list_examples(api_key: str = Depends(verify_api_key)):
    """List all examples with API key authentication"""
    async with get_db_connection() as conn:
        rows = await conn.fetch("""
            SELECT id, name, status
            FROM examples
            ORDER BY created_at DESC
        """)
        return [ExampleResponse(**dict(row)) for row in rows]

@router.post("/", response_model=ExampleResponse, status_code=status.HTTP_201_CREATED)
async def create_example(
    request: ExampleRequest,
    api_key: str = Depends(verify_api_key)
):
    """Create a new example"""
    async with get_db_connection() as conn:
        example_id = str(uuid4())
        await conn.execute("""
            INSERT INTO examples (id, name, description, status)
            VALUES ($1, $2, $3, $4)
        """, example_id, request.name, request.description, "active")

        return ExampleResponse(
            id=example_id,
            name=request.name,
            status="active"
        )
```

#### Error Handling Pattern
```python
@router.get("/{example_id}")
async def get_example(
    example_id: str,
    api_key: str = Depends(verify_api_key)
):
    """Get example by ID with proper error handling"""
    try:
        async with get_db_connection() as conn:
            row = await conn.fetchrow("""
                SELECT * FROM examples WHERE id = $1
            """, example_id)

            if not row:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Example {example_id} not found"
                )

            return ExampleResponse(**dict(row))

    except asyncpg.PostgresError as e:
        logger.error(f"Database error in get_example: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database operation failed"
        )
```

#### Database Transaction Pattern
```python
@router.put("/{example_id}")
async def update_example(
    example_id: str,
    request: ExampleRequest,
    api_key: str = Depends(verify_api_key)
):
    """Update example with database transaction"""
    async with get_db_connection() as conn:
        async with conn.transaction():
            # Check if exists
            exists = await conn.fetchval("""
                SELECT EXISTS(SELECT 1 FROM examples WHERE id = $1)
            """, example_id)

            if not exists:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Example {example_id} not found"
                )

            # Update record
            await conn.execute("""
                UPDATE examples
                SET name = $2, description = $3, updated_at = NOW()
                WHERE id = $1
            """, example_id, request.name, request.description)

            # Log the change
            await conn.execute("""
                INSERT INTO example_audit_log (example_id, action, details)
                VALUES ($1, 'updated', $2)
            """, example_id, f"Updated by API: {request.name}")

    return {"status": "updated", "id": example_id}
```

### How to Extend

#### 1. Create New Router File
```python
# backend/app/routers/my_feature.py
from fastapi import APIRouter, Depends
from ..security import verify_api_key

router = APIRouter(prefix="/api/v1/my-feature", tags=["my-feature"])

@router.get("/")
async def my_endpoint(api_key: str = Depends(verify_api_key)):
    return {"message": "Hello from my feature"}
```

#### 2. Register Router in Main App
```python
# backend/app/main.py
from .routers import my_feature

app.include_router(my_feature.router)
```

#### 3. Add Database Models
```python
# Add to backend/app/models/ if needed
class MyFeature(Base):
    __tablename__ = "my_features"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
```

### Testing This Component

#### Unit Test Example
```python
# backend/tests/test_routers/test_example.py
import pytest
from httpx import AsyncClient
from uuid import uuid4

@pytest.mark.asyncio
async def test_create_example(client: AsyncClient):
    """Test creating a new example"""
    response = await client.post(
        "/api/v1/example/",
        json={"name": "Test Example", "description": "Test description"},
        headers={"X-API-Key": "taylordash-dev-key"}
    )

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Example"
    assert data["status"] == "active"
    assert "id" in data

@pytest.mark.asyncio
async def test_get_example_not_found(client: AsyncClient):
    """Test getting non-existent example"""
    fake_id = str(uuid4())
    response = await client.get(
        f"/api/v1/example/{fake_id}",
        headers={"X-API-Key": "taylordash-dev-key"}
    )

    assert response.status_code == 404
    assert "not found" in response.json()["detail"]

@pytest.mark.asyncio
async def test_unauthorized_access(client: AsyncClient):
    """Test API without authentication"""
    response = await client.get("/api/v1/example/")

    assert response.status_code == 401
    assert "Missing API key" in response.json()["detail"]
```

#### Integration Test Example
```python
@pytest.mark.asyncio
async def test_example_crud_flow(client: AsyncClient, db_session):
    """Test complete CRUD flow for examples"""
    # Create
    create_response = await client.post(
        "/api/v1/example/",
        json={"name": "Integration Test", "description": "Full flow test"},
        headers={"X-API-Key": "taylordash-dev-key"}
    )
    assert create_response.status_code == 201
    example_id = create_response.json()["id"]

    # Read
    get_response = await client.get(
        f"/api/v1/example/{example_id}",
        headers={"X-API-Key": "taylordash-dev-key"}
    )
    assert get_response.status_code == 200
    assert get_response.json()["name"] == "Integration Test"

    # Update
    update_response = await client.put(
        f"/api/v1/example/{example_id}",
        json={"name": "Updated Test", "description": "Updated description"},
        headers={"X-API-Key": "taylordash-dev-key"}
    )
    assert update_response.status_code == 200

    # Verify update
    verify_response = await client.get(
        f"/api/v1/example/{example_id}",
        headers={"X-API-Key": "taylordash-dev-key"}
    )
    assert verify_response.json()["name"] == "Updated Test"
```

### Debugging Tips

#### Enable Debug Logging
```python
import logging
logging.getLogger("app.routers.example").setLevel(logging.DEBUG)

# Add debug logs in your router
logger = logging.getLogger(__name__)

@router.post("/debug")
async def debug_endpoint(api_key: str = Depends(verify_api_key)):
    logger.debug("Debug endpoint called")
    logger.info(f"API key: {api_key[:8]}...")
    return {"debug": "enabled"}
```

#### Database Query Debugging
```bash
# Enable SQL query logging in development
export PYTHONPATH="/TaylorProjects/TaylorDashv1/backend"
export LOG_LEVEL="DEBUG"

# Check database connections
docker-compose exec postgres psql -U taylordash_app -d taylordash -c "\dt"

# Monitor query performance
docker-compose exec postgres psql -U taylordash_app -d taylordash -c "
SELECT query, calls, total_time, mean_time
FROM pg_stat_statements
ORDER BY total_time DESC LIMIT 10;"
```

#### FastAPI Debug Mode
```python
# backend/app/main.py
import os

# Enable debug mode in development
DEBUG = os.getenv("DEBUG", "false").lower() == "true"

app = FastAPI(
    title="TaylorDash API",
    debug=DEBUG,
    # ... other config
)

if DEBUG:
    # Add detailed error responses
    from fastapi.middleware.cors import CORSMiddleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Only in development!
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
```

### API Usage

#### curl Examples for Testing
```bash
# Create new example
curl -X POST "http://localhost:8000/api/v1/example/" \
  -H "X-API-Key: taylordash-dev-key" \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Example", "description": "Created via curl"}'

# Get all examples
curl -X GET "http://localhost:8000/api/v1/example/" \
  -H "X-API-Key: taylordash-dev-key"

# Get specific example
curl -X GET "http://localhost:8000/api/v1/example/{EXAMPLE_ID}" \
  -H "X-API-Key: taylordash-dev-key"

# Update example
curl -X PUT "http://localhost:8000/api/v1/example/{EXAMPLE_ID}" \
  -H "X-API-Key: taylordash-dev-key" \
  -H "Content-Type: application/json" \
  -d '{"name": "Updated Example", "description": "Updated via curl"}'

# Test authentication failure
curl -X GET "http://localhost:8000/api/v1/example/" \
  -H "X-API-Key: invalid-key"
```

#### Python Client Example
```python
import httpx
import asyncio

async def test_api():
    async with httpx.AsyncClient() as client:
        # Create example
        response = await client.post(
            "http://localhost:8000/api/v1/example/",
            json={"name": "Python Client Test"},
            headers={"X-API-Key": "taylordash-dev-key"}
        )
        print(f"Create: {response.status_code} - {response.json()}")

        # List examples
        response = await client.get(
            "http://localhost:8000/api/v1/example/",
            headers={"X-API-Key": "taylordash-dev-key"}
        )
        print(f"List: {response.status_code} - {len(response.json())} items")

if __name__ == "__main__":
    asyncio.run(test_api())
```

## 🔐 Security Notes

- All `/api/v1/` endpoints require API key authentication
- Use `verify_api_key` dependency for authentication
- Always validate input with Pydantic models
- Use database transactions for multi-step operations
- Log security events and errors
- Never expose sensitive data in error messages

## 📊 Monitoring

Each router automatically includes:
- OpenTelemetry tracing with `trace_id`
- Prometheus metrics at `/metrics`
- Request/response logging
- Error tracking and alerting

## 🚀 Performance Tips

- Use `async`/`await` for all database operations
- Implement connection pooling via `get_db_connection()`
- Add database indexes for frequently queried fields
- Use pagination for large datasets
- Cache frequently accessed data
- Monitor query performance with `pg_stat_statements`