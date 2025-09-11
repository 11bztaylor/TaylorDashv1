# TaylorDash Plugin System

## Overview

TaylorDash supports a flexible plugin architecture that enables add-only UI extensions, data integrations, and custom workflows without modifying the core application. Plugins are designed to be isolated, secure, and easily manageable.

## Plugin Types

### UI Plugins
- **Purpose**: Custom dashboard interfaces and visualizations
- **Mounting**: Iframe embedding or micro-frontend integration
- **Examples**: Midnight HUD, custom monitoring dashboards
- **Security**: Sandboxed execution with controlled permissions

### Data Plugins
- **Purpose**: External data source integrations
- **Mounting**: Backend service integration via MQTT events
- **Examples**: Third-party API connectors, database bridges
- **Security**: API key management and rate limiting

### Integration Plugins
- **Purpose**: Workflow automation and external service connections
- **Mounting**: Event-driven hooks and webhook endpoints
- **Examples**: GitHub integration, Slack notifications, CI/CD triggers
- **Security**: OAuth flows and secure credential storage

## Frontend Plugin Manifest

### Plugin Registry (`frontend/src/plugins/registry.ts`)

```typescript
export interface Plugin {
  id: string;           // Unique identifier
  name: string;         // Display name
  kind: 'ui' | 'data' | 'integration';
  path: string;         // Route path in TaylorDash
  description?: string; // Optional description
  version?: string;     // Plugin version
  permissions?: string[]; // Required RBAC permissions
}
```

### Registration Process

1. **Add to Registry**: Define plugin in `PLUGINS` array
2. **Create Route**: Add route handler in frontend routing
3. **RBAC Check**: Verify user permissions before loading
4. **Mount Plugin**: Embed via iframe or micro-frontend

### Example Registration

```typescript
export const PLUGINS: Plugin[] = [
  {
    id: "midnight-hud",
    name: "Midnight HUD",
    kind: "ui",
    path: "/plugins/midnight-hud",
    description: "Cyber-aesthetic dashboard with drag-and-drop widgets",
    version: "0.1.0",
    permissions: ["viewer"]
  }
];
```

## Plugin Surfacing Architecture

### Current Implementation: Iframe-Based Plugin System

TaylorDash currently implements plugin surfacing through iframe embedding, providing secure isolation while enabling rich plugin functionality. This approach ensures plugins operate in sandboxed environments without compromising core application security.

#### Iframe Embedding Benefits
- **Complete Isolation**: Plugins run in separate execution contexts, preventing interference with core application
- **Security Sandboxing**: Built-in browser security model with configurable sandbox attributes
- **Cross-Technology Support**: Plugins can be built with any frontend framework or technology stack
- **Fault Tolerance**: Plugin crashes don't affect the main application
- **Resource Isolation**: Memory and CPU usage contained within plugin boundaries

#### Plugin Registry System
The plugin registry maintains a centralized catalog of available plugins with metadata including permissions, versions, and mounting configurations:

```typescript
export interface PluginRegistryEntry {
  id: string;
  name: string;
  kind: 'ui' | 'data' | 'integration';
  path: string;
  iframeSrc: string;           // Plugin serving URL
  sandboxAttributes: string[]; // Security sandbox configuration
  permissions: string[];       // Required RBAC permissions
  version: string;
  description: string;
  healthEndpoint?: string;     // Optional health check URL
}
```

#### Iframe Implementation Details

```tsx
// Plugin mounting with security configuration
<iframe
  src={plugin.iframeSrc}
  className="w-full h-full border-0"
  title={plugin.name}
  sandbox="allow-scripts allow-same-origin allow-forms"
  allow="fullscreen"
  referrerPolicy="strict-origin-when-cross-origin"
  onLoad={handlePluginLoad}
  onError={handlePluginError}
/>
```

**Sandbox Attributes:**
- `allow-scripts`: Enable JavaScript execution within plugin
- `allow-same-origin`: Allow same-origin requests for plugin assets
- `allow-forms`: Enable form submission within plugin
- Additional restrictions prevent top-level navigation and popup windows

### Future Migration: Micro-Frontend Architecture

TaylorDash is architected to support future migration to micro-frontend patterns for enhanced integration while maintaining the add-only contract principle.

#### Micro-Frontend Benefits
- **Shared Context**: Direct access to TaylorDash state and services
- **Better Integration**: Native React component integration
- **Performance**: Reduced overhead compared to iframe embedding
- **Developer Experience**: Shared build tools and development environment

#### Migration Strategy
```typescript
// Future micro-frontend implementation
import { PluginComponent } from '@plugins/midnight-hud';

const MicroFrontendPlugin: React.FC<PluginProps> = ({ plugin, ...props }) => {
  return (
    <PluginBoundary plugin={plugin}>
      <PluginComponent {...props} />
    </PluginBoundary>
  );
};
```

#### Hybrid Approach
The system will support both iframe and micro-frontend mounting simultaneously:

```typescript
const PluginRenderer: React.FC<{ plugin: Plugin }> = ({ plugin }) => {
  switch (plugin.mountingStrategy) {
    case 'iframe':
      return <IframePlugin plugin={plugin} />;
    case 'microfrontend':
      return <MicroFrontendPlugin plugin={plugin} />;
    default:
      return <IframePlugin plugin={plugin} />; // Default fallback
  }
};
```

## Add-Only Contract for Plugins

### Core Principles
The add-only contract ensures TaylorDash maintains stability and security while enabling unlimited extensibility through plugins.

1. **No Core Modifications**: Plugins cannot alter existing TaylorDash routes, components, or core functionality
2. **Additive Routes**: Plugins may only add new routes, never override or modify existing ones
3. **Isolated State**: Plugin state remains completely separate from core application state
4. **Permission Boundaries**: RBAC enforcement strictly applied at all plugin interaction boundaries
5. **Resource Constraints**: Plugins operate within defined resource limits and cannot affect core performance

### Contract Enforcement
The add-only contract is enforced through multiple layers:

#### Runtime Isolation
- **Iframe Sandboxing**: Prevents direct DOM manipulation of parent application
- **Origin Separation**: Plugins served from different origins prevent cross-origin access
- **Resource Limits**: CPU and memory usage monitoring and throttling

#### Development-Time Constraints
- **Plugin Registry Validation**: All plugins must register through approved registry channels
- **Route Conflict Detection**: Automatic detection and rejection of conflicting route definitions
- **Permission Validation**: Compile-time verification of plugin permission requirements

#### API Surface Control
```typescript
// Approved plugin API surface
interface PluginAPI {
  // READ-ONLY access to application state
  readonly context: {
    user: UserInfo;
    theme: ThemeConfig;
    permissions: string[];
  };
  
  // LIMITED event publishing (plugin-scoped topics only)
  publishEvent: (topic: `plugin.${string}`, data: unknown) => void;
  
  // NO direct access to:
  // - Core routing
  // - Global state modification
  // - Other plugin state
  // - System configuration
}
```

### Plugin Lifecycle Management
All plugins operate under strict lifecycle controls that enforce the add-only contract:

1. **Registration**: Plugins must declare all capabilities and permissions upfront
2. **Validation**: Automated verification of contract compliance before activation
3. **Isolation**: Runtime enforcement of resource and access boundaries
4. **Monitoring**: Continuous monitoring for contract violations
5. **Cleanup**: Automatic cleanup and resource reclamation when plugins are removed

### Implementation Guidelines

```typescript
// ✅ Good: Adding new route
app.get('/plugins/my-plugin', handlePlugin);

// ❌ Bad: Modifying existing route
app.get('/dashboard', modifiedHandler); // Don't do this

// ✅ Good: Adding new menu item
const pluginMenuItems = PLUGINS.map(plugin => ({
  path: plugin.path,
  name: plugin.name
}));

// ❌ Bad: Modifying core menu
// Don't modify existing navigation structure
```

## Security Model

### Sandboxing
- **Iframe Sandbox**: `allow-scripts allow-same-origin allow-forms`
- **CSP Headers**: Content Security Policy enforcement
- **Origin Isolation**: Separate domain/port for plugin serving

### Permission System
```typescript
export function hasPermission(plugin: Plugin, userRole: string): boolean {
  if (!plugin.permissions) return true;
  return plugin.permissions.includes(userRole) || 
         plugin.permissions.includes('viewer');
}
```

### RBAC Integration
- **viewer**: Read-only access to plugins
- **editor**: Plugin configuration access
- **admin**: Plugin installation and management
- **Custom**: Plugin-specific permission levels

## Development Workflow

### Creating a New Plugin

1. **Define Plugin**:
```bash
mkdir examples/my-plugin
cd examples/my-plugin
npm init -y
```

2. **Register in TaylorDash**:
```typescript
// frontend/src/plugins/registry.ts
{
  id: "my-plugin",
  name: "My Plugin",
  kind: "ui",
  path: "/plugins/my-plugin",
  permissions: ["viewer"]
}
```

3. **Create Route Handler**:
```typescript
// frontend/src/pages/plugins/MyPluginPage.tsx
export const MyPluginPage: React.FC = () => {
  return (
    <iframe
      src="http://localhost:3001"
      className="w-full h-full border-0"
      title="My Plugin"
    />
  );
};
```

4. **Add Menu Entry**:
```typescript
// Add to plugin menu in navigation component
const pluginRoutes = PLUGINS.map(plugin => ({
  path: plugin.path,
  name: plugin.name,
  component: lazy(() => import(`../pages/plugins/${plugin.id}`))
}));
```

### Testing Plugins

```bash
# Start plugin development server
cd examples/my-plugin
npm run dev

# Start TaylorDash with plugin integration
cd ../../
npm run dev

# Navigate to /plugins/my-plugin
```

## Plugin Communication

### Parent-Child Messaging (Iframe)
```typescript
// Plugin -> TaylorDash
window.parent.postMessage({
  type: 'PLUGIN_EVENT',
  plugin: 'midnight-hud',
  data: { action: 'resize', height: 600 }
}, '*');

// TaylorDash -> Plugin
iframe.contentWindow.postMessage({
  type: 'DASHBOARD_STATE',
  data: { theme: 'dark', user: 'viewer' }
}, '*');
```

### Event Bus Integration
```typescript
// Plugin publishes to MQTT
publishEvent('plugin.midnight-hud.widget-created', {
  widgetId: 'system-monitor',
  timestamp: Date.now()
});

// TaylorDash core subscribes to plugin events
subscribeToTopic('plugin.+.+', handlePluginEvent);
```

## Plugin Distribution

### Local Development
- **Source**: `examples/plugin-name/`
- **Serving**: Development server (Vite, webpack, etc.)
- **Integration**: Direct iframe embedding

### Production Deployment
- **Packaging**: Static build artifacts
- **Hosting**: CDN, S3, or local static server
- **Integration**: Production URL in plugin registry

### Plugin Marketplace (Future)
- **Repository**: Centralized plugin registry
- **Installation**: One-click plugin installation
- **Versioning**: Semantic versioning with dependency management
- **Security**: Plugin signing and verification

## Best Practices

### Plugin Development
1. **Responsive Design**: Support multiple screen sizes
2. **Theme Consistency**: Use TaylorDash color palette when possible
3. **Error Handling**: Graceful degradation for network issues
4. **Performance**: Lazy loading and efficient rendering
5. **Accessibility**: Keyboard navigation and screen reader support

### Integration Patterns
1. **Stateless Plugins**: Avoid core state dependencies
2. **Event-Driven**: Use MQTT events for coordination
3. **Configuration**: External config files, not hardcoded values
4. **Documentation**: Comprehensive usage and integration docs

### Security Considerations
1. **Input Validation**: Sanitize all user inputs
2. **XSS Prevention**: Content Security Policy enforcement
3. **API Security**: Secure credential management
4. **Permission Checks**: Verify user access at plugin boundaries

## Future Enhancements

### Advanced Features
- **Plugin Hot-Reloading**: Update plugins without restart
- **Dependency Management**: Shared libraries between plugins
- **Multi-Instance**: Multiple plugin instances with different configs
- **Plugin Orchestration**: Workflow automation between plugins

### Developer Experience
- **Plugin CLI**: Scaffolding and development tools
- **Testing Framework**: Unit and integration testing for plugins
- **Debug Console**: Plugin-specific logging and debugging
- **Performance Monitoring**: Plugin resource usage tracking

---

The TaylorDash plugin system enables unlimited extensibility while maintaining security, stability, and user experience consistency.