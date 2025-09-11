# TaylorDash Projects API

This document describes the implementation of the Projects API with RBAC integration for the TaylorDash backend.

## Overview

The Projects API provides CRUD operations for project management with Role-Based Access Control (RBAC) using Keycloak OIDC JWT authentication.

## Authentication & Authorization

### Authentication
- Uses Keycloak OIDC JWT tokens
- Tokens must be provided in the `Authorization: Bearer <token>` header
- JWT verification includes issuer validation against the configured Keycloak realm

### RBAC Roles
- **viewer**: Can read projects (GET operations)
- **maintainer**: Can read and create projects (GET, POST operations)  
- **admin**: Can read, create, update, and delete projects (all operations)

Role hierarchy: `admin` > `maintainer` > `viewer`

## API Endpoints

### GET /api/v1/projects
List projects with optional filtering and pagination.

**Required Role**: `viewer` or higher

**Query Parameters**:
- `status` (optional): Filter by project status (`new`, `active`, `completed`, `archived`)
- `limit` (optional): Maximum number of projects to return (1-1000, default: 50)
- `offset` (optional): Number of projects to skip for pagination (default: 0)

**Response**: 
```json
{
  "projects": [
    {
      "id": "uuid",
      "name": "Project Name",
      "description": "Project description",
      "status": "new",
      "owner_id": "uuid",
      "metadata": {},
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 1
}
```

### POST /api/v1/projects
Create a new project.

**Required Role**: `maintainer` or higher

**Request Body**:
```json
{
  "name": "Project Name",
  "description": "Optional description",
  "status": "new",
  "metadata": {}
}
```

**Response** (201 Created):
```json
{
  "id": "uuid",
  "name": "Project Name", 
  "description": "Optional description",
  "status": "new",
  "owner_id": "uuid",
  "metadata": {},
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

### GET /api/v1/projects/{project_id}
Get a specific project by ID.

**Required Role**: `viewer` or higher

**Response**: Project object or 404 if not found

### PUT /api/v1/projects/{project_id}
Update an existing project.

**Required Role**: `maintainer` or higher

**Request Body**: Partial project object (all fields optional)

### DELETE /api/v1/projects/{project_id}
Delete a project and all associated data.

**Required Role**: `maintainer` or higher

**Response**: 204 No Content on success

## Database Schema

The projects table:
```sql
CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(50) DEFAULT 'new',
    owner_id UUID,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

## Configuration

### Environment Variables
- `KEYCLOAK_URL`: Keycloak server URL (default: http://keycloak:8080)
- `KEYCLOAK_REALM`: Keycloak realm name (default: taylordash)
- `KEYCLOAK_CLIENT_ID`: Client ID for API access (default: taylordash-api)
- `SKIP_JWT_VERIFICATION`: Skip JWT signature verification for development (default: false)

### Development Setup
For development/testing, you can skip JWT verification:
```bash
export SKIP_JWT_VERIFICATION=true
```

## Error Handling

The API returns standard HTTP status codes:
- `200`: Success
- `201`: Created
- `400`: Bad Request (validation errors)
- `401`: Unauthorized (missing/invalid JWT)
- `403`: Forbidden (insufficient permissions)
- `404`: Not Found
- `409`: Conflict (duplicate resource)
- `500`: Internal Server Error

Error responses follow this format:
```json
{
  "detail": "Error message"
}
```

## Testing

Use the provided test script to verify the implementation:
```bash
# With JWT verification disabled (development)
export SKIP_JWT_VERIFICATION=true
python3 test_projects_api.py

# With actual JWT token
export TEST_JWT_TOKEN="your-jwt-token"
python3 test_projects_api.py
```

## Implementation Files

- `app/auth.py`: Authentication and RBAC middleware
- `app/models.py`: Pydantic models for data validation
- `app/routers/projects.py`: Projects API router
- `app/database.py`: Database schema and migrations (updated)
- `app/main.py`: FastAPI application with router integration

## OpenAPI Documentation

Interactive API documentation is available at:
- Swagger UI: `/docs`
- ReDoc: `/redoc`
- OpenAPI JSON: `/openapi.json`

The documentation includes authentication requirements and role-based access information for each endpoint.