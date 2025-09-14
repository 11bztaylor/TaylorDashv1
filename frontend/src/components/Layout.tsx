import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { TabletModeLayout } from './TabletModeLayout';
import { ConnectionStatus } from './ConnectionStatus';
import { UserInfo } from './UserInfo';

interface LayoutProps {
  children: React.ReactNode;
  title: string;
}

export const Layout: React.FC<LayoutProps> = ({ children, title }) => {
  const { user } = useAuth();
  const [isConnected, setIsConnected] = useState<boolean>(false);
  const [currentTime, setCurrentTime] = useState<string>('');

  React.useEffect(() => {
    const updateTime = () => {
      const now = new Date();
      setCurrentTime(now.toLocaleTimeString());
    };

    updateTime();
    const interval = setInterval(updateTime, 1000);
    return () => clearInterval(interval);
  }, []);

  // Use tablet layout if user is in single view mode
  if (user?.single_view_mode) {
    return (
      <TabletModeLayout title={title}>
        {children}
      </TabletModeLayout>
    );
  }

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      {/* Header */}
      <header className="bg-gray-800 border-b border-gray-700 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <h1 className="text-2xl font-bold text-white">TaylorDash</h1>
            <span className="text-sm text-gray-400">{title}</span>
          </div>
          <div className="flex items-center space-x-4">
            <div className="text-sm text-gray-300 font-mono">
              {currentTime}
            </div>
            <ConnectionStatus onConnectionChange={setIsConnected} />
            {user && <UserInfo />}
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-6 py-8">
        {children}
      </main>

      {/* Status Bar */}
      <div className="fixed bottom-0 left-0 right-0 bg-gray-800 border-t border-gray-700 px-6 py-2">
        <div className="flex items-center justify-between text-sm text-gray-400">
          <div className="flex items-center space-x-4">
            <span>Backend Status: {isConnected ? 'Connected' : 'Disconnected'}</span>
            <span>•</span>
            <span>API Endpoint: /api</span>
            <span>•</span>
            <span>Version: 1.0.0</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-400' : 'bg-red-400'}`}></div>
            <span>System Health</span>
          </div>
        </div>
      </div>
    </div>
  );
};