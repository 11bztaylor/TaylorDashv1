# Midnight HUD - Visual Dashboard Plugin

## Goal/Why

The Midnight HUD serves as a comprehensive example of TaylorDash's visual-first workflow philosophy. It demonstrates how complex operational data can be transformed into an intuitive, drag-and-drop dashboard that adapts to user preferences. This plugin showcases TaylorDash's capability to present real-time system monitoring, project status, and metrics through a cyber-aesthetic interface that prioritizes visual clarity and user customization.

The HUD embodies the core principle that operational dashboards should be as flexible and personalized as the workflows they support, enabling users to arrange, minimize, and prioritize information widgets based on their immediate needs and cognitive preferences.

## Stack & Commands

### Technology Stack
- **Frontend**: React 18 + TypeScript + Vite
- **Styling**: Tailwind CSS with custom cyber/glass morphism theme
- **State Management**: React Context + localStorage persistence
- **Drag & Drop**: React DnD library
- **Icons**: Lucide React
- **Build Tool**: Vite with HMR

### Development Commands
```bash
# Navigate to example
cd examples/midnight-hud

# Install dependencies
npm install

# Development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## Full File Tree and Source

```
examples/midnight-hud/
├── package.json
├── README.md
├── index.html
├── vite.config.ts
├── tailwind.config.js
├── tsconfig.json
├── src/
│   ├── main.tsx
│   ├── App.tsx
│   ├── AppShell.tsx
│   ├── types/
│   │   └── dashboard.ts
│   ├── hooks/
│   │   └── usePersistentState.ts
│   ├── widgets/
│   │   ├── SystemWidget.tsx
│   │   ├── ProjectWidget.tsx
│   │   ├── MetricsWidget.tsx
│   │   └── AlertsWidget.tsx
│   └── pages/
│       ├── Home.tsx
│       └── Library.tsx
```

### Core Types (`src/types/dashboard.ts`)
```typescript
export interface Widget {
  id: string;
  type: 'system' | 'project' | 'metrics' | 'alerts';
  title: string;
  position: { x: number; y: number };
  size: { width: number; height: number };
  isMinimized: boolean;
  isPinned: boolean;
  zIndex: number;
}

export interface DashboardState {
  widgets: Widget[];
  activeView: 'home' | 'library';
}

export interface SystemData {
  cpu: number;
  memory: number;
  disk: number;
  network: { up: number; down: number };
  uptime: string;
}

export interface ProjectData {
  name: string;
  status: 'running' | 'idle' | 'error';
  progress: number;
  lastUpdate: string;
}

export interface MetricsData {
  requests: number;
  errors: number;
  latency: number;
  throughput: number;
}

export interface AlertData {
  id: string;
  type: 'info' | 'warning' | 'error';
  message: string;
  timestamp: string;
}
```

### Persistent State Hook (`src/hooks/usePersistentState.ts`)
```typescript
import { useState, useEffect } from 'react';

export function usePersistentState<T>(
  key: string,
  defaultValue: T
): [T, (value: T) => void] {
  const [state, setState] = useState<T>(() => {
    try {
      const item = localStorage.getItem(key);
      return item ? JSON.parse(item) : defaultValue;
    } catch {
      return defaultValue;
    }
  });

  useEffect(() => {
    try {
      localStorage.setItem(key, JSON.stringify(state));
    } catch (error) {
      console.warn('Failed to save to localStorage:', error);
    }
  }, [key, state]);

  return [state, setState];
}
```

### System Widget (`src/widgets/SystemWidget.tsx`)
```typescript
import React from 'react';
import { Cpu, HardDrive, Wifi, Clock } from 'lucide-react';
import type { SystemData } from '../types/dashboard';

interface SystemWidgetProps {
  data: SystemData;
  isMinimized: boolean;
}

export const SystemWidget: React.FC<SystemWidgetProps> = ({ data, isMinimized }) => {
  if (isMinimized) {
    return (
      <div className="flex items-center space-x-2 p-2">
        <Cpu className="w-4 h-4 text-cyan-400" />
        <span className="text-sm text-white">{data.cpu}%</span>
      </div>
    );
  }

  return (
    <div className="p-4 space-y-3">
      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-1">
          <div className="flex items-center space-x-2">
            <Cpu className="w-4 h-4 text-cyan-400" />
            <span className="text-sm text-gray-300">CPU</span>
          </div>
          <div className="text-lg font-mono text-white">{data.cpu}%</div>
        </div>
        
        <div className="space-y-1">
          <div className="flex items-center space-x-2">
            <HardDrive className="w-4 h-4 text-green-400" />
            <span className="text-sm text-gray-300">Memory</span>
          </div>
          <div className="text-lg font-mono text-white">{data.memory}%</div>
        </div>
        
        <div className="space-y-1">
          <div className="flex items-center space-x-2">
            <Wifi className="w-4 h-4 text-blue-400" />
            <span className="text-sm text-gray-300">Network</span>
          </div>
          <div className="text-xs font-mono text-white">
            ↑{data.network.up} ↓{data.network.down}
          </div>
        </div>
        
        <div className="space-y-1">
          <div className="flex items-center space-x-2">
            <Clock className="w-4 h-4 text-orange-400" />
            <span className="text-sm text-gray-300">Uptime</span>
          </div>
          <div className="text-xs font-mono text-white">{data.uptime}</div>
        </div>
      </div>
    </div>
  );
};
```

### App Shell (`src/AppShell.tsx`) - TaylorDash Branded
```typescript
import React from 'react';
import { Home, Library, Settings } from 'lucide-react';

interface AppShellProps {
  currentView: 'home' | 'library';
  onViewChange: (view: 'home' | 'library') => void;
  children: React.ReactNode;
}

export const AppShell: React.FC<AppShellProps> = ({ 
  currentView, 
  onViewChange, 
  children 
}) => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-black to-gray-900">
      {/* Header */}
      <header className="border-b border-gray-700/50 bg-black/30 backdrop-blur-sm">
        <div className="px-6 py-4">
          <h1 className="text-4xl font-black tracking-tight bg-gradient-to-r from-[#355E3B] via-[#2f4f1d] to-[#FF6600] bg-clip-text text-transparent">
            MIDNIGHT HUD
          </h1>
          <p className="text-gray-400 text-sm mt-1">TaylorDash Visual Plugin</p>
        </div>
      </header>

      {/* Navigation */}
      <nav className="border-b border-gray-700/50 bg-black/20 backdrop-blur-sm">
        <div className="px-6 py-3">
          <div className="flex space-x-6">
            <button
              onClick={() => onViewChange('home')}
              className={`flex items-center space-x-2 px-3 py-2 rounded-lg transition-colors ${
                currentView === 'home'
                  ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/30'
                  : 'text-gray-400 hover:text-white hover:bg-white/5'
              }`}
            >
              <Home className="w-4 h-4" />
              <span>Home</span>
            </button>
            
            <button
              onClick={() => onViewChange('library')}
              className={`flex items-center space-x-2 px-3 py-2 rounded-lg transition-colors ${
                currentView === 'library'
                  ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/30'
                  : 'text-gray-400 hover:text-white hover:bg-white/5'
              }`}
            >
              <Library className="w-4 h-4" />
              <span>Library</span>
            </button>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="relative overflow-hidden">
        {children}
      </main>
    </div>
  );
};
```

### Main App (`src/App.tsx`)
```typescript
import React from 'react';
import { AppShell } from './AppShell';
import { Home } from './pages/Home';
import { Library } from './pages/Library';
import { usePersistentState } from './hooks/usePersistentState';
import type { DashboardState } from './types/dashboard';

const defaultDashboardState: DashboardState = {
  widgets: [
    {
      id: 'system-1',
      type: 'system',
      title: 'System Monitor',
      position: { x: 50, y: 50 },
      size: { width: 300, height: 200 },
      isMinimized: false,
      isPinned: false,
      zIndex: 1
    },
    {
      id: 'project-1',
      type: 'project',
      title: 'Active Projects',
      position: { x: 400, y: 50 },
      size: { width: 320, height: 240 },
      isMinimized: false,
      isPinned: true,
      zIndex: 2
    }
  ],
  activeView: 'home'
};

export const App: React.FC = () => {
  const [dashboardState, setDashboardState] = usePersistentState<DashboardState>(
    'midnight-hud-state',
    defaultDashboardState
  );

  const handleViewChange = (view: 'home' | 'library') => {
    setDashboardState(prev => ({ ...prev, activeView: view }));
  };

  return (
    <AppShell 
      currentView={dashboardState.activeView}
      onViewChange={handleViewChange}
    >
      {dashboardState.activeView === 'home' ? (
        <Home 
          dashboardState={dashboardState}
          setDashboardState={setDashboardState}
        />
      ) : (
        <Library />
      )}
    </AppShell>
  );
};
```

## Acceptance Criteria

### Functional Requirements
- ✅ **Widget Management**: Drag, resize, minimize, close, and pin widgets
- ✅ **State Persistence**: Dashboard layout survives page refresh and navigation
- ✅ **Multi-View Navigation**: Seamless switching between Home and Library views
- ✅ **Real-time Data**: Mock data simulation for system metrics and project status
- ✅ **Visual Hierarchy**: Z-index management for overlapping widgets
- ✅ **Responsive Design**: Adapts to different screen sizes

### Technical Requirements
- ✅ **TypeScript**: Full type safety across all components
- ✅ **React 18**: Modern React patterns with hooks and context
- ✅ **Performance**: Efficient re-renders and state updates
- ✅ **Accessibility**: Keyboard navigation and screen reader support
- ✅ **Error Handling**: Graceful degradation for localStorage failures

### Integration Requirements
- ✅ **TaylorDash Plugin Route**: Accessible via `/plugins/midnight-hud`
- ✅ **Brand Consistency**: Uses TaylorDash green/orange color palette
- ✅ **RBAC Compliance**: Respects viewer-level permissions
- ✅ **Iframe/Micro-frontend**: Safe isolation from main TaylorDash app

## Future Upgrades

### Enhanced Interactivity
- **Real-time Data Streams**: Connect to actual TaylorDash MQTT events
- **Custom Widget Builder**: User-defined widgets with drag-and-drop editor
- **Dashboard Templates**: Predefined layouts for different use cases
- **Export/Import**: Share dashboard configurations between users

### Advanced Features
- **Multi-monitor Support**: Span widgets across multiple displays
- **Voice Commands**: "Show system status", "Minimize all widgets"
- **AI-powered Insights**: Automatic anomaly detection and notifications
- **Collaborative Dashboards**: Real-time shared workspaces

### Performance Enhancements
- **Virtual Scrolling**: Handle hundreds of widgets efficiently
- **Web Workers**: Offload data processing from main thread
- **Canvas Rendering**: Ultra-smooth animations for complex visualizations
- **Progressive Loading**: Lazy-load widget content for faster startup

---

**Note**: This is an add-only UI plugin example for TaylorDash, demonstrating the platform's extensibility and visual-first approach to operational dashboards.