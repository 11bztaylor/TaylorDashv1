"""
Plugin Installation and Lifecycle Management Service
Handles secure plugin installation, updates, and management from GitHub repositories
"""
import asyncio
import json
import logging
import os
import shutil
import tempfile
import uuid
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlparse

import aiohttp
import asyncpg

from ..models.plugin import (
    PluginManifest, PluginStatus, PluginInstallRequest, PluginInfo,
    PluginInstallResponse, PluginUpdate, SecurityPermission
)
from .plugin_security import PluginSecurityValidator


logger = logging.getLogger(__name__)


class PluginInstaller:
    """
    Secure plugin installation and lifecycle management
    """
    
    def __init__(self, db_pool: asyncpg.Pool, plugins_dir: Path):
        self.db_pool = db_pool
        self.plugins_dir = plugins_dir
        self.security_validator = PluginSecurityValidator(db_pool)
        
        # Ensure plugins directory exists
        self.plugins_dir.mkdir(parents=True, exist_ok=True)
        
        # GitHub API configuration
        self.github_api_base = "https://api.github.com"
        self.github_token = os.getenv("GITHUB_TOKEN")  # Optional for higher rate limits
    
    async def install_plugin(self, request: PluginInstallRequest) -> PluginInstallResponse:
        """
        Install a plugin from GitHub repository with comprehensive security validation
        """
        installation_id = str(uuid.uuid4())
        repository_url = str(request.repository_url).rstrip('/')
        
        try:
            logger.info(f"Starting plugin installation from {repository_url}")
            
            # 1. Extract repository information
            repo_owner, repo_name = self._parse_github_url(repository_url)
            
            # 2. Check if plugin is already installed
            if not request.force:
                existing = await self._check_existing_plugin(repository_url)
                if existing:
                    return PluginInstallResponse(
                        status="already_installed",
                        plugin_id=existing,
                        message=f"Plugin {existing} is already installed. Use force=true to reinstall.",
                        installation_id=installation_id
                    )
            
            # 3. Download and extract plugin
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                
                await self._update_installation_status(
                    installation_id, PluginStatus.INSTALLING, "Downloading plugin from GitHub"
                )
                
                success = await self._download_plugin(repo_owner, repo_name, request.version, temp_path)
                if not success:
                    raise Exception("Failed to download plugin from GitHub")
                
                # 4. Validate plugin security
                await self._update_installation_status(
                    installation_id, PluginStatus.INSTALLING, "Validating plugin security"
                )
                
                is_valid, validation_errors, manifest = await self.security_validator.validate_plugin_installation(
                    repository_url, temp_path
                )
                
                if not is_valid:
                    error_msg = "Plugin validation failed: " + "; ".join(validation_errors)
                    await self._update_installation_status(
                        installation_id, PluginStatus.FAILED, error_msg
                    )
                    raise Exception(error_msg)
                
                if not manifest:
                    raise Exception("Plugin manifest could not be parsed")
                
                # 5. Install plugin files
                await self._update_installation_status(
                    installation_id, PluginStatus.INSTALLING, "Installing plugin files"
                )
                
                plugin_install_dir = self.plugins_dir / manifest.id
                await self._install_plugin_files(temp_path, plugin_install_dir, manifest)
                
                # 6. Register plugin in database
                await self._register_plugin(
                    installation_id, manifest, repository_url, plugin_install_dir
                )
                
                # 7. Update frontend plugin registry
                await self._update_frontend_registry()
                
                logger.info(f"Successfully installed plugin {manifest.id}")
                
                return PluginInstallResponse(
                    status="installed",
                    plugin_id=manifest.id,
                    message=f"Plugin {manifest.name} installed successfully",
                    installation_id=installation_id
                )
        
        except Exception as e:
            logger.error(f"Plugin installation failed: {e}")
            await self._update_installation_status(
                installation_id, PluginStatus.FAILED, str(e)
            )
            
            return PluginInstallResponse(
                status="failed",
                plugin_id="",
                message=f"Installation failed: {str(e)}",
                installation_id=installation_id
            )
    
    def _parse_github_url(self, url: str) -> Tuple[str, str]:
        """Parse GitHub URL to extract owner and repository name"""
        parsed = urlparse(url)
        path_parts = parsed.path.strip('/').split('/')
        
        if len(path_parts) < 2:
            raise ValueError("Invalid GitHub repository URL")
        
        return path_parts[0], path_parts[1]
    
    async def _check_existing_plugin(self, repository_url: str) -> Optional[str]:
        """Check if plugin from repository is already installed"""
        try:
            async with self.db_pool.acquire() as conn:
                row = await conn.fetchrow(
                    "SELECT id FROM plugins WHERE repository_url = $1 AND status != $2",
                    repository_url, PluginStatus.FAILED.value
                )
                return row['id'] if row else None
        except Exception as e:
            logger.error(f"Error checking existing plugin: {e}")
            return None
    
    async def _download_plugin(self, owner: str, repo: str, version: Optional[str], temp_dir: Path) -> bool:
        """Download plugin from GitHub repository"""
        try:
            # Determine download URL
            if version:
                download_url = f"https://github.com/{owner}/{repo}/archive/refs/tags/{version}.zip"
            else:
                download_url = f"https://github.com/{owner}/{repo}/archive/refs/heads/main.zip"
            
            headers = {}
            if self.github_token:
                headers["Authorization"] = f"Bearer {self.github_token}"
            
            timeout = aiohttp.ClientTimeout(total=300)  # 5 minutes
            async with aiohttp.ClientSession(timeout=timeout, headers=headers) as session:
                async with session.get(download_url) as response:
                    if response.status != 200:
                        # Try 'master' branch if 'main' failed
                        if not version:
                            download_url = f"https://github.com/{owner}/{repo}/archive/refs/heads/master.zip"
                            async with session.get(download_url) as retry_response:
                                if retry_response.status != 200:
                                    logger.error(f"Failed to download from GitHub: {retry_response.status}")
                                    return False
                                response = retry_response
                        else:
                            logger.error(f"Failed to download from GitHub: {response.status}")
                            return False
                    
                    # Download and extract
                    zip_path = temp_dir / "plugin.zip"
                    with open(zip_path, 'wb') as f:
                        async for chunk in response.content.iter_chunked(8192):
                            f.write(chunk)
            
            # Extract ZIP file
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
            
            # Find the extracted directory (usually repo-branch format)
            extracted_dirs = [d for d in temp_dir.iterdir() if d.is_dir()]
            if not extracted_dirs:
                logger.error("No directories found after extraction")
                return False
            
            # Move contents to root of temp_dir
            extracted_dir = extracted_dirs[0]
            for item in extracted_dir.iterdir():
                shutil.move(str(item), str(temp_dir / item.name))
            
            # Clean up
            shutil.rmtree(extracted_dir)
            zip_path.unlink()
            
            return True
        
        except Exception as e:
            logger.error(f"Error downloading plugin: {e}")
            return False
    
    async def _install_plugin_files(self, source_dir: Path, install_dir: Path, manifest: PluginManifest) -> None:
        """Install plugin files to the plugins directory"""
        try:
            # Remove existing installation if it exists
            if install_dir.exists():
                shutil.rmtree(install_dir)
            
            # Copy plugin files
            shutil.copytree(source_dir, install_dir)
            
            # Set appropriate file permissions (read-only for security)
            for root, dirs, files in os.walk(install_dir):
                for file in files:
                    file_path = Path(root) / file
                    os.chmod(file_path, 0o644)
                for dir in dirs:
                    dir_path = Path(root) / dir
                    os.chmod(dir_path, 0o755)
            
            logger.info(f"Plugin files installed to {install_dir}")
        
        except Exception as e:
            logger.error(f"Error installing plugin files: {e}")
            raise
    
    async def _register_plugin(self, 
                             installation_id: str, 
                             manifest: PluginManifest, 
                             repository_url: str, 
                             install_dir: Path) -> None:
        """Register plugin in database"""
        try:
            async with self.db_pool.acquire() as conn:
                # Insert or update plugin record
                await conn.execute("""
                    INSERT INTO plugins (
                        id, name, version, description, author, type, kind,
                        repository_url, install_path, manifest, permissions,
                        status, installed_at, installation_id
                    ) VALUES (
                        $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14
                    )
                    ON CONFLICT (id) DO UPDATE SET
                        name = EXCLUDED.name,
                        version = EXCLUDED.version,
                        description = EXCLUDED.description,
                        author = EXCLUDED.author,
                        type = EXCLUDED.type,
                        kind = EXCLUDED.kind,
                        repository_url = EXCLUDED.repository_url,
                        install_path = EXCLUDED.install_path,
                        manifest = EXCLUDED.manifest,
                        permissions = EXCLUDED.permissions,
                        status = EXCLUDED.status,
                        last_updated = $13,
                        installation_id = EXCLUDED.installation_id
                """, 
                    manifest.id,
                    manifest.name,
                    manifest.version,
                    manifest.description,
                    manifest.author,
                    manifest.type.value,
                    manifest.kind,
                    repository_url,
                    str(install_dir),
                    json.dumps(manifest.dict()),
                    json.dumps([perm.value for perm in manifest.permissions]),
                    PluginStatus.INSTALLED.value,
                    datetime.now(timezone.utc),
                    installation_id
                )
                
                logger.info(f"Plugin {manifest.id} registered in database")
        
        except Exception as e:
            logger.error(f"Error registering plugin: {e}")
            raise
    
    async def _update_installation_status(self, installation_id: str, status: PluginStatus, message: str) -> None:
        """Update installation status"""
        try:
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO plugin_installations (id, status, message, updated_at)
                    VALUES ($1, $2, $3, $4)
                    ON CONFLICT (id) DO UPDATE SET
                        status = EXCLUDED.status,
                        message = EXCLUDED.message,
                        updated_at = EXCLUDED.updated_at
                """, installation_id, status.value, message, datetime.now(timezone.utc))
        except Exception as e:
            logger.error(f"Error updating installation status: {e}")
    
    async def _update_frontend_registry(self) -> None:
        """Update frontend plugin registry with installed plugins"""
        try:
            async with self.db_pool.acquire() as conn:
                plugins = await conn.fetch("""
                    SELECT id, name, version, description, type, kind, install_path, manifest
                    FROM plugins 
                    WHERE status = $1
                    ORDER BY name
                """, PluginStatus.INSTALLED.value)
                
                # Build registry data
                registry_plugins = []
                for plugin in plugins:
                    try:
                        manifest = json.loads(plugin['manifest'])
                        registry_plugins.append({
                            "id": plugin['id'],
                            "name": plugin['name'],
                            "version": plugin['version'],
                            "description": plugin['description'],
                            "kind": plugin['kind'],
                            "type": plugin['type'],
                            "path": f"/plugins/{plugin['id']}",
                            "entry_point": manifest.get('entry_point', 'index.html')
                        })
                    except Exception as e:
                        logger.warning(f"Error processing plugin {plugin['id']} for registry: {e}")
                
                # Write registry file
                registry_path = Path(__file__).parent.parent.parent.parent / "frontend" / "src" / "plugins" / "registry.ts"
                registry_content = f'''// Auto-generated plugin registry
// This file is automatically updated when plugins are installed/uninstalled

export interface Plugin {{
  id: string;
  name: string;
  version: string;
  description?: string;
  kind: 'ui' | 'data' | 'integration';
  type: string;
  path: string;
  entry_point?: string;
}}

export const PLUGINS: Plugin[] = {json.dumps(registry_plugins, indent=2)};

export function getPluginById(id: string): Plugin | null {{
  return PLUGINS.find(plugin => plugin.id === id) || null;
}}

export function getPluginsByKind(kind: Plugin['kind']): Plugin[] {{
  return PLUGINS.filter(plugin => plugin.kind === kind);
}}

export function getInstalledPluginsCount(): number {{
  return PLUGINS.length;
}}

// Plugin security and validation
export function isPluginSecure(pluginId: string): boolean {{
  // All installed plugins have passed security validation
  return PLUGINS.some(plugin => plugin.id === pluginId);
}}
'''
                
                registry_path.parent.mkdir(parents=True, exist_ok=True)
                with open(registry_path, 'w') as f:
                    f.write(registry_content)
                
                logger.info(f"Frontend plugin registry updated with {len(registry_plugins)} plugins")
        
        except Exception as e:
            logger.error(f"Error updating frontend registry: {e}")
    
    async def uninstall_plugin(self, plugin_id: str) -> Dict[str, Any]:
        """Uninstall a plugin"""
        try:
            async with self.db_pool.acquire() as conn:
                # Get plugin info
                plugin = await conn.fetchrow(
                    "SELECT * FROM plugins WHERE id = $1", plugin_id
                )
                
                if not plugin:
                    return {"success": False, "message": "Plugin not found"}
                
                # Update status to uninstalling
                await conn.execute(
                    "UPDATE plugins SET status = $1 WHERE id = $2",
                    PluginStatus.UNINSTALLING.value, plugin_id
                )
                
                # Remove plugin files
                install_path = Path(plugin['install_path'])
                if install_path.exists():
                    shutil.rmtree(install_path)
                
                # Remove from database
                await conn.execute("DELETE FROM plugins WHERE id = $1", plugin_id)
                
                # Clean up related records
                await conn.execute("DELETE FROM plugin_security_violations WHERE plugin_id = $1", plugin_id)
                
                # Update frontend registry
                await self._update_frontend_registry()
                
                logger.info(f"Plugin {plugin_id} uninstalled successfully")
                
                return {"success": True, "message": f"Plugin {plugin_id} uninstalled successfully"}
        
        except Exception as e:
            logger.error(f"Error uninstalling plugin {plugin_id}: {e}")
            return {"success": False, "message": str(e)}
    
    async def update_plugin(self, update_request: PluginUpdate) -> Dict[str, Any]:
        """Update an installed plugin"""
        try:
            async with self.db_pool.acquire() as conn:
                # Get current plugin info
                plugin = await conn.fetchrow(
                    "SELECT * FROM plugins WHERE id = $1", update_request.plugin_id
                )
                
                if not plugin:
                    return {"success": False, "message": "Plugin not found"}
                
                # Check for available updates
                available_version = await self._get_latest_version(plugin['repository_url'])
                current_version = plugin['version']
                
                target_version = update_request.target_version or available_version
                
                if not update_request.force and target_version == current_version:
                    return {"success": False, "message": "Plugin is already up to date"}
                
                # Perform update (essentially reinstall with new version)
                install_request = PluginInstallRequest(
                    repository_url=plugin['repository_url'],
                    version=target_version,
                    force=True
                )
                
                result = await self.install_plugin(install_request)
                
                return {
                    "success": result.status == "installed",
                    "message": f"Plugin updated from {current_version} to {target_version}" if result.status == "installed" else result.message
                }
        
        except Exception as e:
            logger.error(f"Error updating plugin {update_request.plugin_id}: {e}")
            return {"success": False, "message": str(e)}
    
    async def _get_latest_version(self, repository_url: str) -> Optional[str]:
        """Get the latest version/tag from GitHub repository"""
        try:
            owner, repo = self._parse_github_url(repository_url)
            api_url = f"{self.github_api_base}/repos/{owner}/{repo}/releases/latest"
            
            headers = {}
            if self.github_token:
                headers["Authorization"] = f"Bearer {self.github_token}"
            
            async with aiohttp.ClientSession(headers=headers) as session:
                async with session.get(api_url) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get('tag_name')
            
            return None
        
        except Exception as e:
            logger.error(f"Error getting latest version: {e}")
            return None
    
    async def list_plugins(self) -> List[PluginInfo]:
        """List all installed plugins"""
        try:
            async with self.db_pool.acquire() as conn:
                plugins = await conn.fetch("""
                    SELECT 
                        id, name, version, description, author, type, status,
                        repository_url, installed_at, last_updated, permissions,
                        security_violations, last_violation, config
                    FROM plugins 
                    ORDER BY name
                """)
                
                plugin_list = []
                for plugin in plugins:
                    try:
                        permissions = json.loads(plugin['permissions']) if plugin['permissions'] else []
                        config = json.loads(plugin['config']) if plugin['config'] else {}
                        
                        plugin_info = PluginInfo(
                            id=plugin['id'],
                            name=plugin['name'],
                            version=plugin['version'],
                            description=plugin['description'],
                            author=plugin['author'],
                            type=plugin['type'],
                            status=PluginStatus(plugin['status']),
                            repository_url=plugin['repository_url'],
                            installed_at=plugin['installed_at'],
                            last_updated=plugin['last_updated'],
                            permissions=[SecurityPermission(p) for p in permissions],
                            security_violations=plugin['security_violations'] or 0,
                            last_violation=plugin['last_violation'],
                            config=config
                        )
                        plugin_list.append(plugin_info)
                    except Exception as e:
                        logger.warning(f"Error processing plugin {plugin['id']}: {e}")
                
                return plugin_list
        
        except Exception as e:
            logger.error(f"Error listing plugins: {e}")
            return []
    
    async def get_plugin_health(self, plugin_id: str) -> Dict[str, Any]:
        """Get plugin health status"""
        return await self.security_validator.check_runtime_security(plugin_id)
    
    def _versions_compatible(self, required: str, installed: str) -> bool:
        """Check if version requirements are compatible"""
        # Simplified version compatibility check
        # In production, use a proper semver library
        req_clean = required.lstrip('^~')
        return req_clean == installed