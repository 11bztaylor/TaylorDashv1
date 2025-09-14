import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ErrorBoundary, NotificationContainer, AsyncErrorBoundary } from './components/ErrorBoundary';
import { PluginPage } from './components/PluginPage';
import { PluginsPage } from './components/PluginsPage';
import { LoginPage } from './components/LoginPage';
import { ProtectedRoute } from './components/ProtectedRoute';
import { SessionWarning } from './components/SessionWarning';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { eventBusService } from './services/eventBus';
// Refactored components
import { Navigation } from './components/Navigation';
import { Dashboard } from './components/Dashboard';
import { ProjectsView } from './components/ProjectsView';
import { FlowView } from './components/FlowView';
import { SettingsView } from './components/SettingsView';













// Main App component with routing
const AppContent: React.FC = () => {
  const { user } = useAuth();

  return (
    <div className="min-h-screen bg-gray-900">
      {!user?.single_view_mode && (
        <ErrorBoundary component="Navigation">
          <Navigation />
        </ErrorBoundary>
      )}
      
      <Routes>
        {/* Login Route */}
        <Route path="/login" element={<LoginPage />} />
        
        {/* Protected Routes */}
        <Route path="/" element={
          <ProtectedRoute>
            <ErrorBoundary component="Dashboard">
              <Dashboard />
            </ErrorBoundary>
          </ProtectedRoute>
        } />
        <Route path="/projects" element={
          <ProtectedRoute>
            <ErrorBoundary component="ProjectsView">
              <ProjectsView />
            </ErrorBoundary>
          </ProtectedRoute>
        } />
        <Route path="/flow" element={
          <ProtectedRoute>
            <ErrorBoundary component="FlowView">
              <FlowView />
            </ErrorBoundary>
          </ProtectedRoute>
        } />
        <Route path="/settings" element={
          <ProtectedRoute>
            <ErrorBoundary component="SettingsView">
              <SettingsView />
            </ErrorBoundary>
          </ProtectedRoute>
        } />
        <Route path="/plugins" element={
          <ProtectedRoute>
            <ErrorBoundary component="PluginsPage">
              <PluginsPage />
            </ErrorBoundary>
          </ProtectedRoute>
        } />
        <Route path="/plugins/:pluginId" element={
          <ProtectedRoute>
            <ErrorBoundary component="PluginPage">
              <PluginPage />
            </ErrorBoundary>
          </ProtectedRoute>
        } />
        
        {/* Catch all route - redirect to dashboard */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
      
      <NotificationContainer />
      <SessionWarning />
    </div>
  );
};

const App: React.FC = () => {
  // Initialize event bus service on app startup
  React.useEffect(() => {
    console.log('[App] Initializing event bus service...');
    // Event bus is initialized on import, just log for debugging
    const stats = eventBusService.getStats();
    console.log('[App] Event bus initialized with stats:', stats);
  }, []);

  return (
    <ErrorBoundary component="App">
      <AsyncErrorBoundary>
        <AuthProvider>
          <Router>
            <AppContent />
          </Router>
        </AuthProvider>
      </AsyncErrorBoundary>
    </ErrorBoundary>
  );
};

export default App;