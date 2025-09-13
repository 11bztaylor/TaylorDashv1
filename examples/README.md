# 🧩 TaylorDash Plugin Examples

Reference implementations and example plugins demonstrating TaylorDash plugin development patterns, security practices, and integration techniques.

## 📁 Example Plugins

- **`midnight-hud/`** - System monitoring HUD with real-time metrics
- **`projects-manager/`** - Project management and task tracking plugin
- **`mcp-manager/`** - Model Context Protocol integration plugin

## 💻 Code Examples

### Common Patterns

#### Plugin Manifest Structure
```json
// plugin.json - Plugin manifest
{
  "id": "my-awesome-plugin",
  "name": "My Awesome Plugin",
  "version": "1.0.0",
  "description": "An example plugin for TaylorDash",
  "author": "Your Name",
  "license": "MIT",
  "type": "ui",
  "entry": "src/index.tsx",
  "permissions": [
    "api:read",
    "api:write",
    "mqtt:subscribe",
    "storage:read"
  ],
  "routes": [
    {
      "path": "/my-plugin",
      "component": "MyPluginPage"
    }
  ],
  "config": {
    "theme": "dark",
    "refreshInterval": 5000,
    "features": {
      "realtime": true,
      "notifications": false
    }
  },
  "dependencies": {
    "react": "^18.0.0",
    "mqtt": "^4.3.0"
  }
}
```

#### Basic Plugin Component
```typescript
// src/index.tsx - Main plugin component
import React, { useState, useEffect } from 'react';
import { PluginComponent, usePluginAPI, useMQTT } from '@taylordash/plugin-sdk';

interface MyPluginProps {
  config: {
    theme: string;
    refreshInterval: number;
    features: {
      realtime: boolean;
      notifications: boolean;
    };
  };
}

export const MyAwesomePlugin: PluginComponent<MyPluginProps> = ({ config }) => {
  const [data, setData] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const api = usePluginAPI();
  const mqtt = useMQTT();

  useEffect(() => {
    loadData();

    if (config.features.realtime) {
      // Subscribe to real-time updates
      mqtt.subscribe('tracker/events/+', (topic, message) => {
        console.log(`Received: ${topic}`, JSON.parse(message.toString()));
        // Update component state based on real-time data
      });
    }

    return () => {
      if (config.features.realtime) {
        mqtt.unsubscribe('tracker/events/+');
      }
    };
  }, [config]);

  const loadData = async () => {
    setLoading(true);
    try {
      const response = await api.get('/api/v1/my-plugin/data');
      setData(response.data);
    } catch (error) {
      console.error('Failed to load data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAction = async (item: any) => {
    try {
      await api.post('/api/v1/my-plugin/action', { item_id: item.id });
      await loadData(); // Refresh data
    } catch (error) {
      console.error('Action failed:', error);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-cyan-500"></div>
        <span className="ml-2 text-gray-400">Loading...</span>
      </div>
    );
  }

  return (
    <div className={`plugin-container theme-${config.theme}`}>
      <div className="p-4 bg-gray-800 rounded-lg">
        <h2 className="text-xl font-semibold text-white mb-4">
          My Awesome Plugin
        </h2>

        <div className="space-y-2">
          {data.map((item, index) => (
            <div
              key={item.id || index}
              className="bg-gray-700 hover:bg-gray-600 rounded p-3 cursor-pointer transition-colors"
              onClick={() => handleAction(item)}
            >
              <div className="flex items-center justify-between">
                <span className="text-white">{item.name}</span>
                <span className="text-gray-400 text-sm">{item.status}</span>
              </div>
            </div>
          ))}
        </div>

        {config.features.notifications && (
          <div className="mt-4 text-sm text-gray-400">
            Notifications enabled
          </div>
        )}
      </div>
    </div>
  );
};

export default MyAwesomePlugin;
```

#### Plugin API Integration
```typescript
// src/api.ts - API integration helpers
import { PluginAPI } from '@taylordash/plugin-sdk';

export class MyPluginAPI {
  constructor(private api: PluginAPI) {}

  async getItems(): Promise<any[]> {
    const response = await this.api.get('/api/v1/my-plugin/items');
    return response.data;
  }

  async createItem(item: any): Promise<any> {
    const response = await this.api.post('/api/v1/my-plugin/items', item);
    return response.data;
  }

  async updateItem(id: string, updates: any): Promise<any> {
    const response = await this.api.put(`/api/v1/my-plugin/items/${id}`, updates);
    return response.data;
  }

  async deleteItem(id: string): Promise<void> {
    await this.api.delete(`/api/v1/my-plugin/items/${id}`);
  }

  async getConfig(): Promise<any> {
    const response = await this.api.get('/api/v1/my-plugin/config');
    return response.data;
  }

  async updateConfig(config: any): Promise<any> {
    const response = await this.api.put('/api/v1/my-plugin/config', config);
    return response.data;
  }
}

// Usage in component
export const useMyPluginAPI = () => {
  const api = usePluginAPI();
  return new MyPluginAPI(api);
};
```

### How to Extend

#### 1. Create New Plugin
```bash
# Create plugin directory structure
mkdir my-new-plugin
cd my-new-plugin

# Create basic files
touch plugin.json
mkdir -p src components styles tests

# Initialize package.json
npm init -y

# Install dependencies
npm install react react-dom typescript @types/react @types/react-dom
npm install --save-dev @vitejs/plugin-react vite
```

#### 2. Plugin Development Template
```typescript
// src/types.ts - Plugin type definitions
export interface PluginConfig {
  theme: 'light' | 'dark';
  autoRefresh: boolean;
  refreshInterval: number;
}

export interface PluginState {
  data: any[];
  loading: boolean;
  error: string | null;
}

export interface PluginActions {
  loadData: () => Promise<void>;
  refresh: () => Promise<void>;
  handleError: (error: Error) => void;
}
```

#### 3. Plugin Hooks Pattern
```typescript
// src/hooks/usePluginState.ts
import { useState, useEffect, useCallback } from 'react';
import { PluginConfig, PluginState } from '../types';

export const usePluginState = (config: PluginConfig) => {
  const [state, setState] = useState<PluginState>({
    data: [],
    loading: false,
    error: null
  });

  const loadData = useCallback(async () => {
    setState(prev => ({ ...prev, loading: true, error: null }));

    try {
      // Load data logic here
      const data = await fetchPluginData();
      setState(prev => ({ ...prev, data, loading: false }));
    } catch (error) {
      setState(prev => ({
        ...prev,
        loading: false,
        error: error instanceof Error ? error.message : 'Unknown error'
      }));
    }
  }, []);

  const refresh = useCallback(async () => {
    await loadData();
  }, [loadData]);

  useEffect(() => {
    loadData();

    if (config.autoRefresh) {
      const interval = setInterval(refresh, config.refreshInterval);
      return () => clearInterval(interval);
    }
  }, [config, loadData, refresh]);

  return {
    ...state,
    loadData,
    refresh
  };
};
```

### Testing This Component

#### Plugin Testing Setup
```typescript
// tests/setup.ts
import { vi } from 'vitest';

// Mock plugin SDK
vi.mock('@taylordash/plugin-sdk', () => ({
  usePluginAPI: () => ({
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn()
  }),
  useMQTT: () => ({
    subscribe: vi.fn(),
    unsubscribe: vi.fn(),
    publish: vi.fn()
  }),
  PluginComponent: ({ children }: any) => children
}));
```

#### Plugin Component Tests
```typescript
// tests/MyAwesomePlugin.test.tsx
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { vi } from 'vitest';
import MyAwesomePlugin from '../src/index';

const mockConfig = {
  theme: 'dark',
  refreshInterval: 5000,
  features: {
    realtime: true,
    notifications: false
  }
};

describe('MyAwesomePlugin', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders plugin correctly', () => {
    render(<MyAwesomePlugin config={mockConfig} />);

    expect(screen.getByText('My Awesome Plugin')).toBeInTheDocument();
  });

  it('loads data on mount', async () => {
    const mockApi = {
      get: vi.fn().mockResolvedValue({
        data: [
          { id: '1', name: 'Test Item', status: 'active' }
        ]
      })
    };

    render(<MyAwesomePlugin config={mockConfig} />);

    await waitFor(() => {
      expect(screen.getByText('Test Item')).toBeInTheDocument();
    });
  });

  it('handles errors gracefully', async () => {
    const mockApi = {
      get: vi.fn().mockRejectedValue(new Error('Network error'))
    };

    render(<MyAwesomePlugin config={mockConfig} />);

    // Should not crash and should handle error
    await waitFor(() => {
      expect(console.error).toHaveBeenCalled();
    });
  });
});
```

### Debugging Tips

#### Plugin Development Debugging
```typescript
// src/debug.ts - Debug utilities
export const debug = {
  log: (message: string, data?: any) => {
    if (process.env.NODE_ENV === 'development') {
      console.log(`[MyPlugin] ${message}`, data);
    }
  },

  error: (message: string, error?: any) => {
    console.error(`[MyPlugin] ${message}`, error);
  },

  warn: (message: string, data?: any) => {
    console.warn(`[MyPlugin] ${message}`, data);
  }
};

// Usage in component
import { debug } from './debug';

const MyComponent = () => {
  useEffect(() => {
    debug.log('Component mounted');

    return () => {
      debug.log('Component unmounted');
    };
  }, []);

  const handleAction = async () => {
    try {
      debug.log('Performing action...');
      await performAction();
      debug.log('Action completed successfully');
    } catch (error) {
      debug.error('Action failed', error);
    }
  };
};
```

### API Usage

#### Plugin Registration Example
```javascript
// Example: Registering a new plugin
export const MyPlugin = {
  id: 'my-plugin',
  name: 'My Plugin',
  component: MyPluginComponent,
  permissions: ['read', 'write'],
  routes: [
    {
      path: '/my-plugin',
      component: MyPluginPage
    },
    {
      path: '/my-plugin/settings',
      component: MyPluginSettings
    }
  ],
  config: {
    defaultTheme: 'dark',
    features: ['realtime', 'notifications']
  }
};
```

#### MQTT Event Publishing
```typescript
// Example: Publishing events from plugin
export const publishPluginEvent = async (mqtt: any, eventType: string, data: any) => {
  const event = {
    plugin_id: 'my-awesome-plugin',
    event_type: eventType,
    timestamp: new Date().toISOString(),
    data
  };

  await mqtt.publish(
    `tracker/events/plugin/${eventType}`,
    JSON.stringify(event)
  );
};

// Usage in component
const handleDataUpdate = async (newData: any) => {
  // Update local state
  setData(newData);

  // Publish event for other components
  await publishPluginEvent(mqtt, 'data_updated', newData);
};
```

#### Plugin Configuration Management
```typescript
// src/config.ts - Configuration management
export class PluginConfigManager {
  constructor(private api: PluginAPI, private pluginId: string) {}

  async getConfig(): Promise<any> {
    try {
      const response = await this.api.get(`/api/v1/plugins/${this.pluginId}/config`);
      return response.data;
    } catch (error) {
      console.error('Failed to load plugin config:', error);
      return this.getDefaultConfig();
    }
  }

  async updateConfig(updates: Partial<any>): Promise<any> {
    const currentConfig = await this.getConfig();
    const newConfig = { ...currentConfig, ...updates };

    await this.api.put(`/api/v1/plugins/${this.pluginId}/config`, newConfig);
    return newConfig;
  }

  private getDefaultConfig() {
    return {
      theme: 'dark',
      refreshInterval: 5000,
      features: {
        realtime: true,
        notifications: false
      }
    };
  }
}
```

## 🔧 Plugin Development Best Practices

- Follow the plugin manifest schema strictly
- Use TypeScript for type safety
- Implement proper error handling and loading states
- Follow TaylorDash design patterns and theming
- Test plugins thoroughly before deployment
- Use semantic versioning for plugin releases
- Document plugin APIs and configuration options

## 🚀 Plugin Deployment

```bash
# Build plugin for production
npm run build

# Validate plugin manifest
taylordash-cli validate plugin.json

# Package plugin
taylordash-cli package .

# Install plugin locally for testing
taylordash-cli install ./my-plugin.tar.gz

# Publish plugin to registry
taylordash-cli publish ./my-plugin.tar.gz
```