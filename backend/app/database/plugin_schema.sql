-- Plugin Management Database Schema
-- Comprehensive schema for secure plugin installation and monitoring

-- Main plugins table
CREATE TABLE IF NOT EXISTS plugins (
    id VARCHAR(255) PRIMARY KEY,                    -- Plugin ID from manifest
    name VARCHAR(255) NOT NULL,                     -- Human-readable name
    version VARCHAR(50) NOT NULL,                   -- Semantic version
    description TEXT,                               -- Plugin description
    author VARCHAR(255) NOT NULL,                   -- Plugin author
    type VARCHAR(50) NOT NULL,                      -- Plugin type (ui/data/integration/system)
    kind VARCHAR(50) NOT NULL,                      -- Legacy compatibility (ui/data/integration)
    
    -- Installation details
    repository_url TEXT NOT NULL,                   -- GitHub repository URL
    install_path TEXT NOT NULL,                     -- Local installation path
    manifest JSONB NOT NULL,                        -- Full plugin manifest
    permissions JSONB DEFAULT '[]'::jsonb,          -- Granted permissions array
    config JSONB DEFAULT '{}'::jsonb,               -- Plugin configuration
    
    -- Status and lifecycle
    status VARCHAR(50) NOT NULL DEFAULT 'pending', -- installation status
    installed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_updated TIMESTAMP WITH TIME ZONE,
    installation_id VARCHAR(255),                   -- Installation tracking ID
    
    -- Security monitoring
    security_violations INTEGER DEFAULT 0,          -- Count of security violations
    last_violation TIMESTAMP WITH TIME ZONE,        -- Last security violation
    security_score INTEGER DEFAULT 100,             -- Security score (0-100)
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Plugin installation tracking table
CREATE TABLE IF NOT EXISTS plugin_installations (
    id VARCHAR(255) PRIMARY KEY,                    -- Installation tracking ID
    status VARCHAR(50) NOT NULL,                    -- Current installation status
    message TEXT,                                   -- Status message
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    error_details JSONB                             -- Detailed error information
);

-- Plugin security violations table
CREATE TABLE IF NOT EXISTS plugin_security_violations (
    id SERIAL PRIMARY KEY,
    plugin_id VARCHAR(255) NOT NULL REFERENCES plugins(id) ON DELETE CASCADE,
    violation_type VARCHAR(100) NOT NULL,           -- Type of security violation
    description TEXT NOT NULL,                      -- Human-readable description
    severity VARCHAR(20) NOT NULL,                  -- low/medium/high/critical
    context JSONB,                                  -- Violation context data
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    resolved BOOLEAN DEFAULT FALSE,                 -- Whether violation was resolved
    resolution_notes TEXT                           -- Resolution details
);

-- Plugin dependencies table
CREATE TABLE IF NOT EXISTS plugin_dependencies (
    id SERIAL PRIMARY KEY,
    plugin_id VARCHAR(255) NOT NULL REFERENCES plugins(id) ON DELETE CASCADE,
    dependency_name VARCHAR(255) NOT NULL,          -- Name of dependency
    dependency_version VARCHAR(50) NOT NULL,        -- Required version
    dependency_type VARCHAR(50) NOT NULL,           -- Type: plugin/npm/system
    resolved_version VARCHAR(50),                   -- Actually installed version
    status VARCHAR(50) DEFAULT 'pending',           -- pending/resolved/failed
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Plugin API access log table
CREATE TABLE IF NOT EXISTS plugin_api_access (
    id SERIAL PRIMARY KEY,
    plugin_id VARCHAR(255) NOT NULL REFERENCES plugins(id) ON DELETE CASCADE,
    endpoint VARCHAR(255) NOT NULL,                 -- API endpoint accessed
    method VARCHAR(10) NOT NULL,                    -- HTTP method
    status_code INTEGER,                            -- Response status code
    permission_required VARCHAR(100),               -- Required permission
    access_granted BOOLEAN NOT NULL,                -- Whether access was granted
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    request_data JSONB,                             -- Request data (sanitized)
    response_time INTEGER,                          -- Response time in ms
    user_agent TEXT,                                -- Client user agent
    ip_address INET                                 -- Client IP address
);

-- Plugin configuration history table
CREATE TABLE IF NOT EXISTS plugin_config_history (
    id SERIAL PRIMARY KEY,
    plugin_id VARCHAR(255) NOT NULL REFERENCES plugins(id) ON DELETE CASCADE,
    old_config JSONB,                               -- Previous configuration
    new_config JSONB,                               -- New configuration
    changed_by VARCHAR(255),                        -- User who made the change
    change_reason TEXT,                             -- Reason for change
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Plugin health checks table
CREATE TABLE IF NOT EXISTS plugin_health_checks (
    id SERIAL PRIMARY KEY,
    plugin_id VARCHAR(255) NOT NULL REFERENCES plugins(id) ON DELETE CASCADE,
    check_type VARCHAR(50) NOT NULL,                -- Type of health check
    status VARCHAR(20) NOT NULL,                    -- healthy/degraded/unhealthy
    message TEXT,                                   -- Health check message
    response_time INTEGER,                          -- Response time in ms
    details JSONB,                                  -- Detailed health information
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_plugins_status ON plugins(status);
CREATE INDEX IF NOT EXISTS idx_plugins_type ON plugins(type);
CREATE INDEX IF NOT EXISTS idx_plugins_installed_at ON plugins(installed_at);
CREATE INDEX IF NOT EXISTS idx_plugin_violations_plugin_id ON plugin_security_violations(plugin_id);
CREATE INDEX IF NOT EXISTS idx_plugin_violations_timestamp ON plugin_security_violations(timestamp);
CREATE INDEX IF NOT EXISTS idx_plugin_violations_severity ON plugin_security_violations(severity);
CREATE INDEX IF NOT EXISTS idx_plugin_api_access_plugin_id ON plugin_api_access(plugin_id);
CREATE INDEX IF NOT EXISTS idx_plugin_api_access_timestamp ON plugin_api_access(timestamp);
CREATE INDEX IF NOT EXISTS idx_plugin_health_checks_plugin_id ON plugin_health_checks(plugin_id);
CREATE INDEX IF NOT EXISTS idx_plugin_health_checks_timestamp ON plugin_health_checks(timestamp);

-- Triggers to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply triggers
CREATE TRIGGER update_plugins_updated_at BEFORE UPDATE ON plugins
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_plugin_installations_updated_at BEFORE UPDATE ON plugin_installations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Security policies and constraints
ALTER TABLE plugins 
    ADD CONSTRAINT plugins_status_check 
    CHECK (status IN ('pending', 'installing', 'installed', 'failed', 'updating', 'uninstalling', 'disabled'));

ALTER TABLE plugins 
    ADD CONSTRAINT plugins_type_check 
    CHECK (type IN ('ui', 'data', 'integration', 'system'));

ALTER TABLE plugin_security_violations 
    ADD CONSTRAINT violations_severity_check 
    CHECK (severity IN ('low', 'medium', 'high', 'critical'));

ALTER TABLE plugin_api_access 
    ADD CONSTRAINT api_access_method_check 
    CHECK (method IN ('GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS'));

-- Create plugin management schema if it doesn't exist
CREATE SCHEMA IF NOT EXISTS plugin_management;

-- Plugin statistics view
CREATE OR REPLACE VIEW plugin_management.plugin_stats AS
SELECT 
    COUNT(*) as total_plugins,
    COUNT(CASE WHEN status = 'installed' THEN 1 END) as installed_plugins,
    COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed_plugins,
    COUNT(CASE WHEN security_violations > 0 THEN 1 END) as plugins_with_violations,
    AVG(security_score) as avg_security_score,
    MAX(installed_at) as last_installation,
    MIN(security_score) as min_security_score
FROM plugins;

-- Security violations summary view
CREATE OR REPLACE VIEW plugin_management.security_summary AS
SELECT 
    plugin_id,
    p.name as plugin_name,
    COUNT(*) as total_violations,
    COUNT(CASE WHEN severity = 'critical' THEN 1 END) as critical_violations,
    COUNT(CASE WHEN severity = 'high' THEN 1 END) as high_violations,
    COUNT(CASE WHEN severity = 'medium' THEN 1 END) as medium_violations,
    COUNT(CASE WHEN severity = 'low' THEN 1 END) as low_violations,
    MAX(timestamp) as last_violation
FROM plugin_security_violations psv
JOIN plugins p ON psv.plugin_id = p.id
GROUP BY plugin_id, p.name
ORDER BY total_violations DESC, last_violation DESC;

-- Plugin API usage summary view
CREATE OR REPLACE VIEW plugin_management.api_usage_summary AS
SELECT 
    plugin_id,
    p.name as plugin_name,
    endpoint,
    COUNT(*) as total_requests,
    COUNT(CASE WHEN access_granted THEN 1 END) as granted_requests,
    COUNT(CASE WHEN NOT access_granted THEN 1 END) as denied_requests,
    AVG(response_time) as avg_response_time,
    MAX(timestamp) as last_access
FROM plugin_api_access paa
JOIN plugins p ON paa.plugin_id = p.id
GROUP BY plugin_id, p.name, endpoint
ORDER BY total_requests DESC;

-- Plugin permissions reference table (must be created before inserts)
CREATE TABLE IF NOT EXISTS plugin_management.plugin_permissions (
    permission VARCHAR(100) PRIMARY KEY,
    description TEXT NOT NULL,
    category VARCHAR(50) NOT NULL,
    risk_level VARCHAR(20) NOT NULL CHECK (risk_level IN ('low', 'medium', 'high', 'critical')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Insert default plugin permissions (after table creation)
INSERT INTO plugin_management.plugin_permissions (permission, description, category, risk_level) VALUES
('read:projects', 'Read project data', 'data', 'low'),
('write:projects', 'Modify project data', 'data', 'medium'),
('read:events', 'Read event data', 'data', 'low'),
('publish:events', 'Publish events to MQTT', 'messaging', 'medium'),
('read:logs', 'Read application logs', 'data', 'medium'),
('read:system', 'Read system information', 'system', 'low'),
('network:http', 'Make HTTP requests', 'network', 'high'),
('network:websocket', 'Create WebSocket connections', 'network', 'medium'),
('storage:local', 'Access local storage', 'storage', 'medium'),
('plugin:messaging', 'Communicate with other plugins', 'messaging', 'medium')
ON CONFLICT DO NOTHING;