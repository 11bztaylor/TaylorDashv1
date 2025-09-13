# ⚛️ TaylorDash Frontend Components

React components for the TaylorDash frontend. Built with TypeScript, Tailwind CSS, and modern React patterns.

## 📁 Current Components

- **`LoginPage.tsx`** - Authentication interface with role-based login
- **`ErrorBoundary.tsx`** - React error boundary for graceful error handling
- **`FlowCanvas.tsx`** - React Flow canvas for visual project management
- **`PluginPage.tsx`** - Plugin execution and management interface
- **`ProjectsList.tsx`** - Project listing and management
- **`ProtectedRoute.tsx`** - Route protection with authentication checks
- **`SessionWarning.tsx`** - Session timeout warnings and renewal
- **`TabletModeLayout.tsx`** - Responsive layout for tablet interfaces
- **`UserManagement.tsx`** - User administration interface
- **`ConnectionStatus.tsx`** - Real-time connection status indicator

## 💻 Code Examples

### Common Patterns

#### Creating a New Component
```typescript
import React, { useState, useEffect } from 'react';
import { User, Settings, AlertCircle } from 'lucide-react';

interface ExampleComponentProps {
  title: string;
  onAction?: (data: any) => void;
  className?: string;
  children?: React.ReactNode;
}

export const ExampleComponent: React.FC<ExampleComponentProps> = ({
  title,
  onAction,
  className = '',
  children
}) => {
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState<any[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/v1/example', {
        headers: {
          'X-API-Key': process.env.REACT_APP_API_KEY || 'taylordash-dev-key'
        }
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const result = await response.json();
      setData(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  };

  const handleAction = (item: any) => {
    onAction?.(item);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-cyan-500"></div>
        <span className="ml-2 text-gray-400">Loading...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-4">
        <div className="flex items-center space-x-2">
          <AlertCircle className="w-5 h-5 text-red-400" />
          <span className="text-red-400">Error: {error}</span>
        </div>
        <button
          onClick={loadData}
          className="mt-2 px-3 py-1 bg-red-500/20 hover:bg-red-500/30 rounded text-red-400 text-sm transition-colors"
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className={`bg-gray-800 rounded-lg p-4 ${className}`}>
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-semibold text-white flex items-center">
          <User className="w-5 h-5 mr-2" />
          {title}
        </h2>
        <button
          onClick={loadData}
          className="p-1 hover:bg-gray-700 rounded transition-colors"
          title="Refresh"
        >
          <Settings className="w-4 h-4 text-gray-400" />
        </button>
      </div>

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

      {children}
    </div>
  );
};
```

#### Hook Pattern for API Integration
```typescript
// hooks/useApiData.ts
import { useState, useEffect, useCallback } from 'react';

interface UseApiDataOptions {
  endpoint: string;
  dependencies?: any[];
  autoFetch?: boolean;
}

export const useApiData = <T = any>({
  endpoint,
  dependencies = [],
  autoFetch = true
}: UseApiDataOptions) => {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(endpoint, {
        headers: {
          'X-API-Key': process.env.REACT_APP_API_KEY || 'taylordash-dev-key',
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error(`Failed to fetch: ${response.statusText}`);
      }

      const result = await response.json();
      setData(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  }, [endpoint]);

  useEffect(() => {
    if (autoFetch) {
      fetchData();
    }
  }, [fetchData, autoFetch, ...dependencies]);

  return {
    data,
    loading,
    error,
    refetch: fetchData,
    setData
  };
};

// Usage in component:
export const MyComponent: React.FC = () => {
  const { data, loading, error, refetch } = useApiData<Project[]>({
    endpoint: '/api/v1/projects'
  });

  // Component render logic...
};
```

### How to Extend

#### 1. Add New Component
```typescript
// components/MyNewComponent.tsx
import React from 'react';

interface MyNewComponentProps {
  // Define your props here
}

export const MyNewComponent: React.FC<MyNewComponentProps> = (props) => {
  return (
    <div className="bg-gray-800 rounded-lg p-4">
      {/* Your component JSX */}
    </div>
  );
};
```

#### 2. Use in Pages
```typescript
// pages/MyPage.tsx
import React from 'react';
import { MyNewComponent } from '../components/MyNewComponent';

export const MyPage: React.FC = () => {
  return (
    <div className="container mx-auto px-4 py-8">
      <MyNewComponent />
    </div>
  );
};
```

#### 3. Add Route (if needed)
```typescript
// App.tsx
import { Routes, Route } from 'react-router-dom';
import { MyPage } from './pages/MyPage';

// Inside your App component:
<Routes>
  <Route path="/my-page" element={<MyPage />} />
  {/* other routes */}
</Routes>
```

### Testing This Component

#### Component Test Example
```typescript
// __tests__/ExampleComponent.test.tsx
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { ExampleComponent } from '../ExampleComponent';

// Mock fetch
global.fetch = jest.fn();

const mockFetch = fetch as jest.MockedFunction<typeof fetch>;

describe('ExampleComponent', () => {
  beforeEach(() => {
    mockFetch.mockClear();
  });

  it('renders loading state initially', () => {
    mockFetch.mockImplementation(() =>
      new Promise(resolve => setTimeout(resolve, 100))
    );

    render(<ExampleComponent title="Test Component" />);

    expect(screen.getByText('Loading...')).toBeInTheDocument();
  });

  it('renders data after successful fetch', async () => {
    const mockData = [
      { id: '1', name: 'Test Item 1', status: 'active' },
      { id: '2', name: 'Test Item 2', status: 'inactive' }
    ];

    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockData
    } as Response);

    render(<ExampleComponent title="Test Component" />);

    await waitFor(() => {
      expect(screen.getByText('Test Item 1')).toBeInTheDocument();
      expect(screen.getByText('Test Item 2')).toBeInTheDocument();
    });
  });

  it('handles errors gracefully', async () => {
    mockFetch.mockRejectedValueOnce(new Error('Network error'));

    render(<ExampleComponent title="Test Component" />);

    await waitFor(() => {
      expect(screen.getByText('Error: Network error')).toBeInTheDocument();
      expect(screen.getByText('Retry')).toBeInTheDocument();
    });
  });
});
```

### Debugging Tips

#### React Developer Tools
```bash
# Install React Developer Tools browser extension
# Enable component highlighting and profiling
```

#### Console Debugging
```typescript
// Add debug logging to components
import React, { useEffect } from 'react';

export const MyComponent: React.FC = () => {
  useEffect(() => {
    console.log('MyComponent mounted');
    return () => console.log('MyComponent unmounted');
  }, []);

  console.log('MyComponent rendering');

  return <div>My Component</div>;
};
```

#### Error Boundary Usage
```typescript
// Wrap components in ErrorBoundary for better error handling
import { ErrorBoundary } from './components/ErrorBoundary';

<ErrorBoundary
  component="MyComponent"
  onError={(error, errorInfo) => {
    console.error('Component error:', error, errorInfo);
  }}
>
  <MyComponent />
</ErrorBoundary>
```

### API Usage

#### Frontend API Service Pattern
```typescript
// services/apiService.ts
class ApiService {
  private baseUrl = process.env.REACT_APP_API_URL || '';
  private apiKey = process.env.REACT_APP_API_KEY || 'taylordash-dev-key';

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;

    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        'X-API-Key': this.apiKey,
        ...options.headers
      },
      ...options
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    return response.json();
  }

  async get<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint);
  }

  async post<T>(endpoint: string, data: any): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'POST',
      body: JSON.stringify(data)
    });
  }
}

export const apiService = new ApiService();
```

#### MQTT Integration Example
```typescript
// Example: Real-time component with MQTT
import React, { useState, useEffect } from 'react';
import mqtt from 'mqtt';

export const RealTimeComponent: React.FC = () => {
  const [messages, setMessages] = useState<any[]>([]);
  const [connected, setConnected] = useState(false);

  useEffect(() => {
    const client = mqtt.connect('ws://localhost:9001');

    client.on('connect', () => {
      setConnected(true);
      client.subscribe('tracker/events/+');
    });

    client.on('message', (topic, message) => {
      const data = JSON.parse(message.toString());
      setMessages(prev => [...prev.slice(-49), { topic, data, timestamp: Date.now() }]);
    });

    client.on('error', (error) => {
      console.error('MQTT Error:', error);
      setConnected(false);
    });

    return () => {
      client.end();
    };
  }, []);

  return (
    <div className="bg-gray-800 rounded-lg p-4">
      <div className="flex items-center space-x-2 mb-4">
        <div className={`w-3 h-3 rounded-full ${connected ? 'bg-green-400' : 'bg-red-400'}`} />
        <span className="text-white">Real-time Events</span>
      </div>

      <div className="space-y-2 max-h-64 overflow-y-auto">
        {messages.map((msg, index) => (
          <div key={index} className="bg-gray-700 rounded p-2">
            <div className="text-sm text-gray-400">{msg.topic}</div>
            <div className="text-white">{JSON.stringify(msg.data)}</div>
          </div>
        ))}
      </div>
    </div>
  );
};
```

## 🎨 Styling Guidelines

- Use Tailwind CSS classes for styling
- Follow the dark theme color palette: `gray-800`, `gray-700`, `cyan-500`, etc.
- Use responsive design: `sm:`, `md:`, `lg:` prefixes
- Consistent spacing: `p-4`, `m-2`, `space-y-4`
- Interactive elements: hover states and transitions
- Icons from `lucide-react` for consistency

## 🔧 TypeScript Best Practices

- Define interfaces for all props and state
- Use strict typing: avoid `any` when possible
- Export interfaces that other components might use
- Use generics for reusable components
- Implement proper error handling with typed exceptions

## ♿ Accessibility

- Always include `aria-label` for interactive elements
- Use semantic HTML elements (`button`, `form`, `nav`)
- Ensure keyboard navigation works
- Test with screen readers
- Maintain color contrast ratios
- Add focus indicators for keyboard users