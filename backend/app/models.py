"""
Pydantic models for TaylorDash API
Data validation and serialization schemas
"""
from datetime import datetime
from typing import Optional, Dict, Any, List
from uuid import UUID
from enum import Enum

from pydantic import BaseModel, Field, ConfigDict

# Project Models
class ProjectStatus(str, Enum):
    NEW = "new"
    ACTIVE = "active"
    COMPLETED = "completed"
    ARCHIVED = "archived"

class ProjectBase(BaseModel):
    """Base project model"""
    name: str = Field(..., min_length=1, max_length=255, description="Project name")
    description: Optional[str] = Field(None, max_length=1000, description="Project description")
    status: ProjectStatus = Field(default=ProjectStatus.NEW, description="Project status")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional project metadata")

class ProjectCreate(ProjectBase):
    """Project creation request model"""
    pass

class ProjectUpdate(BaseModel):
    """Project update request model"""
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Project name")
    description: Optional[str] = Field(None, max_length=1000, description="Project description")
    status: Optional[ProjectStatus] = Field(None, description="Project status")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional project metadata")

class Project(ProjectBase):
    """Full project model with database fields"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID = Field(..., description="Project ID")
    owner_id: Optional[UUID] = Field(None, description="Project owner ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

class ProjectListResponse(BaseModel):
    """Response model for project list"""
    projects: List[Project] = Field(..., description="List of projects")
    total: int = Field(..., description="Total number of projects")

# Component Models
class ComponentStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"

class ComponentPosition(BaseModel):
    """Component position on canvas"""
    x: float = Field(..., description="X coordinate")
    y: float = Field(..., description="Y coordinate")

class ComponentBase(BaseModel):
    """Base component model"""
    name: str = Field(..., min_length=1, max_length=255, description="Component name")
    type: Optional[str] = Field(None, max_length=100, description="Component type")
    status: ComponentStatus = Field(default=ComponentStatus.PENDING, description="Component status")
    progress: int = Field(default=0, ge=0, le=100, description="Completion progress percentage")
    position: Optional[ComponentPosition] = Field(None, description="Component position")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional component metadata")

class ComponentCreate(ComponentBase):
    """Component creation request model"""
    project_id: UUID = Field(..., description="Parent project ID")

class ComponentUpdate(BaseModel):
    """Component update request model"""
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Component name")
    type: Optional[str] = Field(None, max_length=100, description="Component type")
    status: Optional[ComponentStatus] = Field(None, description="Component status")
    progress: Optional[int] = Field(None, ge=0, le=100, description="Completion progress percentage")
    position: Optional[ComponentPosition] = Field(None, description="Component position")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional component metadata")

class Component(ComponentBase):
    """Full component model with database fields"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID = Field(..., description="Component ID")
    project_id: UUID = Field(..., description="Parent project ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

# Task Models
class TaskStatus(str, Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    DONE = "done"

class TaskBase(BaseModel):
    """Base task model"""
    name: str = Field(..., min_length=1, max_length=255, description="Task name")
    description: Optional[str] = Field(None, max_length=1000, description="Task description")
    status: TaskStatus = Field(default=TaskStatus.TODO, description="Task status")
    assignee_id: Optional[UUID] = Field(None, description="Assigned user ID")
    due_date: Optional[datetime] = Field(None, description="Due date")

class TaskCreate(TaskBase):
    """Task creation request model"""
    component_id: UUID = Field(..., description="Parent component ID")

class TaskUpdate(BaseModel):
    """Task update request model"""
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Task name")
    description: Optional[str] = Field(None, max_length=1000, description="Task description")
    status: Optional[TaskStatus] = Field(None, description="Task status")
    assignee_id: Optional[UUID] = Field(None, description="Assigned user ID")
    due_date: Optional[datetime] = Field(None, description="Due date")

class Task(TaskBase):
    """Full task model with database fields"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID = Field(..., description="Task ID")
    component_id: UUID = Field(..., description="Parent component ID")
    completed_at: Optional[datetime] = Field(None, description="Completion timestamp")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

# API Response Models
class APIResponse(BaseModel):
    """Generic API response wrapper"""
    success: bool = Field(default=True, description="Operation success status")
    message: Optional[str] = Field(None, description="Response message")
    data: Optional[Any] = Field(None, description="Response data")

class ErrorResponse(BaseModel):
    """Error response model"""
    success: bool = Field(default=False, description="Operation success status")
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")

# Health Check Models
class ServiceHealth(BaseModel):
    """Service health status"""
    name: str = Field(..., description="Service name")
    ok: bool = Field(..., description="Service health status")
    detail: str = Field(..., description="Service detail/type")
    note: str = Field(..., description="Additional notes")

class StackHealth(BaseModel):
    """Stack health response"""
    services: List[ServiceHealth] = Field(..., description="List of service health statuses")

# Event Models (for MQTT integration)
class EventPayload(BaseModel):
    """Base event payload"""
    trace_id: str = Field(..., description="Event trace ID")
    ts: datetime = Field(..., description="Event timestamp")
    kind: str = Field(..., description="Event kind")
    idempotency_key: str = Field(..., description="Idempotency key")
    payload: Dict[str, Any] = Field(..., description="Event specific payload")

class EventResponse(BaseModel):
    """Event query response"""
    events: List[Dict[str, Any]] = Field(..., description="List of events")
    count: int = Field(..., description="Number of events returned")

class DLQEventResponse(BaseModel):
    """DLQ event query response"""
    dlq_events: List[Dict[str, Any]] = Field(..., description="List of DLQ events")
    count: int = Field(..., description="Number of DLQ events returned")

# Authentication Models (re-export from auth module)
class UserInfo(BaseModel):
    """User information model"""
    sub: str = Field(..., description="User subject (ID)")
    username: str = Field(..., description="Username")
    email: Optional[str] = Field(None, description="User email")
    roles: List[str] = Field(..., description="User roles")
    preferred_username: Optional[str] = Field(None, description="Preferred username")

# Pagination Models
class PaginationParams(BaseModel):
    """Pagination parameters"""
    page: int = Field(default=1, ge=1, description="Page number")
    limit: int = Field(default=50, ge=1, le=1000, description="Items per page")
    
class PaginatedResponse(BaseModel):
    """Paginated response wrapper"""
    items: List[Any] = Field(..., description="List of items")
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number")
    limit: int = Field(..., description="Items per page")
    pages: int = Field(..., description="Total number of pages")
    
    @property
    def has_next(self) -> bool:
        """Check if there's a next page"""
        return self.page < self.pages
    
    @property
    def has_prev(self) -> bool:
        """Check if there's a previous page"""
        return self.page > 1