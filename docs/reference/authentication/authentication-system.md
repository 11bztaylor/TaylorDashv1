# Authentication System Reference

**Last Updated:** 2025-09-12
**Version:** 1.0
**Status:** Production Ready (Zero breaking changes)

## Overview

TaylorDash implements a dual-authentication system supporting both session-based user authentication and API key service authentication, maintaining backward compatibility while providing enhanced security.

## Authentication Methods

### 1. Session-Based Authentication (JWT)
For user interactions and frontend applications.

#### Login Process
```bash
# User login
curl -X POST http://localhost:3000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin123"
  }'

# Response
{
  "session_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user_id": 1,
  "username": "admin",
  "role": "admin",
  "expires_at": "2025-09-13T23:08:00Z"
}
```

#### Using Session Tokens
```bash
# API calls with session token
curl -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..." \
  http://localhost:3000/api/v1/auth/me

# Expected response
{
  "user_id": 1,
  "username": "admin",
  "role": "admin",
  "session_expires": "2025-09-13T23:08:00Z"
}
```

### 2. API Key Authentication
For service-to-service communication and integrations.

```bash
# API calls with API key
curl -H "X-API-Key: taylordash-dev-key" \
  http://localhost:3000/api/v1/projects

# All core API endpoints support API key authentication
```

## User Management

### User Roles
- **Admin** - Full system access, user management, MCP operations
- **Viewer** - Read-only access to projects and data

### User Operations

#### Create User (Admin Only)
```bash
curl -X POST http://localhost:3000/api/v1/auth/users \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "newuser",
    "password": "securepassword123",
    "role": "viewer"
  }'
```

#### List Users (Admin Only)
```bash
curl -H "Authorization: Bearer <admin_token>" \
  http://localhost:3000/api/v1/auth/users

# Response
[
  {
    "id": 1,
    "username": "admin",
    "role": "admin",
    "created_at": "2025-09-12T10:00:00Z"
  },
  {
    "id": 2,
    "username": "viewer",
    "role": "viewer",
    "created_at": "2025-09-12T11:00:00Z"
  }
]
```

#### Update User (Admin Only)
```bash
curl -X PUT http://localhost:3000/api/v1/auth/users/2 \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "role": "admin"
  }'
```

#### Delete User (Admin Only)
```bash
curl -X DELETE http://localhost:3000/api/v1/auth/users/2 \
  -H "Authorization: Bearer <admin_token>"
```

## Session Management

### Session Lifecycle
```bash
# Check current session
curl -H "Authorization: Bearer <token>" \
  http://localhost:3000/api/v1/auth/me

# Logout (invalidate session)
curl -X POST http://localhost:3000/api/v1/auth/logout \
  -H "Authorization: Bearer <token>"

# Clean expired sessions (API key required)
curl -X DELETE http://localhost:3000/api/v1/auth/sessions/cleanup \
  -H "X-API-Key: taylordash-dev-key"
```

### Session Configuration
- **Default Expiration:** 8 hours (configurable)
- **Token Length:** 32 bytes (URL-safe base64)
- **Storage:** Database-backed for proper invalidation
- **Security:** Cryptographically secure random generation

## Security Features

### Password Security
- **Hashing Algorithm:** bcrypt with 12 rounds
- **Salt:** Unique per password
- **Complexity:** Minimum 8 characters (configurable)
- **Storage:** Never stored in plaintext

### Token Security
- **Generation:** Cryptographically secure random (32 bytes)
- **Encoding:** URL-safe base64
- **Transmission:** HTTPS only in production
- **Storage:** Database with expiration tracking
- **Validation:** Constant-time comparison

### Access Control
```python
# Role-based endpoint protection example
@router.get("/admin-only")
async def admin_endpoint(current_user: User = Depends(get_admin_user)):
    # Only admin users can access
    pass

@router.get("/authenticated")
async def auth_endpoint(current_user: User = Depends(get_current_user)):
    # Any authenticated user can access
    pass
```

## API Endpoints

### Authentication Endpoints

#### POST `/api/v1/auth/login`
**Purpose:** Authenticate user and create session

**Request:**
```json
{
  "username": "string",
  "password": "string"
}
```

**Response (200):**
```json
{
  "session_token": "string",
  "user_id": "integer",
  "username": "string",
  "role": "string",
  "expires_at": "datetime"
}
```

**Response (401):**
```json
{
  "detail": "Invalid credentials"
}
```

#### POST `/api/v1/auth/logout`
**Purpose:** Invalidate current session
**Authentication:** Bearer token required

**Response (200):**
```json
{
  "message": "Logged out successfully"
}
```

#### GET `/api/v1/auth/me`
**Purpose:** Get current user information
**Authentication:** Bearer token required

**Response (200):**
```json
{
  "user_id": "integer",
  "username": "string",
  "role": "string",
  "session_expires": "datetime"
}
```

### User Management Endpoints (Admin Only)

#### GET `/api/v1/auth/users`
**Purpose:** List all users
**Authentication:** Bearer token (admin role)

**Response (200):**
```json
[
  {
    "id": "integer",
    "username": "string",
    "role": "string",
    "created_at": "datetime"
  }
]
```

#### POST `/api/v1/auth/users`
**Purpose:** Create new user
**Authentication:** Bearer token (admin role)

**Request:**
```json
{
  "username": "string",
  "password": "string",
  "role": "admin|viewer"
}
```

#### PUT `/api/v1/auth/users/{user_id}`
**Purpose:** Update user
**Authentication:** Bearer token (admin role)

**Request:**
```json
{
  "username": "string (optional)",
  "password": "string (optional)",
  "role": "admin|viewer (optional)"
}
```

#### DELETE `/api/v1/auth/users/{user_id}`
**Purpose:** Delete user
**Authentication:** Bearer token (admin role)

### Session Management Endpoints

#### DELETE `/api/v1/auth/sessions/cleanup`
**Purpose:** Clean expired sessions
**Authentication:** API key required

**Response (200):**
```json
{
  "cleaned_sessions": "integer",
  "timestamp": "datetime"
}
```

## Integration Examples

### Frontend Authentication
```javascript
// Login function
async function login(username, password) {
  const response = await fetch('/api/v1/auth/login', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ username, password }),
  });

  if (response.ok) {
    const data = await response.json();
    localStorage.setItem('session_token', data.session_token);
    return data;
  } else {
    throw new Error('Login failed');
  }
}

// API call with token
async function apiCall(endpoint) {
  const token = localStorage.getItem('session_token');
  const response = await fetch(endpoint, {
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  });

  if (response.status === 401) {
    // Token expired, redirect to login
    window.location.href = '/login';
    return;
  }

  return response.json();
}
```

### Backend Service Integration
```python
# Using API key for service calls
import requests

class TaylorDashClient:
    def __init__(self, base_url, api_key):
        self.base_url = base_url
        self.api_key = api_key

    def get_projects(self):
        response = requests.get(
            f"{self.base_url}/api/v1/projects",
            headers={"X-API-Key": self.api_key}
        )
        response.raise_for_status()
        return response.json()

# Usage
client = TaylorDashClient("http://localhost:3000", "taylordash-dev-key")
projects = client.get_projects()
```

## Configuration

### Environment Variables
```bash
# Authentication configuration
JWT_SECRET_KEY=your-secret-key-here
API_KEY=your-api-key-here
SESSION_EXPIRE_HOURS=8

# Password security
PASSWORD_MIN_LENGTH=8
BCRYPT_ROUNDS=12

# Session security
SESSION_TOKEN_LENGTH=32
SESSION_CLEANUP_INTERVAL=3600
```

### Database Schema
```sql
-- Users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'viewer',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Sessions table
CREATE TABLE sessions (
    id SERIAL PRIMARY KEY,
    token VARCHAR(255) UNIQUE NOT NULL,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_sessions_token ON sessions(token);
CREATE INDEX idx_sessions_expires_at ON sessions(expires_at);
CREATE INDEX idx_sessions_user_id ON sessions(user_id);
```

## Security Considerations

### Best Practices
- **HTTPS Only:** Always use HTTPS in production
- **Token Storage:** Store tokens securely (avoid localStorage for sensitive apps)
- **Session Timeout:** Implement appropriate session timeouts
- **Rate Limiting:** Implement login attempt rate limiting
- **Input Validation:** Validate all authentication inputs
- **Error Messages:** Use generic error messages to prevent enumeration

### Security Headers
```python
# FastAPI security headers
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Security headers middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response
```

## Troubleshooting

### Common Issues

#### Authentication Failures
```bash
# Test authentication endpoint
curl -v -X POST http://localhost:3000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# Check user exists
docker-compose exec postgres psql -U taylordash -d taylordash \
  -c "SELECT username, role FROM users WHERE username = 'admin';"
```

#### Token Validation Issues
```bash
# Test token validation
TOKEN="your-session-token-here"
curl -v -H "Authorization: Bearer $TOKEN" \
  http://localhost:3000/api/v1/auth/me

# Check session in database
docker-compose exec postgres psql -U taylordash -d taylordash \
  -c "SELECT token, expires_at FROM sessions WHERE token = '$TOKEN';"
```

#### Database Connection Issues
```bash
# Test database connectivity
docker-compose exec backend python -c "
from app.database import SessionLocal
try:
    db = SessionLocal()
    print('Database connection successful')
    db.close()
except Exception as e:
    print(f'Database connection failed: {e}')
"
```

### Debug Mode
```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
docker-compose restart backend

# Check authentication logs
docker-compose logs backend | grep -i auth
```

## Performance Considerations

### Optimization Tips
- **Connection Pooling:** Use database connection pooling
- **Session Cleanup:** Regular cleanup of expired sessions
- **Token Caching:** Consider Redis for session storage in high-load scenarios
- **Query Optimization:** Index session and user lookup queries
- **Rate Limiting:** Implement authentication rate limiting

### Monitoring
```bash
# Monitor authentication metrics
curl -s http://localhost:3000/metrics | grep -E "(auth|session|login)"

# Database performance
docker-compose exec postgres psql -U taylordash -d taylordash -c "
SELECT query, mean_time, calls FROM pg_stat_statements
WHERE query LIKE '%sessions%' OR query LIKE '%users%'
ORDER BY mean_time DESC LIMIT 5;
"
```