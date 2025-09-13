import React, { createContext, useContext, useState, useEffect } from 'react';

interface User {
  id: string;
  username: string;
  role: 'admin' | 'viewer';
  default_view?: string;
  single_view_mode: boolean;
}

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  sessionExpiry: Date | null;
  sessionWarning: boolean;
  login: (username: string, password: string, rememberMe: boolean, singleViewMode: boolean, defaultView?: string) => Promise<void>;
  logout: () => Promise<void>;
  checkAuth: () => Promise<void>;
  renewSession: () => Promise<boolean>;
  dismissSessionWarning: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [sessionToken, setSessionToken] = useState<string | null>(
    localStorage.getItem('taylordash_session_token')
  );
  const [sessionExpiry, setSessionExpiry] = useState<Date | null>(
    localStorage.getItem('taylordash_session_expiry') 
      ? new Date(localStorage.getItem('taylordash_session_expiry')!) 
      : null
  );
  const [sessionWarning, setSessionWarning] = useState(false);
  const [sessionTimer, setSessionTimer] = useState<NodeJS.Timeout | null>(null);

  const setupSessionTimer = (expiry: Date) => {
    // Clear existing timer
    if (sessionTimer) {
      clearTimeout(sessionTimer);
    }

    const now = new Date();
    const timeUntilExpiry = expiry.getTime() - now.getTime();
    const warningTime = 5 * 60 * 1000; // 5 minutes before expiry

    if (timeUntilExpiry <= 0) {
      // Session already expired
      handleSessionExpiry();
      return;
    }

    if (timeUntilExpiry <= warningTime) {
      // Less than 5 minutes left, show warning immediately
      setSessionWarning(true);
    } else {
      // Set timer to show warning 5 minutes before expiry
      const warningTimer = setTimeout(() => {
        setSessionWarning(true);
      }, timeUntilExpiry - warningTime);
      setSessionTimer(warningTimer);
    }

    // Set timer for automatic logout at expiry
    const logoutTimer = setTimeout(() => {
      handleSessionExpiry();
    }, timeUntilExpiry);

    // Store the logout timer (overrides warning timer)
    setSessionTimer(logoutTimer);
  };

  const handleSessionExpiry = async () => {
    setSessionWarning(false);
    await logout();
  };

  const checkAuth = async () => {
    if (!sessionToken) {
      setIsLoading(false);
      return;
    }

    // Check if session is expired locally first
    if (sessionExpiry && new Date() >= sessionExpiry) {
      await handleSessionExpiry();
      setIsLoading(false);
      return;
    }

    try {
      const response = await fetch('/api/v1/auth/me', {
        headers: {
          'Authorization': `Bearer ${sessionToken}`,
          'X-API-Key': import.meta.env.VITE_API_KEY || 'taylordash-dev-key'
        }
      });

      if (response.ok) {
        const userData = await response.json();
        setUser({
          id: userData.id,
          username: userData.username,
          role: userData.role,
          default_view: userData.default_view,
          single_view_mode: userData.single_view_mode
        });

        // Setup session timeout if we have expiry data
        if (sessionExpiry) {
          setupSessionTimer(sessionExpiry);
        }
      } else {
        // Session expired or invalid
        localStorage.removeItem('taylordash_session_token');
        localStorage.removeItem('taylordash_session_expiry');
        setSessionToken(null);
        setSessionExpiry(null);
        setUser(null);
      }
    } catch (error) {
      console.error('Auth check failed:', error);
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  };

  const login = async (
    username: string, 
    password: string, 
    rememberMe: boolean,
    singleViewMode: boolean,
    defaultView?: string
  ) => {
    const response = await fetch('/api/v1/auth/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-API-Key': import.meta.env.VITE_API_KEY || 'taylordash-dev-key'
      },
      body: JSON.stringify({
        username,
        password,
        remember_me: rememberMe,
        single_view_mode: singleViewMode,
        default_view: defaultView
      })
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Login failed');
    }

    const data = await response.json();
    
    // Store session token and expiry
    localStorage.setItem('taylordash_session_token', data.session_token);
    localStorage.setItem('taylordash_session_expiry', data.expires_at);
    setSessionToken(data.session_token);
    
    const expiryDate = new Date(data.expires_at);
    setSessionExpiry(expiryDate);
    
    // Set user data
    setUser({
      id: data.user_id,
      username: data.username,
      role: data.role,
      default_view: data.default_view,
      single_view_mode: data.single_view_mode
    });

    // Setup session timeout timer
    setupSessionTimer(expiryDate);
  };

  const logout = async () => {
    if (sessionToken) {
      try {
        await fetch('/api/v1/auth/logout', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${sessionToken}`,
            'X-API-Key': import.meta.env.VITE_API_KEY || 'taylordash-dev-key'
          }
        });
      } catch (error) {
        console.error('Logout error:', error);
      }
    }
    
    // Clear session timer
    if (sessionTimer) {
      clearTimeout(sessionTimer);
      setSessionTimer(null);
    }
    
    // Clear all session data
    localStorage.removeItem('taylordash_session_token');
    localStorage.removeItem('taylordash_session_expiry');
    setSessionToken(null);
    setSessionExpiry(null);
    setUser(null);
    setSessionWarning(false);
  };

  const renewSession = async (): Promise<boolean> => {
    if (!sessionToken) {
      return false;
    }

    try {
      // Call checkAuth to refresh session activity
      await checkAuth();
      
      // If we're still authenticated after checkAuth, session was renewed
      if (user) {
        setSessionWarning(false);
        return true;
      }
      return false;
    } catch (error) {
      console.error('Session renewal failed:', error);
      return false;
    }
  };

  const dismissSessionWarning = () => {
    setSessionWarning(false);
  };

  useEffect(() => {
    checkAuth();
    
    // Cleanup timer on unmount
    return () => {
      if (sessionTimer) {
        clearTimeout(sessionTimer);
      }
    };
  }, []);

  return (
    <AuthContext.Provider value={{
      user,
      isAuthenticated: !!user,
      isLoading,
      sessionExpiry,
      sessionWarning,
      login,
      logout,
      checkAuth,
      renewSession,
      dismissSessionWarning
    }}>
      {children}
    </AuthContext.Provider>
  );
};