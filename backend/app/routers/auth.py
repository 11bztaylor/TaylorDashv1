"""
TaylorDash Authentication API
Two-tier user system with admin and viewer roles
Session-based authentication with secure token management
"""

from datetime import datetime, timedelta
from typing import Optional, List
import secrets
import bcrypt
from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel, Field
import asyncpg
from uuid import UUID

from ..database import get_db_connection
from ..security import require_api_key

router = APIRouter(prefix="/api/v1/auth", tags=["authentication"])

# Pydantic models for request/response
class LoginRequest(BaseModel):
    username: str
    password: str
    remember_me: bool = False
    single_view_mode: bool = False
    default_view: Optional[str] = None

class LoginResponse(BaseModel):
    user_id: str
    username: str
    role: str
    session_token: str
    expires_at: datetime
    single_view_mode: bool
    default_view: Optional[str]

class UserInfo(BaseModel):
    id: str
    username: str
    role: str
    default_view: Optional[str]
    single_view_mode: bool
    created_at: datetime
    last_login: Optional[datetime]
    is_active: bool

class CreateUserRequest(BaseModel):
    username: str
    password: str
    role: str = Field(..., pattern="^(admin|viewer)$")
    default_view: Optional[str] = None
    single_view_mode: bool = False

class UpdateUserRequest(BaseModel):
    role: Optional[str] = Field(None, pattern="^(admin|viewer)$")
    default_view: Optional[str] = None
    single_view_mode: Optional[bool] = None
    is_active: Optional[bool] = None
    password: Optional[str] = None

# Session management
SESSION_DURATION_HOURS = 24
SESSION_DURATION_REMEMBER_ME_DAYS = 30

def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def generate_session_token() -> str:
    """Generate secure random session token"""
    return secrets.token_urlsafe(32)

async def get_current_user(request: Request, conn: asyncpg.Connection = Depends(get_db_connection)) -> Optional[dict]:
    """Get current user from session token in Authorization header"""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None
    
    token = auth_header[7:]  # Remove "Bearer " prefix
    
    # Check if session is valid and not expired
    query = """
        SELECT u.*, s.expires_at 
        FROM users u
        JOIN user_sessions s ON u.id = s.user_id
        WHERE s.session_token = $1 
        AND s.is_active = true 
        AND s.expires_at > CURRENT_TIMESTAMP
    """
    user = await conn.fetchrow(query, token)
    
    if user:
        # Update last activity
        await conn.execute(
            "UPDATE user_sessions SET last_activity = CURRENT_TIMESTAMP WHERE session_token = $1",
            token
        )
        return dict(user)
    
    return None

async def require_admin(request: Request, conn: asyncpg.Connection = Depends(get_db_connection)) -> dict:
    """Dependency to require admin user"""
    user = await get_current_user(request, conn)
    if not user or user['role'] != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return user

@router.post("/login", response_model=LoginResponse)
async def login(
    request: LoginRequest,
    client_request: Request,
    conn: asyncpg.Connection = Depends(get_db_connection)
):
    """Authenticate user and create session"""
    # Find user by username
    user = await conn.fetchrow(
        "SELECT * FROM users WHERE username = $1 AND is_active = true",
        request.username
    )
    
    if not user or not verify_password(request.password, user['password_hash']):
        # Log failed attempt
        if user:
            await conn.execute(
                """INSERT INTO auth_audit_log (user_id, event_type, ip_address, user_agent, details)
                   VALUES ($1, 'login_failed', $2, $3, $4)""",
                user['id'],
                client_request.client.host,
                client_request.headers.get("User-Agent"),
                {"reason": "invalid_password"}
            )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    
    # Create session
    session_token = generate_session_token()
    if request.remember_me:
        expires_at = datetime.utcnow() + timedelta(days=SESSION_DURATION_REMEMBER_ME_DAYS)
    else:
        expires_at = datetime.utcnow() + timedelta(hours=SESSION_DURATION_HOURS)
    
    # Store session
    await conn.execute(
        """INSERT INTO user_sessions (user_id, session_token, expires_at, ip_address, user_agent)
           VALUES ($1, $2, $3, $4, $5)""",
        user['id'],
        session_token,
        expires_at,
        client_request.client.host,
        client_request.headers.get("User-Agent")
    )
    
    # Update user's last login and settings if provided
    if request.single_view_mode or request.default_view:
        await conn.execute(
            """UPDATE users 
               SET last_login = CURRENT_TIMESTAMP,
                   single_view_mode = COALESCE($2, single_view_mode),
                   default_view = COALESCE($3, default_view)
               WHERE id = $1""",
            user['id'],
            request.single_view_mode if user['role'] == 'viewer' else False,
            request.default_view if user['role'] == 'viewer' else None
        )
    else:
        await conn.execute(
            "UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = $1",
            user['id']
        )
    
    # Log successful login
    await conn.execute(
        """INSERT INTO auth_audit_log (user_id, event_type, ip_address, user_agent)
           VALUES ($1, 'login_success', $2, $3)""",
        user['id'],
        client_request.client.host,
        client_request.headers.get("User-Agent")
    )
    
    return LoginResponse(
        user_id=str(user['id']),
        username=user['username'],
        role=user['role'],
        session_token=session_token,
        expires_at=expires_at,
        single_view_mode=request.single_view_mode if user['role'] == 'viewer' else False,
        default_view=request.default_view if user['role'] == 'viewer' else user.get('default_view')
    )

@router.post("/logout")
async def logout(
    request: Request,
    conn: asyncpg.Connection = Depends(get_db_connection)
):
    """Terminate user session"""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No active session"
        )
    
    token = auth_header[7:]
    
    # Get user for audit log
    session = await conn.fetchrow(
        "SELECT user_id FROM user_sessions WHERE session_token = $1 AND is_active = true",
        token
    )
    
    if session:
        # Deactivate session
        await conn.execute(
            "UPDATE user_sessions SET is_active = false WHERE session_token = $1",
            token
        )
        
        # Log logout
        await conn.execute(
            """INSERT INTO auth_audit_log (user_id, event_type, ip_address, user_agent)
               VALUES ($1, 'logout', $2, $3)""",
            session['user_id'],
            request.client.host,
            request.headers.get("User-Agent")
        )
    
    return {"message": "Logged out successfully"}

@router.get("/me", response_model=UserInfo)
async def get_current_user_info(
    request: Request,
    conn: asyncpg.Connection = Depends(get_db_connection)
):
    """Get current user information"""
    user = await get_current_user(request, conn)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    return UserInfo(
        id=str(user['id']),
        username=user['username'],
        role=user['role'],
        default_view=user.get('default_view'),
        single_view_mode=user.get('single_view_mode', False),
        created_at=user['created_at'],
        last_login=user.get('last_login'),
        is_active=user['is_active']
    )

@router.post("/users", response_model=UserInfo)
async def create_user(
    user_request: CreateUserRequest,
    current_user: dict = Depends(require_admin),
    conn: asyncpg.Connection = Depends(get_db_connection)
):
    """Create new user (admin only)"""
    # Check if username already exists
    existing = await conn.fetchrow(
        "SELECT id FROM users WHERE username = $1",
        user_request.username
    )
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already exists"
        )
    
    # Hash password and create user
    password_hash = hash_password(user_request.password)
    
    new_user = await conn.fetchrow(
        """INSERT INTO users (username, password_hash, role, default_view, single_view_mode, created_by)
           VALUES ($1, $2, $3, $4, $5, $6)
           RETURNING *""",
        user_request.username,
        password_hash,
        user_request.role,
        user_request.default_view if user_request.role == 'viewer' else None,
        user_request.single_view_mode if user_request.role == 'viewer' else False,
        current_user['id']
    )
    
    return UserInfo(
        id=str(new_user['id']),
        username=new_user['username'],
        role=new_user['role'],
        default_view=new_user.get('default_view'),
        single_view_mode=new_user.get('single_view_mode', False),
        created_at=new_user['created_at'],
        last_login=None,
        is_active=new_user['is_active']
    )

@router.get("/users", response_model=List[UserInfo])
async def list_users(
    current_user: dict = Depends(require_admin),
    conn: asyncpg.Connection = Depends(get_db_connection)
):
    """List all users (admin only)"""
    users = await conn.fetch(
        "SELECT * FROM users ORDER BY created_at DESC"
    )
    
    return [
        UserInfo(
            id=str(user['id']),
            username=user['username'],
            role=user['role'],
            default_view=user.get('default_view'),
            single_view_mode=user.get('single_view_mode', False),
            created_at=user['created_at'],
            last_login=user.get('last_login'),
            is_active=user['is_active']
        )
        for user in users
    ]

@router.put("/users/{user_id}", response_model=UserInfo)
async def update_user(
    user_id: str,
    update_request: UpdateUserRequest,
    current_user: dict = Depends(require_admin),
    conn: asyncpg.Connection = Depends(get_db_connection)
):
    """Update user (admin only)"""
    # Build update query dynamically
    updates = []
    params = [user_id]
    param_count = 2
    
    if update_request.role is not None:
        updates.append(f"role = ${param_count}")
        params.append(update_request.role)
        param_count += 1
    
    if update_request.default_view is not None:
        updates.append(f"default_view = ${param_count}")
        params.append(update_request.default_view)
        param_count += 1
    
    if update_request.single_view_mode is not None:
        updates.append(f"single_view_mode = ${param_count}")
        params.append(update_request.single_view_mode)
        param_count += 1
    
    if update_request.is_active is not None:
        updates.append(f"is_active = ${param_count}")
        params.append(update_request.is_active)
        param_count += 1
    
    if update_request.password is not None:
        updates.append(f"password_hash = ${param_count}")
        params.append(hash_password(update_request.password))
        param_count += 1
    
    if not updates:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No updates provided"
        )
    
    query = f"UPDATE users SET {', '.join(updates)} WHERE id = $1 RETURNING *"
    
    updated_user = await conn.fetchrow(query, *params)
    
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserInfo(
        id=str(updated_user['id']),
        username=updated_user['username'],
        role=updated_user['role'],
        default_view=updated_user.get('default_view'),
        single_view_mode=updated_user.get('single_view_mode', False),
        created_at=updated_user['created_at'],
        last_login=updated_user.get('last_login'),
        is_active=updated_user['is_active']
    )

@router.delete("/users/{user_id}")
async def delete_user(
    user_id: str,
    current_user: dict = Depends(require_admin),
    conn: asyncpg.Connection = Depends(get_db_connection)
):
    """Delete user (admin only)"""
    # Prevent admin from deleting themselves
    if str(current_user['id']) == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )
    
    # Get user info for audit log
    user_to_delete = await conn.fetchrow(
        "SELECT id, username FROM users WHERE id = $1",
        user_id
    )
    
    if not user_to_delete:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Delete user (this will cascade to sessions due to foreign key)
    result = await conn.execute(
        "DELETE FROM users WHERE id = $1",
        user_id
    )
    
    if result == "DELETE 0":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Log user deletion
    await conn.execute(
        """INSERT INTO auth_audit_log (user_id, event_type, details)
           VALUES ($1, 'user_deleted', $2)""",
        current_user['id'],
        {
            "deleted_user_id": str(user_to_delete['id']),
            "deleted_username": user_to_delete['username'],
            "deleted_by": current_user['username']
        }
    )
    
    return {"message": f"User {user_to_delete['username']} deleted successfully"}

@router.delete("/sessions/cleanup")
async def cleanup_sessions(
    api_key: str = Depends(require_api_key),
    conn: asyncpg.Connection = Depends(get_db_connection)
):
    """Clean up expired sessions (called by cron job)"""
    result = await conn.execute(
        """UPDATE user_sessions 
           SET is_active = false 
           WHERE expires_at < CURRENT_TIMESTAMP AND is_active = true"""
    )
    
    return {"message": f"Cleaned up {result} expired sessions"}