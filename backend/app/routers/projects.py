"""
Projects API Router
RBAC-protected endpoints for project management
"""
import logging
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
import asyncpg

from ..auth import User, require_viewer, require_maintainer
from ..database import get_db_pool
from ..models import (
    Project, 
    ProjectCreate, 
    ProjectUpdate, 
    ProjectListResponse,
    ProjectStatus,
    APIResponse,
    ErrorResponse
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/projects", tags=["projects"])

@router.get(
    "/",
    response_model=ProjectListResponse,
    summary="List projects",
    description="Get a list of all projects. Requires viewer role or higher."
)
async def get_projects(
    status: Optional[ProjectStatus] = Query(None, description="Filter by project status"),
    limit: int = Query(50, ge=1, le=1000, description="Maximum number of projects to return"),
    offset: int = Query(0, ge=0, description="Number of projects to skip"),
    user: User = Depends(require_viewer)
) -> ProjectListResponse:
    """
    Get a list of projects with optional filtering and pagination.
    
    - **status**: Filter projects by status (new, active, completed, archived)
    - **limit**: Maximum number of projects to return (1-1000)
    - **offset**: Number of projects to skip for pagination
    
    Requires viewer role or higher.
    """
    try:
        db_pool = await get_db_pool()
        async with db_pool.acquire() as conn:
            # Build query with optional status filter
            query = """
                SELECT id, name, description, status, owner_id, metadata, created_at, updated_at
                FROM projects
            """
            params = []
            conditions = []
            
            if status:
                conditions.append(f"status = ${len(params) + 1}")
                params.append(status.value)
            
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            
            # Add ordering and pagination
            query += f" ORDER BY created_at DESC LIMIT ${len(params) + 1} OFFSET ${len(params) + 2}"
            params.extend([limit, offset])
            
            # Execute query
            rows = await conn.fetch(query, *params)
            
            # Get total count for pagination
            count_query = "SELECT COUNT(*) FROM projects"
            count_params = []
            if status:
                count_query += " WHERE status = $1"
                count_params.append(status.value)
            
            total = await conn.fetchval(count_query, *count_params)
            
            # Convert rows to Project models
            projects = []
            for row in rows:
                project = Project(
                    id=row["id"],
                    name=row["name"],
                    description=row["description"],
                    status=ProjectStatus(row["status"]),
                    owner_id=row["owner_id"],
                    metadata=row["metadata"] or {},
                    created_at=row["created_at"],
                    updated_at=row["updated_at"]
                )
                projects.append(project)
            
            logger.info(f"User {user.username} retrieved {len(projects)} projects (total: {total})")
            
            return ProjectListResponse(projects=projects, total=total)
            
    except Exception as e:
        logger.error(f"Failed to get projects: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve projects"
        )

@router.post(
    "/",
    response_model=Project,
    status_code=status.HTTP_201_CREATED,
    summary="Create project",
    description="Create a new project. Requires maintainer role or higher."
)
async def create_project(
    project_data: ProjectCreate,
    user: User = Depends(require_maintainer)
) -> Project:
    """
    Create a new project.
    
    - **name**: Project name (required, 1-255 characters)
    - **description**: Project description (optional, max 1000 characters)
    - **status**: Project status (defaults to 'new')
    - **metadata**: Additional project metadata (optional JSON object)
    
    Requires maintainer role or higher.
    """
    try:
        db_pool = await get_db_pool()
        async with db_pool.acquire() as conn:
            # Check if project with same name already exists
            existing = await conn.fetchval(
                "SELECT id FROM projects WHERE name = $1",
                project_data.name
            )
            
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Project with name '{project_data.name}' already exists"
                )
            
            # Insert new project
            now = datetime.utcnow()
            row = await conn.fetchrow("""
                INSERT INTO projects (name, description, status, owner_id, metadata, created_at, updated_at)
                VALUES ($1, $2, $3, $4, $5, $6, $7)
                RETURNING id, name, description, status, owner_id, metadata, created_at, updated_at
            """, 
                project_data.name,
                project_data.description,
                project_data.status.value,
                user.sub,  # Set current user as owner
                project_data.metadata,
                now,
                now
            )
            
            # Create Project model from database row
            project = Project(
                id=row["id"],
                name=row["name"],
                description=row["description"],
                status=ProjectStatus(row["status"]),
                owner_id=row["owner_id"],
                metadata=row["metadata"] or {},
                created_at=row["created_at"],
                updated_at=row["updated_at"]
            )
            
            logger.info(f"User {user.username} created project '{project.name}' (ID: {project.id})")
            
            return project
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create project: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create project"
        )

@router.get(
    "/{project_id}",
    response_model=Project,
    summary="Get project by ID",
    description="Get a specific project by ID. Requires viewer role or higher."
)
async def get_project(
    project_id: UUID,
    user: User = Depends(require_viewer)
) -> Project:
    """
    Get a specific project by ID.
    
    - **project_id**: UUID of the project to retrieve
    
    Requires viewer role or higher.
    """
    try:
        db_pool = await get_db_pool()
        async with db_pool.acquire() as conn:
            row = await conn.fetchrow("""
                SELECT id, name, description, status, owner_id, metadata, created_at, updated_at
                FROM projects
                WHERE id = $1
            """, project_id)
            
            if not row:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Project with ID {project_id} not found"
                )
            
            project = Project(
                id=row["id"],
                name=row["name"],
                description=row["description"],
                status=ProjectStatus(row["status"]),
                owner_id=row["owner_id"],
                metadata=row["metadata"] or {},
                created_at=row["created_at"],
                updated_at=row["updated_at"]
            )
            
            logger.info(f"User {user.username} retrieved project '{project.name}' (ID: {project.id})")
            
            return project
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get project {project_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve project"
        )

@router.put(
    "/{project_id}",
    response_model=Project,
    summary="Update project",
    description="Update an existing project. Requires maintainer role or higher."
)
async def update_project(
    project_id: UUID,
    project_data: ProjectUpdate,
    user: User = Depends(require_maintainer)
) -> Project:
    """
    Update an existing project.
    
    - **project_id**: UUID of the project to update
    - **name**: New project name (optional)
    - **description**: New project description (optional)
    - **status**: New project status (optional)
    - **metadata**: New project metadata (optional)
    
    Requires maintainer role or higher.
    """
    try:
        db_pool = await get_db_pool()
        async with db_pool.acquire() as conn:
            # Check if project exists
            existing = await conn.fetchrow(
                "SELECT id, name FROM projects WHERE id = $1",
                project_id
            )
            
            if not existing:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Project with ID {project_id} not found"
                )
            
            # Build update query dynamically based on provided fields
            update_fields = []
            params = []
            param_count = 0
            
            if project_data.name is not None:
                param_count += 1
                update_fields.append(f"name = ${param_count}")
                params.append(project_data.name)
            
            if project_data.description is not None:
                param_count += 1
                update_fields.append(f"description = ${param_count}")
                params.append(project_data.description)
            
            if project_data.status is not None:
                param_count += 1
                update_fields.append(f"status = ${param_count}")
                params.append(project_data.status.value)
            
            if project_data.metadata is not None:
                param_count += 1
                update_fields.append(f"metadata = ${param_count}")
                params.append(project_data.metadata)
            
            if not update_fields:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No fields provided for update"
                )
            
            # Add updated_at
            param_count += 1
            update_fields.append(f"updated_at = ${param_count}")
            params.append(datetime.utcnow())
            
            # Add project_id for WHERE clause
            param_count += 1
            params.append(project_id)
            
            query = f"""
                UPDATE projects 
                SET {', '.join(update_fields)}
                WHERE id = ${param_count}
                RETURNING id, name, description, status, owner_id, metadata, created_at, updated_at
            """
            
            row = await conn.fetchrow(query, *params)
            
            project = Project(
                id=row["id"],
                name=row["name"],
                description=row["description"],
                status=ProjectStatus(row["status"]),
                owner_id=row["owner_id"],
                metadata=row["metadata"] or {},
                created_at=row["created_at"],
                updated_at=row["updated_at"]
            )
            
            logger.info(f"User {user.username} updated project '{project.name}' (ID: {project.id})")
            
            return project
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update project {project_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update project"
        )

@router.delete(
    "/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete project",
    description="Delete a project and all associated data. Requires maintainer role or higher."
)
async def delete_project(
    project_id: UUID,
    user: User = Depends(require_maintainer)
):
    """
    Delete a project and all associated data (components, tasks, etc.).
    
    - **project_id**: UUID of the project to delete
    
    Requires maintainer role or higher.
    """
    try:
        db_pool = await get_db_pool()
        async with db_pool.acquire() as conn:
            # Check if project exists
            existing = await conn.fetchrow(
                "SELECT id, name FROM projects WHERE id = $1",
                project_id
            )
            
            if not existing:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Project with ID {project_id} not found"
                )
            
            # Delete project (CASCADE will handle related records)
            deleted_count = await conn.fetchval(
                "DELETE FROM projects WHERE id = $1",
                project_id
            )
            
            if deleted_count == 0:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Project with ID {project_id} not found"
                )
            
            logger.info(f"User {user.username} deleted project '{existing['name']}' (ID: {project_id})")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete project {project_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete project"
        )