"""
Plugin Management API Router
Secure plugin installation, management, and monitoring endpoints
"""
import json
import logging
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import JSONResponse

from ..database import get_db_pool
from ..security import verify_api_key
from ..models.plugin import (
    PluginInstallRequest, PluginInstallResponse, PluginInfo, 
    PluginUpdate, PluginListResponse, PluginHealthCheck,
    PluginConfiguration, PluginSecurityViolation
)
from ..services.plugin_installer import PluginInstaller
from ..services.plugin_security import PluginSecurityValidator


logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter(prefix="/api/v1/plugins", tags=["plugins"])

# Plugin installation directory
PLUGINS_DIR = Path(__file__).parent.parent.parent / "plugins"


async def get_plugin_installer() -> PluginInstaller:
    """Get plugin installer instance"""
    db_pool = await get_db_pool()
    return PluginInstaller(db_pool, PLUGINS_DIR)


async def get_security_validator() -> PluginSecurityValidator:
    """Get plugin security validator instance"""
    db_pool = await get_db_pool()
    return PluginSecurityValidator(db_pool)


@router.post("/install", response_model=PluginInstallResponse, status_code=status.HTTP_202_ACCEPTED)
async def install_plugin(
    request: PluginInstallRequest,
    api_key: str = Depends(verify_api_key),
    installer: PluginInstaller = Depends(get_plugin_installer)
) -> PluginInstallResponse:
    """
    Install a plugin from GitHub repository
    
    This endpoint performs comprehensive security validation before installation:
    - Validates plugin manifest and structure
    - Performs static code analysis for malicious patterns
    - Checks permissions and API access requirements  
    - Validates iframe security configuration
    - Ensures dependency compatibility
    """
    try:
        logger.info(f"Plugin installation requested: {request.repository_url}")
        
        # Perform installation with security validation
        result = await installer.install_plugin(request)
        
        # Log installation attempt
        if result.status == "installed":
            logger.info(f"Plugin {result.plugin_id} installed successfully")
        else:
            logger.warning(f"Plugin installation failed: {result.message}")
        
        return result
        
    except Exception as e:
        logger.error(f"Plugin installation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Plugin installation failed: {str(e)}"
        )


@router.get("/list", response_model=PluginListResponse)
async def list_plugins(
    status_filter: Optional[str] = Query(None, description="Filter by plugin status"),
    type_filter: Optional[str] = Query(None, description="Filter by plugin type"),
    api_key: str = Depends(verify_api_key),
    installer: PluginInstaller = Depends(get_plugin_installer)
) -> PluginListResponse:
    """
    List all installed plugins with status and security information
    """
    try:
        plugins = await installer.list_plugins()
        
        # Apply filters
        if status_filter:
            plugins = [p for p in plugins if p.status.value == status_filter]
        
        if type_filter:
            plugins = [p for p in plugins if p.type.value == type_filter]
        
        # Check for available updates (simplified for now)
        available_updates = []
        # TODO: Implement update checking logic
        
        return PluginListResponse(
            plugins=plugins,
            total=len(plugins),
            available_updates=available_updates
        )
        
    except Exception as e:
        logger.error(f"Error listing plugins: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list plugins: {str(e)}"
        )


@router.get("/{plugin_id}", response_model=PluginInfo)
async def get_plugin(
    plugin_id: str,
    api_key: str = Depends(verify_api_key),
    installer: PluginInstaller = Depends(get_plugin_installer)
) -> PluginInfo:
    """
    Get detailed information about a specific plugin
    """
    try:
        plugins = await installer.list_plugins()
        plugin = next((p for p in plugins if p.id == plugin_id), None)
        
        if not plugin:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Plugin {plugin_id} not found"
            )
        
        return plugin
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting plugin {plugin_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get plugin information: {str(e)}"
        )


@router.delete("/{plugin_id}")
async def uninstall_plugin(
    plugin_id: str,
    api_key: str = Depends(verify_api_key),
    installer: PluginInstaller = Depends(get_plugin_installer)
) -> JSONResponse:
    """
    Uninstall a plugin and clean up all associated data
    """
    try:
        result = await installer.uninstall_plugin(plugin_id)
        
        if result["success"]:
            logger.info(f"Plugin {plugin_id} uninstalled successfully")
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"message": result["message"]}
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["message"]
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uninstalling plugin {plugin_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to uninstall plugin: {str(e)}"
        )


@router.put("/{plugin_id}/update")
async def update_plugin(
    plugin_id: str,
    update_request: PluginUpdate,
    api_key: str = Depends(verify_api_key),
    installer: PluginInstaller = Depends(get_plugin_installer)
) -> JSONResponse:
    """
    Update a plugin to the latest version or specified version
    """
    try:
        # Ensure plugin_id matches the request
        update_request.plugin_id = plugin_id
        
        result = await installer.update_plugin(update_request)
        
        if result["success"]:
            logger.info(f"Plugin {plugin_id} updated successfully")
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"message": result["message"]}
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["message"]
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating plugin {plugin_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update plugin: {str(e)}"
        )


@router.get("/{plugin_id}/health", response_model=PluginHealthCheck)
async def get_plugin_health(
    plugin_id: str,
    api_key: str = Depends(verify_api_key),
    installer: PluginInstaller = Depends(get_plugin_installer)
) -> PluginHealthCheck:
    """
    Get plugin health status including security score and violations
    """
    try:
        health_data = await installer.get_plugin_health(plugin_id)
        
        if health_data.get("status") == "error":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=health_data.get("message", "Plugin not found")
            )
        
        return PluginHealthCheck(
            plugin_id=plugin_id,
            status=health_data["status"],
            message=f"Security score: {health_data.get('security_score', 0)}/100",
            last_check=health_data["last_check"],
            response_time=None,  # TODO: Implement response time checking
            security_score=health_data.get("security_score", 0)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting plugin health {plugin_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get plugin health: {str(e)}"
        )


@router.post("/{plugin_id}/config")
async def update_plugin_config(
    plugin_id: str,
    config_update: PluginConfiguration,
    api_key: str = Depends(verify_api_key)
) -> JSONResponse:
    """
    Update plugin configuration with validation
    """
    try:
        # Ensure plugin_id matches
        config_update.plugin_id = plugin_id
        
        db_pool = await get_db_pool()
        async with db_pool.acquire() as conn:
            # Verify plugin exists
            plugin = await conn.fetchrow(
                "SELECT id, manifest FROM plugins WHERE id = $1", plugin_id
            )
            
            if not plugin:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Plugin {plugin_id} not found"
                )
            
            # TODO: Validate config against plugin's schema if validate_schema is True
            
            # Update configuration
            await conn.execute(
                "UPDATE plugins SET config = $1, updated_at = NOW() WHERE id = $2",
                json.dumps(config_update.config), plugin_id
            )
            
            # Log configuration change
            await conn.execute("""
                INSERT INTO plugin_config_history (plugin_id, new_config, changed_by, timestamp)
                VALUES ($1, $2, $3, NOW())
            """, plugin_id, json.dumps(config_update.config), "api_user")  # TODO: Get actual user
            
            logger.info(f"Configuration updated for plugin {plugin_id}")
            
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"message": "Plugin configuration updated successfully"}
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating plugin config {plugin_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update plugin configuration: {str(e)}"
        )


@router.get("/{plugin_id}/security/violations", response_model=List[PluginSecurityViolation])
async def get_security_violations(
    plugin_id: str,
    limit: int = Query(50, ge=1, le=100),
    api_key: str = Depends(verify_api_key)
) -> List[PluginSecurityViolation]:
    """
    Get security violations for a plugin
    """
    try:
        db_pool = await get_db_pool()
        async with db_pool.acquire() as conn:
            violations = await conn.fetch("""
                SELECT plugin_id, violation_type, description, severity, context, timestamp
                FROM plugin_security_violations 
                WHERE plugin_id = $1 
                ORDER BY timestamp DESC 
                LIMIT $2
            """, plugin_id, limit)
            
            return [
                PluginSecurityViolation(
                    plugin_id=v['plugin_id'],
                    violation_type=v['violation_type'],
                    description=v['description'],
                    severity=v['severity'],
                    timestamp=v['timestamp'],
                    context=json.loads(v['context']) if v['context'] else {}
                )
                for v in violations
            ]
            
    except Exception as e:
        logger.error(f"Error getting security violations for {plugin_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get security violations: {str(e)}"
        )


@router.post("/{plugin_id}/security/scan")
async def scan_plugin_security(
    plugin_id: str,
    api_key: str = Depends(verify_api_key),
    validator: PluginSecurityValidator = Depends(get_security_validator)
) -> JSONResponse:
    """
    Perform a comprehensive security scan on an installed plugin
    """
    try:
        health_data = await validator.check_runtime_security(plugin_id)
        
        if health_data.get("status") == "error":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=health_data.get("message", "Plugin not found")
            )
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "message": "Security scan completed",
                "security_score": health_data.get("security_score", 0),
                "status": health_data["status"],
                "recent_violations": health_data.get("recent_violations", 0)
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error scanning plugin security {plugin_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to scan plugin security: {str(e)}"
        )


@router.get("/stats/overview")
async def get_plugin_stats(
    api_key: str = Depends(verify_api_key)
) -> JSONResponse:
    """
    Get plugin system statistics and overview
    """
    try:
        db_pool = await get_db_pool()
        async with db_pool.acquire() as conn:
            # Get basic stats
            stats = await conn.fetchrow("""
                SELECT 
                    COUNT(*) as total_plugins,
                    COUNT(CASE WHEN status = 'installed' THEN 1 END) as installed_plugins,
                    COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed_plugins,
                    COUNT(CASE WHEN security_violations > 0 THEN 1 END) as plugins_with_violations,
                    COALESCE(AVG(security_score), 100) as avg_security_score
                FROM plugins
            """)
            
            # Get recent violations
            recent_violations = await conn.fetch("""
                SELECT plugin_id, violation_type, severity, timestamp
                FROM plugin_security_violations
                ORDER BY timestamp DESC
                LIMIT 10
            """)
            
            return JSONResponse(content={
                "total_plugins": stats['total_plugins'],
                "installed_plugins": stats['installed_plugins'],
                "failed_plugins": stats['failed_plugins'],
                "plugins_with_violations": stats['plugins_with_violations'],
                "average_security_score": round(float(stats['avg_security_score']), 1),
                "recent_violations": [
                    {
                        "plugin_id": v['plugin_id'],
                        "type": v['violation_type'],
                        "severity": v['severity'],
                        "timestamp": v['timestamp'].isoformat()
                    }
                    for v in recent_violations
                ]
            })
            
    except Exception as e:
        logger.error(f"Error getting plugin stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get plugin statistics: {str(e)}"
        )


@router.post("/registry/refresh")
async def refresh_plugin_registry(
    api_key: str = Depends(verify_api_key),
    installer: PluginInstaller = Depends(get_plugin_installer)
) -> JSONResponse:
    """
    Refresh the frontend plugin registry with current installed plugins
    """
    try:
        await installer._update_frontend_registry()
        
        logger.info("Plugin registry refreshed successfully")
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "Plugin registry refreshed successfully"}
        )
        
    except Exception as e:
        logger.error(f"Error refreshing plugin registry: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to refresh plugin registry: {str(e)}"
        )