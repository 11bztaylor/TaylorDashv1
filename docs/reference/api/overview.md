# TaylorDash API Documentation

## Overview

The TaylorDash API is a RESTful web service built with FastAPI that provides comprehensive project management, authentication, plugin management, and observability features. The API follows OpenAPI 3.1 specification and includes automatic interactive documentation.

## API Status & Performance

**Current Production Metrics:**
- ✅ Sub-second response times across all endpoints
- ✅ 100% security score with comprehensive audit logging
- ✅ JWT-based authentication with session management
- ✅ Plugin security framework operational
- ✅ Real-time MQTT event processing
- ✅ Comprehensive structured logging and metrics

## Base Information

- **Base URL**: `https://taylordash.local/api/v1`
- **API Version**: 1.0.0
- **Protocol**: HTTPS only
- **Format**: JSON
- **Documentation**: Available at `/docs` (Swagger UI) and `/redoc`

## Authentication

### Security Model
TaylorDash uses a dual authentication system:
1. **Session-based Authentication**: For user interactions (JWT-style tokens)
2. **API Key Authentication**: For service-to-service communication

### Authentication Methods

#### 1. Session Authentication (Users)
```http
Authorization: Bearer <session_token>
```

**Token Characteristics:**
- Generated during login
- 24-hour expiration (default) or 30 days (remember me)
- Automatic activity tracking
- Secure session management with audit trail

#### 2. API Key Authentication (Services)
```http
X-API-Key: <api_key>
```

**Key Characteristics:**
- Long-lived service credentials
- Used for system operations and monitoring
- Required for health checks and metrics endpoints

### User Roles & Permissions

#### Admin Role
- **Full System Access**: All API endpoints
- **User Management**: Create, update, delete users
- **System Configuration**: Plugin management, system settings
- **Monitoring**: Access to logs, metrics, health endpoints

#### Viewer Role
- **Read-Only Access**: Project data, public endpoints
- **Limited UI**: Configurable single-view mode for tablets
- **No Administrative Functions**: Cannot modify users or system settings

## API Endpoints Overview

### Core Endpoints

| Category | Endpoint | Purpose |
|----------|----------|---------|
| **Authentication** | `/api/v1/auth/*` | User authentication and session management |
| **Projects** | `/api/v1/projects/*` | Project CRUD operations and hierarchy |
| **Events** | `/api/v1/events/*` | Event sourcing and MQTT integration |
| **Plugins** | `/api/v1/plugins/*` | Plugin management and security |
| **MCP** | `/api/v1/mcp/*` | Model Context Protocol integration |
| **Monitoring** | `/api/v1/logs/*`, `/metrics` | Observability and system health |
| **Health** | `/health/*` | Service health checks |

## Request/Response Format

### Standard Response Structure
```json
{
  "data": { /* Response payload */ },
  "meta": {
    "timestamp": "2025-01-15T10:30:00Z",
    "request_id": "uuid-v4",
    "version": "1.0.0"
  }
}
```

### Error Response Structure
```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": { /* Additional context */ },
    "timestamp": "2025-01-15T10:30:00Z",
    "request_id": "uuid-v4"
  }
}
```

### HTTP Status Codes

| Code | Meaning | Usage |
|------|---------|-------|
| `200` | OK | Successful GET, PUT, DELETE |
| `201` | Created | Successful POST |
| `204` | No Content | Successful DELETE with no response body |
| `400` | Bad Request | Invalid request parameters |
| `401` | Unauthorized | Authentication required |
| `403` | Forbidden | Insufficient permissions |
| `404` | Not Found | Resource not found |
| `409` | Conflict | Resource already exists |
| `422` | Unprocessable Entity | Validation error |
| `500` | Internal Server Error | Server error |
| `503` | Service Unavailable | Service temporarily unavailable |

## Common Headers

### Request Headers
```http
Content-Type: application/json
Authorization: Bearer <session_token>
X-API-Key: <api_key>  # For service endpoints
User-Agent: TaylorDash-Client/1.0.0
```

### Response Headers
```http
Content-Type: application/json
X-Request-ID: uuid-v4
X-Response-Time: 150ms
X-Rate-Limit-Remaining: 99
Cache-Control: no-cache, private
```

## Data Types & Formats

### Standard Types
- **UUID**: RFC 4122 v4 format (`550e8400-e29b-41d4-a716-446655440000`)
- **Timestamps**: ISO 8601 format (`2025-01-15T10:30:00Z`)
- **Metadata**: JSONB objects for flexible data storage

### Common Objects

#### Project Object
```json
{
  "id": "uuid",
  "name": "string",
  "description": "string",
  "status": "string",
  "owner_id": "uuid",
  "metadata": {},
  "created_at": "timestamp",
  "updated_at": "timestamp"
}
```

#### User Object
```json
{
  "id": "uuid",
  "username": "string",
  "role": "admin|viewer",
  "default_view": "string",
  "single_view_mode": boolean,
  "created_at": "timestamp",
  "last_login": "timestamp",
  "is_active": boolean
}
```

#### Plugin Object
```json
{
  "id": "string",
  "name": "string",
  "version": "string",
  "description": "string",
  "author": "string",
  "type": "ui|data|integration|system",
  "status": "pending|installing|installed|failed|updating|uninstalling",
  "repository_url": "string",
  "permissions": ["array"],
  "security_score": integer,
  "installed_at": "timestamp"
}
```

## Rate Limiting

### Current Limits
- **Default**: 100 requests per minute per client
- **Authentication**: 10 login attempts per minute per IP
- **Heavy Operations**: 5 requests per minute for plugin operations

### Rate Limit Headers
```http
X-Rate-Limit-Limit: 100
X-Rate-Limit-Remaining: 95
X-Rate-Limit-Reset: 1642247400
```

## Pagination

For endpoints returning lists, use these parameters:

### Query Parameters
- `limit`: Number of items per page (default: 50, max: 100)
- `offset`: Number of items to skip (default: 0)

### Response Format
```json
{
  "data": [/* items */],
  "pagination": {
    "limit": 50,
    "offset": 0,
    "total": 150,
    "has_more": true,
    "next_offset": 50
  }
}
```

## Filtering & Searching

### Common Filter Parameters
- `status`: Filter by status field
- `type`: Filter by type field
- `created_after`: ISO 8601 timestamp
- `created_before`: ISO 8601 timestamp
- `search`: Full-text search in relevant fields

### Example
```http
GET /api/v1/projects?status=active&created_after=2025-01-01T00:00:00Z&limit=25
```

## WebSocket & Real-time Features

### Event Streaming
- **WebSocket Endpoint**: `wss://taylordash.local/ws/events`
- **Authentication**: Session token in query parameter
- **Topics**: Subscribe to specific event types

### MQTT Integration
- **Internal Topics**: `tracker/events/*`
- **Real-time Updates**: Project, component, task changes
- **Event Correlation**: Trace IDs for request correlation

## Error Handling

### Validation Errors
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed",
    "details": {
      "field_errors": [
        {
          "field": "name",
          "message": "Field is required",
          "code": "required"
        }
      ]
    }
  }
}
```

### Authentication Errors
```json
{
  "error": {
    "code": "AUTHENTICATION_REQUIRED",
    "message": "Valid authentication credentials required",
    "details": {
      "auth_type": "bearer_token",
      "hint": "Include Authorization: Bearer <token> header"
    }
  }
}
```

## Security Considerations

### HTTPS Only
- All API communication must use HTTPS
- HTTP requests are automatically redirected to HTTPS
- HSTS headers enforce secure connections

### CORS Policy
- Restricted origins for production
- Credentials allowed for authenticated requests
- Preflight requests supported

### Security Headers
```http
Strict-Transport-Security: max-age=31536000; includeSubDomains
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Content-Security-Policy: default-src 'self'
```

### Input Validation
- All inputs validated with Pydantic schemas
- SQL injection prevention with parameterized queries
- XSS protection with output encoding

## Performance & Caching

### Response Times
- **Health Checks**: < 10ms
- **Simple Queries**: < 100ms
- **Complex Operations**: < 500ms
- **Plugin Operations**: < 2s

### Caching Strategy
- **Static Content**: Long-term caching with versioning
- **API Responses**: No-cache for dynamic content
- **Database**: Connection pooling for optimal performance

### Database Optimization
- **Connection Pool**: 5-20 connections
- **Indexes**: Comprehensive indexing for performance
- **Query Optimization**: Optimized queries for common operations

## OpenAPI Specification

### Generated Documentation
- **Swagger UI**: Available at `/docs`
- **ReDoc**: Available at `/redoc`
- **OpenAPI JSON**: Available at `/openapi.json`

### Schema Generation
- Automatic schema generation from Pydantic models
- Request/response examples included
- Parameter validation rules documented

## Monitoring & Observability

### Metrics Endpoint
```http
GET /metrics
```
Returns Prometheus-compatible metrics for monitoring.

### Health Endpoints
```http
GET /health/live    # Liveness probe
GET /health/ready   # Readiness probe
```

### Structured Logging
- All requests logged with correlation IDs
- Performance metrics included
- Error tracking with stack traces
- Audit trail for security events

## API Versioning

### Current Strategy
- URL-based versioning (`/api/v1/`)
- Backward compatibility maintained
- Deprecation warnings in headers

### Future Versions
- New versions will be additive
- Breaking changes will increment major version
- Sunset schedule communicated in advance

This API documentation provides the foundation for understanding and integrating with the TaylorDash system. For detailed endpoint documentation, see the specific API reference sections.