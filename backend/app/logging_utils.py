"""
Centralized logging utilities for TaylorDash
Provides structured logging, error handling, and database integration
"""
import json
import logging
import traceback
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from contextlib import asynccontextmanager

import asyncpg
from opentelemetry import trace

# Custom exceptions for error categorization
class TaylorDashError(Exception):
    """Base exception for TaylorDash application errors"""
    def __init__(self, code: str, message: str, details: str = None, 
                 category: str = "SYSTEM", severity: str = "MEDIUM"):
        self.code = code
        self.message = message
        self.details = details
        self.category = category
        self.severity = severity
        super().__init__(message)

class ValidationError(TaylorDashError):
    """Validation-specific errors"""
    def __init__(self, message: str, field: str = None):
        details = f"Field: {field}" if field else None
        super().__init__("VALIDATION_FAILED", message, details, "VALIDATION", "MEDIUM")

class DatabaseError(TaylorDashError):
    """Database operation errors"""
    def __init__(self, message: str, details: str = None):
        super().__init__("DATABASE_ERROR", message, details, "DATABASE", "HIGH")

class MQTTError(TaylorDashError):
    """MQTT communication errors"""
    def __init__(self, message: str, details: str = None):
        super().__init__("MQTT_ERROR", message, details, "MQTT", "HIGH")

class AuthenticationError(TaylorDashError):
    """Authentication failures"""
    def __init__(self, message: str = "Invalid authentication"):
        super().__init__("UNAUTHORIZED", message, None, "AUTHENTICATION", "HIGH")

class AuthorizationError(TaylorDashError):
    """Authorization failures"""
    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__("FORBIDDEN", message, None, "AUTHORIZATION", "HIGH")

# Structured logger class
class StructuredLogger:
    """Enhanced logger with structured output and database integration"""
    
    def __init__(self, service_name: str, db_pool: Optional[asyncpg.Pool] = None):
        self.service_name = service_name
        self.db_pool = db_pool
        self.logger = logging.getLogger(service_name)
        
        # Configure JSON formatter
        handler = logging.StreamHandler()
        formatter = StructuredFormatter()
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
    
    async def log(self, level: str, category: str, severity: str, message: str,
                  details: str = None, trace_id: str = None, request_id: str = None,
                  user_id: str = None, endpoint: str = None, method: str = None,
                  status_code: int = None, duration_ms: int = None,
                  error_code: str = None, stack_trace: str = None,
                  context: Dict[str, Any] = None, **kwargs):
        """Log structured message to both console and database"""
        
        # Get trace context if available
        if not trace_id:
            span = trace.get_current_span()
            if span and span.is_recording():
                trace_id = str(span.get_span_context().trace_id)
        
        # Build log entry
        log_entry = {
            "timestamp": datetime.now(timezone.utc),
            "level": level.upper(),
            "service": self.service_name,
            "category": category.upper(),
            "severity": severity.upper(),
            "message": message,
            "details": details,
            "trace_id": trace_id,
            "request_id": request_id,
            "user_id": user_id,
            "endpoint": endpoint,
            "method": method,
            "status_code": status_code,
            "duration_ms": duration_ms,
            "error_code": error_code,
            "stack_trace": stack_trace,
            "context": context or {},
            **kwargs
        }
        
        # Log to console
        self.logger.log(
            getattr(logging, level.upper()),
            json.dumps(log_entry, default=str)
        )
        
        # Store in database if pool available
        if self.db_pool:
            try:
                await self._store_in_database(log_entry)
            except Exception as e:
                # Fallback logging if database fails
                self.logger.error(f"Failed to store log in database: {e}")
    
    async def _store_in_database(self, log_entry: Dict[str, Any]):
        """Store log entry in database"""
        async with self.db_pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO logging.application_logs (
                    timestamp, level, service, category, severity, message, details,
                    trace_id, request_id, user_id, endpoint, method, status_code,
                    duration_ms, error_code, stack_trace, context, environment,
                    version, host_name
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18, $19, $20)
            """, 
                log_entry.get("timestamp"),
                log_entry.get("level"),
                log_entry.get("service"),
                log_entry.get("category"),
                log_entry.get("severity"),
                log_entry.get("message"),
                log_entry.get("details"),
                log_entry.get("trace_id"),
                log_entry.get("request_id"),
                log_entry.get("user_id"),
                log_entry.get("endpoint"),
                log_entry.get("method"),
                log_entry.get("status_code"),
                log_entry.get("duration_ms"),
                log_entry.get("error_code"),
                log_entry.get("stack_trace"),
                json.dumps(log_entry.get("context", {})),
                log_entry.get("environment", "production"),
                log_entry.get("version"),
                log_entry.get("host_name")
            )
    
    async def error(self, message: str, exc: Exception = None, **kwargs):
        """Log error with exception details"""
        stack_trace = None
        error_code = None
        category = kwargs.pop("category", "SYSTEM")
        severity = kwargs.pop("severity", "HIGH")
        
        if exc:
            stack_trace = traceback.format_exc()
            if isinstance(exc, TaylorDashError):
                error_code = exc.code
                category = exc.category
                severity = exc.severity
        
        await self.log(
            "ERROR", category, severity, message,
            details=str(exc) if exc else None,
            error_code=error_code,
            stack_trace=stack_trace,
            **kwargs
        )
    
    async def warn(self, message: str, **kwargs):
        """Log warning message"""
        category = kwargs.pop("category", "SYSTEM")
        severity = kwargs.pop("severity", "MEDIUM")
        await self.log("WARN", category, severity, message, **kwargs)
    
    async def info(self, message: str, **kwargs):
        """Log info message"""
        category = kwargs.pop("category", "SYSTEM")
        severity = kwargs.pop("severity", "INFO")
        await self.log("INFO", category, severity, message, **kwargs)
    
    async def debug(self, message: str, **kwargs):
        """Log debug message"""
        category = kwargs.pop("category", "SYSTEM")
        severity = kwargs.pop("severity", "LOW")
        await self.log("DEBUG", category, severity, message, **kwargs)

class StructuredFormatter(logging.Formatter):
    """JSON formatter for structured logging"""
    
    def format(self, record):
        try:
            # Try to parse as JSON first - if successful, it's already structured
            parsed_data = json.loads(record.getMessage())
            # If it's already a dict/JSON, serialize it back to string for logging
            return json.dumps(parsed_data, default=str)
        except (json.JSONDecodeError, TypeError):
            # Fallback to standard formatting - create structured log and serialize to JSON string
            fallback_entry = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "level": record.levelname,
                "service": "taylordash-backend",
                "category": "SYSTEM",
                "severity": "INFO",
                "message": record.getMessage(),
                "logger_name": record.name,
                "module": record.module,
                "function": record.funcName,
                "line": record.lineno
            }
            return json.dumps(fallback_entry, default=str)

# Request context manager for correlation
@asynccontextmanager
async def request_context(request_id: str = None, user_id: str = None):
    """Context manager for request-scoped logging"""
    if not request_id:
        request_id = str(uuid.uuid4())
    
    # Store in context (this would typically use contextvars)
    context = {
        "request_id": request_id,
        "user_id": user_id,
        "start_time": datetime.now(timezone.utc)
    }
    
    try:
        yield context
    finally:
        # Log request completion
        duration = (datetime.now(timezone.utc) - context["start_time"]).total_seconds() * 1000
        # Additional cleanup can be done here

# Utility functions
def get_client_info(request) -> Dict[str, Any]:
    """Extract client information from request"""
    return {
        "user_agent": request.headers.get("user-agent"),
        "client_ip": request.client.host if request.client else None,
        "referrer": request.headers.get("referer"),
        "accept_language": request.headers.get("accept-language")
    }

def sanitize_sensitive_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Remove sensitive information from logs"""
    sensitive_keys = {
        "password", "token", "api_key", "secret", "authorization",
        "x-api-key", "cookie", "session"
    }
    
    sanitized = {}
    for key, value in data.items():
        if key.lower() in sensitive_keys:
            sanitized[key] = "[REDACTED]"
        elif isinstance(value, dict):
            sanitized[key] = sanitize_sensitive_data(value)
        else:
            sanitized[key] = value
    
    return sanitized

def extract_error_info(exc: Exception) -> Dict[str, Any]:
    """Extract detailed error information"""
    return {
        "error_type": type(exc).__name__,
        "error_message": str(exc),
        "error_module": exc.__class__.__module__,
        "error_args": exc.args,
        "stack_trace": traceback.format_exc()
    }

# Global logger instance (will be initialized with db_pool)
app_logger: Optional[StructuredLogger] = None

def get_logger() -> StructuredLogger:
    """Get global logger instance"""
    global app_logger
    if app_logger is None:
        app_logger = StructuredLogger("taylordash-backend")
    return app_logger

def init_logger(db_pool: asyncpg.Pool):
    """Initialize global logger with database pool"""
    global app_logger
    app_logger = StructuredLogger("taylordash-backend", db_pool)
    return app_logger

# Decorators for automatic logging
def log_api_call(category: str = "API"):
    """Decorator to automatically log API calls"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            start_time = datetime.now(timezone.utc)
            logger = get_logger()
            
            try:
                result = await func(*args, **kwargs)
                duration = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
                
                await logger.info(
                    f"API call completed: {func.__name__}",
                    category=category,
                    duration_ms=int(duration),
                    function=func.__name__
                )
                
                return result
            except Exception as e:
                duration = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
                
                await logger.error(
                    f"API call failed: {func.__name__}",
                    exc=e,
                    category=category,
                    duration_ms=int(duration),
                    function=func.__name__
                )
                raise
        
        return wrapper
    return decorator