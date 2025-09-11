"""
Logging middleware for FastAPI application
Provides request/response logging, error handling, and performance monitoring
"""
import json
import time
import uuid
from datetime import datetime, timezone
from typing import Callable, Dict, Any

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from .logging_utils import (
    get_logger, 
    TaylorDashError, 
    get_client_info, 
    sanitize_sensitive_data,
    extract_error_info
)

class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for comprehensive request/response logging"""
    
    def __init__(self, app: ASGIApp, exclude_paths: list = None):
        super().__init__(app)
        self.exclude_paths = exclude_paths or ["/health/live", "/metrics"]
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip logging for health checks and metrics
        if any(request.url.path.startswith(path) for path in self.exclude_paths):
            return await call_next(request)
        
        start_time = time.time()
        request_id = str(uuid.uuid4())
        logger = get_logger()
        
        # Store request ID in request state
        request.state.request_id = request_id
        
        # Extract request information
        request_info = {
            "request_id": request_id,
            "method": request.method,
            "endpoint": request.url.path,
            "query_params": dict(request.query_params),
            "client_info": get_client_info(request),
            "content_type": request.headers.get("content-type"),
            "content_length": request.headers.get("content-length")
        }
        
        # Sanitize sensitive data
        request_info = sanitize_sensitive_data(request_info)
        
        # Log request start
        await logger.info(
            f"Request started: {request.method} {request.url.path}",
            category="API",
            severity="INFO",
            request_id=request_id,
            endpoint=request.url.path,
            method=request.method,
            context=request_info
        )
        
        try:
            # Process request
            response = await call_next(request)
            
            # Calculate duration
            duration_ms = int((time.time() - start_time) * 1000)
            
            # Log successful response
            await logger.info(
                f"Request completed: {request.method} {request.url.path}",
                category="API",
                severity="INFO",
                request_id=request_id,
                endpoint=request.url.path,
                method=request.method,
                status_code=response.status_code,
                duration_ms=duration_ms,
                context={
                    "response_headers": dict(response.headers),
                    "response_size": response.headers.get("content-length")
                }
            )
            
            return response
            
        except Exception as exc:
            # Calculate duration
            duration_ms = int((time.time() - start_time) * 1000)
            
            # Determine error details
            status_code = 500
            error_response = {
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "An unexpected error occurred",
                    "details": None,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "trace_id": request_id,
                    "category": "SYSTEM",
                    "severity": "HIGH",
                    "context": {
                        "endpoint": request.url.path,
                        "method": request.method,
                        "request_id": request_id
                    }
                }
            }
            
            if isinstance(exc, TaylorDashError):
                status_code = self._get_status_code_for_error(exc)
                error_response["error"].update({
                    "code": exc.code,
                    "message": exc.message,
                    "details": exc.details,
                    "category": exc.category,
                    "severity": exc.severity
                })
            
            # Log error with full context
            await logger.error(
                f"Request failed: {request.method} {request.url.path}",
                exc=exc,
                request_id=request_id,
                endpoint=request.url.path,
                method=request.method,
                status_code=status_code,
                duration_ms=duration_ms,
                context={
                    **request_info,
                    **extract_error_info(exc)
                }
            )
            
            return JSONResponse(
                content=error_response,
                status_code=status_code
            )
    
    def _get_status_code_for_error(self, exc: TaylorDashError) -> int:
        """Map error codes to HTTP status codes"""
        status_map = {
            "VALIDATION_FAILED": 400,
            "UNAUTHORIZED": 401,
            "FORBIDDEN": 403,
            "RESOURCE_NOT_FOUND": 404,
            "DUPLICATE_RESOURCE": 409,
            "RATE_LIMIT_EXCEEDED": 429,
            "DATABASE_ERROR": 500,
            "MQTT_ERROR": 502,
            "INTERNAL_ERROR": 500
        }
        return status_map.get(exc.code, 500)

class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Middleware specifically for global error handling"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        try:
            return await call_next(request)
        except Exception as exc:
            logger = get_logger()
            request_id = getattr(request.state, 'request_id', str(uuid.uuid4()))
            
            # Log unhandled exception
            await logger.error(
                "Unhandled exception in application",
                exc=exc,
                request_id=request_id,
                endpoint=request.url.path,
                method=request.method,
                category="SYSTEM",
                severity="CRITICAL"
            )
            
            # Return generic error response
            return JSONResponse(
                content={
                    "error": {
                        "code": "INTERNAL_ERROR",
                        "message": "An internal server error occurred",
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "trace_id": request_id
                    }
                },
                status_code=500
            )

class PerformanceMiddleware(BaseHTTPMiddleware):
    """Middleware for performance monitoring and slow query detection"""
    
    def __init__(self, app: ASGIApp, slow_threshold_ms: int = 1000):
        super().__init__(app)
        self.slow_threshold_ms = slow_threshold_ms
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        response = await call_next(request)
        duration_ms = int((time.time() - start_time) * 1000)
        
        # Log slow requests
        if duration_ms > self.slow_threshold_ms:
            logger = get_logger()
            request_id = getattr(request.state, 'request_id', None)
            
            await logger.warn(
                f"Slow request detected: {request.method} {request.url.path}",
                category="PERFORMANCE",
                severity="MEDIUM",
                request_id=request_id,
                endpoint=request.url.path,
                method=request.method,
                duration_ms=duration_ms,
                context={
                    "threshold_ms": self.slow_threshold_ms,
                    "exceeded_by_ms": duration_ms - self.slow_threshold_ms
                }
            )
        
        return response

class SecurityMiddleware(BaseHTTPMiddleware):
    """Middleware for security event logging"""
    
    def __init__(self, app: ASGIApp, suspicious_patterns: list = None):
        super().__init__(app)
        self.suspicious_patterns = suspicious_patterns or [
            "DROP TABLE", "SELECT * FROM", "UNION SELECT",
            "<script", "javascript:", "eval(",
            "../", "..\\", "/etc/passwd",
            "cmd.exe", "powershell"
        ]
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Check for suspicious patterns in request
        await self._check_for_suspicious_activity(request)
        
        response = await call_next(request)
        
        # Log security-relevant status codes
        if response.status_code in [401, 403, 404, 429]:
            await self._log_security_event(request, response)
        
        return response
    
    async def _check_for_suspicious_activity(self, request: Request):
        """Check request for suspicious patterns"""
        suspicious_found = []
        
        # Check URL path
        for pattern in self.suspicious_patterns:
            if pattern.lower() in request.url.path.lower():
                suspicious_found.append(f"URL path: {pattern}")
        
        # Check query parameters
        for key, value in request.query_params.items():
            for pattern in self.suspicious_patterns:
                if pattern.lower() in value.lower():
                    suspicious_found.append(f"Query param {key}: {pattern}")
        
        # Check headers
        for header_name, header_value in request.headers.items():
            for pattern in self.suspicious_patterns:
                if pattern.lower() in header_value.lower():
                    suspicious_found.append(f"Header {header_name}: {pattern}")
        
        if suspicious_found:
            logger = get_logger()
            request_id = getattr(request.state, 'request_id', None)
            
            await logger.warn(
                "Suspicious request patterns detected",
                category="SECURITY",
                severity="HIGH",
                request_id=request_id,
                endpoint=request.url.path,
                method=request.method,
                context={
                    "patterns_found": suspicious_found,
                    "client_ip": request.client.host if request.client else None,
                    "user_agent": request.headers.get("user-agent"),
                    "full_url": str(request.url)
                }
            )
    
    async def _log_security_event(self, request: Request, response: Response):
        """Log security-relevant HTTP responses"""
        logger = get_logger()
        request_id = getattr(request.state, 'request_id', None)
        
        severity_map = {
            401: "HIGH",    # Unauthorized
            403: "HIGH",    # Forbidden
            404: "MEDIUM",  # Not Found (could be probing)
            429: "MEDIUM"   # Rate Limited
        }
        
        await logger.warn(
            f"Security event: HTTP {response.status_code} response",
            category="SECURITY",
            severity=severity_map.get(response.status_code, "LOW"),
            request_id=request_id,
            endpoint=request.url.path,
            method=request.method,
            status_code=response.status_code,
            context={
                "client_ip": request.client.host if request.client else None,
                "user_agent": request.headers.get("user-agent"),
                "referrer": request.headers.get("referer")
            }
        )

# Utility function to add all middleware
def add_logging_middleware(app, db_pool=None, config: Dict[str, Any] = None):
    """Add all logging middleware to FastAPI app"""
    config = config or {}
    
    # Initialize logger with database pool
    if db_pool:
        from .logging_utils import init_logger
        init_logger(db_pool)
    
    # Add middleware in reverse order (last added = first executed)
    app.add_middleware(
        SecurityMiddleware,
        suspicious_patterns=config.get("suspicious_patterns")
    )
    
    app.add_middleware(
        PerformanceMiddleware,
        slow_threshold_ms=config.get("slow_threshold_ms", 1000)
    )
    
    app.add_middleware(
        LoggingMiddleware,
        exclude_paths=config.get("exclude_paths", ["/health/live", "/metrics"])
    )
    
    app.add_middleware(ErrorHandlingMiddleware)