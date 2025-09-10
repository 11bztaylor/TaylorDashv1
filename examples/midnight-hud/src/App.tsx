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