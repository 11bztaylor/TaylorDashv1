"""
Plugin Security Validation and Monitoring System
Implements comprehensive security controls for plugin installation and runtime
"""
import asyncio
import json
import logging
import os
import re
import tempfile
import zipfile
from pathlib import Path
from typing import Dict, List, Optional, Set, Any, Tuple
from datetime import datetime, timezone
import aiohttp
import asyncpg

from ..models.plugin import (
    PluginManifest, SecurityPermission, PluginSecurityViolation, 
    PluginStatus, PluginType
)


logger = logging.getLogger(__name__)


class SecurityViolationType:
    """Security violation types"""
    UNAUTHORIZED_API_ACCESS = "unauthorized_api_access"
    PERMISSION_ESCALATION = "permission_escalation"
    MALICIOUS_CODE_DETECTED = "malicious_code_detected"
    UNSAFE_NETWORK_REQUEST = "unsafe_network_request"
    SANDBOX_ESCAPE_ATTEMPT = "sandbox_escape_attempt"
    RESOURCE_ABUSE = "resource_abuse"
    DATA_EXFILTRATION = "data_exfiltration"


class PluginSecurityValidator:
    """
    Comprehensive plugin security validation system
    Validates plugins before installation and monitors runtime behavior
    """
    
    def __init__(self, db_pool: asyncpg.Pool):
        self.db_pool = db_pool
        self.security_patterns = self._load_security_patterns()
        self.api_whitelist = self._load_api_whitelist()
        
    def _load_security_patterns(self) -> Dict[str, List[str]]:
        """Load malicious code patterns for static analysis"""
        return {
            "dangerous_functions": [
                r"eval\s*\(",
                r"Function\s*\(",
                r"setTimeout\s*\(\s*['\"]",
                r"setInterval\s*\(\s*['\"]",
                r"document\.write\s*\(",
                r"innerHTML\s*=",
                r"outerHTML\s*=",
                r"window\.location\s*=",
                r"top\.location\s*=",
                r"parent\.location\s*=",
            ],
            "script_injection": [
                r"<script[^>]*>.*?</script>",
                r"<script[^>]*>",
                r"javascript:",
                r"on\w+\s*=",  # Event handlers like onclick, onload, etc.
            ],
            "data_access": [
                r"localStorage\.",
                r"sessionStorage\.",
                r"document\.cookie",
                r"navigator\.userAgent",
                r"screen\.",
                r"crypto\.",
            ],
            "network_access": [
                r"fetch\s*\(",
                r"XMLHttpRequest\s*\(",
                r"WebSocket\s*\(",
                r"EventSource\s*\(",
                r"import\s*\(",
            ],
            "dom_manipulation": [
                r"document\.createElement\s*\(\s*['\"]script",
                r"document\.createElement\s*\(\s*['\"]iframe",
                r"document\.createElement\s*\(\s*['\"]link",
                r"appendChild\s*\(",
                r"insertBefore\s*\(",
            ]
        }
    
    def _load_api_whitelist(self) -> Set[str]:
        """Load whitelisted API endpoints"""
        return {
            "/api/v1/projects",
            "/api/v1/projects/{project_id}",
            "/api/v1/events",
            "/api/v1/health/stack",
            "/api/v1/plugins/health",
        }
    
    async def validate_plugin_installation(self, 
                                         repository_url: str, 
                                         temp_dir: Path) -> Tuple[bool, List[str], Optional[PluginManifest]]:
        """
        Comprehensive plugin validation before installation
        
        Returns:
            (is_valid, validation_errors, manifest)
        """
        validation_errors = []
        manifest = None
        
        try:
            # 1. Validate manifest file
            manifest_path = temp_dir / "plugin.json"
            if not manifest_path.exists():
                validation_errors.append("Missing plugin.json manifest file")
                return False, validation_errors, None
            
            try:
                with open(manifest_path, 'r') as f:
                    manifest_data = json.load(f)
                manifest = PluginManifest(**manifest_data)
            except Exception as e:
                validation_errors.append(f"Invalid plugin.json format: {str(e)}")
                return False, validation_errors, None
            
            # 2. Validate repository URL matches manifest
            if not self._validate_repository_consistency(repository_url, manifest):
                validation_errors.append("Repository URL does not match manifest repository")
            
            # 3. Validate entry point exists
            entry_path = temp_dir / manifest.entry_point
            if not entry_path.exists():
                validation_errors.append(f"Entry point file not found: {manifest.entry_point}")
            
            # 4. Perform static code analysis
            static_analysis_errors = await self._perform_static_analysis(temp_dir, manifest)
            validation_errors.extend(static_analysis_errors)
            
            # 5. Validate permissions and API access
            permission_errors = self._validate_permissions(manifest)
            validation_errors.extend(permission_errors)
            
            # 6. Check for dependency conflicts
            dependency_errors = await self._check_dependency_conflicts(manifest)
            validation_errors.extend(dependency_errors)
            
            # 7. Validate iframe security configuration
            iframe_errors = await self._validate_iframe_security(temp_dir, manifest)
            validation_errors.extend(iframe_errors)
            
            is_valid = len(validation_errors) == 0
            return is_valid, validation_errors, manifest
            
        except Exception as e:
            logger.error(f"Plugin validation failed with exception: {e}")
            validation_errors.append(f"Validation failed: {str(e)}")
            return False, validation_errors, None
    
    def _validate_repository_consistency(self, repository_url: str, manifest: PluginManifest) -> bool:
        """Validate that repository URL is consistent with manifest"""
        # Extract repo info from URL
        url_parts = repository_url.rstrip('/').split('/')
        if len(url_parts) < 2:
            return False
        
        repo_owner = url_parts[-2]
        repo_name = url_parts[-1]
        
        # Check if manifest repository matches
        manifest_url = str(manifest.repository).rstrip('/')
        return repository_url.rstrip('/') == manifest_url
    
    async def _perform_static_analysis(self, plugin_dir: Path, manifest: PluginManifest) -> List[str]:
        """Perform static code analysis to detect malicious patterns"""
        errors = []
        
        # Analyze JavaScript, HTML, and CSS files
        files_to_analyze = []
        for ext in ['*.js', '*.html', '*.css', '*.ts', '*.jsx', '*.tsx']:
            files_to_analyze.extend(plugin_dir.glob(f"**/{ext}"))
        
        for file_path in files_to_analyze:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                file_errors = self._analyze_file_content(content, file_path.name, manifest)
                errors.extend(file_errors)
                
            except Exception as e:
                logger.warning(f"Could not analyze file {file_path}: {e}")
        
        return errors
    
    def _analyze_file_content(self, content: str, filename: str, manifest: PluginManifest) -> List[str]:
        """Analyze individual file content for security issues"""
        errors = []
        
        # Check for dangerous patterns
        for category, patterns in self.security_patterns.items():
            for pattern in patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    # Check if usage is permitted
                    if not self._is_usage_permitted(category, pattern, manifest):
                        errors.append(
                            f"Potentially dangerous code detected in {filename}: "
                            f"{category} pattern '{pattern}' without required permissions"
                        )
        
        # Check for hardcoded credentials or sensitive data
        credential_patterns = [
            r"(?i)password\s*[:=]\s*['\"][^'\"]{8,}['\"]",
            r"(?i)api[_-]?key\s*[:=]\s*['\"][^'\"]{16,}['\"]",
            r"(?i)secret\s*[:=]\s*['\"][^'\"]{16,}['\"]",
            r"(?i)token\s*[:=]\s*['\"][^'\"]{20,}['\"]",
        ]
        
        for pattern in credential_patterns:
            if re.search(pattern, content):
                errors.append(f"Hardcoded credentials detected in {filename}")
        
        # Check for external resource loads
        external_resource_patterns = [
            r"(?i)src\s*=\s*['\"]https?://[^'\"]+['\"]",
            r"(?i)href\s*=\s*['\"]https?://[^'\"]+['\"]",
            r"(?i)url\s*\(\s*['\"]?https?://[^'\"]+['\"]?\s*\)",
        ]
        
        for pattern in external_resource_patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                url = self._extract_url_from_match(match.group())
                if not self._is_external_url_allowed(url, manifest):
                    errors.append(
                        f"Unauthorized external resource in {filename}: {url}"
                    )
        
        return errors
    
    def _is_usage_permitted(self, category: str, pattern: str, manifest: PluginManifest) -> bool:
        """Check if dangerous code usage is permitted by manifest permissions"""
        permission_map = {
            "network_access": [SecurityPermission.NETWORK_HTTP, SecurityPermission.NETWORK_WEBSOCKET],
            "data_access": [SecurityPermission.LOCAL_STORAGE],
            "dangerous_functions": [],  # Generally not permitted
            "script_injection": [],     # Generally not permitted - XSS protection
            "dom_manipulation": [],     # Allowed for UI plugins with restrictions
        }
        
        required_permissions = permission_map.get(category, [])
        if not required_permissions:
            if category == "dom_manipulation" and manifest.type == PluginType.UI:
                return True
            if category in ["dangerous_functions", "script_injection"]:
                return False  # Never permitted
            return False
        
        return any(perm in manifest.permissions for perm in required_permissions)
    
    def _extract_url_from_match(self, match_text: str) -> str:
        """Extract URL from regex match"""
        url_match = re.search(r'https?://[^\'\"]+', match_text)
        return url_match.group() if url_match else ""
    
    def _is_external_url_allowed(self, url: str, manifest: PluginManifest) -> bool:
        """Check if external URL is allowed by manifest"""
        if not manifest.allowed_origins:
            return False
        
        for allowed_origin in manifest.allowed_origins:
            if url.startswith(allowed_origin):
                return True
        
        return False
    
    def _validate_permissions(self, manifest: PluginManifest) -> List[str]:
        """Validate requested permissions are reasonable"""
        errors = []
        
        # Check for excessive permissions
        if len(manifest.permissions) > 10:
            errors.append("Plugin requests excessive permissions (>10)")
        
        # Check for permission combinations that might be dangerous
        dangerous_combinations = [
            (SecurityPermission.WRITE_PROJECTS, SecurityPermission.PUBLISH_EVENTS),
            (SecurityPermission.READ_LOGS, SecurityPermission.NETWORK_HTTP),
        ]
        
        for perm1, perm2 in dangerous_combinations:
            if perm1 in manifest.permissions and perm2 in manifest.permissions:
                errors.append(f"Dangerous permission combination: {perm1.value} + {perm2.value}")
        
        # Validate API endpoints against permissions
        for endpoint in manifest.api_endpoints:
            if not self._is_api_endpoint_permitted(endpoint, manifest.permissions):
                errors.append(f"API endpoint {endpoint} not permitted by declared permissions")
        
        return errors
    
    def _is_api_endpoint_permitted(self, endpoint: str, permissions: List[SecurityPermission]) -> bool:
        """Check if API endpoint access is permitted by permissions"""
        endpoint_permissions = {
            "/api/v1/projects": [SecurityPermission.READ_PROJECTS],
            "/api/v1/events": [SecurityPermission.READ_EVENTS],
            "/api/v1/logs": [SecurityPermission.READ_LOGS],
        }
        
        required_perms = endpoint_permissions.get(endpoint, [])
        return any(perm in permissions for perm in required_perms)
    
    async def _check_dependency_conflicts(self, manifest: PluginManifest) -> List[str]:
        """Check for dependency conflicts with installed plugins"""
        errors = []
        
        try:
            async with self.db_pool.acquire() as conn:
                # Get all installed plugins
                installed_plugins = await conn.fetch(
                    "SELECT id, manifest FROM plugins WHERE status = $1",
                    PluginStatus.INSTALLED.value
                )
                
                for row in installed_plugins:
                    try:
                        installed_manifest = PluginManifest(**json.loads(row['manifest']))
                        
                        # Check for ID conflicts
                        if installed_manifest.id == manifest.id:
                            errors.append(f"Plugin ID conflict: {manifest.id} is already installed")
                        
                        # Check for dependency version conflicts
                        for dep_name, dep_version in manifest.dependencies.items():
                            if dep_name in installed_manifest.dependencies:
                                installed_version = installed_manifest.dependencies[dep_name]
                                if not self._versions_compatible(dep_version, installed_version):
                                    errors.append(
                                        f"Dependency conflict for {dep_name}: "
                                        f"requires {dep_version}, installed {installed_version}"
                                    )
                    
                    except Exception as e:
                        logger.warning(f"Could not parse installed plugin manifest: {e}")
        
        except Exception as e:
            logger.error(f"Error checking dependency conflicts: {e}")
            errors.append("Could not verify dependency conflicts")
        
        return errors
    
    def _versions_compatible(self, required: str, installed: str) -> bool:
        """Check if version requirements are compatible"""
        # Simplified version compatibility check
        # In production, use a proper semver library
        req_clean = required.lstrip('^~')
        return req_clean == installed
    
    async def _validate_iframe_security(self, plugin_dir: Path, manifest: PluginManifest) -> List[str]:
        """Validate iframe security configuration"""
        errors = []
        
        entry_path = plugin_dir / manifest.entry_point
        if not entry_path.exists():
            return errors  # Already reported in main validation
        
        try:
            with open(entry_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            # Check for dangerous iframe attributes or lack of security headers
            if 'sandbox' in html_content.lower():
                # Plugin should not define its own sandbox - we control this
                errors.append("Plugin should not define sandbox attributes - TaylorDash controls iframe security")
            
            # Check for attempts to break out of iframe
            iframe_escape_patterns = [
                r"top\.location",
                r"parent\.location",
                r"window\.top",
                r"window\.parent(?!\.postMessage)",  # postMessage is allowed
                r"frameElement",
                r"self\.parent",
            ]
            
            for pattern in iframe_escape_patterns:
                if re.search(pattern, html_content, re.IGNORECASE):
                    errors.append(f"Iframe escape attempt detected: {pattern}")
        
        except Exception as e:
            logger.warning(f"Could not validate iframe security: {e}")
        
        return errors
    
    async def log_security_violation(self, 
                                   plugin_id: str, 
                                   violation_type: str,
                                   description: str,
                                   severity: str,
                                   context: Dict[str, Any]) -> None:
        """Log a security violation"""
        try:
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO plugin_security_violations 
                    (plugin_id, violation_type, description, severity, context, timestamp)
                    VALUES ($1, $2, $3, $4, $5, $6)
                """, plugin_id, violation_type, description, severity, json.dumps(context), 
                    datetime.now(timezone.utc))
                
                # Update plugin violation count
                await conn.execute("""
                    UPDATE plugins 
                    SET security_violations = security_violations + 1,
                        last_violation = $2
                    WHERE id = $1
                """, plugin_id, datetime.now(timezone.utc))
                
                logger.warning(f"Security violation logged for plugin {plugin_id}: {violation_type}")
                
        except Exception as e:
            logger.error(f"Failed to log security violation: {e}")
    
    async def check_runtime_security(self, plugin_id: str) -> Dict[str, Any]:
        """Perform runtime security check on installed plugin"""
        try:
            async with self.db_pool.acquire() as conn:
                plugin_row = await conn.fetchrow(
                    "SELECT * FROM plugins WHERE id = $1", plugin_id
                )
                
                if not plugin_row:
                    return {"status": "error", "message": "Plugin not found"}
                
                violations = await conn.fetch("""
                    SELECT violation_type, severity, timestamp 
                    FROM plugin_security_violations 
                    WHERE plugin_id = $1 
                    ORDER BY timestamp DESC 
                    LIMIT 10
                """, plugin_id)
                
                # Calculate security score based on violations
                security_score = self._calculate_security_score(violations)
                
                return {
                    "status": "healthy" if security_score >= 80 else "degraded" if security_score >= 60 else "unhealthy",
                    "security_score": security_score,
                    "recent_violations": len(violations),
                    "last_check": datetime.now(timezone.utc).isoformat()
                }
        
        except Exception as e:
            logger.error(f"Runtime security check failed for plugin {plugin_id}: {e}")
            return {"status": "error", "message": str(e)}
    
    def _calculate_security_score(self, violations: List[Any]) -> int:
        """Calculate security score based on violations"""
        if not violations:
            return 100
        
        score = 100
        severity_weights = {
            "low": 5,
            "medium": 15,
            "high": 30,
            "critical": 50
        }
        
        for violation in violations:
            severity = violation['severity'].lower()
            score -= severity_weights.get(severity, 10)
        
        return max(0, score)