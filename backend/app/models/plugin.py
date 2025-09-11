"""
Plugin data models and security schemas
"""
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, HttpUrl, validator
import re


class PluginStatus(str, Enum):
    """Plugin installation status"""
    PENDING = "pending"
    INSTALLING = "installing"
    INSTALLED = "installed"
    FAILED = "failed"
    UPDATING = "updating"
    UNINSTALLING = "uninstalling"
    DISABLED = "disabled"


class PluginType(str, Enum):
    """Plugin type categories"""
    UI = "ui"
    DATA = "data"
    INTEGRATION = "integration"
    SYSTEM = "system"


class SecurityPermission(str, Enum):
    """Security permissions for plugins"""
    # API access permissions
    READ_PROJECTS = "read:projects"
    WRITE_PROJECTS = "write:projects"
    READ_EVENTS = "read:events"
    PUBLISH_EVENTS = "publish:events"
    READ_LOGS = "read:logs"
    READ_SYSTEM = "read:system"
    
    # Network access permissions
    NETWORK_HTTP = "network:http"
    NETWORK_WEBSOCKET = "network:websocket"
    
    # Storage permissions
    LOCAL_STORAGE = "storage:local"
    
    # Plugin communication
    PLUGIN_MESSAGING = "plugin:messaging"


class PluginManifest(BaseModel):
    """
    Plugin manifest schema - must be present in plugin.json
    Defines plugin metadata, security requirements, and dependencies
    """
    # Basic metadata
    id: str = Field(..., description="Unique plugin identifier", pattern=r"^[a-z0-9-]+$")
    name: str = Field(..., min_length=1, max_length=100, description="Human-readable plugin name")
    version: str = Field(..., description="Semantic version", pattern=r"^\d+\.\d+\.\d+(-[a-zA-Z0-9.-]+)?$")
    description: str = Field(..., min_length=1, max_length=500, description="Plugin description")
    author: str = Field(..., min_length=1, max_length=100, description="Plugin author")
    homepage: Optional[HttpUrl] = Field(None, description="Plugin homepage URL")
    repository: HttpUrl = Field(..., description="Plugin GitHub repository URL")
    
    # Plugin configuration
    type: PluginType = Field(..., description="Plugin type category")
    kind: str = Field(..., description="Legacy compatibility - ui/data/integration")
    entry_point: str = Field(..., description="Main HTML file path", pattern=r"^[a-zA-Z0-9._/-]+\.html$")
    
    # Security declarations
    permissions: List[SecurityPermission] = Field(default_factory=list, description="Required permissions")
    api_endpoints: List[str] = Field(default_factory=list, description="API endpoints this plugin will access")
    allowed_origins: List[str] = Field(default_factory=list, description="Allowed origins for network requests")
    
    # Dependencies
    taylordash_version: str = Field(..., description="Compatible TaylorDash version", pattern=r"^[~^]?\d+\.\d+\.\d+$")
    dependencies: Dict[str, str] = Field(default_factory=dict, description="Plugin dependencies")
    
    # Installation configuration
    install_hooks: Optional[Dict[str, str]] = Field(default_factory=dict, description="Installation lifecycle hooks")
    config_schema: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Configuration schema")
    
    @validator('id')
    def validate_id(cls, v):
        """Validate plugin ID format"""
        if not re.match(r'^[a-z0-9-]+$', v):
            raise ValueError('Plugin ID must contain only lowercase letters, numbers, and hyphens')
        if len(v) < 3 or len(v) > 50:
            raise ValueError('Plugin ID must be between 3 and 50 characters')
        return v
    
    @validator('api_endpoints', each_item=True)
    def validate_api_endpoints(cls, v):
        """Validate API endpoints format"""
        if not v.startswith('/api/v1/'):
            raise ValueError('API endpoints must start with /api/v1/')
        return v
    
    @validator('repository')
    def validate_repository_url(cls, v):
        """Validate GitHub repository URL"""
        if not str(v).startswith('https://github.com/'):
            raise ValueError('Repository must be a GitHub URL')
        return v


class PluginInstallRequest(BaseModel):
    """Plugin installation request"""
    repository_url: HttpUrl = Field(..., description="GitHub repository URL")
    version: Optional[str] = Field(None, description="Specific version to install (defaults to latest)")
    force: bool = Field(False, description="Force reinstall if already installed")
    
    @validator('repository_url')
    def validate_github_url(cls, v):
        """Validate GitHub repository URL"""
        if not str(v).startswith('https://github.com/'):
            raise ValueError('Only GitHub repositories are supported')
        if not re.match(r'https://github\.com/[a-zA-Z0-9._-]+/[a-zA-Z0-9._-]+/?$', str(v)):
            raise ValueError('Invalid GitHub repository URL format')
        return v


class PluginInstallResponse(BaseModel):
    """Plugin installation response"""
    status: str = Field(..., description="Installation status")
    plugin_id: str = Field(..., description="Installed plugin ID")
    message: str = Field(..., description="Installation message")
    installation_id: str = Field(..., description="Installation tracking ID")


class PluginInfo(BaseModel):
    """Installed plugin information"""
    id: str = Field(..., description="Plugin ID")
    name: str = Field(..., description="Plugin name")
    version: str = Field(..., description="Installed version")
    description: str = Field(..., description="Plugin description")
    author: str = Field(..., description="Plugin author")
    type: PluginType = Field(..., description="Plugin type")
    status: PluginStatus = Field(..., description="Installation status")
    repository_url: str = Field(..., description="GitHub repository URL")
    installed_at: datetime = Field(..., description="Installation timestamp")
    last_updated: Optional[datetime] = Field(None, description="Last update timestamp")
    config: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Plugin configuration")
    permissions: List[SecurityPermission] = Field(..., description="Granted permissions")
    
    # Security monitoring
    security_violations: int = Field(0, description="Count of security violations")
    last_violation: Optional[datetime] = Field(None, description="Last security violation timestamp")


class PluginSecurityViolation(BaseModel):
    """Security violation record"""
    plugin_id: str = Field(..., description="Plugin that violated security")
    violation_type: str = Field(..., description="Type of violation")
    description: str = Field(..., description="Violation description")
    severity: str = Field(..., description="Violation severity: low/medium/high/critical")
    timestamp: datetime = Field(..., description="When violation occurred")
    context: Dict[str, Any] = Field(..., description="Violation context data")


class PluginUpdate(BaseModel):
    """Plugin update information"""
    plugin_id: str = Field(..., description="Plugin to update")
    target_version: Optional[str] = Field(None, description="Target version (latest if not specified)")
    force: bool = Field(False, description="Force update even if version is lower")


class PluginListResponse(BaseModel):
    """Plugin list response"""
    plugins: List[PluginInfo] = Field(..., description="Installed plugins")
    total: int = Field(..., description="Total number of plugins")
    available_updates: List[str] = Field(default_factory=list, description="Plugins with available updates")


class PluginHealthCheck(BaseModel):
    """Plugin health check result"""
    plugin_id: str = Field(..., description="Plugin ID")
    status: str = Field(..., description="Health status: healthy/degraded/unhealthy")
    message: str = Field(..., description="Health check message")
    last_check: datetime = Field(..., description="Last health check timestamp")
    response_time: Optional[float] = Field(None, description="Response time in milliseconds")
    security_score: int = Field(..., ge=0, le=100, description="Security score 0-100")


class PluginConfiguration(BaseModel):
    """Plugin configuration update"""
    plugin_id: str = Field(..., description="Plugin ID")
    config: Dict[str, Any] = Field(..., description="Configuration values")
    validate_schema: bool = Field(True, description="Validate against plugin's config schema")