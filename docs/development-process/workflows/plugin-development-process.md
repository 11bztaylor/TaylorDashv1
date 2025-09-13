# Plugin Development Process

**Last Updated:** 2025-09-12
**Version:** 1.0
**Status:** Production Ready Plugin System

## Plugin Architecture Overview

### Plugin Types
- **UI Plugins** - Frontend components and interfaces
- **Data Plugins** - Data processing and transformation
- **Integration Plugins** - External service connections
- **MCP Plugins** - Model Context Protocol integrations

### Security Model
- **Sandboxed Execution** - Iframe isolation for UI plugins
- **Permission System** - Granular access controls
- **Security Scanning** - Automated vulnerability detection
- **Resource Limits** - CPU, memory, and network constraints

## Plugin Development Lifecycle

### 1. Plugin Planning

#### Plugin Specification
```bash
# Create plugin specification
cat > plugin_spec.md << EOF
# Plugin: [Plugin Name]

## Overview
Brief description of plugin functionality and purpose.

## Plugin Type
- [ ] UI Plugin (frontend interface)
- [ ] Data Plugin (data processing)
- [ ] Integration Plugin (external services)
- [ ] MCP Plugin (model context protocol)

## Capabilities Required
- [ ] Database access
- [ ] MQTT messaging
- [ ] External API calls
- [ ] File system access
- [ ] User interface components

## Security Requirements
- Permission level: [minimal/standard/elevated]
- Network access: [none/restricted/full]
- Data access: [read-only/read-write/admin]
- User context: [anonymous/authenticated/admin]

## Performance Requirements
- Memory limit: [128MB/256MB/512MB]
- CPU limit: [low/medium/high]
- Response time: [<100ms/<500ms/<1s]
- Concurrent users: [1-10/10-100/100+]

## Integration Points
- TaylorDash API endpoints used
- External services integrated
- Data sources required
- Event subscriptions needed
EOF
```

### 2. Plugin Project Setup

#### Directory Structure
```bash
# Create plugin project structure
mkdir taylordash-plugin-example
cd taylordash-plugin-example

# Standard plugin structure
mkdir -p {src,tests,docs,config}
touch {package.json,Dockerfile,plugin.yaml,README.md}

# Plugin structure
taylordash-plugin-example/
├── plugin.yaml          # Plugin metadata
├── package.json         # Dependencies
├── Dockerfile          # Container definition
├── README.md           # Plugin documentation
├── src/
│   ├── index.js        # Main plugin entry
│   ├── components/     # UI components (if UI plugin)
│   └── api/           # API integration
├── tests/
│   ├── unit/          # Unit tests
│   └── integration/   # Integration tests
├── docs/
│   └── user-guide.md  # User documentation
└── config/
    └── permissions.json # Permission requirements
```

#### Plugin Metadata (plugin.yaml)
```yaml
# plugin.yaml
name: "example-plugin"
version: "1.0.0"
description: "Example TaylorDash plugin"
author: "Your Name <email@example.com>"
license: "MIT"

# Plugin configuration
kind: "ui"  # ui, data, integration, mcp
runtime: "node"  # node, python, container

# Security configuration
permissions:
  - "taylordash.api.read"
  - "taylordash.events.subscribe"
  - "network.external.example.com"

# Resource limits
resources:
  memory: "256MB"
  cpu: "100m"
  timeout: "30s"

# Integration points
endpoints:
  health: "/health"
  main: "/app"
  config: "/config"

# Dependencies
dependencies:
  taylordash: ">=1.0.0"

# Environment requirements
environment:
  NODE_ENV: "production"
  API_ENDPOINT: "${TAYLORDASH_API_URL}"
```

### 3. Plugin Implementation

#### Frontend UI Plugin
```javascript
// src/index.js (UI Plugin)
import React from 'react';
import ReactDOM from 'react-dom';
import PluginApp from './components/PluginApp';

// TaylorDash Plugin API
import { TaylorDashPlugin } from '@taylordash/plugin-sdk';

class ExamplePlugin extends TaylorDashPlugin {
  constructor() {
    super();
    this.name = 'example-plugin';
    this.version = '1.0.0';
  }

  async initialize() {
    // Plugin initialization
    await this.registerEventHandlers();
    await this.setupAPI();

    // Render UI
    ReactDOM.render(
      <PluginApp plugin={this} />,
      document.getElementById('plugin-root')
    );
  }

  async registerEventHandlers() {
    // Subscribe to TaylorDash events
    this.addEventListener('project.created', this.handleProjectCreated);
    this.addEventListener('user.authenticated', this.handleUserAuth);
  }

  async handleProjectCreated(event) {
    console.log('Project created:', event.data);
    // Plugin-specific logic
  }

  async setupAPI() {
    // Initialize API client
    this.api = new TaylorDashAPI({
      baseURL: process.env.API_ENDPOINT,
      apiKey: this.getAPIKey(),
      permissions: this.getPermissions()
    });
  }
}

// Initialize plugin
const plugin = new ExamplePlugin();
plugin.initialize();
```

#### Data Processing Plugin
```python
# src/main.py (Data Plugin)
from taylordash_sdk import TaylorDashPlugin, DataProcessor
import asyncio
import logging

class ExampleDataPlugin(TaylorDashPlugin):
    def __init__(self):
        super().__init__()
        self.name = "example-data-plugin"
        self.version = "1.0.0"

    async def initialize(self):
        """Initialize the data plugin"""
        await self.register_data_processors()
        await self.subscribe_to_events()

    async def register_data_processors(self):
        """Register data processing functions"""
        self.register_processor("transform_data", self.transform_data)
        self.register_processor("analyze_metrics", self.analyze_metrics)

    async def transform_data(self, data):
        """Transform incoming data"""
        try:
            # Data transformation logic
            transformed = {
                'original': data,
                'processed_at': datetime.utcnow().isoformat(),
                'processed_by': self.name,
                'result': self.process_logic(data)
            }
            return transformed
        except Exception as e:
            logging.error(f"Data transformation failed: {e}")
            raise

    async def analyze_metrics(self, metrics):
        """Analyze system metrics"""
        analysis = {
            'trends': self.calculate_trends(metrics),
            'anomalies': self.detect_anomalies(metrics),
            'recommendations': self.generate_recommendations(metrics)
        }
        return analysis

# Start plugin
if __name__ == "__main__":
    plugin = ExampleDataPlugin()
    asyncio.run(plugin.start())
```

#### Integration Plugin
```javascript
// src/integration.js (Integration Plugin)
import { TaylorDashPlugin, HTTPClient } from '@taylordash/plugin-sdk';

class ExternalServicePlugin extends TaylorDashPlugin {
  constructor() {
    super();
    this.name = 'external-service-plugin';
    this.client = new HTTPClient({
      baseURL: 'https://api.external-service.com',
      timeout: 30000
    });
  }

  async initialize() {
    await this.authenticateService();
    await this.registerEndpoints();
    await this.startSyncProcess();
  }

  async authenticateService() {
    const credentials = await this.getSecureConfig('external_service_credentials');
    const auth = await this.client.post('/auth', credentials);
    this.client.setAuthToken(auth.data.token);
  }

  async registerEndpoints() {
    // Register plugin endpoints
    this.router.get('/sync', this.handleSync.bind(this));
    this.router.post('/webhook', this.handleWebhook.bind(this));
    this.router.get('/status', this.getStatus.bind(this));
  }

  async handleSync(req, res) {
    try {
      const data = await this.client.get('/data');
      await this.publishEvent('external.data.synced', data);
      res.json({ status: 'success', count: data.length });
    } catch (error) {
      this.logError('Sync failed', error);
      res.status(500).json({ error: 'Sync failed' });
    }
  }

  async startSyncProcess() {
    // Schedule periodic sync
    setInterval(async () => {
      await this.handleSync();
    }, 300000); // 5 minutes
  }
}

export default ExternalServicePlugin;
```

### 4. Plugin Configuration

#### Permission Configuration
```json
{
  "permissions": {
    "api": {
      "read": ["projects", "users", "events"],
      "write": ["events"],
      "admin": []
    },
    "network": {
      "external": ["api.external-service.com", "webhook-service.com"],
      "internal": ["mqtt", "database"]
    },
    "data": {
      "access": ["user_context", "project_data"],
      "storage": ["plugin_config", "user_preferences"]
    },
    "events": {
      "subscribe": ["project.*", "user.authenticated"],
      "publish": ["plugin.example.*"]
    }
  },
  "security": {
    "sandbox": true,
    "csp": "default-src 'self'; connect-src 'self' https://api.external-service.com",
    "isolation": "iframe"
  }
}
```

#### Docker Configuration
```dockerfile
# Dockerfile
FROM node:18-alpine

WORKDIR /app

# Security: Create non-root user
RUN addgroup -g 1001 -S plugin && \
    adduser -S plugin -u 1001

# Install dependencies
COPY package*.json ./
RUN npm ci --only=production

# Copy plugin code
COPY src/ src/
COPY config/ config/

# Set ownership
RUN chown -R plugin:plugin /app

# Switch to non-root user
USER plugin

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:3000/health || exit 1

# Expose port
EXPOSE 3000

# Start plugin
CMD ["node", "src/index.js"]
```

### 5. Plugin Testing

#### Unit Testing
```javascript
// tests/unit/plugin.test.js
import { ExamplePlugin } from '../../src/index.js';
import { MockTaylorDashAPI } from '@taylordash/plugin-sdk/testing';

describe('ExamplePlugin', () => {
  let plugin;
  let mockAPI;

  beforeEach(() => {
    mockAPI = new MockTaylorDashAPI();
    plugin = new ExamplePlugin();
    plugin.api = mockAPI;
  });

  test('should initialize correctly', async () => {
    await plugin.initialize();
    expect(plugin.name).toBe('example-plugin');
    expect(plugin.version).toBe('1.0.0');
  });

  test('should handle project created event', async () => {
    const eventData = { id: 1, name: 'Test Project' };
    const spy = jest.spyOn(plugin, 'handleProjectCreated');

    await plugin.handleProjectCreated({ data: eventData });

    expect(spy).toHaveBeenCalledWith({ data: eventData });
  });

  test('should make API calls correctly', async () => {
    mockAPI.get.mockResolvedValue({ data: [{ id: 1 }] });

    const result = await plugin.api.get('/projects');

    expect(result.data).toHaveLength(1);
    expect(mockAPI.get).toHaveBeenCalledWith('/projects');
  });
});
```

#### Integration Testing
```bash
# tests/integration/plugin_integration.test.js
describe('Plugin Integration', () => {
  beforeAll(async () => {
    // Start TaylorDash test environment
    await startTaylorDashTestEnv();
    // Install plugin
    await installPlugin('example-plugin');
  });

  test('plugin loads in TaylorDash environment', async () => {
    const response = await fetch('http://localhost:5174/plugins/example-plugin');
    expect(response.status).toBe(200);
  });

  test('plugin API integration works', async () => {
    const result = await pluginAPI.get('/health');
    expect(result.status).toBe('healthy');
  });

  test('plugin event handling works', async () => {
    await publishEvent('project.created', { id: 1 });
    // Verify plugin handled event
    const logs = await getPluginLogs('example-plugin');
    expect(logs).toContain('Project created: 1');
  });
});
```

### 6. Plugin Security Testing

#### Security Validation
```bash
# Security testing script
#!/bin/bash

echo "=== Plugin Security Testing ==="

# 1. Container security scan
docker run --rm -v $(pwd):/src aquasec/trivy:latest fs /src

# 2. Dependency vulnerability scan
npm audit --audit-level high

# 3. Code security scan
docker run --rm -v $(pwd):/src securecodewarrior/sast-scanner:latest

# 4. Permission validation
node tests/security/permission_test.js

# 5. Sandbox escape testing
node tests/security/sandbox_test.js

echo "Security testing completed"
```

#### Permission Testing
```javascript
// tests/security/permission_test.js
import { PermissionValidator } from '@taylordash/plugin-sdk/security';

describe('Plugin Permissions', () => {
  test('should enforce API permissions', async () => {
    const plugin = new ExamplePlugin();
    const validator = new PermissionValidator(plugin.permissions);

    // Should allow permitted endpoints
    expect(await validator.canAccess('taylordash.api.projects.read')).toBe(true);

    // Should deny unpermitted endpoints
    expect(await validator.canAccess('taylordash.api.users.admin')).toBe(false);
  });

  test('should enforce network permissions', async () => {
    const plugin = new ExamplePlugin();

    // Should allow permitted domains
    const allowedRequest = plugin.httpClient.get('https://api.external-service.com/data');
    await expect(allowedRequest).resolves.toBeDefined();

    // Should block unpermitted domains
    const blockedRequest = plugin.httpClient.get('https://malicious-site.com');
    await expect(blockedRequest).rejects.toThrow('Network access denied');
  });
});
```

### 7. Plugin Deployment

#### Plugin Package Creation
```bash
# Build plugin package
npm run build

# Create plugin archive
tar -czf example-plugin-1.0.0.tgz \
  plugin.yaml \
  package.json \
  Dockerfile \
  src/ \
  config/

# Generate plugin manifest
cat > manifest.json << EOF
{
  "name": "example-plugin",
  "version": "1.0.0",
  "checksum": "$(sha256sum example-plugin-1.0.0.tgz | cut -d' ' -f1)",
  "size": $(stat -c%s example-plugin-1.0.0.tgz),
  "created": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}
EOF
```

#### Plugin Installation
```bash
# Install plugin via TaylorDash API
curl -X POST http://localhost:3000/api/v1/plugins/install \
  -H "X-API-Key: taylordash-dev-key" \
  -H "Content-Type: multipart/form-data" \
  -F "plugin=@example-plugin-1.0.0.tgz" \
  -F "manifest=@manifest.json"

# Verify installation
curl -H "X-API-Key: taylordash-dev-key" \
  http://localhost:3000/api/v1/plugins/example-plugin

# Check plugin health
curl -H "X-API-Key: taylordash-dev-key" \
  http://localhost:3000/api/v1/plugins/example-plugin/health
```

### 8. Plugin Monitoring

#### Health Monitoring
```javascript
// src/health.js
class PluginHealthCheck {
  constructor(plugin) {
    this.plugin = plugin;
    this.healthStatus = 'unknown';
  }

  async performHealthCheck() {
    try {
      // Check plugin components
      await this.checkAPIConnectivity();
      await this.checkDependencies();
      await this.checkResources();

      this.healthStatus = 'healthy';
      return { status: 'healthy', timestamp: new Date().toISOString() };
    } catch (error) {
      this.healthStatus = 'unhealthy';
      return {
        status: 'unhealthy',
        error: error.message,
        timestamp: new Date().toISOString()
      };
    }
  }

  async checkAPIConnectivity() {
    const response = await this.plugin.api.get('/health');
    if (response.status !== 200) {
      throw new Error('API connectivity failed');
    }
  }

  async checkDependencies() {
    // Check external service connectivity
    if (this.plugin.externalService) {
      await this.plugin.externalService.ping();
    }
  }

  async checkResources() {
    const memoryUsage = process.memoryUsage();
    if (memoryUsage.heapUsed > 256 * 1024 * 1024) { // 256MB
      throw new Error('Memory usage exceeded limit');
    }
  }
}
```

#### Performance Monitoring
```javascript
// src/metrics.js
class PluginMetrics {
  constructor() {
    this.metrics = {
      requests: 0,
      errors: 0,
      responseTime: [],
      memoryUsage: [],
      cpuUsage: []
    };
  }

  recordRequest(duration) {
    this.metrics.requests++;
    this.metrics.responseTime.push(duration);
  }

  recordError(error) {
    this.metrics.errors++;
    console.error('Plugin error:', error);
  }

  recordResourceUsage() {
    const memory = process.memoryUsage();
    const cpu = process.cpuUsage();

    this.metrics.memoryUsage.push(memory.heapUsed);
    this.metrics.cpuUsage.push(cpu.user + cpu.system);
  }

  getMetrics() {
    return {
      ...this.metrics,
      avgResponseTime: this.calculateAverage(this.metrics.responseTime),
      errorRate: this.metrics.errors / this.metrics.requests,
      memoryTrend: this.calculateTrend(this.metrics.memoryUsage)
    };
  }
}
```

## Plugin Development Best Practices

### Security Best Practices
- [ ] Never hardcode credentials or secrets
- [ ] Validate all inputs from external sources
- [ ] Use HTTPS for all external communications
- [ ] Implement proper error handling
- [ ] Follow principle of least privilege
- [ ] Regularly update dependencies
- [ ] Implement proper logging (no sensitive data)

### Performance Best Practices
- [ ] Implement efficient data structures
- [ ] Use async/await for I/O operations
- [ ] Cache frequently accessed data
- [ ] Implement proper error handling
- [ ] Monitor resource usage
- [ ] Optimize bundle size for UI plugins
- [ ] Use connection pooling for databases

### Integration Best Practices
- [ ] Use TaylorDash Plugin SDK
- [ ] Follow semantic versioning
- [ ] Implement proper health checks
- [ ] Handle network failures gracefully
- [ ] Implement retry logic with backoff
- [ ] Document API usage and limitations
- [ ] Provide clear error messages