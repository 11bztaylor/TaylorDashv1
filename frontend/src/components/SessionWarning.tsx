import React, { useState, useEffect } from 'react';
import { Clock, X, RefreshCw } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';

export const SessionWarning: React.FC = () => {
  const { sessionWarning, sessionExpiry, renewSession, dismissSessionWarning, logout } = useAuth();
  const [timeLeft, setTimeLeft] = useState<string>('');
  const [isRenewing, setIsRenewing] = useState(false);

  useEffect(() => {
    if (sessionWarning && sessionExpiry) {
      const updateTimeLeft = () => {
        const now = new Date();
        const expiry = new Date(sessionExpiry);
        const diff = expiry.getTime() - now.getTime();
        
        if (diff <= 0) {
          setTimeLeft('Session expired');
          return;
        }
        
        const minutes = Math.floor(diff / (1000 * 60));
        const seconds = Math.floor((diff % (1000 * 60)) / 1000);
        
        if (minutes > 0) {
          setTimeLeft(`${minutes}m ${seconds}s`);
        } else {
          setTimeLeft(`${seconds}s`);
        }
      };

      updateTimeLeft();
      const interval = setInterval(updateTimeLeft, 1000);

      return () => clearInterval(interval);
    }
  }, [sessionWarning, sessionExpiry]);

  const handleRenewSession = async () => {
    setIsRenewing(true);
    try {
      const success = await renewSession();
      if (!success) {
        // If renewal failed, logout
        await logout();
      }
    } catch (error) {
      console.error('Session renewal error:', error);
      await logout();
    } finally {
      setIsRenewing(false);
    }
  };

  if (!sessionWarning) {
    return null;
  }

  return (
    <div className="fixed top-4 right-4 bg-yellow-900 border border-yellow-600 rounded-lg p-4 shadow-lg z-50 max-w-sm">
      <div className="flex items-start space-x-3">
        <Clock className="w-5 h-5 text-yellow-400 mt-0.5 flex-shrink-0" />
        <div className="flex-1">
          <h4 className="text-yellow-100 font-semibold text-sm">Session Expiring Soon</h4>
          <p className="text-yellow-200 text-sm mt-1">
            Your session will expire in <strong>{timeLeft}</strong>. 
            Renew your session to continue working.
          </p>
          <div className="flex items-center space-x-2 mt-3">
            <button
              onClick={handleRenewSession}
              disabled={isRenewing}
              className="flex items-center space-x-1 px-3 py-1 bg-yellow-600 hover:bg-yellow-700 disabled:bg-yellow-800 text-yellow-100 text-xs rounded transition-colors"
            >
              <RefreshCw className={`w-3 h-3 ${isRenewing ? 'animate-spin' : ''}`} />
              <span>{isRenewing ? 'Renewing...' : 'Renew Session'}</span>
            </button>
            <button
              onClick={dismissSessionWarning}
              className="p-1 text-yellow-400 hover:text-yellow-300 transition-colors"
              title="Dismiss warning"
            >
              <X className="w-3 h-3" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SessionWarning;