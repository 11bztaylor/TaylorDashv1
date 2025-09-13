# Frontend Quick Reference

## 🚀 Start Frontend

```bash
cd /TaylorProjects/TaylorDashv1/frontend
npm install
npm run dev

# Or via Docker
docker compose up frontend -d
```

## 📍 Key Files

- **`src/App.tsx`** - Main React app with routing and authentication
- **`src/contexts/AuthContext.tsx`** - User authentication state management
- **`src/services/`** - External service integrations
  - `api.ts` - HTTP client for backend API
  - `mqttService.ts` - MQTT client for real-time events
  - `eventBus.ts` - Internal event bus for component communication
- **`src/components/`** - Reusable React components
  - `LoginPage.tsx` - User authentication UI
  - `ProjectsList.tsx` - Project management interface
  - `PluginPage.tsx` - Plugin system interface
  - `FlowCanvas.tsx` - React Flow visual canvas
  - `ErrorBoundary.tsx` - Error handling and notifications
- **`src/plugins/registry.ts`** - Plugin registration and management
- **`src/types/api.ts`** - TypeScript type definitions
- **`src/utils/errorHandling.ts`** - Error management utilities

## 🔑 Environment Variables

```bash
# Required in .env
VITE_API_KEY=taylordash-dev-key
VITE_BACKEND_URL=http://localhost:8000

# Optional
VITE_MQTT_URL=ws://localhost:9001
VITE_ENVIRONMENT=development
```

## 🛠 Component Architecture

### Main App Structure
```tsx
App (Router, AuthProvider, ErrorBoundary)
├── Navigation (only in desktop mode)
├── Routes
│   ├── LoginPage (public)
│   ├── Dashboard (protected)
│   ├── ProjectsPage (protected)
│   ├── FlowPage (protected)
│   ├── SettingsPage (protected)
│   └── PluginPage (protected)
└── NotificationContainer
```

### Layout Patterns
```tsx
// Standard layout with header/footer
<Layout title="Page Title">
  <YourContent />
</Layout>

// Tablet mode (single view)
<TabletModeLayout title="Page Title">
  <YourContent />
</TabletModeLayout>
```

### Authentication Context
```tsx
const { user, login, logout, isAuthenticated } = useAuth();

// Protected routes
<ProtectedRoute>
  <YourComponent />
</ProtectedRoute>
```

## 🌐 API Integration

### HTTP Client Setup
```tsx
import { apiClient } from '../services/api';

// Automatic API key and auth headers
const projects = await apiClient.get('/api/v1/projects');
const newProject = await apiClient.post('/api/v1/projects', projectData);
```

### Manual API Calls
```tsx
const sessionToken = localStorage.getItem('taylordash_session_token');
const headers: HeadersInit = {
  'Content-Type': 'application/json',
  'X-API-Key': import.meta.env.VITE_API_KEY || 'taylordash-dev-key'
};

if (sessionToken) {
  headers['Authorization'] = `Bearer ${sessionToken}`;
}

const response = await fetch('/api/v1/projects', {
  method: 'POST',
  headers,
  body: JSON.stringify(data)
});
```

## 📡 Real-time Updates

### MQTT Service
```tsx
import { mqttService } from '../services/mqttService';

// Subscribe to events
useEffect(() => {
  const unsubscribe = mqttService.subscribe('tracker/events/projects/#', (topic, message) => {
    console.log('Project event:', topic, message);
    // Update local state
  });

  return unsubscribe;
}, []);

// Publish events
mqttService.publish('tracker/events/ui/action', {
  action: 'button_click',
  component: 'ProjectsList'
});
```

### Event Bus (Internal)
```tsx
import { eventBusService } from '../services/eventBus';

// Subscribe to internal events
useEffect(() => {
  const unsubscribe = eventBusService.subscribe('project:updated', (data) => {
    // Handle project update
  });

  return unsubscribe;
}, []);

// Emit events
eventBusService.emit('project:created', newProject);
```

## 🎨 Styling with Tailwind

### Common Classes
```tsx
// Layout
className="min-h-screen bg-gray-900 text-white"
className="container mx-auto px-6 py-8"
className="grid grid-cols-1 lg:grid-cols-2 gap-8"

// Components
className="bg-gray-800 rounded-lg p-6"
className="bg-gray-700 border border-gray-600 rounded"

// Buttons
className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors"
className="bg-gray-600 hover:bg-gray-700 text-white px-3 py-2 rounded transition-colors"

// Status indicators
className={`px-2 py-1 rounded text-xs font-medium ${
  status === 'active' ? 'bg-green-900 text-green-300' :
  status === 'completed' ? 'bg-blue-900 text-blue-300' :
  'bg-gray-600 text-gray-300'
}`}
```

### Dark Theme Colors
```css
/* Primary grays */
bg-gray-900   /* Main background */
bg-gray-800   /* Card/header background */
bg-gray-700   /* Input/button background */
bg-gray-600   /* Hover states */

/* Text colors */
text-white    /* Primary text */
text-gray-300 /* Secondary text */
text-gray-400 /* Tertiary text */
text-gray-500 /* Placeholder text */

/* Status colors */
text-green-400, bg-green-900  /* Success */
text-red-400, bg-red-900      /* Error */
text-yellow-400, bg-yellow-900 /* Warning */
text-blue-400, bg-blue-900    /* Info */
```

## 🔌 Plugin System

### Plugin Registration
```tsx
// src/plugins/registry.ts
export const pluginRegistry = {
  'mcp-manager': {
    name: 'MCP Manager',
    path: '/plugins/mcp-manager',
    component: () => import('../pages/plugins/MCPManagerPage'),
    icon: 'Plug',
    description: 'Model Context Protocol management'
  },
  'midnight-hud': {
    name: 'Midnight HUD',
    path: '/plugins/midnight-hud',
    component: () => import('../../examples/midnight-hud/src/App'),
    icon: 'Monitor',
    description: 'Draggable HUD widgets'
  }
};
```

### Plugin Component
```tsx
// Plugin page structure
export const YourPluginPage: React.FC = () => {
  return (
    <Layout title="Your Plugin">
      <div className="pb-16">
        {/* Plugin content */}
      </div>
    </Layout>
  );
};
```

## 📱 Responsive Design

### Breakpoints
```tsx
// Mobile first approach
className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3"

// Responsive spacing
className="px-4 md:px-6 lg:px-8"
className="py-4 md:py-6 lg:py-8"

// Responsive text
className="text-sm md:text-base lg:text-lg"
```

### Tablet Mode
```tsx
// Detected via AuthContext
const { user } = useAuth();
if (user?.single_view_mode) {
  return <TabletModeLayout>{children}</TabletModeLayout>;
}
```

## 🔍 Debugging & Development

### Error Handling
```tsx
import { notificationManager } from '../utils/errorHandling';

try {
  const result = await riskyOperation();
  notificationManager.showSuccess('Operation completed');
} catch (error) {
  notificationManager.showError(error);
}
```

### Performance Monitoring
```tsx
import { measureAsyncPerformance } from '../utils/errorHandling';

const data = await measureAsyncPerformance(
  () => fetchLargeDataset(),
  'fetchLargeDataset',
  2000 // 2 second threshold
);
```

### Development Tools
```bash
# Hot reload development server
npm run dev

# Type checking
npm run type-check

# Linting
npm run lint

# Build for production
npm run build

# Preview production build
npm run preview
```

## 🤖 For AI Agents

### Quick Context
React + TypeScript frontend with Tailwind CSS, featuring authentication, real-time updates via MQTT, plugin system, and comprehensive error handling. Uses modern React patterns with hooks and context.

### Your Tools
- **Command**: `npm run dev` (start development server)
- **File**: `/TaylorProjects/TaylorDashv1/frontend/src/App.tsx` (main app)
- **Pattern**: Create components in `src/components/`, use hooks and context
- **Auth**: Wrap components with `<ProtectedRoute>` for auth requirement

### Common Pitfalls
- ⚠️ Missing API key in headers (`X-API-Key`)
- ⚠️ Not wrapping async operations in try/catch with notifications
- ⚠️ Forgetting to cleanup subscriptions in useEffect cleanup
- ⚠️ Not handling loading states in components
- ⚠️ Missing TypeScript types for new interfaces

### Success Criteria
- ✅ Development server starts on http://localhost:3000
- ✅ All API calls include proper authentication headers
- ✅ Components handle loading and error states gracefully
- ✅ Real-time updates work via MQTT subscriptions
- ✅ Responsive design works on mobile and desktop
- ✅ TypeScript compilation succeeds without errors

## 📚 Dependencies

### Core Libraries
```json
{
  "react": "^18.x",
  "react-dom": "^18.x",
  "react-router-dom": "^6.x",
  "typescript": "^5.x"
}
```

### UI & Styling
```json
{
  "tailwindcss": "^3.x",
  "lucide-react": "^0.x",
  "@headlessui/react": "^1.x"
}
```

### Development Tools
```json
{
  "vite": "^5.x",
  "@vitejs/plugin-react": "^4.x",
  "eslint": "^8.x",
  "@typescript-eslint/parser": "^6.x"
}
```

### Build Commands
```bash
# Install dependencies
npm install

# Development
npm run dev           # Start dev server
npm run type-check    # TypeScript checking
npm run lint          # ESLint

# Production
npm run build         # Build for production
npm run preview       # Preview production build

# Docker
docker build -t taylordash-frontend .
docker run -p 3000:80 taylordash-frontend
```