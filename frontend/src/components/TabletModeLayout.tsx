import React, { useState, useEffect } from 'react';
import { RefreshCw, Maximize2, Minimize2, Clock } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';

interface TabletModeLayoutProps {
  children: React.ReactNode;
  title: string;
  autoRefreshInterval?: number; // in seconds, default 30
  showRefreshButton?: boolean;
  onRefresh?: () => void;
}

export const TabletModeLayout: React.FC<TabletModeLayoutProps> = ({
  children,
  title,
  autoRefreshInterval = 30,
  showRefreshButton = true,
  onRefresh
}) => {
  const { user } = useAuth();
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [currentTime, setCurrentTime] = useState<string>('');
  const [lastRefresh, setLastRefresh] = useState<Date>(new Date());
  const [refreshCountdown, setRefreshCountdown] = useState(autoRefreshInterval);
  const [isManualRefresh, setIsManualRefresh] = useState(false);

  // Update current time every second
  useEffect(() => {
    const updateTime = () => {
      const now = new Date();
      setCurrentTime(now.toLocaleTimeString([], { 
        hour: '2-digit', 
        minute: '2-digit',
        second: '2-digit',
        hour12: false
      }));
    };
    
    updateTime();
    const timeInterval = setInterval(updateTime, 1000);
    return () => clearInterval(timeInterval);
  }, []);

  // Auto-refresh countdown and execution
  useEffect(() => {
    if (autoRefreshInterval <= 0) return;

    const countdownInterval = setInterval(() => {
      setRefreshCountdown(prev => {
        if (prev <= 1) {
          handleRefresh(true);
          return autoRefreshInterval;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(countdownInterval);
  }, [autoRefreshInterval, lastRefresh]);

  const handleRefresh = (isAutomatic = false) => {
    setIsManualRefresh(!isAutomatic);
    setLastRefresh(new Date());
    setRefreshCountdown(autoRefreshInterval);
    
    if (onRefresh) {
      onRefresh();
    } else {
      // Default refresh behavior - reload the page
      window.location.reload();
    }
  };

  const toggleFullscreen = async () => {
    try {
      if (!document.fullscreenElement) {
        await document.documentElement.requestFullscreen();
        setIsFullscreen(true);
      } else {
        await document.exitFullscreen();
        setIsFullscreen(false);
      }
    } catch (error) {
      console.error('Fullscreen toggle failed:', error);
    }
  };

  // Listen for fullscreen changes
  useEffect(() => {
    const handleFullscreenChange = () => {
      setIsFullscreen(!!document.fullscreenElement);
    };

    document.addEventListener('fullscreenchange', handleFullscreenChange);
    return () => document.removeEventListener('fullscreenchange', handleFullscreenChange);
  }, []);

  return (
    <div className="min-h-screen bg-gray-900 text-white flex flex-col touch-manipulation">
      {/* Minimal Header for Tablet Mode */}
      <header className="bg-gray-800 border-b border-gray-700 px-4 py-2 flex-shrink-0">
        <div className="flex items-center justify-between">
          {/* Left side - App info */}
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <h1 className="text-xl font-bold text-white">TaylorDash</h1>
              <span className="text-sm text-gray-400">{title}</span>
            </div>
            {user && (
              <div className="hidden sm:flex items-center space-x-2 px-3 py-1 bg-gray-700 rounded-full">
                <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                <span className="text-sm text-gray-300">{user.username}</span>
                <span className="text-xs text-gray-500">({user.role})</span>
              </div>
            )}
          </div>

          {/* Right side - Controls and time */}
          <div className="flex items-center space-x-4">
            {/* Auto-refresh countdown */}
            {autoRefreshInterval > 0 && (
              <div className="hidden sm:flex items-center space-x-2 text-sm text-gray-400">
                <Clock className="w-4 h-4" />
                <span>Refresh in {refreshCountdown}s</span>
              </div>
            )}
            
            {/* Manual refresh button */}
            {showRefreshButton && (
              <button
                onClick={() => handleRefresh(false)}
                disabled={isManualRefresh}
                className="p-2 bg-gray-700 hover:bg-gray-600 rounded-lg transition-colors touch-target disabled:opacity-50"
                title="Manual refresh"
              >
                <RefreshCw 
                  className={`w-5 h-5 text-gray-300 ${isManualRefresh ? 'animate-spin' : ''}`} 
                />
              </button>
            )}

            {/* Fullscreen toggle */}
            <button
              onClick={toggleFullscreen}
              className="p-2 bg-gray-700 hover:bg-gray-600 rounded-lg transition-colors touch-target"
              title={isFullscreen ? 'Exit fullscreen' : 'Enter fullscreen'}
            >
              {isFullscreen ? (
                <Minimize2 className="w-5 h-5 text-gray-300" />
              ) : (
                <Maximize2 className="w-5 h-5 text-gray-300" />
              )}
            </button>

            {/* Current time */}
            <div className="text-lg font-mono text-white min-w-[90px] text-right">
              {currentTime}
            </div>
          </div>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="flex-1 overflow-auto p-4">
        <div className="h-full">
          {children}
        </div>
      </main>

      {/* Minimal Footer */}
      <footer className="bg-gray-800 border-t border-gray-700 px-4 py-2 flex-shrink-0">
        <div className="flex items-center justify-between text-sm text-gray-400">
          <div className="flex items-center space-x-4">
            <span>Last refresh: {lastRefresh.toLocaleTimeString()}</span>
            {user?.single_view_mode && (
              <span className="px-2 py-1 bg-blue-900 text-blue-300 rounded text-xs">
                Tablet Mode
              </span>
            )}
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 bg-green-400 rounded-full"></div>
            <span>System Active</span>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default TabletModeLayout;