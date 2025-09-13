# Authentication API Reference

**Last Updated:** 2025-09-12
**Version:** 1.0
**Status:** Zero Breaking Changes Validated

## Base URL
```
Development: http://localhost:3000
Production: https://yourdomain.com
```

## Authentication Methods

### Bearer Token (Session-based)
```bash
Authorization: Bearer <session_token>
```
Used for user authentication and frontend interactions.

### API Key (Service-based)
```bash
X-API-Key: <api_key>
```
Used for service-to-service communication and backend integrations.

## Core Authentication Endpoints

### POST `/api/v1/auth/login`
Authenticate user and create session.

#### Request
```http
POST /api/v1/auth/login HTTP/1.1
Content-Type: application/json

{
  "username": "admin",
  "password": "admin123"
}
```

#### Response (200 OK)
```json
{
  "session_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user_id": 1,
  "username": "admin",
  "role": "admin",
  "expires_at": "2025-09-13T23:08:00Z"
}
```

#### Response (401 Unauthorized)
```json
{
  "detail": "Invalid credentials"
}
```

#### Response (422 Validation Error)
```json
{
  "detail": [
    {
      "loc": ["body", "username"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

#### Example Usage
```bash
curl -X POST http://localhost:3000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin123"
  }'
```

---

### POST `/api/v1/auth/logout`
Invalidate current session.

#### Authentication Required
Bearer token

#### Request
```http
POST /api/v1/auth/logout HTTP/1.1
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

#### Response (200 OK)
```json
{
  "message": "Logged out successfully"
}
```

#### Response (401 Unauthorized)
```json
{
  "detail": "Invalid authentication credentials"
}
```

#### Example Usage
```bash
curl -X POST http://localhost:3000/api/v1/auth/logout \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
```

---

### GET `/api/v1/auth/me`
Get current user information.

#### Authentication Required
Bearer token

#### Request
```http
GET /api/v1/auth/me HTTP/1.1
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

#### Response (200 OK)
```json
{
  "user_id": 1,
  "username": "admin",
  "role": "admin",
  "session_expires": "2025-09-13T23:08:00Z"
}
```

#### Response (401 Unauthorized)
```json
{
  "detail": "Invalid authentication credentials"
}
```

#### Example Usage
```bash
curl -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..." \
  http://localhost:3000/api/v1/auth/me
```

## User Management Endpoints (Admin Only)

### GET `/api/v1/auth/users`
List all users.

#### Authentication Required
Bearer token (admin role)

#### Request
```http
GET /api/v1/auth/users HTTP/1.1
Authorization: Bearer <admin_token>
```

#### Response (200 OK)
```json
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

#### Response (403 Forbidden)
```json
{
  "detail": "Admin access required"
}
```

#### Example Usage
```bash
curl -H "Authorization: Bearer <admin_token>" \
  http://localhost:3000/api/v1/auth/users
```

---

### POST `/api/v1/auth/users`
Create new user.

#### Authentication Required
Bearer token (admin role)

#### Request
```http
POST /api/v1/auth/users HTTP/1.1
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "username": "newuser",
  "password": "securepassword123",
  "role": "viewer"
}
```

#### Response (201 Created)
```json
{
  "id": 3,
  "username": "newuser",
  "role": "viewer",
  "created_at": "2025-09-12T15:30:00Z"
}
```

#### Response (400 Bad Request)
```json
{
  "detail": "Username already exists"
}
```

#### Response (422 Validation Error)
```json
{
  "detail": [
    {
      "loc": ["body", "password"],
      "msg": "Password must be at least 8 characters long",
      "type": "value_error.password_too_short"
    }
  ]
}
```

#### Example Usage
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

---

### PUT `/api/v1/auth/users/{user_id}`
Update user.

#### Authentication Required
Bearer token (admin role)

#### Path Parameters
- `user_id` (integer): User ID to update

#### Request
```http
PUT /api/v1/auth/users/2 HTTP/1.1
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "role": "admin"
}
```

#### Response (200 OK)
```json
{
  "id": 2,
  "username": "viewer",
  "role": "admin",
  "created_at": "2025-09-12T11:00:00Z",
  "updated_at": "2025-09-12T15:45:00Z"
}
```

#### Response (404 Not Found)
```json
{
  "detail": "User not found"
}
```

#### Example Usage
```bash
curl -X PUT http://localhost:3000/api/v1/auth/users/2 \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "role": "admin"
  }'
```

---

### DELETE `/api/v1/auth/users/{user_id}`
Delete user.

#### Authentication Required
Bearer token (admin role)

#### Path Parameters
- `user_id` (integer): User ID to delete

#### Request
```http
DELETE /api/v1/auth/users/2 HTTP/1.1
Authorization: Bearer <admin_token>
```

#### Response (200 OK)
```json
{
  "message": "User deleted successfully"
}
```

#### Response (404 Not Found)
```json
{
  "detail": "User not found"
}
```

#### Response (400 Bad Request)
```json
{
  "detail": "Cannot delete the last admin user"
}
```

#### Example Usage
```bash
curl -X DELETE http://localhost:3000/api/v1/auth/users/2 \
  -H "Authorization: Bearer <admin_token>"
```

## Session Management Endpoints

### DELETE `/api/v1/auth/sessions/cleanup`
Clean expired sessions.

#### Authentication Required
API key

#### Request
```http
DELETE /api/v1/auth/sessions/cleanup HTTP/1.1
X-API-Key: taylordash-dev-key
```

#### Response (200 OK)
```json
{
  "cleaned_sessions": 5,
  "timestamp": "2025-09-12T16:00:00Z"
}
```

#### Example Usage
```bash
curl -X DELETE http://localhost:3000/api/v1/auth/sessions/cleanup \
  -H "X-API-Key: taylordash-dev-key"
```

## Error Responses

### Standard Error Format
All error responses follow FastAPI's standard format:

```json
{
  "detail": "Error message or validation details"
}
```

### HTTP Status Codes
- `200` - Success
- `201` - Created
- `400` - Bad Request (business logic error)
- `401` - Unauthorized (authentication required)
- `403` - Forbidden (insufficient permissions)
- `404` - Not Found
- `422` - Validation Error (input validation failed)
- `500` - Internal Server Error

### Validation Error Details
```json
{
  "detail": [
    {
      "loc": ["body", "field_name"],
      "msg": "Error description",
      "type": "error_type"
    }
  ]
}
```

## Request/Response Schemas

### LoginRequest
```json
{
  "username": "string (required, 3-255 chars)",
  "password": "string (required, 8+ chars)"
}
```

### LoginResponse
```json
{
  "session_token": "string",
  "user_id": "integer",
  "username": "string",
  "role": "string",
  "expires_at": "datetime (ISO 8601)"
}
```

### UserCreate
```json
{
  "username": "string (required, 3-255 chars, unique)",
  "password": "string (required, 8+ chars)",
  "role": "string (enum: admin, viewer)"
}
```

### UserUpdate
```json
{
  "username": "string (optional, 3-255 chars, unique)",
  "password": "string (optional, 8+ chars)",
  "role": "string (optional, enum: admin, viewer)"
}
```

### UserResponse
```json
{
  "id": "integer",
  "username": "string",
  "role": "string",
  "created_at": "datetime (ISO 8601)",
  "updated_at": "datetime (ISO 8601, optional)"
}
```

## Client Examples

### JavaScript/Fetch
```javascript
class TaylorDashAuth {
  constructor(baseURL) {
    this.baseURL = baseURL;
    this.token = localStorage.getItem('session_token');
  }

  async login(username, password) {
    const response = await fetch(`${this.baseURL}/api/v1/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ username, password }),
    });

    if (response.ok) {
      const data = await response.json();
      this.token = data.session_token;
      localStorage.setItem('session_token', this.token);
      return data;
    } else {
      const error = await response.json();
      throw new Error(error.detail);
    }
  }

  async logout() {
    const response = await fetch(`${this.baseURL}/api/v1/auth/logout`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.token}`,
      },
    });

    if (response.ok) {
      this.token = null;
      localStorage.removeItem('session_token');
    }
  }

  async getCurrentUser() {
    const response = await fetch(`${this.baseURL}/api/v1/auth/me`, {
      headers: {
        'Authorization': `Bearer ${this.token}`,
      },
    });

    if (response.ok) {
      return response.json();
    } else if (response.status === 401) {
      this.token = null;
      localStorage.removeItem('session_token');
      throw new Error('Session expired');
    }
  }
}
```

### Python/Requests
```python
import requests
from typing import Optional, Dict, Any

class TaylorDashAuth:
    def __init__(self, base_url: str, api_key: Optional[str] = None):
        self.base_url = base_url
        self.api_key = api_key
        self.session_token: Optional[str] = None

    def login(self, username: str, password: str) -> Dict[str, Any]:
        response = requests.post(
            f"{self.base_url}/api/v1/auth/login",
            json={"username": username, "password": password}
        )
        response.raise_for_status()

        data = response.json()
        self.session_token = data['session_token']
        return data

    def logout(self):
        if not self.session_token:
            return

        response = requests.post(
            f"{self.base_url}/api/v1/auth/logout",
            headers={"Authorization": f"Bearer {self.session_token}"}
        )
        response.raise_for_status()
        self.session_token = None

    def get_current_user(self) -> Dict[str, Any]:
        response = requests.get(
            f"{self.base_url}/api/v1/auth/me",
            headers={"Authorization": f"Bearer {self.session_token}"}
        )
        response.raise_for_status()
        return response.json()

    def api_call(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """Make API call with appropriate authentication"""
        headers = kwargs.pop('headers', {})

        if self.session_token:
            headers['Authorization'] = f"Bearer {self.session_token}"
        elif self.api_key:
            headers['X-API-Key'] = self.api_key

        return requests.request(
            method,
            f"{self.base_url}{endpoint}",
            headers=headers,
            **kwargs
        )
```

### cURL Examples
```bash
# Login and store token
TOKEN=$(curl -s -X POST http://localhost:3000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' | \
  jq -r '.session_token')

# Use token for API calls
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:3000/api/v1/auth/me

# Create user (admin only)
curl -X POST http://localhost:3000/api/v1/auth/users \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "testpass123",
    "role": "viewer"
  }'
```

## Rate Limiting

### Default Limits
- Login attempts: 5 per minute per IP
- User creation: 10 per hour per admin user
- General API calls: 1000 per hour per token/key

### Rate Limit Headers
```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1694553600
```

### Rate Limit Exceeded Response (429)
```json
{
  "detail": "Rate limit exceeded. Try again in 60 seconds."
}
```

## OpenAPI Specification

The complete OpenAPI specification is available at:
- Development: `http://localhost:3000/docs`
- OpenAPI JSON: `http://localhost:3000/openapi.json`

### Interactive Documentation
Visit `/docs` for Swagger UI with interactive API testing capabilities.