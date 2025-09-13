# Authentication API Reference

## Overview

The TaylorDash Authentication API provides secure user authentication and session management with comprehensive audit logging. The system supports a two-tier role model (admin/viewer) with session-based authentication and automatic security monitoring.

## Authentication Flow

```mermaid
sequenceDiagram
    participant Client
    participant API
    participant Database
    participant AuditLog

    Client->>API: POST /api/v1/auth/login
    API->>Database: Validate credentials
    Database-->>API: User data
    API->>Database: Create session
    API->>AuditLog: Log login success
    API-->>Client: Session token + user info

    Note over Client: Store token securely

    Client->>API: GET /api/v1/projects (with token)
    API->>Database: Validate session
    API->>Database: Update last activity
    API-->>Client: Project data
```

## Endpoints

### POST /api/v1/auth/login

Authenticate user credentials and create a new session.

#### Request

```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "username": "string",
  "password": "string",
  "remember_me": false,
  "single_view_mode": false,
  "default_view": "dashboard"
}
```

#### Request Schema

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `username` | string | ✓ | User login name |
| `password` | string | ✓ | User password |
| `remember_me` | boolean |  | Extend session to 30 days (default: false) |
| `single_view_mode` | boolean |  | Enable tablet mode for viewers (default: false) |
| `default_view` | string |  | Default view for viewer users |

#### Response

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "username": "john.doe",
  "role": "admin",
  "session_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expires_at": "2025-01-16T10:30:00Z",
  "single_view_mode": false,
  "default_view": null
}
```

#### Response Schema

| Field | Type | Description |
|-------|------|-------------|
| `user_id` | uuid | Unique user identifier |
| `username` | string | User login name |
| `role` | string | User role (`admin` or `viewer`) |
| `session_token` | string | Authentication token for subsequent requests |
| `expires_at` | timestamp | Token expiration time |
| `single_view_mode` | boolean | Whether single view mode is enabled |
| `default_view` | string | Default view for viewer users |

#### Session Duration

- **Standard Login**: 24 hours
- **Remember Me**: 30 days
- **Automatic Extension**: Activity-based renewal

#### Error Responses

```http
HTTP/1.1 401 Unauthorized
Content-Type: application/json

{
  "detail": "Invalid username or password"
}
```

#### Security Features

- **Password Hashing**: Bcrypt with salt
- **Audit Logging**: All login attempts logged
- **IP Tracking**: Source IP recorded for security
- **Failed Attempt Logging**: Detailed failure tracking

#### Example Usage

```bash
curl -X POST "https://taylordash.local/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin123",
    "remember_me": true
  }'
```

### POST /api/v1/auth/logout

Terminate the current user session.

#### Request

```http
POST /api/v1/auth/logout
Authorization: Bearer <session_token>
```

#### Response

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "message": "Logged out successfully"
}
```

#### Security Features

- **Session Deactivation**: Token immediately invalidated
- **Audit Logging**: Logout event recorded
- **Graceful Handling**: No error if session already expired

#### Example Usage

```bash
curl -X POST "https://taylordash.local/api/v1/auth/logout" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### GET /api/v1/auth/me

Get current authenticated user information.

#### Request

```http
GET /api/v1/auth/me
Authorization: Bearer <session_token>
```

#### Response

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "username": "john.doe",
  "role": "admin",
  "default_view": null,
  "single_view_mode": false,
  "created_at": "2025-01-01T00:00:00Z",
  "last_login": "2025-01-15T10:30:00Z",
  "is_active": true
}
```

#### Response Schema

| Field | Type | Description |
|-------|------|-------------|
| `id` | uuid | User identifier |
| `username` | string | User login name |
| `role` | string | User role (`admin` or `viewer`) |
| `default_view` | string | Default view for viewer users |
| `single_view_mode` | boolean | Tablet mode setting |
| `created_at` | timestamp | Account creation time |
| `last_login` | timestamp | Last successful login |
| `is_active` | boolean | Account status |

### User Management (Admin Only)

### POST /api/v1/auth/users

Create a new user account (admin only).

#### Request

```http
POST /api/v1/auth/users
Authorization: Bearer <admin_session_token>
Content-Type: application/json

{
  "username": "new.user",
  "password": "secure_password",
  "role": "viewer",
  "default_view": "dashboard",
  "single_view_mode": true
}
```

#### Request Schema

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `username` | string | ✓ | Unique username |
| `password` | string | ✓ | User password (will be hashed) |
| `role` | string | ✓ | User role (`admin` or `viewer`) |
| `default_view` | string |  | Default view for viewers |
| `single_view_mode` | boolean |  | Enable tablet mode |

#### Response

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "id": "new-user-uuid",
  "username": "new.user",
  "role": "viewer",
  "default_view": "dashboard",
  "single_view_mode": true,
  "created_at": "2025-01-15T10:30:00Z",
  "last_login": null,
  "is_active": true
}
```

#### Error Responses

```http
HTTP/1.1 409 Conflict
Content-Type: application/json

{
  "detail": "Username already exists"
}
```

### GET /api/v1/auth/users

List all users (admin only).

#### Request

```http
GET /api/v1/auth/users
Authorization: Bearer <admin_session_token>
```

#### Response

```http
HTTP/1.1 200 OK
Content-Type: application/json

[
  {
    "id": "user-1-uuid",
    "username": "admin",
    "role": "admin",
    "default_view": null,
    "single_view_mode": false,
    "created_at": "2025-01-01T00:00:00Z",
    "last_login": "2025-01-15T10:30:00Z",
    "is_active": true
  },
  {
    "id": "user-2-uuid",
    "username": "viewer",
    "role": "viewer",
    "default_view": "dashboard",
    "single_view_mode": true,
    "created_at": "2025-01-05T00:00:00Z",
    "last_login": "2025-01-14T15:20:00Z",
    "is_active": true
  }
]
```

### PUT /api/v1/auth/users/{user_id}

Update user account (admin only).

#### Request

```http
PUT /api/v1/auth/users/550e8400-e29b-41d4-a716-446655440000
Authorization: Bearer <admin_session_token>
Content-Type: application/json

{
  "role": "admin",
  "is_active": true,
  "password": "new_password"
}
```

#### Request Schema

| Field | Type | Description |
|-------|------|-------------|
| `role` | string | Update user role |
| `default_view` | string | Update default view |
| `single_view_mode` | boolean | Update tablet mode setting |
| `is_active` | boolean | Enable/disable account |
| `password` | string | Update password (will be hashed) |

#### Response

Returns updated user object (same format as user creation).

### DELETE /api/v1/auth/users/{user_id}

Delete user account (admin only).

#### Request

```http
DELETE /api/v1/auth/users/550e8400-e29b-41d4-a716-446655440000
Authorization: Bearer <admin_session_token>
```

#### Response

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "message": "User john.doe deleted successfully"
}
```

#### Security Features

- **Self-Deletion Prevention**: Admin cannot delete their own account
- **Cascade Deletion**: User sessions automatically removed
- **Audit Logging**: Deletion event recorded with details

### Session Management

### DELETE /api/v1/auth/sessions/cleanup

Clean up expired sessions (API key required).

#### Request

```http
DELETE /api/v1/auth/sessions/cleanup
X-API-Key: <api_key>
```

#### Response

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "message": "Cleaned up 5 expired sessions"
}
```

#### Usage

- **Automated Cleanup**: Called by cron job
- **Performance**: Maintains session table efficiency
- **Security**: Removes stale session tokens

## Authentication Middleware

### Session Validation

All protected endpoints automatically validate session tokens:

1. **Extract Token**: From `Authorization: Bearer <token>` header
2. **Validate Session**: Check token exists and not expired
3. **Update Activity**: Record last activity timestamp
4. **Inject User**: Add user context to request

### Role-Based Access Control

```python
# Admin required
@router.get("/admin-only")
async def admin_endpoint(user: dict = Depends(require_admin)):
    # Only accessible to admin users
    pass

# Any authenticated user
@router.get("/protected")
async def protected_endpoint(user: dict = Depends(get_current_user)):
    # Accessible to any authenticated user
    pass
```

## Security Features

### Password Security

- **Hashing**: Bcrypt with random salt
- **Validation**: Secure password comparison
- **Storage**: Never store plaintext passwords

### Session Security

- **Token Generation**: Cryptographically secure random tokens
- **Expiration**: Automatic token expiration
- **IP Tracking**: Source IP monitoring
- **User Agent**: Client identification

### Audit Trail

All authentication events are logged:

```json
{
  "user_id": "uuid",
  "event_type": "login_success",
  "event_timestamp": "2025-01-15T10:30:00Z",
  "ip_address": "192.168.1.100",
  "user_agent": "TaylorDash-Client/1.0.0",
  "details": {}
}
```

#### Event Types

- `login_success` - Successful authentication
- `login_failed` - Failed login attempt
- `logout` - User-initiated logout
- `session_expired` - Automatic session expiration
- `password_changed` - Password update
- `user_created` - New user account
- `user_updated` - User account modification
- `user_deleted` - User account deletion

### Rate Limiting

- **Login Attempts**: 10 attempts per minute per IP
- **Session Validation**: 100 requests per minute per session
- **User Management**: 10 operations per minute

### CORS & Security Headers

```http
Access-Control-Allow-Origin: https://taylordash.local
Access-Control-Allow-Credentials: true
Strict-Transport-Security: max-age=31536000
X-Content-Type-Options: nosniff
```

## Error Handling

### Common Error Codes

| HTTP Status | Error Code | Description |
|-------------|------------|-------------|
| 401 | AUTHENTICATION_REQUIRED | Valid authentication required |
| 401 | INVALID_CREDENTIALS | Username or password incorrect |
| 401 | SESSION_EXPIRED | Session token expired |
| 403 | INSUFFICIENT_PERMISSIONS | Admin access required |
| 409 | USERNAME_EXISTS | Username already taken |
| 422 | VALIDATION_ERROR | Request validation failed |

### Error Response Format

```json
{
  "detail": "Human-readable error message",
  "error_code": "MACHINE_READABLE_CODE",
  "context": {
    "field": "specific_field",
    "hint": "Resolution suggestion"
  }
}
```

## Best Practices

### Client Implementation

1. **Secure Storage**: Store tokens securely (not in localStorage)
2. **Token Refresh**: Implement automatic token refresh
3. **Error Handling**: Graceful handling of auth errors
4. **Logout**: Proper session cleanup on logout

### Security Considerations

1. **HTTPS Only**: Never send credentials over HTTP
2. **Token Expiration**: Handle token expiration gracefully
3. **Session Management**: Clean up sessions on app exit
4. **Error Logging**: Monitor authentication failures

### Integration Examples

#### JavaScript/TypeScript
```typescript
class AuthClient {
  private token: string | null = null;

  async login(username: string, password: string): Promise<LoginResponse> {
    const response = await fetch('/api/v1/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password })
    });

    if (!response.ok) {
      throw new Error('Login failed');
    }

    const data = await response.json();
    this.token = data.session_token;
    return data;
  }

  async makeAuthenticatedRequest(url: string): Promise<Response> {
    return fetch(url, {
      headers: {
        'Authorization': `Bearer ${this.token}`
      }
    });
  }
}
```

#### Python
```python
import requests
from typing import Optional

class TaylorDashClient:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session_token: Optional[str] = None

    def login(self, username: str, password: str) -> dict:
        response = requests.post(
            f"{self.base_url}/api/v1/auth/login",
            json={"username": username, "password": password}
        )
        response.raise_for_status()

        data = response.json()
        self.session_token = data["session_token"]
        return data

    def get_headers(self) -> dict:
        if not self.session_token:
            raise ValueError("Not authenticated")

        return {"Authorization": f"Bearer {self.session_token}"}
```

This authentication system provides a secure foundation for the TaylorDash platform with comprehensive security features and detailed audit capabilities.