"""
CORS configuration for TaylorDash backend
Supports both production (https://tracker.local) and development (localhost:5173) origins
"""
import os
from typing import List
from fastapi.middleware.cors import CORSMiddleware

# Environment-based configuration
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

# Production origins
PRODUCTION_ORIGINS = [
    "https://tracker.local"
]

# Development origins
DEVELOPMENT_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",  # Additional common dev ports
    "http://127.0.0.1:3000"
]

def get_cors_origins() -> List[str]:
    """
    Get allowed CORS origins based on environment
    
    Returns:
        List of allowed origins
    """
    if ENVIRONMENT == "production":
        return PRODUCTION_ORIGINS
    elif ENVIRONMENT == "development":
        return PRODUCTION_ORIGINS + DEVELOPMENT_ORIGINS
    else:
        # For testing or other environments, allow both
        return PRODUCTION_ORIGINS + DEVELOPMENT_ORIGINS

def get_cors_config() -> dict:
    """
    Get CORS configuration for FastAPI middleware
    
    Returns:
        Dictionary with CORS configuration
    """
    return {
        "allow_origins": get_cors_origins(),
        "allow_credentials": True,
        "allow_methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": [
            "Authorization",
            "Content-Type",
            "Accept",
            "Origin",
            "User-Agent",
            "X-Requested-With",
            "X-CSRF-Token"
        ],
        "expose_headers": [
            "Content-Length",
            "Content-Type"
        ]
    }

def configure_cors(app):
    """
    Configure CORS middleware for FastAPI application
    
    Args:
        app: FastAPI application instance
    """
    cors_config = get_cors_config()
    
    app.add_middleware(
        CORSMiddleware,
        **cors_config
    )
    
    # Log CORS configuration for debugging
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"CORS configured for environment: {ENVIRONMENT}")
    logger.info(f"Allowed origins: {cors_config['allow_origins']}")