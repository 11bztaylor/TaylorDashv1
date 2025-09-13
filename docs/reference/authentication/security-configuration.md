# Security Configuration Guide

**Last Updated:** 2025-09-12
**Version:** 1.0
**Status:** Production Security Hardened

## Overview

This guide covers the security configuration for TaylorDash authentication system, including password policies, session management, and security headers.

## Password Security Configuration

### Password Policy Settings
```python
# backend/app/config.py
class SecurityConfig:
    # Password requirements
    PASSWORD_MIN_LENGTH = 8
    PASSWORD_MAX_LENGTH = 255
    PASSWORD_REQUIRE_UPPERCASE = False
    PASSWORD_REQUIRE_LOWERCASE = False
    PASSWORD_REQUIRE_NUMBERS = False
    PASSWORD_REQUIRE_SPECIAL = False

    # Bcrypt configuration
    BCRYPT_ROUNDS = 12  # Production value

    # Account lockout
    MAX_LOGIN_ATTEMPTS = 5
    LOCKOUT_DURATION_MINUTES = 15
```

### Password Validation Implementation
```python
# backend/app/utils/password.py
import re
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class PasswordValidator:
    def __init__(self, config: SecurityConfig):
        self.config = config

    def validate_password(self, password: str) -> list[str]:
        """Validate password against policy"""
        errors = []

        if len(password) < self.config.PASSWORD_MIN_LENGTH:
            errors.append(f"Password must be at least {self.config.PASSWORD_MIN_LENGTH} characters")

        if len(password) > self.config.PASSWORD_MAX_LENGTH:
            errors.append(f"Password must not exceed {self.config.PASSWORD_MAX_LENGTH} characters")

        if self.config.PASSWORD_REQUIRE_UPPERCASE and not re.search(r'[A-Z]', password):
            errors.append("Password must contain at least one uppercase letter")

        if self.config.PASSWORD_REQUIRE_LOWERCASE and not re.search(r'[a-z]', password):
            errors.append("Password must contain at least one lowercase letter")

        if self.config.PASSWORD_REQUIRE_NUMBERS and not re.search(r'\d', password):
            errors.append("Password must contain at least one number")

        if self.config.PASSWORD_REQUIRE_SPECIAL and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            errors.append("Password must contain at least one special character")

        return errors

    def hash_password(self, password: str) -> str:
        """Hash password with bcrypt"""
        return pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        return pwd_context.verify(plain_password, hashed_password)
```

### Enhanced Password Policy (Production Recommended)
```python
# Production security settings
class ProductionSecurityConfig(SecurityConfig):
    PASSWORD_MIN_LENGTH = 12
    PASSWORD_REQUIRE_UPPERCASE = True
    PASSWORD_REQUIRE_LOWERCASE = True
    PASSWORD_REQUIRE_NUMBERS = True
    PASSWORD_REQUIRE_SPECIAL = True
    BCRYPT_ROUNDS = 14  # Higher for production

    # Additional security
    PASSWORD_HISTORY_COUNT = 5  # Remember last 5 passwords
    PASSWORD_EXPIRY_DAYS = 90   # Force password change
    FORCE_PASSWORD_CHANGE_ON_FIRST_LOGIN = True
```

## Session Security Configuration

### Session Token Settings
```python
# backend/app/config.py
class SessionConfig:
    # Token generation
    TOKEN_LENGTH_BYTES = 32
    TOKEN_ALGORITHM = "HS256"

    # Session timing
    SESSION_EXPIRE_HOURS = 8
    SESSION_REFRESH_THRESHOLD_MINUTES = 30

    # Security features
    SESSION_FINGERPRINTING = True
    REQUIRE_HTTPS_FOR_SESSIONS = True
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "strict"

    # Cleanup
    SESSION_CLEANUP_INTERVAL_SECONDS = 3600  # 1 hour
    MAX_SESSIONS_PER_USER = 5
```

### Session Management Implementation
```python
# backend/app/auth/session.py
import secrets
import hashlib
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

class SessionManager:
    def __init__(self, config: SessionConfig):
        self.config = config

    def generate_session_token(self) -> str:
        """Generate cryptographically secure session token"""
        return secrets.token_urlsafe(self.config.TOKEN_LENGTH_BYTES)

    def create_session(self, user_id: int, user_agent: str = None, ip_address: str = None) -> dict:
        """Create new session with security metadata"""
        token = self.generate_session_token()
        expires_at = datetime.utcnow() + timedelta(hours=self.config.SESSION_EXPIRE_HOURS)

        # Create session fingerprint
        fingerprint = self.create_fingerprint(user_agent, ip_address) if self.config.SESSION_FINGERPRINTING else None

        session_data = {
            "token": token,
            "user_id": user_id,
            "expires_at": expires_at,
            "fingerprint": fingerprint,
            "created_at": datetime.utcnow()
        }

        return session_data

    def create_fingerprint(self, user_agent: str, ip_address: str) -> str:
        """Create session fingerprint for additional security"""
        data = f"{user_agent}:{ip_address}".encode()
        return hashlib.sha256(data).hexdigest()

    def validate_session(self, token: str, user_agent: str = None, ip_address: str = None) -> bool:
        """Validate session token and fingerprint"""
        # Implementation details for session validation
        pass
```

### Session Cleanup Configuration
```python
# backend/app/tasks/session_cleanup.py
from celery import Celery
from datetime import datetime
from app.database import SessionLocal
from app.models import Session as SessionModel

app = Celery('taylordash')

@app.task
def cleanup_expired_sessions():
    """Remove expired sessions from database"""
    db = SessionLocal()
    try:
        expired_count = db.query(SessionModel).filter(
            SessionModel.expires_at < datetime.utcnow()
        ).delete()

        db.commit()
        return {"cleaned_sessions": expired_count, "timestamp": datetime.utcnow()}
    finally:
        db.close()

# Schedule cleanup task
from celery.schedules import crontab

app.conf.beat_schedule = {
    'cleanup-expired-sessions': {
        'task': 'app.tasks.session_cleanup.cleanup_expired_sessions',
        'schedule': crontab(minute=0),  # Every hour
    },
}
```

## API Security Configuration

### API Key Management
```python
# backend/app/config.py
class APIKeyConfig:
    # API key settings
    API_KEY_LENGTH = 32
    API_KEY_PREFIX = "taylordash-"

    # Rate limiting
    API_KEY_RATE_LIMIT_PER_HOUR = 10000
    API_KEY_RATE_LIMIT_PER_MINUTE = 200

    # Security
    API_KEY_ROTATION_DAYS = 90
    REQUIRE_API_KEY_HTTPS = True
```

### Rate Limiting Configuration
```python
# backend/app/middleware/rate_limit.py
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["1000/hour"]
)

# Rate limiting for authentication endpoints
@limiter.limit("5/minute")
async def login_endpoint():
    """Login with rate limiting"""
    pass

@limiter.limit("10/hour")
async def create_user_endpoint():
    """User creation with rate limiting"""
    pass
```

## Security Headers Configuration

### FastAPI Security Headers Middleware
```python
# backend/app/middleware/security.py
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"

        # HSTS for HTTPS
        if request.url.scheme == "https":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"

        # CSP for additional protection
        csp_policy = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "connect-src 'self' wss: ws:; "
            "font-src 'self';"
        )
        response.headers["Content-Security-Policy"] = csp_policy

        return response
```

### CORS Configuration
```python
# backend/app/main.py
from fastapi.middleware.cors import CORSMiddleware

# CORS settings
origins = [
    "http://localhost:5174",  # Development frontend
    "https://yourdomain.com", # Production frontend
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
    expose_headers=["X-RateLimit-Limit", "X-RateLimit-Remaining", "X-RateLimit-Reset"],
)
```

## Database Security Configuration

### Connection Security
```python
# backend/app/database.py
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

# Secure database connection
DATABASE_URL = "postgresql://user:password@host:5432/database?sslmode=require"

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=30,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=False,  # Disable in production
    connect_args={
        "sslmode": "require",
        "connect_timeout": 10,
    }
)
```

### SQL Injection Prevention
```python
# backend/app/crud/user.py
from sqlalchemy.orm import Session
from sqlalchemy import text

class UserCRUD:
    def get_user_by_username(self, db: Session, username: str):
        """Safe parameterized query"""
        # Good: Parameterized query
        return db.query(User).filter(User.username == username).first()

        # Bad: String concatenation (SQL injection risk)
        # return db.execute(f"SELECT * FROM users WHERE username = '{username}'")

    def search_users(self, db: Session, search_term: str):
        """Safe text query with parameters"""
        query = text("SELECT * FROM users WHERE username ILIKE :search")
        return db.execute(query, {"search": f"%{search_term}%"}).fetchall()
```

## Input Validation Configuration

### Pydantic Models with Validation
```python
# backend/app/schemas/auth.py
from pydantic import BaseModel, validator, Field
import re

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=255)
    password: str = Field(..., min_length=8, max_length=255)
    role: str = Field(..., regex="^(admin|viewer)$")

    @validator('username')
    def validate_username(cls, v):
        if not re.match("^[a-zA-Z0-9_-]+$", v):
            raise ValueError('Username can only contain letters, numbers, hyphens, and underscores')
        return v

    @validator('password')
    def validate_password(cls, v):
        # Custom password validation
        validator = PasswordValidator(SecurityConfig())
        errors = validator.validate_password(v)
        if errors:
            raise ValueError('; '.join(errors))
        return v

class LoginRequest(BaseModel):
    username: str = Field(..., min_length=1, max_length=255)
    password: str = Field(..., min_length=1, max_length=255)

    @validator('username', 'password')
    def sanitize_input(cls, v):
        # Strip whitespace and basic sanitization
        return v.strip()
```

### Request Size Limiting
```python
# backend/app/middleware/request_size.py
from fastapi import HTTPException, Request
from starlette.middleware.base import BaseHTTPMiddleware

class RequestSizeLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, max_request_size: int = 1024 * 1024):  # 1MB default
        super().__init__(app)
        self.max_request_size = max_request_size

    async def dispatch(self, request: Request, call_next):
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > self.max_request_size:
            raise HTTPException(status_code=413, detail="Request too large")

        return await call_next(request)
```

## Audit Logging Configuration

### Security Event Logging
```python
# backend/app/audit/logger.py
import logging
from datetime import datetime
from typing import Optional

class SecurityAuditLogger:
    def __init__(self):
        self.logger = logging.getLogger("security_audit")
        self.logger.setLevel(logging.INFO)

        # File handler for audit logs
        handler = logging.FileHandler("/var/log/taylordash/security_audit.log")
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def log_login_attempt(self, username: str, ip_address: str, success: bool):
        """Log authentication attempt"""
        status = "SUCCESS" if success else "FAILURE"
        self.logger.info(f"LOGIN_{status}: user={username}, ip={ip_address}")

    def log_user_creation(self, admin_user: str, new_user: str, role: str):
        """Log user creation"""
        self.logger.info(f"USER_CREATED: admin={admin_user}, new_user={new_user}, role={role}")

    def log_privilege_escalation(self, admin_user: str, target_user: str, new_role: str):
        """Log role changes"""
        self.logger.info(f"ROLE_CHANGED: admin={admin_user}, target={target_user}, new_role={new_role}")

    def log_session_event(self, event_type: str, user: str, session_id: str):
        """Log session events"""
        self.logger.info(f"SESSION_{event_type}: user={user}, session={session_id}")
```

## Environment-Specific Security

### Development Environment
```bash
# .env.development
ENVIRONMENT=development
DEBUG=true
SESSION_EXPIRE_HOURS=24
BCRYPT_ROUNDS=10
REQUIRE_HTTPS_FOR_SESSIONS=false
SESSION_COOKIE_SECURE=false
```

### Production Environment
```bash
# .env.production
ENVIRONMENT=production
DEBUG=false
SESSION_EXPIRE_HOURS=8
BCRYPT_ROUNDS=14
REQUIRE_HTTPS_FOR_SESSIONS=true
SESSION_COOKIE_SECURE=true
SESSION_FINGERPRINTING=true
API_KEY_ROTATION_DAYS=30
```

### Security Monitoring
```bash
# Production monitoring script
#!/bin/bash

# Monitor failed login attempts
tail -f /var/log/taylordash/security_audit.log | grep "LOGIN_FAILURE" | while read line; do
    echo "Failed login attempt: $line"
    # Alert if threshold exceeded
done

# Monitor privilege escalations
tail -f /var/log/taylordash/security_audit.log | grep "ROLE_CHANGED" | while read line; do
    echo "Role change detected: $line"
    # Send security alert
done
```

## Security Checklist

### Production Deployment Security
- [ ] HTTPS enforced for all connections
- [ ] Strong password policy implemented
- [ ] Session fingerprinting enabled
- [ ] Rate limiting configured
- [ ] Security headers implemented
- [ ] CORS properly configured
- [ ] Database connections encrypted
- [ ] Audit logging enabled
- [ ] Input validation comprehensive
- [ ] Error messages sanitized
- [ ] API keys rotated regularly
- [ ] Session cleanup automated
- [ ] Security monitoring active

### Security Testing
```bash
# Security validation script
#!/bin/bash

echo "=== Security Configuration Validation ==="

# Test HTTPS enforcement
curl -I http://localhost:3000/api/v1/auth/login | grep -q "301\|302" && echo "✅ HTTP redirect working" || echo "❌ HTTP redirect failed"

# Test security headers
curl -I https://localhost:3000/api/v1/projects | grep -q "X-Content-Type-Options" && echo "✅ Security headers present" || echo "❌ Security headers missing"

# Test rate limiting
for i in {1..10}; do curl -s http://localhost:3000/api/v1/auth/login > /dev/null; done
curl -I http://localhost:3000/api/v1/auth/login | grep -q "429" && echo "✅ Rate limiting working" || echo "❌ Rate limiting not active"

# Test password policy
curl -X POST http://localhost:3000/api/v1/auth/login -d '{"username":"admin","password":"weak"}' | grep -q "Password must be" && echo "✅ Password policy enforced" || echo "❌ Password policy not enforced"

echo "Security validation completed"
```