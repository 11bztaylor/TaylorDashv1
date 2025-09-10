import React, { useState, useEffect } from 'react';
import { DndProvider } from 'react-dnd';
import { HTML5Backend } from 'react-dnd-html5-backend';
import { Minimize2, X, Pin, PinOff } from 'lucide-react';
import { SystemWidget } from '../widgets/SystemWidget';
import { ProjectWidget } from '../widgets/ProjectWidget';
import type { DashboardState, Widget, SystemData, ProjectData } from '../types/dashboard';

interface HomeProps {
  dashboardState: DashboardState;
  setDashboardState: (state: DashboardState) => void;
}

export const Home: React.FC<HomeProps> = ({ dashboardState, setDashboardState }) => {
  const [systemData, setSystemData] = useState<SystemData>({
    cpu: 45,
    memory: 68,
    disk: 82,
    network: { up: 125, down: 890 },
    uptime: '7d 14h 23m'
  });

  const [projectData, setProjectData] = useState<ProjectData[]>([
    { name: 'TaylorDash Core', status: 'running', progress: 87, lastUpdate: '2m ago' },
    { name: 'MQTT Bridge', status: 'running', progress: 100, lastUpdate: '5m ago' },
    { name: 'Analytics Engine', status: 'idle', progress: 42, lastUpdate: '1h ago' }
  ]);

  // Simulate real-time data updates
  useEffect(() => {
    const interval = setInterval(() => {
      setSystemData(prev => ({
        ...prev,
        cpu: Math.max(20, Math.min(95, prev.cpu + (Math.random() - 0.5) * 10)),
        memory: Math.max(30, Math.min(90, prev.memory + (Math.random() - 0.5) * 5)),
        network: {
          up: Math.max(50, Math.min(500, prev.network.up + (Math.random() - 0.5) * 50)),
          down: Math.max(200, Math.min(1200, prev.network.down + (Math.random() - 0.5) * 100))
        }
      }));
    }, 3000);

    return () => clearInterval(interval);
  }, []);

  const updateWidget = (widgetId: string, updates: Partial<Widget>) => {
    setDashboardState({
      ...dashboardState,
      widgets: dashboardState.widgets.map(widget =>
        widget.id === widgetId ? { ...widget, ...updates } : widget
      )
    });
  };

  const closeWidget = (widgetId: string) => {
    setDashboardState({
      ...dashboardState,
      widgets: dashboardState.widgets.filter(widget => widget.id !== widgetId)
    });
  };

  const renderWidget = (widget: Widget) => {
    let content;
    switch (widget.type) {
      case 'system':
        content = <SystemWidget data={systemData} isMinimized={widget.isMinimized} />;
        break;
      case 'project':
        content = <ProjectWidget data={projectData} isMinimized={widget.isMinimized} />;
        break;
      default:
        content = <div className="p-4 text-gray-400">Unknown widget type</div>;
    }

    return (
      <div
        key={widget.id}
        className="absolute bg-black/40 backdrop-blur-sm border border-gray-700/50 rounded-lg shadow-2xl"
        style={{
          left: widget.position.x,
          top: widget.position.y,
          width: widget.isMinimized ? 'auto' : widget.size.width,
          height: widget.isMinimized ? 'auto' : widget.size.height,
          zIndex: widget.zIndex
        }}
      >
        {/* Widget Header */}
        <div className="flex items-center justify-between p-2 border-b border-gray-700/50 bg-black/20">
          <span className="text-sm font-medium text-white">{widget.title}</span>
          <div className="flex items-center space-x-1">
            <button
              onClick={() => updateWidget(widget.id, { isPinned: !widget.isPinned })}
              className="p-1 hover:bg-white/10 rounded text-gray-400 hover:text-white"
            >
              {widget.isPinned ? <PinOff className="w-3 h-3" /> : <Pin className="w-3 h-3" />}
            </button>
            <button
              onClick={() => updateWidget(widget.id, { isMinimized: !widget.isMinimized })}
              className="p-1 hover:bg-white/10 rounded text-gray-400 hover:text-white"
            >
              <Minimize2 className="w-3 h-3" />
            </button>
            <button
              onClick={() => closeWidget(widget.id)}
              className="p-1 hover:bg-red-500/20 rounded text-gray-400 hover:text-red-400"
            >
              <X className="w-3 h-3" />
            </button>
          </div>
        </div>

        {/* Widget Content */}
        {content}
      </div>
    );
  };

  return (
    <DndProvider backend={HTML5Backend}>
      <div className="relative h-screen bg-gradient-to-br from-gray-900/50 via-black/50 to-gray-900/50">
        {/* Background Grid */}
        <div className="absolute inset-0 opacity-10">
          <div className="grid grid-cols-12 grid-rows-12 h-full border-l border-t border-gray-500">
            {Array.from({ length: 144 }).map((_, i) => (
              <div key={i} className="border-r border-b border-gray-500" />
            ))}
          </div>
        </div>

        {/* Widgets */}
        {dashboardState.widgets.map(renderWidget)}

        {/* HUD Overlay Info */}
        <div className="absolute bottom-4 left-4 text-xs text-gray-500 space-y-1">
          <div>Widgets: {dashboardState.widgets.length}</div>
          <div>Active: {dashboardState.widgets.filter(w => !w.isMinimized).length}</div>
          <div>Last update: {new Date().toLocaleTimeString()}</div>
        </div>
      </div>
    </DndProvider>
  );
};