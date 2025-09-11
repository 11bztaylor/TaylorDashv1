import React, { useState, useEffect } from 'react';
import { Wifi, WifiOff, AlertCircle } from 'lucide-react';
import { apiService } from '../services/api';

interface ConnectionStatusProps {
  onConnectionChange?: (connected: boolean) => void;
}

export const ConnectionStatus: React.FC<ConnectionStatusProps> = ({ onConnectionChange }) => {
  const [isConnected, setIsConnected] = useState<boolean | null>(null);
  const [lastCheck, setLastCheck] = useState<string>('');
  const [error, setError] = useState<string>('');

  const checkConnection = async () => {
    try {
      const health = await apiService.getHealth();
      const isHealthy = health.overall_status === 'healthy';
      setIsConnected(isHealthy);
      setError(isHealthy ? '' : 'Some services are unhealthy');
      setLastCheck(new Date().toLocaleTimeString());
      onConnectionChange?.(isHealthy);
    } catch (err) {
      setIsConnected(false);
      setError(err instanceof Error ? err.message : 'Connection failed');
      onConnectionChange?.(false);
    }
  };

  useEffect(() => {
    checkConnection();
    const interval = setInterval(checkConnection, 30000); // Check every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const getStatusColor = () => {
    if (isConnected === null) return 'text-yellow-500';
    return isConnected ? 'text-green-500' : 'text-red-500';
  };

  const getStatusIcon = () => {
    if (isConnected === null) return <AlertCircle className="w-4 h-4" />;
    return isConnected ? <Wifi className="w-4 h-4" /> : <WifiOff className="w-4 h-4" />;
  };

  const getStatusText = () => {
    if (isConnected === null) return 'Checking...';
    return isConnected ? 'Connected' : 'Disconnected';
  };

  return (
    <div className="flex items-center space-x-2 px-3 py-2 bg-gray-800 rounded-lg">
      <div className={`${getStatusColor()} flex items-center space-x-1`}>
        {getStatusIcon()}
        <span className="text-sm font-medium">{getStatusText()}</span>
      </div>
      
      {lastCheck && (
        <span className="text-xs text-gray-400">
          Last check: {lastCheck}
        </span>
      )}
      
      {error && (
        <span className="text-xs text-red-400" title={error}>
          Error
        </span>
      )}
      
      <button
        onClick={checkConnection}
        className="text-xs text-blue-400 hover:text-blue-300 underline"
      >
        Refresh
      </button>
    </div>
  );
};