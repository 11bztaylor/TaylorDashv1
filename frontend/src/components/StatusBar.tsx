import React, { useState, useEffect } from 'react';
import { 
  Wifi, 
  WifiOff, 
  Battery, 
  Clock, 
  Activity,
  HardDrive,
  Cpu
} from 'lucide-react';
import { cn } from '@/utils';

export function StatusBar() {
  const [currentTime, setCurrentTime] = useState(new Date());
  const [systemStats, setSystemStats] = useState({
    isOnline: navigator.onLine,
    cpuUsage: 0,
    memoryUsage: 0,
    diskUsage: 0,
  });

  // Update time every second
  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000);

    return () => clearInterval(timer);
  }, []);

  // Listen for online/offline status
  useEffect(() => {
    const handleOnline = () => setSystemStats(prev => ({ ...prev, isOnline: true }));
    const handleOffline = () => setSystemStats(prev => ({ ...prev, isOnline: false }));

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  // Simulate system stats (in a real app, these would come from an API)
  useEffect(() => {
    const interval = setInterval(() => {
      setSystemStats(prev => ({
        ...prev,
        cpuUsage: Math.random() * 100,
        memoryUsage: 60 + Math.random() * 30,
        diskUsage: 45 + Math.random() * 20,
      }));
    }, 2000);

    return () => clearInterval(interval);
  }, []);

  return (
    <footer className="h-8 bg-midnight-900/80 backdrop-blur-sm border-t border-midnight-700/50 px-4 flex items-center justify-between text-xs text-midnight-400">
      {/* Left side - System stats */}
      <div className="flex items-center gap-4">
        {/* Network Status */}
        <div className="flex items-center gap-1.5">
          {systemStats.isOnline ? (
            <Wifi className="w-3 h-3 text-cyber-400" />
          ) : (
            <WifiOff className="w-3 h-3 text-red-400" />
          )}
          <span className={cn(
            systemStats.isOnline ? 'text-cyber-400' : 'text-red-400'
          )}>
            {systemStats.isOnline ? 'Online' : 'Offline'}
          </span>
        </div>

        {/* CPU Usage */}
        <div className="hidden md:flex items-center gap-1.5">
          <Cpu className="w-3 h-3" />
          <span>CPU: {systemStats.cpuUsage.toFixed(1)}%</span>
        </div>

        {/* Memory Usage */}
        <div className="hidden lg:flex items-center gap-1.5">
          <Activity className="w-3 h-3" />
          <span>RAM: {systemStats.memoryUsage.toFixed(1)}%</span>
        </div>

        {/* Disk Usage */}
        <div className="hidden xl:flex items-center gap-1.5">
          <HardDrive className="w-3 h-3" />
          <span>Disk: {systemStats.diskUsage.toFixed(1)}%</span>
        </div>
      </div>

      {/* Right side - Time and status */}
      <div className="flex items-center gap-4">
        {/* Application Status */}
        <div className="flex items-center gap-1.5">
          <div className="w-2 h-2 bg-cyber-400 rounded-full animate-pulse-slow"></div>
          <span className="text-cyber-400">Ready</span>
        </div>

        {/* Current Time */}
        <div className="flex items-center gap-1.5">
          <Clock className="w-3 h-3" />
          <span className="font-mono">
            {currentTime.toLocaleTimeString([], { 
              hour: '2-digit', 
              minute: '2-digit',
              second: '2-digit'
            })}
          </span>
        </div>
      </div>
    </footer>
  );
}