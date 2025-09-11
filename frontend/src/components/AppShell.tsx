import React from 'react';
import { Navigation } from './Navigation';
import { StatusBar } from './StatusBar';

interface AppShellProps {
  children: React.ReactNode;
}

export function AppShell({ children }: AppShellProps) {
  return (
    <div className="flex h-screen bg-gradient-midnight overflow-hidden">
      {/* Navigation Sidebar */}
      <Navigation />
      
      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Main Content */}
        <main className="flex-1 overflow-hidden">
          {children}
        </main>
        
        {/* Status Bar */}
        <StatusBar />
      </div>
    </div>
  );
}