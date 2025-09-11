"""
Security module for TaylorDash API
Handles API key authentication and security middleware
"""
import os
import logging
from typing import Optional
from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger(__name__)

# API Key authentication
API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

def get_api_key() -> str:
    """Get the API key from environment variables"""
    api_key = os.getenv("API_KEY", "taylordash-dev-key")
    if not api_key:
        raise RuntimeError("API_KEY environment variable is required")
    return api_key

async def verify_api_key(api_key: Optional[str] = Security(api_key_header)) -> str:
    """
    Verify the provided API key against the configured key
    
    Args:
        api_key: The API key from the request header
        
    Returns:
        The verified API key
        
    Raises:
        HTTPException: If API key is missing or invalid
    """
    if not api_key:
        logger.warning("API request made without API key")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API key",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    
    expected_key = get_api_key()
    if api_key != expected_key:
        logger.warning(f"Invalid API key provided: {api_key[:8]}...")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    
    return api_key

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add security headers to all responses
    """
    
    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        
        # Remove server information leakage
        if "server" in response.headers:
            del response.headers["server"]
            
        return response

def is_protected_endpoint(path: str) -> bool:
    """
    Check if an endpoint requires API key authentication
    
    Args:
        path: The request path
        
    Returns:
        True if endpoint requires authentication, False otherwise
    """
    # Exclude health checks and metrics from authentication
    public_paths = [
        "/health/",
        "/metrics",
        "/",
        "/docs",
        "/openapi.json",
        "/redoc"
    ]
    
    # Check if path starts with any public path
    for public_path in public_paths:
        if path.startswith(public_path):
            return False
    
    # All /api/v1/ endpoints require authentication
    if path.startswith("/api/v1/"):
        return True
        
    return False