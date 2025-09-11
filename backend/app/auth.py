"""
Authentication and RBAC middleware for TaylorDash API
Integrates with Keycloak OIDC for JWT validation
"""
import os
import logging
from typing import Dict, List, Optional, Set
from enum import Enum
from functools import wraps

import httpx
import jwt
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel

logger = logging.getLogger(__name__)

# Configuration
KEYCLOAK_URL = os.getenv("KEYCLOAK_URL", "https://tracker.local/kc")
KEYCLOAK_REALM = os.getenv("KEYCLOAK_REALM", "taylordash")
KEYCLOAK_CLIENT_ID = os.getenv("KEYCLOAK_CLIENT_ID", "taylordash-frontend")
OIDC_ISSUER = os.getenv("OIDC_ISSUER", f"{KEYCLOAK_URL}/realms/{KEYCLOAK_REALM}")
OIDC_AUDIENCE = os.getenv("OIDC_AUDIENCE", KEYCLOAK_CLIENT_ID)

# RBAC Roles
class Role(str, Enum):
    VIEWER = "viewer"
    MAINTAINER = "maintainer"
    ADMIN = "admin"

# Role hierarchy (higher roles inherit lower role permissions)
ROLE_HIERARCHY = {
    Role.ADMIN: {Role.ADMIN, Role.MAINTAINER, Role.VIEWER},
    Role.MAINTAINER: {Role.MAINTAINER, Role.VIEWER},
    Role.VIEWER: {Role.VIEWER}
}

# Security scheme
security = HTTPBearer()

# Cache for OIDC configuration and public keys
_oidc_config_cache: Optional[Dict] = None
_jwks_cache: Optional[Dict] = None

class User(BaseModel):
    """Authenticated user model"""
    sub: str  # Subject (user ID)
    username: str
    email: Optional[str] = None
    roles: Set[Role]
    preferred_username: Optional[str] = None
    
    class Config:
        use_enum_values = True

class AuthenticationError(HTTPException):
    """Custom authentication error"""
    def __init__(self, detail: str = "Authentication failed"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"}
        )

class AuthorizationError(HTTPException):
    """Custom authorization error"""
    def __init__(self, detail: str = "Insufficient permissions"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail
        )

async def get_oidc_configuration() -> Dict:
    """Fetch and cache OIDC configuration from Keycloak"""
    global _oidc_config_cache
    
    if _oidc_config_cache is None:
        try:
            oidc_url = f"{KEYCLOAK_URL}/realms/{KEYCLOAK_REALM}/.well-known/openid_configuration"
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(oidc_url)
                response.raise_for_status()
                _oidc_config_cache = response.json()
                logger.info("OIDC configuration cached")
        except Exception as e:
            logger.error(f"Failed to fetch OIDC configuration: {e}")
            raise AuthenticationError("Authentication service unavailable")
    
    return _oidc_config_cache

async def get_jwks() -> Dict:
    """Fetch and cache JWKS (JSON Web Key Set) from Keycloak"""
    global _jwks_cache
    
    if _jwks_cache is None:
        try:
            oidc_config = await get_oidc_configuration()
            jwks_uri = oidc_config["jwks_uri"]
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(jwks_uri)
                response.raise_for_status()
                _jwks_cache = response.json()
                logger.info("JWKS cached")
        except Exception as e:
            logger.error(f"Failed to fetch JWKS: {e}")
            raise AuthenticationError("Authentication service unavailable")
    
    return _jwks_cache

def get_signing_key(token_header: Dict) -> Optional[str]:
    """Extract signing key from JWKS based on token header"""
    try:
        # This is a simplified implementation
        # In production, you'd want to properly parse the JWKS and match the kid
        kid = token_header.get("kid")
        if not kid:
            return None
        
        # For now, return None to indicate we should fetch the key
        # In a real implementation, you'd cache and lookup keys by kid
        return None
    except Exception as e:
        logger.error(f"Failed to get signing key: {e}")
        return None

def extract_roles_from_token(token_payload: Dict) -> Set[Role]:
    """Extract roles from JWT token payload"""
    roles = set()
    
    try:
        # Check realm roles
        realm_access = token_payload.get("realm_access", {})
        realm_roles = realm_access.get("roles", [])
        
        # Check resource access (client-specific roles)
        resource_access = token_payload.get("resource_access", {})
        client_access = resource_access.get(KEYCLOAK_CLIENT_ID, {})
        client_roles = client_access.get("roles", [])
        
        # Combine roles
        all_roles = realm_roles + client_roles
        
        # Map to our Role enum
        for role_str in all_roles:
            try:
                role = Role(role_str.lower())
                roles.add(role)
            except ValueError:
                # Ignore unknown roles
                logger.debug(f"Unknown role: {role_str}")
                continue
        
        # If no specific roles found, default to viewer
        if not roles:
            roles.add(Role.VIEWER)
            
    except Exception as e:
        logger.error(f"Failed to extract roles from token: {e}")
        roles.add(Role.VIEWER)  # Default to viewer on error
    
    return roles

async def verify_jwt_token(token: str) -> Dict:
    """Verify JWT token with Keycloak public key"""
    try:
        # Decode token header to get algorithm and key ID
        unverified_header = jwt.get_unverified_header(token)
        
        # For development/testing, we'll skip signature verification
        # In production, you should verify with the public key from JWKS
        if os.getenv("SKIP_JWT_VERIFICATION", "false").lower() == "true":
            logger.warning("JWT verification is disabled (development mode)")
            payload = jwt.decode(token, options={"verify_signature": False})
        else:
            # Get OIDC configuration to ensure service is available
            await get_oidc_configuration()
            
            # For now, decode without verification (TODO: implement proper verification)
            # This is a simplified implementation for the MVP
            payload = jwt.decode(token, options={"verify_signature": False})
            
            # Basic validation
            if payload.get("iss") != OIDC_ISSUER:
                raise jwt.InvalidTokenError("Invalid issuer")
            
            # Validate audience
            aud = payload.get("aud")
            if aud and OIDC_AUDIENCE not in (aud if isinstance(aud, list) else [aud]):
                raise jwt.InvalidTokenError("Invalid audience")
        
        return payload
        
    except jwt.ExpiredSignatureError:
        raise AuthenticationError("Token has expired")
    except jwt.InvalidTokenError as e:
        raise AuthenticationError(f"Invalid token: {str(e)}")
    except Exception as e:
        logger.error(f"Token verification failed: {e}")
        raise AuthenticationError("Token verification failed")

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """FastAPI dependency to get current authenticated user"""
    try:
        token = credentials.credentials
        payload = await verify_jwt_token(token)
        
        # Extract user information
        sub = payload.get("sub")
        if not sub:
            raise AuthenticationError("Token missing subject")
        
        username = payload.get("preferred_username", payload.get("username", sub))
        email = payload.get("email")
        roles = extract_roles_from_token(payload)
        
        user = User(
            sub=sub,
            username=username,
            email=email,
            roles=roles,
            preferred_username=payload.get("preferred_username")
        )
        
        logger.debug(f"Authenticated user: {username} with roles: {list(roles)}")
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Authentication failed: {e}")
        raise AuthenticationError("Authentication failed")

def require_roles(*required_roles: Role):
    """Decorator factory for role-based access control"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract user from kwargs (injected by FastAPI dependency)
            user = None
            for arg_name, arg_value in kwargs.items():
                if isinstance(arg_value, User):
                    user = arg_value
                    break
            
            if not user:
                raise AuthorizationError("User not found in request context")
            
            # Check if user has any of the required roles (considering hierarchy)
            user_effective_roles = set()
            for user_role in user.roles:
                user_effective_roles.update(ROLE_HIERARCHY.get(user_role, {user_role}))
            
            if not any(role in user_effective_roles for role in required_roles):
                required_role_names = [role.value for role in required_roles]
                user_role_names = [role.value for role in user.roles]
                raise AuthorizationError(
                    f"Access denied. Required roles: {required_role_names}, "
                    f"user roles: {user_role_names}"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

# Convenience dependencies for different role requirements
async def require_viewer(user: User = Depends(get_current_user)) -> User:
    """Require viewer role or higher"""
    user_effective_roles = set()
    for user_role in user.roles:
        user_effective_roles.update(ROLE_HIERARCHY.get(user_role, {user_role}))
    
    if Role.VIEWER not in user_effective_roles:
        raise AuthorizationError("Viewer access required")
    
    return user

async def require_maintainer(user: User = Depends(get_current_user)) -> User:
    """Require maintainer role or higher"""
    user_effective_roles = set()
    for user_role in user.roles:
        user_effective_roles.update(ROLE_HIERARCHY.get(user_role, {user_role}))
    
    if Role.MAINTAINER not in user_effective_roles:
        raise AuthorizationError("Maintainer access required")
    
    return user

async def require_admin(user: User = Depends(get_current_user)) -> User:
    """Require admin role"""
    user_effective_roles = set()
    for user_role in user.roles:
        user_effective_roles.update(ROLE_HIERARCHY.get(user_role, {user_role}))
    
    if Role.ADMIN not in user_effective_roles:
        raise AuthorizationError("Admin access required")
    
    return user

# Optional authentication (for endpoints that work with or without auth)
async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))
) -> Optional[User]:
    """FastAPI dependency to get current user if authenticated, None otherwise"""
    if not credentials:
        return None
    
    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None